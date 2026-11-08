"""Responsive CargoDoc pixel wordmark."""
from rich.text import Text

from .theme import ACCENT, VIOLET

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
