"""Figures for the Cardiovascular Physiology Overview chapter.

Run:  cd site/scripts && MPLCONFIGDIR=$TMPDIR PNG_PREVIEW=<folder> python3 figs_cv-overview.py
Writes SVGs to ../cardiovascular/figures/cv-overview/.
"""
import numpy as np
import figstyle as fs
from figstyle import C, plt
from matplotlib.patches import FancyBboxPatch, Polygon, Rectangle

PART, SLUG = "cardiovascular", "cv-overview"
ART, VEN, LYM = C["arterial"], C["venous"], C["green"]


# ------------------------------------------------------------------ 1. The circuit
def capillary(ax, x, y, w=0.9, h=0.34, color=C["gray"]):
    """A small capillary bed: a box of fine parallel channels."""
    ax.add_patch(Rectangle((x - w / 2, y - h / 2), w, h, fc="white", ec=color, lw=0.9, zorder=3))
    for k in range(4):
        yy = y - h / 2 + h * (k + 0.5) / 4
        ax.plot([x - w / 2, x + w / 2], [yy, yy], color=color, lw=0.6, zorder=4)


def arteriole(ax, x0, x1, y):
    """Arteriole drawn as a narrowing wedge (blood flows right to left here)."""
    ax.add_patch(Polygon([[x1, y + 0.09], [x0, y + 0.035], [x0, y - 0.035], [x1, y - 0.09]],
                         closed=True, fc=ART, ec=ART, zorder=3))


def bed(ax, y, label, xa=8.6, xv=1.4, series=None):
    """Artery trunk at xa to vein trunk at xv; blood runs right to left."""
    ax.plot([xa, 7.3], [y, y], color=ART, lw=2.2, zorder=2)
    arteriole(ax, 6.5, 7.3, y)
    if series is None:
        capillary(ax, 5.9, y)
        ax.plot([5.45, xv], [y, y], color=VEN, lw=2.2, zorder=2)
    else:
        capillary(ax, 5.9, y)
        ax.plot([5.45, 4.9], [y, y], color=VEN if series == "portal" else ART, lw=2.0, zorder=2)
        if series == "kidney":
            arteriole(ax, 4.3, 4.9, y)
            capillary(ax, 3.75, y)
        else:
            capillary(ax, 4.35, y)
        x_end = 3.3 if series == "kidney" else 3.9
        ax.plot([x_end, xv], [y, y], color=VEN, lw=2.2, zorder=2)
    ax.text(9.25, y, label, va="center", ha="left", fontsize=9.5, color=C["ink"])


def fig_circuit():
    fig, ax = plt.subplots(figsize=(9.6, 8.6))
    ax.set_xlim(0.2, 12.6)
    ax.set_ylim(-0.6, 10.6)
    ax.set_aspect("equal")
    ax.axis("off")
    xa, xv = 8.6, 1.4
    # heart
    ax.add_patch(FancyBboxPatch((2.4, 7.6), 2.0, 1.1, boxstyle="round,pad=0.05", fc=C["cool"], ec=VEN, lw=1.4))
    ax.add_patch(FancyBboxPatch((5.6, 7.6), 2.0, 1.1, boxstyle="round,pad=0.05", fc=C["highlight"], ec=ART, lw=1.4))
    ax.text(3.4, 8.15, "Right heart", ha="center", va="center", fontsize=10, color=VEN, fontweight="bold")
    ax.text(6.6, 8.15, "Left heart", ha="center", va="center", fontsize=10, color=ART, fontweight="bold")
    # pulmonary circuit (series with the systemic circuit)
    ax.plot([3.4, 3.4, 4.6], [8.75, 9.9, 9.9], color=VEN, lw=2.2)
    capillary(ax, 5.0, 9.9, w=0.8)
    ax.plot([5.4, 6.6, 6.6], [9.9, 9.9, 8.75], color=ART, lw=2.2)
    ax.text(5.0, 10.3, "Lungs (pulmonary circulation)", ha="center", fontsize=9.5, color=C["ink"])
    ax.text(3.25, 9.3, "pulmonary\nartery", ha="right", fontsize=8, color=VEN, va="center")
    ax.text(6.75, 9.3, "pulmonary\nveins", ha="left", fontsize=8, color=ART, va="center")
    # aorta and arterial trunk
    ax.plot([7.65, xa, xa], [8.15, 8.15, 0.6], color=ART, lw=3.0, zorder=2)
    ax.text(7.9, 8.3, "aorta", fontsize=8, color=ART)
    # venous trunk to right heart
    ax.plot([xv, xv, 2.35], [0.6, 8.15, 8.15], color=VEN, lw=3.6, zorder=2)
    ax.text(1.4, 8.4, "venae cavae", fontsize=8, color=VEN, ha="center")
    # systemic beds in parallel
    rows = [(6.9, "Brain", None), (6.1, "Heart muscle (coronary)", None), (5.3, "Arms", None),
            (4.3, "Gut, then liver", "portal"), (3.3, "Kidney", "kidney"), (2.3, "Skin", None),
            (1.4, "Skeletal muscle (legs)", None)]
    for y, lab, series in rows:
        bed(ax, y, lab, xa=xa, xv=xv, series=series)
    ax.text(5.17, 4.12, "portal\nvein", fontsize=7, color=VEN, ha="center", va="top", linespacing=0.9)
    ax.annotate("", xy=(4.35, 4.48), xytext=(8.6, 4.85),
                arrowprops=dict(arrowstyle="-", color=ART, lw=1.4, connectionstyle="arc3,rad=0.0"))
    ax.text(7.1, 4.98, "hepatic artery", fontsize=7.5, color=ART, ha="center")
    ax.text(2.55, 3.8, "two capillary\nbeds in series", fontsize=7.5, color=C["text"], ha="center", va="center", linespacing=1.0)
    # lymphatics
    ax.plot([5.9, 5.9, 0.5, 0.5, xv - 0.05], [1.2, 0.2, 0.2, 7.4, 7.4], color=LYM, lw=1.4, ls=(0, (4, 2)))
    ax.text(3.6, -0.15, "Lymphatics return fluid and protein that leak from capillaries", fontsize=8.5,
            color=LYM, ha="center", va="top")
    # flow arrows
    for (x0, y0, x1, y1, col) in ((xa, 7.4, xa, 7.0, ART), (xv, 7.0, xv, 7.4, VEN)):
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle="-|>", color=col, lw=0, mutation_scale=16))
    # roles, labeled on the brain row and along the trunks
    y0 = 6.9
    ax.text(6.9, y0 + 0.22, "arteriole: sets\nresistance and flow", ha="center", va="bottom", fontsize=7.5,
            color=ART, linespacing=1.0)
    ax.text(5.9, y0 - 0.25, "capillaries:\nexchange", ha="center", va="top", fontsize=7.5, color=C["gray"],
            linespacing=1.0)
    ax.text(xa + 0.32, 4.0, "Arteries: distribute blood, store pressure", rotation=90, ha="center",
            va="center", fontsize=8.5, color=ART)
    ax.text(xv - 0.3, 4.0, "Veins: store volume (about two-thirds of the blood)", rotation=90, ha="center",
            va="center", fontsize=8.5, color=VEN)
    ax.text(9.15, 9.0, "Heart: a pump that ejects\nwhatever blood returns to it", fontsize=8.5, color=C["ink"],
            va="center")
    fs.save(fig, PART, SLUG, "circuit.svg")


# ------------------------------------------------------------------ 2. Pressure along the systemic circuit
def fig_pressure_profile():
    segs = [("Left\nventricle", 0.0, 1.0), ("Aorta and\nlarge arteries", 1.0, 3.0), ("Small arteries\nand arterioles", 3.0, 5.0),
            ("Capillaries", 5.0, 6.2), ("Venules\nand veins", 6.2, 8.2), ("Venae cavae,\nright atrium", 8.2, 9.2)]
    x = np.linspace(1.0, 9.2, 2000)
    # mean pressure: little drop in large arteries, the big drop across arterioles
    xs = [1.0, 3.0, 5.0, 6.2, 8.2, 9.2]
    ms = [93, 90, 35, 15, 6, 2]
    mean = np.interp(x, xs, ms)
    # smooth the corners a little
    k = np.exp(-np.linspace(-3, 3, 81) ** 2)
    k /= k.sum()
    mean = np.convolve(np.pad(mean, 40, mode="edge"), k, mode="valid")
    # pulse amplitude (systolic minus diastolic, halved): steady in large arteries, damped by the
    # arterioles. The waveform is a sharp systolic peak on a long diastolic decay, with zero mean,
    # so 120/80 sits around a mean of about 93.
    half = np.where(x < 3.0, 20.0, 20 * np.exp(-((x - 3.0) / 0.9) ** 2))
    ph = ((x - 1.0) / 0.55) % 1.0
    g = np.exp(1.5 * np.cos(2 * np.pi * (ph - 0.3)))
    gg = np.exp(1.5 * np.cos(2 * np.pi * (np.linspace(0, 1, 2000, endpoint=False) - 0.3)))
    wave = 2 * (g - gg.mean()) / (gg.max() - gg.min())
    fig, ax = plt.subplots(figsize=(9.6, 4.8))
    shades = [C["highlight"], "#fbf5ec", "#f8e4e0", C["shade"], C["cool"], "#e3edf2"]
    for (lab, a, b), col in zip(segs, shades):
        ax.axvspan(a, b, color=col, lw=0, zorder=0)
        ax.text((a + b) / 2, 141, lab, ha="center", va="bottom", fontsize=8.5, color=C["ink"])
    tv = np.linspace(0, 1.0, 400)
    lv = np.where(tv < 0.5, 4 + 116 * np.abs(np.sin(np.pi * tv / 0.5)) ** 1.5, 4)
    ax.plot(tv[:200] * 2 * 0.5, lv[:200], color=C["ventricular"], lw=1.6)
    ax.plot([0.5, 1.0], [4, 4], color=C["ventricular"], lw=1.6)
    ax.plot(x, mean + half * wave, color=ART, lw=1.3)
    ax.plot(x, mean, color=C["ink"], lw=2.2, ls=(0, (6, 3)), label="Mean pressure")
    ax.set_xlim(0, 9.2)
    ax.set_ylim(0, 140)
    ax.set_xticks([])
    ax.set_ylabel("Pressure (mm Hg)")
    ax.set_xlabel("Distance along the systemic circulation")
    ax.legend(loc="upper right", fontsize=9, bbox_to_anchor=(1.0, 0.96))
    ax.annotate("The largest pressure drop\nis across the arterioles", xy=(4.2, 60), xytext=(5.4, 85),
                fontsize=9, color=C["ink"], arrowprops=dict(arrowstyle="-", color=C["ink"], lw=0.7))
    ax.annotate("By the capillaries the\nbeat-to-beat swing is gone", xy=(5.6, 26), xytext=(6.4, 48),
                fontsize=9, color=C["ink"], arrowprops=dict(arrowstyle="-", color=C["ink"], lw=0.7))
    ax.text(1.15, 128, "120/80 in the aorta", fontsize=8.5, color=ART)
    fs.save(fig, PART, SLUG, "pressure-profile.svg")


# ------------------------------------------------------------------ 3. Operating point preview
def fig_operating_point():
    pms, pra0, co0 = 7.0, 2.0, 5.0
    rvr = (pms - pra0) / co0
    P = np.linspace(-4, 10, 300)
    vr = np.where(P < 0, pms / rvr, (pms - P) / rvr)
    vr = np.where(P > pms, np.nan, vr)
    s = 4.0 / np.log(9 / 4)
    co = 9 * (1 - np.exp(-(P + 2) / s))
    co = np.where(P < -2, np.nan, co)
    fig, ax = plt.subplots(figsize=(6.6, 4.6))
    ax.plot(P, co, color=C["ventricular"], lw=2.4)
    ax.plot(P, vr, color=VEN, lw=2.4)
    ax.plot(pra0, co0, "o", color=C["ink"], ms=8, zorder=5)
    ax.annotate("Operating point", xy=(pra0, co0), xytext=(3.6, 2.6), fontsize=9.5, color=C["ink"],
                arrowprops=dict(arrowstyle="-", color=C["ink"], lw=0.8))
    ax.text(5.2, 8.2, "Cardiac function curve\n(what the heart pumps)", fontsize=9, color=C["ventricular"])
    ax.text(-3.8, 7.5, "Vascular function curve\n(what the veins return)", fontsize=9, color=VEN)
    ax.plot(pms, 0, "o", color=VEN, ms=6, clip_on=False, zorder=5)
    ax.text(pms + 0.3, 0.3, "Pms", ha="left", fontsize=9, color=VEN)
    ax.axvline(0, color=C["axis"], lw=0.8)
    ax.set_xlim(-4, 10)
    ax.set_ylim(0, 10)
    ax.set_xlabel("Right atrial pressure, Pra (mm Hg)")
    ax.set_ylabel("Cardiac output or venous return (L/min)")
    ax.set_xticks(range(-4, 11, 2))
    ax.set_xticklabels([fs.fmt(v) for v in range(-4, 11, 2)])
    fs.grid(ax)
    fs.save(fig, PART, SLUG, "operating-point.svg")


if __name__ == "__main__":
    fig_circuit()
    fig_pressure_profile()
    fig_operating_point()
