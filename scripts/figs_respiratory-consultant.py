"""Figures for the Think Like a Respiratory Consultant chapter (pulmonary block, P12).

Run:  cd site/scripts && MPLCONFIGDIR=$TMPDIR PNG_PREVIEW=<folder> python3 figs_respiratory-consultant.py
Writes SVGs to ../pulmonary/figures/respiratory-consultant/.
"""
import numpy as np
from matplotlib.patches import FancyBboxPatch, Polygon

import figstyle as fs

plt, C = fs.plt, fs.C
PART, SLUG = "pulmonary", "respiratory-consultant"


def box(ax, x, y, w, h, text, ec, fc="white", fs_=9.3, bold=False, tc=None):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.1",
                                fc=fc, ec=ec, lw=1.7, zorder=2))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs_, color=tc or C["ink"],
            fontweight="bold" if bold else "normal", zorder=3, linespacing=1.25)


def arrow(ax, x0, y0, x1, y1, color=None, label=None, lx=0.0, ly=0.0, ha="center"):
    color = color or C["ink"]
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.5, shrinkA=1, shrinkB=1), zorder=1)
    if label:
        ax.text((x0 + x1) / 2 + lx, (y0 + y1) / 2 + ly, label, fontsize=8.8, color=color, ha=ha, va="center",
                bbox=dict(fc="white", ec="none", pad=0.6), zorder=4)


# ---------------------------------------------------------------- 1. Hypoxemia flowchart
def fig_hypoxemia():
    fig, ax = plt.subplots(figsize=(10.4, 6.6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8.6)
    ax.axis("off")
    box(ax, 6.0, 8.0, 4.4, 0.8, "Hypoxemia (low PaO$_2$)\nCalculate PAO$_2$ and the A–a gradient", C["system"], bold=True)
    box(ax, 2.6, 6.2, 4.4, 0.85, "A–a gradient normal (10 or less)\nLow PAO$_2$: the lung itself is fine", C["cw"])
    box(ax, 8.9, 6.2, 4.4, 0.85, "A–a gradient increased (over 10)\nA problem getting O$_2$ from alveolus to blood", C["lung"])
    arrow(ax, 4.9, 7.6, 3.3, 6.65)
    arrow(ax, 7.1, 7.6, 8.4, 6.65)
    box(ax, 1.45, 4.15, 2.4, 1.5, "Low inspired PO$_2$\naltitude; low FiO$_2$\n(rare: confined space)", C["cw"], fs_=8.8)
    box(ax, 3.85, 4.15, 2.2, 1.5, "Hypoventilation\nhigh PaCO$_2$\n(opioids)", C["cw"], fs_=8.8)
    arrow(ax, 2.0, 5.77, 1.6, 4.92)
    arrow(ax, 3.2, 5.77, 3.7, 4.92)
    ax.text(2.6, 3.05, "Both respond to supplemental O$_2$;\nthe cause still needs fixing", ha="center", va="top",
            fontsize=8.8, color=C["cw"])
    box(ax, 8.9, 4.65, 3.6, 0.7, "Does PaO$_2$ rise with supplemental O$_2$?", C["lung"], fs_=9)
    arrow(ax, 8.9, 5.77, 8.9, 5.02)
    box(ax, 6.8, 2.65, 2.4, 1.55, "V/Q mismatch\nresponsive\nobstructive disease,\nasthma", C["lung"], fs_=8.8)
    box(ax, 9.15, 2.65, 2.0, 1.55, "Diffusion\nlimitation\nthick barrier (ILD);\nworse in exercise", C["lung"], fs_=8.6)
    box(ax, 11.22, 2.65, 1.5, 1.55, "Shunt\nrefractory\natelectasis;\nblood, pus,\nwater; AVM", C["muscle"], fs_=8.6)
    arrow(ax, 8.1, 4.29, 7.2, 3.44, label="yes", lx=-0.25, ly=0.1)
    arrow(ax, 8.9, 4.29, 9.1, 3.44, label="yes", lx=0.3)
    arrow(ax, 10.1, 4.29, 11.0, 3.44, label="no", lx=0.25, ly=0.1)
    ax.add_patch(FancyBboxPatch((5.75, 0.25), 6.2, 1.0, boxstyle="round,pad=0.02,rounding_size=0.1",
                                fc=C["cool"], ec="none", zorder=0))
    ax.text(8.85, 0.75, "A low mixed venous saturation (low cardiac output, fever, exercise) makes\nall three worse. "
            "It does not lower PaO$_2$ by itself when the lungs are normal.",
            ha="center", va="center", fontsize=8.6, color=C["ink"])
    fs.save(fig, PART, SLUG, "hypoxemia-flowchart.svg")


# ---------------------------------------------------------------- 2. Spirometry patterns
def exp_limb(tlc, rv, pef, scoop):
    v = np.linspace(tlc, rv, 300)
    frac = (tlc - v) / (tlc - rv)
    rise = 0.12
    f = np.where(frac < rise, pef * np.sin(np.pi / 2 * frac / rise),
                 pef * ((1 - (frac - rise) / (1 - rise)) ** scoop))
    return v, f


def insp_limb(tlc, rv, pif):
    v = np.linspace(rv, tlc, 200)
    frac = (v - rv) / (tlc - rv)
    return v, -pif * np.sin(np.pi * frac)


def vt_curve(fvc, fev1, t):
    k = -np.log(1 - fev1 / fvc)  # time constant fits FEV1 at 1 s
    return fvc * (1 - np.exp(-k * t))


def fig_spirometry():
    pats = [("Normal", C["system"], 6.0, 1.5, 9.0, 1.0, 6.0, 4.5, 3.6),
            ("Obstructive", C["venous"], 7.0, 3.5, 4.5, 2.4, 4.5, 3.5, 1.7),
            ("Restrictive", C["gold"], 4.0, 1.1, 7.2, 1.0, 5.0, 2.9, 2.6)]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.8, 4.6), gridspec_kw=dict(width_ratios=[1, 1.25]))
    t = np.linspace(0, 6, 300)
    for name, col, tlc, rv, pef, scoop, pif, fvc, fev1 in pats:
        a1.plot(t, vt_curve(fvc, fev1, t), color=col, lw=2.3)
        a1.plot([1], [fev1], "o", color=col, ms=5)
        ratio = fev1 / fvc
        a1.text(6.1, fvc, f"{name}\nFEV$_1$/FVC {100 * ratio:.0f}%", color=col, fontsize=8.8, va="center", ha="left")
    a1.axvline(1, color=C["axis"], lw=0.9, ls=(0, (3, 3)))
    a1.text(1.05, 0.2, "1 s: FEV$_1$", fontsize=8.6, color=C["text"])
    a1.set_xlim(0, 8.3)
    a1.set_xticks([0, 1, 2, 3, 4, 5, 6])
    a1.set_ylim(0, 5)
    a1.set_xlabel("Time (s)")
    a1.set_ylabel("Volume exhaled (L)")
    a1.set_title("A. Volume-time curve")
    fs.grid(a1)
    for name, col, tlc, rv, pef, scoop, pif, fvc, fev1 in pats:
        v, f = exp_limb(tlc, rv, pef, scoop)
        a2.plot(v, f, color=col, lw=2.3)
        vi, fi = insp_limb(tlc, rv, pif)
        a2.plot(vi, fi, color=col, lw=1.6)
    a2.axhline(0, color=C["axis"], lw=0.9)
    a2.set_xlim(7.6, 0.5)
    a2.set_ylim(-7, 10.5)
    a2.set_xlabel("Absolute lung volume (L), TLC on the left")
    a2.set_ylabel("Flow (L/s); expiration up")
    a2.set_title("B. Flow-volume loops placed by lung volume")
    a2.text(5.0, 9.4, "Normal", color=C["system"], fontsize=9.5, ha="left")
    a2.text(6.2, 5.2, "Obstructive:\nbig lungs, scooped,\nlow flows", color=C["venous"], fontsize=9, ha="left")
    a2.text(2.4, 7.0, "Restrictive:\nsmall lungs,\nnarrow loop", color=C["gold"], fontsize=9, ha="right")
    a2.text(4.0, -6.3, "inspiration", fontsize=8.8, color=C["text"], ha="center")
    fs.grid(a2)
    fig.subplots_adjust(wspace=0.28)
    fs.save(fig, PART, SLUG, "spirometry-patterns.svg")


# ---------------------------------------------------------------- 3. Lung volume patterns in the lecture's cases
def fig_volumes():
    cats = ["TLC", "FRC", "RV"]
    x = np.arange(3)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.4, 4.6), sharey=True)
    normal = [90, 87, 89]
    restr = [("Muscle weakness", C["muscle"], [74, 90, 125]), ("Obesity", C["gold"], [68, 72, 71]),
             ("ILD", C["green"], [55, 75, 68])]
    obst = [("Asthma", C["cw"], [118, 122, 177]), ("Emphysema", C["purple"], [122, 178, 222])]
    for ax, cases, title in ((a1, restr, "A. Small lungs, and the step-up of weakness"), (a2, obst, "B. Big lungs: obstruction with gas trapping")):
        ax.axhspan(80, 120, color=C["shade"], zorder=0)
        ax.plot(x, normal, color=C["gray"], lw=1.6, marker="o", ms=5, ls=(0, (4, 2)))
        ax.text(2.08, normal[2], "Normal", color=C["gray"], fontsize=9, va="center")
        for name, col, vals in cases:
            ax.plot(x, vals, color=col, lw=2.3, marker="o", ms=6, ls=(0, (1.5, 1.5)) if name == "ILD" else "-")
            dy = {"Obesity": 4, "ILD": -5}.get(name, 0)
            ax.text(2.08, vals[2] + dy, name, color=col, fontsize=9.5, va="center")
        ax.set_xticks(x)
        ax.set_xticklabels(cats)
        ax.set_xlim(-0.25, 2.9)
        ax.set_title(title)
        fs.grid(ax)
    a1.set_ylabel("Percent predicted")
    a1.set_ylim(40, 240)
    a1.text(-0.2, 115, "normal range 80 to 120%", fontsize=8.6, color=C["text"], va="top")
    fs.save(fig, PART, SLUG, "lung-volume-patterns.svg")


# ---------------------------------------------------------------- 4. PFT interpretation flowchart
def fig_pft_flow():
    fig, ax = plt.subplots(figsize=(10.6, 7.0))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 9.2)
    ax.axis("off")
    box(ax, 6.0, 8.6, 3.4, 0.7, "Look at lung volumes (TLC)", C["system"], bold=True)
    box(ax, 2.6, 7.1, 3.4, 0.7, "Small lungs: TLC below 80%\nRestriction. DLCO?", C["lung"])
    box(ax, 8.9, 7.1, 3.8, 0.7, "Lungs normal or big\nFEV$_1$/FVC and FEV$_1$?", C["cw"])
    arrow(ax, 5.0, 8.25, 3.3, 7.47)
    arrow(ax, 7.0, 8.25, 8.4, 7.47)
    box(ax, 1.25, 5.05, 2.3, 1.25, "Extrathoracic\nobesity, chest wall,\nneuromuscular\ndisease", C["lung"], fs_=8.8)
    box(ax, 3.95, 5.05, 2.3, 1.25, "Lung\nparenchyma\ninterstitial lung\ndisease", C["lung"], fs_=8.8)
    arrow(ax, 2.1, 6.73, 1.4, 5.7, label="normal", lx=-0.35)
    arrow(ax, 3.1, 6.73, 3.8, 5.7, label="low (below 80%)", lx=0.75)
    box(ax, 7.0, 5.3, 3.0, 0.75, "Obstruction\nDLCO?", C["cw"])
    box(ax, 10.75, 5.3, 2.2, 0.9, "Normal ratio\nand FEV$_1$:\nnormal spirometry", C["cw"], fs_=8.6)
    arrow(ax, 8.2, 6.73, 7.4, 5.7, label="FEV$_1$/FVC < 70%\nand FEV$_1$ < 80%", lx=-1.05)
    arrow(ax, 9.7, 6.73, 10.5, 5.77)
    box(ax, 10.75, 3.5, 2.2, 1.15, "History suggests\nasthma? Consider\nbronchoprovocation\n(methacholine)", C["gray"], fs_=8.5)
    arrow(ax, 10.75, 4.84, 10.75, 4.1)
    box(ax, 5.55, 3.5, 2.9, 0.75, "DLCO normal\nbronchodilator response?", C["cw"], fs_=8.8)
    box(ax, 8.55, 3.5, 2.1, 0.75, "DLCO low\n(below 80%)", C["cw"], fs_=8.8)
    arrow(ax, 6.6, 4.91, 5.9, 3.9)
    arrow(ax, 7.4, 4.91, 8.2, 3.9)
    box(ax, 9.0, 1.95, 2.0, 0.7, "Emphysema", C["purple"], bold=True)
    arrow(ax, 8.6, 3.1, 8.95, 2.32)
    box(ax, 3.4, 1.95, 2.0, 0.7, "Asthma", C["cw"], bold=True)
    box(ax, 6.3, 1.95, 2.3, 0.7, "Chronic bronchitis", C["gray"], bold=True)
    arrow(ax, 5.0, 3.1, 3.7, 2.32, label="yes: FEV$_1$ or FVC\nup >10% of predicted", lx=-1.5)
    arrow(ax, 6.0, 3.1, 6.25, 2.32, label="no", lx=0.25)
    ax.text(6.0, 0.75, "Percent of predicted: 80 to 120% is normal. FEV$_1$/FVC is a ratio (normal 0.70 or more); it defines obstruction.\n"
            "FEV$_1$ in percent predicted grades how severe it is. Check hemoglobin before reading a low DLCO.",
            ha="center", va="center", fontsize=8.6, color=C["text"])
    fs.save(fig, PART, SLUG, "pft-flowchart.svg")


# ---------------------------------------------------------------- 5. Strength versus load
def fig_strength_load():
    fig, ax = plt.subplots(figsize=(9.6, 5.4))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7.2)
    ax.axis("off")
    ax.set_aspect("equal")
    ang = np.radians(-9)  # tipped toward the load side
    cx, cy, L = 6.0, 3.0, 4.6
    xl, yl = cx - L * np.cos(ang), cy - L * np.sin(ang)
    xr, yr = cx + L * np.cos(ang), cy + L * np.sin(ang)
    ax.add_patch(Polygon([[cx - 0.55, 1.6], [cx + 0.55, 1.6], [cx, cy - 0.05]], closed=True, fc=C["ink"], ec="none"))
    ax.plot([xl, xr], [yl, yr], color=C["ink"], lw=4, solid_capstyle="round")
    left = "Ability to do work\n\nrespiratory drive\n(free from sedatives)\nneuromuscular integrity\n(free from paralytics)\nstrength, nutrition,\nelectrolytes"
    right = "Load on the system\n\nhigh airway resistance\nmetabolic load (more CO$_2$)\nlow lung compliance\nlow chest wall compliance\nmore dead space"
    box(ax, xl + 0.4, yl + 1.75, 3.6, 2.9, left, C["green"], fs_=9)
    box(ax, xr - 0.4, yr + 1.75, 3.6, 2.9, right, C["muscle"], fs_=9)
    ax.plot([xl + 0.4, xl + 0.4], [yl, yl + 0.3], color=C["ink"], lw=1.5)
    ax.plot([xr - 0.4, xr - 0.4], [yr, yr + 0.3], color=C["ink"], lw=1.5)
    ax.text(6.0, 1.15, "When the load outweighs the ability to do work, PaCO$_2$ rises: hypercapnic respiratory failure.\n"
            "Most patients have a little from each side.", ha="center", va="top", fontsize=9, color=C["ink"])
    fs.save(fig, PART, SLUG, "strength-load.svg")


if __name__ == "__main__":
    fig_hypoxemia()
    fig_spirometry()
    fig_volumes()
    fig_pft_flow()
    fig_strength_load()
