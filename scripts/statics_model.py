"""Python port of the Respiratory Mechanics Lab statics model (dist/model.js, v24).

Units: volume in L, pressure in cm H2O relative to atmosphere. Keep this file in step with
model.js so the book's figures and the simulator draw the same curves.
"""
import math

NORMAL = dict(
    lungV0=1.2530, lungVmax=6.2742, lungK=0.08552, lungSizeExp=0.25,
    cwVlow=1.1398, cwVhigh=8.5, cwPc=0.1816, cwB=4.7798,
    inspSlope=13.0, expSlope=33.0, muscleRefTlc=6.0, muscleRefRv=1.5,
)
CW_PIVOT_VOLUME = 1.5
DEFAULT = dict(lungCompliance=1.0, chestWallCompliance=1.0, chestWallLoad=0.0, muscleStrength=1.0)
PRESETS = {
    "normal": {},
    "emphysema": dict(lungCompliance=2.5),
    "fibrosis": dict(lungCompliance=0.44),
    "obesity": dict(chestWallLoad=5.0),
    "neuromuscular": dict(muscleStrength=0.25),
}


def _g(s, p):
    return s ** p["lungSizeExp"]


def lung_min_volume(s=1.0, p=NORMAL):
    return p["lungV0"] * _g(s, p)


def lung_max_volume(s=1.0, p=NORMAL):
    return p["lungVmax"] * _g(s, p)


def lung_volume(P, s=1.0, p=NORMAL):
    if P < 0:
        return float("nan")
    g = _g(s, p)
    return g * (p["lungVmax"] - (p["lungVmax"] - p["lungV0"]) * math.exp(-p["lungK"] * (s / g) * P))


def lung_pressure(V, s=1.0, p=NORMAL):
    g = _g(s, p)
    v = V / g
    if v <= p["lungV0"]:
        return 0.0
    if v >= p["lungVmax"]:
        return float("inf")
    return -math.log((p["lungVmax"] - v) / (p["lungVmax"] - p["lungV0"])) / (p["lungK"] * (s / g))


def _cw_raw_pressure(V, p):
    if V <= p["cwVlow"]:
        return -float("inf")
    if V >= p["cwVhigh"]:
        return float("inf")
    return p["cwPc"] - p["cwB"] * math.log((p["cwVhigh"] - p["cwVlow"]) / (V - p["cwVlow"]) - 1)


def _cw_raw_volume(P, p):
    return p["cwVlow"] + (p["cwVhigh"] - p["cwVlow"]) / (1 + math.exp(-(P - p["cwPc"]) / p["cwB"]))


def chest_wall_volume(P, s=1.0, p=NORMAL, load=0.0):
    piv = _cw_raw_pressure(CW_PIVOT_VOLUME, p)
    return _cw_raw_volume(piv + s * (P - load - piv), p)


def chest_wall_pressure(V, s=1.0, p=NORMAL, load=0.0):
    piv = _cw_raw_pressure(CW_PIVOT_VOLUME, p)
    return piv + (_cw_raw_pressure(V, p) - piv) / s + load


def settings_of(**kw):
    s = dict(DEFAULT)
    s.update(kw)
    return s


def system_pressure(V, st, p=NORMAL):
    return lung_pressure(V, st["lungCompliance"], p) + chest_wall_pressure(V, st["chestWallCompliance"], p, st["chestWallLoad"])


def _bisect(f, lo, hi):
    for _ in range(100):
        mid = (lo + hi) / 2
        if f(mid) < 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def _vrange(st, p):
    return p["cwVlow"] + 1e-9, min(lung_max_volume(st["lungCompliance"], p), p["cwVhigh"]) - 1e-9


def volume_at_system_pressure(target, st, p=NORMAL):
    lo, hi = _vrange(st, p)
    return _bisect(lambda V: system_pressure(V, st, p) - target, lo, hi)


def _calibrate():
    q = dict(NORMAL)
    d = settings_of()
    q["inspMax"] = system_pressure(q["muscleRefTlc"], d, q)
    q["expMax"] = -system_pressure(q["muscleRefRv"], d, q)
    return q


PARAMS = _calibrate()


def insp_muscle(V, strength=1.0, p=PARAMS):
    return max(0.0, strength * (p["inspMax"] + p["inspSlope"] * (p["muscleRefTlc"] - V)))


def exp_muscle(V, strength=1.0, p=PARAMS):
    return max(0.0, strength * (p["expMax"] + p["expSlope"] * (V - p["muscleRefRv"])))


def analyze(st, p=PARAMS):
    frc = volume_at_system_pressure(0.0, st, p)
    lo, hi = _vrange(st, p)
    tlc = _bisect(lambda V: system_pressure(V, st, p) - insp_muscle(V, st["muscleStrength"], p), lo, hi)
    rv = _bisect(lambda V: system_pressure(V, st, p) + exp_muscle(V, st["muscleStrength"], p), lo, hi)
    rv = max(rv, lung_min_volume(st["lungCompliance"], p))
    return dict(frc=frc, tlc=tlc, rv=rv, vc=tlc - rv,
                pl_frc=lung_pressure(frc, st["lungCompliance"], p),
                pcw_frc=chest_wall_pressure(frc, st["chestWallCompliance"], p, st["chestWallLoad"]),
                cw_rest=chest_wall_volume(0.0, st["chestWallCompliance"], p, st["chestWallLoad"]))


if __name__ == "__main__":
    for k, v in PRESETS.items():
        a = analyze(settings_of(**v))
        print(k, {x: round(y, 2) for x, y in a.items()})
