#!/usr/bin/env python3
"""Check trace health for a CodeRail project."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

def load_events(log_path: Path):
    if not log_path.exists(): return []
    events=[]
    for lineno, raw in enumerate(log_path.read_text(encoding='utf-8').splitlines(),1):
        raw=raw.strip()
        if not raw: continue
        try: events.append(json.loads(raw))
        except json.JSONDecodeError as e: print(f"warning: invalid JSON line {lineno}: {e}", file=sys.stderr)
    return events

def check(events, index_path: Path, log_path: Path):
    severe=[]; warnings=[]
    if not events:
        warnings.append('TRACELOG.jsonl is empty — no trace events yet.'); return severe,warnings
    for ev in events:
        eid=ev.get('id','?'); etype=ev.get('type')
        has_anchor=bool(ev.get('task') or ev.get('north_star') or ev.get('files'))
        if etype=='change':
            if not has_anchor: severe.append(f"change {eid} has no task, north_star, or files")
            elif not (ev.get('task') or ev.get('north_star')): warnings.append(f"change {eid} is files-only; link it to task or north_star when possible")
            if not (ev.get('modifies') or ev.get('files')): warnings.append(f"change {eid} has no modifies/files")
        if etype=='verify' and not ev.get('harness_result'):
            severe.append(f"verify {eid} has no harness_result")
        if etype=='task' and ev.get('task') and not ev.get('north_star'):
            warnings.append(f"task {ev.get('task')} cannot map to a north star")
        if etype in {'research','attempt'} and ev.get('status') not in {'accepted','rejected','superseded','done'}:
            warnings.append(f"{etype} {eid} has no terminal status")
        if etype=='handoff' and not ev.get('task'):
            warnings.append(f"handoff {eid} has no task link")
        if etype in {'change','verify','decision','lesson'} and not has_anchor:
            warnings.append(f"orphan event {eid} has no task/north_star/file")
        if etype in {'change','verify','handoff'} and not ev.get('coordinate'):
            warnings.append(f"{etype} {eid} has no coordinate summary")
    if log_path.exists() and (not index_path.exists() or log_path.stat().st_mtime > index_path.stat().st_mtime):
        warnings.append('TRACE_INDEX.md is stale — rerun scripts/trace_index.py')
    return severe,warnings

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument('--target', default='.')
    args=p.parse_args(argv); root=Path(args.target).resolve(); docs=root/'docs'
    log=docs/'TRACELOG.jsonl'; index=docs/'TRACE_INDEX.md'; events=load_events(log); severe,warnings=check(events,index,log)
    print('# Trace Doctor Report\n')
    status='healthy' if not severe and not warnings else ('unhealthy' if severe else 'usable with warnings')
    print(f'Status: {status}'); print(f'Events: {len(events)}\n')
    print('## Severe'); print('- none' if not severe else '\n'.join(f'- SEVERE: {x}' for x in severe))
    print('\n## Warnings'); print('- none' if not warnings else '\n'.join(f'- {x}' for x in warnings))
    return 1 if severe else 0
if __name__=='__main__': raise SystemExit(main())
