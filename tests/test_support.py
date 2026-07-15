# Shared fixtures and runners for the CodeRail characterization suite.
from pathlib import Path

import ast

import json

import os

import subprocess

import sys

import tempfile

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

def check(cond, msg):
    if not cond:
        raise AssertionError(msg)

def run(cmd):
    subprocess.check_call(cmd)

def write_drive_project(target: Path, tasks: str, trace_rows=None, mode='continuous'):
    (target/'docs').mkdir(parents=True, exist_ok=True)
    (target/'docs'/'NORTH_STAR.md').write_text(f'''# North Star

## Outcome

- ship the current slice

## Current Slice

- Milestone: M-001

## Drive Contract

- Mode: {mode}
- Terminal condition: all autonomous tasks pass their terminal harness
- Progress signal: completed acceptance items
- Retry budget: 3
- No-progress limit: 2
- Human gates: schema, dependency, public API, security, privacy, payment, persistence
''', encoding='utf-8')
    (target/'docs'/'TASKS.md').write_text('# Tasks\n\n' + tasks, encoding='utf-8')
    (target/'docs'/'HARNESS_SPEC.md').write_text('''# Harness Spec

## Drive Progress Harness

- Progress signal: completed acceptance items
- Terminal evidence: all autonomous tasks passed
''', encoding='utf-8')
    rows = trace_rows or []
    (target/'docs'/'TRACELOG.jsonl').write_text(
        ''.join(json.dumps(row) + '\n' for row in rows), encoding='utf-8'
    )

def add_recommendation_contract(
    target: Path,
    *,
    mode='auto-draft',
    mission='active',
    current_slice='complete',
    next_candidate='ID pending',
    human_gate='implementation',
):
    path = target/'docs'/'NORTH_STAR.md'
    text = path.read_text(encoding='utf-8')
    text += f'''\n## Recommendation Contract

- Mode: {mode}
- Mission Status: {mission}
- Current Slice Status: {current_slice}
- Next Candidate: {next_candidate}
- Human Gate: {human_gate}
'''
    path.write_text(text, encoding='utf-8')

def write_contracts(target: Path, *statuses: str):
    rows = []
    for index, status in enumerate(statuses, 1):
        rows.append(f'''## CD-{index:03d} Fixture draft

Status: {status}
''')
    (target/'docs'/'CONTRACTS.md').write_text(
        '# Coordinate Contract Drafts\n\n' + '\n'.join(rows), encoding='utf-8'
    )

def drive_task(task_id='T-001', status='[~]', autonomy='allowed', priority='P1', result='', depends='none'):
    completion = f'\n### Completion\n\nTask result: {result}\n' if result else ''
    return f'''## {task_id} Drive task

Status: {status}
Type: feature
Rail: full
Priority: {priority}
Autonomy: {autonomy}

### CodeRail Coordinate

G — Goal:
- North Star: NS-001

T — Task:
- Advance the slice

S — Scope:
- Allowed:
  - src/**
- Forbidden:
  - schema/**

V — Verify:
- Harness:
  - pytest

X — Stop:
- decision-grade change required

P — Persist:
- TASKS
- TRACE

### Task Contract

Depends on:
- {depends}

Acceptance:
- [ ] task evidence
{completion}'''

def run_drive(target: Path, *args):
    result = subprocess.run([
        sys.executable, str(ROOT/'scripts/drive_check.py'), '--target', str(target), '--json', *args
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
    check(result.returncode == 0, result.stdout + result.stderr)
    return json.loads(result.stdout)

def inspect_task(task_id: str, status: str, verification: str) -> str:
    return f'''## {task_id} Inspect task

Status: {status}
Type: docs
Rail: light
Priority: P1
Autonomy: human-gated

### CodeRail Coordinate

G — Goal:
- North Star: NS-001

T — Task:
- Inspect current state

S — Scope:
- Allowed:
  - docs/**
- Forbidden:
  - src/**

V — Verify:
- {verification}

X — Stop:
- forbidden files needed

P — Persist:
- TASKS
- TRACE
'''

def write_inspect_project(target: Path, tasks: str, enforcement_task) -> None:
    (target/'docs').mkdir(parents=True, exist_ok=True)
    cutoff = (
        f'\n## Legacy Cutoff\n\n- Enforcement starts at: {enforcement_task}\n'
        if enforcement_task is not None else ''
    )
    (target/'docs'/'NORTH_STAR.md').write_text(f'''# North Star

## Outcome

- inspect current work without hiding historical debt
{cutoff}
## Drive Contract

- Mode: manual
''', encoding='utf-8')
    (target/'docs'/'TASKS.md').write_text('# Tasks\n\n' + tasks, encoding='utf-8')
    (target/'docs'/'HANDOFF.md').write_text(
        '# Handoff\n\nHandoff Level: H0\n\n## Coordinate Summary\n', encoding='utf-8'
    )
    (target/'docs'/'CONTRACTS.md').write_text('# Coordinate Contract Drafts\n', encoding='utf-8')
    (target/'docs'/'TRACELOG.jsonl').write_text('', encoding='utf-8')

def run_inspect(target: Path):
    return subprocess.run([
        sys.executable, str(ROOT/'scripts/inspect_state.py'), '--target', str(target), '--no-write'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')

def _lifecycle_env(td):
    """Init a fresh git project in td, return a runner for coderail commands."""
    root = Path(td)
    subprocess.check_call(['git', 'init', '-q'], cwd=td)
    subprocess.check_call(['git', 'config', 'user.email', 't@t.io'], cwd=td)
    subprocess.check_call(['git', 'config', 'user.name', 't'], cwd=td)
    subprocess.run([sys.executable, str(ROOT/'scripts/init_project.py'), '--target', td],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    (root/'docs/NORTH_STAR.md').write_text('Test project goal.\n', encoding='utf-8')
    subprocess.check_call(['git', 'add', '-A'], cwd=td)
    subprocess.check_call(['git', 'commit', '-qm', 'init'], cwd=td)

    def cr(*args):
        return subprocess.run(
            [sys.executable, str(ROOT/'scripts/coderail.py'), *args, '--target', td],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8')
    return root, cr

def _assert_done_inspect_consistent(root, cr, expected_paths):
    result = cr('done')
    check(result.returncode == 0, result.stdout)
    check('== Done:' in result.stdout, result.stdout)
    inspect = cr('inspect', '--no-write')
    check(inspect.returncode == 0 and 'Status: healthy' in inspect.stdout, inspect.stdout)
    check('Closed-task uncommitted ownership: none' in inspect.stdout, inspect.stdout)
    status = subprocess.check_output(['git', '-C', str(root), 'status', '--porcelain'], text=True)
    check(not status.strip(), status)
    committed = set(subprocess.check_output(
        ['git', '-C', str(root), 'show', '--pretty=', '--name-status', 'HEAD~2..HEAD'],
        text=True, encoding='utf-8').splitlines())
    for path in expected_paths:
        check(any(path in row for row in committed), f'{path} missing from closeout commits: {committed}')


def run_module(namespace):
    tests = [value for name, value in namespace.items() if name.startswith("test_")]
    for test in tests:
        test()
        print("ok", test.__name__)
    print(f"{len(tests)} tests passed")

