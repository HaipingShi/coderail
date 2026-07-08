#!/usr/bin/env python3
"""Append a trace event to docs/TRACELOG.jsonl."""
from __future__ import annotations
import argparse, json, secrets, sys
from datetime import datetime, timezone
from pathlib import Path

VALID_TYPES={"intent","align","task","decision","research","attempt","change","verify","handoff","lesson"}
EDGE_KEYS=["serves","derived_from","implements","modifies","validated_by","depends_on","supersedes","blocks","relates_to"]

def make_id(now=None):
    now=now or datetime.now(timezone.utc)
    return f"TR-{now.strftime('%Y%m%d-%H%M%S')}-{secrets.token_hex(2)}"

def split_list(value):
    if value is None: return None
    if isinstance(value,(list,tuple)): return [str(v).strip() for v in value if str(v).strip()]
    parts=[p.strip() for p in str(value).split(',')]
    return [p for p in parts if p]

def build_coordinate(ns):
    if not any(getattr(ns,k,None) for k in ["goal","coordinate_task","scope_allowed","scope_forbidden","verify","stop","persist"]):
        return None
    c={}
    if ns.goal: c["goal"]=ns.goal
    if ns.coordinate_task: c["task"]=ns.coordinate_task
    scope={}
    if split_list(ns.scope_allowed): scope["allowed"]=split_list(ns.scope_allowed)
    if split_list(ns.scope_forbidden): scope["forbidden"]=split_list(ns.scope_forbidden)
    if scope: c["scope"]=scope
    if split_list(ns.verify): c["verify"]=split_list(ns.verify)
    if split_list(ns.stop): c["stop"]=split_list(ns.stop)
    if split_list(ns.persist): c["persist"]=split_list(ns.persist)
    return c

def build_event(ns):
    if ns.type not in VALID_TYPES:
        raise ValueError(f"invalid type {ns.type!r}")
    now=datetime.now(timezone.utc)
    ev={"id": ns.id or make_id(now), "ts": ns.ts or now.isoformat(timespec='seconds'), "type": ns.type, "summary": ns.summary or ""}
    for key in ["task","north_star","status","source_kind","source_ref","harness_command","harness_result","commit"]:
        val=getattr(ns,key,None)
        if val: ev[key]=val
    files=split_list(getattr(ns,"files",None))
    if files: ev["files"]=files
    for edge in EDGE_KEYS:
        val=getattr(ns, edge, None)
        lst=split_list(val)
        if lst: ev[edge]=lst
    coord=build_coordinate(ns)
    if coord: ev["coordinate"]=coord
    if ev["type"]=="change" and not (ev.get("task") or ev.get("north_star") or ev.get("files")):
        raise ValueError("change event must have at least one of --task, --north-star, --files")
    if ev["type"]=="verify" and not ev.get("harness_result"):
        raise ValueError("verify event must have --harness-result")
    return ev

def parse(argv=None):
    p=argparse.ArgumentParser(description='Append a CodeRail trace event')
    p.add_argument('--target', default='.')
    p.add_argument('--from-file')
    p.add_argument('--type', choices=sorted(VALID_TYPES))
    p.add_argument('--summary')
    p.add_argument('--task'); p.add_argument('--north-star', dest='north_star'); p.add_argument('--status')
    p.add_argument('--source-kind', dest='source_kind'); p.add_argument('--source-ref', dest='source_ref')
    p.add_argument('--files'); p.add_argument('--harness-command', dest='harness_command'); p.add_argument('--harness-result', dest='harness_result')
    p.add_argument('--commit'); p.add_argument('--id'); p.add_argument('--ts')
    for edge in EDGE_KEYS:
        p.add_argument('--'+edge.replace('_','-'), dest=edge)
    p.add_argument('--goal'); p.add_argument('--coordinate-task', dest='coordinate_task')
    p.add_argument('--scope-allowed', dest='scope_allowed'); p.add_argument('--scope-forbidden', dest='scope_forbidden')
    p.add_argument('--verify'); p.add_argument('--stop'); p.add_argument('--persist')
    ns=p.parse_args(argv)
    if ns.from_file:
        data=json.loads(Path(ns.from_file).read_text(encoding='utf-8'))
        for key, val in data.items():
            k = 'north_star' if key=='north-star' else key.replace('-', '_')
            if hasattr(ns,k) and getattr(ns,k) in (None, ''):
                setattr(ns,k,val)
    if not ns.type:
        p.error('--type is required unless supplied by --from-file')
    return ns

def append_event(target: Path, ev: dict) -> Path:
    docs=target/'docs'; docs.mkdir(parents=True, exist_ok=True)
    log=docs/'TRACELOG.jsonl'
    with log.open('a', encoding='utf-8') as fh:
        fh.write(json.dumps(ev, ensure_ascii=False)+'\n')
    return log

def main(argv=None):
    try:
        ns=parse(argv); ev=build_event(ns)
    except (ValueError, json.JSONDecodeError) as e:
        print(f"error: {e}", file=sys.stderr); return 2
    target=Path(ns.target).resolve()
    if not target.exists():
        print(f"target does not exist: {target}", file=sys.stderr); return 2
    log=append_event(target, ev)
    print(f"appended {ev['id']} ({ev['type']}) to {log}")
    print(f"next: python3 scripts/trace_index.py --target {target}")
    return 0
if __name__=='__main__':
    raise SystemExit(main())
