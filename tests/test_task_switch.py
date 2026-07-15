from test_support import *
from test_support import _assert_done_inspect_consistent, _lifecycle_env

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

if __name__ == "__main__":
    run_module(globals())
