"""Figures for the Skeletal Muscle chapter.

Run:  cd site/scripts && MPLCONFIGDIR=$TMPDIR PNG_PREVIEW=<folder> python3 figs_skeletal_muscle.py
Writes SVGs to ../muscle/figures/skeletal-muscle/.

Sarcomere geometry uses a thick filament of 1.6 um and thin filaments of 1.0 um, so the
plateau of the length-tension curve falls between 2.0 and 2.2 um, the course's optimal range.
"""
import math
import numpy as np
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle, Ellipse, FancyArrowPatch, Polygon, Arc

import figstyle as fs

plt = fs.plt
C = fs.C
M = fs.MINUS
PART, SLUG = "muscle", "skeletal-muscle"

ACTIN = C["arterial"]
MYOSIN = C["venous"]
CA = C["gold"]
NA = C["arterial"]
ACH = C["green"]
SR = "#e8d9ec"
TT = "#dbe7ec"

THICK, THIN, BARE = 1.6, 1.0, 0.2


def save(fig, name):
    fs.save(fig, PART, SLUG, name)


def arrow(ax, x0, y0, x1, y1, color, lw=1.6, z=5, style="-|>", ms=12):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle=style, mutation_scale=ms, color=color, lw=lw, zorder=z,
                                 shrinkA=0, shrinkB=0))


def num(ax, x, y, n, r=0.28, fsz=9):
    ax.add_patch(Circle((x, y), r, fc="white", ec=C["ink"], lw=1, zorder=8))
    ax.text(x, y, str(n), ha="center", va="center", fontsize=fsz, color=C["ink"], zorder=9)


# ------------------------------------------------------------------ 1. Sarcomere bands
def draw_sarcomere(ax, L, y0, xoff):
    """One sarcomere of length L (um) starting at Z = xoff, with half of each neighbor."""
    rows = [y0 + d for d in (-0.36, -0.12, 0.12, 0.36)]
    zs = [xoff - L, xoff, xoff + L, xoff + 2 * L]
    lo, hi = xoff - 0.75, xoff + L + 0.75
    # thick filaments, centered between Z lines
    for zl in zs[:-1]:
        mid = zl + L / 2
        a, b = mid - THICK / 2, mid + THICK / 2
        a2, b2 = max(a, lo), min(b, hi)
        if a2 >= b2:
            continue
        for y in (y0 - 0.24, y0, y0 + 0.24):
            ax.plot([a2, b2], [y, y], color=MYOSIN, lw=4.2, solid_capstyle="butt", zorder=3)
            for x in np.arange(a + 0.06, b, 0.1):
                if abs(x - mid) < BARE / 2 or x < lo or x > hi:
                    continue
                d = 1 if x > mid else -1
                for s in (1, -1):
                    ax.plot([x, x + d * 0.04], [y + s * 0.03, y + s * 0.085], color=MYOSIN, lw=1.0, zorder=3)
        if lo < mid < hi:
            ax.plot([mid, mid], [y0 - 0.48, y0 + 0.48], color=C["ink"], lw=1.2, zorder=4)
    # thin filaments from each Z line
    for zl in zs:
        for d in (1, -1):
            a, b = zl, zl + d * THIN
            a2, b2 = sorted((a, b))
            a2, b2 = max(a2, lo), min(b2, hi)
            if a2 >= b2:
                continue
            for y in rows:
                ax.plot([a2, b2], [y, y], color=ACTIN, lw=1.6, zorder=2)
        if lo <= zl <= hi:
            zz = np.linspace(y0 - 0.52, y0 + 0.52, 9)
            ax.plot(zl + 0.04 * np.array([(-1) ** i for i in range(9)]), zz, color=C["ink"], lw=2.0, zorder=4)


def bracket(ax, x0, x1, y, label, color, up=True, fsz=9):
    h = 0.08 if up else -0.08
    ax.plot([x0, x0, x1, x1], [y - h, y, y, y - h], color=color, lw=1.1)
    ax.text((x0 + x1) / 2, y + (0.06 if up else -0.06), label, ha="center", va="bottom" if up else "top", fontsize=fsz, color=color)


def fig_sarcomere():
    fig, ax = plt.subplots(figsize=(10.0, 5.8))
    ax.set_xlim(-1.0, 4.0)
    ax.set_ylim(-1.55, 3.75)
    ax.set_aspect("equal")
    ax.axis("off")
    for L, y0, title in ((2.6, 2.3, "Relaxed: sarcomere 2.6 µm"), (2.1, -0.15, "Contracted: sarcomere 2.1 µm")):
        xoff = 0.2
        draw_sarcomere(ax, L, y0, xoff)
        ax.text(-0.95, y0 + 1.3, title, fontsize=10.5, fontweight="bold", color=C["ink"], va="bottom")
        mid = xoff + L / 2
        bracket(ax, xoff, xoff + L, y0 + 0.78, "sarcomere (Z line to Z line)", C["ink"])
        bracket(ax, mid - THICK / 2, mid + THICK / 2, y0 - 0.7, "A band (constant)", MYOSIN, up=False)
        hz = L - 2 * THIN
        if hz > 0.05:
            bracket(ax, mid - hz / 2, mid + hz / 2, y0 + 0.56, "H zone", C["purple"], fsz=8.5)
        else:
            ax.text(mid, y0 + 0.6, "H zone nearly gone", ha="center", va="bottom", fontsize=8.5, color=C["purple"])
        ib = (L - THICK) / 2
        bracket(ax, xoff + L - ib, xoff + L + ib, y0 - 0.7, "I band", ACTIN, up=False)
        ax.text(xoff, y0 - 0.62, "Z", ha="center", va="top", fontsize=9, color=C["ink"])
    ax.text(3.95, 3.55, "thick filament (myosin)", ha="right", fontsize=9, color=MYOSIN)
    ax.text(3.95, 3.3, "thin filament (actin)", ha="right", fontsize=9, color=ACTIN)
    ax.text(-0.95, -1.5, "The filaments keep their length. The thin filaments slide toward the M line, so the I band and H zone shorten.",
            fontsize=9, color=C["text"])
    save(fig, "sarcomere.svg")


# ------------------------------------------------------------------ 2. Neuromuscular junction
def fig_nmj():
    fig, ax = plt.subplots(figsize=(10.6, 6.0))
    ax.set_xlim(0, 17.6)
    ax.set_ylim(0, 10)
    ax.set_aspect("equal")
    ax.axis("off")
    # axon and terminal
    ax.add_patch(Rectangle((3.6, 7.4), 1.2, 2.6, fc="#f3eee2", ec=C["ink"], lw=1.2, zorder=2))
    ax.add_patch(FancyBboxPatch((1.2, 4.9), 6.0, 2.8, boxstyle="round,pad=0.05,rounding_size=1.2", fc="#f3eee2", ec=C["ink"], lw=1.2, zorder=1))
    ax.add_patch(Rectangle((3.65, 7.3), 1.1, 0.6, fc="#f3eee2", ec="none", zorder=3))
    ax.text(4.95, 9.4, "motor neuron\naxon", fontsize=8.8, color=C["text"], va="center")
    # action potential arrow
    arrow(ax, 4.2, 9.8, 4.2, 7.9, C["muscle"], lw=2)
    num(ax, 3.2, 9.0, 1)
    # vesicles
    rng = np.random.default_rng(2)
    for x, y in ((2.2, 6.2), (2.9, 6.6), (3.7, 6.1), (4.5, 6.6), (5.3, 6.15), (6.0, 6.55), (3.1, 5.55), (5.0, 5.55)):
        ax.add_patch(Circle((x, y), 0.3, fc="white", ec=C["ink"], lw=0.9, zorder=3))
        for _ in range(5):
            dx, dy = rng.uniform(-0.15, 0.15, 2)
            ax.add_patch(Circle((x + dx, y + dy), 0.04, fc=ACH, ec="none", zorder=4))
    ax.text(7.5, 6.9, "vesicles of ACh\n(quanta)", fontsize=8.8, color=C["text"], va="center")
    # fusing vesicle and released ACh
    ax.add_patch(Arc((4.1, 4.92), 0.7, 0.6, theta1=0, theta2=180, ec=C["ink"], lw=0.9, zorder=3))
    for _ in range(14):
        ax.add_patch(Circle((4.1 + rng.uniform(-0.9, 0.9), rng.uniform(3.6, 4.7)), 0.05, fc=ACH, ec="none", zorder=4))
    num(ax, 3.1, 4.95 + 0.0, 3) if False else None
    # Ca channel on terminal
    ax.add_patch(Rectangle((5.95, 4.75), 0.35, 0.35, fc=C["gold"], ec=C["ink"], lw=0.8, zorder=4))
    arrow(ax, 6.12, 3.95, 6.12, 5.45, CA, lw=1.6, z=6)
    ax.text(6.35, 4.25, "Ca$^{2+}$", fontsize=9, color=CA)
    # muscle membrane with junctional folds
    xs = np.linspace(0.4, 8.0, 800)
    base = 3.4
    phase = ((xs - 0.4) % 1.3) / 1.3
    folds = base - 1.5 * np.clip(1 - ((phase - 0.5) / 0.12) ** 2, 0, 1) ** 0.5
    ax.fill_between(xs, 0.2, folds, color="#f6e3df", zorder=1)
    ax.plot(xs, folds, color=C["ink"], lw=1.2, zorder=2)
    ax.text(0.5, 0.45, "muscle fiber", fontsize=9, color=C["text"])
    ax.text(8.2, 3.9, "synaptic cleft\n50 to 100 nm", fontsize=8.8, color=C["text"], va="center")
    # AChRs at the crests
    crest = xs[(folds > base - 0.01)]
    for x in np.arange(1.0, 7.8, 0.42):
        if np.interp(x, xs, folds) > base - 0.01:
            ax.add_patch(Rectangle((x - 0.1, base - 0.2), 0.2, 0.32, fc=ACH, ec=C["ink"], lw=0.6, zorder=4))
    # Na+ entry and EPP
    rx = [x for x in np.arange(1.0, 7.8, 0.42) if np.interp(x, xs, folds) > base - 0.01]
    xna = min(rx, key=lambda v: abs(v - 4.4))
    arrow(ax, xna, 4.2, xna, 2.5, NA, lw=1.8, z=6)
    ax.text(xna + 0.15, 2.6, "Na$^+$", fontsize=9, color=NA)
    # voltage-gated Na channels deep in a fold
    for x in (2.35, 6.25):
        for d in (-1, 1):
            ax.add_patch(Rectangle((x + d * 0.13 - 0.07, 2.25), 0.14, 0.28, fc=C["purple"], ec=C["ink"], lw=0.6, zorder=4))
    ax.text(2.6, 1.0, "voltage-gated Na$^+$ channels in the folds", fontsize=8.5, color=C["purple"])
    # AChE
    ax.add_patch(Ellipse((1.5, 3.8), 0.45, 0.25, fc=C["gray"], ec="none", zorder=4))
    ax.text(1.5, 4.1, "AChE", fontsize=8.5, ha="center", color=C["gray"])
    # step numbers on the drawing
    num(ax, 6.8, 5.3, 2)
    num(ax, 3.3, 4.2, 3)
    num(ax, 2.45, 4.2, 4)
    num(ax, xna - 0.55, 2.45, 5)
    num(ax, 1.75, 1.6, 6)
    num(ax, 0.75, 4.25, 7)
    # legend
    steps = [
        "An action potential reaches the motor nerve terminal.",
        "Voltage-gated Ca$^{2+}$ channels open and Ca$^{2+}$ enters.",
        "Ca$^{2+}$ triggers the SNARE proteins to fuse\nvesicles with the membrane, releasing ACh.",
        "ACh binds nicotinic receptors on the crests of\nthe junctional folds (ligand-gated cation channels).",
        "Na$^+$ enters (some K$^+$ leaves): the end-plate\npotential (EPP).",
        "The EPP brings nearby membrane to threshold;\nvoltage-gated Na$^+$ channels fire the muscle\naction potential.",
        "Acetylcholinesterase splits ACh into acetate and\ncholine; the terminal takes choline back up.",
    ]
    y = 9.6
    for i, sline in enumerate(steps, 1):
        num(ax, 10.25, y - 0.12, i, r=0.26, fsz=8.5)
        ax.text(10.7, y, sline, fontsize=8.8, color=C["ink"], va="top")
        y -= 0.62 + 0.36 * sline.count("\n")
    save(fig, "nmj.svg")


# ------------------------------------------------------------------ 3. Triad and E-C coupling
def fig_triad():
    fig, ax = plt.subplots(figsize=(10.4, 5.6))
    ax.set_xlim(0, 18.5)
    ax.set_ylim(0, 10)
    ax.set_aspect("equal")
    ax.axis("off")
    # sarcolemma and T tubule
    ax.add_patch(Rectangle((0.3, 8.7), 9.4, 0.5, fc=TT, ec=C["ink"], lw=1.1))
    ax.text(9.65, 9.45, "sarcolemma", fontsize=9, color=C["text"], ha="right")
    ax.add_patch(Rectangle((4.35, 3.0), 1.3, 5.9, fc=TT, ec=C["ink"], lw=1.1))
    ax.add_patch(Rectangle((4.4, 8.6), 1.2, 0.4, fc=TT, ec="none"))
    ax.text(5.0, 2.55, "T tubule", fontsize=9, ha="center", color=C["text"])
    # AP traveling
    arrow(ax, 1.3, 9.0, 3.9, 9.0, C["muscle"], lw=1.8, z=6)
    arrow(ax, 5.0, 8.4, 5.0, 6.6, C["muscle"], lw=1.8, z=6)
    ax.text(1.3, 9.45, "action potential", fontsize=8.8, color=C["muscle"])
    num(ax, 0.75, 9.0, 1)
    # terminal cisternae
    for x0 in (1.6, 6.0):
        ax.add_patch(FancyBboxPatch((x0, 3.4), 2.4, 4.4, boxstyle="round,pad=0.05,rounding_size=0.7", fc=SR, ec=C["purple"], lw=1.2))
    ax.text(2.8, 7.95, "terminal\ncisterna (SR)", fontsize=8.6, ha="center", va="bottom", color=C["purple"])
    ax.text(7.2, 7.95, "terminal\ncisterna (SR)", fontsize=8.6, ha="center", va="bottom", color=C["purple"])
    # DHPR and RyR pairs on both sides
    for side in (-1, 1):
        for y in (6.6, 5.2):
            xd = 5.0 + side * 0.65
            ax.add_patch(Rectangle((xd - 0.18 if side > 0 else xd - 0.18, y - 0.3), 0.36, 0.6, fc=C["green"], ec=C["ink"], lw=0.8, zorder=5))
            xr = 5.0 + side * 1.2
            ax.add_patch(Rectangle((xr - 0.2, y - 0.38), 0.4, 0.76, fc=C["gold"], ec=C["ink"], lw=0.8, zorder=5))
            ax.plot([xd + side * 0.18, xr - side * 0.2], [y, y], color=C["ink"], lw=1.6, zorder=6)
    num(ax, 4.55, 7.7, 2)
    # Ca release
    rng = np.random.default_rng(1)
    for side in (-1, 1):
        x0 = 5.0 + side * 1.7
        arrow(ax, x0, 4.6, x0 + side * 0.2, 2.2, CA, lw=1.8, z=6)
        for _ in range(10):
            ax.add_patch(Circle((x0 + side * rng.uniform(0.2, 1.4), rng.uniform(3.8, 7.2)), 0.07, fc=CA, ec="none", zorder=4))
    num(ax, 7.4, 2.5, 3)
    ax.text(4.3, 1.5, "Ca$^{2+}$ floods the cytosol around the myofibrils", fontsize=8.8, ha="center", color=CA)
    # SERCA on longitudinal SR
    ax.add_patch(FancyBboxPatch((0.5, 0.25), 9.0, 0.6, boxstyle="round,pad=0.02,rounding_size=0.3", fc=SR, ec=C["purple"], lw=1.0))
    ax.add_patch(Rectangle((8.2, 0.12), 0.42, 0.86, fc=C["purple"], ec=C["ink"], lw=0.8))
    arrow(ax, 8.4, 2.0, 8.4, 1.0, CA, lw=1.4)
    ax.text(8.75, 1.35, "SERCA", fontsize=8.6, color=C["purple"])
    num(ax, 8.4, 2.45, 5)
    # legend
    leg = [("DHP receptor", C["green"]), ("ryanodine receptor (RyR1)", C["gold"]), ("mechanical link", C["ink"])]
    y = 9.5
    for lab, col in leg:
        ax.add_patch(Rectangle((10.4, y - 0.22), 0.4, 0.4, fc=col if col != C["ink"] else "white", ec=C["ink"], lw=0.8))
        if col == C["ink"]:
            ax.plot([10.4, 10.8], [y - 0.02, y - 0.02], color=C["ink"], lw=1.6)
        ax.text(11.0, y, lab, fontsize=8.8, va="center", color=C["ink"])
        y -= 0.6
    steps = [
        "The muscle action potential spreads along the\nsarcolemma and down the T tubules.",
        "Depolarization changes the shape of the DHP\nreceptor, which pulls open the RyR1 it touches.",
        "Ca$^{2+}$ leaves the SR down its gradient.",
        "Ca$^{2+}$ binds troponin C; tropomyosin moves off\nthe myosin-binding sites on actin; cross-bridges\ncycle.",
        "SERCA pumps Ca$^{2+}$ back into the SR (uses ATP),\nand the muscle relaxes.",
    ]
    y = 7.6
    for i, sline in enumerate(steps, 1):
        num(ax, 10.6, y - 0.12, i, r=0.26, fsz=8.5)
        ax.text(11.05, y, sline, fontsize=8.8, color=C["ink"], va="top")
        y -= 0.62 + 0.36 * sline.count("\n")
    save(fig, "triad.svg")


# ------------------------------------------------------------------ 4. Cross-bridge cycle
def cb_state(ax, cx, cy, angle, attached, nucleotide, title, sub, tropo=False):
    w = 3.2
    # actin above, thick filament below
    for i in range(9):
        ax.add_patch(Circle((cx - w / 2 + 0.2 + i * 0.35, cy + 0.95), 0.17, fc="#f1d6d6", ec=ACTIN, lw=0.8, zorder=2))
    ax.add_patch(Rectangle((cx - w / 2, cy - 0.95), w, 0.32, fc=MYOSIN, ec="none", zorder=2))
    ax.text(cx - w / 2 - 0.1, cy - 0.79, r"$\leftarrow$ M line", fontsize=7.5, color=MYOSIN, ha="right", va="center")
    # neck from thick filament
    nx, ny = cx - 0.2, cy - 0.63
    L = 0.85
    a = math.radians(angle)
    hx, hy = nx + L * math.cos(a), ny + L * math.sin(a)
    ax.plot([nx, hx], [ny, hy], color=MYOSIN, lw=3, zorder=3)
    gap = 0.0 if attached else -0.35
    head = Ellipse((hx, hy + 0.22 + gap), 0.95, 0.5, angle=0, fc="#cfe0ea", ec=MYOSIN, lw=1.4, zorder=4)
    ax.add_patch(head)
    if nucleotide:
        ax.text(hx, hy + 0.22 + gap, nucleotide, ha="center", va="center", fontsize=6.6, color=C["ink"], zorder=5)
    ax.text(cx, cy + 1.45, title, ha="center", va="bottom", fontsize=9.5, fontweight="bold", color=C["ink"])
    ax.text(cx, cy - 1.15, sub, ha="center", va="top", fontsize=8.5, color=C["text"])


def fig_crossbridge():
    fig, ax = plt.subplots(figsize=(10.4, 7.6))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 11.6)
    ax.set_aspect("equal")
    ax.axis("off")
    pos = {"A": (3.0, 9.0), "B": (13.0, 9.0), "C": (13.0, 2.6), "D": (3.0, 2.6), "E": (8.0, 5.8)}
    cb_state(ax, *pos["A"], 135, True, "", "A. Attached (rigor)", "head bound to actin,\nno nucleotide")
    cb_state(ax, *pos["B"], 135, False, "ATP", "B. Released", "ATP binds; head\nlets go of actin")
    cb_state(ax, *pos["C"], 70, False, "ADP·P$_i$", "C. Cocked", "ATP split; head\nre-cocked, still detached")
    cb_state(ax, *pos["D"], 70, True, "ADP·P$_i$", "D. Cross-bridge", "Ca$^{2+}$ has moved tropomyosin;\nhead binds actin")
    ax.add_patch(FancyBboxPatch((6.0, 4.75), 4.0, 2.2, boxstyle="round,pad=0.1,rounding_size=0.3", fc="white", ec=C["axis"], lw=1))
    ax.text(8.0, 6.55, "E. Power stroke", ha="center", fontsize=9.5, fontweight="bold", color=C["ink"])
    ax.text(8.0, 6.15, "P$_i$ leaves; the head tilts\nand pulls actin toward\nthe M line; ADP leaves", ha="center", va="top", fontsize=8.5, color=C["text"])

    def curved(p, q, rad, label, lx, ly, ha="center"):
        ax.add_patch(FancyArrowPatch(p, q, connectionstyle=f"arc3,rad={rad}", arrowstyle="-|>", mutation_scale=14,
                                     color=C["ink"], lw=1.4, zorder=6))
        ax.text(lx, ly, label, fontsize=8.6, color=C["ink"], ha=ha, va="center")
    curved((5.1, 9.6), (10.9, 9.6), -0.15, "ATP binds", 8.0, 10.55)
    curved((14.9, 7.4), (14.9, 4.2), -0.3, "ATP hydrolyzed", 15.4, 5.8, ha="left") if False else curved((14.6, 7.4), (14.6, 4.2), -0.3, "ATP\nhydrolyzed", 15.55, 5.8)
    curved((10.9, 2.0), (5.1, 2.0), -0.15, "binds actin", 8.0, 0.75)
    curved((1.4, 4.2), (6.0, 5.3), -0.25, "P$_i$ released", 2.2, 5.35, ha="right")
    curved((6.0, 6.5), (1.4, 7.4), -0.25, "ADP released", 2.2, 6.45, ha="right")
    ax.text(8.0, 3.85, "Without ATP the cycle stops at A: rigor.", ha="center", fontsize=8.6, color=C["muscle"]) if False else None
    save(fig, "crossbridge.svg")


# ------------------------------------------------------------------ 5. Twitch, summation, tetanus
def force_response(spikes, t, tau_a=30.0, tau_r=8.0, tau_f=25.0, K=1.0):
    A = np.zeros_like(t)
    for ts in spikes:
        s = np.clip(t - ts, 0, None)
        A += np.where(t >= ts, np.exp(-s / tau_a) - np.exp(-s / tau_r), 0)
    pk = max(np.exp(-x / tau_a) - np.exp(-x / tau_r) for x in np.linspace(0.01, 60, 3000))
    A /= pk
    S = A ** 2 / (A ** 2 + K ** 2)
    F = np.zeros_like(t)
    dt = t[1] - t[0]
    for i in range(1, len(t)):
        F[i] = F[i - 1] + dt * (S[i - 1] - F[i - 1]) / tau_f
    return F


def fig_twitch():
    t = np.arange(0, 1500, 0.5)
    trains = [("A. Single twitch", [50]), ("B. Summation", [330, 390]),
              ("C. Unfused tetanus", list(np.arange(620, 960, 60))), ("D. Fused tetanus", list(np.arange(1080, 1380, 10)))]
    spikes = [s for _, sp in trains for s in sp]
    F = force_response(spikes, t)
    tet = F.max()
    F = F / tet
    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(10.4, 5.6), sharex=True, gridspec_kw=dict(height_ratios=[3, 1]))
    fs.grid(ax)
    ax.plot(t, F, color=C["arterial"], lw=2.2)
    ax.set_ylim(0, 1.18)
    ax.set_ylabel("Force (fraction of\nfused tetanus)")
    for (title, sp), x in zip(trains, (40, 320, 610, 1070)):
        ax.text(x, 1.1, title, fontsize=9.5, fontweight="bold", color=C["ink"])
    tw = F[(t > 40) & (t < 280)]
    ax.annotate(f"one twitch: about {tw.max() * 100:.0f}%", xy=(t[(t > 40) & (t < 280)][tw.argmax()], tw.max()), xytext=(120, 0.5),
                fontsize=8.8, color=C["ink"], arrowprops=dict(arrowstyle="-", color=C["ink"], lw=0.8))
    ax2.set_ylim(-0.2, 1.4)
    ax2.set_yticks([])
    ax2.spines["left"].set_visible(False)
    for s in spikes:
        ax2.plot([s, s], [0, 1], color=C["ink"], lw=1.0)
    ax2.text(0, 1.25, "muscle action potentials (each lasts a few ms and is over long before the twitch peaks)", fontsize=8.8, color=C["text"], va="center")
    ax2.set_xlabel("Time (ms)")
    ax2.set_xlim(0, 1500)
    fig.subplots_adjust(hspace=0.08)
    save(fig, "twitch-tetanus.svg")
    return tw.max()


# ------------------------------------------------------------------ 6. Length-tension
def skeletal_active(L):
    pts = [(1.25, 0.0), (1.65, 0.82), (2.0, 1.0), (2.2, 1.0), (3.6, 0.0)]
    x, y = zip(*pts)
    return np.interp(L, x, y, left=0, right=0)


def fig_length_tension():
    L = np.linspace(1.2, 3.8, 600)
    act = skeletal_active(L)
    k = np.ones(25) / 25
    act = np.convolve(np.pad(act, 12, mode="edge"), k, mode="valid")
    pas = 0.03 * (np.exp((L - 2.55) / 0.33) - 1)
    pas = np.where(L > 2.55, pas, 0)
    Lc = np.linspace(1.7, 2.3, 200)
    cact = np.clip(1.0 - (np.clip(2.3 - Lc, 0, None) / 0.6) ** 1.6, 0, None)
    Lcp = np.linspace(1.9, 2.42, 200)
    cpas = 0.03 * (np.exp((Lcp - 1.9) / 0.13) - 1)
    keep = cpas < 1.15
    fig, ax = plt.subplots(figsize=(8.2, 5.2))
    fs.grid(ax)
    ax.axvspan(2.0, 2.2, color=C["highlight"], zorder=0)
    ax.plot(L, act, color=C["arterial"], lw=2.6)
    ax.plot(L[pas < 1.15], pas[pas < 1.15], color=C["arterial"], lw=1.8, ls=(0, (5, 3)))
    ax.plot(Lc, cact, color=C["venous"], lw=1.6, alpha=0.8)
    ax.plot(Lcp[keep], cpas[keep], color=C["venous"], lw=1.4, ls=(0, (5, 3)), alpha=0.8)
    ax.set_xlim(1.2, 3.8)
    ax.set_ylim(0, 1.2)
    ax.set_xlabel("Sarcomere length (µm)")
    ax.set_ylabel("Tension (fraction of maximum\nactive tension)")
    ax.text(2.1, 1.08, "optimal overlap\n2.0 to 2.2 µm", ha="center", fontsize=9, color="#8a5a1e")
    ax.text(2.55, 0.86, "Skeletal, active", color=C["arterial"], fontsize=10, fontweight="bold")
    ax.text(3.3, 0.95, "Skeletal,\npassive", color=C["arterial"], fontsize=9.5)
    ax.text(1.86, 0.45, "Cardiac,\nactive", color=C["venous"], fontsize=9.2, ha="right", va="center")
    ax.text(2.43, 0.33, "Cardiac,\npassive", color=C["venous"], fontsize=9.2, ha="left")
    ax.text(1.24, 0.98, "too much overlap:\nfilaments collide", fontsize=8.5, color=C["text"])
    ax.text(3.05, 0.5, "too little overlap:\nfewer cross-bridges", fontsize=8.5, color=C["text"])
    save(fig, "length-tension.svg")


# ------------------------------------------------------------------ 7. Muscle pump
def vein_panel(ax, contracted, title):
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 10)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, loc="center", fontsize=11)
    narrow = 0.55 if contracted else 0.0
    ys = np.linspace(0.5, 9.5, 300)
    squeeze = narrow * np.exp(-((ys - 5.0) / 1.5) ** 2)
    left = 2.2 + squeeze
    right = 3.8 - squeeze
    ax.fill_betweenx(ys, left, right, color="#d6e4ee", zorder=1)
    ax.plot(left, ys, color=C["venous"], lw=2)
    ax.plot(right, ys, color=C["venous"], lw=2)
    # muscles
    bulge = 0.5 if contracted else 0.0
    for side in (-1, 1):
        cx = 3.0 + side * (1.95 - 0.25 * bulge)
        ax.add_patch(Ellipse((cx, 5.0), 1.5 + 2 * bulge, 6.0, fc="#f2c9c3", ec=C["arterial"], lw=1.4, zorder=2))
        if contracted:
            arrow(ax, cx - side * 0.2, 5.0, cx - side * 0.75, 5.0, C["arterial"], lw=1.6, z=6)
    # valves: upper at y=8, lower at y=2
    def valve(y, open_):
        for side in (-1, 1):
            x0 = 2.2 if side < 0 else 3.8
            if open_:
                ax.plot([x0, x0 - side * (-0.3)], [y, y + 0.7], color=C["ink"], lw=2, zorder=4)
                ax.plot([x0, x0 + side * (-0.25)], [y, y + 0.7], color=C["ink"], lw=0) if False else None
            else:
                ax.plot([x0, 3.0 + side * 0.04], [y, y + 0.55], color=C["ink"], lw=2, zorder=4)
    if contracted:
        for side in (-1, 1):
            x0 = 2.2 if side < 0 else 3.8
            ax.plot([x0, x0 + (0.25 if side < 0 else -0.25)], [8.0, 8.75], color=C["ink"], lw=2, zorder=4)
        valve(2.0, False)
        arrow(ax, 3.0, 5.8, 3.0, 9.3, C["venous"], lw=2.2, z=6)
        arrow(ax, 3.0, 4.2, 3.0, 2.75, C["venous"], lw=1.4, z=6)
        ax.text(3.0, 9.65, "toward the heart", ha="center", fontsize=9, color=C["venous"])
        ax.text(3.0, 0.15, "lower valve shut: no backflow", ha="center", fontsize=8.5, color=C["ink"])
    else:
        valve(8.0, False)
        for side in (-1, 1):
            x0 = 2.2 if side < 0 else 3.8
            ax.plot([x0, x0 + (0.25 if side < 0 else -0.25)], [2.0, 2.75], color=C["ink"], lw=2, zorder=4)
        arrow(ax, 3.0, 0.6, 3.0, 4.2, C["venous"], lw=1.8, z=6)
        ax.text(3.0, 9.65, "upper valve shut", ha="center", fontsize=9, color=C["ink"])
        ax.text(3.0, 0.15, "vein refills from below", ha="center", fontsize=8.5, color=C["venous"])


def fig_muscle_pump():
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 5.6))
    vein_panel(axes[0], False, "A. Muscle relaxed")
    vein_panel(axes[1], True, "B. Muscle contracted")
    fig.subplots_adjust(wspace=0.05)
    save(fig, "muscle-pump.svg")


if __name__ == "__main__":
    fig_sarcomere()
    fig_nmj()
    fig_triad()
    fig_crossbridge()
    tw = fig_twitch()
    print("twitch fraction of fused tetanus: %.2f" % tw)
    fig_length_tension()
    fig_muscle_pump()
