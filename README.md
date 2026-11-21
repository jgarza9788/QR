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

## TUI examples

In every prompt, the value in `[brackets]` is the default. Press Enter to accept it. Surrounding quotes on pasted paths are stripped. Press Ctrl+C to cancel.

### Menu

```
$ python main.py

────────────────────────────────────────────────────────
  QR tools
────────────────────────────────────────────────────────
  1) img2text   QR image → text art + decoded text
  2) text2img   text → QR image
  Choose [1]: 2
```

You can type `1`, `2`, or the command name.

### text2img: text to a QR image

```
$ python main.py text2img

────────────────────────────────────────────────────────
  text2img  ·  text → QR image
────────────────────────────────────────────────────────
  Decoded text (paste it here, or give a .txt file path): https://example.com
  Error correction (l/m/q/h) [m]:
  Pixels per module [10]:
  Output PNG [C:\Users\you\QR\qr.png]:

────────────────────────────────────────────────────────
  result
────────────────────────────────────────────────────────
  Encoded : 19 chars (QR version 2)
  Saved   : C:\Users\you\QR\qr.png
```

To encode the contents of a file, enter its path at the first prompt. The output PNG then defaults to the same name with a `.png` extension:

```
  Decoded text (paste it here, or give a .txt file path): notes.txt
  ✓ read 412 chars from notes.txt
```

### img2text: QR image to text art

```
$ python main.py img2text

────────────────────────────────────────────────────────
  img2text  ·  QR image → text
────────────────────────────────────────────────────────
  Path to QR image: qr.png
  ✓ decoded 19 chars
  Art style (braille/half) [braille]:
  Max art characters [10000]:
  Output prefix [qr]:

────────────────────────────────────────────────────────
  result
────────────────────────────────────────────────────────
⠀⡤⠤⠤⡄⣀⡄⢄⡄⡀⡤⠤⠤⡄⠀
⠀⡇⠿⠇⡇⢻⢎⠰⡁⠆⡇⠿⠇⡇⠀
⠀⢍⣉⢉⠅⢗⢁⢅⣓⣣⢍⣩⣭⠁⠀
⠀⣛⡩⡷⠥⣟⡖⠼⢩⡇⢾⠘⢈⠇⠀
⠀⠇⠆⠢⠝⡶⠿⣁⡈⡴⠿⡝⠎⠃⠀
⠀⡏⣭⡍⡇⢠⡍⠖⡴⣧⡥⠇⢔⡅⠀
⠀⠧⠭⠥⠇⠼⠝⠡⠞⠖⠔⠪⠁⠇⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀

  Decoded : https://example.com
  Art size: 127 chars
  Saved   : qr.art.txt
            qr.decoded.txt
```

The output prefix controls the saved filenames: `<prefix>.art.txt` holds the art and `<prefix>.decoded.txt` holds the decoded text.

### Handling errors

If the image can't be read, or no QR code is found, the prompt repeats instead of exiting:

```
  Path to QR image: photo.jpg
  ! No QR code found/decoded in the image.  (tip: crop the image to just the QR)
  Path to QR image:
```

If the art doesn't fit within your character limit, the tool first tries lower error correction, a smaller quiet zone, and Braille. If it still can't fit, it asks for a higher limit:

```
  Max art characters [10000]: 300
  [fit] used style=braille border=1 ecc=L to stay under 300
```

```
    ! Can't fit in 300 chars (best attempt 1820). The QR holds 540 chars of data; that much data needs a big QR.
  Try a higher max [600]:
```

## Options reference

| Prompt | Choices | Default | Notes |
| --- | --- | --- | --- |
| Art style | `braille`, `half` | `braille` | Braille is the smallest. Half-blocks look right on a dark background and appear inverted on a light one. |
| Max art characters | whole number | `10000` | Upper bound on the size of the text art. |
| Error correction | `l`, `m`, `q`, `h` | `m` | Higher levels survive more damage but make a bigger QR. |
| Pixels per module | whole number | `10` | Size of each QR square in the PNG. |

## License

See [LICENSE](LICENSE).
