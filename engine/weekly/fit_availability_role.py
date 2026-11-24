"""R-23: does a starter flag improve P(plays | report status, practice, position)? Leave-one-season-out test over 2023-25 (2026 always in training), then writes the candidate table
config/weekly/availability_by_status_pos_role.csv (fit on all of 2023-26). Does not touch the table the engine uses. usage: python fit_availability_role.py"""
from paths import NFLV, CONF
import numpy as np, pandas as pd
from avail_role import recent_pct, role, SKILL_PG
N = NFLV
pl = pd.read_parquet(N + "players.parquet", columns=["gsis_id", "pfr_id"]).dropna()
YRS = (2023, 2024, 2025, 2026)
inj = pd.concat([pd.read_parquet(N + f"injuries_{y}.parquet") for y in YRS]); inj = inj[inj.game_type == "REG"].copy()
sn = pd.concat([pd.read_parquet(N + f"snap_counts_{y}.parquet") for y in YRS]); sn = sn[sn.game_type == "REG"].copy()
sn["snaps"] = sn.offense_snaps.fillna(0) + sn.defense_snaps.fillna(0) + sn.st_snaps.fillna(0)
sm = sn.merge(pl, left_on="pfr_player_id", right_on="pfr_id", how="left")
played = sm.groupby(["season", "week", "gsis_id"]).snaps.sum().reset_index(); played["played"] = played.snaps > 0
d = inj.merge(played[["season", "week", "gsis_id", "played"]], on=["season", "week", "gsis_id"], how="left")
tw = sn.groupby(["season", "week", "team"]).size().reset_index(name="n")[["season", "week", "team"]]
d = d.merge(tw.assign(has_game=True), on=["season", "week", "team"], how="left"); d = d[d.has_game == True].copy()
d["played"] = d.played.fillna(False).astype(int)
PG = {"QB": "QB", "RB": "RB", "FB": "RB", "WR": "WRTE", "TE": "WRTE", "T": "OL", "G": "OL", "C": "OL", "OL": "OL", "DE": "DL", "DT": "DL", "NT": "DL", "DL": "DL", "LB": "LB", "OLB": "LB", "ILB": "LB", "MLB": "LB", "CB": "DB", "S": "DB", "FS": "DB", "SS": "DB", "DB": "DB"}
d["pg"] = d.position.map(PG).fillna("OTH")
d["rs"] = d.report_status.fillna("None"); d["ps"] = d.practice_status.fillna("None").map({"Did Not Participate In Practice": "DNP", "Limited Participation in Practice": "LP", "Full Participation in Practice": "FP"}).fillna("None")
rp = {(s, w): recent_pct(sm, pl, s, w) for s in YRS for w in sorted(d[d.season == s].week.unique())}
d["recent"] = [rp[(s, w)].get(g, np.nan) for s, w, g in zip(d.season, d.week, d.gsis_id)]
d["role"] = [role(x, w) if pg in SKILL_PG else "A" for x, w, pg in zip(d.recent, d.week, d.pg)]
print("rows", len(d), "| roles (skill):", d[d.pg.isin(SKILL_PG)].role.value_counts().to_dict())


def table(df, m=12):
    root = df.groupby(["rs", "ps"]).played.agg(["sum", "size"]).reset_index(); root["p_parent"] = (root["sum"] + 1) / (root["size"] + 2)
    leaf = df.groupby(["rs", "ps", "pg"]).played.agg(["sum", "size"]).reset_index().merge(root[["rs", "ps", "p_parent"]], on=["rs", "ps"])
    leaf["p"] = (leaf["sum"] + m * leaf.p_parent) / (leaf["size"] + m)
    sk = df[df.pg.isin(SKILL_PG) & df.role.isin(["S", "O"])]
    rl = sk.groupby(["rs", "ps", "pg", "role"]).played.agg(["sum", "size"]).reset_index().merge(leaf[["rs", "ps", "pg", "p"]].rename(columns={"p": "p_leaf"}), on=["rs", "ps", "pg"])
    rl["p"] = (rl["sum"] + m * rl.p_leaf) / (rl["size"] + m)
    return root, leaf, rl


def predict(df, root, leaf, rl, use_role):
    x = df.merge(leaf[["rs", "ps", "pg", "p"]], on=["rs", "ps", "pg"], how="left").merge(root[["rs", "ps", "p_parent"]], on=["rs", "ps"], how="left")
    p = x.p.fillna(x.p_parent).fillna(0.85).values
    if use_role:
        y = df.merge(rl[["rs", "ps", "pg", "role", "p"]].rename(columns={"p": "p_role"}), on=["rs", "ps", "pg", "role"], how="left")
        p = np.where(y.p_role.notna().values, y.p_role.values, p)
    return p


def brier(p, y): return float(np.mean((p - y) ** 2))
def ll(p, y): p = np.clip(p, .02, .98); return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


rows = []
for ho in (2023, 2024, 2025):
    tr, te = d[d.season != ho], d[d.season == ho]
    root, leaf, rl = table(tr); p0 = predict(te, root, leaf, rl, False); p1 = predict(te, root, leaf, rl, True); y = te.played.values
    for nm, mk in (("all", np.ones(len(te), bool)), ("skill", te.pg.isin(SKILL_PG).values), ("QB", (te.pg == "QB").values), ("uncertain (Q/D) skill", (te.pg.isin(SKILL_PG) & te.rs.isin(["Questionable", "Doubtful"])).values)):
        rows.append(dict(holdout=ho, group=nm, n=int(mk.sum()), brier_base=brier(p0[mk], y[mk]), brier_role=brier(p1[mk], y[mk]), ll_base=ll(p0[mk], y[mk]), ll_role=ll(p1[mk], y[mk])))
R = pd.DataFrame(rows); R["d_brier"] = R.brier_role - R.brier_base; R["d_ll"] = R.ll_role - R.ll_base
pd.set_option("display.width", 200); print(R.round(4).to_string(index=False))
print("\nPooled over the three held-out seasons (negative = better):")
for g, x in R.groupby("group"): print(f"  {g:24s} n={x.n.sum():6d}  brier {np.average(x.d_brier, weights=x.n):+.5f}  logloss {np.average(x.d_ll, weights=x.n):+.5f}")
q = d[(d.pg == "QB") & d.rs.isin(["Questionable"]) & d.role.isin(["S", "O"])]
print("\nQB Questionable, played rate by role and practice:"); print(q.groupby(["role", "ps"]).played.agg(["size", "mean"]).round(2).to_string())
root, leaf, rl = table(d); rl.to_csv(CONF + "availability_by_status_pos_role.csv", index=False)
print("\nwrote availability_by_status_pos_role.csv", len(rl), "rows")
