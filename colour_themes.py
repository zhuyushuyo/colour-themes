"""Read the colour themes from Python. Standard library only.

    import colour_themes
    palette = colour_themes.palette("yozakura")          # {"bg": "#17121A", ...}
    today = colour_themes.theme_for_date(date.today())    # "umi" on a Wednesday

Copy this file and themes/tokens.json into a project, or read tokens.json directly.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

TOKENS = Path(__file__).resolve().parent / "themes" / "tokens.json"
_DAYS = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")


def load(path: Path | str | None = None) -> dict:
    """The whole tokens file."""
    return json.loads(Path(path or TOKENS).read_text(encoding="utf-8"))


def theme_ids(path: Path | str | None = None) -> list[str]:
    return [theme["id"] for theme in load(path)["themes"]]


def theme(theme_id: str, path: Path | str | None = None) -> dict:
    """One theme: its names, its weekday and its dark palette."""
    for item in load(path)["themes"]:
        if item["id"] == theme_id:
            return item
    raise KeyError("No colour theme named {!r}".format(theme_id))


def palette(theme_id: str, path: Path | str | None = None) -> dict:
    """The dark palette of one theme, role name to colour."""
    return dict(theme(theme_id, path)["dark"])


def theme_for_date(day: date, base: str = "tsukiakari", path: Path | str | None = None) -> str:
    """The theme of a weekday. Sunday rests: it gives `base`, the owner's own choice."""
    chosen = load(path)["weekdays"].get(_DAYS[day.weekday()])
    return chosen or base
