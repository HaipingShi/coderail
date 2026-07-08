#!/usr/bin/env python3
"""Check CodeRail architecture blueprint coverage.

Blueprint Gate is intentionally repo-local: it detects project complexity signals,
then checks `docs/BLUEPRINTS.md` for the diagrams needed to keep that complexity
inspectable by humans and agents.
"""
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

VALID_STATUSES = {"planned", "current", "stale", "missing", "not-applicable"}
IGNORED_PARTS = {".git", "node_modules", ".venv", "__pycache__", "dist", "build", ".pytest_cache"}


@dataclass(frozen=True)
class Diagram:
    id: str
    name: str
    category: str


DIAGRAMS = [
    Diagram("UJM", "User Journey Map", "User & Interaction"),
    Diagram("UF", "User Flow", "User & Interaction"),
    Diagram("PF", "Page Flow / Wireframe Flow", "User & Interaction"),
    Diagram("SA", "System Architecture", "System & Application Architecture"),
    Diagram("CD", "Component Diagram", "System & Application Architecture"),
    Diagram("SEQ", "Sequence Diagram", "System & Application Architecture"),
    Diagram("SM", "State Machine Diagram", "System & Application Architecture"),
    Diagram("ERD", "ER Diagram / Database Model", "Data & Model"),
    Diagram("DFD", "Data Flow Diagram", "Data & Model"),
    Diagram("DD", "Deployment Diagram", "Deployment & Operations"),
    Diagram("CICD", "CI/CD Pipeline Flow", "Deployment & Operations"),
]
DIAGRAM_BY_ID = {d.id: d for d in DIAGRAMS}


def iter_files(root: Path):
    for path in root.rglob("*"):
        if any(part in IGNORED_PARTS for part in path.parts):
            continue
        if path.is_file():
            yield path


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except FileNotFoundError:
        return ""


def has_any(root: Path, patterns: list[str]) -> bool:
    for pattern in patterns:
        if list(root.glob(pattern)):
            return True
    return False


def detect_layers(root: Path) -> dict[str, list[str]]:
    files = list(iter_files(root))
    rels = [rel(p, root) for p in files]
    lower = [x.lower() for x in rels]
    package = read(root / "package.json").lower()

    frontend = []
    if any(re.search(r"(^|/)(src|app|pages|components)/.*\.(tsx|jsx|vue|svelte)$", x) for x in lower):
        frontend.append("frontend component/page files")
    if any(x.endswith("index.html") for x in lower):
        frontend.append("HTML entrypoint")
    if package and any(k in package for k in ['"next"', '"react"', '"vue"', '"svelte"', '"vite"']):
        frontend.append("frontend package dependencies")

    backend = []
    if any(re.search(r"(^|/)(api|server|routes|controllers)/", x) for x in lower):
        backend.append("API/server directories")
    if any(re.search(r"(^|/)(server|app|main)\.(py|js|ts|go|rs)$", x) for x in lower):
        backend.append("server entrypoint")
    if any(k in package for k in ['"express"', '"fastify"', '"nestjs"', '"hono"']):
        backend.append("backend package dependencies")
    if any(k in "\n".join(lower) for k in ["fastapi", "django", "flask"]):
        backend.append("backend framework signal")

    data = []
    data_patterns = [
        "prisma/schema.prisma",
        "migrations/**",
        "schema.sql",
        "db/**",
        "database/**",
        "models/**",
        "**/*.sql",
    ]
    if has_any(root, data_patterns):
        data.append("database schema/model files")
    if any(k in package for k in ['"prisma"', '"typeorm"', '"sequelize"', '"mongoose"', '"knex"']):
        data.append("data package dependencies")

    ops = []
    if has_any(root, ["Dockerfile", "docker-compose.yml", "docker-compose.yaml", "k8s/**", "helm/**", "terraform/**", "render.yaml", "vercel.json"]):
        ops.append("deployment/infrastructure files")

    ci = []
    if has_any(root, [".github/workflows/*.yml", ".github/workflows/*.yaml"]):
        ci.append("CI workflow files")

    text_blob = "\n".join(read(p).lower()[:4000] for p in files if p.suffix in {".md", ".py", ".js", ".ts", ".tsx", ".json", ".yml", ".yaml"})
    lifecycle = []
    if re.search(r"\b(status|state|workflow|approval|order|payment|refund|shipment|ticket)\b", text_blob):
        lifecycle.append("stateful workflow language")

    dataflow = []
    if re.search(r"\b(import|export|etl|analytics|report|sync|webhook|queue|stream)\b", text_blob):
        dataflow.append("data movement language")

    return {
        "frontend": frontend,
        "backend": backend,
        "data": data,
        "ops": ops,
        "ci": ci,
        "lifecycle": lifecycle,
        "dataflow": dataflow,
    }


def required_diagrams(layers: dict[str, list[str]]) -> tuple[set[str], set[str]]:
    required: set[str] = set()
    recommended: set[str] = set()
    core_layers = [k for k in ["frontend", "backend", "data", "ops"] if layers[k]]

    if len(core_layers) >= 2:
        required.add("SA")
    if layers["frontend"]:
        recommended.update({"UJM", "UF", "PF"})
    if layers["backend"]:
        required.add("CD")
    if layers["frontend"] and layers["backend"]:
        required.add("SEQ")
    if layers["lifecycle"]:
        recommended.add("SM")
    if layers["data"]:
        required.add("ERD")
        recommended.add("DFD")
    if layers["dataflow"] and (layers["backend"] or layers["data"]):
        recommended.add("DFD")
    if layers["ops"]:
        required.add("DD")
    if layers["ci"]:
        required.add("CICD")

    return required, recommended - required


def parse_blueprints(text: str) -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not (line.startswith("|") and line.endswith("|")):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not cells or cells[0].lower() in {"id", "---"} or set(cells[0]) <= {"-"}:
            continue
        diagram_id = cells[0].upper()
        if diagram_id not in DIAGRAM_BY_ID:
            continue
        rows[diagram_id] = {
            "name": cells[1] if len(cells) > 1 else "",
            "status": (cells[2] if len(cells) > 2 else "").lower(),
            "path": cells[3] if len(cells) > 3 else "",
            "owner": cells[4] if len(cells) > 4 else "",
            "updated": cells[5] if len(cells) > 5 else "",
            "notes": cells[6] if len(cells) > 6 else "",
        }
    return rows


def path_exists(root: Path, value: str) -> bool:
    value = value.strip()
    if not value or value.lower() in {"n/a", "none", "not-applicable", "-"}:
        return True
    if re.match(r"https?://", value):
        return True
    first = value.split(",", 1)[0].strip().strip("`")
    return (root / first).exists()


def check_project(root: Path) -> dict:
    layers = detect_layers(root)
    required, recommended = required_diagrams(layers)
    core_layer_count = sum(1 for key in ["frontend", "backend", "data", "ops"] if layers[key])
    high_complexity = core_layer_count >= 3
    path = root / "docs" / "BLUEPRINTS.md"
    severe: list[str] = []
    warnings: list[str] = []
    info: list[str] = []

    if not path.exists():
        if required and high_complexity:
            severe.append("docs/BLUEPRINTS.md missing for high-complexity project")
        elif required or recommended:
            warnings.append("docs/BLUEPRINTS.md missing; add blueprint index for architecture/lifecycle coverage")
        else:
            info.append("no blueprint index needed yet; project complexity signals are low")
        return {
            "status": "unhealthy" if severe else ("usable with warnings" if warnings else "healthy"),
            "layers": layers,
            "required": sorted(required),
            "recommended": sorted(recommended),
            "severe": severe,
            "warnings": warnings,
            "info": info,
        }

    rows = parse_blueprints(read(path))
    if not rows:
        warnings.append("docs/BLUEPRINTS.md has no recognized diagram table rows")

    for diagram_id, row in rows.items():
        status = row["status"]
        if status not in VALID_STATUSES:
            severe.append(f"{diagram_id}: invalid lifecycle status {status!r}")
        if status == "current" and not row["path"]:
            warnings.append(f"{diagram_id}: current diagram should include a path or URL")
        if status == "current" and row["path"] and not path_exists(root, row["path"]):
            warnings.append(f"{diagram_id}: diagram path does not exist: {row['path']}")
        if status in {"current", "stale"} and not row["updated"]:
            warnings.append(f"{diagram_id}: lifecycle status should include an Updated value")

    for diagram_id in sorted(required):
        row = rows.get(diagram_id)
        name = DIAGRAM_BY_ID[diagram_id].name
        if row is None:
            msg = f"{diagram_id} ({name}) missing from docs/BLUEPRINTS.md"
            if diagram_id == "SA" and high_complexity:
                severe.append(msg)
            else:
                warnings.append(msg)
            continue
        status = row["status"]
        if status == "missing":
            severe.append(f"{diagram_id} ({name}) is required but marked missing")
        elif status == "stale":
            warnings.append(f"{diagram_id} ({name}) is required but stale")
        elif status == "planned":
            warnings.append(f"{diagram_id} ({name}) is required but only planned")
        elif status == "not-applicable":
            warnings.append(f"{diagram_id} ({name}) is required by detected project signals but marked not-applicable")

    for diagram_id in sorted(recommended):
        row = rows.get(diagram_id)
        if row is None:
            info.append(f"{diagram_id} ({DIAGRAM_BY_ID[diagram_id].name}) recommended by project signals")
        elif row["status"] in {"missing", "planned", "stale"}:
            info.append(f"{diagram_id} ({DIAGRAM_BY_ID[diagram_id].name}) recommended; current status is {row['status']}")

    status = "unhealthy" if severe else ("usable with warnings" if warnings else "healthy")
    return {
        "status": status,
        "layers": layers,
        "required": sorted(required),
        "recommended": sorted(recommended),
        "severe": severe,
        "warnings": warnings,
        "info": info,
    }


def render_report(result: dict) -> str:
    lines = ["# Blueprint Gate Report", "", f"Status: {result['status']}", ""]
    lines.append("## Detected Layers")
    for layer in ["frontend", "backend", "data", "ops", "ci", "lifecycle", "dataflow"]:
        signals = result["layers"].get(layer) or []
        lines.append(f"- {layer}: {', '.join(signals) if signals else 'none'}")
    lines.append("")
    lines.append("## Required Diagrams")
    lines.append("- none" if not result["required"] else "\n".join(f"- {x}: {DIAGRAM_BY_ID[x].name}" for x in result["required"]))
    lines.append("")
    lines.append("## Recommended Diagrams")
    lines.append("- none" if not result["recommended"] else "\n".join(f"- {x}: {DIAGRAM_BY_ID[x].name}" for x in result["recommended"]))
    lines.append("")
    lines.append("## Severe")
    lines.append("- none" if not result["severe"] else "\n".join(f"- {x}" for x in result["severe"]))
    lines.append("")
    lines.append("## Warnings")
    lines.append("- none" if not result["warnings"] else "\n".join(f"- {x}" for x in result["warnings"]))
    lines.append("")
    lines.append("## Info")
    lines.append("- none" if not result["info"] else "\n".join(f"- {x}" for x in result["info"]))
    return "\n".join(lines)


def run_check(root: Path) -> str:
    return render_report(check_project(root))


def main(argv=None):
    p = argparse.ArgumentParser(description="Check CodeRail blueprint coverage")
    p.add_argument("--target", default=".")
    a = p.parse_args(argv)
    result = check_project(Path(a.target).resolve())
    print(render_report(result))
    return 1 if result["status"] == "unhealthy" else 0


if __name__ == "__main__":
    raise SystemExit(main())
