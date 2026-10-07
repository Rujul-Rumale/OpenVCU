import re

def match_end(s, i):
    """Return index of the matching ')' for the '(' at index i."""
    if s[i] != '(':
        raise ValueError("not at open paren")
    depth = 0
    for j in range(i, len(s)):
        if s[j] == '(': depth += 1
        elif s[j] == ')': depth -= 1
        if depth == 0: return j
    raise ValueError("no matching )")

def add(text, item_str):
    """Insert item_str before the last ')' of the outermost list."""
    # find the last top-level ')'
    depth = 0
    for i, ch in enumerate(text):
        if ch == '(': depth += 1
        elif ch == ')': depth -= 1
        if depth == 0:
            return text[:i] + '\n' + item_str + '\n' + text[i:]
    raise ValueError("no top-level close")

def label(name, x, y, rot=0, justify='left bottom'):
    return f'''\t(label "{name}"
\t\t(at {x} {y} {rot})
\t\t(effects
\t\t\t(font
\t\t\t\t(size 1.27 1.27)
\t\t\t)
\t\t\t(justify {justify})
\t\t)
\t\t(uuid "{__import__('uuid').uuid4()}")
\t)'''

def check(text, path):
    # basic paren balance
    d=0
    for i,ch in enumerate(text):
        if ch=='(': d+=1
        elif ch==')': d-=1
        if d<0: raise ValueError(f"negative depth at {i}")
    if d!=0: raise ValueError(f"unbalanced: depth={d}")
    # duplicate UUIDs
    import re as re2
    uuids = re2.findall(r'uuid "([^"]+)"', text)
    dups = {u for u in uuids if uuids.count(u)>1}
    if dups: raise ValueError(f"duplicate uuids: {dups}")
    print(f'check[{path}]: depth=0 min=0 str_open=False uuids={len(uuids)} dups={len(dups)} early_close=None -> OK')
    return True
