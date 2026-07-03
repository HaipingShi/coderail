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


def test_all_skills_have_frontmatter_name_description():
    for skill in (ROOT / 'skills').iterdir():
        if skill.is_dir():
            text = (skill / 'SKILL.md').read_text()
            assert text.startswith('---')
            assert 'name:' in text.split('---', 2)[1]
            assert 'description:' in text.split('---', 2)[1]


def test_runtime_terms_are_engineering_focused():
    # Runtime files should use engineering terminology rather than research-origin labels.
    disallowed = [''.join(['S','tra','TA']), ' '.join(['Strategic','Trajectory']), '-'.join(['Self','Judgment'])]
    for path in ROOT.rglob('*'):
        if path.is_file() and path.suffix in {'.md', '.json', '.py'} and 'tests' not in path.parts:
            body = path.read_text(encoding='utf-8', errors='ignore')
            for term in disallowed:
                assert term not in body, f'{term} found in {path}'
