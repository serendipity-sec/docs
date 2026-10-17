import importlib.util
import tempfile
import unittest
import zipfile
from pathlib import Path

spec = importlib.util.spec_from_file_location("notion_archive", Path(__file__).with_name("notion_archive.py"))
archive = importlib.util.module_from_spec(spec)
spec.loader.exec_module(archive)


class NotionArchiveTests(unittest.TestCase):
    def export(self, path, extras=None):
        with zipfile.ZipFile(path, "w") as z:
            z.writestr(f"Root {archive.ROOT_ID}.md", "# Root\n\n[missing](Root/missing.csv)\n")
            for name, content in (extras or {}).items():
                z.writestr(name, content)

    def test_repeat_is_noop_and_missing_files_are_retained(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = base / "export.zip"
            repo = base / "repo"
            self.export(source, {"Root/note.txt": b"unchanged bytes\r\n"})
            first = archive.ingest(source, repo)
            self.assertGreater(first["changed_files"], 0)
            self.assertEqual(archive.ingest(source, repo)["changed_files"], 0)
            self.assertEqual(archive.verify(repo)["verified_files"], 2)
            self.export(source)
            archive.ingest(source, repo)
            self.assertEqual((repo / "notion/export/Root/note.txt").read_bytes(), b"unchanged bytes\r\n")

    def test_wrong_root_rejected_before_any_write(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = base / "export.zip"
            with zipfile.ZipFile(source, "w") as z:
                z.writestr("another-page.md", "# Wrong workspace")
            with self.assertRaises(ValueError):
                archive.ingest(source, base / "repo")
            self.assertFalse((base / "repo").exists())

    def test_zip_traversal_and_unrelated_content_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            for unsafe in ("../outside.txt", "Other/private.md", "Root/file.txt:stream"):
                with self.subTest(unsafe=unsafe):
                    source = base / "export.zip"
                    self.export(source, {unsafe: "untrusted"})
                    with self.assertRaises(ValueError):
                        archive.ingest(source, base / "repo")
                    self.assertFalse((base / "repo").exists())


if __name__ == "__main__":
    unittest.main()
