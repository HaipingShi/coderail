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


def append_progress(root: Path, task_id: str, title: str, verified: str, next_hint: str) -> None:
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
        f"- Checked by: {verified or 'see task record'}\n"
        f"- Next: {next_hint}\n"
    )
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
    print()
    print("== Now tell the user, in their language, no jargon ==")
    print(f"  1. What can they see or do now that they couldn't before?")
    print(f"     (task was: {title})")
    print(f"  2. How do you know it works?")
    print(f"     (evidence: {verified or 'state it plainly'})")
    print(f"  3. What do you suggest next, and is any decision needed from them?")
    print("  Rules: 3-6 sentences total. No file paths, no tool names,")
    print("  no framework talk unless the user asks. If they must decide")
    print("  something, make it a clear either/or question.")


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

    created = []
    for did in todo_ids:
        title, mermaid = MERMAID_STUBS[did]
        stub_path = bp_dir / f"{did.lower()}.md"
        if not stub_path.exists():
            stub_path.write_text(
                f"# {title} ({did})\n\n"
                f"Status: draft scaffold - replace the placeholder shapes with this\n"
                f"project's real structure, then set the index row to `current`.\n\n"
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
    """Files touched in >= SPIN_CHURN_THRESHOLD of the last SPIN_CHURN_COMMITS commits."""
    try:
        result = subprocess.run(
            ["git", "log", f"-{SPIN_CHURN_COMMITS}", "--name-only", "--pretty=format:"],
            cwd=str(root), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, encoding="utf-8", errors="replace",
        )
    except OSError:
        return []
    if result.returncode != 0:
        return []
    counts: dict[str, int] = {}
    for name in result.stdout.splitlines():
        name = name.strip()
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

    tasks_text_before = read_tasks(root)
    task_before = args.task or active_task_id(tasks_text_before)

    rc, _ = run_script("finish_task.py", root, extra)

    print()
    if rc == 0:
        if task_before:
            bump_spin_state(root, task_before, reset=True)
        print("Task closed. Docs updated, checks passed, safe files committed.")

        title = verified = ""
        if task_before:
            tasks = list_tasks(tasks_text_before)
            title = next((t["title"] for t in tasks if t["id"] == task_before), "")
            verified = (
                args.manual_acceptance
                or task_field(tasks_text_before, task_before, "V")
            )
            todo = next_todo_task(read_tasks(root))
            next_hint = f"{todo['id']} {todo['title']}" if todo else "decide with the user"
            append_progress(root, task_before, title or task_before, verified, next_hint)
            print("Progress journal updated: docs/PROGRESS.md")

        print_blueprint_notice(root)
        print_next_recommendation(root)
        if task_before:
            print_user_report_scaffold(task_before, title or task_before, verified)
    elif rc == 3:
        print("This project runs in continuous mode: keep going with the next step above.")
    else:
        if task_before:
            bump_spin_state(root, task_before)
        print("Not finished yet - one or more checks did not pass (details above).")
        print("Fix what it points out, then run:  coderail done   again.")
        text = read_tasks(root)
        print_spin_report(root, active_task_id(text), list_tasks(text))
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
    if args.command == "blueprint":
        return cmd_blueprint(args)
    if args.command == "done":
        return cmd_done(args)

    parser.print_help()
    print("\nAdvanced commands: " + ", ".join(sorted(ADVANCED)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
