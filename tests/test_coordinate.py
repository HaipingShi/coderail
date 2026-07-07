"""Tests for scripts/coordinate_check.py."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'scripts'
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import coordinate_check  # noqa: E402

COMPLETE_COORD = """## T-001 Example

Status: [ ]
Type: feature

### CodeRail Coordinate

G — Goal:
- North Star: NS-001
- Outcome served: ship the MVP

T — Task:
- Add the import entry point

S — Scope:
- Allowed:
  - src/import/**
- Forbidden:
  - auth/**

V — Verify:
- Harness:
  - pytest tests/import

X — Stop:
- Need schema change

P — Persist:
- TASKS: T-001
- TRACE: change, verify

### Task Contract

Depends on:
- 

Acceptance:
- [ ] it works
"""

MISSING_G = """## T-002 No goal

Status: [ ]
Type: feature

### CodeRail Coordinate

G — Goal:
- 

T — Task:
- something

S — Scope:
- Allowed:
  - src/**
- Forbidden:
  - none

V — Verify:
- pytest

X — Stop:
- blocked

P — Persist:
- TASKS
- TRACE
"""

DONE_WITHOUT_V = """## T-003 Done but no verify

Status: [x]
Type: feature

### CodeRail Coordinate

G — Goal:
- NS-001

T — Task:
- done thing

S — Scope:
- Allowed:
  - src/**
- Forbidden:
  - none

V — Verify:
- 

X — Stop:
- none

P — Persist:
- TASKS
- TRACE
"""


def test_parse_coordinate_finds_block():
    coord = coordinate_check.parse_coordinate(COMPLETE_COORD)
    assert coord is not None
    assert 'NS-001' in coord['g']
    assert coord['t']
    assert coord['s_allowed']
    assert coord['s_forbidden']
    assert coord['v']
    assert coord['x']
    assert coord['p']


def test_complete_task_no_severe():
    for header, body, status in coordinate_check.split_tasks(COMPLETE_COORD):
        severe, warnings = coordinate_check.check_task(header, body, status)
        assert severe == [], f'unexpected severe: {severe}'


def test_missing_g_is_severe():
    for header, body, status in coordinate_check.split_tasks(MISSING_G):
        severe, warnings = coordinate_check.check_task(header, body, status)
        assert any('G (Goal) missing' in s for s in severe)


def test_done_without_v_is_severe():
    for header, body, status in coordinate_check.split_tasks(DONE_WITHOUT_V):
        severe, warnings = coordinate_check.check_task(header, body, status)
        assert any('V' in s for s in severe)
