# QR

Convert QR codes to text and back, fully offline. The tool is interactive and prompts for every input.

## Install

```
pip install opencv-python qrcode pillow
```

## Usage

```
python main.py img2text    # QR image -> text art + decoded text
python main.py text2img    # text     -> QR image (PNG)
python main.py             # pick from a menu
```

### img2text

Reads a QR image, decodes it, and renders the code as text art (Braille or half-block characters). You choose the art style and a maximum character count. If the art is too big, the tool tries lower error correction, a smaller quiet zone, and Braille before giving up.

Saves `<prefix>.art.txt` (the art) and `<prefix>.decoded.txt` (the decoded text).

Tip: crop the image to just the QR code if decoding fails.

### text2img

Takes text, either pasted or given as a `.txt` file path, and writes a QR code PNG. You choose the error correction level (L/M/Q/H), the pixels per module, and the output path.

## License

See [LICENSE](LICENSE).
