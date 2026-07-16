from test_support import *
from test_support import _assert_done_inspect_consistent, _lifecycle_env

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
    check(len(names) == 108 and len(names) == len(set(names)),
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

if __name__ == "__main__":
    run_module(globals())
