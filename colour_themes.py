"""Read the colour themes from Python. Standard library only.

    import colour_themes
    palette = colour_themes.palette("yozakura")          # {"bg": "#17121A", ...}
    paper = colour_themes.palette("yozakura", mode="light")
    today = colour_themes.theme_for_date(date.today())    # "umi" on a Wednesday
    desk = colour_themes.palette("choba")                 # an app theme: Shiwake's 帳場

The six weekday themes are in `themes`; themes that belong to one app are in
`app_themes`. palette() and theme() find both.

Copy this file and themes/tokens.json into a project, or read tokens.json directly.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

TOKENS = Path(__file__).resolve().parent / "themes" / "tokens.json"
MODES = ("dark", "light")
_DAYS = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")


def load(path: Path | str | None = None) -> dict:
    """The whole tokens file."""
    return json.loads(Path(path or TOKENS).read_text(encoding="utf-8"))


def theme_ids(path: Path | str | None = None, apps: bool = False) -> list[str]:
    """The ids of the six weekday themes, and with `apps=True` the app themes after them."""
    data = load(path)
    found = [theme["id"] for theme in data["themes"]]
    if apps:
        found += [theme["id"] for theme in data.get("app_themes", [])]
    return found


def app_theme_for(app: str, path: Path | str | None = None) -> str | None:
    """The id of an app's own theme ("shiwake" -> "choba"), or None if it has none."""
    for item in load(path).get("app_themes", []):
        if item["app"] == app:
            return item["id"]
    return None


def theme(theme_id: str, path: Path | str | None = None) -> dict:
    """One theme: its names, its weekday or app, and its dark and light palettes."""
    data = load(path)
    for item in data["themes"] + data.get("app_themes", []):
        if item["id"] == theme_id:
            return item
    raise KeyError("No colour theme named {!r}".format(theme_id))


def palette(theme_id: str, path: Path | str | None = None, mode: str = "dark") -> dict:
    """One palette of a theme, role name to colour. `mode` is "dark" or "light"."""
    if mode not in MODES:
        raise ValueError("mode must be 'dark' or 'light', not {!r}".format(mode))
    return dict(theme(theme_id, path)[mode])


def theme_for_date(day: date, base: str = "tsukiakari", path: Path | str | None = None) -> str:
    """The theme of a weekday. Sunday rests: it gives `base`, the owner's own choice."""
    chosen = load(path)["weekdays"].get(_DAYS[day.weekday()])
    return chosen or base
