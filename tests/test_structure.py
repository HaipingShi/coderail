from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def test_manifests_exist():
    assert (ROOT / '.claude-plugin/plugin.json').exists()
    assert (ROOT / '.codex-plugin/plugin.json').exists()


def test_codex_manifest_points_to_skills():
    data = json.loads((ROOT / '.codex-plugin/plugin.json').read_text())
    assert data['skills'] == './skills/'
    assert (ROOT / 'skills').exists()


def test_versions_consistent():
    expected = (ROOT / 'VERSION').read_text().strip()
    assert expected, 'VERSION file is empty'
    for manifest in ['.claude-plugin/plugin.json', '.codex-plugin/plugin.json', 'package.json']:
        data = json.loads((ROOT / manifest).read_text())
        assert data['version'] == expected, f"{manifest} version {data['version']} != VERSION {expected}"


def test_all_skills_have_frontmatter_name_description():
    for skill in (ROOT / 'skills').iterdir():
        if skill.is_dir():
            text = (skill / 'SKILL.md').read_text()
            assert text.startswith('---')
            assert 'name:' in text.split('---', 2)[1]
            assert 'description:' in text.split('---', 2)[1]


def test_trace_and_link_skills_exist():
    assert (ROOT / 'skills/trace/SKILL.md').exists()
    assert (ROOT / 'skills/link/SKILL.md').exists()
    assert (ROOT / 'skills/blueprint/SKILL.md').exists()


def test_coordinate_and_trace_references_exist():
    assert (ROOT / 'references/CODERAIL_COORDINATE.md').exists()
    assert (ROOT / 'references/TRACE_GRAPH.md').exists()
    assert (ROOT / 'references/BLUEPRINT_STANDARD.md').exists()


def test_project_template_has_trace_files():
    assert (ROOT / 'project-template/docs/TRACELOG.jsonl').exists()
    assert (ROOT / 'project-template/docs/TRACE_INDEX.md').exists()


def test_tasks_template_has_coordinate_block():
    text = (ROOT / 'project-template/docs/TASKS.md').read_text(encoding='utf-8')
    assert 'CodeRail Coordinate' in text
    assert 'G — Goal' in text
    assert 'P — Persist' in text


def test_entry_files_stay_short():
    # Entry files must remain concise; full schemas live in references.
    agents = (ROOT / 'project-template/AGENTS.md').read_text(encoding='utf-8')
    assert len(agents.splitlines()) <= 130, 'AGENTS.md grew too long'
    claude = (ROOT / 'project-template/CLAUDE.md').read_text(encoding='utf-8')
    assert len(claude.splitlines()) <= 60, 'CLAUDE.md grew too long'


def test_trace_scripts_exist():
    for script in ['trace_event.py', 'trace_index.py', 'trace_doctor.py', 'coordinate_check.py', 'blueprint_check.py']:
        assert (ROOT / 'scripts' / script).exists(), f'missing scripts/{script}'


def test_runtime_terms_are_engineering_focused():
    # Runtime files should use engineering terminology rather than research-origin labels.
    disallowed = [''.join(['S','tra','TA']), ' '.join(['Strategic','Trajectory']), '-'.join(['Self','Judgment'])]
    for path in ROOT.rglob('*'):
        if path.is_file() and path.suffix in {'.md', '.json', '.py'} and 'tests' not in path.parts:
            body = path.read_text(encoding='utf-8', errors='ignore')
            for term in disallowed:
                assert term not in body, f'{term} found in {path}'
