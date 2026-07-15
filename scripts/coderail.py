#!/usr/bin/env python3
"""CodeRail single entry point.

Three everyday commands, in plain language:

    coderail start "what you want to do"   Begin a task
    coderail check                         Am I on track? What's missing?
    coderail done                          Finish the task safely

Everything else (gates, traces, drive loops) runs automatically behind
these three commands. Advanced commands remain available for power users.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import task_switch  # noqa: E402
import inspect_state  # noqa: E402
import closeout_transaction  # noqa: E402
import repository_state  # noqa: E402

# Advanced/legacy commands, kept for compatibility and power users.
ADVANCED = {
    "ci": "ci_gate.py",
    "closeout": "closeout_check.py",
    "coordinate": "coordinate_check.py",
    "doctor": "doctor.py",
    "done-gate": "done_gate.py",
    "drive": "drive_check.py",
    "finish": "finish_task.py",
    "finish-task": "finish_task.py",
    "hook": "hook_guard.py",
    "init": "init_project.py",
    "inspect": "inspect_state.py",
    "tdd": "tdd_check.py",
    "trace": "trace_event.py",
    "trace-index": "trace_index.py",
}

TASK_HEADER = re.compile(r"^##\s+T-(\d+)", re.M)
ACTIVE_RE = re.compile(r"^##\s+(T-\d+)[^\n]*\n(?:(?!^##\s).)*?^Status:\s*\[(?:~|!)\]", re.M | re.S)

LIGHT_HINTS = ["doc", "readme", "note", "design", "research", "adr", "写文档", "笔记", "调研", "设计稿"]

MINIMAL_TASKS = """# Tasks

## Status legend

- `[ ]` todo
- `[~]` doing
- `[!]` blocked
- `[p]` paused
- `[x]` done

"""


def run_script(script: str, root: Path, args: list[str] | None = None, capture: bool = False):
    cmd = [sys.executable, str(SCRIPTS / script), "--target", str(root), *(args or [])]
    if capture:
        result = subprocess.run(cmd, cwd=str(root), stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True,
                                encoding="utf-8", errors="replace")
        return result.returncode, result.stdout or ""
    return subprocess.run(cmd, cwd=str(root)).returncode, ""


def tasks_path(root: Path) -> Path:
    return root / "docs" / "TASKS.md"


def read_tasks(root: Path) -> str:
    path = tasks_path(root)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(MINIMAL_TASKS, encoding="utf-8")
    return path.read_text(encoding="utf-8")


def next_task_id(text: str) -> str:
    numbers = [int(n) for n in TASK_HEADER.findall(text)]
    return f"T-{(max(numbers) + 1) if numbers else 1:03d}"


def active_task_id(text: str):
    m = ACTIVE_RE.search(text)
    return m.group(1) if m else None


TASK_BLOCK_RE = re.compile(
    r"^##\s+(T-\d+)\s+([^\n]*)\n((?:(?!^##\s).)*)", re.M | re.S
)


def list_tasks(text: str) -> list[dict]:
    """Return all tasks as {id, title, status} in file order."""
    tasks = []
    for m in TASK_BLOCK_RE.finditer(text):
        body = m.group(3)
        status_m = re.search(r"^Status:\s*(\[[ ~!xprf]\])", body, re.M)
        tasks.append({
            "id": m.group(1),
            "title": m.group(2).strip(),
            "status": status_m.group(1) if status_m else "[ ]",
        })
    return tasks


def task_contract_metadata(text: str, task_id: str | None) -> dict:
    if not task_id:
        return {}
    for match in TASK_BLOCK_RE.finditer(text):
        if match.group(1) != task_id:
            continue
        body = match.group(3)
        verify_section = re.search(
            r"^V\s+[^\n]*\n(.*?)(?=^A\s+[^\n]*\n|^X\s+[^\n]*\n|\Z)",
            body,
            re.M | re.S,
        )
        verify = []
        if verify_section:
            executables = {
                "python", "python3", "pytest", "node", "npm", "pnpm", "yarn",
                "ruff", "mypy", "go", "cargo", "dotnet", "mvn", "gradle",
                "bash", "sh", "powershell", "pwsh", "true", "false",
            }
            for candidate in re.findall(r"`([^`]+)`", verify_section.group(1)):
                first = candidate.strip().split(maxsplit=1)[0].lower() if candidate.strip() else ""
                if first in executables:
                    verify.append(candidate.strip())
        acceptance_section = re.search(
            r"^A\s+[^\n]*\n(.*?)(?=^X\s+[^\n]*\n|\Z)", body, re.M | re.S,
        )
        accept = []
        if acceptance_section:
            accept = re.findall(r"^- \[[ x]\]\s+(.+)$", acceptance_section.group(1), re.M)
        return {"verify": verify, "accept": accept}
    return {}


def next_todo_task(text: str):
    """Smart-but-simple recommendation: first `[ ]` task in file order.

    File order is the priority order the plan was written in, so the
    recommendation is deterministic and needs no configuration.
    """
    for task in list_tasks(text):
        if task["status"] == "[ ]":
            return task
    return None


def activate_task(root: Path, task_id: str) -> bool:
    path = tasks_path(root)
    text = path.read_text(encoding="utf-8")
    block = re.compile(
        rf"(^##\s+{re.escape(task_id)}\b(?:(?!^##\s).)*?^Status:\s*)\[(?: |p|r)\]",
        re.M | re.S,
    )
    new, n = block.subn(r"\g<1>[~]", text)
    if n:
        path.write_text(new, encoding="utf-8")
    return bool(n)


# ------------------------------------------------- task metadata (FN-009/010/011/012)
#
# Machine-checkable commitments registered at `start`, enforced at `done`:
#   verify:      shell commands that must exit 0 before the task can close
#   tests:       test files that must appear in the diff (TDD promise)
#   accept:      acceptance items that must each be marked done/deferred
#   display_id:  the user's business id (e.g. T-186), kept consistent everywhere
# Stored in .coderail/tasks.json (committed, so handoffs keep the contract).

DISPLAY_ID_RE = re.compile(r"^([A-Z]{1,10}-\d+)\s+(.+)$")


def meta_path(root: Path) -> Path:
    return root / ".coderail" / "tasks.json"


def load_meta(root: Path) -> dict:
    import json
    path = meta_path(root)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return {}


def save_meta(root: Path, meta: dict) -> None:
    import json
    path = meta_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def task_meta(root: Path, task_id: str) -> dict:
    return load_meta(root).get(task_id, {})


def record_activation_baseline(root: Path, task_id: str, baseline: dict, dirty_fork: bool = False) -> None:
    meta = load_meta(root)
    entry = meta.setdefault(task_id, {})
    entry["baseline"] = baseline
    if dirty_fork:
        entry["dirty_fork"] = True
    save_meta(root, meta)


def fmt_id(task_id: str, meta: dict | None = None) -> str:
    """One id policy everywhere: the user's business id leads (it is what
    humans remember and grep for); the internal id follows (FN-014)."""
    display = (meta or {}).get("display_id")
    if display and display != task_id:
        return f"{display} (internal {task_id})"
    return task_id


def run_verify_commands(root: Path, commands: list[str]) -> list[dict]:
    """Run each registered verify command; capture exit code and output tail."""
    results = []
    for cmd in commands:
        print(f"  running: {cmd}")
        try:
            executable = cmd
            if os.name == "nt":
                executable = re.sub(r"(?<!\S)true(?!\S)", "ver >nul", executable)
                executable = re.sub(r"(?<!\S)false(?!\S)", "exit /b 1", executable)
            proc = subprocess.run(
                executable, shell=True, cwd=str(root),
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace", timeout=600,
            )
            code, out = proc.returncode, proc.stdout or ""
        except subprocess.TimeoutExpired:
            code, out = 124, "(timed out after 600s)"
        except OSError as exc:
            code, out = 127, str(exc)
        tail = "\n".join(out.strip().splitlines()[-20:])
        results.append({"cmd": cmd, "exit": code, "tail": tail})
        print(f"    exit {code}")
    return results


def changed_files_now(root: Path) -> set[str]:
    """Files changed but not yet committed, plus files in recent commits."""
    names: set[str] = set()
    try:
        r = subprocess.run(["git", "status", "--porcelain", "-uall"], cwd=str(root),
                           stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                           text=True, encoding="utf-8", errors="replace")
        for line in r.stdout.splitlines():
            if len(line) > 3:
                names.add(line[3:].strip().strip('"'))
        r = subprocess.run(["git", "log", "-10", "--name-only", "--pretty=format:"],
                           cwd=str(root), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                           text=True, encoding="utf-8", errors="replace")
        for line in r.stdout.splitlines():
            if line.strip():
                names.add(line.strip())
    except OSError:
        pass
    return names


def print_next_recommendation(root: Path) -> None:
    text = read_tasks(root)
    todo = next_todo_task(text)
    if todo:
        print(f"Next up: {todo['id']} {todo['title']}")
        print(f"  Continue with:  coderail next --go")
        print(f"  Or start something new:  coderail start \"...\"")
    else:
        remaining = [t for t in list_tasks(text) if t["status"] in ("[~]", "[!]")]
        if remaining:
            ids = ", ".join(f"{t['id']}({t['status']})" for t in remaining)
            print(f"No queued tasks. Still open: {ids}")
        else:
            print("Task list is clear. Start your next task with:  coderail start \"...\"")


# ------------------------------------------------- plain-language reporting
#
# Vibe coders lose judgment late in a project because every report is jargon
# and every doc is unreadable. Two countermeasures:
#   1. docs/PROGRESS.md - ONE file, newest first, three short lines per task.
#      The only file a non-technical owner ever needs to read.
#   2. A report scaffold printed after every `done`, forcing the agent to
#      answer three plain questions before moving on.

def task_field(text: str, task_id: str, field: str) -> str:
    """Pull a one-line value (e.g. first Verify bullet) from a task block."""
    block_m = re.search(
        rf"^##\s+{re.escape(task_id)}\b((?:(?!^##\s).)*)", text, re.M | re.S
    )
    if not block_m:
        return ""
    block = block_m.group(1)
    section = re.search(rf"^{field}[^\n]*\n((?:- [^\n]+\n?)+)", block, re.M)
    if not section:
        return ""
    first = section.group(1).strip().splitlines()[0]
    return first.lstrip("- ").strip()


def append_progress(root: Path, task_id: str, title: str, verified: str, next_hint: str,
                    evidence: list[str] | None = None,
                    deferred: list[str] | None = None,
                    warnings: list[str] | None = None,
                    accepted: list[tuple[str, str]] | None = None) -> None:
    path = root / "docs" / "PROGRESS.md"
    header = (
        "# Progress - plain language, newest first\n\n"
        "If you only read one file in this project, read this one.\n"
        "Each entry: what got done, how it was checked, what comes next.\n"
    )
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    entry = (
        f"\n## {today} - {title} ({task_id})\n\n"
        f"- Done: {title}\n"
        f"- Checked by: {verified or 'UNVERIFIED - no machine check was run'}\n"
        f"- Next: {next_hint}\n"
    )
    for line in evidence or []:
        entry += f"- Evidence: {line}\n"
    for item, status in accepted or []:
        entry += f"- Acceptance [{status}]: {item}\n"
    for item in deferred or []:
        entry += f"- Deferred: {item} (registered as a follow-up task)\n"
    for w in warnings or []:
        entry += f"- Warning: {w}\n"
    if path.exists():
        text = path.read_text(encoding="utf-8")
        # Insert newest entry right after the header (before older entries).
        first_entry = text.find("\n## ")
        if first_entry == -1:
            text = text.rstrip() + "\n" + entry
        else:
            text = text[:first_entry] + entry + text[first_entry:]
        path.write_text(text, encoding="utf-8")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(header + entry, encoding="utf-8")


def print_user_report_scaffold(task_id: str, title: str, verified: str) -> None:
    # FN-020: long verify command lists overflow the prompt line; truncate
    # here - the full text lives in the on-disk done report.
    evidence = verified or "state plainly"
    if len(evidence) > 70:
        evidence = evidence[:67] + "... (full evidence in the done report)"
    print()
    print("== Now tell the user (their language, no jargon, 3-6 sentences) ==")
    print(f"  1. what they can do now  2. how you know it works ({evidence})")
    print("  3. what next / any decision - phrase decisions as clear either/or.")


POST_CLOSE_LEDGER_FILES = {
    ".coderail/tasks.json",
    "docs/PROGRESS.md",
    "docs/TASKS.md",
    "docs/HANDOFF.md",
    "docs/TRACELOG.jsonl",
    "docs/TRACE_INDEX.md",
    "docs/CODERAIL_STATUS.md",
}


def commit_post_close_ledger(root: Path, task_id: str) -> tuple[bool, str]:
    """Persist state written after finish_task's first safe commit."""
    changed = [
        row["path"] for row in task_switch.git_status_entries(root)
        if row["path"] in POST_CLOSE_LEDGER_FILES and row["status"] != "!!"
    ]
    if not changed:
        return True, "no post-close ledger changes"
    add = subprocess.run(
        ["git", "-C", str(root), "add", "--", *changed],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if add.returncode:
        return False, add.stdout.strip() or "git add failed"
    commit = subprocess.run(
        ["git", "-C", str(root), "commit", "-m", f"chore({task_id}): persist closeout ledger"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if commit.returncode:
        return False, commit.stdout.strip() or "git commit failed"
    return True, ", ".join(changed)


def reopen_after_close_failure(root: Path, task_id: str) -> None:
    path = tasks_path(root)
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(
        rf"(^##\s+{re.escape(task_id)}\b(?:(?!^##\s).)*?^Status:\s*)\[x\]",
        re.M | re.S,
    )
    updated, count = pattern.subn(r"\g<1>[!]", text, count=1)
    if count:
        path.write_text(updated, encoding="utf-8")
    task_switch.clear_closed_pending(root, task_id)


def post_close_consistency(root: Path, task_id: str) -> tuple[bool, list[str], str]:
    """Prove the final Git state and the same state model used by inspect agree."""
    baseline = task_switch.unchanged_baseline_paths(root, task_id)
    residual = sorted({
        row.path for row in repository_state.capture(root).files
        if row.status != "!!"
        and row.path not in baseline
        and row.path != ".coderail/pending_close.json"
    })
    status, _ = inspect_state.render(root)
    owned = [path for owner, path in task_switch.closed_pending_paths(root)
             if owner == task_id]
    paths = sorted(set(residual + owned))
    return not paths and status != "blocked", paths, status


def append_switch_trace(root: Path, task_id: str, summary: str, event_type: str = "task") -> bool:
    rc, output = run_script(
        "trace_event.py",
        root,
        [
            "--type", event_type,
            "--task", task_id,
            "--status", "progress",
            "--summary", summary,
            "--coordinate-task", task_id,
            "--persist", "TASKS,HANDOFF,TRACE",
        ],
        capture=True,
    )
    if rc:
        print(output or f"Could not append switch trace for {task_id}.")
    return rc == 0


def write_done_report(root: Path, shown: str, title: str,
                      verify_results: list[dict],
                      accepted_pairs: list[tuple[str, str]],
                      tdd_warnings: list[str],
                      gate_output: str) -> str:
    """FN-018: persist the full evidence trail (incl. verify output tails)
    so the console can stay quiet without losing anything."""
    reports = root / ".coderail" / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    safe_id = re.sub(r"[^A-Za-z0-9_-]", "_", shown)
    path = reports / f"done-{stamp}-{safe_id}.md"
    lines = [f"# Done report - {shown} - {title}", ""]
    if verify_results:
        lines.append("## Verify commands")
        for r in verify_results:
            lines += [f"### `{r['cmd']}` (exit {r['exit']})", "", "```",
                      r.get("tail", "").rstrip(), "```", ""]
    else:
        lines += ["## Verify commands", "", "None registered - task closed unverified.", ""]
    if accepted_pairs:
        lines.append("## Acceptance")
        for item, status in accepted_pairs:
            lines.append(f"- [{status}] {item}")
        lines.append("")
    if tdd_warnings:
        lines.append("## Warnings")
        lines += [f"- {w}" for w in tdd_warnings] + [""]
    lines += ["## Full gate output", "", "```", gate_output.rstrip(), "```", ""]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path.relative_to(root).as_posix()  # FN-029: portable path in TASKS/PROGRESS


# ------------------------------------------------- blueprint coverage
#
# 4 layers, 11 diagram classes (defined in blueprint_check.py). The engine
# detects which diagrams THIS project needs from actual code signals; here we
# surface the gaps in everyday commands and scaffold the missing ones so the
# project stays followable, maintainable, learnable, and deliverable.
# Convergent rule applies: diagrams are ratified output, never upfront input.

MERMAID_STUBS = {
    "UJM": ("User Journey Map", "journey\n    title User journey\n    section Arrive\n      Open the app: 3: User\n    section Core action\n      Do the main thing: 4: User\n    section Leave satisfied\n      See the result: 5: User"),
    "UF": ("User Flow", "flowchart TD\n    Start([User arrives]) --> A{Main choice?}\n    A -->|Path 1| B[Step]\n    A -->|Path 2| C[Step]\n    B --> Done([Goal reached])\n    C --> Done"),
    "PF": ("Page Flow", "flowchart LR\n    Home[Home page] --> Detail[Detail page]\n    Detail --> Action[Action page]\n    Action --> Home"),
    "SA": ("System Architecture", "flowchart TB\n    User([User]) --> FE[Frontend]\n    FE --> API[Backend / API]\n    API --> DB[(Database)]"),
    "CD": ("Component Diagram", "flowchart TB\n    subgraph App\n      A[Module A] --> B[Module B]\n      B --> C[Shared utils]\n    end"),
    "SEQ": ("Sequence Diagram", "sequenceDiagram\n    participant U as User\n    participant F as Frontend\n    participant B as Backend\n    U->>F: action\n    F->>B: request\n    B-->>F: response\n    F-->>U: result"),
    "SM": ("State Machine", "stateDiagram-v2\n    [*] --> Draft\n    Draft --> Active: submit\n    Active --> Done: complete\n    Active --> Draft: reject\n    Done --> [*]"),
    "ERD": ("ER Diagram", "erDiagram\n    USER ||--o{ ITEM : owns\n    USER {\n      string id PK\n      string name\n    }\n    ITEM {\n      string id PK\n      string user_id FK\n    }"),
    "DFD": ("Data Flow Diagram", "flowchart LR\n    In[/Input/] --> P1[Transform]\n    P1 --> S[(Store)]\n    S --> Out[/Output/]"),
    "DD": ("Deployment Diagram", "flowchart TB\n    subgraph Cloud\n      Web[Web service] --> DB[(Managed database)]\n    end\n    Dev[Developer] -->|deploy| Cloud"),
    "CICD": ("CI/CD Pipeline", "flowchart LR\n    Commit --> Test --> Build --> Deploy"),
}


def load_blueprint_module():
    try:
        sys.path.insert(0, str(SCRIPTS))
        import blueprint_check
        return blueprint_check
    except ImportError:
        return None
    finally:
        if str(SCRIPTS) in sys.path:
            sys.path.remove(str(SCRIPTS))


def blueprint_gaps(root: Path) -> dict:
    """Return {'required': [...ids missing/not-current...], 'stale': [...], 'recommended': [...]}."""
    bc = load_blueprint_module()
    empty = {"required": [], "stale": [], "recommended": []}
    if bc is None:
        return empty
    try:
        result = bc.check_project(root)
    except Exception:
        return empty
    path = root / "docs" / "BLUEPRINTS.md"
    rows = bc.parse_blueprints(bc.read(path)) if path.exists() else {}
    gaps = {"required": [], "stale": [], "recommended": []}
    for did in result.get("required", []):
        status = rows.get(did, {}).get("status", "")
        if status == "stale":
            gaps["stale"].append(did)
        elif status != "current":
            gaps["required"].append(did)
    for did in result.get("recommended", []):
        status = rows.get(did, {}).get("status", "")
        if status not in {"current", "not-applicable"}:
            gaps["recommended"].append(did)
    return gaps


def print_blueprint_notice(root: Path) -> None:
    gaps = blueprint_gaps(root)
    if not (gaps["required"] or gaps["stale"]):
        return
    bc = load_blueprint_module()
    names = (lambda ids: ", ".join(f"{i} ({bc.DIAGRAM_BY_ID[i].name})" for i in ids)) if bc else (lambda ids: ", ".join(ids))
    print("\n== Blueprints ==")
    if gaps["required"]:
        print(f"  ! The code now needs diagrams it does not have: {names(gaps['required'])}")
    if gaps["stale"]:
        print(f"  ! These diagrams no longer match the code: {names(gaps['stale'])}")
    print("  A project without current diagrams cannot be handed over, maintained,")
    print("  or learned from. Create/update them with:  coderail blueprint --scaffold")
    print()


def cmd_blueprint(args) -> int:
    root = Path(args.target).resolve()
    bc = load_blueprint_module()
    if bc is None:
        print("blueprint_check.py not found next to coderail.py")
        return 1

    result = bc.check_project(root)
    if not args.scaffold:
        print(bc.render_report(result))
        gaps = blueprint_gaps(root)
        if gaps["required"] or gaps["stale"]:
            print("\nFill the gaps automatically with:  coderail blueprint --scaffold")
        return 1 if result["status"] == "unhealthy" else 0

    # --scaffold: create stub diagrams for every required/stale/recommended gap.
    gaps = blueprint_gaps(root)
    todo_ids = gaps["required"] + gaps["stale"] + (gaps["recommended"] if args.all else [])
    if not todo_ids:
        print("Blueprint coverage is already complete for the detected project shape.")
        return 0

    bp_dir = root / "docs" / "blueprints"
    bp_dir.mkdir(parents=True, exist_ok=True)
    index_path = root / "docs" / "BLUEPRINTS.md"
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # FN-008b: anchor each stub in the project's REAL detected shape so the
    # agent replaces placeholders with facts, not more placeholders.
    layers = result.get("layers", {}) or {}
    detected = [f"{layer}: {', '.join(sig)}" for layer, sig in layers.items() if sig]
    top_dirs = sorted(
        p.name + "/" for p in root.iterdir()
        if p.is_dir() and not p.name.startswith(".")
        and p.name not in ("node_modules", "docs", "__pycache__")
    )[:12]
    anchor = ""
    if detected or top_dirs:
        anchor = "\nDetected in this codebase (use these real names in the diagram):\n"
        for d in detected:
            anchor += f"- {d}\n"
        if top_dirs:
            anchor += f"- top-level dirs: {', '.join(top_dirs)}\n"

    created = []
    for did in todo_ids:
        title, mermaid = MERMAID_STUBS[did]
        stub_path = bp_dir / f"{did.lower()}.md"
        if not stub_path.exists():
            stub_path.write_text(
                f"# {title} ({did})\n\n"
                f"Status: draft scaffold - replace the placeholder shapes with this\n"
                f"project's real structure, then set the index row to `current`.\n"
                f"{anchor}\n"
                f"What this diagram answers: see docs/BLUEPRINTS.md notes for {did}.\n\n"
                f"```mermaid\n{mermaid}\n```\n",
                encoding="utf-8",
            )
        created.append(did)
        # Update the index row: status -> planned, path -> stub, updated -> today.
        if index_path.exists():
            text = index_path.read_text(encoding="utf-8")
            row_re = re.compile(
                rf"^(\|\s*{did}\s*\|[^|]*\|)\s*[^|]*(\|)\s*[^|]*(\|[^|]*\|)\s*[^|]*(\|[^|]*\|)\s*$",
                re.M,
            )
            replacement = rf"\g<1> planned \g<2> docs/blueprints/{did.lower()}.md \g<3> {today} \g<4>"
            text, n = row_re.subn(replacement, text, count=1)
            if n:
                index_path.write_text(text, encoding="utf-8")

    print(f"Scaffolded {len(created)} diagram stub(s): {', '.join(created)}")
    print(f"  Stubs: docs/blueprints/  (Mermaid, edit in place)")
    print(f"  Index: docs/BLUEPRINTS.md  (rows set to 'planned')")
    print()
    print("Now replace each placeholder with the project's real structure,")
    print("then set its index row to 'current'. Keep every diagram small:")
    print("the goal is that a newcomer understands the system without guesswork.")
    return 0


# ------------------------------------------------- spinning-in-place detection
#
# Second-order feedback (Wiener): when first-order feedback (edit -> verify)
# keeps failing to converge, that is itself a signal that the problem lives
# one abstraction level up. No intelligence needed - just counting.
#
#   level 1 (action -> design):      repeated attempts on the same task
#   level 2 (design -> architecture): same files churning across recent commits
#   level 3 (architecture -> intent): repeated blocked/failed tasks

SPIN_ATTEMPTS_DESIGN = 3      # attempts on one task before suggesting design review
SPIN_ATTEMPTS_INTENT = 5      # attempts before suggesting requirement review
SPIN_CHURN_COMMITS = 20       # how many recent commits to scan for churn
SPIN_CHURN_THRESHOLD = 5      # same file in >= N of those commits = oscillation
SPIN_BLOCKED_THRESHOLD = 2    # blocked/failed tasks before questioning intent


def trace_attempts(root: Path, task_id: str) -> tuple[int, int]:
    """Count (total_verify_attempts, failed_attempts) for a task from TRACELOG.jsonl."""
    log = root / "docs" / "TRACELOG.jsonl"
    if not log.exists():
        return 0, 0
    import json
    attempts = failed = 0
    try:
        for line in log.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if entry.get("task") != task_id:
                continue
            if entry.get("type") in ("verify", "fix", "change"):
                attempts += 1
                if entry.get("harness_result") == "failed" or entry.get("status") == "failed":
                    failed += 1
    except OSError:
        return 0, 0
    return attempts, failed


def spin_state_path(root: Path) -> Path:
    return root / ".coderail" / "spin.json"


def load_spin_state(root: Path) -> dict:
    import json
    path = spin_state_path(root)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return {}


def bump_spin_state(root: Path, task_id: str, *, reset: bool = False) -> None:
    """Count failed `done` attempts per task; reset on success."""
    import json
    state = load_spin_state(root)
    if reset:
        state.pop(task_id, None)
    else:
        state[task_id] = state.get(task_id, 0) + 1
    path = spin_state_path(root)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except OSError:
        pass


def churning_files(root: Path) -> list[tuple[str, int]]:
    """Files MODIFIED in >= SPIN_CHURN_THRESHOLD of the last SPIN_CHURN_COMMITS
    commits. Renames/copies/adds/deletes are excluded: moving a file is
    housekeeping, not oscillation (FN-003)."""
    try:
        result = subprocess.run(
            ["git", "log", f"-{SPIN_CHURN_COMMITS}", "--name-status",
             "-M", "-C", "--pretty=format:"],
            cwd=str(root), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, encoding="utf-8", errors="replace",
        )
    except OSError:
        return []
    if result.returncode != 0:
        return []
    counts: dict[str, int] = {}
    for line in result.stdout.splitlines():
        parts = line.strip().split("\t")
        if len(parts) < 2 or not parts[0].startswith("M"):
            continue  # only pure modifications count toward churn
        name = parts[-1].strip()
        if not name or name.startswith("docs/") or name.startswith(".coderail/"):
            continue
        counts[name] = counts.get(name, 0) + 1
    hot = [(f, n) for f, n in counts.items() if n >= SPIN_CHURN_THRESHOLD]
    hot.sort(key=lambda x: -x[1])
    return hot[:3]


def north_star_line(root: Path) -> str:
    path = root / "docs" / "NORTH_STAR.md"
    if not path.exists():
        return ""
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and not line.startswith("<!--"):
            return line
    return ""


def spin_report(root: Path, active: str | None, tasks: list[dict]) -> list[str]:
    """Deterministic escalation hints. Returns plain-language lines (may be empty)."""
    lines: list[str] = []

    # Level 1 / 3: repeated attempts on the active task.
    if active:
        attempts, failed = trace_attempts(root, active)
        failed_dones = load_spin_state(root).get(active, 0)
        # Trace entries and the failed-done counter can describe the same
        # attempt, so take the strongest single signal instead of summing.
        signal = max(failed, attempts - 1, failed_dones)
        attempts = max(attempts, failed_dones)  # for honest reporting below
        if signal >= SPIN_ATTEMPTS_INTENT:
            lines.append(
                f"You have circled {active} {attempts} times. Stop repairing. "
                f"Step two levels up: is this the right thing to build at all?"
            )
            star = north_star_line(root)
            if star:
                lines.append(f"Project goal for reference: \"{star}\"")
        elif signal >= SPIN_ATTEMPTS_DESIGN:
            lines.append(
                f"{active} has been attempted {attempts} times without closing. "
                f"Stop fixing the symptom. Step one level up: "
                f"is the design of this module right?"
            )

    # Level 2: file churn across recent commits.
    for filename, n in churning_files(root):
        lines.append(
            f"{filename} changed in {n} of the last {SPIN_CHURN_COMMITS} commits. "
            f"A file that never settles usually means the design around it is wrong, "
            f"not the code inside it."
        )

    # Level 3: repeated blocked/failed tasks.
    blocked = [t for t in tasks if t["status"] == "[!]"]
    if len(blocked) >= SPIN_BLOCKED_THRESHOLD:
        ids = ", ".join(t["id"] for t in blocked)
        lines.append(
            f"{len(blocked)} tasks are blocked ({ids}). When multiple tasks jam, "
            f"the requirement itself may be unclear. Re-read docs/NORTH_STAR.md "
            f"before starting anything new."
        )
    return lines


def print_spin_report(root: Path, active: str | None, tasks: list[dict]) -> None:
    hints = spin_report(root, active, tasks)
    if not hints:
        return
    print("\n== Step back ==")
    for hint in hints:
        print(f"  ! {hint}")
    print()


def guess_rail(title: str, goal: str, task_type: str) -> str:
    blob = f"{title} {goal} {task_type}".lower()
    if task_type in {"docs", "design", "research", "note"}:
        return "light"
    if any(h in blob for h in LIGHT_HINTS):
        return "light"
    return "full"


# ---------------------------------------------------------------- start

def cmd_start(args) -> int:
    root = Path(args.target).resolve()
    text = read_tasks(root)

    dirty_fork = bool(getattr(args, "dirty_fork", False))
    preflight = task_switch.activation_preflight(root, text, dirty_fork=dirty_fork)
    if not preflight["allowed"] and preflight["reason"] == "active-task":
        active = ", ".join(preflight["active"])
        print(f"Task Switch Gate blocked start: active owner {active}.")
        print('Use:  coderail switch "new task"')
        print("A verified checkpoint may use:  coderail switch \"new task\" --checkpoint")
        if getattr(args, "force", False):
            print("NOTE: --force cannot bypass the single-active-task invariant.")
        return 1
    if not preflight["allowed"] and preflight["reason"] == "closed-dirty":
        print("Task Switch Gate blocked start: a closed task still owns uncommitted paths:")
        for owner, path in preflight["paths"]:
            print(f"  - {path} (owner {owner})")
        print("Commit those exact paths, or explicitly carry them with:  --dirty-fork")
        return 1

    task_id = next_task_id(text)
    title = args.title.strip()

    # FN-011: bind the user's business id. Explicit --id wins; otherwise a
    # title prefix like "T-186 ..." or "PROJ-42 ..." is parsed and stripped.
    display_id = (args.id or "").strip()
    prefix_m = DISPLAY_ID_RE.match(title)
    if not display_id and prefix_m:
        display_id, title = prefix_m.group(1), prefix_m.group(2).strip()
    elif display_id and prefix_m and prefix_m.group(1) == display_id:
        title = prefix_m.group(2).strip()

    goal = (args.goal or title).strip()
    done_when = (args.done_when or "Manually confirm the result works as intended.").strip()
    # FN-021: --files is repeatable and each value may mix comma lists and
    # globs. Preserve each normalized pattern as the durable scope contract;
    # current matches are useful detail, but future matches must remain owned.
    raw_files: list[str] = []
    for chunk in (args.files or []):
        raw_files += [f.strip() for f in chunk.split(",") if f.strip()]
    files: list[str] = []
    for pat in raw_files:
        # FN-029: TASKS.md is a committed, cross-platform artifact whose paths
        # are matched against git output (always forward-slash). Normalize the
        # pattern to forward-slash BEFORE globbing (so a Windows-style
        # "src\x\*.ts" still expands), and store results forward-slash too.
        pat = pat.replace("\\", "/")
        if any(ch in pat for ch in "*?["):
            matches = sorted(
                p.relative_to(root).as_posix() for p in root.glob(pat) if p.is_file()
            )
            files.append(pat)
            files += matches
        else:
            files.append(pat)
    seen: set[str] = set()
    files = [f for f in files if not (f in seen or seen.add(f))]
    avoid = [f.strip() for f in (args.avoid or "").split(",") if f.strip()]
    task_type = (args.type or "feature").strip().lower()
    rail = guess_rail(title, goal, task_type)

    verify_cmds = [v.strip() for v in (args.verify or []) if v.strip()]
    test_files = [t.strip() for t in (args.tests or []) if t.strip()]
    accept_items = [a.strip() for a in (args.accept or []) if a.strip()]

    if dirty_fork and preflight.get("paths"):
        task_switch.consume_closed_pending(root)
    meta = load_meta(root)
    meta[task_id] = {
        k: v for k, v in {
            "display_id": display_id or None,
            "verify": verify_cmds or None,
            "tests": test_files or None,
            "accept": accept_items or None,
            "baseline": preflight.get("baseline"),
            "baseline_adoption": (
                task_switch.build_baseline_adoption(root, files, avoid)
                if getattr(args, "adopt_baseline", False) else None
            ),
            "dirty_fork": dirty_fork or None,
        }.items() if v
    }
    save_meta(root, meta)

    allowed_lines = "\n".join(f"  - {f}" for f in files) if files else "  - to be decided while working"
    forbidden_lines = "\n".join(f"  - {f}" for f in avoid) if avoid else "  - none"
    verify_lines = "".join(f"\n- Run: `{c}` (must exit 0)" for c in verify_cmds)
    accept_lines = ""
    if accept_items:
        accept_lines = "\nA — Acceptance\n" + "\n".join(f"- [ ] {a}" for a in accept_items) + "\n"
    display_line = f"\nDisplay id: {display_id}" if display_id else ""

    block = f"""
## {task_id} {title}

Status: [~]{display_line}
Type: {task_type}
Rail: {rail}

### CodeRail Coordinate

G — Goal
- {goal}

T — Task
- {title}

S — Scope
Allowed:
{allowed_lines}
Forbidden:
{forbidden_lines}

V — Verify
- {done_when}{verify_lines}
{accept_lines}
X — Stop
- Stop and ask if changes are needed outside the allowed files.

P — Persist
- TASKS, TRACE
"""
    path = tasks_path(root)
    path.write_text(text.rstrip() + "\n" + block, encoding="utf-8")

    shown = fmt_id(task_id, meta[task_id])
    print(f"Started task {shown}: {title}")
    print(f"  Goal:      {goal}")
    print(f"  Files:     {', '.join(files) if files else 'decide while working'}")
    print(f"  Done when: {done_when}")
    if verify_cmds:
        print(f"  Verify:    {' && '.join(verify_cmds)}  (done will run these)")
    else:
        print("  Verify:    NONE registered - done will warn and record the task")
        print("             as unverified. Add machine checks with --verify \"cmd\".")
    if test_files:
        print(f"  Tests:     {', '.join(test_files)}  (must appear in the diff)")
    if accept_items:
        print(f"  Accepts:   {len(accept_items)} item(s) - done will require a status for each")
    print()
    print("Recorded in docs/TASKS.md. When you are finished, run:  coderail done")
    return 0


# ---------------------------------------------------------------- check

def cmd_check(args) -> int:
    root = Path(args.target).resolve()
    text = read_tasks(root)
    active = active_task_id(text)

    print("# CodeRail Check\n")
    if active:
        a_meta = task_meta(root, active)
        print(f"Active task: {fmt_id(active, a_meta)}")
        if a_meta.get("verify"):
            print(f"  Verify on done: {' && '.join(a_meta['verify'])}")
        else:
            print("  Verify on done: none registered (will close as unverified)")
    else:
        print("Active task: none (start one with:  coderail start \"...\")")
    all_tasks = list_tasks(text)
    queued = [t for t in all_tasks if t["status"] == "[ ]"]
    if queued:
        print(f"Queued: {len(queued)} task(s), next would be {queued[0]['id']} {queued[0]['title']}")

    print_spin_report(root, active, all_tasks)
    print_blueprint_notice(root)

    coord_rc, coord_out = run_script("coordinate_check.py", root, capture=True)
    tdd_rc, tdd_out = run_script("tdd_check.py", root, capture=True)

    problems = []
    if coord_rc:
        problems.append("Some tasks are missing goal, scope, or verification info.")
    if tdd_rc:
        problems.append("A task that needs tests does not have test evidence yet.")

    if not problems:
        print("Everything looks consistent. You can keep working or run:  coderail done")
    else:
        print("\nBefore finishing, fix these:")
        for p in problems:
            print(f"  - {p}")
        print("\nDetails below.")
        if coord_rc:
            print("\n--- task record check ---\n" + coord_out)
        if tdd_rc:
            print("\n--- test evidence check ---\n" + tdd_out)
    return 1 if problems else 0


# ---------------------------------------------------------------- done

BOILERPLATE_VERIFY = "Manually confirm the result works as intended."


# FN-027/FN-028: everything the closeout ledger needs is snapshotted BEFORE
# any state-mutating step runs, and persisted to disk so a crash or a
# mid-flow "task not found" can never lose it. progress --repair reads it.

def pending_close_path(root: Path) -> Path:
    return root / ".coderail" / "pending_close.json"


def write_pending_close(root: Path, snapshot: dict) -> None:
    path = pending_close_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")


def load_pending_close(root: Path) -> dict:
    try:
        return json.loads(pending_close_path(root).read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError, OSError):
        return {}


def clear_pending_close(root: Path) -> None:
    try:
        pending_close_path(root).unlink()
    except (FileNotFoundError, OSError):
        pass


def cmd_done(args) -> int:
    root = Path(args.target).resolve()

    tasks_text_before = read_tasks(root)
    task_before = args.task or active_task_id(tasks_text_before)
    transaction = closeout_transaction.CloseoutTransaction(task_before or "(unknown)")
    meta = task_meta(root, task_before) if task_before else {}
    contract_meta = task_contract_metadata(tasks_text_before, task_before)
    for key in ("verify", "accept"):
        if not meta.get(key) and contract_meta.get(key):
            meta[key] = contract_meta[key]
    shown = fmt_id(task_before, meta) if task_before else ""

    # ---- FN-010: run registered verify commands. This is the gate itself.
    verify_cmds = meta.get("verify", [])
    verify_results: list[dict] = []
    if verify_cmds:
        print(f"Verifying {shown} ({len(verify_cmds)} command(s)):")
        verify_results = run_verify_commands(root, verify_cmds)
        failed = [r for r in verify_results if r["exit"] != 0]
        if failed:
            print()
            for r in failed:
                print(f"VERIFY FAILED (exit {r['exit']}): {r['cmd']}")
                for line in r["tail"].splitlines():
                    print(f"    {line}")
            print()
            print(f"Cannot close {shown}: {len(failed)} verify command(s) failed.")
            print("Fix the failures, then run:  coderail done   again.")
            if task_before:
                bump_spin_state(root, task_before)
            text = read_tasks(root)
            print_spin_report(root, active_task_id(text), list_tasks(text))
            return 1
    transaction.advance(closeout_transaction.Phase.VERIFIED)

    # ---- FN-012: acceptance items must each be marked done or deferred.
    # Two input forms (FN-016 improvement): positional "done,deferred,done"
    # or unambiguous numbered "1=done" "2=deferred" (repeatable, any order).
    accept_items = meta.get("accept", [])
    accept_statuses: list[str] = []
    deferred_items: list[str] = []
    if accept_items and args.result == "done":
        raw_parts: list[str] = []
        for chunk in (args.accept_status or []):
            raw_parts += [p.strip() for p in chunk.split(",") if p.strip()]
        statuses: list[str] | None = None
        if raw_parts and all("=" in p for p in raw_parts):
            by_index: dict[int, str] = {}
            for p in raw_parts:
                idx_s, _, val = p.partition("=")
                try:
                    by_index[int(idx_s.strip())] = val.strip().lower()
                except ValueError:
                    by_index = {}
                    break
            if len(by_index) == len(accept_items) and set(by_index) == set(range(1, len(accept_items) + 1)):
                statuses = [by_index[i] for i in range(1, len(accept_items) + 1)]
        elif raw_parts and not any("=" in p for p in raw_parts):
            statuses = [p.lower() for p in raw_parts]

        if (statuses is None or len(statuses) != len(accept_items)
                or any(s not in ("done", "deferred") for s in statuses)):
            print(f"Cannot close {shown}: this task registered {len(accept_items)} acceptance item(s).")
            print("State each one explicitly, either positionally or by number:")
            for i, item in enumerate(accept_items, 1):
                print(f"  {i}. {item}")
            print('Positional:  coderail done --accept-status "done,deferred,done"')
            print('By number:   coderail done --accept-status "1=done" --accept-status "2=deferred"')
            return 1
        accept_statuses = statuses
        deferred_items = [item for item, s in zip(accept_items, statuses) if s == "deferred"]

    # ---- FN-009: promised test files must appear in the diff.
    tdd_warnings: list[str] = []
    promised_tests = meta.get("tests", [])
    if promised_tests:
        touched = changed_files_now(root)
        for tf in promised_tests:
            if not any(name == tf or name.endswith("/" + tf) or tf in name for name in touched):
                tdd_warnings.append(
                    f"Promised test file was never touched: {tf} "
                    f"(declared at start with --tests, absent from the diff)"
                )
        for w in tdd_warnings:
            print(f"WARNING: {w}")

    # FN-027/FN-028: snapshot the full closeout context to disk BEFORE the
    # gate runs. From here on, no ledger step may depend on "the current
    # active task" - the task will stop being active mid-flow by design.
    snapshot_title = ""
    if task_before:
        for t in list_tasks(tasks_text_before):
            if t["id"] == task_before:
                snapshot_title = t["title"]
                break
        write_pending_close(root, {
            "task": task_before,
            "display_id": meta.get("display_id", ""),
            "title": snapshot_title,
            "next_hint": (args.next_hint or "").strip(),
            "accept_items": accept_items,
            "accept_statuses": accept_statuses,
            "manual_acceptance": args.manual_acceptance or "",
            "verify_results": [
                {"cmd": r["cmd"], "exit": r["exit"]} for r in verify_results
            ],
            "stamp": datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S"),
        })
    transaction.advance(closeout_transaction.Phase.SNAPSHOTTED)

    extra = []
    # FN-017-1: ALWAYS pass the resolved task explicitly, so the gate chain
    # and the reporting chain are guaranteed to close the SAME task.
    if task_before:
        extra += ["--task", task_before]
    extra += ["--task-result", args.result]
    harness = args.harness_result
    if not harness and verify_results:
        harness = "passed"  # all verify commands exited 0 (enforced above)
    if harness:
        extra += ["--harness-result", harness]
    if args.manual_acceptance:
        extra += ["--manual-acceptance", args.manual_acceptance]
    if args.no_commit:
        extra += ["--no-auto-commit"]
    if getattr(args, "pause_after", False):
        extra += ["--pause-after"]
    if meta.get("display_id"):
        extra += ["--commit-message",
                  f"chore({meta['display_id']}/{task_before}): "
                  + ("complete task" if args.result == "done" else f"{args.result} checkpoint")]

    # FN-018: capture the full gate output instead of dumping 100+ lines.
    rc, gate_output = run_script("finish_task.py", root, extra, capture=True)
    if args.verbose:
        print(gate_output)
        if rc == 0 and "Status: blocked" in gate_output:
            print("NOTE: the inspect section above says 'blocked' for a project-level")
            print("      reason (e.g. empty North Star) - unrelated to this task closure,")
            print("      which PASSED.")

    print()
    # FN-027: decide by FACTS, not by the gate's return code alone. The field
    # run proved rc can be 1 while the task WAS closed and committed - and the
    # old rc-only branch then skipped the entire ledger and told the user to
    # "run done again" (which can only yield "no active task").
    after_by_id_fact = {t["id"]: t for t in list_tasks(read_tasks(root))}
    task_closed_fact = bool(
        task_before
        and after_by_id_fact.get(task_before, {}).get("status") == "[x]"
        and {t["id"]: t for t in list_tasks(tasks_text_before)}.get(
            task_before, {}).get("status") != "[x]"
    )
    if rc in (0, 3) or task_closed_fact:
        transaction.advance(closeout_transaction.Phase.CLASSIFIED)
        transaction.advance(closeout_transaction.Phase.STAGED)
        transaction.advance(closeout_transaction.Phase.COMMITTED)
        if rc not in (0, 3):
            print(f"GATE INCONSISTENCY: the gate reported failure (rc={rc}) but")
            print(f"{shown} WAS closed in docs/TASKS.md. Trusting the file: writing")
            print("the ledger now. Do NOT rerun done. Gate output is in the report;")
            print("investigate it, but the close itself stands.")
            print()
        # FN-023: rc==3 (continuous mode) is ALSO a successful close - the
        # gate closed the task and committed. The ledger steps below must run
        # for every successful close, and each is individually guarded so a
        # failure is loud, named, and repairable - never silent.
        if task_before:
            bump_spin_state(root, task_before, reset=True)

        title = verified = ""
        report_path = None
        ledger_errors: list[str] = []
        if task_before:
            # FN-017-1: trust the file, not our assumption - the closed task is
            # the one whose status actually flipped away from [~].
            before_by_id = {t["id"]: t for t in list_tasks(tasks_text_before)}
            after_by_id = {t["id"]: t for t in list_tasks(read_tasks(root))}
            flipped = [
                tid for tid, t in after_by_id.items()
                if before_by_id.get(tid, {}).get("status") == "[~]" and t["status"] != "[~]"
            ]
            closed_id = task_before
            if flipped and task_before not in flipped:
                closed_id = flipped[0]
                print(f"NOTE: the gate closed {closed_id}, not {task_before}; reporting on {closed_id}.")
                meta = task_meta(root, closed_id)
                shown = fmt_id(closed_id, meta)
            title = before_by_id.get(closed_id, {}).get("title", "")

            # FN-017-2: "Checked by" is true evidence, never boilerplate.
            evidence_lines: list[str] = []
            if verify_results:
                verified = "; ".join(f"`{r['cmd']}` exit {r['exit']}" for r in verify_results)
                evidence_lines = [f"`{r['cmd']}` -> exit {r['exit']}" for r in verify_results]
            elif args.manual_acceptance:
                verified = f"manual check: {args.manual_acceptance}"
            else:
                verified = "unverified - no verify commands registered"

            accepted_pairs = list(zip(accept_items, accept_statuses)) if accept_statuses else []

            # Ledger step 1: persist the full evidence report.
            try:
                report_path = write_done_report(
                    root, shown, title, verify_results, accepted_pairs,
                    tdd_warnings, gate_output,
                )
            except Exception as e:  # noqa: BLE001 - must be loud, not fatal
                ledger_errors.append(f"report file (.coderail/reports/): {e}")

            # Ledger step 2: append the plain-language journal entry.
            try:
                todo = next_todo_task(read_tasks(root))
                default_hint = f"{todo['id']} {todo['title']}" if todo else "decide with the user"
                next_hint = (args.next_hint or "").strip() or default_hint  # FN-020
                append_progress(
                    root, shown, title or shown, verified, next_hint,
                    evidence=evidence_lines,
                    deferred=deferred_items,
                    warnings=tdd_warnings,
                    accepted=accepted_pairs,
                )
            except Exception as e:  # noqa: BLE001
                ledger_errors.append(f"progress journal (docs/PROGRESS.md): {e}")

        # Ledger step 3 (FN-012): deferred acceptance items become queued tasks.
        if deferred_items:
            try:
                text_now = read_tasks(root)
                blocks = ""
                for item in deferred_items:
                    new_id = next_task_id(text_now + blocks)
                    blocks += (
                        f"\n## {new_id} {item}\n\nStatus: [ ]\nType: feature\nRail: full\n\n"
                        f"### CodeRail Coordinate\n\nG — Goal\n- Deferred from {shown}: {item}\n\n"
                        f"T — Task\n- {item}\n\nS — Scope\nAllowed:\n  - to be decided while working\n"
                        f"Forbidden:\n  - none\n\nV — Verify\n- {BOILERPLATE_VERIFY}\n\n"
                        f"X — Stop\n- Stop and ask if changes are needed outside the allowed files.\n\n"
                        f"P — Persist\n- TASKS, TRACE\n"
                    )
                tasks_path(root).write_text(text_now.rstrip() + "\n" + blocks, encoding="utf-8")
                print(f"  deferred:    {len(deferred_items)} item(s) registered as queued tasks")
            except Exception as e:  # noqa: BLE001
                ledger_errors.append(f"deferred task queueing (docs/TASKS.md): {e}")

        # FN-027 fuse: audit the ledger with the same logic as
        # `coderail progress` before declaring victory. If the entry we just
        # claimed to write is not actually on disk, that is a hard error.
        if task_before and not ledger_errors:
            gap_ids = {g[0] for g in ledger_gaps(root)}
            if task_before in gap_ids or closed_id in gap_ids:
                ledger_errors.append(
                    "post-close audit: the PROGRESS entry claimed above is NOT on disk")

        if task_before and not ledger_errors and not args.no_commit:
            committed, detail = commit_post_close_ledger(root, task_before)
            if committed:
                print(f"  ledger commit: {detail}")
            else:
                ledger_errors.append(f"post-close ledger commit: {detail}")

        if ledger_errors:
            transaction.fail(closeout_transaction.Failure.PERSIST_FAILED)
            print()
            print("LEDGER ERROR: the task WAS closed and committed, but these")
            print("record-keeping steps FAILED and must be repaired now:")
            for e in ledger_errors:
                print(f"  - {e}")
            print("Repair with:  coderail progress --repair")
            print("(the closeout snapshot is kept in .coderail/pending_close.json)")
            return 1

        transaction.advance(closeout_transaction.Phase.PERSISTED)

        # Ledger complete: the snapshot has served its purpose.
        clear_pending_close(root)

        if task_before:
            consistent, residue, inspect_status = post_close_consistency(root, closed_id)
            transaction.advance(closeout_transaction.Phase.RESCANNED)
            transaction.finalize(inspect_status=inspect_status, residual_paths=residue)
            if not transaction.success:
                reopen_after_close_failure(root, closed_id)
                print()
                print("POST-CLOSE CONSISTENCY FAILED: the task was reopened and done returns failure.")
                print(f"Inspect-equivalent status: {inspect_status}")
                print(f"Transaction failure: {transaction.result().failure.name}")
                print("Exact unresolved paths:")
                if residue:
                    for path in residue:
                        print(f"  - {path}")
                else:
                    print("  - none; inspect reported a blocking project-state inconsistency")
                print("Resolve these paths, verify task ownership, then run coderail done again.")
                return 1

            # FN-018: the success word is emitted only after the final rescan.
            print(f"== Done: {shown} - {title or '(untitled)'} ==")
            if verify_results:
                ok = sum(1 for r in verify_results if r["exit"] == 0)
                print(f"  verify:      {ok}/{len(verify_results)} command(s) passed")
            else:
                print("  verify:      none registered - closed as unverified")
            if accepted_pairs:
                n_done = sum(1 for _, s in accepted_pairs if s == "done")
                n_def = len(accepted_pairs) - n_done
                print(f"  acceptance:  {n_done} done, {n_def} deferred")
            print(f"  warnings:    {len(tdd_warnings)}")
            print(f"  committed:   {'no (--no-commit)' if args.no_commit else 'yes (safe task files)'}")
            print("  inspect:     consistent")
            print("  journal:     docs/PROGRESS.md updated")
            if report_path:
                print(f"  full report: {report_path}")
        else:
            print("Task closed. Docs updated, checks passed, safe files committed.")

        print_blueprint_notice(root)
        print_next_recommendation(root)
        if task_before:
            print_user_report_scaffold(shown, title or shown, verified)
        if rc == 3:
            print("This project runs in continuous mode: keep going with the next task.")
            return 3
        return 0
    else:
        if not args.verbose:
            print(gate_output)  # on failure, details ARE the point
        if task_before:
            bump_spin_state(root, task_before)
        # FN-027: only tell the user to rerun done if the task is genuinely
        # still open - "run done again" on a closed task can only produce
        # "no active task" and is actively misleading.
        still_open = bool(
            task_before
            and after_by_id_fact.get(task_before, {}).get("status") in ("[~]", "[!]", "[ ]")
        )
        print("Not finished yet - one or more checks did not pass (details above).")
        if still_open or not task_before:
            print("Fix what it points out, then run:  coderail done   again.")
        else:
            print(f"NOTE: {shown} is no longer open in docs/TASKS.md. Do NOT rerun")
            print("done. Audit the ledger instead:  coderail progress --repair")
        text = read_tasks(root)
        print_spin_report(root, active_task_id(text), list_tasks(text))
    return rc


# ---------------------------------------------------------------- progress

def ledger_gaps(root: Path) -> list[tuple[str, str, dict]]:
    """Every closed task must have a PROGRESS.md entry. Returns the ones that
    do not, as (task_id, title, meta). Shared by `coderail progress` and the
    post-close audit fuse inside `done` (FN-027)."""
    progress_file = root / "docs" / "PROGRESS.md"
    progress_text = progress_file.read_text(encoding="utf-8") if progress_file.exists() else ""

    missing = []
    for t in list_tasks(read_tasks(root)):
        if t["status"] in ("[ ]", "[~]") or "Example task" in t["title"]:
            continue
        tid = t["id"]
        m = task_meta(root, tid)
        display = m.get("display_id")
        if f"({tid})" in progress_text or f"internal {tid})" in progress_text \
                or (display and f"({display}" in progress_text):
            continue
        missing.append((tid, t["title"], m))
    return missing


def cmd_progress(args) -> int:
    """FN-023: audit the ledger - every closed task must have a PROGRESS
    entry. --repair writes honest retroactive entries for any that are missing
    (e.g. closes that predate the transactional fix)."""
    root = Path(args.target).resolve()
    missing = ledger_gaps(root)

    if not missing:
        print("Ledger is complete: every closed task has a PROGRESS.md entry.")
        return 0

    print(f"Ledger gap: {len(missing)} closed task(s) missing from docs/PROGRESS.md:")
    for tid, title, m in missing:
        print(f"  - {fmt_id(tid, m)} {title}")
    if not args.repair:
        print("Write retroactive entries with:  coderail progress --repair")
        return 1

    # FN-028: if the interrupted close left its snapshot behind, restore the
    # REAL --next text, acceptance verdicts, and verify evidence from it
    # instead of falling back to default copy.
    pending = load_pending_close(root)

    for tid, title, m in missing:
        shown = fmt_id(tid, m)
        snap = pending if pending.get("task") == tid else {}
        # Point at the on-disk done report if one survived the original close.
        reports = sorted((root / ".coderail" / "reports").glob("done-*.md")) \
            if (root / ".coderail" / "reports").is_dir() else []
        safe = re.sub(r"[^A-Za-z0-9_-]", "_", shown)
        matching = [p for p in reports if safe in p.name or tid in p.name]

        if snap.get("verify_results"):
            checked = ("retroactive entry - verify results recovered from the "
                       "closeout snapshot: "
                       + "; ".join(f"`{r['cmd']}` exit {r['exit']}"
                                   for r in snap["verify_results"]))
        elif snap.get("manual_acceptance"):
            checked = f"retroactive entry - manual check: {snap['manual_acceptance']}"
        elif m.get("verify"):
            checked = ("retroactive entry - verify commands were registered ("
                       + "; ".join(f"`{c}`" for c in m["verify"])
                       + "); original console evidence was lost to a ledger bug")
        else:
            checked = "retroactive entry - no verify commands were registered"
        if matching:
            checked += f"; surviving report: {matching[-1].relative_to(root).as_posix()}"

        next_hint = snap.get("next_hint") or "decide with the user"
        accepted = list(zip(snap.get("accept_items", []),
                            snap.get("accept_statuses", []))) \
            if snap.get("accept_statuses") else []
        append_progress(root, shown, title, checked, next_hint,
                        accepted=accepted,
                        warnings=["this entry was written by progress --repair, "
                                  "after the close itself skipped the journal"])
        if snap:
            clear_pending_close(root)
            pending = {}
        print(f"  repaired: {shown}")
    print("Ledger repaired. Review docs/PROGRESS.md and commit it.")
    return 0


# ---------------------------------------------------------------- next

def cmd_next(args) -> int:
    root = Path(args.target).resolve()
    text = read_tasks(root)

    dirty_fork = bool(getattr(args, "dirty_fork", False))
    preflight = task_switch.activation_preflight(root, text, dirty_fork=dirty_fork)
    if not preflight["allowed"] and preflight["reason"] == "active-task":
        print(f"Task Switch Gate blocked next --go: active owner {', '.join(preflight['active'])}.")
        print("Use coderail switch --to <TASK_ID> after closing or checkpointing the current task.")
        return 1
    if not preflight["allowed"] and preflight["reason"] == "closed-dirty":
        print("Task Switch Gate blocked next --go: a closed task still owns uncommitted paths:")
        for owner, path in preflight["paths"]:
            print(f"  - {path} (owner {owner})")
        print("Commit those exact paths, or rerun with --dirty-fork.")
        return 1

    todo = next_todo_task(text)
    if not todo:
        print("No queued tasks in docs/TASKS.md.")
        print("Start a new one with:  coderail start \"...\"")
        return 0

    if not args.go:
        print(f"Recommended next task: {todo['id']} {todo['title']}")
        print("Pick it up with:  coderail next --go")
        return 0

    if dirty_fork and preflight.get("paths"):
        task_switch.consume_closed_pending(root)
    record_activation_baseline(root, todo["id"], preflight["baseline"], dirty_fork=dirty_fork)
    if activate_task(root, todo["id"]):
        print(f"Now working on {todo['id']}: {todo['title']}")
        print("Details are in docs/TASKS.md. When finished, run:  coderail done")
        return 0

    print(f"Could not activate {todo['id']}. Check docs/TASKS.md formatting.")
    return 1


# ---------------------------------------------------------------- switch

def cmd_switch(args) -> int:
    root = Path(args.target).resolve()
    text = read_tasks(root)
    active = active_task_id(text)

    if args.continue_current:
        if not active:
            print("Task Switch Gate: there is no active task to continue.")
            return 1
        print(f"Task Switch Gate: continuing {active}; no task state or Git state changed.")
        return 0

    if not args.title and not args.to:
        print('Task Switch Gate needs a destination title or --to TASK_ID.')
        return 1
    if args.title and args.to:
        print("Choose one destination: a new title or --to TASK_ID, not both.")
        return 1
    if args.checkpoint and args.dirty_fork:
        print("Choose one source disposition: --checkpoint or --dirty-fork.")
        return 1

    destination = args.to or args.title
    if active:
        if args.dirty_fork:
            task_switch.write_h3_handoff(
                root,
                active,
                f"explicit dirty-fork waiver before switching to {destination}",
            )
            if not task_switch.pause_task(root, active, "dirty-fork"):
                print(f"Could not pause {active}; repair docs/TASKS.md before switching.")
                return 1
        else:
            done_args = argparse.Namespace(
                target=str(root),
                task=active,
                result="stage-complete" if args.checkpoint else "done",
                harness_result=args.harness_result,
                manual_acceptance=args.manual_acceptance,
                accept_status=args.accept_status,
                verbose=args.verbose,
                next_hint=f"switch to {destination}",
                no_commit=False,
                pause_after=args.checkpoint,
            )
            rc = cmd_done(done_args)
            if rc != 0:
                current = active_task_id(read_tasks(root)) or active
                task_switch.write_h3_handoff(
                    root,
                    current,
                    f"safe closeout failed before switching to {destination}",
                )
                append_switch_trace(
                    root,
                    current,
                    f"switch to {destination} stopped; H3 decision required",
                    event_type="handoff",
                )
                print()
                print("Task Switch Gate did not activate the destination.")
                print("Choose one:")
                print("  coderail switch --continue-current")
                if args.to:
                    print(f"  coderail switch --to {args.to} --dirty-fork")
                else:
                    print(f'  coderail switch "{args.title}" --dirty-fork')
                return 1

    if args.to:
        text = read_tasks(root)
        dirty_fork = bool(args.dirty_fork)
        preflight = task_switch.activation_preflight(root, text, dirty_fork=dirty_fork)
        if not preflight["allowed"]:
            print(f"Task Switch Gate blocked activation of {args.to}: {preflight['reason']}.")
            for owner, path in preflight.get("paths", []):
                print(f"  - {path} (owner {owner})")
            return 1
        known = {task["id"]: task for task in list_tasks(text)}
        target = known.get(args.to)
        if not target or target["status"] not in {"[ ]", "[p]", "[r]"}:
            print(f"{args.to} is not a queued, paused, or reopened task.")
            return 1
        if dirty_fork and preflight.get("paths"):
            task_switch.consume_closed_pending(root)
        if target["status"] != "[p]":
            record_activation_baseline(root, args.to, preflight["baseline"], dirty_fork=dirty_fork)
        activated = (
            task_switch.resume_task(root, args.to)
            if target["status"] in {"[p]", "[r]"}
            else activate_task(root, args.to)
        )
        if not activated:
            print(f"Could not activate {args.to}; repair docs/TASKS.md before retrying.")
            return 1
        if not append_switch_trace(
            root,
            args.to,
            f"activated {args.to} through Task Switch Gate",
        ):
            print(f"{args.to} is active, but its switch trace failed. Repair TRACE before coding.")
            return 1
        print(f"Task Switch Gate activated {args.to}; exactly one task now owns new changes.")
        return 0

    source = active or "none"
    new_id = next_task_id(read_tasks(root))
    rc = cmd_start(args)
    if rc == 0 and not append_switch_trace(
        root,
        new_id,
        f"switched from {source} to {new_id} through Task Switch Gate",
    ):
        print(f"{new_id} is active, but its switch trace failed. Repair TRACE before coding.")
        return 1
    return rc


# ---------------------------------------------------------------- main

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="coderail",
        description="CodeRail: start a task, check progress, finish safely.",
    )
    sub = parser.add_subparsers(dest="command")

    p_start = sub.add_parser("start", help="Begin a new task")
    p_start.add_argument("title", help="What you want to do, in one sentence")
    p_start.add_argument("--goal", help="Why this matters (defaults to the title)")
    p_start.add_argument("--files", action="append",
                         help="Files you expect to touch: repeatable, comma lists "
                              'and globs both work (e.g. --files "src/x/*.ts" --files "docs/y.md")')
    p_start.add_argument("--avoid", help="Files/folders that must NOT change, comma separated")
    p_start.add_argument("--done-when", help="How you will know it is finished")
    p_start.add_argument("--type", help="feature | bug | refactor | docs (default: feature)")
    p_start.add_argument("--id", help="Your own task id (e.g. T-186); also parsed from title prefix")
    p_start.add_argument("--verify", action="append",
                         help="Shell command that must exit 0 before done (repeatable)")
    p_start.add_argument("--tests", action="append",
                         help="Test file that must appear in the diff (repeatable)")
    p_start.add_argument("--accept", action="append",
                         help="Acceptance item; done requires done/deferred per item (repeatable)")
    p_start.add_argument("--force", action="store_true",
                         help="Deprecated: cannot bypass the single-active-task invariant")
    p_start.add_argument("--dirty-fork", action="store_true",
                         help="Explicitly carry a fingerprinted dirty baseline")
    p_start.add_argument("--adopt-baseline", action="store_true",
                         help="Adopt explicitly allowed files in a repository with no Git baseline")
    p_start.add_argument("--target", default=".")

    p_check = sub.add_parser("check", help="Am I on track? What's missing?")
    p_check.add_argument("--target", default=".")

    p_next = sub.add_parser("next", help="Recommend (or pick up) the next queued task")
    p_next.add_argument("--go", action="store_true", help="Activate the recommended task")
    p_next.add_argument("--dirty-fork", action="store_true",
                        help="Explicitly carry closed-task dirty paths as the new baseline")
    p_next.add_argument("--target", default=".")

    p_switch = sub.add_parser("switch", help="Close or pause the current task, then activate one destination")
    p_switch.add_argument("title", nargs="?", help="New destination task title")
    p_switch.add_argument("--to", help="Activate an existing queued, paused, or reopened task")
    p_switch.add_argument("--checkpoint", action="store_true",
                          help="Commit a verified stage-complete checkpoint and pause the source")
    p_switch.add_argument("--dirty-fork", action="store_true",
                          help="Explicitly pause without committing implementation and carry its fingerprinted baseline")
    p_switch.add_argument("--continue-current", action="store_true",
                          help="Keep the current task active after a stopped switch")
    p_switch.add_argument("--goal", help="Why the new task matters")
    p_switch.add_argument("--files", action="append", help="Files the new task may touch")
    p_switch.add_argument("--avoid", help="Files/folders the new task must not change")
    p_switch.add_argument("--done-when", help="How the new task will be accepted")
    p_switch.add_argument("--type", help="feature | bug | refactor | docs")
    p_switch.add_argument("--id", help="Business id for a new destination task")
    p_switch.add_argument("--verify", action="append", help="New-task verify command (repeatable)")
    p_switch.add_argument("--tests", action="append", help="New-task promised test file (repeatable)")
    p_switch.add_argument("--accept", action="append", help="New-task acceptance item (repeatable)")
    p_switch.add_argument("--accept-status", action="append",
                          help="Source-task acceptance verdicts used during safe closeout")
    p_switch.add_argument("--harness-result", choices=["passed", "failed", "manual", "skipped"])
    p_switch.add_argument("--manual-acceptance", help="Source-task manual acceptance evidence")
    p_switch.add_argument("--verbose", action="store_true")
    p_switch.add_argument("--target", default=".")
    p_switch.set_defaults(force=False)

    p_bp = sub.add_parser("blueprint", help="Check diagram coverage; --scaffold fills the gaps")
    p_bp.add_argument("--scaffold", action="store_true",
                      help="Create Mermaid stubs for missing required/stale diagrams")
    p_bp.add_argument("--all", action="store_true",
                      help="With --scaffold: also stub recommended diagrams")
    p_bp.add_argument("--target", default=".")

    p_done = sub.add_parser("done", help="Finish the current task safely")
    p_done.add_argument("--task", help="Task id (defaults to the active task)")
    p_done.add_argument("--result", default="done",
                        choices=["done", "stage-complete", "blocked", "failed", "deferred"],
                        help="How the task ended (default: done)")
    p_done.add_argument("--harness-result", choices=["passed", "failed", "manual", "skipped"])
    p_done.add_argument("--manual-acceptance", help="One sentence: how you manually confirmed it works")
    p_done.add_argument("--accept-status", action="append",
                        help='Per acceptance item: "done,deferred,..." (positional) '
                             'or "1=done" "2=deferred" (numbered, repeatable)')
    p_done.add_argument("--verbose", action="store_true",
                        help="Print the full gate reports (always saved to .coderail/reports/)")
    p_done.add_argument("--next", dest="next_hint",
                        help="The real next step, written to the journal's Next field (FN-020)")
    p_done.add_argument("--no-commit", action="store_true", help="Do not auto-commit")
    p_done.add_argument("--target", default=".")

    p_prog = sub.add_parser("progress", help="Audit or repair the progress journal")
    p_prog.add_argument("--repair", action="store_true",
                        help="Write retroactive entries for closed tasks missing from PROGRESS.md")
    p_prog.add_argument("--target", default=".")

    return parser


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)

    # Advanced/legacy passthrough keeps every old command working.
    if argv and argv[0] in ADVANCED:
        script = ADVANCED[argv[0]]
        rest = argv[1:]
        cmd = [sys.executable, str(SCRIPTS / script), *rest]
        if "--target" not in rest and script != "init_project.py":
            cmd += ["--target", "."]
        return subprocess.call(cmd)

    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "start":
        return cmd_start(args)
    if args.command == "check":
        return cmd_check(args)
    if args.command == "next":
        return cmd_next(args)
    if args.command == "switch":
        return cmd_switch(args)
    if args.command == "blueprint":
        return cmd_blueprint(args)
    if args.command == "done":
        return cmd_done(args)
    if args.command == "progress":
        return cmd_progress(args)

    parser.print_help()
    print("\nAdvanced commands: " + ", ".join(sorted(ADVANCED)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
