#!/usr/bin/env python3
"""Sync schematic lib_symbols cache with project library."""
import sys, re, uuid

if len(sys.argv) != 2:
    print("usage: libsync.py <root.kicad_sch>")
    sys.exit(1)

root_path = sys.argv[1]
root_t = open(root_path).read()

# Load project library
lib_path = root_path.replace('.kicad_sch', '.kicad_sym')
lib_t = open(lib_path).read()

# Parse library symbols - only the _0_1 variants which have the actual pin definitions
lib_symbols = {}
for m in re.finditer(r'\(symbol\s+"([^"]+_0_1)"', lib_t):
    name = m.group(1)
    start = m.start()
    depth = 1
    j = start + 1
    while j < len(lib_t) and depth > 0:
        if lib_t[j] == '(': depth += 1
        elif lib_t[j] == ')': depth -= 1
        j += 1
    block = lib_t[start:j]
    pins = []
    for pm in re.finditer(r'\(pin\s+(\w+)\s+(\w+)\s*\n\s*\(at\s+([\-\d.]+)\s+([\-\d.]+)\s+([\-\d.]+)\)\s*\n\s*\(length\s+([\d.]+)\)\s*\n\s*\(name\s+"([^"]*)"', block):
        pins.append({
            'type': pm.group(1), 'shape': pm.group(2),
            'x': float(pm.group(3)), 'y': float(pm.group(4)), 'rot': float(pm.group(5)),
            'length': float(pm.group(6)), 'name': pm.group(7)
        })
    base_name = name.replace('_0_1', '')
    lib_symbols[base_name] = pins
    print(f"Library: {base_name} -> {len(pins)} pins")

# Update root schematic's lib_symbols cache
ls_start = root_t.find('(lib_symbols')
if ls_start == -1:
    print("No lib_symbols cache in root schematic")
else:
    depth = 1
    j = ls_start + 1
    while j < len(root_t) and depth > 0:
        if root_t[j] == '(': depth += 1
        elif root_t[j] == ')': depth -= 1
        j += 1
    ls_block = root_t[ls_start:j]

    updated = 0
    for name, pins in lib_symbols.items():
        # Find this symbol in the cache
        pattern = f'(symbol "{re.escape(name)}"'
        m = re.search(pattern, ls_block)
        if not m:
            continue
        sym_start = m.start()
        depth = 1
        k = sym_start + 1
        while k < len(ls_block) and depth > 0:
            if ls_block[k] == '(': depth += 1
            elif ls_block[k] == ')': depth -= 1
            k += 1
        sym_block = ls_block[sym_start:k]
        
        # Rebuild pins section
        new_pins = []
        for idx, p in enumerate(pins):
            new_pins.append(f'''\t\t(pin {p['type']} {p['shape']}
\t\t\t(at {p['x']} {p['y']} {p['rot']})
\t\t\t(length {p['length']})
\t\t\t(name "{p['name']}"
\t\t\t\t(effects
\t\t\t\t\t(font
\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t)
\t\t\t(number "{idx+1}"
\t\t\t\t(effects
\t\t\t\t\t(font
\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t)
\t\t)''')
        
        first_pin = sym_block.find('(pin ')
        if first_pin == -1:
            continue
        last_pin = sym_block.rfind('(pin ')
        if last_pin == -1:
            continue
        depth = 1
        k2 = last_pin + 1
        while k2 < len(sym_block) and depth > 0:
            if sym_block[k2] == '(': depth += 1
            elif sym_block[k2] == ')': depth -= 1
            k2 += 1
        
        new_sym_block = sym_block[:first_pin] + '\n' + '\n'.join(new_pins) + '\n' + sym_block[k2:]
        ls_block = ls_block[:sym_start] + new_sym_block + ls_block[sym_start + len(sym_block):]
        updated += 1
        print(f"Updated root cache for {name}")

    root_t = root_t[:ls_start] + ls_block + root_t[j:]

# Also update sheet schematics that have cached copies
sheet_files = re.findall(r'\(property "Sheetfile" "([^"]*)"', root_t)
for sf in sheet_files:
    sheet_path = root_path.replace('OpenVCU.kicad_sch', sf)
    try:
        sheet_t = open(sheet_path).read()
    except:
        continue
    
    modified = False
    for m in re.finditer(r'\(symbol\s*\n', sheet_t):
        start = m.start()
        depth = 1
        k = start + 1
        while k < len(sheet_t) and depth > 0:
            if sheet_t[k] == '(': depth += 1
            elif sheet_t[k] == ')': depth -= 1
            k += 1
        block = sheet_t[start:k]
        lib_m = re.search(r'\(lib_id "OpenVCU:([^"]*)"', block)
        if lib_m:
            sym_name = lib_m.group(1)
            if sym_name in lib_symbols:
                pins = lib_symbols[sym_name]
                new_pins = []
                for idx, p in enumerate(pins):
                    new_pins.append(f'''\t\t\t(pin {p['type']} {p['shape']}
\t\t\t\t(at {p['x']} {p['y']} {p['rot']})
\t\t\t\t(length {p['length']})
\t\t\t\t(name "{p['name']}"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t\t(number "{idx+1}"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t)''')
                
                first_pin = block.find('(pin ')
                if first_pin != -1:
                    last_pin = block.rfind('(pin ')
                    if last_pin != -1:
                        depth = 1
                        k2 = last_pin + 1
                        while k2 < len(block) and depth > 0:
                            if block[k2] == '(': depth += 1
                            elif block[k2] == ')': depth -= 1
                            k2 += 1
                        new_block = block[:first_pin] + '\n' + '\n'.join(new_pins) + '\n\t\t' + block[k2:]
                        sheet_t = sheet_t[:start] + new_block + sheet_t[start + len(block):]
                        modified = True
                        print(f"  Updated cached {sym_name} in {sf}")
    
    if modified:
        open(sheet_path, 'w').write(sheet_t)

open(root_path, 'w').write(root_t)
print(f"Done. Updated {updated} symbols in root cache.")
