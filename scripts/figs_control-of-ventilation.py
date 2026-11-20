"""Figures for the Control of "Ventilation" chapter (pulmonary block, P10).

Run:  cd site/scripts && MPLCONFIGDIR=$TMPDIR PNG_PREVIEW=<folder> python3 figs_control-of-ventilation.py
Writes SVGs to ../pulmonary/figures/control-of-ventilation/.

The chemoreceptor curves come from one small model, chosen so that a person at PaO2 100 and
PaCO2 40 mm Hg breathes the course's 7.5 L/min and the shapes match the lecture's curves:
    VE = max(Vmin, S(PaO2) * (PaCO2 - T(PaO2)))
    S = 1.1 * H(PaO2) L/min per mm Hg, H = 1 + 20 exp(-(PaO2 - 20)/10)
    T = 33.2 - 1.5 (H - 1) mm Hg (hypoxia lowers the threshold a little), Vmin = 2 L/min (soft floor)
    so at PaO2 100 the knee sits near PaCO2 35 and 40 is on the straight part.
"""
import numpy as np
from matplotlib.patches import FancyBboxPatch

import figstyle as fs

plt, C = fs.plt, fs.C
PART, SLUG = "pulmonary", "control-of-ventilation"
M = fs.MINUS


def H(p):
    return 1 + 20 * np.exp(-(p - 20) / 10)


def ve(pco2, po2, vmin=2.0):
    h = H(po2)
    t = 33.2 - 1.5 * (h - 1)
    raw = 1.1 * h * (pco2 - t)
    k = 1.2  # soft floor, so the curves bend smoothly onto the awake minimum
    return vmin + k * np.log1p(np.exp((raw - vmin) / k))


def box(ax, x, y, w, h, text, fc, ec, fs_=9.5, bold=False, tc=None):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc=fc, ec=ec, lw=1.6, zorder=2))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs_, color=tc or C["ink"],
            fontweight="bold" if bold else "normal", zorder=3)


def arrow(ax, x0, y0, x1, y1, color, style="-|>", lw=1.6, ls="-", rad=0.0):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle=style, color=color, lw=lw, ls=ls,
                                connectionstyle=f"arc3,rad={rad}", shrinkA=2, shrinkB=2), zorder=1)


# ---------------------------------------------------------------- 1. The brainstem centers
def fig_centers():
    fig, ax = plt.subplots(figsize=(9.6, 6.6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 9)
    ax.axis("off")
    # regions
    ax.add_patch(FancyBboxPatch((0.4, 5.6), 7.4, 3.0, boxstyle="round,pad=0.02,rounding_size=0.3",
                                fc=C["highlight"], ec="none", zorder=0))
    ax.add_patch(FancyBboxPatch((0.4, 1.3), 7.4, 4.1, boxstyle="round,pad=0.02,rounding_size=0.3",
                                fc=C["cool"], ec="none", zorder=0))
    ax.text(0.6, 8.3, "PONS: modulates the rhythm", fontsize=10, color=C["gold"], fontweight="bold")
    ax.text(0.6, 5.1, "MEDULLA: generates the rhythm", fontsize=10, color=C["cw"], fontweight="bold")
    # pontine centers
    box(ax, 2.4, 7.4, 3.0, 0.9, "Pneumotaxic center (PC)\ninhibits the AC", "white", C["gold"])
    box(ax, 2.4, 6.15, 3.0, 0.9, "Apneustic center (AC)\ndrives inspiration", "white", C["gold"])
    arrow(ax, 2.4, 6.95, 2.4, 6.6, C["gold"], style="-[", lw=1.6)
    # medullary centers
    box(ax, 2.0, 4.15, 2.8, 1.0, "Pre-Bötzinger complex\nautorhythmic: starts\neach breath", "white", C["system"], bold=False)
    box(ax, 2.0, 2.25, 2.8, 0.95, "Bötzinger complex\ninhibitory: ends\ninspiration", "white", C["system"])
    arrow(ax, 2.0, 2.73, 2.0, 3.62, C["system"], style="-[", lw=1.6)
    box(ax, 5.9, 4.15, 3.0, 1.0, "Dorsal respiratory group\n(DRG): tidal breathing;\nbeside the NTS", "white", C["cw"])
    box(ax, 5.9, 2.25, 3.0, 1.0, "Ventral respiratory group\n(VRG): augmented\nbreathing", "white", C["cw"])
    arrow(ax, 3.42, 4.25, 4.38, 4.25, C["system"])
    arrow(ax, 3.42, 3.95, 4.38, 2.5, C["system"])
    arrow(ax, 3.9, 6.15, 4.6, 4.7, C["gold"], rad=-0.2)
    # muscles
    box(ax, 10.1, 5.5, 3.2, 1.25, "Primary muscles\ndiaphragm,\nexternal intercostals", C["shade"], C["muscle"])
    box(ax, 10.1, 2.25, 3.2, 1.6, "Secondary muscles\nupper airway, neck (SCM,\nscalenes), pectorals; internal\nintercostals, abdominal", C["shade"], C["muscle"])
    arrow(ax, 7.42, 4.35, 8.48, 5.3, C["cw"])
    arrow(ax, 7.42, 2.25, 8.48, 2.25, C["cw"])
    ax.text(10.1, 6.45, "quiet (eupneic) inspiration", ha="center", fontsize=8.8, color=C["muscle"])
    ax.text(10.1, 3.25, "augmented inspiration, forced expiration", ha="center", fontsize=8.8, color=C["muscle"])
    ax.text(0.4, 0.55, "Arrows excite; bars inhibit. Quiet expiration needs no muscle: the lung recoils back to FRC.",
            fontsize=8.8, color=C["text"])
    fs.save(fig, PART, SLUG, "centers.svg")


# ---------------------------------------------------------------- 2. Transections
def trace(kind, t):
    """Synthetic breathing traces, after the transection figure the lecture uses."""
    y = np.zeros_like(t)
    def saw(period, rise, height, start=0.3):
        out = np.zeros_like(t)
        for k in np.arange(start, t[-1], period):
            up = (t >= k) & (t < k + rise)
            out[up] = height * (t[up] - k) / rise
            dn = (t >= k + rise) & (t < k + rise + 0.35)
            out[dn] = height * (1 - (t[dn] - k - rise) / 0.35)
        return out
    if kind == "normal":
        y = saw(4.0, 2.4, 0.55)
    elif kind == "slow-deep":
        y = saw(6.5, 4.6, 1.0)
    elif kind == "apneusis":
        k0, rise, hold = 1.0, 2.5, 9.0
        up = (t >= k0) & (t < k0 + rise)
        y[up] = 1.0 * (t[up] - k0) / rise
        hl = (t >= k0 + rise) & (t < k0 + rise + hold)
        y[hl] = 1.0 - 0.06 * np.sin(np.pi * (t[hl] - k0 - rise) / hold)
        dn = (t >= k0 + rise + hold) & (t < k0 + rise + hold + 0.6)
        y[dn] = 1.0 * (1 - (t[dn] - k0 - rise - hold) / 0.6)
    elif kind == "gasp":
        for k in (1.0, 4.2, 5.4, 9.5, 12.0):
            up = (t >= k) & (t < k + 0.35)
            y[up] = 1.0 * (t[up] - k) / 0.35
            dn = (t >= k + 0.35) & (t < k + 0.6)
            y[dn] = 1.0 * (1 - (t[dn] - k - 0.35) / 0.25)
    return y


def fig_transections():
    rows = [("I", "Above the pons", "normal", "normal", "slow-deep", "slower, deeper"),
            ("II", "Between PC and AC", "slow-deep", "slower, deeper", "apneusis", "apneusis (held inspiration)"),
            ("III", "Between pons and medulla", "gasp", "gasping", "gasp", "gasping"),
            ("IV", "Below the medulla", None, "no breathing", None, "no breathing")]
    t = np.linspace(0, 15, 1500)
    fig, axes = plt.subplots(4, 2, figsize=(9.2, 6.4), sharex=True, sharey=True)
    for i, (lev, where, k1, l1, k2, l2) in enumerate(rows):
        for j, (k, lab) in enumerate(((k1, l1), (k2, l2))):
            ax = axes[i, j]
            y = trace(k, t) if k else np.zeros_like(t)
            ax.plot(t, y, color=C["system"], lw=1.8)
            ax.set_ylim(-0.1, 1.25)
            ax.set_xlim(0, 15)
            ax.set_yticks([])
            for s in ("left", "bottom"):
                ax.spines[s].set_visible(False)
            ax.tick_params(axis="x", length=0, labelbottom=False)
            ax.text(15, 1.12, lab, ha="right", fontsize=9, color=C["ink"], style="italic")
            if j == 0:
                ax.text(-0.6, 0.5, f"Level {lev}\n{where}", ha="right", va="center", fontsize=9.5,
                        color=C["ink"], fontweight="bold")
    axes[0, 0].set_title("Vagi intact", loc="center", fontsize=11)
    axes[0, 1].set_title("Vagi cut", loc="center", fontsize=11)
    axes[3, 1].plot([10, 15], [-0.05, -0.05], color=C["ink"], lw=2)
    axes[3, 1].text(12.5, 0.08, "5 s", ha="center", fontsize=9, color=C["ink"])
    fig.text(0.5, 0.01, "Upward deflection is inspiration. Levels run from the top of the pons (I) to below the medulla (IV).",
             ha="center", fontsize=8.8, color=C["text"])
    fig.subplots_adjust(left=0.22, wspace=0.08, hspace=0.25)
    fs.save(fig, PART, SLUG, "transections.svg")


# ---------------------------------------------------------------- 3. Chemoreceptor response curves
def fig_chemo():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.4, 4.6))
    po2 = np.linspace(30, 140, 400)
    for pc, col in ((36, C["venous"]), (40, C["system"]), (44, C["gold"])):
        a1.plot(po2, ve(pc, po2), color=col, lw=2.2)
        lab_x = 118
        a1.text(lab_x, ve(pc, lab_x) + 1.2, f"PaCO$_2$ {pc}", color=col, fontsize=9.5, ha="center")
    a1.axvspan(30, 60, color=C["shade"], zorder=0)
    a1.text(45, 1.2, "steep below about 60", ha="center", fontsize=8.6, color=C["text"])
    a1.text(95, 30, "flat above about 60:\na wide range of PaO$_2$\nbarely changes $\\dot{V}_E$", ha="center", fontsize=9, color=C["text"])
    a1.set_xlim(30, 140)
    a1.set_ylim(0, 60)
    a1.set_xlabel("Arterial PO$_2$ (mm Hg)")
    a1.set_ylabel("Minute ventilation, $\\dot{V}_E$ (L/min)")
    a1.set_title("A. Response to O$_2$, PaCO$_2$ held constant")
    fs.grid(a1)
    pco2 = np.linspace(25, 55, 400)
    for p, col, lab in ((110, C["system"], "PaO$_2$ 110"), (47, C["gold"], "PaO$_2$ 47"), (37, C["muscle"], "PaO$_2$ 37")):
        y = ve(pco2, p)
        a2.plot(pco2, y, color=col, lw=2.2)
        xi = np.argmin(np.abs(y - 52))
        if y.max() > 52:
            a2.text(pco2[xi] - 0.4, 54, lab, color=col, fontsize=9.5, ha="right")
        else:
            a2.text(55, y[-1] + 1.5, lab, color=col, fontsize=9.5, ha="right")
    a2.plot([40], [ve(40, 100)], "o", color=C["system"], ms=6, zorder=5)
    a2.annotate("normal: PaCO$_2$ 40,\n$\\dot{V}_E$ about 7.5 L/min", xy=(40, ve(40, 100)), xytext=(42.5, 3),
                fontsize=9, color=C["ink"], arrowprops=dict(arrowstyle="-", color=C["ink"], lw=0.8))
    a2.set_xlim(25, 55)
    a2.set_ylim(0, 60)
    a2.set_xlabel("Arterial PCO$_2$ (mm Hg)")
    a2.set_title("B. Response to CO$_2$, PaO$_2$ held constant")
    fs.grid(a2)
    fig.subplots_adjust(wspace=0.18)
    fs.save(fig, PART, SLUG, "chemoreceptor-curves.svg")


# ---------------------------------------------------------------- 4. Blunted CO2 response
def fig_copd():
    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    x = np.linspace(30, 65, 300)
    normal = ve(x, 100)
    rawb = 0.8 * (x - 42.6)
    blunt = 2.0 + 1.2 * np.log1p(np.exp((rawb - 2.0) / 1.2))  # same soft floor as the normal curve
    ax.plot(x, normal, color=C["system"], lw=2.4)
    ax.plot(x, blunt, color=C["venous"], lw=2.4)
    ax.text(36.5, 18, "Normal", color=C["system"], fontsize=10.5, fontweight="bold")
    ax.text(55.6, 1.0, "Chronic CO$_2$\nretention (COPD)", color=C["venous"], fontsize=10.5, fontweight="bold", ha="left")
    ax.plot([40], [7.5], "o", color=C["system"], ms=6)
    ax.plot([52], [7.5], "o", color=C["venous"], ms=6)
    ax.annotate("", xy=(51.3, 7.5), xytext=(40.7, 7.5), arrowprops=dict(arrowstyle="-|>", color=C["ink"], lw=1.3))
    ax.text(46.5, 8.6, "same $\\dot{V}_E$,\nhigher PaCO$_2$", ha="center", fontsize=9, color=C["ink"])
    ax.annotate("flatter: each extra mm Hg\nof CO$_2$ drives less breathing", xy=(61.5, 14.4), xytext=(55.6, 7.0),
                fontsize=9, color=C["venous"], arrowprops=dict(arrowstyle="-", color=C["venous"], lw=0.8))
    ax.set_xlim(30, 65)
    ax.set_ylim(0, 40)
    ax.set_xlabel("Arterial PCO$_2$ (mm Hg)")
    ax.set_ylabel("Minute ventilation, $\\dot{V}_E$ (L/min)")
    fs.grid(ax)
    fs.save(fig, PART, SLUG, "blunted-co2-response.svg")


# ---------------------------------------------------------------- 5. Cheyne-Stokes
def fig_cheyne_stokes():
    t = np.linspace(0, 130, 6000)
    period, hyper = 65.0, 40.0
    phase = (t % period)
    env = np.where(phase < hyper, np.sin(np.pi * phase / hyper) ** 2, 0.0)
    breaths = np.sin(2 * np.pi * t / 3.2)
    vt = 1.4 * env * breaths
    # PaCO2 follows ventilation at once: it falls through the hyperpnea and builds during apnea.
    # (The delay in the loop is on the sensing side: breathing keeps rising after PaCO2 has started to fall.)
    dt = t[1] - t[0]
    p, pco2 = 42.0, np.zeros_like(t)
    for _ in range(3):  # run to a steady cycle
        for i in range(len(t)):
            p += dt * (0.25 - 0.95 * env[i]) * 0.9
            pco2[i] = p
    pco2 = 40 + (pco2 - pco2.mean()) * (6 / (pco2.max() - pco2.min()))
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(9.0, 4.8), sharex=True, gridspec_kw=dict(height_ratios=[1.5, 1]))
    a1.plot(t, vt, color=C["system"], lw=1.3)
    a1.axhline(0, color=C["axis"], lw=0.8, ls=(0, (3, 3)))
    a1.set_ylabel("Breathing\n(volume)")
    a1.set_yticks([])
    for k in (0, 1):
        a1.text(k * period + hyper / 2, 1.6, "hyperpnea: deep,\nfast breaths", ha="center", fontsize=9, color=C["ink"])
        a1.text(k * period + hyper + (period - hyper) / 2, 0.35, "apnea", ha="center", fontsize=9.5, color=C["ink"])
    a1.set_ylim(-1.6, 2.4)
    a1.spines["left"].set_visible(False)
    a2.plot(t, pco2, color=C["venous"], lw=2)
    a2.set_ylabel("PaCO$_2$\n(mm Hg)")
    a2.set_yticks([37, 40, 43])
    a2.set_xlabel("Time (s)")
    a2.set_xlim(0, 130)
    a2.text(129, 43.6, "CO$_2$ builds during apnea and is blown off, past normal, during hyperpnea",
            ha="right", fontsize=8.8, color=C["venous"])
    a2.set_ylim(35.5, 45)
    fs.grid(a2)
    fig.subplots_adjust(hspace=0.12)
    fs.save(fig, PART, SLUG, "cheyne-stokes.svg")


# ---------------------------------------------------------------- 6. The whole control system
def fig_loop():
    fig, ax = plt.subplots(figsize=(9.8, 6.4))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8.4)
    ax.axis("off")
    box(ax, 6.0, 7.5, 5.4, 0.9, "Higher brain centers: motor and prefrontal cortex,\nhypothalamus, amygdala (can override the rhythm)",
        C["shade"], C["purple"], fs_=9.3)
    box(ax, 6.0, 5.7, 4.0, 1.0, "Rhythm generation (medulla)\npre-Bötzinger, Bötzinger\nand modulation (pons)",
        "white", C["system"], fs_=9.3, bold=False)
    box(ax, 10.2, 5.7, 3.0, 1.0, "Respiratory muscles\nprimary (via DRG)\nsecondary (via VRG)", "white", C["muscle"], fs_=9.3)
    box(ax, 10.2, 3.2, 3.0, 1.0, "Lungs and\ngas exchange", "white", C["lung"], fs_=9.5)
    box(ax, 6.0, 1.15, 4.2, 0.85, "Arterial blood: PaO$_2$, PaCO$_2$, pH;\nblood pressure", C["cool"], C["cw"], fs_=9.3)
    sens = [(1.8, 5.9, "Central chemoreceptors\nventral medulla\nCO$_2$ and H$^+$"),
            (1.8, 4.25, "Peripheral chemoreceptors\ncarotid (CN IX), aortic (CN X)\nO$_2$ more than CO$_2$; pH"),
            (1.8, 2.6, "Baroreceptors\ncarotid sinus (CN IX),\naortic arch (CN X)"),
            (6.0, 3.25, "Lung receptors (vagus to NTS)\nirritant, stretch,\nC fibers, J receptors")]
    for x, y, s in sens:
        box(ax, x, y, 3.3, 1.05, s, "white", C["cw"], fs_=8.8)
    arrow(ax, 6.0, 7.03, 6.0, 6.22, C["purple"])
    arrow(ax, 8.7, 7.3, 10.2, 6.22, C["purple"], rad=-0.25)
    ax.text(9.9, 7.0, "direct, voluntary", fontsize=8.5, color=C["purple"], ha="left")
    arrow(ax, 8.02, 5.7, 8.68, 5.7, C["system"])
    arrow(ax, 10.2, 5.18, 10.2, 3.72, C["muscle"])
    arrow(ax, 10.2, 2.68, 8.12, 1.3, C["lung"], rad=-0.15)
    arrow(ax, 8.68, 3.2, 7.67, 3.25, C["lung"])
    ax.text(8.2, 3.45, "stretch,\nirritants", fontsize=8.2, color=C["lung"], ha="center", va="bottom")
    arrow(ax, 3.88, 1.15, 1.8, 2.06, C["cw"], rad=-0.3)
    arrow(ax, 3.45, 2.6, 3.45, 3.72, C["cw"], style="-", lw=0.0)
    for y in (5.9, 4.25, 2.6):
        arrow(ax, 3.47, y, 3.98, 5.45 if y < 5.8 else 5.75, C["cw"])
    arrow(ax, 6.0, 3.78, 6.0, 5.18, C["cw"])
    ax.text(0.15, 0.25, "The arrow from arterial blood stands for all three blood sensors on the left.",
            fontsize=8.5, color=C["text"])
    fs.save(fig, PART, SLUG, "control-loop.svg")


if __name__ == "__main__":
    fig_centers()
    fig_transections()
    fig_chemo()
    fig_copd()
    fig_cheyne_stokes()
    fig_loop()
