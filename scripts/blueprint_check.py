#!/usr/bin/env python3
"""Optional blueprint awareness reminder."""
from __future__ import annotations
import argparse
from pathlib import Path

def run_check(root: Path) -> str:
    return '> Optional. If the project has UI/API/DB/state/deployment complexity, consider a small diagram. Not a compliance gate.'
def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument('--target', default='.')
    a=p.parse_args(argv); print('# Blueprint Awareness\n'); print(run_check(Path(a.target).resolve())); return 0
if __name__=='__main__': raise SystemExit(main())
