"""Planificador puro de sincronización; no abre conexiones ni escribe datos."""
from dataclasses import dataclass


@dataclass(frozen=True)
class SyncPlan:
    upserts: tuple[dict, ...]
    mark_absent_ids: tuple[int, ...]
    duplicate_ids: tuple[int, ...]
    errors: tuple[str, ...]
    complete_snapshot: bool


def build_sync_plan(source_rows, current_ids, *, complete_snapshot):
    by_id, duplicate_ids, errors = {}, set(), []
    for index, row in enumerate(source_rows):
        source_id = row.get("id_usuario")
        if source_id is None:
            errors.append(f"row_{index}:missing_id")
            continue
        if source_id in by_id:
            duplicate_ids.add(source_id)
            continue
        by_id[source_id] = dict(row)
    for source_id in duplicate_ids:
        by_id.pop(source_id, None)
    source_ids = set(by_id)
    # Un lote incompleto o inválido jamás produce ausencias.
    may_mark_absent = complete_snapshot and not errors and not duplicate_ids and bool(source_ids)
    absent = tuple(sorted(set(current_ids) - source_ids)) if may_mark_absent else ()
    return SyncPlan(
        tuple(by_id[key] for key in sorted(by_id)),
        absent,
        tuple(sorted(duplicate_ids)),
        tuple(errors),
        complete_snapshot,
    )

