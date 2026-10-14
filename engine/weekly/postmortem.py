"""Tuesday postmortem in one command: python postmortem.py SEASON WEEK [--out docs/weekly/POSTMORTEM_<season>_W<week>_tables.md]
Per final game it picks, per track, the LATEST frozen run whose as_of_utc is before kickoff (else the latest run), then reports from frozen projections + nflverse actuals only:
  games     team points / margin / total vs the DraftKings line stored in nflverse (what the market track is anchored to) and the model-only track
  skill     player-level MAE/bias/correlation against the naive 'weeks 1..W-1 per-game average' baseline (is the model better than an average?)
  availability  p_active calibration, projected-active players who logged no snap, players with real usage the model never had
  volume    team pass/rush attempts and TDs vs projection
  dk        DraftKings points bias by position and by within-team rank (the optimizer's-curse check)
Nothing here changes a frozen run. Book-vs-model prop grading needs the operator's odds file and lives in price_odds.py outputs."""
import argparse, glob, json, os, sys
import numpy as np, pandas as pd
from paths import NFLV
from load import norm_name

NV2T = {"LAR": "LA", "WSH": "WAS", "JAC": "JAX", "LVR": "LV", "OAK": "LV", "SD": "LAC", "STL": "LA"}


def pick_runs(runs_dir, season, week, games):
    """{(game, track): run_dir}: latest run with as_of_utc <= kickoff, else the latest run that has the game."""
    ms = []
    for p in glob.glob(os.path.join(runs_dir, f"{season}_w{week:02d}_*", "manifest.json")):
        m = json.load(open(p)); ms.append((m["as_of_utc"], m["track"], os.path.dirname(p)))
    out = {}
    for g in games.itertuples():
        ts = pd.Timestamp(f"{g.gameday} {g.gametime}"); ko = ts + pd.Timedelta(hours=4 if 3 < ts.month < 11 else 5)      # ET -> UTC without tzdata (early-Nov weeks can be an hour off; only affects which run is 'pre-kickoff')
        for tr in ("market", "model"):
            c = sorted((a, d) for a, t, d in ms if t == tr)
            pre = [d for a, d in c if pd.Timestamp(a).tz_localize(None) <= ko]
            out[(f"{g.away_team}@{g.home_team}", tr)] = (pre or [d for a, d in c])[-1] if c else None
    return out


def load_games(season, week):
    g = pd.read_parquet(NFLV + "games.parquet"); g = g[(g.season == season) & (g.week == week) & (g.game_type == "REG")].copy()
    for c in ("home_team", "away_team"):
        g[c] = g[c].replace(NV2T)
    return g[g.home_score.notna()]


def games_table(g, pick):
    rows = []
    for r in g.itertuples():
        k = f"{r.away_team}@{r.home_team}"; d = dict(game=k, away=r.away_score, home=r.home_score, dk_margin=r.spread_line, dk_total=r.total_line)
        for t in ("market", "model"):
            p = pick[(k, t)]
            if p is None: continue
            e = pd.read_csv(os.path.join(p, "w4_game_environment.csv")); x = e[(e.away == r.away_team) & (e.home == r.home_team)].iloc[0]
            d[f"{t}_away"], d[f"{t}_home"] = x[f"{r.away_team}_pts_mean"], x[f"{r.home_team}_pts_mean"]
        rows.append(d)
    D = pd.DataFrame(rows); D["act_margin"] = D.home - D.away; D["act_total"] = D.home + D.away
    s = {}
    for t in ("market", "model"):
        if f"{t}_home" not in D: continue
        e = np.r_[D[f"{t}_away"] - D.away, D[f"{t}_home"] - D.home]
        s[t] = dict(team_rmse=float(np.sqrt((e ** 2).mean())), bias=float(e.mean()), margin_mae=float(((D[f"{t}_home"] - D[f"{t}_away"]) - D.act_margin).abs().mean()),
                    total_mae=float(((D[f"{t}_home"] + D[f"{t}_away"]) - D.act_total).abs().mean()), winner_hit=float((((D[f"{t}_home"] - D[f"{t}_away"]) > 0) == (D.act_margin > 0)).mean()))
    e = np.r_[D.dk_total / 2 - D.dk_margin / 2 - D.away, D.dk_total / 2 + D.dk_margin / 2 - D.home]
    s["dk_line"] = dict(team_rmse=float(np.sqrt((e ** 2).mean())), bias=float(e.mean()), margin_mae=float((D.dk_margin - D.act_margin).abs().mean()),
                        total_mae=float((D.dk_total - D.act_total).abs().mean()), winner_hit=float(((D.dk_margin > 0) == (D.act_margin > 0)).mean()))
    return D, s


def player_frame(pick, season, week, track="market"):
    from grade import grade
    fr = []
    for (k, t), p in pick.items():
        if t != track or p is None: continue
        grade(p)                                  # writes grade_players.csv beside the (frozen) manifest; idempotent for a final game
        gp = pd.read_csv(os.path.join(p, "grade_players.csv")); fr.append(gp[gp.game == k])
    return pd.concat(fr) if fr else pd.DataFrame()


def skill_table(P, season, week):
    st = pd.read_parquet(NFLV + f"stats_player_week_{season}.parquet"); st = st[(st.season_type == "REG") & (st.week < week)].copy(); st["nkey"] = st.player_display_name.map(norm_name)
    MK = [("rec_yds", "rec_yds_mean", "receiving_yards", "targets", lambda d: (d.rec_mean >= 1) & (d.pos != "QB")), ("rec", "rec_mean", "receptions", "targets", lambda d: (d.rec_mean >= 1) & (d.pos != "QB")),
          ("rush_yds", "rush_yds_mean", "rushing_yards", "carries", lambda d: (d.rush_att_mean >= 4) & (d.pos != "QB")), ("pass_yds", "pass_yds_mean", "passing_yards", "attempts", lambda d: d.pass_yds_mean >= 100),
          ("pass_cmp", "pass_cmp_mean", "completions", "attempts", lambda d: d.pass_yds_mean >= 100)]
    rows = []
    for n, pc, ac, vol, mask in MK:
        d = P[mask(P)].copy(); h = st[st[vol] > 0].groupby("nkey")[ac].agg(["mean", "size"]); d["naive"] = d.nkey.map(h["mean"]); d["ng"] = d.nkey.map(h["size"]); d = d[d.naive.notna() & (d.ng >= 2)]
        if len(d) < 5: continue
        rows.append(dict(market=n, n=len(d), mae_model=(d[pc] - d[ac]).abs().mean(), mae_naive=(d.naive - d[ac]).abs().mean(), mae_blend=((0.5 * d[pc] + 0.5 * d.naive) - d[ac]).abs().mean(),
                         bias_model=(d[pc] - d[ac]).mean(), corr_model=np.corrcoef(d[pc], d[ac])[0, 1], corr_naive=np.corrcoef(d.naive, d[ac])[0, 1]))
    return pd.DataFrame(rows)


def availability(pick, season, week):
    sn = pd.read_parquet(NFLV + f"snap_counts_{season}.parquet"); sn = sn[(sn.game_type == "REG") & (sn.week == week)].copy(); sn["nkey"] = sn.player.map(norm_name); sn["team"] = sn.team.replace(NV2T)
    off = set(zip(sn[sn.offense_snaps > 0].nkey, sn[sn.offense_snaps > 0].team)); fr = []
    for (k, t), p in pick.items():
        if t != "market" or p is None: continue
        a = pd.read_csv(os.path.join(p, "projections.csv")); fr.append(a[a.game == k])
    A = pd.concat(fr); A["nkey"] = A.player.map(norm_name); A["played"] = [(a, b) in off for a, b in zip(A.nkey, A.team)]
    bins = [(0, .05), (.05, .5), (.5, .9), (.9, .99), (.99, 1.01)]
    cal = pd.DataFrame([dict(lo=lo, hi=hi, n=int(((A.p_active >= lo) & (A.p_active < hi)).sum()), mean_p=float(A[(A.p_active >= lo) & (A.p_active < hi)].p_active.mean()),
                             played=float(A[(A.p_active >= lo) & (A.p_active < hi)].played.mean())) for lo, hi in bins])
    ghost = A[(A.p_active >= .9) & (~A.played) & ((A.get("tgt_mean", 0) >= 2) | (A.get("rush_att_mean", 0) >= 4))][["game", "player", "pos", "team", "p_active"]]
    st = pd.read_parquet(NFLV + f"stats_player_week_{season}.parquet"); st = st[(st.season_type == "REG") & (st.week == week)].copy(); st["nkey"] = st.player_display_name.map(norm_name); st["team"] = st.team.replace(NV2T)
    known = set(zip(A.nkey, A.team)); u = st[(st.targets >= 3) | (st.carries >= 5) | (st.attempts >= 10)]
    unknown = u[[(a, b) not in known for a, b in zip(u.nkey, u.team)]][["player_display_name", "team", "targets", "carries", "attempts"]]
    return cal, ghost, unknown


def volume(pick, season, week):
    ts = pd.read_parquet(NFLV + f"stats_team_week_{season}.parquet"); ts = ts[(ts.season_type == "REG") & (ts.week == week)].copy(); ts["team"] = ts.team.replace(NV2T)
    fr = []
    for (k, t), p in pick.items():
        if t != "market" or p is None: continue
        e = pd.read_csv(os.path.join(p, "w4_team_environment.csv")); fr.append(e[e.game == k])
    M = pd.concat(fr).merge(ts[["team", "attempts", "carries", "passing_yards", "rushing_yards", "passing_tds", "rushing_tds"]], on="team")
    rows = []
    for a, b in (("pass_att", "attempts"), ("rush_att", "carries"), ("pass_yds", "passing_yards"), ("rush_yds", "rushing_yards"), ("pass_td", "passing_tds"), ("rush_td", "rushing_tds")):
        rows.append(dict(stat=a, proj=M[a].mean(), actual=M[b].mean(), rmse=float(np.sqrt(((M[a] - M[b]) ** 2).mean())), sd_actual=float(M[b].std()), corr=float(np.corrcoef(M[a], M[b])[0, 1])))
    return pd.DataFrame(rows)


def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("season", type=int); ap.add_argument("week", type=int); ap.add_argument("--runs", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "runs", "weekly"))
    a = ap.parse_args(argv)
    g = load_games(a.season, a.week); pick = pick_runs(a.runs, a.season, a.week, g)
    D, s = games_table(g, pick); P = player_frame(pick, a.season, a.week)
    pd.set_option("display.width", 220); pd.set_option("display.max_rows", 200)
    print(f"# Postmortem tables, {a.season} week {a.week}: {len(g)} final games\n"); print("## games\n", D.round(1).to_string(index=False)); print(json.dumps(s, indent=1))
    print("\n## skill vs naive per-game average (market track)\n", skill_table(P, a.season, a.week).round(3).to_string(index=False))
    cal, ghost, unknown = availability(pick, a.season, a.week); print("\n## availability calibration\n", cal.round(3).to_string(index=False))
    print("\nprojected active with usage but no snap:\n", ghost.to_string(index=False)); print("\nreal usage, not in projections:\n", unknown.to_string(index=False))
    print("\n## team volume\n", volume(pick, a.season, a.week).round(2).to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
