#!/usr/bin/env python3
"""CodeRail Closeout Check: stop with auto-commit and resume state."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import done_gate  # noqa: E402
import coordinate_check  # noqa: E402


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except FileNotFoundError:
        return ""


def git_status_entries(root: Path, include_ignored: bool = True) -> list[tuple[str, str]]:
    cmd = ["git", "-C", str(root), "status", "--short", "--untracked-files=all"]
    if include_ignored:
        cmd.append("--ignored=matching")
    try:
        out = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
    except Exception:
        return []
    entries = []
    for raw in out.splitlines():
        if not raw.strip() or len(raw) < 4:
            continue
        code = raw[:2]
        path = raw[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        entries.append((code, path.replace("\\", "/")))
    return entries


STATE_FILES = {
    "docs/TASKS.md",
    "docs/TRACELOG.jsonl",
    "docs/TRACE_INDEX.md",
    "docs/CODERAIL_STATUS.md",
    "docs/HANDOFF.md",
}


def classify(
    entries: list[tuple[str, str]],
    allowed: list[str],
    forbidden: list[str],
    include_state: bool = False,
) -> dict[str, list[str]]:
    result = {
        "safe": [],
        "outside": [],
        "forbidden": [],
        "ignored": [],
    }
    for code, path in entries:
        if code == "!!":
            result["ignored"].append(path)
            continue
        if forbidden and done_gate.matches_any(path, forbidden):
            result["forbidden"].append(path)
        elif include_state and path in STATE_FILES:
            result["safe"].append(path)
        elif allowed and not done_gate.matches_any(path, allowed):
            result["outside"].append(path)
        else:
            result["safe"].append(path)
    return result


def bullet(items: list[str], limit: int = 20) -> str:
    if not items:
        return "- none"
    shown = items[:limit]
    lines = [f"- {x}" for x in shown]
    if len(items) > limit:
        lines.append(f"- ... {len(items) - limit} more")
    return "\n".join(lines)


def yes_no(value: bool) -> str:
    return "yes" if value else "no"


def git_output(root: Path, args: list[str]) -> tuple[int, str]:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.returncode, result.stdout.strip()


def in_git_repo(root: Path) -> bool:
    code, out = git_output(root, ["rev-parse", "--is-inside-work-tree"])
    return code == 0 and out.lower() == "true"


def default_commit_message(task_id: str, task_result: str, commit_type: str) -> str:
    summary = "complete task" if task_result == "done" else f"{task_result} checkpoint"
    return f"{commit_type}({task_id}): {summary}"


def auto_commit(root: Path, files: list[str], message: str) -> tuple[str, str]:
    if not in_git_repo(root):
        return "skipped", "target is not a git repository"
    if not files:
        return "skipped", "no safe task-scoped files to commit"
    code, out = git_output(root, ["add", "--", *files])
    if code != 0:
        return "failed", out or "git add failed"
    code, _ = git_output(root, ["diff", "--cached", "--quiet"])
    if code == 0:
        return "skipped", "no staged changes after task-scoped add"
    code, out = git_output(root, ["commit", "-m", message])
    if code != 0:
        return "failed", out or "git commit failed"
    first = out.splitlines()[0] if out else "commit created"
    return "committed", first


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Run CodeRail closeout check")
    ap.add_argument("--target", default=".")
    ap.add_argument("--task", help="Task id to check, e.g. T-001")
    ap.add_argument(
        "--task-result",
        choices=["done", "stage-complete", "blocked", "failed", "deferred"],
        default="stage-complete",
        help="Closeout result being prepared",
    )
    ap.add_argument("--no-ignored", action="store_true", help="Do not include ignored files in the auto-commit scan")
    ap.add_argument(
        "--auto-commit", action="store_true",
        help="Commit safe task-scoped files automatically when possible",
    )
    ap.add_argument(
        "--include-state", action="store_true",
        help="Include CodeRail persistence files in the task-scoped commit",
    )
    ap.add_argument("--commit-message", help="Commit message to use with --auto-commit")
    ap.add_argument("--commit-type", default="chore", help="Commit type for the default auto-commit message")
    args = ap.parse_args(argv)

    root = Path(args.target).resolve()
    found = done_gate.find_task(root, args.task)
    severe, warnings = [], []
    task_id = args.task or "(unknown)"
    coord = {}

    if not found:
        severe.append("task not found or no active task")
    else:
        header, body, status = found
        task_id = header.split()[0]
        coord = coordinate_check.parse_coordinate(body) or {}
        if not coord:
            severe.append(f"{task_id}: missing CodeRail Coordinate")
        elif not coordinate_check.explicit_rail(body):
            severe.append(f"{task_id}: Rail missing; write 'Rail: full' or 'Rail: light' explicitly")

    allowed = done_gate.split_patterns(coord.get("s_allowed", ""))
    forbidden = done_gate.split_patterns(coord.get("s_forbidden", ""))
    if coord and not allowed:
        severe.append(f"{task_id}: S allowed missing")

    entries = git_status_entries(root, include_ignored=not args.no_ignored)
    files = classify(entries, allowed, forbidden, include_state=args.include_state)
    if args.task_result not in {"done", "stage-complete"} and args.include_state:
        # Preserve the blocked/failed evidence without committing an attempted
        # implementation that has not reached a safe task boundary.
        state_safe = [path for path in files["safe"] if path in STATE_FILES]
        implementation_safe = [path for path in files["safe"] if path not in STATE_FILES]
        files["safe"] = state_safe
        files["outside"].extend(implementation_safe)
    if files["forbidden"]:
        severe.append(f"{task_id}: forbidden files are changed")
    if files["outside"]:
        warnings.append(f"{task_id}: changed files outside S allowed")

    handoff = read(root / "docs" / "HANDOFF.md")
    if handoff:
        if "Next Executable Step" not in handoff:
            warnings.append("HANDOFF.md should include Next Executable Step")
        if "Auto Commit" not in handoff:
            warnings.append("HANDOFF.md should include Auto Commit")

    dirty = bool([item for item in entries if item[0] != "!!"])
    unsafe_add_all = bool(files["forbidden"] or files["outside"] or files["ignored"])
    auto_commit_allowed = (
        dirty
        and bool(files["safe"])
        and not files["forbidden"]
        and not severe
        and (args.task_result in {"done", "stage-complete"} or args.include_state)
    )
    status_out = "blocked" if severe else ("warning" if warnings or unsafe_add_all else "ready")
    commit_message = args.commit_message or default_commit_message(task_id, args.task_result, args.commit_type)
    auto_action = "not requested"
    auto_detail = "run with --auto-commit to create a task-scoped commit"
    if args.auto_commit:
        if auto_commit_allowed:
            auto_action, auto_detail = auto_commit(root, files["safe"], commit_message)
            if auto_action == "failed":
                severe.append(f"{task_id}: auto commit failed")
                status_out = "blocked"
        elif severe or files["forbidden"]:
            auto_action = "blocked"
            auto_detail = "severe findings or forbidden file changes require resolution before auto-commit"
        elif not files["safe"]:
            auto_action = "skipped"
            auto_detail = "no safe task-scoped files to commit"
        else:
            auto_action = "skipped"
            auto_detail = "task result does not create an automatic commit boundary"

    print("# Closeout Check Report\n")
    print(f"Status: {status_out}")
    print(f"Task: {task_id}")
    print(f"Task result: {args.task_result}\n")
    print(f"Include CodeRail state: {yes_no(args.include_state)}")

    print("## Severe")
    print("- none" if not severe else "\n".join(f"- {x}" for x in severe))
    print("\n## Warnings")
    print("- none" if not warnings else "\n".join(f"- {x}" for x in warnings))

    print("\n## Auto Commit")
    print(f"- Eligible: {yes_no(auto_commit_allowed)}")
    print(f"- Action: {auto_action}")
    print(f"- Detail: {auto_detail}")
    print(f"- Message: {commit_message}")
    print(f"- Avoid git add .: {yes_no(unsafe_add_all)}")

    print("\n### Safe to stage")
    print(bullet(files["safe"]))
    print("\n### Exact files staged")
    print(bullet(files["safe"] if auto_action == "committed" else []))
    print("\n### Do not stage")
    do_not_stage = files["forbidden"] + files["outside"]
    print(bullet(do_not_stage))
    print("\n### Ignored/generated artifacts")
    print(bullet(files["ignored"]))

    print("\n## Next")
    if severe:
        print("- Do not stop as a clean closeout. Resolve severe findings or record a blocked handoff with a next executable step.")
    else:
        print("- Final response must include Closeout State, Auto Commit action, Handoff Trigger Check, and one Next Executable Step.")
    return 1 if severe else 0


if __name__ == "__main__":
    raise SystemExit(main())
