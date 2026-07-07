#!/usr/bin/env python3
"""Blueprint Awareness — developer blind-spot reminder, not a compliance gate.

Scans project signals, infers which of the 11 standard technical diagrams this
kind of project typically benefits from, and surfaces the relevant ones with a
one-line explanation + minimal mermaid example. Educational, non-blocking.

The diagram encyclopedia lives in references/BLUEPRINT_STANDARD.md (single
source of truth). This script extracts per-diagram entries from it so the doc
and the tool never drift apart.

Standard library only.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT_DOC = ROOT / "references" / "BLUEPRINT_STANDARD.md"

# Diagram registry: id -> (display name, keywords to match the ### header).
DIAGRAMS = {
    "user_journey": ("User Journey Map", ["User Journey"]),
    "user_flow": ("User Flow", ["User Flow"]),
    "page_flow": ("Page Flow", ["Page Flow"]),
    "system_arch": ("System Architecture", ["System Architecture"]),
    "component": ("Component Diagram", ["Component"]),
    "sequence": ("Sequence Diagram", ["Sequence"]),
    "state_machine": ("State Machine", ["State Machine"]),
    "er": ("ER Diagram", ["ER Diagram"]),
    "data_flow": ("Data Flow Diagram", ["Data Flow"]),
    "deployment": ("Deployment Diagram", ["Deployment"]),
    "ci_cd": ("CI/CD Pipeline", ["CI/CD"]),
}

# Signal keywords.
UI_MARKERS = ["import gradio", "from gradio", "import streamlit", "from streamlit", "from flask", "import flask", "from fastapi", "import fastapi", "from react", "import react", "from vue", "import vue", "@angular/core", "import {", "from 'svelte'", "next.config", "import tkinter", "from tkinter", "from PyQt", "import PyQt", "from kivy", "WxPython", "import wx", "flutter", "package:flutter", "import UIKit", "from SwiftUI"]
DB_MARKERS = ["sqlite", "postgres", "postgresql", "mysql", "sqlalchemy", "CREATE TABLE", "import peewee", "motor", "pymongo", "mongodb", "prisma", "sequelize", "django.db", "tortoise"]
HTTP_MARKERS = ["@app.route", "@router", "APIRouter", "fastapi", "flask.Flask", "express()", "gin.", "echo.New", "requests.post", "httpx", "aiohttp", "uvicorn", "gunicorn"]
STATE_MARKERS = [
    r"status\s*[:=]\s*['\"](pending|active|draft|published|approved|rejected|processing|completed|cancelled|shipped|paid)",
    r"STATUS_CHOICES",
    r"state_machine",
    r"StateMachine",
    r"class\s+\w*(State|Status)\w*\b.*transition",
    r"allowed_transitions",
    r"status_flow",
]
UI_MULTI_PAGE_HINTS = ["react-router", "react_router", "next/navigation", "next/link", "vue-router", "vue_router", "@angular/router", "react-navigation", "<Route", "createBrowserRouter", "BrowserRouter", "StaticRouter", "pages/", "app/", "src/pages", "src/views", "src/screens"]


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except (FileNotFoundError, IsADirectoryError):
        return ""


def _iter_source_files(root: Path):
    """Yield .py/.js/.ts/.jsx/.tsx/.go/.rs/.java/.dart/.rb/.php/.vue/.svelte files.

    Excludes tests/fixtures/examples so they don't trigger false UI/DB/HTTP
    signals from fixture code (e.g. a test that imports gradio shouldn't make
    the project look like a UI app).
    """
    extensions = {".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java", ".dart", ".rb", ".php", ".vue", ".svelte", ".cs", ".kt"}
    skip = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", ".pytest_cache", "checkpoints", "assets", "docker-outputs", "tests", "test", "cli_tests", "fixtures", "examples", "demo", "demo-app", "e2e-test"}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in skip for part in path.parts):
            continue
        if path.suffix.lower() in extensions:
            yield path


def detect_signals(root: Path) -> dict:
    """Scan the project and return a signal dict."""
    ui = False
    db = False
    http_api = False
    stateful = False
    ui_multipage = False
    file_count = 0

    for path in _iter_source_files(root):
        file_count += 1
        text = _read_text(path)
        low = text.lower()
        if not ui and any(m.lower() in low for m in UI_MARKERS):
            ui = True
        if not ui_multipage and any(m.lower() in low for m in UI_MULTI_PAGE_HINTS):
            ui_multipage = True
        if not db and any(m.lower() in low for m in DB_MARKERS):
            db = True
        if not http_api and any(m.lower() in low for m in HTTP_MARKERS):
            http_api = True
        if not stateful and any(re.search(p, text, re.I) for p in STATE_MARKERS):
            stateful = True

    # Dockerfile / docker-compose
    deploy = any((root / f).exists() for f in ["Dockerfile", "docker-compose.yml", "docker-compose.yaml", "compose.yml", "k8s", "kubernetes", ".kube"])
    deploy = deploy or any(p.name.lower().startswith("dockerfile") for p in root.glob("Dockerfile*"))

    # CI
    ci = (root / ".github" / "workflows").exists() or (root / ".gitlab-ci.yml").exists() or (root / ".circleci").exists() or any((root / f).exists() for f in ["azure-pipelines.yml", "Jenkinsfile", ".travis.yml"])

    # Module count: subdirectories of the main source package.
    modules = _count_modules(root)

    return {
        "ui": ui,
        "ui_multipage": ui_multipage,
        "db": db,
        "http_api": http_api,
        "stateful": stateful,
        "deploy": deploy,
        "ci": ci,
        "modules": modules,
        "source_files": file_count,
    }


def _count_modules(root: Path) -> int:
    """Count plausible source subpackages (dirs containing .py or .js with __init__ or package.json)."""
    skip = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", ".pytest_cache", "checkpoints", "assets", "docker-outputs", "tests", "test", "docs", "examples", "scripts", "references", "skills", "e2e-test", "demo-app"}
    count = 0
    for path in root.iterdir():
        if not path.is_dir():
            continue
        if path.name in skip or path.name.startswith("."):
            continue
        has_code = any(p.suffix in {".py", ".js", ".ts"} for p in path.rglob("*") if p.is_file())
        if has_code:
            count += 1
    return count


def relevant_diagrams(signals: dict) -> list:
    """Return [(diagram_id, reason_str), ...] for diagrams this project benefits from."""
    out = []
    out.append(("system_arch", "任何多组件项目都需要一张全局分层图"))

    if signals["modules"] >= 3:
        out.append(("component", f"你有 {signals['modules']} 个子模块，模块间调用关系值得画清"))

    if signals["ui"] or signals["http_api"]:
        out.append(("sequence", "有 UI 或 HTTP 调用，跨组件交互时序值得画"))

    if signals["ui"] and signals["ui_multipage"]:
        out.append(("user_journey", "多页面 UI，用户跨页路径值得梳理"))
        out.append(("user_flow", "多页面 UI 通常有分支/鉴权，完整流程图能覆盖异常分支"))
        out.append(("page_flow", "多页面 UI 的页面跳转关系值得画清"))

    if signals["stateful"]:
        out.append(("state_machine", "检测到状态字段/转换逻辑，状态转化值得显式定义"))

    if signals["db"]:
        out.append(("er", "有数据库，表与表的关联关系值得画清"))
        if signals["http_api"]:
            out.append(("data_flow", "有 DB 且有多源调用，数据流动链路值得画"))

    if signals["deploy"]:
        out.append(("deployment", "检测到 Dockerfile/compose，线上拓扑值得画"))

    if signals["ci"]:
        out.append(("ci_cd", "检测到 CI 配置，发布流水线值得画清"))

    return out


def extract_diagram_entry(doc_text: str, diagram_id: str) -> str:
    """Extract a single diagram's encyclopedia entry (### header to next ### or #)."""
    name, keywords = DIAGRAMS[diagram_id]
    # Find the ### header matching any keyword.
    pattern = re.compile(rf"(###\s+[^\n]*(?:{'|'.join(re.escape(k) for k in keywords)})[^\n]*)", re.I)
    m = pattern.search(doc_text)
    if not m:
        return f"## {name}\n（详见 references/BLUEPRINT_STANDARD.md）"
    start = m.start()
    # End at next ### or # at column 0 that's a section header.
    rest = doc_text[start + 1:]
    end_m = re.search(r"\n#{2,3}\s", rest)
    block = doc_text[start:start + 1 + end_m.start()] if end_m else doc_text[start:]
    return block.strip()


def format_reminder(diagram_id: str, reason: str, doc_text: str) -> str:
    """Format one diagram reminder: why-relevant + the encyclopedia entry."""
    name = DIAGRAMS[diagram_id][0]
    entry = extract_diagram_entry(doc_text, diagram_id)
    lines = [f"### {name}", f"**为何相关**：{reason}", ""]
    # Re-label the entry's bold fields for inline reading.
    entry_lines = entry.split("\n")[1:]  # drop the duplicate ### header
    entry_lines = [ln for ln in entry_lines if ln.strip()]
    lines.extend(entry_lines)
    lines.append("")
    return "\n".join(lines)


def run_check(root: Path) -> str:
    """Run the full awareness check; return the formatted report string."""
    doc_text = _read_text(BLUEPRINT_DOC)
    signals = detect_signals(root)
    relevant = relevant_diagrams(signals)

    sig_desc = []
    sig_desc.append(f"{signals['modules']} 个子模块")
    sig_desc.append("有 UI" if signals["ui"] else "无 UI")
    sig_desc.append("有 DB" if signals["db"] else "无 DB")
    sig_desc.append("有 HTTP API" if signals["http_api"] else "无 HTTP API")
    sig_desc.append("有状态转化" if signals["stateful"] else "无明显状态机")
    sig_desc.append("有 Dockerfile/部署" if signals["deploy"] else "无部署配置")
    sig_desc.append("有 CI" if signals["ci"] else "无 CI")

    out = []
    out.append("> 不是合规检查。这些是你这类项目常受益的技术图——你可能没听过名字，看看哪些有用。")
    out.append(f"> 检测信号：{', '.join(sig_desc)}。")
    out.append(f"> 完整百科见 `references/BLUEPRINT_STANDARD.md`。")
    out.append("")
    if not relevant:
        out.append("（未匹配到相关图——项目可能太小或信号不足。）")
        return "\n".join(out)

    for did, reason in relevant:
        out.append(format_reminder(did, reason, doc_text))

    omitted = [DIAGRAMS[d][0] for d in DIAGRAMS if d not in {x[0] for x in relevant}]
    if omitted:
        out.append(f"---\n未推荐（信号未命中，未必需要）：{', '.join(omitted)}")
    return "\n".join(out)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Blueprint Awareness — developer blind-spot reminder")
    parser.add_argument("--target", default=".", help="Project root to scan")
    parser.add_argument("--json", action="store_true", help="Output signals + relevant diagrams as JSON")
    args = parser.parse_args(argv)

    target = Path(args.target).resolve()
    if not target.exists():
        print(f"target does not exist: {target}", file=sys.stderr)
        return 2

    if args.json:
        signals = detect_signals(target)
        relevant = relevant_diagrams(signals)
        print(json.dumps({
            "signals": signals,
            "relevant": [{"id": did, "name": DIAGRAMS[did][0], "reason": reason} for did, reason in relevant],
        }, ensure_ascii=False, indent=2))
        return 0

    print("# Blueprint Awareness\n")
    print(run_check(target))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
