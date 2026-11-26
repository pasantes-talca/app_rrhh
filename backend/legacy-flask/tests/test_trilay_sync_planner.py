import unittest

from integrations.trilay.planner import build_sync_plan


class TrilaySyncPlannerTests(unittest.TestCase):
    def test_complete_snapshot_marks_absent(self):
        plan = build_sync_plan(
            [{"id_usuario": 1}, {"id_usuario": 2}], {1, 2, 3},
            complete_snapshot=True,
        )
        self.assertEqual(plan.mark_absent_ids, (3,))

    def test_incomplete_snapshot_never_marks_absent(self):
        plan = build_sync_plan([{"id_usuario": 1}], {1, 2, 3}, complete_snapshot=False)
        self.assertEqual(plan.mark_absent_ids, ())

    def test_empty_snapshot_never_marks_everyone_absent(self):
        plan = build_sync_plan([], {1, 2, 3}, complete_snapshot=True)
        self.assertEqual(plan.mark_absent_ids, ())

    def test_duplicate_source_ids_are_quarantined(self):
        plan = build_sync_plan(
            [{"id_usuario": 1, "nombre": "A"}, {"id_usuario": 1, "nombre": "B"}],
            {1, 2}, complete_snapshot=True,
        )
        self.assertEqual(plan.duplicate_ids, (1,))
        self.assertEqual(plan.upserts, ())
        self.assertEqual(plan.mark_absent_ids, ())

    def test_invalid_row_prevents_absence_marking(self):
        plan = build_sync_plan(
            [{"id_usuario": 1}, {"nombre": "sin id"}],
            {1, 2}, complete_snapshot=True,
        )
        self.assertTrue(plan.errors)
        self.assertEqual(plan.mark_absent_ids, ())

    def test_planning_is_idempotent(self):
        rows = [{"id_usuario": 2}, {"id_usuario": 1}]
        self.assertEqual(
            build_sync_plan(rows, {1, 2}, complete_snapshot=True),
            build_sync_plan(rows, {1, 2}, complete_snapshot=True),
        )


if __name__ == "__main__":
    unittest.main()

