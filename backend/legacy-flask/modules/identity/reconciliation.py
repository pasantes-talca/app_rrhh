"""Reconciliación pura entre Empleado y Empleado2 usando evidencia sintética."""
from dataclasses import dataclass, field
from enum import Enum


class MatchStatus(str, Enum):
    VERIFIED = "verified"
    PENDING = "pending"
    CONFLICT = "conflict"
    DUPLICATE = "duplicate"
    MISSING_IDENTIFIERS = "missing_identifiers"


@dataclass(frozen=True)
class IdentityRecord:
    technical_id: int
    source: str
    dni: str | None = None
    cuil: str | None = None
    legajo: str | None = None
    company: str | None = None
    trilay_id: int | None = None
    linked_user_id: int | None = None


@dataclass(frozen=True)
class MatchEvidence:
    field: str
    left_value: str
    right_value: str


@dataclass
class MatchResult:
    left_id: int
    right_ids: list[int]
    status: MatchStatus
    evidence: list[MatchEvidence] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    requires_manual_review: bool = False


def _norm(value):
    if value is None:
        return None
    normalized = "".join(ch for ch in str(value).upper().strip() if ch.isalnum())
    return normalized or None


def _identifier(record, field_name):
    return _norm(getattr(record, field_name))


def reconcile_one(legacy: IdentityRecord, candidates: list[IdentityRecord]) -> MatchResult:
    fields = ("dni", "cuil")
    legacy_identifiers = {field: _identifier(legacy, field) for field in fields}
    legacy_legajo = _identifier(legacy, "legajo")
    legacy_company = _identifier(legacy, "company")
    if not any(legacy_identifiers.values()) and not legacy_legajo:
        return MatchResult(legacy.technical_id, [], MatchStatus.MISSING_IDENTIFIERS, requires_manual_review=True)

    scored = []
    for candidate in candidates:
        evidence, conflicts = [], []
        for field in fields:
            left, right = legacy_identifiers[field], _identifier(candidate, field)
            if left and right:
                if left == right:
                    evidence.append(MatchEvidence(field, left, right))
                else:
                    conflicts.append(field)
        left_legajo, right_legajo = legacy_legajo, _identifier(candidate, "legajo")
        same_company = legacy_company and legacy_company == _identifier(candidate, "company")
        if left_legajo and right_legajo:
            if left_legajo == right_legajo and same_company:
                evidence.append(MatchEvidence("legajo+empresa", left_legajo, right_legajo))
            elif left_legajo != right_legajo and evidence:
                conflicts.append("legajo")
        if evidence or conflicts:
            scored.append((candidate, evidence, conflicts))

    contradictory = [(c, e, x) for c, e, x in scored if e and x]
    if contradictory:
        return MatchResult(
            legacy.technical_id,
            [c.technical_id for c, _, _ in contradictory],
            MatchStatus.CONFLICT,
            [item for _, evidence, _ in contradictory for item in evidence],
            sorted({item for _, _, conflicts in contradictory for item in conflicts}),
            True,
        )
    valid = [(c, e) for c, e, x in scored if e and not x]
    if len(valid) > 1:
        return MatchResult(
            legacy.technical_id,
            [c.technical_id for c, _ in valid],
            MatchStatus.DUPLICATE,
            [item for _, evidence in valid for item in evidence],
            requires_manual_review=True,
        )
    if len(valid) == 1:
        candidate, evidence = valid[0]
        strong = {e.field for e in evidence}
        verified = bool(strong & {"dni", "cuil"}) or len(strong) >= 2
        return MatchResult(
            legacy.technical_id,
            [candidate.technical_id],
            MatchStatus.VERIFIED if verified else MatchStatus.PENDING,
            evidence,
            requires_manual_review=not verified,
        )
    return MatchResult(legacy.technical_id, [], MatchStatus.PENDING, requires_manual_review=True)


def reconcile_all(legacy_records, source_records):
    return [reconcile_one(record, list(source_records)) for record in legacy_records]

