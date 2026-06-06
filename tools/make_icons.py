from pathlib import Path
import importlib
import sys
from tempfile import NamedTemporaryFile


def import_pillow_image():
    try:
        PIL_Image = importlib.import_module("PIL.Image")
        return PIL_Image
    except Exception:
        return None


def make_icon_from_png(png_path: Path, out_ico: Path, sizes=(512, 256, 128, 64, 48, 32, 16)):
    Image = import_pillow_image()
    if Image is None:
        print("Missing dependency: pillow. Install with `pip install pillow`", file=sys.stderr)
        sys.exit(1)
    img = Image.open(png_path).convert("RGBA")
    out_ico.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_ico, format="ICO", sizes=[(s, s) for s in sizes])
    print(f"Wrote {out_ico}")


def try_cairosvg(svg_path: Path, tmp_png: Path, size: int):
    try:
        cairosvg = importlib.import_module("cairosvg")
    except Exception:
        return False
    cairosvg.svg2png(url=str(svg_path), write_to=str(tmp_png), output_width=size, output_height=size)
    return True


def try_qt_renderer(svg_path: Path, tmp_png: Path, size: int):
    try:
        from PySide6.QtGui import QGuiApplication, QPixmap, QPainter
        from PySide6.QtSvg import QSvgRenderer
    except Exception:
        return False

    app = QGuiApplication.instance() or QGuiApplication([])
    renderer = QSvgRenderer(str(svg_path))
    pixmap = QPixmap(size, size)
    pixmap.fill(0)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    pixmap.save(str(tmp_png), "PNG")
    return True


def make_icon(svg_path: Path, out_ico: Path, sizes=(512, 256, 128, 64, 48, 32, 16)):
    max_size = max(sizes)
    with NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_png = Path(tmp.name)

    rendered = False
    # Try CairoSVG first (needs libcairo), else use Qt renderer
    try:
        rendered = try_cairosvg(svg_path, tmp_png, max_size)
    except Exception:
        rendered = False

    if not rendered:
        rendered = try_qt_renderer(svg_path, tmp_png, max_size)

    if not rendered:
        print("Failed to render SVG: need cairosvg+libcairo or PySide6 available", file=sys.stderr)
        sys.exit(1)

    make_icon_from_png(tmp_png, out_ico, sizes=sizes)


if __name__ == "__main__":
    repo_root = Path(__file__).parent.parent
    svg = repo_root / "assets" / "lock.svg"
    ico = repo_root / "assets" / "lock.ico"
    if not svg.exists():
        print(f"SVG not found: {svg}", file=sys.stderr)
        sys.exit(1)
    make_icon(svg, ico)