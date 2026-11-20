"""Figures for the Respiratory Statics chapter.

Run from anywhere:  python3 figs_statics.py
Writes SVGs to ../pulmonary/figures/statics/. Curves come from statics_model.py, the port of
the Respiratory Mechanics Lab model, so they match the simulator.
"""
import os
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle

import statics_model as m

OUT = os.path.join(os.path.dirname(__file__), "..", "pulmonary", "figures", "statics")
os.makedirs(OUT, exist_ok=True)

# Simulator palette (Respiratory Mechanics Lab app.js)
C = dict(system="#800000", lung="#a65e00", cw="#155f83", muscle="#d22f1e",
         ink="#193944", text="#4d4d4d", grid="#eaf0f2", axis="#aebdc4", shade="#f4f4f4")

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 11, "axes.edgecolor": C["axis"], "axes.labelcolor": C["text"],
    "xtick.color": C["text"], "ytick.color": C["text"], "axes.spines.top": False,
    "axes.spines.right": False, "svg.fonttype": "none", "axes.titlesize": 12,
    "axes.titleweight": "bold", "axes.titlecolor": C["ink"],
})


def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, format="svg", bbox_inches="tight", metadata={"Date": None})
    if os.environ.get("PNG_PREVIEW"):
        fig.savefig(os.path.join(os.environ["PNG_PREVIEW"], name.replace(".svg", ".png")), dpi=110, bbox_inches="tight")
    plt.close(fig)
    print("wrote", os.path.relpath(path))


def curves(st, pmin=-45, pmax=45):
    P = np.linspace(pmin, pmax, 400)
    lungP = P[P >= 0]
    lungV = np.array([m.lung_volume(x, st["lungCompliance"]) for x in lungP])
    cwV = np.array([m.chest_wall_volume(x, st["chestWallCompliance"], load=st["chestWallLoad"]) for x in P])
    lo = m.NORMAL["cwVlow"] + 0.02
    hi = min(m.lung_max_volume(st["lungCompliance"]), m.NORMAL["cwVhigh"]) - 0.02
    V = np.linspace(lo, hi, 400)
    rsP = np.array([m.system_pressure(v, st) for v in V])
    keep = (rsP > pmin - 5) & (rsP < pmax + 5)
    return (lungP, lungV), (P, cwV), (rsP[keep], V[keep])


def pv_axes(ax, pmin=-45, pmax=45, vmax=7.0):
    ax.set_xlim(pmin, pmax)
    ax.set_ylim(0, vmax)
    ax.axvline(0, color=C["axis"], lw=1)
    ax.set_xlabel("Pressure (cm H$_2$O)")
    ax.set_ylabel("Volume (L)")
    ax.text(pmin + 1, -0.75, "← compression (inward)", fontsize=9, color=C["text"], ha="left")
    ax.text(pmax - 1, -0.75, "expansion (outward) →", fontsize=9, color=C["text"], ha="right")
    ax.grid(color=C["grid"], lw=0.8)
    ax.set_axisbelow(True)


# ---------------------------------------------------------------- 1. Spirogram
def fig_spirogram():
    a = m.analyze(m.settings_of())
    frc, tlc, rv, vt = a["frc"], a["tlc"], a["rv"], 0.5
    t = np.linspace(0, 30, 3000)
    v = np.full_like(t, frc)
    tid = lambda tt: frc + vt * (1 - np.cos(2 * np.pi * tt / 4)) / 2
    for i, tt in enumerate(t):
        if tt < 12:
            v[i] = tid(tt)
        elif tt < 15:  # slow maximal inspiration to TLC
            u = (tt - 12) / 3
            v[i] = frc + (tlc - frc) * (1 - np.cos(np.pi * u)) / 2
        elif tt < 20:  # slow maximal expiration to RV
            u = (tt - 15) / 5
            v[i] = tlc - (tlc - rv) * (1 - np.cos(np.pi * u)) / 2
        elif tt < 22:  # back to FRC
            u = (tt - 20) / 2
            v[i] = rv + (frc - rv) * (1 - np.cos(np.pi * u)) / 2
        else:
            v[i] = tid(tt - 22)
    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    ax.axhspan(0, rv, color=C["shade"], zorder=0)
    ax.text(1.0, rv / 2, "Residual volume stays in the lung:\nspirometry cannot see it",
            fontsize=9, color=C["text"], va="center")
    ax.plot(t, v, color=C["ink"], lw=1.8)
    for y in (rv, frc, frc + vt, tlc):
        ax.axhline(y, color=C["axis"], lw=0.8, ls=(0, (3, 3)))
    ax.set_xlim(0, 44)
    ax.set_ylim(0, 6.6)
    ax.set_xticks([])
    ax.set_xlabel("Time")
    ax.set_ylabel("Lung volume (L)")
    ax.spines["bottom"].set_visible(False)

    def bracket(x, y0, y1, label, color, yl=None):
        ax.annotate("", xy=(x, y0), xytext=(x, y1),
                    arrowprops=dict(arrowstyle="<->", color=color, lw=1.4, shrinkA=0, shrinkB=0))
        ax.text(x + 0.4, (y0 + y1) / 2 if yl is None else yl, label, va="center", fontsize=9.5, color=color,
                bbox=dict(fc="white", ec="none", pad=1.2))

    vol = C["cw"]
    cap = C["system"]
    bracket(31.0, frc + vt, tlc, "IRV", vol)
    bracket(31.0, frc, frc + vt, "V$_T$", vol)
    bracket(31.0, rv, frc, "ERV", vol)
    bracket(31.0, 0, rv, "RV", vol)
    bracket(35.0, frc, tlc, "IC", cap)
    bracket(35.0, 0, frc, "FRC", cap, yl=2.25)
    bracket(38.5, rv, tlc, "VC", cap)
    bracket(41.8, 0, tlc, "TLC", cap)
    ax.text(31.0, 6.42, "Volumes", color=vol, fontsize=9.5, fontweight="bold", ha="left")
    ax.text(35.0, 6.42, "Capacities", color=cap, fontsize=9.5, fontweight="bold", ha="left")
    save(fig, "spirogram.svg")


# ---------------------------------------------------------------- 2. Lung, chest wall, system
def fig_pv_curves():
    st = m.settings_of()
    a = m.analyze(st)
    (lp, lv), (cp, cv), (rp, rvv) = curves(st)
    fig, ax = plt.subplots(figsize=(7.2, 5.4))
    pv_axes(ax)
    ax.plot(cp, cv, color=C["cw"], lw=2.2, label="Chest wall")
    ax.plot(lp, lv, color=C["lung"], lw=2.2, label="Lung")
    ax.plot(rp, rvv, color=C["system"], lw=2.6, label="Respiratory system")
    for y, lab, x in ((a["tlc"], "TLC", -12), (a["rv"], "RV", -44)):
        ax.axhline(y, color="#6b6b6b", lw=0.8, ls=(0, (4, 3)))
        ax.text(x, y + 0.07, lab, ha="left", fontsize=9, color="#6b6b6b")
    frc = a["frc"]
    ax.plot([0], [frc], "o", color=C["system"], ms=7, zorder=5)
    ax.annotate("FRC: the system's\nrelaxed volume (3.0 L)", xy=(0, frc), xytext=(-40, 3.9),
                fontsize=9, color=C["system"], arrowprops=dict(arrowstyle="-", color=C["system"], lw=0.8))
    ax.plot([a["pl_frc"], a["pcw_frc"]], [frc, frc], "o", color=C["ink"], ms=4, zorder=5)
    ax.text(6.5, frc - 0.32, "lung +5", fontsize=8.5, ha="left", color=C["lung"])
    ax.text(-6.5, frc - 0.32, "chest wall −5", fontsize=8.5, ha="right", color=C["cw"])
    cw0 = a["cw_rest"]
    ax.plot([0], [cw0], "o", color=C["cw"], ms=6, zorder=5)
    ax.annotate("Chest wall rests near 4.75 L,\n72% of the way from RV to TLC", xy=(0, cw0), xytext=(-40, 5.6),
                fontsize=9, color=C["cw"], arrowprops=dict(arrowstyle="-", color=C["cw"], lw=0.8))
    ax.text(8, 2.1, "Lung", color=C["lung"], fontsize=10.5, fontweight="bold")
    ax.text(-30, 1.75, "Chest wall", color=C["cw"], fontsize=10.5, fontweight="bold")
    ax.text(22, 6.45, "Respiratory\nsystem", color=C["system"], fontsize=10.5, fontweight="bold")
    save(fig, "pv-lung-chestwall-system.svg")


# ---------------------------------------------------------------- 3. Muscles set TLC and RV
def fig_muscles():
    st = m.settings_of()
    a = m.analyze(st)
    (lp, lv), (cp, cv), (rp, rvv) = curves(st, -70, 70)
    V = np.linspace(1.2, 6.6, 300)
    insp = np.array([m.system_pressure(v, st) - m.insp_muscle(v) for v in V])
    expi = np.array([m.system_pressure(v, st) + m.exp_muscle(v) for v in V])
    # Plot the muscle limits as the pressure the muscles can hold the system at:
    # inspiratory limit = +insp_muscle(V) on the relaxation axis (the system curve meets it at TLC).
    insp_lim = np.array([m.insp_muscle(v) for v in V])
    exp_lim = np.array([-m.exp_muscle(v) for v in V])
    fig, ax = plt.subplots(figsize=(7.2, 5.4))
    pv_axes(ax, -70, 70)
    ax.plot(cp, cv, color=C["cw"], lw=1.3, alpha=0.5)
    ax.plot(lp, lv, color=C["lung"], lw=1.3, alpha=0.5)
    ax.plot(rp, rvv, color=C["system"], lw=2.6)
    m1 = (insp_lim < 70)
    ax.plot(insp_lim[m1], V[m1], color=C["muscle"], lw=2, ls=(0, (6, 3)))
    m2 = (exp_lim > -70)
    ax.plot(exp_lim[m2], V[m2], color=C["muscle"], lw=2, ls=(0, (6, 3)))
    ax.plot([m.system_pressure(a["tlc"], st)], [a["tlc"]], "o", color=C["muscle"], ms=7, zorder=5)
    ax.plot([m.system_pressure(a["rv"], st)], [a["rv"]], "o", color=C["muscle"], ms=7, zorder=5)
    ax.text(11, a["tlc"] + 0.25, "TLC: the system's inward\nrecoil equals the most the\ninspiratory muscles can pull",
            fontsize=8.8, color=C["ink"])
    ax.text(-68, 0.95, "RV: the most the expiratory\nmuscles can squeeze against\nthe stiff, compressed chest wall",
            fontsize=8.8, color=C["ink"])
    ax.text(57, 4.85, "inspiratory\nmuscles", color=C["muscle"], fontsize=9, ha="center")
    ax.text(-50, 3.45, "expiratory\nmuscles", color=C["muscle"], fontsize=9, ha="center")
    ax.text(14, 3.2, "Respiratory\nsystem", color=C["system"], fontsize=10, fontweight="bold")
    save(fig, "pv-muscles-tlc-rv.svg")


# ---------------------------------------------------------------- 4. Single alveolus model
def fmt(x):
    return f"{x:g}".replace("-", "−")


def alveolus_panel(ax, title, ppl, pel, palv, ptp, note, flow=False):
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_aspect("equal")
    ax.set_title(title, loc="left")
    ax.add_patch(FancyBboxPatch((0.6, 0.6), 8.8, 7.2, boxstyle="round,pad=0.1,rounding_size=0.6",
                                fc="#f3f7f9", ec=C["cw"], lw=3))
    ax.text(9.25, 0.85, "chest wall", color=C["cw"], fontsize=9, ha="right")
    ax.add_patch(Rectangle((4.55, 6.0), 0.9, 3.6, fc="white", ec=C["lung"], lw=2))
    ax.add_patch(Rectangle((4.62, 6.0), 0.76, 3.7, fc="white", ec="none", zorder=3))
    ax.add_patch(Circle((5, 3.9), 2.25, fc="white", ec=C["lung"], lw=2.5, zorder=2))
    ax.text(5, 9.75, "mouth  P = 0", ha="center", fontsize=9, color=C["text"])
    ax.text(5, 4.35, "P$_{alv}$ = " + fmt(palv), ha="center", fontsize=12, color=C["system"], fontweight="bold", zorder=4)
    ax.text(5, 3.45, f"P$_{{el}}$ = +{pel:g}", ha="center", fontsize=10.5, color=C["lung"], zorder=4)
    ax.text(1.0, 1.35, "P$_{pl}$ = " + fmt(ppl), fontsize=11.5, color=C["cw"], fontweight="bold")
    ax.text(7.55, 1.35, f"P$_{{tp}}$ = {ptp:g}", fontsize=10.5, color=C["ink"], ha="center")
    for ang in (200, 250, 290, 340):
        r = math.radians(ang)
        x0, y0 = 5 + 2.3 * math.cos(r), 3.9 + 2.3 * math.sin(r)
        x1, y1 = 5 + 1.55 * math.cos(r), 3.9 + 1.55 * math.sin(r)
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle="-|>", color=C["lung"], lw=1.2), zorder=4)
    if flow:
        ax.annotate("", xy=(5, 6.6), xytext=(5, 9.3),
                    arrowprops=dict(arrowstyle="-|>", color=C["system"], lw=2.2), zorder=5)
        ax.text(5.6, 8.0, "air in", color=C["system"], fontsize=9.5, zorder=5)
    ax.text(0.2, -0.55, note, fontsize=9, color=C["text"], va="top")


def fig_alveolus():
    fig, axes = plt.subplots(1, 2, figsize=(9.4, 5.6))
    alveolus_panel(axes[0], "A. At FRC, no flow", ppl=-5, pel=5, palv=0, ptp=5,
                   note="P$_{alv}$ = P$_{pl}$ + P$_{el}$ = −5 + 5 = 0\nP$_{tp}$ = P$_{alv}$ − P$_{pl}$ = 0 − (−5) = 5")
    alveolus_panel(axes[1], "B. Inspiration starts", ppl=-7, pel=5, palv=-2, ptp=5, flow=True,
                   note="Muscles lower P$_{pl}$ to −7; volume (so P$_{el}$) not yet changed\n"
                        "P$_{alv}$ = −7 + 5 = −2, below the mouth, so air flows in\n"
                        "Mouth-to-pleural pressure is 7; P$_{tp}$ stays 5 until volume rises")
    fig.subplots_adjust(wspace=0.12)
    save(fig, "single-alveolus.svg")


# ---------------------------------------------------------------- 5. Air vs saline (schematic)
def fig_air_saline():
    P = np.linspace(0, 30, 400)
    sal_in = 200 * (1 - np.exp(-P / 3.0))
    sal_out = 200 * (1 - np.exp(-P / 2.6))
    air_out = 25 + 175 * (1 - np.exp(-P / 7.0))
    air_in = 200 / (1 + np.exp(-(P - 15.5) / 2.6))
    air_in = (air_in - air_in[0]) / (air_in[-1] - air_in[0]) * air_out[-1]
    Vg = np.linspace(25.5, 195, 300)
    p_sal = np.interp(Vg, sal_in, P)
    p_def = np.interp(Vg, air_out, P)
    p_inf = np.interp(Vg, air_in, P)
    fig, ax = plt.subplots(figsize=(6.6, 5.0))
    ax.grid(color=C["grid"], lw=0.8)
    ax.set_axisbelow(True)
    ax.fill_betweenx(Vg, p_sal, p_def, color="#f6ece0", zorder=0)
    ax.fill_betweenx(Vg, p_def, p_inf, color="#eef2f4", zorder=0)
    ax.plot(P, sal_in, color=C["cw"], lw=2.2)
    ax.plot(P, sal_out, color=C["cw"], lw=1.4, ls=(0, (4, 2)))
    ax.plot(P, air_in, color=C["lung"], lw=2.4)
    ax.plot(P, air_out, color=C["lung"], lw=1.6, ls=(0, (4, 2)))
    ax.annotate("", xy=(22, np.interp(22, P, air_in)), xytext=(19, np.interp(19, P, air_in)),
                arrowprops=dict(arrowstyle="-|>", color=C["lung"], lw=1.6))
    ax.annotate("", xy=(10, np.interp(10, P, air_out)), xytext=(13, np.interp(13, P, air_out)),
                arrowprops=dict(arrowstyle="-|>", color=C["lung"], lw=1.6))
    ax.text(0.6, 214, "Saline", color=C["cw"], fontsize=10.5, fontweight="bold")
    ax.text(21.5, 118, "Air,\ninflation", color=C["lung"], fontsize=10.5, fontweight="bold")
    ax.text(16, 192, "Air, deflation", color=C["lung"], fontsize=10)
    ax.annotate("surface tension", xy=(6.2, 150), xytext=(7.5, 214), fontsize=9, color="#8a5a1e",
                arrowprops=dict(arrowstyle="-", color="#8a5a1e", lw=0.8))
    ax.text(10.2, 92, "hysteresis", fontsize=9, color="#4d6a77", ha="center")
    ax.set_xlim(0, 30)
    ax.set_ylim(0, 230)
    ax.set_xlabel("Transpulmonary pressure (cm H$_2$O)")
    ax.set_ylabel("Lung volume (mL)")
    ax.text(30, -40, "Schematic of an isolated animal lung", fontsize=8.5, color=C["text"], ha="right")
    save(fig, "air-vs-saline.svg")


# ---------------------------------------------------------------- 6. Laplace and surfactant
def bubble_pair(ax, title, r_small, r_large, t_small, t_large, verdict):
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.6)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, loc="left", fontsize=11)
    ys = 3.3
    ax.plot([2.4, 7.2], [ys + 0.0, ys + 0.0], color=C["axis"], lw=9, solid_capstyle="butt", zorder=1)
    ax.plot([2.4, 7.2], [ys, ys], color="white", lw=6, zorder=1)
    ax.add_patch(Circle((2.4, ys), r_small, fc="white", ec=C["lung"], lw=2.5, zorder=2))
    ax.add_patch(Circle((7.2, ys), r_large, fc="white", ec=C["lung"], lw=2.5, zorder=2))
    ps, pl = 2 * t_small / r_small, 2 * t_large / r_large
    ax.text(2.4, ys - r_small - 0.55, f"r = {r_small:g}, T = {t_small:g}\nP = 2T/r = {ps:.0f}", ha="center", va="top", fontsize=9.5, color=C["ink"])
    ax.text(7.2, ys - r_large - 0.3, f"r = {r_large:g}, T = {t_large:g}\nP = 2T/r = {pl:.0f}", ha="center", va="top", fontsize=9.5, color=C["ink"])
    ax.text(0.0, 5.9, verdict, ha="left", va="top", fontsize=9.5, color=C["system"])


def fig_laplace():
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.9))
    bubble_pair(axes[0], "A. Same surface tension", 0.8, 1.6, 50, 50,
                "The small alveolus needs more pressure,\nso it empties into the large one")
    bubble_pair(axes[1], "B. With surfactant", 0.8, 1.6, 12.5, 25,
                "Surfactant is denser on the small one, so its tension\nfalls; the pressures match and both stay open")
    fig.text(0.5, -0.03, "Arbitrary units. Tension falls in the small alveolus because the same amount of surfactant covers less surface.",
             ha="center", fontsize=8.5, color=C["text"])
    save(fig, "laplace-surfactant.svg")


# ---------------------------------------------------------------- 7. Disease patterns
def fig_disease():
    cases = [("A. Pulmonary fibrosis", m.PRESETS["fibrosis"], "Stiff lung: lung curve shifts down and right.\nFRC and TLC fall; RV falls a little."),
             ("B. Emphysema", m.PRESETS["emphysema"], "Lost recoil: lung curve shifts up and left.\nFRC and TLC rise. (RV rise from air\ntrapping is not in this static model.)"),
             ("C. Obesity: load on the chest wall", m.PRESETS["obesity"], "Lung normal; chest wall curve shifts right.\nFRC falls; RV barely moves, so ERV shrinks most."),
             ("D. Respiratory muscle weakness", m.PRESETS["neuromuscular"], "Curves unchanged; muscles weak.\nTLC falls, RV rises, FRC unchanged.")]
    base = m.settings_of()
    a0 = m.analyze(base)
    (blp, blv), (bcp, bcv), (brp, brv) = curves(base, -60, 60)
    fig, axes = plt.subplots(2, 2, figsize=(11.6, 9.4), sharey=True, sharex=True)
    for ax, (title, pre, note) in zip(axes.flat, cases):
        st = m.settings_of(**pre)
        a = m.analyze(st)
        (lp, lv), (cp, cv), (rp, rvv) = curves(st, -60, 60)
        ax.set_xlim(-45, 60)
        ax.set_ylim(0, 8)
        ax.axvline(0, color=C["axis"], lw=1)
        ax.grid(color=C["grid"], lw=0.8)
        ax.set_axisbelow(True)
        if pre.get("chestWallLoad", 0):
            ax.plot(bcp, bcv, color=C["cw"], lw=1.2, ls=(0, (3, 2)), alpha=0.7)
        else:
            ax.plot(blp, blv, color=C["lung"], lw=1.2, ls=(0, (3, 2)), alpha=0.7)
        ax.plot(brp, brv, color=C["system"], lw=1.2, ls=(0, (3, 2)), alpha=0.7)
        ax.plot(cp, cv, color=C["cw"], lw=1.8)
        ax.plot(lp, lv, color=C["lung"], lw=2.2)
        ax.plot(rp, rvv, color=C["system"], lw=2.4)
        strength = pre.get("muscleStrength", 1)
        V = np.linspace(1.2, 7.8, 300)
        il = np.array([m.insp_muscle(v, strength) for v in V])
        el = np.array([-m.exp_muscle(v, strength) for v in V])
        ax.plot(il[il < 60], V[il < 60], color=C["muscle"], lw=1.6, ls=(0, (6, 3)))
        ax.plot(el[el > -45], V[el > -45], color=C["muscle"], lw=1.6, ls=(0, (6, 3)))
        rows = [("TLC", a["tlc"], a0["tlc"]), ("FRC", a["frc"], a0["frc"]), ("RV", a["rv"], a0["rv"])]
        if pre.get("lungCompliance", 1) > 1:
            rows = rows[:2]
        for lab, v, v0 in rows:
            ax.axhline(v, color="#6b6b6b", lw=0.7, ls=(0, (4, 3)))
            ax.text(-43, v + 0.08, f"{lab} {v:.1f} L ({100 * v / v0:.0f}%)", ha="left", fontsize=8.3, color="#4d4d4d",
                    bbox=dict(fc="white", ec="none", pad=0.8))
        ax.set_title(title, loc="left")
        ax.text(58, 0.25, note, fontsize=8.8, color=C["ink"], va="bottom", ha="right",
                bbox=dict(fc="white", ec="none", pad=1.5))
    for ax in axes[1]:
        ax.set_xlabel("Pressure (cm H$_2$O)")
    for ax in axes[:, 0]:
        ax.set_ylabel("Volume (L)")
    for lab, col, y in (("Lung", C["lung"], 7.55), ("Chest wall", C["cw"], 7.2), ("Respiratory system", C["system"], 6.85), ("Muscle limits", C["muscle"], 6.5)):
        axes[0, 0].text(-43, y, lab, color=col, fontsize=8.8, fontweight="bold")
    fig.text(0.5, 0.035, "Dashed thin lines: the healthy curve that changed, and the healthy respiratory system. Percent values are of the healthy model (TLC 6.0, FRC 3.0, RV 1.5 L).",
             ha="center", fontsize=8.5, color=C["text"])
    fig.subplots_adjust(wspace=0.06, hspace=0.18)
    save(fig, "disease-patterns.svg")


if __name__ == "__main__":
    fig_spirogram()
    fig_pv_curves()
    fig_muscles()
    fig_alveolus()
    fig_air_saline()
    fig_laplace()
    fig_disease()
