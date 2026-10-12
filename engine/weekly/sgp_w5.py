"""Same-game parlay fair prices from the simulated JOINT distribution (never multiplied legs). Model numbers only: no book SGP prices are in the odds files.
Usage: APEX_ENV=<track> python sgp_w5.py  -> prints markdown. Legs are conditioned on every named player being active (their availability masks)."""
import numpy as np, pandas as pd
import run_all as R
from params import SCHED, norm_name, is_neutral

def amer(p):
    p = float(np.clip(p, 1e-4, 1 - 1e-4)); return int(round(-100 * p / (1 - p))) if p >= .5 else int(round(100 * (1 - p) / p))
def game(a, h):
    R.run_game(a, h, neutral=is_neutral(a, h)); d = R.STORE.pop((a, h))
    pls = {}
    for t in (a, h):
        for pl in d["players"][t]: pls[norm_name(pl["player"])] = pl
    return d, pls
def atd(pl): return (pl["rush_td"] + pl["rec_td"]) >= 1
STACKS = {
 ("TB", "DAL"): [("Javonte Williams anytime TD + CeeDee Lamb anytime TD", ["javonte williams", "ceedee lamb"], lambda d, P: atd(P["javonte williams"]) & atd(P["ceedee lamb"]), ["atd:javonte williams", "atd:ceedee lamb"]),
                 ("Dak Prescott 2+ pass TD + CeeDee Lamb anytime TD", ["dak prescott", "ceedee lamb"], lambda d, P: (P["dak prescott"]["pass_td"] >= 2) & atd(P["ceedee lamb"]), ["ptd2:dak prescott", "atd:ceedee lamb"]),
                 ("DAL wins + Javonte Williams anytime TD", ["javonte williams"], lambda d, P: (d["H"]["pts"] > d["A"]["pts"]) & atd(P["javonte williams"]), ["win:H", "atd:javonte williams"])],
 ("DET", "ARI"): [("Jahmyr Gibbs anytime TD + Amon-Ra St. Brown anytime TD", ["jahmyr gibbs", "amon-ra st brown"], lambda d, P: atd(P["jahmyr gibbs"]) & atd(P["amon-ra st brown"]), ["atd:jahmyr gibbs", "atd:amon-ra st brown"]),
                  ("Jared Goff 2+ pass TD + Amon-Ra St. Brown anytime TD", ["jared goff", "amon-ra st brown"], lambda d, P: (P["jared goff"]["pass_td"] >= 2) & atd(P["amon-ra st brown"]), ["ptd2:jared goff", "atd:amon-ra st brown"])],
}
def marg(spec, d, P, mask):
    k, n = spec.split(":")
    if k == "atd": return atd(P[n])
    if k == "ptd2": return P[n]["pass_td"] >= 2
    if k == "win": return d["H"]["pts"] > d["A"]["pts"]
rows = []
for (a, h), stacks in STACKS.items():
    d, P = game(a, h)
    for label, names, f, legs in stacks:
        m = np.ones(len(P[names[0]]["mask"]), bool)
        for n in names: m &= P[n]["mask"]
        j = float(f(d, P)[m].mean()); prod = float(np.prod([marg(l, d, P, m)[m].mean() for l in legs]))
        rows.append((f"{a}@{h}", label, j, prod, int(m.sum())))
print("| Game | Same-game parlay (all named players active) | Joint probability (sim) | Naive product of legs | Joint fair price | Correlation uplift |\n|---|---|---|---|---|---|")
for g, l, j, p, n in rows:
    flag = " (above 85%, shown capped)" if j > .85 else ""
    print(f"| {g} | {l} | {'85%+' if j > .85 else f'{j*100:.1f}%'}{flag} | {p*100:.1f}% | {amer(j):+d} | {j/p:.2f}x |")
