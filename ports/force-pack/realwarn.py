#!/usr/bin/env python3
"""Skin build warnings that matter: overlaps between controls that are both on screen, and anything off the page.
Drops the TOUCH warnings an open popup list causes (it covers what is under it while open, and closes on a pick).
    realwarn.py <id> ...   (reads logs_<id>.txt and the port's layout.conf)"""
import os
import re
import sys

import hwskin

for pid in sys.argv[1:]:
    lay = open(os.path.join(hwskin.WORK, hwskin.PORTS[pid], "layout.conf")).read()
    pops = set(re.findall(r'^popup .*?label="([^"]*)"', lay, re.M))
    real = []
    for l in open("logs_%s.txt" % pid):
        if "warning" not in l:
            continue
        m = re.search(r"TOUCH (.+?) and (.+?) overlap", l)
        if m and any(n.startswith(p + " ") for n in m.groups() for p in pops):
            continue
        if "EDGE" in l and any((" %s " % p) in l for p in pops):
            continue
        real.append(l.strip())
    print("%-10s %d" % (pid, len(real)))
    for l in real[:6]:
        print("    " + l)
