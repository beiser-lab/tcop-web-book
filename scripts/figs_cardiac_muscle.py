"""Figures for the Cardiac Muscle chapter (site/muscle/cardiac-muscle.qmd).

Run:  cd site/scripts && MPLCONFIGDIR=$TMPDIR PNG_PREVIEW=<folder> python3 figs_cardiac_muscle.py
All figures are schematics drawn for the book from the 2026 Cardiac Muscle lecture.
"""
import numpy as np
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, Ellipse, Polygon
import figstyle as fs

plt, C, M = fs.plt, fs.C, fs.MINUS
PART, SLUG = "muscle", "cardiac-muscle"
CA = C["arterial"]       # Ca2+ paths
SR_FC, SR_EC = "#e8dcef", C["purple"]
CELL_FC = "#fbf1ea"


def arrow(ax, x0, y0, x1, y1, color=None, lw=1.6, rad=0.0, style="-|>"):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle=style, color=color or C["ink"], lw=lw, shrinkA=1, shrinkB=1,
                                connectionstyle=f"arc3,rad={rad}"), zorder=6)


def badge(ax, x, y, n, color=None):
    ax.add_patch(Circle((x, y), 0.26, fc=color or C["ink"], ec="white", lw=1, zorder=8))
    ax.text(x, y, str(n), ha="center", va="center", color="white", fontsize=9, fontweight="bold", zorder=9)


# ------------------------------------------------------------------ 1. Intercalated disc
def fig_disc():
    fig, ax = plt.subplots(figsize=(9.0, 4.4))
    ax.set_xlim(0, 14); ax.set_ylim(-0.6, 6.1); ax.set_aspect("equal"); ax.axis("off")
    # stepped boundary between two cells: transverse segments (vertical) and longitudinal (horizontal)
    steps = [(6.2, 0.6), (6.2, 2.0), (7.4, 2.0), (7.4, 3.6), (6.6, 3.6), (6.6, 5.2)]
    xs = [p[0] for p in steps]; ys = [p[1] for p in steps]
    left = [(1.0, 0.6)] + steps + [(1.0, 5.2)]
    right = [(13.0, 0.6)] + steps + [(13.0, 5.2)]
    ax.add_patch(Polygon(left, closed=True, fc=CELL_FC, ec=C["ink"], lw=1.2))
    ax.add_patch(Polygon(right, closed=True, fc="#f3ebe3", ec=C["ink"], lw=1.2))
    # myofibril striations (Z lines) in each cell
    for x in np.arange(1.6, 6.0, 0.9):
        ax.plot([x, x], [0.75, 5.05], color=C["axis"], lw=0.8)
    for x in np.arange(7.9, 12.8, 0.9):
        ax.plot([x, x], [0.75, 5.05], color=C["axis"], lw=0.8)
    for y in (1.3, 2.8, 4.4):
        ax.plot([1.2, 6.1], [y, y], color="#e2b8a8", lw=3, alpha=0.6, solid_capstyle="butt")
        ax.plot([7.5, 12.8], [y, y], color="#e2b8a8", lw=3, alpha=0.6, solid_capstyle="butt")
    # transverse segments: adherens junctions (thick bars) and desmosomes (paired plaques)
    for (x, y0, y1) in ((6.2, 0.6, 2.0), (7.4, 2.0, 3.6), (6.6, 3.6, 5.2)):
        ax.plot([x, x], [y0 + 0.15, y1 - 0.15], color=C["green"], lw=5, solid_capstyle="butt", zorder=4)
        ym = (y0 + y1) / 2
        ax.add_patch(Rectangle((x - 0.2, ym - 0.12), 0.4, 0.24, fc=C["gold"], ec="white", lw=0.6, zorder=5))
    # longitudinal segments: gap junctions
    for (x0, x1, y) in ((6.2, 7.4, 2.0), (6.6, 7.4, 3.6)):
        for xg in np.linspace(x0 + 0.15, x1 - 0.15, 5):
            ax.add_patch(Rectangle((xg - 0.06, y - 0.12), 0.12, 0.24, fc=C["venous"], ec="white", lw=0.4, zorder=5))
    ax.text(3.5, 5.45, "Myocyte 1", ha="center", fontsize=10, color=C["ink"], fontweight="bold")
    ax.text(10.2, 5.45, "Myocyte 2", ha="center", fontsize=10, color=C["ink"], fontweight="bold")
    ax.annotate("transverse region:\nadherens junctions (green)\nand desmosomes (gold)",
                xy=(6.2, 1.0), xytext=(2.3, -0.55), fontsize=9, color=C["ink"],
                arrowprops=dict(arrowstyle="-", color=C["ink"], lw=0.8))
    ax.annotate("longitudinal region:\ngap junctions (blue)", xy=(7.0, 2.0), xytext=(9.3, -0.4),
                fontsize=9, color=C["venous"], arrowprops=dict(arrowstyle="-", color=C["venous"], lw=0.8))
    ax.annotate("", xy=(5.4, 5.5), xytext=(8.4, 5.5), arrowprops=dict(arrowstyle="<->", color=C["text"], lw=1))
    ax.text(6.9, 5.7, "long axis of the cells", ha="center", fontsize=8.5, color=C["text"])
    fs.save(fig, PART, SLUG, "intercalated-disc.svg")


# ------------------------------------------------------------------ 2. Dyad vs triad
def sarcomere_strip(ax, x0, x1, y0, y1, zlines, aw):
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc=CELL_FC, ec="none", zorder=0.4))
    ax.plot([x0, x1], [y1, y1], color=C["venous"], lw=2.2, zorder=1)   # sarcolemma
    ax.text(x1, y1 + 0.12, "sarcolemma", ha="right", fontsize=8, color=C["venous"])
    for za, zb in zip(zlines[:-1], zlines[1:]):
        m = (za + zb) / 2
        ax.add_patch(Rectangle((m - aw / 2, y0), aw, y1 - y0, fc="#ecd3c3", ec="none", zorder=0.6))
        ax.text(m, y0 - 0.3, "A band", ha="center", fontsize=8, color=C["text"])
    for z in zlines:
        ax.plot([z, z], [y0, y1 - 0.05], color=C["ink"], lw=1.4, zorder=0.8)
        ax.text(z, y0 - 0.3, "Z", ha="center", fontsize=8.5, color=C["ink"])


def ttubule(ax, x, w, y0, y1):
    ax.add_patch(Rectangle((x - w / 2, y0), w, y1 - y0, fc="white", ec=C["venous"], lw=1.2, zorder=3))
    ax.plot([x - w / 2, x + w / 2], [y1, y1], color=CELL_FC, lw=2.6, zorder=3.5)  # open to the outside


def cistern(ax, x, w, yc, h):
    ax.add_patch(FancyBboxPatch((x - w / 2, yc - h / 2), w, h, boxstyle="round,pad=0,rounding_size=0.1",
                                fc=SR_FC, ec=SR_EC, lw=1.1, zorder=2.5))


def fig_dyad():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.4, 4.6))
    for ax in (a1, a2):
        ax.set_xlim(0, 6.4); ax.set_ylim(-1.9, 4.3); ax.set_aspect("equal"); ax.axis("off")
    a1.set_title("A  Skeletal muscle: triad", loc="left")
    a2.set_title("B  Cardiac muscle: dyad", loc="left")
    z = [0.5, 3.2, 5.9]
    y0, y1 = 0.4, 3.6
    # skeletal: T-tubules at A-I junctions, two per sarcomere, a cisterna on each side
    sarcomere_strip(a1, 0.2, 6.2, y0, y1, z, 1.7)
    for zz in (0.5, 3.2):
        for xt in (zz + 0.5, zz + 2.2):
            ttubule(a1, xt, 0.1, y0 + 0.4, y1)
            cistern(a1, xt - 0.2, 0.22, 2.0, 2.2)
            cistern(a1, xt + 0.2, 0.22, 2.0, 2.2)
    for xa, xb in ((1.2, 2.5), (3.9, 5.2), (0.2, 0.8), (2.9, 3.5), (5.6, 6.2)):
        for yy in (1.4, 2.0, 2.6):
            a1.plot([xa + 0.12, xb - 0.12], [yy, yy], color=SR_EC, lw=0.8, zorder=2.4)
    a1.text(3.2, -0.85, "Two T-tubules per sarcomere, at the A-I junctions.\nEach has an SR cisterna on both sides.",
            ha="center", fontsize=8.8, color=C["ink"], va="top")
    # cardiac: wider T-tubules at the Z lines, one cisterna beside each
    sarcomere_strip(a2, 0.2, 6.2, y0, y1, z, 1.7)
    for xt in z:
        ttubule(a2, xt, 0.3, y0 + 0.4, y1)
        if xt < 5.5:
            cistern(a2, xt + 0.33, 0.24, 2.0, 1.4)
    for xa, xb in ((0.83, 3.2), (3.53, 5.9)):
        for yy in (1.6, 2.4):
            a2.plot([xa + 0.1, xb - 0.2], [yy, yy], color=SR_EC, lw=0.8, zorder=2.4)
    a2.text(3.2, -0.85, "One wider T-tubule per sarcomere, at the Z line,\nwith a single SR cisterna beside it.",
            ha="center", fontsize=8.8, color=C["ink"], va="top")
    a1.annotate("T-tubule", xy=(1.0, 3.3), xytext=(0.2, 4.05), fontsize=8.5, color=C["venous"],
                arrowprops=dict(arrowstyle="-", color=C["venous"], lw=0.7))
    a1.annotate("SR cisternae", xy=(2.95, 3.0), xytext=(2.3, 4.05), fontsize=8.5, color=SR_EC,
                arrowprops=dict(arrowstyle="-", color=SR_EC, lw=0.7))
    a2.annotate("T-tubule", xy=(3.2, 3.3), xytext=(2.0, 4.05), fontsize=8.5, color=C["venous"],
                arrowprops=dict(arrowstyle="-", color=C["venous"], lw=0.7))
    a2.annotate("SR cisterna", xy=(3.55, 2.65), xytext=(3.7, 4.05), fontsize=8.5, color=SR_EC,
                arrowprops=dict(arrowstyle="-", color=SR_EC, lw=0.7))
    fs.save(fig, PART, SLUG, "dyad-triad.svg")


# ------------------------------------------------------------------ 3. Ca2+ cycle in the myocyte
def fig_calcium():
    fig, ax = plt.subplots(figsize=(9.4, 6.4))
    ax.set_xlim(0, 15); ax.set_ylim(0, 10.2); ax.set_aspect("equal"); ax.axis("off")
    # cell outline with a T-tubule invagination on the left
    cell = [(0.6, 9.0), (14.4, 9.0), (14.4, 0.6), (3.0, 0.6), (3.0, 7.6), (2.2, 7.6), (2.2, 0.6), (0.6, 0.6)]
    ax.add_patch(Polygon(cell, closed=True, fc=CELL_FC, ec=C["venous"], lw=2.4, zorder=1))
    ax.add_patch(Rectangle((2.2, 0.0), 0.8, 7.6, fc="#e6eef3", ec="none", zorder=1.5))
    ax.plot([2.2, 2.2, 3.0, 3.0], [0.6, 7.6, 7.6, 0.6], color=C["venous"], lw=2.4, zorder=2)
    ax.plot([0.6, 2.2], [0.6, 0.6], color=C["venous"], lw=2.4, zorder=2)
    ax.plot([3.0, 14.4], [0.6, 0.6], color=C["venous"], lw=2.4, zorder=2)
    ax.text(2.6, 0.25, "T-tubule", ha="center", fontsize=8.5, color=C["venous"])
    ax.text(5.0, 9.4, "extracellular fluid", ha="center", fontsize=9, color=C["text"])
    ax.text(2.6, 4.2, "Ca²⁺", ha="center", fontsize=8.5, color=CA, rotation=90)
    # L-type channel in T-tubule wall
    ax.add_patch(Rectangle((2.92, 5.6), 0.22, 0.7, fc=C["gold"], ec=C["ink"], lw=0.8, zorder=5))
    ax.text(2.0, 6.85, "L-type Ca²⁺\nchannel", ha="right", fontsize=8.5, color=C["ink"])
    # SR
    sr = Ellipse((6.0, 5.95), 4.6, 1.4, fc=SR_FC, ec=SR_EC, lw=1.4, zorder=3)
    ax.add_patch(sr)
    ax.text(6.4, 6.0, "SR", ha="center", va="center", fontsize=11, fontweight="bold", color=SR_EC, zorder=4)
    ax.add_patch(Rectangle((3.65, 5.6), 0.3, 0.7, fc=C["purple"], ec="white", lw=0.8, zorder=5))
    ax.text(3.8, 6.55, "RyR2", ha="center", fontsize=8.5, color=C["purple"], zorder=6)
    ax.add_patch(Rectangle((8.08, 5.6), 0.36, 0.7, fc=C["green"], ec="white", lw=0.8, zorder=5))
    ax.text(8.3, 5.05, "SERCA + PLB", ha="center", fontsize=8.5, color=C["green"], zorder=6)
    # myofilaments
    ax.add_patch(FancyBboxPatch((5.2, 1.6), 3.6, 1.4, boxstyle="round,pad=0.02,rounding_size=0.15",
                                fc="white", ec=C["ink"], lw=1.0, zorder=3))
    for y in (2.0, 2.3, 2.6):
        ax.plot([5.4, 7.0], [y, y], color=CA, lw=1.2, zorder=4)
        ax.plot([7.0, 8.6], [y + 0.12, y + 0.12], color=CA, lw=1.2, zorder=4)
        ax.plot([6.1, 7.9], [y + 0.06, y + 0.06], color=C["purple"], lw=2.4, zorder=4)
    ax.text(7.0, 1.3, "myofilaments (troponin C)", ha="center", fontsize=8.5, color=C["ink"])
    # mitochondrion
    ax.add_patch(Ellipse((12.4, 2.4), 2.4, 1.2, fc="#f2dfc6", ec=C["gold"], lw=1.2, zorder=3))
    ax.text(12.4, 2.4, "mitochondrion", ha="center", va="center", fontsize=8.5, color=C["ink"], zorder=4)
    # surface membrane transporters
    ax.add_patch(Circle((10.4, 9.0), 0.42, fc="#d7ecd9", ec=C["green"], lw=1.2, zorder=5))
    ax.text(10.4, 9.0, "NCX", ha="center", va="center", fontsize=8.5, color=C["green"], zorder=6)
    ax.add_patch(Circle((12.8, 9.0), 0.42, fc="#f6e3c9", ec=C["gold"], lw=1.2, zorder=5))
    ax.text(12.8, 9.0, "Na⁺/K⁺\npump", ha="center", va="center", fontsize=7, color=C["ink"], zorder=6)
    ax.text(10.4, 9.75, "3 Na⁺ in, 1 Ca²⁺ out", ha="center", fontsize=8, color=C["green"])
    ax.text(13.3, 9.75, "3 Na⁺ out, 2 K⁺ in", ha="center", fontsize=8, color=C["gold"])
    ax.text(9.6, 7.45, "Ca²⁺", ha="center", fontsize=10, color=CA, fontweight="bold")

    # Ca2+ arrows
    arrow(ax, 2.6, 5.95, 3.55, 5.95, color=CA, lw=2.0)                 # 2 entry
    badge(ax, 3.25, 6.55, 2)
    arrow(ax, 4.0, 5.3, 5.6, 3.15, color=CA, lw=2.4)                   # 3/4 release to filaments
    badge(ax, 4.35, 4.35, 4)
    badge(ax, 3.8, 7.15, 3)
    badge(ax, 5.9, 3.65, 5)
    arrow(ax, 8.9, 2.6, 9.5, 7.2, color=CA, lw=1.6, rad=0.15)          # Ca leaves filaments
    arrow(ax, 9.2, 7.3, 8.5, 6.35, color=C["green"], lw=2.2)           # back to SR
    ax.text(8.15, 6.75, "70%", fontsize=10, fontweight="bold", color=C["green"])
    arrow(ax, 9.9, 7.6, 10.25, 8.55, color=C["green"], lw=2.0)        # out via NCX
    ax.text(10.0, 8.05, "28%", fontsize=10, fontweight="bold", color=C["green"], ha="right")
    arrow(ax, 9.9, 7.25, 11.6, 3.0, color=C["green"], lw=1.4, rad=-0.1)  # to mitochondria
    ax.text(10.55, 4.4, "2%", fontsize=10, fontweight="bold", color=C["green"])
    ax.add_patch(Circle((10.2, 0.6), 0.38, fc="#d7ecd9", ec=C["green"], lw=1.2, zorder=5))
    ax.text(10.2, 0.6, "ATP", ha="center", va="center", fontsize=7.5, color=C["green"], zorder=6)
    ax.text(10.75, 0.15, "sarcolemmal Ca²⁺ pump", ha="left", fontsize=8, color=C["green"])
    arrow(ax, 9.75, 7.2, 10.1, 1.02, color=C["green"], lw=1.2)
    badge(ax, 9.0, 8.1, 6, color=C["green"])
    badge(ax, 1.5, 8.4, 1)
    ax.text(1.85, 8.4, "action potential", fontsize=8.5, color=C["ink"], va="center")
    fs.save(fig, PART, SLUG, "calcium-cycle.svg")


# ------------------------------------------------------------------ 4. Action potentials
def smooth_step(t, t0, t1):
    u = np.clip((t - t0) / (t1 - t0), 0, 1)
    return u * u * (3 - 2 * u)


def ventricular_ap(t, t0=50):
    v = np.full_like(t, -90.0)
    up = (t >= t0) & (t < t0 + 2)
    v[up] = -90 + 110 * (t[up] - t0) / 2
    after = t >= t0 + 2
    tt = t[after] - (t0 + 2)
    notch = 20 - 15 * smooth_step(tt, 0, 10)                 # phase 1 to +5
    plateau = 5 - 10 * smooth_step(tt, 10, 200)               # slow drift to -5
    v_after = np.where(tt < 10, notch, plateau)
    rep = smooth_step(tt, 200, 290)
    v_after = v_after * (1 - rep) + (-90) * rep
    v[after] = v_after
    return v


def pacemaker_ap(t, slope, start=-60, thr=-40, t_start=0, n=3):
    """Slow-response AP train: linear phase 4 from 'start' to threshold, slow upstroke, repolarization."""
    v = np.full_like(t, np.nan)
    tc = t_start
    for _ in range(n):
        t4 = (thr - start) / slope                      # duration of phase 4
        seg = (t >= tc) & (t < tc + t4)
        v[seg] = start + slope * (t[seg] - tc)
        tu = tc + t4
        seg = (t >= tu) & (t < tu + 40)                 # phase 0
        v[seg] = thr + 50 * smooth_step(t[seg], tu, tu + 40)
        tr = tu + 40
        seg = (t >= tr) & (t < tr + 130)                # phase 3
        v[seg] = 10 + (start - 10) * smooth_step(t[seg], tr, tr + 130)
        tc = tr + 130
    return v


def fig_ap():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.6, 4.3), sharey=True)
    t = np.linspace(0, 1300, 6000)
    base = pacemaker_ap(t, 0.04, start=-60, n=1)
    symp = pacemaker_ap(t, 0.075, start=-60, n=1)
    para = pacemaker_ap(t, 0.025, start=-65, n=1)
    a1.plot(t, para, color=C["venous"], lw=1.6, ls=(0, (4, 2)), label="parasympathetic (ACh)")
    a1.plot(t, symp, color=C["arterial"], lw=1.6, ls=(0, (4, 2)), label="sympathetic (NE)")
    a1.plot(t, base, color=C["ink"], lw=2.2, label="baseline")
    a1.axhline(-40, color=C["axis"], lw=0.8, ls=":")
    a1.text(760, -38, "threshold", ha="center", fontsize=8.5, color=C["text"])
    a1.set_xlim(0, 1300)
    a1.set_title("A  Pacemaker cell (SA node): slow response")
    a1.text(250, -70, "phase 4", fontsize=8.5, color=C["ink"], ha="center")
    a1.text(478, -15, "0", fontsize=9, color=C["ink"], ha="right")
    a1.text(640, -25, "3", fontsize=9, color=C["ink"])
    a1.legend(loc="upper right", fontsize=8.5, bbox_to_anchor=(1.0, 1.0))
    a1.set_ylabel("Membrane potential (mV)")
    a1.set_xlabel("Time (ms)")

    t2 = np.linspace(0, 450, 3000)
    v = ventricular_ap(t2)
    a2.plot(t2, v, color=C["ventricular"], lw=2.2)
    a2.set_xlim(0, 450)
    a2.set_title("B  Ventricular myocyte: fast response")
    for x, y, lab in ((44, -20, "0"), (60, 23, "1"), (160, 9, "2"), (320, -50, "3"), (400, -86, "4")):
        a2.text(x, y, lab, fontsize=9, color=C["ink"], ha="center")
    a2.annotate("", xy=(52, 32), xytext=(305, 32), arrowprops=dict(arrowstyle="<->", color=C["ink"], lw=1))
    a2.text(178, 35, "absolute refractory period", ha="center", fontsize=8.5, color=C["ink"])
    a2.annotate("", xy=(305, 32), xytext=(345, 32), arrowprops=dict(arrowstyle="<->", color=C["gray"], lw=1))
    a2.text(335, 40, "relative", ha="left", fontsize=8.5, color=C["gray"])
    a2.set_xlabel("Time (ms)")
    for ax in (a1, a2):
        ax.set_ylim(-100, 50)
        ax.set_yticks([-90, -60, -30, 0, 30])
        ax.set_yticklabels([fs.fmt(x) for x in (-90, -60, -30, 0, 30)])
        fs.grid(ax)
    fs.save(fig, PART, SLUG, "action-potentials.svg")


# ------------------------------------------------------------------ 5. Length-tension, skeletal vs cardiac
def fig_length_tension():
    CD = C["venous"]   # cardiac color, as in the Skeletal Muscle chapter's comparison
    # Course decision 2026-11-18: cardiac curve only; the skeletal curve lives in the Skeletal Muscle chapter.
    card_L = np.linspace(1.6, 2.3, 300)
    card = np.clip((card_L - 1.65) / (2.3 - 1.65), 0, 1) ** 1.6
    cp_L = np.linspace(1.9, 2.36, 200)
    cpass = 0.03 * (np.exp((cp_L - 1.9) / 0.12) - 1)
    fig, ax = plt.subplots(figsize=(6.6, 4.6))
    ax.axvspan(1.8, 2.3, color=C["cool"], lw=0, zorder=0)
    ax.text(2.05, 1.3, "working range\nof the heart", ha="center", fontsize=8.5, color=CD)
    ax.plot(card_L, card, color=CD, lw=2.4)
    ax.plot(cp_L, cpass, color=CD, lw=1.8, ls=(0, (4, 2)))
    ax.text(1.93, 0.42, "active", fontsize=9.5, color=CD, ha="right")
    ax.text(2.4, 1.22, "passive", fontsize=9.5, color=CD, ha="left")
    ax.annotate("passive stiffness rises steeply,\nso the heart rarely works\npast the top of its curve",
                xy=(2.3, 0.95), xytext=(2.42, 0.45), fontsize=8.5, color=C["ink"],
                arrowprops=dict(arrowstyle="-", color=C["ink"], lw=0.8))
    ax.set_xlim(1.5, 2.9); ax.set_ylim(0, 1.45)
    ax.set_xlabel("Sarcomere length (µm)")
    ax.set_xticks([1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8])
    ax.set_ylabel("Tension (fraction of maximum active)")
    fs.grid(ax)
    fs.save(fig, PART, SLUG, "length-tension.svg")


# ------------------------------------------------------------------ 6. Ca sensitivity and Frank-Starling
def fig_starling():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.6, 4.3))
    pca = np.linspace(7.5, 4.5, 400)
    for p50, col, lab, ls in ((6.15, C["ink"], "short sarcomere (1.9 µm)", "-"),
                              (6.35, C["ventricular"], "stretched sarcomere (2.5 µm)", "-")):
        f = 1 / (1 + 10 ** (3.5 * (pca - p50)))
        a1.plot(pca, f, color=col, lw=2.2, ls=ls, label=lab)
    a1.set_xlim(7.5, 4.5)
    a1.set_xlabel("pCa  (higher [Ca²⁺] to the right)")
    a1.set_ylabel("Force (fraction of maximum)")
    a1.set_title("A  Stretch raises Ca²⁺ sensitivity")
    a1.legend(loc="lower right", fontsize=8.5)
    a1.set_ylim(0, 1.08)
    fs.grid(a1)

    edv = np.linspace(50, 250, 400)
    def sv(e, smax):
        return smax * (1 - np.exp(-(e - 50) / 70))
    a2.plot(edv, sv(edv, 100), color=C["ventricular"], lw=2.4)
    a2.plot(edv, sv(edv, 130), color=C["arterial"], lw=1.8, ls=(0, (5, 2)))
    a2.plot(edv, sv(edv, 70), color=C["venous"], lw=1.8, ls=(0, (5, 2)))
    a2.text(252, sv(250, 130), "more contractility", fontsize=8.5, color=C["arterial"], va="center")
    a2.text(252, sv(250, 100), "baseline", fontsize=8.5, color=C["ventricular"], va="center")
    a2.text(252, sv(250, 70), "less contractility", fontsize=8.5, color=C["venous"], va="center")
    A, B = 120, 170
    a2.plot([A], [sv(A, 100)], "o", color=C["ink"], ms=6, zorder=5)
    a2.plot([B], [sv(B, 100)], "o", color=C["ink"], ms=6, zorder=5)
    a2.plot([A], [sv(A, 130)], "o", color=C["ink"], ms=6, zorder=5)
    a2.annotate("", xy=(B - 3, sv(B, 100) - 0.5), xytext=(A + 3, sv(A, 100) + 0.5),
                arrowprops=dict(arrowstyle="-|>", color=C["ink"], lw=1.3, connectionstyle="arc3,rad=-0.15"))
    a2.annotate("", xy=(A, sv(A, 130) - 3), xytext=(A, sv(A, 100) + 3),
                arrowprops=dict(arrowstyle="-|>", color=C["arterial"], lw=1.3))
    a2.text(A - 4, sv(A, 100) - 4, "1", fontsize=9, ha="right", va="top", fontweight="bold")
    a2.text(B + 2, sv(B, 100) - 6, "2", fontsize=9, ha="left", va="top", fontweight="bold")
    a2.text(A - 4, sv(A, 130) + 2, "3", fontsize=9, ha="right", va="bottom", fontweight="bold")
    a2.set_xlim(50, 320); a2.set_ylim(0, 140)
    a2.set_xticks([50, 100, 150, 200, 250])
    a2.set_xlabel("End-diastolic volume (mL)")
    a2.set_ylabel("Stroke volume (mL)")
    a2.set_title("B  Frank-Starling curves")
    fs.grid(a2)
    fs.save(fig, PART, SLUG, "frank-starling.svg")


if __name__ == "__main__":
    fig_disc()
    fig_dyad()
    fig_calcium()
    fig_ap()
    fig_length_tension()
    fig_starling()
