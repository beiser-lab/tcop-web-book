"""Figures for ECG II: Vectors and Mean Electrical Axis (cardiovascular/ecg-vectors-axis.qmd).

Run:  cd site/scripts && MPLCONFIGDIR=$TMPDIR PNG_PREVIEW=<folder> python3 figs_ecg-vectors-axis.py

Uses the synthetic-ECG library in figs_ecg-interpretation.py: every complex here is the projection
of a dipole vector loop on a lead axis, so the lead tracings, the loop and the mean electrical axis
in these figures agree with each other.
"""
import os
import importlib.util
import numpy as np
from matplotlib.patches import Rectangle, Wedge, Circle, FancyArrowPatch, Ellipse
import figstyle as fs
from figstyle import C, plt, MINUS

_spec = importlib.util.spec_from_file_location("ecglib", os.path.join(os.path.dirname(__file__), "figs_ecg-interpretation.py"))
E = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E)

PART, SLUG = "cardiovascular", "ecg-vectors-axis"
LEADS = E.LEADS
LEAD_COL = {"I": C["arterial"], "II": C["venous"], "III": C["green"], "aVR": C["gray"], "aVL": C["gold"], "aVF": C["purple"]}


def xy(theta, r=1.0):
    """ECG angle (clockwise from lead I, downward positive) to plot coordinates with y up."""
    return r * np.cos(np.radians(theta)), -r * np.sin(np.radians(theta))


def deg(x):
    return f"{x:+.0f}°".replace("-", MINUS) if x != 0 else "0°"


def mean_axis(comps, rot=0.0):
    t = np.arange(-0.05, 0.25, 1e-4)
    x, y = E.vector(t, 0.0, comps, rot)
    return np.degrees(np.arctan2(y.sum(), x.sum()))


# ------------------------------------------------------------------ 1. two-cell model, extracellular electrodes
def fig_two_cell():
    fig, axes = plt.subplots(3, 2, figsize=(8.8, 6.6), gridspec_kw=dict(width_ratios=[1.9, 1], hspace=0.45, wspace=0.08))
    rows = [("A  Depolarization moving toward the positive electrode", "toward"),
            ("B  Depolarization moving away from the positive electrode", "away"),
            ("C  Depolarization moving perpendicular to the lead", "perp")]
    t = np.linspace(0, 1, 400)
    for (ax, axt), (title, kind) in zip(axes, rows):
        ax.set_xlim(-0.6, 6.6)
        ax.set_ylim(-1.3, 1.5)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.text(-0.6, 1.45, title, fontsize=10, fontweight="bold", color=C["ink"], va="bottom")
        n_dep = 3
        for i in range(6):
            dep = i < n_dep
            ax.add_patch(Rectangle((i, -0.5), 0.95, 1.0, fc=C["highlight"] if dep else "white",
                                   ec=C["ventricular"] if dep else C["axis"], lw=1.3))
            outside = MINUS if dep else "+"
            col = C["arterial"] if dep else C["venous"]
            ax.text(i + 0.47, 0.68, outside, ha="center", va="center", fontsize=11, color=col)
            ax.text(i + 0.47, -0.70, outside, ha="center", va="center", fontsize=11, color=col)
        ax.text(1.5, -1.08, "depolarized", ha="center", va="center", fontsize=8.5, color=C["ventricular"])
        ax.text(4.5, -1.08, "resting", ha="center", va="center", fontsize=8.5, color=C["text"])
        ax.plot([2.975, 2.975], [-0.55, 0.55], color=C["ink"], lw=1.0, ls=(0, (2, 2)))
        ax.add_patch(FancyArrowPatch((2.6, 1.15), (3.8, 1.15), arrowstyle="-|>", mutation_scale=14, color=C["ink"], lw=1.6))
        ax.text(3.9, 1.15, "wave of depolarization", fontsize=8.5, color=C["ink"], va="center")
        if kind in ("toward", "away"):
            pos_x, neg_x = (6.35, -0.4) if kind == "toward" else (-0.4, 6.35)
            for xe, sgn, col in [(pos_x, "+", C["arterial"]), (neg_x, MINUS, C["venous"])]:
                ax.add_patch(Circle((xe, 0), 0.2, fc="white", ec=col, lw=1.6))
                ax.text(xe, 0, sgn, ha="center", va="center", fontsize=11, color=col, fontweight="bold")
        else:
            ax.plot([6.35, 6.35], [-0.42, 0.42], color=C["axis"], lw=1.0)
            for xe, ye, sgn, col in [(6.35, -0.6, "+", C["arterial"]), (6.35, 0.6, MINUS, C["venous"])]:
                ax.add_patch(Circle((xe - 0.0, ye), 0.17, fc="white", ec=col, lw=1.6))
                ax.text(xe, ye, sgn, ha="center", va="center", fontsize=10, color=col, fontweight="bold")
        # trace
        if kind == "toward":
            y = np.exp(-((t - 0.3) / 0.07) ** 2)
            txt = "upward deflection"
        elif kind == "away":
            y = -np.exp(-((t - 0.3) / 0.07) ** 2)
            txt = "downward deflection"
        else:
            y = 0 * t
            txt = "no deflection"
        axt.plot(t, y, color=C["ecg_trace"], lw=1.8)
        axt.axhline(0, color=C["axis"], lw=0.8, ls=(0, (2, 2)))
        axt.set_ylim(-1.3, 1.3)
        axt.set_xlim(0, 1)
        axt.set_xticks([])
        axt.set_yticks([])
        axt.spines["left"].set_visible(False)
        axt.spines["bottom"].set_visible(False)
        axt.text(0.5, 1.15, "recorded: " + txt, ha="center", fontsize=9, color=C["ink"])
    fs.save(fig, PART, SLUG, "two-cell.svg")


# ------------------------------------------------------------------ 2. conduction timing
def fig_conduction_timing():
    fig, (ax, axe) = plt.subplots(2, 1, figsize=(8.6, 5.8), sharex=True, gridspec_kw=dict(height_ratios=[2.2, 1], hspace=0.08))
    rows = [("SA node", 0, 15, "0.05 m/s", "not seen on the ECG", C["atrial"]),
            ("Atrial muscle", 10, 95, "about 1 m/s", "P wave", C["atrial"]),
            ("AV node", 35, 130, "0.05 m/s", "most of the PR interval", C["gold"]),
            ("His bundle and bundle branches", 128, 148, "about 1 m/s", "not seen", C["ventricular"]),
            ("Purkinje fibers", 142, 165, "about 4 m/s", "not seen", C["ventricular"]),
            ("Ventricular muscle", 155, 245, "0.3 to 1 m/s", "QRS complex", C["arterial"])]
    for i, (name, a, b, v, ecg, col) in enumerate(rows):
        yy = len(rows) - i
        ax.barh(yy, b - a, left=a, height=0.55, color=col, alpha=0.85)
        ax.text(-12, yy, name, ha="right", va="center", fontsize=9.5, color=C["ink"])
        ax.text(b + 6, yy, f"{v}; {ecg}", ha="left", va="center", fontsize=8.5, color=C["text"])
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_ylim(0.4, len(rows) + 0.6)
    ax.set_title("When each part of the conduction system is active", loc="left")
    fs.grid(ax)
    t = np.arange(-0.05, 0.62, 1e-3)
    y = E.beat(t, 0.010, pr=0.15)
    axe.plot(t * 1000, y, color=C["ecg_trace"], lw=1.6)
    axe.axhline(0, color=C["axis"], lw=0.7)
    for x0, x1, lab in [(10, 160, "PR interval"), (160, 245, "QRS")]:
        axe.annotate("", xy=(x0, -0.45), xytext=(x1, -0.45), arrowprops=dict(arrowstyle="<->", color=C["ink"], lw=1.0,
                                                                              shrinkA=0, shrinkB=0))
        axe.text((x0 + x1) / 2, -0.62, lab, ha="center", va="top", fontsize=8.5, color=C["ink"])
    axe.text(470, 1.1, "lead II", fontsize=9, color=C["ink"])
    axe.set_ylim(-0.95, 1.6)
    axe.set_ylabel("mV")
    axe.set_yticks([0, 1])
    axe.set_xlabel("Time from the first SA node action potential (ms)")
    axe.set_xlim(-60, 620)
    fs.grid(axe)
    fs.save(fig, PART, SLUG, "conduction-timing.svg")


# ------------------------------------------------------------------ 3. Einthoven triangle and hexaxial system
def fig_leads():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.6, 4.8), gridspec_kw=dict(wspace=0.15))
    ra, la, ll = np.array([-1.0, 0.0]), np.array([1.0, 0.0]), np.array([0.0, -np.sqrt(3)])
    a1.add_patch(Ellipse((0.05, -0.62), 0.55, 0.72, angle=-35, fc=C["highlight"], ec=C["ventricular"], lw=1.2))
    a1.text(0.05, -0.62, "heart", ha="center", va="center", fontsize=8.5, color=C["ventricular"])
    for p, q, name, off in [(ra, la, "I", (0, 0.16)), (ra, ll, "II", (-0.22, 0.0)), (la, ll, "III", (0.22, 0.0))]:
        a1.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=16, color=LEAD_COL[name], lw=2.0, shrinkA=10, shrinkB=10))
        mid = (p + q) / 2 + np.array(off)
        a1.text(*mid, "Lead " + name, ha="center", va="center", fontsize=10, color=LEAD_COL[name], fontweight="bold")
    for p, name in [(ra, "RA"), (la, "LA"), (ll, "LL")]:
        a1.add_patch(Circle(p, 0.09, fc="white", ec=C["ink"], lw=1.4))
        off = {"RA": (-0.2, 0.12), "LA": (0.2, 0.12), "LL": (0, -0.2)}[name]
        a1.text(p[0] + off[0], p[1] + off[1], name, ha="center", va="center", fontsize=10, color=C["ink"])
    a1.text(0, 0.55, "I = LA " + MINUS + " RA    II = LL " + MINUS + " RA    III = LL " + MINUS + " LA",
            ha="center", fontsize=9, color=C["text"])
    a1.set_xlim(-1.45, 1.45)
    a1.set_ylim(-2.05, 0.75)
    a1.set_aspect("equal")
    a1.axis("off")
    a1.set_title("A  Einthoven's triangle", loc="left")
    # hexaxial
    a2.add_patch(Circle((0, 0), 1.0, fill=False, ec=C["axis"], lw=0.8))
    for name, th in LEADS.items():
        x, y = xy(th, 1.0)
        a2.plot([0, x], [0, y], color=LEAD_COL[name], lw=2.0)
        a2.plot([0, -x], [0, -y], color=LEAD_COL[name], lw=1.0, ls=(0, (3, 3)))
        a2.plot(x, y, marker="o", ms=4, color=LEAD_COL[name])
        lx, ly = xy(th, 1.27)
        a2.text(lx, ly, f"{name}\n{deg(th)}", ha="center", va="center", fontsize=9, color=LEAD_COL[name], fontweight="bold")
    a2.text(0, -1.62, "Solid half: the lead's positive end. Angles run clockwise (downward) from lead I.",
            ha="center", fontsize=8.5, color=C["text"])
    a2.set_xlim(-1.6, 1.6)
    a2.set_ylim(-1.75, 1.6)
    a2.set_aspect("equal")
    a2.axis("off")
    a2.set_title("B  The hexaxial reference system", loc="left")
    fs.save(fig, PART, SLUG, "leads.svg")


# ------------------------------------------------------------------ 4. projection and Einthoven's law
def fig_projection():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.4, 4.6), gridspec_kw=dict(width_ratios=[1.2, 1], wspace=0.1))
    th_v = 60
    vx, vy = xy(th_v, 1.0)
    for name in ("I", "II", "III"):
        th = LEADS[name]
        x, y = xy(th, 1.25)
        a1.plot([-x, x], [-y, y], color=LEAD_COL[name], lw=1.0, ls=(0, (3, 3)))
        a1.text(*xy(th, 1.42), name, ha="center", va="center", fontsize=10, color=LEAD_COL[name], fontweight="bold")
        p = np.cos(np.radians(th_v - th))
        px, py = xy(th, p)
        a1.plot([0, px], [0, py], color=LEAD_COL[name], lw=5, alpha=0.55, solid_capstyle="butt")
        a1.plot([vx, px], [vy, py], color=C["axis"], lw=0.9, ls=(0, (1, 2)))
    a1.add_patch(FancyArrowPatch((0, 0), (vx, vy), arrowstyle="-|>", mutation_scale=18, color=C["ink"], lw=2.2))
    a1.text(vx + 0.08, vy - 0.02, "dipole vector\nat +60°", fontsize=9, color=C["ink"], va="top")
    a1.set_xlim(-1.55, 1.55)
    a1.set_ylim(-1.55, 1.4)
    a1.set_aspect("equal")
    a1.axis("off")
    a1.set_title("A  Projection on leads I, II and III", loc="left")
    # complexes
    t = np.arange(0, 0.12, 1e-3)
    for i, name in enumerate(("I", "II", "III")):
        h = np.cos(np.radians(th_v - LEADS[name]))
        y = h * np.exp(-((t - 0.05) / 0.012) ** 2)
        a2.plot(t * 1000 + i * 140, y, color=LEAD_COL[name], lw=2)
        a2.text(50 + i * 140, -0.17, f"lead {name}\n{h:.1f}", ha="center", va="top", fontsize=9.5, color=LEAD_COL[name])
    a2.axhline(0, color=C["axis"], lw=0.7)
    a2.text(190, 1.25, "I + III = II\n0.5 + 0.5 = 1.0", ha="center", fontsize=10, color=C["ink"])
    a2.set_ylim(-0.6, 1.55)
    a2.set_xlim(-20, 410)
    a2.axis("off")
    a2.set_title("B  Relative size of the deflection", loc="left")
    fs.save(fig, PART, SLUG, "projection.svg")


# ------------------------------------------------------------------ 5. QRS vector loop and leads
def fig_qrs_loop():
    comps = E.QRS_NARROW
    t = np.arange(-0.005, 0.10, 2e-4)
    x, y = E.vector(t, 0.0, comps)
    fig = plt.figure(figsize=(9.6, 5.2))
    gs = fig.add_gridspec(4, 2, width_ratios=[1.25, 1], wspace=0.15, hspace=0.35)
    ax = fig.add_subplot(gs[:, 0])
    for name, th in LEADS.items():
        lx, ly = xy(th, 1.75)
        ax.plot([-lx, lx], [-ly, ly], color=C["grid"], lw=1.0, zorder=0)
        ax.text(*xy(th, 1.92), name, ha="center", va="center", fontsize=8.5, color=LEAD_COL[name])
    ax.plot(x, -y, color=C["arterial"], lw=1.6)
    # direction arrows along the loop
    for k in (120, 260, 380):
        ax.add_patch(FancyArrowPatch((x[k], -y[k]), (x[k + 6], -y[k + 6]), arrowstyle="-|>", mutation_scale=12,
                                     color=C["arterial"], lw=0))
    picks = [(0.012, "1"), (0.040, "2"), (0.068, "3")]
    for tp, lab in picks:
        k = np.argmin(np.abs(t - tp))
        ax.add_patch(FancyArrowPatch((0, 0), (x[k], -y[k]), arrowstyle="-|>", mutation_scale=13, color=C["ink"], lw=1.4))
        r = np.hypot(x[k], y[k])
        ux, uy = x[k] / r, -y[k] / r
        ax.text(x[k] + 0.22 * ux, -y[k] + 0.22 * uy, lab, fontsize=11, fontweight="bold",
                color=C["ink"], ha="center", va="center")
    mx, my = x.sum(), y.sum()
    ang = np.degrees(np.arctan2(my, mx))
    mx2, my2 = xy(ang, 1.25)
    ax.add_patch(FancyArrowPatch((0, 0), (mx2, my2), arrowstyle="-|>", mutation_scale=16, color=C["venous"], lw=2.2,
                                 ls=(0, (4, 2))))
    ax.text(mx2 - 0.12, my2 - 0.02, f"mean QRS vector\n(MEA ≈ {deg(ang)})", fontsize=9, color=C["venous"], va="top", ha="right")
    ax.text(-1.95, -2.15, "1  septum, left to right   2  apex and free walls   3  last regions, base",
            fontsize=8.5, color=C["text"])
    ax.set_xlim(-2.05, 2.05)
    ax.set_ylim(-2.25, 2.05)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("A  The QRS vector loop in the frontal plane", loc="left")
    tt = np.arange(-0.01, 0.11, 5e-4)
    for i, name in enumerate(("I", "II", "aVF", "aVR")):
        a = fig.add_subplot(gs[i, 1])
        yy = E.wave(tt, 0.0, comps, LEADS[name])
        a.plot(tt * 1000, yy, color=LEAD_COL[name], lw=1.8)
        a.axhline(0, color=C["axis"], lw=0.7)
        a.set_ylim(-1.5, 1.6)
        a.set_xlim(-5, 95)
        a.axis("off")
        a.text(-7, 0.6, name, ha="right", va="center", fontsize=10, color=LEAD_COL[name], fontweight="bold")
        if i == 0:
            a.set_title("B  The same loop seen by four leads", loc="left")
    fs.save(fig, PART, SLUG, "qrs-loop.svg")
    return ang


# ------------------------------------------------------------------ 6. axis ranges
def fig_axis_ranges():
    fig, ax = plt.subplots(figsize=(6.6, 6.2))
    R = 1.0

    def sector(a_from, a_to, col, alpha=1.0):
        # ECG angles a_from..a_to (clockwise) -> math angles
        th1, th2 = -a_to, -a_from
        ax.add_patch(Wedge((0, 0), R, th1, th2, fc=col, ec="white", lw=2, alpha=alpha))
    sector(0, 90, "#dbe9d4")
    sector(-30, 0, "#c3dcb6")
    sector(-90, -30, "#f3d2c2")
    sector(90, 180, "#cfe0ea")
    sector(-180, -90, "#dedede")
    for name, th in LEADS.items():
        x, y = xy(th, 1.0)
        ax.plot([0, x], [0, y], color=LEAD_COL[name], lw=1.4)
        ax.text(*xy(th, 1.2), f"{name} {deg(th)}", ha="center", va="center", fontsize=8.5, color=LEAD_COL[name],
                fontweight="bold")
    for th, txt, col in [(30, "Normal\n" + MINUS + "30° to +90°", C["green"]),
                         (-15, "physiologic\nleftward axis\n" + MINUS + "30° to 0°", C["green"]),
                         (-60, "Left axis\ndeviation\nbeyond " + MINUS + "30°\n(to " + MINUS + "90°)", C["arterial"]),
                         (152, "Right axis\ndeviation\n+90° to 180°", C["venous"]),
                         (-118, "Extreme axis\n" + MINUS + "90° to 180°", C["text"])]:
        r = 0.62 if th != -15 else 0.68
        ax.text(*xy(th, r), txt, ha="center", va="center", fontsize=8.5, color=col)
    ax.plot(0, 0, "o", color=C["ink"], ms=3)
    ax.set_xlim(-1.4, 1.4)
    ax.set_ylim(-1.35, 1.35)
    ax.set_aspect("equal")
    ax.axis("off")
    fs.save(fig, PART, SLUG, "axis-ranges.svg")


# ------------------------------------------------------------------ 7. ER Doc method
def fig_axis_method():
    base = mean_axis(E.QRS_NARROW)
    cases = [(60, "Normal", "I +, II +"),
             (-15, "Physiologic leftward", "I +, II +\n(aVF is negative)"),
             (-60, "Left axis deviation", "I +, II " + MINUS),
             (120, "Right axis deviation", "I " + MINUS)]
    leads = ["I", "II", "aVF"]
    fig, axes = plt.subplots(len(leads) + 1, len(cases), figsize=(9.4, 6.0),
                             gridspec_kw=dict(height_ratios=[1, 1, 1, 0.9], hspace=0.15, wspace=0.12))
    tt = np.arange(-0.01, 0.11, 5e-4)
    for j, (target, name, rule) in enumerate(cases):
        rot = target - base
        for i, ld in enumerate(leads):
            a = axes[i, j]
            y = E.wave(tt, 0.0, E.QRS_NARROW, LEADS[ld], rot)
            net = np.trapezoid(y, tt) if hasattr(np, "trapezoid") else np.trapz(y, tt)
            col = C["green"] if net > 0 else C["arterial"]
            a.fill_between(tt * 1000, 0, y, color=col, alpha=0.15, lw=0)
            a.plot(tt * 1000, y, color=C["ecg_trace"], lw=1.6)
            a.axhline(0, color=C["axis"], lw=0.7)
            a.set_ylim(-1.6, 1.6)
            a.set_xlim(-10, 110)
            a.axis("off")
            if j == 0:
                a.text(-14, 0, ld, ha="right", va="center", fontsize=11, color=LEAD_COL[ld], fontweight="bold")
            a.text(104, 1.25, "net +" if net > 0 else "net " + MINUS, ha="right", fontsize=8, color=col)
            if i == 0:
                a.set_title(f"{name}\naxis {deg(target)}", loc="center", fontsize=10)
        a = axes[-1, j]
        a.axis("off")
        a.text(0.5, 0.75, rule, ha="center", va="top", fontsize=9.5, color=C["ink"], transform=a.transAxes)
    fs.save(fig, PART, SLUG, "axis-method.svg")


# ------------------------------------------------------------------ 8. precordial leads
TRANS = [  # transverse plane: angle 0 = patient's left, +90 = anterior
    (0.012, 0.0055, 0.0055, 115, 0.35),   # septum: rightward and anterior
    (0.034, 0.0085, 0.0080, 15, 0.85),    # apex and anterior free walls: left and anterior
    (0.050, 0.0085, 0.0085, -45, 1.35),   # left ventricular free wall: left and posterior
    (0.070, 0.0070, 0.0070, -100, 0.30),  # base: posterior
]
V_ANG = {"V1": 108, "V2": 82, "V3": 63, "V4": 45, "V5": 22, "V6": 2}


def fig_precordial():
    fig = plt.figure(figsize=(9.6, 4.6))
    gs = fig.add_gridspec(1, 2, width_ratios=[1, 1.5], wspace=0.05)
    ax = fig.add_subplot(gs[0])
    ax.add_patch(Ellipse((0, 0), 2.7, 1.9, fc="white", ec=C["axis"], lw=1.4))
    ax.add_patch(Ellipse((0.18, 0.12), 0.95, 0.75, angle=25, fc=C["highlight"], ec=C["ventricular"], lw=1.2))
    ax.text(0.2, 0.12, "heart", ha="center", va="center", fontsize=8.5, color=C["ventricular"])
    for name, th in V_ANG.items():
        r = 1.0
        x = 1.35 * np.cos(np.radians(th))
        yv = 0.95 * np.sin(np.radians(th))
        ax.plot([0.18, x], [0.12, yv], color=C["grid"], lw=1.0, zorder=0)
        ax.add_patch(Circle((x, yv), 0.07, fc="white", ec=C["venous"], lw=1.4))
        ax.text(x * 1.13, yv * 1.16 + (0.03 if th > 60 else 0), name, ha="center", va="center", fontsize=9,
                color=C["venous"], fontweight="bold")
    ax.text(-0.9, 1.12, "front", ha="center", fontsize=8.5, color=C["text"])
    ax.text(0, -1.15, "back", ha="center", fontsize=8.5, color=C["text"], va="top")
    ax.text(-1.45, 0, "patient's\nright", ha="right", va="center", fontsize=8.5, color=C["text"])
    ax.text(1.62, -0.3, "patient's\nleft", ha="left", va="center", fontsize=8.5, color=C["text"])
    ax.set_xlim(-1.9, 2.0)
    ax.set_ylim(-1.4, 1.4)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("A  Chest seen from below", loc="left")
    tt = np.arange(-0.01, 0.11, 5e-4)
    sub = gs[1].subgridspec(1, 6, wspace=0.05)
    for i, (name, th) in enumerate(V_ANG.items()):
        a = fig.add_subplot(sub[i])
        y = E.wave(tt, 0.0, TRANS, th)
        a.plot(tt * 1000, y, color=C["ecg_trace"], lw=1.6)
        a.axhline(0, color=C["axis"], lw=0.7)
        a.set_ylim(-2.2, 2.2)
        a.set_xlim(-10, 110)
        a.axis("off")
        a.text(50, 1.75, name, ha="center", fontsize=10, color=C["venous"], fontweight="bold")
        if i == 0:
            a.text(-10, 2.25, "B  R wave progression", fontsize=12, fontweight="bold", color=C["ink"], ha="left")
    fs.save(fig, PART, SLUG, "precordial.svg")


if __name__ == "__main__":
    fig_two_cell()
    fig_conduction_timing()
    fig_leads()
    fig_projection()
    print("mean axis of the standard loop:", round(fig_qrs_loop(), 1))
    fig_axis_ranges()
    fig_axis_method()
    fig_precordial()
