"""Figures for the Cardiovascular Adaptation to Exercise chapter.

Run:  cd site/scripts && MPLCONFIGDIR=$TMPDIR PNG_PREVIEW=<folder> python3 figs_cv-exercise.py
Writes SVGs to ../cardiovascular/figures/cv-exercise/.

The cardiac and vascular function curves are imported from figs_control-of-co.py so they match
the earlier chapters. Exercise numbers follow the lecture: VO2 3.5 to 35 mL/kg/min (0.25 to about
2.45 L/min for 70 kg); HR 70 to 180/min, SV 70 to 110 mL, CO 4.9 to 19.8 L/min (slide 13); skeletal
muscle about 15% of CO at rest and about 80% at maximal exercise.
"""
import importlib.util
import os
import numpy as np
from scipy.interpolate import PchipInterpolator
from matplotlib.patches import FancyBboxPatch
import figstyle as fs
from figstyle import C, plt

_spec = importlib.util.spec_from_file_location(
    "coco", os.path.join(os.path.dirname(__file__), "figs_control-of-co.py"))
coco = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(coco)
vr_curve, cardiac_curve, operating_point, curve_axes = (
    coco.vr_curve, coco.cardiac_curve, coco.operating_point, coco.curve_axes)

PART, SLUG = "cardiovascular", "cv-exercise"
PRA = np.linspace(-3, 14, 700)
UP, DN = r"$\uparrow$", r"$\downarrow$"

# Exercise cardiac function curve: passes through Pra 2, CO 20 (p0 -2, cmax 28)
EX_CMAX, EX_K = 28.0, 3.193


def save(fig, name):
    fs.save(fig, PART, SLUG, name)


def op(cmax=12.0, k=7.42, pms=7.0, rvr=1.0):
    return operating_point(lambda x: cardiac_curve(x, cmax=cmax, k=k), lambda x: vr_curve(x, pms, rvr),
                           lo=-3, hi=14)


def draw_vasc(ax, pms, rvr=1.0, **kw):
    m = PRA <= pms + 0.03
    ax.plot(PRA[m], vr_curve(PRA[m], pms, rvr), **kw)


def draw_card(ax, cmax=12.0, k=7.42, **kw):
    ax.plot(PRA, cardiac_curve(PRA, cmax=cmax, k=k), **kw)


def mark(ax, xy, color, filled=True):
    if filled:
        ax.plot([xy[0]], [xy[1]], "o", color=color, ms=8, zorder=7)
    else:
        ax.plot([xy[0]], [xy[1]], "o", mfc="white", mec=color, mew=1.6, ms=8, zorder=7)


def arrow(ax, a, b, color):
    ax.annotate("", xy=b, xytext=a,
                arrowprops=dict(arrowstyle="->", color=color, lw=1.4, shrinkA=6, shrinkB=6), zorder=6)


# ---------------------------------------------------------------- 1. The control inputs
def box(ax, x, y, w, h, text, fc, ec, size=8.8, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc=fc, ec=ec, lw=1.3))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size, color=C["ink"],
            fontweight="bold" if bold else "normal")


def link(ax, a, b, color, ls="-"):
    ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="-|>", color=color, lw=1.3,
                                                    shrinkA=1, shrinkB=1, linestyle=ls))


def fig_inputs():
    fig, ax = plt.subplots(figsize=(10.6, 7.0))
    ax.set_xlim(0, 10.6)
    ax.set_ylim(0, 7.0)
    ax.axis("off")
    neu_fc, neu_ec = "#eef2f4", C["venous"]
    loc_fc, loc_ec = "#f6ece0", C["ventricular"]
    ax.text(0.1, 6.75, "Neural inputs", fontsize=11, fontweight="bold", color=C["venous"])
    inputs = [
        ("Central command\n(cortex; feed-forward, starts\nin anticipation)", 5.55),
        ("Exercise pressor reflex\n(mechanoreceptors and\nmetaboreceptors in muscle)", 4.2),
        ("Baroreceptor reflex\n(reset to a higher pressure)", 2.95),
        ("Chemoreceptor reflex\n(mainly in heavy exercise)", 1.8),
    ]
    for txt, y in inputs:
        hh = 1.0 if txt.count("\n") == 2 else 0.8
        box(ax, 0.1, y, 2.7, hh, txt, neu_fc, neu_ec)
        link(ax, (2.8, y + hh / 2), (3.45, 3.85), C["venous"])
    box(ax, 3.45, 3.3, 2.0, 1.1, "Medullary\ncardiorespiratory\ncenter", "white", C["venous"], 9.2, bold=True)
    box(ax, 3.45, 1.55, 2.0, 1.15, f"{UP} sympathetic\n{DN} vagal outflow", neu_fc, neu_ec, 9.2)
    link(ax, (4.45, 3.3), (4.45, 2.7), C["venous"])
    ax.text(6.05, 6.75, "Effects", fontsize=11, fontweight="bold", color=C["ink"])
    effects = [
        (f"Heart: {UP} HR, {UP} contractility, faster\nrelaxation (lusitropy); cardiac\nfunction curve shifts up", 5.5),
        (f"Veins: venoconstriction, {UP} P$_{{ms}}$", 4.55),
        ("Arterioles of inactive beds constrict:\ngut, kidney, inactive muscle,\nskin (early in exercise)", 3.25),
    ]
    for txt, y in effects:
        hh = 1.0 if txt.count("\n") == 2 else 0.65
        box(ax, 6.05, y, 4.45, hh, txt, "white", C["venous"])
        link(ax, (5.45, 2.2), (6.05, y + hh / 2), C["venous"])
    # local and mechanical
    ax.text(0.1, 1.2, "Local and mechanical", fontsize=11, fontweight="bold", color=C["ventricular"])
    box(ax, 0.1, 0.1, 4.3, 0.95, f"Metabolites in active muscle dilate its arterioles\n"
        f"and blunt sympathetic constriction there\n(functional sympatholysis): {DN} SVR, {DN} RVR",
        loc_fc, loc_ec, 8.6)
    box(ax, 4.65, 0.1, 2.85, 0.95, f"Skeletal muscle pump and\nrespiratory pump: {UP} venous\nreturn ({DN} effective RVR)",
        loc_fc, loc_ec, 8.6)
    box(ax, 7.75, 0.1, 2.75, 0.95, "Net: CO about 4 times rest,\nSVR much lower, MAP a little\nhigher, flow sent to muscle",
        "white", C["ink"], 8.6, bold=False)
    link(ax, (7.5, 0.58), (7.75, 0.58), C["ink"])
    save(fig, "control-inputs.svg")


# ---------------------------------------------------------------- 2. Where the cardiac output goes
def fig_distribution():
    vo2 = np.array([0.25, 0.8, 1.35, 1.9, 2.45])           # L/min, 70 kg, 3.5 to 35 mL/kg/min
    co = 5.0 + 15.0 * (vo2 - 0.25) / 2.2                   # 5 to 20 L/min
    heart = np.array([0.25, 0.45, 0.65, 0.82, 1.0])
    brain = np.array([0.75, 0.77, 0.8, 0.82, 0.85])
    visc = np.array([2.75, 2.4, 1.9, 1.4, 1.0])            # splanchnic and kidney
    skin = np.array([0.5, 0.25, 1.3, 1.5, 0.6])            # triphasic
    muscle = co - heart - brain - visc - skin
    x = np.linspace(0.25, 2.45, 300)
    f = lambda y: PchipInterpolator(vo2, y)(x)
    layers = [("Skeletal muscle", f(muscle), "#2f6f88"), ("Gut and kidney", f(visc), "#c9a25e"),
              ("Heart", f(heart), "#c98f8f"), ("Brain", f(brain), "#a8a8a8"), ("Skin", f(skin), "#e7c9b8")]
    fig, ax = plt.subplots(figsize=(7.4, 5.2))
    base = np.zeros_like(x)
    for lab, y, col in layers:
        ax.fill_between(x, base, base + y, color=col, lw=0)
        ax.plot(x, base + y, color="white", lw=0.8)
        base = base + y
    ax.plot(x, base, color=C["ink"], lw=1.6)
    ax.text(1.6, 5.0, "Skeletal muscle", color="white", fontsize=11, fontweight="bold", ha="center")
    ax.annotate("Gut and kidney", xy=(0.62, 5.0), xytext=(0.3, 10.6), fontsize=9.2, color="#7a5c22",
                arrowprops=dict(arrowstyle="-", color="#7a5c22", lw=0.8))
    ax.annotate("Heart", xy=(1.45, 9.95), xytext=(0.95, 15.6), fontsize=9.2, color="#8a4f4f",
                arrowprops=dict(arrowstyle="-", color="#8a4f4f", lw=0.8))
    ax.annotate("Brain", xy=(0.75, 7.45), xytext=(0.55, 13.4), fontsize=9.2, color=C["text"],
                arrowprops=dict(arrowstyle="-", color=C["text"], lw=0.8))
    ax.annotate("Skin", xy=(1.6, 13.4), xytext=(1.15, 17.6), fontsize=9.2, color="#9a5a3a",
                arrowprops=dict(arrowstyle="-", color="#9a5a3a", lw=0.8))
    ax.text(2.42, 20.4, "total 20 L/min", fontsize=8.8, color=C["ink"], ha="right", va="bottom")
    ax.text(0.27, 0.25, "15%", fontsize=8.8, color="white")
    ax.text(2.4, 7.0, "about\n80%", fontsize=8.8, color="white", ha="right")
    ax.set_xlim(0.25, 2.45)
    ax.set_ylim(0, 22)
    ax.set_xticks([0.25, 0.8, 1.35, 1.9, 2.45])
    ax.set_xticklabels(["0.25\nrest", "0.8", "1.35", "1.9", "2.45\nmax"])
    ax.set_xlabel("O$_2$ consumption (L/min)")
    ax.set_ylabel("Cardiac output (L/min)")
    fs.grid(ax)
    save(fig, "flow-distribution.svg")
    return dict(muscle_frac=(muscle[0] / co[0], muscle[-1] / co[-1]))


# ---------------------------------------------------------------- 3. Graded exercise
def fig_graded():
    work = np.array([0, 300, 600, 900])
    hr = np.array([62, 93, 122, 165])
    sv = np.array([92, 100, 105, 100])
    co = hr * sv / 1000
    sbp = np.array([128, 148, 165, 188])
    dbp = np.array([66, 70, 74, 80])
    mapv = dbp + (sbp - dbp) / 3
    svr = mapv / co
    vo2 = np.array([280, 870, 1500, 2400])
    avd = vo2 / (co * 10)                                   # mL O2 per dL
    panels = [
        ("Heart rate (/min)", [(hr, C["arterial"], None)], (40, 180)),
        ("Stroke volume (mL)", [(sv, C["ventricular"], None)], (0, 120)),
        ("Cardiac output (L/min)", [(co, C["ink"], None)], (0, 20)),
        ("Arterial pressure (mm Hg)", [(sbp, C["arterial"], "systolic"), (mapv, C["arterial"], "mean"),
                                       (dbp, C["arterial"], "diastolic")], (50, 200)),
        ("SVR (mm Hg·min/L)", [(svr, C["venous"], None)], (0, 18)),
        ("a-v O$_2$ difference (mL/dL)", [(avd, C["green"], None)], (0, 16)),
    ]
    fig, axs = plt.subplots(3, 2, figsize=(9.4, 8.2), sharex=True)
    for ax, (lab, series, ylim) in zip(axs.flat, panels):
        for y, col, name in series:
            ls = "-" if name in (None, "mean") else (0, (4, 2))
            ax.plot(work, y, marker="o", color=col, lw=2.0, ms=5, ls=ls)
            if name:
                ax.text(940, y[-1], name, fontsize=8.6, color=col, va="center")
        if len(series) == 3:
            ax.fill_between(work, series[2][0], series[0][0], color=C["highlight"], zorder=0)
        ax.set_ylim(*ylim)
        ax.set_title(lab, fontsize=10.5)
        fs.grid(ax)
    for ax in axs[-1]:
        ax.set_xlabel("Work (kg·m/min)")
        ax.set_xticks(work)
    axs[1, 0].set_xlim(-40, 1060)
    fig.tight_layout()
    save(fig, "graded-exercise.svg")
    return dict(co=co.round(1), map=mapv.round(0), svr=svr.round(1), avd=avd.round(1), pp=(sbp - dbp))


# ---------------------------------------------------------------- 4. Exercise on the curves, step by step
def fig_exercise_curves():
    p0 = op()
    pA = op(pms=10.0)
    pB = op(pms=10.0, rvr=0.4)
    pC = op(pms=10.0, rvr=0.4, cmax=EX_CMAX, k=EX_K)
    fig, axs = plt.subplots(2, 2, figsize=(10.2, 8.6), sharex=True, sharey=True)
    steps = [
        ("A  Venoconstriction: P$_{ms}$ 7 to 10", dict(pms=10.0, rvr=1.0), None, pA, p0),
        ("B  Add a lower RVR (muscle pump, dilation)", dict(pms=10.0, rvr=0.4), None, pB, pA),
        ("C  Add a stronger, faster heart", dict(pms=10.0, rvr=0.4), (EX_CMAX, EX_K), pC, pB),
        ("D  Rest and exercise compared", dict(pms=10.0, rvr=0.4), (EX_CMAX, EX_K), pC, p0),
    ]
    for ax, (title, vk, ck, pnew, pold) in zip(axs.flat, steps):
        draw_card(ax, color=C["ventricular"], lw=1.4 if ck else 2.3, alpha=0.45 if ck else 1.0)
        draw_vasc(ax, 7.0, color=C["venous"], lw=1.4, alpha=0.45)
        if ck:
            draw_card(ax, cmax=ck[0], k=ck[1], color=C["ventricular"], lw=2.3)
        draw_vasc(ax, vk["pms"], vk["rvr"], color=C["venous"], lw=2.3)
        mark(ax, p0, C["ink"], filled=False)
        if title.startswith("B") or title.startswith("C"):
            mark(ax, pold, C["gray"], filled=False)
        mark(ax, pnew, C["arterial"])
        arrow(ax, pold, pnew, C["arterial"])
        ax.text(pnew[0] + 0.35, pnew[1] - 0.3, f"CO {pnew[1]:.0f}, P$_{{ra}}$ {pnew[0]:.0f}", fontsize=9,
                color=C["arterial"], va="top", bbox=dict(fc="white", ec="none", pad=0.8))
        ax.set_title(title, fontsize=10.5)
        curve_axes(ax, xmax=12, ymax=26)
    axs[0, 0].text(8.7, 9.6, "resting\ncardiac\nfunction\ncurve", color=C["ventricular"], fontsize=9, ha="center")
    axs[0, 0].text(10.15, 0.6, "P$_{ms}$ 10", color=C["venous"], fontsize=9)
    axs[0, 0].text(-2.7, 24.5, "open circle: rest (CO 5, P$_{ra}$ 2)", fontsize=8.8, color=C["text"], va="top")
    axs[0, 1].text(1.0, 23.5, "same P$_{ms}$,\nsteeper curve", color=C["venous"], fontsize=9, va="top")
    axs[0, 1].text(8.4, 15.5, "the resting heart\ncannot keep up:\nP$_{ra}$ rises", color=C["ventricular"],
                   fontsize=9, va="top")
    axs[1, 0].text(6.0, 24.6, "exercise cardiac\nfunction curve", color=C["ventricular"], fontsize=9, va="top")
    axs[1, 1].text(5.0, 17.5, "CO four times rest,\nP$_{ra}$ about the same", fontsize=9, color=C["arterial"],
                   va="top")
    for ax in axs[0]:
        ax.set_xlabel("")
    for ax in axs[:, 1]:
        ax.set_ylabel("")
    fig.tight_layout()
    save(fig, "exercise-curves.svg")
    return dict(rest=p0, A=pA, B=pB, C=pC)


# ---------------------------------------------------------------- 5. Baroreflex resetting
def fig_baroreflex_reset():
    m = np.linspace(50, 160, 400)

    def hr(mp, lo, hi, c, s):
        return lo + (hi - lo) / (1 + np.exp((mp - c) / s))

    rest = (45, 125, 86.7, 8.0)
    ex = (110, 195, 108.0, 9.0)
    fig, ax = plt.subplots(figsize=(7.0, 4.9))
    ax.plot(m, hr(m, *rest), color=C["ink"], lw=2.3)
    ax.plot(m, hr(m, *ex), color=C["arterial"], lw=2.3)
    r0 = (93, float(hr(93, *rest)))
    e0 = (112, float(hr(112, *ex)))
    mark(ax, r0, C["ink"])
    mark(ax, e0, C["arterial"])
    arrow(ax, r0, e0, C["gray"])
    ax.text(r0[0] + 5, r0[1] + 12, f"rest: MAP {r0[0]}, HR {r0[1]:.0f}", fontsize=9, color=C["ink"], va="top")
    ax.text(e0[0] + 3, e0[1] + 4, f"exercise: MAP {e0[0]}, HR {e0[1]:.0f}", fontsize=9, color=C["arterial"])
    ax.text(56, 100, "resting\nreflex curve", fontsize=9.2, color=C["ink"])
    ax.text(140, 128, "reflex curve\nduring exercise", fontsize=9.2, color=C["arterial"])
    ax.annotate("still steep here: a fall in MAP\nstill raises HR", xy=(105, float(hr(105, *ex))), xytext=(56, 168),
                fontsize=8.8, color=C["text"], arrowprops=dict(arrowstyle="-", color=C["text"], lw=0.8))
    ax.set_xlim(50, 160)
    ax.set_ylim(30, 205)
    ax.set_xlabel("Mean arterial pressure (mm Hg)")
    ax.set_ylabel("Heart rate (/min)")
    fs.grid(ax)
    save(fig, "baroreflex-reset.svg")
    return dict(rest=r0, ex=e0)


# ---------------------------------------------------------------- 6. The pump experiment
def fig_pump():
    fig, ax = plt.subplots(figsize=(7.2, 5.1))
    pra_set = 2.0
    pms0, pms1 = 6.2, 12.4                # VR = (Pms - 2)/1: 4.2 and 10.4 L/min
    draw_vasc(ax, pms0, color=C["venous"], lw=2.0, alpha=0.55)
    draw_vasc(ax, pms1, color=C["venous"], lw=2.3)
    ax.axvline(pra_set, color=C["gray"], lw=2.6, ls=(0, (6, 3)), zorder=2)
    a = (pra_set, float(vr_curve(np.array([pra_set]), pms0)[0]))
    b = (pra_set, float(vr_curve(np.array([pra_set]), pms1)[0]))
    mark(ax, a, C["ink"], filled=False)
    mark(ax, b, C["arterial"])
    arrow(ax, (a[0] + 0.3, a[1]), (b[0] + 0.3, b[1]), C["arterial"])
    ax.text(1.65, a[1] - 0.2, f"before: {a[1]:.1f} L/min", fontsize=9.2, color=C["ink"], va="top", ha="right")
    ax.text(2.35, b[1] + 0.3, f"after epinephrine: {b[1]:.1f} L/min", fontsize=9.2, color=C["arterial"])
    ax.text(2.25, 13.0, "pump holds P$_{ra}$ fixed", fontsize=9.2, color=C["gray"])
    ax.text(pms0 + 0.15, 0.35, f"P$_{{ms}}$ {pms0}", fontsize=9, color=C["venous"])
    ax.text(pms1 + 0.15, 0.35, f"P$_{{ms}}$ {pms1}", fontsize=9, color=C["venous"])
    ax.text(7.6, 7.5, "epinephrine constricts\nthe veins: P$_{ms}$ rises", fontsize=9, color=C["venous"])
    curve_axes(ax, xmax=14, ymax=14)
    save(fig, "pump-experiment.svg")
    return dict(before=a, after=b)


if __name__ == "__main__":
    fig_inputs()
    print("distribution", fig_distribution())
    print("graded", fig_graded())
    print("curves", {k: tuple(round(float(v), 2) for v in p) for k, p in fig_exercise_curves().items()})
    print("baroreflex", fig_baroreflex_reset())
    print("pump", fig_pump())
