#!/usr/bin/env python3
import os
import sys
import tempfile
import shutil

OUTPUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
SRC_PNG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_SIZE = 1048576

def verify_file(path):
    if not os.path.exists(path):
        print(f"Error: {path} does not exist", file=sys.stderr)
        sys.exit(1)
    size = os.path.getsize(path)
    if size > MAX_SIZE:
        print(f"Error: {path} size {size} bytes exceeds 1 MiB", file=sys.stderr)
        sys.exit(1)
    with open(path, "rb") as f:
        header = f.read(8)
    if header != PNG_MAGIC:
        print(f"Error: {path} invalid PNG magic header: {header!r}", file=sys.stderr)
        sys.exit(1)

def main():
    if not os.path.exists(SRC_PNG):
        print(f"Error: Source image {SRC_PNG} not found", file=sys.stderr)
        sys.exit(1)

    verify_file(SRC_PNG)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    dst_path = os.path.join(OUTPUT_DIR, "entry.png")

    # Staged temp file in the output dir
    fd, tmp_path = tempfile.mkstemp(dir=OUTPUT_DIR, prefix=".tmp_entry_", suffix=".png")
    os.close(fd)

    try:
        shutil.copy(SRC_PNG, tmp_path)
        verify_file(tmp_path)
        os.chmod(tmp_path, 0o644)
        os.replace(tmp_path, dst_path)
    except Exception as e:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        print(f"Error during deployment: {e}", file=sys.stderr)
        sys.exit(1)

    verify_file(dst_path)
    print(f"Successfully deployed {SRC_PNG} to {dst_path} (mode 0644)")

if __name__ == "__main__":
    main()
