"""Figures for the Smooth Muscle chapter (site/muscle/smooth-muscle.qmd).

Run:  cd site/scripts && MPLCONFIGDIR=$TMPDIR PNG_PREVIEW=<folder> python3 figs_smooth_muscle.py
All figures are schematics drawn for the book from the 2026 Smooth Muscle lecture.
"""
import numpy as np
from matplotlib.patches import Ellipse, FancyBboxPatch, Circle, Rectangle, Polygon
import figstyle as fs

plt, C, M = fs.plt, fs.C, fs.MINUS
PART, SLUG = "muscle", "smooth-muscle"
CON, REL = C["arterial"], C["venous"]   # contraction maroon, relaxation blue


def box(ax, x, y, text, w=2.2, h=0.62, fc="white", ec=None, color=None, fs_=9.5, bold=False):
    ec = ec or C["axis"]
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc=fc, ec=ec, lw=1.2, zorder=3))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs_, color=color or C["ink"], zorder=4,
            fontweight="bold" if bold else "normal")


def arrow(ax, x0, y0, x1, y1, color=None, lw=1.4, style="-|>", ls="-", rad=0.0):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle=style, color=color or C["ink"], lw=lw, ls=ls,
                                shrinkA=2, shrinkB=2, connectionstyle=f"arc3,rad={rad}"), zorder=2)


def blocker(ax, x0, y0, x1, y1, color, lw=1.4, rad=0.0, label=None):
    """Inhibition: a line ending in a flat bar."""
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="-[, widthB=0.5, lengthB=0.01", color=color, lw=lw,
                                shrinkA=2, shrinkB=2, connectionstyle=f"arc3,rad={rad}"), zorder=2)


# ------------------------------------------------------------------ 1. Cell structure
def lattice(ax, cx, cy, a, b, n_db=9, seed=3):
    """Dense bodies inside an ellipse, linked by diagonal contractile bundles."""
    rng = np.random.default_rng(seed)
    pts = []
    # membrane dense bodies (attachment plaques)
    for t in np.linspace(0.25, np.pi - 0.25, 5):
        pts.append((cx + a * np.cos(t) * 0.97, cy + b * np.sin(t) * 0.93, "m"))
        pts.append((cx + a * np.cos(t + np.pi) * 0.97, cy + b * np.sin(t + np.pi) * 0.93, "m"))
    # cytoplasmic dense bodies
    for xf in np.linspace(-0.62, 0.62, 5):
        for yf in (-0.38, 0.38):
            pts.append((cx + a * xf + rng.normal(0, a * 0.02), cy + b * yf * (1 - xf ** 2 * 0.5), "c"))
    P = np.array([(p[0], p[1]) for p in pts])
    # bundles: link each point to two neighbors at a diagonal
    for i, (x, y, _) in enumerate(pts):
        d = np.hypot(P[:, 0] - x, (P[:, 1] - y) * a / b * 0.6)
        order = np.argsort(d)
        k = 0
        for j in order[1:]:
            dx, dy = P[j, 0] - x, P[j, 1] - y
            if abs(dy) > 0.15 * b and abs(dx) > 0.05 * a:
                ax.plot([x, P[j, 0]], [y, P[j, 1]], color=CON, lw=1.6, alpha=0.75, zorder=2,
                        solid_capstyle="round")
                k += 1
            if k == 2:
                break
    for x, y, kind in pts:
        ax.add_patch(Circle((x, y), 0.11, fc=C["ink"], ec="none", zorder=4))
    return P


def fig_structure():
    fig = plt.figure(figsize=(9.0, 6.2))
    axA = fig.add_axes([0.0, 0.47, 0.62, 0.5])
    axB = fig.add_axes([0.62, 0.47, 0.38, 0.5])
    axC = fig.add_axes([0.0, 0.0, 1.0, 0.43])
    for ax in (axA, axB, axC):
        ax.axis("off")
        ax.set_aspect("equal")

    # A relaxed
    axA.set_xlim(0, 10); axA.set_ylim(-0.6, 6)
    axA.set_title("A  Relaxed cell", loc="left")
    cx, cy, a, b = 5.0, 3.0, 4.6, 1.15
    axA.add_patch(Ellipse((cx, cy), 2 * a, 2 * b, fc=C["highlight"], ec=C["ink"], lw=1.4, zorder=1))
    axA.add_patch(Ellipse((cx, cy), 1.5, 0.45, fc="#c9b9d6", ec=C["purple"], lw=1, zorder=3))
    # intermediate filaments (thin gray, longitudinal)
    for yf in (-0.6, 0.0, 0.6):
        xs = np.linspace(cx - a * 0.85, cx + a * 0.85, 50)
        axA.plot(xs, cy + yf * b * np.sqrt(1 - ((xs - cx) / a) ** 2) * 0.9, color=C["gray"], lw=0.7,
                 ls=(0, (2, 2)), zorder=2)
    lattice(axA, cx, cy, a, b)
    # caveolae: small flask indentations on the top membrane
    for xc in (2.6, 3.4, 6.6, 7.4):
        yt = cy + b * np.sqrt(1 - ((xc - cx) / a) ** 2)
        axA.add_patch(Circle((xc, yt - 0.09), 0.09, fc="white", ec=C["ink"], lw=0.9, zorder=5))
    axA.annotate("caveolae", xy=(3.4, cy + b * 0.93), xytext=(0.6, 5.2), fontsize=9, color=C["text"],
                 arrowprops=dict(arrowstyle="-", color=C["text"], lw=0.7))
    axA.annotate("dense body (in cytoplasm)", xy=(cx + a * 0.31, cy + b * 0.36), xytext=(4.9, 5.2),
                 fontsize=9, color=C["text"], arrowprops=dict(arrowstyle="-", color=C["text"], lw=0.7))
    axA.annotate("dense body on the membrane", xy=(cx + a * np.cos(np.pi - 0.25) * 0.97,
                 cy - b * np.sin(0.25) * 0.93), xytext=(0.0, 0.55), fontsize=9, color=C["text"],
                 arrowprops=dict(arrowstyle="-", color=C["text"], lw=0.7))
    axA.annotate("actin and myosin bundle", xy=(cx + a * 0.5, cy - b * 0.15), xytext=(6.2, 0.55),
                 fontsize=9, color=CON, arrowprops=dict(arrowstyle="-", color=CON, lw=0.7))
    axA.annotate("nucleus", xy=(cx - 0.4, cy + 0.12), xytext=(3.0, 5.2), fontsize=9, color=C["purple"],
                 arrowprops=dict(arrowstyle="-", color=C["purple"], lw=0.7))
    axA.annotate("intermediate filaments (dotted)", xy=(cx + a * 0.62, cy - 0.47), xytext=(3.2, -0.45),
                 fontsize=9, color=C["gray"], arrowprops=dict(arrowstyle="-", color=C["gray"], lw=0.7))

    # B contracted
    axB.set_xlim(0, 6); axB.set_ylim(0, 6)
    axB.set_title("B  Contracted cell", loc="left")
    cx, cy, a, b = 3.0, 3.0, 2.6, 1.55
    t = np.linspace(0, 2 * np.pi, 400)
    r = 1 + 0.045 * np.sin(14 * t)  # puckered membrane
    axB.fill(cx + a * r * np.cos(t), cy + b * r * np.sin(t), fc=C["highlight"], ec=C["ink"], lw=1.4, zorder=1)
    axB.add_patch(Ellipse((cx, cy), 1.0, 0.6, angle=20, fc="#c9b9d6", ec=C["purple"], lw=1, zorder=3))
    lattice(axB, cx, cy, a, b)
    axB.text(3.0, 0.55, "shorter and wider; the membrane\npuckers between attachment points",
             ha="center", fontsize=9, color=C["text"])

    # C thick filaments
    axC.set_xlim(0, 20); axC.set_ylim(0, 7.2)
    axC.set_title("C  Thick filaments: bipolar (skeletal) and side-polar (smooth)", loc="left")

    def actin(ax, x0, x1, y, direction, below=False):
        xs = np.arange(x0, x1, 0.22)
        for i, x in enumerate(xs):
            ax.add_patch(Circle((x, y + 0.07 * (i % 2)), 0.12, fc="#e9a29a", ec=CON, lw=0.4, zorder=2))
        xm = (x0 + x1) / 2
        ya = y - 0.55 if below else y + 0.55
        ax.annotate("", xy=(xm + 0.9 * direction, ya), xytext=(xm - 0.9 * direction, ya),
                    arrowprops=dict(arrowstyle="-|>", color=C["ink"], lw=1.1))

    def heads(ax, xs, y, up, lean):
        for x in xs:
            dy = 0.55 if up else -0.55
            ax.plot([x, x + lean], [y, y + dy], color=C["purple"], lw=1.3, zorder=3)
            ax.add_patch(Ellipse((x + lean * 1.15, y + dy * 1.15), 0.32, 0.2, angle=0, fc="#b9a3cc",
                                 ec=C["purple"], lw=0.6, zorder=3))

    # skeletal bipolar: heads lean away from bare zone in the middle
    y0 = 4.2
    axC.add_patch(FancyBboxPatch((1.0, y0 - 0.2), 7.0, 0.4, boxstyle="round,pad=0,rounding_size=0.2",
                                 fc="#d9cce4", ec=C["purple"], lw=1, zorder=3))
    left = np.arange(1.3, 4.0, 0.45)
    right = np.arange(5.0, 7.8, 0.45)
    heads(axC, left, y0 + 0.2, True, -0.25); heads(axC, left, y0 - 0.2, False, -0.25)
    heads(axC, right, y0 + 0.2, True, 0.25); heads(axC, right, y0 - 0.2, False, 0.25)
    axC.text(4.5, y0 - 0.75, "bare\nzone", ha="center", va="top", fontsize=8.5, color=C["text"])
    actin(axC, 0.0, 3.8, y0 + 1.5, +1)
    actin(axC, 5.2, 9.0, y0 + 1.5, -1)
    axC.text(4.5, 0.6, "Skeletal: heads reverse at the middle.\nBoth ends pull thin filaments toward the center.",
             ha="center", fontsize=9, color=C["ink"])

    # smooth side-polar: heads on top all lean one way, bottom the other
    x0s = 11.5
    axC.add_patch(FancyBboxPatch((x0s, y0 - 0.2), 7.0, 0.4, boxstyle="round,pad=0,rounding_size=0.2",
                                 fc="#d9cce4", ec=C["purple"], lw=1, zorder=3))
    xs = np.arange(x0s + 0.3, x0s + 6.9, 0.45)
    heads(axC, xs, y0 + 0.2, True, -0.25)
    heads(axC, xs, y0 - 0.2, False, 0.25)
    actin(axC, x0s - 0.3, x0s + 7.3, y0 + 1.5, -1)
    actin(axC, x0s - 0.3, x0s + 7.3, y0 - 1.5, +1, below=True)
    axC.text(x0s + 3.5, 0.6, "Smooth: heads on each side face opposite ways along the whole length,\n"
             "so thin filaments on the two sides slide in opposite directions.",
             ha="center", fontsize=9, color=C["ink"])
    axC.text(x0s + 7.6, y0, "myosin", fontsize=9, color=C["purple"], va="center")
    axC.text(x0s + 7.6, y0 + 1.5, "actin", fontsize=9, color=CON, va="center")
    fs.save(fig, PART, SLUG, "cell-structure.svg")


# ------------------------------------------------------------------ 2. EC coupling
def fig_ec():
    fig, ax = plt.subplots(figsize=(9.0, 6.4))
    ax.set_xlim(0, 15); ax.set_ylim(0.2, 10.6); ax.axis("off")
    # sources
    ax.text(0.2, 10.25, "Sources of Ca²⁺", fontsize=10.5, fontweight="bold", color=C["ink"])
    src = [(1.9, 9.2, "Voltage-gated Ca²⁺\nchannel (depolarization)"),
           (5.6, 9.2, "Receptor-operated\nchannel (ligand)"),
           (9.3, 9.2, "Stretch-activated\nchannel"),
           (13.0, 9.2, "SR release\n(IP₃ receptor, RyR)")]
    for x, y, t in src:
        box(ax, x, y, t, w=3.3, h=1.0, fs_=9)
        arrow(ax, x, y - 0.52, 7.5 + (x - 7.45) * 0.25, 7.45)
    ax.text(7.45, 8.0, "", fontsize=1)
    box(ax, 7.5, 7.1, "Cytosolic [Ca²⁺] rises", w=3.2, fc=C["highlight"], bold=True)
    arrow(ax, 7.5, 6.78, 7.5, 6.12)
    box(ax, 7.5, 5.8, "4 Ca²⁺ bind calmodulin (CaM)", w=4.0)
    arrow(ax, 7.5, 5.48, 7.5, 4.82)
    box(ax, 7.5, 4.5, "Ca²⁺–CaM activates MLCK", w=4.0)
    # switch
    for x0, fc, ec, txt, lab, lc in ((1.0, C["cool"], REL, "Myosin light chain\ndephosphorylated", "Relaxation", REL),
                                     (10.0, C["highlight"], CON, "Myosin light chain\nphosphorylated (P)",
                                      "Cross-bridge cycling:\ncontraction", CON)):
        ax.add_patch(FancyBboxPatch((x0, 1.3), 4.0, 1.5, boxstyle="round,pad=0.02,rounding_size=0.15",
                                    fc=fc, ec=ec, lw=1.4))
        ax.text(x0 + 2.0, 2.05, txt, ha="center", va="center", fontsize=9.5, color=C["ink"])
        ax.text(x0 + 2.0, 1.1, lab, ha="center", va="top", fontsize=10, fontweight="bold", color=lc)
    arrow(ax, 5.1, 2.5, 9.9, 2.5, color=CON, lw=2)
    ax.text(7.5, 2.68, "MLCK + ATP", ha="center", fontsize=9.5, color=CON, fontweight="bold")
    arrow(ax, 9.9, 1.6, 5.1, 1.6, color=REL, lw=2)
    ax.text(7.5, 1.38, "MLCP", ha="center", va="top", fontsize=9.5, color=REL, fontweight="bold")
    arrow(ax, 7.5, 4.18, 7.5, 3.05, color=CON)
    # removal
    ax.text(0.2, 5.3, "Ca²⁺ removal", fontsize=10, fontweight="bold", color=REL)
    ax.text(0.2, 4.35, "SERCA pumps Ca²⁺ back\ninto the SR. A sarcolemmal\nCa²⁺ pump and NCX move\nit out of the cell. As [Ca²⁺]\n"
            "falls, MLCK switches off\nand MLCP wins.", fontsize=9, color=C["text"], va="center")
    fs.save(fig, PART, SLUG, "ec-coupling.svg")


# ------------------------------------------------------------------ 3. Multi-unit vs single-unit
def fusiform(ax, x, y, L=2.4, W=0.8, ang=0.0, fc="#f2d4cc"):
    t = np.linspace(0, 2 * np.pi, 120)
    xs = L / 2 * np.cos(t)
    ys = W / 2 * np.sin(t) * (np.abs(np.sin(t)) ** 0.4)
    ca, sa = np.cos(np.radians(ang)), np.sin(np.radians(ang))
    ax.fill(x + xs * ca - ys * sa, y + xs * sa + ys * ca, fc=fc, ec=CON, lw=0.9, zorder=2)
    ax.add_patch(Ellipse((x, y), 0.6, 0.24, angle=ang, fc="#9d86b5", ec="none", zorder=3))


def varicose(ax, x0, x1, y, n=3):
    xs = np.linspace(x0, x1, 60)
    ax.plot(xs, y + 0.06 * np.sin(xs * 6), color=C["green"], lw=1.6, zorder=4)
    for xv in np.linspace(x0 + 0.5, x1 - 0.2, n):
        ax.add_patch(Circle((xv, y + 0.06 * np.sin(xv * 6)), 0.13, fc=C["green"], ec="white", lw=0.6, zorder=5))


def fig_units():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.2, 4.9))
    for ax in (a1, a2):
        ax.set_xlim(0, 8); ax.set_ylim(-0.6, 7.4); ax.set_aspect("equal"); ax.axis("off")
    a1.set_title("A  Multi-unit", loc="left")
    a2.set_title("B  Single-unit", loc="left")
    # multi-unit: separated cells, each with its own varicose fiber along it
    for row, y in enumerate((5.6, 3.6, 1.6)):
        for col, x in enumerate((1.9, 5.6)):
            xx = x + (0.5 if row == 1 else 0)
            fusiform(a1, xx, y)
            varicose(a1, xx - 1.9, xx + 0.9, y + 0.55)
    a1.text(4.0, -0.5, "Each cell has its own nerve supply.\nNo gap junctions. Fine, graded control.",
            ha="center", fontsize=9, color=C["ink"])
    # single-unit: packed, staggered cells joined by gap junctions
    cells = []
    for row, y in enumerate((5.6, 4.8, 4.0, 3.2, 2.4, 1.6)):
        off = 1.25 if row % 2 else 0.0
        for x in (0.95 + off, 3.45 + off, 5.95 + off):
            if x < 7.6:
                fusiform(a2, x, y)
                cells.append((x, y))
    for (x1, y1) in cells:
        for (x2, y2) in cells:
            if 0 < y1 - y2 < 0.9 and abs(x1 - x2) < 1.4:
                a2.add_patch(Rectangle(((x1 + x2) / 2 - 0.09, (y1 + y2) / 2 - 0.09), 0.18, 0.18,
                                       fc=C["gold"], ec="white", lw=0.5, zorder=5))
    varicose(a2, 1.2, 4.6, 6.15, n=2)
    a2.text(4.0, -0.5, "Only a few cells receive nerve endings.\nGap junctions spread excitation to the rest.",
            ha="center", fontsize=9, color=C["ink"])
    a2.add_patch(Rectangle((5.5, 6.85), 0.18, 0.18, fc=C["gold"], ec="white"))
    a2.text(5.8, 6.94, "gap junction", fontsize=8.5, va="center", color=C["text"])
    a1.add_patch(Circle((5.5, 6.95), 0.13, fc=C["green"], ec="white"))
    a1.text(5.75, 6.95, "varicosity", fontsize=8.5, va="center", color=C["text"])
    fs.save(fig, PART, SLUG, "multi-single-unit.svg")


# ------------------------------------------------------------------ 4. Regulation network
def fig_regulation():
    fig, ax = plt.subplots(figsize=(9.4, 7.0))
    ax.set_xlim(0, 16); ax.set_ylim(-0.2, 11.8); ax.axis("off")
    ax.text(0.2, 11.55, "Contracting signals", fontsize=10.5, fontweight="bold", color=CON)
    ax.text(15.8, 11.55, "Relaxing signals", fontsize=10.5, fontweight="bold", color=REL, ha="right")
    # bottom switch
    box(ax, 4.0, 1.6, "MLCK", w=3.2, h=0.8, fc=C["highlight"], ec=CON, color=CON, bold=True, fs_=11)
    box(ax, 12.0, 1.6, "MLCP", w=3.2, h=0.8, fc=C["cool"], ec=REL, color=REL, bold=True, fs_=11)
    ax.text(4.0, 0.95, "phosphorylates myosin:\ncontraction", ha="center", va="top", fontsize=9, color=CON)
    ax.text(12.0, 0.95, "dephosphorylates myosin:\nrelaxation", ha="center", va="top", fontsize=9, color=REL)
    # contracting side
    box(ax, 1.7, 10.6, "Depolarization", w=2.9, fs_=9)
    box(ax, 1.7, 9.0, "Voltage-gated\nCa²⁺ channels open", w=2.9, h=0.9, fs_=9)
    box(ax, 5.4, 10.6, "α₁ (NE, epinephrine)\nGq", w=3.2, h=0.9, fs_=9)
    box(ax, 5.4, 9.0, "PLC makes IP₃ and DAG", w=3.4, fs_=9)
    box(ax, 5.4, 7.5, "IP₃: SR releases Ca²⁺", w=3.4, fs_=9)
    box(ax, 3.4, 4.6, "[Ca²⁺] rises: Ca²⁺–calmodulin", w=4.6, fc=C["highlight"], fs_=9)
    box(ax, 9.6, 5.6, "Rho kinase", w=2.2, fs_=9, ec=CON)
    arrow(ax, 1.7, 10.28, 1.7, 9.47)
    arrow(ax, 1.9, 8.53, 2.9, 4.93)
    arrow(ax, 5.4, 10.13, 5.4, 9.32)
    arrow(ax, 5.4, 8.68, 5.4, 7.82)
    arrow(ax, 5.1, 7.18, 4.1, 4.93)
    arrow(ax, 3.6, 4.28, 3.9, 2.02, color=CON, lw=1.8)
    ax.text(3.95, 3.1, "activates", fontsize=8.5, color=CON)
    arrow(ax, 6.7, 10.15, 9.4, 5.93)
    blocker(ax, 10.0, 5.28, 11.6, 2.03, CON, lw=1.6)
    ax.text(8.0, 3.0, "Rho kinase\ninhibits MLCP:\nmore force at\nthe same [Ca²⁺]", fontsize=8.5, color=CON, ha="center")
    # relaxing side
    box(ax, 10.6, 10.6, "β₂ (epinephrine)\nGs", w=3.0, h=0.9, fs_=9)
    box(ax, 10.6, 9.0, "adenylyl cyclase:\ncAMP, PKA", w=3.0, h=0.9, fs_=9)
    box(ax, 8.05, 10.6, "α₂\nGi", w=1.7, h=0.9, fs_=9, ec=CON)
    box(ax, 14.0, 7.6, "NO (from endothelium\nor a drug)", w=3.6, h=0.9, fs_=9)
    box(ax, 14.0, 5.9, "guanylyl cyclase:\ncGMP, PKG", w=3.4, h=0.9, fs_=9)
    arrow(ax, 10.6, 10.13, 10.6, 9.47)
    blocker(ax, 8.5, 10.13, 9.15, 9.3, CON)
    ax.text(9.15, 9.85, "less\ncAMP", fontsize=8.5, color=CON, ha="left", va="center")
    blocker(ax, 9.3, 8.53, 5.4, 2.03, REL, lw=1.6)
    ax.text(6.5, 5.4, "PKA\ninhibits\nMLCK", fontsize=8.5, color=REL, ha="center")
    arrow(ax, 14.0, 7.13, 14.0, 6.37)
    arrow(ax, 13.6, 5.43, 12.5, 2.03, color=REL, lw=1.8)
    ax.text(13.35, 3.3, "activates\nMLCP", fontsize=8.5, color=REL)
    blocker(ax, 12.35, 5.5, 5.7, 4.45, REL, lw=1.4)
    ax.text(11.4, 4.9, "lowers [Ca²⁺]", fontsize=8.5, color=REL, ha="center", va="top")
    fs.save(fig, PART, SLUG, "regulation.svg")


# ------------------------------------------------------------------ 5. Patterns of contraction
def fig_patterns():
    t = np.linspace(0, 10, 1000)
    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    sph = 0.92 - 0.85 * np.exp(-((t - 6.2) / 0.55) ** 6)          # sphincter: tonic, relaxes briefly
    ves = 0.58 + 0.04 * np.sin(t * 0.9)                           # vessels/airways: partial tone
    gut = 0.18 + 0.32 * np.exp(-((t - 3.2) / 1.2) ** 2) + 0.18 * np.exp(-((t - 8.6) / 1.1) ** 2)
    eso = 0.06 + 0.88 * np.exp(-((t - 2.3) / 0.22) ** 2)          # esophagus/bladder: relaxed, phasic burst
    for y, col, lab, yl in ((sph, C["green"], "Sphincters: normally contracted", 0.97),
                            (ves, C["venous"], "Blood vessels, airways: partial\ncontraction (tone)", 0.71),
                            (gut, C["purple"], "Stomach, intestines:\nrhythmic (phasic)", 0.42),
                            (eso, CON, "Esophagus, urinary bladder:\nnormally relaxed, brief contractions", 0.12)):
        ax.plot(t, y, color=col, lw=2.2)
        ax.text(10.2, yl, lab, color=col, fontsize=9, va="center")
    ax.set_xlim(0, 10); ax.set_ylim(0, 1.05)
    ax.set_xticks([]); ax.set_yticks([0.06, 0.92]); ax.set_yticklabels(["relaxed", "contracted"])
    ax.set_xlabel("Time")
    ax.set_ylabel("Force")
    fs.save(fig, PART, SLUG, "contraction-patterns.svg")


# ------------------------------------------------------------------ 6. Latch
def fig_latch():
    t = np.linspace(0, 10, 1200)
    stim_on, stim_off = 0.5, 8.0

    def rise(t0, tau):
        return np.where(t > t0, 1 - np.exp(-(t - t0) / tau), 0)

    # phasic: brief stimulus
    ca_p = np.where(t > 0.5, np.exp(-(t - 0.5) / 0.45) * (1 - np.exp(-(t - 0.5) / 0.08)), 0)
    ca_p = ca_p / ca_p.max()
    ph_p = np.where(t > 0.6, np.exp(-(t - 0.6) / 0.9) * (1 - np.exp(-(t - 0.6) / 0.25)), 0)
    ph_p = 0.85 * ph_p / ph_p.max()
    f_p = np.where(t > 0.7, np.exp(-(t - 0.7) / 1.6) * (1 - np.exp(-(t - 0.7) / 0.6)), 0)
    f_p = 0.6 * f_p / f_p.max()

    # tonic: sustained stimulus
    def tonic(peak, plateau, t0, tau_up, tau_down):
        y = np.where(t > t0, plateau + (peak - plateau) * np.exp(-(t - t0) / tau_down), 0) * (1 - np.exp(-np.clip(t - t0, 0, None) / tau_up))
        return np.where(t > stim_off, y[np.searchsorted(t, stim_off)] * np.exp(-(t - stim_off) / 0.4), y)

    ca_t = tonic(1.0, 0.32, 0.5, 0.08, 0.45)
    ph_t = tonic(0.85, 0.25, 0.6, 0.25, 0.9)
    f_t = np.where(t > 0.7, 0.92 * (1 - np.exp(-(t - 0.7) / 0.9)), 0)
    f_t = np.where(t > stim_off, f_t[np.searchsorted(t, stim_off)] * np.exp(-(t - stim_off) / 0.9), f_t)

    fig, (a1, a2) = plt.subplots(2, 1, figsize=(8.0, 6.4), sharex=True)
    for ax, ca, ph, f, title, stim in ((a1, ca_p, ph_p, f_p, "A  Phasic contraction: a brief stimulus", (0.5, 0.8)),
                                      (a2, ca_t, ph_t, f_t, "B  Tonic contraction: a sustained stimulus", (0.5, stim_off))):
        ax.plot(t, ca, color=CON, lw=2, label="Cytosolic Ca²⁺")
        ax.plot(t, ph, color=C["gold"], lw=2, label="Myosin light chain phosphorylation\n(and cross-bridge cycling rate)")
        ax.plot(t, f, color=C["venous"], lw=2.4, label="Force")
        ax.fill_between([stim[0], stim[1]], -0.16, -0.08, color=C["gray"], lw=0)
        ax.text(stim[1] + 0.12, -0.12, "stimulus", fontsize=8.5, color=C["text"], va="center")
        ax.set_ylim(-0.18, 1.08)
        ax.set_yticks([0, 0.5, 1]); ax.set_yticklabels(["0", "", "max"])
        ax.set_title(title)
        fs.grid(ax)
    a1.legend(loc="upper right", fontsize=9)
    a2.annotate("Latch: force stays high while Ca²⁺ and\nphosphorylation have fallen (only 20 to 30%\n"
                "of cross-bridges phosphorylated)", xy=(5.0, 0.30), xytext=(3.6, 0.48), fontsize=9,
                color=C["ink"], arrowprops=dict(arrowstyle="-", color=C["ink"], lw=0.8))
    a2.set_xlabel("Time (arbitrary units)")
    a2.set_xlim(0, 10)
    fig.text(0.0, 0.5, "Level (fraction of maximum)", rotation=90, va="center", color=C["text"])
    fig.subplots_adjust(left=0.08, hspace=0.3)
    fs.save(fig, PART, SLUG, "latch.svg")


# ------------------------------------------------------------------ 7. Length-tension and length adaptation
def fig_length():
    L = np.linspace(0.3, 1.9, 600)
    L0 = 2.1  # µm, middle of the 2.0 to 2.2 µm optimum
    pts = [(1.27, 0), (1.67, 0.84), (2.0, 1.0), (2.25, 1.0), (3.6, 0)]
    sk = np.interp(L, [p[0] / L0 for p in pts], [p[1] for p in pts], left=0, right=0)
    gauss = lambda x, mu, sd: np.exp(-((x - mu) / sd) ** 2)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.4, 4.0), sharey=True)
    a1.plot(L, sk, color=C["arterial"], lw=2.2)
    a1.text(1.25, 0.95, "One fixed\noptimal length, L₀", fontsize=9, color=C["arterial"])
    for mu, col, lab in ((0.7, C["gold"], "adapted\nto 0.7 L₀"), (1.0, C["green"], "L₀"), (1.3, C["purple"], "adapted\nto 1.3 L₀")):
        a2.plot(L, gauss(L, mu, 0.36), color=col, lw=2.2)
        a2.text(mu, 1.04, lab, ha="center", fontsize=8.5, color=col, va="bottom")
    a1.set_title("A  Classic length-tension relationship", pad=26)
    a2.set_title("B  Smooth muscle: length adaptation", pad=26)
    for ax in (a1, a2):
        ax.set_xlim(0.3, 1.9); ax.set_ylim(0, 1.15)
        ax.set_xticks([0.5, 0.7, 1.0, 1.3, 1.5, 1.7])
        ax.set_xticklabels(["0.5", "0.7", "1.0", "1.3", "1.5", "1.7"])
        ax.set_xlabel("Muscle length (multiples of L₀)")
        fs.grid(ax)
    a1.set_ylabel("Active force (fraction of maximum)")
    fs.save(fig, PART, SLUG, "length-adaptation.svg")


if __name__ == "__main__":
    fig_structure()
    fig_ec()
    fig_units()
    fig_regulation()
    fig_patterns()
    fig_latch()
    fig_length()
