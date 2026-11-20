"""Figures for the Membrane Potentials and Excitable Cells chapter.

Run:  cd site/scripts && MPLCONFIGDIR=$TMPDIR PNG_PREVIEW=<folder> python3 figs_excitable_cells.py
Writes SVGs to ../muscle/figures/excitable-cells/.

Membrane potential traces come from a Hodgkin-Huxley model of the squid axon. The Na+
activation gate is shifted 3 mV in the depolarizing direction and the whole trace is offset
so that rest is -70 mV and threshold about -55 mV, the values the course uses for a neuron.
Equilibrium potentials use the course's ion concentrations and 61 mV x log10 at 37 C.
"""
import math
import numpy as np
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle, Ellipse, FancyArrowPatch, Polygon

import figstyle as fs

plt = fs.plt
C = fs.C
M = fs.MINUS
PART, SLUG = "muscle", "excitable-cells"

NA = C["arterial"]     # Na+
K = C["venous"]        # K+
CL = C["green"]        # Cl-
CA = C["gold"]         # Ca2+
LIPID = "#e9dcc3"
PROT = "#c9d6dc"


def save(fig, name):
    fs.save(fig, PART, SLUG, name)


# ------------------------------------------------------------------ course numbers
CONC = {  # mM, outside, inside (2018 course notes; Cl- inside 5 to 25, 7 used here)
    "K": (4.5, 155.0, 1), "Na": (145.0, 12.0, 1), "Cl": (123.0, 7.0, -1), "Ca": (1.8, 0.0001, 2),
}


def nernst(ion):
    o, i, z = CONC[ion]
    return 61.0 / z * math.log10(o / i)


def ghk(pk, pna, pcl):
    ko, ki, _ = CONC["K"]
    nao, nai, _ = CONC["Na"]
    clo, cli, _ = CONC["Cl"]
    return 61.0 * math.log10((pk * ko + pna * nao + pcl * cli) / (pk * ki + pna * nai + pcl * clo))


# ------------------------------------------------------------------ Hodgkin-Huxley model
SM = 3.0  # shift of the Na+ activation gate (mV)


def _rates():
    am = lambda V: 0.1 * (V - SM + 40) / (1 - np.exp(-(V - SM + 40) / 10))
    bm = lambda V: 4 * np.exp(-(V - SM + 65) / 18)
    ah = lambda V: 0.07 * np.exp(-(V + 65) / 20)
    bh = lambda V: 1 / (1 + np.exp(-(V + 35) / 10))
    an = lambda V: 0.01 * (V + 55) / (1 - np.exp(-(V + 55) / 10))
    bn = lambda V: 0.125 * np.exp(-(V + 65) / 80)
    return am, bm, ah, bh, an, bn


def hh(tmax, I, dt=0.005):
    """Return t, V (offset so rest = -70), gNa, gK, h (Na+ inactivation gate, 1 = not inactivated)."""
    am, bm, ah, bh, an, bn = _rates()
    V = -65.0
    for _ in range(4000):  # settle to rest
        m = am(V) / (am(V) + bm(V)); h = ah(V) / (ah(V) + bh(V)); n = an(V) / (an(V) + bn(V))
        Iion = 120 * m ** 3 * h * (V - 50) + 36 * n ** 4 * (V + 77) + 0.3 * (V + 54.387)
        V -= 0.01 * Iion
    m = am(V) / (am(V) + bm(V)); h = ah(V) / (ah(V) + bh(V)); n = an(V) / (an(V) + bn(V))
    rest = V
    t = np.arange(0, tmax, dt)
    out = np.zeros((len(t), 4))
    for i, tt in enumerate(t):
        gna = 120 * m ** 3 * h
        gk = 36 * n ** 4
        out[i] = [V, gna, gk, h]
        Iion = gna * (V - 50) + gk * (V + 77) + 0.3 * (V + 54.387)
        V += dt * (I(tt) - Iion)
        m += dt * (am(V) * (1 - m) - bm(V) * m)
        h += dt * (ah(V) * (1 - h) - bh(V) * h)
        n += dt * (an(V) * (1 - n) - bn(V) * n)
    off = -70.0 - rest
    return t, out[:, 0] + off, out[:, 1], out[:, 2], out[:, 3]


def pulse(t0, amp, dur=0.1):
    return lambda tt: amp if t0 <= tt < t0 + dur else 0.0


def pulses(lst, dur=0.1):
    return lambda tt: sum(a for (t0, a) in lst if t0 <= tt < t0 + dur)


def nspikes(I, tmax):
    t, V, *_ = hh(tmax, I, dt=0.01)
    up = (V[1:] > 0) & (V[:-1] <= 0)
    return int(up.sum())


def fires(I, tmax, n=1):
    return nspikes(I, tmax) >= n


# ------------------------------------------------------------------ 1. Transport across the membrane
def membrane(ax, x0, x1, y0=3.0, y1=5.0):
    """Lipid bilayer as two rows of heads with tails."""
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc=LIPID, ec="none", zorder=1))
    xs = np.arange(x0 + 0.15, x1, 0.3)
    for x in xs:
        for y, d in ((y1 - 0.13, -1), (y0 + 0.13, 1)):
            ax.add_patch(Circle((x, y), 0.13, fc="#d9b98a", ec="#b08a55", lw=0.5, zorder=2))
            ax.plot([x - 0.04, x - 0.04], [y + d * 0.13, y + d * 0.8], color="#b08a55", lw=0.6, zorder=1.5)
            ax.plot([x + 0.04, x + 0.04], [y + d * 0.13, y + d * 0.8], color="#b08a55", lw=0.6, zorder=1.5)


def protein(ax, cx, w=1.1, y0=2.6, y1=5.4, gap=0.0, color=PROT):
    if gap > 0:
        for s in (-1, 1):
            xa = cx + s * (gap / 2 + w / 4)
            ax.add_patch(FancyBboxPatch((xa - w / 4, y0), w / 2, y1 - y0,
                                        boxstyle="round,pad=0.02,rounding_size=0.25", fc=color, ec=C["ink"], lw=1, zorder=3))
    else:
        ax.add_patch(FancyBboxPatch((cx - w / 2, y0), w, y1 - y0,
                                    boxstyle="round,pad=0.02,rounding_size=0.35", fc=color, ec=C["ink"], lw=1, zorder=3))


def arrow(ax, x0, y0, x1, y1, color, lw=1.8, z=5):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, shrinkA=0, shrinkB=0), zorder=z)


def fig_transport():
    fig, ax = plt.subplots(figsize=(10.4, 4.9))
    ax.set_xlim(0, 20.8)
    ax.set_ylim(-0.6, 9.4)
    ax.set_aspect("equal")
    ax.axis("off")
    membrane(ax, 0.2, 20.6)
    ax.text(0.3, 8.0, "Extracellular fluid", fontsize=10, color=C["text"], va="center")
    ax.text(0.3, 0.2, "Cytosol", fontsize=10, color=C["text"], va="center")
    cols = [2.6, 7.6, 12.6, 17.6]
    heads = ["Simple diffusion", "Channel", "Carrier", "Pump (active)"]
    for x, h in zip(cols, heads):
        ax.text(x, 9.0, h, ha="center", fontsize=10.5, fontweight="bold", color=C["ink"])
    # simple diffusion
    for dx, lab in ((-0.9, "O$_2$"), (0.9, "CO$_2$")):
        arrow(ax, cols[0] + dx, 7.0 if lab == "O$_2$" else 1.0, cols[0] + dx, 1.0 if lab == "O$_2$" else 7.0, C["ink"], lw=1.4)
        ax.text(cols[0] + dx + 0.25, 7.25 if lab == "O$_2$" else 0.55, lab, fontsize=9.5, color=C["ink"], ha="center")
    # channel
    protein(ax, cols[1], w=1.6, gap=0.45)
    arrow(ax, cols[1], 0.9, cols[1], 7.2, K)
    ax.text(cols[1] + 0.35, 7.3, "K$^+$ out", fontsize=10, color=K)
    # carrier: two conformations
    protein(ax, cols[2] - 0.9, w=1.3)
    protein(ax, cols[2] + 0.9, w=1.3)
    ax.add_patch(Polygon([[cols[2] - 1.25, 5.42], [cols[2] - 0.55, 5.42], [cols[2] - 0.9, 4.35]], fc="white", ec=C["ink"], lw=1, zorder=4))
    ax.add_patch(Polygon([[cols[2] + 0.55, 2.58], [cols[2] + 1.25, 2.58], [cols[2] + 0.9, 3.65]], fc="white", ec=C["ink"], lw=1, zorder=4))
    ax.add_patch(Circle((cols[2] - 0.9, 5.05), 0.2, fc=C["green"], ec="none", zorder=5))
    ax.add_patch(Circle((cols[2] + 0.9, 2.95), 0.2, fc=C["green"], ec="none", zorder=5))
    arrow(ax, cols[2] - 0.45, 4.0, cols[2] + 0.45, 4.0, C["ink"], lw=1.2)
    ax.text(cols[2] - 0.9, 6.0, "binds\noutside", fontsize=8, ha="center", color=C["text"])
    ax.text(cols[2] + 0.9, 1.3, "releases\ninside", fontsize=8, ha="center", color=C["text"])
    ax.text(cols[2], 7.3, "glucose", fontsize=9.5, color=C["green"], ha="center")
    # pump
    protein(ax, cols[3], w=2.4, color="#d8cfe0")
    ax.text(cols[3], 4.0, "Na$^+$/K$^+$\nATPase", fontsize=9, ha="center", va="center", color=C["ink"], zorder=6)
    arrow(ax, cols[3] - 0.7, 1.4, cols[3] - 0.7, 7.0, NA)
    ax.text(cols[3] - 0.85, 7.25, "3 Na$^+$ out", fontsize=9.5, color=NA, ha="right")
    arrow(ax, cols[3] + 0.7, 7.0, cols[3] + 0.7, 1.4, K)
    ax.text(cols[3] + 0.85, 7.25, "2 K$^+$ in", fontsize=9.5, color=K, ha="left")
    ax.text(cols[3] + 1.4, 1.65, r"ATP $\rightarrow$ ADP + P$_i$", fontsize=9, color=C["purple"], ha="left")
    # passive/active bands
    ax.plot([0.6, 15.0], [-0.25, -0.25], color=C["axis"], lw=1)
    ax.text(7.8, -0.55, "Passive: down the electrochemical gradient, no ATP", ha="center", va="top", fontsize=9.5, color=C["text"])
    ax.plot([15.6, 20.2], [-0.25, -0.25], color=C["axis"], lw=1)
    ax.text(17.9, -0.55, "Active: against the gradient", ha="center", va="top", fontsize=9.5, color=C["text"])
    save(fig, "transport.svg")


# ------------------------------------------------------------------ 2. Two compartments
def fig_two_compartment():
    rng = np.random.default_rng(4)
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.9))
    for k, ax in enumerate(axes):
        ax.set_xlim(0, 10)
        ax.set_ylim(-1.3, 7.4)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.add_patch(Rectangle((0.2, 0.4), 9.6, 5.4, fc="#f7fafb", ec=C["axis"], lw=1.2))
        ax.add_patch(Rectangle((4.85, 0.4), 0.3, 5.4, fc=LIPID, ec="#b08a55", lw=0.8))
        ax.text(2.5, 6.05, "Compartment 1\n0.15 M KCl", ha="center", fontsize=9.5, color=C["ink"])
        ax.text(7.5, 6.05, "Compartment 2\n0.15 M NaCl", ha="center", fontsize=9.5, color=C["ink"])

        def grid_ions(x0, cation, ccol, skip=(), w=3.0):
            for r, y in enumerate(np.linspace(1.0, 5.2, 5)):
                for c, x in enumerate(np.linspace(x0, x0 + w, 4)):
                    jx, jy = rng.uniform(-0.15, 0.15, 2)
                    lab, col = (cation, ccol) if (r + c) % 2 == 0 else ("Cl$^-$", CL)
                    if (r, c) in skip:
                        continue
                    ax.text(x + jx, y + jy, lab, fontsize=8.5, color=col, ha="center", va="center")
        moved = ((1, 3), (3, 3)) if k == 1 else ()
        grid_ions(0.9, "K$^+$", K, skip=moved)
        grid_ions(6.55, "Na$^+$", NA, w=2.75)
        if k == 0:
            ax.set_title("A. At the start: no potential", fontsize=11)
            ax.text(5.0, -0.1, "The membrane lets only K$^+$ through.", ha="center", fontsize=9, color=C["text"])
        else:
            ax.set_title("B. At equilibrium", fontsize=11)
            for y in np.linspace(0.8, 5.4, 8):
                ax.text(4.62, y, M, fontsize=11, color=CL, ha="center", va="center", fontweight="bold")
                ax.text(5.42, y, "+", fontsize=11, color=K, ha="center", va="center", fontweight="bold")
            for y in (2.05, 4.15):
                ax.text(5.72, y, "K$^+$", fontsize=8.5, color=K, ha="left", va="center", fontweight="bold")
            ax.text(5.0, -0.1, "A few K$^+$ have crossed. Their charge holds back the rest:", ha="center", fontsize=9, color=C["text"])
            ax.text(5.0, -0.65, "compartment 1 is negative and net K$^+$ flux is zero.", ha="center", fontsize=9, color=C["text"])
    fig.subplots_adjust(wspace=0.08)
    save(fig, "two-compartment.svg")


# ------------------------------------------------------------------ 3. Equilibrium potentials
def fig_equilibrium():
    ek, ena, ecl, eca = nernst("K"), nernst("Na"), nernst("Cl"), nernst("Ca")
    fig, ax = plt.subplots(figsize=(6.6, 6.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(-128, 150)
    for s in ("top", "right", "bottom"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_position(("data", 5))
    ax.set_xticks([])
    ax.set_yticks(range(-120, 151, 30))
    ax.set_yticklabels([fs.fmt(v) for v in range(-120, 151, 30)])
    ax.tick_params(axis="y", pad=2)
    ax.text(5, 157, "Membrane potential (mV)", ha="center", fontsize=10, color=C["text"])
    left = [("E$_{Ca}$", eca, CA), ("E$_{Na}$", ena, NA), ("E$_{Cl}$", ecl, CL), ("E$_K$", ek, K)]
    for lab, v, col in left:
        ax.plot([2.6, 3.9], [v, v], color=col, lw=2.4)
        ax.text(2.45, v, f"{lab}  {fs.fmt(round(v))}", ha="right", va="center", fontsize=10.5, color=col, fontweight="bold")
    right = [("Neuron at rest", -70, C["ink"], -64), ("Skeletal and cardiac\nmuscle at rest", -90, C["ink"], -92)]
    for lab, v, col, yl in right:
        ax.plot([5.1, 6.6], [v, v], color=col, lw=2.4)
        ax.text(6.8, yl, f"{lab}  {fs.fmt(v)}", ha="left", va="center", fontsize=10, color=col)
    ax.axhline(0, xmin=0.3, xmax=0.7, color=C["axis"], lw=0.8, ls=(0, (3, 3)))
    ax.text(0.1, -104, "Equilibrium potentials\n(Nernst, 37 °C)", fontsize=9.5, color=C["text"], va="top")
    ax.text(9.9, -104, "Resting potentials", fontsize=9.5, color=C["text"], ha="right", va="top")
    save(fig, "equilibrium-potentials.svg")


# ------------------------------------------------------------------ 4. Depolarization, hyperpolarization, graded potentials
def psp(t, t0, amp, tau1=1.0, tau2=6.0):
    s = np.clip(t - t0, 0, None)
    k = (np.exp(-s / tau2) - np.exp(-s / tau1))
    pk = max((np.exp(-x / tau2) - np.exp(-x / tau1)) for x in np.linspace(0.01, 20, 2000))
    return amp * k / pk


def fig_potential_changes():
    fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.4), gridspec_kw=dict(width_ratios=[1, 1.15]))
    ax = axes[0]
    t = np.linspace(0, 60, 1200)
    v = -70 + psp(t, 8, 9) + psp(t, 34, -5)
    fs.grid(ax)
    ax.plot(t, v, color=C["ink"], lw=2)
    ax.axhline(-70, color=C["axis"], lw=0.8, ls=(0, (3, 3)))
    ax.set_ylim(-85, -50)
    ax.set_xlim(0, 60)
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("Membrane potential (mV)")
    ax.set_yticks([-80, -70, -60, -50])
    ax.set_yticklabels([fs.fmt(x) for x in (-80, -70, -60, -50)])
    ax.annotate("Glutamate opens\ncation channels:\nNa$^+$ in, depolarization", xy=(11, -61.5), xytext=(16, -55.5),
                fontsize=9, color=NA, arrowprops=dict(arrowstyle="-", color=NA, lw=0.8))
    ax.annotate("GABA opens Cl$^-$ channels:\nCl$^-$ in, hyperpolarization", xy=(37, -76.8), xytext=(14, -83.5),
                fontsize=9, color=CL, arrowprops=dict(arrowstyle="-", color=CL, lw=0.8))
    ax.text(58, -69.3, "rest", fontsize=9, color=C["text"], ha="right", va="bottom")
    ax.set_title("A. Two directions of change")

    ax = axes[1]
    thr = 14.8  # 1 ms current pulse that just reaches threshold in this model
    stim = [(2, 0.35 * thr), (12, 0.55 * thr), (22, 0.8 * thr), (32, 0.85 * thr), (33.5, 0.85 * thr)]
    t, V, *_ = hh(45, pulses(stim, dur=1.0))
    fs.grid(ax)
    ax.plot(t, V, color=C["ink"], lw=1.8)
    ax.axhline(-55, color=C["muscle"], lw=1, ls=(0, (4, 3)))
    ax.text(44.5, -54, "threshold", fontsize=9, color=C["muscle"], va="bottom", ha="right")
    ax.axhline(-70, color=C["axis"], lw=0.8, ls=(0, (3, 3)))
    ax.set_ylim(-86, 40)
    ax.set_xlim(0, 45)
    ax.set_xlabel("Time (ms)")
    ax.set_yticks([-80, -55, -40, 0, 40])
    ax.set_yticklabels([fs.fmt(x) for x in (-80, -55, -40, 0, 40)])
    for x, lab in ((2, "small"), (12, "larger"), (22, "larger still,\nbelow threshold")):
        ax.text(x + 1.5, -50, lab, fontsize=8.5, color=C["text"], ha="center", va="bottom")
    ax.text(31.0, 10, "two inputs close\ntogether summate,\nreach threshold, and\nfire an action potential",
            fontsize=8.8, color=C["ink"], ha="right", va="center")
    for (x, a) in stim:
        ax.plot([x, x], [-85, -82], color=C["purple"], lw=1.4)
    ax.text(44.5, -83.5, "stimuli", fontsize=8.5, color=C["purple"], ha="right", va="center")
    ax.set_title("B. Graded potentials and threshold")
    fig.subplots_adjust(wspace=0.22)
    save(fig, "potential-changes.svg")


# ------------------------------------------------------------------ 5. The action potential
COND = (1.0, 18.0, 1.0)  # conditioning stimulus: start (ms), amplitude, duration (ms)


def refractory_bounds():
    """Absolute refractory period: the time after the conditioning stimulus before a brief test pulse
    (0.1 ms, 4 times the resting threshold for that pulse) can set off a new Na+-driven spike.
    A response counts as a spike only if V keeps rising after the pulse ends to a peak above 0 mV
    within 2 ms of the pulse, and the test adds g_Na of at least 0.3 of the conditioning spike's peak.
    This rejects passive voltage kicks from the test current."""
    t0, amp, dur = COND
    lo, hi = 0.0, 400.0
    for _ in range(12):
        mid = (lo + hi) / 2
        if fires(pulse(t0, mid), t0 + 8):
            hi = mid
        else:
            lo = mid
    test_amp = 4 * hi
    dt = 0.01
    tc, Vc, gc, *_ = hh(t0 + 8, pulses([(t0, amp)], dur=dur), dt=dt)
    g_ctrl = gc.max()
    t_peak = tc[Vc.argmax()]  # the cell is already firing before its peak; search after it
    for d in np.arange(t_peak - t0, 13.0, 0.05):
        test = t0 + d
        I = lambda tt, test=test: (amp if t0 <= tt < t0 + dur else 0.0) + (test_amp if test <= tt < test + 0.1 else 0.0)
        t, V, g, *_ = hh(test + 3, I, dt=dt)
        end = test + 0.1
        w = (t > end) & (t <= test + 2.0)
        if not w.any():
            continue
        iw = np.argmax(V[w])
        vpk = V[w][iw]
        rising = iw > int(0.05 / dt)
        gc_w = np.interp(t[w], tc, gc)
        extra_g = (g[w] - gc_w).max()   # Na+ conductance beyond the conditioning spike's own
        if vpk > 0 and rising and extra_g > 0.3 * g_ctrl:
            return test
    return None


def fig_action_potential():
    t0, amp, dur = COND
    t, V, gna, gk, h = hh(14, pulses([(t0, amp)], dur=dur))
    ith = np.argmax(V > -55)
    ipk = V.argmax()
    tpk = t[ipk]
    i_min = ipk + V[ipk:].argmin()
    # Drawn as the lecture teaches it: absolute refractory from the upstroke through repolarization
    # (until Vm falls back past rest); relative refractory during the rebound hyperpolarization.
    arp_end = t[ipk + np.argmax(V[ipk:] < -70)]
    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(9.2, 7.6), sharex=True, gridspec_kw=dict(height_ratios=[1.7, 1]))
    fs.grid(ax)
    ax.axvspan(t[ith], arp_end, color=C["highlight"], zorder=0)
    ax.axvspan(arp_end, 14, color=C["cool"], zorder=0)
    ax.plot(t, V, color=C["ink"], lw=2.2)
    ax.axhline(-55, color=C["muscle"], lw=1, ls=(0, (4, 3)))
    ax.axhline(-70, color=C["axis"], lw=0.8, ls=(0, (3, 3)))
    ax.set_ylim(-95, 50)
    ax.set_ylabel("Membrane potential (mV)")
    ax.set_yticks([-90, -70, -55, -30, 0, 30])
    ax.set_yticklabels([fs.fmt(x) for x in (-90, -70, -55, -30, 0, 30)])
    ax.text(0.1, -53.5, "threshold", fontsize=9, color=C["muscle"], ha="left", va="bottom")
    ax.text(0.1, -68.5, "rest", fontsize=9, color=C["text"], ha="left", va="bottom")
    iup = np.argmax(V > 0)
    idn = ipk + np.argmax(V[ipk:] < 0)

    def num(n, x, y):
        ax.add_patch(Ellipse((x, y), 0.34, 9, fc="white", ec=C["ink"], lw=1, zorder=6))
        ax.text(x, y, n, ha="center", va="center", fontsize=9, zorder=7, color=C["ink"])
    num("1", t[ith] - 0.3, -55)
    num("2", t[iup] - 0.3, 0)
    num("3", t[idn] + 0.3, 0)
    num("4", t[i_min], V[i_min] - 8)
    ax.text(t[iup] - 0.55, 12, "Na$^+$ channels\nopen, Na$^+$ in", fontsize=8.6, color=NA, ha="right", va="center")
    ax.text(t[idn] + 0.55, 12, "Na$^+$ channels inactivate,\nK$^+$ channels open, K$^+$ out", fontsize=8.6, color=C["ink"], ha="left", va="center")
    ax.text(t[i_min] + 0.3, V[i_min] - 8, "K$^+$ channels still open:\nV$_m$ moves toward E$_K$", fontsize=8.6, color=K, va="center")
    ax.text((t[ith] + arp_end) / 2 - 0.35, -84, "absolute refractory:\nno second spike possible", ha="center", va="center", fontsize=8.6, color="#8a5a1e")
    ax.text(arp_end + 0.25, -45, "5. relative refractory:\nthreshold still raised", ha="left", va="center", fontsize=8.6, color="#4d6a77")
    ax.set_title("A. Membrane potential")
    fs.grid(ax2)
    ax2.plot(t, gna, color=NA, lw=2.2)
    ax2.plot(t, gk, color=K, lw=2.2)
    ig = gna.argmax()
    ax2.text(t[ig] + 0.25, gna.max() * 0.95, "g$_{Na}$: opens fast,\nthen inactivates", color=NA, fontsize=9, va="top")
    ik = gk.argmax()
    ax2.text(t[ik] + 0.7, gk.max() * 0.9, "g$_K$: opens slowly,\ncloses slowly", color=K, fontsize=9, va="center")
    ax2.set_ylabel("Conductance (mS/cm$^2$)")
    ax2.set_xlabel("Time (ms)")
    ax2.set_xlim(0, 14)
    ax2.set_ylim(0, max(gna.max(), gk.max()) * 1.12)
    ax2.set_title("B. Na$^+$ and K$^+$ conductances")
    fig.subplots_adjust(hspace=0.2)
    save(fig, "action-potential.svg")
    return arp_end - t[ith]


# ------------------------------------------------------------------ 6. Action potential shapes
def cardiac_ap(t):
    v = np.full_like(t, -90.0)
    up = (t >= 10) & (t < 12)
    v[up] = -90 + 110 * (t[up] - 10) / 2
    a = t >= 12
    s = t[a] - 12
    notch = 20 - 18 * (1 - np.exp(-s / 3))
    plateau = 2 + 4 * np.exp(-s / 60)
    v2 = np.where(s < 12, notch, plateau)
    rep = 1 / (1 + np.exp((s - 235) / 14))
    v[a] = -90 + (v2 + 90) * rep
    from numpy import convolve
    k = np.ones(15) / 15
    vv = np.convolve(np.pad(v, 7, mode="edge"), k, mode="valid")
    return vv


def skeletal_ap(t):
    s = np.clip(t - 1.0, 0, None)
    rise = 1 - np.exp(-(s / 0.35) ** 2)
    fall = np.exp(-np.clip(s - 0.7, 0, None) / 1.0)
    return -90 + 120 * rise * fall


def fig_ap_shapes():
    t1, V1, *_ = hh(8, pulses([(COND[0], COND[1])], dur=COND[2]))
    t2 = np.linspace(0, 12, 1200)
    V2 = skeletal_ap(t2)
    t3 = np.linspace(0, 400, 4000)
    V3 = cardiac_ap(t3)
    fig, axes = plt.subplots(1, 3, figsize=(11.2, 4.0), sharey=True, gridspec_kw=dict(width_ratios=[1, 1, 1.5]))
    data = [(t1, V1, "A. Neuron", C["purple"], "about 2 ms", 8), (t2, V2, "B. Skeletal muscle fiber", C["green"], "about 5 ms", 12),
            (t3, V3, "C. Ventricular muscle cell", C["arterial"], "about 250 ms", 400)]
    for ax, (t, V, title, col, dur, tmax) in zip(axes, data):
        fs.grid(ax)
        ax.plot(t, V, color=col, lw=2.2)
        ax.set_xlim(0, tmax)
        ax.set_title(title)
        ax.set_xlabel("Time (ms)")
        ax.axhline(0, color=C["axis"], lw=0.8)
    axes[0].set_ylabel("Membrane potential (mV)")
    axes[0].set_ylim(-100, 45)
    axes[0].set_yticks([-90, -70, -50, -30, 0, 30])
    axes[0].set_yticklabels([fs.fmt(x) for x in (-90, -70, -50, -30, 0, 30)])
    axes[0].text(4.2, 25, "about 2 ms", fontsize=9, color=C["purple"])
    axes[1].set_xticks([0, 2, 4, 6, 8, 10, 12])
    axes[1].text(4.0, 20, "about 5 ms", fontsize=9, color=C["green"])
    axes[2].annotate("", xy=(255, -20), xytext=(12, -20), arrowprops=dict(arrowstyle="<->", color=C["arterial"], lw=1.2))
    axes[2].text(130, -16, "about 250 ms: Ca$^{2+}$ plateau", fontsize=9, color=C["arterial"], ha="center", va="bottom")
    fig.subplots_adjust(wspace=0.08)
    save(fig, "ap-shapes.svg")


# ------------------------------------------------------------------ 7. Propagation by local circuit currents
def fig_propagation():
    t0, amp, dur = COND
    t, V, gna, gk, h = hh(14, pulses([(t0, amp)], dur=dur))
    tpk = t[V.argmax()]
    x = np.linspace(0, 10, 1000)
    # the wave travels to the right at 1 length unit per ms; the peak sits at x = 6.8
    tt = tpk + (6.8 - x)
    Vx = np.interp(tt, t, V)
    # ahead of the wave, replace the injected-current ramp with a smooth exponential foot
    t_end = t0 + dur
    v_end = np.interp(t_end, t, V)
    foot = tt < t_end
    Vx[foot] = -70 + (v_end + 70) * np.exp((tt[foot] - t_end) / 0.35)
    kern = np.ones(15) / 15
    Vx = np.convolve(np.pad(Vx, 7, mode="edge"), kern, mode="valid")
    gx = np.interp(tt, t, gna)
    hx = np.interp(tt, t, h)
    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(9.6, 6.8), sharex=True, gridspec_kw=dict(height_ratios=[1.25, 1]))
    fs.grid(ax)
    ax.plot(x, Vx, color=C["ink"], lw=2.2)
    ax.axhline(-55, color=C["muscle"], lw=1, ls=(0, (4, 3)))
    ax.set_ylabel("V$_m$ (mV)")
    ax.set_ylim(-90, 50)
    ax.set_xlim(0, 10)
    ax.set_xticks([])
    ax.set_yticks([-70, -55, 0, 30])
    ax.set_yticklabels([fs.fmt(v) for v in (-70, -55, 0, 30)])
    ax.set_title("A. One moment in time: membrane potential along the axon")
    ax.annotate("", xy=(9.8, 38), xytext=(8.2, 38), arrowprops=dict(arrowstyle="-|>", color=C["ink"], lw=1.6))
    ax.text(8.1, 38, "direction of travel", ha="right", va="center", fontsize=9, color=C["ink"])
    ax.text(0.1, -53.5, "threshold", fontsize=9, color=C["muscle"], ha="left", va="bottom")
    ax2.set_ylim(-2.9, 2.6)
    ax2.set_xlim(0, 10)
    ax2.axis("off")
    ax2.add_patch(Rectangle((0, -0.7), 10, 1.4, fc="#f7fafb", ec="none"))
    act = x[gx > 0.25 * gx.max()]
    a_lo, a_hi = act.min(), act.max()
    ref = x[(hx < 0.3) & (x < a_lo)]
    r_lo = ref.min()
    ax2.add_patch(Rectangle((a_lo, -0.7), a_hi - a_lo, 1.4, fc=C["highlight"], ec="none"))
    ax2.add_patch(Rectangle((r_lo, -0.7), a_lo - r_lo, 1.4, fc=C["cool"], ec="none"))
    ax2.plot([0, 10], [0.7, 0.7], color=C["ink"], lw=1.5)
    ax2.plot([0, 10], [-0.7, -0.7], color=C["ink"], lw=1.5)
    for xx in (r_lo, a_lo, a_hi):
        ax.axvline(xx, color=C["axis"], lw=0.8, ls=(0, (2, 2)))
    xp = (a_lo + a_hi) / 2
    ax2.annotate("", xy=(xp, -0.3), xytext=(xp, 1.7), arrowprops=dict(arrowstyle="-|>", color=NA, lw=1.8))
    ax2.text(xp + 0.12, 1.75, "Na$^+$ in", color=NA, fontsize=9.5, va="bottom")
    for d in (-1, 1):
        ax2.add_patch(FancyArrowPatch((xp + d * 0.2, 0.15), (xp + d * 1.7, 0.15), arrowstyle="-|>",
                                      mutation_scale=12, color=C["ink"], lw=1.3))
        ax2.add_patch(FancyArrowPatch((xp + d * 1.8, 1.05), (xp + d * 0.35, 1.05), arrowstyle="-|>",
                                      mutation_scale=12, color=C["ink"], lw=1.0, ls=(0, (3, 2))))
    ax2.text(xp - 1.9, 0.15, "current inside", fontsize=8.5, va="center", ha="right", color=C["ink"])
    ax2.text(xp - 1.95, 1.05, "return current outside", fontsize=8.5, va="center", ha="right", color=C["ink"])
    ax2.text((r_lo + a_lo) / 2, -1.0, "refractory:\nNa$^+$ channels\ninactivated", ha="center", va="top", fontsize=8.8, color="#4d6a77")
    ax2.text(xp, -1.0, "active:\nNa$^+$ channels\nopen", ha="center", va="top", fontsize=8.8, color=NA)
    ax2.text((a_hi + 10) / 2, -1.0, "resting:\ndepolarized by\nlocal current", ha="center", va="top", fontsize=8.8, color=C["ink"])
    ax2.text(r_lo / 2, -1.0, "recovering\n(relative refractory)", ha="center", va="top", fontsize=8.8, color=C["text"])
    ax2.set_title("B. The axon at that moment", loc="left")
    fig.subplots_adjust(hspace=0.12)
    save(fig, "propagation.svg")


if __name__ == "__main__":
    print("E_K %.1f  E_Na %.1f  E_Cl %.1f  E_Ca %.1f" % (nernst("K"), nernst("Na"), nernst("Cl"), nernst("Ca")))
    print("GHK rest (1:0.04:0.45) %.1f   peak (1:20:0.45) %.1f" % (ghk(1, 0.04, 0.45), ghk(1, 20, 0.45)))
    CONC["K"] = (9.0, 155.0, 1)
    print("K_o 9 mM: E_K %.1f  GHK rest %.1f" % (nernst("K"), ghk(1, 0.04, 0.45)))
    CONC["K"] = (4.5, 155.0, 1)
    fig_transport()
    fig_two_compartment()
    fig_equilibrium()
    fig_potential_changes()
    arp = fig_action_potential()
    print("absolute refractory lasts %.2f ms from threshold" % arp)
    fig_ap_shapes()
    fig_propagation()
