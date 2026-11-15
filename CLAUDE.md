# Colour themes: notes for Claude

This repository holds the owner's own colours. When you make anything for the owner that has a look (an app screen, slides, a document, a chart, a web page), take its colours from here instead of inventing a palette.

## How to use it

- Read `themes/tokens.json`. It is the source of truth: six dark themes, each with the same role names (`bg`, `surf`, `text`, `accent`, ...).
- Pick one theme for the whole piece. If the owner did not name one, use the theme of the day it is made (`weekdays` in the tokens file; on Sunday use 月明かり Tsukiakari), and say which one you used.
- Use the roles as the README describes. One accent per piece; `good`, `app` and `script` are for data.
- Use the Japanese name with its reading when you mention a theme: 夜桜 Yozakura.
- Only dark themes exist. If a piece needs a light background, say so and ask before making a light version; do not make one up silently.

## Changing this repository

- Change colours only in `themes/tokens.json`, then run `python tools/build.py`. It checks contrast and writes `themes/themes.css`, the previews and the icon SVGs. Never edit the made files by hand.
- A theme that fails the contrast check is not committed.
- Keep docs and comments in plain English. Theme names keep their Japanese form.
- This repository is public: no personal data, no keys, nothing from the owner's research.
