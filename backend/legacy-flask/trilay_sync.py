import argparse
import logging
import time

from app import create_app
from integrations.trilay.empleados2 import sync_empleados2


def execute(app, apply):
    with app.app_context():
        if not apply:
            raise SystemExit("Modo seguro: use --apply para escribir exclusivamente en rrhh.empleados2")
        result = sync_empleados2(app.config)
        logging.info("Trilay sync empleados2: consultados=%s actualizados=%s sin_cambios=%s cuentas_creadas=%s vinculadas=%s",
                     result["consultados"], result["insertados_o_actualizados"], result["sin_cambios"],
                     result["cuentas_creadas"], result["cuentas_vinculadas"])


def main():
    parser = argparse.ArgumentParser(description="Sincronizacion de empleados Trilay -> RRHH")
    parser.add_argument("--apply", action="store_true", help="aplica altas y cambios; sin esta opcion solo simula")
    parser.add_argument("--worker", action="store_true", help="repite segun TRILAY_SYNC_INTERVAL_SECONDS")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    app = create_app()
    if not app.config["TRILAY_SYNC_ENABLED"]:
        raise SystemExit("TRILAY_SYNC_ENABLED=false; la integracion permanece desactivada")
    while True:
        execute(app, args.apply)
        if not args.worker:
            break
        time.sleep(max(60, app.config["TRILAY_SYNC_INTERVAL_SECONDS"]))


if __name__ == "__main__":
    main()
