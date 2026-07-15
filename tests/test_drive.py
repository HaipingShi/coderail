from test_support import *
from test_support import _assert_done_inspect_consistent, _lifecycle_env

def test_drive_field_value_does_not_cross_blank_field_lines():
    scripts = str(ROOT/'scripts')
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    import drive_check

    text = '- Terminal condition:\n\nContinuous Drive requires evidence.\n'
    check(drive_check.field_value(text, 'Terminal condition') == '', 'blank field must stay blank')

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

if __name__ == "__main__":
    run_module(globals())
