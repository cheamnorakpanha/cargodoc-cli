"""Command-line argument parsing and task dispatch."""
import argparse
from datetime import date
from pathlib import Path

from .folders import FolderPlan, create_folders
from .interactive import interactive
from .ui.theme import ACCENT, console
from .ui.views import preview, show_result


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


def execute(plan):
    with console.status("Creating folders...", spinner_style=ACCENT):
        result = create_folders(plan)
    return show_result(result)


def main(argv=None):
    arguments = parser()
    args = arguments.parse_args(argv)
    try:
        if args.command is None:
            return interactive(execute)
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
