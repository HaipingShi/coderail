"""Tests for scripts/init_project.py — verify the generated project ships trace files
and a CodeRail Coordinate in TASKS.md."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'scripts'
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import init_project  # noqa: E402


def test_standard_init_ships_trace_files(tmp_path):
    for rel in init_project.STANDARD_FILES:
        init_project.copy_file(rel, tmp_path, force=False)
    assert (tmp_path / 'docs/TRACELOG.jsonl').exists()
    assert (tmp_path / 'docs/TRACE_INDEX.md').exists()
    assert (tmp_path / 'docs/NORTH_STAR.md').exists()
    assert (tmp_path / 'docs/TASKS.md').exists()


def test_init_tasks_has_coordinate(tmp_path):
    for rel in init_project.STANDARD_FILES:
        init_project.copy_file(rel, tmp_path, force=False)
    tasks = (tmp_path / 'docs/TASKS.md').read_text(encoding='utf-8')
    assert 'CodeRail Coordinate' in tasks
    assert 'G — Goal' in tasks
    assert 'T — Task' in tasks
    assert 'V — Verify' in tasks
    assert 'X — Stop' in tasks
    assert 'P — Persist' in tasks


def test_init_handoff_has_coordinate_summary(tmp_path):
    for rel in init_project.STANDARD_FILES:
        init_project.copy_file(rel, tmp_path, force=False)
    handoff = (tmp_path / 'docs/HANDOFF.md').read_text(encoding='utf-8')
    assert 'Coordinate Summary' in handoff


def test_init_does_not_overwrite_nonempty(tmp_path):
    # Pre-create a non-empty NORTH_STAR.md; init should skip it.
    (tmp_path / 'docs').mkdir(parents=True, exist_ok=True)
    (tmp_path / 'docs/NORTH_STAR.md').write_text('# My custom North Star\n', encoding='utf-8')
    msg = init_project.copy_file('docs/NORTH_STAR.md', tmp_path, force=False)
    assert msg.startswith('skipped')
    content = (tmp_path / 'docs/NORTH_STAR.md').read_text(encoding='utf-8')
    assert 'My custom North Star' in content
