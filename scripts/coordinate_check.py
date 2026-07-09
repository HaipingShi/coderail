#!/usr/bin/env python3
"""Check CodeRail Coordinate coverage in docs/TASKS.md."""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path

TASK_HEADER = re.compile(r"^##\s+([A-Z]-\d+[^\n]*)", re.M)
DONE_MARKERS = {"[x]"}
STATUS_RE = re.compile(r"Status:\s*(\[[ x~!fr]\])")
FIELD_RE = re.compile(r"^([GTSVXP])\s*[—\-:]\s*(Goal|Task|Scope|Verify|Stop|Persist):?\s*$", re.I)
SUB_RE = re.compile(r"^[-*\s]*(Allowed|Forbidden|Harness|Manual acceptance):\s*$", re.I)
LIGHT_TYPES = {"docs", "documentation", "design", "research", "adr", "note", "notes", "positioning", "principle", "terminology"}
FULL_TYPES = {"feature", "bug", "fix", "refactor", "harness", "runner", "pipeline", "schema", "data", "api", "migration", "release"}

def split_tasks(text: str):
    matches = list(TASK_HEADER.finditer(text))
    for i, m in enumerate(matches):
        start = m.end(); end = matches[i+1].start() if i+1 < len(matches) else len(text)
        body = text[start:end]
        status = _extract_status(body)
        yield m.group(1).strip(), body, status

def _extract_status(body: str) -> str:
    m = STATUS_RE.search(body)
    return m.group(1) if m else "unknown"

def meta_value(label: str, body: str) -> str:
    m = re.search(rf"^{re.escape(label)}:\s*([^\n]+)", body, re.I | re.M)
    return m.group(1).strip().lower() if m else ""

def task_type(body: str, override: str | None = None) -> str:
    return (override or meta_value("Type", body)).strip().lower()

def explicit_rail(body: str, override: str | None = None) -> str:
    value = (override or meta_value("Rail", body)).strip().lower()
    return value if value in {"full", "light"} else ""

def rail_type(header: str, body: str, rail_override: str | None = None, task_type_override: str | None = None) -> str:
    explicit = explicit_rail(body, rail_override)
    if explicit in {"full", "light"}:
        return explicit
    t = task_type(body, task_type_override)
    if t in LIGHT_TYPES:
        return "light"
    if t in FULL_TYPES:
        return "full"
    blob = f"{header}\n{body}".lower()
    if any(k in blob for k in ["schema", "migration", "runner", "pipeline", "api", "data write", "dependency", "release"]):
        return "full"
    if any(k in blob for k in ["adr", "design note", "principle", "terminology", "positioning", "philosoph"]):
        return "light"
    return "full"

def parse_coordinate(body: str) -> dict | None:
    m = re.search(r"###\s+CodeRail Coordinate(.*?)(?=^###\s|^##\s|\Z)", body, re.S|re.M)
    if not m:
        return None
    block = m.group(1)
    coord = {"g":"", "t":"", "s_allowed":"", "s_forbidden":"", "v":"", "x":"", "p":""}
    field = None
    for raw in block.splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith(">"):
            continue
        fm = FIELD_RE.match(stripped)
        if fm:
            field = {"G":"g","T":"t","S":"s_pending","V":"v","X":"x","P":"p"}[fm.group(1).upper()]
            continue
        sm = SUB_RE.match(stripped)
        if sm:
            label = sm.group(1).lower()
            if label == "allowed": field = "s_allowed"
            elif label == "forbidden": field = "s_forbidden"
            else: field = "v"
            continue
        if stripped.startswith("#"):
            field = None; continue
        if not field:
            continue
        value = stripped.lstrip("-* \t").rstrip()
        if not value:
            continue
        if field == "s_pending": field = "s_allowed"
        coord[field] = (coord[field] + "\n" + value).strip() if coord[field] else value
    return coord

def check_task(header: str, body: str, status: str):
    severe, warnings = [], []
    tid = header.split()[0]
    rail_meta = meta_value("Rail", body)
    explicit = explicit_rail(body)
    rail = rail_type(header, body)
    coord = parse_coordinate(body)
    if coord is None:
        if status in {"[ ]", "[~]", "[!]", "[x]"}:
            severe.append(f"{tid}: no CodeRail Coordinate block")
        return severe, warnings
    if not explicit and status in {"[ ]", "[~]", "[!]"}:
        severe.append(f"{tid}: Rail missing; write 'Rail: full' or 'Rail: light' explicitly")
    elif rail_meta and not explicit:
        severe.append(f"{tid}: Rail must be full or light")
    for key, label in [("g","G (Goal)"),("t","T (Task)"),("s_allowed","S allowed"),("v","V (Verify)"),("p","P (Persist)")]:
        if not coord.get(key): severe.append(f"{tid}: {label} missing")
    if not coord.get("s_forbidden"):
        warnings.append(f"{tid}: S forbidden empty (write 'none' if truly nothing is forbidden)")
    if not coord.get("x"):
        warnings.append(f"{tid}: X (Stop) empty")
    if status in DONE_MARKERS:
        v = coord.get("v", "").lower()
        if not v:
            severe.append(f"{tid}: done task missing V evidence")
        elif rail == "full" and not any(word in v for word in ["harness", "manual", "pytest", "test", "lint", "typecheck", "build", "passed"]):
            warnings.append(f"{tid}: done task V has no clear harness/manual acceptance evidence")
        elif rail == "light" and not any(word in v for word in ["manual", "accept", "review", "trace", "decision", "adr", "docs", "design"]):
            warnings.append(f"{tid}: done light-rail task should record review, trace, decision, or manual acceptance evidence")
        p = coord.get("p", "").upper()
        if "TASKS" not in p: severe.append(f"{tid}: done task P missing TASKS")
        if "TRACE" not in p and rail == "full": severe.append(f"{tid}: done task P missing TRACE")
        if "TRACE" not in p and rail == "light": warnings.append(f"{tid}: done light-rail task P missing TRACE; manual acceptance or decision backlink must be explicit")
    return severe, warnings

def main(argv=None) -> int:
    ap=argparse.ArgumentParser(description="Check CodeRail Coordinate coverage in TASKS.md")
    ap.add_argument("--target", default=".")
    args=ap.parse_args(argv)
    tasks_path=Path(args.target).resolve()/"docs"/"TASKS.md"
    if not tasks_path.exists():
        print(f"error: {tasks_path} not found", file=sys.stderr); return 2
    text=tasks_path.read_text(encoding="utf-8", errors="ignore")
    severe=[]; warnings=[]; checked=0
    for header, body, status in split_tasks(text):
        s,w=check_task(header, body, status); severe.extend(s); warnings.extend(w); checked+=1
    print("# Coordinate Check Report\n")
    status="healthy" if not severe and not warnings else ("unhealthy" if severe else "usable with warnings")
    print(f"Status: {status}")
    print(f"Tasks checked: {checked}\n")
    print("## Severe")
    print("- none" if not severe else "\n".join(f"- {x}" for x in severe))
    print("\n## Warnings")
    print("- none" if not warnings else "\n".join(f"- {x}" for x in warnings))
    return 1 if severe else 0
if __name__ == "__main__":
    raise SystemExit(main())
