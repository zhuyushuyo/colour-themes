#!/usr/bin/env python3
"""Make the PNG files and the Windows .ico from each app's icons/<app>/icon.svg.

    python tools/render_icons.py            # every app
    python tools/render_icons.py shiwake    # one app

Needs PyQt6 (the apps already use it). Run tools/build.py first: it writes the
Tsukiakari SVGs. Other apps' icon.svg files are drawn by hand and kept as they are.
"""

from __future__ import annotations

import os
import struct
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtCore import QBuffer, QByteArray, QIODevice, QRectF, Qt  # noqa: E402
from PyQt6.QtGui import QGuiApplication, QImage, QPainter  # noqa: E402
from PyQt6.QtSvg import QSvgRenderer  # noqa: E402

ICONS = Path(__file__).resolve().parents[1] / "icons"
PNG_SIZES = (16, 24, 32, 48, 64, 128, 256, 512, 1024)
ICO_SIZES = (16, 24, 32, 48, 64, 128, 256)


def render(renderer: QSvgRenderer, size: int) -> bytes:
    image = QImage(size, size, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    renderer.render(painter, QRectF(0, 0, size, size))
    painter.end()
    data = QByteArray()
    buffer = QBuffer(data)
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    image.save(buffer, "PNG")
    buffer.close()
    return bytes(data)


def write_ico(path: Path, images: dict[int, bytes]) -> None:
    """A Windows icon file holding one PNG per size."""
    sizes = sorted(images)
    header = struct.pack("<HHH", 0, 1, len(sizes))
    entries, blobs = b"", b""
    offset = len(header) + 16 * len(sizes)
    for size in sizes:
        blob = images[size]
        entries += struct.pack("<BBBBHHII", size % 256, size % 256, 0, 0, 1, 32, len(blob), offset)
        blobs += blob
        offset += len(blob)
    path.write_bytes(header + entries + blobs)


def render_app(folder: Path) -> bool:
    """Write png/icon-<size>.png and icon.ico from folder/icon.svg."""
    renderer = QSvgRenderer(str(folder / "icon.svg"))
    if not renderer.isValid():
        print("icons/{}/icon.svg is missing or not valid.".format(folder.name))
        return False
    png = folder / "png"
    png.mkdir(exist_ok=True)
    images = {size: render(renderer, size) for size in PNG_SIZES}
    for size, data in images.items():
        (png / "icon-{}.png".format(size)).write_bytes(data)
    write_ico(folder / "icon.ico", {size: images[size] for size in ICO_SIZES})
    print("icons/{}: wrote {} PNG files and icon.ico".format(folder.name, len(images)))
    return True


def main() -> int:
    app = QGuiApplication(sys.argv[:1])  # noqa: F841 (Qt needs one to draw)
    names = sys.argv[1:] or sorted(p.name for p in ICONS.iterdir() if (p / "icon.svg").exists())
    ok = [render_app(ICONS / name) for name in names]
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
