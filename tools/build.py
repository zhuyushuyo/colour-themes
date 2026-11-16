#!/usr/bin/env python3
"""Check the themes and write everything that is made from them.

    python tools/build.py

Reads themes/tokens.json (the one source of truth), checks text contrast, and
writes themes/themes.css, preview/themes.svg, preview/themes-light.svg,
preview/index.html and the icon SVGs. It needs only Python's standard library.
It stops with an error, and writes nothing, when a theme fails the contrast
check in either mode (dark or light).
"""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKENS = ROOT / "themes" / "tokens.json"

# (foreground, background, least contrast ratio). 4.5:1 is the rule for all text.
CHECKS = [
    ("text", "bg", 7.0), ("text", "surf2", 7.0), ("text2", "surf2", 4.5), ("text3", "surf2", 4.5),
    ("text3", "side", 4.5), ("accent", "bg", 4.5), ("accent", "surf2", 4.5), ("btn_ink", "btn", 7.0),
    ("good", "side", 4.5),
]
# Light palettes are also used on paper-white slides and cards, so more is checked there.
LIGHT_CHECKS = CHECKS + [
    ("text2", "side", 4.5), ("accent", "side", 4.5), ("accent", "surf", 4.5),
    ("good", "bg", 4.5), ("app", "bg", 4.5), ("app", "side", 4.5),
    ("script", "bg", 4.5), ("script", "side", 4.5),
]
MODES = ("dark", "light")
MODE_CHECKS = {"dark": CHECKS, "light": LIGHT_CHECKS}
SOLID = ("bg", "side", "surf", "surf2", "line", "line_strong", "text", "text2", "text3", "accent",
         "btn", "btn_ink", "track", "good", "app", "script")
WEEKDAY_JA = {"mon": "月", "tue": "火", "wed": "水", "thu": "木", "fri": "金", "sat": "土"}
WEEKDAY_EN = {"mon": "Monday", "tue": "Tuesday", "wed": "Wednesday", "thu": "Thursday",
              "fri": "Friday", "sat": "Saturday"}


def _channel(value: int) -> float:
    c = value / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(colour: str) -> float:
    r, g, b = (int(colour[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * _channel(r) + 0.7152 * _channel(g) + 0.0722 * _channel(b)


def contrast(a: str, b: str) -> float:
    high, low = sorted((luminance(a), luminance(b)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def check(themes: list[dict]) -> list[str]:
    problems = []
    for theme in themes:
        for mode in MODES:
            name = "{} ({})".format(theme["id"], mode)
            palette = theme.get(mode)
            if not isinstance(palette, dict):
                problems.append("{}: the palette is missing".format(name))
                continue
            bad = False
            for key in SOLID:
                value = palette.get(key, "")
                if not (isinstance(value, str) and len(value) == 7 and value.startswith("#")):
                    problems.append("{}: {} must be a #RRGGBB colour".format(name, key))
                    bad = True
            for key in ("accent_soft", "nav_on"):
                if not str(palette.get(key, "")).startswith("rgba("):
                    problems.append("{}: {} must be an rgba() colour".format(name, key))
            if bad:
                continue
            for fg, bg, least in MODE_CHECKS[mode]:
                ratio = contrast(palette[fg], palette[bg])
                if ratio < least:
                    problems.append("{}: {} on {} is {:.1f}:1, needs {}:1".format(
                        name, fg, bg, ratio, least))
            darker = luminance(palette["bg"]) < luminance(palette["text"])
            if darker != (mode == "dark"):
                problems.append("{}: the background and the text are the wrong way round".format(name))
    return problems


# ------------------------------------------------------------------ CSS

def write_css(themes: list[dict]) -> None:
    lines = [
        "/* Made by tools/build.py from themes/tokens.json. Do not edit by hand. */",
        "/* Dark is the default. Add data-mode=\"light\" to the same element for the light palette. */",
        "",
    ]
    for mode in MODES:
        for index, theme in enumerate(themes):
            selector = '[data-theme="{}"]'.format(theme["id"])
            if mode == "light":
                selector += '[data-mode="light"]'
            if index == 0:
                first = ':root[data-mode="light"]' if mode == "light" else ":root"
                selector = first + ", " + selector
            lines.append("/* {} {} ({}), {} */".format(
                theme["ja"], theme["reading"], theme["meaning"], mode))
            lines.append(selector + " {")
            for key, value in theme[mode].items():
                lines.append("  --ct-{}: {};".format(key.replace("_", "-"), value))
            lines.append("}")
            lines.append("")
    (ROOT / "themes" / "themes.css").write_text("\n".join(lines), encoding="utf-8")


# ------------------------------------------------------------------ icons

def icon_water(bg: str, fg: str) -> str:
    """The Tsukiakari icon: a crescent above its reflection on water."""
    return (
        '<rect width="256" height="256" rx="58" fill="{bg}"/>\n'
        '<mask id="moon" maskUnits="userSpaceOnUse" x="0" y="0" width="256" height="256">'
        '<rect width="256" height="256" fill="#000"/><circle cx="124" cy="96" r="58" fill="#fff"/>'
        '<circle cx="152" cy="78" r="50" fill="#000"/></mask>\n'
        '<rect width="256" height="256" fill="{fg}" mask="url(#moon)"/>\n'
        '<rect x="60" y="176" width="136" height="12" rx="6" fill="{fg}"/>\n'
        '<rect x="82" y="200" width="92" height="12" rx="6" fill="{fg}" opacity="0.7"/>\n'
        '<rect x="104" y="224" width="48" height="12" rx="6" fill="{fg}" opacity="0.45"/>'
    ).format(bg=bg, fg=fg)


def icon_bubble(bg: str, fg: str) -> str:
    return (
        '<rect width="256" height="256" rx="58" fill="{bg}"/>\n'
        '<path d="M76 52h104a40 40 0 0 1 40 40v64a40 40 0 0 1-40 40h-62l-44 34a6 6 0 0 1-9.6-5.4L68 195'
        'a40 40 0 0 1-32-39V92a40 40 0 0 1 40-40z" fill="{fg}"/>\n'
        '<mask id="moon" maskUnits="userSpaceOnUse" x="0" y="0" width="256" height="256">'
        '<rect width="256" height="256" fill="#000"/><circle cx="124" cy="124" r="42" fill="#fff"/>'
        '<circle cx="144" cy="110" r="36" fill="#000"/></mask>\n'
        '<rect width="256" height="256" fill="{bg}" mask="url(#moon)"/>'
    ).format(bg=bg, fg=fg)


def icon_window(bg: str, fg: str) -> str:
    return (
        '<rect width="256" height="256" rx="58" fill="{bg}"/>\n'
        '<circle cx="128" cy="128" r="82" fill="none" stroke="{fg}" stroke-width="14"/>\n'
        '<circle cx="154" cy="100" r="24" fill="{fg}"/>\n'
        '<path d="M54 160h148" stroke="{fg}" stroke-width="12" stroke-linecap="round"/>\n'
        '<path d="M88 184h80" stroke="{fg}" stroke-width="10" stroke-linecap="round" opacity="0.6"/>'
    ).format(bg=bg, fg=fg)


def icon_character(bg: str, fg: str) -> str:
    return (
        '<rect width="256" height="256" rx="58" fill="{bg}"/>\n'
        '<g fill="none" stroke="{fg}" stroke-width="20" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M88 56v92c0 30-10 46-30 56"/><path d="M88 56h84v130c0 12-8 18-22 18"/>'
        '<path d="M88 102h84"/><path d="M88 146h84"/></g>'
    ).format(bg=bg, fg=fg)


def svg_file(inner: str, title: str) -> str:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256" '
        'role="img" aria-label="{title}">\n<title>{title}</title>\n{inner}\n</svg>\n'
    ).format(title=html.escape(title), inner=inner)


def write_icons(themes: list[dict]) -> None:
    folder = ROOT / "icons" / "tsukiakari"
    by_id = {theme["id"]: theme["dark"] for theme in themes}
    base = by_id["tsukiakari"]
    # The app icon is fixed: the moon on water in the 月明かり colours.
    (folder / "icon.svg").write_text(
        svg_file(icon_water(base["bg"], base["accent"]), "Tsukiakari"), encoding="utf-8")
    for theme in themes:
        palette = theme["dark"]
        (folder / "icon-{}.svg".format(theme["id"])).write_text(
            svg_file(icon_water(palette["bg"], palette["accent"]),
                     "Tsukiakari, {}".format(theme["reading"])), encoding="utf-8")
    concepts = (("b-moon-bubble", icon_bubble), ("c-round-window", icon_window),
                ("d-character", icon_character))
    for name, draw in concepts:
        (folder / "concepts" / (name + ".svg")).write_text(
            svg_file(draw(base["bg"], base["accent"]), "Tsukiakari concept " + name), encoding="utf-8")


# ------------------------------------------------------------------ previews

def write_swatch_sheet(themes: list[dict], mode: str = "dark") -> None:
    """One SVG that GitHub shows in the README: a row per theme, for one mode."""
    row_h, width = 132, 980
    height = 24 + row_h * len(themes)
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        'role="img" aria-label="The six {mode} colour themes" '
        'font-family="\'Hiragino Sans\', \'Yu Gothic UI\', \'Noto Sans JP\', system-ui, sans-serif">'
        .format(w=width, h=height, mode=mode),
        '<rect width="{w}" height="{h}" fill="{c}"/>'.format(
            w=width, h=height, c="#101114" if mode == "dark" else "#E4E4E6"),
    ]
    shown = (("bg", "bg"), ("surf", "surf"), ("surf2", "surf2"), ("line", "line"),
             ("text", "text"), ("text2", "text2"), ("accent", "accent"), ("good", "good"),
             ("app", "app"), ("script", "script"))
    for index, theme in enumerate(themes):
        p = theme[mode]
        y = 12 + index * row_h
        parts.append('<g transform="translate(12 {y})">'.format(y=y))
        parts.append('<rect width="{w}" height="{h}" rx="14" fill="{bg}" stroke="{line}"/>'.format(
            w=width - 24, h=row_h - 12, bg=p["bg"], line=p["line"]))
        parts.append('<text x="22" y="42" font-size="24" font-weight="700" fill="{c}">{t}</text>'.format(
            c=p["text"], t=html.escape(theme["ja"])))
        parts.append('<text x="22" y="68" font-size="14" font-weight="600" fill="{c}">{t}</text>'.format(
            c=p["accent"], t=html.escape(theme["reading"])))
        parts.append('<text x="22" y="92" font-size="12" fill="{c}">{t}</text>'.format(
            c=p["text2"], t=html.escape("{} · {}曜 {}".format(
                theme["meaning"], WEEKDAY_JA[theme["weekday"]], WEEKDAY_EN[theme["weekday"]]))))
        for n, (key, label) in enumerate(shown):
            x = 250 + n * 70
            parts.append('<rect x="{x}" y="22" width="58" height="40" rx="8" fill="{c}" stroke="{s}"/>'
                         .format(x=x, c=p[key], s=p["line_strong"]))
            parts.append('<text x="{x}" y="80" font-size="11" fill="{c}">{t}</text>'.format(
                x=x, c=p["text2"], t=label))
            parts.append('<text x="{x}" y="96" font-size="10.5" fill="{c}">{t}</text>'.format(
                x=x, c=p["text3"], t=p[key]))
        parts.append("</g>")
    parts.append("</svg>")
    name = "themes.svg" if mode == "dark" else "themes-{}.svg".format(mode)
    (ROOT / "preview" / name).write_text("\n".join(parts) + "\n", encoding="utf-8")


def write_preview_page(themes: list[dict]) -> None:
    """A page to open in a browser: every theme on a small app window, dark then light."""
    cards = []
    for mode, theme in [(m, t) for t in themes for m in MODES]:
        p = theme[mode]
        nav = "".join(
            '<div class="nav{on}">{name}</div>'.format(on=" on" if name == "チャット" else "", name=name)
            for name in ("ホーム", "チャット", "タスク", "ビルド", "使用量", "設定"))
        chips = "".join(
            '<span class="chip"><i style="background:{c}"></i>{k} {c}</span>'.format(k=key, c=p[key])
            for key in ("bg", "surf2", "line", "text", "accent", "good"))
        cards.append(
            '<section class="card" data-theme="{id}" data-mode="{mode}">'
            '<aside><div class="brand"><b>月明かり</b><small>Tsukiakari</small></div>{nav}</aside>'
            '<main><h2>{ja} <em>{reading} · {mode}</em></h2>'
            '<p class="about">{meaning}. {description} {day}曜 ({day_en}).</p>'
            '<div class="you"><small>あなた</small>来週の勉強会の案内文を、3行くらいで下書きしてください。</div>'
            '<div class="claude"><small>Claude</small>下書きです。日時は11月20日（金）15:00〜16:00です。 '
            '<a href="#">全文を見る</a></div>'
            '<div class="row"><span class="field">メッセージを入力</span><button type="button">送信</button></div>'
            '<div class="chips">{chips}</div></main></section>'.format(
                id=theme["id"], mode=mode, nav=nav, ja=html.escape(theme["ja"]),
                reading=theme["reading"], meaning=html.escape(theme["meaning"]),
                description=html.escape(
                    theme["description"] if mode == "dark" else theme["light_description"]),
                day=WEEKDAY_JA[theme["weekday"]], day_en=WEEKDAY_EN[theme["weekday"]], chips=chips))
    css = (ROOT / "themes" / "themes.css").read_text(encoding="utf-8")
    page = """<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Colour themes</title>
<style>
{css}
body {{ margin: 0; padding: 24px; background: #101114; color: #E9EAEE;
  font-family: 'Hiragino Sans', 'Yu Gothic UI', 'Noto Sans JP', system-ui, sans-serif; }}
h1 {{ font-size: 22px; margin: 0 0 16px; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(560px, 1fr)); gap: 20px; }}
.card {{ display: flex; min-height: 380px; border-radius: 14px; overflow: hidden; font-size: 13px;
  line-height: 1.5; background: var(--ct-bg); color: var(--ct-text); border: 1px solid var(--ct-line); }}
aside {{ width: 150px; flex: none; background: var(--ct-side); border-right: 1px solid var(--ct-line);
  padding: 16px 12px; display: flex; flex-direction: column; gap: 3px; }}
.brand {{ display: flex; flex-direction: column; padding: 0 8px 12px; }}
.brand small {{ color: var(--ct-text3); font-size: 10.5px; }}
.nav {{ padding: 5px 10px; border-radius: 7px; color: var(--ct-text2); }}
.nav.on {{ background: var(--ct-nav-on); color: var(--ct-text); font-weight: 600; }}
main {{ flex: 1; min-width: 0; padding: 18px 20px; display: flex; flex-direction: column; gap: 11px; }}
h2 {{ margin: 0; font-size: 20px; }}
h2 em {{ font-style: normal; font-size: 13px; color: var(--ct-accent); font-weight: 600; }}
.about {{ margin: 0; color: var(--ct-text2); font-size: 11.5px; }}
.you, .claude {{ border: 1px solid var(--ct-line); border-radius: 11px; padding: 10px 13px; }}
.you {{ background: var(--ct-surf2); }}
.claude {{ background: var(--ct-surf); }}
.you small, .claude small {{ display: block; color: var(--ct-text3); font-weight: 600; font-size: 10.5px; }}
.card a {{ color: var(--ct-accent); }}
.row {{ display: flex; gap: 10px; }}
.field {{ flex: 1; display: flex; align-items: center; min-height: 44px; padding: 0 12px;
  border: 1px solid var(--ct-line-strong); border-radius: 10px; background: var(--ct-surf);
  color: var(--ct-text3); font-size: 12px; }}
button {{ min-width: 84px; min-height: 44px; border: 0; border-radius: 10px; background: var(--ct-btn);
  color: var(--ct-btn-ink); font: inherit; font-weight: 700; }}
.chips {{ margin-top: auto; display: flex; flex-wrap: wrap; gap: 6px 12px; font-size: 10.5px;
  color: var(--ct-text3); }}
.chip i {{ display: inline-block; width: 12px; height: 12px; border-radius: 3px; margin-right: 5px;
  vertical-align: -2px; border: 1px solid var(--ct-line-strong); }}
</style>
</head>
<body>
<h1>Colour themes</h1>
<div class="grid">
{cards}
</div>
</body>
</html>
""".format(css=css, cards="\n".join(cards))
    (ROOT / "preview" / "index.html").write_text(page, encoding="utf-8")


def main() -> int:
    data = json.loads(TOKENS.read_text(encoding="utf-8"))
    themes = data["themes"]
    problems = check(themes)
    ids = [theme["id"] for theme in themes]
    for day, theme_id in data["weekdays"].items():
        if theme_id is not None and theme_id not in ids:
            problems.append("weekdays: {} names an unknown theme {}".format(day, theme_id))
    if problems:
        print("Not written. Fix these first:")
        for line in problems:
            print("  " + line)
        return 1
    write_css(themes)
    write_icons(themes)
    for mode in MODES:
        write_swatch_sheet(themes, mode)
    write_preview_page(themes)
    print("{} themes pass the contrast check in dark and light. Files written.".format(len(themes)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
