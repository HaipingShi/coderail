"""Tests for scripts/trace_event.py and scripts/trace_index.py."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'scripts'
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import trace_event  # noqa: E402
import trace_index  # noqa: E402


def _ns(**kwargs):
    """Build a minimal argparse.Namespace for trace_event.build_event."""
    defaults = dict(
        id=None, ts=None, type='change', summary='test', task=None, north_star=None,
        status=None, source_kind=None, source_ref=None, files=None,
        serves=None, derived_from=None, implements=None, modifies=None,
        validated_by=None, depends_on=None, supersedes=None, blocks=None,
        relates_to=None, harness_command=None, harness_result=None, commit=None,
        goal=None, coordinate_task=None, scope_allowed=None, scope_forbidden=None,
        verify=None, stop=None, persist=None,
    )
    defaults.update(kwargs)
    return argparse_namespace(defaults)


def argparse_namespace(d):
    import argparse
    return argparse.Namespace(**d)


def test_build_event_creates_valid_change(tmp_path):
    ns = _ns(type='change', summary='Update task template',
             task='T-001', north_star='NS-001', files='docs/TASKS.md',
             modifies='docs/TASKS.md', implements='T-001')
    event = trace_event.build_event(ns)
    assert event['type'] == 'change'
    assert event['task'] == 'T-001'
    assert event['files'] == ['docs/TASKS.md']
    assert event['id'].startswith('TR-')
    assert event['ts']


def test_change_without_task_northstar_files_rejected():
    ns = _ns(type='change', summary='orphan change')
    with pytest.raises(ValueError, match='change event must have'):
        trace_event.build_event(ns)


def test_verify_without_harness_result_rejected():
    ns = _ns(type='verify', summary='ran tests', task='T-001')
    with pytest.raises(ValueError, match='verify event must have'):
        trace_event.build_event(ns)


def test_invalid_type_rejected():
    ns = _ns(type='bogus', summary='bad type')
    with pytest.raises(ValueError, match='invalid --type'):
        trace_event.build_event(ns)


def test_coordinate_attached(tmp_path):
    ns = _ns(type='task', summary='Create task', task='T-001', north_star='NS-001',
             goal='Initialize project', coordinate_task='Create docs',
             scope_allowed='docs/**', scope_forbidden='src/**',
             verify='manual check', stop='business impl', persist='TASKS,TRACE')
    event = trace_event.build_event(ns)
    assert event['coordinate']['goal'] == 'Initialize project'
    assert event['coordinate']['scope']['allowed'] == ['docs/**']
    assert event['coordinate']['scope']['forbidden'] == ['src/**']
    assert event['coordinate']['persist'] == ['TASKS', 'TRACE']


def test_append_event_writes_jsonl(tmp_path):
    ns = _ns(type='change', summary='hi', task='T-001', files='a.py')
    event = trace_event.build_event(ns)
    log = trace_event.append_event(tmp_path, event)
    assert log.exists()
    lines = log.read_text(encoding='utf-8').strip().splitlines()
    assert len(lines) == 1
    parsed = json.loads(lines[0])
    assert parsed['type'] == 'change'
    assert parsed['task'] == 'T-001'


def test_trace_index_empty_log(tmp_path):
    docs = tmp_path / 'docs'
    docs.mkdir()
    (docs / 'TRACELOG.jsonl').write_text('', encoding='utf-8')
    events = trace_index.load_events(docs / 'TRACELOG.jsonl')
    text = trace_index.render(events)
    assert 'Event count: 0' in text
    assert 'By Task' in text
    assert '(empty)' in text


def test_trace_index_groups_by_task_and_file(tmp_path):
    docs = tmp_path / 'docs'
    docs.mkdir()
    log = docs / 'TRACELOG.jsonl'
    events = [
        {'id': 'TR-1', 'ts': '2026-07-06T10:00:00+00:00', 'type': 'task',
         'summary': 't1', 'task': 'T-001', 'north_star': 'NS-001'},
        {'id': 'TR-2', 'ts': '2026-07-06T11:00:00+00:00', 'type': 'change',
         'summary': 'c1', 'task': 'T-001', 'files': ['src/a.py'], 'modifies': ['src/a.py']},
        {'id': 'TR-3', 'ts': '2026-07-06T12:00:00+00:00', 'type': 'change',
         'summary': 'c2', 'task': 'T-002', 'files': ['src/b.py'], 'modifies': ['src/b.py']},
    ]
    with log.open('w', encoding='utf-8') as fh:
        for e in events:
            fh.write(json.dumps(e) + '\n')
    loaded = trace_index.load_events(log)
    text = trace_index.render(loaded)
    assert '### T-001' in text
    assert '### T-002' in text
    assert '`src/a.py`' in text
    assert '`src/b.py`' in text
    assert 'NS-001' in text
