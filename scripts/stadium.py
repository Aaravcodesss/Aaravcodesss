"""Generates the animated night-match SVGs used in README.md.

Everything is drawn in code: a tactics-board pitch where a passing move plays
out (with a rainbow flick before the finish), a live scoreboard of
Aarav vs Bugs FC, and a floodlit crowd doing a Mexican wave.
Animations are pure CSS/SMIL so they run on GitHub with no JavaScript.

Run:  python3 scripts/stadium.py
Headline lettering is converted to vector paths (Inter Display) when the font
is available, so it looks identical on every device.
"""
import math
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(exist_ok=True)

BG = "#05070d"
BONE = "#e8eef5"
MUTED = "#7f8ba0"
LINE = "#1d6b45"
GREEN = "#39ff88"
CYAN = "#00e5ff"
RED = "#ff2a46"
MONO = "ui-monospace,'SFMono-Regular',Menlo,Consolas,'DejaVu Sans Mono',monospace"
SANS = "Inter,'Segoe UI',Helvetica,Arial,sans-serif"


def f(v):
    return f"{v:.1f}"


# --------------------------------------------------------------------------
# Text -> vector paths (falls back to live text if the font is missing)
# --------------------------------------------------------------------------
FONT_DIRS = [Path("/usr/share/fonts/opentype/inter"), Path.home() / "Library/Fonts", Path("C:/Windows/Fonts")]


def text_path(text, font_file, size, x, y, tracking=0.0):
    try:
        from fontTools.ttLib import TTFont
        from fontTools.pens.svgPathPen import SVGPathPen
        from fontTools.pens.transformPen import TransformPen
    except ImportError:
        return None
    path = next((d / font_file for d in FONT_DIRS if (d / font_file).exists()), None)
    if path is None:
        return None
    font = TTFont(path)
    gs = font.getGlyphSet()
    cmap = font.getBestCmap()
    upm = font["head"].unitsPerEm
    s = size / upm
    pen = SVGPathPen(gs)
    cx = x
    for ch in text:
        g = cmap.get(ord(ch))
        if g is None:
            continue
        tp = TransformPen(pen, (s, 0, 0, -s, cx, y))
        gs[g].draw(tp)
        cx += gs[g].width * s + tracking
    return pen.getCommands(), cx - x


def headline(text, font_file, size, x, y, attrs, tracking=0.0, fallback_weight=900, italic=True):
    res = text_path(text, font_file, size, x, y, tracking)
    if res:
        return f'<path d="{res[0]}" {attrs}/>'
    style = "italic" if italic else "normal"
    return (f'<text x="{x}" y="{y}" font-family="{SANS}" font-weight="{fallback_weight}" font-style="{style}" '
            f'font-size="{size}" letter-spacing="{tracking}" {attrs}>{text}</text>')


# --------------------------------------------------------------------------
# Header: name + tactics board with an animated passing move
# --------------------------------------------------------------------------
def header():
    rng = random.Random(10)
    W, H = 1200, 420
    # pitch rectangle (top-down, attacking right)
    px, py, pw, ph = 600, 46, 560, 330
    cycle = 13.0

    def P(u, v):  # pitch coords 0..1 -> svg
        return px + u * pw, py + v * ph

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
           f'aria-label="Aarav — a passing move on a neon tactics board ends in a goal">',
           '<title>Aarav — Night Match</title>']

    css = [f"""
.draw{{fill:none;stroke:{LINE};stroke-width:1.6;stroke-dasharray:var(--l);stroke-dashoffset:var(--l);animation:draw 2.6s cubic-bezier(.65,0,.35,1) var(--d) forwards}}
@keyframes draw{{to{{stroke-dashoffset:0}}}}
.rise{{animation:rise 1.4s cubic-bezier(.19,1,.22,1) both}}
.r1{{animation-delay:.1s}}.r2{{animation-delay:.3s}}.r3{{animation-delay:.6s}}.r4{{animation-delay:.9s}}
@keyframes rise{{from{{transform:translateY(30px);opacity:0}}to{{transform:none;opacity:1}}}}
.heat{{animation:heat 5s ease-in-out infinite alternate}}
@keyframes heat{{from{{opacity:.35}}to{{opacity:.8}}}}
.node{{animation:pulse 2.4s ease-in-out infinite alternate}}
@keyframes pulse{{from{{opacity:.55}}to{{opacity:1}}}}
.flash{{opacity:0;animation:goal {cycle}s linear infinite}}
.net{{stroke:{LINE};animation:net {cycle}s linear infinite}}
.dot{{animation:blink 1.2s steps(2) infinite}}
@keyframes blink{{50%{{opacity:.2}}}}
"""]

    # ---- pitch markings, drawn in
    marks = []

    def mark(d, length, delay):
        marks.append(f'<path class="draw" style="--l:{length:.0f};--d:{delay}s" d="{d}"/>')

    x0, y0 = P(0, 0)
    x1, y1 = P(1, 1)
    mark(f"M{f(x0)} {f(y0)}H{f(x1)}V{f(y1)}H{f(x0)}Z", 2 * (pw + ph), 0.2)
    mx = px + pw / 2
    mark(f"M{f(mx)} {f(y0)}V{f(y1)}", ph, 0.5)
    r = ph * 0.15
    mark(f"M{f(mx)} {f(py + ph / 2 - r)}a{f(r)} {f(r)} 0 1 1 0 {f(2 * r)}a{f(r)} {f(r)} 0 1 1 0 {f(-2 * r)}", 2 * math.pi * r, 0.7)
    for side in (0, 1):
        bw, bh = pw * 0.16, ph * 0.58
        sw, sh = pw * 0.06, ph * 0.28
        if side == 0:
            mark(f"M{f(x0)} {f(py + (ph - bh) / 2)}h{f(bw)}v{f(bh)}h{f(-bw)}", 2 * bw + bh, 0.9)
            mark(f"M{f(x0)} {f(py + (ph - sh) / 2)}h{f(sw)}v{f(sh)}h{f(-sw)}", 2 * sw + sh, 1.1)
        else:
            mark(f"M{f(x1)} {f(py + (ph - bh) / 2)}h{f(-bw)}v{f(bh)}h{f(bw)}", 2 * bw + bh, 0.9)
            mark(f"M{f(x1)} {f(py + (ph - sh) / 2)}h{f(-sw)}v{f(sh)}h{f(sw)}", 2 * sw + sh, 1.1)
    # goal net on the right
    gy0, gy1 = py + ph * 0.42, py + ph * 0.58
    net = [f'<path class="net" fill="none" stroke-width="1.2" d="M{f(x1)} {f(gy0)}h14v{f(gy1 - gy0)}h-14"/>']
    for i in range(1, 6):
        yy = gy0 + (gy1 - gy0) * i / 6
        net.append(f'<path class="net" stroke-width=".6" d="M{f(x1)} {f(yy)}h14"/>')

    # ---- heat map in the left-wing channel (top flank when attacking right)
    heat = []
    for _ in range(14):
        u = rng.uniform(0.45, 0.95)
        v = rng.uniform(0.05, 0.38)
        cx, cy = P(u, v)
        rr = rng.uniform(18, 46)
        heat.append(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(rr)}" fill="url(#hg)" '
                    f'style="animation-delay:-{rng.uniform(0, 5):.1f}s"/>')

    # ---- players (4-3-3), opponents
    team = {
        "gk": (0.04, 0.5), "lb": (0.22, 0.14), "cb1": (0.18, 0.38), "cb2": (0.18, 0.62), "rb": (0.22, 0.86),
        "cm1": (0.42, 0.3), "cm2": (0.38, 0.55), "cm3": (0.45, 0.78),
        "lw": (0.68, 0.14), "st": (0.74, 0.5), "rw": (0.68, 0.84),
    }
    opp = [(0.97, 0.5), (0.86, 0.3), (0.84, 0.52), (0.86, 0.72), (0.82, 0.14), (0.6, 0.4), (0.62, 0.62), (0.56, 0.25)]

    # the move: cb1 -> cm2 -> cm1 -> lb(overlap) -> lw ... rainbow flick over defender -> shot
    seq = [team["cb1"], team["cm2"], team["cm1"], (0.5, 0.1), team["lw"]]
    pts = [P(*s) for s in seq]
    flick_from = pts[-1]
    flick_to = P(0.88, 0.2)          # past the full-back at (0.82,0.14)
    shot_to = P(1.0, 0.47)

    segs = []
    for a, b in zip(pts, pts[1:]):
        segs.append(("pass", f"M{f(a[0])} {f(a[1])}L{f(b[0])} {f(b[1])}", math.dist(a, b), a, b))
    # rainbow flick: a high arc (drawn as an arc above the defender)
    fx, fy = flick_from
    tx, ty = flick_to
    arc_d = f"M{f(fx)} {f(fy)}Q{f((fx + tx) / 2)} {f(fy - 70)} {f(tx)} {f(ty)}"
    segs.append(("flick", arc_d, math.dist(flick_from, flick_to) * 1.5, flick_from, flick_to))
    shot_d = f"M{f(tx)} {f(ty)}Q{f(tx + 40)} {f(ty + 20)} {f(shot_to[0])} {f(shot_to[1])}"
    segs.append(("shot", shot_d, math.dist(flick_to, shot_to) * 1.1, flick_to, shot_to))

    total = sum(s[2] for s in segs)
    move_start, move_end = 2.6, 8.4      # seconds within the cycle
    t = move_start
    pass_svg = []
    motion_path = ""
    timeline = []
    for i, (kind, d, L, a, b) in enumerate(segs):
        dur = (move_end - move_start) * L / total
        a_pct, b_pct = 100 * t / cycle, 100 * (t + dur) / cycle
        timeline.append((t, t + dur))
        colour = {"pass": CYAN, "flick": GREEN, "shot": RED}[kind]
        width = {"pass": 1.8, "flick": 2.2, "shot": 2.6}[kind]
        dash = 'stroke-dasharray:6 7;' if kind == "pass" else ""
        name = f"s{i}"
        css.append(
            f"@keyframes {name}{{0%,{a_pct:.2f}%{{stroke-dashoffset:{L:.0f};opacity:1}}"
            f"{b_pct:.2f}%{{stroke-dashoffset:0;opacity:1}}86%{{stroke-dashoffset:0;opacity:1}}96%,100%{{stroke-dashoffset:0;opacity:0}}}}")
        # draw with a mask trick: solid dash for reveal, dashed look via second stroke
        pass_svg.append(
            f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{width}" stroke-linecap="round" filter="url(#glow)" '
            f'style="stroke-dasharray:{L:.0f};stroke-dashoffset:{L:.0f};animation:{name} {cycle}s linear infinite"/>')
        motion_path += d if i == 0 else " " + d.replace("M", "L", 1)
        t += dur

    # goal flash timing
    g0 = 100 * move_end / cycle
    css.append(f"@keyframes goal{{0%,{g0:.2f}%{{opacity:0}}{g0 + 1:.2f}%{{opacity:1}}{g0 + 18:.2f}%{{opacity:1}}{g0 + 22:.2f}%,100%{{opacity:0}}}}")
    css.append(f"@keyframes net{{0%,{g0:.2f}%{{stroke:{LINE}}}{g0 + 1:.2f}%,{g0 + 14:.2f}%{{stroke:{RED}}}{g0 + 20:.2f}%,100%{{stroke:{LINE}}}}}")

    # ball motion via SMIL along the stitched path
    kt_end = move_end / cycle
    kt_start = move_start / cycle
    ball = (f'<g><circle r="5.5" fill="#fff" filter="url(#glow)"/>'
            f'<animateMotion dur="{cycle}s" repeatCount="indefinite" calcMode="linear" '
            f'keyPoints="0;0;1;1" keyTimes="0;{kt_start:.4f};{kt_end:.4f};1" path="{motion_path}"/>'
            f'<animate attributeName="opacity" dur="{cycle}s" repeatCount="indefinite" values="1;1;0;0" keyTimes="0;{(move_end + 1.6) / cycle:.4f};{(move_end + 1.7) / cycle:.4f};1"/></g>')

    nodes = []
    for (u, v) in opp:
        x, y = P(u, v)
        nodes.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="5" fill="none" stroke="{RED}" stroke-opacity=".6" stroke-width="1.4"/>')
    for k, (u, v) in team.items():
        x, y = P(u, v)
        nodes.append(f'<circle class="node" cx="{f(x)}" cy="{f(y)}" r="6" fill="{CYAN}" filter="url(#glow)" '
                     f'style="animation-delay:-{rng.uniform(0, 2.4):.1f}s"/>')
    lx, ly = P(*team["lw"])
    nodes.append(f'<text x="{f(lx)}" y="{f(ly - 13)}" text-anchor="middle" font-family="{MONO}" font-size="10" '
                 f'font-weight="700" fill="{GREEN}">10</text>')

    defs = f"""<defs>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.6" result="b"/>
<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="22"/></filter>
<radialGradient id="hg"><stop offset="0" stop-color="{GREEN}" stop-opacity=".32"/><stop offset=".6" stop-color="{CYAN}" stop-opacity=".1"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>
<radialGradient id="flood" cx=".75" cy="0" r=".9"><stop offset="0" stop-color="#0d2a3a" stop-opacity=".9"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></radialGradient>
<linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="{BG}"/><stop offset=".12" stop-color="{BG}" stop-opacity="0"/></linearGradient>
</defs>"""

    # ---- left column: label, name, tagline
    name_top = headline("AARAV", "InterDisplay-BlackItalic.otf", 150, 36, 200, f'fill="{BONE}"', tracking=-4)
    name_bot = headline("CODES", "InterDisplay-BlackItalic.otf", 108, 120, 300,
                        f'fill="none" stroke="{BONE}" stroke-opacity=".75" stroke-width="1.4"', tracking=2)
    left = f"""
<g class="rise r1"><circle class="dot" cx="44" cy="62" r="5" fill="{RED}"/>
<text x="58" y="67" font-family="{MONO}" font-size="13" letter-spacing="4" fill="{MUTED}">LEFT WING · DEVELOPER — INDIA</text></g>
<g class="rise r2">{name_top}</g>
<g class="rise r3">{name_bot}</g>
<g class="rise r4"><text x="40" y="350" font-family="{MONO}" font-size="13" letter-spacing="3.2" fill="{MUTED}">DRIBBLING PAST BUGS, SHIPPING WITH <tspan fill="{RED}">FLAIR</tspan>.</text></g>
<text x="40" y="400" font-family="{MONO}" font-size="10" letter-spacing="4" fill="#3b4558">NIGHT MATCH · KICK-OFF 00:00</text>
"""
    goal_txt = (f'<text class="flash" x="{f(px + pw * 0.62)}" y="{f(py + ph * 0.62)}" text-anchor="middle" '
                f'font-family="{MONO}" font-size="12" letter-spacing="10" fill="{RED}">GOAL</text>')
    caption = (f'<text x="{f(x1)}" y="400" text-anchor="end" font-family="{MONO}" font-size="10" letter-spacing="4" fill="#3b4558">'
               f'CB → CM → CM → LW · RAINBOW FLICK · FINISH</text>')

    out += [f"<style>{''.join(css)}</style>", defs,
            f'<rect width="{W}" height="{H}" fill="{BG}"/>',
            f'<rect width="{W}" height="{H}" fill="url(#flood)"/>',
            f'<g class="heat" filter="url(#soft)">{"".join(heat)}</g>',
            f"<g>{''.join(marks)}</g>", "".join(net),
            "".join(pass_svg), "".join(nodes), ball, goal_txt, caption, left, "</svg>"]
    (OUT / "night-match.svg").write_text("\n".join(out))


# --------------------------------------------------------------------------
# Scoreboard: Aarav vs Bugs FC, ticking through a full match
# --------------------------------------------------------------------------
def scoreboard():
    W, H = 1200, 170
    cycle = 16.0
    events = [
        ("0'", 0, 0, "KICK-OFF", MUTED),
        ("12'", 0, 1, "BUGS — NullPointerException", RED),
        ("27'", 1, 1, "AARAV — console.log()", GREEN),
        ("38'", 1, 2, "BUGS — Off-by-one", RED),
        ("51'", 2, 2, "AARAV — Stack Overflow assist", GREEN),
        ("66'", 2, 3, "BUGS — Merge conflict", RED),
        ("79'", 3, 3, "AARAV — git commit -m \"fix\"", GREEN),
        ("90+4'", 4, 3, "AARAV — rainbow flick · WINNER", CYAN),
    ]
    n = len(events)
    # last frame lingers longer
    weights = [1] * (n - 1) + [2.4]
    total = sum(weights)
    css = [f""".fr{{opacity:0;animation-duration:{cycle}s;animation-iteration-count:infinite;animation-timing-function:step-end}}
.bar{{animation:bar {cycle}s linear infinite;transform-origin:0 0}}@keyframes bar{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}
.live{{animation:blink 1s steps(2) infinite}}@keyframes blink{{50%{{opacity:.15}}}}"""]
    frames = []
    acc = 0.0
    for i, (minute, a, b, label, col) in enumerate(events):
        s, e = 100 * acc / total, 100 * (acc + weights[i]) / total
        acc += weights[i]
        css.append(f"@keyframes k{i}{{0%{{opacity:0}}{s:.2f}%{{opacity:1}}{e:.2f}%,100%{{opacity:0}}}}"
                   if i else f"@keyframes k{i}{{0%{{opacity:1}}{e:.2f}%,100%{{opacity:0}}}}")
        frames.append(f"""<g class="fr" style="animation-name:k{i}">
<text x="600" y="48" text-anchor="middle" font-family="{MONO}" font-size="14" letter-spacing="6" fill="{col}">{minute}</text>
<text x="545" y="118" text-anchor="end" font-family="{SANS}" font-weight="800" font-size="72" fill="{BONE}">{a}</text>
<text x="655" y="118" text-anchor="start" font-family="{SANS}" font-weight="800" font-size="72" fill="{BONE}">{b}</text>
<text x="600" y="150" text-anchor="middle" font-family="{MONO}" font-size="12" letter-spacing="3" fill="{col}">{label.replace('"', '&quot;')}</text></g>""")
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Live scoreboard: Aarav versus Bugs FC">
<title>Aarav vs Bugs FC</title>
<style>{''.join(css)}</style>
<rect width="{W}" height="{H}" fill="{BG}"/>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" fill="none" stroke="#141b2a"/>
<g font-family="{MONO}" letter-spacing="6" font-size="13">
<circle class="live" cx="40" cy="30" r="4" fill="{RED}"/><text x="52" y="35" fill="{RED}">LIVE</text>
<text x="{W - 36}" y="35" text-anchor="end" fill="#3b4558">MATCHDAY · EVERY DAY</text></g>
<text x="380" y="106" text-anchor="end" font-family="{SANS}" font-weight="800" font-style="italic" font-size="30" letter-spacing="4" fill="{CYAN}">AARAV</text>
<text x="820" y="106" font-family="{SANS}" font-weight="800" font-style="italic" font-size="30" letter-spacing="4" fill="{RED}">BUGS FC</text>
<text x="600" y="112" text-anchor="middle" font-family="{SANS}" font-weight="300" font-size="50" fill="{MUTED}">–</text>
{''.join(frames)}
<rect class="bar" x="0" y="{H - 3}" width="{W}" height="3" fill="{GREEN}" opacity=".85"/>
</svg>"""
    (OUT / "scoreboard.svg").write_text(svg)


# --------------------------------------------------------------------------
# Divider: lines run out from a centre circle with a spinning ball
# --------------------------------------------------------------------------
def divider():
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 40" width="1200" height="40" role="img" aria-label="divider">
<style>.l{{stroke:{LINE};stroke-width:1;stroke-dasharray:560;stroke-dashoffset:560;animation:d 2.4s ease forwards}}
.c{{fill:none;stroke:{GREEN};stroke-width:1.2;stroke-dasharray:4 4;animation:spin 10s linear infinite;transform-origin:600px 20px}}
.b{{animation:roll 4s cubic-bezier(.45,0,.55,1) infinite alternate}}
@keyframes d{{to{{stroke-dashoffset:0}}}}@keyframes spin{{to{{transform:rotate(360deg)}}}}
@keyframes roll{{from{{transform:translateX(-9px)}}to{{transform:translateX(9px)}}}}</style>
<line class="l" x1="582" y1="20" x2="20" y2="20"/><line class="l" x1="618" y1="20" x2="1180" y2="20"/>
<circle class="c" cx="600" cy="20" r="15"/>
<circle class="b" cx="600" cy="20" r="3.4" fill="{CYAN}"/>
</svg>"""
    (OUT / "divider.svg").write_text(svg)


# --------------------------------------------------------------------------
# Footer: the crowd — tiers of seats, phone lights, flashes and a wave
# --------------------------------------------------------------------------
def crowd():
    rng = random.Random(7)
    W, H = 1200, 300
    buckets = 48
    wave_cycle = 7.0
    groups = [[] for _ in range(buckets)]
    lights = []
    y = 34.0
    row = 0
    while y < 222:
        depth = (y - 30) / 190            # 0 far .. 1 near
        size = 1.3 + depth * 2.6
        gap = size * 2.3
        x = (row % 2) * gap / 2 - gap
        while x < W + gap:
            jx = x + rng.uniform(-0.4, 0.4) * gap * 0.2
            b = min(buckets - 1, max(0, int(jx / W * buckets)))
            groups[b].append(f"M{f(jx)} {f(y)}h{f(size)}v{f(size)}h{f(-size)}z")
            if rng.random() < 0.03:
                lights.append((jx + size / 2, y + size / 2, size, rng.choice([CYAN, GREEN, CYAN, RED, BONE])))
            x += gap
        y += size * 1.9
        row += 1

    css = [f""".g{{fill:#18233a;animation:wave {wave_cycle}s ease-in-out infinite}}
@keyframes wave{{0%,70%,100%{{fill:#18233a;transform:none}}80%{{fill:{CYAN};transform:translateY(-3px)}}86%{{fill:{GREEN}}}}}
.ph{{animation:ph 3s ease-in-out infinite alternate}}@keyframes ph{{from{{opacity:.25}}to{{opacity:1}}}}
.fl{{opacity:0;animation:fl 5s linear infinite}}@keyframes fl{{0%,96%,100%{{opacity:0}}97%{{opacity:1}}}}
.beam{{animation:beam 6s ease-in-out infinite alternate}}@keyframes beam{{from{{opacity:.25}}to{{opacity:.6}}}}"""]
    g_svg = []
    for i, g in enumerate(groups):
        if g:
            g_svg.append(f'<path class="g" style="animation-delay:{i * wave_cycle * 0.55 / buckets:.2f}s" d="{"".join(g)}"/>')
    l_svg = []
    for (x, y, s, c) in lights:
        l_svg.append(f'<circle class="ph" cx="{f(x)}" cy="{f(y)}" r="{f(max(0.9, s * 0.45))}" fill="{c}" '
                     f'style="animation-delay:-{rng.uniform(0, 3):.1f}s"/>')
    flashes = []
    for _ in range(46):
        x, yy = rng.uniform(10, W - 10), rng.uniform(40, 215)
        flashes.append(f'<circle class="fl" cx="{f(x)}" cy="{f(yy)}" r="{rng.uniform(1.4, 2.8):.1f}" fill="#fff" '
                       f'style="animation-delay:{rng.uniform(0, 5):.2f}s;animation-duration:{rng.uniform(3.5, 7):.1f}s"/>')
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="A floodlit crowd doing a Mexican wave">
<title>The Crowd</title>
<style>{''.join(css)}</style>
<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0a1222"/><stop offset="1" stop-color="{BG}"/></linearGradient>
<linearGradient id="bm" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#cfefff" stop-opacity=".35"/><stop offset="1" stop-color="#cfefff" stop-opacity="0"/></linearGradient>
<linearGradient id="turf" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0b2a1a"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>
<rect width="{W}" height="{H}" fill="url(#sky)"/>
<polygon class="beam" points="70,0 110,0 420,230 -60,230" fill="url(#bm)"/>
<polygon class="beam" style="animation-delay:-3s" points="1090,0 1130,0 1260,230 780,230" fill="url(#bm)"/>
<rect x="60" y="0" width="60" height="7" rx="2" fill="#e9fbff"/><rect x="1080" y="0" width="60" height="7" rx="2" fill="#e9fbff"/>
{''.join(g_svg)}
{''.join(l_svg)}
{''.join(flashes)}
<rect x="0" y="224" width="{W}" height="4" fill="{RED}" opacity=".7"/>
<rect x="0" y="228" width="{W}" height="{H - 228}" fill="url(#turf)"/>
<path d="M0 262H{W}" stroke="{LINE}" stroke-width="1.2"/>
<text x="40" y="288" font-family="{MONO}" font-size="10" letter-spacing="4" fill="#3b4558">FULL-TIME · AARAV 4 – 3 BUGS FC</text>
<text x="{W - 40}" y="288" text-anchor="end" font-family="{MONO}" font-size="10" letter-spacing="4" fill="#3b4558">THE WAVE NEVER STOPS</text>
</svg>"""
    (OUT / "crowd.svg").write_text(svg)


if __name__ == "__main__":
    header()
    scoreboard()
    divider()
    crowd()
    for p in sorted(OUT.glob("*.svg")):
        print(f"{p.name:20s} {p.stat().st_size / 1024:7.1f} KB")
