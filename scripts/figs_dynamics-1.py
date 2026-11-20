"""Figures for the Respiratory Dynamics I chapter.

Run:  cd site/scripts && MPLCONFIGDIR=$TMPDIR PNG_PREVIEW=<folder> python3 figs_dynamics-1.py
Writes SVGs to ../pulmonary/figures/dynamics-1/.

The breath uses the lecture's round numbers: FRC 3.0 L with Pel 5 cm H2O, end inspiration 3.5 L
with Pel 9 (Dynamics I slides 7 and 10), so Pel rises 8 cm H2O per liter in this range. Volume
follows a smooth half-cosine in each phase. Alveolar pressure is -Raw x flow, and pleural
pressure is Palv - Pel (Palv = Ppl + Pel, decision T14). The regional figure uses the statics
model lung curve (statics_model.py), so it matches the statics chapter.
"""
import math
import numpy as np
import figstyle as fs
import statics_model as m
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle, FancyArrowPatch, Polygon

plt = fs.plt
C = fs.C
MINUS = fs.MINUS
PART, SLUG = "pulmonary", "dynamics-1"

FRC, VT = 3.0, 0.5
TI = TE = 1.5          # s, inspiration and expiration
RAW = 1.9              # cm H2O per L/s, so that Palv reaches about -1 and +1


def pel(V):
    return 5.0 + 8.0 * (V - FRC)


def breath(raw=RAW, n=601):
    t = np.linspace(0, TI + TE, n)
    V = np.where(t <= TI, FRC + VT / 2 * (1 - np.cos(np.pi * t / TI)),
                 FRC + VT - VT / 2 * (1 - np.cos(np.pi * (t - TI) / TE)))
    flow = np.where(t <= TI, VT / 2 * np.pi / TI * np.sin(np.pi * t / TI),
                    -VT / 2 * np.pi / TE * np.sin(np.pi * (t - TI) / TE))   # + = inspiratory
    palv = -raw * flow
    ppl = palv - pel(V)
    return t, V, flow, palv, ppl


# B and D at 3,300 mL, as on the slides and in errata 1 (0.3 L of the 0.5 L tidal volume)
T_B = TI / np.pi * np.arccos(1 - 2 * 0.3 / VT)
T_D = TI + TE / np.pi * np.arccos(1 - 2 * 0.2 / VT)
POINTS = [("A", 0.0), ("B", T_B), ("C", TI), ("D", T_D), ("E", TI + TE)]


def mark(ax, t, y, tp, lab, color, dy=0.0, dx=0.06, va="bottom"):
    yy = np.interp(tp, t, y)
    ax.plot([tp], [yy], "o", color=color, ms=5, zorder=5)
    ax.text(tp + dx, yy + dy, lab, fontsize=9.5, color=color, fontweight="bold", va=va)


# ------------------------------------------------------------ 1. Traces through one breath
def fig_traces():
    t, V, flow, palv, ppl = breath()
    fig, axes = plt.subplots(4, 1, figsize=(7.4, 8.6), sharex=True,
                             gridspec_kw=dict(hspace=0.18))
    specs = [
        (axes[0], (V - FRC) * 1000, "Volume above\nFRC (mL)", C["ink"], (-40, 560), [0, 250, 500]),
        (axes[1], ppl, "Pleural pressure\n(cm H$_2$O)", C["cw"], (-9.6, -4.4), [-9, -8, -7, -6, -5]),
        (axes[2], -flow, "Flow (L/s)\nout is +", C["green"], (-0.65, 0.65), [-0.5, 0, 0.5]),
        (axes[3], palv, "Alveolar pressure\n(cm H$_2$O)", C["system"], (-1.4, 1.4), [-1, 0, 1]),
    ]
    for ax, y, lab, col, ylim, ticks in specs:
        ax.axvspan(TI, TI + TE, color=C["shade"], zorder=0)
        ax.plot(t, y, color=col, lw=2.3)
        ax.set_ylim(*ylim)
        ax.set_yticks(ticks)
        ax.set_yticklabels([fs.fmt(v) for v in ticks])
        ax.set_ylabel(lab, fontsize=9.5)
        fs.grid(ax)
        if ylim[0] < 0 < ylim[1]:
            ax.axhline(0, color=C["axis"], lw=1)
        for name, tp in POINTS:
            dy = (ylim[1] - ylim[0]) * 0.05
            mark(ax, t, y, tp, name, col, dy=dy)
    axes[0].text(TI / 2, 590, "Inspiration (active)", ha="center", fontsize=10, color=C["ink"])
    axes[0].text(TI + TE / 2, 590, "Expiration (passive)", ha="center", fontsize=10, color=C["ink"])
    axes[0].set_ylim(-40, 640)
    axes[3].set_xlabel("Time (s)")
    axes[3].set_xlim(0, TI + TE + 0.15)
    fs.save(fig, PART, SLUG, "breath-traces.svg")


# ------------------------------------------------------------ 2. Single alveolus at each point
def alveolus(ax, title, ppl, pel_, palv, flow=0):
    ax.set_xlim(0, 10)
    ax.set_ylim(-2.6, 10.6)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, loc="left", fontsize=10.5)
    ax.add_patch(FancyBboxPatch((0.6, 0.6), 8.8, 7.0, boxstyle="round,pad=0.1,rounding_size=0.6",
                                fc="#f3f7f9", ec=C["cw"], lw=2.5))
    r = 1.9 + 0.5 * (pel_ - 5) / 4
    ax.add_patch(Rectangle((4.55, 3.9 + r - 0.2), 0.9, 9.6 - (3.9 + r - 0.2), fc="white", ec=C["lung"], lw=1.8))
    ax.add_patch(Rectangle((4.63, 3.9 + r - 0.3), 0.74, 9.8 - (3.9 + r - 0.3), fc="white", ec="none", zorder=3))
    ax.add_patch(Circle((5, 3.9), r, fc="white", ec=C["lung"], lw=2.3, zorder=2))
    ax.text(5, 4.25, "P$_{alv}$ = " + fs.fmt(palv), ha="center", fontsize=10.5, color=C["system"],
            fontweight="bold", zorder=4)
    ax.text(5, 3.3, "P$_{el}$ = " + fs.fmt(pel_), ha="center", fontsize=9.5, color=C["lung"], zorder=4)
    ax.text(1.0, 1.1, "P$_{pl}$ = " + fs.fmt(ppl), fontsize=10.5, color=C["cw"], fontweight="bold")
    ax.text(9.0, 1.1, "P$_{tp}$ = " + fs.fmt(palv - ppl), fontsize=9.5, color=C["ink"], ha="right")
    if flow:
        y0, y1 = (9.4, 6.6) if flow > 0 else (6.6, 9.4)
        ax.add_patch(FancyArrowPatch((6.3, y0), (6.3, y1), arrowstyle="-|>", mutation_scale=13,
                                     color=C["system"], lw=2, zorder=5))
        ax.text(6.7, 8.0, "in" if flow > 0 else "out", fontsize=9, color=C["system"])
    ax.text(0.4, -0.2, f"P$_{{pl}}$ + P$_{{el}}$ = {fs.fmt(ppl)} + {fs.fmt(pel_)} = {fs.fmt(palv)}",
            fontsize=8.8, color=C["text"], va="top")


def fig_alveolus_states():
    states = [("A. FRC, no flow", -5, 5, 0, 0),
              ("Thought experiment: first instant", -6, 5, -1, 1),
              ("B. Inspiration, 3,300 mL", -8, 7, -1, 1),
              ("C. End inspiration, no flow", -9, 9, 0, 0),
              ("D. Expiration, 3,300 mL", -6, 7, 1, -1),
              ("E. Back at FRC", -5, 5, 0, 0)]
    fig, axes = plt.subplots(2, 3, figsize=(10.2, 7.6))
    for ax, (ti, ppl, pe, pa, fl) in zip(axes.flat, states):
        alveolus(ax, ti, ppl, pe, pa, fl)
    fig.subplots_adjust(wspace=0.06, hspace=0.12)
    fig.text(0.5, 0.03, "Pressures in cm H$_2$O relative to the atmosphere (mouth = 0). The alveolus is drawn larger as P$_{el}$ rises with volume.",
             ha="center", fontsize=8.8, color=C["text"])
    fs.save(fig, PART, SLUG, "alveolus-states.svg")


# ------------------------------------------------------------ 3. Regional differences
def fig_regional():
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.9), gridspec_kw=dict(width_ratios=[0.75, 1.25]))
    ax = axes[0]
    ax.set_xlim(0, 8); ax.set_ylim(-1.6, 10.6); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("A. Upright lung", loc="left")
    lung = Polygon([[2.2, 1.0], [5.8, 1.0], [6.3, 3.0], [6.0, 6.5], [4.6, 8.9], [3.4, 8.9], [2.0, 6.5], [1.7, 3.0]],
                   closed=True, fc="#fbf3ea", ec=C["lung"], lw=2)
    ax.add_patch(lung)
    for y, rr in ((8.0, 0.42), (6.3, 0.37), (4.6, 0.32), (2.9, 0.27), (1.6, 0.23)):
        ax.add_patch(Circle((4.0, y), rr, fc="white", ec=C["lung"], lw=1.2))
    ax.text(4.0, 9.3, "Apex: P$_{pl}$ about " + MINUS + "10, alveoli larger", fontsize=9, color=C["cw"], ha="center")
    ax.text(4.0, 0.3, "Base: P$_{pl}$ about " + MINUS + "2.5, alveoli smaller", fontsize=9, color=C["cw"], ha="center", va="top")
    ax.add_patch(FancyArrowPatch((0.9, 8.6), (0.9, 1.4), arrowstyle="-|>", mutation_scale=12, color=C["text"], lw=1.3))
    ax.text(0.55, 5.0, "gravity", rotation=90, fontsize=9, color=C["text"], va="center", ha="center")

    ax = axes[1]
    tlc = m.analyze(m.settings_of())["tlc"]
    P = np.linspace(0, 30, 300)
    vp = np.array([100 * m.lung_volume(p) / tlc for p in P])
    ax.plot(P, vp, color=C["lung"], lw=2.4)
    fs.grid(ax)
    ax.set_xlim(0, 30); ax.set_ylim(0, 105)
    ax.set_xlabel("Transpulmonary pressure, P$_{tp}$ (cm H$_2$O)")
    ax.set_ylabel("Regional volume (% of TLC)")
    ax.set_title("B. The same lung curve, two starting points", loc="left")
    for p0, lab, col, dx in ((10, "apex", C["cw"], 0.6), (2.5, "base", C["system"], 0.6)):
        p1 = p0 + 4
        v0 = 100 * m.lung_volume(p0) / tlc
        v1 = 100 * m.lung_volume(p1) / tlc
        ax.plot([p0, p1], [v0, v1], "o", color=col, ms=6, zorder=5)
        ax.annotate("", xy=(p1, v1), xytext=(p0, v0), arrowprops=dict(arrowstyle="-|>", color=col, lw=1.6))
        ax.plot([p1, p1], [v0, v1], color=col, lw=1, ls=(0, (3, 2)))
        ax.plot([p0, p1], [v0, v0], color=col, lw=1, ls=(0, (3, 2)))
        ax.text(p1 + dx, (v0 + v1) / 2, f"{lab}: +{v1 - v0:.0f} points", fontsize=9.5, color=col, va="center")
        ax.text(p0, v0 - 6, f"{lab} at FRC", fontsize=8.5, color=col, ha="center")
    ax.text(29.5, 8, "Each region gets the same fall in P$_{pl}$ (4 cm H$_2$O here).\n"
            "The base starts on the steep part of the curve,\nso it gains more volume.",
            fontsize=8.8, ha="right", color=C["ink"])
    fig.subplots_adjust(wspace=0.22)
    fs.save(fig, PART, SLUG, "regional.svg")


# ------------------------------------------------------------ 4. Airway resistance and pleural pressure
def fig_resistance():
    t, V, flow, palv, ppl = breath(RAW)
    _, _, _, palv3, ppl3 = breath(3 * RAW)
    ppl_el = -pel(V)
    fig, axes = plt.subplots(2, 1, figsize=(7.4, 6.2), sharex=True,
                             gridspec_kw=dict(height_ratios=[1, 1.6], hspace=0.12))
    ax = axes[0]
    ax.axvspan(TI, TI + TE, color=C["shade"], zorder=0)
    ax.plot(t, (V - FRC) * 1000, color=C["ink"], lw=2.2)
    ax.set_ylabel("Volume above\nFRC (mL)", fontsize=9.5)
    ax.set_ylim(-40, 640); ax.set_yticks([0, 250, 500]); fs.grid(ax)
    ax.text(TI / 2, 580, "Inspiration", ha="center", fontsize=10, color=C["ink"])
    ax.text(TI + TE / 2, 580, "Expiration", ha="center", fontsize=10, color=C["ink"])
    ax.text(0.08, 400, "Same volume and flow\nin every case", ha="left", fontsize=8.8, color=C["text"])
    ax = axes[1]
    ax.axvspan(TI, TI + TE, color=C["shade"], zorder=0)
    ax.fill_between(t, ppl_el, ppl, color=C["highlight"], zorder=1)
    ax.plot(t, ppl_el, color=C["cw"], lw=1.6, ls=(0, (5, 3)))
    ax.plot(t, ppl, color=C["cw"], lw=2.4)
    ins = t <= TI
    ax.plot(t[ins], ppl3[ins], color=C["system"], lw=2.0, ls=(0, (1.5, 1.5)))
    ax.set_ylim(-13.5, -3)
    ticks = [-13, -11, -9, -7, -5, -3]
    ax.set_yticks(ticks); ax.set_yticklabels([fs.fmt(v) for v in ticks])
    ax.set_ylabel("Pleural pressure (cm H$_2$O)", fontsize=9.5)
    ax.set_xlabel("Time (s)")
    ax.set_xlim(0, TI + TE + 0.05)
    fs.grid(ax)
    tb = TI / 2
    ax.annotate("B: no airway resistance\n(elastic recoil only)", xy=(1.95, np.interp(1.95, t, ppl_el)), xytext=(1.62, -10.6),
                fontsize=8.6, color=C["cw"], va="top", arrowprops=dict(arrowstyle="-", color=C["cw"], lw=0.8))
    ax.annotate("B′: normal airway resistance", xy=(0.35, np.interp(0.35, t, ppl)), xytext=(0.3, -3.9),
                fontsize=8.6, color=C["cw"], arrowprops=dict(arrowstyle="-", color=C["cw"], lw=0.8))
    ax.annotate("Dotted: airway resistance tripled.\nP$_{pl}$ must fall further for the\nsame inspiratory flow", xy=(0.7, np.interp(0.7, t, ppl3)), xytext=(0.05, -11.6),
                fontsize=8.6, color=C["system"], va="top", arrowprops=dict(arrowstyle="-", color=C["system"], lw=0.8))
    ax.text(1.62, -3.6, "the gap above the dashed line\nis the pressure that drives\nair out through the airways", fontsize=8.3, color=C["text"])
    fs.save(fig, PART, SLUG, "resistance-ppl.svg")


if __name__ == "__main__":
    fig_traces()
    fig_alveolus_states()
    fig_regional()
    fig_resistance()
    t, V, flow, palv, ppl = breath()
    i = np.argmin(abs(t - TI / 2)); j = np.argmin(abs(t - (TI + TE / 2)))
    print("mid-insp V %.3f Pel %.2f Palv %.2f Ppl %.2f" % (V[i], pel(V[i]), palv[i], ppl[i]))
    print("mid-exp  V %.3f Pel %.2f Palv %.2f Ppl %.2f" % (V[j], pel(V[j]), palv[j], ppl[j]))
    print("end-insp Ppl %.2f, peak flow %.3f" % (ppl[np.argmin(abs(t - TI))], flow.max()))
