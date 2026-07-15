#!/usr/bin/env python3
"""Shared Task Switch Gate state, fingerprint, and recovery helpers."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

import repository_state


ACTIVE_STATUSES = {"[~]", "[!]"}


def _matches(path: str, patterns: list[str]) -> bool:
    return repository_state.matches_any(path, patterns)


def _git(root: Path, args: list[str], *, text: bool = True):
    return repository_state._git(root, args, text=text)


def git_status_entries(root: Path, include_ignored: bool = False) -> list[dict]:
    """Compatibility projection of the canonical repository snapshot."""
    return repository_state.as_legacy_entries(
        repository_state.capture(root, include_ignored=include_ignored)
    )


def fingerprint_path(root: Path, relative: str) -> str:
    return repository_state.fingerprint_path(root, relative)


def snapshot_dirty(root: Path) -> dict:
    snapshot = repository_state.capture(root, fingerprints=True)
    return {
        "captured_at": snapshot.captured_at,
        "head": snapshot.head,
        "files": repository_state.as_legacy_entries(snapshot),
    }


def build_baseline_adoption(root: Path, allowed: list[str], forbidden: list[str]) -> dict:
    """Record an auditable, content-free manifest for an unborn repository."""
    head = _git(root, ["rev-parse", "HEAD"])
    if head.returncode == 0:
        raise ValueError("--adopt-baseline is only valid before the first Git commit")
    files = []
    for row in git_status_entries(root):
        path = row["path"]
        disposition = "allowed" if _matches(path, allowed) else "outside"
        if _matches(path, forbidden):
            disposition = "forbidden"
        files.append({**row, "fingerprint": fingerprint_path(root, path),
                      "disposition": disposition})
    return {"captured_at": datetime.now(timezone.utc).isoformat(), "head": None,
            "files": files}


def _meta_path(root: Path) -> Path:
    return root / ".coderail" / "tasks.json"


def load_meta(root: Path) -> dict:
    try:
        return json.loads(_meta_path(root).read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError, OSError):
        return {}


def save_meta(root: Path, meta: dict) -> None:
    path = _meta_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def unchanged_baseline_paths(root: Path, task_id: str | None) -> set[str]:
    if not task_id:
        return set()
    entry = load_meta(root).get(task_id, {})
    baseline = entry.get("baseline", {}).get("files", [])
    adoption_files = entry.get("baseline_adoption", {}).get("files", [])
    adopted = {row.get("path") for row in adoption_files
               if row.get("disposition") == "allowed"}
    adoption_sensitive = {row.get("path") for row in adoption_files
                          if _matches(row.get("path", ""),
                                      [".env", ".env.*", "*.pem", "*.key", "*.p12", "*.pfx"])}
    current = {row["path"]: row for row in git_status_entries(root)}
    unchanged = set()
    for original in baseline:
        if original.get("path") in adopted or original.get("path") in adoption_sensitive:
            continue
        row = current.get(original.get("path"))
        if not row or row.get("status") != original.get("status"):
            continue
        if fingerprint_path(root, row["path"]) == original.get("fingerprint"):
            unchanged.add(row["path"])
    return unchanged


def active_task_ids(tasks_text: str) -> list[str]:
    ids = []
    pattern = re.compile(
        r"^##\s+(T-\d+)\b(?:(?!^##\s).)*?^Status:\s*(\[[^]]+\])",
        re.M | re.S,
    )
    for match in pattern.finditer(tasks_text):
        if match.group(2) in ACTIVE_STATUSES:
            ids.append(match.group(1))
    return ids


def closed_pending_paths(root: Path) -> list[tuple[str, str]]:
    current = {row["path"] for row in git_status_entries(root) if row["status"] != "!!"}
    pending = []
    for owner, entry in load_meta(root).items():
        for row in entry.get("closed_pending", {}).get("files", []):
            path = row.get("path")
            if path in current:
                pending.append((owner, path))
    return pending


def activation_preflight(root: Path, tasks_text: str, dirty_fork: bool = False) -> dict:
    active = active_task_ids(tasks_text)
    if active:
        return {
            "allowed": False,
            "reason": "active-task",
            "active": active,
            "paths": [],
        }
    pending = closed_pending_paths(root)
    if pending and not dirty_fork:
        return {
            "allowed": False,
            "reason": "closed-dirty",
            "active": [],
            "paths": pending,
        }
    return {
        "allowed": True,
        "reason": "dirty-fork" if pending else "clean-owner",
        "active": [],
        "paths": pending,
        "baseline": snapshot_dirty(root),
    }


def consume_closed_pending(root: Path) -> None:
    meta = load_meta(root)
    changed = False
    for entry in meta.values():
        if "closed_pending" in entry:
            del entry["closed_pending"]
            changed = True
    if changed:
        save_meta(root, meta)


def clear_closed_pending(root: Path, task_id: str) -> None:
    meta = load_meta(root)
    entry = meta.get(task_id, {})
    if "closed_pending" in entry:
        del entry["closed_pending"]
        save_meta(root, meta)


def record_closed_pending(root: Path, task_id: str, files: list[dict]) -> None:
    if not files:
        return
    meta = load_meta(root)
    entry = meta.setdefault(task_id, {})
    entry["closed_pending"] = {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "files": files,
    }
    save_meta(root, meta)


def pause_task(root: Path, task_id: str, reason: str) -> bool:
    path = root / "docs" / "TASKS.md"
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(
        rf"(^##\s+{re.escape(task_id)}\b(?:(?!^##\s).)*?^Status:\s*)\[(?:~|!)\]",
        re.M | re.S,
    )
    updated, count = pattern.subn(r"\g<1>[p]", text, count=1)
    if not count:
        return False
    block_pattern = re.compile(
        rf"(^##\s+{re.escape(task_id)}\b(?:(?!^##\s).)*)(?=^##\s|\Z)",
        re.M | re.S,
    )
    match = block_pattern.search(updated)
    if match:
        block = match.group(1).rstrip()
        block += (
            f"\nPause reason: {reason}\n"
            f"Resume command: coderail switch --to {task_id}\n\n"
        )
        updated = updated[:match.start()] + block + updated[match.end():]
    path.write_text(updated, encoding="utf-8")
    meta = load_meta(root)
    entry = meta.setdefault(task_id, {})
    entry["pause"] = {
        "reason": reason,
        "paused_at": datetime.now(timezone.utc).isoformat(),
        "resume": f"coderail switch --to {task_id}",
    }
    save_meta(root, meta)
    return True


def resume_task(root: Path, task_id: str) -> bool:
    path = root / "docs" / "TASKS.md"
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(
        rf"(^##\s+{re.escape(task_id)}\b(?:(?!^##\s).)*?^Status:\s*)\[(?:p|r| )\]",
        re.M | re.S,
    )
    updated, count = pattern.subn(r"\g<1>[~]", text, count=1)
    if count:
        path.write_text(updated, encoding="utf-8")
    return bool(count)


def write_h3_handoff(root: Path, task_id: str, reason: str) -> None:
    dirty = snapshot_dirty(root)["files"]
    paths = "\n".join(f"- `{row['path']}` ({row['status']})" for row in dirty) or "- none"
    text = f"""# Handoff

Handoff Level: H3
Task: {task_id}
Reason: {reason}

## Coordinate Summary

- Current owner remains `{task_id}`.
- No implementation commit was created by the failed switch.
- No destination task was activated.

## Dirty Paths

{paths}

## Decision Required

- Continue current: `coderail switch --continue-current`
- Carry a fingerprinted dirty baseline: `coderail switch \"new task\" --dirty-fork`

## Auto Commit

- Action: not requested
- Automatic push: never

## Next Executable Step

- Choose exactly one command from Decision Required.
"""
    path = root / "docs" / "HANDOFF.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
