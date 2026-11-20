"""Figures for the ANS and Extrinsic Control chapter.

Run:  cd site/scripts && MPLCONFIGDIR=$TMPDIR PNG_PREVIEW=<folder> python3 figs_ans-extrinsic-control.py
Writes SVGs to ../cardiovascular/figures/ans-extrinsic-control/.

Most figures are block diagrams drawn for this book. The curve figure reuses the cardiac and vascular function
curves of the Control of CO chapter (Pms 7 mm Hg, Pra 2 mm Hg at CO 5 L/min).
"""
import numpy as np
from matplotlib.patches import FancyBboxPatch
import figstyle as fs
from figstyle import C, plt, MINUS

PART, SLUG = "cardiovascular", "ans-extrinsic-control"
SYMP = C["arterial"]
PARA = C["venous"]


def save(fig, name):
    fs.save(fig, PART, SLUG, name)


def box(ax, x, y, w, h, text, fc="white", ec=None, fs_=9.5, color=None, bold=False, lw=1.4, ha="center"):
    ec = ec or C["ink"]
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc=fc, ec=ec, lw=lw, zorder=3))
    tx = x if ha == "center" else x - w / 2 + 0.12
    ax.text(tx, y, text, ha=ha, va="center", fontsize=fs_, color=color or C["ink"], zorder=4,
            fontweight="bold" if bold else "normal")


def arrow(ax, p0, p1, color=None, lw=1.5, style="-|>", rad=0.0, ls="-", shrink=2, z=2):
    ax.annotate("", xy=p1, xytext=p0, zorder=z,
                arrowprops=dict(arrowstyle=style, color=color or C["ink"], lw=lw, linestyle=ls,
                                shrinkA=shrink, shrinkB=shrink, mutation_scale=12,
                                connectionstyle=f"arc3,rad={rad}"))


def blank(ax, xlim, ylim):
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")


# ---------------------------------------------------------------- 1. Control hierarchy
def fig_hierarchy():
    fig, ax = plt.subplots(figsize=(9.2, 6.6))
    blank(ax, (0, 13), (0, 9.4))
    box(ax, 3.0, 8.5, 4.6, 0.95, "Cortex and limbic system\n(amygdala, hippocampus, cingulate cortex)",
        fc=C["cool"], fs_=9)
    ax.text(5.5, 8.5, "context: fear, anticipation", fontsize=8.8, color=C["text"], va="center")
    box(ax, 3.0, 6.9, 4.6, 0.95, "Hypothalamus\ncoordinator: sets the overall pattern", fc=C["cool"], fs_=9.2)
    ax.text(5.5, 6.95, "also temperature and\nendocrine control", fontsize=8.8, color=C["text"], va="center")
    arrow(ax, (3.0, 8.0), (3.0, 7.4))
    # medulla
    ax.add_patch(FancyBboxPatch((0.3, 2.3), 8.6, 3.7, boxstyle="round,pad=0.02,rounding_size=0.2",
                                fc=C["highlight"], ec=C["gold"], lw=1.4, zorder=1))
    ax.text(0.5, 5.75, "Medullary cardiorespiratory center: the integrator", fontsize=9.8, color=C["ink"],
            fontweight="bold", va="center")
    arrow(ax, (3.0, 6.4), (3.0, 5.98))
    box(ax, 2.0, 4.55, 2.6, 0.9, "NTS\nreceives afferents", fs_=9)
    box(ax, 2.0, 3.0, 2.6, 0.9, "DMV and\nnucleus ambiguus", fs_=9, ec=PARA, color=PARA, bold=True)
    box(ax, 5.2, 3.0, 2.0, 0.9, "CVLM\n(inhibitory)", fs_=9)
    box(ax, 7.9, 3.0, 1.6, 0.9, "RVLM", fs_=9.5, ec=SYMP, color=SYMP, bold=True)
    arrow(ax, (3.3, 4.3), (4.4, 3.45), color=C["green"])
    ax.text(4.05, 4.0, "+", color=C["green"], fontsize=11, ha="center", fontweight="bold")
    arrow(ax, (6.2, 3.0), (7.05, 3.0), color=C["muscle"], style="-[,widthB=0.6,lengthB=0")
    ax.text(6.62, 3.2, MINUS, color=C["muscle"], fontsize=13, ha="center", fontweight="bold")
    arrow(ax, (2.0, 4.1), (2.0, 3.45), color=C["green"])
    ax.text(2.15, 3.72, "+", color=C["green"], fontsize=11, fontweight="bold")
    # outputs
    arrow(ax, (7.9, 2.55), (7.9, 1.55), color=SYMP, lw=2)
    box(ax, 7.9, 1.0, 3.0, 1.0, "Sympathetic outflow\n(spinal cord T1 to L2)", fc="white", ec=SYMP, color=SYMP,
        fs_=9)
    arrow(ax, (2.0, 2.55), (2.0, 1.55), color=PARA, lw=2)
    box(ax, 2.0, 1.0, 3.0, 1.0, "Vagal (parasympathetic)\noutflow to the heart", fc="white", ec=PARA, color=PARA,
        fs_=9)
    # afferents: one bus into the NTS
    box(ax, 11.4, 4.65, 2.8, 1.25, "Baroreceptors\ncarotid sinus (CN IX)\naortic arch (CN X)", fs_=8.8)
    box(ax, 11.4, 2.85, 2.8, 1.25, "Chemoreceptors\ncarotid bodies (CN IX)\naortic bodies (CN X)", fs_=8.8)
    bus_y, bus_x = 5.35, 9.6
    ax.plot([10.0, bus_x], [4.65, 4.65], color=C["ink"], lw=1.5)
    ax.plot([10.0, bus_x], [2.85, 2.85], color=C["ink"], lw=1.5)
    ax.plot([bus_x, bus_x], [2.85, bus_y], color=C["ink"], lw=1.5)
    ax.plot([bus_x, 2.0], [bus_y, bus_y], color=C["ink"], lw=1.5)
    arrow(ax, (2.0, bus_y), (2.0, 5.02), color=C["ink"], shrink=0)
    ax.text(6.6, bus_y - 0.12, "afferents in CN IX and CN X", fontsize=8.6, color=C["text"], ha="center",
            va="top")
    ax.text(5.6, 0.15, "NTS, nucleus tractus solitarius; CVLM and RVLM, caudal and rostral ventrolateral medulla; "
            "DMV, dorsal motor nucleus of the vagus", fontsize=8, color=C["text"], ha="center")
    save(fig, "control-hierarchy.svg")


# ---------------------------------------------------------------- 2. Efferent pathways
def fig_efferents():
    fig, ax = plt.subplots(figsize=(10.4, 5.8))
    blank(ax, (0, 15.4), (0, 8.6))
    xo, xt = 3.75, 13.7          # centers of origin and target boxes
    xs, xe = xo + 0.95, xt - 1.5  # where the neuron leaves the origin and reaches the target
    rows = [
        (7.4, "Parasympathetic", PARA, "brainstem (CN X)\nor sacral cord", 10.0, "ACh", "muscarinic",
         "heart (SA and AV nodes,\natria), a few vessels"),
        (5.4, "Sympathetic", SYMP, "lateral horn,\nT1 to L2", 6.9, "NE", "adrenergic\n(α$_1$, β$_1$, β$_2$)",
         "heart, arterioles,\nveins"),
        (3.4, "Sympathetic to\nsweat glands", SYMP, "lateral horn,\nT1 to L2", 6.9, "ACh", "muscarinic",
         "sweat glands"),
    ]
    for y, name, col, origin, xg, tx, rec, target in rows:
        ax.text(0.1, y, name, fontsize=9.8, color=col, fontweight="bold", va="center")
        box(ax, xo, y, 1.9, 0.9, origin, fs_=8.4, ec=col)
        ax.plot([xs, xg - 0.33], [y, y], color=col, lw=2.2, solid_capstyle="round")
        ax.add_patch(plt.Circle((xg, y), 0.33, fc=C["shade"], ec=col, lw=1.5, zorder=3))
        ax.text(xg, y + 0.5, "ganglion", fontsize=8, color=C["text"], ha="center")
        ax.text((xs + xg - 0.33) / 2, y - 0.3, "ACh, nicotinic", fontsize=8.3, color=C["text"], ha="center",
                va="top")
        ax.plot([xg + 0.33, xe], [y, y], color=col, lw=2.2, ls=(0, (4, 2)))
        ax.text((xg + 0.33 + xe) / 2, y + 0.18, tx, fontsize=9, color=col, ha="center", fontweight="bold")
        ax.text((xg + 0.33 + xe) / 2, y - 0.25, rec, fontsize=8.3, color=C["text"], ha="center", va="top")
        box(ax, xt, y, 3.0, 0.95, target, fs_=8.5, ec=col)
    y = 1.4
    ax.text(0.1, y, "Adrenal\nmedulla", fontsize=9.8, color=SYMP, fontweight="bold", va="center")
    box(ax, xo, y, 1.9, 0.9, "lateral horn,\nT1 to L2", fs_=8.4, ec=SYMP)
    ax.plot([xs, 8.9], [y, y], color=SYMP, lw=2.2)
    ax.text((xs + 8.9) / 2, y - 0.3, "ACh, nicotinic", fontsize=8.3, color=C["text"], ha="center", va="top")
    box(ax, 9.9, y, 2.0, 0.95, "chromaffin\ncells", fs_=8.5, ec=SYMP, fc=C["highlight"])
    arrow(ax, (10.9, y), (12.2, y), color=SYMP, ls=(0, (2, 2)))
    ax.text(11.55, y + 0.2, "blood", fontsize=8.3, color=C["text"], ha="center")
    box(ax, xt, y, 3.0, 0.95, "epinephrine (and some NE)\nto all tissues", fs_=8.3, ec=SYMP)
    ax.text(7.7, 8.35, "solid line: preganglionic neuron      dashed line: postganglionic neuron", fontsize=8.6,
            color=C["text"], ha="center")
    save(fig, "efferent-pathways.svg")


# ---------------------------------------------------------------- 4. Dual blockade
def fig_dual_blockade():
    fig, ax = plt.subplots(figsize=(6.8, 4.6))
    x = [0, 1, 2]
    a_first = [63, 117, 100]
    p_first = [61, 51, 100]
    ax.plot(x, a_first, "o-", color=PARA, lw=2.2, ms=7)
    ax.plot(x, p_first, "o-", color=SYMP, lw=2.2, ms=7)
    ax.text(1.08, 119, "atropine first:\nvagal block, rate rises", color=PARA, fontsize=9, va="bottom")
    ax.text(1.06, 47, "propranolol first:\nβ block, rate falls a little", color=SYMP, fontsize=9, va="center")
    ax.text(2.05, 100, "both blocked:\nintrinsic rate\nabout 100/min", color=C["ink"], fontsize=9, va="center")
    ax.set_xticks(x)
    ax.set_xticklabels(["Control", "After the\nfirst drug", "After both\ndrugs"])
    ax.set_xlim(-0.3, 2.75)
    ax.set_ylim(40, 135)
    ax.set_ylabel("Heart rate (beats/min)")
    fs.grid(ax)
    save(fig, "dual-blockade.svg")


# ---------------------------------------------------------------- 5. Receptor signaling
def fig_signaling():
    fig, axs = plt.subplots(1, 2, figsize=(10.6, 6.0))
    # A: cardiac myocyte / SA node
    ax = axs[0]
    blank(ax, (0, 8), (0, 9.2))
    ax.set_title("A  Heart: β$_1$ and M$_2$", loc="left")
    box(ax, 2.0, 8.3, 2.6, 0.8, "NE, epinephrine\nat β$_1$ receptors", fs_=8.8, ec=SYMP, color=SYMP)
    box(ax, 6.0, 8.3, 2.6, 0.8, "ACh\nat M$_2$ receptors", fs_=8.8, ec=PARA, color=PARA)
    box(ax, 2.0, 6.9, 1.6, 0.6, "G$_s$", fs_=9)
    box(ax, 6.0, 6.9, 1.6, 0.6, "G$_i$", fs_=9)
    box(ax, 2.0, 5.5, 2.6, 0.7, "adenylyl cyclase", fs_=8.8)
    box(ax, 2.0, 4.2, 2.4, 0.6, "cAMP, PKA", fs_=9)
    arrow(ax, (2.0, 7.9), (2.0, 7.2), color=SYMP)
    arrow(ax, (2.0, 6.6), (2.0, 5.85), color=SYMP)
    arrow(ax, (2.0, 5.15), (2.0, 4.5), color=SYMP)
    arrow(ax, (6.0, 7.9), (6.0, 7.2), color=PARA)
    arrow(ax, (5.2, 6.75), (3.35, 5.75), color=PARA, style="-[,widthB=0.6,lengthB=0")
    ax.text(4.45, 6.45, "inhibits", fontsize=8.3, color=PARA, ha="center", rotation=30)
    arrow(ax, (6.0, 6.6), (6.0, 5.75), color=PARA)
    box(ax, 6.0, 5.3, 3.2, 0.85, "opens K$^+$ channels (SA node,\natria): more negative", fs_=8.2, ec=PARA)
    box(ax, 3.55, 1.85, 7.0, 2.5,
        "In the SA node: more funny current (I$_f$) and Ca$^{2+}$ current,\n"
        "so phase 4 is steeper and the rate rises.\n"
        "In myocytes: L-type Ca$^{2+}$ channels let in more Ca$^{2+}$;\n"
        "phospholamban is phosphorylated, so SERCA refills\n"
        "the SR faster (more Ca$^{2+}$ to release, faster relaxation).\n"
        "Result: more force at the same preload (contractility up).",
        fs_=8.3, ha="left", fc=C["highlight"], ec=SYMP)
    arrow(ax, (2.0, 3.9), (2.0, 3.12), color=SYMP)
    # B: vascular smooth muscle
    ax = axs[1]
    blank(ax, (0, 8), (0, 9.2))
    ax.set_title("B  Vascular smooth muscle: α$_1$ and β$_2$", loc="left")
    box(ax, 2.0, 8.3, 2.6, 0.8, "NE, epinephrine\nat α$_1$ receptors", fs_=8.8, ec=SYMP, color=SYMP)
    box(ax, 6.0, 8.3, 2.6, 0.8, "epinephrine\nat β$_2$ receptors", fs_=8.8, ec=C["green"], color=C["green"])
    box(ax, 2.0, 6.9, 1.6, 0.6, "G$_q$", fs_=9)
    box(ax, 6.0, 6.9, 1.6, 0.6, "G$_s$", fs_=9)
    box(ax, 2.0, 5.5, 2.6, 0.7, "PLC, IP$_3$", fs_=9)
    box(ax, 2.0, 4.1, 2.8, 0.8, "Ca$^{2+}$ released\nfrom SR", fs_=8.8)
    box(ax, 2.0, 2.6, 2.8, 0.8, "Ca$^{2+}$-calmodulin\nactivates MLCK", fs_=8.8)
    box(ax, 6.0, 5.5, 2.4, 0.7, "cAMP", fs_=9)
    box(ax, 6.0, 4.1, 2.4, 0.8, "MLCK\ninhibited", fs_=8.8)
    for (a, b) in (((2.0, 7.9), (2.0, 7.2)), ((2.0, 6.6), (2.0, 5.85)), ((2.0, 5.15), (2.0, 4.5)),
                   ((2.0, 3.7), (2.0, 3.0))):
        arrow(ax, a, b, color=SYMP)
    for (a, b) in (((6.0, 7.9), (6.0, 7.2)), ((6.0, 6.6), (6.0, 5.85)), ((6.0, 5.15), (6.0, 4.5))):
        arrow(ax, a, b, color=C["green"])
    box(ax, 2.0, 1.0, 3.2, 0.95, "CONSTRICTION\nmost arterioles and veins", fs_=8.6, ec=SYMP, color=SYMP,
        fc=C["highlight"], bold=True)
    box(ax, 6.0, 2.6, 3.0, 0.95, "RELAXATION\nskeletal muscle arterioles", fs_=8.6, ec=C["green"],
        color=C["green"], fc="#e9f1ec", bold=True)
    arrow(ax, (2.0, 2.2), (2.0, 1.48), color=SYMP)
    arrow(ax, (6.0, 3.7), (6.0, 3.08), color=C["green"])
    fig.tight_layout()
    save(fig, "receptor-signaling.svg")


# ---------------------------------------------------------------- 6. Sympathetic effect on the curves
def softplus(x, w=0.45):
    return w * np.log1p(np.exp(x / w))


def vr_curve(pra, pms=7.0, rvr=1.0):
    return np.clip((pms - softplus(pra)) / rvr, 0, None)


def cardiac_curve(pra, cmax=12.0, p0=-2.0, k=7.42):
    return np.where(pra > p0, cmax * (1 - np.exp(-(pra - p0) / k)), 0.0)


def op(card, vasc):
    x = np.linspace(-3, 12, 20001)
    d = card(x) - vasc(x)
    i = np.where(np.diff(np.sign(d)) != 0)[0][0]
    return x[i], float(card(np.array([x[i]]))[0])


def fig_curves():
    pra = np.linspace(-3, 12, 600)
    fig, ax = plt.subplots(figsize=(7.2, 5.0))
    c0 = lambda x: cardiac_curve(x)
    v0 = lambda x: vr_curve(x)
    c1 = lambda x: cardiac_curve(x, cmax=16.0)
    v1 = lambda x: vr_curve(x, 9.0)
    m7, m9 = pra <= 7, pra <= 9
    ax.plot(pra, c0(pra), color=C["ventricular"], lw=2.2)
    ax.plot(pra[m7], v0(pra[m7]), color=C["venous"], lw=2.2)
    ax.plot(pra, c1(pra), color=C["ventricular"], lw=2.0, ls=(0, (5, 3)))
    ax.plot(pra[m9], v1(pra[m9]), color=C["venous"], lw=2.0, ls=(0, (5, 3)))
    x0, y0 = op(c0, v0)
    x1, y1 = op(c1, v1)
    ax.plot([x0], [y0], "o", mfc="white", mec=C["ink"], ms=8, zorder=6)
    ax.plot([x1], [y1], "o", color=C["arterial"], ms=8, zorder=6)
    arrow(ax, (x0, y0), (x1, y1), color=C["arterial"], shrink=5)
    ax.plot([7, 9], [0, 0], "o", color=C["venous"], ms=6, clip_on=False, zorder=6)
    ax.text(7.2, 0.35, "P$_{ms}$", color=C["venous"], fontsize=9, ha="left")
    ax.text(9.2, 0.35, "higher P$_{ms}$", color=C["venous"], fontsize=9, ha="left")
    ax.text(5.8, 14.1, "β$_1$: rate and contractility up", color=C["ventricular"], fontsize=9, ha="center")
    ax.text(10.4, 7.0, "normal\nheart", color=C["ventricular"], fontsize=9, ha="center")
    ax.text(-2.8, 9.4, "venoconstriction:\nstressed volume up", color=C["venous"], fontsize=9)
    ax.text(-2.8, 6.0, "normal veins", color=C["venous"], fontsize=9)
    ax.set_xlim(-3, 12)
    ax.set_ylim(0, 15)
    ticks = list(range(-2, 13, 2))
    ax.set_xticks(ticks)
    ax.set_xticklabels([fs.fmt(v) for v in ticks])
    ax.axvline(0, color=C["axis"], lw=0.8)
    ax.set_xlabel("Right atrial pressure, P$_{ra}$ (mm Hg)")
    ax.set_ylabel("Cardiac output or venous return (L/min)")
    fs.grid(ax)
    save(fig, "sympathetic-curves.svg")
    return (x0, y0), (x1, y1)


# ---------------------------------------------------------------- 7. Baroreceptor reflex
def fig_baroreflex():
    fig, ax = plt.subplots(figsize=(10.0, 6.2))
    blank(ax, (0, 15), (0, 9.6))
    box(ax, 1.6, 8.3, 2.7, 0.9, "MAP rises", fc=C["highlight"], ec=C["arterial"], color=C["arterial"], bold=True)
    box(ax, 1.6, 6.55, 2.7, 1.1, "carotid sinus and\naortic arch walls\nstretch", fs_=8.8)
    box(ax, 1.6, 4.8, 2.7, 1.1, "baroreceptor\nfiring rises\n(CN IX, CN X)", fs_=8.8)
    box(ax, 5.2, 4.8, 2.2, 1.0, "NTS\n(medulla)", fs_=9.2, bold=True)
    arrow(ax, (1.6, 7.85), (1.6, 7.1))
    arrow(ax, (1.6, 6.0), (1.6, 5.35))
    arrow(ax, (2.95, 4.8), (4.1, 4.8))
    # sympathetic branch: NTS excites CVLM, CVLM inhibits RVLM
    box(ax, 8.6, 5.6, 2.2, 0.85, "CVLM", fs_=9.2)
    box(ax, 8.6, 7.1, 2.2, 0.85, "RVLM", fs_=9.2, ec=SYMP, color=SYMP, bold=True)
    arrow(ax, (6.3, 5.0), (7.5, 5.45), color=C["green"])
    ax.text(6.85, 5.45, "+", color=C["green"], fontsize=12, fontweight="bold", ha="center")
    arrow(ax, (8.6, 6.02), (8.6, 6.68), color=C["muscle"], style="-[,widthB=0.6,lengthB=0")
    ax.text(8.85, 6.33, MINUS, color=C["muscle"], fontsize=13, fontweight="bold", va="center")
    box(ax, 12.4, 7.1, 3.4, 0.85, "sympathetic outflow falls", fs_=9, ec=SYMP, color=SYMP)
    arrow(ax, (9.7, 7.1), (10.7, 7.1), color=SYMP)
    # parasympathetic branch
    box(ax, 8.6, 3.0, 2.2, 1.0, "DMV and\nnucleus ambiguus", fs_=8.4, ec=PARA, color=PARA)
    arrow(ax, (6.3, 4.6), (7.5, 3.3), color=C["green"])
    ax.text(6.75, 3.75, "+", color=C["green"], fontsize=12, fontweight="bold", ha="center")
    box(ax, 12.4, 3.0, 3.4, 0.85, "vagal outflow rises", fs_=9, ec=PARA, color=PARA)
    arrow(ax, (9.7, 3.0), (10.7, 3.0), color=PARA)
    # effects
    box(ax, 12.4, 5.05, 3.4, 2.4,
        "heart rate down\ncontractility down\narterioles dilate (SVR down)\nveins dilate (P$_{ms}$ down)\n"
        "CO and SVR fall,\nso MAP comes down", fs_=8.5, fc=C["highlight"], ec=C["arterial"])
    arrow(ax, (12.4, 6.67), (12.4, 6.27), color=SYMP, shrink=0)
    arrow(ax, (12.4, 3.43), (12.4, 3.83), color=PARA, shrink=0)
    # negative feedback loop over the top
    gy, gx = 9.25, 14.6
    kw = dict(color=C["gray"], lw=1.2, ls=(0, (3, 3)))
    ax.plot([14.1, gx], [5.05, 5.05], **kw)
    ax.plot([gx, gx], [5.05, gy], **kw)
    ax.plot([gx, 1.6], [gy, gy], **kw)
    arrow(ax, (1.6, gy), (1.6, 8.77), color=C["gray"], lw=1.2, shrink=0)
    ax.text(8.0, gy + 0.1, "negative feedback", fontsize=8.6, color=C["gray"], ha="center", va="bottom")
    ax.text(0.2, 1.6, "A fall in MAP runs the same loop the other way:\nless firing, more sympathetic and less vagal\n"
            "outflow, and MAP comes back up.", fontsize=8.8, color=C["text"], va="center")
    save(fig, "baroreflex.svg")


# ---------------------------------------------------------------- 8. Chemoreceptor reflex
def fig_chemoreflex():
    fig, axs = plt.subplots(1, 2, figsize=(10.4, 5.6))
    # A: integrated response (taught first in the lecture)
    ax = axs[0]
    blank(ax, (0, 7.4), (0, 8.2))
    ax.set_title("A  Integrated response, breathing free", loc="left", fontsize=11)
    box(ax, 1.6, 7.2, 2.9, 0.8, "low P$_{O_2}$", fc=C["highlight"], fs_=9)
    box(ax, 5.6, 7.2, 3.0, 0.8, "high P$_{CO_2}$, low pH", fc=C["highlight"], fs_=9)
    box(ax, 1.6, 5.7, 2.9, 0.8, "peripheral\nchemoreceptors", fs_=8.8)
    box(ax, 5.6, 5.7, 3.0, 0.8, "central (and peripheral)\nchemoreceptors", fs_=8.6)
    arrow(ax, (1.6, 6.8), (1.6, 6.1))
    arrow(ax, (5.6, 6.8), (5.6, 6.1))
    arrow(ax, (4.2, 6.85), (2.9, 6.05), lw=1.1)
    box(ax, 3.7, 4.3, 3.0, 0.8, "ventilation up", fs_=9.2, bold=True)
    arrow(ax, (1.8, 5.3), (3.0, 4.7))
    arrow(ax, (5.4, 5.3), (4.4, 4.7))
    box(ax, 1.7, 2.8, 2.8, 0.85, "lungs stretch,\nP$_{CO_2}$ falls", fs_=8.8)
    arrow(ax, (3.2, 3.9), (2.2, 3.25))
    box(ax, 5.6, 2.8, 2.6, 0.85, "vagal center", fs_=8.8, ec=PARA, color=PARA)
    arrow(ax, (3.1, 2.8), (4.25, 2.8), color=C["muscle"], style="-[,widthB=0.6,lengthB=0")
    ax.text(3.68, 3.0, "inhibits", fontsize=8.2, color=C["muscle"], ha="center")
    box(ax, 5.6, 0.8, 2.6, 0.95, "less vagal outflow:\nTACHYCARDIA", fs_=8.8, ec=PARA, color=PARA, bold=True)
    arrow(ax, (5.6, 2.37), (5.6, 1.28), color=PARA)
    ax.text(0.2, 0.9, "This respiratory response\nnormally overrides the\nprimary vagal response.",
            fontsize=8.6, color=C["text"], va="center")
    # B: primary response with ventilation fixed
    ax = axs[1]
    blank(ax, (0, 7.4), (0, 8.2))
    ax.set_title("B  Primary response, ventilation held fixed", loc="left", fontsize=11)
    box(ax, 3.7, 7.2, 4.6, 0.8, "low P$_{O_2}$, high P$_{CO_2}$, low pH", fc=C["highlight"], fs_=9)
    box(ax, 3.7, 5.7, 4.0, 0.8, "peripheral chemoreceptors\n(carotid and aortic bodies)", fs_=8.8)
    box(ax, 3.7, 4.3, 3.0, 0.8, "medulla", fs_=9.2, bold=True)
    arrow(ax, (3.7, 6.8), (3.7, 6.1))
    arrow(ax, (3.7, 5.3), (3.7, 4.7))
    box(ax, 1.7, 2.6, 3.0, 1.0, "vagal outflow up\nto the heart", fs_=8.8, ec=PARA, color=PARA)
    box(ax, 5.7, 2.6, 3.0, 1.0, "sympathetic outflow\nup to vessels", fs_=8.8, ec=SYMP, color=SYMP)
    arrow(ax, (3.0, 3.9), (2.0, 3.1), color=PARA)
    arrow(ax, (4.4, 3.9), (5.4, 3.1), color=SYMP)
    box(ax, 1.7, 0.8, 3.0, 0.8, "BRADYCARDIA", fs_=9, ec=PARA, color=PARA, bold=True)
    box(ax, 5.7, 0.8, 3.0, 0.8, "VASOCONSTRICTION", fs_=9, ec=SYMP, color=SYMP, bold=True)
    arrow(ax, (1.7, 2.1), (1.7, 1.2), color=PARA)
    arrow(ax, (5.7, 2.1), (5.7, 1.2), color=SYMP)
    fig.tight_layout()
    save(fig, "chemoreflex.svg")


if __name__ == "__main__":
    fig_hierarchy()
    fig_efferents()
    fig_dual_blockade()
    fig_signaling()
    print("operating points", fig_curves())
    fig_baroreflex()
    fig_chemoreflex()
