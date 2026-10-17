"""Anytime-TD probability floor (candidate v3, DECISIONS #29).

Backtest 2023-25 weeks 4-12: the simulator's anytime-TD probability is too low in the tail. Non-QB players projected under 5% scored about 7.5% of the time, and a floor
on that probability improved held-out log loss. The floor changes only the published anytime-TD probability (market rows, `any_td_pct`); simulated TD means, shares,
first-TD and 2+ TD probabilities are untouched. 0.0 (the default) is the baseline: byte-identical output.
"""
import json
import os


def load_floor(path):
    """anytime_floor from a td_params file; 0.0 when the file or key is absent."""
    if not path or not os.path.exists(path):
        return 0.0
    return float(json.load(open(path)).get("anytime_floor", 0.0) or 0.0)


def floor_anytime(p, pos, rec_mean, floor, active=True):
    """max(p, floor) for an active non-QB player projected for at least 0.5 receptions (the population the backtest measured); otherwise p."""
    if floor and active and pos != "QB" and rec_mean >= 0.5:
        return max(float(p), float(floor))
    return float(p)
