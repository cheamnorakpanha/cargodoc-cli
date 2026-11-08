"""Welcome screen, prompts, task previews, and result presentation."""
from pathlib import Path
from shutil import get_terminal_size

from prompt_toolkit.formatted_text import FormattedText
from rich import box
from rich.console import Group
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from .banner import supports_blocks, wordmark
from .theme import ACCENT, VIOLET, SECONDARY, MUTED, FRAME, console

def welcome(console, destination: Path, recent="No tasks yet. Ready when you are."):
    width = min(console.width, 112)
    rule = "─" if supports_blocks(console) else "-"
    console.print()
    console.print(wordmark(console))
    console.print()
    masthead = Table.grid(expand=True)
    masthead.add_column(ratio=1)
    masthead.add_column(justify="right", style=MUTED)
    masthead.add_row(Text("DOCUMENT WORKSPACE", style=f"bold {ACCENT}"), "v0.1.0 / LOCAL")
    console.print(masthead, width=width)
    console.print(Text("Prepare the paperwork. Keep cargo moving.", style=MUTED))
    console.print()

    destination_text = Text(str(destination), overflow="fold")
    console.print(Panel(destination_text, title=Text(" Destination ", style=ACCENT),
                        title_align="left", border_style=FRAME, box=box.ROUNDED,
                        padding=(0, 2)), width=width)
    console.print()
    actions = (
        ("01 / OUTBOUND", "/export", "Export folders", "RE-001-YEAR", ACCENT),
        ("02 / INBOUND", "/import", "Import folders", "IMP-001", "#6aafff"),
        ("03 / WORKSPACE", "/directory", "Switch destination", "Choose a folder", VIOLET),
    )
    if width >= 88:
        cards = Table.grid(expand=True, padding=(0, 1))
        for _ in actions:
            cards.add_column(ratio=1)
        cards.add_row(*[
            Panel(Group(Text(command, style=f"bold {color}"), Text(label), Text(example, style=MUTED)),
                  title=Text(title, style=color), title_align="left", border_style=FRAME,
                  box=box.ROUNDED, padding=(1, 2))
            for title, command, label, example, color in actions
        ])
        console.print(cards, width=width)
    else:
        tasks = Table.grid(padding=(0, 2))
        tasks.add_column(style=MUTED)
        tasks.add_column()
        tasks.add_column()
        for title, command, label, _, color in actions:
            tasks.add_row(title[:2], Text(command, style=f"bold {color}"), label)
        console.print(tasks, width=width)
    console.print()
    console.print(Rule(style=FRAME, characters=rule), width=width)
    console.print(Text.assemble(("SESSION  ", f"bold {VIOLET}"), (recent, MUTED)), width=width)
    console.print(Text("Type / to start a task. Tab explores commands.\n", style=MUTED))


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


def show_result(result):
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


def command_prompt():
    width = max(1, get_terminal_size().columns - 1)
    label = "  CARGODOC "
    return FormattedText([("class:brand", label[:width]),
                          ("class:frame", "─" * max(0, width - len(label)) + "\n"),
                          ("class:prompt", "  > ")])


def toolbar():
    width = max(1, get_terminal_size().columns - 1)
    hint = "  Tab explore    ↑↓ history    Ctrl+C cancel    /help commands    /exit quit"
    if width < 65:
        hint = "  Tab explore · /help · /exit"
    return FormattedText([("class:frame", "─" * width + "\n"), ("class:hint", hint[:width])])
