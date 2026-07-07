#!/usr/bin/env python3
"""Append a trace event to docs/TRACELOG.jsonl.

Standard library only. Auto-generates an event id (TR-YYYYMMDD-HHMMSS-XXXX) and
an ISO timestamp. Supports both CLI flags and --from-file JSON input.

Schema reference: references/TRACE_GRAPH.md
"""
from __future__ import annotations

import argparse
import json
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path

VALID_TYPES = {
    "intent", "align", "task", "decision", "research", "attempt",
    "change", "verify", "handoff", "lesson",
}
EDGE_KEYS = [
    "serves", "derived_from", "implements", "modifies", "validated_by",
    "depends_on", "supersedes", "blocks", "relates_to",
]


def make_id(now: datetime | None = None) -> str:
    now = now or datetime.now(timezone.utc)
    suffix = secrets.token_hex(2)
    return f"TR-{now.strftime('%Y%m%d-%H%M%S')}-{suffix}"


def _split_list(value):
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        return [v for v in value if v]
    parts = [p.strip() for p in str(value).split(",")]
    return [p for p in parts if p]


def build_event(args) -> dict:
    """Build a trace event dict from parsed args. Raises ValueError on invalid input."""
    etype = args.type
    if etype not in VALID_TYPES:
        raise ValueError(f"invalid --type {etype!r}; one of {sorted(VALID_TYPES)}")

    now = datetime.now(timezone.utc)
    event = {
        "id": args.id or make_id(now),
        "ts": args.ts or now.isoformat(timespec="seconds"),
        "type": etype,
        "summary": args.summary or "",
    }

    optional_scalars = {
        "task": args.task,
        "north_star": args.north_star,
        "status": args.status,
        "source_kind": args.source_kind,
        "source_ref": args.source_ref,
        "harness_command": args.harness_command,
        "harness_result": args.harness_result,
        "commit": args.commit,
    }
    for key, val in optional_scalars.items():
        if val:
            event[key] = val

    files = _split_list(args.files)
    if files:
        event["files"] = files

    for edge in EDGE_KEYS:
        cli_attr = edge.replace("_", "-")
        val = getattr(args, cli_attr, None)
        lst = _split_list(val)
        if lst:
            event[edge] = lst

    coordinate = _build_coordinate(args)
    if coordinate is not None:
        event["coordinate"] = coordinate

    # Type-specific rules.
    if etype == "change":
        has_anchor = bool(event.get("task") or event.get("north_star") or event.get("files"))
        if not has_anchor:
            raise ValueError(
                "change event must have at least one of --task, --north-star, --files"
            )
    if etype == "verify":
        if not event.get("harness_result"):
            raise ValueError("verify event must have --harness-result")

    return event


def _build_coordinate(args) -> dict | None:
    has_any = any([
        args.goal, args.coordinate_task,
        args.scope_allowed, args.scope_forbidden,
        args.verify, args.stop, args.persist,
    ])
    if not has_any:
        return None
    coord = {}
    if args.goal:
        coord["goal"] = args.goal
    if args.coordinate_task:
        coord["task"] = args.coordinate_task
    scope = {}
    allowed = _split_list(args.scope_allowed)
    forbidden = _split_list(args.scope_forbidden)
    if allowed:
        scope["allowed"] = allowed
    if forbidden:
        scope["forbidden"] = forbidden
    if scope:
        coord["scope"] = scope
    if args.verify:
        coord["verify"] = _split_list(args.verify) or [args.verify]
    if args.stop:
        coord["stop"] = _split_list(args.stop) or [args.stop]
    if args.persist:
        coord["persist"] = _split_list(args.persist) or [args.persist]
    return coord


def append_event(target: Path, event: dict) -> Path:
    docs = target / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    log = docs / "TRACELOG.jsonl"
    with log.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=False, sort_keys=False) + "\n")
    return log


def _load_from_file(path: Path) -> argparse.Namespace:
    data = json.loads(path.read_text(encoding="utf-8"))
    ns = argparse.Namespace()
    for key in ["id", "ts", "type", "summary", "task", "north_star", "status",
                "source_kind", "source_ref", "files", "harness_command",
                "harness_result", "commit", "goal", "coordinate_task",
                "scope_allowed", "scope_forbidden", "verify", "stop", "persist"]:
        attr = key if "_" in key and key not in ("scope_allowed", "scope_forbidden", "coordinate_task") else key
        setattr(ns, attr, data.get(key))
    for edge in EDGE_KEYS:
        setattr(ns, edge.replace("_", "-"), data.get(edge))
    return ns


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Append a trace event to docs/TRACELOG.jsonl")
    parser.add_argument("--target", default=".", help="Repository root containing docs/")
    parser.add_argument("--type", required=True, choices=sorted(VALID_TYPES))
    parser.add_argument("--summary", help="1-3 line summary of the event")
    parser.add_argument("--task", help="Task id, e.g. T-001")
    parser.add_argument("--north-star", help="North star id, e.g. NS-001")
    parser.add_argument("--status", help="open | accepted | rejected | superseded | blocked | done")
    parser.add_argument("--source-kind", help="user | agent | ci | external")
    parser.add_argument("--source-ref", help="Reference to the source (chat id, url, file)")
    parser.add_argument("--files", help="Comma-separated modified files")
    parser.add_argument("--serves", help="Comma-separated north star ids served")
    parser.add_argument("--derived-from", help="Comma-separated event/source ids")
    parser.add_argument("--implements", help="Comma-separated task ids implemented")
    parser.add_argument("--modifies", help="Comma-separated files/assets modified")
    parser.add_argument("--validated-by", help="Comma-separated verify/task ids")
    parser.add_argument("--depends-on", help="Comma-separated ids depended on")
    parser.add_argument("--supersedes", help="Comma-separated ids superseded")
    parser.add_argument("--blocks", help="Comma-separated ids blocked")
    parser.add_argument("--relates-to", help="Comma-separated ids related")
    parser.add_argument("--harness-command", help="Harness command run")
    parser.add_argument("--harness-result", help="passed | failed | skipped | manual")
    parser.add_argument("--commit", help="Commit sha if available")
    parser.add_argument("--id", help="Override the auto-generated event id")
    parser.add_argument("--ts", help="Override the auto-generated ISO timestamp")
    # CodeRail Coordinate fields.
    parser.add_argument("--goal", help="Coordinate G: which North Star outcome this serves")
    parser.add_argument("--coordinate-task", dest="coordinate_task", help="Coordinate T: the exact task")
    parser.add_argument("--scope-allowed", help="Coordinate S allowed, comma-separated")
    parser.add_argument("--scope-forbidden", help="Coordinate S forbidden, comma-separated")
    parser.add_argument("--verify", help="Coordinate V: harness/test/manual acceptance")
    parser.add_argument("--stop", help="Coordinate X: stop conditions")
    parser.add_argument("--persist", help="Coordinate P: assets to update, comma-separated")
    parser.add_argument("--from-file", help="Read event fields from a JSON file")
    args = parser.parse_args(argv)

    if args.from_file:
        file_ns = _load_from_file(Path(args.from_file))
        # CLI flags take precedence over the file where both are present.
        for key in dir(args):
            if key.startswith("_"):
                continue
            val = getattr(args, key)
            if val is None and hasattr(file_ns, key):
                setattr(args, key, getattr(file_ns, key))
        if not args.type:
            args.type = file_ns.type

    try:
        event = build_event(args)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    target = Path(args.target).resolve()
    if not target.exists():
        print(f"target does not exist: {target}", file=sys.stderr)
        return 2

    log = append_event(target, event)
    print(f"appended {event['id']} ({event['type']}) to {log}")
    print("next: run scripts/trace_index.py --target " + str(target))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
