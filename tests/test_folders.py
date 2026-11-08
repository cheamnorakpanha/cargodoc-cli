from pathlib import Path
import tempfile
import unittest
from cargodoc.folders import FolderPlan, create_folders


class FolderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.destination = Path(self.temp.name)

    def plan(self, kind="export", start="001", end="003", year=2027):
        return FolderPlan(kind, start, end, self.destination, year)

    def test_export_padding_and_configurable_year(self):
        result = create_folders(self.plan())
        self.assertEqual(result.created, 3)
        self.assertEqual(sorted(p.name for p in self.destination.iterdir()),
                         ["RE-001-2027", "RE-002-2027", "RE-003-2027"])

    def test_existing_directory_and_file_conflict(self):
        (self.destination / "IMP-001").mkdir()
        conflict = self.destination / "IMP-002"
        conflict.write_text("keep me")
        result = create_folders(self.plan(kind="import"))
        self.assertEqual((result.created, result.existing, len(result.failed)), (1, 1, 1))
        self.assertEqual(conflict.read_text(), "keep me")
        again = create_folders(self.plan(kind="import"))
        self.assertEqual((again.created, again.existing, len(again.failed)), (0, 2, 1))

    def test_invalid_ranges_make_no_folders(self):
        for start, end in [("", "3"), ("-1", "3"), ("1.0", "3"), ("3", "1"),
                           ("1", "100001"), ("１２", "１３"), ("1" * 13, "2" * 13)]:
            with self.subTest(start=start, end=end), self.assertRaises(ValueError):
                self.plan(start=start, end=end)
        with self.assertRaises(ValueError):
            self.plan(year=99)
        self.assertEqual(list(self.destination.iterdir()), [])

    def test_missing_destination(self):
        with self.assertRaises(ValueError):
            FolderPlan("export", "1", "2", self.destination / "missing", 2026)


if __name__ == "__main__":
    unittest.main()
