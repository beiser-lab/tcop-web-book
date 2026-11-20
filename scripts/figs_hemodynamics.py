"""Figures for the Peripheral Circulation and Hemodynamics chapter.

Run:  cd site/scripts && MPLCONFIGDIR=$TMPDIR PNG_PREVIEW=<folder> python3 figs_hemodynamics.py
Writes SVGs to ../cardiovascular/figures/hemodynamics/.
Numbers come from the 2026 lecture (vascular dimensions table, slide 39) or from the
equations the course teaches (Ohm's law, Q = A x v, a two-element Windkessel for the
hydraulic filter).
"""
import numpy as np
import figstyle as fs
from matplotlib.patches import FancyBboxPatch, Circle, Polygon, FancyArrowPatch

plt = fs.plt
C = fs.C
M = fs.MINUS
PART, SLUG = "cardiovascular", "hemodynamics"


def save(fig, name):
    fs.save(fig, PART, SLUG, name)


def box(ax, x, y, w, h, text, fc, ec, fs_=9.5, color=None, bold=False):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc=fc, ec=ec, lw=1.4, zorder=3))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs_, color=color or C["ink"],
            fontweight="bold" if bold else "normal", zorder=4)


def arrow(ax, x0, y0, x1, y1, color, lw=1.6, head=True):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="-|>" if head else "-", color=color, lw=lw,
                                shrinkA=0, shrinkB=0, mutation_scale=12), zorder=2)


# ---------------------------------------------------------------- 1. Organization of the circulation
def fig_circuit():
    fig, ax = plt.subplots(figsize=(9.0, 6.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    art, ven = C["arterial"], C["venous"]
    xa, xv = 8.6, 1.4  # arterial and venous "buses"
    # heart and lungs
    box(ax, xv, 8.7, 1.9, 0.8, "Right heart", "#e9f0f4", ven, bold=True, color=ven)
    box(ax, xa, 8.7, 1.9, 0.8, "Left heart", "#f6e9e9", art, bold=True, color=art)
    box(ax, 5.0, 9.45, 2.6, 0.7, "Lungs (one bed)", "#f6f0e6", C["ventricular"], color=C["ink"])
    arrow(ax, xv, 9.1, 3.7, 9.45, ven)
    arrow(ax, 6.3, 9.45, xa, 9.1, art)
    ax.text(2.3, 9.5, "pulmonary\nartery", fontsize=8, color=ven, ha="center")
    ax.text(7.7, 9.5, "pulmonary\nveins", fontsize=8, color=art, ha="center")
    # buses
    ytop, ybot = 8.3, 0.75
    ax.plot([xa, xa], [ytop, ybot], color=art, lw=3, solid_capstyle="round", zorder=1)
    ax.plot([xv, xv], [ytop, ybot], color=ven, lw=3, solid_capstyle="round", zorder=1)
    arrow(ax, xa + 0.25, 7.9, xa + 0.25, 6.9, art, lw=1.2)
    arrow(ax, xv - 0.25, 6.9, xv - 0.25, 7.9, ven, lw=1.2)
    ax.text(xa + 0.15, 4.3, "aorta and\narteries", fontsize=8.5, color=art, rotation=90, va="center", ha="left")
    ax.text(xv - 0.45, 4.3, "veins and\nvena cava", fontsize=8.5, color=ven, rotation=90, va="center", ha="left")

    def row(y, label):
        ax.plot([xv, xa], [y, y], color=C["axis"], lw=1.6, zorder=1)
        arrow(ax, 7.3, y, 7.0, y, C["gray"], lw=1.2)

    # ordinary parallel beds
    for y, lab in ((7.4, "Brain"), (6.5, "Heart (coronary)"), (5.6, "Skeletal muscle"), (4.7, "Skin")):
        row(y, lab)
        box(ax, 5.0, y, 2.6, 0.62, lab, "white", C["axis"], fs_=9.5)
    # kidney: two capillary beds in series
    yk = 3.55
    row(yk, "")
    box(ax, 6.0, yk, 1.6, 0.62, "glomerular\ncapillaries", "#fff6e8", C["gold"], fs_=8.3)
    box(ax, 3.6, yk, 1.6, 0.62, "peritubular\ncapillaries", "#fff6e8", C["gold"], fs_=8.3)
    ax.text(4.8, yk + 0.42, "efferent arteriole", fontsize=7.8, color=C["gold"], ha="center")
    ax.text(5.0, yk - 0.6, "Kidney: two capillary beds in series", fontsize=8.8, color=C["gold"], ha="center",
            fontweight="bold")
    # gut and liver
    yg, yl = 2.15, 1.25
    ax.plot([5.9, xa], [yg, yg], color=C["axis"], lw=1.6, zorder=1)
    arrow(ax, 7.6, yg, 7.3, yg, C["gray"], lw=1.2)
    arrow(ax, 2.4, yl, 2.1, yl, C["gray"], lw=1.2)
    box(ax, 5.9, yg, 2.2, 0.6, "gut, spleen, pancreas", "#fff6e8", C["gold"], fs_=8.3)
    ax.plot([xv, 4.2], [yl, yl], color=C["axis"], lw=1.6, zorder=1)
    ax.plot([xa, 4.8], [yl, yl], color=C["axis"], lw=1.6, zorder=1)
    box(ax, 3.9, yl, 1.4, 0.6, "liver", "#fff6e8", C["gold"], fs_=8.5)
    ax.annotate("", xy=(4.1, yl + 0.3), xytext=(4.8, yg - 0.3),
                arrowprops=dict(arrowstyle="-|>", color=C["gold"], lw=1.4), zorder=2)
    ax.text(3.0, 1.85, "portal vein", fontsize=7.8, color=C["gold"], ha="center")
    ax.text(6.9, yl + 0.12, "hepatic artery", fontsize=7.8, color=C["gold"], ha="center")
    ax.text(5.0, 0.45, "Gut and liver: portal circulation, beds in series plus a separate arterial supply",
            fontsize=8.8, color=C["gold"], ha="center", fontweight="bold")
    ax.text(5.0, 7.9, "Systemic organ beds in parallel, most with one capillary bed", fontsize=9, color=C["ink"], ha="center",
            fontweight="bold")
    save(fig, "circuit.svg")


# ---------------------------------------------------------------- 2. Perfusion vs transmural pressure
def vessel_long(ax, p_up, p_down, p_in, p_out, flow, title, note):
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=11)
    ax.add_patch(FancyBboxPatch((0.3, 1.0), 9.4, 3.6, boxstyle="round,pad=0,rounding_size=0.3",
                                fc=C["shade"], ec="none", zorder=0))
    ax.text(5.0, 1.35, f"surrounding tissue {p_out} mm Hg", fontsize=8.5, color=C["text"], ha="center")
    ax.plot([0.8, 9.2], [3.4, 3.4], color=C["arterial"], lw=2.5)
    ax.plot([0.8, 9.2], [2.2, 2.2], color=C["arterial"], lw=2.5)
    ax.add_patch(plt.Rectangle((0.8, 2.2), 8.4, 1.2, fc="#f6e9e9", ec="none", zorder=0))
    ax.text(0.9, 3.85, f"upstream {p_up}", fontsize=9.5, color=C["arterial"], fontweight="bold")
    ax.text(9.1, 3.85, f"downstream {p_down}", fontsize=9.5, color=C["arterial"], fontweight="bold", ha="right")
    ax.plot([5], [2.8], "o", color=C["ink"], ms=5)
    ax.text(5.25, 2.85, f"inside {p_in}", fontsize=8.5, color=C["ink"], va="center")
    if flow:
        arrow(ax, 2.0, 2.8, 4.2, 2.8, C["arterial"], lw=2.2)
        ax.text(3.1, 3.05, "flow", fontsize=8.5, color=C["arterial"], ha="center")
    else:
        ax.text(3.0, 2.8, "no flow", fontsize=8.5, color=C["arterial"], ha="center", va="center")
    ax.text(0.3, 0.6, note, fontsize=9, color=C["ink"], va="top")


def fig_perfusion_transmural():
    fig, axes = plt.subplots(1, 3, figsize=(13.0, 4.3), gridspec_kw=dict(width_ratios=[1, 0.72, 1]))
    vessel_long(axes[0], 100, 20, 60, 10, True, "A. Perfusion pressure (along)",
                f"ΔP = P$_{{upstream}}$ {M} P$_{{downstream}}$\n= 100 {M} 20 = 80 mm Hg\nDrives flow: Q = ΔP / R")
    ax = axes[1]
    ax.set_xlim(0, 7)
    ax.set_ylim(0, 6)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("B. Transmural pressure (across)", fontsize=11)
    ax.add_patch(Circle((3.5, 3.0), 2.2, fc=C["shade"], ec="none"))
    ax.add_patch(Circle((3.5, 3.0), 1.3, fc="#f6e9e9", ec=C["arterial"], lw=2.5))
    ax.text(3.5, 3.0, "inside\n60", ha="center", va="center", fontsize=9.5, color=C["arterial"], fontweight="bold")
    ax.text(3.5, 5.0, "outside 10", ha="center", fontsize=8.5, color=C["text"])
    for ang in (20, 160, 250, 300):
        r = np.radians(ang)
        arrow(ax, 3.5 + 1.35 * np.cos(r), 3.0 + 1.35 * np.sin(r), 3.5 + 1.95 * np.cos(r), 3.0 + 1.95 * np.sin(r),
              C["arterial"], lw=1.3)
    ax.text(0.2, 0.6, f"P$_{{tm}}$ = P$_{{inside}}$ {M} P$_{{outside}}$\n= 60 {M} 10 = +50 mm Hg\n"
                      f"+ distends; {M} favors collapse", fontsize=9, color=C["ink"], va="top")
    vessel_long(axes[2], 60, 60, 60, 10, False, "C. Equal pressures at both ends",
                f"ΔP = 60 {M} 60 = 0: no flow\nP$_{{tm}}$ = 60 {M} 10 = +50 mm Hg:\nthe vessel stays distended")
    fig.subplots_adjust(wspace=0.08)
    save(fig, "perfusion-vs-transmural.svg")


# ---------------------------------------------------------------- 3. MAP as a time average
def model_wave(hr, ts, tau=0.3, pn=96.0, dt=0.0005):
    """Model arterial waveform, 120/80: fast upstroke, fall through late systole to a small
    incisura at aortic valve closure, then a long diastolic runoff toward 80 mm Hg."""
    T = 60.0 / hr
    t = np.arange(0, T, dt)
    P = np.zeros_like(t)
    tr = 0.08
    for i, tt in enumerate(t):
        if tt < tr:
            P[i] = 80 + 40 * (1 - np.cos(np.pi * tt / tr)) / 2
        elif tt < ts:
            u = (tt - tr) / (ts - tr)
            P[i] = 120 - (120 - pn) * (1 - np.cos(np.pi * u)) / 2
        else:
            td, Td = tt - ts, T - ts
            notch = -2.0 * np.exp(-((td - 0.012) / 0.008) ** 2)
            e = (np.exp(-td / tau) - np.exp(-Td / tau)) / (1 - np.exp(-Td / tau))
            P[i] = 80 + (pn + 1 - 80) * e + notch
    return t, P


def fig_map():
    fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.0), sharey=True, gridspec_kw=dict(width_ratios=[1, 0.5]))
    for ax, hr, ts, title in ((axes[0], 75, 0.29, "A. Resting heart rate (75/min)"),
                              (axes[1], 150, 0.22, "B. Fast heart rate (150/min)")):
        t, P = model_wave(hr, ts)
        mean = P.mean()
        est = 80 + 40 / 3
        ax.fill_between(t, P, mean, where=P >= mean, color=C["highlight"], lw=0)
        ax.fill_between(t, P, mean, where=P < mean, color=C["cool"], lw=0)
        ax.plot(t, P, color=C["arterial"], lw=2.2)
        ax.axhline(mean, color=C["ink"], lw=1.4)
        ax.axhline(est, color=C["ink"], lw=1.0, ls=(0, (4, 3)))
        ax.axhline(100, color=C["gray"], lw=0.8, ls=(0, (1, 2)))
        ax.axvline(ts, color=C["gray"], lw=0.8)
        ax.set_title(title, fontsize=11)
        ax.set_xlim(0, t[-1])
        ax.set_xlabel("Time (s)")
        fs.grid(ax)
        print(title, "mean", round(mean, 1))
        ax.text(ts + 0.01, 117, "diastole", fontsize=8.5, color=C["gray"])
        ax.text(ts - 0.01, 117, "systole", fontsize=8.5, color=C["gray"], ha="right")
        ax.text(t[-1] * 0.98, mean + 0.9, f"true mean {mean:.0f}", ha="right", fontsize=9, color=C["ink"])
        if hr < 100:
            ax.text(t[-1] * 0.98, est - 2.7, "DBP + ⅓ PP = 93", ha="right", fontsize=9, color=C["ink"])
        else:
            ax.text(0.045, est - 3.0, "DBP + ⅓ PP = 93", ha="left", fontsize=9, color=C["ink"])
    axes[0].text(0.36, 100.8, "halfway (100)", fontsize=8.5, color=C["gray"])
    axes[0].set_ylabel("Arterial pressure (mm Hg)")
    axes[0].set_ylim(76, 124)
    fig.subplots_adjust(wspace=0.06)
    save(fig, "map-time-average.svg")


# ---------------------------------------------------------------- 4. Series and parallel resistances
def resistor(ax, x0, x1, y, color, n=6, amp=0.18, lw=1.8):
    xs = np.linspace(x0, x1, 2 * n + 1)
    ys = np.full_like(xs, y)
    ys[1:-1:2] += amp
    ys[2:-1:2] -= amp
    ax.plot(xs, ys, color=color, lw=lw, solid_joinstyle="miter")


def fig_series_parallel():
    fig = plt.figure(figsize=(11.0, 4.9))
    axA = fig.add_axes([0.07, 0.42, 0.42, 0.48])
    axP = fig.add_axes([0.07, 0.10, 0.42, 0.30])
    axB = fig.add_axes([0.53, 0.10, 0.45, 0.80])
    for a in (axA, axB):
        a.axis("off")
    # series
    axA.set_xlim(0, 10)
    axA.set_ylim(0, 3)
    axA.set_title("A. In series: resistances add", fontsize=11)
    segs = [("artery", 0.1, C["arterial"]), ("arteriole", 0.6, C["ventricular"]),
            ("capillaries", 0.2, C["gold"]), ("veins", 0.1, C["venous"])]
    x = 0.6
    widths = [2.2, 2.2, 2.2, 2.2]
    xs = [0.6]
    axA.plot([0.2, 0.6], [1.5, 1.5], color=C["ink"], lw=1.8)
    for (lab, r, col), w in zip(segs, widths):
        n = max(2, int(round(r * 14)))
        resistor(axA, x, x + w, 1.5, col, n=n, amp=0.12 + 0.35 * r)
        axA.text(x + w / 2, 2.25, lab, ha="center", fontsize=9, color=col)
        x += w
        xs.append(x)
    axA.plot([x, x + 0.4], [1.5, 1.5], color=C["ink"], lw=1.8)
    axA.text(0.2, 0.75, "P$_i$ = 95", fontsize=9, color=C["ink"])
    axA.text(9.8, 0.75, "P$_o$ = 5", fontsize=9, color=C["ink"], ha="right")
    axA.text(5.0, 0.2, "R$_t$ = R$_1$ + R$_2$ + R$_3$ + R$_4$; the same Q passes through each", ha="center",
             fontsize=9, color=C["ink"])
    # pressure along the series path
    Pi, Po = 95.0, 5.0
    rt = sum(s[1] for s in segs)
    P = [Pi]
    for lab, r, col in segs:
        P.append(P[-1] - (Pi - Po) * r / rt)
    axP.set_xlim(0, 10)
    for i, (lab, r, col) in enumerate(segs):
        axP.plot([xs[i], xs[i + 1]], [P[i], P[i + 1]], color=col, lw=2.4)
        axP.text((xs[i] + xs[i + 1]) / 2 + 0.1, (P[i] + P[i + 1]) / 2 + 4,
                 f"{M}{P[i] - P[i + 1]:.0f}", fontsize=8.5, color=col)
    axP.set_ylim(0, 105)
    axP.set_yticks([0, 50, 100])
    axP.set_xticks([])
    axP.set_ylabel("P (mm Hg)", fontsize=9)
    fs.grid(axP)
    axP.text(9.9, 85, "largest drop across\nthe largest resistance", fontsize=8.5, color=C["text"], ha="right")
    # parallel
    axB.set_xlim(0, 10)
    axB.set_ylim(0, 7)
    axB.set_title("B. In parallel: flows add, total R falls", fontsize=11)
    axB.plot([1.2, 1.2], [1.4, 5.6], color=C["arterial"], lw=2.5)
    axB.plot([8.8, 8.8], [1.4, 5.6], color=C["venous"], lw=2.5)
    axB.plot([0.2, 1.2], [3.5, 3.5], color=C["arterial"], lw=2.5)
    axB.plot([8.8, 9.8], [3.5, 3.5], color=C["venous"], lw=2.5)
    arrow(axB, 0.2, 3.85, 1.0, 3.85, C["arterial"], lw=1.2)
    axB.text(0.2, 4.05, "Q$_t$", fontsize=9.5, color=C["arterial"])
    axB.text(9.8, 4.05, "Q$_t$", fontsize=9.5, color=C["venous"], ha="right")
    for y, lab in ((5.6, "Q$_1$, R$_1$"), (3.5, "Q$_2$, R$_2$"), (1.4, "Q$_3$, R$_3$")):
        axB.plot([1.2, 3.4], [y, y], color=C["ink"], lw=1.6)
        axB.plot([6.6, 8.8], [y, y], color=C["ink"], lw=1.6)
        resistor(axB, 3.4, 6.6, y, C["ventricular"], n=6, amp=0.22)
        axB.text(5.0, y + 0.42, lab, ha="center", fontsize=9.5, color=C["ink"])
    axB.text(1.2, 6.15, "P$_i$", fontsize=10, color=C["arterial"], ha="center")
    axB.text(8.8, 6.15, "P$_o$", fontsize=10, color=C["venous"], ha="center")
    axB.text(5.0, 0.45, "Every branch has the same ΔP = P$_i$ " + M + " P$_o$\n"
             "Q$_t$ = Q$_1$ + Q$_2$ + Q$_3$;   1/R$_t$ = 1/R$_1$ + 1/R$_2$ + 1/R$_3$",
             ha="center", fontsize=9, color=C["ink"], va="center")
    save(fig, "series-parallel.svg")


# ---------------------------------------------------------------- 5. Continuity: Q = A x v
def fig_continuity():
    fig, ax = plt.subplots(figsize=(10.0, 3.9))
    ax.set_xlim(0, 12)
    ax.set_ylim(-2.0, 3.4)
    ax.set_aspect("equal")
    ax.axis("off")
    Q = 10.0
    secs = [(0.3, 4.0, 2.0), (4.6, 7.6, 1.0), (8.2, 11.7, 4.0)]  # x0, x1, area (cm2)
    # tube outline: half-height proportional to sqrt(area)
    hs = [0.62 * np.sqrt(a) for _, _, a in secs]
    xo, yt, yb = [], [], []
    for i, ((x0, x1, a), h) in enumerate(zip(secs, hs)):
        xo += [x0, x1]
        yt += [1.0 + h, 1.0 + h]
        yb += [1.0 - h, 1.0 - h]
    ax.plot(xo, yt, color=C["arterial"], lw=2)
    ax.plot(xo, yb, color=C["arterial"], lw=2)
    ax.fill_between(xo, yb, yt, color="#f8eeee", lw=0, zorder=0)
    for (x0, x1, a), h in zip(secs, hs):
        v = Q / a
        L = v * 0.18  # length of the 1-second slug, drawn to scale (cm/s x 0.18)
        xm = (x0 + x1) / 2
        ax.add_patch(plt.Rectangle((xm - L / 2, 1.0 - h), L, 2 * h, fc=C["arterial"], alpha=0.55, ec="none"))
        ax.text(xm, -0.75, f"A = {a:g} cm²", ha="center", fontsize=9.5, color=C["ink"])
        ax.text(xm, -1.2, f"v = Q/A = {v:g} cm/s", ha="center", fontsize=9.5, color=C["ink"], fontweight="bold")
        ax.text(xm, -1.65, f"Q = {Q:g} cm³/s", ha="center", fontsize=9, color=C["text"])
    arrow(ax, 0.3, 3.1, 2.0, 3.1, C["arterial"], lw=1.8)
    ax.text(2.2, 3.1, "flow", fontsize=9, color=C["arterial"], va="center")
    ax.text(11.7, 3.1, "dark band: the volume that passes in one second", fontsize=8.5, color=C["text"],
            ha="right", va="center")
    save(fig, "continuity.svg")


# ---------------------------------------------------------------- 6. Area, velocity and pressure profiles
def fig_profiles():
    names = ["Aorta", "Small\narteries", "Arterioles", "Capillaries", "Vena\ncava"]
    area = [4, 63, 141, 2827, 6]
    vel = [21, 1.3, 0.6, 0.03, 14]
    x = np.arange(5)
    fig, axes = plt.subplots(3, 1, figsize=(7.6, 8.4), sharex=True)
    bands = [C["highlight"], "#f8eeee", "#fbf3ea", "#f1edf4", "#e9f0f4"]
    for ax in axes:
        for i in x:
            ax.axvspan(i - 0.5, i + 0.5, color=bands[i], lw=0, zorder=0)
        ax.set_xlim(-0.5, 4.5)
    ax = axes[0]
    ax.plot(x, area, "o-", color=C["green"], lw=2.2, ms=6)
    ax.set_yscale("log")
    ax.set_ylim(2, 8000)
    ax.set_ylabel("Aggregate cross-\nsectional area (cm²)")
    ax.set_title("A. Aggregate cross-sectional area", fontsize=11)
    for i, a in enumerate(area):
        ax.text(i + 0.1, a, f"{a:,}", fontsize=8.5, color=C["green"], ha="left", va="top")
    ax.text(3.0, 6.0, "≈ a 24-inch pizza", fontsize=8.5, color=C["text"], ha="center")
    ax = axes[1]
    ax.plot(x, vel, "o-", color=C["purple"], lw=2.2, ms=6)
    ax.set_yscale("log")
    ax.set_ylim(0.01, 100)
    ax.set_ylabel("Mean velocity\n(cm/s)")
    ax.set_title("B. Mean velocity (Q / A, with Q = 83 mL/s at every level)", fontsize=11)
    for i, v in enumerate(vel):
        ax.text(i, v * 2.0, f"{v:g}", fontsize=8.5, color=C["purple"], ha="center", va="bottom")
    ax = axes[2]
    # mean pressure, with the systolic/diastolic envelope in the arteries
    xp = np.array([-0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5])
    pm = np.array([93, 93, 91, 87, 65, 45, 35, 25, 15, 6, 3])
    xs = np.linspace(-0.5, 4.5, 400)
    pms = np.interp(xs, xp, pm)
    k = np.convolve(pms, np.ones(25) / 25, mode="same")
    k[:12], k[-12:] = pms[:12], pms[-12:]
    f = np.clip((2.4 - xs) / 1.2, 0, 1) ** 1.2
    up, dn = k + 27 * f, k - 13 * f
    ax.fill_between(xs, dn, up, color="#f1d9d9", lw=0)
    ax.plot(xs, up, color=C["arterial"], lw=0.9)
    ax.plot(xs, dn, color=C["arterial"], lw=0.9)
    ax.plot(xs, k, color=C["arterial"], lw=2.4)
    ax.set_ylim(0, 125)
    ax.set_ylabel("Pressure (mm Hg)")
    ax.set_title("C. Pressure: mean (thick) and systolic to diastolic range", fontsize=11)
    ax.text(-0.35, 52, "aorta 120/80,\nmean 93", fontsize=8.5, color=C["arterial"], ha="left")
    ax.text(3.0, 33, "about 25", fontsize=8.5, color=C["arterial"], ha="center")
    ax.text(2.5, 40, "35", fontsize=8.5, color=C["arterial"], ha="center")
    ax.text(3.5, 20, "15", fontsize=8.5, color=C["arterial"], ha="center")
    ax.text(4.0, 12, "about 3", fontsize=8.5, color=C["arterial"], ha="center")
    ax.annotate("steepest fall across\nsmall arteries and arterioles", xy=(1.6, 62), xytext=(2.15, 92),
                fontsize=8.5, color=C["ink"], arrowprops=dict(arrowstyle="-", color=C["ink"], lw=0.8))
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    for a in axes:
        a.grid(axis="y", color=C["grid"], lw=0.8)
        a.set_axisbelow(True)
    fig.subplots_adjust(hspace=0.32)
    save(fig, "area-velocity-pressure.svg")


# ---------------------------------------------------------------- 7. Compliance of arteries and veins
def fig_compliance():
    P = np.linspace(0, 100, 400)
    vein = 100 * (1 - np.exp(-P / 9))
    artery = 38 * (1 - np.exp(-P / 70))
    fig, ax = plt.subplots(figsize=(6.6, 4.8))
    ax.plot(P, vein, color=C["venous"], lw=2.4)
    ax.plot(P, artery, color=C["arterial"], lw=2.4)

    def tangent(f, p0, dp, col, label_side):
        v0 = np.interp(p0, P, f)
        s = np.gradient(f, P)[np.searchsorted(P, p0)]
        ax.plot([p0 - dp, p0 + dp], [v0 - s * dp, v0 + s * dp], color=col, lw=1.2, ls=(0, (3, 2)))
        ax.plot([p0], [v0], "o", color=col, ms=5)
        ax.plot([p0, p0 + dp, p0 + dp], [v0, v0, v0 + s * dp], color=C["gray"], lw=0.9)
        ax.text(p0 + dp / 2, v0 - 4.5, "ΔP", ha="center", fontsize=9, color=C["gray"])
        ax.text(p0 + dp + 1.2, v0 + s * dp / 2, "ΔV", va="center", fontsize=9, color=C["gray"])
    tangent(vein, 8, 7, C["venous"], "r")
    tangent(artery, 60, 15, C["arterial"], "r")
    ax.text(60, 96, "Vein", color=C["venous"], fontsize=11, fontweight="bold")
    ax.text(86, 18, "Artery", color=C["arterial"], fontsize=11, fontweight="bold")
    ax.text(31, 62, "steep: large ΔV for a\nsmall ΔP (high compliance)", fontsize=9, color=C["venous"])
    ax.text(28, 41, "shallow: small ΔV for a\nlarge ΔP (low compliance)", fontsize=9, color=C["arterial"])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 110)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel("Transmural pressure")
    ax.set_ylabel("Volume")
    ax.text(100, -9, "Slope = ΔV/ΔP = compliance", ha="right", fontsize=9, color=C["text"])
    save(fig, "compliance-artery-vein.svg")


# ---------------------------------------------------------------- 8. Hydraulic filter (Windkessel)
def fig_filter():
    hr, tej, sv = 75, 0.30, 70.0
    T = 60.0 / hr
    dt = 0.0005
    R = 1.0  # mm Hg per mL/s
    out = {}
    for label, Cc in (("compliant", 1.5), ("stiff", 0.6)):
        t = np.arange(0, 30 * T, dt)
        p = 85.0
        P = np.zeros_like(t)
        Qin = np.zeros_like(t)
        peak = sv * np.pi / (2 * tej)
        for i, tt in enumerate(t):
            ph = tt % T
            q = peak * np.sin(np.pi * ph / tej) if ph < tej else 0.0
            p += dt * (q - p / R) / Cc
            P[i], Qin[i] = p, q
        keep = t >= 27 * T
        out[label] = (t[keep] - t[keep][0], P[keep], Qin[keep], P[keep] / R)
    fig, axes = plt.subplots(3, 1, figsize=(7.6, 7.6), sharex=True)
    t, P, Qin, Qout = out["compliant"]
    axes[0].fill_between(t, 0, Qin, color="#f6e3cc", lw=0)
    axes[0].plot(t, Qin, color=C["ventricular"], lw=2)
    axes[0].set_ylabel("Flow out of\nLV (mL/s)")
    axes[0].set_title("A. The ventricle ejects in bursts", fontsize=11)
    axes[0].set_ylim(0, 400)
    for lab, col, ls in (("compliant", C["arterial"], "-"), ("stiff", C["gray"], (0, (4, 2)))):
        t, P, Qin, Qout = out[lab]
        axes[1].plot(t, P, color=col, lw=2.2, ls=ls)
        axes[2].plot(t, Qout, color=col, lw=2.2, ls=ls)
        print(lab, "P range", round(P.min()), round(P.max()), "mean", round(P.mean(), 1))
    axes[1].set_ylabel("Aortic pressure\n(mm Hg)")
    axes[1].set_title("B. Aortic pressure: compliance holds it up in diastole", fontsize=11)
    axes[2].set_ylabel("Flow through\narterioles (mL/s)")
    axes[2].set_title("C. Flow into the arterioles continues between beats", fontsize=11)
    axes[2].set_xlabel("Time (s)")
    tc, Pc, _, _ = out["compliant"]
    ts, Ps, _, _ = out["stiff"]
    axes[1].text(0.45, 109, "compliant aorta", ha="left", fontsize=9, color=C["arterial"])
    axes[1].text(0.33, Ps.max() - 2, "stiff aorta", ha="left", fontsize=9, color=C["gray"])
    for a in axes:
        fs.grid(a)
    axes[2].set_xlim(0, 3 * T)
    axes[1].set_ylim(40, 160)
    axes[2].set_ylim(40, 160)
    fig.subplots_adjust(hspace=0.34)
    save(fig, "hydraulic-filter.svg")


# ---------------------------------------------------------------- 9. Laminar flow profile
def fig_laminar_profile():
    fig, ax = plt.subplots(figsize=(5.6, 3.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.plot([0.5, 9.5], [5.0, 5.0], color=C["arterial"], lw=2.5)
    ax.plot([0.5, 9.5], [1.0, 1.0], color=C["arterial"], lw=2.5)
    ys = np.linspace(1.15, 4.85, 13)
    r = (ys - 3.0) / 2.0
    v = 1 - r ** 2
    for y, vv in zip(ys, v):
        arrow(ax, 2.0, y, 2.0 + 0.2 + 5.0 * vv, y, C["arterial"], lw=1.2)
    yy = np.linspace(1.0, 5.0, 100)
    ax.plot(2.0 + 0.2 + 5.0 * (1 - ((yy - 3) / 2) ** 2), yy, color=C["ink"], lw=1.2, ls=(0, (3, 2)))
    ax.plot([2.0, 2.0], [1.0, 5.0], color=C["gray"], lw=0.9)
    ax.text(7.6, 3.0, "fastest\nin the\ncenter", fontsize=9, color=C["ink"], va="center")
    ax.text(5.0, 0.35, "velocity is zero at the wall", fontsize=9, color=C["ink"], ha="center")
    save(fig, "laminar-profile.svg")


if __name__ == "__main__":
    fig_circuit()
    fig_perfusion_transmural()
    fig_map()
    fig_series_parallel()
    fig_continuity()
    fig_profiles()
    fig_compliance()
    fig_filter()
    fig_laminar_profile()
