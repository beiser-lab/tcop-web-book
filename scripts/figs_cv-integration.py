"""Figures for the Cardiovascular Integration and Adaptation chapter.

Run:  cd site/scripts && MPLCONFIGDIR=$TMPDIR PNG_PREVIEW=<folder> python3 figs_cv-integration.py
Writes SVGs to ../cardiovascular/figures/cv-integration/.

The cardiac and vascular function curves are imported from figs_control-of-co.py, so the
curves look the same in both chapters (Pms 7 mm Hg, RVR 1 mm Hg*min/L, operating point
Pra 2 mm Hg and CO 5 L/min). The hemorrhage reserve model uses the same illustrative
numbers as the stressed-volume figure in that chapter: blood volume 5 L, unstressed volume
3.6 L, systemic compliance 0.2 L/mm Hg, so Pms = stressed volume / compliance = 7 mm Hg.
"""
import importlib.util
import os
import numpy as np
from matplotlib.patches import FancyBboxPatch
import figstyle as fs
from figstyle import C, plt

_spec = importlib.util.spec_from_file_location(
    "coco", os.path.join(os.path.dirname(__file__), "figs_control-of-co.py"))
coco = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(coco)
vr_curve, cardiac_curve, operating_point, curve_axes = (
    coco.vr_curve, coco.cardiac_curve, coco.operating_point, coco.curve_axes)

PART, SLUG = "cardiovascular", "cv-integration"
CAP = 1.0 / 0.85  # blood lost when the 1 L venous reserve is used up
HF_CMAX, HF_K = 5.0, 3.0  # failing heart: lower and flatter cardiac function curve
PRA = np.linspace(-3, 14, 700)


def save(fig, name):
    fs.save(fig, PART, SLUG, name)


def draw_vasc(ax, pms, rvr=1.0, **kw):
    m = PRA <= pms + 0.03
    ax.plot(PRA[m], vr_curve(PRA[m], pms, rvr), **kw)


def draw_card(ax, cmax=12.0, k=7.42, **kw):
    ax.plot(PRA, cardiac_curve(PRA, cmax=cmax, k=k), **kw)


def point(ax, xy, num, color, dx=0.35, dy=0.45, filled=True, ha="left"):
    x, y = xy
    if filled:
        ax.plot([x], [y], "o", color=color, ms=8, zorder=7)
    else:
        ax.plot([x], [y], "o", mfc="white", mec=color, mew=1.6, ms=8, zorder=7)
    ax.text(x + dx, y + dy, num, fontsize=10, color=color, fontweight="bold", ha=ha, zorder=8,
            bbox=dict(fc="white", ec="none", pad=0.6))


def arrow(ax, a, b, color):
    ax.annotate("", xy=b, xytext=a,
                arrowprops=dict(arrowstyle="->", color=color, lw=1.4, shrinkA=6, shrinkB=6), zorder=6)


def op(cmax=12.0, pms=7.0, rvr=1.0, k=7.42):
    return operating_point(lambda x: cardiac_curve(x, cmax=cmax, k=k), lambda x: vr_curve(x, pms, rvr),
                           lo=-3, hi=14)


# ---------------------------------------------------------------- 1. Process diagram for hemorrhage
def box(ax, x, y, w, h, text, fc, ec, fs_=9.2, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc=fc, ec=ec, lw=1.3))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs_, color=C["ink"],
            fontweight="bold" if bold else "normal", wrap=True)


def link(ax, a, b, color=None, style="-|>", ls="-"):
    ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle=style, color=color or C["ink"], lw=1.3,
                                                    shrinkA=1, shrinkB=1, linestyle=ls))


def fig_flowchart():
    fig, ax = plt.subplots(figsize=(10.4, 7.6))
    ax.set_xlim(0, 10.4)
    ax.set_ylim(0, 7.6)
    ax.axis("off")
    inj_fc, inj_ec = "#f6ece0", C["ventricular"]
    ref_fc, ref_ec = "#eef2f4", C["venous"]
    # injury column
    ax.text(0.2, 7.35, "Injury, before compensation", fontsize=11, fontweight="bold", color=C["ventricular"])
    steps = ["Hemorrhage", "$\\downarrow$ stressed volume, $\\downarrow$ P$_{ms}$", "$\\downarrow$ venous return, $\\downarrow$ preload (EDV)",
             "$\\downarrow$ force of contraction, $\\downarrow$ SV\n(Frank-Starling)", "$\\downarrow$ CO", "$\\downarrow$ arterial blood volume",
             "$\\downarrow$ MAP, narrow pulse pressure"]
    ys = np.linspace(6.55, 0.55, len(steps))
    w, h = 3.0, 0.62
    for i, (s, y) in enumerate(zip(steps, ys)):
        box(ax, 0.2, y, w, h, s, inj_fc, inj_ec, bold=(i == 0))
        if i:
            link(ax, (0.2 + w / 2, ys[i - 1]), (0.2 + w / 2, y + h))
    # sensing
    box(ax, 3.75, 0.55, 2.2, 0.85, "Arterial and atrial baroreceptors\nfire less; chemoreceptors\nactivated", ref_fc, ref_ec, 8.0)
    link(ax, (3.2, 0.86), (3.75, 0.97))
    box(ax, 3.75, 2.0, 2.2, 0.85, "Medulla: $\\uparrow$ sympathetic,\n$\\downarrow$ vagal outflow", ref_fc, ref_ec, 8.8)
    link(ax, (4.85, 1.4), (4.85, 2.0))
    ax.text(0.2 + 3.0 + 2.75 + 0.95, 7.35, "Compensation", fontsize=11, fontweight="bold", color=C["venous"])
    # compensation arms
    arms = [
        ("Veins: venoconstriction moves unstressed volume\ninto stressed volume, $\\uparrow$ P$_{ms}$, $\\uparrow$ venous return\n"
         "(vascular function curve shifts right)", 6.0),
        ("Heart: $\\uparrow$ HR, $\\uparrow$ contractility\n(cardiac function curve shifts up)", 4.85),
        ("Arterioles: $\\uparrow$ SVR, less diastolic runoff,\n$\\uparrow$ arterial blood volume\n(cost: $\\uparrow$ afterload)", 3.6),
        ("Microcirculation: lower capillary pressure,\nreabsorption of interstitial fluid; flow\n"
         "redirected from gut, skin, kidney to brain, heart", 2.25),
        ("Hormones: epinephrine, vasopressin, angiotensin II.\nKidneys (hours to days): retain salt and\nwater, restore blood volume and P$_{ms}$", 0.85),
    ]
    x0, wa = 6.55, 3.75
    for txt, y in arms:
        hh = 1.0 if txt.count("\n") >= 2 else 0.8
        box(ax, x0, y, wa, hh, txt, "white", C["venous"], 8.6)
        link(ax, (5.95, 2.43), (x0, y + hh / 2), color=C["venous"])
    ax.text(x0 + wa / 2, 7.08, "$\\uparrow$ CO and $\\uparrow$ SVR together defend MAP", ha="center", fontsize=9.2,
            color=C["venous"], fontstyle="italic")
    save(fig, "hemorrhage-flowchart.svg")


# ---------------------------------------------------------------- 2. Hemorrhage on the curves: three states
def fig_hemorrhage_states():
    fig, axs = plt.subplots(1, 2, figsize=(10.4, 4.9), sharey=True)
    p1 = op()
    p2 = op(pms=4.5)
    p3 = op(pms=5.5)
    p4 = op(pms=5.5, cmax=13.0)
    # A: injury
    ax = axs[0]
    draw_card(ax, color=C["ventricular"], lw=2.3)
    draw_vasc(ax, 7.0, color=C["venous"], lw=1.4, alpha=0.45)
    draw_vasc(ax, 4.5, color=C["venous"], lw=2.3)
    point(ax, p1, "1", C["ink"], filled=False)
    point(ax, p2, "2", C["arterial"], dx=-0.3, dy=-0.95, ha="right")
    arrow(ax, p1, p2, C["arterial"])
    ax.text(4.65, 0.3, "P$_{ms}$ 4.5", color=C["venous"], fontsize=9)
    ax.text(7.15, 0.3, "7", color=C["gray"], fontsize=9)
    ax.text(8.0, 7.2, "cardiac function\ncurve unchanged", color=C["ventricular"], fontsize=9, ha="center")
    ax.text(-2.7, 11.2, "1  before the hemorrhage\n2  injury: P$_{ms}$ falls; CO and P$_{ra}$ fall",
            fontsize=8.8, color=C["text"], va="top")
    ax.set_title("A  Injury, before compensation")
    curve_axes(ax, xmax=10, ymax=11.5)
    # B: compensation
    ax = axs[1]
    draw_card(ax, color=C["ventricular"], lw=1.4, alpha=0.45)
    draw_card(ax, cmax=13.0, color=C["ventricular"], lw=2.3)
    draw_vasc(ax, 4.5, color=C["venous"], lw=1.3, ls=(0, (2, 2)), alpha=0.8)
    draw_vasc(ax, 5.5, color=C["venous"], lw=2.3)
    draw_vasc(ax, 7.0, color=C["venous"], lw=1.4, alpha=0.45)
    point(ax, p1, "1", C["ink"], filled=False, dx=0.3, dy=0.35)
    point(ax, p2, "2", C["gray"], filled=False, dx=-0.3, dy=-0.95, ha="right")
    point(ax, p3, "3", C["venous"], dx=0.3, dy=-0.95)
    point(ax, p4, "4", C["arterial"], dx=-0.3, dy=0.35, ha="right")
    arrow(ax, p2, p3, C["venous"])
    arrow(ax, p3, p4, C["arterial"])
    ax.text(5.65, 0.3, "P$_{ms}$ 5.5", color=C["venous"], fontsize=9)
    ax.text(0.5, 9.4, "stronger,\nfaster heart", color=C["ventricular"], fontsize=9, ha="left", va="top")
    ax.text(-2.7, 11.2, "3  venoconstriction raises P$_{ms}$ part way\n4  heart rate and contractility rise",
            fontsize=8.8, color=C["text"], va="top")
    ax.set_title("B  Compensation")
    curve_axes(ax, xmax=10, ymax=11.5)
    ax.set_ylabel("")
    fig.tight_layout()
    save(fig, "hemorrhage-states.svg")
    return dict(p1=p1, p2=p2, p3=p3, p4=p4)


# ---------------------------------------------------------------- 3. Venous reserve: 1 L versus 2 L
def reserve_model(loss, reflex):
    total, vu, comp = 5.0, 3.6, 0.2
    recruit = np.minimum(0.85 * loss, 1.0) if reflex else 0.0 * loss
    stressed = np.clip(total - loss - (vu - recruit), 0, None)
    pms = stressed / comp
    return pms


def fig_reserve():
    loss = np.linspace(0, 2.0, 201)
    fig, axs = plt.subplots(1, 2, figsize=(10.2, 4.3))
    res = {}
    for reflex, col, lab, ls in ((False, C["gray"], "no reflexes", (0, (5, 3))),
                                 (True, C["venous"], "with sympathetic reflexes", "-")):
        pms = reserve_model(loss, reflex)
        co = []
        for L, p in zip(loss, pms):
            if p <= 0.3:
                co.append(0.0)
                continue
            cmax = 12.0 + (1.0 * min(L / 1.0, 1.0) if reflex else 0.0)
            co.append(op(cmax=cmax, pms=p)[1])
        co = np.array(co)
        axs[0].plot(loss, pms, color=col, lw=2.3, ls=ls)
        axs[1].plot(loss, co, color=col, lw=2.3, ls=ls)
        res[lab] = (pms, co)
    for ax in axs:
        ax.axvspan(CAP, 2.0, color=C["shade"], zorder=0)
        ax.axvline(CAP, color=C["axis"], lw=0.9, ls=(0, (3, 3)))
        ax.set_xlim(0, 2.0)
        ax.set_xticks([0, 0.5, 1.0, 1.5, 2.0])
        ax.set_xlabel("Blood lost (L)")
        fs.grid(ax)
    axs[0].set_ylim(0, 8)
    axs[0].set_ylabel("P$_{ms}$ (mm Hg)")
    axs[1].set_ylim(0, 6.5)
    axs[1].set_ylabel("Cardiac output (L/min)")
    axs[0].text(CAP + 0.04, 7.3, "1 L of venous\nreserve used up", fontsize=8.8, color=C["text"], va="top")
    axs[0].text(0.06, 7.55, "with sympathetic reflexes", color=C["venous"], fontsize=9)
    axs[0].text(0.2, 3.3, "no reflexes", color=C["gray"], fontsize=9)
    axs[1].text(0.06, 5.95, "with sympathetic reflexes", color=C["venous"], fontsize=9)
    axs[1].text(0.15, 2.5, "no reflexes", color=C["gray"], fontsize=9)
    axs[0].set_title("A  Mean systemic filling pressure")
    axs[1].set_title("B  Cardiac output")
    fig.tight_layout()
    save(fig, "venous-reserve.svg")
    i1, i2 = 100, 200
    return {k: (round(v[0][i1], 2), round(v[1][i1], 2), round(v[0][i2], 2), round(v[1][i2], 2))
            for k, v in res.items()}


# ---------------------------------------------------------------- 4. Heart failure
def fig_heart_failure():
    fig, ax = plt.subplots(figsize=(7.4, 5.3))
    p1 = op()
    p2 = op(cmax=HF_CMAX, k=HF_K)
    p3 = op(cmax=HF_CMAX, k=HF_K, pms=10.0)
    p4 = op(cmax=HF_CMAX, k=HF_K, pms=13.0)
    draw_card(ax, color=C["ventricular"], lw=1.4, alpha=0.45)
    draw_card(ax, cmax=HF_CMAX, k=HF_K, color=C["ventricular"], lw=2.3)
    draw_vasc(ax, 7.0, color=C["venous"], lw=2.0)
    draw_vasc(ax, 10.0, color=C["venous"], lw=2.0, ls=(0, (5, 3)))
    draw_vasc(ax, 13.0, color=C["venous"], lw=1.6, ls=(0, (2, 2)))
    point(ax, p1, "1", C["ink"], filled=False, dx=0.3, dy=0.45)
    point(ax, p2, "2", C["arterial"], dx=-0.3, dy=-1.15, ha="right")
    point(ax, p3, "3", C["venous"], dx=0.2, dy=-1.15)
    point(ax, p4, "4", C["venous"], dx=0.2, dy=-1.15)
    arrow(ax, p1, p2, C["arterial"])
    arrow(ax, p2, p3, C["venous"])
    arrow(ax, p3, p4, C["venous"])
    ax.annotate("normal heart", xy=(11.5, 10.15), xytext=(11.5, 11.6), ha="center", fontsize=9,
                color=C["ventricular"], arrowprops=dict(arrowstyle="-", color=C["ventricular"], lw=0.8))
    ax.text(11.0, 4.6, "weakened heart", color=C["ventricular"], fontsize=9, ha="center", va="top")
    for pms in (7, 10, 13):
        ax.text(pms + 0.12, 0.35, f"P$_{{ms}}$ {pms}", color=C["venous"], fontsize=8.6)
    ax.text(9.0, 9.0, "1  before the injury\n2  injury: contractility falls\n3  venoconstriction and fluid\n"
            "    retention raise P$_{ms}$\n4  more fluid: P$_{ra}$ climbs,\n    CO rises little",
            fontsize=8.6, color=C["text"], va="top", bbox=dict(fc="white", ec="none", pad=1.5))
    curve_axes(ax, xmax=14, ymax=13)
    save(fig, "heart-failure.svg")
    return dict(p1=p1, p2=p2, p3=p3, p4=p4)


# ---------------------------------------------------------------- 5. Septic shock
def fig_sepsis():
    fig, axs = plt.subplots(1, 2, figsize=(10.6, 4.8), gridspec_kw=dict(width_ratios=[1.25, 1]))
    ax = axs[0]
    p1 = op()
    p2 = op(pms=4.5, cmax=13.0)
    p3 = op(pms=6.5, cmax=20.0)
    draw_card(ax, color=C["ventricular"], lw=1.4, alpha=0.45)
    draw_vasc(ax, 7.0, color=C["venous"], lw=1.4, alpha=0.45)
    draw_card(ax, cmax=13.0, color=C["ventricular"], lw=1.3, ls=(0, (2, 2)), alpha=0.8)
    draw_vasc(ax, 4.5, color=C["venous"], lw=1.3, ls=(0, (2, 2)), alpha=0.8)
    draw_card(ax, cmax=20.0, color=C["ventricular"], lw=2.3)
    draw_vasc(ax, 6.5, color=C["venous"], lw=2.3)
    point(ax, p1, "1", C["ink"], filled=False, dx=0.35, dy=-1.1)
    point(ax, p2, "2", C["gray"], filled=False, dx=-0.3, dy=-1.2, ha="right")
    point(ax, p3, "3", C["arterial"], dx=-0.35, dy=0.35, ha="right")
    arrow(ax, p1, p2, C["gray"])
    arrow(ax, p2, p3, C["arterial"])
    ax.text(4.6, 0.4, "4.5", color=C["venous"], fontsize=8.6)
    ax.annotate("P$_{ms}$ 6.5", xy=(5.0, 1.5), xytext=(8.0, 2.6), fontsize=8.6, color=C["venous"],
                arrowprops=dict(arrowstyle="-", color=C["venous"], lw=0.8))
    ax.text(7.1, 0.4, "7", color=C["gray"], fontsize=8.6)
    ax.text(-2.7, 12.6, "1  before the illness\n2  venodilation and capillary leak lower P$_{ms}$;\n"
            "    low SVR unloads the heart\n3  sympathetic drive: faster, stronger heart",
            fontsize=8.6, color=C["text"], va="top")
    ax.set_title("A  The curves")
    curve_axes(ax, xmax=12, ymax=13)
    # B: bars
    ax = axs[1]
    states = ["Normal", "Hemorrhage,\ncompensated", "Sepsis,\ncompensated"]
    hem = op(pms=5.5, cmax=13.0)  # compensated hemorrhage point 4 of the hemorrhage figure
    co = np.array([5.0, hem[1], p3[1]])
    pra = np.array([2.0, hem[0], p3[0]])
    svr = np.array([18.0, 20.0, 10.0])
    mapv = co * svr + pra
    x = np.arange(3)
    cols = [C["ink"], C["venous"], C["arterial"]]
    ax.bar(x, mapv, color=cols, width=0.6, alpha=0.9)
    for i in range(3):
        ax.text(x[i], mapv[i] + 2, f"MAP {mapv[i]:.0f}", ha="center", fontsize=9.2, color=cols[i], fontweight="bold")
        ax.text(x[i], 6, f"CO {co[i]:.1f}\n× SVR {svr[i]:.0f}\n+ P$_{{ra}}$ {pra[i]:.1f}", ha="center",
                fontsize=8.4, color="white")
    ax.set_xticks(x)
    ax.set_xticklabels(states, fontsize=9)
    ax.set_ylim(0, 115)
    ax.set_ylabel("Mean arterial pressure (mm Hg)")
    ax.set_title("B  MAP needs SVR as well as CO")
    fs.grid(ax)
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    save(fig, "septic-shock.svg")
    return dict(p1=p1, p2=p2, p3=p3, map=mapv.round(0))


# ---------------------------------------------------------------- 6. P-V loops: hemorrhage and MI
def _pump():
    spec = importlib.util.spec_from_file_location(
        "pump", os.path.join(os.path.dirname(__file__), "figs_cardiac-pump.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def fig_pv_loops():
    pm = _pump()
    B = pm.B
    hem = pm.run(Ppv=6.2)                               # less venous return: lower filling pressure
    ami = pm.run(Ees=1.2)                               # flatter ESPVR, same filling pressure
    comp = pm.run(Ees=1.2, Ppv=15.5)                    # compensation: higher filling pressure
    fig, axs = plt.subplots(1, 2, figsize=(11.0, 4.8), sharey=True)
    out = {}
    for ax, title, beats in ((axs[0], "A  Hemorrhage, before compensation", [(hem, "hemorrhage", "-")]),
                             (axs[1], "B  Myocardial infarction", [(ami, "infarct", "-"),
                                                                  (comp, "compensated", (0, (5, 2)))])):
        pm.pv_axes(ax, vmax=200, pmax=150)
        pm.edpvr(ax, B["p"], vmax=190, color=C["venous"], lw=1.5)
        pm.espvr(ax, B["p"], vmax=80, color=C["arterial"], lw=1.5,
                 alpha=0.45 if ax is axs[1] else 1.0)
        V0_, P0_ = pm.loop_xy(B)
        ax.plot(V0_, P0_, color=C["ventricular"], lw=2.2, alpha=0.35)
        ax.set_title(title, fontsize=11)
        y = 26
        ax.plot([B["ESV"], B["EDV"]], [y, y], color=C["gray"], lw=3, solid_capstyle="butt")
        xl = 162 if ax is axs[1] else B["EDV"] + 3
        ax.text(xl, y, "%d mL before" % round(B["SV"]), va="center", fontsize=8.5, color=C["gray"])
        for b, lab, ls in beats:
            V1, P1 = pm.loop_xy(b)
            ax.plot(V1, P1, color=C["ventricular"], lw=2.2, ls=ls)
            y += 11
            col = C["green"] if lab == "compensated" else C["arterial"]
            ax.plot([b["ESV"], b["EDV"]], [y, y], color=col, lw=3, solid_capstyle="butt")
            ax.text(xl, y, "%d mL %s" % (round(b["SV"]), lab), va="center", fontsize=8.5, color=col)
            out[lab] = dict(EDV=round(b["EDV"]), ESV=round(b["ESV"]), SV=round(b["SV"]),
                            EDP=round(float(b["Plv"][b["i_mc"]]), 1))
    out["before"] = dict(EDV=round(B["EDV"]), ESV=round(B["ESV"]), SV=round(B["SV"]),
                         EDP=round(float(B["Plv"][B["i_mc"]]), 1))
    ami_p = ami["p"]
    pm.espvr(axs[1], ami_p, vmax=125, color=C["arterial"], lw=1.6, ls=":")
    axs[0].text(84, 140, "ESPVR unchanged\n(same contractility)", fontsize=8.5, color=C["arterial"], va="top")
    axs[0].text(150, 92, "EDPVR\n(filling curve)", fontsize=8.5, color=C["venous"])
    axs[0].text(4, 146, "faded: before", fontsize=8.5, color=C["text"], va="top")
    axs[1].text(127, 128, "flatter ESPVR", fontsize=8.5, color=C["arterial"])
    axs[1].annotate("higher LVEDP", xy=(comp["EDV"], float(comp["Plv"][comp["i_mc"]])),
                    xytext=(163, 75), fontsize=8.5, color=C["green"],
                    arrowprops=dict(arrowstyle="-", color=C["green"], lw=0.8))
    axs[1].set_ylabel("")
    fig.tight_layout(w_pad=1.5)
    save(fig, "pv-loops.svg")
    return out


# ---------------------------------------------------------------- 7. Autotransfusion
def fig_autotransfusion():
    t = np.array([-0.5, 0.0, 0.1, 0.25, 0.4, 0.5, 0.75, 1.0, 1.25, 1.75, 2.25, 2.5])
    bp = np.array([115, 115, 95, 62, 49, 48, 80, 100, 107, 108, 107, 106])
    tc = np.array([-0.5, 0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 2.5])
    cop = np.array([27, 27, 23.5, 21.5, 20.5, 19.5, 18.0, 17.0, 16.3])
    from scipy.interpolate import PchipInterpolator
    tt = np.linspace(-0.5, 2.5, 400)
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    ax.axvspan(0, 0.5, color=C["shade"], zorder=0)
    ax.text(0.25, 6, "bleeding", rotation=90, ha="center", fontsize=9, color=C["text"])
    ax.plot(tt, PchipInterpolator(t, bp)(tt), color=C["arterial"], lw=2.3)
    ax.set_ylim(0, 125)
    ax.set_xlim(-0.5, 2.5)
    ax.set_xlabel("Time (h)")
    ax.set_ylabel("Arterial pressure (mm Hg)", color=C["arterial"])
    fs.grid(ax)
    ax2 = ax.twinx()
    ax2.spines["right"].set_visible(True)
    ax2.plot(tt, PchipInterpolator(tc, cop)(tt), color=C["venous"], lw=2.3, ls=(0, (5, 2)))
    ax2.set_ylim(0, 31.25)
    ax2.set_ylabel("Plasma colloid osmotic pressure (mm Hg)", color=C["venous"])
    ax.text(1.2, 113, "arterial pressure recovers", fontsize=9, color=C["arterial"])
    ax2.text(1.1, 13.3, "colloid osmotic pressure falls:\nthe plasma is diluted by\nreabsorbed tissue fluid",
             fontsize=9, color=C["venous"], va="top")
    save(fig, "autotransfusion.svg")


if __name__ == "__main__":
    fig_flowchart()
    print("hemorrhage", {k: tuple(round(v, 2) for v in p) for k, p in fig_hemorrhage_states().items()})
    print("reserve at 1 L and 2 L (Pms, CO):", fig_reserve())
    print("heart failure", {k: tuple(round(v, 2) for v in p) for k, p in fig_heart_failure().items()})
    print("sepsis", fig_sepsis())
    print("pv loops", fig_pv_loops())
    fig_autotransfusion()
