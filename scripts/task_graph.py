#!/usr/bin/env python3
"""Task dependency registration and validation."""
from __future__ import annotations

import json
import re
from pathlib import Path


RELATIONS = ("depends_on", "blocks", "supersedes")
LABELS = {
    "depends_on": "Depends on",
    "blocks": "Blocks",
    "supersedes": "Supersedes",
}


def split_refs(values) -> list[str]:
    if not values:
        return []
    if isinstance(values, str):
        values = [values]
    result: list[str] = []
    for value in values:
        for item in str(value).split(","):
            ref = item.strip().upper()
            if ref and ref not in result:
                result.append(ref)
    return result


def load_meta(root: Path) -> dict:
    try:
        return json.loads((root / ".coderail" / "tasks.json").read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def save_meta(root: Path, meta: dict) -> None:
    path = root / ".coderail" / "tasks.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def known_task_ids(root: Path, meta: dict | None = None) -> set[str]:
    ids = set((meta or load_meta(root)).keys())
    for rel in ("docs/TASKS.md", "docs/PROGRESS.md", "docs/TRACELOG.jsonl"):
        path = root / rel
        if path.exists():
            ids.update(re.findall(r"\bT-\d+\b", path.read_text(encoding="utf-8", errors="ignore")))
    return {task_id for task_id in ids if re.fullmatch(r"T-\d+", task_id)}


def relations(meta: dict, task_id: str) -> dict[str, list[str]]:
    stored = meta.get(task_id, {}).get("relations", {})
    return {relation: split_refs(stored.get(relation)) for relation in RELATIONS}


def dependency_graph(meta: dict) -> dict[str, set[str]]:
    graph = {task_id: set() for task_id in meta}
    for task_id in meta:
        row = relations(meta, task_id)
        graph.setdefault(task_id, set()).update(row["depends_on"])
        for blocked in row["blocks"]:
            graph.setdefault(blocked, set()).add(task_id)
    return graph


def cycles(meta: dict) -> list[list[str]]:
    graph = dependency_graph(meta)
    found: list[list[str]] = []
    visiting: list[str] = []
    visited: set[str] = set()

    def walk(node: str) -> None:
        if node in visiting:
            start = visiting.index(node)
            cycle = visiting[start:] + [node]
            if cycle not in found:
                found.append(cycle)
            return
        if node in visited:
            return
        visiting.append(node)
        for dependency in sorted(graph.get(node, set())):
            walk(dependency)
        visiting.pop()
        visited.add(node)

    for task_id in sorted(graph):
        walk(task_id)
    return found


def validate(meta: dict, known: set[str]) -> list[str]:
    problems: list[str] = []
    for task_id in sorted(meta):
        for relation, targets in relations(meta, task_id).items():
            for target in targets:
                if target == task_id:
                    problems.append(f"{task_id}: {relation} cannot reference itself")
                elif target not in known:
                    problems.append(f"{task_id}: {relation} references missing task {target}")
    for cycle in cycles(meta):
        problems.append("dependency cycle: " + " -> ".join(cycle))
    return problems


def with_relation(
    meta: dict,
    source: str,
    relation: str,
    targets: list[str],
) -> dict:
    if relation not in RELATIONS:
        raise ValueError(f"unsupported task relation {relation!r}")
    updated = json.loads(json.dumps(meta))
    row = updated.setdefault(source, {}).setdefault("relations", {})
    row[relation] = list(dict.fromkeys(split_refs(row.get(relation)) + split_refs(targets)))
    return updated


def validate_add(
    root: Path,
    source: str,
    relation: str,
    targets: list[str],
    *,
    allow_source_new: bool = False,
) -> tuple[dict, list[str]]:
    meta = load_meta(root)
    known = known_task_ids(root, meta)
    if allow_source_new:
        known.add(source)
    if source not in known:
        return meta, [f"source task {source} does not exist"]
    updated = with_relation(meta, source, relation, targets)
    return updated, validate(updated, known)


def completed_task_ids(root: Path) -> set[str]:
    result: set[str] = set()
    progress = root / "docs" / "PROGRESS.md"
    if progress.exists():
        result.update(re.findall(r"\bT-\d+\b", progress.read_text(encoding="utf-8", errors="ignore")))
    trace = root / "docs" / "TRACELOG.jsonl"
    if trace.exists():
        for raw in trace.read_text(encoding="utf-8", errors="ignore").splitlines():
            try:
                event = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if event.get("type") == "task" and event.get("status") == "done" and event.get("task"):
                result.add(str(event["task"]))
    return result


def unresolved_dependencies(root: Path, task_id: str) -> list[str]:
    meta = load_meta(root)
    done = completed_task_ids(root)
    return [dep for dep in relations(meta, task_id)["depends_on"] if dep not in done]


def render_relation_section(row: dict[str, list[str]]) -> str:
    lines = ["### Task Relations", ""]
    for relation in RELATIONS:
        values = row.get(relation) or []
        lines.append(f"- {LABELS[relation]}: {', '.join(values) if values else 'none'}")
    return "\n".join(lines) + "\n"


def sync_task_block(root: Path, task_id: str, row: dict[str, list[str]]) -> None:
    path = root / "docs" / "TASKS.md"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    match = re.search(
        rf"(^##\s+{re.escape(task_id)}\b.*?)(?=^##\s|\Z)",
        text,
        re.M | re.S,
    )
    if not match:
        return
    block = match.group(1)
    section = render_relation_section(row)
    existing = re.search(r"^### Task Relations\s*$.*?(?=^###\s|\Z)", block, re.M | re.S)
    if existing:
        block = block[:existing.start()] + section + "\n" + block[existing.end():].lstrip()
    else:
        block = block.rstrip() + "\n\n" + section
    path.write_text(text[:match.start()] + block + text[match.end():], encoding="utf-8")
