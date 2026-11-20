"""Figures for the Respiratory Physiology Introduction chapter.

Run:  cd site/scripts && MPLCONFIGDIR=$TMPDIR PNG_PREVIEW=<folder> python3 figs_respiratory-intro.py
Writes SVGs to ../pulmonary/figures/respiratory-intro/.
"""
import figstyle as fs
from matplotlib.patches import Circle, FancyBboxPatch, FancyArrowPatch, Ellipse

plt = fs.plt
C = fs.C
PART, SLUG = "pulmonary", "respiratory-intro"
O2C = C["system"]   # oxygen: maroon
CO2C = C["cw"]      # carbon dioxide: blue


def arrow(ax, p0, p1, color, lw=1.8, style="-|>", ms=12, **kw):
    a = FancyArrowPatch(p0, p1, arrowstyle=style, mutation_scale=ms, color=color, lw=lw, **kw)
    ax.add_patch(a)
    return a


# ------------------------------------------------------------ 1. One cell versus a whole body
def fig_circuit():
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.9), gridspec_kw=dict(width_ratios=[1, 1.55]))
    # A: single cell
    ax = axes[0]
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("A. One cell: diffusion is enough", loc="left")
    ax.add_patch(Circle((5, 4.6), 2.6, fc=C["shade"], ec=C["ink"], lw=2))
    ax.add_patch(Ellipse((5, 4.6), 2.9, 1.1, fc="white", ec=C["text"], lw=1.2))
    ax.text(5, 4.6, "mitochondria", ha="center", va="center", fontsize=8, color=C["text"])
    arrow(ax, (0.9, 7.3), (3.9, 5.3), O2C, lw=2)
    ax.text(0.2, 7.6, "O$_2$ in, down its gradient", color=O2C, fontsize=9.5)
    arrow(ax, (6.1, 4.0), (9.2, 2.4), CO2C, lw=2)
    ax.text(5.4, 1.35, "CO$_2$ out, down its gradient", color=CO2C, fontsize=9.5)
    ax.text(5, 9.0, "High O$_2$, low CO$_2$ outside", ha="center", fontsize=9, color=C["ink"])

    # B: lungs plus circulation
    ax = axes[1]
    ax.set_xlim(0, 15); ax.set_ylim(0, 10); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("B. A whole body: move the gas in bulk, then diffuse", loc="left")
    # loop of blood vessels
    left, right, top, bot = 3.0, 12.0, 7.0, 2.2
    ax.plot([left, left], [bot, top], color=CO2C, lw=7, solid_capstyle="round")
    ax.plot([right, right], [bot, top], color=O2C, lw=7, solid_capstyle="round")
    ax.plot([left, right], [top, top], color="#9a6a7a", lw=7, solid_capstyle="round")
    ax.plot([left, right], [bot, bot], color="#9a6a7a", lw=7, solid_capstyle="round")
    ax.plot([left, right], [top, top], color=C["shade"], lw=0)
    # lung box at top, tissue box at bottom
    ax.add_patch(FancyBboxPatch((5.6, 6.3), 3.8, 1.4, boxstyle="round,pad=0.1,rounding_size=0.5",
                                fc="#fbf3ea", ec=C["lung"], lw=2, zorder=3))
    ax.text(7.5, 7.0, "alveoli", ha="center", va="center", fontsize=10, color=C["lung"], zorder=4)
    ax.add_patch(FancyBboxPatch((5.6, 1.5), 3.8, 1.4, boxstyle="round,pad=0.1,rounding_size=0.5",
                                fc=C["shade"], ec=C["ink"], lw=2, zorder=3))
    ax.text(7.5, 2.2, "tissues", ha="center", va="center", fontsize=10, color=C["ink"], zorder=4)
    # airway
    ax.plot([7.5, 7.5], [7.8, 9.5], color=C["lung"], lw=6, solid_capstyle="butt", zorder=2)
    ax.plot([7.5, 7.5], [7.8, 9.5], color="white", lw=3.5, solid_capstyle="butt", zorder=2)
    arrow(ax, (6.6, 9.7), (6.9, 8.0), O2C, lw=2)
    ax.text(3.3, 9.25, "Ventilation brings\nO$_2$ in", color=O2C, fontsize=9, ha="center")
    arrow(ax, (8.1, 8.0), (8.4, 9.7), CO2C, lw=2)
    ax.text(11.6, 9.25, "and carries\nCO$_2$ out", color=CO2C, fontsize=9, ha="center")
    # flow direction on loop
    arrow(ax, (right - 0.45, 5.9), (right - 0.45, 3.4), O2C, lw=2, ms=14)
    arrow(ax, (left + 0.45, 3.4), (left + 0.45, 5.9), CO2C, lw=2, ms=14)
    ax.text(right + 0.45, 4.6, "arterial\nblood", fontsize=9, color=O2C, va="center")
    ax.text(left - 0.45, 4.6, "venous\nblood", fontsize=9, color=CO2C, va="center", ha="right")
    ax.text(7.5, 4.6, "The circulation carries O$_2$ to the tissues\nand CO$_2$ back to the lungs",
            ha="center", va="center", fontsize=9, color=C["text"])
    ax.text(7.5, 0.6, "In the tissues, O$_2$ leaves the blood and CO$_2$ enters it", ha="center",
            fontsize=9, color=C["text"])
    fig.subplots_adjust(wspace=0.08)
    fs.save(fig, PART, SLUG, "circuit.svg")


# ------------------------------------------------------------ 2. Map of the block
def box(ax, x, y, w, h, title, body, ec, fc="white"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05,rounding_size=0.25",
                                fc=fc, ec=ec, lw=1.8))
    ax.text(x + 0.18, y + h - 0.22, title, ha="left", va="top", fontsize=10, fontweight="bold", color=ec)
    ax.text(x + 0.18, y + h - 0.68, body, ha="left", va="top", fontsize=8.6, color=C["ink"], linespacing=1.35)


def fig_block_map():
    fig, ax = plt.subplots(figsize=(10.4, 5.3))
    ax.set_xlim(0, 16); ax.set_ylim(0, 7.9); ax.axis("off")
    w, h, y = 3.55, 2.5, 4.4
    xs = [0.2, 4.2, 8.2, 12.2]
    steps = [
        ("Mechanics", "Statics: volumes, lung and\nchest wall curves, FRC\nDynamics I and II: a breath,\nairway resistance, flow limits", C["lung"]),
        ("Ventilation", "Fresh air to the alveoli\n$\dot{V}_E$ = V$_T$ × RR\nAlveolar gas equation\nPaCO$_2$ and $\dot{V}_A$", C["cw"]),
        ("Gas exchange", "Diffusion across the barrier\nVentilation and perfusion\n(V/Q) matching\nShunt and dead space", C["green"]),
        ("Transport", "O$_2$ on hemoglobin, O$_2$ content\nCO$_2$ as bicarbonate\nO$_2$ delivery = $\dot{Q}$ × CaO$_2$\nAcid-base", C["system"]),
    ]
    for x, (t, b, col) in zip(xs, steps):
        box(ax, x, y, w, h, t, b, col)
    for i in range(3):
        arrow(ax, (xs[i] + w + 0.05, y + h / 2), (xs[i + 1] - 0.05, y + h / 2), C["ink"], lw=1.6)
    ax.text(0.2, 7.55, "From the air ...", ha="left", fontsize=9.5, color=C["text"])
    ax.text(15.75, 7.55, "... to the mitochondria", ha="right", fontsize=9.5, color=C["text"])
    # control bar
    box(ax, 2.0, 1.2, 12.0, 1.9, "Control of ventilation",
        "Brainstem rhythm, chemoreceptors that sense CO$_2$, pH and O$_2$, and lung receptors\n"
        "set how much we breathe from minute to minute", C["purple"], fc="#f6f2f7")
    for x in xs:
        arrow(ax, (x + w / 2, 3.15), (x + w / 2, y - 0.05), C["purple"], lw=1.2, style="-|>", ms=9)
    ax.text(8.0, 0.35, "Then the whole system is tested: pulmonary function tests, exercise, and the respiratory consultant",
            ha="center", fontsize=9, color=C["ink"])
    fs.save(fig, PART, SLUG, "block-map.svg")


# ------------------------------------------------------------ 3. The two scaffolds
def node(ax, x, y, w, h, text, ec, fs_=9, fc="white", bold=False):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.04,rounding_size=0.2",
                                fc=fc, ec=ec, lw=1.6))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs_, color=C["ink"],
            fontweight="bold" if bold else "normal", linespacing=1.3)


def fig_scaffolds():
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 5.6), gridspec_kw=dict(width_ratios=[1.45, 1]))
    ax = axes[0]
    ax.set_xlim(0, 12); ax.set_ylim(0, 10); ax.axis("off")
    ax.set_title("A. Oxygenation: why is the PaO$_2$ low?", loc="left")
    node(ax, 6, 9.0, 4.6, 0.9, "Hypoxemia (low PaO$_2$)", C["system"], fs_=10, fc=C["highlight"], bold=True)
    node(ax, 6, 7.4, 6.6, 0.9, "Compute PAO$_2$ = (P$_B$ − P$_{H_2O}$) FiO$_2$ − PaCO$_2$/R\nthen the A–a gradient = PAO$_2$ − PaO$_2$",
         C["ink"], fs_=8.8)
    arrow(ax, (6, 8.55), (6, 7.87), C["ink"])
    node(ax, 2.9, 4.6, 5.0, 2.6, "A–a gradient normal\nThe alveolar PO$_2$ is low\n\n• Low P$_B$ (altitude)\n• Low FiO$_2$\n• Hypoventilation (high PaCO$_2$)",
         C["cw"], fs_=8.8)
    node(ax, 9.1, 4.6, 5.0, 2.6, "A–a gradient raised\nGas exchange is impaired\n\n• Diffusion limitation\n• V/Q mismatch\n• Shunt",
         C["system"], fs_=8.8)
    arrow(ax, (5.0, 6.93), (3.6, 5.95), C["ink"])
    arrow(ax, (7.0, 6.93), (8.4, 5.95), C["ink"])
    ax.text(9.1, 2.65, "A low mixed venous O$_2$ makes each of\nthese worse; it is not a cause on its own",
            ha="center", va="top", fontsize=8.3, color=C["text"])
    ax.text(0.3, 1.2, "Later chapters add: does the PaO$_2$ rise with supplemental O$_2$?\n"
            "V/Q mismatch and diffusion limitation respond; shunt responds poorly.",
            ha="left", va="top", fontsize=8.5, color=C["ink"])

    ax = axes[1]
    ax.set_xlim(0, 8); ax.set_ylim(0, 10); ax.axis("off")
    ax.set_title("B. Ventilation: why is the PaCO$_2$ high?", loc="left")
    node(ax, 4, 9.0, 4.4, 0.9, "Hypercapnia (high PaCO$_2$)", C["cw"], fs_=10, fc=C["cool"], bold=True)
    node(ax, 4, 7.4, 6.4, 0.9, "PaCO$_2$ $\propto$ $\dot{V}$CO$_2$ / $\dot{V}_A$\ntoo little alveolar ventilation for the CO$_2$ made",
         C["ink"], fs_=8.8)
    arrow(ax, (4, 8.55), (4, 7.87), C["ink"])
    # balance beam
    ax.plot([0.9, 7.1], [5.0, 4.2], color=C["ink"], lw=3)
    ax.add_patch(plt.Polygon([[3.75, 4.6], [4.25, 4.6], [4.0, 3.5]], closed=True, fc=C["ink"]))
    node(ax, 1.9, 5.62, 2.6, 1.2, "Strength\n(drive, nerves,\nmuscles)", C["green"], fs_=8.4)
    node(ax, 6.1, 5.08, 2.6, 1.2, "Load\n(airways, lungs,\nchest wall)", C["system"], fs_=8.4)
    
    ax.text(4, 2.9, "When the load outweighs the strength,\n$\dot{V}_A$ falls behind and PaCO$_2$ rises.\n"
            "\"Won't breathe\" or \"can't breathe\".", ha="center", va="top", fontsize=8.5, color=C["ink"])
    fig.subplots_adjust(wspace=0.05)
    fs.save(fig, PART, SLUG, "scaffolds.svg")


if __name__ == "__main__":
    fig_circuit()
    fig_block_map()
    fig_scaffolds()
