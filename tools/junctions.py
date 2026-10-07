#!/usr/bin/env python3
"""Detect T-junction / pin-on-wire shorts in a KiCad 7 .kicad_sch file.
These are connections where a wire endpoint lands exactly on the middle of
another wire (a T-junction) or on a pin, but no junction dot or label exists.
KiCad requires explicit junctions for T-connections; without them it's a
silent disconnect (or an unintended short if the nets differ).
"""
import sys, re, math, collections

if len(sys.argv) != 2:
    print("usage: junctions.py <file.kicad_sch>")
    sys.exit(1)
path = sys.argv[1]
t = open(path).read()

EPS = 1e-9

# ──────────────────────────────────────────────────────────────────────────────
# extract wires
wires = []
for m in re.finditer(r'\(wire\s*\n\s*\(pts\s*\n\s*\(xyz ([\-\d.]+) ([\-\d.]+) 0\)\s*\n\s*\(xyz ([\-\d.]+) ([\-\d.]+) 0\)', t):
    x1, y1, x2, y2 = map(float, m.groups())
    wires.append((x1, y1, x2, y2))

# ──────────────────────────────────────────────────────────────────────────────
# extract junctions (explicit junction dots)
junctions = set()
for m in re.finditer(r'\(junction\s*\n\s*\(at ([\-\d.]+) ([\-\d.]+)\)', t):
    x, y = map(float, m.groups())
    junctions.add((round(x, 3), round(y, 3)))

# ──────────────────────────────────────────────────────────────────────────────
# extract pin connection points from instance blocks (local coordinates)
# pattern: (pin "N" ... (at X Y R))
pin_points = []
# First, find all instance blocks with their position/rotation
instances = []
for m in re.finditer(r'\(symbol\s*\n.*?\(lib_id "([^"]*)".*?\(at ([\-\d.]+) ([\-\d.]+) ([\-\d.]+)\)', t, re.S):
    lib_id, ix, iy, irot = m.group(1), float(m.group(2)), float(m.group(3)), float(m.group(4))
    # find pins inside this instance's block
    # the instance block ends at the matching ')'
    start = m.end()
    # find matching closing paren for this symbol
    depth = 1
    j = start
    while j < len(t) and depth > 0:
        if t[j] == '(': depth += 1
        elif t[j] == ')': depth -= 1
        j += 1
    block = t[m.start():j]
    # extract pins from this block
    for pm in re.finditer(r'\(pin\s+"(\d+)"\s+\w+\s*\n\s*\(at ([\-\d.]+) ([\-\d.]+) ([\-\d.]+)\)', block):
        pnum, px, py, prot = pm.group(1), float(pm.group(2)), float(pm.group(3)), float(pm.group(4))
        # transform from local to global
        # rotation is 0, 90, 180, 270
        angle = math.radians(irot + prot)
        cos_a = round(math.cos(angle))
        sin_a = round(math.sin(angle))
        gx = ix + cos_a * px - sin_a * py
        gy = iy + sin_a * px + cos_a * py
        pin_points.append((round(gx, 3), round(gy, 3)))

# also check hierarchical pins / sheet pins on root sheet
for m in re.finditer(r'\(pin\s+"([^"]+)"\s+\w+\s*\n\s*\(at ([\-\d.]+) ([\-\d.]+) ([\-\d.]+)\)', t):
    px, py = float(m.group(2)), float(m.group(3))
    pin_points.append((round(px, 3), round(py, 3)))

# ──────────────────────────────────────────────────────────────────────────────
# helper: point on segment
def point_on_seg(px, py, x1, y1, x2, y2):
    if abs(x2 - x1) < EPS:  # vertical
        if abs(px - x1) > EPS: return False
        return min(y1, y2) - EPS <= py <= max(y1, y2) + EPS
    if abs(y2 - y1) < EPS:  # horizontal
        if abs(py - y1) > EPS: return False
        return min(x1, x2) - EPS <= px <= max(x1, x2) + EPS
    return False

# ──────────────────────────────────────────────────────────────────────────────
# 1) wire endpoints that land on another wire's interior (T-junctions)
found_t = 0
for i, (x1, y1, x2, y2) in enumerate(wires):
    for ep in [(x1, y1), (x2, y2)]:
        ex, ey = ep
        for j, (x3, y3, x4, y4) in enumerate(wires):
            if i == j: continue
            if point_on_seg(ex, ey, x3, y3, x4, y4):
                # is it exactly at an endpoint of the other wire? that's fine
                if (abs(ex - x3) < EPS and abs(ey - y3) < EPS) or \
                   (abs(ex - x4) < EPS and abs(ey - y4) < EPS):
                    continue
                # is there an explicit junction?
                if (round(ex, 3), round(ey, 3)) in junctions:
                    continue
                found_t += 1
                print(f"T-JUNCTION: wire {i} endpoint ({ex:.3f},{ey:.3f}) on wire {j} interior")

# 2) pin points landing on wire interior (pin-on-wire)
found_p = 0
for px, py in pin_points:
    for j, (x3, y3, x4, y4) in enumerate(wires):
        if point_on_seg(px, py, x3, y3, x4, y4):
            # not at wire endpoint
            if (abs(px - x3) < EPS and abs(py - y3) < EPS) or \
               (abs(px - x4) < EPS and abs(py - y4) < EPS):
                continue
            # is there a junction?
            if (round(px, 3), round(py, 3)) in junctions:
                continue
            found_p += 1
            print(f"PIN-ON-WIRE: pin ({px:.3f},{py:.3f}) on wire {j} interior")

# 3) wire endpoints on pin (should have label/junction)
found_ep = 0
for i, (x1, y1, x2, y2) in enumerate(wires):
    for ep in [(x1, y1), (x2, y2)]:
        ex, ey = ep
        for px, py in pin_points:
            if abs(ex - px) < EPS and abs(ey - py) < EPS:
                # endpoint lands on pin - check for label/hier_label at this pos
                # (simplified: just warn if no junction)
                if (round(ex, 3), round(ey, 3)) not in junctions:
                    found_ep += 1
                    print(f"WIRE-END-ON-PIN: wire {i} endpoint ({ex:.3f},{ey:.3f}) on pin")

total = found_t + found_p + found_ep
print(f"Total T-junctions: {found_t}, Pin-on-wire: {found_p}, Wire-end-on-pin: {found_ep}")
sys.exit(1 if total else 0)
