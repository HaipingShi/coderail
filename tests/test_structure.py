from pathlib import Path
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


def test_manifests_exist():
    check((ROOT/'.claude-plugin/plugin.json').exists(), 'missing claude manifest')
    check((ROOT/'.codex-plugin/plugin.json').exists(), 'missing codex manifest')


def test_versions_consistent():
    # FN-015: VERSION is the single source of truth for every version display.
    expected = (ROOT/'VERSION').read_text(encoding='utf-8').strip().splitlines()[0].strip()
    for path in ['.claude-plugin/plugin.json', '.codex-plugin/plugin.json', 'package.json']:
        data = json.loads((ROOT/path).read_text(encoding='utf-8'))
        check(data['version'] == expected, f'{path} version mismatch')
    readme = (ROOT/'README.md').read_text(encoding='utf-8')
    check(f'version-v{expected}-' in readme, f'README badge does not match VERSION ({expected})')
    shim = (ROOT/'scripts/local_entry.py').read_text(encoding='utf-8')
    check('SHIM_VERSION = "0.0.0-dev"' in shim,
          'local_entry.py template must keep the 0.0.0-dev placeholder (stamped at install)')
    check('def effective_version' in shim,
          'local_entry.py must fall back to reading home VERSION for hand-copied shims')


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


def test_paused_status_is_current_but_non_active():
    import scripts.doctor as doctor
    import scripts.coordinate_check as coordinate_check

    check(not doctor.is_historical_status('[p]'), 'paused work must remain current governance state')
    check(coordinate_check._extract_status('Status: [p]') == '[p]',
          'Coordinate parser must preserve paused status')


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
    check('`[p]` paused' in tasks, 'TASKS template should expose formal paused state')
    check('## Paused Tasks' in status, 'status template should surface paused tasks')
    check('## Task Switch Gate' in status, 'status template should expose switch ownership health')
    agents = (ROOT/'project-template/AGENTS.md').read_text(encoding='utf-8')
    check('run `switch`' in agents and '--force' in agents,
          'AGENTS template should route task changes through Task Switch Gate')


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


def test_task_switch_force_cannot_create_multiple_active_tasks():
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        r = cr('start', 'First owner', '--verify', 'true')
        check(r.returncode == 0, r.stdout)
        r = cr('start', 'Second owner', '--verify', 'true', '--force')
        check(r.returncode == 1, r.stdout)
        check('switch' in r.stdout.lower(), r.stdout)
        tasks = (root/'docs/TASKS.md').read_text(encoding='utf-8')
        check(tasks.count('Status: [~]') == 1, tasks)


def test_task_start_records_preexisting_dirty_fingerprint():
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        (root/'notes.txt').write_text('belongs to the user\n', encoding='utf-8')
        r = cr('start', 'Fingerprint baseline', '--files', 'notes.txt,work.txt',
               '--verify', 'true')
        check(r.returncode == 0, r.stdout)
        meta = json.loads((root/'.coderail/tasks.json').read_text(encoding='utf-8'))
        baseline = meta['T-001']['baseline']
        note = next(row for row in baseline['files'] if row['path'] == 'notes.txt')
        check(note['status'] == '??', note)
        check(len(note['fingerprint']) == 64, note)
        check('belongs to the user' not in json.dumps(baseline), baseline)


def test_task_closeout_excludes_unchanged_dirty_baseline_from_commit():
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        (root/'notes.txt').write_text('pre-existing\n', encoding='utf-8')
        r = cr('start', 'Scoped work', '--files', 'notes.txt,work.txt', '--verify', 'true')
        check(r.returncode == 0, r.stdout)
        (root/'work.txt').write_text('task-owned\n', encoding='utf-8')
        r = cr('done')
        check(r.returncode == 0, r.stdout)
        committed = subprocess.check_output(
            ['git', '-C', td, 'log', '-2', '--name-only', '--format='],
            text=True, encoding='utf-8')
        check('work.txt' in committed, committed)
        check('notes.txt' not in committed, committed)
        status = subprocess.check_output(
            ['git', '-C', td, 'status', '--short'], text=True, encoding='utf-8')
        check('notes.txt' in status, status)


def test_task_done_ignores_unchanged_forbidden_baseline():
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        (root/'notes.txt').write_text('unrelated forbidden baseline\n', encoding='utf-8')
        r = cr('start', 'Narrow task', '--files', 'work.txt', '--avoid', 'notes.txt',
               '--verify', 'true')
        check(r.returncode == 0, r.stdout)
        (root/'work.txt').write_text('owned\n', encoding='utf-8')
        r = cr('done')
        check(r.returncode == 0, r.stdout)
        status = subprocess.check_output(
            ['git', '-C', td, 'status', '--short'], text=True, encoding='utf-8')
        check('notes.txt' in status, status)


def test_task_switch_checkpoint_commits_pauses_then_starts_destination():
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        r = cr('start', 'Checkpoint source', '--files', 'work.txt', '--verify', 'true',
               '--accept', 'final acceptance remains open')
        check(r.returncode == 0, r.stdout)
        (root/'work.txt').write_text('verified checkpoint\n', encoding='utf-8')
        r = cr('switch', 'Checkpoint destination', '--checkpoint',
               '--files', 'next.txt', '--verify', 'true')
        check(r.returncode == 0, r.stdout)
        tasks = (root/'docs/TASKS.md').read_text(encoding='utf-8')
        check(tasks.count('Status: [~]') == 1, tasks)
        check('## T-001 Checkpoint source\n\nStatus: [p]' in tasks, tasks)
        check('## T-002 Checkpoint destination\n\nStatus: [~]' in tasks, tasks)
        committed = subprocess.check_output(
            ['git', '-C', td, 'log', '-2', '--name-only', '--format='],
            text=True, encoding='utf-8')
        check('work.txt' in committed, committed)


def test_task_switch_accepted_source_closes_before_destination_starts():
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        r = cr('start', 'Accepted source', '--files', 'work.txt', '--verify', 'true')
        check(r.returncode == 0, r.stdout)
        (root/'work.txt').write_text('accepted work\n', encoding='utf-8')
        r = cr('switch', 'Accepted destination', '--verify', 'true')
        check(r.returncode == 0, r.stdout)
        tasks = (root/'docs/TASKS.md').read_text(encoding='utf-8')
        check('## T-001 Accepted source\n\nStatus: [x]' in tasks, tasks)
        check('## T-002 Accepted destination\n\nStatus: [~]' in tasks, tasks)
        check(tasks.count('Status: [~]') == 1, tasks)
        committed = subprocess.check_output(
            ['git', '-C', td, 'log', '-2', '--name-only', '--format='],
            text=True, encoding='utf-8')
        check('work.txt' in committed, committed)


def test_task_switch_uncommittable_work_writes_h3_and_stays_current():
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        r = cr('start', 'Failing source', '--verify', 'false')
        check(r.returncode == 0, r.stdout)
        r = cr('switch', 'Must not start')
        check(r.returncode == 1, r.stdout)
        check('--continue-current' in r.stdout and '--dirty-fork' in r.stdout, r.stdout)
        tasks = (root/'docs/TASKS.md').read_text(encoding='utf-8')
        check(tasks.count('Status: [~]') == 1, tasks)
        check('Must not start' not in tasks, tasks)
        handoff = (root/'docs/HANDOFF.md').read_text(encoding='utf-8')
        check('Handoff Level: H3' in handoff, handoff)
        r = cr('switch', '--continue-current')
        check(r.returncode == 0, r.stdout)
        tasks = (root/'docs/TASKS.md').read_text(encoding='utf-8')
        check(tasks.count('Status: [~]') == 1 and 'Must not start' not in tasks, tasks)


def test_task_switch_dirty_fork_pauses_source_and_preserves_resume_ownership():
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        r = cr('start', 'Dirty source', '--files', 'source.txt', '--verify', 'true')
        check(r.returncode == 0, r.stdout)
        (root/'source.txt').write_text('source-owned and not committed\n', encoding='utf-8')
        source_baseline = json.loads(
            (root/'.coderail/tasks.json').read_text(encoding='utf-8'))['T-001']['baseline']
        r = cr('switch', 'Fork destination', '--dirty-fork', '--verify', 'true')
        check(r.returncode == 0, r.stdout)
        tasks = (root/'docs/TASKS.md').read_text(encoding='utf-8')
        check(tasks.count('Status: [~]') == 1 and 'Status: [p]' in tasks, tasks)
        meta = json.loads((root/'.coderail/tasks.json').read_text(encoding='utf-8'))
        check(any(row['path'] == 'source.txt'
                  for row in meta['T-002']['baseline']['files']), meta)
        check(meta['T-001']['baseline'] == source_baseline, meta['T-001'])
        r = cr('switch', '--to', 'T-001')
        check(r.returncode == 0, r.stdout)
        tasks = (root/'docs/TASKS.md').read_text(encoding='utf-8')
        check('## T-001 Dirty source\n\nStatus: [~]' in tasks, tasks)
        check('## T-002 Fork destination\n\nStatus: [x]' in tasks, tasks)
        meta = json.loads((root/'.coderail/tasks.json').read_text(encoding='utf-8'))
        check(meta['T-001']['baseline'] == source_baseline, meta['T-001'])
        status = subprocess.check_output(
            ['git', '-C', td, 'status', '--short'], text=True, encoding='utf-8')
        check('source.txt' in status, status)


def test_task_activation_blocks_closed_dirty_owner_without_waiver():
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        (root/'leftover.txt').write_text('closed task residue\n', encoding='utf-8')
        meta_path = root/'.coderail/tasks.json'
        meta_path.write_text(json.dumps({
            'T-000': {
                'closed_pending': {
                    'files': [{'path': 'leftover.txt', 'status': '??', 'fingerprint': 'old'}]
                }
            }
        }, indent=2) + '\n', encoding='utf-8')
        r = cr('start', 'Blocked destination', '--verify', 'true')
        check(r.returncode == 1, r.stdout)
        check('leftover.txt' in r.stdout and '--dirty-fork' in r.stdout, r.stdout)
        r = cr('start', 'Waived destination', '--verify', 'true', '--dirty-fork')
        check(r.returncode == 0, r.stdout)
        tasks = (root/'docs/TASKS.md').read_text(encoding='utf-8')
        check(tasks.count('Status: [~]') == 1, tasks)
        meta = json.loads(meta_path.read_text(encoding='utf-8'))
        check(any(row['path'] == 'leftover.txt'
                  for row in meta['T-001']['baseline']['files']), meta)


def test_task_next_go_uses_closed_dirty_gate():
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        tasks = root/'docs/TASKS.md'
        tasks.write_text(tasks.read_text(encoding='utf-8').rstrip() + '''

## T-001 Queued destination

Status: [ ]
Type: feature
Rail: full
''', encoding='utf-8')
        (root/'leftover.txt').write_text('closed owner\n', encoding='utf-8')
        (root/'.coderail/tasks.json').write_text(json.dumps({
            'T-000': {'closed_pending': {'files': [
                {'path': 'leftover.txt', 'status': '??', 'fingerprint': 'old'}
            ]}}
        }, indent=2) + '\n', encoding='utf-8')
        r = cr('next', '--go')
        check(r.returncode == 1, r.stdout)
        check('leftover.txt' in r.stdout and 'closed task' in r.stdout.lower(), r.stdout)
        check('Status: [ ]' in tasks.read_text(encoding='utf-8'),
              tasks.read_text(encoding='utf-8'))


def test_task_switch_implementation_has_no_git_push_path():
    for relative in ['scripts/coderail.py', 'scripts/task_switch.py',
                     'scripts/closeout_check.py', 'scripts/finish_task.py']:
        source = (ROOT/relative).read_text(encoding='utf-8')
        check('["git", "push"' not in source and "['git', 'push'" not in source,
              f'automatic push command found in {relative}')


def test_progress_entries_match_their_tasks():
    # FN-017-1: start A -> done A -> start B -> done B; each PROGRESS entry
    # must carry ITS OWN task's title, never the previous one.
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        r = cr('start', 'X-1 Alpha feature', '--verify', 'true'); check(r.returncode == 0, r.stdout)
        r = cr('done'); check(r.returncode == 0, r.stdout)
        r = cr('start', 'X-2 Beta feature', '--verify', 'true'); check(r.returncode == 0, r.stdout)
        r = cr('done'); check(r.returncode == 0, r.stdout)
        progress = (root/'docs/PROGRESS.md').read_text(encoding='utf-8')
        entries = [l for l in progress.splitlines() if l.startswith('## ')]
        check(len(entries) == 2, f'expected 2 entries, got {entries}')
        check('Beta feature' in entries[0] and 'Alpha feature' not in entries[0],
              f'newest entry cross-contaminated: {entries[0]}')
        check('Alpha feature' in entries[1] and 'Beta feature' not in entries[1],
              f'older entry cross-contaminated: {entries[1]}')
        # FN-014: business id leads everywhere.
        check('X-2 (internal' in entries[0], f'business id not leading: {entries[0]}')


def test_progress_checked_by_carries_real_verify_evidence():
    # FN-017-2: verify exit codes must reach the report; no boilerplate.
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        cr('start', 'Verified task', '--verify', 'true')
        r = cr('done'); check(r.returncode == 0, r.stdout)
        progress = (root/'docs/PROGRESS.md').read_text(encoding='utf-8')
        check('`true` exit 0' in progress, f'verify evidence missing: {progress}')
        check('Manually confirm the result works as intended' not in progress,
              'boilerplate leaked into Checked by')
        # Unverified fallback wording (task without verify commands).
        cr('start', 'Unverified task')
        r = cr('done'); check(r.returncode == 0, r.stdout)
        progress = (root/'docs/PROGRESS.md').read_text(encoding='utf-8')
        check('unverified - no verify commands registered' in progress,
              f'unverified wording missing: {progress}')


def test_progress_lists_acceptance_and_defers_queue():
    # FN-017-3: per-item acceptance statuses land in PROGRESS; deferred items
    # are trackable as queued tasks. Also covers numbered --accept-status.
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        cr('start', 'Accept task', '--verify', 'true',
           '--accept', 'item one', '--accept', 'item two', '--accept', 'item three')
        r = cr('done')  # missing statuses -> refuse, numbered list shown
        check(r.returncode == 1 and '1. item one' in r.stdout, r.stdout)
        r = cr('done', '--accept-status', '1=done', '--accept-status', '3=done',
               '--accept-status', '2=deferred')
        check(r.returncode == 0, r.stdout)
        progress = (root/'docs/PROGRESS.md').read_text(encoding='utf-8')
        check('Acceptance [done]: item one' in progress, progress)
        check('Acceptance [deferred]: item two' in progress, progress)
        check('Acceptance [done]: item three' in progress, progress)
        tasks = (root/'docs/TASKS.md').read_text(encoding='utf-8')
        check('## T-002 item two' in tasks, f'deferred item not queued: {tasks[-400:]}')


def test_done_output_is_summary_with_report_on_disk():
    # FN-018: default done output stays compact; full gate report is on disk
    # with verify output tails.
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        cr('start', 'Quiet task', '--verify', 'echo deep-evidence-line && true')
        r = cr('done'); check(r.returncode == 0, r.stdout)
        check('== Done:' in r.stdout, r.stdout)
        core = r.stdout.split('== Done:')[1].split('== Now tell')[0]
        check(len(core.strip().splitlines()) <= 15, f'summary too long:\n{core}')
        check('Done Gate Report' not in r.stdout, 'full gate report leaked to console')
        reports = list((root/'.coderail/reports').glob('done-*.md'))
        check(len(reports) == 1, f'expected 1 report, got {reports}')
        body = reports[0].read_text(encoding='utf-8')
        check('deep-evidence-line' in body, 'verify output tail missing from report')
        check('Full gate output' in body, 'gate output missing from report')


def test_done_with_warnings_still_writes_ledger():
    # FN-023: a done that produces warnings (EOF newline + TDD heuristic)
    # must STILL write the PROGRESS entry and the on-disk report.
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        # File without trailing newline -> EOF warning in the gates.
        (root/'src').mkdir(exist_ok=True)
        (root/'src/parser.py').write_text('def parse(): pass', encoding='utf-8')  # no EOF newline
        # Title with correctness-sensitive words + promised test never touched
        # -> TDD warnings on done.
        r = cr('start', 'Fix parser validation logic', '--verify', 'true',
               '--tests', 'tests/test_parser.py')
        check(r.returncode == 0, r.stdout)
        r = cr('done')
        check(r.returncode == 0, r.stdout)
        check('WARNING' in r.stdout, f'expected TDD warning in output: {r.stdout}')
        progress = (root/'docs/PROGRESS.md').read_text(encoding='utf-8')
        check('Fix parser validation logic' in progress,
              f'PROGRESS entry missing despite warnings (FN-023): {progress}')
        reports = list((root/'.coderail/reports').glob('done-*.md'))
        check(len(reports) == 1, f'report missing despite warnings (FN-023): {reports}')


def test_done_ledger_failure_is_loud_and_repairable():
    # FN-023: if a ledger step fails, done must say so explicitly (not report
    # success), and progress --repair must backfill the missing entry.
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        cr('start', 'Ledger failure task', '--verify', 'true')
        # Sabotage the journal: make docs/PROGRESS.md an unwritable directory.
        (root/'docs/PROGRESS.md').mkdir()
        r = cr('done')
        check(r.returncode == 1, f'done must fail loudly on ledger error: {r.stdout}')
        check('LEDGER ERROR' in r.stdout, f'no explicit ledger error: {r.stdout}')
        check('progress --repair' in r.stdout, f'no repair remedy given: {r.stdout}')
        # Repair: restore the path, then backfill.
        (root/'docs/PROGRESS.md').rmdir()
        r = cr('progress')
        check(r.returncode == 1 and 'Ledger gap' in r.stdout, r.stdout)
        r = cr('progress', '--repair')
        check(r.returncode == 0, r.stdout)
        progress = (root/'docs/PROGRESS.md').read_text(encoding='utf-8')
        check('Ledger failure task' in progress, f'repair did not backfill: {progress}')
        check('retroactive entry' in progress, f'repair entry not marked honest: {progress}')
        r = cr('progress')
        check(r.returncode == 0 and 'complete' in r.stdout, r.stdout)


def test_tdd_heuristic_respects_declared_type():
    # FN-024: --type refactor silences the TDD hint from start to done;
    # a feature-typed correctness-sensitive task without --tests keeps it.
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        r = cr('start', 'Refactor the parser validation logic',
               '--type', 'refactor', '--verify', 'true')
        check(r.returncode == 0, r.stdout)
        r = cr('done')
        check(r.returncode == 0, r.stdout)
        reports = list((root/'.coderail/reports').glob('done-*.md'))
        body = reports[-1].read_text(encoding='utf-8')
        check('likely needs TDD' not in body,
              f'refactor task still got TDD hint (FN-024): {body}')
        # Control: same wording, feature type, no --tests -> hint kept.
        r = cr('start', 'Improve the parser validation logic',
               '--type', 'feature', '--verify', 'true')
        check(r.returncode == 0, r.stdout)
        r = cr('done')
        check(r.returncode == 0, r.stdout)
        body = sorted((root/'.coderail/reports').glob('done-*.md'))[-1].read_text(encoding='utf-8')
        check('likely needs TDD' in body,
              f'feature task lost the TDD hint (FN-024 control): {body}')


def test_files_globs_expand_and_accumulate():
    # FN-021: --files is repeatable and supports globs mixed with plain paths.
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        (root/'src/director').mkdir(parents=True)
        for n in ['director_core.ts', 'director_utils.ts']:
            (root/'src/director'/n).write_text('export {}\n', encoding='utf-8')
        r = cr('start', 'Glob scope task',
               # FN-029: a backslash-style pattern must still expand and, more
               # importantly, must be stored forward-slash - TASKS.md is a
               # committed artifact matched against git output on every OS.
               '--files', r'src\director\director*.ts',
               '--files', 'docs/NOTES.md,README.md',
               '--verify', 'true')
        check(r.returncode == 0, r.stdout)
        tasks = (root/'docs/TASKS.md').read_text(encoding='utf-8')
        for expect in ['src/director/director_core.ts', 'src/director/director_utils.ts',
                       'docs/NOTES.md', 'README.md']:
            check(f'- {expect}' in tasks, f'missing expanded file {expect}: {tasks[-800:]}')
        # Narrow to THIS task's Allowed scope block (the template's example
        # task legitimately contains an escaped "\##" heading elsewhere).
        task_block = tasks[tasks.rindex('## T-001 Glob scope task'):]
        allowed = task_block[task_block.index('Allowed:'):task_block.index('Forbidden:')]
        check('\\' not in allowed,
              f'FN-029: backslash leaked into committed TASKS scope: {allowed!r}')
        check('- src/director/director*.ts' in allowed,
              f'glob intent was lost after expansion: {allowed!r}')


def test_done_commits_file_created_after_start_under_glob_and_inspect_is_healthy():
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        r = cr('start', 'Own future library files', '--files', 'lib/**',
               '--verify', f'"{sys.executable}" -c "pass"')
        check(r.returncode == 0, r.stdout)
        (root/'lib/audio').mkdir(parents=True)
        (root/'lib/audio/mock-wav.ts').write_text('export const wav = true;\n', encoding='utf-8')
        r = cr('done')
        check(r.returncode == 0, r.stdout)
        tracked = subprocess.check_output(
            ['git', '-C', td, 'ls-files', 'lib/audio/mock-wav.ts'], text=True).strip()
        check(tracked == 'lib/audio/mock-wav.ts', tracked)
        inspect = cr('inspect', '--no-write')
        check(inspect.returncode == 0 and 'Status: healthy' in inspect.stdout, inspect.stdout)
        check('Closed-task uncommitted ownership: none' in inspect.stdout, inspect.stdout)


def test_unborn_repository_baseline_adoption_is_audited_and_safe():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        subprocess.check_call(['git', 'init', '-q'], cwd=td)
        subprocess.check_call(['git', 'config', 'user.email', 't@t.io'], cwd=td)
        subprocess.check_call(['git', 'config', 'user.name', 't'], cwd=td)
        subprocess.run([sys.executable, str(ROOT/'scripts/init_project.py'), '--target', td],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        (root/'lib').mkdir()
        (root/'lib/app.ts').write_text('export {};\n', encoding='utf-8')
        (root/'.env').write_text('TOKEN=secret\n', encoding='utf-8')
        (root/'node_modules/pkg').mkdir(parents=True)
        (root/'node_modules/pkg/index.js').write_text('generated\n', encoding='utf-8')
        (root/'dist').mkdir()
        (root/'dist/app.js').write_text('built\n', encoding='utf-8')

        def cr(*args):
            return subprocess.run([sys.executable, str(ROOT/'scripts/coderail.py'), *args,
                                   '--target', td], capture_output=True, text=True,
                                  encoding='utf-8', errors='replace')

        r = cr('start', 'Adopt existing baseline', '--files', 'lib/**',
               '--files', '.coderail/**,docs/**,AGENTS.md,CLAUDE.md',
               '--adopt-baseline', '--verify', f'"{sys.executable}" -c "pass"')
        check(r.returncode == 0, r.stdout + r.stderr)
        meta = json.loads((root/'.coderail/tasks.json').read_text(encoding='utf-8'))['T-001']
        adoption = meta.get('baseline_adoption', {})
        check(adoption.get('head') is None and adoption.get('files'), adoption)
        check(all('fingerprint' in row and 'content' not in row for row in adoption['files']), adoption)
        r = cr('done')
        check(r.returncode == 1 and '.env' in r.stdout, r.stdout)
        check('Status: [~]' in (root/'docs/TASKS.md').read_text(encoding='utf-8'), r.stdout)
        (root/'.env').unlink()
        r = cr('done')
        check(r.returncode == 0, r.stdout)
        tracked = set(subprocess.check_output(['git', '-C', td, 'ls-files'], text=True).splitlines())
        check('lib/app.ts' in tracked, tracked)
        check('.env' not in tracked and not any(p.startswith('node_modules/') for p in tracked), tracked)
        check(not any(p.startswith('dist/') for p in tracked), tracked)
        inspect = cr('inspect', '--no-write')
        check(inspect.returncode == 0 and 'Status: healthy' in inspect.stdout, inspect.stdout)


def test_closeout_implementation_never_uses_git_add_dot():
    source = (ROOT/'scripts/closeout_check.py').read_text(encoding='utf-8')
    check('["add", "."]' not in source and "['add', '.']" not in source,
          'closeout must stage an explicit audited path list')


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


def test_atomic_done_handles_tracked_delete_and_rename_then_inspect_is_healthy():
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        (root/'lib').mkdir()
        (root/'lib/modify.ts').write_text('old\n', encoding='utf-8')
        (root/'lib/delete.ts').write_text('delete\n', encoding='utf-8')
        (root/'lib/old-name.ts').write_text('rename\n', encoding='utf-8')
        subprocess.check_call(['git', '-C', td, 'add', '--', 'lib/modify.ts',
                               'lib/delete.ts', 'lib/old-name.ts'])
        subprocess.check_call(['git', '-C', td, 'commit', '-qm', 'fixture'])
        r = cr('start', 'Atomic tracked lifecycle', '--files', 'lib/**',
               '--verify', f'"{sys.executable}" -c "pass"')
        check(r.returncode == 0, r.stdout)
        (root/'lib/modify.ts').write_text('new\n', encoding='utf-8')
        (root/'lib/delete.ts').unlink()
        (root/'lib/old-name.ts').rename(root/'lib/new-name.ts')
        _assert_done_inspect_consistent(
            root, cr, ['lib/modify.ts', 'lib/delete.ts', 'lib/old-name.ts', 'lib/new-name.ts'])


def test_atomic_done_refuses_outside_and_sensitive_paths_without_closing():
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        r = cr('start', 'Narrow atomic task', '--files', 'lib/**',
               '--verify', f'"{sys.executable}" -c "pass"')
        check(r.returncode == 0, r.stdout)
        (root/'lib').mkdir()
        (root/'lib/owned.ts').write_text('safe\n', encoding='utf-8')
        (root/'outside.txt').write_text('ambiguous\n', encoding='utf-8')
        (root/'.env.local').write_text('API_KEY=secret\n', encoding='utf-8')
        (root/'api_key.txt').write_text('secret\n', encoding='utf-8')
        result = cr('done')
        check(result.returncode == 1, result.stdout)
        check(all(path in result.stdout for path in ['outside.txt', '.env.local', 'api_key.txt']),
              result.stdout)
        check('== Done:' not in result.stdout, result.stdout)
        check('Status: [~]' in (root/'docs/TASKS.md').read_text(encoding='utf-8'), result.stdout)
        tracked = subprocess.check_output(['git', '-C', td, 'ls-files'], text=True).splitlines()
        check('outside.txt' not in tracked and '.env.local' not in tracked, tracked)


def test_atomic_done_excludes_ignored_generated_and_local_state():
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        r = cr('start', 'Generated artifact boundary', '--files', 'lib/**',
               '--verify', f'"{sys.executable}" -c "pass"')
        check(r.returncode == 0, r.stdout)
        (root/'lib').mkdir()
        (root/'lib/owned.ts').write_text('safe\n', encoding='utf-8')
        for path in ['node_modules/pkg/index.js', 'build/app.js', '.coderail/reports/local.md']:
            target = root/path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text('generated\n', encoding='utf-8')
        result = cr('done')
        check(result.returncode == 1, result.stdout)
        check('build/app.js' in result.stdout and 'node_modules/pkg/index.js' in result.stdout,
              result.stdout)
        check('== Done:' not in result.stdout, result.stdout)
        tracked = subprocess.check_output(['git', '-C', td, 'ls-files'], text=True).splitlines()
        check(not any(p.startswith(('node_modules/', 'build/', '.coderail/reports/'))
                      for p in tracked), tracked)


def test_atomic_done_fails_and_reopens_when_post_commit_status_changes():
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        r = cr('start', 'Detect post commit mutation', '--files', 'lib/**',
               '--verify', f'"{sys.executable}" -c "pass"')
        check(r.returncode == 0, r.stdout)
        (root/'lib').mkdir()
        owned = root/'lib/owned.ts'
        owned.write_text('before\n', encoding='utf-8')
        hook = root/'.git/hooks/post-commit'
        hook.write_text('#!/bin/sh\nprintf "after\\n" >> lib/owned.ts\n', encoding='utf-8')
        hook.chmod(0o755)
        result = cr('done')
        check(result.returncode == 1, result.stdout)
        check('POST-CLOSE CONSISTENCY FAILED' in result.stdout, result.stdout)
        check('lib/owned.ts' in result.stdout, result.stdout)
        check('== Done:' not in result.stdout, result.stdout)
        tasks = (root/'docs/TASKS.md').read_text(encoding='utf-8')
        check('Status: [!]' in tasks, tasks)


def test_atomic_done_reopens_when_closeout_commit_fails():
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        r = cr('start', 'Commit failure contract', '--files', 'lib/**',
               '--verify', f'"{sys.executable}" -c "pass"')
        check(r.returncode == 0, r.stdout)
        (root/'lib').mkdir()
        (root/'lib/owned.ts').write_text('safe\n', encoding='utf-8')
        hook = root/'.git/hooks/pre-commit'
        hook.write_text('#!/bin/sh\nexit 1\n', encoding='utf-8')
        hook.chmod(0o755)
        result = cr('done')
        check(result.returncode == 1, result.stdout)
        check('auto commit failed' in result.stdout.lower(), result.stdout)
        check('== Done:' not in result.stdout, result.stdout)
        tasks = (root/'docs/TASKS.md').read_text(encoding='utf-8')
        check('Status: [!]' in tasks, tasks)
        check((root/'lib/owned.ts').exists(), 'failed commit must preserve the work')


def test_closeout_convergence_spec_and_task_sequence_are_registered():
    spec = (ROOT/'docs/CLOSEOUT_CONVERGENCE.md').read_text(encoding='utf-8')
    for term in ['RepositorySnapshot', 'owned-safe', 'FINALIZED', 'Non-Goals',
                 'T-007', 'T-008', 'T-009']:
        check(term in spec, f'convergence spec missing {term}')
    tasks = (ROOT/'docs/TASKS.md').read_text(encoding='utf-8')
    positions = [tasks.index(f'## T-00{number}') for number in [7, 8, 9]]
    check(positions == sorted(positions), f'convergence tasks out of order: {positions}')
    check('Depends on:\n- T-007' in tasks and 'Depends on:\n- T-008' in tasks,
          'convergence dependency chain is incomplete')


def test_repository_snapshot_is_immutable_and_preserves_rename_origin():
    sys.path.insert(0, str(ROOT/'scripts'))
    import repository_state
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        subprocess.check_call(['git', 'init', '-q'], cwd=td)
        subprocess.check_call(['git', 'config', 'user.email', 't@t.io'], cwd=td)
        subprocess.check_call(['git', 'config', 'user.name', 't'], cwd=td)
        (root/'old.txt').write_text('content\n', encoding='utf-8')
        subprocess.check_call(['git', 'add', '--', 'old.txt'], cwd=td)
        subprocess.check_call(['git', 'commit', '-qm', 'fixture'], cwd=td)
        (root/'old.txt').rename(root/'new.txt')
        subprocess.check_call(['git', 'add', '--', 'old.txt', 'new.txt'], cwd=td)
        snapshot = repository_state.capture(root)
        renamed = next(row for row in snapshot.files if row.path == 'new.txt')
        check(renamed.original_path == 'old.txt', renamed)
        try:
            renamed.path = 'mutated.txt'
        except Exception:
            pass
        else:
            raise AssertionError('FileState must be immutable')


def test_repository_classifier_is_the_single_closeout_vocabulary():
    sys.path.insert(0, str(ROOT/'scripts'))
    import repository_state
    rows = (
        repository_state.FileState(' M', 'lib/a.ts'),
        repository_state.FileState('??', '.env.local'),
        repository_state.FileState('??', 'build/app.js'),
        repository_state.FileState('??', 'outside.txt'),
        repository_state.FileState('!!', 'node_modules/'),
    )
    result = repository_state.classify(
        rows, allowed=['lib/**'], forbidden=[], unchanged_baseline=set(),
        state_files=set(), include_state=False,
    )
    check(result.safe == ('lib/a.ts',), result)
    check(result.sensitive == ('.env.local',), result)
    check(result.generated == ('build/app.js',), result)
    check(result.outside == ('outside.txt',), result)
    check(result.ignored == ('node_modules/',), result)


def test_repository_state_is_the_only_porcelain_parser():
    owners = []
    for relative in ['scripts/repository_state.py', 'scripts/task_switch.py',
                     'scripts/closeout_check.py', 'scripts/done_gate.py',
                     'scripts/inspect_state.py']:
        source = (ROOT/relative).read_text(encoding='utf-8')
        if 'status", "--porcelain' in source or "status', '--porcelain" in source:
            owners.append(relative)
    check(owners == ['scripts/repository_state.py'], f'duplicate porcelain parsers: {owners}')


def test_closeout_transaction_is_the_only_success_authority():
    sys.path.insert(0, str(ROOT/'scripts'))
    import closeout_transaction
    tx = closeout_transaction.CloseoutTransaction('T-999')
    for phase in ['VERIFIED', 'SNAPSHOTTED', 'CLASSIFIED', 'STAGED', 'COMMITTED',
                  'PERSISTED', 'RESCANNED']:
        tx.advance(closeout_transaction.Phase[phase])
        check(not tx.success, f'{phase} declared success early')
    tx.finalize(inspect_status='healthy', residual_paths=[])
    check(tx.success and tx.phase is closeout_transaction.Phase.FINALIZED, tx.result())


def test_closeout_transaction_failure_suppresses_success_and_keeps_exact_paths():
    sys.path.insert(0, str(ROOT/'scripts'))
    import closeout_transaction
    tx = closeout_transaction.CloseoutTransaction('T-999')
    tx.advance(closeout_transaction.Phase.VERIFIED)
    tx.fail(closeout_transaction.Failure.POST_COMMIT_DIRTY, ['lib/residue.ts'])
    result = tx.result()
    check(not result.success, result)
    check(result.failure is closeout_transaction.Failure.POST_COMMIT_DIRTY, result)
    check(result.paths == ('lib/residue.ts',), result)


def test_queued_task_hydrates_verify_and_acceptance_contract():
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        tasks = root/'docs/TASKS.md'
        tasks.write_text(tasks.read_text(encoding='utf-8').rstrip() + '''

## T-001 Queued contract evidence

Status: [ ]
Type: bug
Rail: full

### CodeRail Coordinate

G — Goal
- Preserve queued verification.

T — Task
- Queued contract evidence.

S — Scope
Allowed:
  - lib/**
Forbidden:
  - none

V — Verify
- Run: `false` (must exit 0)

A — Acceptance
- [ ] queued acceptance survives activation

X — Stop
- verification failure

P — Persist
- TASKS, TRACE
''', encoding='utf-8')
        result = cr('next', '--go')
        check(result.returncode == 0, result.stdout)
        result = cr('done', '--accept-status', '1=done')
        check(result.returncode == 1, result.stdout)
        check('VERIFY FAILED' in result.stdout and 'false' in result.stdout, result.stdout)
        check('Status: [~]' in tasks.read_text(encoding='utf-8'), result.stdout)


def test_shim_probes_candidate_homes():
    # FN-022: config.local.json overrides config.json, and coderail_home may
    # be a list of candidates probed in order.
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        shim = root/'.coderail/coderail.py'
        # Break the committed config; provide a working local override.
        (root/'.coderail/config.json').write_text(
            json.dumps({'coderail_home': ['/nonexistent/one', '/nonexistent/two']}),
            encoding='utf-8')
        env = {k: v for k, v in os.environ.items() if k != 'CODERAIL_HOME'}
        r = subprocess.run([sys.executable, str(shim), 'check'],
                           capture_output=True, text=True, cwd=td, env=env)
        check(r.returncode == 2 and 'candidate' in (r.stderr or ''),
              f'broken candidates should be listed: {r.stderr}')
        (root/'.coderail/config.local.json').write_text(
            json.dumps({'coderail_home': str(ROOT)}), encoding='utf-8')
        r = subprocess.run([sys.executable, str(shim), 'check'],
                           capture_output=True, text=True, cwd=td, env=env)
        check(r.returncode == 0, f'local override not honoured: {r.stderr}\n{r.stdout}')


def test_done_next_flag_sets_journal_next():
    # FN-020: --next injects the real next step into the journal.
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        cr('start', 'Next field task', '--verify', 'true')
        r = cr('done', '--next', 'wire the harness to file-backed storage')
        check(r.returncode == 0, r.stdout)
        progress = (root/'docs/PROGRESS.md').read_text(encoding='utf-8')
        check('- Next: wire the harness to file-backed storage' in progress,
              f'--next not honoured: {progress}')


def test_done_produces_all_four_artifacts_end_to_end():
    # FN-027: the real done flow (no mocks) must leave all four artifacts at
    # once - PROGRESS entry, on-disk report, TASKS closed, commit made - and
    # the captured Done Gate Report must not be blocked. Two consecutive
    # tasks, per the field acceptance criteria.
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        for n, (biz, title) in enumerate([('T-201', 'First artifact task'),
                                          ('T-202', 'Second artifact task')], 1):
            r = cr('start', f'{biz} {title}', '--verify', 'true')
            check(r.returncode == 0, r.stdout)
            r = cr('done', '--next', f'next step after {biz}')
            check(r.returncode == 0, r.stdout)
            progress = (root/'docs/PROGRESS.md').read_text(encoding='utf-8')
            check(title in progress, f'(1/4) PROGRESS missing {biz}: {progress}')
            check(f'next step after {biz}' in progress, f'--next lost for {biz}: {progress}')
            reports = list((root/'.coderail/reports').glob('done-*.md'))
            check(len(reports) == n, f'(2/4) report count {len(reports)} != {n}')
            body = sorted(reports)[-1].read_text(encoding='utf-8')
            check('Status: blocked' not in body,
                  f'(FN-027b) Done Gate blocked inside a passing close: {body}')
            tasks = (root/'docs/TASKS.md').read_text(encoding='utf-8')
            check(tasks.count('Status: [x]') == n, f'(3/4) TASKS close count != {n}: {tasks}')
            log = subprocess.run(['git', 'log', '--oneline'], cwd=td,
                                 capture_output=True, text=True).stdout
            check(f'chore({biz}/' in log, f'(4/4) commit missing for {biz}: {log}')
            check(not (root/'.coderail/pending_close.json').exists(),
                  'snapshot must be cleared after a fully-ledgered close')
        r = cr('progress')
        check(r.returncode == 0 and 'complete' in r.stdout,
              f'built-in audit disagrees with artifacts: {r.stdout}')


def test_snapshot_survives_ledger_failure_and_repair_restores_params():
    # FN-028: a close whose ledger step fails must keep the snapshot on disk,
    # and progress --repair must restore the REAL --next text and per-item
    # acceptance verdicts from it - not default copy.
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        r = cr('start', 'Snapshot recovery task', '--verify', 'true',
               '--accept', 'first criterion', '--accept', 'second criterion')
        check(r.returncode == 0, r.stdout)
        (root/'docs/PROGRESS.md').unlink(missing_ok=True)
        (root/'docs/PROGRESS.md').mkdir()  # sabotage: journal unwritable
        r = cr('done', '--next', 'switch harness to real compiler output',
               '--accept-status', '1=done', '--accept-status', '2=deferred')
        check(r.returncode == 1 and 'LEDGER ERROR' in r.stdout, r.stdout)
        check((root/'.coderail/pending_close.json').exists(),
              'snapshot must survive a failed ledger (FN-028)')
        (root/'docs/PROGRESS.md').rmdir()
        r = cr('progress', '--repair')
        check(r.returncode == 0, r.stdout)
        progress = (root/'docs/PROGRESS.md').read_text(encoding='utf-8')
        check('- Next: switch harness to real compiler output' in progress,
              f'real --next text not restored (FN-028): {progress}')
        check('[done]' in progress and 'first criterion' in progress,
              f'acceptance verdicts not restored: {progress}')
        check('[deferred]' in progress and 'second criterion' in progress,
              f'deferred verdict not restored: {progress}')
        check(not (root/'.coderail/pending_close.json').exists(),
              'snapshot must be consumed by repair')


def test_failed_done_on_open_task_still_says_rerun():
    # FN-027: "run done again" is only printed when the task is genuinely
    # still open (here: verify fails, task stays [~]).
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        cr('start', 'Failing verify task', '--verify', 'false')
        r = cr('done')
        check(r.returncode == 1, r.stdout)
        check('coderail done' in r.stdout and 'again' in r.stdout,
              f'open-task failure should still suggest rerun: {r.stdout}')
        tasks = (root/'docs/TASKS.md').read_text(encoding='utf-8')
        check('Status: [~]' in tasks, 'task must remain open after failed verify')


def run_all():
    tests = [v for k, v in globals().items() if k.startswith('test_')]
    for t in tests:
        t(); print('ok', t.__name__)
    print(f'{len(tests)} tests passed')


if __name__ == '__main__':
    run_all()
