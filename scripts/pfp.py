"""Generates the neon wireframe-football profile picture (assets/pfp.svg).

A real truncated icosahedron (the classic football) is built in 3D, rotated,
and projected with depth-shaded neon edges, mid rainbow-flick.
Run:  python3 scripts/pfp.py   (then render the SVG to PNG at 1000x1000)
"""
import itertools
import math
from pathlib import Path

import numpy as np
from scipy.spatial import ConvexHull

OUT = Path(__file__).resolve().parent.parent / "assets"
BG = "#05070d"
GREEN, CYAN, RED, BONE = "#39ff88", "#00e5ff", "#ff2a46", "#e8eef5"
S = 1000
phi = (1 + 5 ** 0.5) / 2


def even_perms(v):
    x, y, z = v
    return [(x, y, z), (z, x, y), (y, z, x)]


def football():
    base = [(0, 1, 3 * phi), (1, 2 + phi, 2 * phi), (phi, 2, 2 * phi + 1)]
    pts = set()
    for b in base:
        for sx, sy, sz in itertools.product((1, -1), repeat=3):
            for p in even_perms((b[0] * sx, b[1] * sy, b[2] * sz)):
                pts.add(tuple(round(c, 6) for c in p))
    V = np.array(sorted(pts))
    hull = ConvexHull(V)
    faces = {}
    for simplex, eq in zip(hull.simplices, hull.equations):
        key = tuple(np.round(eq[:3], 4))
        faces.setdefault(key, set()).update(simplex)
    out = []
    for normal, idx in faces.items():
        idx = list(idx)
        c = V[idx].mean(axis=0)
        n = np.array(normal)
        a = V[idx[0]] - c
        b = np.cross(n, a)
        idx.sort(key=lambda i: math.atan2(np.dot(V[i] - c, b), np.dot(V[i] - c, a)))
        out.append((idx, n))
    edges = {tuple(sorted((i, j))) for i in range(len(V)) for j in range(i + 1, len(V))
             if abs(np.linalg.norm(V[i] - V[j]) - 2) < 1e-3}
    return V, out, edges


def rot(ax, ay, az):
    cx, sx, cy, sy, cz, sz = math.cos(ax), math.sin(ax), math.cos(ay), math.sin(ay), math.cos(az), math.sin(az)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


def f(v):
    return f"{v:.1f}"


def main():
    V, faces, edges = football()
    R = rot(0.55, -0.7, 0.3)
    V = V @ R.T
    Rad = np.linalg.norm(V, axis=1).max()
    r_ball = 215
    cx, cy = 560, 455
    cam = 14.0

    def proj(p):
        k = cam / (cam - p[2] / Rad * 2.2)
        return cx + p[0] / Rad * r_ball * k, cy - p[1] / Rad * r_ball * k

    P = [proj(p) for p in V]

    face_svg = []
    for idx, n in sorted(faces, key=lambda fn: (R @ np.zeros(3))[2] + V[fn[0]].mean(axis=0)[2]):
        n_rot = V[idx].mean(axis=0)
        facing = n_rot[2] > 0
        if not facing:
            continue
        pts = " ".join(f"{f(P[i][0])},{f(P[i][1])}" for i in idx)
        light = max(0.0, n_rot[2] / Rad)
        if len(idx) == 5:
            face_svg.append(f'<polygon points="{pts}" fill="url(#pent)" fill-opacity="{0.55 + 0.45 * light:.2f}" '
                            f'stroke="{RED}" stroke-width="3" stroke-linejoin="round" filter="url(#g1)"/>')
        else:
            face_svg.append(f'<polygon points="{pts}" fill="#0a1830" fill-opacity="{0.35 + 0.5 * light:.2f}"/>')

    back, front = [], []
    for i, j in edges:
        z = (V[i][2] + V[j][2]) / 2 / Rad
        line = f'M{f(P[i][0])} {f(P[i][1])}L{f(P[j][0])} {f(P[j][1])}'
        if z < 0:
            back.append(f'<path d="{line}" stroke="{CYAN}" stroke-opacity="{0.12 + 0.2 * (1 + z):.2f}" stroke-width="1.6"/>')
        else:
            front.append(f'<path d="{line}" stroke="{CYAN}" stroke-opacity="{0.55 + 0.45 * z:.2f}" stroke-width="{2.2 + 1.6 * z:.1f}"/>')
    verts = []
    for p, q in zip(V, P):
        if p[2] > 0:
            verts.append(f'<circle cx="{f(q[0])}" cy="{f(q[1])}" r="{2 + 2.5 * p[2] / Rad:.1f}" fill="#eafcff"/>')

    # rainbow-flick trail: arc from bottom-left, over the top, into the ball
    trail_d = f"M150 860 C 170 420, 420 150, {cx - 120} {cy - 175}"
    trails = []
    for w, op in ((62, .08), (40, .16), (24, .35), (12, .7), (4, 1)):
        trails.append(f'<path d="{trail_d}" fill="none" stroke="url(#trail)" stroke-width="{w}" '
                      f'stroke-linecap="round" stroke-opacity="{op}"/>')

    # speed streaks
    streaks = []
    for k, (x0, y0, L) in enumerate([(235, 620, 120), (210, 540, 90), (275, 700, 150), (300, 780, 80), (180, 460, 70)]):
        streaks.append(f'<path d="M{x0} {y0}l{L} {-L * 0.55}" stroke="{[GREEN, CYAN, RED][k % 3]}" stroke-width="3" '
                       f'stroke-linecap="round" opacity=".55"/>')

    # HUD ring segments
    ring = []
    rr = 452
    segs = [(-80, 20, GREEN), (28, 118, CYAN), (126, 196, RED), (204, 272, CYAN)]
    for a0, a1, col in segs:
        a0r, a1r = math.radians(a0), math.radians(a1)
        x0, y0 = 500 + rr * math.cos(a0r), 500 + rr * math.sin(a0r)
        x1, y1 = 500 + rr * math.cos(a1r), 500 + rr * math.sin(a1r)
        large = 1 if (a1 - a0) > 180 else 0
        ring.append(f'<path d="M{f(x0)} {f(y0)}A{rr} {rr} 0 {large} 1 {f(x1)} {f(y1)}" fill="none" stroke="{col}" '
                    f'stroke-width="6" stroke-linecap="round" filter="url(#g1)"/>')
    ticks = []
    for a in range(0, 360, 6):
        ar = math.radians(a)
        r0, r1 = 430, 436 if a % 30 else 444
        ticks.append(f'M{f(500 + r0 * math.cos(ar))} {f(500 + r0 * math.sin(ar))}L{f(500 + r1 * math.cos(ar))} {f(500 + r1 * math.sin(ar))}')

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {S} {S}" width="{S}" height="{S}">
<defs>
<radialGradient id="bg" cx=".56" cy=".45" r=".7"><stop offset="0" stop-color="#0e1d3a"/><stop offset=".55" stop-color="#070b18"/><stop offset="1" stop-color="{BG}"/></radialGradient>
<radialGradient id="halo" cx=".5" cy=".5" r=".5"><stop offset=".55" stop-color="{CYAN}" stop-opacity=".22"/><stop offset=".8" stop-color="{GREEN}" stop-opacity=".07"/><stop offset="1" stop-color="{GREEN}" stop-opacity="0"/></radialGradient>
<linearGradient id="pent" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ff5a72"/><stop offset="1" stop-color="#8a0018"/></linearGradient>
<linearGradient id="trail" gradientUnits="userSpaceOnUse" x1="150" y1="860" x2="{cx - 120}" y2="{cy - 175}">
<stop offset="0" stop-color="{GREEN}" stop-opacity="0"/><stop offset=".35" stop-color="{GREEN}"/><stop offset=".75" stop-color="{CYAN}"/><stop offset="1" stop-color="#ffffff"/></linearGradient>
<filter id="g1" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="g2" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="9" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<path id="tp" d="M500 500m-395 0a395 395 0 1 1 790 0a395 395 0 1 1 -790 0"/>
</defs>
<rect width="{S}" height="{S}" fill="url(#bg)"/>
<g stroke="#1d6b45" stroke-width="2" fill="none" opacity=".55">
<circle cx="500" cy="500" r="300"/><path d="M500 0V1000"/><circle cx="500" cy="500" r="7" fill="#1d6b45"/></g>
<path d="{''.join(ticks)}" stroke="#2a3a55" stroke-width="2"/>
{''.join(ring)}
<text font-family="'JetBrains Mono','DejaVu Sans Mono',monospace" font-size="22" letter-spacing="9" fill="#5b6a85">
<textPath href="#tp" startOffset="2%">AARAV · CODES · Nº10 · LEFT WING · AARAV · CODES · Nº10 · LEFT WING ·</textPath></text>
<g filter="url(#g2)">{''.join(trails)}</g>
{''.join(streaks)}
<circle cx="{cx}" cy="{cy}" r="{r_ball * 1.55}" fill="url(#halo)"/>
<g fill="none">{''.join(back)}</g>
<circle cx="{cx}" cy="{cy}" r="{r_ball * 1.02}" fill="#06101f" fill-opacity=".55"/>
{''.join(face_svg)}
<g fill="none" filter="url(#g1)" stroke-linecap="round">{''.join(front)}</g>
<g filter="url(#g1)">{''.join(verts)}</g>
<circle cx="{cx}" cy="{cy}" r="{r_ball * 1.03}" fill="none" stroke="{CYAN}" stroke-width="3" opacity=".6" filter="url(#g1)"/>
<g font-family="'Inter','Segoe UI',Helvetica,sans-serif" font-weight="900" font-style="italic">
<text x="500" y="842" text-anchor="middle" font-size="96" letter-spacing="6" fill="{BONE}" filter="url(#g1)">AARAV</text>
<text x="702" y="770" font-size="54" fill="{GREEN}" filter="url(#g1)">10</text></g>
</svg>"""
    OUT.mkdir(exist_ok=True)
    (OUT / "pfp.svg").write_text(svg)
    print("wrote assets/pfp.svg")


if __name__ == "__main__":
    main()
