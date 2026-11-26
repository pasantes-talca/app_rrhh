import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from modules.security.private_storage import PrivateStorage


PDF = b"%PDF-1.4\nsynthetic document\n%%EOF"


class PrivateStorageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.storage = PrivateStorage(self.temp.name, max_size=100)

    def tearDown(self):
        self.temp.cleanup()

    def test_owner_can_store_and_read(self):
        document = self.storage.store(10, "recibo.pdf", PDF, "application/pdf")
        self.assertNotEqual(document.internal_name, document.original_name)
        self.assertEqual(self.storage.read(document, 10), PDF)

    def test_other_user_is_denied(self):
        document = self.storage.store(10, "privado.pdf", PDF, "application/pdf")
        with self.assertRaises(PermissionError):
            self.storage.read(document, 11)

    def test_extension_and_signature_are_both_validated(self):
        with self.assertRaises(ValueError):
            self.storage.store(10, "fake.jpg", PDF, "image/jpeg")
        with self.assertRaises(ValueError):
            self.storage.store(10, "fake.exe", PDF, "application/pdf")

    def test_size_limit(self):
        with self.assertRaisesRegex(ValueError, "file_too_large"):
            self.storage.store(10, "large.pdf", PDF * 10, "application/pdf")

    def test_original_path_is_removed(self):
        document = self.storage.store(10, "../../secret.pdf", PDF, "application/pdf")
        self.assertEqual(document.original_name, "secret.pdf")
        self.assertTrue((Path(self.temp.name) / document.internal_name).is_file())

    def test_integrity_failure_is_detected(self):
        document = self.storage.store(10, "recibo.pdf", PDF, "application/pdf")
        (Path(self.temp.name) / document.internal_name).write_bytes(b"tampered")
        with self.assertRaisesRegex(ValueError, "integrity_check_failed"):
            self.storage.read(document, 10)

    def test_internal_path_traversal_is_denied(self):
        document = self.storage.store(10, "recibo.pdf", PDF, "application/pdf")
        tampered = replace(document, internal_name="../outside.pdf")
        with self.assertRaises(PermissionError):
            self.storage.read(tampered, 10)


if __name__ == "__main__":
    unittest.main()

