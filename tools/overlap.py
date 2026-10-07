#!/usr/bin/env python3
"""Detect collinear overlapping wire segments on the same layer in a KiCad 7 .kicad_sch file.
These are shorts that ERC misses: two wires on the same net that overlap collinearly
but have no junction between them (or are on different nets, which is a hard short).
"""
import sys, re, math, itertools, collections

# ──────────────────────────────────────────────────────────────────────────────
# read file
if len(sys.argv) != 2:
    print("usage: overlap.py <file.kicad_sch>")
    sys.exit(1)
path = sys.argv[1]
t = open(path).read()

# ──────────────────────────────────────────────────────────────────────────────
# extract wires from a sheet file
# each wire: (x1, y1, x2, y2)
wires = []
for m in re.finditer(r'\(wire\s*\n\s*\(pts\s*\n\s*\(xyz ([\-\d.]+) ([\-\d.]+) 0\)\s*\n\s*\(xyz ([\-\d.]+) ([\-\d.]+) 0\)', t):
    x1, y1, x2, y2 = map(float, m.groups())
    wires.append((x1, y1, x2, y2))

# ──────────────────────────────────────────────────────────────────────────────
# collinear overlap test
EPS = 1e-9

def collinear_overlap(a, b):
    """Return True if segments a and b are collinear and overlap by > EPS."""
    x1, y1, x2, y2 = a
    x3, y3, x4, y4 = b
    # direction vectors
    dx1, dy1 = x2 - x1, y2 - y1
    dx2, dy2 = x4 - x3, y4 - y3
    # both must be axis-aligned (KiCad wires are always H or V)
    if not ((abs(dx1) < EPS and abs(dy1) > EPS) or (abs(dy1) < EPS and abs(dx1) > EPS)):
        return False
    if not ((abs(dx2) < EPS and abs(dy2) > EPS) or (abs(dy2) < EPS and abs(dx2) > EPS)):
        return False
    # must be parallel
    if abs(dx1) < EPS and abs(dx2) < EPS:
        # both vertical: same x?
        if abs(x1 - x3) > EPS: return False
        # y-ranges overlap?
        a1, a2 = sorted([y1, y2])
        b1, b2 = sorted([y3, y4])
        return min(a2, b2) - max(a1, b1) > EPS
    if abs(dy1) < EPS and abs(dy2) < EPS:
        # both horizontal: same y?
        if abs(y1 - y3) > EPS: return False
        a1, a2 = sorted([x1, x2])
        b1, b2 = sorted([x3, x4])
        return min(a2, b2) - max(a1, b1) > EPS
    return False

# ──────────────────────────────────────────────────────────────────────────────
# check all pairs
found = 0
for i, a in enumerate(wires):
    for b in wires[i+1:]:
        if collinear_overlap(a, b):
            found += 1
            print(f"OVERLAP: {a}  ×  {b}")

print(f"Total overlapping collinear wire pairs: {found}")
sys.exit(1 if found else 0)
