#!/usr/bin/env python3
"""Lightweight drift check."""
from __future__ import annotations
import argparse, re
from pathlib import Path

def read(p):
    try: return p.read_text(encoding='utf-8', errors='ignore')
    except FileNotFoundError: return ''
def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument('--target', default='.')
    a=p.parse_args(argv); root=Path(a.target).resolve(); docs=root/'docs'
    issues=[]
    ns=read(docs/'NORTH_STAR.md'); tasks=read(docs/'TASKS.md'); handoff=read(docs/'HANDOFF.md')
    if 'Outcome' not in ns or 'Current Slice' not in ns: issues.append('NORTH_STAR.md lacks Outcome or Current Slice')
    if 'CodeRail Coordinate' not in tasks: issues.append('TASKS.md lacks CodeRail Coordinate')
    if 'Status: [x]' in tasks and 'Harness result:' not in tasks: issues.append('done task may lack harness result')
    if handoff and 'Coordinate Summary' not in handoff: issues.append('HANDOFF.md lacks Coordinate Summary')
    print('# Drift Check Report\n')
    print('Status: ' + ('aligned' if not issues else 'minor drift'))
    print('\n## Findings')
    print('- none' if not issues else '\n'.join(f'- {x}' for x in issues))
    return 1 if issues else 0
if __name__=='__main__': raise SystemExit(main())
