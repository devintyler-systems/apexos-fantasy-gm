"""Starter audit (DECISIONS #93): every current depth-chart starter for every team on the slate must be projected, unless he is Out.

Checked slots: QB1, RB1, WR1-WR3, TE1 (proj_all.pkl) and PK1 (w4_rankings_K.csv). A starter missing without an Out/IR/manual-out
reason is a STARTER GAP and the script exits 1. usage: APEX_OUT=<run out dir> python starter_audit.py [--teams GB,LA,...]
"""
import os, sys
import pandas as pd
from load import norm_name
from paths import OUT, NFLV

TM = {"LAR": "LA", "JAC": "JAX", "WSH": "WAS"}
SLOTS = {"QB": 1, "RB": 1, "WR": 3, "TE": 1, "PK": 1}


def main():
    P = pd.read_pickle(OUT + "proj_all.pkl"); P["nkey"] = P.player.map(norm_name)
    K = pd.read_csv(OUT + "w4_rankings_K.csv"); K["nkey"] = K.player.map(norm_name)
    teams = sys.argv[sys.argv.index("--teams") + 1].split(",") if "--teams" in sys.argv else sorted(P.team.unique())
    dc = pd.read_parquet(NFLV + f"depth_charts_{os.environ.get('APEX_SEASON', 2026)}.parquet"); dc = dc[dc.dt == dc.dt.max()].copy()
    dc["team"] = dc.team.replace(TM); dc["nkey"] = dc.player_name.map(norm_name)
    out = set()
    mo = os.environ.get("APEX_MANUAL_OUT")
    if mo and os.path.exists(mo):
        m = pd.read_csv(mo, keep_default_na=False); out |= set(zip(m.player.map(norm_name), m.team.replace(TM)))
    ov = os.environ.get("APEX_STATUS_OVERLAY")
    if ov and os.path.exists(ov):
        o = pd.read_csv(ov, keep_default_na=False); o = o[o.report_status.isin(["Out", "Doubtful"])]; out |= set(zip(o.player.map(norm_name), o.team.replace(TM)))
    inj = pd.read_parquet(NFLV + f"injuries_{os.environ.get('APEX_SEASON', 2026)}.parquet"); inj = inj[(inj.week == inj.week.max()) & inj.report_status.isin(["Out", "Doubtful"])]
    out |= set(zip(inj.full_name.map(norm_name), inj.team.replace(TM)))
    r = pd.read_parquet(NFLV + f"roster_{os.environ.get('APEX_SEASON', 2026)}.parquet"); r = r[r.week == r.week.max()]
    res = set(zip(r[r.status != "ACT"].full_name.map(norm_name), r[r.status != "ACT"].team.replace(TM)))
    gaps = []
    for t in teams:
        for pos, n in SLOTS.items():
            ch = dc[(dc.team == t) & (dc.pos_abb == pos)].sort_values("pos_rank").drop_duplicates("nkey").head(n)
            have = set(K[K.team == t].nkey) if pos == "PK" else set(P[(P.team == t) & (P.p_active > 0)].nkey)
            for row in ch.itertuples():
                if row.nkey in have or (row.nkey, t) in out or (row.nkey, t) in res:
                    continue
                gaps.append(dict(team=t, slot=f"{pos}{int(row.pos_rank)}", player=row.player_name))
    if gaps:
        print("STARTER GAP: depth-chart starters missing from the projections (not Out / reserve / manual-out):\n" + pd.DataFrame(gaps).to_string(index=False))
        sys.exit(1)
    print(f"starter audit OK: {len(teams)} teams, QB1/RB1/WR1-3/TE1/PK1 all projected or explained")


if __name__ == "__main__":
    main()
