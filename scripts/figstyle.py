"""Shared figure style for the TCOP web-book.

Every chapter's figure script imports this so all figures share one look, matching the
Respiratory Mechanics Lab and Circulation Lab simulators.

    import figstyle as fs
    fig, ax = fs.plt.subplots(figsize=(7.2, 5.0))
    ...
    fs.save(fig, "cardiovascular", "cardiac-pump", "wiggers.svg")

`save` writes the SVG to site/<part>/figures/<chapter>/ and, when the environment variable
PNG_PREVIEW names a folder, a PNG copy there so you can look at it. Run scripts with
MPLCONFIGDIR=$TMPDIR so matplotlib can write its cache.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

SITE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Palette (UChicago maroon family, as in the simulators).
C = dict(
    # pulmonary roles
    system="#800000",   # respiratory system
    lung="#a65e00",     # lung
    cw="#155f83",       # chest wall
    muscle="#d22f1e",   # respiratory muscles
    # cardiovascular roles (Circulation Lab: arterial / ventricular / venous)
    arterial="#800000",
    ventricular="#a65e00",
    venous="#155f83",
    atrial="#58593f",
    # extra series, in order of preference
    green="#275d38",
    gold="#c16622",
    purple="#59315f",
    gray="#767676",
    # ink and furniture
    ink="#193944", text="#4d4d4d", grid="#eaf0f2", axis="#aebdc4", shade="#f4f4f4",
    highlight="#f6ece0", cool="#eef2f4",
    # ECG paper
    ecg_minor="#f4c7c3", ecg_major="#e58a82", ecg_trace="#1a1a1a",
)
SERIES = [C["arterial"], C["venous"], C["ventricular"], C["green"], C["purple"], C["gold"], C["gray"]]
MINUS = "−"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 11, "axes.edgecolor": C["axis"], "axes.labelcolor": C["text"],
    "xtick.color": C["text"], "ytick.color": C["text"], "axes.spines.top": False,
    "axes.spines.right": False, "svg.fonttype": "none", "axes.titlesize": 12,
    "axes.titleweight": "bold", "axes.titlecolor": C["ink"], "axes.titlelocation": "left",
    "axes.unicode_minus": True, "legend.frameon": False,
})


def grid(ax):
    """Light grid behind the data, as in the simulators."""
    ax.grid(color=C["grid"], lw=0.8)
    ax.set_axisbelow(True)


def fmt(x):
    """Number with a true minus sign."""
    return f"{x:g}".replace("-", MINUS)


def save(fig, part, chapter, name):
    """Write site/<part>/figures/<chapter>/<name> (SVG) and an optional PNG preview."""
    out = os.path.join(SITE, part, "figures", chapter)
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, name)
    fig.savefig(path, format="svg", bbox_inches="tight", metadata={"Date": None})
    prev = os.environ.get("PNG_PREVIEW")
    if prev:
        os.makedirs(prev, exist_ok=True)
        fig.savefig(os.path.join(prev, f"{chapter}--{name.replace('.svg', '.png')}"), dpi=110, bbox_inches="tight")
    plt.close(fig)
    print("wrote", os.path.relpath(path, SITE))
    return path
