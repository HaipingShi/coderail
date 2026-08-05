from test_support import *


def write_persist_assert_project(target: Path, assertion: str = ''):
    (target/'docs').mkdir(parents=True, exist_ok=True)
    assertion_line = f'\n- {assertion}' if assertion else ''
    (target/'docs/TASKS.md').write_text(f'''# Tasks

## T-001 Persist structured truth

Status: [~]
Type: bug
Rail: full

### CodeRail Coordinate

G — Goal
- Keep declared structured truth current

T — Task
- Verify one structured surface

S — Scope
Allowed:
  - docs/**
Forbidden:
  - none

V — Verify
- Harness: passed

X — Stop
- semantic prose parsing required

P — Persist
- TASKS
- TRACE{assertion_line}
''', encoding='utf-8')
    (target/'docs/TRACELOG.jsonl').write_text('', encoding='utf-8')
    (target/'docs/TRACE_INDEX.md').write_text('# Trace Index\n', encoding='utf-8')


def run_persist_done_gate(target: Path):
    return subprocess.run([
        sys.executable, str(ROOT/'scripts/done_gate.py'), '--target', str(target),
        '--task', 'T-001', '--harness-result', 'passed',
        '--changed-files', 'docs/TASKS.md',
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')


def test_done_gate_blocks_declared_missing_persist_file_and_literal():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        write_persist_assert_project(
            target,
            'Persist-Assert: {"path":"docs/HANDOFF.md","contains":["machine-marker"]}',
        )
        missing_file = run_persist_done_gate(target)
        check(missing_file.returncode == 1, missing_file.stdout)
        check('PERSIST_GAP' in missing_file.stdout and 'reason=missing_file' in missing_file.stdout,
              missing_file.stdout)
        (target/'docs/HANDOFF.md').write_text('# Handoff\n', encoding='utf-8')
        missing_literal = run_persist_done_gate(target)
        check(missing_literal.returncode == 1, missing_literal.stdout)
        check('PERSIST_GAP' in missing_literal.stdout and 'reason=missing_literal' in missing_literal.stdout,
              missing_literal.stdout)


def test_done_gate_blocks_invalid_or_unsafe_persist_assertion():
    for assertion, reason in [
        ('Persist-Assert: not-json', 'invalid_json'),
        ('Persist-Assert: {"path":"../outside","contains":["x"]}', 'unsafe_path'),
    ]:
        with tempfile.TemporaryDirectory() as td:
            target = Path(td)
            write_persist_assert_project(target, assertion)
            result = run_persist_done_gate(target)
            check(result.returncode == 1, result.stdout)
            check('PERSIST_GAP' in result.stdout and f'reason={reason}' in result.stdout,
                  result.stdout)


def test_done_gate_accepts_valid_or_undeclared_legacy_persist_contract():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        marker = '<!-- machine-owned:start -->'
        write_persist_assert_project(
            target,
            f'Persist-Assert: {{"path":"docs/HANDOFF.md","contains":["{marker}"]}}',
        )
        (target/'docs/HANDOFF.md').write_text(f'# Handoff\n\n{marker}\n', encoding='utf-8')
        valid = run_persist_done_gate(target)
        check(valid.returncode == 0, valid.stdout)
        check('PERSIST_GAP' not in valid.stdout, valid.stdout)
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        write_persist_assert_project(target)
        legacy = run_persist_done_gate(target)
        check(legacy.returncode == 0, legacy.stdout)
        check('PERSIST_GAP' not in legacy.stdout, legacy.stdout)


if __name__ == "__main__":
    run_module(globals())
