"""Figures for the Pulmonary Acid Base chapter.

Run:  cd site/scripts && MPLCONFIGDIR=$TMPDIR PNG_PREVIEW=<folder> python3 figs_acid-base.py
Writes SVGs to ../pulmonary/figures/acid-base/.

Relations used, as the course writes them:
  pH = 6.1 + log10( HCO3 / (0.03 * PaCO2) )            (Henderson-Hasselbalch, shown as a check)
  PAO2 = (PB - PH2O) * FiO2 - PaCO2 / R                 (alveolar gas equation; PB 747, R 0.8)
Every blood gas drawn here is Henderson-Hasselbalch consistent.
"""
import numpy as np
import figstyle as fs
from figstyle import C, plt, MINUS
from matplotlib.patches import FancyBboxPatch, Polygon, Circle

PART, SLUG = "pulmonary", "acid-base"


def save(fig, name):
    fs.save(fig, PART, SLUG, name)


def ph(hco3, pco2):
    return 6.1 + np.log10(hco3 / (0.03 * pco2))


def hco3_at(phv, pco2):
    return 0.03 * pco2 * 10 ** (phv - 6.1)


# ---------------------------------------------------------------- 1. buffer curve
def fig_titration():
    frac = np.linspace(0.005, 0.995, 400)          # fraction of the buffer as HCO3-
    p = 6.1 + np.log10(frac / (1 - frac))
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    ax.axhspan(5.1, 7.1, color=C["cool"], zorder=0)
    ax.text(3, 6.95, "Best buffering: within about 1 pH unit of the pK", fontsize=9, color=C["venous"], va="top")
    ax.plot(frac * 100, p, color=C["system"], lw=2.4)
    ax.axhline(6.1, color=C["venous"], lw=1, ls="--")
    ax.text(101, 6.1, "pK 6.1", color=C["venous"], va="center", fontsize=10)
    f74 = 1 / (1 + 10 ** (6.1 - 7.4))
    ax.plot([f74 * 100], [7.4], "o", color=C["arterial"], ms=7, zorder=5)
    ax.annotate("Normal blood, pH 7.4\n(HCO$_3^-$ : dissolved CO$_2$ = 20 : 1)", xy=(f74 * 100, 7.4),
                xytext=(48, 7.75), fontsize=9.5, color=C["arterial"],
                arrowprops=dict(arrowstyle="->", color=C["arterial"], lw=1))
    ax.set_xlim(0, 100)
    ax.set_ylim(4, 8.2)
    ax.set_xlabel("Share of the buffer present as HCO$_3^-$ (%)")
    ax.set_ylabel("pH")
    ax.annotate("", xy=(22, 4.45), xytext=(48, 4.45), arrowprops=dict(arrowstyle="->", color=C["arterial"], lw=1.5))
    ax.text(35, 4.6, "acid added", ha="center", fontsize=9, color=C["arterial"])
    ax.annotate("", xy=(78, 4.45), xytext=(52, 4.45), arrowprops=dict(arrowstyle="->", color=C["venous"], lw=1.5))
    ax.text(65, 4.6, "base added", ha="center", fontsize=9, color=C["venous"])
    fs.grid(ax)
    save(fig, "buffer-curve.svg")


# ---------------------------------------------------------------- 2. four disorders
def fig_four_disorders():
    fig, ax = plt.subplots(figsize=(7.4, 5.6))
    P = np.linspace(10, 100, 200)
    for v in (7.1, 7.2, 7.3, 7.4, 7.5, 7.6):
        y = hco3_at(v, P)
        m = y < 44
        ax.plot(P[m], y[m], color=C["axis"] if v != 7.4 else C["text"], lw=0.9 if v != 7.4 else 1.4, zorder=1)
        # label at the top or right edge
        if hco3_at(v, 100) < 44:
            ax.text(101, hco3_at(v, 100), f"{v:.1f}", fontsize=8.5, color=C["text"], va="center")
        else:
            x = 44 / (0.03 * 10 ** (v - 6.1))
            ax.text(x, 44.6, f"{v:.1f}", fontsize=8.5, color=C["text"], ha="center")
    # shade acidemia (below 7.4 line = right/below) lightly
    N = (40, 24)
    ax.plot(*N, "o", color=C["ink"], ms=8, zorder=6)
    ax.text(41.5, 22.0, "Normal\n7.40, 40, 24", fontsize=9, color=C["ink"], va="top")

    def path(p1, h1, p2, h2, col, lab, lx, ly, ha="left"):
        ax.annotate("", xy=(p1, h1), xytext=N, arrowprops=dict(arrowstyle="-|>", color=col, lw=2.2), zorder=4)
        ax.annotate("", xy=(p2, h2), xytext=(p1, h1),
                    arrowprops=dict(arrowstyle="-|>", color=col, lw=1.6, ls=(0, (4, 2))), zorder=4)
        ax.plot([p2], [h2], "o", color=col, ms=5, zorder=5)
        ax.text(lx, ly, lab, color=col, fontsize=9.5, ha=ha, va="center", fontweight="bold")

    # respiratory acidosis: PaCO2 up at ~constant HCO3, then kidney raises HCO3
    path(80, 26, 80, 34, C["arterial"], "Respiratory acidosis", 81, 21)
    # respiratory alkalosis: PaCO2 down, then kidney lowers HCO3
    path(25, 22, 25, 17.5, C["venous"], "Respiratory\nalkalosis", 13, 12.5)
    # metabolic acidosis: HCO3 down, then lung lowers PaCO2
    path(40, 12, 28, 12, C["gold"], "Metabolic acidosis", 47, 10.5)
    # metabolic alkalosis: HCO3 up, then lung raises PaCO2 a little
    path(40, 36, 46, 36, C["green"], "Metabolic alkalosis", 30, 40.5, ha="center")

    ax.set_xlim(10, 100)
    ax.set_ylim(5, 44)
    ax.set_xlabel("PaCO$_2$ (mm Hg)")
    ax.set_ylabel("HCO$_3^-$ (mEq/L)")
    ax.text(97, 7.0, "Acidemia: below and right of the 7.4 line", fontsize=8.5, ha="right", color=C["text"])
    ax.text(12, 42.0, "Alkalemia: above and left of the 7.4 line", fontsize=8.5, ha="left", color=C["text"])
    ax.text(97, 9.0, "Gray lines: constant pH", fontsize=8.5, ha="right", color=C["text"])
    fs.grid(ax)
    # legend for line styles
    ax.plot([], [], color=C["ink"], lw=2.2, label="Primary change")
    ax.plot([], [], color=C["ink"], lw=1.6, ls=(0, (4, 2)), label="Compensation")
    ax.legend(loc="lower right", bbox_to_anchor=(1.0, 0.11), fontsize=9)
    save(fig, "four-disorders.svg")


# ---------------------------------------------------------------- 3. alveolar gas in the opioid case
def fig_opioid_gas():
    PB, PH2O, R = 747, 47, 0.8
    cases = [("Normal\nroom air", 0.21, 40), ("Opioid overdose\nroom air", 0.21, 85),
             ("Opioid overdose\n30% O$_2$", 0.30, 85)]
    fig, ax = plt.subplots(figsize=(7.0, 4.8))
    x = np.arange(len(cases))
    for i, (lab, fio2, pco2) in enumerate(cases):
        pao2 = (PB - PH2O) * fio2 - pco2 / R
        n2 = PB - PH2O - pco2 - pao2
        parts = [(PH2O, C["gray"], "H$_2$O"), (pco2, C["gold"], "CO$_2$"), (pao2, C["venous"], "O$_2$"),
                 (n2, C["shade"], "N$_2$")]
        b = 0
        for val, col, nm in parts:
            ax.bar(i, val, bottom=b, color=col, width=0.6, edgecolor="white", lw=1)
            if nm != "N$_2$":
                ax.text(i, b + val / 2, f"{nm} {val:.0f}", ha="center", va="center", fontsize=9.5,
                        color="white" if nm != "H$_2$O" or True else C["ink"], fontweight="bold")
            else:
                ax.text(i, b + val / 2, f"N$_2$ and others\n{val:.0f}", ha="center", va="center", fontsize=9,
                        color=C["text"])
            b += val
    ax.set_xticks(x)
    ax.set_xticklabels([c[0] for c in cases], fontsize=10)
    ax.set_ylabel("Partial pressure in alveolar gas (mm Hg)")
    ax.set_ylim(0, 800)
    ax.axhline(PB, color=C["axis"], lw=1, ls="--")
    ax.text(2.42, PB + 12, "PB 747 (Chicago)", ha="right", fontsize=9, color=C["text"])
    ax.spines["bottom"].set_visible(False)
    ax.tick_params(axis="x", length=0)
    save(fig, "alveolar-gas-opioid.svg")


# ---------------------------------------------------------------- 4. strength and load
def fig_strength_load():
    fig, ax = plt.subplots(figsize=(8.6, 6.0))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8.0)
    ax.axis("off")
    # fulcrum and beam, tipped toward the load side
    ax.add_patch(Polygon([[4.6, 0.75], [5.4, 0.75], [5.0, 1.6]], closed=True, color=C["ink"]))
    y0, y1 = 2.05, 1.15
    beam = lambda x: y0 + (y1 - y0) * (x - 0.6) / (9.4 - 0.6)
    ax.plot([0.6, 9.4], [beam(0.6), beam(9.4)], color=C["ink"], lw=3)
    # strength box
    def box(x, y, w, h, title, lines, col):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06,rounding_size=0.12",
                                    fc="white", ec=col, lw=1.6))
        ax.text(x + w / 2, y + h - 0.22, title, ha="center", va="top", fontsize=11.5, fontweight="bold", color=col)
        ax.text(x + 0.18, y + h - 0.68, "\n".join(lines), ha="left", va="top", fontsize=9.3, color=C["ink"],
                linespacing=1.45)
    box(0.15, beam(0.6) + 0.1, 3.5, 5.5, "Strength (ability to do work)", [
        "Won't breathe: respiratory drive",
        "   opioids, sedatives, brainstem stroke",
        "Can't breathe: nerves and muscles",
        "   paralytics, ALS, myasthenia gravis,",
        "   high spinal cord injury",
        "Can't breathe: muscle fuel",
        "   malnutrition, low phosphate,",
        "   low K$^+$ or Mg$^{2+}$",
    ], C["venous"])
    box(6.05, beam(6.05) + 0.1, 3.8, 5.5, "Load on the system", [
        "Metabolic: more CO$_2$ to clear",
        "   fever, sepsis, an added acid load",
        "Airways: high resistance",
        "   asthma, COPD",
        "Lung and pleura: low compliance",
        "   fibrosis, pneumonia, effusion,",
        "   pneumothorax, large heart",
        "Chest wall and abdomen",
        "   kyphoscoliosis, obesity,",
        "   pregnancy, ascites",
        "Dead space: wasted ventilation",
        "   pulmonary embolism",
    ], C["arterial"])
    ax.text(5.0, 0.25, r"When load outweighs strength, $\dot{V}_A$ falls, PaCO$_2$ rises and pH falls: respiratory acidosis",
            ha="center", fontsize=10, color=C["ink"])
    save(fig, "strength-load.svg")


# ---------------------------------------------------------------- 5. tiring asthma
def fig_asthma_course():
    """Schematic PaCO2 course through Small Group 3, Case 1 (normal, presentation 7.45/33, tiring 7.28/54)."""
    from scipy.interpolate import PchipInterpolator
    tt = np.array([0, 1, 4, 6, 7.5, 10])
    yy = np.array([40, 33, 33, 40, 46, 54])
    f = PchipInterpolator(tt, yy)
    t = np.linspace(0, 10, 300)
    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    ax.axhspan(20, 40, color=C["cool"], zorder=0)
    ax.axhspan(40, 60, color=C["highlight"], zorder=0)
    ax.text(0.15, 21.5, "PaCO$_2$ below 40: hyperventilation", fontsize=8.5, color=C["venous"])
    ax.text(0.15, 58.2, "PaCO$_2$ above 40: hypoventilation", fontsize=8.5, color=C["arterial"], va="top")
    ax.plot(t, f(t), color=C["system"], lw=2.4)
    ax.axhline(40, color=C["text"], lw=1, ls="--")
    ax.plot([1, 6, 10], [33, 40, 54], "o", color=C["system"], ms=6, zorder=5)
    ax.annotate("Presentation: pH 7.45, PaCO$_2$ 33\nhyperventilating", xy=(1, 33), xytext=(1.5, 25.5),
                fontsize=9, color=C["ink"], arrowprops=dict(arrowstyle="->", color=C["text"], lw=0.8))
    ax.annotate("PaCO$_2$ back to 40:\ntiring, not better", xy=(6, 40), xytext=(2.6, 47.5), fontsize=9,
                color=C["arterial"], arrowprops=dict(arrowstyle="->", color=C["arterial"], lw=0.8))
    ax.annotate("pH 7.28, PaCO$_2$ 54", xy=(10, 54), xytext=(6.6, 53.5), fontsize=9, color=C["ink"],
                va="center", arrowprops=dict(arrowstyle="->", color=C["text"], lw=0.8))
    ax.set_xlim(0, 10.4)
    ax.set_ylim(20, 60)
    ax.set_xticks([])
    ax.set_xlabel("Time (schematic)")
    ax.set_ylabel("PaCO$_2$ (mm Hg)")
    save(fig, "asthma-course.svg")


if __name__ == "__main__":
    fig_titration()
    fig_four_disorders()
    fig_opioid_gas()
    fig_strength_load()
    fig_asthma_course()
