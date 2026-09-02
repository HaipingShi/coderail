from test_support import *
from test_support import _lifecycle_env

from scripts import delivery_contract


def _commit_pending_files(root: Path, pending: dict) -> None:
    subprocess.check_call(['git', '-C', str(root), 'add', '--', *pending['safe_files']])
    subprocess.check_call([
        'git', '-C', str(root), 'commit', '-qm', pending['expected_commit_message']
    ])


DELIVERY_SECTION = '''
### Delivery Contract

delivery:
  task_status: pending
  milestone_status: in_progress
  product_status: not_assessed
  customer_outcome: Customer can use the delivered capability.
  capability_delta:
    - Added one governed capability.
  remaining_gaps:
    - Product completion is not assessed.
  evidence_boundary:
    - Local verification only.
  recommended_next:
    id: null
    status: none
    reason: No next candidate is declared.
  decisions_required:
    - none
  technical_receipt:
    commits: []
    verification: []
    safe_files: []
'''


def _parsed_delivery(section=DELIVERY_SECTION):
    contract, issues = delivery_contract.parse_delivery_contract(section)
    check(not issues, issues)
    return contract


def _final_delivery(contract=None):
    return delivery_contract.finalized_delivery(
        contract or _parsed_delivery(),
        commits=['abc123'],
        verification=['python3 tests/test_delivery.py (exit 0)'],
        safe_files=['scripts/delivery_contract.py'],
    )


def _write_inspect_project(target: Path, *, readme_marker='', trace_rows=None):
    (target/'docs').mkdir(parents=True, exist_ok=True)
    (target/'docs/NORTH_STAR.md').write_text('''# North Star

## Outcome

- deliver safely

## Current Slice

- Milestone: M-001

## Drive Contract

- Mode: manual
- Next-task mode: recommend
- Terminal condition:
- Progress signal:
- Retry budget: 3
- No-progress limit: 2
- Human gates:
''', encoding='utf-8')
    (target/'docs/TASKS.md').write_text('''# Tasks

## T-001 Completed task

Status: [x]
Type: feature
Rail: full

### CodeRail Coordinate

G — Goal:
- North Star: NS-001

T — Task:
- Complete one task

S — Scope:
- Allowed:
  - README.md
- Forbidden:
  - none

V — Verify:
- test passed

X — Stop:
- none

P — Persist:
- TASKS, TRACE
''', encoding='utf-8')
    (target/'docs/PROGRESS.md').write_text('''# Progress

## 2026-08-06 - Completed task (T-001)

- Checked by: test passed
''', encoding='utf-8')
    (target/'docs/HANDOFF.md').write_text('''# Handoff

<!-- coderail:continuation:start -->
Handoff Level: H0
Last Closed Task: T-001
Closeout State: finalized
Recommendation Status: NO_RECOMMENDATION
Next Candidate/Direction: none
Human Gate: none
Next Executable Step: wait for explicit owner direction
<!-- coderail:continuation:end -->
''', encoding='utf-8')
    (target/'docs/ASSETS.md').write_text('''# Asset Registry

| Asset | Type | Canonical | Update Rule |
|---|---|---:|---|
| README.md | A3 | yes | current delivery view |
| docs/TASKS.md | A3 | yes | update task state |
| docs/TRACELOG.jsonl | A3 append-only | yes | append events only |
''', encoding='utf-8')
    (target/'README.md').write_text(
        '# Project\n\n' + readme_marker + ('\n' if readme_marker else ''),
        encoding='utf-8',
    )
    rows = trace_rows or []
    (target/'docs/TRACELOG.jsonl').write_text(
        ''.join(json.dumps(row) + '\n' for row in rows), encoding='utf-8'
    )
    (target/'docs/TRACE_INDEX.md').write_text('# Trace Index\n', encoding='utf-8')


def _run_inspect(target: Path):
    return subprocess.run(
        [sys.executable, str(ROOT/'scripts/inspect_state.py'), '--target', str(target), '--no-write'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8',
    )


def test_finalized_task_does_not_imply_completed_product():
    delivery = _final_delivery()
    check(delivery['task_status'] == 'finalized', delivery)
    check(delivery['milestone_status'] == 'in_progress', delivery)
    check(delivery['product_status'] == 'not_assessed', delivery)
    check(delivery['product_status'] != 'completed', delivery)


def test_legacy_client_markdown_renderer_is_removed():
    check(not hasattr(delivery_contract, 'render_client_markdown'),
          'legacy seven-section client renderer still exists')


def test_recommended_next_states_remain_distinct_in_normalized_facts():
    normalized = {}
    for status in ('planned', 'recommended', 'active'):
        contract = _parsed_delivery().copy()
        contract['recommended_next'] = {
            'id': 'T-002', 'status': status, 'reason': f'{status} reason',
        }
        delivery = delivery_contract.finalized_delivery(
            contract, commits=[], verification=[], safe_files=[]
        )
        normalized[status] = delivery['recommended_next']
        check(delivery['recommended_next']['status'] == status, delivery)
    check(len({row['status'] for row in normalized.values()}) == 3, normalized)


def test_inspect_blocks_stale_current_truth_for_finalized_task():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        _write_inspect_project(
            target,
            readme_marker='<!-- coderail:current-truth task=T-001 status=active -->',
        )
        result = _run_inspect(target)
        check(result.returncode == 1, result.stdout + result.stderr)
        check('Current Truth Projection Consistency' in result.stdout, result.stdout)
        check('CURRENT_TRUTH_GAP' in result.stdout and 'README.md' in result.stdout,
              result.stdout)
        check('severity=error' in result.stdout, result.stdout)
        check('category=control_plane_conflict' in result.stdout, result.stdout)
        check('blocks=activation' in result.stdout, result.stdout)
        check('- formulation: false' in result.stdout, result.stdout)
        check('- activation: true' in result.stdout, result.stdout)
        check('Status: healthy' not in result.stdout, result.stdout)


def test_inspect_warns_on_stale_prose_without_blocking_formulation():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        _write_inspect_project(target)
        (target/'README.md').write_text('''# Project

## T-001 Current Coordinate

### Closeout

Status: active
''', encoding='utf-8')
        result = _run_inspect(target)
        check(result.returncode == 0, result.stdout + result.stderr)
        check(
            'CURRENT_TRUTH_PROSE_GAP file=README.md line=7 task=T-001 '
            'recorded=active expected=finalized' in result.stdout,
            result.stdout,
        )
        check('severity=warning' in result.stdout, result.stdout)
        check('category=projection_staleness' in result.stdout, result.stdout)
        check('blocks=none' in result.stdout, result.stdout)
        check('- formulation: false' in result.stdout, result.stdout)
        check('Status: warning' in result.stdout, result.stdout)
        check('Repair every declared current-truth projection' not in result.stdout,
              result.stdout)


def test_projection_staleness_never_creates_recursive_governance_coordinate():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        _write_inspect_project(target)
        (target/'README.md').write_text('''# Project

Task: T-001
Closeout State: waiting for commit/push
''', encoding='utf-8')
        north_star = target/'docs/NORTH_STAR.md'
        north_star.write_text(north_star.read_text(encoding='utf-8') + '''
## Recommendation Contract

- Mode: auto-draft
- Mission Status: active
- Current Slice Status: complete
- Next Candidate: PRODUCT-002
- Human Gate: activation
''', encoding='utf-8')
        before_tasks = (target/'docs/TASKS.md').read_bytes()
        before_trace = (target/'docs/TRACELOG.jsonl').read_bytes()
        result = _run_inspect(target)
        check(result.returncode == 0, result.stdout + result.stderr)
        check('category=projection_staleness' in result.stdout, result.stdout)
        check('- Status: PROPOSE_COORDINATE' in result.stdout, result.stdout)
        check('PRODUCT-002' in result.stdout, result.stdout)
        check('GOV' not in (target/'docs/TASKS.md').read_text(encoding='utf-8'),
              'projection debt created a recursive GOV Coordinate')
        check((target/'docs/TASKS.md').read_bytes() == before_tasks,
              'formulation/recommendation changed task ownership')
        check((target/'docs/TRACELOG.jsonl').read_bytes() == before_trace,
              'formulation/recommendation appended lifecycle history')


def test_standard_readme_prose_warns_without_canonical_registration():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        _write_inspect_project(target)
        (target/'docs/ASSETS.md').write_text('''# Asset Registry

| Asset | Type | Canonical | Update Rule |
|---|---|---:|---|
| docs/TASKS.md | A3 | yes | live lifecycle |
| docs/TRACELOG.jsonl | A3 append-only | yes | append only |
''', encoding='utf-8')
        (target/'README.md').write_text('''# Project

Task: T-001
Status: waiting for commit/push
''', encoding='utf-8')
        diagnostics = delivery_contract.current_truth_diagnostics(target, {'T-001'})
        check(len(diagnostics) == 1, diagnostics)
        check(diagnostics[0]['category'] == 'projection_staleness', diagnostics)
        check(diagnostics[0]['blocks'] == 'none', diagnostics)


def test_current_authority_status_scan_binds_display_id_and_exact_coordinate():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        _write_inspect_project(target)
        (target/'.coderail').mkdir()
        (target/'.coderail/tasks.json').write_text(
            json.dumps({'T-001': {'display_id': 'GOV-007'}}), encoding='utf-8'
        )
        for stale_status in (
            'active', 'in_progress', 'pending-closeout',
            'verified-commit-pending', 'pending', '待提交', '待收口',
        ):
            (target/'README.md').write_text(f'''# Project

| Coordinate | Closeout status |
|---|---|
| GOV-007 | {stale_status} |
| T-002 | active |
''', encoding='utf-8')
            diagnostics = delivery_contract.current_truth_diagnostics(target, {'T-001'})
            check(len(diagnostics) == 1, (stale_status, diagnostics))
            diagnostic = diagnostics[0]
            check(
                f'line=5 task=T-001 alias=GOV-007 recorded={stale_status}'
                in diagnostic['evidence'],
                (stale_status, diagnostics),
            )
            check(diagnostic['severity'] == 'warning', diagnostic)
            check(diagnostic['category'] == 'projection_staleness', diagnostic)
            check(diagnostic['blocks'] == 'none', diagnostic)
            check('T-002' not in diagnostic['evidence'], diagnostic)
        (target/'README.md').write_text('''# Project

| Coordinate | Review note |
|---|---|
| GOV-007 | Fixed the old active projection detector. |
''', encoding='utf-8')
        check(
            not delivery_contract.current_truth_diagnostics(target, {'T-001'}),
            'narrative table cell was interpreted as a status assertion',
        )
        (target/'README.md').write_text('''# Project

**Task:** GOV-007
**Status:** 待提交
''', encoding='utf-8')
        diagnostics = delivery_contract.current_truth_diagnostics(target, {'T-001'})
        check(len(diagnostics) == 1 and 'recorded=待提交' in diagnostics[0]['evidence'], diagnostics)
        (target/'README.md').write_text('''# Project

Task: GOV-007
收口：待收口
''', encoding='utf-8')
        diagnostics = delivery_contract.current_truth_diagnostics(target, {'T-001'})
        check(len(diagnostics) == 1 and 'recorded=待收口' in diagnostics[0]['evidence'], diagnostics)


def test_historical_trace_active_event_is_not_current_truth():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        _write_inspect_project(target, trace_rows=[{
            'id': 'TR-001', 'type': 'task', 'task': 'T-001', 'status': 'active',
            'summary': 'historical activation',
        }])
        gaps = delivery_contract.current_truth_projection_gaps(target, {'T-001'})
        check(not gaps, gaps)
        result = _run_inspect(target)
        check('CURRENT_TRUTH_GAP' not in result.stdout, result.stdout)


def test_append_only_progress_lifecycle_wording_is_historical_not_current():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        _write_inspect_project(target)
        assets = target/'docs/ASSETS.md'
        assets.write_text(
            assets.read_text(encoding='utf-8')
            + '| docs/PROGRESS.md | A3 append-only | yes | append events only |\n',
            encoding='utf-8',
        )
        progress = target/'docs/PROGRESS.md'
        progress.write_text(progress.read_text(encoding='utf-8') + '''
- Historical handoff at the time: waiting for commit/push.
- Historical status: active.
''', encoding='utf-8')
        diagnostics = delivery_contract.current_truth_diagnostics(target, {'T-001'})
        check(not any(
            item['category'] == 'projection_staleness'
            and 'docs/PROGRESS.md' in item['evidence']
            for item in diagnostics
        ), diagnostics)


def test_canonical_prose_without_coordinate_status_assertion_is_not_interpreted():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        _write_inspect_project(target)
        (target/'README.md').write_text('''# Project

T-001 fixed the stale active projection detector.
The historical incident said 待收口, but this paragraph declares no current status.
''', encoding='utf-8')
        gaps = delivery_contract.current_truth_projection_gaps(target, {'T-001'})
        check(not gaps, gaps)


def test_done_resume_projection_failure_stays_pending_and_unhealthy():
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        (root/'README.md').write_text('# Project\n', encoding='utf-8')
        assets = root/'docs/ASSETS.md'
        assets.write_text(
            assets.read_text(encoding='utf-8')
            + '| README.md | A3 | yes | current delivery view |\n',
            encoding='utf-8',
        )
        subprocess.check_call(['git', '-C', td, 'add', '--', 'README.md', 'docs/ASSETS.md'])
        subprocess.check_call(['git', '-C', td, 'commit', '-qm', 'fixture: current truth registry'])
        started = cr(
            'start', 'Close with recoverable projections', '--files', 'lib/**',
            '--verify', f'"{sys.executable}" -c "pass"',
        )
        check(started.returncode == 0, started.stdout)
        (root/'lib').mkdir()
        (root/'lib/owned.ts').write_text('export const owned = true;\n', encoding='utf-8')
        pending_result = cr('done', '--no-commit')
        check(pending_result.returncode == 2, pending_result.stdout)
        (root/'README.md').write_text(
            '# Project\n\n<!-- coderail:current-truth task=T-001 status=active -->\n',
            encoding='utf-8',
        )
        resumed = cr('done', '--resume')
        check(resumed.returncode != 0, resumed.stdout)
        check('CURRENT_TRUTH_PROJECTION_PENDING' in resumed.stdout, resumed.stdout)
        check('README.md' in resumed.stdout, resumed.stdout)
        pending = json.loads((root/'.coderail/pending_close.json').read_text(encoding='utf-8'))
        check(pending.get('state') == 'verified-commit-pending', pending)
        handoff = (root/'docs/HANDOFF.md').read_text(encoding='utf-8')
        check('Closeout State: verified-commit-pending' in handoff, handoff)
        inspect = cr('inspect', '--no-write')
        check('Status: healthy' not in inspect.stdout, inspect.stdout)


def test_done_resume_ignores_stale_canonical_prose_as_projection_debt():
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        (root/'README.md').write_text('# Project\n', encoding='utf-8')
        assets = root/'docs/ASSETS.md'
        assets.write_text(
            assets.read_text(encoding='utf-8')
            + '| README.md | A3 | yes | current delivery view |\n',
            encoding='utf-8',
        )
        subprocess.check_call(['git', '-C', td, 'add', '--', 'README.md', 'docs/ASSETS.md'])
        subprocess.check_call(['git', '-C', td, 'commit', '-qm', 'fixture: prose registry'])
        (root/'README.md').write_text('''# Project

## Current Coordinate

Task: T-001
Closeout State: verified-commit-pending
''', encoding='utf-8')
        subprocess.check_call(['git', '-C', td, 'add', '--', 'README.md'])
        subprocess.check_call(['git', '-C', td, 'commit', '-qm', 'fixture: stale prose'])
        started = cr(
            'start', 'Close with prose projection audit', '--files', 'lib/**',
            '--verify', f'"{sys.executable}" -c "pass"',
        )
        check(started.returncode == 0, started.stdout)
        (root/'lib').mkdir()
        (root/'lib/owned.ts').write_text('export const owned = true;\n', encoding='utf-8')
        pending_result = cr('done', '--no-commit')
        check(pending_result.returncode == 2, pending_result.stdout)
        pending = json.loads((root/'.coderail/pending_close.json').read_text(encoding='utf-8'))
        _commit_pending_files(root, pending)
        resumed = cr('done', '--resume')
        check(resumed.returncode == 0, resumed.stdout)
        check('CURRENT_TRUTH_PROSE_GAP' not in resumed.stdout, resumed.stdout)
        inspect = cr('inspect', '--no-write')
        check(inspect.returncode == 0, inspect.stdout)
        check('CURRENT_TRUTH_PROSE_GAP' in inspect.stdout, inspect.stdout)
        check('category=projection_staleness' in inspect.stdout, inspect.stdout)


def test_done_does_not_reopen_when_only_canonical_prose_is_stale():
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        (root/'README.md').write_text('# Project\n', encoding='utf-8')
        assets = root/'docs/ASSETS.md'
        assets.write_text(
            assets.read_text(encoding='utf-8')
            + '| README.md | A3 | yes | current delivery view |\n',
            encoding='utf-8',
        )
        subprocess.check_call(['git', '-C', td, 'add', '--', 'README.md', 'docs/ASSETS.md'])
        subprocess.check_call(['git', '-C', td, 'commit', '-qm', 'fixture: done prose registry'])
        started = cr(
            'start', 'Reject stale prose before commit',
            '--files', 'lib/**', '--files', 'README.md',
            '--verify', f'"{sys.executable}" -c "pass"',
        )
        check(started.returncode == 0, started.stdout)
        (root/'lib').mkdir()
        (root/'lib/owned.ts').write_text('export const owned = true;\n', encoding='utf-8')
        (root/'README.md').write_text('''# Project

Task: T-001
Status: in_progress
''', encoding='utf-8')
        before_head = subprocess.check_output(
            ['git', '-C', td, 'rev-parse', 'HEAD'], text=True
        ).strip()
        result = cr('done')
        check(result.returncode == 0, result.stdout)
        check('CURRENT_TRUTH_PROJECTION_FAILED' not in result.stdout, result.stdout)
        check('Completed:' in result.stdout, result.stdout)
        after_head = subprocess.check_output(
            ['git', '-C', td, 'rev-parse', 'HEAD'], text=True
        ).strip()
        check(after_head != before_head, (before_head, after_head, result.stdout))


def test_done_no_commit_allows_stale_prose_in_verified_snapshot():
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        (root/'README.md').write_text('# Project\n', encoding='utf-8')
        assets = root/'docs/ASSETS.md'
        assets.write_text(
            assets.read_text(encoding='utf-8')
            + '| README.md | A3 | yes | current delivery view |\n',
            encoding='utf-8',
        )
        subprocess.check_call(['git', '-C', td, 'add', '--', 'README.md', 'docs/ASSETS.md'])
        subprocess.check_call(['git', '-C', td, 'commit', '-qm', 'fixture: pending prose registry'])
        started = cr(
            'start', 'Reject stale prose before pending snapshot',
            '--files', 'lib/**', '--files', 'README.md',
            '--verify', f'"{sys.executable}" -c "pass"',
        )
        check(started.returncode == 0, started.stdout)
        (root/'lib').mkdir()
        (root/'lib/owned.ts').write_text('export const owned = true;\n', encoding='utf-8')
        (root/'README.md').write_text('''# Project

Task: T-001
提交：待提交
''', encoding='utf-8')
        result = cr('done', '--no-commit')
        check(result.returncode == 2, result.stdout)
        check('verified-commit-pending' in result.stdout, result.stdout)
        check('CURRENT_TRUTH_PROJECTION_FAILED' not in result.stdout, result.stdout)
        check((root/'.coderail/pending_close.json').exists(), result.stdout)


def test_done_synchronizes_declared_current_truth_marker():
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        (root/'README.md').write_text(
            '# Project\n\n<!-- coderail:current-truth task=T-001 status=active -->\n',
            encoding='utf-8',
        )
        assets = root/'docs/ASSETS.md'
        assets.write_text(
            assets.read_text(encoding='utf-8')
            + '| README.md | A3 | yes | current delivery view |\n',
            encoding='utf-8',
        )
        subprocess.check_call(['git', '-C', td, 'add', '--', 'README.md', 'docs/ASSETS.md'])
        subprocess.check_call(['git', '-C', td, 'commit', '-qm', 'fixture: active projection'])
        started = cr(
            'start', 'Synchronize a declared projection',
            '--files', 'lib/**', '--files', 'README.md',
            '--verify', f'"{sys.executable}" -c "pass"',
        )
        check(started.returncode == 0, started.stdout)
        (root/'lib').mkdir()
        (root/'lib/owned.ts').write_text('export const owned = true;\n', encoding='utf-8')
        result = cr('done')
        check(result.returncode == 0, result.stdout)
        readme = (root/'README.md').read_text(encoding='utf-8')
        check('task=T-001 status=finalized' in readme, readme)
        inspect = cr('inspect', '--no-write')
        check(inspect.returncode == 0 and 'CURRENT_TRUTH_GAP' not in inspect.stdout,
              inspect.stdout)


def test_manual_drive_recommendation_does_not_activate_task():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        write_drive_project(
            target,
            drive_task(status='[x]') + '\n' + drive_task('T-002', '[ ]', autonomy='human-gated'),
            mode='manual',
        )
        add_recommendation_contract(target, next_candidate='T-002')
        before = (target/'docs/TASKS.md').read_text(encoding='utf-8')
        report = subprocess.run(
            [sys.executable, str(ROOT/'scripts/drive_check.py'), '--target', str(target), '--json'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8',
        )
        check(report.returncode == 0, report.stdout + report.stderr)
        payload = json.loads(report.stdout)
        check(payload['mode'] == 'manual' and payload['decision'] == 'BLOCKED_DECISION', payload)
        check(payload['recommendation']['requires_human_for_execution'] is True, payload)
        check((target/'docs/TASKS.md').read_text(encoding='utf-8') == before,
              'manual recommendation activated or registered a task')


def test_legacy_task_without_delivery_contract_is_not_assessed():
    contract, issues = delivery_contract.parse_delivery_contract('G — Goal:\n- legacy task\n')
    check(not issues, issues)
    delivery = delivery_contract.finalized_delivery(
        contract, commits=['abc123'], verification=['test passed'], safe_files=['legacy.txt']
    )
    check(delivery['milestone_status'] == 'not_assessed', delivery)
    check(delivery['product_status'] == 'not_assessed', delivery)
    check(delivery['customer_outcome'] == 'not_assessed', delivery)
    check(delivery['recommended_next']['status'] == 'none', delivery)


def test_done_emits_bounded_owner_receipt_instead_of_legacy_report():
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        started = cr(
            'start', 'Deliver a client-visible result', '--files', 'lib/**',
            '--verify', f'"{sys.executable}" -c "pass"',
        )
        check(started.returncode == 0, started.stdout)
        tasks = root/'docs/TASKS.md'
        tasks.write_text(tasks.read_text(encoding='utf-8') + DELIVERY_SECTION, encoding='utf-8')
        (root/'lib').mkdir()
        (root/'lib/delivered.ts').write_text('export const delivered = true;\n', encoding='utf-8')
        result = cr('done')
        check(result.returncode == 0, result.stdout)
        check('Completed:' in result.stdout, result.stdout)
        check('== Done:' not in result.stdout, result.stdout)
        check('# 客户交付摘要' not in result.stdout, result.stdout)
        check('## 技术附录' not in result.stdout, result.stdout)
        lines = [line for line in result.stdout.splitlines() if line.strip()]
        check(3 <= len(lines) <= 6, lines)


def test_delivery_contract_parser_self_heals_finish_task_residue():
    # BUG-1 regression: an interrupted closeout appended its nine lifecycle
    # receipt lines after the contract; the next done then failed with
    # "unsupported Delivery Contract syntax" on every retry. The parser must
    # ignore CodeRail's own residue lines so a poisoned file self-heals.
    residue = "\n".join(f"{label}: x" for label in [
        "Task result", "Harness result", "Handoff level", "Handoff updated",
        "Inspect status", "Drive decision", "Resume anchor",
        "Next executable step", "Auto commit"])
    bodies = [DELIVERY_SECTION + residue + "\n"]
    bodies.append(
        DELIVERY_SECTION.replace(
            "### Delivery Contract\n", "### Delivery Contract\n\n```yaml\n", 1
        ).rstrip("\n") + "\n```\n" + residue + "\n"
    )
    for body in bodies:
        contract, issues = delivery_contract.parse_delivery_contract(body)
        check(not issues, issues)
    contract, _ = delivery_contract.parse_delivery_contract(bodies[0])
    check(contract["customer_outcome"] == "Customer can use the delivered capability.", contract)


if __name__ == "__main__":
    run_module(globals())
