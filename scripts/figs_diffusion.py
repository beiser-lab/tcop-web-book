"""Figures for the Diffusion chapter (P6).

Run:  cd site/scripts && MPLCONFIGDIR=$TMPDIR PNG_PREVIEW=<folder> python3 figs_diffusion.py

The capillary O2 curves come from a one-line model of O2 loading along the capillary:
    dC/dt = k (PAO2 - P),   C(P) = 1.39 Hb S(P) + 0.003 P
where S(P) is the course's HbO2 curve (Hill fit, P50 27 mm Hg, n 2.79, which passes through
the anchor points 27/50%, 40/75%, 60/90%, 100/97.5%). k stands for DL per unit blood volume and
is set so a normal lung at sea level reaches alveolar PO2 within the first third of the
transit (about 0.15 s), as the course teaches. The model holds DL constant; real blood binds O2
faster at low saturation, so the altitude curves are on the slow side (slide 22: about 0.45 s).
Lower k is a lower DL (thick barrier). The model reproduces the shape of West's curves, including
the slow start on the steep part of the dissociation curve.
"""
import numpy as np
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch

import figstyle as fs

plt = fs.plt
C = fs.C
M = fs.MINUS
PART, SLUG = "pulmonary", "diffusion"
P50, NH, HB = 27.0, 2.79, 15.0


def sat(p):
    p = np.maximum(p, 0)
    x = (p / P50) ** NH
    return x / (1 + x)


def content(p):
    return 1.39 * HB * sat(p) + 0.003 * p


PGRID = np.linspace(0, 160, 16001)
CGRID = content(PGRID)


def p_of_c(c):
    return np.interp(c, CGRID, PGRID)


def capillary(pa, pv, k, t_end=0.75, n=3000):
    t = np.linspace(0, t_end, n)
    dt = t[1] - t[0]
    c = content(pv)
    out = np.empty(n)
    for i in range(n):
        p = p_of_c(c)
        out[i] = p
        c += k * (pa - p) * dt
    return t, out


K_NORMAL = 1.2  # mL O2/dL per s per mm Hg


# ---------------------------------------------------------------- 1. Thin and thick barrier
def barrier_panel(ax, title, thick, transfer):
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7.2)
    ax.axis("off")
    ax.set_title(title, loc="left")
    x0 = 3.6
    w = 1.2 if not thick else 2.4
    ax.add_patch(Rectangle((0.3, 1.2), x0 - 0.3, 4.6, fc=C["cool"], ec="none"))
    ax.add_patch(Rectangle((x0, 1.2), w, 4.6, fc=C["highlight"], ec=C["lung"], lw=1.5))
    ax.add_patch(Rectangle((x0 + w, 1.2), 9.7 - x0 - w, 4.6, fc="#f6e6e6", ec="none"))
    ax.text((0.3 + x0) / 2, 6.1, "Alveolar gas", ha="center", fontsize=9.5, color=C["cw"])
    ax.text(x0 + w / 2, 6.1, "Barrier", ha="center", fontsize=9.5, color=C["lung"])
    ax.text((x0 + w + 9.7) / 2, 6.1, "Capillary blood", ha="center", fontsize=9.5, color=C["system"])
    yh, yl = 5.0, 2.0
    ax.plot([0.3, x0], [yh, yh], color=C["ink"], lw=2.2)
    ax.plot([x0, x0 + w], [yh, yl], color=C["ink"], lw=2.2)
    ax.plot([x0 + w, 9.7], [yl, yl], color=C["ink"], lw=2.2)
    ax.text(0.5, yh + 0.2, "PO$_2$ 100", fontsize=9, color=C["ink"])
    ax.text(9.5, yl + 0.2, "PO$_2$ 40", fontsize=9, color=C["ink"], ha="right")
    ax.text(x0 + w / 2, 0.75, "thickness " + ("2T" if thick else "T"), ha="center", fontsize=9, color=C["lung"])
    lw = 2.5 if thick else 5
    ax.annotate("", xy=(9.0, 0.35), xytext=(1.0, 0.35),
                arrowprops=dict(arrowstyle="-|>", color=C["system"], lw=lw, mutation_scale=18))
    ax.text(5, -0.35, transfer, ha="center", fontsize=9.5, color=C["system"])


def fig_barrier():
    fig, axes = plt.subplots(1, 2, figsize=(9.4, 3.8))
    barrier_panel(axes[0], "A. Thin barrier", False, "O$_2$ transfer × 2")
    barrier_panel(axes[1], "B. Thick barrier", True, "O$_2$ transfer × 1")
    fig.text(0.5, -0.06, "Same gradient (100 to 40 mm Hg). Half the thickness, twice the slope, twice the transfer.",
             ha="center", fontsize=9, color=C["text"])
    fig.subplots_adjust(wspace=0.08)
    fs.save(fig, PART, SLUG, "barrier-thickness.svg")


# ---------------------------------------------------------------- 2. Solubility
def fig_solubility():
    p = np.linspace(0, 100, 50)
    fig, ax = plt.subplots(figsize=(7.0, 4.6))
    ax.plot(p, 0.067 * p, color=C["system"], lw=2.4)
    ax.plot(p, 0.003 * p, color=C["cw"], lw=2.4)
    ax.plot(p, 0.0015 * p, color=C["gray"], lw=2.0, ls=(0, (4, 2)))
    ax.annotate("Ether: far more soluble;\nat this scale nearly vertical", xy=(5.5, 6.6), xytext=(10, 6.2),
                fontsize=9, color=C["ink"], va="center",
                arrowprops=dict(arrowstyle="-|>", color=C["ink"], lw=1))
    ax.plot([0, 5], [0, 7], color=C["ink"], lw=1.6)
    ax.text(80, 4.4, "CO$_2$  0.067", color=C["system"], fontsize=10, fontweight="bold")
    ax.text(78, 0.72, "O$_2$  0.003", color=C["cw"], fontsize=10, fontweight="bold")
    ax.text(99, -0.5, "N$_2$: less soluble than O$_2$", color=C["gray"], fontsize=9, ha="right", va="bottom")
    ax.plot([40], [0.067 * 40], "o", color=C["system"], ms=6)
    ax.text(41.5, 0.067 * 40 - 0.35, "2.7 mL/dL at 40", fontsize=8.8, color=C["system"])
    ax.plot([100], [0.3], "o", color=C["cw"], ms=6, clip_on=False)
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.6, 7.2)
    ax.set_xlabel("Partial pressure of the gas (mm Hg)")
    ax.set_ylabel("Dissolved gas (mL/dL)")
    fs.grid(ax)
    ax.text(12, 4.3, "slope = solubility\n(mL/dL per mm Hg)", fontsize=8.8, color=C["text"])
    fs.save(fig, PART, SLUG, "solubility.svg")


# ---------------------------------------------------------------- 3. Layers from alveolus to Hb
def fig_layers():
    layers = [("Alveolar\nair", C["cool"]), ("Surface\nliquid", "#e3eef3"), ("Type I\nepithelium", C["highlight"]),
              ("Inter-\nstitium", "#f2e2cc"), ("Endo-\nthelium", C["highlight"]), ("Plasma", "#f6e6e6"),
              ("Red cell", "#efd0d0"), ("Hb\nbinding", "#e4b5b5")]
    widths = [1.4, 0.9, 1.1, 1.1, 1.1, 1.0, 1.3, 1.3]
    fig, ax = plt.subplots(figsize=(10.0, 3.9))
    ax.set_xlim(0, sum(widths) + 0.2)
    ax.set_ylim(-1.9, 4.2)
    ax.axis("off")
    x = 0.1
    centers = []
    for (lab, col), w in zip(layers, widths):
        ax.add_patch(Rectangle((x, 0.6), w, 2.4, fc=col, ec="white", lw=2))
        ax.text(x + w / 2, 1.8, lab, ha="center", va="center", fontsize=9, color=C["ink"])
        centers.append(x + w / 2)
        x += w
    # falling PO2 markers
    for i, cx in enumerate(centers[:-1]):
        ax.text(cx, 3.15 - 0.07 * i, "O$_2$", ha="center", fontsize=9, color=C["system"])
    ax.annotate("", xy=(centers[-1] - 0.3, 3.85), xytext=(centers[0] - 0.3, 3.85),
                arrowprops=dict(arrowstyle="-|>", color=C["system"], lw=1.4))
    # brackets
    x_ep0 = 0.1 + widths[0]
    x_rc1 = 0.1 + sum(widths[:7])
    x_end = 0.1 + sum(widths)

    def bracket(xa, xb, y, text, col):
        ax.plot([xa, xa, xb, xb], [y + 0.18, y, y, y + 0.18], color=col, lw=1.6)
        ax.text((xa + xb) / 2, y - 0.35, text, ha="center", va="top", fontsize=9.5, color=col)

    bracket(x_ep0, x_rc1, 0.35, "D$_M$, the membrane part: resistances in series add\n"
            "1/D$_M$ = sum of 1/D for each layer", C["lung"])
    bracket(x_rc1 + 0.02, x_end, 0.35, "θ·V$_c$, the\nhemoglobin part", C["system"])
    ax.text(x_end, -1.75, "1/D$_L$ = 1/D$_M$ + 1/(θ·V$_c$)", ha="right", fontsize=10.5, color=C["ink"],
            fontweight="bold")
    fs.save(fig, PART, SLUG, "layers.svg")


# ---------------------------------------------------------------- 4. Perfusion versus diffusion limitation
def fig_perf_diff():
    t = np.linspace(0, 0.75, 400)
    n2o = 1 - np.exp(-t / 0.03)
    co = 0.06 * (1 - np.exp(-t / 1.5)) / (1 - np.exp(-0.75 / 1.5))
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.9), sharey=True)
    for ax, y, col, title, note in ((axes[0], n2o, C["cw"], "A. N$_2$O: perfusion limited",
                                     "Blood reaches alveolar PN$_2$O early.\nAfter that nothing crosses;\nmore uptake needs more blood flow."),
                                    (axes[1], co, C["system"], "B. CO: diffusion limited",
                                     "Hb takes up CO as fast as it arrives,\nso capillary PCO stays near zero.\nThe gradient never closes.")):
        ax.axhline(1, color=C["ink"], lw=1.2, ls=(0, (4, 3)))
        ax.text(0.74, 1.03, "alveolar partial pressure", ha="right", fontsize=8.8, color=C["ink"])
        ax.plot(t, y, color=col, lw=2.6)
        ax.set_title(title)
        ax.set_xlim(0, 0.75)
        ax.set_ylim(0, 1.15)
        ax.set_xticks([0, 0.25, 0.5, 0.75])
        ax.set_xticklabels(["0", "0.25", "0.50", "0.75"])
        ax.set_xlabel("Time in capillary (s)")
        ax.text(0.74, 0.42, note, ha="right", fontsize=8.8, color=C["text"])
        fs.grid(ax)
    axes[0].set_ylabel("Capillary partial pressure\n(fraction of alveolar)")
    fig.subplots_adjust(wspace=0.08)
    fs.save(fig, PART, SLUG, "perfusion-vs-diffusion.svg")


# ---------------------------------------------------------------- 5. O2 and CO2 at rest
def fig_o2_co2():
    t, po2 = capillary(100, 40, K_NORMAL)
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.9))
    ax = axes[0]
    ax.axhline(100, color=C["ink"], lw=1.2, ls=(0, (4, 3)))
    ax.plot(t, po2, color=C["system"], lw=2.6)
    ax.axvspan(0.25, 0.75, color=C["shade"], zorder=0)
    ax.text(0.5, 60, "diffusion reserve:\nthe last two thirds", ha="center", fontsize=9, color=C["text"])
    ax.text(0.01, 102.5, "alveolar PO$_2$ 100", fontsize=8.8, color=C["ink"])
    ax.text(0.02, 34, "mixed venous 40", fontsize=8.8, color=C["ink"])
    ax.set_ylim(30, 110)
    ax.set_ylabel("PO$_2$ (mm Hg)")
    ax.set_title("A. O$_2$ uptake")
    ax = axes[1]
    tt = np.linspace(0, 0.75, 400)
    pco2 = 40 + 6 * np.exp(-tt / 0.06)
    ax.axhline(40, color=C["ink"], lw=1.2, ls=(0, (4, 3)))
    ax.plot(tt, pco2, color=C["cw"], lw=2.6)
    ax.text(0.74, 40.3, "alveolar PCO$_2$ 40", ha="right", fontsize=8.8, color=C["ink"])
    ax.text(0.03, 46.2, "mixed venous 46", fontsize=8.8, color=C["ink"])
    ax.set_ylim(38, 47)
    ax.set_ylabel("PCO$_2$ (mm Hg)")
    ax.set_title("B. CO$_2$ removal")
    for ax in axes:
        ax.set_xlim(0, 0.75)
        ax.set_xticks([0, 0.25, 0.5, 0.75])
        ax.set_xlabel("Time in capillary (s)")
        fs.grid(ax)
    fig.subplots_adjust(wspace=0.28)
    fs.save(fig, PART, SLUG, "o2-co2-equilibration.svg")


# ---------------------------------------------------------------- 6. Diffusion reserve: sea level and altitude
LABEL_AT = {(100, "normal"): (0.19, 91), (100, "D$_L$ ¼ normal"): (0.40, 90),
            (100, "D$_L$ ⅛ normal"): (0.60, 63), (50, "normal"): (0.62, 43),
            (50, "D$_L$ ¼ normal"): (0.62, 37.5), (50, "D$_L$ ⅛ normal"): (0.62, 22)}


def fig_reserve():
    fig, axes = plt.subplots(1, 2, figsize=(10.0, 4.4), sharey=True)
    cases = [(axes[0], 100, 40, "A. Sea level (alveolar PO$_2$ 100)"),
             (axes[1], 50, 25, "B. Altitude (alveolar PO$_2$ 50)")]
    for ax, pa, pv, title in cases:
        ax.axhline(pa, color=C["ink"], lw=1.2, ls=(0, (4, 3)))
        ax.text(0.745, pa + 2, "alveolar", ha="right", fontsize=8.8, color=C["ink"])
        for k, col, lab in ((K_NORMAL, C["system"], "normal"), (K_NORMAL / 4, C["lung"], "D$_L$ ¼ normal"),
                            (K_NORMAL / 8, C["cw"], "D$_L$ ⅛ normal")):
            t, p = capillary(pa, pv, k)
            ax.plot(t, p, color=col, lw=2.4)
            ax.text(*LABEL_AT[(pa, lab)], lab, color=col, fontsize=9, ha="center")
            if lab == "normal":
                hit = np.nonzero(p > pa - 1.0)[0]
                print(title, "normal within 1 mm Hg of PA at", f"{t[hit[0]]:.2f} s" if hit.size else "never")
            else:
                print(title, lab, "end-capillary", round(p[-1], 1))
        ax.axvline(0.25, color=C["gray"], lw=1, ls=(0, (2, 3)))
        ax.text(0.255, 4, "heavy exercise:\ntransit about 0.25 s", fontsize=8.5, color=C["gray"])
        ax.set_title(title)
        ax.set_xlim(0, 0.75)
        ax.set_ylim(0, 110)
        ax.set_xticks([0, 0.25, 0.5, 0.75])
        ax.set_xticklabels(["0", "0.25", "0.50", "0.75"])
        ax.set_xlabel("Time in capillary (s)")
        fs.grid(ax)
    axes[0].set_ylabel("Capillary PO$_2$ (mm Hg)")
    fig.subplots_adjust(wspace=0.12)
    fs.save(fig, PART, SLUG, "diffusion-reserve.svg")


if __name__ == "__main__":
    fig_barrier()
    fig_solubility()
    fig_layers()
    fig_perf_diff()
    fig_o2_co2()
    fig_reserve()
