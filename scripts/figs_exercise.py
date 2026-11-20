"""Figures for the Physiology of Exercise chapter (pulmonary block, P11).

Run:  cd site/scripts && MPLCONFIGDIR=$TMPDIR PNG_PREVIEW=<folder> python3 figs_exercise.py
Writes SVGs to ../pulmonary/figures/exercise/.
"""
import numpy as np
from matplotlib.patches import FancyBboxPatch

import figstyle as fs

plt, C = fs.plt, fs.C
PART, SLUG = "pulmonary", "exercise"
K = 0.863  # mm Hg·L/mL: PaCO2 = K × VCO2 (mL/min) / VA (L/min), course Ventilation notes


def box(ax, x, y, w, h, text, ec, fc="white", fs_=9.5, bold=False):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc=fc, ec=ec, lw=1.8, zorder=2))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs_, color=C["ink"],
            fontweight="bold" if bold else "normal", zorder=3)


def arrow(ax, x0, y0, x1, y1, color, lw=1.8):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, shrinkA=1, shrinkB=1), zorder=1)


# ---------------------------------------------------------------- 1. Drive train
def fig_drive_train():
    fig, ax = plt.subplots(figsize=(10.6, 4.4))
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 6)
    ax.axis("off")
    stages = [(1.4, "Lungs", "deeper breaths (V$_T$),\nthen faster (RR)", C["lung"]),
              (4.45, "Pulmonary\ncirculation", "recruitment of\nparallel vessels:\nPVR falls", C["cw"]),
              (7.5, "Heart", "heart rate and\nstroke volume rise", C["system"]),
              (10.55, "Systemic\ncirculation", "arteriolar dilation in\nmuscle, venoconstriction,\nmuscle pump", C["venous"]),
              (13.6, "Muscle", "more O$_2$ extracted;\nfuel and type of\nmetabolism change R", C["muscle"])]
    for x, name, what, col in stages:
        box(ax, x, 3.0, 2.4, 1.15, name, col, fs_=10.5, bold=True)
        ax.text(x, 1.75, what, ha="center", va="top", fontsize=8.8, color=C["text"])
    for x0, x1 in ((2.6, 3.25), (5.65, 6.3), (8.7, 9.35), (11.75, 12.4)):
        arrow(ax, x0, 3.3, x1, 3.3, C["muscle"])
        arrow(ax, x1, 2.7, x0, 2.7, C["cw"])
    ax.annotate("", xy=(14.6, 4.6), xytext=(0.4, 4.6),
                arrowprops=dict(arrowstyle="-|>", color=C["muscle"], lw=2.4))
    ax.text(7.5, 4.85, "O$_2$ in: ambient air to mitochondria ($\\dot{V}$O$_2$, O$_2$ delivery = CO × CaO$_2$)",
            ha="center", fontsize=9.5, color=C["muscle"])
    ax.annotate("", xy=(0.4, 0.25), xytext=(14.6, 0.25),
                arrowprops=dict(arrowstyle="-|>", color=C["cw"], lw=2.4))
    ax.text(7.5, -0.2, "CO$_2$ out: mitochondria to ambient air ($\\dot{V}$CO$_2$ = $\\dot{V}$O$_2$ × R)",
            ha="center", fontsize=9.5, color=C["cw"])
    fs.save(fig, PART, SLUG, "drive-train.svg")


# ---------------------------------------------------------------- 2. CO2 output and ventilation
def fig_co2():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.6, 4.6))
    vco2 = np.linspace(0, 3000, 300)
    for pc, col, lab in ((30, C["muscle"], "PaCO$_2$ 30"), (40, C["system"], "PaCO$_2$ 40"), (50, C["venous"], "PaCO$_2$ 50")):
        va = K * vco2 / pc
        a1.plot(vco2 / 1000, va, color=col, lw=2.3)
        if pc == 30:
            a1.text(2.15, 66, lab, color=col, fontsize=9.5, ha="right")
        else:
            a1.text(3.04, K * 3000 / pc, lab, color=col, fontsize=9.5, ha="left", va="center")
    for x, lab, dx, dy in ((0.2, "rest: $\\dot{V}$CO$_2$ about\n200 mL/min", 0.8, -1), (2.0, "heavy exercise:\nabout 2000 mL/min", 0.1, -16)):
        y = K * x * 1000 / 40
        a1.plot([x], [y], "o", color=C["system"], ms=6, zorder=5)
        a1.annotate(lab, xy=(x, y), xytext=(x + dx, y + dy), fontsize=9, color=C["ink"],
                    arrowprops=dict(arrowstyle="-", color=C["ink"], lw=0.8))
    a1.set_xlim(0, 3.55)
    a1.set_xticks([0, 0.5, 1, 1.5, 2, 2.5, 3])
    a1.set_ylim(0, 80)
    a1.set_xlabel("CO$_2$ output, $\\dot{V}$CO$_2$ (L/min)")
    a1.set_ylabel("Alveolar ventilation, $\\dot{V}_A$ (L/min)")
    a1.set_title("A. $\\dot{V}_A$ needed to hold PaCO$_2$")
    fs.grid(a1)
    vo2 = np.linspace(0, 3.2, 100)
    for r, col in ((1.0, C["gold"]), (0.85, C["system"]), (0.7, C["venous"])):
        a2.plot(vo2, r * vo2, color=col, lw=2.3)
        a2.text(3.24, r * 3.2, f"R = {r:g}", color=col, fontsize=9.5, ha="left", va="center")
    a2.text(0.2, 2.75, "R = 1.0: all carbohydrate\nR = 0.7: all fat\nR = 0.8 to 0.85: a mixed diet",
            fontsize=9, color=C["text"], va="top")
    a2.set_xlim(0, 3.75)
    a2.set_xticks([0, 0.5, 1, 1.5, 2, 2.5, 3])
    a2.set_ylim(0, 3.4)
    a2.set_xlabel("O$_2$ consumption, $\\dot{V}$O$_2$ (L/min)")
    a2.set_ylabel("$\\dot{V}$CO$_2$ (L/min)")
    a2.set_title("B. $\\dot{V}$CO$_2$ = $\\dot{V}$O$_2$ × R")
    fs.grid(a2)
    fig.subplots_adjust(wspace=0.25)
    fs.save(fig, PART, SLUG, "co2-and-ventilation.svg")


# ---------------------------------------------------------------- 3. Deeper, then faster
def pchip(xk, yk, x):
    """Monotone cubic (Fritsch-Carlson) interpolation without scipy."""
    xk, yk = np.asarray(xk, float), np.asarray(yk, float)
    h = np.diff(xk)
    d = np.diff(yk) / h
    m = np.zeros_like(yk)
    m[0], m[-1] = d[0], d[-1]
    for i in range(1, len(xk) - 1):
        if d[i - 1] * d[i] > 0:
            w1, w2 = 2 * h[i] + h[i - 1], h[i] + 2 * h[i - 1]
            m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])
    out = np.empty_like(x, dtype=float)
    for j, xx in enumerate(x):
        i = min(max(np.searchsorted(xk, xx) - 1, 0), len(xk) - 2)
        t = (xx - xk[i]) / h[i]
        h00, h10, h01, h11 = 2*t**3 - 3*t**2 + 1, t**3 - 2*t**2 + t, -2*t**3 + 3*t**2, t**3 - t**2
        out[j] = h00 * yk[i] + h10 * h[i] * m[i] + h01 * yk[i + 1] + h11 * h[i] * m[i + 1]
    return out


def fig_pattern():
    ve = np.linspace(10, 96, 300)
    rr = pchip([10, 31, 45, 60, 78, 96], [12.5, 18, 20, 25, 32, 40], ve)
    vt = ve / rr
    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    ax.plot(ve, vt, color=C["lung"], lw=2.6)
    ax.set_xlabel("Minute ventilation, $\\dot{V}_E$ (L/min)")
    ax.set_ylabel("Tidal volume, V$_T$ (L)", color=C["lung"])
    ax.set_ylim(0, 3)
    ax.set_xlim(0, 105)
    fs.grid(ax)
    b = ax.twinx()
    b.plot(ve, rr, color=C["cw"], lw=2.6)
    b.set_ylabel("Respiratory rate (breaths/min)", color=C["cw"])
    b.set_ylim(0, 45)
    b.spines["right"].set_visible(True)
    ax.text(60, 2.55, "V$_T$ levels off near 2.4 L", color=C["lung"], fontsize=9.5, ha="center")
    b.text(80, 24, "then the rate\nclimbs to about 40", color=C["cw"], fontsize=9.5, ha="left")
    ax.text(22, 0.6, "V$_T$ doubles while the\nrate barely changes", color=C["ink"], fontsize=9.5)
    for v, lab in ((10, "rest"), (31, "AT"), (96, "max")):
        ax.axvline(v, color=C["axis"], lw=0.8, ls=(0, (3, 3)))
        ax.text(v, 2.88, lab, ha="center", fontsize=8.8, color=C["text"], bbox=dict(fc="white", ec="none", pad=0.5))
    fs.save(fig, PART, SLUG, "breathing-pattern.svg")


# ---------------------------------------------------------------- 4. Low venous O2 widens the A-a gradient
def sat(p):
    p = np.maximum(p, 0.1)
    return 1 / (23400 / (p**3 + 150 * p) + 1)  # Severinghaus; fits the course anchors 27/50, 40/75, 60/90, 100/97.5


def content(p, hb=15):
    return 1.39 * hb * sat(p) + 0.003 * p


def po2_from_content(c, hb=15):
    lo, hi = 1.0, 700.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if content(mid, hb) < c:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def fig_shunt():
    pao2 = 100.0
    pv = np.linspace(45, 18, 60)
    fig, ax = plt.subplots(figsize=(7.0, 4.8))
    for qs, col, lab in ((0.03, C["system"], "Healthy lung\n(3% shunt)"),
                         (0.15, C["venous"], "Diseased lung\n(15% shunt)")):
        aa = []
        for p in pv:
            ca = (1 - qs) * content(pao2) + qs * content(p)
            aa.append(pao2 - po2_from_content(ca))
        aa = np.array(aa)
        ax.plot(pv, aa, color=col, lw=2.5)
        ax.text(pv[-1] - 0.5, aa[-1], lab, color=col, fontsize=9.5, va="center", ha="left")
        if qs < 0.1:
            r0 = aa[np.argmin(np.abs(pv - 40))]
            ax.plot([40], [r0], "o", color=col, ms=6, zorder=5)
            ax.text(40, r0 + 2.5, "rest", ha="center", fontsize=9, color=col)
    ax.axhspan(0, 10, color=C["shade"], zorder=0)
    ax.text(21, 3.5, "normal resting A–a gradient (10 or less)", fontsize=8.8, color=C["text"], ha="center")
    ax.set_xlim(46, 10)
    ax.set_ylim(0, 70)
    ax.set_xlabel("Mixed venous PO$_2$ (mm Hg); it falls as exercise extracts more O$_2$")
    ax.set_ylabel("A–a gradient (mm Hg)")
    fs.grid(ax)
    ax.text(45.5, 66, "Same lungs, same alveolar PO$_2$ (100 mm Hg);\nonly the venous blood entering the shunt changes",
            fontsize=9, color=C["ink"], va="top")
    fs.save(fig, PART, SLUG, "shunt-and-venous-o2.svg")


# ---------------------------------------------------------------- 5. Idealized CPET
def fig_cpet():
    t = np.linspace(-2, 10, 600)          # minutes; ramp starts at 0, stops at 10
    work = np.clip(t, 0, None) * 25       # W: 25 W/min ramp to 250 W
    vo2 = 350 + 10.0 * work               # mL/min, about 10 mL/min per W
    t_at, t_rcp = 5.0, 8.3
    r_base = np.where(t < 0, 0.85, 0.85 + 0.08 * np.clip(t, 0, t_at) / t_at)
    vco2 = r_base * vo2
    extra = np.where(t > t_at, 150 * np.clip(t - t_at, 0, None) ** 1.25, 0.0)   # CO2 from bicarbonate buffering of lactic acid
    vco2 = vco2 + extra
    eq_co2 = np.where(t < 0, 32.0, np.where(t < t_at, 32 - 5 * np.clip(t, 0, t_at) / t_at, 27.0))   # VE/VCO2
    eq_co2 = np.where(t > t_rcp, 27 + 2.6 * np.clip(t - t_rcp, 0, None) ** 1.3, eq_co2)
    ve = eq_co2 * vco2 / 1000
    eq_o2 = ve * 1000 / vo2
    R = vco2 / vo2
    fig, (a1, a2, a3) = plt.subplots(3, 1, figsize=(8.4, 9.0), sharex=True,
                                     gridspec_kw=dict(height_ratios=[1.6, 1, 0.8]))
    a1.plot(t, vo2, color=C["muscle"], lw=2.4)
    a1.plot(t, vco2, color=C["cw"], lw=2.4)
    a1.set_ylabel("$\\dot{V}$O$_2$, $\\dot{V}$CO$_2$ (mL/min)")
    a1.set_ylim(0, 4200)
    b = a1.twinx()
    b.plot(t, ve, color=C["green"], lw=2.2, ls=(0, (6, 2)))
    b.set_ylabel("$\\dot{V}_E$ (L/min)", color=C["green"])
    b.set_ylim(0, 140)
    b.spines["right"].set_visible(True)
    a1.text(9.9, 1750, "$\\dot{V}$O$_2$: straight\nline to $\\dot{V}$O$_2$max", color=C["muscle"], fontsize=9, ha="right")
    a1.text(8.0, 3350, "$\\dot{V}$CO$_2$", color=C["cw"], fontsize=9.5, ha="right")
    b.text(2.4, 6, "$\\dot{V}_E$ (dashed)", color=C["green"], fontsize=9.5)
    a2.plot(t, eq_o2, color=C["muscle"], lw=2.4)
    a2.plot(t, eq_co2, color=C["cw"], lw=2.4)
    a2.set_ylabel("Ventilatory\nequivalents")
    a2.set_ylim(15, 50)
    a2.text(7.4, 44, "$\\dot{V}_E$/$\\dot{V}$O$_2$", color=C["muscle"], fontsize=9.5, ha="right")
    a2.text(6.6, 25.5, "$\\dot{V}_E$/$\\dot{V}$CO$_2$ flat:\nisocapnic buffering", color=C["cw"], fontsize=9, ha="center", va="top")
    a3.plot(t, R, color=C["system"], lw=2.4)
    a3.axhline(1.0, color=C["axis"], lw=0.9, ls=(0, (3, 3)))
    a3.set_ylabel("R")
    a3.set_ylim(0.7, 1.35)
    a3.text(-1.9, 1.02, "R = 1", fontsize=8.5, color=C["text"])
    a3.set_xlabel("Time (min); work rises steadily from 0 to 250 W after minute 0")
    for ax in (a1, a2, a3):
        fs.grid(ax)
        for x in (0, t_at, t_rcp, 10):
            ax.axvline(x, color=C["axis"], lw=0.9, ls=(0, (4, 3)))
    for x, lab in ((0, "work\nstarts"), (t_at, "anaerobic\nthreshold"), (t_rcp, "respiratory\ncompensation"), (10, "$\\dot{V}$O$_2$max")):
        a1.text(x, 4230, lab, ha="center", va="bottom", fontsize=8.6, color=C["ink"])
    a1.set_xlim(-2, 10.3)
    fig.subplots_adjust(hspace=0.1)
    fs.save(fig, PART, SLUG, "cpet.svg")


if __name__ == "__main__":
    fig_drive_train()
    fig_co2()
    fig_pattern()
    fig_shunt()
    fig_cpet()
