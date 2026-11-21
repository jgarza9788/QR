"""QR <-> text, fully offline. Always interactive (prompts for every input).

Usage:
    python main.py img2text    QR image  -> text art + decoded text
    python main.py text2img    text      -> QR image (PNG)
    python main.py             pick from a menu

Install deps:
    pip install opencv-python qrcode pillow
"""
import sys
from pathlib import Path

import cv2
import qrcode

LINE = "─" * 56


# ───────────────────────── core ─────────────────────────

def decode_qr(path: Path) -> str:
    img = cv2.imread(str(path))
    if img is None:
        raise ValueError(f"Could not read image: {path}")
    detector = cv2.QRCodeDetector()
    data, _, _ = detector.detectAndDecode(img)
    if not data:
        # retry upscaled with a white border, which helps small/tight crops
        img = cv2.copyMakeBorder(img, 40, 40, 40, 40, cv2.BORDER_CONSTANT, value=(255, 255, 255))
        img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
        data, _, _ = detector.detectAndDecode(img)
    if not data:
        raise ValueError("No QR code found/decoded in the image.")
    return data


def to_braille(m: list) -> str:
    """Braille: 2 cols x 4 rows of modules per character. Dots = dark modules."""
    h, w = len(m), len(m[0])
    m = [r + [False] * (-w % 2) for r in m]
    m += [[False] * len(m[0]) for _ in range(-h % 4)]
    bits = [(0, 0, 0x01), (0, 1, 0x02), (0, 2, 0x04), (0, 3, 0x40),
            (1, 0, 0x08), (1, 1, 0x10), (1, 2, 0x20), (1, 3, 0x80)]
    lines = []
    for y in range(0, len(m), 4):
        row = ""
        for x in range(0, len(m[0]), 2):
            code = sum(b for dx, dy, b in bits if m[y + dy][x + dx])
            row += chr(0x2800 + code)
        lines.append(row)
    return "\n".join(lines)


def to_ascii(data: str, border: int = 2, style: str = "braille", ecc: str = "M") -> str:
    """Render QR as text. style: 'braille' (smallest) or 'half' (half-blocks)."""
    qr = qrcode.QRCode(border=border, error_correction=getattr(qrcode.constants, f"ERROR_CORRECT_{ecc}"))
    qr.add_data(data)
    qr.make(fit=True)
    m = qr.get_matrix()  # True = dark
    if style == "braille":
        return to_braille(m)
    if len(m) % 2:
        m.append([False] * len(m[0]))
    # Light modules = filled block, dark modules = space. This looks right on a
    # dark terminal/editor; on a white background it appears inverted (many
    # scanners still read inverted codes, otherwise swap the mapping below).
    lines = []
    for y in range(0, len(m), 2):
        row = ""
        for top, bot in zip(m[y], m[y + 1]):
            row += {(False, False): "█", (False, True): "▀",
                    (True, False): "▄", (True, True): " "}[(top, bot)]
        lines.append(row)
    return "\n".join(lines)


def fit(data: str, style: str, limit: int) -> str:
    """Pick the first rendering within `limit` chars, trading off in this order:
    requested style -> lower error correction -> smaller quiet zone -> braille."""
    styles = [style] + [s for s in ("braille",) if s != style]
    art = ""
    for st in styles:
        for border in (2, 1):
            for ecc in ("M", "L"):
                art = to_ascii(data, border=border, style=st, ecc=ecc)
                if len(art) <= limit:
                    if (st, border, ecc) != (style, 2, "M"):
                        print(f"  [fit] used style={st} border={border} ecc={ecc} to stay under {limit}")
                    return art
    raise ValueError(f"Can't fit in {limit} chars (best attempt {len(art)}). "
                     f"The QR holds {len(data)} chars of data; that much data needs a big QR.")


# ───────────────────────── tui helpers ─────────────────────────

def header(title: str) -> None:
    print(f"\n{LINE}\n  {title}\n{LINE}")


def ask(label: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    raw = input(f"  {label}{suffix}: ").strip().strip('"').strip("'")
    return raw or default


def ask_path(label: str, must_exist: bool = True, default: str = "") -> Path:
    while True:
        raw = ask(label, default)
        if not raw:
            print("    ! a path is required")
            continue
        p = Path(raw).expanduser()
        if must_exist and not p.is_file():
            print(f"    ! file not found: {p}")
            continue
        return p


def ask_choice(label: str, choices: list, default: str) -> str:
    while True:
        raw = ask(f"{label} ({'/'.join(choices)})", default).lower()
        if raw in choices:
            return raw
        print(f"    ! pick one of: {', '.join(choices)}")


def ask_int(label: str, default: int, lo: int = 1) -> int:
    while True:
        raw = ask(label, str(default))
        if raw.isdigit() and int(raw) >= lo:
            return int(raw)
        print(f"    ! enter a whole number >= {lo}")


# ───────────────────────── commands ─────────────────────────

def img2text() -> None:
    header("img2text  ·  QR image → text")
    while True:
        img = ask_path("Path to QR image")
        try:
            data = decode_qr(img)
            break
        except ValueError as e:
            print(f"    ! {e}  (tip: crop the image to just the QR)")
    print(f"  ✓ decoded {len(data)} chars")

    style = ask_choice("Art style", ["braille", "half"], "braille")
    limit = ask_int("Max art characters", 10000)
    while True:
        try:
            art = fit(data, style, limit)
            break
        except ValueError as e:
            print(f"    ! {e}")
            limit = ask_int("Try a higher max", limit * 2)

    prefix = ask("Output prefix", str(img.with_suffix("")))
    art_file, txt_file = Path(f"{prefix}.art.txt"), Path(f"{prefix}.decoded.txt")
    art_file.write_text(art, encoding="utf-8")
    txt_file.write_text(data, encoding="utf-8")

    header("result")
    print(art)
    print(f"\n  Decoded : {data}")
    print(f"  Art size: {len(art)} chars")
    print(f"  Saved   : {art_file}\n            {txt_file}")


def text2img() -> None:
    header("text2img  ·  text → QR image")
    data = ""
    while not data:
        data = ask("Decoded text (paste it here, or give a .txt file path)")
    default_out = str(Path.cwd() / "qr.png")
    try:
        p = Path(data).expanduser()
        if p.is_file():
            data = p.read_text(encoding="utf-8").strip("\r\n")
            default_out = str(p.with_suffix(".png"))
            print(f"  ✓ read {len(data)} chars from {p.name}")
    except OSError:
        pass  # not a valid path, so treat it as literal text

    ecc = ask_choice("Error correction", ["l", "m", "q", "h"], "m").upper()
    box = ask_int("Pixels per module", 10)
    out = Path(ask("Output PNG", default_out)).expanduser()

    qr = qrcode.QRCode(border=4, box_size=box, error_correction=getattr(qrcode.constants, f"ERROR_CORRECT_{ecc}"))
    qr.add_data(data)
    qr.make(fit=True)
    qr.make_image(fill_color="black", back_color="white").save(out)

    header("result")
    print(f"  Encoded : {len(data)} chars (QR version {qr.version})")
    print(f"  Saved   : {out}")


COMMANDS = {"img2text": img2text, "text2img": text2img}


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles/pipes default to cp1252
    cmd = sys.argv[1].lower() if len(sys.argv) > 1 else None
    if cmd not in COMMANDS:
        if cmd:
            print(f"Unknown command: {cmd}")
        header("QR tools")
        print("  1) img2text   QR image → text art + decoded text")
        print("  2) text2img   text → QR image")
        choice = ask("Choose", "1")
        cmd = {"1": "img2text", "2": "text2img"}.get(choice, choice.lower())
        if cmd not in COMMANDS:
            sys.exit("Nothing selected.")
    try:
        COMMANDS[cmd]()
    except (KeyboardInterrupt, EOFError):
        print("\n  cancelled")


if __name__ == "__main__":
    main()
