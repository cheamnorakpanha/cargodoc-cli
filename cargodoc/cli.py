"""Interactive prompt and scriptable command-line entry point."""

import argparse
from datetime import date
from pathlib import Path
import sys

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.validation import Validator
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from .folders import FolderPlan, create_folders
from .ui import ACCENT, FRAME, SECONDARY, PROMPT_STYLE, command_prompt, toolbar, welcome

console = Console(highlight=False)
COMMANDS = ["/export", "/import", "/directory", "/help", "/clear", "/exit"]


def parser():
    root = argparse.ArgumentParser(prog="cargodoc", description="CargoDoc: prepare import and export folders. Run without arguments for the workspace.")
    root.add_argument("--version", action="version", version="cargodoc 0.1.0")
    tasks = root.add_subparsers(dest="command")
    for kind in ("export", "import"):
        task = tasks.add_parser(kind, help=f"Create {kind} folders")
        task.add_argument("--start", required=True, help="First number; leading zeros set padding (e.g. 001)")
        task.add_argument("--end", required=True, help="Last number, inclusive")
        if kind == "export":
            task.add_argument("--year", type=int, default=date.today().year, help="Four-digit year (default: current year)")
        task.add_argument("--directory", type=Path, default=Path.cwd(), help="Existing destination (default: current directory)")
        task.add_argument("--dry-run", action="store_true", help="Preview without creating folders")
    return root


def preview(plan):
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="dim")
    table.add_column()
    table.add_row("Destination", str(plan.destination))
    table.add_row("First", plan.name(int(plan.start)))
    table.add_row("Last", plan.name(int(plan.end)))
    table.add_row("Requested", str(plan.count))
    console.print(Panel(table, title=f"{plan.kind.title()} · review", title_align="left",
                        border_style=FRAME, box=box.ROUNDED, padding=(1, 1)))


def execute(plan):
    with console.status("Creating folders...", spinner_style=ACCENT):
        result = create_folders(plan)
    summary = Text.assemble((f"{result.created} created", f"bold {SECONDARY}"),
                            (f"   {result.existing} already existing", "dim"),
                            (f"   {len(result.failed)} failed", "red" if result.failed else "dim"))
    console.print(Panel(summary, title="Needs attention" if result.failed else "Task complete",
                        title_align="left", border_style="red" if result.failed else SECONDARY,
                        box=box.ROUNDED))
    for path, error in result.failed:
        console.print(f"{path.name}: {error}", style="red", markup=False)
    return 1 if result.failed else 0


def show_help():
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style=f"bold {ACCENT}")
    table.add_column()
    for command, description in (
        ("/export", "Create RE-001-YEAR folders"),
        ("/import", "Create IMP-001 folders"),
        ("/directory", "Change the destination for this session"),
        ("/help", "Show commands"),
        ("/clear", "Clear the screen and return to the welcome panel"),
        ("/exit", "Quit"),
    ):
        table.add_row(command, description)
    console.print(Panel(table, title="Commands", title_align="left", border_style=ACCENT))
    console.print("Tab completes commands. Up/Down recalls commands. Ctrl+C cancels; Ctrl+D exits.", style="dim")


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


def interactive():
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


def main(argv=None):
    arguments = parser()
    args = arguments.parse_args(argv)
    try:
        if args.command is None:
            return interactive()
        plan = FolderPlan(args.command, args.start, args.end, args.directory.expanduser().resolve(),
                          getattr(args, "year", date.today().year))
        preview(plan)
        if args.dry_run:
            console.print("Dry run: no folders created.", style="dim")
            return 0
        return execute(plan)
    except (ValueError, OSError) as error:
        console.print(str(error), style="red", markup=False)
        return 2
    except (KeyboardInterrupt, EOFError):
        console.print("Interrupted. Some folders may already have been created.", style="yellow")
        return 130
