"""Figures for EKG III: Clinical Interpretation (cardiovascular/ecg-interpretation.qmd).

Run:  cd site/scripts && MPLCONFIGDIR=$TMPDIR PNG_PREVIEW=<folder> python3 figs_ecg-interpretation.py

The first half of this file is a small synthetic-ECG library that the ECG II script also loads.
A beat is built the way the ECG II chapter explains it: each wave is a cardiac dipole vector that
grows and shrinks in time with a fixed direction in the frontal plane, and a lead records the
projection of that vector on the lead's axis (V = |v| cos(angle - lead angle)). Angles use the
ECG convention: 0 degrees is lead I (toward the left arm), positive angles point downward.

Strips are drawn on standard paper: 1 mm minor and 5 mm major boxes, 25 mm/s and 10 mm/mV,
so one small box is 0.04 s by 0.1 mV and one large box is 0.2 s by 0.5 mV.
"""
import numpy as np
import figstyle as fs
from figstyle import C, plt, MINUS

PART, SLUG = "cardiovascular", "ecg-interpretation"
FS = 1000  # samples per second

# frontal-plane lead angles (degrees, ECG convention)
LEADS = {"I": 0, "II": 60, "III": 120, "aVR": -150, "aVL": -30, "aVF": 90}

# ------------------------------------------------------------------ wave components
# Each component: (time of peak after wave onset [s], sd before peak, sd after peak, angle [deg], amplitude [mV])
P_WAVE = [(0.045, 0.020, 0.020, 60, 0.15)]
QRS_NARROW = [
    (0.012, 0.0055, 0.0055, 170, 0.22),   # septum, left to right
    (0.032, 0.0085, 0.0080, 25, 0.95),    # apex and free walls, early
    (0.047, 0.0085, 0.0090, 80, 1.00),    # free walls, later and more inferior
    (0.068, 0.0070, 0.0070, -120, 0.24),  # last regions, posterobasal and superior
]
T_NORMAL = [(0.0, 0.050, 0.032, 45, 0.33)]          # placed by its peak time
QRS_PVC = [(0.045, 0.020, 0.022, 75, 1.45), (0.110, 0.022, 0.025, 250, 0.55)]
T_PVC = [(0.0, 0.045, 0.040, 250, 0.45)]
QRS_BBB = [(0.035, 0.017, 0.013, 65, 0.85), (0.088, 0.016, 0.018, 45, 1.0)]
T_BBB = [(0.0, 0.050, 0.035, 230, 0.22)]


def skew_gauss(t, mu, s1, s2):
    return np.where(t < mu, np.exp(-0.5 * ((t - mu) / s1) ** 2), np.exp(-0.5 * ((t - mu) / s2) ** 2))


def wave(t, t0, comps, lead=60, rot=0.0, scale=1.0):
    """Projection on a lead (angle in degrees) of a set of dipole components starting at t0."""
    y = np.zeros_like(t)
    for (tp, s1, s2, ang, amp) in comps:
        y += scale * amp * np.cos(np.radians(ang + rot - lead)) * skew_gauss(t, t0 + tp, s1, s2)
    return y


def vector(t, t0, comps, rot=0.0):
    """Frontal-plane vector (x to the patient's left, y downward) of a set of components."""
    x = np.zeros_like(t)
    y = np.zeros_like(t)
    for (tp, s1, s2, ang, amp) in comps:
        g = amp * skew_gauss(t, t0 + tp, s1, s2)
        x += g * np.cos(np.radians(ang + rot))
        y += g * np.sin(np.radians(ang + rot))
    return x, y


def beat(t, t_p, pr=0.16, lead=60, p=True, p_angle=60, p_scale=1.0, qrs="narrow", rot=0.0, qt=0.38, t_scale=1.0):
    """One beat. t_p is P onset (or the QRS onset minus pr if p is False)."""
    y = np.zeros_like(t)
    if p:
        y += wave(t, t_p, [(0.045, 0.020, 0.020, p_angle, 0.15 * p_scale)], lead)
    tq = t_p + pr
    if qrs == "narrow":
        y += wave(t, tq, QRS_NARROW, lead, rot)
        y += wave(t, tq + qt - 0.075, T_NORMAL, lead, rot, t_scale)
    elif qrs == "pvc":
        y += wave(t, tq, QRS_PVC, lead, rot)
        y += wave(t, tq + qt - 0.08, T_PVC, lead, rot, t_scale)
    elif qrs == "bbb":
        y += wave(t, tq, QRS_BBB, lead, rot)
        y += wave(t, tq + qt - 0.075, T_BBB, lead, rot, t_scale)
    return y


def p_only(t, t_p, lead=60, p_angle=60, p_scale=1.0):
    return wave(t, t_p, [(0.045, 0.020, 0.020, p_angle, 0.15 * p_scale)], lead)


def timebase(dur):
    return np.arange(0, dur, 1.0 / FS)


# ------------------------------------------------------------------ paper
def paper(ax, t0, t1, y0, y1, minor=True):
    """Standard ECG paper from t0 to t1 seconds and y0 to y1 mV, at 25 mm/s and 10 mm/mV."""
    if minor:
        for x in np.arange(np.ceil(t0 / 0.04) * 0.04, t1 + 1e-9, 0.04):
            ax.axvline(x, color=C["ecg_minor"], lw=0.45, zorder=0)
        for y in np.arange(np.ceil(y0 / 0.1) * 0.1, y1 + 1e-9, 0.1):
            ax.axhline(y, color=C["ecg_minor"], lw=0.45, zorder=0)
    for x in np.arange(np.ceil(t0 / 0.2 - 1e-9) * 0.2, t1 + 1e-9, 0.2):
        ax.axvline(x, color=C["ecg_major"], lw=0.9, zorder=0)
    for y in np.arange(np.ceil(y0 / 0.5 - 1e-9) * 0.5, y1 + 1e-9, 0.5):
        ax.axhline(y, color=C["ecg_major"], lw=0.9, zorder=0)
    ax.set_xlim(t0, t1)
    ax.set_ylim(y0, y1)
    ax.set_aspect(0.4)  # 1 s = 25 mm and 1 mV = 10 mm
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)


def cal_pulse(t, start=0.04, width=0.2):
    """1 mV calibration pulse, 0.2 s wide."""
    return np.where((t >= start) & (t < start + width), 1.0, 0.0)


def trace(ax, t, y, lw=1.25, **kw):
    ax.plot(t, y, color=C["ecg_trace"], lw=lw, solid_joinstyle="round", **kw)


def strip_axes(n, dur, y0=-0.8, y1=1.7, width_scale=1.0, hspace=0.35):
    """n strips of dur seconds stacked vertically; figure sized so paper is true to scale ratio."""
    w = dur * 25 / 25.4 * 1.5 * width_scale        # inches, 1.5 times true size
    h_one = (y1 - y0) * 10 / 25.4 * 1.5 * width_scale
    fig, axes = plt.subplots(n, 1, figsize=(w, n * h_one + (n - 1) * 0.42 + 0.2))
    if n == 1:
        axes = [axes]
    for ax in axes:
        paper(ax, 0, dur, y0, y1)
    fig.subplots_adjust(hspace=hspace, left=0.01, right=0.99, top=0.95, bottom=0.02)
    return fig, axes


def label(ax, txt, x=0.0, y=1.02, size=10, color=None):
    """Strip title, just above the paper."""
    ax.text(x, y, txt, transform=ax.transAxes, ha="left", va="bottom", fontsize=size, color=color or C["ink"],
            fontweight="bold", zorder=5)


def note(ax, x, y, txt, size=8.5, ha="center", color=None):
    ax.text(x, y, txt, ha=ha, va="center", fontsize=size, color=color or C["ink"],
            bbox=dict(fc="white", ec="none", pad=1.0, alpha=0.9), zorder=5)


def rhythm(t, rr, pr=0.16, start=0.35, **kw):
    """Regular sinus-type rhythm. rr in s; first P onset at start."""
    y = np.zeros_like(t)
    tp = start
    while tp < t[-1] + 0.2:
        y += beat(t, tp, pr=pr, **kw)
        tp += rr
    return y


# ================================================================== chapter figures
def fig_paper_beat():
    t = np.arange(0, 1.6, 1 / FS)
    tp, tq = 0.50, 0.66
    y = cal_pulse(t, 0.04) + beat(t, tp, pr=0.16)
    fig, ax = plt.subplots(figsize=(9.6, 6.2))
    paper(ax, 0, 1.6, -0.9, 1.8)
    trace(ax, t, y, lw=1.6)
    qrs_end = tq + 0.085
    t_end = tq + 0.38
    i_s = np.argmin(np.where((t > tq + 0.05) & (t < tq + 0.1), y, 9))
    i_q = np.argmin(np.where((t > tq) & (t < tq + 0.03), y, 9))
    note(ax, tp + 0.045, 0.30, "P")
    note(ax, t[i_q] - 0.035, y[i_q] - 0.02, "Q")
    note(ax, tq + 0.040, 1.30, "R")
    note(ax, t[i_s] + 0.035, y[i_s] - 0.02, "S")
    note(ax, tq + 0.305, 0.50, "T")

    def bar(x0, x1, yb, txt, col, txtdy=0.0, size=8.5):
        ax.annotate("", xy=(x0, yb), xytext=(x1, yb), arrowprops=dict(arrowstyle="<->", color=col, lw=1.4, shrinkA=0, shrinkB=0))
        ax.text((x0 + x1) / 2, yb + txtdy, txt, ha="center", va="center", fontsize=size, color=col,
                bbox=dict(fc="white", ec="none", pad=0.8, alpha=0.9))
    for x in (tp, tq, qrs_end, t_end):
        ax.plot([x, x], [-0.78, 0.0], color=C["axis"], lw=0.8, ls=(0, (2, 2)), zorder=2)
    bar(tp, tq, -0.45, "PR interval", C["arterial"], -0.11)
    bar(tq, qrs_end, -0.45, "QRS", C["venous"], -0.11)
    bar(tq, t_end, -0.72, "QT interval", C["ventricular"], 0.0)
    bar(tp + 0.095, tq, 0.22, "PR\nsegment", C["green"], 0.16, 8)
    bar(qrs_end, tq + 0.20, 0.22, "ST\nsegment", C["purple"], 0.16, 8)
    ax.annotate("J point", xy=(qrs_end, 0.0), xytext=(qrs_end + 0.10, -0.22), fontsize=8.5, color=C["ink"],
                arrowprops=dict(arrowstyle="->", color=C["ink"], lw=0.9),
                bbox=dict(fc="white", ec="none", pad=0.8, alpha=0.9))
    note(ax, 0.14, 1.15, "1 mV calibration\n(10 mm tall)", size=8)
    ax.add_patch(plt.Rectangle((1.2, 1.0), 0.2, 0.5, fill=False, ec=C["arterial"], lw=1.8, zorder=4))
    ax.add_patch(plt.Rectangle((1.2, 0.5), 0.04, 0.1, fill=True, fc=C["arterial"], ec=C["arterial"], lw=1.0, zorder=4, alpha=0.6))
    note(ax, 1.30, 1.62, "large box: 5 mm\n0.2 s and 0.5 mV", size=8)
    note(ax, 1.36, 0.42, "small box: 1 mm\n0.04 s and 0.1 mV", size=8)
    fs.save(fig, PART, SLUG, "paper-beat.svg")


def fig_rate():
    dur = 4.0
    t = timebase(dur)
    rr = 0.8
    # put an R peak (QRS onset + 0.04) on a heavy line: QRS onset at 0.56 -> R at 0.60
    y = rhythm(t, rr, pr=0.16, start=0.40)
    fig, axes = strip_axes(1, dur, -0.6, 2.1)
    ax = axes[0]
    trace(ax, t, y)
    label(ax, "II")
    r0 = 0.60
    for k, lab in enumerate(["300", "150", "100", "75", "60", "50"], start=1):
        x = r0 + 0.2 * k
        ax.text(x, 1.88, lab, ha="center", va="center", fontsize=8, color=C["arterial"],
                bbox=dict(fc="white", ec="none", pad=0.6, alpha=0.9))
    ax.annotate("", xy=(r0, 1.5), xytext=(r0 + rr, 1.5), arrowprops=dict(arrowstyle="<->", color=C["venous"], lw=1.3,
                                                                           shrinkA=0, shrinkB=0))
    note(ax, r0 + rr / 2, 1.22, "R-R = 4 large boxes\n= 0.8 s", size=8, color=C["venous"])
    note(ax, 2.6, 1.45, "60 / 0.8 s = 75 per minute\n300 / 4 = 75 per minute", size=8.5)
    fs.save(fig, PART, SLUG, "rate.svg")


def fig_sinus():
    dur = 6.0
    t = timebase(dur)
    fig, axes = strip_axes(3, dur, -0.6, 1.8)
    runs = [(0.8, "A  Normal sinus rhythm, 75 per minute", {}),
            (0.4, "B  Sinus tachycardia, 150 per minute", dict(pr=0.13, qt=0.28)),
            (1.4, "C  Sinus bradycardia, about 43 per minute", dict(qt=0.42))]
    for ax, (rr, lab, kw) in zip(axes, runs):
        y = rhythm(t, rr, start=0.30, **kw)
        trace(ax, t, y)
        label(ax, "II   " + lab)
    fs.save(fig, PART, SLUG, "sinus.svg")


def fig_ectopy():
    dur = 6.0
    t = timebase(dur)
    fig, axes = strip_axes(3, dur, -1.1, 1.8)
    # A: sinus 75 with two PVCs
    y = np.zeros_like(t)
    rr = 0.8
    times = [0.25 + k * rr for k in range(8)]
    pvc_at = {2, 6}
    for k, tp in enumerate(times):
        if k in pvc_at:
            # PVC comes early (before the next sinus P), no P wave before it
            y += beat(t, tp - 0.30, pr=0.16, p=False, qrs="pvc", qt=0.42)
            # the sinus P still fires on time but finds the ventricles refractory (hidden in the PVC)
            y += p_only(t, tp)
        else:
            y += beat(t, tp, pr=0.16)
    trace(ax := axes[0], t, y)
    label(ax, "II   A  Sinus rhythm with premature ventricular contractions (PVCs)")
    for k in pvc_at:
        note(ax, times[k] - 0.30 + 0.16 + 0.07, -0.95, "PVC: early, wide,\nno P before it", size=8)
    # B: ectopic atrial rhythm: P inverted in lead II (vector pointing up, from low atrium)
    y = rhythm(t, 0.86, pr=0.15, start=0.30, p_angle=-100, p_scale=1.4)
    trace(ax := axes[1], t, y)
    label(ax, "II   B  Ectopic atrial rhythm: every P is negative in lead II")
    # C: multifocal atrial tachycardia: P shapes and PR vary, rate about 120, irregular
    rng = np.random.default_rng(4)
    y = np.zeros_like(t)
    tp = 0.25
    shapes = [(60, 1.6, 0.16), (-100, 1.7, 0.13), (5, 2.2, 0.20), (100, 0.9, 0.14)]
    k = 0
    while tp < dur:
        ang, sc, pr = shapes[k % 4]
        y += beat(t, tp, pr=pr, p_angle=ang, p_scale=sc, qt=0.30)
        tp += rng.uniform(0.42, 0.60)
        k += 1
    trace(ax := axes[2], t, y)
    label(ax, "II   C  Multifocal atrial tachycardia: P waves of several shapes, irregular, over 100 per minute")
    fs.save(fig, PART, SLUG, "ectopy.svg")


def fig_av_blocks():
    dur = 7.0
    t = timebase(dur)
    fig, axes = strip_axes(5, dur, -0.6, 1.7)
    pp = 0.8
    # A: first degree
    y = rhythm(t, pp, pr=0.30, start=0.25)
    trace(ax := axes[0], t, y)
    label(ax, "II   A  First-degree AV block: PR 0.30 s, every P conducts")
    ax.annotate("", xy=(0.25, 0.5), xytext=(0.55, 0.5), arrowprops=dict(arrowstyle="<->", color=C["arterial"], lw=1.2,
                                                                         shrinkA=0, shrinkB=0))
    note(ax, 0.40, 0.68, "PR", size=8, color=C["arterial"])
    # B: Mobitz I (Wenckebach) 4:3
    y = np.zeros_like(t)
    prs = [0.16, 0.26, 0.32, None]
    marks = []
    for k in range(9):
        tp = 0.25 + k * pp
        pr = prs[k % 4]
        if pr is None:
            y += p_only(t, tp)
            marks.append(tp)
        else:
            y += beat(t, tp, pr=pr)
    trace(ax := axes[1], t, y)
    label(ax, "II   B  Second-degree, Mobitz I (Wenckebach): PR lengthens until a P is not conducted")
    for m in marks:
        ax.annotate("", xy=(m + 0.045, 0.22), xytext=(m + 0.045, 0.62), arrowprops=dict(arrowstyle="->", color=C["arterial"], lw=1.2))
    # C: Mobitz II: constant PR, occasional non-conducted P, wide QRS
    y = np.zeros_like(t)
    marks = []
    for k in range(9):
        tp = 0.25 + k * pp
        if k in (3, 7):
            y += p_only(t, tp)
            marks.append(tp)
        else:
            y += beat(t, tp, pr=0.18, qrs="bbb", qt=0.42)
    trace(ax := axes[2], t, y)
    label(ax, "II   C  Second-degree, Mobitz II: constant PR, then a P that is not conducted (here with a wide QRS)")
    for m in marks:
        ax.annotate("", xy=(m + 0.045, 0.22), xytext=(m + 0.045, 0.62), arrowprops=dict(arrowstyle="->", color=C["arterial"], lw=1.2))
    # D: 2:1
    y = np.zeros_like(t)
    for k in range(9):
        tp = 0.25 + k * pp
        y += beat(t, tp, pr=0.18) if k % 2 == 0 else p_only(t, tp)
    trace(ax := axes[3], t, y)
    label(ax, "II   D  2:1 AV block: every second P is not conducted, so the type cannot be told")
    # E: third degree: P at 90/min, narrow escape at 42/min
    y = np.zeros_like(t)
    tp = 0.12
    ptimes = []
    while tp < dur:
        y += p_only(t, tp)
        ptimes.append(tp)
        tp += 60 / 90
    tq = 0.55
    while tq < dur:
        y += beat(t, tq - 0.16, pr=0.16, p=False, qt=0.44)
        tq += 60 / 42
    trace(ax := axes[4], t, y)
    label(ax, "II   E  Third-degree (complete) AV block: P waves at 90 and QRS complexes at 42 per minute, unrelated")
    for m in ptimes:
        ax.plot(m + 0.045, -0.35, marker="^", ms=4.5, color=C["arterial"], zorder=4)
    fs.save(fig, PART, SLUG, "av-blocks.svg")


def fig_qt_torsades():
    # A: long QT measurement, rate about 94 (RR 0.64 s), QT 0.40 s
    dur = 3.0
    t = timebase(dur)
    fig = plt.figure(figsize=(8.8, 5.2))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.1, 1], hspace=0.25)
    ax = fig.add_subplot(gs[0])
    paper(ax, 0, dur, -0.6, 1.9)
    rr, qt = 0.64, 0.40
    y = rhythm(t, rr, pr=0.16, start=0.04, qt=qt)
    trace(ax, t, y)
    label(ax, "II   A  Measuring a long QT")
    q0 = 0.04 + rr + 0.16   # QRS onset of the second beat
    ax.annotate("", xy=(q0, -0.32), xytext=(q0 + qt, -0.32), arrowprops=dict(arrowstyle="<->", color=C["ventricular"],
                                                                              lw=1.3, shrinkA=0, shrinkB=0))
    note(ax, q0 + qt / 2, -0.48, "QT = 0.40 s", size=8, color=C["ventricular"])
    r0 = q0 + 0.04
    ax.annotate("", xy=(r0, 1.58), xytext=(r0 + rr, 1.58), arrowprops=dict(arrowstyle="<->", color=C["venous"],
                                                                            lw=1.3, shrinkA=0, shrinkB=0))
    note(ax, r0 + rr / 2, 1.75, "R-R = 0.64 s", size=8, color=C["venous"])
    note(ax, 2.48, 1.15, "QTc = QT / √RR\n= 0.40 / 0.8\n= 0.50 s (500 ms)", size=8.5)
    # B: torsades de pointes
    dur2 = 6.0
    t2 = timebase(dur2)
    ax2 = fig.add_subplot(gs[1])
    paper(ax2, 0, dur2, -1.6, 1.7)
    y2 = beat(t2, 0.05, pr=0.16, qt=0.48)
    # wide complexes at about 240 per minute, amplitude envelope that swings through zero (twisting)
    tt = t2 - 0.66   # the run starts on the down-slope of the T wave
    carrier = np.where(tt > 0, np.sin(2 * np.pi * 4.0 * tt) + 0.35 * np.sin(2 * np.pi * 8.0 * tt + 0.6), 0)
    env = np.where(tt > 0, 1.25 * np.cos(2 * np.pi * tt / 2.6) * (1 - np.exp(-tt / 0.15)), 0)
    env = np.where(np.abs(env) < 0.25, np.sign(env + 1e-9) * 0.25, env) * (tt > 0)
    y2 = y2 + carrier * env
    trace(ax2, t2, y2, lw=1.1)
    label(ax2, "II   B  Torsades de pointes: QRS complexes that twist around the baseline")
    fs.save(fig, PART, SLUG, "qt-torsades.svg")


def fig_t_wave():
    """Endocardial and epicardial action potentials and their difference."""
    import importlib.util, os
    spec = importlib.util.spec_from_file_location("ionic", os.path.join(os.path.dirname(__file__), "figs_ecg-ionic-basis.py"))
    ionic = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ionic)
    t = np.linspace(-0.05, 0.50, 5000)
    v_endo = ionic.fast_ap(t, apd=0.30, t0=0.0)
    v_epi = ionic.fast_ap(t, apd=0.24, t0=0.012)
    fig, axes = plt.subplots(2, 1, figsize=(7.6, 5.6), sharex=True, gridspec_kw=dict(height_ratios=[1.5, 1], hspace=0.12))
    ax = axes[0]
    ax.plot(t * 1000, v_endo, color=C["ventricular"], lw=2.0, label="endocardial cell: depolarizes first, repolarizes last")
    ax.plot(t * 1000, v_epi, color=C["venous"], lw=2.0, ls=(0, (5, 2)),
            label="epicardial cell: depolarizes later, repolarizes first")
    ax.set_ylabel("Membrane potential (mV)")
    ax.set_ylim(-100, 60)
    ax.set_yticks([-90, -60, -30, 0, 30])
    ax.set_yticklabels([fs.fmt(v) for v in [-90, -60, -30, 0, 30]])
    ax.legend(loc="upper right", fontsize=8.5)
    fs.grid(ax)
    ax = axes[1]
    d = (v_endo - v_epi) / 100.0
    ax.plot(t * 1000, d, color=C["ecg_trace"], lw=1.8)
    ax.axhline(0, color=C["axis"], lw=0.8)
    ax.set_ylabel("Endo minus epi\n(relative)")
    ax.set_yticks([0])
    ax.set_xlabel("Time (ms)")
    ax.text(14, 0.85, "QRS: depolarization\nmoves endo to epi", fontsize=8.5, color=C["text"], va="top", ha="left")
    ax.text(335, 0.95, "T: repolarization moves\nepi to endo, so the\nT wave is also upright", fontsize=8.5,
            color=C["text"], va="top", ha="left")
    ax.set_ylim(-0.2, 1.25)
    ax.set_xlim(-50, 500)
    fs.grid(ax)
    fs.save(fig, PART, SLUG, "t-wave.svg")


def fig_tachy():
    dur = 6.0
    t = timebase(dur)
    rng = np.random.default_rng(7)
    fig, axes = strip_axes(4, dur, -1.4, 1.8)
    # A: atrial fibrillation: fibrillatory baseline, irregularly irregular narrow QRS
    base = np.zeros_like(t)
    for f in rng.uniform(5, 9, 7):
        base += rng.uniform(0.012, 0.028) * np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28))
    y = base.copy()
    tq = 0.2
    while tq < dur:
        y += beat(t, tq - 0.16, p=False, qt=0.32)
        tq += rng.uniform(0.38, 0.95)
    trace(ax := axes[0], t, y)
    label(ax, "II   A  Atrial fibrillation: no P waves, irregularly irregular")
    # B: atrial flutter, sawtooth at 300 per minute with 4:1 conduction
    ff = 5.0
    phase = (t * ff) % 1.0
    saw = -0.35 * np.where(phase < 0.8, phase / 0.8, 1 - (phase - 0.8) / 0.2) + 0.17
    y = saw.copy()
    for k in range(int(dur * ff / 4) + 1):
        y += beat(t, 0.10 + k * 0.8, pr=0.24, p=False, qt=0.36)
    trace(ax := axes[1], t, y)
    label(ax, "II   B  Atrial flutter: sawtooth flutter waves at about 300 per minute, here every fourth one conducted")
    # C: monomorphic VT, about 160 per minute
    y = np.zeros_like(t)
    tq = 0.15
    while tq < dur:
        y += beat(t, tq - 0.16, p=False, qrs="pvc", qt=0.30, t_scale=0.8)
        tq += 0.375
    trace(ax := axes[2], t, y)
    label(ax, "II   C  Ventricular tachycardia: regular, wide QRS complexes, about 160 per minute")
    # D: VF
    y = np.zeros_like(t)
    for f in rng.uniform(3.5, 7.0, 6):
        y += rng.uniform(0.15, 0.35) * np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28))
    y *= 0.8 + 0.4 * np.sin(2 * np.pi * t / 3.7)
    trace(ax := axes[3], t, y)
    label(ax, "II   D  Ventricular fibrillation: chaotic, no organized QRS complexes")
    fs.save(fig, PART, SLUG, "tachyarrhythmias.svg")


if __name__ == "__main__":
    fig_paper_beat()
    fig_rate()
    fig_sinus()
    fig_ectopy()
    fig_av_blocks()
    fig_qt_torsades()
    fig_t_wave()
    fig_tachy()
