#!/usr/bin/env python3
"""compare.py <id> <ref image> [page] [crop x0,y0,x1,y1] -> preview/<id>/cmp.png: the reference (cropped, stretched to
the plugin area) over our page, and a 50/50 blend of the two under them, to check positions."""
import sys, os
from PIL import Image
pid, ref = sys.argv[1], sys.argv[2]
pg = sys.argv[3] if len(sys.argv) > 3 else "0"
d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preview", pid)
ours = Image.open(os.path.join(d, "p%s.png" % pg)).convert("RGB")
# the preview is the full 1280 x 800 screen? keep only the plugin area if so
if ours.size[1] > 628:
    ours = ours.crop((0, 86, 1280, 86 + 628))
r = Image.open(ref).convert("RGB")
if len(sys.argv) > 4:
    r = r.crop(tuple(int(v) for v in sys.argv[4].split(",")))
r = r.resize((1280, 628), Image.LANCZOS)
out = Image.new("RGB", (1280, 628 * 3), "white")
out.paste(r, (0, 0)); out.paste(ours, (0, 628)); out.paste(Image.blend(r, ours, 0.5), (0, 1256))
out.save(os.path.join(d, "cmp.png")); print(os.path.join(d, "cmp.png"))
