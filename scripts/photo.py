#!/usr/bin/env python3
r"""Add pictures to the portfolio: resize, convert to WebP, strip EXIF/GPS, print the Markdown lines to paste.

    python scripts/photo.py D:\pics\a.jpg D:\pics\b.jpg

Saves assets/portfolio/NN.webp (max 1280 px wide) and NN-t.webp (thumbnail, 480 px), numbering on after the existing ones.
Needs Pillow:  pip install pillow
"""
import os
import re
import sys

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit('This tool needs Pillow:  pip install pillow')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOLDER = os.path.join(ROOT, 'assets', 'portfolio')


def save(im, dst, max_w, q):
    im = im.convert('RGB')
    if im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    im.save(dst, 'WEBP', quality=q, method=6)               # re-encoding drops EXIF / GPS


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    nums = [int(m.group(1)) for f in os.listdir(FOLDER) if (m := re.fullmatch(r'(\d\d)\.webp', f))]
    n = max(nums, default=0) + 1
    lines = []
    for f in sys.argv[1:]:
        im = ImageOps.exif_transpose(Image.open(f))
        save(im, os.path.join(FOLDER, f'{n:02d}.webp'), 1280, 82)
        save(im, os.path.join(FOLDER, f'{n:02d}-t.webp'), 480, 74)
        lines.append(f'![](portfolio/{n:02d}.webp)')
        n += 1
    print('Saved. Paste these lines under the right "## heading" in the content/portfolio/*.md file.')
    print('Add a caption in quotes if you like:  ![](portfolio/38.webp "說明文字")\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
