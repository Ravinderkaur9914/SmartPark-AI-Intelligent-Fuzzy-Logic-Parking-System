"""
Fuzzy Logic Engine for Smart Parking System
Implements fuzzification, rule evaluation, and defuzzification from scratch using NumPy.
"""
import numpy as np


# ─────────────────────────────────────────────
#  MEMBERSHIP FUNCTIONS
# ─────────────────────────────────────────────

def trimf(x, a, b, c):
    """Triangular membership function."""
    x = np.asarray(x, dtype=float)
    left  = np.where(x <= a, 0.0, np.where(x <= b, (x - a) / (b - a + 1e-9), 0.0))
    right = np.where(x >= c, 0.0, np.where(x >= b, (c - x) / (c - b + 1e-9), 0.0))
    top   = np.where(x == b, 1.0, 0.0)
    return np.clip(left + right + top, 0.0, 1.0)


def trapmf(x, a, b, c, d):
    """Trapezoidal membership function."""
    x = np.asarray(x, dtype=float)
    rise = np.clip((x - a) / (b - a + 1e-9), 0.0, 1.0)
    fall = np.clip((d - x) / (d - c + 1e-9), 0.0, 1.0)
    return np.minimum(rise, fall)


# ─────────────────────────────────────────────
#  FUZZIFICATION  (scalar → membership degrees)
# ─────────────────────────────────────────────

def fuzzify_distance(d):
    """Distance 0-10: Near / Medium / Far"""
    return {
        "near":   float(trapmf(d, 0, 0, 2, 4)),
        "medium": float(trimf(d, 2, 5, 8)),
        "far":    float(trapmf(d, 6, 8, 10, 10)),
    }


def fuzzify_space(s):
    """Space 0-10: Small / Medium / Large"""
    return {
        "small":  float(trapmf(s, 0, 0, 2, 4)),
        "medium": float(trimf(s, 2, 5, 8)),
        "large":  float(trapmf(s, 6, 8, 10, 10)),
    }


def fuzzify_speed(v):
    """Speed 0-100 km/h: Slow / Medium / Fast"""
    return {
        "slow":   float(trapmf(v, 0, 0, 20, 40)),
        "medium": float(trimf(v, 20, 50, 80)),
        "fast":   float(trapmf(v, 60, 80, 100, 100)),
    }


# ─────────────────────────────────────────────
#  RULE BASE & INFERENCE
# ─────────────────────────────────────────────

def evaluate_rules(fd, fs, fv, experience, weather):
    """
    Returns dict of output fuzzy sets: tight / normal / easy
    experience: 'beginner' | 'expert'
    weather:    'clear'    | 'rainy'
    """
    exp_factor = 1.0 if experience == "expert" else 0.0   # 1 = expert
    rain_factor = 1.0 if weather == "rainy" else 0.0       # 1 = rainy

    activations = {"tight": [], "normal": [], "easy": []}

    # ── Core distance × space rules ──────────────────────────────
    activations["tight"].append( min(fd["near"],   fs["small"]) )
    activations["tight"].append( min(fd["near"],   fs["medium"]) )
    activations["normal"].append(min(fd["near"],   fs["large"]) )
    activations["normal"].append(min(fd["medium"], fs["small"]) )
    activations["normal"].append(min(fd["medium"], fs["medium"]) )
    activations["easy"].append(  min(fd["medium"], fs["large"]) )
    activations["easy"].append(  min(fd["far"],    fs["large"]) )
    activations["normal"].append(min(fd["far"],    fs["medium"]) )
    activations["tight"].append( min(fd["far"],    fs["small"]) )

    # ── Speed influence ───────────────────────────────────────────
    activations["tight"].append(fv["fast"] * 0.9)
    activations["normal"].append(fv["medium"] * 0.5)
    activations["easy"].append(fv["slow"] * 0.4)

    # ── Experience modifier ───────────────────────────────────────
    if exp_factor:   # expert: loosen output
        activations["easy"].append(0.3)
        activations["tight"].append(-0.0)   # no negative; just not adding
    else:            # beginner: tighten output
        activations["tight"].append(0.25)

    # ── Weather modifier ─────────────────────────────────────────
    if rain_factor:
        activations["tight"].append(0.3)

    return {k: max(v) for k, v in activations.items()}


# ─────────────────────────────────────────────
#  DEFUZZIFICATION  (centroid method)
# ─────────────────────────────────────────────

def defuzzify(activations):
    """
    Output universe 0-100 (parking difficulty).
    Tight → 0-40, Normal → 30-70, Easy → 60-100
    """
    universe = np.linspace(0, 100, 500)

    mf_tight  = trapmf(universe, 0, 0, 20, 45)
    mf_normal = trimf(universe, 30, 50, 70)
    mf_easy   = trapmf(universe, 55, 80, 100, 100)

    agg = np.zeros_like(universe)
    agg = np.maximum(agg, np.minimum(activations["tight"],  mf_tight))
    agg = np.maximum(agg, np.minimum(activations["normal"], mf_normal))
    agg = np.maximum(agg, np.minimum(activations["easy"],   mf_easy))

    denom = np.sum(agg)
    if denom < 1e-9:
        return 50.0
    return float(np.sum(universe * agg) / denom)


# ─────────────────────────────────────────────
#  MEMBERSHIP CURVES  (for graph visualisation)
# ─────────────────────────────────────────────

def get_membership_curves():
    d_x = np.linspace(0, 10, 300).tolist()
    s_x = np.linspace(0, 10, 300).tolist()
    o_x = np.linspace(0, 100, 300).tolist()
    d_arr = np.linspace(0, 10, 300)
    s_arr = np.linspace(0, 10, 300)
    o_arr = np.linspace(0, 100, 300)
    return {
        "distance": {
            "x": d_x,
            "near":   trapmf(d_arr, 0, 0, 2, 4).tolist(),
            "medium": trimf(d_arr, 2, 5, 8).tolist(),
            "far":    trapmf(d_arr, 6, 8, 10, 10).tolist(),
        },
        "space": {
            "x": s_x,
            "small":  trapmf(s_arr, 0, 0, 2, 4).tolist(),
            "medium": trimf(s_arr, 2, 5, 8).tolist(),
            "large":  trapmf(s_arr, 6, 8, 10, 10).tolist(),
        },
        "output": {
            "x": o_x,
            "tight":  trapmf(o_arr, 0, 0, 20, 45).tolist(),
            "normal": trimf(o_arr, 30, 50, 70).tolist(),
            "easy":   trapmf(o_arr, 55, 80, 100, 100).tolist(),
        },
    }


# ─────────────────────────────────────────────
#  MAIN ENTRY POINT
# ─────────────────────────────────────────────

def run_fuzzy(distance, space, speed, experience="beginner", weather="clear"):
    fd = fuzzify_distance(distance)
    fs = fuzzify_space(space)
    fv = fuzzify_speed(speed)
    activations = evaluate_rules(fd, fs, fv, experience, weather)
    score = defuzzify(activations)
    score = max(0.0, min(100.0, score))

    if score >= 60:
        decision, risk = "Easy",   "Low"
    elif score >= 35:
        decision, risk = "Normal", "Medium"
    else:
        decision, risk = "Tight",  "High"

    return {
        "score": round(score, 1),
        "decision": decision,
        "risk": risk,
        "activations": {k: round(v, 3) for k, v in activations.items()},
        "memberships": {
            "distance": fd,
            "space": fs,
            "speed": fv,
        }
    }
