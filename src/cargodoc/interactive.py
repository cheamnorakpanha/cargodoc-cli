"""Persistent command session and guided task questions."""
from datetime import date
from pathlib import Path
import sys

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.validation import Validator
from rich.text import Text

from .folders import FolderPlan
from .ui.theme import ACCENT, PROMPT_STYLE, console
from .ui.views import command_prompt, toolbar, welcome, preview, show_help

COMMANDS = ["/export", "/import", "/directory", "/help", "/clear", "/exit"]


def ask_plan(session, kind, destination):
    console.print()
    console.print(Text(f"  {kind.title()} folders", style=f"bold {ACCENT}"))
    console.print("  Start with 001 for three-digit folder numbers. Ctrl+C cancels.\n", style="dim")
    digits = Validator.from_callable(
        lambda text: bool(text) and text.isascii() and text.isdecimal() and len(text) <= 12,
        error_message="Enter 1 to 12 digits (0-9).", move_cursor_to_end=True,
    )
    start = session.prompt("Starting number: ", validator=digits)
    end = session.prompt("Ending number:   ", validator=digits)
    year = date.today().year
    if kind == "export":
        year = int(session.prompt("Year:            ", default=str(year), validator=Validator.from_callable(
            lambda text: text.isascii() and text.isdecimal() and len(text) == 4 and int(text) >= 1000,
            error_message="Enter a four-digit year.",
        )))
    return FolderPlan(kind, start, end, destination, year)


def interactive(execute):
    """Run guided tasks using the same executor as direct commands."""
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        console.print("Interactive mode needs a terminal. Use cargodoc --help for direct commands.", style="red")
        return 2
    destination = Path.cwd()
    session = PromptSession(history=InMemoryHistory(), style=PROMPT_STYLE)
    # Keep task answers out of command history and completion.
    answers = PromptSession(style=PROMPT_STYLE)
    recent = "No tasks yet. Ready when you are."
    welcome(console, destination, recent)
    while True:
        try:
            command = session.prompt(command_prompt, completer=WordCompleter(COMMANDS),
                                     bottom_toolbar=toolbar).strip().lower()
            if command in {"/exit", "exit", "quit"}:
                console.print("See you next time.\n", style="dim")
                return 0
            if command in {"/help", "help", "?"}:
                show_help()
            elif command == "/clear":
                console.clear()
                welcome(console, destination, recent)
            elif command == "/directory":
                # prompt_toolkit retains validators; passing None to prompt()
                # does not reset one from an earlier question.
                answers.validator = None
                target = answers.prompt("Destination directory: ", default=str(destination))
                candidate = Path(target).expanduser().resolve()
                if not candidate.is_dir():
                    raise ValueError("Choose an existing directory.")
                destination = candidate
                console.print(f"Destination: {destination}", markup=False)
            elif command in {"/export", "/import"}:
                plan = ask_plan(answers, command[1:], destination)
                preview(plan)
                answers.validator = None
                answer = answers.prompt("Create these folders? [y/N]: ").strip().lower()
                if answer in {"y", "yes"}:
                    status = execute(plan)
                    recent = f"{plan.kind.title()} · {plan.count} requested · {'needs attention' if status else 'complete'}"
                else:
                    console.print("Cancelled.", style="dim")
            elif command:
                console.print("Unknown command. Type /help or press Tab.", style="yellow")
        except KeyboardInterrupt:
            console.print("Cancelled. Type /exit to quit.", style="dim")
        except EOFError:
            console.print("Goodbye.")
            return 0
        except (ValueError, OSError) as error:
            console.print(str(error), style="red", markup=False)
