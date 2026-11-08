import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from prompt_toolkit import PromptSession
from prompt_toolkit.document import Document
from prompt_toolkit.input import DummyInput
from prompt_toolkit.output import DummyOutput

from cargodoc.cli import main


class InteractiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.destination = Path(self.temp.name)

    def run_session(self, commands, answers, real_answers=False):
        command_session = Mock()
        command_session.prompt.side_effect = commands
        if real_answers:
            # Exercise real PromptSession validator persistence without waiting
            # for terminal input. Only replace its event-loop runner.
            answer_session = PromptSession(input=DummyInput(), output=DummyOutput())
            responses = iter(answers)

            def accept_answer(**kwargs):
                value = next(responses)
                if answer_session.validator is not None:
                    answer_session.validator.validate(Document(value))
                return value

            answer_session.app.run = Mock(side_effect=accept_answer)
        else:
            answer_session = Mock()
            answer_session.prompt.side_effect = answers
        with contextlib.redirect_stdout(io.StringIO()), \
             patch("cargodoc.interactive.sys.stdin.isatty", return_value=True), \
             patch("cargodoc.interactive.sys.stdout.isatty", return_value=True), \
             patch("cargodoc.interactive.Path.cwd", return_value=self.destination), \
             patch("cargodoc.interactive.PromptSession", side_effect=[command_session, answer_session]):
            return main([])

    def test_interactive_create_then_return_to_prompt(self):
        self.assertEqual(self.run_session(["/export", "/exit"], ["001", "002", "2029", "y"]), 0)
        self.assertTrue((self.destination / "RE-001-2029").is_dir())
        self.assertTrue((self.destination / "RE-002-2029").is_dir())

    def test_interactive_cancel_and_interrupt(self):
        self.assertEqual(self.run_session(["/import", "/import", "/exit"],
                                         ["001", "002", "", KeyboardInterrupt()]), 0)
        self.assertEqual(list(self.destination.iterdir()), [])

    def test_interactive_destination_change(self):
        target = self.destination / "client folder"
        target.mkdir()
        self.assertEqual(self.run_session(["/directory", "/import", "/exit"],
                                         [str(target), "01", "01", "yes"]), 0)
        self.assertTrue((target / "IMP-01").is_dir())

    def test_confirmation_does_not_reuse_numeric_or_year_validator(self):
        for kind in ("export", "import"):
            for confirmation in ("y", "N", ""):
                with self.subTest(kind=kind, confirmation=confirmation):
                    answers = ["001", "001"]
                    if kind == "export":
                        answers.append("2029")
                    answers.append(confirmation)
                    with patch("cargodoc.cli.execute", return_value=0) as execute:
                        self.assertEqual(self.run_session([f"/{kind}", "/exit"], answers,
                                                          real_answers=True), 0)
                    self.assertEqual(execute.call_count, int(confirmation == "y"))

    def test_directory_does_not_reuse_validator_after_export(self):
        target = self.destination / "client folder"
        target.mkdir()
        self.assertEqual(self.run_session(["/export", "/directory", "/exit"],
                                         ["001", "001", "2029", "N", str(target)],
                                         real_answers=True), 0)


if __name__ == "__main__":
    unittest.main()
