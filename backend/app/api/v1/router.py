from fastapi import APIRouter

from app.modules.employees.router import router as employees_router
from app.modules.auth.router import router as auth_router
from app.modules.self_service.router import router as self_service_router
from app.modules.licenses.router import router as licenses_router
from app.modules.vacations.router import router as vacations_router
from app.modules.absence.router import router as absence_router
from app.modules.communications.router import router as communications_router
from app.modules.sanctions.router import router as sanctions_router
from app.modules.overtime.router import router as overtime_router
from app.modules.documents.router import router as documents_router
from app.modules.profile.router import router as profile_router
from app.modules.administration.router import router as administration_router
from app.modules.organization.router import router as organization_router
from app.modules.dashboard.router import router as dashboard_router


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(employees_router)
api_router.include_router(auth_router)
api_router.include_router(self_service_router)
api_router.include_router(licenses_router)
api_router.include_router(vacations_router)
api_router.include_router(absence_router)
api_router.include_router(communications_router)
api_router.include_router(sanctions_router)
api_router.include_router(overtime_router)
api_router.include_router(documents_router)
api_router.include_router(profile_router)
api_router.include_router(administration_router)
api_router.include_router(organization_router)
api_router.include_router(dashboard_router)


@api_router.get("/health", tags=["system"])
def health():
    return {"status": "ok", "service": "talca-rrhh-api", "version": "v1"}

