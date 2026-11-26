import ast
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class StaticSafetyTests(unittest.TestCase):
    def test_python_sources_parse(self):
        for path in ROOT.rglob("*.py"):
            if any(part in {".venv", ".venv-test", "__pycache__"} for part in path.parts):
                continue
            with self.subTest(path=str(path.relative_to(ROOT))):
                ast.parse(path.read_text(encoding="utf-8-sig"))

    def test_sync_requires_explicit_apply_flag(self):
        source = (ROOT / "trilay_sync.py").read_text(encoding="utf-8")
        self.assertIn("if not apply:", source)
        self.assertIn("--apply", source)
        self.assertIn("TRILAY_SYNC_ENABLED", source)

    def test_import_scripts_do_not_run_on_import(self):
        for relative in (
            "scripts/import_nomina_maestra_empleados2.py",
            "scripts/importar_vacaciones_excel.py",
            "scripts/importar_ausentismo_excel.py",
        ):
            source = (ROOT / relative).read_text(encoding="utf-8-sig")
            tree = ast.parse(source)
            guarded = any(
                isinstance(node, ast.If)
                and isinstance(node.test, ast.Compare)
                and isinstance(node.test.left, ast.Name)
                and node.test.left.id == "__name__"
                for node in tree.body
            )
            with self.subTest(path=relative):
                self.assertTrue(guarded)


if __name__ == "__main__":
    unittest.main()

