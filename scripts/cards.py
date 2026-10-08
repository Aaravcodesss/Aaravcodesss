"""Generates the neon project cards for the 'Highlights reel' section.

Run:  python3 scripts/cards.py
"""
import math
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"
BG, PANEL, LINE = "#05070d", "#0a1020", "#1a2438"
BONE, MUTED = "#e8eef5", "#7f8ba0"
GREEN, CYAN, RED = "#39ff88", "#00e5ff", "#ff2a46"
SANS = "Inter,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,'SFMono-Regular',Menlo,Consolas,monospace"
W, H = 460, 250


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def card(slug, minute, title, lines, tags, accent, art):
    tag_svg, x = [], 28
    for t in tags:
        w = 14 + len(t) * 7.4
        tag_svg.append(f'<rect x="{x}" y="206" width="{w:.0f}" height="22" rx="11" fill="none" stroke="{LINE}"/>'
                       f'<text x="{x + w / 2:.0f}" y="221" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{MUTED}">{esc(t)}</text>')
        x += w + 8
    body = "".join(f'<text x="28" y="{118 + i * 21}" font-family="{SANS}" font-size="14" fill="#b9c4d4">{esc(l)}</text>'
                   for i, l in enumerate(lines))
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{esc(title)}">
<style>
.edge{{stroke-dasharray:1400;stroke-dashoffset:1400;animation:e 2.2s cubic-bezier(.65,0,.35,1) forwards}}
@keyframes e{{to{{stroke-dashoffset:0}}}}
.pulse{{animation:p 2.4s ease-in-out infinite alternate}}@keyframes p{{from{{opacity:.35}}to{{opacity:1}}}}
{art[1]}
</style>
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0d1730"/><stop offset="1" stop-color="{BG}"/></linearGradient>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" fill="url(#g)" stroke="{LINE}"/>
<rect class="edge" x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" fill="none" stroke="{accent}" stroke-width="1.6"/>
<g>{art[0]}</g>
<circle class="pulse" cx="34" cy="38" r="4.5" fill="{accent}"/>
<text x="46" y="43" font-family="{MONO}" font-size="12" letter-spacing="3" fill="{accent}">{minute}</text>
<text x="28" y="84" font-family="{SANS}" font-weight="900" font-style="italic" font-size="{30 if len(title) <= 13 else 26}" fill="{BONE}">{esc(title)}</text>
{body}
{''.join(tag_svg)}
</svg>"""
    (OUT / f"card-{slug}.svg").write_text(svg)


def art_tactics():
    # mini pitch with a passing triangle drawn in
    x0, y0, w, h = 300, 30, 135, 190
    s = [f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="4" fill="#0b2418" stroke="{GREEN}" stroke-opacity=".5"/>',
         f'<path d="M{x0} {y0 + h / 2}h{w}" stroke="{GREEN}" stroke-opacity=".5"/>',
         f'<circle cx="{x0 + w / 2}" cy="{y0 + h / 2}" r="20" fill="none" stroke="{GREEN}" stroke-opacity=".5"/>']
    pts = [(x0 + 30, y0 + 150), (x0 + 70, y0 + 110), (x0 + 40, y0 + 60), (x0 + 100, y0 + 40)]
    d = "M" + " L".join(f"{x} {y}" for x, y in pts)
    s.append(f'<path class="mv" d="{d}" fill="none" stroke="{CYAN}" stroke-width="2.4" stroke-dasharray="230" filter="url(#glow)"/>')
    for (x, y) in pts:
        s.append(f'<circle cx="{x}" cy="{y}" r="6" fill="{CYAN}" filter="url(#glow)"/>')
    css = ".mv{stroke-dashoffset:230;animation:mv 3.2s ease-in-out infinite}@keyframes mv{0%{stroke-dashoffset:230}55%,85%{stroke-dashoffset:0}100%{stroke-dashoffset:-230}}"
    return "".join(s), css


def art_penalty():
    gx, gy, gw, gh = 305, 100, 130, 72
    s = [f'<path d="M{gx} {gy + gh}V{gy}H{gx + gw}V{gy + gh}" fill="none" stroke="#f2fbff" stroke-width="3.5" filter="url(#glow)"/>']
    for i in range(1, 9):
        s.append(f'<path d="M{gx + gw * i / 9:.1f} {gy}v{gh}" stroke="#ffffff" stroke-opacity=".12"/>')
    for i in range(1, 5):
        s.append(f'<path d="M{gx} {gy + gh * i / 5:.1f}h{gw}" stroke="#ffffff" stroke-opacity=".12"/>')
    s.append(f'<g class="kp"><circle cx="{gx + gw / 2}" cy="{gy + 34}" r="6" fill="{RED}" filter="url(#glow)"/>'
             f'<rect x="{gx + gw / 2 - 6}" y="{gy + 42}" width="12" height="24" rx="4" fill="{RED}"/></g>')
    s.append(f'<circle class="bl" cx="{gx + gw / 2}" cy="{gy + gh + 42}" r="7" fill="#fff" filter="url(#glow)"/>')
    css = (".kp{animation:kp 3s ease-in-out infinite;transform-box:fill-box;transform-origin:center}"
           "@keyframes kp{0%,35%{transform:none}55%,85%{transform:translateX(-34px) rotate(-60deg)}100%{transform:none}}"
           ".bl{transform-box:fill-box;transform-origin:center;animation:bl 3s ease-in infinite}"
           "@keyframes bl{0%,30%{transform:none;opacity:1}50%{transform:translate(40px,-76px) scale(.6)}85%{transform:translate(40px,-76px) scale(.6);opacity:1}100%{opacity:0}}")
    return "".join(s), css


def art_sim():
    rng = random.Random(4)
    x0, y0 = 300, 40
    s = []
    vals = sorted([rng.uniform(0.15, 1) for _ in range(8)], reverse=True)
    for i, v in enumerate(vals):
        w = 130 * v
        col = CYAN if i < 2 else (RED if i > 5 else GREEN)
        s.append(f'<rect class="bar" style="animation-delay:{i * 0.12:.2f}s" x="{x0}" y="{y0 + i * 22}" width="{w:.0f}" height="12" rx="3" fill="{col}" fill-opacity=".85"/>')
    css = (".bar{transform-box:fill-box;transform-origin:left;animation:bar 4s cubic-bezier(.19,1,.22,1) infinite}"
           "@keyframes bar{0%{transform:scaleX(0)}30%,85%{transform:scaleX(1)}100%{transform:scaleX(0)}}")
    return "".join(s), css


if __name__ == "__main__":
    card("tactics-board", "WEB APP", "Tactics Board",
         ["Pick a formation, drag players,", "draw passes & runs — then share", "the lineup as a link or a PNG."],
         ["JavaScript", "SVG", "Pointer Events"], CYAN, art_tactics())
    card("penalty-shootout", "BROWSER GAME", "Penalty Shootout",
         ["A neon shootout where the keeper", "learns your habits with a Markov", "chain. Don't be predictable."],
         ["Canvas", "Web Audio", "AI"], RED, art_penalty())
    card("league-sim", "PYTHON · DATA", "league-sim",
         ["Simulates a football season 10,000", "times with Elo + Poisson to get", "title & relegation odds."],
         ["Python", "numpy", "Monte Carlo"], GREEN, art_sim())
    for p in sorted(OUT.glob("card-*.svg")):
        print(p.name)
