#!/usr/bin/env python3
"""Prepare Daily Atlas artwork: featured scenes + grid strips.

Featured: center-crop each winner to 314x157 and save as JPEG.
Strips:  center-crop each grid scene to 96x52 and save as JPEG.

Usage:  python3 prep_assets.py featured
        python3 prep_assets.py strips
"""
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")

# candidate -> final name, for the three featured panels
FEATURED = [
    ("f1-b.png", "f1.jpg"),
    ("f2-b.png", "f2.jpg"),
    ("f3-b.png", "f3.jpg"),
]

# grid strip sources, in story order 4..15
STRIPS = [
    ("s04.png", "g04.jpg"),
    ("s05.png", "g05.jpg"),
    ("s06.png", "g06.jpg"),
    ("s07.png", "g07.jpg"),
    ("s08.png", "g08.jpg"),
    ("s09.png", "g09.jpg"),
    ("s10.png", "g10.jpg"),
    ("s11.png", "g11.jpg"),
    ("s12.png", "g12.jpg"),
    ("s13.png", "g13.jpg"),
    ("s14.png", "g14.jpg"),
    ("s15.png", "g15.jpg"),
]


def center_crop(src, dst, w, h, quality=88):
    im = Image.open(src).convert("RGB")
    sw, sh = im.size
    target = w / h
    have = sw / sh
    if have > target:                      # too wide -> trim sides
        nw = int(round(sh * target))
        left = (sw - nw) // 2
        box = (left, 0, left + nw, sh)
    else:                                  # too tall -> trim top/bottom
        nh = int(round(sw / target))
        top = (sh - nh) // 2
        box = (0, top, sw, top + nh)
    out = im.crop(box).resize((w, h), Image.LANCZOS)
    out.save(dst, "JPEG", quality=quality, optimize=True, progressive=False)
    print("%-10s %sx%s -> %dx%d  %d bytes"
          % (os.path.basename(dst), sw, sh, w, h, os.path.getsize(dst)))


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "featured"
    if which == "featured":
        for src, dst in FEATURED:
            p = os.path.join(ASSETS, src)
            if not os.path.exists(p):
                print("missing %s" % p)
                continue
            center_crop(p, os.path.join(ASSETS, dst), 314, 157, 90)
    elif which == "strips":
        for src, dst in STRIPS:
            p = os.path.join(ASSETS, src)
            if not os.path.exists(p):
                print("missing %s -- will ship tinted panel" % p)
                continue
            center_crop(p, os.path.join(ASSETS, dst), 96, 52, 86)
    else:
        raise SystemExit("usage: prep_assets.py featured|strips")


if __name__ == "__main__":
    main()
