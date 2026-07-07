"""Tests for scripts/blueprint_check.py — signal detection + relevance mapping."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import blueprint_check  # noqa: E402


def _write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_detect_ui_via_gradio(tmp_path):
    _write(tmp_path / "app.py", "import gradio as gr\ngr.Interface()\n")
    sig = blueprint_check.detect_signals(tmp_path)
    assert sig["ui"] is True


def test_detect_ui_via_fastapi(tmp_path):
    _write(tmp_path / "main.py", "from fastapi import FastAPI\napp = FastAPI()\n@app.get('/')\ndef r(): return {}")
    sig = blueprint_check.detect_signals(tmp_path)
    assert sig["ui"] is True
    assert sig["http_api"] is True


def test_no_ui_no_false_positive(tmp_path):
    # Pure CLI tool, no UI framework.
    _write(tmp_path / "cli.py", "import argparse\np = argparse.ArgumentParser()\np.parse_args()")
    _write(tmp_path / "Link to" / "x.py", "# the string 'Link to' alone should not trigger ui_multipage")
    sig = blueprint_check.detect_signals(tmp_path)
    assert sig["ui"] is False


def test_detect_db_via_sqlite(tmp_path):
    _write(tmp_path / "db.py", "import sqlite3\nconn = sqlite3.connect('x.db')")
    sig = blueprint_check.detect_signals(tmp_path)
    assert sig["db"] is True


def test_detect_db_via_orm(tmp_path):
    _write(tmp_path / "models.py", "from sqlalchemy import Column\nCREATE TABLE users (id int)")
    sig = blueprint_check.detect_signals(tmp_path)
    assert sig["db"] is True


def test_no_db_when_just_files(tmp_path):
    _write(tmp_path / "infer.py", "import torch\ndef f(): pass")
    sig = blueprint_check.detect_signals(tmp_path)
    assert sig["db"] is False


def test_detect_deploy_via_dockerfile(tmp_path):
    (tmp_path / "Dockerfile").write_text("FROM python:3.11\n", encoding="utf-8")
    sig = blueprint_check.detect_signals(tmp_path)
    assert sig["deploy"] is True


def test_detect_ci_via_github_workflows(tmp_path):
    _write(tmp_path / ".github" / "workflows" / "ci.yml", "on: [push]\njobs:\n  build:\n    runs-on: ubuntu-latest")
    sig = blueprint_check.detect_signals(tmp_path)
    assert sig["ci"] is True


def test_detect_stateful_via_status_choices(tmp_path):
    _write(tmp_path / "models.py", "STATUS_CHOICES = ['draft', 'published', 'archived']")
    sig = blueprint_check.detect_signals(tmp_path)
    assert sig["stateful"] is True


def test_not_stateful_on_transformer_transition(tmp_path):
    # 'transition' alone in ML attention code must NOT trigger a business state machine.
    _write(tmp_path / "attn.py", "# attention transition matrix\nscore = q @ k.T")
    sig = blueprint_check.detect_signals(tmp_path)
    assert sig["stateful"] is False


def test_relevant_always_includes_system_arch(tmp_path):
    sig = blueprint_check.detect_signals(tmp_path)
    rel = blueprint_check.relevant_diagrams(sig)
    ids = [d[0] for d in rel]
    assert "system_arch" in ids


def test_relevant_excludes_er_when_no_db(tmp_path):
    _write(tmp_path / "infer.py", "import torch\ndef f(): pass")
    sig = blueprint_check.detect_signals(tmp_path)
    rel = blueprint_check.relevant_diagrams(sig)
    ids = [d[0] for d in rel]
    assert "er" not in ids
    assert "state_machine" not in ids


def test_relevant_includes_er_when_db(tmp_path):
    _write(tmp_path / "models.py", "import sqlite3")
    sig = blueprint_check.detect_signals(tmp_path)
    rel = blueprint_check.relevant_diagrams(sig)
    ids = [d[0] for d in rel]
    assert "er" in ids


def test_relevant_includes_deployment_when_dockerfile(tmp_path):
    (tmp_path / "Dockerfile").write_text("FROM python:3.11", encoding="utf-8")
    sig = blueprint_check.detect_signals(tmp_path)
    rel = blueprint_check.relevant_diagrams(sig)
    ids = [d[0] for d in rel]
    assert "deployment" in ids


def test_run_check_contains_mermaid_and_pain(tmp_path):
    _write(tmp_path / "app.py", "import gradio as gr")
    report = blueprint_check.run_check(tmp_path)
    assert "解决什么痛" in report
    assert "mermaid" in report.lower() or "graph" in report.lower()
    assert "System Architecture" in report


def test_run_check_omits_unrelated(tmp_path):
    # Pure TTS-style: UI via gradio, no DB, no state machine.
    _write(tmp_path / "infer.py", "import gradio as gr\ndef infer(): pass")
    report = blueprint_check.run_check(tmp_path)
    assert "ER Diagram" not in report.split("未推荐")[0]  # not in recommended
    assert "State Machine" not in report.split("未推荐")[0]


def test_extract_diagram_entry_from_doc():
    doc = (ROOT / "references" / "BLUEPRINT_STANDARD.md").read_text(encoding="utf-8")
    entry = blueprint_check.extract_diagram_entry(doc, "system_arch")
    assert "System Architecture" in entry
    assert "解决什么痛" in entry
