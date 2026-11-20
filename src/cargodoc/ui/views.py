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
    framed = width >= 32
    content_width = width - 4 if framed else width
    unicode_borders = supports_blocks(console)
    panel_box = box.SQUARE if unicode_borders else box.ASCII

    masthead = Table.grid(expand=True)
    masthead.add_column(ratio=1, overflow="fold")
    masthead.add_column(justify="right", style=MUTED, overflow="fold")
    masthead.add_row(Text("DOCUMENT WORKSPACE", style=f"bold {ACCENT}"), "v0.1.0 / LOCAL")

    destination_panel = Panel(
        Text(str(destination), overflow="fold"),
        title=Text("Destination", style=f"bold {ACCENT}"),
        title_align="left", border_style=f"dim {ACCENT}", box=panel_box, padding=(0, 1),
    )
    actions = (
        ("01 / OUTBOUND", "/export", "Export folders", "RE-001-YEAR", ACCENT),
        ("02 / INBOUND", "/import", "Import folders", "IMP-001", "#6aafff"),
        ("03 / WORKSPACE", "/directory", "Switch destination", "Choose a folder", VIOLET),
        ("04 / EXCEPTION", "/skipped", "Skip a range", "IMP-720 - skipped", SECONDARY),
    )
    if content_width >= 92:
        tasks = Table.grid(expand=True, padding=(0, 1))
        for _ in actions:
            tasks.add_column(ratio=1)
        tasks.add_row(*[
            Panel(
                Group(Text(command, style=f"bold {color}"), Text(label), Text(example, style=MUTED)),
                title=Text(title, style=color), title_align="left", border_style=f"dim {color}",
                box=panel_box, padding=(1, 1),
            )
            for title, command, label, example, color in actions
        ])
    else:
        tasks = Table.grid(padding=(0, 1))
        tasks.add_column(style=MUTED)
        tasks.add_column(no_wrap=True)
        tasks.add_column(overflow="fold")
        for title, command, label, _, color in actions:
            tasks.add_row(title[:2], Text(command, style=f"bold {color}"), label)

    workspace = Group(
        wordmark(console, content_width),
        Text(),
        masthead,
        Text("Prepare the paperwork. Keep cargo moving.", style=MUTED),
        Text(),
        destination_panel,
        Text(),
        tasks,
        Text(),
        Rule(style=FRAME, characters="─" if unicode_borders else "-"),
        Text.assemble(("SESSION  ", f"bold {VIOLET}"), (recent, MUTED)),
        Text("Type / to start a task. Tab explores commands.", style=MUTED),
    )
    if framed:
        workspace = Panel(workspace, box=box.DOUBLE_EDGE if unicode_borders else box.ASCII,
                          border_style=f"dim {VIOLET}", padding=(1, 1))

    console.print()
    console.print(workspace, width=width)
    console.print()


def preview(plan):
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="dim")
    table.add_column()
    table.add_row("Destination", str(plan.destination))
    table.add_row("First", plan.name(int(plan.start)))
    table.add_row("Last", plan.name(int(plan.end)))
    table.add_row("Requested", str(plan.count))
    task = "skipped folders" if plan.skipped else "review"
    title = f"{plan.kind.title()} · {task}"
    console.print(Panel(table, title=title, title_align="left",
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
        ("/skipped", "Create skipped import or export folders for a range"),
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
