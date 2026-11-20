"""Figures for EKG I: Ionic Basis (cardiovascular/ecg-ionic-basis.qmd).

Run:  cd site/scripts && MPLCONFIGDIR=$TMPDIR PNG_PREVIEW=<folder> python3 figs_ecg-ionic-basis.py

Action potentials and currents are schematic shapes built from smooth pieces, drawn to match
the shapes, phases and voltages the course uses. They are not the output of an ionic model,
and current traces are not to scale (inward current is drawn downward, as on the slides).
"""
import numpy as np
import figstyle as fs
from figstyle import C, plt, MINUS

PART, SLUG = "cardiovascular", "ecg-ionic-basis"

# colors for currents
CUR = dict(Na=C["arterial"], to=C["gold"], CaL=C["ventricular"], Kr=C["venous"], Ks=C["green"],
           K1=C["purple"], f=C["green"], CaT=C["gold"], K=C["venous"])


def sig(x):
    return 1.0 / (1.0 + np.exp(-x))


# ------------------------------------------------------------------ AP shapes
def fast_ap(t, rest=-90.0, peak=25.0, plateau=5.0, apd=0.27, up=0.0015, t0=0.0):
    """Fast-response (ventricular) AP. t in s. Returns mV."""
    v = np.full_like(t, rest, dtype=float)
    s = t - t0
    on = s >= 0
    x = s[on]
    rise = np.clip(x / up, 0, 1)
    rise = 0.5 - 0.5 * np.cos(np.pi * rise)                        # phase 0
    notch = (peak - plateau) * np.exp(-np.maximum(x - up, 0) / 0.004)  # phase 1
    drift = -12.0 * np.clip((x - 0.01) / (apd - 0.01), 0, 1) ** 1.6   # slow decline in phase 2
    top = plateau + notch + drift
    repol = sig((x - apd) / 0.018)                                   # phase 3
    vv = rest + rise * (top - rest)
    vv = vv - repol * (vv - rest)
    v[on] = vv
    return v


def plot_phase_labels(ax, pts):
    for txt, (x, y) in pts.items():
        ax.text(x, y, txt, fontsize=12, fontweight="bold", color=C["ink"], ha="center", va="center")


def ap_axes(ax, ylim=(-100, 40)):
    ax.set_ylim(*ylim)
    ax.set_ylabel("Membrane potential (mV)")
    ax.set_yticks([-90, -60, -30, 0, 30])
    ax.set_yticklabels([fs.fmt(v) for v in [-90, -60, -30, 0, 30]])
    fs.grid(ax)


# ------------------------------------------------------------------ 1. fast AP with currents
def fig_fast_ap_currents():
    t = np.linspace(-0.03, 0.40, 4000)
    v = fast_ap(t)
    ms = t * 1000
    fig, axes = plt.subplots(7, 1, figsize=(7.6, 8.6), sharex=True,
                             gridspec_kw=dict(height_ratios=[3.2, 1, 1, 1, 1, 1, 1], hspace=0.12))
    ax = axes[0]
    ax.plot(ms, v, color=C["ventricular"], lw=2.2)
    ap_axes(ax)
    ax.axhline(-65, color=C["axis"], lw=0.8, ls=(0, (3, 3)))
    ax.text(395, -61, "threshold, about " + MINUS + "65 mV", fontsize=8.5, color=C["text"], ha="right")
    plot_phase_labels(ax, {"0": (-9, -20), "1": (12, 31), "2": (130, 13), "3": (300, -40), "4": (-20, -82), "4 ": (370, -82)})
    ax.set_title("Fast-response action potential (ventricular myocyte)")

    def gate(x, a, b, w):
        return sig((x - a) / w) * (1 - sig((x - b) / w))

    s = t
    pos = np.maximum(s, 0)
    I = {}
    I["Na"] = -(np.exp(-pos / 0.0035) * (s >= 0)) * sig(s / 0.0006)
    I["to"] = 0.6 * (s >= 0) * (1 - np.exp(-pos / 0.0015)) * np.exp(-pos / 0.008)
    I["CaL"] = -0.55 * (s >= 0) * (1 - np.exp(-pos / 0.002)) * (0.45 + 0.55 * np.exp(-pos / 0.03)) * (1 - sig((s - 0.26) / 0.015))
    I["Ks"] = 0.45 * (s >= 0) * (1 - np.exp(-pos / 0.09)) * (1 - sig((s - 0.285) / 0.012))
    I["Kr"] = 0.35 * (s >= 0) * (1 - np.exp(-pos / 0.05)) * (1 + 1.3 * np.exp(-((s - 0.27) / 0.025) ** 2)) * (1 - sig((s - 0.30) / 0.01))
    vr = fast_ap(t)
    I["K1"] = 0.08 * (1 - sig(s / 0.002)) + 0.9 * np.exp(-((s - 0.300) / 0.014) ** 2) + 0.08 * sig((s - 0.31) / 0.006)
    rows = [("Na", "I$_{Na}$", "Na$^+$ in"), ("to", "I$_{to}$", "K$^+$ out"), ("CaL", "I$_{Ca,L}$", "Ca$^{2+}$ in"),
            ("Kr", "I$_{Kr}$", "K$^+$ out"), ("Ks", "I$_{Ks}$", "K$^+$ out"), ("K1", "I$_{K1}$", "K$^+$ out")]
    for axi, (k, lab, ion) in zip(axes[1:], rows):
        y = I[k]
        axi.fill_between(ms, 0, y, color=CUR[k], alpha=0.85, lw=0)
        axi.axhline(0, color=C["axis"], lw=0.8)
        axi.set_ylim(-1.05, 1.05)
        axi.set_yticks([])
        axi.spines["left"].set_visible(False)
        axi.text(-0.01, 0.5, lab, transform=axi.transAxes, ha="right", va="center", fontsize=11, color=CUR[k])
        axi.text(1.0, 0.5, ion, transform=axi.transAxes, ha="left", va="center", fontsize=9, color=C["text"])
        if axi is not axes[-1]:
            axi.spines["bottom"].set_visible(False)
            axi.tick_params(axis="x", length=0)
    axes[1].text(0.03, 0.15, "currents not to scale; inward is down", transform=axes[1].transAxes, ha="left", va="center",
                 fontsize=8.5, color=C["text"], style="italic")
    axes[-1].set_xlabel("Time (ms)")
    axes[-1].set_xlim(-30, 400)
    fs.save(fig, PART, SLUG, "fast-ap-currents.svg")


# ------------------------------------------------------------------ 2. skeletal vs cardiac
def twitch(t, t0, tp, tr, amp=1.0):
    x = np.maximum(t - t0, 0)
    return amp * (x / tp) * np.exp(1 - x / tp) * (t >= t0) if tr is None else amp * (x / tp) ** 2 * np.exp(2 * (1 - x / tp))


def fig_skeletal_vs_cardiac():
    fig, axes = plt.subplots(2, 2, figsize=(9.2, 5.6), sharex="col",
                             gridspec_kw=dict(height_ratios=[1.3, 1], hspace=0.12, wspace=0.28))
    t = np.linspace(-0.02, 0.5, 6000)
    ms = t * 1000
    # skeletal: AP of 4 ms, stimuli every 25 ms from 0 to 200 ms -> fused tetanus
    stims = np.arange(0, 0.201, 0.025)
    vs = np.full_like(t, -85.0)
    for s0 in stims:
        x = t - s0
        bump = 115 * np.exp(-((x - 0.0012) / 0.0007) ** 2) * (x < 0.0012) + 115 * np.exp(-(x - 0.0012) / 0.0011) * (x >= 0.0012)
        vs = vs + bump * (x > 0)
    vs = np.minimum(vs, 30)
    ax = axes[0, 0]
    ax.plot(ms, vs, color=C["arterial"], lw=1.3)
    ap_axes(ax)
    ax.set_title("A  Skeletal muscle")
    ax.text(215, 10, "Each action potential\nlasts about 5 ms and\nends before the next", fontsize=8.5, color=C["text"])
    # force: twitch impulse response, summed with tetanic saturation
    def tw(x):
        x = np.maximum(x, 0)
        return (x / 0.04) * np.exp(1 - x / 0.04)
    f1 = tw(t)
    ftet = np.zeros_like(t)
    for s0 in stims:
        ftet += 0.35 * tw(t - s0)
    ftet = 1 - np.exp(-1.2 * ftet)
    ftet = ftet / ftet.max() * 3.2
    ax = axes[1, 0]
    ax.plot(ms, f1, color=C["gray"], lw=1.5, ls=(0, (4, 2)))
    ax.plot(ms, ftet, color=C["arterial"], lw=2)
    ax.text(75, 0.75, "single twitch", fontsize=8.5, color=C["gray"])
    ax.text(225, 3.35, "stimuli every 25 ms:\nforces sum (tetanus)", fontsize=8.5, color=C["arterial"])
    ax.set_ylabel("Force (relative)")
    ax.set_xlabel("Time (ms)")
    ax.set_ylim(0, 4.2)
    ax.set_yticks([0, 1, 2, 3])
    fs.grid(ax)
    ax.set_xlim(-20, 500)
    # cardiac: one AP of ~270 ms, contraction lags; a stimulus at 150 ms does nothing
    vc = fast_ap(t)
    late = t > 0.1
    arp = 1000 * t[late][np.argmax(vc[late] < -50)]   # absolute refractory period ends near -50 mV
    rrp = 1000 * t[late][np.argmax(vc[late] < -86)]   # relative refractory period ends near rest
    ax = axes[0, 1]
    ax.axvspan(0, arp, color=C["highlight"], zorder=0)
    ax.axvspan(arp, rrp, color=C["cool"], zorder=0)
    ax.text(arp / 2, -97, "absolute refractory period", fontsize=8.5, color=C["ventricular"], ha="center", va="bottom")
    ax.text(rrp + 4, -97, "relative", fontsize=8.5, color=C["venous"], ha="left", va="bottom")
    ax.plot(ms, vc, color=C["ventricular"], lw=2)
    ap_axes(ax)
    ax.set_title("B  Cardiac muscle")
    ax.annotate("extra stimulus:\nno response", xy=(150, 3), xytext=(330, 22), fontsize=8.5, color=C["text"],
                arrowprops=dict(arrowstyle="->", color=C["text"], lw=0.9))
    ax = axes[1, 1]
    x = np.maximum(t - 0.02, 0)
    fc = (x / 0.16) ** 2 * np.exp(2 * (1 - x / 0.16)) * (t > 0.02)
    ax.axvspan(0, arp, color=C["highlight"], zorder=0)
    ax.axvspan(arp, rrp, color=C["cool"], zorder=0)
    ax.plot(ms, fc, color=C["ventricular"], lw=2, label="contraction")
    ax.set_ylim(0, 4.2)
    ax.set_yticks([0, 1, 2, 3])
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("Force (relative)")
    ax.text(335, 1.6, "The rise and peak of\nthe contraction happen\nwhile the cell is refractory,\nso twitches cannot fuse", fontsize=8.5,
            color=C["text"])
    fs.grid(ax)
    ax.set_xlim(-20, 500)
    fs.save(fig, PART, SLUG, "skeletal-vs-cardiac.svg")


# ------------------------------------------------------------------ 3. slow-response AP and currents
def slow_ap(t, cycle=0.8, mdp=-60.0, thr=-40.0, peak=10.0, slope_scale=1.0, n=3):
    """SA node AP train. Phase 4 rises from mdp toward threshold, then phase 0 and 3."""
    v = np.full_like(t, mdp, dtype=float)
    upd, apd = 0.04, 0.17  # phase 0 duration and total AP duration from takeoff
    for k in range(-1, n + 1):
        t0 = k * cycle
        x = t - t0
        # phase 4 from end of previous AP (x in [0, cycle - apd])
        d4 = cycle - apd
        m = (x >= 0) & (x < d4)
        u = x[m] / d4
        v[m] = mdp + (thr - mdp) * (0.75 * u + 0.25 * u ** 3)
        m = (x >= d4) & (x < cycle)
        w = (x[m] - d4) / apd
        up = 0.5 - 0.5 * np.cos(np.pi * np.clip(w / (upd / apd), 0, 1))
        dn = np.clip((w - upd / apd) / (1 - upd / apd), 0, 1)
        dn = 0.5 - 0.5 * np.cos(np.pi * dn)
        v[m] = thr + up * (peak - thr) - dn * (peak - mdp)
    return v


def fig_slow_ap_currents():
    cycle = 0.8
    t = np.linspace(0, 2.0, 5000)
    v = slow_ap(t, cycle=cycle)
    ms = t * 1000
    fig, axes = plt.subplots(5, 1, figsize=(7.6, 6.9), sharex=True,
                             gridspec_kw=dict(height_ratios=[3, 1, 1, 1, 1], hspace=0.12))
    ax = axes[0]
    ax.plot(ms, v, color=C["atrial"], lw=2.2)
    ax.set_ylim(-75, 25)
    ax.set_yticks([-60, -40, -20, 0, 20])
    ax.set_yticklabels([fs.fmt(x) for x in [-60, -40, -20, 0, 20]])
    ax.set_ylabel("Membrane potential (mV)")
    fs.grid(ax)
    ax.axhline(-40, color=C["axis"], lw=0.8, ls=(0, (3, 3)))
    ax.text(10, -37.5, "threshold, about " + MINUS + "40 mV", fontsize=8.5, color=C["text"])
    d4 = cycle - 0.17
    plot_phase_labels(ax, {"4": (d4 * 1000 / 2 + 800, -56), "0": (d4 * 1000 + 800 - 15, -8), "3": (d4 * 1000 + 800 + 125, -8)})
    ax.text(1240, -68, "no stable resting potential", fontsize=8.5, color=C["text"], ha="center")
    ax.set_title("Slow-response action potential (SA node cell)")

    # currents, per cycle
    If = np.zeros_like(t); IT = np.zeros_like(t); IL = np.zeros_like(t); IK = np.zeros_like(t)
    for k in range(-2, 4):
        x = t - k * cycle   # x=0: start of phase 4 (maximum diastolic potential)
        p = x >= 0
        xx = np.maximum(x, 0)
        If += p * -0.8 * (1 - np.exp(-xx / 0.05)) * np.exp(-xx / 0.45) * (1 - sig((x - d4 - 0.01) / 0.015))
        IT += -0.6 * np.exp(-((x - (d4 - 0.06)) / 0.05) ** 2)
        IL += -1.0 * np.exp(-((x - (d4 + 0.035)) / 0.035) ** 2) - 0.25 * np.exp(-((x - (d4 - 0.03)) / 0.04) ** 2)
        y = x - (d4 + 0.10)
        IK += 0.8 * sig((x - (d4 + 0.07)) / 0.012) * np.where(y > 0, np.exp(-np.maximum(y, 0) / 0.25), 1.0)
    rows = [(If, "I$_f$", C["green"], "Na$^+$ in (mixed cation)"), (IT, "I$_{Ca,T}$", C["gold"], "Ca$^{2+}$ in"),
            (IL, "I$_{Ca,L}$", C["ventricular"], "Ca$^{2+}$ in"), (IK, "I$_K$", C["venous"], "K$^+$ out")]
    for axi, (y, lab, col, ion) in zip(axes[1:], rows):
        axi.fill_between(ms, 0, y, color=col, alpha=0.85, lw=0)
        axi.axhline(0, color=C["axis"], lw=0.8)
        axi.set_ylim(-1.05, 1.05)
        axi.set_yticks([])
        axi.spines["left"].set_visible(False)
        axi.text(-0.01, 0.5, lab, transform=axi.transAxes, ha="right", va="center", fontsize=11, color=col)
        axi.text(1.0, 0.5, ion, transform=axi.transAxes, ha="left", va="center", fontsize=9, color=C["text"])
        if axi is not axes[-1]:
            axi.spines["bottom"].set_visible(False)
            axi.tick_params(axis="x", length=0)
    axes[1].text(0.01, 0.85, "currents not to scale; inward is down", transform=axes[1].transAxes, ha="left", va="center",
                 fontsize=8.5, color=C["text"], style="italic")
    axes[-1].set_xlabel("Time (ms)")
    axes[-1].set_xlim(0, 2000)
    fs.save(fig, PART, SLUG, "slow-ap-currents.svg")


# ------------------------------------------------------------------ 4. refractory periods
def fig_refractory():
    t = np.linspace(-0.03, 0.98, 9000)
    ms = t * 1000
    base = fast_ap(t)
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    after = t > 0.1
    arp_end = t[after][np.argmax(base[after] < -50)]
    rrp_end = t[after][np.argmax(base[after] < -86)]
    ax.axvspan(0, arp_end * 1000, ymin=0.21, color=C["highlight"], zorder=0)
    ax.axvspan(arp_end * 1000, rrp_end * 1000, ymin=0.21, color=C["cool"], zorder=0)
    ax.text(arp_end * 500, 37, "absolute refractory period", ha="center", fontsize=9, color=C["ventricular"])
    ax.text((arp_end + rrp_end) * 500, 37, "relative", ha="center", fontsize=9, color=C["venous"])
    ax.plot(ms, base, color=C["ventricular"], lw=2.2)
    # response in the relative refractory period: starts from the partly repolarized level,
    # rises more slowly to a lower peak and is shorter
    t1 = arp_end + 0.6 * (rrp_end - arp_end)
    v1 = fast_ap(np.array([t1]))[0]
    m = t >= t1
    xr = t[m] - t1
    up = 0.5 - 0.5 * np.cos(np.pi * np.clip(xr / 0.006, 0, 1))
    top = -8 - 10 * np.clip(xr / 0.12, 0, 1)
    dn = sig((xr - 0.12) / 0.013)
    r = v1 + up * (top - v1)
    r = r - dn * (r + 90)
    keep = t[m] < 0.60
    ax.plot(ms[m][keep], r[keep], color=C["venous"], lw=1.8, ls=(0, (4, 2)))
    # normal AP after recovery
    t2 = 0.62
    full = fast_ap(t, t0=t2)
    m2 = t >= t2
    ax.plot(ms[m2], full[m2], color=C["ventricular"], lw=2.2)
    for ts, col, lab in [(0.12, C["ventricular"], "extra stimulus:\nno response"),
                         (t1, C["venous"], "stronger stimulus:\nsmall, slow AP"),
                         (t2, C["ventricular"], "after recovery:\nnormal AP")]:
        ax.annotate("", xy=(ts * 1000, -101), xytext=(ts * 1000, -116), arrowprops=dict(arrowstyle="->", color=col, lw=1.4))
        ax.text(ts * 1000 + 8, -110, lab, ha="left", va="center", fontsize=8.5, color=C["text"])
    ax.axhline(-50, color=C["axis"], lw=0.7, ls=(0, (2, 3)))
    ax.text(975, -47, MINUS + "50 mV", fontsize=8, color=C["text"], ha="right")
    ap_axes(ax, ylim=(-125, 45))
    ax.set_xlabel("Time (ms)")
    ax.set_xlim(-30, 980)
    fs.save(fig, PART, SLUG, "refractory.svg")


# ------------------------------------------------------------------ 5. autonomic effects on the SA node
def sa_train(t, mdp, thr, d4, peak=10.0, apd=0.17, upd=0.04, n=6, curv=0.25):
    v = np.full_like(t, mdp, dtype=float)
    cycle = d4 + apd
    for k in range(-1, n + 1):
        x = t - k * cycle
        m = (x >= 0) & (x < d4)
        u = x[m] / d4
        v[m] = mdp + (thr - mdp) * ((1 - curv) * u + curv * u ** 3)
        m = (x >= d4) & (x < cycle)
        w = (x[m] - d4)
        up = 0.5 - 0.5 * np.cos(np.pi * np.clip(w / upd, 0, 1))
        dn = np.clip((w - upd) / (apd - upd), 0, 1)
        dn = 0.5 - 0.5 * np.cos(np.pi * dn)
        v[m] = thr + up * (peak - thr) - dn * (peak - mdp)
    return v, cycle


def fig_autonomic_sa():
    t = np.linspace(0, 2.4, 6000)
    ms = t * 1000
    fig, axes = plt.subplots(3, 1, figsize=(8.4, 6.6), sharex=True, gridspec_kw=dict(hspace=0.18))
    runs = [
        (sa_train(t, -60, -42, 0.33), C["arterial"], "-", "Sympathetic (β$_1$): steeper phase 4"),
        (sa_train(t, -60, -40, 0.63), C["ink"], "-", "Control"),
        (sa_train(t, -66, -40, 1.03, curv=0.3), C["venous"], "-", "Parasympathetic (M$_2$): more negative start and flatter phase 4"),
    ]
    for ax, ((v, cyc), col, ls, lab) in zip(axes, runs):
        ax.plot(ms, v, color=col, lw=2.0, ls=ls)
        ax.axhline(-40, color=C["axis"], lw=0.8, ls=(0, (3, 3)))
        ax.axhline(-60, color=C["axis"], lw=0.6, ls=(0, (1, 3)))
        ax.set_ylim(-75, 25)
        ax.set_yticks([-60, -40, -20, 0, 20])
        ax.set_yticklabels([fs.fmt(x) for x in [-60, -40, -20, 0, 20]])
        ax.text(0.0, 1.02, f"{lab}   ({60 / cyc:.0f} beats/min)", transform=ax.transAxes, fontsize=10, color=col,
                fontweight="bold", ha="left", va="bottom")
        fs.grid(ax)
    axes[1].set_ylabel("Membrane potential (mV)")
    axes[1].text(1180, -38, "threshold", fontsize=8.5, color=C["text"], ha="left", va="bottom")
    axes[2].annotate("starts from a more\nnegative potential", xy=(1210, -66), xytext=(1300, -20), fontsize=8.5,
                     color=C["venous"], va="center", arrowprops=dict(arrowstyle="->", color=C["venous"], lw=0.9))
    axes[-1].set_xlabel("Time (ms)")
    axes[-1].set_xlim(0, 2400)
    fs.save(fig, PART, SLUG, "autonomic-sa.svg")


# ------------------------------------------------------------------ 6. upstroke: Na channel block and partial depolarization
def fig_upstroke():
    t = np.linspace(-0.004, 0.03, 3000)
    ms = t * 1000
    fig, ax = plt.subplots(figsize=(7.4, 4.3))
    cases = [
        (fast_ap(t, rest=-90, peak=25, up=0.0015), C["ventricular"], "normal (rest " + MINUS + "90 mV)", "-"),
        (fast_ap(t, rest=-90, peak=12, up=0.0045), C["arterial"], "Na$^+$ channel blocker", (0, (5, 2))),
        (fast_ap(t, rest=-72, peak=5, up=0.0055), C["venous"], "high extracellular K$^+$ (rest " + MINUS + "72 mV)", (0, (2, 1.5))),
    ]
    for v, col, lab, ls in cases:
        ax.plot(ms, v, color=col, lw=2.2, ls=ls, label=lab)
    ax.set_xlim(-4, 30)
    ap_axes(ax)
    ax.set_xlabel("Time (ms)")
    ax.legend(loc="lower right", fontsize=9)
    ax.text(5.5, -40, "slower phase 0\n= slower conduction", fontsize=9, color=C["text"])
    ax.set_title("The first 30 ms of a fast-response action potential")
    fs.save(fig, PART, SLUG, "upstroke.svg")


if __name__ == "__main__":
    fig_fast_ap_currents()
    fig_skeletal_vs_cardiac()
    fig_slow_ap_currents()
    fig_refractory()
    fig_autonomic_sa()
    fig_upstroke()
