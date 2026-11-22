"""Copy entry.png to the output directory as entry.png.

Standard library only. Reads entry.png that sits beside this file, so the
bytes copied are exactly the bytes committed to the repo. Running twice
produces identical output.

MAKEFUN_OUTPUT_DIR stands in for /output outside the grader's container:
    mkdir -p out1 && MAKEFUN_OUTPUT_DIR=out1 python3 main.py
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")


def main() -> None:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(SRC, os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
