"""Figures for the Other Special Circulations chapter.

Run:  cd site/scripts && MPLCONFIGDIR=$TMPDIR PNG_PREVIEW=<folder> python3 figs_special-circulations.py
Writes SVGs to ../cardiovascular/figures/special-circulations/.

Numbers from the 2025 Other Special Circulations deck: body mass and basal metabolic rate shares
(slide 8); cerebral autoregulation about 50 to 150 mm Hg at about 50 mL/100 g/min, shifted right in
chronic hypertension (slides 20 and 21); splanchnic layout and the >25% reservoir (slide 45);
apical and non-apical skin (slides 63 to 78, after Boron and Boulpaep).
"""
import numpy as np
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch, Circle
import figstyle as fs

plt = fs.plt
C = fs.C
M = fs.MINUS
PART, SLUG = "cardiovascular", "special-circulations"


def save(fig, name):
    fs.save(fig, PART, SLUG, name)


def box(ax, x, y, w, h, text, fc, ec, tc=None, fs_=9.5, bold=False):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc=fc, ec=ec, lw=1.4))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs_, color=tc or C["ink"],
            fontweight="bold" if bold else "normal")


def arrow(ax, x0, y0, x1, y1, col, lw=1.6, rad=0.0):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=13, color=col, lw=lw,
                                 connectionstyle=f"arc3,rad={rad}", shrinkA=2, shrinkB=2))


# ---------------------------------------------------------------- 1. Mass vs metabolic rate
def fig_mass_metabolism():
    organs = ["Brain", "Heart", "Kidneys", "Liver", "Skeletal muscle", "Adipose tissue", "Everything else"]
    mass = [2, 0.4, 0.5, 2, 42, 21, 32]
    bmr = [20, 11, 6, 17, 20, 5, 21]
    y = np.arange(len(organs))[::-1]
    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    fs.grid(ax)
    ax.barh(y + 0.19, mass, height=0.36, color=C["gray"], label="Share of body mass")
    ax.barh(y - 0.19, bmr, height=0.36, color=C["arterial"], label="Share of basal metabolic rate")
    for yy, a, b in zip(y, mass, bmr):
        ax.text(a + 0.6, yy + 0.19, f"{a:g}%", va="center", fontsize=8.6, color=C["text"])
        ax.text(b + 0.6, yy - 0.19, f"{b:g}%", va="center", fontsize=8.6, color=C["arterial"])
    ax.set_yticks(y)
    ax.set_yticklabels(organs)
    ax.set_xlabel("Percent of the whole body (approximate)")
    ax.set_xlim(0, 48)
    ax.legend(loc="upper right", fontsize=9)
    save(fig, "mass-vs-metabolism.svg")


# ---------------------------------------------------------------- 2. Cerebral autoregulation
def autoreg_curve(P, lo, hi, q0=50.0):
    """Flow vs perfusion pressure with a plateau from lo to hi and smooth shoulders."""
    k = 9.0
    below = q0 / (1 + np.exp(-(P - (lo - 18)) / k * 1.0))
    below = q0 * np.clip((P - (lo - 40)) / 40, 0, 1) ** 0.8
    q = np.where(P < lo, below, q0)
    above = q0 + 0.9 * np.clip(P - hi, 0, None) ** 1.25
    q = np.where(P > hi, above, q)
    # soften corners
    w = 9
    kern = np.ones(w) / w
    qs = np.convolve(np.pad(q, (w // 2, w // 2), mode="edge"), kern, mode="valid")
    return qs


def fig_cerebral():
    P = np.linspace(0, 220, 600)
    q_n = autoreg_curve(P, 50, 150)
    q_h = autoreg_curve(P, 75, 180)
    fig, ax = plt.subplots(figsize=(7.4, 4.8))
    fs.grid(ax)
    ax.axvspan(50, 150, color=C["cool"], zorder=0)
    ax.plot(P, q_n, color=C["arterial"], lw=2.6)
    ax.plot(P, q_h, color=C["venous"], lw=2.2, ls=(0, (6, 3)))
    ax.set_xlim(0, 220)
    ax.set_ylim(0, 100)
    ax.set_xlabel("Cerebral perfusion pressure (mm Hg)")
    ax.set_ylabel("Cerebral blood flow (mL/100 g/min)")
    ax.text(100, 93, "autoregulatory range, about 50 to 150", ha="center", fontsize=9.5, color=C["ink"])
    ax.text(100, 54, "normotension", color=C["arterial"], fontsize=10, fontweight="bold", ha="center")
    ax.text(168, 40, "chronic\nhypertension", color=C["venous"], fontsize=10, fontweight="bold", ha="center")
    ax.annotate("too little: vessels fully\ndilated, ischemia", xy=(30, 26), xytext=(3, 70), fontsize=8.6,
                color=C["text"], arrowprops=dict(arrowstyle="-", color=C["text"], lw=0.8))
    ax.annotate("too much: vessels forced\nopen, more flow, edema", xy=(166, 72), xytext=(105, 70), fontsize=8.6,
                color=C["text"], ha="left", va="center", arrowprops=dict(arrowstyle="-", color=C["text"], lw=0.8))
    save(fig, "cerebral-autoregulation.svg")


# ---------------------------------------------------------------- 3. Signals on a muscle arteriole
def fig_muscle_signals():
    fig, ax = plt.subplots(figsize=(9.2, 4.4))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis("off")
    # arteriole in the middle
    ax.add_patch(Rectangle((4.4, 2.35), 3.2, 1.3, fc="#f3e4e4", ec=C["arterial"], lw=2))
    ax.add_patch(Rectangle((4.4, 2.7), 3.2, 0.6, fc="white", ec="none"))
    ax.text(6.0, 3.0, "arteriole", ha="center", va="center", fontsize=9.5, color=C["arterial"])
    box(ax, 1.7, 4.55, 3.0, 1.1, "Sympathetic nerves\nnorepinephrine (NE)", "#f6ece0", C["ventricular"])
    box(ax, 1.7, 1.45, 3.0, 1.1, "Adrenal medulla, via blood\nepinephrine", "#eef2f4", C["venous"])
    box(ax, 10.3, 3.0, 3.0, 2.2, "Working muscle\nmore CO$_2$, less O$_2$,\nlower pH, adenosine, NO", "#e8efe9", C["green"])
    arrow(ax, 3.2, 4.3, 4.6, 3.7, C["ventricular"])
    ax.text(4.3, 4.3, "α$_1$: constrict", fontsize=9.5, color=C["ventricular"], ha="left")
    arrow(ax, 3.2, 1.7, 4.6, 2.3, C["venous"])
    ax.text(4.3, 1.75, "β$_2$: dilate", fontsize=9.5, color=C["venous"], ha="left")
    arrow(ax, 8.8, 3.0, 7.7, 3.0, C["green"])
    ax.text(8.25, 3.35, "dilate", fontsize=9.5, color=C["green"], ha="center")
    ax.text(6.0, 5.7, "NE: mainly α$_1$.  Epinephrine: β$_2$ as well as α$_1$", ha="center",
            fontsize=9, color=C["ink"])
    ax.text(6.0, 0.25, "In working muscle the metabolic dilators predominate: net vasodilation", ha="center",
            fontsize=9.5, color=C["ink"], fontweight="bold")
    save(fig, "muscle-signals.svg")


# ---------------------------------------------------------------- 4. Splanchnic: beds in series
def fig_splanchnic():
    fig, ax = plt.subplots(figsize=(9.6, 5.0))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6.4)
    ax.axis("off")
    art, ven = C["arterial"], C["venous"]
    box(ax, 1.1, 3.2, 1.5, 5.4, "Aorta", "#f3e4e4", art, tc=art, bold=True)
    box(ax, 10.9, 3.2, 1.5, 5.4, "Inferior\nvena cava", "#e3edf3", ven, tc=ven, bold=True)
    organs = [("Stomach", 5.4), ("Spleen", 4.3), ("Pancreas", 3.2), ("Small and\nlarge intestine", 2.0)]
    for name, y in organs:
        box(ax, 4.0, y, 2.2, 0.85, name + "\ncapillaries" if "\n" not in name else name, "#f7f0e6", C["ventricular"], fs_=8.6)
        arrow(ax, 1.9, y, 2.85, y, art)
        arrow(ax, 5.15, y, 6.25, 3.2 + (y - 3.2) * 0.35, ven, rad=0.0)
    box(ax, 6.9, 3.2, 1.3, 1.1, "Portal\nvein", "#e3edf3", ven, tc=ven, fs_=9)
    box(ax, 8.6, 3.2, 1.6, 1.4, "Liver\nsinusoids", "#f7f0e6", C["ventricular"], fs_=9)
    arrow(ax, 7.55, 3.2, 7.8, 3.2, ven)
    arrow(ax, 9.4, 3.2, 10.15, 3.2, ven)
    ax.text(9.78, 3.38, "hepatic\nveins", fontsize=7.8, color=ven, ha="center", va="bottom")
    # hepatic artery
    ax.plot([1.85, 8.6], [0.6, 0.6], color=art, lw=1.6)
    arrow(ax, 8.6, 0.6, 8.6, 2.5, art)
    ax.text(5.2, 0.75, "hepatic artery (from the celiac trunk)", fontsize=8.6, color=art, ha="center")
    ax.text(4.0, 6.15, "first capillary bed", fontsize=9, color=C["ink"], ha="center", fontweight="bold")
    ax.text(8.6, 4.15, "second capillary bed", fontsize=9, color=C["ink"], ha="center", fontweight="bold")
    ax.text(6.0, 5.45, "Splanchnic veins and liver hold\nover 25% of blood volume at rest.\nSympathetic venoconstriction moves\nit to the central circulation.",
            fontsize=8.6, color=ven, ha="left", va="center")
    save(fig, "splanchnic-series.svg")


# ---------------------------------------------------------------- 5. Apical vs non-apical skin
def skin_panel(ax, title, apical):
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis("off")
    ax.set_title(title, fontsize=11)
    ax.add_patch(Rectangle((0.3, 6.6), 9.4, 0.7, fc="#f1dcc6", ec="none"))
    ax.text(0.45, 6.95, "epidermis", fontsize=8.3, color=C["text"], va="center")
    ax.add_patch(Rectangle((0.3, 0.6), 9.4, 6.0, fc="#fbf3ec", ec="none"))
    ax.text(0.45, 0.85, "dermis", fontsize=8.3, color=C["text"])
    art, ven = C["arterial"], C["venous"]
    # arteriole along y=4.6 from left, capillary loops up toward the surface, venule along y=2.4
    ax.plot([0.8, 4.2], [4.6, 4.6], color=art, lw=4)
    ax.plot([0.8, 4.2], [2.4, 2.4], color=ven, lw=4)
    for x in (2.4, 3.0, 3.6):
        ax.plot([x, x, x + 0.25, x + 0.25, x + 0.25], [4.6, 6.1, 6.25, 6.1, 2.4], color="#b56576", lw=1.2)
    ax.text(3.0, 6.4, "capillaries", fontsize=8.3, color="#b56576", ha="center")
    ax.text(0.8, 4.85, "arteriole", fontsize=8.6, color=art)
    ax.text(0.8, 1.95, "venule", fontsize=8.6, color=ven)
    if apical:
        t = np.linspace(0, 1, 200)
        xs = 4.2 + 0.9 * np.sin(4 * np.pi * t) * 0.35 + 0.5 * t
        ys = 4.6 - 2.2 * t
        ax.plot([4.2] + list(xs) + [4.2], [4.6] + list(ys) + [2.4], color=C["purple"], lw=2.4)
        ax.text(5.15, 2.85, "arteriovenous\nanastomosis\n(no capillaries)", fontsize=8.6, color=C["purple"], va="center")
    # sympathetic adrenergic fiber
    nx = 8.3
    ax.plot([nx, nx], [7.6, 3.0], color=C["ink"], lw=1.4)
    ax.plot([nx, 4.0], [5.6, 4.75], color=C["ink"], lw=1.1)
    ax.text(nx + 0.1, 7.45, "sympathetic\n(NE, α$_1$):\nconstriction", fontsize=8.3, color=C["ink"], va="top")
    ax.text(3.95, 4.95, "α$_1$", fontsize=8.6, color=C["ink"], ha="right")
    if apical:
        ax.plot([nx, 4.75], [4.2, 3.6], color=C["ink"], lw=1.1)
        ax.text(4.75, 3.95, "α$_1$", fontsize=8.6, color=C["ink"], ha="right")
    # sweat gland and cholinergic fiber
    ax.add_patch(Circle((6.6, 1.5), 0.35, fc="#e8e0c8", ec=C["gold"], lw=1.4))
    ax.plot([6.6, 6.6], [1.85, 6.6], color=C["gold"], lw=1.2)
    ax.text(7.05, 1.5, "sweat gland", fontsize=8.3, color=C["gold"], va="center")
    ax.plot([9.3, 6.95], [0.9, 1.35], color=C["green"], lw=1.6)
    ax.text(9.6, 0.35, "sympathetic cholinergic (ACh)", fontsize=8.3, color=C["green"], ha="right")
    if not apical:
        arrow(ax, 6.3, 1.75, 4.3, 4.45, C["green"], lw=1.4, rad=-0.35)
        ax.text(5.6, 3.3, "active\nvasodilation", fontsize=8.6, color=C["green"], ha="left")


def fig_skin():
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.8))
    skin_panel(axes[0], "A. Apical skin (palms, soles, lips, nose, ears, face)", True)
    skin_panel(axes[1], "B. Non-apical (hairy) skin", False)
    fig.subplots_adjust(wspace=0.04)
    save(fig, "skin-apical-nonapical.svg")


if __name__ == "__main__":
    fig_mass_metabolism()
    fig_cerebral()
    fig_muscle_signals()
    fig_splanchnic()
    fig_skin()
