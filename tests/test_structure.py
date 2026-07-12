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
        'references/TDD_GATE.md',
        'references/DONE_GATE.md',
        'references/CLOSEOUT_GATE.md',
        'references/LOOP_ENGINEERING.md',
        'references/DRIVE_LOOP.md',
        'scripts/coordinate_check.py',
        'scripts/trace_event.py',
        'scripts/trace_index.py',
        'scripts/trace_doctor.py',
        'scripts/contract_check.py',
        'scripts/inspect_state.py',
        'scripts/tdd_check.py',
        'scripts/done_gate.py',
        'scripts/closeout_check.py',
        'scripts/ci_gate.py',
        'scripts/regression_observe.py',
        'scripts/drive_check.py',
        'scripts/drive_observe.py',
        'scripts/blueprint_check.py',
        'scripts/hook_guard.py',
        'skills/trace/SKILL.md',
        'skills/link/SKILL.md',
        'skills/contract-draft/SKILL.md',
        'skills/inspect/SKILL.md',
        'skills/tdd-gate/SKILL.md',
        'skills/done-gate/SKILL.md',
        'skills/closeout/SKILL.md',
        'skills/ci-gate/SKILL.md',
        'skills/blueprint/SKILL.md',
        'skills/drive/SKILL.md',
        'project-template/docs/CONTRACTS.md',
        'project-template/docs/CODERAIL_STATUS.md',
        'project-template/docs/BLUEPRINTS.md',
        'docs/BLUEPRINTS.md',
        'docs/REGRESSION_OBSERVE.md',
        'docs/DRIVE_LOOP_DESIGN.md',
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
        tasks.write_text('''# Tasks\n\n## T-001 Init docs\n\nStatus: [~]\nType: docs\nRail: light\n\n### CodeRail Coordinate\n\nG — Goal:\n- North Star: NS-001\n- Outcome served: initialize governance\n\nT — Task:\n- Create governance docs\n\nS — Scope:\n- Allowed:\n  - docs/**\n- Forbidden:\n  - src/**\n\nV — Verify:\n- Harness:\n  - manual template check passed\n\nX — Stop:\n- business implementation requested\n\nP — Persist:\n- TASKS\n- TRACE\n\n### Task Contract\n\nAcceptance:\n- [ ] docs present\n''', encoding='utf-8')
        run([sys.executable, str(ROOT/'scripts/trace_event.py'), '--target', td, '--type', 'verify', '--summary', 'manual check passed', '--task', 'T-001', '--north-star', 'NS-001', '--harness-result', 'passed', '--goal', 'initialize governance', '--coordinate-task', 'Create governance docs', '--verify', 'manual template check passed', '--persist', 'TASKS,TRACE'])
        run([sys.executable, str(ROOT/'scripts/trace_index.py'), '--target', td])
        run([sys.executable, str(ROOT/'scripts/done_gate.py'), '--target', td, '--task', 'T-001', '--harness-result', 'passed'])


def test_done_gate_scope_prefix_is_segment_aware():
    import scripts.done_gate as done_gate

    check(done_gate.matches_any('docs/file.md', ['docs/**']), 'docs/** should match docs/file.md')
    check(not done_gate.matches_any('docs2/file.md', ['docs/**']), 'docs/** must not match docs2/file.md')
    check(done_gate.matches_any('src\\app.py', ['src/**']), 'src/** should match backslash paths')
    check(not done_gate.matches_any('src2\\app.py', ['src/**']), 'src/** must not match src2 paths')


def test_tdd_gate_blocks_done_required_without_red_green():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        (target/'docs').mkdir()
        (target/'docs'/'TASKS.md').write_text('''# Tasks\n\n## B-001 Fix parser regression\n\nStatus: [x]\nType: bug\n\n### CodeRail Coordinate\n\nG — Goal:\n- North Star: NS-001\n\nT — Task:\n- Fix parser regression\n\nS — Scope:\n- Allowed:\n  - src/parser.py\n- Forbidden:\n  - none\n\nV — Verify:\n- TDD mode: required\n- Harness:\n  - pytest tests/test_parser.py\n\nX — Stop:\n- forbidden files needed\n\nP — Persist:\n- TASKS\n- TRACE\n''', encoding='utf-8')
        result = subprocess.run([
            sys.executable, str(ROOT/'scripts/tdd_check.py'), '--target', td
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        check(result.returncode == 1, 'done required TDD task without red/green should fail')
        check('missing Red check, Green check' in result.stdout, 'missing red/green diagnostic')


def test_tdd_gate_accepts_required_evidence():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        (target/'docs').mkdir()
        (target/'docs'/'TASKS.md').write_text('''# Tasks\n\n## B-001 Fix parser regression\n\nStatus: [x]\nType: bug\n\n### CodeRail Coordinate\n\nG — Goal:\n- North Star: NS-001\n\nT — Task:\n- Fix parser regression\n\nS — Scope:\n- Allowed:\n  - src/parser.py\n- Forbidden:\n  - none\n\nV — Verify:\n- TDD mode: required\n- Red check: pytest tests/test_parser.py failed on malformed token case\n- Green check: pytest tests/test_parser.py passed\n- Refactor check: pytest tests/test_parser.py passed after cleanup\n- Regression check: malformed token case remains in tests/test_parser.py\n- CI check: npm run ci passed\n- Harness:\n  - pytest tests/test_parser.py\n\nX — Stop:\n- forbidden files needed\n\nP — Persist:\n- TASKS\n- TRACE\n''', encoding='utf-8')
        result = subprocess.run([
            sys.executable, str(ROOT/'scripts/tdd_check.py'), '--target', td
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        check(result.returncode == 0, result.stdout)
        check('Status: healthy' in result.stdout, 'complete TDD evidence should be healthy')


def test_done_gate_skipped_requires_manual_acceptance():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        run([sys.executable, str(ROOT/'scripts/init_project.py'), '--target', td, '--mode', 'standard'])
        (target/'docs/TASKS.md').write_text('''# Tasks\n\n## T-001 Init docs\n\nStatus: [~]\nType: docs\nRail: light\n\n### CodeRail Coordinate\n\nG — Goal:\n- North Star: NS-001\n\nT — Task:\n- Create governance docs\n\nS — Scope:\n- Allowed:\n  - docs/**\n- Forbidden:\n  - src/**\n\nV — Verify:\n- Harness:\n  - manual template check\n\nX — Stop:\n- business implementation requested\n\nP — Persist:\n- TASKS\n- TRACE\n''', encoding='utf-8')
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


def test_done_gate_light_rail_allows_docs_manual_acceptance_without_trace_p():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        run([sys.executable, str(ROOT/'scripts/init_project.py'), '--target', td, '--mode', 'standard'])
        (target/'docs/TASKS.md').write_text('''# Tasks\n\n## T-001 Design boundary\n\nStatus: [~]\nType: docs\nRail: light\n\n### CodeRail Coordinate\n\nG — Goal:\n- North Star: NS-001\n\nT — Task:\n- Draft design boundary\n\nS — Scope:\n- Allowed:\n  - docs/**\n- Forbidden:\n  - src/**\n\nV — Verify:\n- Manual acceptance:\n  - User accepted design boundary draft\n\nX — Stop:\n- code implementation requested\n\nP — Persist:\n- TASKS\n- DECISIONS\n''', encoding='utf-8')
        result = subprocess.run([
            sys.executable, str(ROOT/'scripts/done_gate.py'), '--target', td,
            '--task', 'T-001', '--rail-type', 'light', '--task-type', 'docs',
            '--harness-result', 'skipped',
            '--manual-acceptance', 'User accepted design boundary draft',
            '--changed-files', 'docs/TASKS.md'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        check(result.returncode == 0, result.stdout)
        check('Rail: light' in result.stdout, 'done gate should report light rail')
        check('P must include TRACE' not in result.stdout, 'light rail should not require TRACE when manual acceptance is explicit')


def test_current_tasks_must_declare_rail_explicitly():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        (target/'docs').mkdir()
        (target/'docs/TASKS.md').write_text('''# Tasks\n\n## T-001 Missing rail\n\nStatus: [~]\nType: docs\n\n### CodeRail Coordinate\n\nG — Goal:\n- North Star: NS-001\n\nT — Task:\n- Draft docs\n\nS — Scope:\n- Allowed:\n  - docs/**\n- Forbidden:\n  - src/**\n\nV — Verify:\n- Manual acceptance:\n  - accepted\n\nX — Stop:\n- code requested\n\nP — Persist:\n- TASKS\n- TRACE\n''', encoding='utf-8')
        (target/'docs/TRACELOG.jsonl').write_text('', encoding='utf-8')
        coord = subprocess.run([
            sys.executable, str(ROOT/'scripts/coordinate_check.py'), '--target', td
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        check(coord.returncode == 1, 'current task without explicit Rail should fail coordinate check')
        check("Rail missing" in coord.stdout, 'missing rail diagnostic should be explicit')

        done = subprocess.run([
            sys.executable, str(ROOT/'scripts/done_gate.py'), '--target', td,
            '--task', 'T-001', '--harness-result', 'manual'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        check(done.returncode == 1, 'done gate should not rely on inferred rail')
        check("--rail-type" in done.stdout, 'done gate should name the CLI override escape hatch')


def test_closeout_check_reports_commit_boundaries():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        run(['git', '-C', td, 'init'])
        (target/'docs').mkdir()
        (target/'src').mkdir()
        (target/'build').mkdir()
        (target/'docs'/'TASKS.md').write_text('''# Tasks\n\n## T-001 Closeout docs\n\nStatus: [~]\nType: docs\nRail: light\n\n### CodeRail Coordinate\n\nG — Goal:\n- North Star: NS-001\n\nT — Task:\n- Improve closeout docs\n\nS — Scope:\n- Allowed:\n  - docs/**\n- Forbidden:\n  - src/**\n\nV — Verify:\n- Harness:\n  - manual docs check\n\nX — Stop:\n- forbidden files needed\n\nP — Persist:\n- TASKS\n- TRACE\n''', encoding='utf-8')
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
        (target/'docs'/'TASKS.md').write_text('''# Tasks\n\n## T-002 Auto commit docs\n\nStatus: [~]\nType: docs\nRail: light\n\n### CodeRail Coordinate\n\nG — Goal:\n- North Star: NS-001\n\nT — Task:\n- Improve docs\n\nS — Scope:\n- Allowed:\n  - docs/**\n- Forbidden:\n  - none\n\nV — Verify:\n- Harness:\n  - manual docs check\n\nX — Stop:\n- forbidden files needed\n\nP — Persist:\n- TASKS\n- TRACE\n''', encoding='utf-8')
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


def test_doctor_separates_historical_debt_from_current_blockers():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        run([sys.executable, str(ROOT/'scripts/init_project.py'), '--target', td, '--mode', 'standard'])
        (target/'docs/TASKS.md').write_text('''# Tasks\n\n## T-001 Old closed task\n\nStatus: [x]\nType: bug\n\n### Task Contract\n\nAcceptance:\n- [x] legacy task closed before CodeRail coordinate existed\n\n## T-002 Current design note\n\nStatus: [~]\nType: docs\nRail: light\n\n### CodeRail Coordinate\n\nG — Goal:\n- North Star: NS-001\n\nT — Task:\n- Draft terms\n\nS — Scope:\n- Allowed:\n  - docs/**\n- Forbidden:\n  - src/**\n\nV — Verify:\n- Manual acceptance:\n  - maintainer review pending\n\nX — Stop:\n- code change requested\n\nP — Persist:\n- TASKS\n- TRACE\n''', encoding='utf-8')
        result = subprocess.run([
            sys.executable, str(ROOT/'scripts/doctor.py'), '--target', td
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace')
        check(result.returncode == 0, result.stdout)
        check('## Historical Debt' in result.stdout, 'doctor should expose historical debt section')
        check('historical debt: Coordinate: T-001' in result.stdout, 'closed task issue should be historical debt')
        check('must-fix blocker: T-001' not in result.stdout, 'closed task debt must not be current blocker')


def test_doctor_accepts_legacy_and_repo_local_inspect_markers():
    import scripts.doctor as doctor

    legacy = '> Generated by `scripts/inspect_state.py`. Prefer regenerating this file.'
    repo_local = '> Generated by `python .coderail/coderail.py inspect`. Prefer regenerating this file.'
    check(doctor.is_generated_status(legacy), 'legacy Inspect marker should remain compatible')
    check(doctor.is_generated_status(repo_local), 'repo-local launcher marker should be accepted')
    check(not doctor.is_generated_status('# CodeRail Status\n\nhand-written'), 'unrelated text must not pass marker validation')


def test_templates_include_rail_and_compact_handoff_policy():
    tasks = (ROOT/'project-template/docs/TASKS.md').read_text(encoding='utf-8')
    handoff = (ROOT/'project-template/docs/HANDOFF.md').read_text(encoding='utf-8')
    north_star = (ROOT/'project-template/docs/NORTH_STAR.md').read_text(encoding='utf-8')
    status = (ROOT/'project-template/docs/CODERAIL_STATUS.md').read_text(encoding='utf-8')
    check('Rail: full | light' in tasks, 'TASKS template should expose rail type')
    check('Autonomy: allowed | human-gated' in tasks, 'TASKS template should expose autonomy')
    check('Compact summary policy' in tasks, 'TASKS template should include compact summary policy')
    check('Recovery Commands' in handoff, 'HANDOFF template should include recovery commands')
    check('Archived history' in handoff, 'HANDOFF template should move long history elsewhere')
    check('## Legacy Cutoff' in north_star, 'NORTH_STAR template should include legacy cutoff')
    check('## Drive Contract' in north_star, 'NORTH_STAR template should include Drive Contract')
    check('## Recommendation Contract' in north_star, 'NORTH_STAR template should include Recommendation Contract')
    check('## Historical Verification Debt' in status, 'status template should separate historical verification debt')
    check('## Drive Decision' in status, 'status template should include Drive Decision')
    check('## Execution Decision' in status, 'status template should name the execution channel')
    check('## Recommendation Decision' in status, 'status template should name the recommendation channel')


def test_regression_observe_scaffold_keeps_artifacts_ignored():
    gitignore = (ROOT/'.gitignore').read_text(encoding='utf-8')
    package = json.loads((ROOT/'package.json').read_text(encoding='utf-8'))
    docs = (ROOT/'docs/REGRESSION_OBSERVE.md').read_text(encoding='utf-8')
    check('.coderail-runs/' in gitignore, 'regression run directory must be gitignored')
    check('tmp/coderail-regression/' in gitignore, 'alternate regression temp directory must be gitignored')
    check('regression-observe' in package.get('scripts', {}), 'npm regression-observe script missing')
    check('Do not\nstage the run directory' in docs or 'Do not stage the run directory' in docs, 'docs must warn not to stage run artifacts')

    with tempfile.TemporaryDirectory() as td:
        result = subprocess.run([
            sys.executable, str(ROOT/'scripts/regression_observe.py'), '--target', str(ROOT),
            '--run-dir', td, '--skip-npm-test'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace')
        check(result.returncode == 0, result.stdout + result.stderr)
        check((Path(td)/'summary.json').exists(), 'regression observer should write summary.json to run dir')
        check((Path(td)/'report.md').exists(), 'regression observer should write report.md to run dir')
        check('CodeRail Regression Observation' in result.stdout, 'observer should print summary report')


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


def test_drive_field_value_does_not_cross_blank_field_lines():
    scripts = str(ROOT/'scripts')
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    import drive_check

    text = '- Terminal condition:\n\nContinuous Drive requires evidence.\n'
    check(drive_check.field_value(text, 'Terminal condition') == '', 'blank field must stay blank')


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


def test_drive_check_continues_active_autonomous_task():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        write_drive_project(target, drive_task())
        report = run_drive(target)
        check(report['decision'] == 'CONTINUE', report)
        check(report['task'] == 'T-001', report)
        check(report['next_action'], 'CONTINUE must name a next action')


def test_drive_check_repairs_known_failure_with_budget():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        write_drive_project(target, drive_task())
        report = run_drive(target, '--harness-result', 'failed', '--retry-count', '1', '--failure-known')
        check(report['decision'] == 'REPAIR', report)


def test_drive_check_exhausts_retry_budget():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        write_drive_project(target, drive_task())
        report = run_drive(target, '--harness-result', 'failed', '--retry-count', '3', '--failure-known')
        check(report['decision'] == 'EXHAUSTED', report)


def test_drive_check_advances_to_ready_task_after_current_task_is_done():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        tasks = drive_task('T-001', '[x]', result='done') + '\n' + drive_task('T-002', '[ ]', priority='P1')
        write_drive_project(target, tasks)
        report = run_drive(target)
        check(report['decision'] == 'ADVANCE', report)
        check(report['task'] == 'T-002', report)


def test_drive_check_keeps_stage_complete_task_active_until_done():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        tasks = drive_task('T-001', '[~]', result='stage-complete') + '\n' + drive_task('T-002', '[ ]', priority='P1')
        write_drive_project(target, tasks)
        report = run_drive(target)
        check(report['decision'] == 'CONTINUE', report)
        check(report['task'] == 'T-001', report)


def test_drive_check_blocks_human_gated_task():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        write_drive_project(target, drive_task(autonomy='human-gated'))
        report = run_drive(target)
        check(report['decision'] == 'BLOCKED_DECISION', report)


def test_drive_check_requests_direction_review_after_repeated_reopen():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        trace = [
            {'id': 'TR-1', 'type': 'task', 'task': 'T-001', 'status': 'reopened', 'summary': 'reopened once'},
            {'id': 'TR-2', 'type': 'task', 'task': 'T-001', 'status': 'reopened', 'summary': 'reopened twice'},
        ]
        write_drive_project(target, drive_task(), trace)
        report = run_drive(target)
        check(report['decision'] == 'REVIEW_DIRECTION', report)


def test_drive_check_completes_only_with_terminal_evidence():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        write_drive_project(target, drive_task(status='[x]'))
        report = run_drive(target, '--terminal-evidence')
        check(report['decision'] == 'COMPLETE', report)


def test_drive_check_manual_mode_is_backward_compatible():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        write_drive_project(target, drive_task(), mode='manual')
        report = run_drive(target)
        check(report['decision'] == 'BLOCKED_DECISION', report)
        check(report['mode'] == 'manual', report)


def test_manual_drive_can_propose_coordinate_without_execution_authority():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        write_drive_project(target, drive_task(status='[x]'), mode='manual')
        add_recommendation_contract(target)
        report = run_drive(target)
        check(report['decision'] == 'BLOCKED_DECISION', report)
        check(report['recommendation']['status'] == 'PROPOSE_COORDINATE', report)
        check(report['recommendation']['requires_human_for_execution'] is True, report)


def test_manual_drive_reviews_only_pending_contract_drafts():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        write_drive_project(target, drive_task(status='[x]'), mode='manual')
        add_recommendation_contract(target)
        write_contracts(target, 'proposed')
        report = run_drive(target)
        check(report['recommendation']['status'] == 'REVIEW_ACTIVE_DRAFT', report)


def test_accepted_and_terminal_contract_drafts_are_not_active():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        write_drive_project(target, drive_task(status='[x]'), mode='manual')
        add_recommendation_contract(target)
        write_contracts(target, 'accepted-human-gated', 'accepted', 'completed', 'rejected', 'backlogged')
        report = run_drive(target)
        check(report['recommendation']['status'] == 'PROPOSE_COORDINATE', report)


def test_mission_complete_requires_terminal_evidence_for_recommendation():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        write_drive_project(target, drive_task(status='[x]'), mode='manual')
        add_recommendation_contract(target, mission='complete', next_candidate='none')
        without_evidence = run_drive(target)
        check(without_evidence['recommendation']['status'] != 'MISSION_COMPLETE', without_evidence)
        with_evidence = run_drive(target, '--terminal-evidence')
        check(with_evidence['recommendation']['status'] == 'MISSION_COMPLETE', with_evidence)


def test_mission_complete_terminal_evidence_wins_over_stale_pending_draft():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        write_drive_project(target, drive_task(status='[x]'), mode='manual')
        add_recommendation_contract(target, mission='complete', next_candidate='none')
        write_contracts(target, 'proposed')
        report = run_drive(target, '--terminal-evidence')
        check(report['recommendation']['status'] == 'MISSION_COMPLETE', report)


def test_mission_complete_does_not_override_open_task():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        write_drive_project(target, drive_task(status='[~]', autonomy='human-gated'), mode='manual')
        add_recommendation_contract(target, mission='complete', next_candidate='none')
        report = run_drive(target, '--terminal-evidence')
        check(report['recommendation']['status'] == 'REVIEW_DIRECTION', report)
        check('open task' in report['recommendation']['reason'].lower(), report)


def test_manual_recommendation_mode_does_not_auto_draft_coordinate():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        write_drive_project(target, drive_task(status='[x]'), mode='manual')
        add_recommendation_contract(target, mode='manual')
        report = run_drive(target)
        check(report['recommendation']['status'] == 'REVIEW_DIRECTION', report)


def test_active_mission_without_next_candidate_requests_direction_review():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        write_drive_project(target, drive_task(status='[x]'), mode='manual')
        add_recommendation_contract(target, next_candidate='none')
        report = run_drive(target)
        check(report['recommendation']['status'] == 'REVIEW_DIRECTION', report)


def test_human_gated_ready_task_is_recommended_but_not_advanced():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        write_drive_project(
            target, drive_task(status='[x]') + '\n' + drive_task('T-002', '[ ]', autonomy='human-gated'),
            mode='manual',
        )
        add_recommendation_contract(target, current_slice='active', next_candidate='T-002')
        report = run_drive(target)
        check(report['decision'] == 'BLOCKED_DECISION', report)
        check(report['recommendation']['status'] == 'REQUEST_HUMAN_GATE', report)
        check(report['recommendation']['requires_human_for_execution'] is True, report)


def test_legacy_project_without_recommendation_contract_stays_non_autonomous():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        write_drive_project(target, drive_task(status='[x]'), mode='manual')
        report = run_drive(target)
        check(report['decision'] == 'BLOCKED_DECISION', report)
        check(report['recommendation']['status'] == 'NO_RECOMMENDATION', report)


def test_drive_check_blocks_decision_grade_changed_files_before_repair():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        write_drive_project(target, drive_task())
        report = run_drive(
            target, '--harness-result', 'failed', '--retry-count', '1', '--failure-known',
            '--changed-files', 'prisma/schema.prisma'
        )
        check(report['decision'] == 'BLOCKED_DECISION', report)


def test_drive_check_blocks_changed_file_outside_active_scope():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        write_drive_project(target, drive_task())
        report = run_drive(target, '--changed-files', 'unrelated/file.py')
        check(report['decision'] == 'BLOCKED_DECISION', report)
        check('outside' in report['reason'].lower(), report)


def test_drive_check_reads_git_status_when_changed_files_omitted():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        write_drive_project(target, drive_task())
        subprocess.run(['git', 'init', '-q', str(target)], check=True)
        subprocess.run(['git', '-C', str(target), 'add', 'docs'], check=True)
        subprocess.run([
            'git', '-C', str(target), '-c', 'user.name=CodeRail Test',
            '-c', 'user.email=coderail@example.invalid', 'commit', '-qm', 'fixture'
        ], check=True)
        (target/'unrelated').mkdir()
        (target/'unrelated'/'file.py').write_text('changed\n', encoding='utf-8')
        report = run_drive(target)
        check(report['decision'] == 'BLOCKED_DECISION', report)
        check('unrelated/file.py' in report['reason'], report)


def test_drive_check_resets_retry_budget_after_passing_checkpoint():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        trace = [
            {'type': 'verify', 'task': 'T-001', 'status': 'failed', 'harness_result': 'failed'},
            {'type': 'task', 'task': 'T-001', 'status': 'retry'},
            {'type': 'verify', 'task': 'T-001', 'status': 'failed', 'harness_result': 'failed'},
            {'type': 'verify', 'task': 'T-001', 'status': 'complete', 'harness_result': 'passed'},
        ]
        write_drive_project(target, drive_task(), trace)
        report = run_drive(target)
        check(report['decision'] == 'CONTINUE', report)
        check('retry 0/3' in report['evidence'], report)


def test_drive_check_blocks_multiple_active_tasks():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        tasks = drive_task('T-001') + '\n' + drive_task('T-002')
        write_drive_project(target, tasks)
        report = run_drive(target)
        check(report['decision'] == 'BLOCKED_DECISION', report)
        check('multiple active tasks' in report['reason'].lower(), report)


def test_drive_check_requires_valid_selected_task_coordinate():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        malformed = '''## T-001 Malformed drive task

Status: [~]
Type: feature
Rail: full
Priority: P1
Autonomy: allowed

### Task Contract

Depends on:
- none
'''
        write_drive_project(target, malformed)
        report = run_drive(target, '--changed-files', '')
        check(report['decision'] == 'BLOCKED_DECISION', report)
        check('coordinate' in report['reason'].lower(), report)


def test_drive_check_requires_configured_progress_harness():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        write_drive_project(target, drive_task())
        (target/'docs'/'HARNESS_SPEC.md').write_text('# Harness Spec\n\n## Global Checks\n', encoding='utf-8')
        report = run_drive(target)
        check(report['decision'] == 'BLOCKED_DECISION', report)
        check('progress harness' in report['reason'].lower(), report)


def test_drive_check_does_not_advance_task_with_unmet_dependency():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        write_drive_project(target, drive_task('T-002', '[ ]', depends='T-001'))
        report = run_drive(target)
        check(report['decision'] == 'BLOCKED_DECISION', report)
        check(report['task'] is None, report)


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


def test_inspect_legacy_cutoff_separates_historical_verification_debt():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        tasks = (
            inspect_task('T-001', '[x]', 'legacy note only')
            + '\n' + inspect_task('T-178', '[~]', 'manual acceptance passed')
        )
        write_inspect_project(target, tasks, 'T-178')
        result = run_inspect(target)
        check(result.returncode == 0, result.stdout + result.stderr)
        check('Status: warning' in result.stdout, result.stdout)
        check('## Verification Gaps\n\n- none' in result.stdout, result.stdout)
        check('## Historical Verification Debt' in result.stdout, result.stdout)
        check('T-001: done task has weak V evidence' in result.stdout, result.stdout)
        check('- Enforcement starts at: T-178' in result.stdout, result.stdout)


def test_inspect_legacy_cutoff_keeps_pre_cutover_doing_task_in_current_scope():
    scripts = str(ROOT/'scripts')
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    import inspect_state

    tasks = [
        {'id': 'T-100', 'status': '[~]'},
        {'id': 'T-101', 'status': '[x]'},
        {'id': 'T-178', 'status': '[x]'},
    ]
    ns = '## Legacy Cutoff\n\n- Enforcement starts at: T-178\n'
    _, enforced, historical, issue = inspect_state.legacy_cutoff(ns, tasks)
    check(not issue, issue)
    check([task['id'] for task in enforced] == ['T-100', 'T-178'], enforced)
    check([task['id'] for task in historical] == ['T-101'], historical)


def test_inspect_legacy_cutoff_keeps_post_cutover_gap_blocking():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        tasks = (
            inspect_task('T-001', '[x]', 'legacy note only')
            + '\n' + inspect_task('T-178', '[x]', 'manual acceptance passed')
            + '\n' + inspect_task('T-179', '[x]', 'weak current note')
        )
        write_inspect_project(target, tasks, 'T-178')
        result = run_inspect(target)
        check(result.returncode == 1, result.stdout + result.stderr)
        current = result.stdout.split('## Historical Verification Debt', 1)[0]
        check('T-179: done task has weak V evidence' in current, result.stdout)
        check('T-001: done task has weak V evidence' not in current, result.stdout)


def test_inspect_legacy_cutoff_fails_closed_when_anchor_is_missing():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        write_inspect_project(target, inspect_task('T-001', '[x]', 'legacy note only'), 'T-178')
        result = run_inspect(target)
        check(result.returncode == 1, result.stdout + result.stderr)
        check('configured enforcement task T-178 was not found' in result.stdout, result.stdout)


def test_inspect_without_legacy_cutoff_preserves_existing_behavior():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        write_inspect_project(target, inspect_task('T-001', '[x]', 'legacy note only'), None)
        result = run_inspect(target)
        check(result.returncode == 1, result.stdout + result.stderr)
        check('T-001: done task has weak V evidence' in result.stdout, result.stdout)
        check('- Enforcement starts at: none (all tasks enforced)' in result.stdout, result.stdout)


def test_inspect_surfaces_drive_decision():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        write_drive_project(target, drive_task())
        (target/'docs'/'HANDOFF.md').write_text('# Handoff\n\nHandoff Level: H0\n\n## Coordinate Summary\n', encoding='utf-8')
        result = subprocess.run([
            sys.executable, str(ROOT/'scripts/inspect_state.py'), '--target', str(target), '--no-write'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        check(result.returncode == 0, result.stdout + result.stderr)
        check('## Drive Decision' in result.stdout, result.stdout)
        check('- Decision: CONTINUE' in result.stdout, result.stdout)


def test_inspect_separates_execution_and_recommendation_and_ignores_closed_drafts():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        write_drive_project(target, drive_task(status='[x]'), mode='manual')
        add_recommendation_contract(target)
        write_contracts(target, 'accepted-human-gated', 'completed')
        (target/'docs'/'HANDOFF.md').write_text(
            '# Handoff\n\nHandoff Level: H0\n\n## Coordinate Summary\n', encoding='utf-8'
        )
        result = run_inspect(target)
        check(result.returncode == 0, result.stdout + result.stderr)
        check('## Execution Decision' in result.stdout, result.stdout)
        check('## Recommendation Decision' in result.stdout, result.stdout)
        check('- Status: PROPOSE_COORDINATE' in result.stdout, result.stdout)
        check('active contract draft' not in result.stdout.lower(), result.stdout)


def test_drift_check_validates_recommendation_contract_contradictions():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        write_drive_project(target, drive_task(status='[x]'), mode='manual')
        add_recommendation_contract(target, mission='complete', next_candidate='T-999')
        result = subprocess.run([
            sys.executable, str(ROOT/'scripts/drift_check.py'), '--target', str(target)
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        check(result.returncode == 1, result.stdout)
        check('Mission complete requires Next Candidate: none' in result.stdout, result.stdout)


def test_drift_check_requires_next_candidate_for_auto_draft_continuation():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        write_drive_project(target, drive_task(status='[x]'), mode='manual')
        add_recommendation_contract(target, next_candidate='')
        result = subprocess.run([
            sys.executable, str(ROOT/'scripts/drift_check.py'), '--target', str(target)
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        check(result.returncode == 1, result.stdout)
        check('auto-draft continuation requires Next Candidate' in result.stdout, result.stdout)


def test_drift_check_requires_active_task_for_active_slice():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        write_drive_project(target, drive_task(status='[x]'), mode='manual')
        add_recommendation_contract(target, current_slice='active', next_candidate='T-002')
        result = subprocess.run([
            sys.executable, str(ROOT/'scripts/drift_check.py'), '--target', str(target)
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        check(result.returncode == 1, result.stdout)
        check('Current Slice active requires a non-empty Active Task' in result.stdout, result.stdout)


def test_drive_observe_reports_forward_progress_and_safety_metrics():
    with tempfile.TemporaryDirectory() as td:
        result = subprocess.run([
            sys.executable, str(ROOT/'scripts/drive_observe.py'), '--target', str(ROOT), '--run-dir', td
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        check(result.returncode == 0, result.stdout + result.stderr)
        summary_path = Path(td)/'summary.json'
        report_path = Path(td)/'report.md'
        check(summary_path.exists(), 'drive observation summary missing')
        check(report_path.exists(), 'drive observation report missing')
        summary = json.loads(summary_path.read_text(encoding='utf-8'))
        check(summary['scenario_agreement'] == 1.0, summary)
        check(summary['unsafe_decision_crossings'] == 0, summary)
        check(summary['baseline_unnecessary_stops'] > summary['drive_unnecessary_stops'], summary)
        check('CodeRail Drive A/B Observation' in result.stdout, result.stdout)


def run_all():
    tests = [v for k, v in globals().items() if k.startswith('test_')]
    for t in tests:
        t(); print('ok', t.__name__)
    print(f'{len(tests)} tests passed')


if __name__ == '__main__':
    run_all()
