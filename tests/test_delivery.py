from test_support import *
from test_support import _lifecycle_env

from scripts import delivery_contract


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


def test_client_markdown_keeps_technical_receipt_last():
    markdown = delivery_contract.render_client_markdown(_final_delivery())
    headings = [
        '## 交付结果', '## 能力变化', '## 项目整体状态', '## 未完成与风险',
        '## 推荐下一任务', '## 需要决策', '## 技术附录',
    ]
    positions = [markdown.index(heading) for heading in headings]
    check(positions == sorted(positions), markdown)
    client_body = markdown[markdown.index('## 交付结果'):]
    check(not client_body.startswith(('commit', 'Commit', 'safe files', 'verification')),
          client_body)
    check(markdown.index('abc123') > markdown.index('## 技术附录'), markdown)


def test_recommended_next_states_remain_distinct():
    rendered = {}
    for status in ('planned', 'recommended', 'active'):
        contract = _parsed_delivery().copy()
        contract['recommended_next'] = {
            'id': 'T-002', 'status': status, 'reason': f'{status} reason',
        }
        rendered[status] = delivery_contract.render_client_markdown(
            delivery_contract.finalized_delivery(
                contract, commits=[], verification=[], safe_files=[]
            )
        )
        check(f'- 状态：{status}' in rendered[status], rendered[status])
    check(len(set(rendered.values())) == 3, rendered)


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
        check('Status: healthy' not in result.stdout, result.stdout)


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


def test_no_next_candidate_renders_none_without_invention():
    markdown = delivery_contract.render_client_markdown(_final_delivery())
    section = markdown.split('## 推荐下一任务', 1)[1].split('## 需要决策', 1)[0]
    check('- ID：none' in section, section)
    check('- 状态：none' in section, section)
    check('T-002' not in section and 'next task' not in section.lower(), section)


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


def test_done_emits_client_delivery_separately_from_internal_receipt():
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
        check('== Done:' in result.stdout, result.stdout)
        check('# 客户交付摘要' in result.stdout, result.stdout)
        client = result.stdout.split('# 客户交付摘要', 1)[1]
        check(client.lstrip().startswith('## 交付结果'), client)
        check(client.index('## 技术附录') > client.index('## 需要决策'), client)


if __name__ == "__main__":
    run_module(globals())
