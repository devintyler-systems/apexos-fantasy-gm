"""Score hindsight-diagnostic replays (tools/replay/build_vintage.py) against final nflverse actuals.

python tools/replay/score_replay.py 2026 9 10   -> docs/weekly/intake_2026_w09_w11/retro/*.csv + printed summary
NOT a grade of original forecasts (none were archived for W9/W10). Actuals come from the FULL cache (var/nflverse).
Sign conventions: margin = home - away; error = projected - actual (positive = over-projected).
Line baseline = nflverse spread_line/total_line, which are CLOSING lines (known at kickoff, not at a Wednesday cutoff).
Player join: norm_name + team (same convention as engine/weekly/postmortem.py); unmatched rows are counted, not dropped silently.
"""
import sys, json
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[2]
import re


def norm_name(s):  # copy of engine/weekly/load.py norm_name (importing load.py has side effects)
    s = str(s).replace("*", "").replace("+", "").strip()
    s = re.sub(r"[.’']", "", s).lower()
    s = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b", "", s)
    return re.sub(r"\s+", " ", s).strip()

NV = ROOT / "var/nflverse"
OUTD = ROOT / "docs/weekly/intake_2026_w09_w11/retro"; OUTD.mkdir(parents=True, exist_ok=True)
season, weeks = int(sys.argv[1]), [int(w) for w in sys.argv[2:]]
TM = {"LA": "LA", "LAR": "LA", "WSH": "WAS"}
tm = lambda t: TM.get(t, t)


def fp(d):  # engine definition (sim.py fp): no yardage bonuses, -2 INT, -2 fumbles lost
    fl = d.sack_fumbles_lost.fillna(0) + d.rushing_fumbles_lost.fillna(0) + d.receiving_fumbles_lost.fillna(0)
    return (0.04 * d.passing_yards + 4 * d.passing_tds - 2 * d.passing_interceptions + 0.1 * (d.rushing_yards + d.receiving_yards)
            + 6 * (d.rushing_tds + d.receiving_tds) + d.receptions - 2 * fl).fillna(0)


G = pd.read_parquet(NV / "games.parquet"); G = G[(G.season == season) & (G.game_type == "REG")]
ST = pd.read_parquet(NV / f"stats_player_week_{season}.parquet"); ST = ST[ST.season_type == "REG"].copy()
ST["team"] = ST.team.map(tm); ST["nkey"] = ST.player_display_name.map(norm_name); ST["fp"] = fp(ST)
SN = pd.read_parquet(NV / f"snap_counts_{season}.parquet"); SN = SN[SN.game_type == "REG"].copy()
SN["team"] = SN.team.map(tm); SN["nkey"] = SN.player.map(norm_name)
TS = pd.read_parquet(NV / f"stats_team_week_{season}.parquet"); TS = TS[TS.season_type == "REG"].copy(); TS["team"] = TS.team.map(tm)

games, teams, players = [], [], []
for w in weeks:
    gw = G[G.week == w]
    for track in ("model", "market"):
        od = ROOT / f"var/replay_{season}_w{w:02d}/out_{track}"
        ge = pd.read_csv(od / "w4_game_environment.csv")
        for r in ge.itertuples():
            a, h = tm(r.away), tm(r.home)
            g = gw[(gw.away_team.map(tm) == a) & (gw.home_team.map(tm) == h)]
            if not len(g):
                continue
            g = g.iloc[0]; m_act = g.home_score - g.away_score; t_act = g.home_score + g.away_score
            p = float(r.home_win_prob); y = 1.0 if m_act > 0 else (0.0 if m_act < 0 else 0.5)
            games.append(dict(week=w, track=track, game=f"{a}@{h}", home_win_prob=p, proj_margin=r.mean_margin_home, act_margin=m_act,
                              proj_total=r.total_mean, total_p25=r.total_p25, total_p75=r.total_p75, act_total=t_act,
                              line_margin=g.spread_line, line_total=g.total_line, home_won=y, overtime=g.overtime))
        tt = pd.read_csv(od / "w4_team_environment.csv"); tp = pd.read_csv(od / "w4_team_totals.csv")
        tt = tt.merge(tp[["team", "pts_mean"]], on="team", how="left")
        for r in tt.itertuples():
            act = TS[(TS.week == w) & (TS.team == tm(r.team))]
            gg = gw[(gw.home_team.map(tm) == tm(r.team)) | (gw.away_team.map(tm) == tm(r.team))]
            if not len(act) or not len(gg):
                continue
            act = act.iloc[0]; gg = gg.iloc[0]
            pts = gg.home_score if tm(gg.home_team) == tm(r.team) else gg.away_score
            teams.append(dict(week=w, track=track, team=tm(r.team), proj_pts=r.pts_mean, act_pts=pts, proj_pass_att=r.pass_att, act_pass_att=act.attempts,
                              proj_rush_att=r.rush_att, act_rush_att=act.carries, proj_pass_yds=r.pass_yds, act_pass_yds=act.passing_yards,
                              proj_rush_yds=r.rush_yds, act_rush_yds=act.rushing_yards, proj_sacks=r.sacks_taken, act_sacks=act.sacks_suffered))
        pa = pd.read_pickle(od / "proj_all.pkl"); rk = pd.read_csv(od / "w4_rankings_ALL.csv")
        pa = pa.merge(rk[["player", "team", "ev_pts", "median_if_active", "p25", "p75"]].rename(columns={"p25": "fp_p25", "p75": "fp_p75"}), on=["player", "team"], how="left")
        pa["team"] = pa.team.map(tm); pa["nkey"] = pa.player.map(norm_name)
        sw = ST[ST.week == w]; snw = SN[SN.week == w][["nkey", "team", "offense_snaps"]]
        m = pa.merge(sw[["nkey", "team", "passing_yards", "passing_tds", "rushing_yards", "carries", "receiving_yards", "receptions", "targets",
                         "rushing_tds", "receiving_tds", "fp"]], on=["nkey", "team"], how="left").merge(snw, on=["nkey", "team"], how="left")
        m["played"] = (m.offense_snaps.fillna(0) > 0) | m.fp.notna() & (m[["carries", "targets"]].fillna(0).sum(axis=1) > 0)
        m["any_td_act"] = ((m.rushing_tds.fillna(0) + m.receiving_tds.fillna(0)) > 0).astype(float)
        m["fp_act"] = m.fp.fillna(0.0)
        m["week"], m["track"] = w, track
        players.append(m)

GM = pd.DataFrame(games); TT = pd.DataFrame(teams); PL = pd.concat(players, ignore_index=True)
# naive baseline: player's per-game average in games played before the target week (same season)
nav = []
for w in weeks:
    pre = ST[ST.week < w].groupby(["nkey", "team"])[["passing_yards", "rushing_yards", "receiving_yards", "receptions", "fp"]].mean().add_prefix("naive_").reset_index()
    pre["week"] = w; nav.append(pre)
PL = PL.merge(pd.concat(nav), on=["nkey", "team", "week"], how="left")
GM.to_csv(OUTD / "replay_games.csv", index=False); TT.to_csv(OUTD / "replay_teams.csv", index=False)
keep = ["week", "track", "player", "pos", "team", "opp", "game", "p_active", "status", "played", "offense_snaps", "pass_yds_mean", "pass_yds_p25", "pass_yds_p75", "passing_yards",
        "rush_yds_mean", "rush_yds_p25", "rush_yds_p75", "rushing_yards", "rush_att_mean", "carries", "rec_yds_mean", "rec_yds_p25", "rec_yds_p75", "receiving_yards",
        "rec_mean", "receptions", "tgt_mean", "targets", "any_td_pct", "any_td_act", "ev_pts", "median_if_active", "fp_act",
        "naive_passing_yards", "naive_rushing_yards", "naive_receiving_yards", "naive_receptions", "naive_fp"]
PL[keep].to_csv(OUTD / "replay_players.csv", index=False)


def err(p, a):
    e = (p - a).dropna(); return dict(n=len(e), bias=e.mean(), mae=e.abs().mean(), rmse=np.sqrt((e ** 2).mean()))


S = {}
for (w, tr), d in list(GM.groupby(["week", "track"])) + [(("pooled", tr), d) for tr, d in GM.groupby("track")]:
    dd = d[d.home_won != 0.5]; p = dd.home_win_prob.clip(1e-3, 1 - 1e-3)
    line_w = d[(d.line_margin != 0) & (d.home_won != 0.5)]
    S[f"games|{w}|{tr}"] = dict(n=len(d), winner_acc=float(((dd.home_win_prob > .5) == (dd.home_won == 1)).mean()),
        brier=float(((p - dd.home_won) ** 2).mean()), logloss=float(-(dd.home_won * np.log(p) + (1 - dd.home_won) * np.log(1 - p)).mean()),
        margin=err(d.proj_margin, d.act_margin), total=err(d.proj_total, d.act_total),
        total_iqr_cov=float(((d.act_total >= d.total_p25) & (d.act_total <= d.total_p75)).mean()),
        line_winner_acc=float(((line_w.line_margin > 0) == (line_w.home_won == 1)).mean()), line_margin=err(d.line_margin, d.act_margin), line_total=err(d.line_total, d.act_total))
for tr, d in TT.groupby("track"):
    S[f"teams|pooled|{tr}"] = {k: err(d[f"proj_{k}"], d[f"act_{k}"]) for k in ("pts", "pass_att", "rush_att", "pass_yds", "rush_yds", "sacks")}
for tr, d in PL.groupby("track"):
    out = {}
    pl = d[d.played]
    for stat, pc, ac, nc, posf in [("pass_yds", "pass_yds_mean", "passing_yards", "naive_passing_yards", ["QB"]), ("rush_yds", "rush_yds_mean", "rushing_yards", "naive_rushing_yards", ["QB", "RB", "WR"]),
                                   ("rec_yds", "rec_yds_mean", "receiving_yards", "naive_receiving_yards", ["RB", "WR", "TE"]), ("rec", "rec_mean", "receptions", "naive_receptions", ["RB", "WR", "TE"])]:
        for pos in posf:
            x = pl[(pl.pos == pos) & pl[pc].notna()].copy(); x[ac] = x[ac].fillna(0)
            out[f"{stat}|{pos}"] = dict(model=err(x[pc], x[ac]), naive=err(x[nc], x[ac]),
                                        iqr_cov=float(((x[ac] >= x[pc.replace('mean', 'p25')]) & (x[ac] <= x[pc.replace('mean', 'p75')])).mean()) if pc.replace('mean', 'p25') in x else None)
    t = d[d.any_td_pct.notna() & d.pos.isin(["RB", "WR", "TE", "QB"])]
    pr = t.any_td_pct.clip(1e-3, 1 - 1e-3); base = t.any_td_act.mean()
    out["anytime_td"] = dict(n=len(t), brier=float(((pr - t.any_td_act) ** 2).mean()), flat_brier=float(((base - t.any_td_act) ** 2).mean()),
                             logloss=float(-(t.any_td_act * np.log(pr) + (1 - t.any_td_act) * np.log(1 - pr)).mean()), mean_p=float(pr.mean()), base_rate=float(base))
    f = d[d.ev_pts.notna() & d.pos.isin(["QB", "RB", "WR", "TE"])]
    out["fantasy_ev_all_projected"] = {pos: dict(model=err(x.ev_pts, x.fp_act), naive=err(x.naive_fp, x.fp_act)) for pos, x in f.groupby("pos")}
    out["availability"] = dict(projected=int(len(d)), played=int(d.played.sum()), projected_p_active_ge_0_5_did_not_play=int(((d.p_active >= .5) & ~d.played).sum()))
    S[f"players|pooled|{tr}"] = out
(OUTD / "replay_summary.json").write_text(json.dumps(S, indent=1, default=float))
print(json.dumps(S, indent=1, default=lambda v: round(float(v), 3)))
