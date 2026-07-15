#!/usr/bin/env python3
"""Run the complete CodeRail stop boundary from one command."""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import drive_check  # noqa: E402
import task_switch  # noqa: E402


def run(label: str, script: str, root: Path, args: list[str] | None = None) -> int:
    command = [sys.executable, str(SCRIPTS / script), "--target", str(root), *(args or [])]
    print(f"\n# {label}\n")
    result = subprocess.run(command, cwd=str(root))
    return result.returncode


def run_report(label: str, script: str, root: Path, args: list[str] | None = None) -> tuple[int, str]:
    command = [sys.executable, str(SCRIPTS / script), "--target", str(root), *(args or [])]
    print(f"\n# {label}\n")
    result = subprocess.run(
        command,
        cwd=str(root),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.stdout:
        print(result.stdout, end="")
    return result.returncode, result.stdout or ""


def active_task(root: Path) -> str | None:
    tasks = drive_check.parse_tasks(root)
    task = next((item for item in tasks if item["status"] in {"[~]", "[!]"}), None)
    return task["id"] if task else None


def set_task_status(root: Path, task_id: str, status: str) -> bool:
    path = root / "docs" / "TASKS.md"
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(
        rf"(^##\s+{re.escape(task_id)}(?:\s+[^\n]*)?\n.*?^Status:\s*)\[[^]]+\]",
        re.M | re.S,
    )
    updated, count = pattern.subn(rf"\g<1>{status}", text, count=1)
    if count:
        path.write_text(updated, encoding="utf-8")
    return bool(count)


def update_completion(
    root: Path,
    task_id: str | None,
    task_result: str,
    harness_result: str,
    decision: dict,
    auto_action: str,
) -> bool:
    if not task_id:
        return False
    path = root / "docs" / "TASKS.md"
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False
    pattern = re.compile(
        rf"(^##\s+{re.escape(task_id)}(?:\s+[^\n]*)?\n.*?)(?=^##\s|\Z)",
        re.M | re.S,
    )
    match = pattern.search(text)
    if not match:
        return False
    block = match.group(1)
    level = "H0" if task_result == "done" else ("H3" if task_result in {"blocked", "failed", "deferred"} else "H1")
    values = {
        "Task result": task_result,
        "Harness result": harness_result,
        "Handoff level": level,
        "Handoff updated": "no",
        "Inspect status": "refreshed",
        "Drive decision": decision["decision"],
        "Resume anchor": f"docs/TASKS.md#{task_id}",
        "Next executable step": decision["next_action"],
        "Auto commit": auto_action,
    }
    for label, value in values.items():
        field = re.compile(rf"^({re.escape(label)}:)\s*.*$", re.I | re.M)
        block, count = field.subn(rf"\1 {value}", block, count=1)
        if not count:
            block += f"\n{label}: {value}\n"
    path.write_text(text[:match.start()] + block + text[match.end():], encoding="utf-8")
    return True


def append_verify_trace(root: Path, task_id: str | None, result: str, summary: str) -> int:
    if not task_id or result not in {"passed", "failed", "manual", "skipped"}:
        return 0
    return run(
        "Verification Trace",
        "trace_event.py",
        root,
        [
            "--type", "verify",
            "--task", task_id,
            "--status", "progress" if result in {"passed", "manual"} else "failed",
            "--harness-result", result,
            "--summary", summary,
            "--coordinate-task", task_id,
            "--verify", summary,
            "--persist", "TASKS,TRACE",
        ],
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Finish a CodeRail task and enforce the stop boundary")
    parser.add_argument("--target", default=".")
    parser.add_argument("--task", help="Task id; defaults to the active task")
    parser.add_argument(
        "--task-result",
        choices=["done", "stage-complete", "blocked", "failed", "deferred"],
        default="stage-complete",
    )
    parser.add_argument("--harness-result", choices=["passed", "failed", "manual", "skipped"])
    parser.add_argument("--manual-acceptance")
    parser.add_argument("--next-task-mode", choices=["recommend", "activate"])
    parser.add_argument("--skip-ci", action="store_true")
    parser.add_argument("--no-auto-commit", action="store_true")
    parser.add_argument("--commit-message", help="Override the auto-commit message")
    parser.add_argument("--pause-after", action="store_true",
                        help="After a stage-complete checkpoint, persist the source as [p] paused")
    args = parser.parse_args(argv)
    root = Path(args.target).resolve()

    if args.pause_after and args.task_result != "stage-complete":
        parser.error("--pause-after requires --task-result stage-complete")

    task_id = args.task or active_task(root)
    task_args = ["--task", task_id] if task_id else []
    evidence_args = []
    if args.harness_result:
        evidence_args += ["--harness-result", args.harness_result]
    if args.manual_acceptance:
        evidence_args += ["--manual-acceptance", args.manual_acceptance]

    failures = 0
    failures += bool(run("TDD Gate", "tdd_check.py", root))
    ci_rc = 0
    if not args.skip_ci:
        ci_rc = run("CI Gate", "ci_gate.py", root)
        failures += bool(ci_rc)

    verification = args.harness_result
    if not verification:
        verification = "passed" if ci_rc == 0 and not args.skip_ci else "skipped"
    failures += bool(append_verify_trace(
        root,
        task_id,
        verification,
        "finish_task verification boundary",
    ))
    if task_id:
        failures += bool(run("Trace Index", "trace_index.py", root))

    done_rc = 0
    task_marked_done = False  # FN-027: track the actual close, for honest reporting
    if args.task_result == "done":
        done_evidence = list(evidence_args)
        if not args.harness_result and verification:
            done_evidence += ["--harness-result", verification]
        done_rc = run(
            "Done Gate",
            "done_gate.py",
            root,
            task_args + done_evidence,
        )
        failures += bool(done_rc)
        if done_rc == 0:
            preflight_rc, preflight_output = run_report(
                "Closeout Preflight", "closeout_check.py", root,
                task_args + ["--task-result", "done", "--include-state", "--preflight"],
            )
            if preflight_rc:
                print(preflight_output)
                print("Closeout preflight refused to close the task; resolve the exact paths above.")
                failures += 1
                done_rc = preflight_rc
        if done_rc == 0:
            if task_id and not set_task_status(root, task_id, "[x]"):
                print(f"Could not mark {task_id} done in docs/TASKS.md", file=sys.stderr)
                failures += 1
            else:
                task_marked_done = bool(task_id)
    elif args.pause_after:
        if task_id and not set_task_status(root, task_id, "[p]"):
            print(f"Could not mark {task_id} paused in docs/TASKS.md", file=sys.stderr)
            failures += 1

    # Drive is evaluated from the task state. Closeout remains the authority for
    # changed-file scope and performs the final task-scoped commit below.
    activated_task = None
    decision = drive_check.evaluate(
        root,
        harness_result=args.harness_result or "",
        changed_files=[],
        next_task_mode=args.next_task_mode,
    )
    if decision["decision"] == "ADVANCE" and decision["next_task_mode"] == "activate":
        next_task = decision["recommended_task"]
        if next_task and set_task_status(root, next_task, "[~]"):
            activated_task = next_task
            decision = drive_check.evaluate(
                root,
                harness_result=args.harness_result or "",
                changed_files=[],
                next_task_mode=args.next_task_mode,
            )
            decision["evidence"].append(f"activated={next_task}")
        else:
            failures += 1
            decision["next_action"] = f"Failed to activate {next_task}; repair TASKS.md before stopping."

    auto_action = "disabled" if args.no_auto_commit else "requested"
    update_completion(root, task_id, args.task_result, verification, decision, auto_action)
    run("Inspect", "inspect_state.py", root, ["--write"])

    if args.task_result != "done" or task_marked_done:
        closeout_args = task_args + ["--task-result", args.task_result]
        if not args.no_auto_commit:
            closeout_args.append("--auto-commit")
        if args.commit_message:
            closeout_args += ["--commit-message", args.commit_message]
        closeout_args.append("--include-state")
        closeout_rc, closeout_output = run_report("Closeout", "closeout_check.py", root, closeout_args)
        failures += bool(closeout_rc)
        action_match = re.search(r"^- Action: (committed|skipped|blocked|failed|not requested)$", closeout_output, re.M)
        actual_auto_action = action_match.group(1) if action_match else auto_action
    else:
        actual_auto_action = "blocked"

    if failures and task_marked_done and task_id:
        set_task_status(root, task_id, "[!]")
        task_switch.clear_closed_pending(root, task_id)
        task_marked_done = False
        print(f"Atomic closeout compensation: reopened {task_id} as [!] because a post-mark step failed.")

    print("\n" + drive_check.render_human(decision))
    print("\n# Finish Task Report\n")
    # FN-027: the verdict must match what actually happened. If the task WAS
    # closed (and possibly committed), never report it as simply "blocked" -
    # that leads callers to "run done again", which can only produce
    # "no active task" once the task is [x].
    if failures and task_marked_done:
        print(f"Closeout state: {args.task_result} (WITH ERRORS)")
        print(f"NOTE: {task_id} WAS marked done in docs/TASKS.md and the commit")
        print("step ran. Do NOT rerun done for this task. Investigate the failed")
        print("check(s) above, then audit the ledger:  coderail progress")
    else:
        print(f"Closeout state: {'blocked' if failures else args.task_result}")
    print(f"May stop: {'yes' if decision['may_stop'] and not failures else 'no'}")
    print(f"Next task mode: {decision['next_task_mode']}")
    print(f"Activated task: {activated_task or 'none'}")
    print(f"Recommended task: {decision['recommended_task'] or 'none'}")
    print(f"Next executable step: {decision['next_action']}")
    print(f"Auto Commit action: {actual_auto_action}")
    handoff_level = (
        "H0" if args.task_result == "done"
        else "H3" if args.task_result in {"blocked", "failed", "deferred"}
        else "H1"
    )
    print(f"Handoff Trigger Check: {handoff_level} (HANDOFF updated: no)")

    if failures:
        return 1
    if decision["mode"] == "continuous" and not decision["may_stop"]:
        print("Continuous Drive is non-terminal. The agent must continue and may not end its response.")
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
