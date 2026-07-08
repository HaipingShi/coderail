#!/usr/bin/env python3
"""Check Coordinate Contract Drafts in docs/CONTRACTS.md.

Standard library only. A draft is valid when its Coordinate Contract Draft has
G/T/S/V/X/P and accepted drafts have a concrete decision. This check is a
pre-implementation gate, not a project-management system.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DRAFT_HEADER = re.compile(r"^##\s+(CD-\d+[^\n]*)", re.M)


def split_drafts(text: str):
    matches = list(DRAFT_HEADER.finditer(text))
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end]
        yield m.group(1).strip(), body, _extract_status(body)


def _extract_status(body: str) -> str:
    m = re.search(r"Status:\s*([^\n]+)", body)
    return (m.group(1).strip().lower() if m else "unknown")


def parse_draft_coordinate(body: str) -> dict | None:
    m = re.search(r"###\s+Coordinate Contract Draft(.*?)(?=^###\s|^##\s|\Z)", body, re.S | re.M)
    if not m:
        return None
    block = m.group(1)
    coord = {"g": "", "t": "", "s_allowed": "", "s_forbidden": "", "v": "", "x": "", "p": "", "decision": ""}
    field = None
    label = re.compile(r"^([GTSVXP])\s*[—\-:]\s*(Goal|Task|Scope|Verify|Stop|Persist):?\s*$")
    sub = re.compile(r"^[-*\s]*(Allowed|Forbidden|Harness|Manual acceptance):\s*$", re.I)
    for raw in block.splitlines():
        stripped = raw.strip()
        if not stripped:
            continue
        lm = label.match(stripped)
        if lm:
            letter = lm.group(1)
            field = {"G": "g", "T": "t", "V": "v", "X": "x", "P": "p"}.get(letter, "s_pending")
            continue
        if stripped.lower().startswith("decision:"):
            field = "decision"
            rest = stripped.split(":", 1)[1].strip()
            if rest:
                coord["decision"] = rest
            continue
        sm = sub.match(stripped)
        if sm:
            name = sm.group(1).lower()
            if name == "allowed":
                field = "s_allowed"
            elif name == "forbidden":
                field = "s_forbidden"
            elif name in {"harness", "manual acceptance"}:
                field = "v"
            continue
        if stripped.startswith("#"):
            field = None
            continue
        if field is None:
            continue
        if field == "s_pending":
            field = "s_allowed"
        value = stripped.lstrip("-* \t").rstrip()
        if not value:
            continue
        coord[field] = (coord[field] + "\n" + value).strip() if coord[field] else value
    return coord


def check_draft(header: str, body: str, status: str):
    severe, warnings = [], []
    coord = parse_draft_coordinate(body)
    did = header.split()[0]
    if coord is None:
        severe.append(f"{did}: missing Coordinate Contract Draft")
        return severe, warnings
    for key, label in [("g", "G"), ("t", "T"), ("s_allowed", "S allowed"), ("v", "V"), ("p", "P")]:
        if not coord.get(key):
            severe.append(f"{did}: {label} missing")
    if not coord.get("s_forbidden"):
        warnings.append(f"{did}: S forbidden empty (write 'none' if there is no forbidden scope)")
    if not coord.get("x"):
        warnings.append(f"{did}: X stop conditions empty")
    if status == "accepted" and not re.search(r"Decision:\s*(proceed|revise|ask user|split task|backlog)", body, re.I):
        warnings.append(f"{did}: accepted draft should record a Decision")
    return severe, warnings


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Check CodeRail coordinate contract drafts")
    ap.add_argument("--target", default=".")
    args = ap.parse_args(argv)
    root = Path(args.target).resolve()
    path = root / "docs" / "CONTRACTS.md"
    if not path.exists():
        print("# Contract Check Report\n")
        print("Status: usable with warnings")
        print("\n## Warnings\n- docs/CONTRACTS.md missing (only needed for draft-gated work)")
        return 0
    drafts = list(split_drafts(path.read_text(encoding="utf-8", errors="ignore")))
    severe, warnings = [], []
    for h, b, s in drafts:
        sev, warn = check_draft(h, b, s)
        severe.extend(sev)
        warnings.extend(warn)
    print("# Contract Check Report\n")
    status = "healthy" if not severe and not warnings else ("unhealthy" if severe else "usable with warnings")
    print(f"Status: {status}")
    print(f"Drafts checked: {len(drafts)}\n")
    print("## Severe")
    print("- none" if not severe else "\n".join(f"- {x}" for x in severe))
    print("\n## Warnings")
    print("- none" if not warnings else "\n".join(f"- {x}" for x in warnings))
    return 1 if severe else 0


if __name__ == "__main__":
    raise SystemExit(main())
