#!/usr/bin/env python3
"""Shared Task Switch Gate state, fingerprint, and recovery helpers."""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ACTIVE_STATUSES = {"[~]", "[!]"}


def _git(root: Path, args: list[str], *, text: bool = True):
    return subprocess.run(
        ["git", "-C", str(root), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=text,
        encoding="utf-8" if text else None,
        errors="surrogateescape" if text else None,
    )


def git_status_entries(root: Path, include_ignored: bool = False) -> list[dict]:
    """Return unquoted porcelain entries, including paths containing spaces."""
    args = ["status", "--porcelain=v1", "-z", "--untracked-files=all"]
    if include_ignored:
        args.append("--ignored=matching")
    result = _git(root, args, text=False)
    if result.returncode != 0:
        return []
    records = (result.stdout or b"").split(b"\0")
    entries: list[dict] = []
    index = 0
    while index < len(records):
        raw = records[index]
        index += 1
        if len(raw) < 4:
            continue
        status = raw[:2].decode("ascii", errors="replace")
        path = os.fsdecode(raw[3:]).replace("\\", "/")
        row = {"status": status, "path": path}
        if ("R" in status or "C" in status) and index < len(records):
            original = records[index]
            index += 1
            if original:
                row["original_path"] = os.fsdecode(original).replace("\\", "/")
        entries.append(row)
    return entries


def fingerprint_path(root: Path, relative: str) -> str:
    path = root / relative
    if not path.exists() and not path.is_symlink():
        return "missing"
    digest = hashlib.sha256()
    if path.is_symlink():
        digest.update(b"symlink\0")
        digest.update(os.readlink(path).encode("utf-8", errors="surrogateescape"))
        return digest.hexdigest()
    if path.is_dir():
        digest.update(b"directory\0")
        for child in sorted(p.relative_to(path).as_posix() for p in path.rglob("*")):
            digest.update(child.encode("utf-8", errors="surrogateescape") + b"\0")
        return digest.hexdigest()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def snapshot_dirty(root: Path) -> dict:
    files = []
    for row in git_status_entries(root):
        if row["status"] == "!!":
            continue
        item = dict(row)
        item["fingerprint"] = fingerprint_path(root, row["path"])
        files.append(item)
    head = _git(root, ["rev-parse", "HEAD"])
    return {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "head": head.stdout.strip() if head.returncode == 0 else None,
        "files": files,
    }


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
    baseline = load_meta(root).get(task_id, {}).get("baseline", {}).get("files", [])
    current = {row["path"]: row for row in git_status_entries(root)}
    unchanged = set()
    for original in baseline:
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
