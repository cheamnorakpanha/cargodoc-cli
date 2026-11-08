import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from cargodoc.cli import main


class CliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.destination = Path(self.temp.name)

    def invoke(self, *args):
        with contextlib.redirect_stdout(io.StringIO()):
            return main([*args, "--directory", str(self.destination)])

    def test_direct_dry_run_and_create(self):
        args = ("export", "--start", "009", "--end", "010", "--year", "2028")
        self.assertEqual(self.invoke(*args, "--dry-run"), 0)
        self.assertEqual(list(self.destination.iterdir()), [])
        self.assertEqual(self.invoke(*args), 0)
        self.assertTrue((self.destination / "RE-009-2028").is_dir())
        self.assertTrue((self.destination / "RE-010-2028").is_dir())

    def test_direct_errors_return_nonzero(self):
        self.assertEqual(self.invoke("import", "--start", "3", "--end", "1"), 2)
        (self.destination / "IMP-1").write_text("keep me")
        self.assertEqual(self.invoke("import", "--start", "1", "--end", "1"), 1)


if __name__ == "__main__":
    unittest.main()
