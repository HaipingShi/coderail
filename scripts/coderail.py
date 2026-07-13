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
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent

# Advanced/legacy commands, kept for compatibility and power users.
ADVANCED = {
    "blueprint": "blueprint_check.py",
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
ACTIVE_RE = re.compile(r"^##\s+(T-\d+)[^\n]*\n(?:(?!^##\s).)*?^Status:\s*\[~\]", re.M | re.S)

LIGHT_HINTS = ["doc", "readme", "note", "design", "research", "adr", "写文档", "笔记", "调研", "设计稿"]

MINIMAL_TASKS = """# Tasks

## Status legend

- `[ ]` todo
- `[~]` doing
- `[!]` blocked
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
        status_m = re.search(r"^Status:\s*(\[[ ~!x]\])", body, re.M)
        tasks.append({
            "id": m.group(1),
            "title": m.group(2).strip(),
            "status": status_m.group(1) if status_m else "[ ]",
        })
    return tasks


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
        rf"(^##\s+{re.escape(task_id)}\b(?:(?!^##\s).)*?^Status:\s*)\[ \]",
        re.M | re.S,
    )
    new, n = block.subn(r"\g<1>[~]", text)
    if n:
        path.write_text(new, encoding="utf-8")
    return bool(n)


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

    active = active_task_id(text)
    if active and not args.force:
        print(f"You already have an active task: {active}.")
        print(f"Finish it first with:  coderail done")
        print(f"Or start anyway with: coderail start ... --force")
        return 1

    task_id = next_task_id(text)
    title = args.title.strip()
    goal = (args.goal or title).strip()
    done_when = (args.done_when or "Manually confirm the result works as intended.").strip()
    files = [f.strip() for f in (args.files or "").split(",") if f.strip()]
    avoid = [f.strip() for f in (args.avoid or "").split(",") if f.strip()]
    task_type = (args.type or "feature").strip().lower()
    rail = guess_rail(title, goal, task_type)

    allowed_lines = "\n".join(f"  - {f}" for f in files) if files else "  - to be decided while working"
    forbidden_lines = "\n".join(f"  - {f}" for f in avoid) if avoid else "  - none"

    block = f"""
## {task_id} {title}

Status: [~]
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
- {done_when}

X — Stop
- Stop and ask if changes are needed outside the allowed files.

P — Persist
- TASKS, TRACE
"""
    path = tasks_path(root)
    path.write_text(text.rstrip() + "\n" + block, encoding="utf-8")

    print(f"Started task {task_id}: {title}")
    print(f"  Goal:      {goal}")
    print(f"  Files:     {', '.join(files) if files else 'decide while working'}")
    print(f"  Done when: {done_when}")
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
        print(f"Active task: {active}")
    else:
        print("Active task: none (start one with:  coderail start \"...\")")
    queued = [t for t in list_tasks(text) if t["status"] == "[ ]"]
    if queued:
        print(f"Queued: {len(queued)} task(s), next would be {queued[0]['id']} {queued[0]['title']}")

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

def cmd_done(args) -> int:
    root = Path(args.target).resolve()
    extra = []
    if args.task:
        extra += ["--task", args.task]
    extra += ["--task-result", args.result]
    if args.harness_result:
        extra += ["--harness-result", args.harness_result]
    if args.manual_acceptance:
        extra += ["--manual-acceptance", args.manual_acceptance]
    if args.no_commit:
        extra += ["--no-auto-commit"]

    rc, _ = run_script("finish_task.py", root, extra)

    print()
    if rc == 0:
        print("Task closed. Docs updated, checks passed, safe files committed.")
        print_next_recommendation(root)
    elif rc == 3:
        print("This project runs in continuous mode: keep going with the next step above.")
    else:
        print("Not finished yet - one or more checks did not pass (details above).")
        print("Fix what it points out, then run:  coderail done   again.")
    return rc


# ---------------------------------------------------------------- next

def cmd_next(args) -> int:
    root = Path(args.target).resolve()
    text = read_tasks(root)

    active = active_task_id(text)
    if active:
        print(f"You already have an active task: {active}.")
        print("Finish it first with:  coderail done")
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

    if activate_task(root, todo["id"]):
        print(f"Now working on {todo['id']}: {todo['title']}")
        print("Details are in docs/TASKS.md. When finished, run:  coderail done")
        return 0

    print(f"Could not activate {todo['id']}. Check docs/TASKS.md formatting.")
    return 1


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
    p_start.add_argument("--files", help="Files/folders you expect to touch, comma separated")
    p_start.add_argument("--avoid", help="Files/folders that must NOT change, comma separated")
    p_start.add_argument("--done-when", help="How you will know it is finished")
    p_start.add_argument("--type", help="feature | bug | refactor | docs (default: feature)")
    p_start.add_argument("--force", action="store_true", help="Start even if another task is active")
    p_start.add_argument("--target", default=".")

    p_check = sub.add_parser("check", help="Am I on track? What's missing?")
    p_check.add_argument("--target", default=".")

    p_next = sub.add_parser("next", help="Recommend (or pick up) the next queued task")
    p_next.add_argument("--go", action="store_true", help="Activate the recommended task")
    p_next.add_argument("--target", default=".")

    p_done = sub.add_parser("done", help="Finish the current task safely")
    p_done.add_argument("--task", help="Task id (defaults to the active task)")
    p_done.add_argument("--result", default="done",
                        choices=["done", "stage-complete", "blocked", "failed", "deferred"],
                        help="How the task ended (default: done)")
    p_done.add_argument("--harness-result", choices=["passed", "failed", "manual", "skipped"])
    p_done.add_argument("--manual-acceptance", help="One sentence: how you manually confirmed it works")
    p_done.add_argument("--no-commit", action="store_true", help="Do not auto-commit")
    p_done.add_argument("--target", default=".")

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
    if args.command == "done":
        return cmd_done(args)

    parser.print_help()
    print("\nAdvanced commands: " + ", ".join(sorted(ADVANCED)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
