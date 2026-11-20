"""Figures for the Transport of O2 and CO2 chapter (P7).

Run:  cd site/scripts && MPLCONFIGDIR=$TMPDIR PNG_PREVIEW=<folder> python3 figs_o2-co2-transport.py

HbO2 curve: a Hill equation, S = (P/P50)^n / (1 + (P/P50)^n), with P50 27 mm Hg and n 2.79.
That standard fit passes through all four course anchor points:
    27 mm Hg -> 50%, 40 -> 75%, 60 -> 90%, 100 -> 97.5%  (printed when the script runs).
Content: CaO2 = 1.39 x Hb x S + 0.003 x PO2 (course constants).
Shifted and CO curves are illustrative (P50 moved; COHb curve left-shifted to P50 about 10).
CO2 curves: power functions through the course points (40 mm Hg, 48 mL/dL arterial;
46 mm Hg, 52 mL/dL venous) with a slope of about 0.33 mL/dL per mm Hg at 40.
"""
import numpy as np
from matplotlib.patches import FancyBboxPatch, Polygon

import figstyle as fs

plt = fs.plt
C = fs.C
M = fs.MINUS
PART, SLUG = "pulmonary", "o2-co2-transport"
P50, NH, HB = 27.0, 2.79, 15.0


def sat(p, p50=P50, n=NH):
    p = np.maximum(np.asarray(p, float), 0)
    x = (p / p50) ** n
    return x / (1 + x)


def content(p, hb=HB, p50=P50, scale=1.0):
    return 1.39 * hb * scale * sat(p, p50) + 0.003 * np.asarray(p, float)


for pp, target in ((27, 50), (40, 75), (60, 90), (100, 97.5)):
    print(f"Hill fit: PO2 {pp} -> {100 * sat(pp):.1f}% (course {target}%)")

P = np.linspace(0, 120, 600)


def hb_axes(ax, xmax=100):
    ax.set_xlim(0, xmax)
    ax.set_ylim(0, 105)
    ax.set_xlabel("PO$_2$ (mm Hg)")
    ax.set_ylabel("Hb saturation (%)")
    fs.grid(ax)


# ---------------------------------------------------------------- 1. HbO2 curve, anchor points, zones
def fig_hbo2():
    p = np.linspace(0, 100, 500)
    fig, ax = plt.subplots(figsize=(7.6, 5.2))
    hb_axes(ax)
    ax.axvspan(85, 100, color=C["highlight"], zorder=0)
    ax.axvspan(12, 45, color=C["cool"], zorder=0)
    ax.text(92.5, 30, "loading\nzone\n(lungs)", ha="center", fontsize=9, color=C["lung"])
    ax.text(28.5, 3, "unloading zone (tissues)", ha="center", fontsize=9, color=C["cw"])
    nc = p / (p + P50)
    ax.plot(p, 100 * nc, color=C["gray"], lw=1.6, ls=(0, (5, 3)))
    ax.text(68, 58, "no cooperativity\n(same P$_{50}$)", fontsize=9, color=C["gray"])
    ax.plot(p, 100 * sat(p), color=C["system"], lw=2.8)
    pts = [(100, 97.5, "arterial\n100, 97.5%", (88, 80)), (60, 90, "the knee\n60, 90%", (63, 76)),
           (40, 75, "mixed venous\n40, 75%", (46, 58)), (27, 50, "P$_{50}$\n27, 50%", (31, 36))]
    for x, y, lab, xy in pts:
        ax.plot([x], [y], "o", color=C["ink"], ms=7, zorder=5)
        ax.annotate(lab, xy=(x, y), xytext=xy, fontsize=9, color=C["ink"],
                    arrowprops=dict(arrowstyle="-", color=C["ink"], lw=0.7))
    fs.save(fig, PART, SLUG, "hbo2-curve.svg")


# ---------------------------------------------------------------- 2. O2 content: bound, dissolved, Hb level
def fig_content():
    p = np.linspace(0, 150, 600)
    fig, ax = plt.subplots(figsize=(7.6, 5.0))
    ax.plot(p, content(p, hb=20.2), color=C["green"], lw=2.2)
    ax.plot(p, content(p), color=C["system"], lw=2.8)
    ax.plot(p, content(p, hb=7.5), color=C["lung"], lw=2.2)
    ax.plot(p, 0.003 * p, color=C["cw"], lw=1.8, ls=(0, (4, 2)))
    ax.text(150, content(150, hb=20.2) + 0.7, "polycythemia (Hb 20)", ha="right", fontsize=9, color=C["green"])
    ax.text(150, content(150) + 0.7, "normal (Hb 15)", ha="right", fontsize=9, color=C["system"])
    ax.text(150, content(150, hb=7.5) + 0.7, "anemia (Hb 7.5)", ha="right", fontsize=9, color=C["lung"])
    ax.text(150, 0.003 * 150 + 0.6, "dissolved O$_2$ (0.003 × PO$_2$)", ha="right", fontsize=9, color=C["cw"])
    for x in (40, 100):
        ax.plot([x], [content(x)], "o", color=C["ink"], ms=6, zorder=5)
    # Labels match the text's worked examples (1.39 x 15 x 0.975 + 0.3; 1.39 x 15 x 0.75 + 0.12).
    ax.text(101, content(100) - 2.2, "20.6", fontsize=9, color=C["ink"])
    ax.text(41, content(40) - 2.2, "15.8", fontsize=9, color=C["ink"])
    ax.set_xlim(0, 150)
    ax.set_ylim(0, 30)
    ax.set_xlabel("PO$_2$ (mm Hg)")
    ax.set_ylabel("O$_2$ content (mL O$_2$/dL)")
    fs.grid(ax)
    fs.save(fig, PART, SLUG, "o2-content.svg")


# ---------------------------------------------------------------- 3. Curve shifts
def fig_shifts():
    p = np.linspace(0, 100, 500)
    fig, ax = plt.subplots(figsize=(8.8, 4.8))
    hb_axes(ax)
    ax.plot(p, 100 * sat(p, 20), color=C["cw"], lw=2, ls=(0, (5, 3)))
    ax.plot(p, 100 * sat(p), color=C["system"], lw=2.8)
    ax.plot(p, 100 * sat(p, 36), color=C["lung"], lw=2, ls=(0, (5, 3)))
    ax.axhline(50, color=C["axis"], lw=0.8)
    for x, col in ((20, C["cw"]), (27, C["system"]), (36, C["lung"])):
        ax.plot([x], [50], "o", color=col, ms=6, zorder=5)
    ax.text(13, 53, "P$_{50}$ 20", fontsize=8.5, color=C["cw"], ha="center")
    ax.text(27, 44, "27", fontsize=8.5, color=C["system"], ha="center")
    ax.text(41, 44, "P$_{50}$ 36", fontsize=8.5, color=C["lung"], ha="center")
    ax.text(43, 4, "Right shift (lower affinity,\nmore unloading):\nhigher temperature\nhigher PCO$_2$ and H$^+$ (Bohr effect)\nmore 2,3-DPG (hours to days)",
            fontsize=9, color=C["lung"], va="bottom")
    ax.text(83, 4, "Left shift (higher affinity):\nlower temperature\nlower PCO$_2$ and H$^+$ (alkalosis)\nless 2,3-DPG (stored blood)\nCO, fetal Hb, methemoglobin",
            fontsize=9, color=C["cw"], va="bottom")
    ax.set_xlim(0, 120)
    fs.save(fig, PART, SLUG, "curve-shifts.svg")


# ---------------------------------------------------------------- 4. CO versus anemia, content
def fig_co_anemia():
    p = np.linspace(0, 100, 500)
    fig, ax = plt.subplots(figsize=(7.6, 5.0))
    ax.axvspan(25, 40, color=C["cool"], zorder=0)
    ax.axvspan(95, 100, color=C["highlight"], zorder=0)
    ax.text(32.5, 23, "tissue PO$_2$", ha="center", fontsize=9, color=C["cw"])
    ax.text(97.5, 23, "lung", ha="center", fontsize=9, color=C["lung"])
    normal = content(p)
    anemia = content(p, hb=7.5)
    cohb = 1.39 * HB * 0.5 * sat(p, 10) + 0.003 * p
    ax.plot(p, normal, color=C["system"], lw=2.8)
    ax.plot(p, anemia, color=C["lung"], lw=2.4)
    ax.plot(p, cohb, color=C["ink"], lw=2.4, ls=(0, (6, 2)))
    ax.text(55, content(55) + 1.8, "normal Hb", fontsize=9.5, color=C["system"])
    ax.text(62, content(62, hb=7.5) - 2.2, "anemia, half the Hb", fontsize=9.5, color=C["lung"])
    ax.text(48, 11.3, "50% COHb", fontsize=9.5, color=C["ink"])
    for curve, col, lab, dx in ((anemia, C["lung"], "gives up", -1), (cohb, C["ink"], "gives up", 1)):
        c100, c40 = np.interp(100, p, curve), np.interp(40, p, curve)
    a_d = np.interp(100, p, anemia) - np.interp(40, p, anemia)
    c_d = np.interp(100, p, cohb) - np.interp(40, p, cohb)
    print(f"From 100 to 40 mm Hg: anemia gives up {a_d:.1f}, 50% COHb gives up {c_d:.1f} mL/dL")
    ax.text(3, 26.5, f"From 100 down to 40 mm Hg, anemic blood gives up about {a_d:.1f} mL/dL;\n"
                     "50% COHb blood gives up almost none.", fontsize=8.8, color=C["text"])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 29)
    ax.set_xlabel("PO$_2$ (mm Hg)")
    ax.set_ylabel("O$_2$ content (mL O$_2$/dL)")
    fs.grid(ax)
    fs.save(fig, PART, SLUG, "co-vs-anemia.svg")


# ---------------------------------------------------------------- 5. Delivery, uptake, return
def fig_fick_loop():
    fig, ax = plt.subplots(figsize=(9.0, 4.0))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4.6)
    ax.axis("off")

    def box(x, y, w, h, text, fc, ec):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05,rounding_size=0.15", fc=fc, ec=ec, lw=1.6))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=9.5, color=C["ink"])

    box(0.2, 1.6, 2.0, 1.4, "Lungs\nO$_2$ uptake\n250 mL/min", C["cool"], C["cw"])
    box(7.8, 1.6, 2.0, 1.4, "Tissues\n$\\dot{V}$O$_2$\n250 mL/min", C["highlight"], C["lung"])
    ax.annotate("", xy=(7.75, 3.6), xytext=(2.25, 3.6), arrowprops=dict(arrowstyle="-|>", color=C["system"], lw=3))
    ax.text(5, 3.8, "Arterial blood: CaO$_2$ about 20 mL/dL\nDelivery = Q × CaO$_2$ = 5,000 mL/min × 20/100 = 1,000 mL O$_2$/min",
            ha="center", va="bottom", fontsize=9.3, color=C["system"])
    ax.annotate("", xy=(2.25, 1.0), xytext=(7.75, 1.0), arrowprops=dict(arrowstyle="-|>", color=C["cw"], lw=3))
    ax.text(5, 0.8, "Mixed venous blood: CvO$_2$ about 15 mL/dL\nReturn = Q × CvO$_2$ = 5,000 mL/min × 15/100 = 750 mL O$_2$/min",
            ha="center", va="top", fontsize=9.3, color=C["cw"])
    ax.text(5, 2.3, "Uptake = delivery " + M + " return\n$\\dot{V}$O$_2$ = Q × (CaO$_2$ " + M + " CvO$_2$) = 1,000 " + M + " 750 = 250",
            ha="center", va="center", fontsize=10, color=C["ink"], fontweight="bold")
    fs.save(fig, PART, SLUG, "delivery-uptake-return.svg")


# ---------------------------------------------------------------- 6. Shares of CO2 carried and exchanged
def fig_co2_shares():
    fig, ax = plt.subplots(figsize=(7.8, 4.0))
    cats = ["Total CO$_2$ in\narterial blood\n(about 48 mL/dL)", "CO$_2$ given off\nin the lungs\n(about 4 mL/dL)"]
    parts = [("bicarbonate", C["system"], (90, 60)), ("carbamino", C["lung"], (5, 30)), ("dissolved", C["cw"], (5, 10))]
    y = np.array([1, 0])
    left = np.zeros(2)
    for name, col, vals in parts:
        vals = np.array(vals, float)
        ax.barh(y, vals, left=left, color=col, height=0.55, zorder=3)
        for yi, l, v in zip(y, left, vals):
            ax.text(l + v / 2, yi, f"{name}\n{v:.0f}%" if v >= 9 else f"{v:.0f}%", ha="center", va="center",
                    fontsize=8.8, color="white")
        left += vals
    ax.set_yticks(y)
    ax.set_yticklabels(cats, fontsize=9.5)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Percent")
    ax.text(97.5, 1.42, "carbamino and dissolved\n5% each", ha="right", fontsize=8.5, color=C["text"])
    fs.grid(ax)
    ax.grid(axis="y", visible=False)
    fs.save(fig, PART, SLUG, "co2-shares.svg")


# ---------------------------------------------------------------- 7. Haldane effect
def fig_haldane():
    b = 0.33 * 40 / 48
    pc = np.linspace(25, 70, 300)
    art = 48 * (pc / 40) ** b
    av = 52 / (46 ** b)
    ven = av * pc ** b
    fig, ax = plt.subplots(figsize=(7.6, 5.0))
    ax.plot(pc, ven, color=C["cw"], lw=2.6)
    ax.plot(pc, art, color=C["system"], lw=2.6)
    ax.text(70, av * 70 ** b + 0.6, "venous blood (SO$_2$ 75%)", ha="right", fontsize=9.5, color=C["cw"])
    ax.text(70, 50.6, "arterial blood (SO$_2$ 97.5%)", ha="right", fontsize=9.5, color=C["system"])
    a46 = 48 * (46 / 40) ** b
    ax.plot([40], [48], "o", color=C["system"], ms=8, zorder=5)
    ax.plot([46], [52], "o", color=C["cw"], ms=8, zorder=5)
    ax.text(38.8, 48.4, "a", fontsize=11, color=C["system"], fontweight="bold", ha="right")
    ax.text(45.2, 52.5, "v", fontsize=11, color=C["cw"], fontweight="bold", ha="right")
    ax.annotate("", xy=(45.85, 51.85), xytext=(40.15, 48.15), arrowprops=dict(arrowstyle="-|>", color=C["ink"], lw=1.8))
    ax.plot([46, 46], [48, a46], color=C["system"], lw=1, ls=(0, (2, 2)))
    ax.plot([40, 46], [48, 48], color=C["system"], lw=1, ls=(0, (2, 2)))
    ax.annotate("", xy=(46.6, 52), xytext=(46.6, a46), arrowprops=dict(arrowstyle="<->", color=C["cw"], lw=1.2))
    ax.annotate(f"Haldane effect:\nabout {52 - a46:.1f} mL/dL", xy=(46.4, (52 + a46) / 2), xytext=(31, 54.5),
                fontsize=9, color=C["cw"], va="center",
                arrowprops=dict(arrowstyle="-", color=C["cw"], lw=0.8))
    ax.text(47.2, (48 + a46) / 2 - 0.6, f"rise along the arterial curve, about {a46 - 48:.1f}", fontsize=9,
            color=C["system"], va="center")
    print(f"Haldane split: along curve {a46 - 48:.2f}, between curves {52 - a46:.2f}")
    ax.text(26, 58.6, "tissues: a to v\nlungs: v to a", fontsize=9, color=C["ink"])
    ax.set_xlim(25, 70)
    ax.set_ylim(40, 60)
    ax.set_yticks([40, 45, 50, 55, 60])
    ax.set_xlabel("PCO$_2$ (mm Hg)")
    ax.set_ylabel("Blood CO$_2$ content (mL/dL)")
    fs.grid(ax)
    fs.save(fig, PART, SLUG, "haldane.svg")


if __name__ == "__main__":
    fig_hbo2()
    fig_content()
    fig_shifts()
    fig_co_anemia()
    fig_fick_loop()
    fig_co2_shares()
    fig_haldane()
