# Colour themes: notes for Claude

This repository holds the owner's own colours. When you make anything for the owner that has a look (an app screen, slides, a document, a chart, a web page), take its colours from here instead of inventing a palette.

## How to use it

- Read `themes/tokens.json`. It is the source of truth: six weekday themes (`themes`), each with a `dark` and a `light` palette that share the same role names (`bg`, `surf`, `text`, `accent`, ...), and app themes (`app_themes`) made the same way.
- Pick one theme for the whole piece. If the owner did not name one, use the theme of the day it is made (`weekdays` in the tokens file; on Sunday use 月明かり Tsukiakari), and say which one you used.
- An app theme belongs to one app (帳場 Chōba is Shiwake's). Use it only for that app, or for slides and pages about it. Never use one as the theme of the day.
- Use the roles as the README describes. One accent per piece; `good`, `app` and `script` are for data. `warn` marks what a person must check; like `good` it is a state, always beside a word or a mark, never a second accent.
- Use the Japanese name with its reading when you mention a theme: 夜桜 Yozakura.
- Pick one mode for the whole piece. If the owner did not say, use dark for apps and for slides shown on a screen, and light for documents, print and anything read in a bright room. Say which one you used.
- Never mix the two palettes, and never use a dark-mode accent on a light background: it cannot be read there. Take the accent from the light palette.
- App icons are in `icons/<app>/`. Use the files; do not redraw them.

## Changing this repository

- Change colours only in `themes/tokens.json`, then run `python tools/build.py`. It checks contrast in both modes and writes `themes/themes.css`, the previews and the icon SVGs. Never edit the made files by hand.
- A theme that fails the contrast check is not committed.
- Keep docs and comments in plain English. Theme names keep their Japanese form.
- This repository is public: no personal data, no keys, nothing from the owner's research.
