"""Figures for the Respiratory Dynamics II chapter.

Run:  cd site/scripts && MPLCONFIGDIR=$TMPDIR PNG_PREVIEW=<folder> python3 figs_dynamics-2.py
Writes SVGs to ../pulmonary/figures/dynamics-2/.

Airway areas come from Weibel's symmetric airway model, the model the Ventilation lecture uses.
Resistance by generation, Raw against lung volume, the area-transmural pressure curves and the
isovolume effort curves are schematics drawn to the shapes on the Dynamics II slides. The forced
expiration numbers are the lecture's (TLC: Ppl -30; forced: Ppl +60, Palv 90, then Pel 20, Palv 80).
"""
import numpy as np
import figstyle as fs
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle, FancyArrowPatch

plt = fs.plt
C = fs.C
MINUS = fs.MINUS
PART, SLUG = "pulmonary", "dynamics-2"

# Weibel model A: total cross-sectional area (cm^2) by generation 0-23
WEIBEL_AREA = [2.54, 2.33, 2.13, 2.00, 2.48, 3.11, 3.96, 5.10, 6.95, 9.56, 13.4, 19.6, 28.8,
               44.5, 69.4, 113, 180, 300, 534, 944, 1600, 3220, 5880, 11800]


def ticks_minus(ax, axis="y"):
    if axis == "y":
        ax.set_yticklabels([fs.fmt(v) for v in ax.get_yticks()])
    else:
        ax.set_xticklabels([fs.fmt(v) for v in ax.get_xticks()])


# ------------------------------------------------------------ 1. Poiseuille: radius dominates
def fig_poiseuille():
    fig, ax = plt.subplots(figsize=(6.6, 4.4))
    r = np.linspace(0.45, 1.0, 200)
    ax.plot(r * 100, 1 / r ** 4, color=C["system"], lw=2.4)
    fs.grid(ax)
    ax.set_xlabel("Airway radius (% of starting radius)")
    ax.set_ylabel("Resistance (× starting value)")
    ax.set_xlim(45, 102); ax.set_ylim(0, 24)
    for pct in (100, 80, 50):
        y = 1 / (pct / 100) ** 4
        ax.plot([pct], [y], "o", color=C["system"], ms=6, zorder=5)
        if pct == 100:
            ax.text(99, y + 1.0, "starting airway: 1×", fontsize=9.5, color=C["ink"], ha="right")
        else:
            ax.text(pct + 1.2, y + 0.6, f"{pct}% radius: {y:.1f}×", fontsize=9.5, color=C["ink"])
    ax.text(101, 21.5, "R = 8ηl / πr$^4$\nHalving the radius raises\nresistance 16-fold", ha="right", va="top",
            fontsize=10, color=C["ink"])
    fs.save(fig, PART, SLUG, "poiseuille-radius.svg")


# ------------------------------------------------------------ 2. Laminar versus turbulent
def fig_flow_types():
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.3), gridspec_kw=dict(width_ratios=[1, 1.05]))
    ax = axes[0]
    ax.set_xlim(0, 10); ax.set_ylim(-0.4, 7.6); ax.axis("off")
    ax.set_title("A. Velocity across the airway", loc="left")
    for y0, title in ((4.2, "Laminar: smooth layers, fastest in the center"), (0.2, "Turbulent: eddies, a blunt profile")):
        ax.plot([0.5, 9.5], [y0, y0], color=C["ink"], lw=2)
        ax.plot([0.5, 9.5], [y0 + 2.6, y0 + 2.6], color=C["ink"], lw=2)
        ax.text(0.5, y0 + 2.85, title, fontsize=9.5, color=C["ink"])
    ys = np.linspace(4.35, 6.65, 9)
    for y in ys:
        u = 1 - ((y - 5.5) / 1.3) ** 2
        ax.add_patch(FancyArrowPatch((1.5, y), (1.5 + 5.5 * u + 0.05, y), arrowstyle="-|>", mutation_scale=9,
                                     color=C["cw"], lw=1.3))
    yy = np.linspace(4.2, 6.8, 100)
    ax.plot(1.5 + 5.5 * (1 - ((yy - 5.5) / 1.3) ** 2), yy, color=C["cw"], lw=1, ls=(0, (3, 2)))
    rng = np.random.default_rng(3)
    ys = np.linspace(0.35, 2.65, 9)
    for y in ys:
        u = 0.85 * (1 - abs((y - 1.5) / 1.3) ** 6)
        ax.add_patch(FancyArrowPatch((1.5, y), (1.5 + 5.5 * u + 0.05, y), arrowstyle="-|>", mutation_scale=9,
                                     color=C["system"], lw=1.3))
    for cx, cy in ((7.8, 1.0), (8.6, 2.0), (8.2, 1.5)):
        th = np.linspace(0, 1.7 * np.pi, 60)
        rr = np.linspace(0.05, 0.38, 60)
        ax.plot(cx + rr * np.cos(th), cy + rr * np.sin(th), color=C["system"], lw=1.2)
    ax = axes[1]
    dp = np.linspace(0, 4, 400)
    lam = dp / 2
    real = np.where(dp <= 1, dp / 2, 0.5 * np.sqrt(np.maximum(dp, 1e-9)))
    ax.plot(dp[dp >= 1], lam[dp >= 1], color=C["cw"], lw=1.6, ls=(0, (5, 3)))
    ax.plot(dp, real, color=C["system"], lw=2.6)
    ax.plot(dp[dp <= 1], lam[dp <= 1], color=C["cw"], lw=2.6)
    ax.plot([1], [0.5], "o", color=C["ink"], ms=5, zorder=5)
    fs.grid(ax)
    ax.set_xlim(0, 4.1); ax.set_ylim(0, 2.2)
    ax.set_xlabel("Driving pressure, ΔP (cm H$_2$O)")
    ax.set_ylabel("Flow (L/s)")
    ax.set_title("B. Pressure needed for flow", loc="left")
    ax.text(2.55, 1.5, r"if flow stayed laminar: flow $\propto$ ΔP", color=C["cw"], fontsize=9.5, rotation=0)
    ax.text(2.3, 0.72, r"turbulent: flow $\propto \sqrt{\Delta P}$", color=C["system"], fontsize=9.5)
    ax.text(0.15, 0.62, "laminar", color=C["cw"], fontsize=9.5)
    ax.annotate("flow becomes\nturbulent", xy=(1, 0.5), xytext=(1.2, 0.18), fontsize=8.8, color=C["ink"],
                arrowprops=dict(arrowstyle="-", color=C["ink"], lw=0.8))
    ax.text(0.1, 2.12, "Once flow is turbulent, the same rise in flow\nneeds a larger rise in pressure", fontsize=8.8,
            color=C["ink"], va="top")
    fig.subplots_adjust(wspace=0.18)
    fs.save(fig, PART, SLUG, "flow-types.svg")


# ------------------------------------------------------------ 3. Cross-sectional area and velocity
def fig_area_velocity():
    g = np.arange(24)
    A = np.array(WEIBEL_AREA)
    v = 500.0 / A     # cm/s at a flow of 0.5 L/s
    fig, ax = plt.subplots(figsize=(6.6, 4.3))
    ax.semilogy(g, v, color=C["cw"], lw=2.4, marker="o", ms=3.5)
    ax.set_xlabel("Airway generation (0 = trachea)")
    ax.set_ylabel("Average gas velocity (cm/s)")
    fs.grid(ax)
    ax.axvspan(16.5, 23.5, color=C["shade"], zorder=0)
    ax.text(17, 120, "respiratory\nzone", fontsize=9, color=C["text"])
    ax.text(9.5, 60, "Flow 0.5 L/s: the same total flow\npasses every generation", fontsize=8.8, color=C["ink"])
    ax.annotate("highest in generations 2 to 4,\nwhere total area dips slightly", xy=(3, v[3]), xytext=(4.5, 0.6),
                fontsize=8.8, color=C["ink"], arrowprops=dict(arrowstyle="-", color=C["ink"], lw=0.8))
    ax.set_xlim(-0.5, 23.5)
    fs.save(fig, PART, SLUG, "area-velocity.svg")


# ------------------------------------------------------------ 4. Where resistance lies; lung volume
def fig_resistance():
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.3))
    ax = axes[0]
    g = np.linspace(0, 20, 400)
    r = 0.075 * np.exp(-0.5 * ((g - 3.5) / 2.0) ** 2) + 0.012 * np.exp(-g / 3.0) * (g < 3.5) + 0.003 * np.exp(-(g - 8) / 2.5) * (g > 8)
    r = np.where(g < 3.5, 0.075 * np.exp(-0.5 * ((g - 3.5) / 2.0) ** 2), 0.075 * np.exp(-(np.abs(g - 3.5) / 4.2) ** 1.6))
    r += np.where(g < 3.5, 0.0, 0.0)
    r = np.maximum(r, 0.0) + 0.002
    ax.plot(g, r, color=C["system"], lw=2.4)
    fs.grid(ax)
    ax.set_xlim(0, 20); ax.set_ylim(0, 0.09)
    ax.set_xlabel("Airway generation (0 = trachea)")
    ax.set_ylabel("Resistance of each generation\n(cm H$_2$O/L/s)")
    ax.set_title("A. Most resistance sits in medium bronchi", loc="left")
    ax.axvspan(16.5, 20, color=C["shade"], zorder=0)
    ax.text(17, 0.08, "respiratory\nzone", fontsize=9, color=C["text"])
    ax.text(9.5, 0.055, "Small airways: each is narrow,\nbut so many lie in parallel that\ntheir combined resistance is small",
            fontsize=8.8, color=C["ink"])
    ax = axes[1]
    vc = np.linspace(2, 100, 300)
    raw = 0.6 + 2.4 * (20 / (vc + 14))
    ax.plot(vc, raw, color=C["cw"], lw=2.4)
    fs.grid(ax)
    ax.set_xlim(0, 100); ax.set_ylim(0, 4)
    ax.set_xlabel("Lung volume (% of vital capacity above RV)")
    ax.set_ylabel("Airway resistance (cm H$_2$O/L/s)")
    ax.set_title("B. Resistance falls as the lung fills", loc="left")
    frc = 33
    ax.plot([frc], [0.6 + 2.4 * 20 / (frc + 14)], "o", color=C["cw"], ms=6)
    ax.text(frc + 2, 0.6 + 2.4 * 20 / (frc + 14) + 0.15, "FRC: normal R$_{aw}$ < 2", fontsize=9, color=C["cw"])
    ax.text(97, 3.6, "Lung tissue tethers the airways\nopen, more so at high volume", ha="right", va="top",
            fontsize=8.8, color=C["ink"])
    ax.text(2, 0.25, "RV", fontsize=9, color=C["text"]); ax.text(93, 0.25, "TLC", fontsize=9, color=C["text"])
    fig.subplots_adjust(wspace=0.32)
    fs.save(fig, PART, SLUG, "resistance-volume.svg")


# ------------------------------------------------------------ 5. Forced expiration: transmural pressure
def lung_airway(ax, title, ppl, palv, labels, note, pel, narrow=None):
    ax.set_xlim(0, 10); ax.set_ylim(-1.2, 12.2); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(title, loc="left", fontsize=10.5)
    ax.add_patch(FancyBboxPatch((0.6, 0.5), 8.8, 6.6, boxstyle="round,pad=0.1,rounding_size=0.6",
                                fc="#f3f7f9", ec=C["cw"], lw=2.5))
    ax.add_patch(Circle((5, 3.3), 1.9, fc="white", ec=C["lung"], lw=2.3, zorder=2))
    ys = np.linspace(5.0, 11.5, 200)
    half = np.full_like(ys, 0.45)
    if narrow:
        y0, y1 = narrow
        mid, w = (y0 + y1) / 2, (y1 - y0) / 2
        half = np.where(abs(ys - mid) < w, 0.45 - 0.2 * np.cos(np.pi / 2 * (ys - mid) / w) ** 2, half)
    ax.fill_betweenx(ys, 5 - half, 5 + half, color="white", zorder=3)
    ax.plot(5 - half, ys, color=C["lung"], lw=1.8, zorder=4)
    ax.plot(5 + half, ys, color=C["lung"], lw=1.8, zorder=4)
    for yv, pv in labels:
        col = C["system"] if (yv < 7.1 and pv < ppl) else C["ink"]
        ax.text(5.75, yv, fs.fmt(pv), fontsize=8.8, color=col, va="center", zorder=5)
    ax.text(5, 3.7, "P$_{alv}$ = " + fs.fmt(palv), ha="center", fontsize=10.5, color=C["system"], fontweight="bold", zorder=5)
    ax.text(5, 2.8, "P$_{el}$ = " + fs.fmt(pel), ha="center", fontsize=9.5, color=C["lung"], zorder=5)
    ax.text(1.0, 0.9, "P$_{pl}$ = " + ("+" if ppl > 0 else "") + fs.fmt(ppl), fontsize=10.5, color=C["cw"], fontweight="bold")
    ax.text(0.3, -0.25, note, fontsize=8.6, color=C["text"], va="top")
    ax.text(5, 11.9, "mouth 0", ha="center", fontsize=8.8, color=C["text"])


def fig_forced():
    fig, axes = plt.subplots(1, 3, figsize=(11.4, 5.6))
    lung_airway(axes[0], "A. At TLC, no flow", -30, 0, [(6.0, 0), (9.5, 0)],
                "P$_{alv}$ = P$_{pl}$ + P$_{el}$ = " + MINUS + "30 + 30 = 0\nAirway P$_{tm}$ = 0 " + MINUS + " (" + MINUS + "30) = +30", 30)
    lung_airway(axes[1], "B. Forced expiration begins", 60, 90, [(5.5, 80), (6.15, 70), (6.8, 60), (8.6, 40), (10.2, 20)],
                "P$_{alv}$ = +60 + 30 = 90\nAirway pressure stays at or above +60\ninside the chest: P$_{tm}$ not negative", 30)
    lung_airway(axes[2], "C. Later, at a lower volume", 60, 80, [(5.5, 70), (6.15, 60), (6.8, 50), (8.6, 30), (10.2, 15)],
                "P$_{alv}$ = +60 + 20 = 80\nAirway pressure falls below +60\ninside the chest: P$_{tm}$ < 0, the airway narrows", 20,
                narrow=(6.35, 7.25))
    for ax in axes[1:]:
        for yv in (2.0, 4.5):
            ax.add_patch(FancyArrowPatch((-0.3, yv), (0.75, yv), arrowstyle="-|>", mutation_scale=14, color=C["cw"], lw=2, clip_on=False))
            ax.add_patch(FancyArrowPatch((10.3, yv), (9.25, yv), arrowstyle="-|>", mutation_scale=14, color=C["cw"], lw=2, clip_on=False))
    fig.subplots_adjust(wspace=0.08)
    fig.text(0.5, 0.0, "Pressures in cm H$_2$O. Numbers beside the airway are the pressure inside it, falling from the alveolus to the mouth. "
             "Red: below pleural pressure. Arrows: expiratory muscles squeezing the chest.", ha="center", fontsize=8.6, color=C["text"])
    fs.save(fig, PART, SLUG, "forced-expiration.svg")


# ------------------------------------------------------------ 6. Airway area and transmural pressure
def fig_ptm_area():
    fig, ax = plt.subplots(figsize=(6.4, 4.3))
    p = np.linspace(-20, 20, 300)
    trachea = 100 - 12 / (1 + np.exp(p / 4))
    bron = 100 / (1 + np.exp(-(p + 2) / 3.2))
    bron = bron / bron.max() * 100
    ax.plot(p, trachea, color=C["ink"], lw=2.4)
    ax.plot(p, bron, color=C["lung"], lw=2.4)
    ax.axvline(0, color=C["axis"], lw=1)
    fs.grid(ax)
    ax.set_xlim(-20, 20); ax.set_ylim(0, 108)
    ax.set_xticks([-20, -10, 0, 10, 20]); ticks_minus(ax, "x")
    ax.set_xlabel("Airway transmural pressure, P$_{tm}$ = P$_{aw}$ " + MINUS + " P$_{pl}$ (cm H$_2$O)")
    ax.set_ylabel("Luminal area (% of maximum)")
    ax.text(-19, 80, "Trachea: cartilage keeps it open", fontsize=9.5, color=C["ink"])
    ax.text(1.5, 12, "Bronchi and bronchioles:\nnarrow and collapse\nwhen P$_{tm}$ < 0", fontsize=9.5, color=C["lung"])
    fs.save(fig, PART, SLUG, "ptm-area.svg")


# ------------------------------------------------------------ 7. Effort independence
def fev_curve(vc_pct, peak_scale=1.0):
    """Maximal expiratory flow envelope (L/s) against volume (% VC, 100 = TLC)."""
    x = vc_pct / 100
    return 8.0 * x * peak_scale


def fig_effort():
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.4))
    ax = axes[0]
    import statics_model as sm
    pe = np.linspace(-30, 60, 500)
    for vc, col, vmax in ((90, C["system"], None), (60, C["lung"], 5.0), (30, C["cw"], 2.5), (10, C["green"], 0.9)):
        pel = sm.lung_pressure(1.5 + 4.5 * vc / 100)
        drive = np.maximum(pe + pel, 0)           # Palv = Ppl + Pel
        if vmax is None:
            f = 5.0 * (1 - np.exp(-drive / 10)) + 0.035 * drive   # near TLC: keeps rising
        else:
            f = vmax * (1 - np.exp(-drive / (1.2 + vc / 12)))
        on = drive > 0
        ax.plot(pe[on], f[on], color=col, lw=2.2)
        ax.plot([-pel], [0], "o", color=col, ms=5, zorder=5, clip_on=False)
        ax.text(61, f[-1], f"{vc}% VC", fontsize=9, color=col, va="center")
    fs.grid(ax)
    ax.axvline(0, color=C["axis"], lw=1)
    ax.set_xlim(-30, 72); ax.set_ylim(0, 8.4)
    ax.set_xticks([-30, -15, 0, 15, 30, 45, 60]); ticks_minus(ax, "x")
    ax.set_xlabel("Pleural pressure: expiratory effort (cm H$_2$O)")
    ax.set_ylabel("Expiratory flow (L/s)")
    ax.set_title("A. Effort and flow at fixed lung volumes", loc="left")
    ax.text(9, 4.35, "Flow starts where P$_{alv}$ = P$_{pl}$ + P$_{el}$ > 0 (dots).\nAt 60% VC and below, flow levels off;\nnear TLC it keeps rising with effort.",
            fontsize=8.6, color=C["ink"], va="top")
    ax = axes[1]
    x = np.linspace(0, 100, 500)        # % of VC exhaled
    for tau, col, lab in ((2.5, C["system"], "maximal effort"), (9, C["lung"], "less effort"), (18, C["cw"], "gentle effort")):
        f = 8.6 * (1 - x / 100) * (1 - np.exp(-x / tau))
        ax.plot(100 - x, f, color=col, lw=2.2, label=lab)
    fs.grid(ax)
    ax.set_xlim(100, 0); ax.set_ylim(0, 8.4)
    ax.set_xticks([100, 75, 50, 25, 0]); ax.set_xticklabels(["100\n(TLC)", "75", "50", "25", "0\n(RV)"])
    ax.set_xlabel("Volume (% of vital capacity)")
    ax.set_ylabel("Expiratory flow (L/s)")
    ax.set_title("B. Different peaks, the same late curve", loc="left")
    ax.legend(loc="upper right", fontsize=8.8)
    ax.text(48, 5.2, "Later in the breath every effort\nfollows the same line: flow is\nlimited, not set by effort",
            fontsize=8.8, color=C["ink"])
    fig.subplots_adjust(wspace=0.25)
    fs.save(fig, PART, SLUG, "effort-independence.svg")


# ------------------------------------------------------------ 8. Spirometry patterns
def loop(vol_tlc, fvc, peak, scoop=0.0, cap=None, insp_peak=None, n=300):
    """Flow-volume loop on absolute volume. Returns (V_exp, F_exp, V_insp, F_insp)."""
    rv = vol_tlc - fvc
    u = np.linspace(0, 1, n)          # fraction of FVC exhaled
    rise = np.clip(u / 0.08, 0, 1)
    fall = (1 - u) ** (1 + 2.5 * scoop) / (1 - 0.08) ** (1 + 2.5 * scoop)
    F = peak * np.minimum(rise, np.minimum(1, fall))
    if cap:
        F = np.minimum(F, cap)
    V = vol_tlc - u * fvc
    ip = insp_peak if insp_peak else 0.75 * peak
    Fi = -ip * np.sin(np.pi * u)
    if cap:
        Fi = np.maximum(Fi, -cap)
    Vi = rv + u * fvc
    return V, F, Vi, Fi


def volume_time(fvc, fev1_frac, t):
    k = -np.log(1 - fev1_frac)
    return fvc * (1 - np.exp(-k * t))


def fig_spirometry():
    fig, axes = plt.subplots(1, 3, figsize=(12.6, 4.6), gridspec_kw=dict(width_ratios=[1.25, 1.0, 1.0]))
    ax = axes[0]
    cases = [("Normal", 6.0, 4.5, 8.0, 0.0, None, C["ink"], "-"),
             ("Obstructive", 7.2, 3.6, 4.2, 1.0, None, C["system"], "-"),
             ("Restrictive", 4.2, 2.8, 6.6, -0.25, None, C["cw"], "-")]
    for lab, tlc, fvc, pk, sc, cap, col, ls in cases:
        V, F, Vi, Fi = loop(tlc, fvc, pk, sc, cap)
        ax.plot(V, F, color=col, lw=2.2, ls=ls)
        ax.plot(Vi, Fi, color=col, lw=1.6, ls=ls)
    ax.axhline(0, color=C["axis"], lw=1)
    ax.set_xlim(7.6, 1.0)
    ax.set_ylim(-7.2, 9)
    yt = [-6, -3, 0, 3, 6, 9]; ax.set_yticks(yt); ax.set_yticklabels([fs.fmt(v) for v in yt])
    fs.grid(ax)
    ax.set_xlabel("Lung volume (L), TLC on the left")
    ax.set_ylabel("Flow (L/s): expiration up, inspiration down")
    ax.set_title("A. Flow-volume loops", loc="left")
    ax.text(5.65, 8.3, "Normal", color=C["ink"], fontsize=9.5, fontweight="bold")
    ax.text(7.5, 4.9, "Obstructive:\nscooped, starts\nat a high volume", color=C["system"], fontsize=9)
    ax.text(3.05, 6.4, "Restrictive:\nsmall, steep,\nshifted to low\nvolume", color=C["cw"], fontsize=9)
    ax = axes[1]
    V, F, Vi, Fi = loop(6.0, 4.5, 8.0)
    ax.plot(V, F, color=C["ink"], lw=1.3, ls=(0, (3, 2)))
    ax.plot(Vi, Fi, color=C["ink"], lw=1.0, ls=(0, (3, 2)))
    V, F, Vi, Fi = loop(6.0, 4.5, 8.0, cap=3.2)
    ax.plot(V, F, color=C["green"], lw=2.3)
    ax.plot(Vi, Fi, color=C["green"], lw=1.8)
    ax.axhline(0, color=C["axis"], lw=1)
    ax.set_xlim(6.6, 1.0); ax.set_ylim(-7.2, 9)
    ax.set_yticks(yt); ax.set_yticklabels([fs.fmt(v) for v in yt])
    fs.grid(ax)
    ax.set_xlabel("Lung volume (L)")
    ax.set_title("B. Fixed narrowing of the trachea", loc="left")
    ax.text(3.9, 8.4, "Expiratory flow capped\nat high volumes;\nthe late part is normal", color=C["green"], fontsize=9, va="top")
    ax.text(6.4, -4.6, "Inspiration\ncapped too", color=C["green"], fontsize=9)
    ax.text(2.6, -6.6, "dashed: normal", color=C["ink"], fontsize=8.6)
    ax = axes[2]
    t = np.linspace(0, 6, 300)
    for lab, fvc, r, col in (("Normal", 4.5, 0.80, C["ink"]), ("Obstructive", 3.6, 0.45, C["system"]),
                             ("Restrictive", 2.8, 0.90, C["cw"])):
        y = volume_time(fvc, r, t)
        y = y / y[-1] * fvc
        ax.plot(t, y, color=col, lw=2.2)
        f1 = np.interp(1, t, y)
        ax.plot([1], [f1], "o", color=col, ms=5)
        ax.text(6.1, fvc, f"{lab}\nFEV$_1$/FVC {100 * f1 / fvc:.0f}%", fontsize=8.6, color=col, va="center")
    ax.axvline(1, color=C["axis"], lw=1, ls=(0, (3, 2)))
    ax.text(1.05, 0.2, "1 s", fontsize=9, color=C["text"])
    fs.grid(ax)
    ax.set_xlim(0, 8.6); ax.set_ylim(0, 5.2)
    ax.set_xticks([0, 1, 2, 3, 4, 5, 6])
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Volume exhaled (L)")
    ax.set_title("C. Volume-time curves", loc="left")
    fig.subplots_adjust(wspace=0.22)
    fs.save(fig, PART, SLUG, "spirometry-patterns.svg")


if __name__ == "__main__":
    fig_poiseuille()
    fig_flow_types()
    fig_area_velocity()
    fig_resistance()
    fig_forced()
    fig_ptm_area()
    fig_effort()
    fig_spirometry()
