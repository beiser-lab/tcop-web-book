"""Figures for the Control of Cardiac Output and Ventricular-Vascular Coupling chapter.

Run:  cd site/scripts && MPLCONFIGDIR=$TMPDIR PNG_PREVIEW=<folder> python3 figs_control-of-co.py
Writes SVGs to ../cardiovascular/figures/control-of-co/.

Models used here are the simple relations the lecture teaches:
  - two-element Windkessel: C dP/dt = Q_in(t) - P/R (pulse pressure in shock)
  - vascular function curve: VR = (Pms - Pra)/RVR, with a plateau where the great veins collapse
  - cardiac function curve: a Frank-Starling curve, CO rising with Pra and flattening
Numbers follow the lecture where it gives them (Pms 7 mm Hg; Pra 2 mm Hg at CO 5 L/min).
"""
import numpy as np
import figstyle as fs
from figstyle import C, plt, MINUS

PART, SLUG = "cardiovascular", "control-of-co"


def save(fig, name):
    fs.save(fig, PART, SLUG, name)


# ---------------------------------------------------------------- shared models
def windkessel(sv=70.0, hr=75.0, R=1.06, Cart=1.0, t_end=6.0, dt=0.0005, tej=0.30):
    """Two-element Windkessel. sv mL, hr /min, R mm Hg*s/mL, Cart mL/mm Hg. Returns t, Qin, P."""
    T = 60.0 / hr
    tej = min(tej, 0.4 * T)
    qpk = sv * np.pi / (2 * tej)
    t = np.arange(0, t_end, dt)
    ph = np.mod(t, T)
    q = np.where(ph < tej, qpk * np.sin(np.pi * ph / tej), 0.0)
    P = np.empty_like(t)
    P[0] = 80.0
    for i in range(1, len(t)):
        P[i] = P[i - 1] + dt * (q[i - 1] - P[i - 1] / R) / Cart
    return t, q, P, T


def last_beats(t, y, T, n=3):
    m = t >= t[-1] - n * T
    return t[m] - t[m][0], y[m]


def softplus(x, w=0.45):
    return w * np.log1p(np.exp(x / w))


def vr_curve(pra, pms=7.0, rvr=1.0):
    """Vascular function curve, L/min. Plateau below Pra of about 0 (veins collapse)."""
    return np.clip((pms - softplus(pra)) / rvr, 0, None)


def cardiac_curve(pra, cmax=12.0, p0=-2.0, k=7.42):
    """Cardiac function curve, L/min. Passes through Pra 2, CO 5 with the defaults."""
    return np.where(pra > p0, cmax * (1 - np.exp(-(pra - p0) / k)), 0.0)


def operating_point(card, vasc, lo=-3, hi=12):
    x = np.linspace(lo, hi, 20001)
    d = card(x) - vasc(x)
    i = np.where(np.diff(np.sign(d)) != 0)[0][0]
    return x[i], card(np.array([x[i]]))[0]


def curve_axes(ax, xmax=12, ymax=13, xmin=-3):
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(0, ymax)
    ax.axvline(0, color=C["axis"], lw=0.8)
    ax.set_xlabel("Right atrial pressure, P$_{ra}$ (mm Hg)")
    ax.set_ylabel("Cardiac output or venous return (L/min)")
    ticks = [v for v in range(-10, xmax + 1, 2) if v >= xmin]
    ax.set_xticks(ticks)
    ax.set_xticklabels([fs.fmt(v) for v in ticks])
    fs.grid(ax)


# ---------------------------------------------------------------- 2. Pulse pressure and compliance
def fig_pulse_pressure():
    fig, ax = plt.subplots(figsize=(6.8, 5.0))
    u = np.linspace(0, 85, 50)             # volume added above the end-diastolic arterial volume, mL
    young_c, old_c = 1.75, 0.85            # mL per mm Hg over the working range
    dbp_y, dbp_o = 80, 75
    sv = 70.0
    ax.plot(u, dbp_y + u / young_c, color=C["arterial"], lw=2.4)
    ax.plot(u, dbp_o + u / old_c, color=C["gray"], lw=2.4)
    ax.text(87, 126, "young,\ncompliant aorta", color=C["arterial"], fontsize=9.5,
            ha="left", va="center")
    ax.text(57, dbp_o + 57 / old_c + 3, "older,\nstiff aorta", color=C["gray"], fontsize=9.5, ha="right")
    for c, d, col in ((young_c, dbp_y, C["arterial"]), (old_c, dbp_o, C["gray"])):
        sbp = d + sv / c
        ax.plot([0, sv], [d, sbp], "o", color=col, ms=5, zorder=5)
        ax.plot([sv, sv], [d, sbp], color=col, lw=0.8, ls=(0, (2, 2)))
        ax.plot([0, sv], [d, d], color=col, lw=0.8, ls=(0, (2, 2)))
    ax.annotate("", xy=(0, 52), xytext=(sv, 52),
                arrowprops=dict(arrowstyle="<->", color=C["ink"], lw=1.2, shrinkA=0, shrinkB=0))
    ax.text(sv / 2, 45, "same stroke volume (70 mL)", ha="center", fontsize=9, color=C["ink"])
    sy = dbp_y + sv / young_c
    so = dbp_o + sv / old_c
    ax.annotate("", xy=(sv + 6, dbp_y), xytext=(sv + 6, sy),
                arrowprops=dict(arrowstyle="<->", color=C["arterial"], lw=1.2, shrinkA=0, shrinkB=0))
    ax.text(sv + 8, (dbp_y + sy) / 2, f"pulse pressure\n{sy - dbp_y:.0f} mm Hg", fontsize=9,
            color=C["arterial"], va="center")
    ax.annotate("", xy=(-6, dbp_o), xytext=(-6, so),
                arrowprops=dict(arrowstyle="<->", color=C["gray"], lw=1.2, shrinkA=0, shrinkB=0))
    ax.text(-8, (dbp_o + so) / 2, f"pulse pressure\n{so - dbp_o:.0f} mm Hg", fontsize=9,
            color=C["gray"], va="center", ha="right")
    ax.set_xlim(-45, 112)
    ax.set_ylim(40, 180)
    ax.set_xticks([0, 35, 70])
    ax.set_xlabel("Volume added to the arteries during ejection (mL)")
    ax.set_ylabel("Arterial pressure (mm Hg)")
    fs.grid(ax)
    save(fig, "pulse-pressure-compliance.svg")


# ---------------------------------------------------------------- 3. Pulse pressure in shock
def fig_shock_pp():
    cases = [
        ("Normal", dict(sv=70, hr=75, R=1.06, Cart=1.0), C["ink"]),
        ("Low-output hypotension\n(hemorrhage)", dict(sv=30, hr=115, R=1.35, Cart=1.0), C["venous"]),
        ("High-output hypotension\n(sepsis)", dict(sv=90, hr=110, R=0.36, Cart=1.0), C["arterial"]),
    ]
    fig, axs = plt.subplots(1, 3, figsize=(9.6, 3.9), sharey=True)
    out = []
    for ax, (lab, kw, col) in zip(axs, cases):
        t, q, P, T = windkessel(**kw, t_end=8.0)
        tt, pp = last_beats(t, P, T, n=2.4 / T)
        ax.plot(tt, pp, color=col, lw=2)
        sbp, dbp = pp.max(), pp.min()
        co = kw["sv"] * kw["hr"] / 1000
        ax.axhline(sbp, color=col, lw=0.7, ls=(0, (2, 2)))
        ax.axhline(dbp, color=col, lw=0.7, ls=(0, (2, 2)))
        xa = tt[-1] * 1.03
        ax.annotate("", xy=(xa, dbp), xytext=(xa, sbp),
                    arrowprops=dict(arrowstyle="<->", color=col, lw=1.2, shrinkA=0, shrinkB=0))
        ax.text(tt[-1] * 0.5, 8, f"{sbp:.0f}/{dbp:.0f} mm Hg\npulse pressure {sbp - dbp:.0f}\nCO {co:.1f} L/min",
                ha="center", fontsize=8.8, color=col)
        ax.set_title(lab, fontsize=10.5)
        ax.set_xlim(0, tt[-1] * 1.12)
        ax.set_ylim(0, 135)
        ax.set_xlabel("Time (s)")
        fs.grid(ax)
        out.append((lab, sbp, dbp, co))
    axs[0].set_ylabel("Aortic pressure (mm Hg)")
    fig.tight_layout()
    save(fig, "shock-pulse-pressure.svg")
    return out


# ---------------------------------------------------------------- 4. Cardiac arrest: equilibration at Pms
def fig_equilibration():
    co = np.array([0, 1, 2, 3, 4, 5])
    pa = np.array([7, 26, 45, 64, 83, 102])
    pv = np.array([7, 6, 5, 4, 3, 2])
    fig, ax = plt.subplots(figsize=(6.8, 4.8))
    ax.plot(co, pa, "o-", color=C["arterial"], lw=2.2, ms=6)
    ax.plot(co, pv, "o-", color=C["venous"], lw=2.2, ms=6)
    ax.text(4.1, 92, "arterial pressure", color=C["arterial"], fontsize=10, ha="right")
    ax.text(3.0, 12, "venous pressure", color=C["venous"], fontsize=10, ha="center")
    ax.annotate("Heart stopped: both pressures\nmeet at P$_{ms}$ = 7 mm Hg", xy=(0, 7), xytext=(0.25, 70),
                fontsize=9.5, color=C["ink"], arrowprops=dict(arrowstyle="-", color=C["ink"], lw=0.8))
    ax.annotate("", xy=(5.25, 7), xytext=(5.25, 102),
                arrowprops=dict(arrowstyle="<->", color=C["arterial"], lw=1.1, shrinkA=0, shrinkB=0))
    ax.text(5.32, 55, "falls\n95", color=C["arterial"], fontsize=9, va="center")
    ax.annotate("", xy=(5.25, 2), xytext=(5.25, 7),
                arrowprops=dict(arrowstyle="<->", color=C["venous"], lw=1.1, shrinkA=0, shrinkB=0))
    ax.text(5.32, 8.5, "rises 5", color=C["venous"], fontsize=9, va="center")
    ax.set_xlim(-0.2, 6.0)
    ax.set_ylim(0, 112)
    ax.set_xlabel("Cardiac output (L/min)")
    ax.set_ylabel("Pressure (mm Hg)")
    fs.grid(ax)
    save(fig, "equilibration-pms.svg")


# ---------------------------------------------------------------- 5. Stressed and unstressed volume
def fig_stressed_volume():
    fig, ax = plt.subplots(figsize=(7.0, 4.9))
    V = np.linspace(0.0, 6.0, 600)
    comp = 0.2  # L per mm Hg

    def p_of(v, vu):
        return np.clip((v - vu) / comp, 0, None)

    vu_n, vu_c = 3.6, 3.2
    ax.plot(V, p_of(V, vu_n), color=C["venous"], lw=2.4)
    ax.plot(V, p_of(V, vu_c), color=C["arterial"], lw=2.2, ls=(0, (6, 3)))
    vt = 5.0
    ax.axvline(vt, color=C["gray"], lw=0.9, ls=(0, (3, 3)))
    ax.text(vt + 0.05, 0.6, "systemic volume\n5 L (illustrative)", fontsize=9, color=C["gray"])
    ax.plot([vt], [p_of(vt, vu_n)], "o", color=C["venous"], ms=7, zorder=5)
    ax.plot([vt], [p_of(vt, vu_c)], "o", color=C["arterial"], ms=7, zorder=5)
    ax.text(vt + 0.08, p_of(vt, vu_n) - 0.5, "P$_{ms}$ 7", color=C["venous"], fontsize=9.5, va="top")
    ax.text(vt - 0.07, p_of(vt, vu_c) + 0.15, "P$_{ms}$ 9", color=C["arterial"], fontsize=9.5, va="center",
            ha="right")
    # unstressed and stressed brackets for the normal curve
    y = 12.9
    ax.annotate("", xy=(0.0, y), xytext=(vu_n, y), annotation_clip=False,
                arrowprops=dict(arrowstyle="<->", color=C["venous"], lw=1.2, shrinkA=0, shrinkB=0))
    ax.text(vu_n / 2, y + 0.35, "unstressed volume 3.6 L", ha="center", fontsize=9, color=C["venous"])
    ax.annotate("", xy=(vu_n, y), xytext=(vt, y), annotation_clip=False,
                arrowprops=dict(arrowstyle="<->", color=C["venous"], lw=1.2, shrinkA=0, shrinkB=0))
    ax.text((vu_n + vt) / 2, y + 0.35, "stressed 1.4 L", ha="center", fontsize=9, color=C["venous"])
    ax.text(5.75, 8.2, "normal\nvenous tone", color=C["venous"], fontsize=9.5, ha="center", va="top")
    ax.text(4.05, 9.6, "venoconstriction:\nsmaller unstressed\nvolume", color=C["arterial"], fontsize=9.5,
            ha="center")
    ax.set_xlim(0, 6.0)
    ax.set_ylim(0, 14.5)
    ax.set_yticks([0, 2, 4, 6, 8, 10, 12, 14])
    ax.set_xlabel("Volume in the systemic circulation (L)")
    ax.set_ylabel("Pressure with no flow (mm Hg)")
    fs.grid(ax)
    save(fig, "stressed-unstressed.svg")


# ---------------------------------------------------------------- 6. Vascular function curves
def fig_vascular_curves():
    pra = np.linspace(-3, 12, 600)
    fig, axs = plt.subplots(1, 2, figsize=(10.2, 4.6), sharey=True)
    ax = axs[0]
    for pms, lab, col, ls in ((5, "hemorrhage or\nvenodilation", C["venous"], (0, (5, 3))),
                              (7, "normal", C["ink"], "-"),
                              (9, "transfusion or\nvenoconstriction", C["arterial"], (0, (5, 3)))):
        m = pra <= pms
        ax.plot(pra[m], vr_curve(pra[m], pms), color=col, lw=2.2, ls=ls)
        ax.plot([pms], [0], "o", color=col, ms=6, zorder=5, clip_on=False)
        ax.text(pms + 0.15, 0.35, f"P$_{{ms}}$ {pms}", color=col, fontsize=9)
    ax.text(-2.7, 9.4, "transfusion or\nvenoconstriction", color=C["arterial"], fontsize=9)
    ax.text(-2.7, 4.6, "hemorrhage or\nvenodilation", color=C["venous"], fontsize=9, va="top")
    ax.text(-2.7, 7.25, "normal", color=C["ink"], fontsize=9)
    ax.annotate("plateau: veins collapse\nas they enter the chest", xy=(-0.3, 9.0), xytext=(1.0, 10.8),
                fontsize=8.8, color=C["text"], arrowprops=dict(arrowstyle="-", color=C["text"], lw=0.8))
    ax.set_title("A  Changing P$_{ms}$ shifts the curve")
    curve_axes(ax, ymax=12)
    ax.set_ylabel("Venous return (L/min)")
    ax = axs[1]
    for rvr, lab, col, ls, yl in ((0.7, "lower RVR", C["green"], (0, (5, 3)), 8.0),
                                  (1.0, "normal RVR", C["ink"], "-", 4.9),
                                  (1.5, "higher RVR", C["gold"], (0, (5, 3)), 2.0)):
        m = pra <= 7
        ax.plot(pra[m], vr_curve(pra[m], 7, rvr), color=col, lw=2.2, ls=ls)
    ax.text(1.2, 8.6, "lower RVR (steeper)", color=C["green"], fontsize=9)
    ax.text(-2.7, 7.25, "normal", color=C["ink"], fontsize=9)
    ax.text(-2.7, 3.2, "higher RVR\n(flatter)", color=C["gold"], fontsize=9)
    ax.plot([7], [0], "o", color=C["ink"], ms=6, zorder=5, clip_on=False)
    ax.text(7.15, 0.35, "same P$_{ms}$", fontsize=9, color=C["ink"])
    ax.set_title("B  Changing RVR changes the slope")
    curve_axes(ax, ymax=12)
    ax.set_ylabel("")
    for a in axs:
        a.set_xlabel("Right atrial pressure, P$_{ra}$ (mm Hg)")
    fig.tight_layout()
    save(fig, "vascular-function-curves.svg")


# ---------------------------------------------------------------- 7. Operating point and four shifts
def fig_operating_shifts():
    pra = np.linspace(-3, 12, 600)
    base_c = lambda x: cardiac_curve(x)
    base_v = lambda x: vr_curve(x)
    x0, y0 = operating_point(base_c, base_v)
    scen = [
        ("A  Transfusion", base_c, lambda x: vr_curve(x, 9.0), "vascular"),
        ("B  Reduced contractility", lambda x: cardiac_curve(x, cmax=7.0), base_v, "cardiac"),
        ("C  Hemorrhage", base_c, lambda x: vr_curve(x, 5.0), "vascular"),
        ("D  Hemorrhage, with compensation", lambda x: cardiac_curve(x, cmax=14.0),
         lambda x: vr_curve(x, 6.2), "both"),
    ]
    fig, axs = plt.subplots(2, 2, figsize=(9.8, 8.4), sharex=True, sharey=True)
    pts = {"normal": (x0, y0)}
    for ax, (title, cf, vf, which) in zip(axs.flat, scen):
        ax.plot(pra, base_c(pra), color=C["ventricular"], lw=1.4, alpha=0.45)
        mv = pra <= 7
        ax.plot(pra[mv], base_v(pra[mv]), color=C["venous"], lw=1.4, alpha=0.45)
        if which == "both":
            mh = pra <= 5
            ax.plot(pra[mh], vr_curve(pra[mh], 5.0), color=C["venous"], lw=1.3, ls=(0, (2, 2)), alpha=0.7)
            xh, yh = operating_point(base_c, lambda x: vr_curve(x, 5.0))
            ax.plot([xh], [yh], "o", mfc="white", mec=C["gray"], ms=7, zorder=6)
            ax.text(xh - 0.3, yh - 1.0, "2", fontsize=9, color=C["gray"], ha="center")
            ax.annotate("", xy=(xh, yh), xytext=(x0, y0),
                        arrowprops=dict(arrowstyle="->", color=C["gray"], lw=1.2, shrinkA=5, shrinkB=5))
        ax.plot(pra, cf(pra), color=C["ventricular"], lw=2.3, ls="-" if which != "vascular" else "-")
        x1, y1 = operating_point(cf, vf)
        pms_new = pra[np.where(vf(pra) > 1e-3)[0][-1]] + 0.03
        mn = pra <= pms_new
        ax.plot(pra[mn], vf(pra[mn]), color=C["venous"], lw=2.3)
        pts[title] = (x1, y1)
        ax.plot([x0], [y0], "o", mfc="white", mec=C["ink"], ms=7, zorder=6)
        ax.plot([x1], [y1], "o", color=C["arterial"], ms=8, zorder=7)
        start = (xh, yh) if which == "both" else (x0, y0)
        ax.annotate("", xy=(x1, y1), xytext=start,
                    arrowprops=dict(arrowstyle="->", color=C["arterial"], lw=1.4, shrinkA=5, shrinkB=5))
        ax.set_title(title, fontsize=11)
        curve_axes(ax, ymax=14)
    # labels
    a = axs[0, 0]
    a.text(9.6, 6.6, "cardiac\nfunction\ncurve", color=C["ventricular"], fontsize=9, ha="center")
    a.text(6.9, 3.0, "vascular\nfunction\ncurve", color=C["venous"], fontsize=9)
    a.text(-2.7, 12.6, "open circle: normal operating point\nfilled circle: new operating point", fontsize=8.5,
           color=C["text"])
    axs[0, 1].text(8.5, 6.0, "weaker heart", color=C["ventricular"], fontsize=9, ha="center")
    axs[1, 0].text(-2.7, 6.0, "P$_{ms}$ 5", color=C["venous"], fontsize=9)
    d = axs[1, 1]
    d.text(-2.7, 12.6, "2: hemorrhage before compensation\nfilled: after sympathetic compensation", fontsize=8.5,
           color=C["text"])
    d.text(8.2, 12.9, "stronger,\nfaster heart", color=C["ventricular"], fontsize=9, ha="center")
    for ax in axs[0]:
        ax.set_xlabel("")
    for ax in axs[:, 1]:
        ax.set_ylabel("")
    fig.tight_layout()
    save(fig, "operating-point-shifts.svg")
    return pts


# ---------------------------------------------------------------- 8. Reading the cause from the movement
def fig_find_cause():
    pra = np.linspace(-3, 12, 600)
    base_c = lambda x: cardiac_curve(x)
    base_v = lambda x: vr_curve(x)
    x0, y0 = operating_point(base_c, base_v)
    fig, axs = plt.subplots(1, 2, figsize=(10.2, 4.8), sharey=True)
    # A: vascular shifts, point slides along the cardiac curve
    ax = axs[0]
    ax.plot(pra, base_c(pra), color=C["ventricular"], lw=3.2, alpha=0.9)
    for pms in (4.5, 9.5):
        vf = lambda x, p=pms: vr_curve(x, p)
        mm = pra <= pms
        ax.plot(pra[mm], vf(pra[mm]), color=C["venous"], lw=1.5, ls=(0, (5, 3)))
        x1, y1 = operating_point(base_c, vf)
        ax.plot([x1], [y1], "o", color=C["arterial"], ms=7, zorder=7)
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle="->", color=C["arterial"], lw=1.6, shrinkA=5, shrinkB=5))
    m7 = pra <= 7
    ax.plot(pra[m7], base_v(pra[m7]), color=C["venous"], lw=2.0)
    ax.plot([x0], [y0], "o", mfc="white", mec=C["ink"], ms=8, zorder=8)
    ax.annotate("P$_{ms}$ up:\nCO up, P$_{ra}$ up", xy=(3.4, 6.3), xytext=(3.6, 10.0), color=C["arterial"],
                fontsize=9.2, arrowprops=dict(arrowstyle="-", color=C["arterial"], lw=0.7))
    ax.text(-2.8, 2.25, "P$_{ms}$ down:\nCO down,\nP$_{ra}$ down", color=C["arterial"], fontsize=9.2)
    ax.text(8.0, 12.1, "the point slides along the\nunchanged cardiac function curve", color=C["ventricular"],
            fontsize=8.8, ha="center")
    ax.set_title("A  The vascular function curve moves")
    curve_axes(ax, ymax=14)
    # B: cardiac shifts, point slides along the vascular curve
    ax = axs[1]
    m7 = pra <= 7
    ax.plot(pra[m7], base_v(pra[m7]), color=C["venous"], lw=3.2, alpha=0.9)
    for cmax in (7.0, 17.0):
        cf = lambda x, c=cmax: cardiac_curve(x, cmax=c)
        ax.plot(pra, cf(pra), color=C["ventricular"], lw=1.5, ls=(0, (5, 3)))
        x1, y1 = operating_point(cf, base_v)
        ax.plot([x1], [y1], "o", color=C["arterial"], ms=7, zorder=7)
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle="->", color=C["arterial"], lw=1.6, shrinkA=5, shrinkB=5))
    ax.plot(pra, base_c(pra), color=C["ventricular"], lw=2.0)
    ax.plot([x0], [y0], "o", mfc="white", mec=C["ink"], ms=8, zorder=8)
    ax.text(-2.8, 8.9, "stronger heart:\nCO up, P$_{ra}$ down", color=C["arterial"], fontsize=9.2)
    ax.annotate("weaker heart:\nCO down, P$_{ra}$ up", xy=(3.5, 3.5), xytext=(7.4, 1.6), color=C["arterial"],
                fontsize=9.2, arrowprops=dict(arrowstyle="-", color=C["arterial"], lw=0.7))
    ax.text(8.0, 12.1, "the point slides along the\nunchanged vascular function curve", color=C["venous"],
            fontsize=8.8, ha="center")
    ax.set_title("B  The cardiac function curve moves")
    curve_axes(ax, ymax=14)
    ax.set_ylabel("")
    fig.tight_layout()
    save(fig, "find-the-cause.svg")


if __name__ == "__main__":
    fig_pulse_pressure()
    print(fig_shock_pp())
    fig_equilibration()
    fig_stressed_volume()
    fig_vascular_curves()
    pts = fig_operating_shifts()
    for k, v in pts.items():
        print(k.replace("\n", " "), "Pra %.1f CO %.1f" % v)
    fig_find_cause()
