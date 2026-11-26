"""Registro central de modelos para Alembic.

Importar este módulo no ejecuta DDL; únicamente completa ``Base.metadata``.
"""

from app.modules.absence import models as absence_models  # noqa: F401
from app.modules.administration import models as administration_models  # noqa: F401
from app.modules.auth import models as auth_models  # noqa: F401
from app.modules.communications import models as communications_models  # noqa: F401
from app.modules.documents import models as documents_models  # noqa: F401
from app.modules.employees import models as employee_models  # noqa: F401
from app.modules.licenses import models as license_models  # noqa: F401
from app.modules.overtime import models as overtime_models  # noqa: F401
from app.modules.profile import models as profile_models  # noqa: F401
from app.modules.sanctions import models as sanction_models  # noqa: F401
from app.modules.self_service import models as self_service_models  # noqa: F401
from app.modules.vacations import models as vacation_models  # noqa: F401
