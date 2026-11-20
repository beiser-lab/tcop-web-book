"""Figures for the Ventilation and Perfusion chapter.

Run:  cd site/scripts && MPLCONFIGDIR=$TMPDIR PNG_PREVIEW=<folder> python3 figs_ventilation-perfusion.py
Writes SVGs to ../pulmonary/figures/ventilation-perfusion/.

Relations used:
  HbO2 curve: Severinghaus form, S = 1 / (1 + 23400 / (P^3 + 150 P)), which passes through the course
     anchor points (PO2 27: 50%, 40: 75%, 60: 90%, 100: 97.5%).
  O2 content: CaO2 = 1.39 x Hb x S + 0.003 x PO2, Hb 15 g/dL (course constants).
  Alveolar gas: PAO2 = (PB - 47) FiO2 - PaCO2/R, R 0.8.
  Shunt mixing: contents mix in proportion to flow; saturation is read back from the mixed content.
  Iso-shunt: fixed arterial-mixed venous content difference of 5 mL/dL, PaCO2 40, PB 760.
"""
import numpy as np
import figstyle as fs
from figstyle import C, plt, MINUS
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle, FancyArrowPatch
from scipy.optimize import brentq

PART, SLUG = "pulmonary", "ventilation-perfusion"
HB = 15.0


def save(fig, name):
    fs.save(fig, PART, SLUG, name)


def sat(p):
    p = np.maximum(p, 0.01)
    return 1.0 / (1.0 + 23400.0 / (p ** 3 + 150.0 * p))


def content(p, s=None):
    s = sat(p) if s is None else s
    return 1.39 * HB * s + 0.003 * p


def p_from_content(c):
    return brentq(lambda p: content(p) - c, 0.5, 3000)


def mix(streams):
    """streams: list of (flow fraction, PO2). Returns (PO2, SO2) of the mixture."""
    c = sum(f * content(p) for f, p in streams)
    p = p_from_content(c)
    return p, sat(p)


# ---------------------------------------------------------------- 1. dead space and breathing pattern
def fig_dead_space():
    fig = plt.figure(figsize=(9.6, 4.4))
    a = fig.add_axes([0.0, 0.0, 0.40, 1.0])
    a.set_xlim(0, 10)
    a.set_ylim(0, 10)
    a.set_aspect("equal")
    a.axis("off")
    air = "#f4c9a3"
    # airway tree
    a.add_patch(Rectangle((4.4, 6.2), 1.2, 3.3, color=air))
    a.plot([4.4, 2.4], [6.25, 4.3], color=air, lw=26, solid_capstyle="butt")
    a.plot([5.6, 7.6], [6.25, 4.3], color=air, lw=26, solid_capstyle="butt")
    a.text(5.0, 7.7, "Anatomic\ndead space", ha="center", va="center", fontsize=10, color=C["ink"])
    a.text(5.0, 9.75, "~150 mL", ha="center", fontsize=9, color=C["text"])
    for cx, lab, sub, perf in ((2.2, "Alveolar\nventilation", "perfused alveolus", True),
                               (7.8, "Alveolar\ndead space", "ventilated, not perfused", False)):
        a.add_patch(Circle((cx, 3.0), 1.55, fc="#d9ebf7", ec="none"))
        th = np.linspace(np.pi * 0.95, np.pi * 2.05, 80)
        xs, ys = cx + 1.75 * np.cos(th), 3.0 + 1.75 * np.sin(th)
        if perf:
            for k in range(len(th) - 1):
                frac = k / (len(th) - 1)
                col = (0.2 + 0.5 * frac, 0.25 - 0.1 * frac, 0.6 - 0.45 * frac)
                a.plot(xs[k:k + 2], ys[k:k + 2], color=col, lw=6, solid_capstyle="butt")
        else:
            a.plot(xs, ys, color=C["axis"], lw=6, ls=(0, (2, 1.5)))
        a.text(cx, 3.0, lab, ha="center", va="center", fontsize=9.5, color=C["ink"])
        a.text(cx, 0.6, sub, ha="center", fontsize=9, color=C["text"])
    a.text(0.0, 9.6, "A", fontsize=13, fontweight="bold", color=C["ink"])
    a.text(5.0, -0.3, "Physiologic dead space = anatomic + alveolar", ha="center", fontsize=9.5, color=C["ink"])

    b = fig.add_axes([0.62, 0.14, 0.37, 0.74])
    # slide 5: fast (VT 500, RR 30) vs deep (VT 1000, RR 15)
    pats = [("Fast\nV$_T$ 500 mL, 30/min", 150, 350, 30), ("Deep\nV$_T$ 1000 mL, 15/min", 170, 830, 15)]
    for i, (lab, vd, va, rr) in enumerate(pats):
        dsv, alv = vd * rr / 1000, va * rr / 1000
        b.barh(i, alv, color=C["venous"], height=0.55)
        b.barh(i, dsv, left=alv, color=air, height=0.55)
        b.text(alv / 2, i, f"V̇$_A$ {alv:.1f}", ha="center", va="center", color="white", fontsize=10,
               fontweight="bold")
        b.text(alv + dsv / 2, i, f"{dsv:.1f}", ha="center", va="center", color=C["ink"], fontsize=9.5)
        b.text(alv + dsv + 0.3, i, f"V$_D$/V$_T$ {vd / (vd + va):.2f}", va="center", fontsize=9.5, color=C["ink"])
    b.set_yticks([0, 1])
    b.set_yticklabels([p[0] for p in pats], fontsize=9.5)
    b.set_xlim(0, 21)
    b.set_ylim(-0.6, 1.6)
    b.set_xlabel("Ventilation (L/min); both give V̇$_E$ 15 L/min")
    b.text(-0.5, 1.13, "B", transform=b.transAxes, fontsize=13, fontweight="bold", color=C["ink"])
    from matplotlib.patches import Patch
    b.legend(handles=[Patch(color=C["venous"], label="alveolar"), Patch(color=air, label="dead space")],
             loc="upper right", fontsize=9, ncol=2, bbox_to_anchor=(1.0, 1.12))
    fs.grid(b)
    save(fig, "dead-space.svg")


# ---------------------------------------------------------------- 2. Bohr method
def fig_bohr():
    fig, axs = plt.subplots(1, 2, figsize=(9.2, 3.9), sharey=True)
    v = np.linspace(0, 500, 501)

    def profile(vd, plateau):
        # smooth phase II over about 40 mL
        return plateau / (1 + np.exp(-(v - vd) / 9))

    for ax, (title, plateau, note) in zip(axs, [
            ("A  Healthy lung", 40, None),
            ("B  Half the alveoli unperfused (embolism)", 20, True)]):
        pco2 = profile(150, plateau)
        mixed = np.trapezoid(pco2, v) / 500
        ax.fill_between(v, 0, pco2, color=C["highlight"], zorder=1)
        ax.plot(v, pco2, color=C["gold"], lw=2.4, zorder=3)
        ax.axhline(40, color=C["arterial"], lw=1.4, ls="--", zorder=2)
        ax.text(5, 41.5, "PaCO$_2$ 40", color=C["arterial"], fontsize=9.5)
        ax.axhline(mixed, color=C["ink"], lw=1.4, ls=":", zorder=2)
        ax.text(495, mixed + 1.3, f"mixed expired PĒCO$_2$ {mixed:.0f}", color=C["ink"], fontsize=9.5,
                ha="right")
        ax.annotate(f"end-tidal {plateau}", xy=(500, plateau), xytext=(360, plateau + 6) if plateau < 30 else (300, 45.5),
                    fontsize=9.5, color=C["gold"], arrowprops=dict(arrowstyle="->", color=C["gold"], lw=0.9))
        ax.annotate("", xy=(0, -3.6), xytext=(150, -3.6),
                    arrowprops=dict(arrowstyle="<->", color=C["text"], lw=1), annotation_clip=False)
        ax.text(75, -2.9, "anatomic V$_D$", ha="center", fontsize=8.5, color=C["text"], va="bottom")
        vdvt = (40 - mixed) / 40
        ax.text(250, 8, f"V$_D$/V$_T$ = (40 {MINUS} {mixed:.0f}) / 40 = {vdvt:.2f}", ha="center", fontsize=10,
                color=C["ink"], bbox=dict(fc="white", ec=C["axis"], boxstyle="round,pad=0.3"))
        ax.set_title(title, fontsize=11)
        ax.set_xlim(0, 500)
        ax.set_ylim(-5, 50)
        ax.set_xlabel("Volume exhaled (mL)")
        fs.grid(ax)
    axs[0].set_ylabel("PCO$_2$ of exhaled gas (mm Hg)")
    fig.tight_layout(w_pad=2)
    save(fig, "bohr.svg")


# ---------------------------------------------------------------- 3. regional V/Q
def fig_regional():
    fig, (a, b) = plt.subplots(1, 2, figsize=(9.4, 4.2), gridspec_kw=dict(width_ratios=[1.0, 1.25]))
    regions = ["Base", "Middle", "Apex"]
    va = [0.82, 0.52, 0.24]
    q = [1.29, 0.50, 0.07]
    y = np.arange(3)
    a.barh(y + 0.18, va, height=0.34, color=C["venous"], label="V̇$_A$ (ventilation)")
    a.barh(y - 0.18, q, height=0.34, color=C["arterial"], label="Q̇ (blood flow)")
    for i in range(3):
        a.text(va[i] + 0.03, y[i] + 0.18, f"{va[i]:.2f}", va="center", fontsize=9, color=C["venous"])
        a.text(q[i] + 0.03, y[i] - 0.18, f"{q[i]:.2f}", va="center", fontsize=9, color=C["arterial"])
        a.text(1.78, y[i], ["0.63", "1.0", "3.3"][i], va="center",
               ha="center", fontsize=11, fontweight="bold", color=C["ink"])
    a.text(1.78, 2.62, "V̇/Q̇", ha="center", fontsize=10.5, fontweight="bold", color=C["ink"])
    a.set_yticks(y)
    a.set_yticklabels(regions)
    a.set_xlim(0, 2.0)
    a.set_ylim(-0.6, 2.9)
    a.set_xticks([0, 0.5, 1.0, 1.5])
    a.set_xlabel("L/min, per region")
    a.legend(loc="upper left", fontsize=8.5, bbox_to_anchor=(0.0, -0.2), ncol=2)
    a.set_title("A  Upright lung, three slices", fontsize=11)
    fs.grid(a)
    # panel B: PO2-PCO2 points from the lecture's Costanzo figure
    pts = [("Mixed venous\nblood", 40, 46), ("Base\n(V̇/Q̇ lowest)", 89, 42),
           ("Middle", 100, 40), ("Apex\n(V̇/Q̇ highest)", 130, 33), ("Inspired\nair", 150, 0)]
    from scipy.interpolate import PchipInterpolator
    xs = np.array([p[1] for p in pts], float)
    ys = np.array([p[2] for p in pts], float)
    f = PchipInterpolator(xs, ys)
    xx = np.linspace(40, 150, 300)
    b.plot(xx, f(xx), color=C["purple"], lw=2)
    offs = [(4, 3.5), (-10, -6), (-2, 4.5), (4, 4.5), (-28, 3)]
    for (lab, px, py), (dx, dy) in zip(pts, offs):
        b.plot(px, py, "o", color=C["purple"], ms=7, zorder=5)
        b.text(px + dx, py + dy, lab, fontsize=9, color=C["ink"], va="center")
    b.text(58, 18, "V̇/Q̇ rises to the right", fontsize=9.5, color=C["purple"], rotation=0)
    b.set_xlim(30, 165)
    b.set_ylim(-2, 55)
    b.set_xlabel("PO$_2$ (mm Hg)")
    b.set_ylabel("PCO$_2$ (mm Hg)")
    b.set_title("B  Alveolar gas set by V̇/Q̇", fontsize=11)
    fs.grid(b)
    fig.tight_layout(w_pad=2.5)
    save(fig, "regional-vq.svg")


# ---------------------------------------------------------------- unit drawing for alveolus models
def unit(ax, cx, cy, alv_text, cap_in, cap_out, filled=False, vent=True, r=0.9, flow_w=1.0, label=None,
         alv_fc="white"):
    ax.add_patch(Circle((cx, cy + 0.35), r, fc="#c9c3b8" if filled else alv_fc, ec=C["lung"], lw=1.6, zorder=3))
    if vent:
        ax.add_patch(Rectangle((cx - 0.17, cy + 0.35 + r - 0.05), 0.34, 1.0, fc=alv_fc if not filled else "white",
                               ec="none", zorder=2))
        ax.plot([cx - 0.17, cx - 0.17], [cy + 0.35 + r - 0.1, cy + 0.35 + r + 0.95], color=C["lung"], lw=1.6, zorder=4)
        ax.plot([cx + 0.17, cx + 0.17], [cy + 0.35 + r - 0.1, cy + 0.35 + r + 0.95], color=C["lung"], lw=1.6, zorder=4)
    else:
        ax.plot([cx - 0.17, cx - 0.17], [cy + 0.35 + r - 0.1, cy + 0.35 + r + 0.95], color=C["lung"], lw=1.6)
        ax.plot([cx + 0.17, cx + 0.17], [cy + 0.35 + r - 0.1, cy + 0.35 + r + 0.95], color=C["lung"], lw=1.6)
    ax.text(cx, cy + 0.35, alv_text, ha="center", va="center", fontsize=8.5, color=C["ink"], zorder=5)
    # capillary under the alveolus
    lw = 4 + 6 * flow_w
    ax.plot([cx - 1.3, cx + 1.3], [cy - 0.75, cy - 0.75], color=C["venous"], lw=lw, solid_capstyle="butt",
            zorder=1, alpha=0.9)
    ax.plot([cx, cx + 1.3], [cy - 0.75, cy - 0.75], color=C["arterial"] if not filled else C["venous"], lw=lw,
            solid_capstyle="butt", zorder=1, alpha=0.9)
    ax.text(cx - 1.35, cy - 1.25, cap_in, ha="left", va="top", fontsize=8, color=C["venous"])
    ax.text(cx + 1.35, cy - 1.25, cap_out, ha="right", va="top", fontsize=8,
            color=C["arterial"] if not filled else C["venous"])
    if label:
        ax.text(cx, cy + 2.55, label, ha="center", fontsize=8.5, color=C["text"])


def panel(ax, title):
    ax.set_xlim(0, 7)
    ax.set_ylim(-2.9, 3.6)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=10.5, loc="left")


def mixed_box(ax, text, col=C["arterial"]):
    ax.text(3.5, -2.45, text, ha="center", va="center", fontsize=9.5, color=col, fontweight="bold",
            bbox=dict(fc="white", ec=col, boxstyle="round,pad=0.3"))


# ---------------------------------------------------------------- 5. V/Q spectrum
def fig_spectrum():
    fig, axs = plt.subplots(1, 3, figsize=(9.2, 2.9))
    specs = [("V̇/Q̇ = 0: shunt", "no air\nPO$_2$ 40\nPCO$_2$ 46", "40 / 46", "40 / 46", True, True),
             ("V̇/Q̇ near 1: matched", "PAO$_2$ 100\nPACO$_2$ 40", "40 / 46", "100 / 40", False, True),
             ("V̇/Q̇ = ∞: dead space", "PAO$_2$ 150\nPACO$_2$ 0", "no blood flow", "", False, False)]
    for ax, (title, alv, cin, cout, filled, perf) in zip(axs, specs):
        ax.set_xlim(0, 7)
        ax.set_ylim(-1.8, 3.6)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.text(3.5, 3.4, title, ha="center", fontsize=10.5, fontweight="bold", color=C["ink"])
        ax.add_patch(Circle((3.5, 0.6), 1.05, fc="#c9c3b8" if filled else "white", ec=C["lung"], lw=1.6, zorder=3))
        ax.plot([3.33, 3.33], [1.6, 2.8], color=C["lung"], lw=1.6)
        ax.plot([3.67, 3.67], [1.6, 2.8], color=C["lung"], lw=1.6)
        if filled:
            ax.plot([3.25, 3.75], [2.3, 2.3], color=C["lung"], lw=3)
        ax.text(3.5, 0.6, alv, ha="center", va="center", fontsize=8.8, color=C["ink"], zorder=5)
        if perf:
            ax.plot([1.3, 3.5], [-0.75, -0.75], color=C["venous"], lw=8, solid_capstyle="butt")
            ax.plot([3.5, 5.7], [-0.75, -0.75], color=C["venous"] if filled else C["arterial"], lw=8,
                    solid_capstyle="butt")
            ax.text(1.3, -1.25, "in " + cin, fontsize=8.5, color=C["venous"], va="top")
            ax.text(5.7, -1.25, "out " + cout, fontsize=8.5, ha="right", va="top",
                    color=C["venous"] if filled else C["arterial"])
        else:
            ax.plot([1.3, 5.7], [-0.75, -0.75], color=C["axis"], lw=3, ls=(0, (3, 2)))
            ax.text(3.5, -1.25, cin, ha="center", fontsize=8.5, color=C["text"], va="top")
    save(fig, "vq-spectrum.svg")


# ---------------------------------------------------------------- 6. shunt in the two-alveolus model
def fig_shunt():
    pv_norm = 40.0
    pv_low = brentq(lambda p: sat(p) - 0.50, 5, 60)  # SvO2 50%
    fig, axs = plt.subplots(2, 2, figsize=(9.2, 7.4))
    cases = [
        ("A  Shunt, room air", 0.21, pv_norm),
        ("B  Same shunt, 100% O$_2$", 1.0, pv_norm),
        ("C  Same shunt, low SvO$_2$ (50%), 100% O$_2$", 1.0, pv_low),
    ]
    out = []
    for ax, (title, fio2, pv) in zip([axs[0, 0], axs[0, 1], axs[1, 0]], cases):
        panel(ax, title)
        pao2 = 0.21 * 713 - 40 / 0.8 if fio2 < 0.5 else 1.0 * 713 - 40 / 0.8
        sv = sat(pv)
        good_s = 1.0  # course convention: 100% leaving a ventilated unit
        unit(ax, 1.8, 0.6, "pus or\nfluid", f"SO$_2$ {sv * 100:.0f}%", f"{sv * 100:.0f}%", filled=True, vent=False)
        unit(ax, 5.2, 0.6, f"PAO$_2$\n{pao2:.0f}", f"SO$_2$ {sv * 100:.0f}%", "100%")
        c_good = content(pao2, good_s)
        c_bad = content(pv, sv)
        cm = 0.5 * c_good + 0.5 * c_bad
        pm = p_from_content(cm)
        out.append((title, sv, pao2, cm, sat(pm), pm))
        avg = (sv * 100 + 100) / 2
        mixed_box(ax, f"Mixed (equal flow): SaO$_2$ about {sat(pm) * 100:.0f}%")
    # panel D: shunt fraction vs SaO2 on room air and 100% O2
    ax = axs[1, 1]
    f = np.linspace(0, 0.6, 61)
    for fio2, col, lab in ((0.21, C["venous"], "room air"), (1.0, C["arterial"], "100% O$_2$")):
        pao2 = fio2 * 713 - 40 / 0.8
        s = []
        for fr in f:
            cm = (1 - fr) * content(pao2, 1.0) + fr * content(pv_norm)
            s.append(sat(p_from_content(cm)) * 100)
        ax.plot(f * 100, s, color=col, lw=2.2, label=lab)
    ax.axvline(50, color=C["axis"], lw=1, ls="--")
    ax.set_xlim(0, 60)
    ax.set_ylim(70, 101)
    ax.set_xlabel("Shunt fraction (% of blood flow)")
    ax.set_ylabel("SaO$_2$ (%)")
    ax.set_title("D  More O$_2$ barely helps a large shunt", fontsize=10.5, loc="left")
    ax.legend(loc="lower left", fontsize=9)
    ax.text(49, 99, "panels A to C\n(50% shunt)", fontsize=8.5, color=C["text"], va="top", ha="right")
    fs.grid(ax)
    fig.tight_layout(h_pad=1.5, w_pad=1.5)
    save(fig, "shunt-two-alveolus.svg")
    return out


# ---------------------------------------------------------------- 7. low V/Q and HPV
def fig_lowvq_hpv():
    fig, axs = plt.subplots(1, 3, figsize=(10.2, 3.9))
    # A and B: low V/Q unit (slide 58 numbers) on room air and with more O2
    panel(axs[0], "A  Low V̇/Q̇, room air")
    unit(axs[0], 1.8, 0.6, "PAO$_2$ 77\nPACO$_2$ 45", "40 / 46", "77", flow_w=1.0, label="narrowed airway")
    unit(axs[0], 5.2, 0.6, "PAO$_2$ 105\nPACO$_2$ 36", "40 / 46", "105", label="extra ventilation")
    pm, sm = mix([(0.5, 77), (0.5, 105)])
    mixed_box(axs[0], "Mixed: PO$_2$ about 89, PCO$_2$ about 40")
    # B: same units, FiO2 0.30: each alveolar PO2 rises by about 0.09 x 713 = 64
    rise = 0.09 * 713
    panel(axs[1], "B  Same lung, 30% O$_2$")
    unit(axs[1], 1.8, 0.6, f"PAO$_2$\nabout {77 + rise:.0f}", "40 / 46", f"{77 + rise:.0f}")
    unit(axs[1], 5.2, 0.6, f"PAO$_2$\nabout {105 + rise:.0f}", "40 / 46", f"{105 + rise:.0f}")
    pm2, sm2 = mix([(0.5, 77 + rise), (0.5, 105 + rise)])
    mixed_box(axs[1], f"Mixed: SaO$_2$ about {sm2 * 100:.0f}%")
    # C: HPV in a shunt: flow to the airless unit falls from 50% to 25%
    panel(axs[2], "C  Shunt with hypoxic vasoconstriction")
    unit(axs[2], 1.8, 0.6, "airless", "75%", "75%", filled=True, vent=False, flow_w=0.25, label="vessel constricted")
    unit(axs[2], 5.2, 0.6, "PAO$_2$\n99", "75%", "100%", flow_w=1.0, label="gets the diverted flow")
    cm = 0.25 * content(40) + 0.75 * content(99, 1.0)
    s3 = sat(p_from_content(cm))
    mixed_box(axs[2], f"Shunt 25%: SaO$_2$ about {s3 * 100:.0f}%")
    fig.tight_layout(w_pad=1.0)
    save(fig, "lowvq-hpv.svg")
    return (pm, sm, pm2, sm2, s3)


# ---------------------------------------------------------------- 8. approach to hypoxemia
def fig_flowchart():
    fig, ax = plt.subplots(figsize=(8.8, 5.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis("off")

    def box(x, y, w, h, text, ec, fc="white", fs_=10, bold=False):
        ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.05,rounding_size=0.15",
                                    fc=fc, ec=ec, lw=1.6))
        ax.text(x, y, text, ha="center", va="center", fontsize=fs_, color=C["ink"],
                fontweight="bold" if bold else "normal", linespacing=1.3)

    def arrow(x0, y0, x1, y1, lab=None, lx=0, ly=0):
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle="-|>", color=C["text"], lw=1.4))
        if lab:
            ax.text((x0 + x1) / 2 + lx, (y0 + y1) / 2 + ly, lab, fontsize=9.5, color=C["text"], ha="center")

    box(5, 6.35, 4.6, 0.8, "Low PaO$_2$: calculate PAO$_2$, then the A" + MINUS + "a gradient", C["ink"], fs_=10.5,
        bold=True)
    box(2.3, 4.5, 3.9, 1.35, "Normal gradient: low PAO$_2$\nHypoventilation (high PaCO$_2$)\nAltitude (low PB)\n"
        "Suffocation (low FiO$_2$)", C["venous"], fc="#eef4f8")
    box(7.4, 4.75, 3.6, 0.85, "Raised gradient: gas exchange\nGive O$_2$ (FiO$_2$ up to 1.0)", C["arterial"],
        fc="#f8eeee")
    box(5.9, 2.55, 2.6, 1.05, "Responsive\nLow V̇/Q̇\n(diffusion limitation too)", C["green"], fc="#eef5f0")
    box(8.9, 2.55, 2.0, 1.05, "Not responsive\nShunt", C["arterial"], fc="#f8eeee")
    arrow(4.0, 5.95, 2.9, 5.2, "normal", -0.25, 0.05)
    arrow(6.0, 5.95, 7.0, 5.2, "increased", 0.4, 0.05)
    arrow(6.9, 4.3, 6.2, 3.1)
    arrow(8.1, 4.3, 8.7, 3.1)
    ax.text(7.4, 1.35, "A low mixed venous O$_2$ (low cardiac output, fever, high extraction)\nmakes shunt and "
            "low V̇/Q̇ worse; it does little in normal lungs.", ha="center", fontsize=9, color=C["text"])
    ax.text(2.3, 3.4, "Supplemental O$_2$ corrects the PaO$_2$,\nbut only more ventilation fixes a high PaCO$_2$.",
            ha="center", va="top", fontsize=9, color=C["text"])
    save(fig, "hypoxemia-approach.svg")


if __name__ == "__main__":
    fig_dead_space()
    fig_bohr()
    fig_regional()
    fig_spectrum()
    for row in fig_shunt():
        print("shunt", row)
    print("lowvq/hpv", fig_lowvq_hpv())
    fig_flowchart()
