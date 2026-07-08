from pathlib import Path
import json
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


def test_manifests_exist():
    check((ROOT/'.claude-plugin/plugin.json').exists(), 'missing claude manifest')
    check((ROOT/'.codex-plugin/plugin.json').exists(), 'missing codex manifest')


def test_versions_consistent():
    expected = (ROOT/'VERSION').read_text(encoding='utf-8').strip()
    for path in ['.claude-plugin/plugin.json', '.codex-plugin/plugin.json', 'package.json']:
        data = json.loads((ROOT/path).read_text(encoding='utf-8'))
        check(data['version'] == expected, f'{path} version mismatch')


def test_entry_files_short():
    check(len((ROOT/'project-template/AGENTS.md').read_text(encoding='utf-8').splitlines()) <= 130, 'AGENTS too long')
    check(len((ROOT/'project-template/CLAUDE.md').read_text(encoding='utf-8').splitlines()) <= 60, 'CLAUDE too long')


def test_skills_have_frontmatter():
    for d in (ROOT/'skills').iterdir():
        if d.is_dir():
            txt = (d/'SKILL.md').read_text(encoding='utf-8')
            head = txt.split('---', 2)[1]
            check(txt.startswith('---'), f'{d} no frontmatter')
            check('name:' in head and 'description:' in head, f'{d} incomplete frontmatter')


def test_required_v06_files_exist():
    required = [
        'references/CODERAIL_COORDINATE.md',
        'references/TRACE_GRAPH.md',
        'references/CONTRACT_DRAFT.md',
        'references/RUNTIME_STATE_INSPECT.md',
        'references/DONE_GATE.md',
        'scripts/coordinate_check.py',
        'scripts/trace_event.py',
        'scripts/trace_index.py',
        'scripts/trace_doctor.py',
        'scripts/contract_check.py',
        'scripts/inspect_state.py',
        'scripts/done_gate.py',
        'skills/trace/SKILL.md',
        'skills/link/SKILL.md',
        'skills/contract-draft/SKILL.md',
        'skills/inspect/SKILL.md',
        'skills/done-gate/SKILL.md',
        'project-template/docs/CONTRACTS.md',
        'project-template/docs/CODERAIL_STATUS.md',
    ]
    for p in required:
        check((ROOT/p).exists(), f'missing {p}')


def test_runtime_terms_are_engineering_focused():
    disallowed = [''.join(['S','tra','TA']), ' '.join(['Strategic','Trajectory']), '-'.join(['Self','Judgment'])]
    for path in ROOT.rglob('*'):
        if path.is_file() and path.suffix in {'.md', '.json', '.py'} and 'tests' not in path.parts:
            body = path.read_text(encoding='utf-8', errors='ignore')
            for term in disallowed:
                check(term not in body, f'{term} found in {path}')


def test_trace_event_edges_and_from_file():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td); (target/'docs').mkdir()
        event = target/'event.json'
        event.write_text(json.dumps({
            'type': 'change', 'summary': 'change thing', 'task': 'T-001',
            'north_star': 'NS-001', 'files': 'src/a.py',
            'derived_from': ['intent-1'], 'validated_by': ['TR-v'],
            'goal': 'G', 'coordinate_task': 'T', 'verify': 'pytest', 'persist': 'TASKS,TRACE'
        }), encoding='utf-8')
        run([sys.executable, str(ROOT/'scripts/trace_event.py'), '--target', str(target), '--from-file', str(event)])
        row = json.loads((target/'docs/TRACELOG.jsonl').read_text(encoding='utf-8').splitlines()[0])
        check(row['derived_from'] == ['intent-1'], 'derived_from edge missing')
        check(row['validated_by'] == ['TR-v'], 'validated_by edge missing')
        check(row['coordinate']['goal'] == 'G', 'coordinate missing')


def test_init_contract_inspect_done_gate_flow():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        run([sys.executable, str(ROOT/'scripts/init_project.py'), '--target', td, '--mode', 'standard'])
        check((target/'docs/CONTRACTS.md').exists(), 'CONTRACTS missing')
        check((target/'docs/CODERAIL_STATUS.md').exists(), 'STATUS missing')
        run([sys.executable, str(ROOT/'scripts/contract_check.py'), '--target', td])
        run([sys.executable, str(ROOT/'scripts/inspect_state.py'), '--target', td, '--write'])
        check('CodeRail Status' in (target/'docs/CODERAIL_STATUS.md').read_text(encoding='utf-8'), 'inspect did not write status')
        # Add a real task by unescaping the template enough for the parser.
        tasks = target/'docs/TASKS.md'
        tasks.write_text('''# Tasks\n\n## T-001 Init docs\n\nStatus: [~]\n\n### CodeRail Coordinate\n\nG — Goal:\n- North Star: NS-001\n- Outcome served: initialize governance\n\nT — Task:\n- Create governance docs\n\nS — Scope:\n- Allowed:\n  - docs/**\n- Forbidden:\n  - src/**\n\nV — Verify:\n- Harness:\n  - manual template check passed\n\nX — Stop:\n- business implementation requested\n\nP — Persist:\n- TASKS\n- TRACE\n\n### Task Contract\n\nAcceptance:\n- [ ] docs present\n''', encoding='utf-8')
        run([sys.executable, str(ROOT/'scripts/trace_event.py'), '--target', td, '--type', 'verify', '--summary', 'manual check passed', '--task', 'T-001', '--north-star', 'NS-001', '--harness-result', 'passed', '--goal', 'initialize governance', '--coordinate-task', 'Create governance docs', '--verify', 'manual template check passed', '--persist', 'TASKS,TRACE'])
        run([sys.executable, str(ROOT/'scripts/trace_index.py'), '--target', td])
        run([sys.executable, str(ROOT/'scripts/done_gate.py'), '--target', td, '--task', 'T-001', '--harness-result', 'passed'])


def test_done_gate_scope_prefix_is_segment_aware():
    import scripts.done_gate as done_gate

    check(done_gate.matches_any('docs/file.md', ['docs/**']), 'docs/** should match docs/file.md')
    check(not done_gate.matches_any('docs2/file.md', ['docs/**']), 'docs/** must not match docs2/file.md')
    check(done_gate.matches_any('src\\app.py', ['src/**']), 'src/** should match backslash paths')
    check(not done_gate.matches_any('src2\\app.py', ['src/**']), 'src/** must not match src2 paths')


def test_done_gate_skipped_requires_manual_acceptance():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        run([sys.executable, str(ROOT/'scripts/init_project.py'), '--target', td, '--mode', 'standard'])
        (target/'docs/TASKS.md').write_text('''# Tasks\n\n## T-001 Init docs\n\nStatus: [~]\n\n### CodeRail Coordinate\n\nG — Goal:\n- North Star: NS-001\n\nT — Task:\n- Create governance docs\n\nS — Scope:\n- Allowed:\n  - docs/**\n- Forbidden:\n  - src/**\n\nV — Verify:\n- Harness:\n  - manual template check\n\nX — Stop:\n- business implementation requested\n\nP — Persist:\n- TASKS\n- TRACE\n''', encoding='utf-8')
        failed = subprocess.run([
            sys.executable, str(ROOT/'scripts/done_gate.py'), '--target', td,
            '--task', 'T-001', '--harness-result', 'skipped', '--changed-files', 'docs/TASKS.md'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        check(failed.returncode == 1, 'skipped harness without manual acceptance must block done')
        check('skipped harness requires explicit manual acceptance evidence' in failed.stdout, 'missing skipped harness diagnostic')

        passed = subprocess.run([
            sys.executable, str(ROOT/'scripts/done_gate.py'), '--target', td,
            '--task', 'T-001', '--harness-result', 'skipped',
            '--manual-acceptance', 'User accepted no automated harness for docs-only task',
            '--changed-files', 'docs/TASKS.md'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        check(passed.returncode == 0, 'skipped harness with manual acceptance should pass')


def run_all():
    tests = [v for k, v in globals().items() if k.startswith('test_')]
    for t in tests:
        t(); print('ok', t.__name__)
    print(f'{len(tests)} tests passed')


if __name__ == '__main__':
    run_all()
