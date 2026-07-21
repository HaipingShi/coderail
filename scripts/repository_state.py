#!/usr/bin/env python3
"""Canonical immutable Git snapshot and ownership classification."""
from __future__ import annotations

import fnmatch
import hashlib
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


SENSITIVE_PATTERNS = (
    ".env", ".env.*", "*.pem", "*.key", "*.p12", "*.pfx",
    "*api_key*", "*api-key*", "credentials.*", ".aws/**",
)
GENERATED_PATTERNS = (
    "node_modules/**", "dist/**", "build/**", "coverage/**", ".next/**",
)
EPHEMERAL_PATHS = frozenset({".coderail/pending_close.json"})


@dataclass(frozen=True)
class FileState:
    status: str
    path: str
    original_path: str | None = None
    fingerprint: str | None = None


@dataclass(frozen=True)
class RepositorySnapshot:
    captured_at: str
    head: str | None
    files: tuple[FileState, ...]
    available: bool = True


@dataclass(frozen=True)
class OwnershipClassification:
    safe: tuple[str, ...] = ()
    outside: tuple[str, ...] = ()
    forbidden: tuple[str, ...] = ()
    sensitive: tuple[str, ...] = ()
    generated: tuple[str, ...] = ()
    ephemeral: tuple[str, ...] = ()
    ignored: tuple[str, ...] = ()
    baseline: tuple[str, ...] = ()
    ambiguous: tuple[str, ...] = ()


@dataclass(frozen=True)
class ScopeContradiction:
    path: str
    allowed_pattern: str
    forbidden_pattern: str


def _git(root: Path, args: list[str], *, text: bool = True):
    return subprocess.run(
        ["git", "-C", str(root), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=text,
        encoding="utf-8" if text else None,
        errors="surrogateescape" if text else None,
    )


def fingerprint_path(root: Path, relative: str) -> str:
    path = root / relative
    if not path.exists() and not path.is_symlink():
        return "missing"
    digest = hashlib.sha256()
    if path.is_symlink():
        digest.update(b"symlink\0")
        digest.update(os.readlink(path).encode("utf-8", errors="surrogateescape"))
        return digest.hexdigest()
    if path.is_dir():
        digest.update(b"directory\0")
        for child in sorted(p.relative_to(path).as_posix() for p in path.rglob("*")):
            digest.update(child.encode("utf-8", errors="surrogateescape") + b"\0")
        return digest.hexdigest()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def capture(
    root: Path,
    *,
    include_ignored: bool = False,
    fingerprints: bool = False,
) -> RepositorySnapshot:
    args = ["status", "--porcelain=v1", "-z", "--untracked-files=all"]
    if include_ignored:
        args.append("--ignored=matching")
    result = _git(root, args, text=False)
    files: list[FileState] = []
    if result.returncode == 0:
        records = (result.stdout or b"").split(b"\0")
        index = 0
        while index < len(records):
            raw = records[index]
            index += 1
            if len(raw) < 4:
                continue
            status = raw[:2].decode("ascii", errors="replace")
            path = os.fsdecode(raw[3:]).replace("\\", "/")
            original_path = None
            if ("R" in status or "C" in status) and index < len(records):
                original = records[index]
                index += 1
                if original:
                    original_path = os.fsdecode(original).replace("\\", "/")
            fingerprint = fingerprint_path(root, path) if fingerprints else None
            files.append(FileState(status, path, original_path, fingerprint))
    head = _git(root, ["rev-parse", "HEAD"])
    return RepositorySnapshot(
        datetime.now(timezone.utc).isoformat(),
        head.stdout.strip() if head.returncode == 0 else None,
        tuple(files),
        result.returncode == 0,
    )


def normalize_pattern(pattern: str) -> str:
    return pattern.replace("\\", "/").lstrip("./").rstrip()


def normalize_patterns(patterns: list[str] | tuple[str, ...]) -> list[str]:
    normalized = []
    for pattern in patterns:
        candidate = normalize_pattern(pattern)
        if candidate and candidate.lower() not in {"none", "n/a"}:
            normalized.append(candidate)
    return list(dict.fromkeys(normalized))


def matching_patterns(path: str, patterns: list[str] | tuple[str, ...]) -> list[str]:
    normalized = normalize_pattern(path)
    matches = []
    for pattern in normalize_patterns(patterns):
        if normalized == pattern or matches_any(normalized, [pattern]):
            matches.append(pattern)
    return matches


def find_scope_contradictions(
    paths: list[str] | tuple[str, ...],
    allowed: list[str] | tuple[str, ...],
    forbidden: list[str] | tuple[str, ...],
) -> tuple[ScopeContradiction, ...]:
    contradictions = []
    seen = set()
    for raw_path in paths:
        path = normalize_pattern(raw_path)
        if not path:
            continue
        for allowed_pattern in matching_patterns(path, allowed):
            for forbidden_pattern in matching_patterns(path, forbidden):
                key = (path, allowed_pattern, forbidden_pattern)
                if key not in seen:
                    seen.add(key)
                    contradictions.append(ScopeContradiction(*key))
    return tuple(contradictions)


def matches_any(path: str, patterns: list[str] | tuple[str, ...]) -> bool:
    normalized = normalize_pattern(path)
    for pattern in patterns:
        candidate = normalize_pattern(pattern)
        if not candidate:
            continue
        if candidate.endswith("/**"):
            base = candidate[:-3].rstrip("/")
            if normalized.rstrip("/") == base or normalized.startswith(base + "/"):
                return True
        if normalized == candidate or fnmatch.fnmatch(normalized, candidate):
            return True
    return False


def classify(
    files: tuple[FileState, ...] | list[FileState],
    *,
    allowed: list[str],
    forbidden: list[str],
    unchanged_baseline: set[str],
    state_files: set[str],
    include_state: bool,
) -> OwnershipClassification:
    buckets: dict[str, list[str]] = {
        name: [] for name in OwnershipClassification.__dataclass_fields__
    }
    for row in files:
        path = row.path
        if path in EPHEMERAL_PATHS:
            buckets["ephemeral"].append(path)
        elif row.status == "!!":
            buckets["ignored"].append(path)
        elif path in unchanged_baseline:
            buckets["baseline"].append(path)
        elif matches_any(path, SENSITIVE_PATTERNS):
            buckets["sensitive"].append(path)
        elif forbidden and matches_any(path, forbidden):
            buckets["forbidden"].append(path)
        elif matches_any(path, GENERATED_PATTERNS):
            buckets["generated"].append(path)
        elif include_state and path in state_files:
            buckets["safe"].append(path)
        elif allowed and not matches_any(path, allowed):
            buckets["outside"].append(path)
        elif not allowed:
            buckets["ambiguous"].append(path)
        else:
            buckets["safe"].append(path)
    return OwnershipClassification(**{key: tuple(value) for key, value in buckets.items()})
