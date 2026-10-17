"""Team offense, team defense and defense-vs-position tables for a target week (all from nflverse; no model inputs).

Usage: python team_tables.py [SEASON] [THROUGH_WEEK] [OUT_DIR]   (defaults: 2026, APEX_THROUGH_WEEK or 5, OUT)
Writes team_offense.csv, team_defense.csv, dvp.csv, matchups.csv and returns the frames. League TD points (6 per TD for every credited player) are reported beside PPR
so the same table serves the SPAMML league. Rank 1 = most allowed (weakest defense) for defense tables, 1 = best for offense tables.
Sample is a handful of games: treat ranks as descriptions of what has happened, not predictions.
"""
import os
import sys

import numpy as np
import pandas as pd

from paths import NFLV, OUT

POS = ["QB", "RB", "WR", "TE"]


def _pbp(season, through):
    cols = ["week", "posteam", "defteam", "play_type", "epa", "success", "yardline_100", "touchdown", "drive", "game_id", "season_type", "pass", "rush", "sack", "interception", "fumble_lost", "down", "ydstogo", "first_down", "qb_scramble"]
    p = pd.read_parquet(NFLV + f"play_by_play_{season}.parquet", columns=cols)
    return p[(p.season_type == "REG") & (p.week <= through)]


def build(season=2026, through=5, target_week=None):
    target_week = target_week or through + 1
    tw = pd.read_parquet(NFLV + f"stats_team_week_{season}.parquet"); tw = tw[(tw.season_type == "REG") & (tw.week <= through)]
    g = pd.read_parquet(NFLV + "games.parquet"); g = g[(g.season == season) & (g.game_type == "REG")]
    sc = pd.concat([g[g.week <= through].assign(team=g.home_team, opp=g.away_team, pf=g.home_score, pa=g.away_score),
                    g[g.week <= through].assign(team=g.away_team, opp=g.home_team, pf=g.away_score, pa=g.home_score)])[["week", "team", "opp", "pf", "pa"]].dropna()
    p = _pbp(season, through)
    pl = p[p.play_type.isin(["pass", "run"]) & p.epa.notna()]
    rz = p[(p.yardline_100 <= 20) & p.play_type.isin(["pass", "run"]) & p.posteam.notna()]
    rzd = rz.groupby(["posteam", "game_id", "drive"]).touchdown.max().reset_index()

    off = tw.groupby("team").agg(g=("week", "nunique"), pass_att=("attempts", "mean"), cmp=("completions", "mean"), pass_yds=("passing_yards", "mean"), pass_td=("passing_tds", "mean"),
                                 rush_att=("carries", "mean"), rush_yds=("rushing_yards", "mean"), rush_td=("rushing_tds", "mean"), sacks_taken=("sacks_suffered", "mean"), tgt=("targets", "mean"))
    off["pts"] = sc.groupby("team").pf.mean()
    off["plays"] = off.pass_att + off.rush_att + off.sacks_taken
    off["pass_rate"] = off.pass_att / (off.pass_att + off.rush_att)
    off["td_per_g"] = off.pass_td + off.rush_td
    for nm, m in (("pass", pl[pl["pass"] == 1]), ("rush", pl[pl["rush"] == 1])):
        off[f"{nm}_epa"] = m.groupby("posteam").epa.mean()
        off[f"{nm}_sr"] = m.groupby("posteam").success.mean()
    off["rz_trips_pg"] = rzd.groupby("posteam").size() / off.g
    off["rz_td_pct"] = rzd.groupby("posteam").touchdown.mean()
    off["turnovers"] = (p[p.posteam.notna()].groupby("posteam").interception.sum() + p[p.posteam.notna()].groupby("posteam").fumble_lost.sum()) / off.g

    dfn = tw.groupby("opponent_team").agg(g=("week", "nunique"), pass_att=("attempts", "mean"), pass_yds=("passing_yards", "mean"), pass_td=("passing_tds", "mean"), rush_att=("carries", "mean"),
                                         rush_yds=("rushing_yards", "mean"), rush_td=("rushing_tds", "mean"), sacks=("sacks_suffered", "mean"), ints=("passing_interceptions", "mean"))
    dfn["pts_allowed"] = sc.groupby("opp").pf.mean()
    dfn["td_allowed_pg"] = dfn.pass_td + dfn.rush_td
    for nm, m in (("pass", pl[pl["pass"] == 1]), ("rush", pl[pl["rush"] == 1])):
        dfn[f"{nm}_epa_allowed"] = m.groupby("defteam").epa.mean()
        dfn[f"{nm}_sr_allowed"] = m.groupby("defteam").success.mean()
    dfn["rz_td_pct_allowed"] = rz.groupby(["defteam", "game_id", "drive"]).touchdown.max().reset_index().groupby("defteam").touchdown.mean()
    dfn["takeaways"] = (p[p.defteam.notna()].groupby("defteam").interception.sum() + p[p.defteam.notna()].groupby("defteam").fumble_lost.sum()) / dfn.g

    # defense vs position (what each defense allowed to each position group, per game)
    pw = pd.read_parquet(NFLV + f"stats_player_week_{season}.parquet"); pw = pw[(pw.season_type == "REG") & (pw.week <= through) & pw.position.isin(POS)].copy()
    for c in ("passing_tds", "rushing_tds", "receiving_tds", "receptions", "receiving_yards", "rushing_yards", "passing_yards", "targets", "carries", "fantasy_points_ppr"):
        pw[c] = pd.to_numeric(pw[c], errors="coerce").fillna(0)
    pw["tds"] = pw.passing_tds + pw.rushing_tds + pw.receiving_tds
    ng = pw.groupby("opponent_team").week.nunique()
    d = pw.groupby(["opponent_team", "position"]).agg(rec=("receptions", "sum"), rec_yds=("receiving_yards", "sum"), tgt=("targets", "sum"), rush_yds=("rushing_yards", "sum"), car=("carries", "sum"),
                                                      pass_yds=("passing_yards", "sum"), rush_td=("rushing_tds", "sum"), rec_td=("receiving_tds", "sum"), pass_td=("passing_tds", "sum"),
                                                      tds=("tds", "sum"), ppr=("fantasy_points_ppr", "sum")).reset_index()
    d["g"] = d.opponent_team.map(ng)
    for c in ("rec", "rec_yds", "tgt", "rush_yds", "car", "pass_yds", "rush_td", "rec_td", "pass_td", "tds", "ppr"):
        d[c + "_pg"] = d[c] / d.g
    d["league_td_pts_pg"] = 6 * d.tds_pg
    d["td_rank"] = d.groupby("position").tds_pg.rank(ascending=False, method="min")
    d["ppr_rank"] = d.groupby("position").ppr_pg.rank(ascending=False, method="min")
    d = d.rename(columns={"opponent_team": "defense", "position": "pos"})

    for df, higher_better in ((off, True),):
        for c in ("pts", "pass_yds", "rush_yds", "td_per_g", "pass_epa", "rush_epa", "rz_td_pct", "plays"):
            off[c + "_rk"] = off[c].rank(ascending=not higher_better, method="min")
    for c in ("pts_allowed", "pass_yds", "rush_yds", "td_allowed_pg", "pass_epa_allowed", "rush_epa_allowed", "rz_td_pct_allowed"):
        dfn[c + "_rk"] = dfn[c].rank(ascending=False, method="min")     # 1 = allows the most

    # week-N matchups from the schedule lines
    wk = g[g.week == target_week]
    rows = []
    for r in wk.itertuples():
        for tm, op, home in ((r.away_team, r.home_team, False), (r.home_team, r.away_team, True)):
            imp = (r.total_line - r.spread_line) / 2 if tm == r.away_team else (r.total_line + r.spread_line) / 2
            row = dict(week=target_week, team=tm, opp=op, home=home, implied_pts=imp, total=r.total_line, spread_for_team=(r.spread_line if tm == r.away_team else -r.spread_line))
            for pos in POS:
                x = d[(d.defense == op) & (d.pos == pos)]
                if len(x):
                    row[f"opp_{pos}_td_rk"] = int(x.td_rank.iloc[0]); row[f"opp_{pos}_ppr_rk"] = int(x.ppr_rank.iloc[0]); row[f"opp_{pos}_td_pg"] = round(float(x.tds_pg.iloc[0]), 2)
            rows.append(row)
    mu = pd.DataFrame(rows)
    return off.round(3), dfn.round(3), d.round(3), mu.round(2)


def main(season=2026, through=None, out=None):
    through = through or int(os.environ.get("APEX_THROUGH_WEEK", 5))
    out = out or OUT
    off, dfn, d, mu = build(season, through)
    os.makedirs(out, exist_ok=True)
    off.to_csv(os.path.join(out, "team_offense.csv")); dfn.to_csv(os.path.join(out, "team_defense.csv")); d.to_csv(os.path.join(out, "dvp.csv"), index=False); mu.to_csv(os.path.join(out, "matchups.csv"), index=False)
    print(f"offense {off.shape}, defense {dfn.shape}, dvp {d.shape}, matchups {mu.shape} -> {out}")
    return off, dfn, d, mu


def advanced(season=2026, through=5):
    """Pro Football Reference advanced stats (nflverse `pfr_advstats` mirror of the PFR advanced tabs) aggregated to team level, per game.
    Defense: coverage allowed (cmp%, yds/tgt, rating, ADOT, YAC), pass rush (pressures, hurries, QB hits, sacks, blitzes) and tackling. Offense: pressure, bad-throw and drop rates, yards before and after contact.
    pro-football-reference.com itself serves a bot challenge (HTTP 403), so this uses the nflverse copy of the same data."""
    def rd(name):
        d = pd.read_parquet(NFLV + f"advstats_week_{name}_{season}.parquet")
        return d[(d.game_type == "REG") & (d.week <= through)].copy()
    df = rd("def")
    for c in df.columns:
        if c.startswith("def_") and df[c].dtype == object:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.fillna({c: 0 for c in df.columns if c.startswith("def_")})
    g = df.groupby("team")
    n = g.week.nunique()
    out = pd.DataFrame({"g": n})
    t = g.def_targets.sum(); cmp_ = g.def_completions_allowed.sum()
    out["tgt_pg"] = t / n; out["cmp_pct_allowed"] = cmp_ / t.replace(0, np.nan)
    out["yds_pg"] = g.def_yards_allowed.sum() / n; out["yds_per_tgt"] = g.def_yards_allowed.sum() / t.replace(0, np.nan)
    out["td_allowed_pg"] = g.def_receiving_td_allowed.sum() / n; out["ints_pg"] = g.def_ints.sum() / n
    out["adot_allowed"] = (df.def_adot * df.def_targets).groupby(df.team).sum() / t.replace(0, np.nan)
    out["yac_pg"] = g.def_yards_after_catch.sum() / n
    out["rating_allowed"] = (df.def_passer_rating_allowed * df.def_targets).groupby(df.team).sum() / t.replace(0, np.nan)
    out["pressures_pg"] = g.def_pressures.sum() / n; out["hurries_pg"] = g.def_times_hurried.sum() / n; out["qb_hits_pg"] = g.def_times_hitqb.sum() / n
    out["sacks_pg"] = g.def_sacks.sum() / n; out["blitzes_pg"] = g.def_times_blitzed.sum() / n
    tk = g.def_tackles_combined.sum(); mt = g.def_missed_tackles.sum()
    out["missed_tackle_pct"] = mt / (tk + mt).replace(0, np.nan)
    for c in ("cmp_pct_allowed", "yds_per_tgt", "rating_allowed", "td_allowed_pg"):
        out[c + "_rk"] = out[c].rank(ascending=False, method="min")        # 1 = allows the most
    for c in ("pressures_pg", "sacks_pg", "blitzes_pg"):
        out[c + "_rk"] = out[c].rank(ascending=False, method="min")        # 1 = most
    # offense: pass protection / QB, drops, run-game contact
    ps, ru, rc = rd("pass"), rd("rush"), rd("rec")
    off = pd.DataFrame(index=sorted(set(ps.team) | set(ru.team)))
    pg = ps.groupby("team"); pn = pg.week.nunique()
    off["g"] = pn
    for c in ("passing_drops", "passing_bad_throws", "times_pressured", "times_sacked", "times_blitzed"):
        ps[c] = pd.to_numeric(ps[c], errors="coerce").fillna(0)
    pg = ps.groupby("team")
    off["pressured_pg"] = pg.times_pressured.sum() / pn; off["sacked_pg"] = pg.times_sacked.sum() / pn; off["blitzed_pg"] = pg.times_blitzed.sum() / pn
    off["bad_throws_pg"] = pg.passing_bad_throws.sum() / pn; off["drops_pg"] = pg.passing_drops.sum() / pn
    off["pressure_rate"] = (ps.times_pressured * ps.get("times_pressured_pct", 1).notna()).groupby(ps.team).sum()      # placeholder replaced below
    team_att = pd.read_parquet(NFLV + f"stats_team_week_{season}.parquet"); team_att = team_att[(team_att.season_type == "REG") & (team_att.week <= through)].groupby("team").agg(db=("attempts", "sum"), sk=("sacks_suffered", "sum"))
    off["pressure_rate"] = pg.times_pressured.sum() / (team_att.db + team_att.sk)
    off["bad_throw_rate"] = pg.passing_bad_throws.sum() / team_att.db
    for c in ("carries", "rushing_yards_before_contact", "rushing_yards_after_contact", "rushing_broken_tackles"):
        ru[c] = pd.to_numeric(ru[c], errors="coerce").fillna(0)
    rg = ru.groupby("team"); car = rg.carries.sum()
    off["ybc_per_att"] = rg.rushing_yards_before_contact.sum() / car; off["yac_per_att"] = rg.rushing_yards_after_contact.sum() / car
    off["broken_tackles_pg"] = rg.rushing_broken_tackles.sum() / rg.week.nunique()
    rc["receiving_drop"] = pd.to_numeric(rc["receiving_drop"], errors="coerce").fillna(0)
    off["rec_drops_pg"] = rc.groupby("team").receiving_drop.sum() / rc.groupby("team").week.nunique()
    for c in ("pressure_rate", "bad_throw_rate"):
        off[c + "_rk"] = off[c].rank(ascending=False, method="min")        # 1 = worst (most)
    off["ybc_rk"] = off.ybc_per_att.rank(ascending=False, method="min")    # 1 = best
    return out.round(3), off.drop(columns=["g"]).round(3)


def advanced_main(season=2026, through=None, out=None):
    through = through or int(os.environ.get("APEX_THROUGH_WEEK", 5))
    out = out or OUT
    d, o = advanced(season, through)
    os.makedirs(out, exist_ok=True)
    d.to_csv(os.path.join(out, "adv_defense.csv")); o.to_csv(os.path.join(out, "adv_offense.csv"))
    print(f"advanced defense {d.shape}, offense {o.shape} -> {out}")
    return d, o


if __name__ == "__main__":
    a = sys.argv[1:]
    main(int(a[0]) if a else 2026, int(a[1]) if len(a) > 1 else None, a[2] if len(a) > 2 else None)
    advanced_main(int(a[0]) if a else 2026, int(a[1]) if len(a) > 1 else None, a[2] if len(a) > 2 else None)
