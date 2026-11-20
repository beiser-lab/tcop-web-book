"""Figures for the Microcirculation and Local Control chapter.

Run:  cd site/scripts && MPLCONFIGDIR=$TMPDIR PNG_PREVIEW=<folder> python3 figs_microcirculation.py
Writes SVGs to ../cardiovascular/figures/microcirculation/.
Starling numbers are the lecture's classical example (supplementary slide 31). The arteriolar
tone figure uses lumped resistances in series (Ohm's law). Autoregulation is drawn across the
course range of 20 to 150 mm Hg (errata entry 12). The two isolated-arteriole
panels are drawn approximately from the figures the lecture reproduces.
"""
import numpy as np
import figstyle as fs

plt = fs.plt
C = fs.C
M = fs.MINUS
PART, SLUG = "cardiovascular", "microcirculation"


def save(fig, name):
    fs.save(fig, PART, SLUG, name)


# ---------------------------------------------------------------- 1. Starling forces along a capillary
def fig_starling():
    x = np.linspace(0, 1, 200)
    Pc = 35 - 20 * x
    Pi = -2 + 0 * x
    pic = 25 + 0 * x
    pii = 0 + 3 * x
    out = Pc - Pi          # hydrostatic difference, outward
    inn = pic - pii        # oncotic difference, inward (sigma = 1)
    net = out - inn
    xc = x[np.argmin(np.abs(net))]
    fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.2))
    ax = axes[0]
    ax.plot(x, out, color=C["arterial"], lw=2.4)
    ax.plot(x, inn, color=C["venous"], lw=2.4)
    ax.fill_between(x, inn, out, where=out >= inn, color="#f6e3e3", lw=0)
    ax.fill_between(x, inn, out, where=out < inn, color="#e3edf3", lw=0)
    ax.text(0.03, 38.5, f"outward: P$_c$ {M} P$_i$", color=C["arterial"], fontsize=10)
    ax.text(0.03, 25.8, f"inward: π$_c$ {M} π$_i$", color=C["venous"], fontsize=10)
    ax.text(0.02, 11.2, f"P$_c$ falls from 35 to 15; P$_i$ = {M}2; π$_c$ = 25; π$_i$ rises from 0 to 3",
            color=C["text"], fontsize=8.5, ha="left")
    ax.set_xlim(0, 1)
    ax.set_ylim(10, 42)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["arteriolar end", "venular end"])
    ax.set_ylabel("Pressure difference (mm Hg)")
    ax.set_title("A. The two pressure differences", fontsize=11)
    fs.grid(ax)
    ax = axes[1]
    ax.axhline(0, color=C["ink"], lw=1)
    ax.plot(x, net, color=C["ink"], lw=2.4)
    ax.fill_between(x, 0, net, where=net >= 0, color="#f6e3e3", lw=0)
    ax.fill_between(x, 0, net, where=net < 0, color="#e3edf3", lw=0)
    ax.text(0.04, 13.2, "+12", fontsize=10, color=C["arterial"], fontweight="bold")
    ax.text(0.96, -7.6, f"{M}5", fontsize=10, color=C["venous"], fontweight="bold", ha="right")
    ax.text(0.05, 0.8, "net filtration\n(out of the capillary)", fontsize=9.5, color=C["arterial"])
    ax.text(0.95, 3.0, "net absorption\n(back in)", fontsize=9.5, color=C["venous"], ha="right")
    ax.set_xlim(0, 1)
    ax.set_ylim(-9, 15)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["arteriolar end", "venular end"])
    ax.set_ylabel("Net driving pressure (mm Hg)")
    ax.set_title(f"B. Net: (P$_c$ {M} P$_i$) {M} (π$_c$ {M} π$_i$)", fontsize=11)
    fs.grid(ax)
    print("crossover at", round(xc, 2))
    fig.subplots_adjust(wspace=0.3)
    save(fig, "starling-classical.svg")


# ---------------------------------------------------------------- 2. Lymph flow and interstitial pressure
def fig_lymph():
    P = np.linspace(-7, 6, 300)
    flow = 1 + 21.5 / (1 + np.exp(-(P - 0.0) / 0.95))
    fig, ax = plt.subplots(figsize=(6.4, 4.3))
    ax.axvspan(1.8, 6, color=C["shade"], lw=0)
    ax.plot(P, flow, color=C["green"], lw=2.6)
    ax.set_xlim(-7, 6)
    ax.set_ylim(0, 26)
    ax.set_xlabel("Interstitial fluid pressure, P$_i$ (mm Hg)")
    ax.set_ylabel("Lymph flow (relative)")
    ax.set_xticks(range(-6, 7, 2))
    ax.set_xticklabels([fs.fmt(v) for v in range(-6, 7, 2)])
    fs.grid(ax)
    ax.text(3.9, 9.5, "lymph flow\nat its maximum:\nmore fluid now\ncollects as edema", fontsize=9, color=C["ink"],
            ha="center")
    ax.annotate("steep part, near the normal P$_i$:\nmore interstitial fluid raises P$_i$,\nand lymph flow rises sharply", xy=(-0.5, 9.3),
                xytext=(-6.7, 15.5), fontsize=9, color=C["green"],
                arrowprops=dict(arrowstyle="-", color=C["green"], lw=0.8))
    save(fig, "lymph-flow.svg")


# ---------------------------------------------------------------- 3. Arteriolar tone sets capillary pressure
def profile(pa, pv, rpre):
    segs = [("arteries", 0.15), ("arterioles", rpre), ("capillaries", 0.2), ("venules", 0.1), ("veins", 0.05)]
    rt = sum(r for _, r in segs)
    q = (pa - pv) / rt
    P = [pa]
    for _, r in segs:
        P.append(P[-1] - q * r)
    return np.array(P), q


def fig_arteriolar_tone():
    xs = np.arange(6)
    cases = [("normal", 95, 5, 0.5, C["ink"], "-", 2.4),
             ("arteriolar constriction", 95, 5, 1.0, C["arterial"], "-", 2.2),
             ("arteriolar dilation", 95, 5, 0.25, C["venous"], "-", 2.2),
             ("venous pressure raised to 20", 95, 20, 0.5, C["gray"], (0, (4, 2)), 2.0)]
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    names = ["arteries", "arterioles", "capillaries", "venules", "veins"]
    bands = ["#f8eeee", "#fbf3ea", "#f1edf4", "#eef2f4", "#e9f0f4"]
    for i in range(5):
        ax.axvspan(i, i + 1, color=bands[i], lw=0, zorder=0)
        ax.text(i + 0.5, 101, names[i], ha="center", fontsize=9.5, color=C["text"])
    q0 = None
    for lab, pa, pv, rpre, col, ls, lw in cases:
        P, q = profile(pa, pv, rpre)
        if q0 is None:
            q0 = q
        pc = (P[2] + P[3]) / 2
        ax.plot(xs, P, color=col, lw=lw, ls=ls, marker="o", ms=3.5,
                label=f"{lab}: P$_c$ ≈ {pc:.0f}, flow {q / q0 * 100:.0f}%")
        print(lab, "Pc", round(pc), "flow", round(q / q0 * 100))
    ax.legend(loc="upper right", bbox_to_anchor=(1.0, 0.93), fontsize=8.8, handlelength=2.6, frameon=True,
              facecolor="white", edgecolor="none", framealpha=0.9)
    ax.set_xlim(0, 5)
    ax.set_ylim(0, 106)
    ax.set_xticks([])
    ax.set_ylabel("Mean pressure (mm Hg)")
    fs.grid(ax)
    save(fig, "arteriolar-tone-pc.svg")


# ---------------------------------------------------------------- 4. Autoregulation
def fig_autoregulation():
    P = np.linspace(0, 200, 400)
    Qc, Pc0 = 1.0, 100.0
    lo, hi = 20.0, 150.0
    k = 0.0012  # slight slope: autoregulation is nearly, not perfectly, complete
    plateau = Qc + k * (P - Pc0)
    qlo, qhi = Qc + k * (lo - Pc0), Qc + k * (hi - Pc0)
    ss = np.where(P < lo, qlo * P / lo, np.where(P <= hi, plateau, qhi * P / hi))
    fig, ax = plt.subplots(figsize=(7.0, 4.8))
    ax.axvspan(lo, hi, color=C["shade"], lw=0, zorder=0)
    imm = Qc * P / Pc0
    ax.plot(P, imm, color=C["gray"], lw=1.6, ls=(0, (4, 3)))
    ax.plot(P, ss, color=C["arterial"], lw=2.6)
    for p in (40, 70, 130, 170):
        qi, qs = Qc * p / Pc0, np.interp(p, P, ss)
        ax.plot([p], [qi], "o", color=C["ink"], ms=6)
        ax.plot([p], [qs], "o", mfc="white", mec=C["ink"], ms=6, mew=1.5)
        ax.annotate("", xy=(p, qs + (0.04 if qs < qi else -0.04)), xytext=(p, qi),
                    arrowprops=dict(arrowstyle="-|>", color=C["ink"], lw=1.0))
    ax.plot([Pc0], [Qc], "o", color=C["ink"], ms=7)
    ax.text(103, 0.86, "control", fontsize=9, color=C["ink"])
    ax.text(85, 0.08, "autoregulatory range,\nabout 20 to 150 mm Hg", fontsize=9, color=C["text"], ha="center")
    ax.text(118, 1.82, "dashed: immediately after the pressure\nchange, before resistance adjusts", fontsize=8.8,
            color=C["gray"], ha="center")
    ax.text(186, 0.84, "solid: after local\ncompensation", fontsize=8.8, color=C["arterial"], ha="center")
    ax.set_xlim(0, 200)
    ax.set_ylim(0, 2.1)
    ax.set_xlabel("Perfusion pressure (mm Hg)")
    ax.set_ylabel("Tissue blood flow (relative to control)")
    fs.grid(ax)
    save(fig, "autoregulation.svg")


# ---------------------------------------------------------------- 5. Myogenic and flow-induced responses
def fig_isolated_arteriole():
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.3))
    ax = axes[0]
    ptm = np.array([20, 40, 60, 80, 100, 120, 140])
    intact = np.array([0.76, 0.80, 0.72, 0.68, 0.66, 0.66, 0.66])
    denud = np.array([0.75, 0.78, 0.74, 0.70, 0.68, 0.68, 0.68])
    passive = np.array([0.88, 0.95, 1.00, 1.01, 1.02, 1.04, 1.05])
    ax.plot(ptm, passive, "^-", color=C["gray"], lw=2, ms=6)
    ax.plot(ptm, intact, "o-", color=C["arterial"], lw=2.2, ms=6)
    ax.plot(ptm, denud, "o--", color=C["arterial"], lw=1.6, ms=6, mfc="white")
    ax.text(140, 1.075, "relaxed with nitroprusside:\npassive stretch", fontsize=8.8, color=C["gray"], ha="right")
    ax.text(142, 0.625, "endothelium intact (solid)\nor removed (dashed):\nactive constriction", fontsize=8.8,
            color=C["arterial"], ha="right", va="top")
    ax.set_xlim(10, 150)
    ax.set_ylim(0.45, 1.15)
    ax.set_xlabel("Transmural pressure (cm H$_2$O), no flow")
    ax.set_ylabel("Normalized diameter")
    ax.set_title("A. Myogenic: raise pressure, no flow", fontsize=11)
    fs.grid(ax)
    ax = axes[1]
    g = np.array([0, 4, 10, 20, 40, 60])
    intact = np.array([0.73, 0.83, 0.89, 0.915, 0.922, 0.922])
    denud = np.array([0.73, 0.733, 0.738, 0.738, 0.737, 0.736])
    ax.plot(g, intact, "o-", color=C["venous"], lw=2.2, ms=6)
    ax.plot(g, denud, "o--", color=C["venous"], lw=1.6, ms=6, mfc="white")
    ax.text(60, 0.95, "endothelium intact: dilates", fontsize=8.8, color=C["venous"], ha="right")
    ax.text(60, 0.70, "endothelium removed: no response", fontsize=8.8, color=C["venous"], ha="right")
    ax.set_xlim(-3, 64)
    ax.set_ylim(0.45, 1.15)
    ax.set_xlabel("Pressure gradient along the vessel (cm H$_2$O)")
    ax.set_title("B. Endothelial: raise flow, transmural P constant", fontsize=11)
    fs.grid(ax)
    fig.subplots_adjust(wspace=0.22)
    save(fig, "isolated-arteriole.svg")


# ---------------------------------------------------------------- 6. Reactive and active hyperemia
def fig_hyperemia():
    fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.0), sharey=True)
    t = np.linspace(0, 10, 1000)
    ax = axes[0]
    q = np.ones_like(t)
    occ = (t >= 2) & (t < 4)
    q[occ] = 0.0
    after = t >= 4
    q[after] = 1 + 2.2 * np.exp(-(t[after] - 4) / 0.55) * (1 - np.exp(-(t[after] - 4) / 0.06))
    ax.axvspan(2, 4, color=C["shade"], lw=0)
    ax.plot(t, q, color=C["arterial"], lw=2.4)
    ax.axhline(1, color=C["gray"], lw=0.9, ls=(0, (3, 3)))
    ax.text(3, 0.25, "flow\nstopped", ha="center", fontsize=9, color=C["text"])
    ax.text(4.6, 2.9, "flow above baseline after release:\nmetabolites that built up during\nthe occlusion dilate the arterioles",
            fontsize=8.8, color=C["arterial"])
    ax.set_title("A. Reactive hyperemia", fontsize=11)
    ax.set_xlabel("Time (min)")
    ax.set_ylabel("Blood flow (relative to baseline)")
    ax.set_ylim(0, 3.6)
    ax.set_xlim(0, 10)
    fs.grid(ax)
    ax = axes[1]
    act = (t >= 2) & (t < 7)
    q = np.ones_like(t)
    q[act] = 1 + 1.8 * (1 - np.exp(-(t[act] - 2) / 0.35))
    post = t >= 7
    q[post] = 1 + 1.8 * (1 - np.exp(-5 / 0.35)) * np.exp(-(t[post] - 7) / 0.5)
    ax.axvspan(2, 7, color=C["highlight"], lw=0)
    ax.plot(t, q, color=C["arterial"], lw=2.4)
    ax.axhline(1, color=C["gray"], lw=0.9, ls=(0, (3, 3)))
    ax.text(4.5, 0.4, "muscle working:\nmetabolism raised", ha="center", fontsize=9, color=C["text"])
    ax.text(4.5, 3.05, "flow rises with demand,\nfor as long as the activity lasts", ha="center", fontsize=8.8,
            color=C["arterial"])
    ax.set_title("B. Active hyperemia", fontsize=11)
    ax.set_xlabel("Time (min)")
    ax.set_xlim(0, 10)
    fs.grid(ax)
    fig.subplots_adjust(wspace=0.08)
    save(fig, "hyperemia.svg")


if __name__ == "__main__":
    fig_starling()
    fig_lymph()
    fig_arteriolar_tone()
    fig_autoregulation()
    fig_isolated_arteriole()
    fig_hyperemia()
