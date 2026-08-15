#!/usr/bin/env python3
"""Low-noise, locale-aware owner projection for CloseoutFacts."""
from __future__ import annotations

import re


SUPPORTED_LOCALES = {"en", "zh-CN"}
GOVERNANCE_JARGON = re.compile(
    r"\b(?:closeout|commit|push|Coordinate|Drive|Green|Red|marker|safe files?)\b|"
    r"(?:治理|控制面|生命周期|收口|任务编号|坐标状态|安全文件)",
    re.I,
)
TASK_ID = re.compile(r"\b(?:T-\d+|[A-Z][A-Z0-9]+(?:-[A-Z0-9]+)+)\b")
PATH = re.compile(
    r"(?:^|[\s`])(?:\.?/?[A-Za-z0-9_.-]+/)+[A-Za-z0-9_.-]+|"
    r"(?:^|[\s`])\.[A-Za-z0-9_.-]+/|"
    r"\b[A-Za-z0-9_.-]+\.(?:md|py|ts|tsx|js|json|jsonl|yml|yaml)\b"
)
ENGLISH_WORD = re.compile(r"[A-Za-z]{2,}")
ANNOTATED_ENGLISH = re.compile(
    r"(?<=[\u3400-\u9fff])（[^（）\n]*[A-Za-z][^（）\n]*）|"
    r"(?<=[\u3400-\u9fff])\([^()\n]*[A-Za-z][^()\n]*\)"
)


def _plain(value) -> str:
    return str(value or "").strip().rstrip("。！？.!?;；")


def _join(values) -> str:
    return "；".join(_plain(value) for value in values if _plain(value))


def _next_reason(product: dict) -> str:
    return _plain((product.get("recommended_next") or {}).get("reason"))


def _product_copy(product: dict) -> str:
    return "\n".join([
        str(product.get("customer_outcome") or ""),
        *(product.get("capability_delta") or []),
        *(product.get("remaining_gaps") or []),
        *(product.get("evidence_boundary") or []),
        _next_reason(product),
        *(product.get("decisions_required") or []),
    ])


def sentence_count(text: str) -> int:
    return len(re.findall(r"[^。！？.!?\n]+[。！？.!?]", text))


DECISIONS_HEADERS = ("需要你决定：", "Your decision:")


def _narrative(text: str) -> str:
    """The part of the receipt subject to the information budget. The
    decisions block is enumerated choice, not narrative, and is exempt so
    options are never compressed away to fit a sentence budget."""
    for header in DECISIONS_HEADERS:
        marker = f"\n{header}"
        if marker in text:
            return text.split(marker, 1)[0]
    return text


def _decision_items(product: dict) -> list[str]:
    return [
        _plain(item)
        for item in (product.get("decisions_required") or [])
        if _plain(item) and _plain(item) not in {"none", "无"}
    ]


def _with_decisions(text: str, product: dict, header: str) -> str:
    items = _decision_items(product)
    if not items:
        return text
    return text + f"\n{header}\n" + "\n".join(f"- {item}" for item in items)


def _unannotated_english(text: str) -> list[str]:
    outside_notes = ANNOTATED_ENGLISH.sub("", text)
    return sorted(set(ENGLISH_WORD.findall(outside_notes)), key=str.lower)


def surface_violations(text: str, *, locale: str) -> list[str]:
    issues = []
    narrative = _narrative(text)
    count = sentence_count(narrative)
    if not 3 <= count <= 10:
        issues.append(f"information budget requires 3-10 narrative sentences; found {count}")
    if TASK_ID.search(text):
        issues.append("task or product id is visible")
    if PATH.search(text):
        issues.append("file path is visible")
    if GOVERNANCE_JARGON.search(text):
        issues.append("governance jargon is visible")
    if locale == "zh-CN":
        english = _unannotated_english(text)
        if english:
            issues.append("unannotated English is visible: " + ", ".join(english))
    return issues


def product_copy_violations(facts: dict, *, locale: str) -> list[str]:
    """Validate authored owner copy before any closeout state transition."""
    text = _product_copy(facts.get("product") or {})
    issues = []
    if not text.strip():
        issues.append("owner product copy is empty")
    if TASK_ID.search(text):
        issues.append("task or product id appears in owner product copy")
    if PATH.search(text):
        issues.append("file path appears in owner product copy")
    if GOVERNANCE_JARGON.search(text):
        issues.append("governance jargon appears in owner product copy")
    if locale == "zh-CN" and _unannotated_english(text):
        issues.append("unannotated English appears in Chinese owner product copy")
    return issues


def _zh_fallback() -> str:
    return "\n".join([
        "本次工作已通过已登记的检查。",
        "当前交付事实尚未提供符合要求的中文产品说明，因此这里不转述未本地化的内容。",
        "完整证据已保存供执行代理查阅，请先补充中文产品说明再决定下一步。",
    ])


def _render_zh(product: dict, verification_count: int) -> str:
    source_text = _product_copy(product)
    if _unannotated_english(source_text):
        return _zh_fallback()

    lines = [f"本次完成：{_plain(product.get('customer_outcome')) or '当前没有可确认的新产品能力'}。"]
    capabilities = _join(product.get("capability_delta") or [])
    lines.append(f"现在可以：{capabilities or '维持本次交付前已经验证的能力'}。")
    evidence = _join(product.get("evidence_boundary") or [])
    if evidence:
        lines.append(f"验证范围：{evidence}。")
    elif verification_count:
        lines.append(f"验证范围：已完成{verification_count}项登记检查。")
    else:
        lines.append("验证范围：当前没有登记可转述的验证证据。")
    gaps = _join(product.get("remaining_gaps") or [])
    if gaps:
        lines.append(f"尚未覆盖：{gaps}。")
    next_reason = _next_reason(product)
    lines.append(f"下一步：{next_reason or '由你决定是否开始新的产品工作'}。")
    return _with_decisions("\n".join(lines), product, "需要你决定：")


def _render_en(product: dict, verification_count: int) -> str:
    capabilities = "; ".join(product.get("capability_delta") or []) or "no new capability was claimed"
    evidence = "; ".join(product.get("evidence_boundary") or [])
    gaps = "; ".join(product.get("remaining_gaps") or [])
    next_reason = _next_reason(product) or "the owner decides whether to begin new product work"
    lines = [
        f"Completed: {_plain(product.get('customer_outcome')) or 'no assessed product outcome'}.",
        f"You can now: {capabilities}.",
        f"Evidence: {evidence or f'{verification_count} registered checks were recorded'}.",
    ]
    if gaps:
        lines.append(f"Not yet covered: {gaps}.")
    lines.append(f"Next: {next_reason}.")
    return _with_decisions("\n".join(lines), product, "Your decision:")


def render(facts: dict, *, locale: str | None = None) -> str:
    selected = locale or facts.get("owner_locale") or "en"
    if selected not in SUPPORTED_LOCALES:
        raise ValueError(f"unsupported owner locale: {selected}")
    product = facts.get("product") or {}
    verification_count = len((facts.get("agent_receipt") or {}).get("verification") or [])
    text = _render_zh(product, verification_count) if selected == "zh-CN" else _render_en(
        product, verification_count
    )
    issues = surface_violations(text, locale=selected)
    if issues:
        if selected == "zh-CN":
            fallback = _zh_fallback()
            fallback_issues = surface_violations(fallback, locale=selected)
            if not fallback_issues:
                return fallback
        raise ValueError("invalid Owner Receipt: " + "; ".join(issues))
    return text
