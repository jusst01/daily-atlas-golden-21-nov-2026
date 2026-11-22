#!/usr/bin/env python3
import os
import sys
import hashlib
from PIL import Image

PNG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
MAX_SIZE = 1048576
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"

def main():
    if not os.path.exists(PNG_PATH):
        print(f"Error: {PNG_PATH} not found", file=sys.stderr)
        sys.exit(1)

    size = os.path.getsize(PNG_PATH)
    if size > MAX_SIZE:
        print(f"Error: size {size} bytes exceeds 1 MiB", file=sys.stderr)
        sys.exit(1)

    with open(PNG_PATH, "rb") as f:
        header = f.read(8)
        f.seek(0)
        content = f.read()

    if header != PNG_MAGIC:
        print("Error: invalid PNG header", file=sys.stderr)
        sys.exit(1)

    im = Image.open(PNG_PATH)
    if im.size != (1024, 1024):
        print(f"Error: expected 1024x1024, got {im.size}", file=sys.stderr)
        sys.exit(1)

    sha256 = hashlib.sha256(content).hexdigest()
    print(f"SHA256: {sha256}")
    print(f"Bytes: {size}")

if __name__ == "__main__":
    main()
