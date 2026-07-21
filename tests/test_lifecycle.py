from test_support import *
from test_support import _assert_done_inspect_consistent, _lifecycle_env

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

def test_start_rejects_scope_contradiction_without_partial_state():
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        tasks_path = root/'docs/TASKS.md'
        meta_path = root/'.coderail/tasks.json'
        trace_path = root/'docs/TRACELOG.jsonl'
        before = {
            'tasks': tasks_path.read_bytes(),
            'meta': meta_path.read_bytes() if meta_path.exists() else None,
            'trace': trace_path.read_bytes(),
        }
        allowed = 'lib/memory/__tests__/memory-write-effect-gate.test.ts'
        forbidden = 'lib/memory/**'
        result = cr('start', 'Contradictory scope', '--files', allowed,
                    '--avoid', forbidden, '--verify', 'true')
        check(result.returncode == 1, result.stdout)
        for expected in ['SCOPE_CONTRADICTION', allowed, forbidden]:
            check(expected in result.stdout, result.stdout)
        check('narrow the forbidden' in result.stdout.lower(), result.stdout)
        check(tasks_path.read_bytes() == before['tasks'],
              'contradictory start partially wrote TASKS')
        meta_after = meta_path.read_bytes() if meta_path.exists() else None
        check(meta_after == before['meta'],
              'contradictory start partially wrote task metadata')
        check(trace_path.read_bytes() == before['trace'],
              'contradictory start partially wrote TRACE')
        check('Status: [~]' not in tasks_path.read_text(encoding='utf-8'),
              'contradictory task became active')

def test_exact_production_forbidden_rule_allows_declared_test_scope():
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        allowed = 'lib/memory/__tests__/memory-write-effect-gate.test.ts'
        forbidden = 'lib/memory/memory-store.ts'
        result = cr('start', 'Narrow memory test', '--files', allowed,
                    '--avoid', forbidden, '--verify', 'true')
        check(result.returncode == 0, result.stdout)
        target = root/allowed
        target.parent.mkdir(parents=True)
        target.write_text('test\n', encoding='utf-8')
        result = cr('done')
        check(result.returncode == 0, result.stdout)
        check('== Done:' in result.stdout, result.stdout)
        tracked = subprocess.check_output(
            ['git', '-C', td, 'ls-files', allowed], text=True).strip()
        check(tracked == allowed, tracked)

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
- Run the queued check `false` before closeout.

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
    # once - PROGRESS entry, TRACE fact, hot TASKS compacted, commit made - and
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
            check('# Done Gate Report\n\nStatus: pass' in body,
                  f'(FN-027b) Done Gate did not pass inside closeout: {body}')
            tasks = (root/'docs/TASKS.md').read_text(encoding='utf-8')
            check('Status: [x]' not in tasks and title not in tasks,
                  f'(3/4) completed history leaked into hot TASKS: {tasks}')
            trace = (root/'docs/TRACELOG.jsonl').read_text(encoding='utf-8')
            check(trace.count('"type": "verify"') == n,
                  f'(3/4) TRACE verify count != {n}: {trace}')
            log = subprocess.run(['git', 'log', '--oneline'], cwd=td,
                                 capture_output=True, text=True).stdout
            check(f'chore({biz}/' in log, f'(4/4) commit missing for {biz}: {log}')
            check(not (root/'.coderail/pending_close.json').exists(),
                  'snapshot must be cleared after a fully-ledgered close')
            inspect = cr('inspect', '--no-write')
            check(inspect.returncode == 0 and 'Status: healthy' in inspect.stdout,
                  f'final inspect disagrees with successful done: {inspect.stdout}')
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
        tasks = (root/'docs/TASKS.md').read_text(encoding='utf-8')
        check('Snapshot recovery task' in tasks and 'Status: [x]' in tasks,
              'failed ledger must retain the closed task body for repair')
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

def test_single_snapshot_commit_eliminates_post_source_ledger_failure_window():
    with tempfile.TemporaryDirectory() as td:
        root, cr = _lifecycle_env(td)
        r = cr('start', 'Rejected ledger commit', '--verify', 'true')
        check(r.returncode == 0, r.stdout)
        hook = root/'.git/hooks/post-commit'
        hook.write_text(
            '#!/bin/sh\n'
            'printf "#!/bin/sh\\nexit 1\\n" > .git/hooks/pre-commit\n'
            'chmod +x .git/hooks/pre-commit\n',
            encoding='utf-8',
        )
        hook.chmod(0o755)
        subprocess.check_call(
            ['git', '-C', td, 'config', 'core.hooksPath', str(root/'.git/hooks')]
        )
        r = cr('done')
        check(r.returncode == 0 and '== Done:' in r.stdout, r.stdout)
        tasks = (root/'docs/TASKS.md').read_text(encoding='utf-8')
        check('Rejected ledger commit' not in tasks and 'Status: [x]' not in tasks,
              'single snapshot commit must persist and compact the completed body')
        check(not (root/'.coderail/pending_close.json').exists(),
              'successful single commit must consume the closeout snapshot')
        check((root/'.git/hooks/pre-commit').exists(),
              'post-commit fixture did not install the second-commit rejection hook')
        progress = (root/'docs/PROGRESS.md').read_text(encoding='utf-8')
        trace = (root/'docs/TRACELOG.jsonl').read_text(encoding='utf-8')
        check('Rejected ledger commit' in progress and '"type": "verify"' in trace,
              'source and ledger facts were not persisted atomically')

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

if __name__ == "__main__":
    run_module(globals())
