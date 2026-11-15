# Colour themes

One set of colours for my apps, slides and documents, so they look like they belong together and not like everything else.

Six dark themes, each named after a Japanese scene and each tied to a day of the week. Monday to Saturday take the element in the day's name (月 moon, 火 fire, 水 water, 木 wood) or its mood; Sunday rests.

![The six themes](preview/themes.svg)

| Day | Theme | Meaning | Colours | Why this day |
| --- | --- | --- | --- | --- |
| 月 Monday | 月明かり Tsukiakari | Moonlight | Navy and pale gold | 月曜 is the day of the moon |
| 火 Tuesday | 墨と朱 Sumi | Ink and vermilion | Warm charcoal and seal red | 火曜 is the day of fire |
| 水 Wednesday | 海 Umi | Deep sea | Blue-green black and aqua | 水曜 is the day of water |
| 木 Thursday | 竹林 Chikurin | Bamboo grove | Forest black and bamboo green | 木曜 is the day of wood |
| 金 Friday | 夜桜 Yozakura | Cherry blossom at night | Plum black and sakura pink | 花金, the flowery Friday night |
| 土 Saturday | 藤 Fuji | Wisteria | Violet black and wisteria purple | The quiet of the weekend |
| 日 Sunday | (rest) | | | No theme of its own: an app shows the base theme its owner chose |

## What is here

| Path | What it is |
| --- | --- |
| `themes/tokens.json` | **The source of truth.** Every theme, its names, its weekday and its colours by role. |
| `themes/themes.css` | The same colours as CSS variables (`--ct-bg`, `--ct-accent`, ...), one block per theme. Made by the build tool. |
| `colour_themes.py` | A small Python helper: `palette("umi")`, `theme_for_date(date.today())`. |
| `preview/index.html` | Open in a browser to see every theme on a small app window. |
| `icons/tsukiakari/` | The Tsukiakari app icon (moon on water): `icon.svg`, PNG sizes, `icon.ico`, one variant per theme, and the three concepts that were not chosen. |
| `tools/build.py` | Checks the themes and writes the CSS, the previews and the icon SVGs. |
| `tools/render_icons.py` | Makes the PNG files and the `.ico` from `icon.svg` (needs PyQt6). |

## The roles

Every theme has the same role names, so a design made with one theme works with all of them.

| Role | Use |
| --- | --- |
| `bg`, `side` | The background, and the sidebar a shade darker |
| `surf`, `surf2` | Cards and panels; raised or highlighted panels |
| `line`, `line_strong` | Hairlines; borders of inputs and controls |
| `text`, `text2`, `text3` | Body text; secondary text; labels and hints |
| `accent` | The theme's one accent: links, the active item, key numbers |
| `accent_soft`, `nav_on` | The accent at 14% and 12%, for soft fills |
| `btn`, `btn_ink` | The primary button and the text on it |
| `track` | The empty part of a meter |
| `good`, `app`, `script` | Success, and two more colours for charts and labels |

## Using it

**Python (PyQt apps).** Copy `themes/tokens.json` and `colour_themes.py` into the project.

```python
from datetime import date
import colour_themes

palette = colour_themes.palette("yozakura")              # {"bg": "#17121A", ...}
today = colour_themes.theme_for_date(date.today(), base="tsukiakari")
```

**Web pages.** Link `themes/themes.css` and set the theme on any element.

```html
<body data-theme="chikurin" style="background: var(--ct-bg); color: var(--ct-text)">
```

**Slides and documents.** Pick one theme for the whole piece. Use `bg` for the slide, `surf` for cards, `text` for words, and `accent` for the one thing each slide should make you look at. Use `good`, `app` and `script` only for data.

## Rules

- All text passes a contrast check: 4.5:1 or better for every text colour on the backgrounds it is used on, 7:1 for body text. `tools/build.py` refuses to write anything when a theme fails.
- One accent per theme. A second bright colour is for data only.
- Dark themes only for now. Light versions come when something needs them.

## Adding or changing a theme

1. Edit `themes/tokens.json`. A new theme needs every role.
2. Run `python tools/build.py`. Fix what it reports.
3. If the Tsukiakari icon's colours changed, run `python tools/render_icons.py`.
4. Open `preview/index.html` and look at it.
5. Commit everything, the made files included.
