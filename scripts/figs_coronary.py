"""Figures for the Coronary Circulation chapter.

Run:  cd site/scripts && MPLCONFIGDIR=$TMPDIR PNG_PREVIEW=<folder> python3 figs_coronary.py
Writes SVGs to ../cardiovascular/figures/coronary/.

Numbers come from the 2025 Coronary Circulation deck: aortic pressure 80 to 90 mm Hg in
diastole and 120 in systole, LV 5 to 10 in diastole and about 120 in systole, RV about 25 in
systole (slides 24 to 32); phasic coronary flow shape from slide 33; the autoregulation plateau
from slide 43; myocardial O2 use against coronary flow from slide 45; extraction 70 to 80% at
rest from errata entry 20. Cardiac cycle 0.8 s (75 beats/min): isovolumic contraction 0.10 to
0.15 s, ejection 0.15 to 0.42 s, isovolumic relaxation 0.42 to 0.48 s.
"""
import numpy as np
from matplotlib.patches import Wedge, Circle, FancyBboxPatch, Rectangle
import figstyle as fs

plt = fs.plt
C = fs.C
M = fs.MINUS
PART, SLUG = "cardiovascular", "coronary"


def save(fig, name):
    fs.save(fig, PART, SLUG, name)


# ---------------------------------------------------------------- 1. Territories (short axis)
def fig_territories():
    fig, ax = plt.subplots(figsize=(7.4, 5.6))
    ax.set_aspect("equal")
    ax.axis("off")
    cx, cy = 0.6, 0.0
    ro, ri = 2.0, 1.15
    lad, lcx, rca = C["arterial"], C["gold"], C["venous"]
    # RV on the viewer's left (patient's right): a crescent that meets the LV at the septal edges
    rvc, rvr = (cx - 1.5, cy), 1.8
    ax.add_patch(Circle(rvc, rvr, fc="#eef3f6", ec="none"))
    ax.add_patch(Wedge(rvc, rvr + 0.17, 74, 286, width=0.34, fc=rca, ec="white", lw=1.5))
    # LV wall sectors, angles counterclockwise from the lateral wall (0 deg)
    ax.add_patch(Wedge((cx, cy), ro, 45, 200, width=ro - ri, fc=lad, ec="white", lw=2))
    ax.add_patch(Wedge((cx, cy), ro, 200, 300, width=ro - ri, fc=rca, ec="white", lw=2))
    ax.add_patch(Wedge((cx, cy), ro, 300, 405, width=ro - ri, fc=lcx, ec="white", lw=2))
    ax.add_patch(Circle((cx, cy), ri, fc="white", ec=C["axis"], lw=1))
    ax.text(cx, cy + 0.12, "LV cavity", ha="center", fontsize=9.5, color=C["text"])
    ax.text(cx - 2.68, cy, "RV\ncavity", ha="center", va="center", fontsize=9, color=C["text"])
    # orientation labels
    ax.text(cx, cy + 2.35, "anterior", ha="center", fontsize=9, color=C["text"], style="italic")
    ax.text(cx, cy - 2.45, "inferior (posterior)", ha="center", fontsize=9, color=C["text"], style="italic")
    ax.text(cx + 2.25, cy, "lateral", ha="left", va="center", fontsize=9, color=C["text"], style="italic")
    ax.text(cx - 1.55, cy + 0.0, "septum", ha="center", va="center", fontsize=8.5, color="white",
            rotation=90, fontweight="bold")
    # legend boxes
    items = [(lad, "LAD (from the left main)", "anterior wall and front of the septum"),
             (lcx, "Left circumflex (from the left main)", "lateral wall"),
             (rca, "Right coronary artery", "RV, and in right-dominant hearts the\ninferior wall and back of the septum (via the PDA)")]
    y = 2.2
    for col, name, terr in items:
        ax.add_patch(Rectangle((3.35, y - 0.17), 0.32, 0.32, fc=col, ec="none"))
        ax.text(3.8, y + 0.03, name, fontsize=9.5, color=C["ink"], fontweight="bold", va="center")
        ax.text(3.8, y - 0.36, terr, fontsize=8.8, color=C["text"], va="top")
        y -= 1.35
    ax.set_xlim(-3.2, 8.4)
    ax.set_ylim(-2.8, 2.7)
    save(fig, "territories.svg")


# ---------------------------------------------------------------- 2. Driving pressure, systole vs diastole
def fig_driving_pressure():
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.6), gridspec_kw=dict(width_ratios=[1.05, 1], wspace=0.32))
    # Panel A: LV wall schematic
    ax = axes[0]
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.6, 8)
    ax.axis("off")
    ax.set_title("A. Vessels in the left ventricular wall")
    ax.add_patch(Rectangle((0.4, 1.2), 7.0, 5.2, fc="#f3e4e4", ec="none"))
    ax.add_patch(Rectangle((0.4, 0.5), 7.0, 0.7, fc="#f7f0e6", ec="none"))
    ax.text(3.9, 0.78, "LV cavity: 5 to 10 mm Hg in diastole,\nabout 120 in systole", ha="center", va="center",
            fontsize=8.3, color=C["ventricular"])
    ax.plot([0.4, 7.4], [6.6, 6.6], color=C["arterial"], lw=6, solid_capstyle="butt")
    ax.text(0.4, 7.0, "epicardial artery (aortic pressure)", fontsize=8.8, color=C["arterial"])
    for x in (1.5, 3.9, 6.3):
        ax.plot([x, x], [6.6, 1.5], color=C["arterial"], lw=2.2)
        for yy in (5.2, 3.9, 2.6):
            ax.plot([x, x - 0.5], [yy, yy - 0.35], color=C["arterial"], lw=1)
            ax.plot([x, x + 0.5], [yy, yy - 0.35], color=C["arterial"], lw=1)
    ax.plot([0.6, 7.2], [1.5, 1.5], color=C["arterial"], lw=1.4)
    ax.text(7.6, 1.55, "subendocardial\nplexus", fontsize=8.3, color=C["arterial"], va="center", ha="left")
    ax.text(7.6, 6.0, "subepicardium", fontsize=8.3, color=C["text"], ha="left", va="center")
    ax.text(7.6, 3.9, "intramural\narteries", fontsize=8.3, color=C["text"], ha="left", va="center")
    for yy, s_ in ((5.75, 0.3), (4.45, 0.55), (3.15, 0.8), (2.0, 1.0)):
        ax.annotate("", xy=(3.75, yy), xytext=(3.75 - 0.35 - s_, yy),
                    arrowprops=dict(arrowstyle="-|>", color=C["ink"], lw=0.8 + 1.4 * s_))
        ax.annotate("", xy=(4.05, yy), xytext=(4.05 + 0.35 + s_, yy),
                    arrowprops=dict(arrowstyle="-|>", color=C["ink"], lw=0.8 + 1.4 * s_))
    ax.text(0.4, -0.35, "Arrows: systolic squeeze on the vessels, strongest near the endocardium",
            fontsize=8.3, color=C["ink"])

    # Panel B: driving pressure bars
    ax = axes[1]
    fs.grid(ax)
    aorta = dict(dia=85, sys=120)
    vent = dict(LV=dict(dia=7.5, sys=120), RV=dict(dia=7.5, sys=25))
    xs, labs, vals, cols = [], [], [], []
    for i, (v, d) in enumerate(vent.items()):
        for j, ph in enumerate(("dia", "sys")):
            x = i * 2.6 + j * 1.05
            xs.append(x)
            vals.append(max(aorta[ph] - d[ph], 0))
            labs.append("diastole" if ph == "dia" else "systole")
            cols.append(C["arterial"] if ph == "dia" else C["ventricular"])
    ax.bar(xs, vals, width=0.85, color=cols)
    notes = [f"85 {M} 7.5\n≈ 78", "120 " + M + " 120\n≈ 0", f"85 {M} 7.5\n≈ 78", f"120 {M} 25\n≈ 95"]
    for x, v, n in zip(xs, vals, notes):
        ax.text(x, v + 3, n, ha="center", va="bottom", fontsize=8.6, color=C["ink"])
    ax.set_xticks(xs)
    ax.set_xticklabels(labs, fontsize=9)
    ax.text(0.52, -19, "Left ventricle", ha="center", fontsize=10, color=C["ink"], fontweight="bold")
    ax.text(3.12, -19, "Right ventricle", ha="center", fontsize=10, color=C["ink"], fontweight="bold")
    ax.set_ylim(0, 125)
    ax.set_ylabel("Aortic minus ventricular\npressure (mm Hg)")
    ax.set_title("B. Pressure driving flow into the inner wall")
    save(fig, "driving-pressure.svg")


# ---------------------------------------------------------------- 3. Phasic coronary flow
def smooth_step(t, t0, t1):
    u = np.clip((t - t0) / (t1 - t0), 0, 1)
    return u * u * (3 - 2 * u)


def fig_phasic_flow():
    t = np.linspace(0, 0.8, 1601)
    ivc0, ej0, ej1, ivr1 = 0.10, 0.15, 0.42, 0.48
    # simpler, explicit construction of the aortic trace
    p = np.where(t < ej0, 88 - 8 * (t / ej0) ** 0.9, 0)
    rise = (t >= ej0) & (t < ej1)
    u = (t[rise] - ej0) / (ej1 - ej0)
    p[rise] = 80 + 41 * np.sin(np.pi * u / 1.25) ** 1.5
    p_end = p[rise][-1]
    after = t >= ej1
    ta = t[after] - ej1
    notch = -5 * np.sin(np.pi * np.clip(ta / 0.02, 0, 1)) + 3 * np.sin(np.pi * np.clip((ta - 0.02) / 0.04, 0, 1))
    p[after] = 80 + (p_end - 80) * np.exp(-ta / 0.45) + notch
    # Left coronary flow (mL/min)
    q_l = np.empty_like(t)
    pre = t < ivc0
    q_l[pre] = 200 - 20 * (t[pre] / ivc0)
    ivc = (t >= ivc0) & (t < ej0)
    q_l[ivc] = 180 - 175 * smooth_step(t[ivc], ivc0, ivc0 + 0.04)
    ej = (t >= ej0) & (t < ej1)
    ue = (t[ej] - ej0) / (ej1 - ej0)
    q_l[ej] = 5 + 145 * np.sin(np.pi * np.clip(ue / 0.75, 0, 1) * 0.5) ** 2 * (1 - 0.35 * smooth_step(ue, 0.55, 1.0))
    ivr = (t >= ej1) & (t < ivr1)
    q_ej_end = q_l[ej][-1]
    q_l[ivr] = q_ej_end + (370 - q_ej_end) * smooth_step(t[ivr], ej1, ivr1)
    dia = t >= ivr1
    q_l[dia] = 370 - (370 - 200) * ((t[dia] - ivr1) / (0.8 - ivr1)) ** 0.8
    # Right coronary flow: follows aortic pressure, small dip in isovolumic contraction
    q_r = 40 + 0.9 * (p - 85)
    q_r = q_r - 14 * np.exp(-((t - 0.125) / 0.018) ** 2) - 6 * np.exp(-((t - 0.425) / 0.012) ** 2)

    fig, axes = plt.subplots(3, 1, figsize=(8.0, 7.4), sharex=True,
                             gridspec_kw=dict(height_ratios=[1, 1.25, 0.95], hspace=0.12))
    for ax in axes:
        ax.axvspan(ivc0, ej1, color=C["highlight"], zorder=0, lw=0)
        ax.axvspan(ivc0, ej0, color="#efd6d0", zorder=0, lw=0)
        ax.axvspan(ej1, ivr1, color="#e2ecd9", zorder=0, lw=0)
        fs.grid(ax)
    axes[0].plot(t, p, color=C["arterial"], lw=2.2)
    axes[0].set_ylabel("Aortic pressure\n(mm Hg)")
    axes[0].set_ylim(70, 130)
    axes[1].plot(t, q_l, color=C["ventricular"], lw=2.2)
    axes[1].set_ylabel("Left coronary flow\n(mL/min)")
    axes[1].set_ylim(0, 420)
    axes[2].plot(t, q_r, color=C["venous"], lw=2.2)
    axes[2].set_ylabel("Right coronary flow\n(mL/min)")
    axes[2].set_ylim(0, 80)
    axes[2].set_xlabel("Time (s)")
    axes[2].set_xlim(0, 0.8)
    top = axes[0]
    top.text(0.05, 126, "diastole", ha="center", fontsize=9, color=C["text"])
    top.text(0.26, 126, "systole", ha="center", fontsize=9, color=C["text"])
    top.text(0.64, 126, "diastole", ha="center", fontsize=9, color=C["text"])
    axes[1].annotate("near zero in isovolumic\ncontraction", xy=(0.14, 8), xytext=(0.17, 290),
                     fontsize=8.6, color=C["ink"], arrowprops=dict(arrowstyle="-", color=C["ink"], lw=0.8))
    axes[1].annotate("peak early in diastole,\nas the muscle relaxes", xy=(0.485, 368), xytext=(0.55, 380),
                     fontsize=8.6, color=C["ink"], va="center", arrowprops=dict(arrowstyle="-", color=C["ink"], lw=0.8))
    axes[2].text(0.20, 12, "flow continues through systole", fontsize=8.6, color=C["ink"])
    fig.text(0.13, 0.005, "Tan: systole, with isovolumic contraction darker. Green: isovolumic relaxation, the first part of diastole.",
             fontsize=8.3, color=C["text"])
    save(fig, "phasic-flow.svg")


# ---------------------------------------------------------------- 4. Autoregulation
def fig_autoregulation():
    P = np.linspace(40, 140, 300)
    lo, hi = 60, 120
    q_plateau = lambda x: 0.42 + 0.0015 * (x - lo)       # gentle slope across the range
    Q = np.where(P < lo, q_plateau(lo) * P / lo,
                 np.where(P > hi, q_plateau(hi) * P / hi, q_plateau(P)))
    R = P / Q
    fig, ax = plt.subplots(figsize=(7.4, 4.8))
    fs.grid(ax)
    ax.axvspan(lo, hi, color=C["cool"], zorder=0)
    ax.plot(P, Q, color=C["arterial"], lw=2.6)
    ax.set_xlabel("Coronary perfusion pressure (mm Hg)")
    ax.set_ylabel("Coronary blood flow (mL/min/g)", color=C["arterial"])
    ax.set_ylim(0, 0.9)
    ax.set_xlim(40, 140)
    ax2 = ax.twinx()
    ax2.plot(P, R, color=C["venous"], lw=2, ls=(0, (5, 3)))
    ax2.set_ylabel("Coronary vascular resistance\n(mm Hg per mL/min/g)", color=C["venous"])
    ax2.spines["right"].set_visible(True)
    ax2.set_ylim(0, 260)
    ax.text(90, 0.82, "autoregulatory range", ha="center", fontsize=9.5, color=C["ink"])
    ax.text(124, 0.64, "flow", color=C["arterial"], fontsize=10, fontweight="bold")
    ax2.text(80, 213, "resistance", color=C["venous"], fontsize=10, fontweight="bold")
    ax.text(41.5, 0.05, "maximally dilated:\nflow follows pressure", fontsize=8.5, color=C["text"])
    ax.text(121.5, 0.05, "maximally constricted:\nflow follows pressure", fontsize=8.5, color=C["text"])
    save(fig, "autoregulation.svg")


# ---------------------------------------------------------------- 5. Extraction and demand
def fig_demand():
    fig, axes = plt.subplots(1, 2, figsize=(10.0, 4.4), gridspec_kw=dict(width_ratios=[0.8, 1.2]))
    ax = axes[0]
    fs.grid(ax)
    ax.bar([0, 1], [75, 25], width=0.6, color=[C["arterial"], C["gray"]])
    ax.errorbar([0], [75], yerr=[[5], [5]], color=C["ink"], capsize=5, lw=1)
    ax.bar([0], [25], bottom=75, width=0.6, color="none", ec=C["arterial"], ls=(0, (3, 2)), lw=1.2)
    ax.text(0, 88, "little room\nto rise", ha="center", fontsize=8.8, color=C["arterial"])
    ax.text(0, 37, "70 to 80%", ha="center", color="white", fontsize=9.5, fontweight="bold")
    ax.text(1, 12, "about 25%", ha="center", color="white", fontsize=9.5, fontweight="bold")
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Heart", "Whole body"])
    ax.set_ylim(0, 100)
    ax.set_ylabel("O$_2$ extraction at rest (% of O$_2$ delivered)")
    ax.set_title("A. Extraction is already high")

    ax = axes[1]
    fs.grid(ax)
    q = np.linspace(20, 120, 50)
    cao2, ext = 0.20, 0.70          # mL O2 per mL blood; fraction extracted
    ax.plot(q, q * cao2 * ext, color=C["arterial"], lw=2.6)
    ax.set_xlabel("Coronary blood flow (mL/min/100 g)")
    ax.set_ylabel("Myocardial O$_2$ consumption\n(mL/min/100 g)")
    ax.set_xlim(15, 125)
    ax.set_ylim(0, 20)
    ax.set_title("B. So flow rises in step with O$_2$ use")
    ax.text(22, 17.2, "O$_2$ use = flow × CaO$_2$ (20 mL/dL) × extraction (0.7)",
            fontsize=8.6, color=C["ink"])
    fig.subplots_adjust(wspace=0.35)
    save(fig, "demand.svg")


# ---------------------------------------------------------------- 6. ST changes on ECG paper
def beat(t, st=0.0, t_amp=0.3):
    """One synthetic beat (mV) at time t (s) from the start of the beat."""
    g = lambda c, w, a: a * np.exp(-((t - c) / w) ** 2)
    v = g(0.10, 0.025, 0.12)                                 # P
    v += g(0.235, 0.008, -0.12) + g(0.255, 0.010, 1.3) + g(0.275, 0.009, -0.30)   # QRS
    seg = smooth_step(t, 0.268, 0.29) * (1 - smooth_step(t, 0.38, 0.50))
    v += st * seg
    v += g(0.46, 0.05, t_amp) * (1 if st >= 0 else 1)
    return v


def fig_st():
    fig, axes = plt.subplots(1, 3, figsize=(10.2, 3.2))
    cases = [("A. Normal", 0.0, 0.3), ("B. ST depression", -0.2, 0.15), ("C. ST elevation", 0.3, 0.45)]
    dur = 0.8
    for ax, (title, st, ta) in zip(axes, cases):
        x0, x1, y0, y1 = 0, dur, -0.6, 1.6
        for xm in np.arange(x0, x1 + 1e-9, 0.04):
            ax.axvline(xm, color=C["ecg_minor"], lw=0.5, zorder=0)
        for ym in np.arange(y0, y1 + 1e-9, 0.1):
            ax.axhline(ym, color=C["ecg_minor"], lw=0.5, zorder=0)
        for xm in np.arange(x0, x1 + 1e-9, 0.2):
            ax.axvline(xm, color=C["ecg_major"], lw=1.0, zorder=0)
        for ym in np.arange(y0, y1 + 1e-9, 0.5):
            ax.axhline(ym, color=C["ecg_major"], lw=1.0, zorder=0)
        t = np.linspace(0, dur, 1600)
        ax.plot(t, beat(t, st, ta), color=C["ecg_trace"], lw=1.6)
        ax.set_xlim(x0, x1)
        ax.set_ylim(y0, y1)
        ax.set_aspect(0.4 / 1.0)   # 0.04 s per mm and 0.1 mV per mm: 25 mm/s, 10 mm/mV
        ax.set_xticks([])
        ax.set_yticks([])
        for s in ax.spines.values():
            s.set_visible(False)
        ax.set_title(title, fontsize=11)
    axes[1].text(0.40, -0.52, "subendocardial ischemia", ha="center", fontsize=8.6, color=C["ink"])
    axes[2].text(0.40, -0.52, "transmural injury", ha="center", fontsize=8.6, color=C["ink"])
    fig.text(0.5, 0.0, "Synthetic traces on standard paper: 25 mm/s, 10 mm/mV (small box 40 ms and 0.1 mV).",
             ha="center", fontsize=8.5, color=C["text"])
    save(fig, "st-changes.svg")


if __name__ == "__main__":
    fig_territories()
    fig_driving_pressure()
    fig_phasic_flow()
    fig_autoregulation()
    fig_demand()
    fig_st()
