"""Evaluador Default Deny en modo sombra; nunca cambia el permiso efectivo."""
from dataclasses import dataclass
from enum import Enum


class Scope(str, Enum):
    OWN = "own"
    SUPERVISED = "supervised"
    ORG = "org"
    GLOBAL = "global"
    TECHNICAL = "technical"


ROLE_CAPABILITIES = {
    "empleado": {"perfil:propio", "documentos:propios", "recibos:propios", "licencias:propias"},
    "supervisor": {"perfil:propio", "licencias:propias", "licencias:supervisados"},
    "recursos_humanos": {"empleados:consultar", "licencias:resolver", "documentos:gestionar"},
    "gerencia": {"indicadores:consultar", "ausentismo:consultar"},
    "administrador": {"administracion:gestionar"},
}


@dataclass(frozen=True)
class PermissionContext:
    role: str
    capability: str
    actor_employee_id: int | None = None
    resource_employee_id: int | None = None
    supervised_employee_ids: frozenset[int] = frozenset()
    allowed_orgs: frozenset[str] = frozenset()
    resource_org: str | None = None
    scope: Scope = Scope.OWN


@dataclass(frozen=True)
class ShadowDecision:
    current_allowed: bool
    target_allowed: bool
    difference: str
    reason: str


def target_allows(context: PermissionContext) -> tuple[bool, str]:
    if context.capability not in ROLE_CAPABILITIES.get(context.role, set()):
        return False, "capability_missing"
    if context.scope == Scope.OWN:
        return (
            context.actor_employee_id is not None
            and context.actor_employee_id == context.resource_employee_id,
            "own_resource",
        )
    if context.scope == Scope.SUPERVISED:
        return (
            context.resource_employee_id in context.supervised_employee_ids,
            "supervised_resource",
        )
    if context.scope == Scope.ORG:
        return (context.resource_org in context.allowed_orgs, "organization_scope")
    if context.scope == Scope.TECHNICAL:
        return (context.role == "administrador", "technical_scope")
    return False, "global_scope_requires_explicit_policy"


def compare(current_allowed: bool, context: PermissionContext) -> ShadowDecision:
    target, reason = target_allows(context)
    if current_allowed == target:
        difference = "same"
    elif current_allowed and not target:
        difference = "excessive_current_access"
    else:
        difference = "legitimate_access_at_risk"
    return ShadowDecision(current_allowed, target, difference, reason)

