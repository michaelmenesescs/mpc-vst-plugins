#!/usr/bin/env python3
"""sheet.py <id> [pages...] -> preview/<id>/sheet.png: the pages two across at half size (for a quick look)."""
import os, sys, glob, re
from PIL import Image
pid = sys.argv[1]
d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preview", pid)
files = sorted([f for f in glob.glob(d + "/p*.png") if re.search(r"/p\d+\.png$", f)], key=lambda f: int(re.search(r"p(\d+)\.png", f).group(1)))
if len(sys.argv) > 2:
    files = [os.path.join(d, "p%s.png" % n) for n in sys.argv[2:]]
w, h = 640, 314
cols = 2
rows = -(-len(files) // cols)
im = Image.new("RGB", (w * cols, h * rows), "white")
for i, f in enumerate(files):
    im.paste(Image.open(f).convert("RGB").resize((w, h), Image.LANCZOS), ((i % cols) * w, (i // cols) * h))
im.save(os.path.join(d, "sheet.png"))
print(os.path.join(d, "sheet.png"), len(files))
