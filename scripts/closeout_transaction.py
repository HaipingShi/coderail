#!/usr/bin/env python3
"""Single success authority for the CodeRail closeout lifecycle."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class Phase(Enum):
    CREATED = auto()
    VERIFIED = auto()
    SNAPSHOTTED = auto()
    CLASSIFIED = auto()
    STAGED = auto()
    COMMIT_PENDING = auto()
    COMMITTED = auto()
    PERSISTED = auto()
    RESCANNED = auto()
    FINALIZED = auto()
    FAILED = auto()


class Failure(Enum):
    BLOCKED_SCOPE = auto()
    BLOCKED_SENSITIVE = auto()
    STAGE_FAILED = auto()
    COMMIT_FAILED = auto()
    PERSIST_FAILED = auto()
    POST_COMMIT_DIRTY = auto()
    INSPECT_INCONSISTENT = auto()


TRANSITIONS = {
    Phase.CREATED: {Phase.VERIFIED},
    Phase.VERIFIED: {Phase.SNAPSHOTTED},
    Phase.SNAPSHOTTED: {Phase.CLASSIFIED},
    Phase.CLASSIFIED: {Phase.STAGED, Phase.COMMIT_PENDING},
    Phase.STAGED: {Phase.COMMITTED, Phase.COMMIT_PENDING},
    Phase.COMMIT_PENDING: {Phase.STAGED, Phase.COMMITTED},
    Phase.COMMITTED: {Phase.PERSISTED},
    Phase.PERSISTED: {Phase.RESCANNED},
}


@dataclass(frozen=True)
class TransactionResult:
    task_id: str
    phase: Phase
    success: bool
    failure: Failure | None
    paths: tuple[str, ...]
    inspect_status: str | None


class CloseoutTransaction:
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.phase = Phase.CREATED
        self.failure: Failure | None = None
        self.paths: tuple[str, ...] = ()
        self.inspect_status: str | None = None

    @property
    def success(self) -> bool:
        return self.phase is Phase.FINALIZED and self.failure is None

    def advance(self, phase: Phase) -> None:
        if self.phase in {Phase.FAILED, Phase.FINALIZED}:
            raise ValueError(f"cannot advance terminal transaction from {self.phase.name}")
        expected = TRANSITIONS.get(self.phase, set())
        if phase not in expected:
            names = ", ".join(item.name for item in sorted(expected, key=lambda item: item.value))
            raise ValueError(f"expected one of {names or 'none'}, got {phase.name}")
        self.phase = phase

    def mark_commit_pending(self, paths: list[str] | tuple[str, ...]) -> None:
        if self.phase not in {Phase.CLASSIFIED, Phase.STAGED}:
            raise ValueError(f"cannot mark commit pending from {self.phase.name}")
        self.paths = tuple(sorted(set(paths)))
        self.phase = Phase.COMMIT_PENDING

    @classmethod
    def from_commit_pending(
        cls, task_id: str, paths: list[str] | tuple[str, ...]
    ) -> "CloseoutTransaction":
        transaction = cls(task_id)
        transaction.phase = Phase.COMMIT_PENDING
        transaction.paths = tuple(sorted(set(paths)))
        return transaction

    def fail(self, failure: Failure, paths: list[str] | tuple[str, ...] = ()) -> None:
        if self.phase is Phase.FINALIZED:
            raise ValueError("cannot fail a finalized transaction")
        self.failure = failure
        self.paths = tuple(sorted(set(paths)))
        self.phase = Phase.FAILED

    def finalize(self, *, inspect_status: str, residual_paths: list[str]) -> None:
        if self.phase is not Phase.RESCANNED:
            raise ValueError(f"cannot finalize from {self.phase.name}")
        self.inspect_status = inspect_status
        if residual_paths:
            self.fail(Failure.POST_COMMIT_DIRTY, residual_paths)
        elif inspect_status == "blocked":
            self.fail(Failure.INSPECT_INCONSISTENT)
        else:
            self.phase = Phase.FINALIZED

    def result(self) -> TransactionResult:
        return TransactionResult(
            self.task_id,
            self.phase,
            self.success,
            self.failure,
            self.paths,
            self.inspect_status,
        )
