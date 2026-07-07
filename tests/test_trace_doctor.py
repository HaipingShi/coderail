"""Tests for scripts/trace_doctor.py."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'scripts'
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import trace_doctor  # noqa: E402


def _write_log(tmp_path, events):
    docs = tmp_path / 'docs'
    docs.mkdir(exist_ok=True)
    log = docs / 'TRACELOG.jsonl'
    with log.open('w', encoding='utf-8') as fh:
        for e in events:
            fh.write(json.dumps(e) + '\n')
    return docs / 'TRACE_INDEX.md', log


def test_change_without_task_or_north_star_is_severe(tmp_path):
    index_path, log_path = _write_log(tmp_path, [
        {'id': 'TR-1', 'ts': '2026-07-06T10:00:00+00:00', 'type': 'change',
         'summary': 'orphan change'},
    ])
    severe, warnings = trace_doctor.check([], index_path, log_path)
    severe, warnings = trace_doctor.check(
        trace_doctor.load_events(log_path), index_path, log_path)
    assert any('TR-1' in s and 'no task or north_star' in s for s in severe)


def test_verify_without_harness_result_is_severe(tmp_path):
    index_path, log_path = _write_log(tmp_path, [
        {'id': 'TR-2', 'ts': '2026-07-06T10:00:00+00:00', 'type': 'verify',
         'summary': 'ran tests', 'task': 'T-001'},
    ])
    severe, warnings = trace_doctor.check(
        trace_doctor.load_events(log_path), index_path, log_path)
    assert any('TR-2' in s and 'harness_result' in s for s in severe)


def test_healthy_events_no_severe(tmp_path):
    index_path, log_path = _write_log(tmp_path, [
        {'id': 'TR-1', 'ts': '2026-07-06T10:00:00+00:00', 'type': 'change',
         'summary': 'c1', 'task': 'T-001', 'north_star': 'NS-001',
         'modifies': ['src/a.py'], 'files': ['src/a.py'],
         'coordinate': {'goal': 'g', 'task': 't', 'verify': ['pytest'], 'persist': ['TASKS']}},
        {'id': 'TR-2', 'ts': '2026-07-06T11:00:00+00:00', 'type': 'verify',
         'summary': 'passed', 'task': 'T-001', 'harness_result': 'passed',
         'coordinate': {'goal': 'g', 'task': 't'}},
    ])
    severe, warnings = trace_doctor.check(
        trace_doctor.load_events(log_path), index_path, log_path)
    assert severe == []


def test_empty_log_is_warning_not_severe(tmp_path):
    docs = tmp_path / 'docs'
    docs.mkdir(exist_ok=True)
    log = docs / 'TRACELOG.jsonl'
    log.write_text('', encoding='utf-8')
    index_path = docs / 'TRACE_INDEX.md'
    severe, warnings = trace_doctor.check(
        trace_doctor.load_events(log), index_path, log)
    assert severe == []
    assert any('empty' in w.lower() for w in warnings)
