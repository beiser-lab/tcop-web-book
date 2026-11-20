"""Figures for The Cardiac Pump chapter.

Run:  cd site/scripts && MPLCONFIGDIR=$TMPDIR PNG_PREVIEW=<folder> python3 figs_cardiac-pump.py
Writes SVGs to ../cardiovascular/figures/cardiac-pump/.

Every curve comes from one small model of the left heart, so the Wiggers diagram and the
pressure-volume loops are the same beat:

- Left ventricle: time-varying elastance. P = e(t) Ees (V - V0) + (1 - e(t)) Pd(V), where
  Pd(V) = A (exp(k (V - V0)) - 1) is the filling curve (EDPVR) and Ees (V - V0) is the
  end-systolic line (ESPVR). e(t) is a double-Hill activation that runs from 0 to 1.
- Left atrium: a compliant chamber with its own small activation (atrial systole), filled
  from the pulmonary veins at a fixed pressure. Descent of the base as the ventricle empties
  enlarges the atrium (x descent), and the closed mitral leaflets bulge back into it (c wave).
- Valves: ideal one-way valves. Aortic flow has a small resistance and inertance, so LV
  pressure stays just above aortic pressure until late ejection, ejection then continues
  briefly on momentum after aortic pressure exceeds ventricular pressure, and a small
  backflow closes the valve (dicrotic notch).
- Arteries: three-element Windkessel (characteristic impedance, compliance, resistance).
"""
import numpy as np
import figstyle as fs
from figstyle import C, plt, MINUS

PART, SLUG = "cardiovascular", "cardiac-pump"

BASE = dict(Ees=1.98, V0=10.0, A=0.46, k=0.025, Ppv=10.85, Rs=1.04, Ca=1.5, Zc=0.06, L=0.0002, Rav=0.004,
            Rmv=0.006, T=0.8, tv=0.16, ta=0.05, ta_dur=0.12, t1=0.2, t2=0.36, m1=1.32, m2=27.4,
            qback=80.0, Eap=0.3, Eaa=0.22, V0a=40.0, Rpv=0.03, beta=0.2, cb=0.06)


def act_atrium(u, dur):
    if 0 <= u < dur / 2:
        return 0.5 * (1 - np.cos(2 * np.pi * u / dur))
    if dur / 2 <= u < dur:
        return 0.5 * (1 + np.cos(2 * np.pi * (u - dur / 2) / dur))
    return 0.0


def make_ev(p):
    t1, t2, m1, m2, T = p["t1"], p["t2"], p["m1"], p["m2"], p["T"]
    uu = np.linspace(1e-6, T, 4001)
    raw = lambda u: ((u / t1) ** m1 / (1 + (u / t1) ** m1)) / (1 + (u / t2) ** m2)
    emax = raw(uu).max()
    return lambda u: raw(u) / emax if u > 0 else 0.0


def Pd(V, p=BASE):
    return p["A"] * (np.exp(p["k"] * (np.asarray(V) - p["V0"])) - 1)


def run(nbeats=8, dt=2e-5, **over):
    """Simulate to steady state and return the last beat as a dict of arrays."""
    p = dict(BASE, **over)
    ev_of = make_ev(p)
    T = p["T"]
    Vlv, Vla, Pc, Q = 120.0, 70.0, 80.0, 0.0
    av_open = ejected = False
    bulge = 0.0
    rows = []
    for i in range(int(nbeats * T / dt)):
        t = i * dt
        tc = t % T
        u = tc - p["tv"]
        if u < 0:
            u += T
        ev = ev_of(u)
        ea = act_atrium(tc - p["ta"], p["ta_dur"])
        Plv = ev * p["Ees"] * (Vlv - p["V0"]) + (1 - ev) * Pd(Vlv, p)
        Ela = p["Eap"] + ea * p["Eaa"]
        Pla = Ela * (Vla - p["V0a"] + p["beta"] * (Vlv - 130.0))
        # closed mitral leaflets bulge into the atrium (c wave). The bulge holds through
        # isovolumic relaxation and relaxes over about 15 ms once the valve opens, so the
        # v wave peaks at mitral opening.
        if Plv > Pla:
            target = bulge if (ejected and not av_open) else min(Plv - Pla, 60.0)
        else:
            target = 0.0
        bulge += (target - bulge) * dt / 0.015
        Pla += Ela * p["cb"] * bulge
        Qm = max(0.0, (Pla - Plv) / p["Rmv"])
        if Qm > 0:
            ejected = False
        Pao = Pc + p["Zc"] * Q
        if not av_open and not ejected and Plv > Pao:
            av_open = ejected = True
        if av_open:
            Q += (Plv - Pao - p["Rav"] * Q) / p["L"] * dt
            if Q < -p["qback"]:
                av_open, Q = False, 0.0
        else:
            Q = 0.0
        Pao = Pc + p["Zc"] * Q
        Qpv = (p["Ppv"] - Pla) / p["Rpv"]
        Vlv += (Qm - Q) * dt
        Vla += (Qpv - Qm) * dt
        Pc += (Q - Pc / p["Rs"]) / p["Ca"] * dt
        if i % 10 == 0:
            rows.append((t, Plv, Pao, Pla, Vlv, Q, Qm, int(av_open)))
    a = np.array(rows)
    a = a[a[:, 0] >= (nbeats - 1) * T]
    a[:, 0] -= (nbeats - 1) * T
    b = dict(zip(["t", "Plv", "Pao", "Pla", "V", "Q", "Qm", "ao"], a.T))
    b["p"] = p
    t, Plv, Pla = b["t"], b["Plv"], b["Pla"]
    ch = np.where(np.diff(b["ao"]) != 0)[0]
    b["i_ao"], b["i_ac"] = ch[0] + 1, ch[1] + 1
    b["i_mc"] = np.where((t >= p["tv"]) & (Plv > Pla))[0][0]
    b["i_mo"] = np.where((t > t[b["i_ac"]]) & (Plv < Pla))[0][0]
    b["EDV"], b["ESV"] = b["V"][b["i_mc"]], b["V"][b["i_ac"]]
    b["SV"] = b["EDV"] - b["ESV"]
    return b


def loop_xy(b):
    """P-V loop starting at mitral closure, closed."""
    i0 = b["i_mc"]
    V = np.r_[b["V"][i0:], b["V"][:i0 + 1]]
    P = np.r_[b["Plv"][i0:], b["Plv"][:i0 + 1]]
    return V, P


def pv_axes(ax, vmax=180, pmax=160):
    ax.set_xlim(0, vmax)
    ax.set_ylim(0, pmax)
    ax.set_xlabel("Left ventricular volume (mL)")
    ax.set_ylabel("Left ventricular pressure (mm Hg)")
    fs.grid(ax)


def espvr(ax, p, vmax=95, **kw):
    V = np.linspace(p["V0"], vmax, 50)
    ax.plot(V, p["Ees"] * (V - p["V0"]), **kw)


def edpvr(ax, p, vmax=175, **kw):
    V = np.linspace(p["V0"], vmax, 200)
    ax.plot(V, Pd(V, p), **kw)


# ------------------------------------------------------------------ baseline beat
B = run()
print("baseline EDV %.0f ESV %.0f SV %.0f, LV max %.0f, Ao %.0f/%.0f, EDP %.1f" % (
    B["EDV"], B["ESV"], B["SV"], B["Plv"].max(), B["Pao"].max(), B["Pao"].min(), B["Plv"][B["i_mc"]]))
tA = B["t"]
i_pre = np.where(tA >= BASE["ta"])[0][0]
print("atrial kick: %.0f mL of EDV (%.0f%%)" % (B["EDV"] - B["V"][i_pre], 100 * (B["EDV"] - B["V"][i_pre]) / B["EDV"]))


# ------------------------------------------------------------------ 1. Wiggers diagram
def ecg(t):
    g = lambda c, w, a: a * np.exp(-((t - c) / w) ** 2)
    return (g(0.03, 0.022, 0.15) + g(0.135, 0.006, -0.10) + g(0.150, 0.008, 1.10)
            + g(0.166, 0.007, -0.25) + g(0.42, 0.035, 0.30))


def sound(t, t0, dur, amp, f=55.0):
    env = np.where((t > t0) & (t < t0 + dur), np.sin(np.pi * (t - t0) / dur) ** 2, 0)
    return amp * env * np.sin(2 * np.pi * f * (t - t0))


def phases(b):
    t, p = b["t"], b["p"]
    t_mc, t_ao, t_ac, t_mo = (t[b[k]] for k in ("i_mc", "i_ao", "i_ac", "i_mo"))
    sys = (t >= t_ao) & (t <= t_ac)
    t_pk = t[np.where(sys)[0][np.argmax(b["Plv"][sys])]]
    dV = np.gradient(b["V"], t)
    after = np.where(t > t_mo)[0]
    peak = after[np.argmax(dV[after])]
    t_rf = t[peak + np.where(dV[peak:] < 0.30 * dV[peak])[0][0]]
    return [("Diastasis", 0.0, p["ta"]),
            ("Atrial systole", p["ta"], t_mc),
            ("Isovolumic contraction", t_mc, t_ao),
            ("Rapid ejection", t_ao, t_pk),
            ("Reduced ejection", t_pk, t_ac),
            ("Isovolumic relaxation", t_ac, t_mo),
            ("Rapid ventricular filling", t_mo, t_rf),
            ("Diastasis", t_rf, p["T"])]


PHASE_COL = ["#ffffff", "#eef0e6", "#f8e4e0", "#f6ece0", "#fbf5ec", "#e3edf2", "#eef3f6", "#ffffff"]


def fig_wiggers():
    b = B
    t = b["t"]
    ph = phases(b)
    for name, a, z in ph:
        print("  %-26s %.3f to %.3f s" % (name, a, z))
    fig = plt.figure(figsize=(8.6, 11.4))
    gs = fig.add_gridspec(6, 1, height_ratios=[1.75, 3.2, 1.25, 1.7, 1.0, 0.8], hspace=0.12)
    axs = [fig.add_subplot(gs[i]) for i in range(6)]
    top, axP, axA, axV, axE, axS = axs
    for ax in axs[1:]:
        ax.set_xlim(0, 0.8)
        for (name, a, z), col in zip(ph, PHASE_COL):
            ax.axvspan(a, z, color=col, zorder=0, lw=0)
        for x in (t[b["i_mc"]], t[b["i_ao"]], t[b["i_ac"]], t[b["i_mo"]]):
            ax.axvline(x, color=C["axis"], lw=0.8, ls=(0, (3, 3)), zorder=1)
        ax.tick_params(labelbottom=False)
    # phase names strip
    top.set_xlim(0, 0.8)
    top.set_ylim(0, 1)
    top.axis("off")
    for (name, a, z), col in zip(ph, PHASE_COL):
        top.axvspan(a, z, ymin=0, ymax=0.74, color=col, lw=0)
        lab = name.replace("Isovolumic ", "Isovolumic\n").replace("Rapid ventricular ", "Rapid ventricular\n")
        top.text((a + z) / 2, 0.03, lab, rotation=90, ha="center", va="bottom", fontsize=8.5,
                 color=C["ink"], linespacing=1.0)
    t_mc, t_ac = t[b["i_mc"]], t[b["i_ac"]]
    for a, z, lab in ((t_mc, t_ac, "Ventricular systole"), (0.0, t_mc, "Ventricular diastole"),
                      (t_ac, 0.8, "Ventricular diastole")):
        top.annotate("", xy=(a, 0.82), xytext=(z, 0.82),
                     arrowprops=dict(arrowstyle="<->", color=C["ink"], lw=1.0, shrinkA=0, shrinkB=0))
        top.text((a + z) / 2, 0.87, lab, ha="center", va="bottom", fontsize=9.5, color=C["ink"],
                 fontweight="bold")
    # pressures
    axP.plot(t, b["Pao"], color=C["arterial"], lw=2, label="Aortic pressure")
    axP.plot(t, b["Plv"], color=C["ventricular"], lw=2, label="Left ventricular pressure")
    axP.plot(t, b["Pla"], color=C["atrial"], lw=1.6, label="Left atrial pressure")
    axP.set_ylim(0, 140)
    axP.set_yticks(range(0, 141, 20))
    axP.set_ylabel("Pressure (mm Hg)")
    axP.legend(loc="upper right", fontsize=8.5, bbox_to_anchor=(1.0, 0.64))
    ev = [("Mitral valve\ncloses", b["i_mc"], b["Plv"], (0.02, 30), "left"),
          ("Aortic valve\nopens", b["i_ao"], b["Plv"], (0.06, 52), "left"),
          ("Aortic valve\ncloses", b["i_ac"], b["Pao"], (0.40, 128), "left"),
          ("Mitral valve\nopens", b["i_mo"], b["Plv"], (0.60, 34), "left")]
    for lab, i, y, (xt, yt), ha in ev:
        axP.plot(t[i], y[i], "o", ms=5, color=C["ink"], zorder=5)
        axP.annotate(lab, xy=(t[i], y[i]), xytext=(xt, yt), fontsize=8.5, color=C["ink"], ha=ha,
                     arrowprops=dict(arrowstyle="-", color=C["ink"], lw=0.7))
    i_n = b["i_ac"] + np.argmin(b["Pao"][b["i_ac"] - 20:b["i_ac"] + 40]) - 20
    axP.annotate("Dicrotic notch", xy=(t[i_n], b["Pao"][i_n]), xytext=(0.60, 116), fontsize=8.5,
                 color=C["arterial"], arrowprops=dict(arrowstyle="-", color=C["arterial"], lw=0.7))
    # left atrial pressure, expanded
    axA.plot(t, b["Pla"], color=C["atrial"], lw=1.8)
    axA.set_ylim(4, 13)
    axA.set_ylabel("LA pressure\n(mm Hg)")
    for lab, tt in (("a", 0.105), ("c", 0.235), ("v", 0.552)):
        j = np.argmin(abs(t - tt))
        j = j - 30 + np.argmax(b["Pla"][j - 30:j + 30])
        axA.text(t[j], b["Pla"][j] + 0.5, lab, ha="center", fontsize=10, color=C["atrial"],
                 fontstyle="italic", fontweight="bold")
    axA.text(0.79, 12.0, "expanded scale", ha="right", fontsize=8, color=C["text"])
    # volume
    axV.plot(t, b["V"], color=C["ventricular"], lw=2)
    axV.set_ylim(50, 150)
    axV.set_ylabel("LV volume\n(mL)")
    axV.axhline(b["EDV"], color=C["gray"], lw=0.8, ls=":")
    axV.axhline(b["ESV"], color=C["gray"], lw=0.8, ls=":")
    axV.text(0.30, b["EDV"] + 3, "EDV %d mL" % round(b["EDV"]), fontsize=8.5, color=C["text"])
    axV.text(0.565, b["ESV"] - 9, "ESV %d mL" % round(b["ESV"]), fontsize=8.5, color=C["text"])
    xs = 0.775
    axV.annotate("", xy=(xs, b["ESV"]), xytext=(xs, b["EDV"]),
                 arrowprops=dict(arrowstyle="<->", color=C["green"], lw=1.4, shrinkA=0, shrinkB=0))
    axV.text(xs - 0.008, b["ESV"] + 12, "Stroke\nvolume", ha="right", va="center",
             fontsize=8.5, color=C["green"])
    axV.annotate("Atrial kick", xy=(0.12, 131), xytext=(0.02, 140), fontsize=8.5, color=C["text"],
                 arrowprops=dict(arrowstyle="-", color=C["text"], lw=0.7))
    # ECG
    axE.plot(t, ecg(t), color=C["ecg_trace"], lw=1.3)
    axE.set_ylim(-0.4, 1.3)
    axE.set_yticks([])
    axE.set_ylabel("ECG")
    for lab, x, y in (("P", 0.03, 0.24), ("Q", 0.128, -0.33), ("R", 0.162, 1.08), ("S", 0.174, -0.36),
                      ("T", 0.42, 0.40)):
        axE.text(x, y, lab, fontsize=9, ha="center", color=C["ink"])
    # heart sounds
    s = sound(t, t[b["i_mc"]], 0.045, 1.0, 50) + sound(t, t[b["i_ac"]], 0.030, 0.8, 70)
    axS.plot(t, s, color=C["ink"], lw=1.0)
    axS.set_ylim(-1.3, 1.6)
    axS.set_yticks([])
    axS.set_ylabel("Heart\nsounds")
    axS.text(t[b["i_mc"]] + 0.05, 0.6, "S$_1$", fontsize=10, color=C["ink"])
    axS.text(t[b["i_ac"]] + 0.035, 0.6, "S$_2$", fontsize=10, color=C["ink"])
    axS.tick_params(labelbottom=True)
    axS.set_xlabel("Time (s)")
    for ax in (axE, axS):
        ax.spines["left"].set_visible(False)
    fs.save(fig, PART, SLUG, "wiggers.svg")


# ------------------------------------------------------------------ 2. Right side and S2 split
def fig_right_left():
    R = run(Ees=0.6, A=0.42, k=0.025, Ppv=7.6, Rs=0.16, Ca=3.5, Zc=0.02, Eap=0.25,
            beta=0.15, cb=0.04, qback=40.0)
    print("RV: EDV %.0f ESV %.0f SV %.0f, RV max %.0f, PA %.0f/%.0f, EDP %.1f" % (
        R["EDV"], R["ESV"], R["SV"], R["Plv"].max(), R["Pao"].max(), R["Pao"].min(), R["Plv"][R["i_mc"]]))
    fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(12.6, 4.4), gridspec_kw=dict(width_ratios=[1, 1, 1.05]))
    for ax, b, names, title in ((a1, B, ("Aorta", "Left ventricle", "Left atrium"), "A  Left heart"),
                                (a2, R, ("Pulmonary artery", "Right ventricle", "Right atrium"), "B  Right heart")):
        t = b["t"]
        ax.plot(t, b["Pao"], color=C["arterial"], lw=1.8, label=names[0])
        ax.plot(t, b["Plv"], color=C["ventricular"], lw=1.8, label=names[1])
        ax.plot(t, b["Pla"], color=C["atrial"], lw=1.4, label=names[2])
        ax.set_xlim(0, 0.8)
        ax.set_ylim(0, 140)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Pressure (mm Hg)")
        ax.set_title(title)
        ax.legend(loc="upper right", fontsize=8.5)
        fs.grid(ax)
        sysP, edP = b["Plv"].max(), b["Plv"][b["i_mc"]]
        ax.text(0.03, 0.72 * 140, "Ventricle\n%d/%d mm Hg" % (round(sysP / 5) * 5, round(edP)),
                fontsize=9, color=C["ventricular"])
    a2.text(0.03, 0.55 * 140, "Same time scale and\npressure scale as A", fontsize=8.5, color=C["text"])
    # S2 split schematic
    ax = a3
    ax.set_title("C  Splitting of S$_2$ (schematic)")
    tt = np.linspace(0, 0.16, 3000)
    rows = [("Expiration", 1.6, 0.050, 0.072), ("Inspiration", 0.4, 0.044, 0.096)]
    for lab, y0, ta2, tp2 in rows:
        s = sound(tt, ta2, 0.018, 0.42, 160) + sound(tt, tp2, 0.016, 0.30, 180)
        ax.plot(tt, y0 + s, color=C["ink"], lw=1.0)
        ax.text(-0.004, y0, lab, ha="right", va="center", fontsize=9.5, color=C["ink"])
        ax.text(ta2 + 0.004, y0 + 0.52, "A$_2$", ha="right", fontsize=9.5, color=C["arterial"])
        ax.text(tp2 + 0.006, y0 + 0.52, "P$_2$", ha="left", fontsize=9.5, color=C["venous"])
    ax.annotate("", xy=(0.048, -0.15), xytext=(0.102, -0.15),
                arrowprops=dict(arrowstyle="<->", color=C["venous"], lw=1.1, shrinkA=0, shrinkB=0))
    ax.text(0.075, -0.42, "wider split", ha="center", fontsize=8.5, color=C["venous"])
    ax.set_xlim(-0.06, 0.16)
    ax.set_ylim(-0.7, 2.4)
    ax.axis("off")
    fig.tight_layout(w_pad=2.5)
    fs.save(fig, PART, SLUG, "left-right-s2.svg")


# ------------------------------------------------------------------ 3. Filling curve (EDPVR)
def fig_edpvr():
    p = BASE
    stiff = dict(p, k=0.035)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.4, 4.6))
    for ax in (a1, a2):
        ax.set_xlim(0, 180)
        ax.set_ylim(0, 40)
        ax.set_xlabel("Left ventricular volume (mL)")
        ax.set_ylabel("Left ventricular pressure (mm Hg)")
        fs.grid(ax)
    V = np.linspace(p["V0"], 178, 300)
    a1.plot(V, Pd(V, p), color=C["venous"], lw=2.2)
    a1.set_title("A  The filling curve (EDPVR)")
    for v1, v2 in ((60, 80), (140, 160)):
        p1, p2 = Pd(v1), Pd(v2)
        a1.plot([v1, v2, v2], [p1, p1, p2], color=C["ink"], lw=1)
        if v1 < 100:
            a1.text(v1 - 2, p1 + 1.6, "ΔV 20 mL, ΔP %.1f mm Hg" % (p2 - p1), ha="right", fontsize=8.5,
                    color=C["ink"])
        else:
            a1.text((v1 + v2) / 2, p1 - 1.6, "ΔV 20 mL", ha="center", fontsize=8.5, color=C["ink"])
            a1.text(v2 + 2, (p1 + p2) / 2, "ΔP %.0f mm Hg" % (p2 - p1), va="center", fontsize=8.5,
                    color=C["ink"])
    a1.text(40, 12, "Low volume: a large ΔV\nfor a small ΔP\n(high compliance)", fontsize=9, color=C["text"])
    a1.text(98, 25, "High volume: the same ΔV\ntakes more pressure\n(lower compliance)", fontsize=9,
            color=C["text"])
    edv, edp = B["EDV"], Pd(B["EDV"])
    a1.plot(edv, edp, "o", color=C["ventricular"], ms=7, zorder=5)
    a1.annotate("End of diastole:\nLVEDV = preload\n(LVEDP %.0f mm Hg)" % edp, xy=(edv, edp), xytext=(146, 1.2),
                fontsize=8.5, color=C["ventricular"], arrowprops=dict(arrowstyle="-", color=C["ventricular"], lw=0.7))
    # B: stiffer ventricle
    a2.set_title("B  A stiffer ventricle (less compliant)")
    a2.plot(V, Pd(V, p), color=C["venous"], lw=2.2, label="Normal")
    Vs = np.linspace(p["V0"], 150, 300)
    a2.plot(Vs, Pd(Vs, stiff), color=C["venous"], lw=2.2, ls="--", label="Stiffer")
    v_same_p = p["V0"] + np.log(edp / stiff["A"] + 1) / stiff["k"]
    p_same_v = float(Pd(edv, stiff))
    a2.axhline(edp, color=C["gray"], lw=0.9, ls=":")
    a2.plot([edv, v_same_p], [edp, edp], "o", color=C["ventricular"], ms=6, zorder=5)
    a2.annotate("", xy=(v_same_p + 2, edp - 0.8), xytext=(edv - 2, edp - 0.8),
                arrowprops=dict(arrowstyle="->", color=C["ink"], lw=1))
    a2.text(142, 2.0, "same LVEDP,\n%d mL less volume" % round(edv - v_same_p),
            ha="left", fontsize=8.5, color=C["ink"])
    a2.plot([edv], [p_same_v], "o", color=C["ventricular"], ms=6, mfc="white", zorder=5)
    a2.annotate("same LVEDV,\nLVEDP %d mm Hg" % round(p_same_v), xy=(edv, p_same_v), xytext=(143, 35),
                fontsize=8.5, color=C["ink"], arrowprops=dict(arrowstyle="-", color=C["ink"], lw=0.7))
    a2.legend(loc="upper left", fontsize=9)
    fig.tight_layout(w_pad=3)
    fs.save(fig, PART, SLUG, "edpvr.svg")


# ------------------------------------------------------------------ 4. Building the ESPVR
def fig_espvr():
    p = BASE
    ev_of = make_ev(p)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.4, 4.8))
    for ax in (a1, a2):
        pv_axes(ax, vmax=180, pmax=330)
    a1.set_title("A  Contracting against a closed aortic valve")
    edpvr(a1, p, color=C["venous"], lw=2)
    espvr(a1, p, vmax=168, color=C["arterial"], lw=2)
    uu = np.linspace(0, 0.45, 400)
    e = np.array([ev_of(x) for x in uu])
    for lab_d, lab_s, v in (("1", "A", 80), ("2", "B", 115), ("3", "C", 150)):
        P = e * p["Ees"] * (v - p["V0"]) + (1 - e) * Pd(v)
        a1.plot([v, v], [Pd(v), P.max()], color=C["ventricular"], lw=1.6)
        a1.annotate("", xy=(v, P.max() * 0.62), xytext=(v, P.max() * 0.45),
                    arrowprops=dict(arrowstyle="->", color=C["ventricular"], lw=1.4))
        a1.plot(v, Pd(v), "o", color=C["venous"], ms=6, zorder=5)
        a1.plot(v, P.max(), "o", color=C["arterial"], ms=6, zorder=5)
        a1.text(v + 3, Pd(v) + 8, lab_d, fontsize=10, color=C["venous"], fontweight="bold")
        a1.text(v - 10, P.max() + 6, lab_s, fontsize=10, color=C["arterial"], fontweight="bold")
    a1.text(30, 285, "Systolic P-V curve (ESPVR)", fontsize=9, color=C["arterial"])
    a1.text(154, 34, "Diastolic\nP-V curve\n(EDPVR)", fontsize=9, color=C["venous"])
    # B
    a2.set_title("B  Slope = contractility")
    for ees, ls, lab, xy in ((3.2, ":", "Higher contractility", (22, 312)), (p["Ees"], "-", "", None),
                             (1.3, "--", "Lower contractility", (128, 140))):
        V = np.linspace(p["V0"], min(168, p["V0"] + 320 / ees), 50)
        a2.plot(V, ees * (V - p["V0"]), color=C["arterial"], lw=2, ls=ls)
        if lab:
            a2.text(*xy, lab, fontsize=9.5, color=C["arterial"])
    edpvr(a2, p, color=C["venous"], lw=1.4, alpha=0.6)
    for v in (80, 115, 150):
        a2.plot(v, p["Ees"] * (v - p["V0"]), "o", color=C["ink"], ms=6, zorder=5)
    a2.annotate("", xy=(144, 306), xytext=(88, 190), arrowprops=dict(arrowstyle="->", color=C["ink"], lw=1.3))
    a2.text(104, 50, "More filling moves the beat\nup the same line: more force,\nsame contractility",
            fontsize=8.5, color=C["ink"])
    fig.tight_layout(w_pad=3)
    fs.save(fig, PART, SLUG, "espvr.svg")


# ------------------------------------------------------------------ 5. The P-V loop
def arrow_on(ax, V, P, i, color):
    ax.annotate("", xy=(V[i + 6], P[i + 6]), xytext=(V[i], P[i]),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.5, mutation_scale=14))


def fig_pv_loop():
    b, p = B, BASE
    V, P = loop_xy(b)
    fig, ax = plt.subplots(figsize=(8.4, 6.0))
    pv_axes(ax, vmax=175, pmax=150)
    edpvr(ax, p, vmax=165, color=C["venous"], lw=1.6)
    espvr(ax, p, vmax=82, color=C["arterial"], lw=1.6)
    ax.fill(V, P, color=C["highlight"], zorder=1)
    ax.plot(V, P, color=C["ventricular"], lw=2.4, zorder=3)
    n = len(V)
    for frac in (0.08, 0.28, 0.62, 0.85):
        arrow_on(ax, V, P, int(frac * n), C["ventricular"])
    k_ao = b["i_ao"] - b["i_mc"]
    k_ac = b["i_ac"] - b["i_mc"]
    k_mo = b["i_mo"] - b["i_mc"]
    # the end-systolic point: where the loop touches the ESPVR (top left corner)
    k_es = int(np.argmax(P[:k_mo] / (V[:k_mo] - p["V0"])))
    pts = [(0, "Mitral valve closes", (148, 30)), (k_ao, "Aortic valve opens", (148, 80)),
           (k_es, "Aortic valve closes", (84, 106)), (k_mo, "Mitral valve opens", (6, 32))]
    for k, lab, xy in pts:
        ax.plot(V[k], P[k], "o", color=C["ink"], ms=6, zorder=5)
        ax.annotate(lab, xy=(V[k], P[k]), xytext=xy, fontsize=9, color=C["ink"],
                    arrowprops=dict(arrowstyle="-", color=C["ink"], lw=0.7))
    edv, esv = b["EDV"], b["ESV"]
    ax.text(edv + 3, 50, "Isovolumic\ncontraction", fontsize=8.5, color=C["ventricular"])
    ax.text(esv - 3, 58, "Isovolumic\nrelaxation", fontsize=8.5, color=C["ventricular"], ha="right")
    k_pk = int(np.argmax(P))
    ax.plot([V[k_pk]] * 2, [P[k_pk] - 3, P[k_pk] + 3], color=C["ventricular"], lw=1.4)
    ax.text((V[k_pk] + edv) / 2 + 4, P[k_pk] + 6, "Rapid ejection", fontsize=8.5, color=C["ventricular"],
            ha="center")
    ax.text((V[k_pk] + esv) / 2 + 2, P[k_pk] + 6, "Reduced ejection", fontsize=8.5, color=C["ventricular"],
            ha="center")
    ax.text(100, 11, "Filling", fontsize=8.5, color=C["ventricular"], ha="center")
    ax.text(100, 60, "Area inside the loop =\nstroke work", fontsize=9, color=C["text"], ha="center")
    sbp, dbp = P.max(), P[k_ao]
    ax.axhline(sbp, xmax=V[np.argmax(P)] / 175, color=C["gray"], lw=0.8, ls=":")
    ax.text(2, sbp + 2, "Peak LV pressure ≈ SBP (%d)" % round(sbp), fontsize=8.5, color=C["text"])
    ax.axhline(dbp, xmax=edv / 175, color=C["gray"], lw=0.8, ls=":")
    ax.text(2, dbp + 2, "Aortic valve opens at DBP (%d)" % round(dbp), fontsize=8.5, color=C["text"])
    ax.annotate("", xy=(esv, 20), xytext=(edv, 20),
                arrowprops=dict(arrowstyle="<->", color=C["green"], lw=1.6, shrinkA=0, shrinkB=0))
    ax.text((edv + esv) / 2, 22, "Stroke volume = EDV %s ESV" % MINUS, ha="center", fontsize=9,
            color=C["green"])
    ax.text(edv, -11, "EDV", ha="center", fontsize=9, color=C["ink"], clip_on=False)
    ax.text(esv, -11, "ESV", ha="center", fontsize=9, color=C["ink"], clip_on=False)
    ax.set_xlabel("Left ventricular volume (mL)", labelpad=16)
    ax.text(84, 131, "ESPVR", fontsize=9, color=C["arterial"])
    ax.text(160, 20, "EDPVR", fontsize=9, color=C["venous"])
    fs.save(fig, PART, SLUG, "pv-loop.svg")


# ------------------------------------------------------------------ 6. Preload, afterload, contractility
def sv_bars(ax, b0, b1, y0, y1, base_left=False):
    ax.plot([b0["ESV"], b0["EDV"]], [y0, y0], color=C["gray"], lw=3, solid_capstyle="butt")
    ax.plot([b1["ESV"], b1["EDV"]], [y1, y1], color=C["green"], lw=3, solid_capstyle="butt")
    if base_left:
        ax.text(b0["ESV"] - 3, y0, "%d mL" % round(b0["SV"]), va="center", ha="right", fontsize=8.5,
                color=C["gray"])
    else:
        ax.text(b0["EDV"] + 3, y0, "%d mL" % round(b0["SV"]), va="center", fontsize=8.5, color=C["gray"])
    ax.text(b1["EDV"] + 3, y1, "%d mL" % round(b1["SV"]), va="center", fontsize=8.5, color=C["green"])


def fig_determinants():
    cases = [("A  More preload: SV rises", dict(Ppv=14.0, Rs=0.84, Ca=2.05, Zc=0.05)),
             ("B  More afterload: SV falls", dict(Rs=1.6, Ppv=10.4)),
             ("C  More contractility: SV rises", dict(Ees=3.2, Ppv=11.7, Rs=0.79, Ca=2.3, Zc=0.045))]
    fig, axs = plt.subplots(1, 3, figsize=(13.2, 4.7), sharey=True)
    for ax, (title, over) in zip(axs, cases):
        b1 = run(**over)
        p1 = b1["p"]
        print("  %s: EDV %.0f ESV %.0f SV %.0f SBP %.0f DBP %.0f" % (
            title, b1["EDV"], b1["ESV"], b1["SV"], b1["Pao"].max(), b1["Pao"].min()))
        pv_axes(ax, vmax=180, pmax=200)
        if ax is not axs[0]:
            ax.set_ylabel("")
        ax.set_title(title)
        edpvr(ax, BASE, vmax=170, color=C["venous"], lw=1.4)
        espvr(ax, BASE, vmax=95, color=C["arterial"], lw=1.4, alpha=0.45 if "Ees" in over else 1)
        if "Ees" in over:
            espvr(ax, p1, vmax=72, color=C["arterial"], lw=1.6, ls=":")
        V0_, P0_ = loop_xy(B)
        V1_, P1_ = loop_xy(b1)
        ax.plot(V0_, P0_, color=C["ventricular"], lw=2.2, alpha=0.35)
        ax.plot(V1_, P1_, color=C["ventricular"], lw=2.2)
        sv_bars(ax, B, b1, 30, 42)
    axs[0].text(110, 185, "Faded: baseline beat\nSolid: new beat", fontsize=8.5, color=C["text"], va="top")
    axs[0].text(110, 165, "Bars: stroke volume\n(gray baseline, green new)", fontsize=8.5, color=C["text"], va="top")
    fig.tight_layout(w_pad=1.5)
    fs.save(fig, PART, SLUG, "determinants.svg")


# ------------------------------------------------------------------ 7. Pericardium
def fig_pericardium():
    fig, axs = plt.subplots(1, 2, figsize=(11.6, 4.8), sharey=True)
    cases = [("A  Pericardiectomy: same filling pressure, more preload", dict(k=0.023, Ppv=11.25), "Without pericardium\n(more compliant)"),
             ("B  Tamponade: same filling pressure, less preload", dict(k=0.034, Ppv=9.7), "Fluid in the pericardial sac\n(stiffer filling curve)")]
    edp = B["Plv"][B["i_mc"]]
    for ax, (title, over, lab) in zip(axs, cases):
        b1 = run(**over)
        print("  %s: EDV %.0f ESV %.0f SV %.0f EDP %.1f" % (title[:3], b1["EDV"], b1["ESV"], b1["SV"],
                                                            b1["Plv"][b1["i_mc"]]))
        pv_axes(ax, vmax=200, pmax=150)
        if ax is axs[1]:
            ax.set_ylabel("")
        ax.set_title(title, fontsize=11)
        edpvr(ax, BASE, vmax=175, color=C["venous"], lw=1.8)
        edpvr(ax, b1["p"], vmax=195 if over["k"] < 0.025 else 142, color=C["venous"], lw=1.8, ls="--")
        espvr(ax, BASE, vmax=80, color=C["arterial"], lw=1.4)
        ax.axhline(edp, color=C["ink"], lw=0.9, ls=(0, (5, 3)))
        V0_, P0_ = loop_xy(B)
        V1_, P1_ = loop_xy(b1)
        ax.plot(V0_, P0_, color=C["ventricular"], lw=2.2, alpha=0.35)
        ax.plot(V1_, P1_, color=C["ventricular"], lw=2.2)
        sv_bars(ax, B, b1, 55, 67, base_left=over["k"] < 0.025)
        ax.text(2, edp + 2.5, "same filling pressure", fontsize=8.5, color=C["ink"])
        ax.text(152 if over["k"] < 0.025 else 140, 40 if over["k"] < 0.025 else 82, lab, fontsize=8.5,
                color=C["venous"])
    axs[0].text(150, 145, "Faded: with a normal\npericardium", fontsize=8.5, color=C["text"], va="top")
    fig.tight_layout(w_pad=1.5)
    fs.save(fig, PART, SLUG, "pericardium.svg")


if __name__ == "__main__":
    fig_wiggers()
    fig_right_left()
    fig_edpvr()
    fig_espvr()
    fig_pv_loop()
    fig_determinants()
    fig_pericardium()
