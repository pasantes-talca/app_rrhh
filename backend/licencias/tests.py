from django.test import SimpleTestCase
from django.urls import resolve

from .serializers import CrearLicenciaSerializer, ResolucionLicenciaSerializer


class ContratoLicenciasTests(SimpleTestCase):
    def test_rechaza_periodo_invertido(self):
        serializer = CrearLicenciaSerializer(data={"type_id": 1, "date_from": "2026-11-20", "date_to": "2026-11-10", "days": 5})
        self.assertFalse(serializer.is_valid())

    def test_acepta_solo_resoluciones_validas(self):
        self.assertTrue(ResolucionLicenciaSerializer(data={"decision": "Aprobada"}).is_valid())
        self.assertFalse(ResolucionLicenciaSerializer(data={"decision": "Pendiente"}).is_valid())

    def test_publica_rutas_del_contrato_existente(self):
        self.assertEqual(resolve("/api/v1/licenses/types").url_name, "licencias-tipos")
        self.assertEqual(resolve("/api/v1/licenses/9/hr-resolution").url_name, "licencias-resolver-rrhh")
