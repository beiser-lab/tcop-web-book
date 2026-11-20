"""Figures for the Pulmonary Circulation chapter (taught in the CV block).

Run:  cd site/scripts && MPLCONFIGDIR=$TMPDIR PNG_PREVIEW=<folder> python3 figs_pulmonary-circulation.py
Writes SVGs to ../cardiovascular/figures/pulmonary-circulation/.

Numbers from the 2025 Pulmonary Circulation deck: pulmonary artery 20/10 against systemic 120/80 at
6 L/min (slide 6); mPAP 14, PCWP 5, CO 6 at rest (slide 12). The pressure-flow curve is a
schematic in which flow rises with the square of (mPAP - PLA), with PLA held at 5 mm Hg and the
curve passing through the resting point (14 mm Hg, 6 L/min); PVR = (mPAP - PCWP)/CO x 80.
Two-alveolus HPV model saturations 100%, 87.5% and 94% from slides 21 to 23 (flow to the
unventilated unit 50% without HPV and 25% with it).
"""
import numpy as np
from matplotlib.patches import Circle, Ellipse, FancyBboxPatch, Polygon, Rectangle, FancyArrowPatch, Wedge
import figstyle as fs

plt = fs.plt
C = fs.C
M = fs.MINUS
PART, SLUG = "cardiovascular", "pulmonary-circulation"


def save(fig, name):
    fs.save(fig, PART, SLUG, name)


def arrow(ax, x0, y0, x1, y1, col, lw=1.6, rad=0.0, ms=13):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=ms, color=col, lw=lw,
                                 connectionstyle=f"arc3,rad={rad}", shrinkA=1, shrinkB=1))


# ---------------------------------------------------------------- 1. Wedge pressure
def fig_wedge():
    fig, ax = plt.subplots(figsize=(10.0, 3.9))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 5)
    ax.axis("off")
    ven, art = C["venous"], C["arterial"]
    # chambers
    for x, lab, col in ((0.9, "RA", ven), (2.5, "RV", ven), (11.9, "LA", art)):
        ax.add_patch(FancyBboxPatch((x - 0.6, 1.9), 1.2, 1.2, boxstyle="round,pad=0.02,rounding_size=0.25",
                                    fc="white", ec=col, lw=2))
        ax.text(x, 2.5, lab, ha="center", va="center", fontsize=11, color=col, fontweight="bold")
    # pulmonary artery tree: trunk then branches
    ax.plot([3.1, 4.6], [2.5, 2.5], color=ven, lw=9, solid_capstyle="round")
    for dy in (1.2, 0.0, -1.2):
        ax.plot([4.6, 6.4], [2.5, 2.5 + dy], color=ven, lw=5, solid_capstyle="round")
        for dd in (0.35, -0.35):
            ax.plot([6.4, 7.6], [2.5 + dy, 2.5 + dy + dd], color=ven, lw=2.4, solid_capstyle="round")
    # capillaries
    ax.add_patch(Rectangle((7.6, 0.8), 0.9, 3.4, fc="#efe3ea", ec="none"))
    ax.text(8.05, 4.4, "capillaries", ha="center", fontsize=8.8, color=C["text"])
    # pulmonary veins
    for dy in (1.2, 0.0, -1.2):
        for dd in (0.35, -0.35):
            ax.plot([8.5, 9.6], [2.5 + dy + dd, 2.5 + dy], color=art, lw=2.4, solid_capstyle="round")
        ax.plot([9.6, 11.3], [2.5 + dy, 2.5], color=art, lw=5, solid_capstyle="round")
    ax.text(5.3, 4.25, "pulmonary arteries", ha="center", fontsize=8.8, color=ven)
    ax.text(10.3, 4.25, "pulmonary veins", ha="center", fontsize=8.8, color=art)
    # catheter path RA -> RV -> PA -> wedge in the lowest small branch
    path_x = [0.6, 1.4, 2.2, 3.0, 4.6, 6.4, 7.35]
    path_y = [2.2, 2.2, 2.3, 2.45, 2.5, 1.3, 0.95]
    ax.plot(path_x, path_y, color=C["ink"], lw=1.6, zorder=5)
    ax.add_patch(Ellipse((7.25, 0.98), 0.42, 0.32, angle=-17, fc=C["gold"], ec=C["ink"], lw=1, zorder=6))
    # static column to LA
    ax.plot([7.45, 8.5, 9.6, 11.3], [0.93, 0.95, 1.3, 2.5], color=C["gold"], lw=2.2, ls=(0, (2, 2)), zorder=4)
    ax.annotate("balloon wedged in a small\npulmonary artery: no flow beyond it", xy=(7.25, 0.85), xytext=(3.0, 0.25),
                fontsize=8.8, color=C["ink"], arrowprops=dict(arrowstyle="-", color=C["ink"], lw=0.8))
    ax.text(9.0, 0.3, "still column of blood: tip pressure ≈ P$_\\mathrm{LA}$ (the PCWP)", fontsize=8.8, color=C["gold"])
    ax.text(0.3, 3.5, "catheter enters\nfrom a vein", fontsize=8.6, color=C["ink"])
    save(fig, "wedge.svg")


# ---------------------------------------------------------------- 2. West zones
def fig_west_zones():
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 5.0), gridspec_kw=dict(width_ratios=[1.0, 0.9]))
    ax = axes[0]
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_aspect("equal")
    # lung outline
    t = np.linspace(0, np.pi, 100)
    xs = np.concatenate([[0.6], 0.6 + 2.4 * (1 - np.cos(t)) / 2 * 0 + 0.6 * 0 + 0 * t, [5.4]])
    outline = np.array([[0.7, 0.6], [0.6, 6.0], [1.2, 8.4], [3.0, 9.6], [4.8, 8.4], [5.4, 6.0], [5.3, 0.6]])
    ax.add_patch(Polygon(outline, closed=True, fc="#fbf3ec", ec=C["lung"], lw=2))
    for y in (7.3, 4.6):
        ax.plot([0.62, 5.38], [y, y], color=C["axis"], lw=1, ls=(0, (4, 3)))
    rows = [(8.3, "Zone 1", "P$_\\mathrm{alv}$ > P$_\\mathrm{a}$ > P$_\\mathrm{v}$", "no flow"),
            (6.1, "Zone 2", "P$_\\mathrm{a}$ > P$_\\mathrm{alv}$ > P$_\\mathrm{v}$", "flow set by P$_\\mathrm{a}$ " + M + " P$_\\mathrm{alv}$"),
            (2.6, "Zone 3", "P$_\\mathrm{a}$ > P$_\\mathrm{v}$ > P$_\\mathrm{alv}$", "flow set by P$_\\mathrm{a}$ " + M + " P$_\\mathrm{v}$")]
    for y, z, order, flow in rows:
        ax.text(3.0, y + 0.4, z, ha="center", fontsize=10.5, color=C["ink"], fontweight="bold")
        ax.text(3.0, y - 0.15, order, ha="center", fontsize=9.5, color=C["ink"])
        ax.text(3.0, y - 0.7, flow, ha="center", fontsize=8.6, color=C["text"])
    ax.text(3.0, 0.0, "upright lung", ha="center", fontsize=9, color=C["text"], style="italic")
    ax.annotate("", xy=(-0.1, 1.0), xytext=(-0.1, 9.0), arrowprops=dict(arrowstyle="-|>", color=C["text"], lw=1.2), annotation_clip=False)
    ax.text(-0.35, 5.0, "gravity raises vascular pressure toward the base", rotation=90, va="center",
            ha="center", fontsize=8.4, color=C["text"])

    ax = axes[1]
    fs.grid(ax)
    h = np.linspace(0, 1, 300)          # 0 = base, 1 = apex
    z12, z23 = 0.74, 0.44
    q = np.where(h > z12, 0.0, np.where(h > z23, (z12 - h) / (z12 - z23) * 0.55, 0.55 + (z23 - h) / z23 * 0.45))
    ax.plot(q, h, color=C["system"], lw=2.6)
    for y in (z12, z23):
        ax.axhline(y, color=C["axis"], lw=1, ls=(0, (4, 3)))
    ax.text(0.85, 0.85, "Zone 1", fontsize=9.5, color=C["ink"])
    ax.text(0.85, 0.55, "Zone 2", fontsize=9.5, color=C["ink"])
    ax.text(0.25, 0.2, "Zone 3", fontsize=9.5, color=C["ink"])
    ax.set_xlim(0, 1.05)
    ax.set_ylim(0, 1)
    ax.set_xticks([])
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["base", "apex"])
    ax.set_xlabel("Blood flow per unit lung volume")
    ax.set_ylabel("Height in the lung")
    ax.text(0.03, 0.93, "zone 1 drawn large\nto show it; little\nor none in health", fontsize=8.3, color=C["text"], va="top")
    save(fig, "west-zones.svg")


# ---------------------------------------------------------------- 3. Recruitment and distension
def vessel(ax, x, y, r, open_=True, col=None):
    col = col or C["venous"]
    if open_:
        ax.add_patch(Rectangle((x, y - r), 3.0, 2 * r, fc="#dbe7ee", ec=col, lw=2))
    else:
        ax.plot([x, x + 3.0], [y, y], color=col, lw=2)
        ax.plot([x, x + 3.0], [y + 0.04, y + 0.04], color=col, lw=2)


def fig_recruitment():
    fig, axes = plt.subplots(1, 3, figsize=(10.4, 3.6))
    titles = ["A. Rest", "B. Recruitment", "C. Distension"]
    for k, ax in enumerate(axes):
        ax.set_xlim(-0.6, 4.0)
        ax.set_ylim(0, 5)
        ax.axis("off")
        ax.set_title(titles[k], fontsize=11)
        ys = [4.0, 3.0, 2.0, 1.0]
        for i, y in enumerate(ys):
            if k == 0:
                vessel(ax, 0.3, y, 0.22, open_=(i % 2 == 0))
            elif k == 1:
                vessel(ax, 0.3, y, 0.22 if i % 2 == 0 else 0.2, open_=True,
                       col=C["venous"] if i % 2 == 0 else C["arterial"])
            else:
                vessel(ax, 0.3, y, 0.36, open_=True, col=C["arterial"]) if i in (0, 2) else vessel(ax, 0.3, y, 0.22, open_=False)
        arrow(ax, -0.5, 2.5, 0.2, 2.5, C["ink"], lw=1.4)
    axes[0].text(1.8, 0.15, "2 vessels collapsed,\n2 modestly filled", ha="center", fontsize=8.6, color=C["text"])
    axes[1].text(1.8, 0.15, "collapsed vessels open:\nmore channels in parallel", ha="center", fontsize=8.6, color=C["text"])
    axes[2].text(1.8, 0.15, "vessels already open\nwiden", ha="center", fontsize=8.6, color=C["text"])
    save(fig, "recruitment-distension.svg")


# ---------------------------------------------------------------- 4. PVR and flow vs mPAP
def fig_pvr_pap():
    pla = 5.0
    P = np.linspace(10, 22, 200)
    Q = 6.0 * ((P - pla) / 9.0) ** 2          # L/min; passes through (14, 6)
    pvr = (P - pla) / Q * 80
    fig, axes = plt.subplots(1, 2, figsize=(10.0, 4.2))
    ax = axes[0]
    fs.grid(ax)
    ax.plot(P, Q, color=C["system"], lw=2.6)
    ax.plot([14], [6], "o", color=C["system"], ms=7)
    ax.annotate("rest: mPAP 14 mm Hg,\n6 L/min", xy=(14, 6), xytext=(10.4, 12), fontsize=9, color=C["ink"],
                arrowprops=dict(arrowstyle="-", color=C["ink"], lw=0.8))
    ax.set_xlabel("Mean pulmonary artery pressure (mm Hg)")
    ax.set_ylabel("Pulmonary blood flow (L/min)")
    ax.set_title("A. Small pressure rise, large flow rise")
    ax.set_xlim(10, 22)
    ax.set_ylim(0, 25)
    ax = axes[1]
    fs.grid(ax)
    ax.plot(P, pvr, color=C["venous"], lw=2.6)
    ax.plot([14], [120], "o", color=C["venous"], ms=7)
    ax.axhspan(80, 150, color=C["cool"], zorder=0)
    ax.text(21.8, 140, "normal at rest,\n80 to 150", ha="right", fontsize=8.8, color=C["ink"], va="top")
    ax.set_xlabel("Mean pulmonary artery pressure (mm Hg)")
    ax.set_ylabel("PVR (dyn·s·cm$^{" + M + "5}$)")
    ax.set_title("B. So resistance falls")
    ax.set_xlim(10, 22)
    ax.set_ylim(0, 300)
    fig.subplots_adjust(wspace=0.32)
    save(fig, "pvr-vs-pap.svg")


# ---------------------------------------------------------------- 5. Lung volume and PVR
def fig_lung_volume():
    v = np.linspace(0, 1, 300)     # 0 = RV, 1 = TLC; FRC at 0.36
    frc = 0.36
    extra = 0.22 + 1.2 * np.exp(-v / 0.12)
    alv = 0.18 + 0.164 * np.exp((v - frc) / 0.33)
    tot = extra + alv
    fig, ax = plt.subplots(figsize=(7.0, 4.6))
    fs.grid(ax)
    ax.plot(v, extra, color=C["venous"], lw=2.2)
    ax.plot(v, alv, color=C["arterial"], lw=2.2)
    ax.plot(v, tot, color=C["ink"], lw=2.8)
    ax.axvline(frc, color=C["axis"], lw=1, ls=(0, (4, 3)))
    i = np.argmin(tot)
    ax.plot([v[i]], [tot[i]], "o", color=C["ink"], ms=6)
    ax.set_xticks([0, frc, 1])
    ax.set_xticklabels(["RV", "FRC", "TLC"])
    ax.set_yticks([])
    ax.set_xlabel("Lung volume")
    ax.set_ylabel("Pulmonary vascular resistance")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 2.1)
    ax.text(0.05, 1.72, "total", color=C["ink"], fontsize=10, fontweight="bold")
    ax.annotate("extra-alveolar vessels:\nnarrow at low volume", xy=(0.17, 0.22 + 1.2 * np.exp(-0.17 / 0.12)), xytext=(0.13, 1.38),
                color=C["venous"], fontsize=9, arrowprops=dict(arrowstyle="-", color=C["venous"], lw=0.9))
    ax.text(0.55, 1.78, "alveolar vessels: squeezed\nby stretched alveolar walls", color=C["arterial"], fontsize=9)
    ax.text(frc + 0.02, 0.10, "minimum near FRC", color=C["ink"], fontsize=9)
    save(fig, "lung-volume-pvr.svg")


# ---------------------------------------------------------------- 6. Two-alveolus HPV model
def two_alveolus(ax, title, blocked, f_bad, note):
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 9)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=10.5)
    # airway
    ax.plot([4.6, 4.6, 2.9], [8.6, 7.2, 5.9], color=C["lung"], lw=2)
    ax.plot([5.4, 5.4, 7.1], [8.6, 7.2, 5.9], color=C["lung"], lw=2)
    ax.plot([4.6, 5.0, 5.4], [7.2, 6.6, 7.2], color=C["lung"], lw=2)
    ax.text(5.0, 8.75, "O$_2$", ha="center", fontsize=9.5, color=C["lung"])
    for cx, bad in ((2.6, blocked), (7.4, False)):
        ax.add_patch(Circle((cx, 4.9), 1.25, fc="#d9d9d9" if bad else "white", ec=C["lung"], lw=2))
        ax.text(cx, 4.9, "no\nventilation" if bad else "P$_A$O$_2$\n99", ha="center", va="center", fontsize=8.5,
                color=C["text"] if bad else C["ink"])
    # capillaries under each alveolus and mixing
    sat_bad = 75 if blocked else 100
    lw_bad = 1.5 + 6 * f_bad
    lw_good = 1.5 + 6 * (1 - f_bad)
    out_bad = C["venous"] if blocked else C["arterial"]
    ax.plot([0.4, 2.6], [3.2, 3.2], color=C["venous"], lw=lw_bad, solid_capstyle="round")
    ax.plot([2.6, 4.9], [3.2, 2.0], color=out_bad, lw=lw_bad, solid_capstyle="round")
    ax.plot([9.6, 7.4], [3.2, 3.2], color=C["venous"], lw=lw_good, solid_capstyle="round")
    ax.plot([7.4, 5.1], [3.2, 2.0], color=C["arterial"], lw=lw_good, solid_capstyle="round")
    ax.plot([5.0, 5.0], [2.0, 0.9], color=C["arterial"], lw=4)
    ax.text(0.2, 3.45, "S$_{\\bar{v}}$O$_2$ 75%", fontsize=8, color=C["venous"])
    ax.text(9.8, 3.45, "S$_{\\bar{v}}$O$_2$ 75%", fontsize=8, color=C["venous"], ha="right")
    ax.text(2.6, 2.45, f"{sat_bad}%", ha="center", fontsize=9.5, color=C["venous"] if blocked else C["arterial"], fontweight="bold")
    ax.text(7.4, 2.45, "100%", ha="center", fontsize=9.5, color=C["arterial"], fontweight="bold")
    ax.text(2.6, 1.6, f"flow {round(100 * f_bad)}%", ha="center", fontsize=8.3, color=C["text"])
    ax.text(7.4, 1.6, f"flow {round(100 * (1 - f_bad))}%", ha="center", fontsize=8.3, color=C["text"])
    sa = f_bad * sat_bad + (1 - f_bad) * 100
    lab = {100.0: "100", 87.5: "87.5", 93.75: "94"}.get(round(sa, 2), f"{sa:.0f}")
    ax.text(5.0, 0.35, f"to left atrium: SaO$_2$ ≈ {lab}%", ha="center", fontsize=9.5,
            color=C["ink"], fontweight="bold")
    ax.text(5.0, -0.5, note, ha="center", fontsize=8.3, color=C["text"], va="top")


def fig_hpv():
    fig, axes = plt.subplots(1, 3, figsize=(11.4, 4.6))
    two_alveolus(axes[0], "A. Both alveoli ventilated", False, 0.5, "")
    two_alveolus(axes[1], "B. One alveolus blocked, no HPV", True, 0.5, "half the flow passes\nan unventilated alveolus")
    two_alveolus(axes[2], "C. With hypoxic vasoconstriction", True, 0.25, "vessels next to the hypoxic\nalveolus constrict; flow shifts")
    fig.subplots_adjust(wspace=0.05)
    save(fig, "hpv-two-alveolus.svg")


# ---------------------------------------------------------------- 7. RV response to raised PVR
def heart(ax, title, r, a, rv_w, lv_squash, note):
    """Short-axis sketch: LV ring at the origin, RV crescent on the left on a circle of radius r at (-a, 0)."""
    R, lv_w = 1.4, 0.55
    ax.set_xlim(-4.6, 1.8)
    ax.set_ylim(-3.6, 2.6)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=10.5)
    x = (r * r - R * R - a * a) / (2 * a)
    y = np.sqrt(max(R * R - x * x, 0.01))
    th = np.degrees(np.arctan2(y, x + a))
    ax.add_patch(Circle((-a, 0), r, fc="#eef3f6", ec="none"))
    ax.add_patch(Wedge((-a, 0), r + rv_w, th, 360 - th, width=rv_w, fc=C["venous"], ec="none"))
    if lv_squash < 1:
        # septum flattened: clip the LV circle on its left (septal) side
        def d_shape(rad, xcut):
            t = np.linspace(0, 2 * np.pi, 400)
            xs, ys = rad * np.cos(t), rad * np.sin(t)
            return np.column_stack([np.maximum(xs, xcut), ys])
        cut = -R * 0.55
        ax.add_patch(Polygon(d_shape(R, cut), closed=True, fc=C["arterial"], ec="white", lw=1))
        ax.add_patch(Polygon(d_shape(R - lv_w, cut + lv_w), closed=True, fc="white", ec="none"))
    else:
        ax.add_patch(Circle((0, 0), R, fc=C["arterial"], ec="white", lw=1))
        ax.add_patch(Circle((0, 0), R - lv_w, fc="white", ec="none"))
    ax.text(0.05, 0, "LV", ha="center", va="center", fontsize=10, color=C["arterial"], fontweight="bold")
    ax.text(-a - r * 0.35, 0, "RV", ha="center", va="center", fontsize=10, color=C["venous"], fontweight="bold")
    ax.text(-1.4, -3.3, note, ha="center", fontsize=8.6, color=C["text"])


def fig_rv():
    fig, axes = plt.subplots(1, 3, figsize=(10.8, 3.9))
    heart(axes[0], "A. Normal", 1.75, 1.15, 0.2, 1.0, "thin RV wall, low pressure")
    heart(axes[1], "B. Acute rise in PVR", 2.25, 1.75, 0.16, 0.8, "RV dilates; septum pushed\ntoward the LV; RV failure")
    heart(axes[2], "C. Chronic rise in PVR", 1.75, 1.15, 0.55, 1.0, "RV hypertrophies over time\n(cor pulmonale)")
    fig.subplots_adjust(wspace=0.05)
    save(fig, "rv-response.svg")


if __name__ == "__main__":
    fig_wedge()
    fig_west_zones()
    fig_recruitment()
    fig_pvr_pap()
    fig_lung_volume()
    fig_hpv()
    fig_rv()
