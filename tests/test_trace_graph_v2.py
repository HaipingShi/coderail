import json
import subprocess
import tempfile
from pathlib import Path

from test_support import _lifecycle_env, check


def _events(root: Path):
    return [
        json.loads(line)
        for line in (root / "docs" / "TRACELOG.jsonl").read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]


def _candidates(root: Path):
    rows = {}
    for line in (root / "docs" / "TRACE_CANDIDATES.jsonl").read_text(
        encoding="utf-8"
    ).splitlines():
        row = json.loads(line)
        if row.get("id"):
            rows.setdefault(row["id"], {}).update(row)
    return rows


def test_lifecycle_registers_provable_fact_edges_and_keeps_git_clean():
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        result = cr(
            "start",
            "Build fact graph",
            "--files",
            "feature.txt",
            "--verify",
            "true",
        )
        check(result.returncode == 0, result.stdout)
        started = _events(root)[-1]
        check(started["type"] == "task", started)
        check(started["subject"] == "T-001", started)
        check(started["edge_class"] == "fact", started)
        check(started["serves"], started)

        (root / "feature.txt").write_text("proved\n", encoding="utf-8")
        result = cr("done")
        check(result.returncode == 0, result.stdout)
        events = _events(root)
        verify = [
            event for event in events
            if event.get("type") == "verify" and event.get("task") == "T-001"
        ][-1]
        check(verify["edge_class"] == "fact", verify)
        check(verify["validates"] == ["T-001"], verify)
        message = subprocess.check_output(
            ["git", "-C", str(root), "log", "-1", "--format=%B"],
            text=True,
            encoding="utf-8",
        )
        check("CodeRail-Task: T-001" in message, message)
        check(f"CodeRail-Verified-By: {verify['id']}" in message, message)
        graph = cr("graph", "T-001")
        check("Modified:" in graph.stdout and "feature.txt" in graph.stdout, graph.stdout)
        check("Implementation commits: 1" in graph.stdout, graph.stdout)
        status = cr("inspect", "--no-write")
        check(status.returncode == 0 and "Status: healthy" in status.stdout, status.stdout)


def test_dependency_registration_checks_missing_refs_and_cycles():
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        cr("start", "First task", "--verify", "true")
        result = cr("done")
        check(result.returncode == 0, result.stdout)

        result = cr(
            "start",
            "Second task",
            "--depends-on",
            "T-001",
            "--verify",
            "true",
        )
        check(result.returncode == 0, result.stdout)
        meta = json.loads((root / ".coderail/tasks.json").read_text(encoding="utf-8"))
        check(meta["T-002"]["relations"]["depends_on"] == ["T-001"], meta)
        tasks = (root / "docs/TASKS.md").read_text(encoding="utf-8")
        check("- Depends on: T-001" in tasks, tasks)
        result = cr("done")
        check(result.returncode == 0, result.stdout)

        result = cr(
            "link",
            "T-001",
            "depends_on",
            "T-002",
            "--reason",
            "would create a cycle",
            "--confirmed-by",
            "test operator",
        )
        check(result.returncode == 1 and "dependency cycle" in result.stdout, result.stdout)
        result = cr(
            "link",
            "T-001",
            "blocks",
            "T-999",
            "--reason",
            "missing target",
            "--confirmed-by",
            "test operator",
        )
        check(result.returncode == 1 and "missing task T-999" in result.stdout, result.stdout)

        result = cr(
            "link",
            "T-001",
            "blocks",
            "T-002",
            "--reason",
            "explicit delivery order",
            "--confirmed-by",
            "test operator",
        )
        check(result.returncode == 0, result.stdout)
        result = cr(
            "link",
            "T-002",
            "supersedes",
            "T-001",
            "--reason",
            "explicit replacement",
            "--evidence",
            "docs/DECISIONS.md#replacement",
        )
        check(result.returncode == 0, result.stdout)
        decision = _events(root)[-1]
        check(decision["edge_class"] == "decision", decision)
        check(decision["supersedes"] == ["T-001"], decision)


def test_switch_activation_records_a_temporal_fact_not_a_dependency():
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        cr("start", "Source task", "--verify", "true")
        result = cr("switch", "Destination task", "--verify", "true")
        check(result.returncode == 0, result.stdout)
        event = [
            row for row in _events(root)
            if row.get("type") == "task" and row.get("task") == "T-002"
        ][-1]
        check(event["edge_class"] == "fact", event)
        check(event["follows"] == ["T-001"], event)
        check(not event.get("depends_on"), event)


def test_why_impact_and_graph_are_plain_language_summaries():
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        cr(
            "start",
            "Explainable task",
            "--goal",
            "Keep project reasoning understandable",
            "--files",
            "docs/result.md",
            "--verify",
            "true",
        )
        (root / "docs/result.md").write_text("# Result\n", encoding="utf-8")
        result = cr("done")
        check(result.returncode == 0, result.stdout)

        why = cr("why", "T-001")
        check(why.returncode == 0, why.stdout)
        for phrase in ["Serves:", "Modified:", "Verification evidence:", "Depends on: none"]:
            check(phrase in why.stdout, why.stdout)
        impact = cr("impact", "docs/result.md")
        check("Modified by 1 task(s): T-001" in impact.stdout, impact.stdout)
        graph = cr("graph", "T-001")
        check("# Graph: T-001" in graph.stdout and "Blocked by: none" in graph.stdout, graph.stdout)


def test_candidate_edges_are_isolated_until_evidence_backed_promotion():
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        cr("start", "Original task", "--verify", "true")
        check(cr("done").returncode == 0, "first close failed")
        cr("start", "Possible replacement", "--verify", "true")
        check(cr("done").returncode == 0, "second close failed")

        before_trace_count = len(_events(root))
        result = cr(
            "candidate",
            "add",
            "T-002",
            "supersedes",
            "T-001",
            "--reason",
            "the model suspects the new task replaces the old one",
            "--proposed-by",
            "model",
        )
        check(result.returncode == 0, result.stdout)
        check(len(_events(root)) == before_trace_count, "candidate leaked into TRACELOG")
        candidate_id = next(iter(_candidates(root)))
        graph = cr("graph", "T-002")
        check("Unconfirmed candidates: 1" in graph.stdout, graph.stdout)
        check("Important decisions: 0" in graph.stdout, graph.stdout)

        result = cr("candidate", "promote", candidate_id)
        check(result.returncode == 1 and "requires --evidence" in result.stdout, result.stdout)
        check(_candidates(root)[candidate_id]["status"] == "proposed", _candidates(root))

        result = cr(
            "candidate",
            "promote",
            candidate_id,
            "--evidence",
            "docs/DECISIONS.md#replacement",
        )
        check(result.returncode == 0, result.stdout)
        check(_candidates(root)[candidate_id]["status"] == "promoted", _candidates(root))
        formal = [
            event for event in _events(root)
            if event.get("edge_class") == "decision"
            and event.get("supersedes") == ["T-001"]
        ]
        check(len(formal) == 1, formal)
        graph = cr("graph", "T-002")
        check("Unconfirmed candidates" not in graph.stdout, graph.stdout)
        check("Important decisions: 1" in graph.stdout, graph.stdout)
