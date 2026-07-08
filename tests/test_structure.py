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
        'references/CLOSEOUT_GATE.md',
        'references/LOOP_ENGINEERING.md',
        'scripts/coordinate_check.py',
        'scripts/trace_event.py',
        'scripts/trace_index.py',
        'scripts/trace_doctor.py',
        'scripts/contract_check.py',
        'scripts/inspect_state.py',
        'scripts/done_gate.py',
        'scripts/closeout_check.py',
        'scripts/ci_gate.py',
        'scripts/blueprint_check.py',
        'scripts/hook_guard.py',
        'skills/trace/SKILL.md',
        'skills/link/SKILL.md',
        'skills/contract-draft/SKILL.md',
        'skills/inspect/SKILL.md',
        'skills/done-gate/SKILL.md',
        'skills/closeout/SKILL.md',
        'skills/ci-gate/SKILL.md',
        'skills/blueprint/SKILL.md',
        'project-template/docs/CONTRACTS.md',
        'project-template/docs/CODERAIL_STATUS.md',
        'project-template/docs/BLUEPRINTS.md',
        'docs/BLUEPRINTS.md',
        'examples/hooks.example.json',
        'examples/claude/settings.example.json',
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
        check((target/'docs/BLUEPRINTS.md').exists(), 'BLUEPRINTS missing')
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


def test_closeout_check_reports_commit_boundaries():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        run(['git', '-C', td, 'init'])
        (target/'docs').mkdir()
        (target/'src').mkdir()
        (target/'build').mkdir()
        (target/'docs'/'TASKS.md').write_text('''# Tasks\n\n## T-001 Closeout docs\n\nStatus: [~]\n\n### CodeRail Coordinate\n\nG — Goal:\n- North Star: NS-001\n\nT — Task:\n- Improve closeout docs\n\nS — Scope:\n- Allowed:\n  - docs/**\n- Forbidden:\n  - src/**\n\nV — Verify:\n- Harness:\n  - manual docs check\n\nX — Stop:\n- forbidden files needed\n\nP — Persist:\n- TASKS\n- TRACE\n''', encoding='utf-8')
        (target/'docs'/'HANDOFF.md').write_text('''# Handoff\n\n## Coordinate Summary\n\nG:\n\n## Auto Commit\n\n## Next Executable Step\n\n- run closeout\n''', encoding='utf-8')
        (target/'docs'/'note.md').write_text('note\n', encoding='utf-8')
        (target/'src'/'app.py').write_text('print("x")\n', encoding='utf-8')
        (target/'.gitignore').write_text('build/\n', encoding='utf-8')
        (target/'build'/'out.txt').write_text('generated\n', encoding='utf-8')

        result = subprocess.run([
            sys.executable, str(ROOT/'scripts/closeout_check.py'), '--target', td,
            '--task', 'T-001', '--task-result', 'stage-complete'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        check(result.returncode == 1, 'forbidden changed files should block clean closeout')
        check('src/app.py' in result.stdout, 'forbidden file should be listed as do-not-stage')
        check('build/' in result.stdout or 'build/out.txt' in result.stdout, 'ignored artifact should be reported')
        check('Avoid git add .: yes' in result.stdout, 'unsafe broad staging should be explicit')


def test_closeout_check_auto_commits_safe_scope_only():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        run(['git', '-C', td, 'init'])
        run(['git', '-C', td, 'config', 'user.email', 'coderail@example.invalid'])
        run(['git', '-C', td, 'config', 'user.name', 'CodeRail Test'])
        (target/'docs').mkdir()
        (target/'src').mkdir()
        (target/'docs'/'TASKS.md').write_text('''# Tasks\n\n## T-002 Auto commit docs\n\nStatus: [~]\n\n### CodeRail Coordinate\n\nG — Goal:\n- North Star: NS-001\n\nT — Task:\n- Improve docs\n\nS — Scope:\n- Allowed:\n  - docs/**\n- Forbidden:\n  - none\n\nV — Verify:\n- Harness:\n  - manual docs check\n\nX — Stop:\n- forbidden files needed\n\nP — Persist:\n- TASKS\n- TRACE\n''', encoding='utf-8')
        (target/'docs'/'HANDOFF.md').write_text('''# Handoff\n\n## Coordinate Summary\n\nG:\n\n## Auto Commit\n\n## Next Executable Step\n\n- continue\n''', encoding='utf-8')
        (target/'docs'/'note.md').write_text('note\n', encoding='utf-8')
        (target/'src'/'outside.py').write_text('print("outside")\n', encoding='utf-8')

        result = subprocess.run([
            sys.executable, str(ROOT/'scripts/closeout_check.py'), '--target', td,
            '--task', 'T-002', '--task-result', 'stage-complete', '--auto-commit'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        check(result.returncode == 0, result.stdout)
        check('Action: committed' in result.stdout, 'safe task-scoped files should be auto-committed')
        committed = subprocess.check_output(['git', '-C', td, 'show', '--name-only', '--format='], text=True, encoding='utf-8')
        check('docs/note.md' in committed.replace('\\', '/'), 'docs file should be committed')
        check('src/outside.py' not in committed.replace('\\', '/'), 'outside file must not be committed')


def test_blueprint_gate_blocks_complex_project_without_index():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        (target/'src'/'components').mkdir(parents=True)
        (target/'api').mkdir()
        (target/'prisma').mkdir()
        (target/'.github'/'workflows').mkdir(parents=True)
        (target/'src'/'components'/'App.tsx').write_text('export function App() { return null }\n', encoding='utf-8')
        (target/'api'/'server.py').write_text('from fastapi import FastAPI\napp = FastAPI()\n', encoding='utf-8')
        (target/'prisma'/'schema.prisma').write_text('model User { id Int @id }\n', encoding='utf-8')
        (target/'Dockerfile').write_text('FROM python:3.13\n', encoding='utf-8')
        (target/'.github'/'workflows'/'ci.yml').write_text('name: CI\n', encoding='utf-8')
        result = subprocess.run([
            sys.executable, str(ROOT/'scripts/blueprint_check.py'), '--target', td
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        check(result.returncode == 1, 'high-complexity project without BLUEPRINTS should fail')
        check('docs/BLUEPRINTS.md missing for high-complexity project' in result.stdout, 'missing blueprint diagnostic')


def test_blueprint_gate_accepts_current_required_diagrams():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        (target/'src'/'components').mkdir(parents=True)
        (target/'api').mkdir()
        (target/'prisma').mkdir()
        (target/'.github'/'workflows').mkdir(parents=True)
        (target/'docs').mkdir()
        (target/'docs'/'diagrams').mkdir()
        (target/'src'/'components'/'App.tsx').write_text('export function App() { return null }\n', encoding='utf-8')
        (target/'api'/'server.py').write_text('from fastapi import FastAPI\napp = FastAPI()\n', encoding='utf-8')
        (target/'prisma'/'schema.prisma').write_text('model User { id Int @id }\n', encoding='utf-8')
        (target/'Dockerfile').write_text('FROM python:3.13\n', encoding='utf-8')
        (target/'.github'/'workflows'/'ci.yml').write_text('name: CI\n', encoding='utf-8')
        for name in ['sa.md', 'cd.md', 'seq.md', 'erd.md', 'dd.md', 'cicd.md']:
            (target/'docs'/'diagrams'/name).write_text('# diagram\n', encoding='utf-8')
        (target/'docs'/'BLUEPRINTS.md').write_text('''# Blueprints\n\n| ID | Diagram | Status | Path / URL | Owner | Updated | Notes |\n|---|---|---|---|---|---|---|\n| SA | System Architecture | current | docs/diagrams/sa.md | team | 2026-07-08 | ok |\n| CD | Component Diagram | current | docs/diagrams/cd.md | team | 2026-07-08 | ok |\n| SEQ | Sequence Diagram | current | docs/diagrams/seq.md | team | 2026-07-08 | ok |\n| ERD | ER Diagram / Database Model | current | docs/diagrams/erd.md | team | 2026-07-08 | ok |\n| DD | Deployment Diagram | current | docs/diagrams/dd.md | team | 2026-07-08 | ok |\n| CICD | CI/CD Pipeline Flow | current | docs/diagrams/cicd.md | team | 2026-07-08 | ok |\n''', encoding='utf-8')
        result = subprocess.run([
            sys.executable, str(ROOT/'scripts/blueprint_check.py'), '--target', td
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        check(result.returncode == 0, result.stdout)
        check('Status: healthy' in result.stdout, 'complete blueprint index should be healthy')


def test_hook_guard_blocks_casual_governance_edits():
    payload = json.dumps({'tool_input': {'file_path': 'AGENTS.md'}})
    result = subprocess.run([
        sys.executable, str(ROOT/'scripts/hook_guard.py'), '--stage', 'pre-edit', '--target', str(ROOT)
    ], input=payload, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
    check(result.returncode == 1, 'hook guard should block casual AGENTS.md edits')
    check('Protected governance/kernel files' in result.stdout, 'missing protected file diagnostic')


def test_hook_guard_allows_explicit_governance_upgrade():
    payload = json.dumps({'tool_input': {'file_path': 'AGENTS.md'}})
    env = dict(**__import__('os').environ, CODERAIL_ALLOW_GOVERNANCE_EDIT='1')
    result = subprocess.run([
        sys.executable, str(ROOT/'scripts/hook_guard.py'), '--stage', 'pre-edit', '--target', str(ROOT)
    ], input=payload, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', env=env)
    check(result.returncode == 0, 'explicit governance upgrade should bypass hook guard')


def run_all():
    tests = [v for k, v in globals().items() if k.startswith('test_')]
    for t in tests:
        t(); print('ok', t.__name__)
    print(f'{len(tests)} tests passed')


if __name__ == '__main__':
    run_all()
