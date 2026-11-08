"""CargoDoc's responsive cyan-to-violet terminal identity."""

from pathlib import Path
from shutil import get_terminal_size

from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.styles import Style
from rich import box
from rich.console import Group
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

ACCENT = "#35d9f5"
VIOLET = "#9270ff"
SECONDARY = "#67e8c0"
MUTED = "#94a3b8"
FRAME = "#46516c"
PROMPT_STYLE = Style.from_dict({
    "prompt": f"bold {ACCENT}",
    "brand": f"bold {VIOLET}",
    "frame": FRAME,
    "hint": MUTED,
    "bottom-toolbar": "noreverse",
    "completion-menu.completion": "bg:#191d30 #e2e8f0",
    "completion-menu.completion.current": f"bg:{ACCENT} #101320 bold",
    "completion-menu.meta.completion": "bg:#191d30 #94a3b8",
    "completion-menu.meta.completion.current": f"bg:{ACCENT} #101320",
    "validation-toolbar": "bg:#191d30 #fda4af",
})

# Small native terminal glyphs keep the banner sharp at every font size.
GLYPHS = {
    "C": ("01111", "11000", "11000", "11000", "11000", "11000", "01111"),
    "A": ("01110", "11011", "11011", "11111", "11011", "11011", "11011"),
    "R": ("11110", "11011", "11011", "11110", "11100", "11010", "11011"),
    "G": ("01111", "11000", "11000", "11011", "11011", "11011", "01111"),
    "O": ("01110", "11011", "11011", "11011", "11011", "11011", "01110"),
    "D": ("11110", "11011", "11011", "11011", "11011", "11011", "11110"),
}


def gradient(position):
    """Interpolate cyan through blue to violet across the wordmark."""
    start, end = (53, 217, 245), (145, 91, 255)
    rgb = [round(a + (b - a) * position) for a, b in zip(start, end)]
    return "#" + "".join(f"{channel:02x}" for channel in rgb)


def supports_blocks(console):
    try:
        "█░─".encode(console.encoding)
        return True
    except UnicodeEncodeError:
        return False


def wordmark(console):
    if console.width < 52 or not supports_blocks(console):
        return Text.assemble(("CARGO", f"bold {ACCENT}"), ("DOC", f"bold {VIOLET}"))
    scale = 2 if console.width >= 100 else 1
    rows = ["0".join(GLYPHS[letter][row] for letter in "CARGODOC") for row in range(7)]
    pixels = {(x * scale + step, y) for y, row in enumerate(rows)
              for x, value in enumerate(row) if value == "1" for step in range(scale)}
    width = len(rows[0]) * scale + 2
    result = Text()
    for y in range(9):
        for x in range(width):
            if (x, y) in pixels:
                result.append("█", style=gradient(x / (width - 1)))
            elif (x - 1, y - 1) in pixels or (x - 2, y - 2) in pixels:
                result.append("░", style="#3c375f")
            else:
                result.append(" ")
        if y < 8:
            result.append("\n")
    return result


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
