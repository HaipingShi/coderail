from test_support import *
from test_support import _assert_done_inspect_consistent, _lifecycle_env

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

def test_compacted_history_uses_progress_and_trace_for_legacy_cutoff():
    scripts = str(ROOT/'scripts')
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    import inspect_state

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root/'docs').mkdir()
        (root/'docs/TASKS.md').write_text('# Tasks\n', encoding='utf-8')
        (root/'docs/PROGRESS.md').write_text('''# Progress

## 2026-07-16 - Current verified task (T-002)

- Checked by: `pytest` exit 0

## 2026-07-16 - Legacy weak task (T-001)

- Checked by: unverified - no verify commands registered
''', encoding='utf-8')
        events = [
            {'type': 'verify', 'task': 'T-001', 'harness_result': 'skipped'},
            {'type': 'verify', 'task': 'T-002', 'harness_result': 'passed'},
        ]
        (root/'docs/TRACELOG.jsonl').write_text(
            ''.join(json.dumps(event) + '\n' for event in events), encoding='utf-8'
        )
        tasks = inspect_state.task_statuses(root)
        check([task['id'] for task in tasks] == ['T-001', 'T-002'], tasks)
        _, enforced, historical, issue = inspect_state.legacy_cutoff(
            '## Legacy Cutoff\n\n- Enforcement starts at: T-002\n', tasks
        )
        check(not issue, issue)
        check([task['id'] for task in enforced] == ['T-002'], enforced)
        check([task['id'] for task in historical] == ['T-001'], historical)
        check(not inspect_state.weak_verification_gaps(enforced), enforced)
        check('T-001: done task has weak V evidence'
              in inspect_state.weak_verification_gaps(historical), historical)

def test_inspect_surfaces_drive_decision():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        write_drive_project(target, drive_task())
        (target/'docs'/'HANDOFF.md').write_text('# Handoff\n\nHandoff Level: H0\n\n## Coordinate Summary\n', encoding='utf-8')
        result = subprocess.run([
            sys.executable, str(ROOT/'scripts/inspect_state.py'), '--target', str(target), '--no-write'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        check(result.returncode == 0, result.stdout + result.stderr)
        check('Point-in-time snapshot' in result.stdout, result.stdout)
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

def test_inspect_detects_closed_task_pending_handoff_contradiction():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        write_drive_project(target, drive_task(status='[x]'), mode='manual')
        (target/'docs'/'HANDOFF.md').write_text('''# Handoff

项目自定义正文，不由 CodeRail 解释。

<!-- coderail:continuation:start -->
Handoff Level: H1
Last Closed Task: T-001
Closeout State: pending-closeout
Recommendation Status: REQUEST_DIRECTION
Next Candidate/Direction: owner choice
Human Gate: owner decision
Next Executable Step: ask the owner
<!-- coderail:continuation:end -->
''', encoding='utf-8')
        result = run_inspect(target)
        check(result.returncode == 0, result.stdout + result.stderr)
        check('Status: warning' in result.stdout, result.stdout)
        check('- Needs update: yes' in result.stdout, result.stdout)
        check('T-001' in result.stdout and 'pending-closeout' in result.stdout,
              result.stdout)

def test_inspect_uses_only_structured_handoff_block_not_free_text_keywords():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        write_drive_project(target, '', mode='manual')
        (target/'docs'/'HANDOFF.md').write_text('''# Handoff

这里可写 needs、待收口或任何项目正文，都不应参与机器判断。

<!-- coderail:continuation:start -->
Handoff Level: H0
Last Closed Task: none
Closeout State: idle
Recommendation Status: NO_RECOMMENDATION
Next Candidate/Direction: none
Human Gate: none
Next Executable Step: wait for explicit direction
<!-- coderail:continuation:end -->
''', encoding='utf-8')
        result = run_inspect(target)
        check(result.returncode == 0, result.stdout + result.stderr)
        check('- Needs update: no' in result.stdout, result.stdout)
        check('free-text keyword' not in result.stdout, result.stdout)

def test_write_inspect_migrates_legacy_handoff_without_rewriting_project_prose():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        write_drive_project(target, '', mode='manual')
        custom = '# Handoff\n\n项目自定义正文 needs 保留。\n\n## Coordinate Summary\n'
        (target/'docs'/'HANDOFF.md').write_text(custom, encoding='utf-8')
        result = subprocess.run([
            sys.executable, str(ROOT/'scripts/inspect_state.py'),
            '--target', str(target), '--write',
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        check(result.returncode == 0, result.stdout + result.stderr)
        migrated = (target/'docs'/'HANDOFF.md').read_text(encoding='utf-8')
        check('项目自定义正文 needs 保留。' in migrated, migrated)
        check(migrated.count('<!-- coderail:continuation:start -->') == 1, migrated)
        check('Closeout State: idle' in migrated, migrated)
        check('- Needs update: no' in result.stdout, result.stdout)

def test_write_inspect_repairs_malformed_delimiters_without_parsing_project_prose():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        write_drive_project(target, '', mode='manual')
        custom = '''# Handoff

项目自定义正文。

<!-- coderail:continuation:start -->
broken machine fragment
'''
        (target/'docs'/'HANDOFF.md').write_text(custom, encoding='utf-8')
        result = subprocess.run([
            sys.executable, str(ROOT/'scripts/inspect_state.py'),
            '--target', str(target), '--write',
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        check(result.returncode == 0, result.stdout + result.stderr)
        repaired = (target/'docs'/'HANDOFF.md').read_text(encoding='utf-8')
        check('项目自定义正文。' in repaired, repaired)
        check('broken machine fragment' in repaired, repaired)
        check(repaired.count('<!-- coderail:continuation:start -->') == 1, repaired)
        check(repaired.count('<!-- coderail:continuation:end -->') == 1, repaired)
        check('- Needs update: no' in result.stdout, result.stdout)

if __name__ == "__main__":
    run_module(globals())
