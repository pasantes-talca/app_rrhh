import unittest

from modules.identity.reconciliation import (
    IdentityRecord, MatchStatus, reconcile_one,
)


class IdentityReconciliationTests(unittest.TestCase):
    def test_exact_dni_match_is_verified(self):
        legacy = IdentityRecord(1, "empleado", dni="12.345.678")
        source = IdentityRecord(101, "empleado2", dni="12345678", trilay_id=900)
        result = reconcile_one(legacy, [source])
        self.assertEqual(result.status, MatchStatus.VERIFIED)
        self.assertEqual(result.right_ids, [101])

    def test_name_is_not_an_identifier(self):
        legacy = IdentityRecord(1, "empleado")
        source = IdentityRecord(101, "empleado2")
        result = reconcile_one(legacy, [source])
        self.assertEqual(result.status, MatchStatus.MISSING_IDENTIFIERS)

    def test_legajo_requires_company_and_manual_review(self):
        legacy = IdentityRecord(1, "empleado", legajo="44", company="Oeste")
        source = IdentityRecord(101, "empleado2", legajo="44", company="Oeste")
        result = reconcile_one(legacy, [source])
        self.assertEqual(result.status, MatchStatus.PENDING)
        self.assertTrue(result.requires_manual_review)

    def test_contradictory_identifiers_do_not_link(self):
        legacy = IdentityRecord(1, "empleado", dni="111", cuil="20-111-1", legajo="5", company="Oeste")
        source = IdentityRecord(101, "empleado2", dni="111", cuil="20-999-9", legajo="8", company="Oeste")
        result = reconcile_one(legacy, [source])
        self.assertEqual(result.status, MatchStatus.CONFLICT)
        self.assertTrue(result.requires_manual_review)

    def test_duplicate_candidates_are_not_linked(self):
        legacy = IdentityRecord(1, "empleado", dni="111")
        candidates = [
            IdentityRecord(101, "empleado2", dni="111"),
            IdentityRecord(102, "empleado2", dni="111"),
        ]
        result = reconcile_one(legacy, candidates)
        self.assertEqual(result.status, MatchStatus.DUPLICATE)
        self.assertEqual(set(result.right_ids), {101, 102})


if __name__ == "__main__":
    unittest.main()

