#!/usr/bin/env python3
"""Normalized closeout facts shared by owner and agent projections.

This module does not decide lifecycle state.  It receives the already verified
Delivery Contract and closeout receipt, then persists product delivery facts in
an append-only ledger.  TASKS, the live marker, and TRACE remain authoritative
for lifecycle and authorization.
"""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import TypedDict


SCHEMA = "coderail.closeout-facts/v1"
LEDGER_PATH = "docs/DELIVERIES.jsonl"


class CloseoutFacts(TypedDict):
    """Serializable value projected to owner, agent, and durable surfaces."""

    schema: str
    delivery_id: str
    recorded_at: str
    owner_locale: str
    product: dict
    agent_receipt: dict


def _strings(values) -> list[str]:
    if not isinstance(values, list):
        return []
    return [value.strip() for value in values if isinstance(value, str) and value.strip()]


def build(
    *,
    task_id: str,
    stamp: str,
    owner_locale: str,
    delivery: dict,
    verify_results: list[dict] | None = None,
    technical_report: str = "",
) -> CloseoutFacts:
    """Build facts without inferring claims from roadmap or lifecycle prose."""
    recommended = delivery.get("recommended_next") or {}
    verification = []
    for row in verify_results or []:
        if not isinstance(row, dict):
            continue
        verification.append({
            "cmd": str(row.get("cmd") or "(unknown)"),
            "exit": row.get("exit"),
        })
    delivery_id = f"delivery-{stamp}-{task_id}" if stamp else f"delivery-{task_id}"
    return {
        "schema": SCHEMA,
        "delivery_id": delivery_id,
        "recorded_at": stamp,
        "owner_locale": owner_locale,
        "product": {
            "milestone_status": str(delivery.get("milestone_status") or "not_assessed"),
            "product_status": str(delivery.get("product_status") or "not_assessed"),
            "customer_outcome": str(delivery.get("customer_outcome") or "not_assessed").strip(),
            "capability_delta": _strings(delivery.get("capability_delta")),
            "remaining_gaps": _strings(delivery.get("remaining_gaps")),
            "evidence_boundary": _strings(delivery.get("evidence_boundary")),
            "recommended_next": {
                "id": recommended.get("id"),
                "status": str(recommended.get("status") or "none"),
                "reason": str(recommended.get("reason") or "").strip(),
            },
            "decisions_required": _strings(delivery.get("decisions_required")),
        },
        "agent_receipt": {
            "source_task": task_id,
            "technical_report": technical_report,
            "verification": verification,
            "repository": {"commits": [], "safe_files": []},
        },
    }


def with_repository_receipt(
    facts: dict,
    *,
    commits: list[str],
    safe_files: list[str],
) -> dict:
    """Return a technical projection enriched from Git after closeout."""
    enriched = deepcopy(facts)
    receipt = enriched.setdefault("agent_receipt", {})
    receipt["repository"] = {
        "commits": _strings(commits),
        "safe_files": _strings(safe_files),
    }
    return enriched


def ledger_path(root: Path) -> Path:
    return root / LEDGER_PATH


def load(root: Path) -> list[dict]:
    path = ledger_path(root)
    if not path.exists():
        return []
    rows = []
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            row = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid {LEDGER_PATH} line {number}: {exc.msg}") from exc
        if (
            not isinstance(row, dict)
            or row.get("schema") != SCHEMA
            or not row.get("delivery_id")
            or not isinstance(row.get("product"), dict)
            or not isinstance(row.get("agent_receipt"), dict)
        ):
            raise ValueError(f"invalid {LEDGER_PATH} line {number}: unsupported fact schema")
        rows.append(row)
    return rows


def latest(root: Path) -> dict:
    rows = load(root)
    return rows[-1] if rows else {}


def append(root: Path, facts: dict) -> None:
    """Append exactly once; a reused id with different data fails closed."""
    if facts.get("schema") != SCHEMA or not facts.get("delivery_id"):
        raise ValueError("CloseoutFacts must use the supported schema and delivery_id")
    existing = {row["delivery_id"]: row for row in load(root)}
    delivery_id = facts["delivery_id"]
    if delivery_id in existing:
        if existing[delivery_id] != facts:
            raise ValueError(f"conflicting durable delivery fact: {delivery_id}")
        return
    path = ledger_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(facts, ensure_ascii=False, sort_keys=True) + "\n")


def reconstruct_product_contract(facts: dict) -> dict:
    """Rebuild the authoritative product subset without lifecycle fields."""
    product = deepcopy(facts.get("product") or {})
    return {
        "milestone_status": product.get("milestone_status") or "not_assessed",
        "product_status": product.get("product_status") or "not_assessed",
        "customer_outcome": product.get("customer_outcome") or "not_assessed",
        "capability_delta": _strings(product.get("capability_delta")),
        "remaining_gaps": _strings(product.get("remaining_gaps")),
        "evidence_boundary": _strings(product.get("evidence_boundary")),
        "recommended_next": deepcopy(product.get("recommended_next") or {
            "id": None, "status": "none", "reason": ""
        }),
        "decisions_required": _strings(product.get("decisions_required")),
    }


def render_technical_report(facts: dict) -> str:
    """Render the complete agent-facing receipt for one CloseoutFacts row."""
    product = facts.get("product") or {}
    receipt = facts.get("agent_receipt") or {}
    repository = receipt.get("repository") or {}
    lines = [
        "# CodeRail Technical Closeout Report",
        "",
        f"- Delivery fact: {facts.get('delivery_id') or '(missing)'}",
        f"- Source task: {receipt.get('source_task') or '(missing)'}",
        f"- Recorded at: {facts.get('recorded_at') or '(missing)'}",
        f"- Owner locale: {facts.get('owner_locale') or '(missing)'}",
        f"- Closeout report: {receipt.get('technical_report') or '(missing)'}",
        "",
        "## Product Facts",
        "",
        f"- Customer outcome: {product.get('customer_outcome') or 'not_assessed'}",
        f"- Milestone assessment: {product.get('milestone_status') or 'not_assessed'}",
        f"- Product assessment: {product.get('product_status') or 'not_assessed'}",
        "- Capability delta:",
        *[f"  - {value}" for value in (product.get("capability_delta") or ["none"])],
        "- Remaining gaps:",
        *[f"  - {value}" for value in (product.get("remaining_gaps") or ["none"])],
        "- Evidence boundary:",
        *[f"  - {value}" for value in (product.get("evidence_boundary") or ["none"])],
        f"- Recommended next: {json.dumps(product.get('recommended_next') or {}, ensure_ascii=False, sort_keys=True)}",
        "- Decisions required:",
        *[f"  - {value}" for value in (product.get("decisions_required") or ["none"])],
        "",
        "## Verification",
        "",
    ]
    verification = receipt.get("verification") or []
    lines.extend(
        [f"- {row.get('cmd') or '(unknown)'} — exit {row.get('exit')}" for row in verification]
        or ["- none"]
    )
    lines.extend(["", "## Repository Receipt", "", "- Commits:"])
    lines.extend([f"  - {value}" for value in (repository.get("commits") or ["none"])])
    lines.append("- Safe files:")
    lines.extend([f"  - {value}" for value in (repository.get("safe_files") or ["none"])])
    lines.append("")
    return "\n".join(lines)
