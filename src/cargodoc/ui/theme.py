"""Shared colors, prompt styles, and terminal console."""
from prompt_toolkit.styles import Style
from rich.console import Console

console = Console(highlight=False)

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
