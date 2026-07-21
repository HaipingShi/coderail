from test_support import *
from test_support import _assert_done_inspect_consistent, _lifecycle_env

def _pending_close(root):
    return json.loads((root/'.coderail/pending_close.json').read_text(encoding='utf-8'))

def _commit_pending_files(root, pending):
    subprocess.check_call(['git', '-C', str(root), 'add', '--', *pending['safe_files']])
    subprocess.check_call([
        'git', '-C', str(root), 'commit', '-qm', pending['expected_commit_message']
    ])

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

def test_done_accepts_inline_code_formatted_allowed_glob():
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        result = cr('start', 'Formatted allowed scope', '--files', 'lib/**',
                    '--verify', f'"{sys.executable}" -c "pass"')
        check(result.returncode == 0, result.stdout)
        tasks = root/'docs/TASKS.md'
        tasks.write_text(
            tasks.read_text(encoding='utf-8').replace('  - lib/**', '  - `lib/**`'),
            encoding='utf-8',
        )
        (root/'lib').mkdir()
        (root/'lib/new-file.ts').write_text('export const value = 1;\n', encoding='utf-8')

        result = cr('done')
        check(result.returncode == 0, result.stdout)
        tracked = subprocess.check_output(
            ['git', '-C', td, 'ls-files', 'lib/new-file.ts'], text=True).strip()
        check(tracked == 'lib/new-file.ts', tracked)
        inspect = cr('inspect', '--no-write')
        check(inspect.returncode == 0 and 'Status: healthy' in inspect.stdout, inspect.stdout)

def test_done_keeps_inline_code_formatted_forbidden_path_blocking():
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        result = cr('start', 'Formatted forbidden scope', '--files', 'lib/**',
                    '--avoid', 'lib/secret.ts',
                    '--verify', f'"{sys.executable}" -c "pass"')
        check(result.returncode == 0, result.stdout)
        tasks = root/'docs/TASKS.md'
        text = tasks.read_text(encoding='utf-8')
        text = text.replace('  - lib/**', '  - `lib/**`')
        text = text.replace('  - lib/secret.ts', '  - `lib/secret.ts`')
        tasks.write_text(text, encoding='utf-8')
        (root/'lib').mkdir()
        (root/'lib/secret.ts').write_text('export const token = "secret";\n', encoding='utf-8')

        result = cr('done')
        check(result.returncode == 1, result.stdout)
        check('lib/secret.ts' in result.stdout, result.stdout)
        check('== Done:' not in result.stdout, result.stdout)
        tracked = subprocess.check_output(
            ['git', '-C', td, 'ls-files', 'lib/secret.ts'], text=True).strip()
        check(not tracked, tracked)

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

def test_closeout_rejects_legacy_scope_contradiction_before_status_transition():
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        allowed = 'lib/memory/__tests__/memory-write-effect-gate.test.ts'
        tasks = root/'docs/TASKS.md'
        tasks.write_text(tasks.read_text(encoding='utf-8').rstrip() + f'''

## T-001 Legacy contradictory scope

Status: [~]
Type: bug
Rail: full

### CodeRail Coordinate

G — Goal
- Reject legacy contradictory scope.

T — Task
- Legacy contradictory scope.

S — Scope
Allowed:
  - {allowed}
Forbidden:
  - lib/memory/**

V — Verify
- Run: `true` (must exit 0)

X — Stop
- scope contradiction

P — Persist
- TASKS, TRACE
''', encoding='utf-8')
        target = root/allowed
        target.parent.mkdir(parents=True)
        target.write_text('test\n', encoding='utf-8')
        result = cr('done')
        check(result.returncode == 1, result.stdout)
        for expected in ['SCOPE_CONTRADICTION', allowed, 'lib/memory/**']:
            check(expected in result.stdout, result.stdout)
        check('== Done:' not in result.stdout, result.stdout)
        check('Status: [~]' in tasks.read_text(encoding='utf-8'),
              'closeout contradiction changed task status')

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

def test_atomic_done_preserves_verified_commit_pending_when_closeout_commit_fails():
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        r = cr('start', 'Commit failure contract', '--files', 'lib/**',
               '--verify', f'"{sys.executable}" -c "pass"')
        check(r.returncode == 0, r.stdout)
        (root/'lib').mkdir()
        (root/'lib/owned.ts').write_text('safe\n', encoding='utf-8')
        hook = root/'.git/hooks/pre-commit'
        hook.write_text(
            '#!/bin/sh\n'
            'echo "fatal: Unable to create .git/index.lock: Permission denied" >&2\n'
            'exit 1\n',
            encoding='utf-8',
        )
        hook.chmod(0o755)
        result = cr('done')
        check(result.returncode == 2, result.stdout)
        check('auto commit failed' in result.stdout.lower(), result.stdout)
        check('verified-commit-pending' in result.stdout, result.stdout)
        check('== Done:' not in result.stdout, result.stdout)
        tasks = (root/'docs/TASKS.md').read_text(encoding='utf-8')
        check('Status: [!]' not in tasks, tasks)
        pending = _pending_close(root)
        check(pending.get('state') == 'verified-commit-pending', pending)
        check(pending.get('closeout_mode') == 'auto', pending)
        check(pending.get('verify_results') == [{'cmd': f'"{sys.executable}" -c "pass"',
                                                 'exit': 0}], pending)
        check('lib/owned.ts' in pending.get('safe_files', []), pending)
        for path in ['docs/PROGRESS.md', 'docs/TRACELOG.jsonl',
                     'docs/TRACE_INDEX.md', 'docs/CODERAIL_STATUS.md']:
            check(path in pending.get('safe_files', []), pending)
        check(pending.get('scope_classification', {}).get('docs/TASKS.md') == 'clean',
              pending)
        check(pending.get('expected_commit_message'), pending)
        check((root/'lib/owned.ts').exists(), 'failed commit must preserve the work')
        inspect = cr('inspect', '--no-write')
        check('verified-commit-pending' in inspect.stdout and 'T-001' in inspect.stdout,
              inspect.stdout)

def test_manual_exact_commit_then_resume_finalizes_without_coderail_residue():
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        cr('start', 'Manual recovery', '--files', 'lib/**', '--verify', 'true')
        (root/'lib').mkdir()
        (root/'lib/owned.ts').write_text('safe\n', encoding='utf-8')
        hook = root/'.git/hooks/pre-commit'
        hook.write_text('#!/bin/sh\nexit 1\n', encoding='utf-8')
        hook.chmod(0o755)
        result = cr('done')
        check(result.returncode == 2, result.stdout)
        pending = _pending_close(root)
        hook.unlink()
        _commit_pending_files(root, pending)
        result = cr('done', '--resume')
        check(result.returncode == 0 and '== Done:' in result.stdout, result.stdout)
        check(not (root/'.coderail/pending_close.json').exists(),
              'finalize must consume the pending snapshot')
        status = subprocess.check_output(
            ['git', '-C', td, 'status', '--porcelain'], text=True).strip()
        check(not status, status)
        inspect = cr('inspect', '--no-write')
        check(inspect.returncode == 0 and 'Status: healthy' in inspect.stdout, inspect.stdout)

def test_permission_recovery_resume_retries_only_exact_pending_files():
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        cr('start', 'Automatic permission recovery', '--files', 'lib/**', '--verify', 'true')
        (root/'lib').mkdir()
        (root/'lib/owned.ts').write_text('safe\n', encoding='utf-8')
        hook = root/'.git/hooks/pre-commit'
        hook.write_text('#!/bin/sh\nexit 1\n', encoding='utf-8')
        hook.chmod(0o755)
        result = cr('done')
        check(result.returncode == 2, result.stdout)
        pending = _pending_close(root)
        hook.unlink()
        result = cr('done', '--resume')
        check(result.returncode == 0 and '== Done:' in result.stdout, result.stdout)
        committed = set(subprocess.check_output(
            ['git', '-C', td, 'show', '--pretty=', '--name-only', 'HEAD'],
            text=True, encoding='utf-8').splitlines())
        check(committed == set(pending['safe_files']),
              f'resume commit differs from exact safe snapshot: {committed} != {pending["safe_files"]}')
        check(not subprocess.check_output(
            ['git', '-C', td, 'status', '--porcelain'], text=True).strip(),
            'permission recovery left closeout residue')

def test_explicit_no_commit_snapshots_all_generated_closeout_files_without_post_dirty():
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        cr('start', 'Manual closeout mode', '--files', 'lib/**', '--verify', 'true')
        (root/'lib').mkdir()
        (root/'lib/owned.ts').write_text('safe\n', encoding='utf-8')
        head = subprocess.check_output(['git', '-C', td, 'rev-parse', 'HEAD'], text=True).strip()
        result = cr('done', '--no-commit')
        check(result.returncode == 2, result.stdout)
        check('verified-commit-pending' in result.stdout, result.stdout)
        check('POST-CLOSE CONSISTENCY FAILED' not in result.stdout, result.stdout)
        check('== Done:' not in result.stdout, result.stdout)
        pending = _pending_close(root)
        check(pending.get('closeout_mode') == 'manual', pending)
        check(pending.get('pre_commit_head') == head, pending)
        for path in ['lib/owned.ts', '.coderail/tasks.json', 'docs/PROGRESS.md',
                     'docs/TRACELOG.jsonl', 'docs/TRACE_INDEX.md',
                     'docs/CODERAIL_STATUS.md']:
            check(path in pending.get('safe_files', []), pending)
        for path in ['.coderail/tasks.json', 'docs/PROGRESS.md', 'docs/TASKS.md',
                     'docs/TRACELOG.jsonl', 'docs/TRACE_INDEX.md',
                     'docs/CODERAIL_STATUS.md']:
            check(path in pending.get('scope_classification', {}), pending)
        current = subprocess.check_output(['git', '-C', td, 'rev-parse', 'HEAD'], text=True).strip()
        check(current == head, 'explicit no-commit unexpectedly created a commit')

def test_pending_recovery_never_stages_or_rewrites_unrelated_dirty_files():
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        unrelated = root/'notes.txt'
        unrelated.write_text('user-owned\n', encoding='utf-8')
        cr('start', 'Preserve unrelated work', '--files', 'lib/**', '--verify', 'true')
        (root/'lib').mkdir()
        (root/'lib/owned.ts').write_text('safe\n', encoding='utf-8')
        result = cr('done', '--no-commit')
        check(result.returncode == 2, result.stdout)
        pending = _pending_close(root)
        check('notes.txt' not in pending.get('safe_files', []), pending)
        _commit_pending_files(root, pending)
        result = cr('done', '--resume')
        check(result.returncode == 0, result.stdout)
        check(unrelated.read_text(encoding='utf-8') == 'user-owned\n',
              'resume rewrote unrelated content')
        status = subprocess.check_output(
            ['git', '-C', td, 'status', '--short'], text=True)
        check(status.strip() == '?? notes.txt', status)
        tracked = subprocess.check_output(
            ['git', '-C', td, 'ls-files', 'notes.txt'], text=True).strip()
        check(not tracked, tracked)

def test_pending_resume_is_idempotent_without_duplicate_ledger_or_commit():
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        cr('start', 'Idempotent resume', '--files', 'lib/**', '--verify', 'true')
        (root/'lib').mkdir()
        (root/'lib/owned.ts').write_text('safe\n', encoding='utf-8')
        result = cr('done', '--no-commit')
        check(result.returncode == 2, result.stdout)
        pending = _pending_close(root)
        _commit_pending_files(root, pending)
        first = cr('done', '--resume')
        check(first.returncode == 0, first.stdout)
        before = {
            'commits': subprocess.check_output(
                ['git', '-C', td, 'rev-list', '--count', 'HEAD'], text=True).strip(),
            'progress': (root/'docs/PROGRESS.md').read_text(encoding='utf-8'),
            'trace': (root/'docs/TRACELOG.jsonl').read_text(encoding='utf-8'),
        }
        second = cr('done', '--resume')
        check(second.returncode == 0, second.stdout)
        after = {
            'commits': subprocess.check_output(
                ['git', '-C', td, 'rev-list', '--count', 'HEAD'], text=True).strip(),
            'progress': (root/'docs/PROGRESS.md').read_text(encoding='utf-8'),
            'trace': (root/'docs/TRACELOG.jsonl').read_text(encoding='utf-8'),
        }
        check(after == before, f'repeated resume changed durable state: {before} -> {after}')
        check('already finalized' in second.stdout.lower(), second.stdout)

def test_closeout_convergence_spec_and_task_sequence_are_registered():
    spec = (ROOT/'docs/CLOSEOUT_CONVERGENCE.md').read_text(encoding='utf-8')
    for term in ['RepositorySnapshot', 'owned-safe', 'FINALIZED', 'Non-Goals',
                 'T-007', 'T-008', 'T-009']:
        check(term in spec, f'convergence spec missing {term}')
    positions = [spec.index(f'### T-00{number}') for number in [7, 8, 9]]
    check(positions == sorted(positions), f'convergence tasks out of order: {positions}')
    progress = (ROOT/'docs/PROGRESS.md').read_text(encoding='utf-8')
    trace = (ROOT/'docs/TRACELOG.jsonl').read_text(encoding='utf-8')
    for task_id in ['T-007', 'T-008', 'T-009']:
        check(f'({task_id})' in progress, f'PROGRESS authority missing {task_id}')
        check(f'"task": "{task_id}"' in trace, f'TRACE authority missing {task_id}')

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

def test_runtime_has_no_repository_state_compatibility_adapters():
    task_switch = (ROOT/'scripts/task_switch.py').read_text(encoding='utf-8')
    closeout = (ROOT/'scripts/closeout_check.py').read_text(encoding='utf-8')
    coderail = (ROOT/'scripts/coderail.py').read_text(encoding='utf-8')
    repository = (ROOT/'scripts/repository_state.py').read_text(encoding='utf-8')
    check('def git_status_entries' not in task_switch,
          'task_switch still projects canonical snapshots into legacy status rows')
    check('def git_status_entries' not in closeout,
          'closeout_check still owns a status compatibility adapter')
    check('as_legacy_entries' not in repository + task_switch,
          'repository snapshot legacy projection still exists')
    check('task_switch.git_status_entries' not in closeout + coderail,
          'runtime callers still consume task_switch status compatibility rows')
    modules = [
        'test_structure.py', 'test_static.py', 'test_drive.py',
        'test_inspect.py', 'test_task_switch.py', 'test_lifecycle.py',
        'test_closeout.py',
    ]
    paths = [ROOT/'tests'/name for name in modules]
    check(all(path.exists() for path in paths), 'responsibility test modules are incomplete')
    names = []
    for path in paths:
        source = path.read_text(encoding='utf-8')
        check(len(source.splitlines()) <= 650, f'{path.name} exceeds 650 lines')
        tree = ast.parse(source)
        names.extend(node.name for node in tree.body
                     if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'))
    check(len(names) == 121 and len(names) == len(set(names)),
          f'test inventory changed or contains duplicates: {len(names)}/{len(set(names))}')

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

def test_verified_commit_pending_is_non_success_and_resumes_to_finalized():
    sys.path.insert(0, str(ROOT/'scripts'))
    import closeout_transaction
    tx = closeout_transaction.CloseoutTransaction('T-999')
    for phase in ['VERIFIED', 'SNAPSHOTTED', 'CLASSIFIED']:
        tx.advance(closeout_transaction.Phase[phase])
    tx.mark_commit_pending(['lib/owned.ts', 'docs/PROGRESS.md'])
    result = tx.result()
    check(not result.success and result.failure is None, result)
    check(result.phase is closeout_transaction.Phase.COMMIT_PENDING, result)
    resumed = closeout_transaction.CloseoutTransaction.from_commit_pending(
        'T-999', result.paths
    )
    for phase in ['STAGED', 'COMMITTED', 'PERSISTED', 'RESCANNED']:
        resumed.advance(closeout_transaction.Phase[phase])
    resumed.finalize(inspect_status='healthy', residual_paths=[])
    check(resumed.success and resumed.phase is closeout_transaction.Phase.FINALIZED,
          resumed.result())

if __name__ == "__main__":
    run_module(globals())
