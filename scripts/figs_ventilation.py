"""Figures for the Alveolar Ventilation chapter (P5).

Run:  cd site/scripts && MPLCONFIGDIR=$TMPDIR PNG_PREVIEW=<folder> python3 figs_ventilation.py
Curves come from the course equations:
  PAO2 = FiO2 (PB - 47) - PaCO2 / R
  PaCO2 = K * VCO2 / VA, with K = 0.863 (Ventilation 2026 slide 28 notes)
"""
import numpy as np
from matplotlib.patches import FancyBboxPatch, Rectangle

import figstyle as fs

plt = fs.plt
C = fs.C
M = fs.MINUS
PART, SLUG = "pulmonary", "ventilation"
K = 0.863
R = 0.8


def pao2(pb, fio2, paco2, r=R):
    return fio2 * (pb - 47) - paco2 / r


# ---------------------------------------------------------------- 1. PO2 from air to alveolus
def fig_po2_steps():
    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    labels = ["Ambient air\n(dry)", "Inspired air\n(humidified)", "Alveolar gas"]
    vals = [760 * 0.209, 713 * 0.209, pao2(760, 0.21, 40)]
    x = np.arange(3)
    bars = ax.bar(x, vals, width=0.55, color=[C["gray"], C["cw"], C["system"]], zorder=3)
    for xi, v in zip(x, vals):
        ax.text(xi, v + 4, f"{v:.0f}", ha="center", fontsize=11, color=C["ink"], fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("PO$_2$ (mm Hg)")
    ax.set_ylim(0, 185)
    fs.grid(ax)
    ax.grid(axis="x", visible=False)
    ax.annotate("", xy=(0.72, 152), xytext=(0.28, 160),
                arrowprops=dict(arrowstyle="-|>", color=C["text"], lw=1.2))
    ax.text(0.5, 167, f"water vapor\ntakes 47 of 760", ha="center", fontsize=8.8, color=C["text"])
    ax.annotate("", xy=(1.72, 104), xytext=(1.28, 145),
                arrowprops=dict(arrowstyle="-|>", color=C["text"], lw=1.2))
    ax.text(1.62, 135, "O$_2$ leaves for the blood,\nCO$_2$ arrives:\n" + M + " PaCO$_2$/R = " + M + "50",
            ha="left", fontsize=8.8, color=C["text"])
    ax.text(0, 20, "760 × 0.209", ha="center", fontsize=8.5, color="white")
    ax.text(1, 20, "713 × 0.209", ha="center", fontsize=8.5, color="white")
    ax.text(2, 20, "149 " + M + " 40/0.8", ha="center", fontsize=8.5, color="white")
    fs.save(fig, PART, SLUG, "po2-steps.svg")


# ---------------------------------------------------------------- 2. Airway cross-sectional area
# Weibel 1963, model A: total cross-sectional area (cm2) by generation, as plotted on 2026 slide 7.
WEIBEL_AREA = [2.54, 2.33, 2.13, 2.00, 2.48, 3.11, 3.96, 5.10, 6.95, 9.56, 13.4, 19.6, 28.8,
               44.5, 69.4, 113, 180, 300, 534, 944, 1600, 3220, 5880, 11800]


def fig_airway_area():
    g = np.arange(24)
    a = np.array(WEIBEL_AREA)
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    ax.axvspan(16.5, 23.5, color=C["highlight"], zorder=0)
    ax.text(20, 1.4, "Respiratory zone\n(generations 17 to 23)", ha="center", fontsize=9.5, color=C["lung"],
            fontweight="bold")
    ax.text(8, 14000, "Conducting zone (generations 0 to 16)\nabout 150 mL, no gas exchange",
            ha="center", va="center", fontsize=9.5, color=C["ink"])
    ax.semilogy(g, a, "-s", color=C["ink"], lw=2, ms=5, mfc="white", mec=C["ink"], zorder=3)
    ax.set_ylim(0.6, 30000)
    ax.set_xlim(-0.7, 23.7)
    ax.set_xticks([0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 23])
    ax.set_yticks([1, 10, 100, 1000, 10000])
    ax.set_yticklabels(["1", "10", "100", "1,000", "10,000"])
    ax.set_xlabel("Airway generation (0 = trachea)")
    ax.set_ylabel("Total cross-sectional area (cm$^2$)", color=C["ink"])
    fs.grid(ax)
    ax2 = ax.twinx()
    vel = a.min() / a * 100
    ax2.plot(g, vel, color=C["system"], lw=2, ls=(0, (5, 3)))
    ax2.set_ylim(0, 160)
    ax2.set_ylabel("Relative air velocity (%)", color=C["system"])
    ax2.spines["right"].set_visible(True)
    ax2.tick_params(axis="y", colors=C["system"])
    ax2.text(4.6, 96, "velocity peaks where total\narea is smallest (generations 2 to 4)",
             fontsize=9, color=C["system"])
    ax.text(9.6, 30, "total area", fontsize=9.5, color=C["ink"], ha="right")
    fs.save(fig, PART, SLUG, "airway-area.svg")


# ---------------------------------------------------------------- 3. Fast versus deep breathing
def fig_fast_deep():
    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    cases = [("Quiet breathing", 500, 150, 15), ("Fast", 500, 150, 30), ("Deep", 1000, 170, 15)]
    x = np.arange(3)
    for xi, (lab, vt, vd, rr) in zip(x, cases):
        ax.bar(xi, vd, width=0.5, color=C["gray"], zorder=3)
        ax.bar(xi, vt - vd, bottom=vd, width=0.5, color=C["lung"], zorder=3)
        ax.text(xi, vd / 2, f"V$_D$ {vd}", ha="center", va="center", color="white", fontsize=9)
        ax.text(xi, vd + (vt - vd) / 2, f"V$_A$ {vt - vd}", ha="center", va="center", color="white", fontsize=9.5)
        ve = vt * rr
        va = (vt - vd) * rr
        ax.text(xi, vt + 40, f"V$_T$ {vt} mL × {rr}/min\n"
                             f"$\\dot{{V}}_E$ = {ve:,} mL/min\n$\\dot{{V}}_A$ = {va:,} mL/min\nV$_D$/V$_T$ = {vd / vt:.2f}",
                ha="center", va="bottom", fontsize=8.8, color=C["ink"])
    ax.set_xticks(x)
    ax.set_xticklabels([c[0] for c in cases])
    ax.set_ylabel("Volume per breath (mL)")
    ax.set_ylim(0, 1500)
    fs.grid(ax)
    ax.grid(axis="x", visible=False)
    fs.save(fig, PART, SLUG, "fast-vs-deep.svg")


# ---------------------------------------------------------------- 4. PaCO2 against alveolar ventilation
def fig_paco2_va():
    va = np.linspace(1.5, 25, 400)
    fig, ax = plt.subplots(figsize=(7.4, 4.8))
    for vco2, col, lab, xy in ((250, C["system"], "Rest: $\\dot{V}$CO$_2$ 250 mL/min", (10.5, 3.5)),
                               (750, C["cw"], "Mild exercise: $\\dot{V}$CO$_2$ 750 mL/min", (12.8, 62))):
        p = K * vco2 / va
        ax.plot(va, p, color=col, lw=2.4)
        ax.text(*xy, lab, color=col, fontsize=9.5, fontweight="bold")
    ax.axhline(40, color=C["axis"], lw=1, ls=(0, (4, 3)))
    va40r, va40e = K * 250 / 40, K * 750 / 40
    ax.plot([va40r, va40e], [40, 40], "o", color=C["ink"], ms=6, zorder=5)
    ax.annotate("", xy=(va40e - 0.3, 43), xytext=(va40r + 0.3, 43),
                arrowprops=dict(arrowstyle="-|>", color=C["ink"], lw=1.3))
    ax.text((va40r + va40e) / 2, 47, "$\\dot{V}_A$ must triple to hold 40", ha="center", fontsize=9, color=C["ink"])
    ax.text(va40r, 33, f"{va40r:.1f}", ha="center", fontsize=8.5, color=C["ink"])
    ax.text(va40e, 33, f"{va40e:.1f}", ha="center", fontsize=8.5, color=C["ink"])
    ax.text(24.7, 42, "above 40: hypoventilation", fontsize=8.8, color=C["text"], ha="right", va="bottom")
    ax.text(24.7, 38, "below 40: hyperventilation", fontsize=8.8, color=C["text"], ha="right", va="top")
    ax.set_xlim(0, 25)
    ax.set_ylim(0, 120)
    ax.set_xlabel("Alveolar ventilation, $\\dot{V}_A$ (L/min)")
    ax.set_ylabel("PaCO$_2$ (mm Hg)")
    fs.grid(ax)
    fs.save(fig, PART, SLUG, "paco2-va.svg")


# ---------------------------------------------------------------- 5. VA sets both alveolar gases
def fig_alveolar_gases_va():
    va = np.linspace(1.6, 20, 400)
    paco2 = K * 250 / va
    pa_o2 = pao2(760, 0.21, paco2)
    fig, ax = plt.subplots(figsize=(7.4, 4.8))
    ax.plot(va, pa_o2, color=C["system"], lw=2.4)
    ax.plot(va, paco2, color=C["cw"], lw=2.4)
    piO2 = 0.21 * 713
    ax.axhline(piO2, color=C["axis"], lw=1, ls=(0, (4, 3)))
    ax.text(19.8, piO2 + 3, "PIO$_2$ about 149: the ceiling", ha="right", fontsize=8.8, color=C["text"])
    v0 = K * 250 / 40
    ax.plot([v0, v0], [40, pao2(760, 0.21, 40)], "o", color=C["ink"], ms=6, zorder=5)
    ax.axvline(v0, color=C["axis"], lw=0.8, ls=(0, (2, 3)))
    ax.text(v0 + 0.3, 160, "rest", fontsize=9, color=C["ink"])
    ax.text(14, 114, "PAO$_2$", color=C["system"], fontsize=11, fontweight="bold")
    ax.text(14, 25, "PACO$_2$", color=C["cw"], fontsize=11, fontweight="bold")
    ax.text(2.2, 6, "hypoventilation", fontsize=8.8, color=C["text"])
    ax.text(9.5, 6, "hyperventilation", fontsize=8.8, color=C["text"])
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 170)
    ax.set_xlabel("Alveolar ventilation, $\\dot{V}_A$ (L/min)")
    ax.set_ylabel("Partial pressure (mm Hg)")
    fs.grid(ax)
    fs.save(fig, PART, SLUG, "alveolar-gases-va.svg")


# ---------------------------------------------------------------- 6. Alveolar PO2 in six settings
def fig_pao2_settings():
    rows = [
        ("Sea level\nPB 760", pao2(760, 0.21, 40), C["system"]),
        ("Chicago\nPB 747", pao2(747, 0.21, 40), C["system"]),
        ("Airplane cabin\n(7,000 ft) PB 586", pao2(586, 0.21, 40), C["lung"]),
        ("Everest summit, PB 253\nroom air, PaCO$_2$ 40", pao2(253, 0.21, 40), C["gray"]),
        ("Everest summit, PB 253\nbottled O$_2$ (FiO$_2$ 1.0)", pao2(253, 1.0, 40), C["cw"]),
        ("Everest summit, PB 253\nroom air, PaCO$_2$ 8", pao2(253, 0.21, 8), C["green"]),
    ]
    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    y = np.arange(len(rows))[::-1]
    for yi, (lab, v, col) in zip(y, rows):
        ax.barh(yi, v, height=0.6, color=col, zorder=3)
        ax.text(v + 3 if v > 0 else 3, yi, fs.fmt(round(v, 1)) if abs(v) < 10 else f"{v:.0f}",
                va="center", fontsize=10, color=C["ink"], fontweight="bold")
    ax.set_yticks(y)
    ax.set_yticklabels([r[0] for r in rows], fontsize=9.5)
    ax.axvline(0, color=C["ink"], lw=1)
    ax.set_xlim(-15, 185)
    ax.set_xlabel("PAO$_2$ from the alveolar gas equation (mm Hg)")
    fs.grid(ax)
    ax.grid(axis="y", visible=False)
    ax.text(18, y[3], "impossible: no steady state", va="center", fontsize=8.8, color=C["text"])
    ax.text(150, y[4], "the easy way", va="center", ha="right", fontsize=8.8, color="white")
    ax.text(47, y[5], "the hard way", va="center", fontsize=8.8, color=C["text"])
    fs.save(fig, PART, SLUG, "pao2-settings.svg")


if __name__ == "__main__":
    fig_po2_steps()
    fig_airway_area()
    fig_fast_deep()
    fig_paco2_va()
    fig_alveolar_gases_va()
    fig_pao2_settings()
