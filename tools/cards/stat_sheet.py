"""Shareable single-game stat sheet (PNG) from a finished engine run. Reads engine outputs only; never book prices.

python tools/cards/stat_sheet.py RUN_OUT_DIR AWAY HOME OUT_HTML [--label TEXT] [--players-json FILE] [--notes-html FILE]
  RUN_OUT_DIR  folder holding proj_all.pkl, w4_td_markets.csv, w4_game_environment.csv, w4_game_props.csv
  players-json {"HOU": [names in order], "IND": [...]}; default: per team, players with >= 1.5 projected points by anytime TD/volume
Render the HTML with Playwright (see the render step in the W11 TNF notes). Percentages round half up.
"""
import argparse, html, json, math
from pathlib import Path
import pandas as pd

TEAM = {"ARI": "ARIZONA CARDINALS", "ATL": "ATLANTA FALCONS", "BAL": "BALTIMORE RAVENS", "BUF": "BUFFALO BILLS", "CAR": "CAROLINA PANTHERS",
        "CHI": "CHICAGO BEARS", "CIN": "CINCINNATI BENGALS", "CLE": "CLEVELAND BROWNS", "DAL": "DALLAS COWBOYS", "DEN": "DENVER BRONCOS",
        "DET": "DETROIT LIONS", "GB": "GREEN BAY PACKERS", "HOU": "HOUSTON TEXANS", "IND": "INDIANAPOLIS COLTS", "JAX": "JACKSONVILLE JAGUARS",
        "KC": "KANSAS CITY CHIEFS", "LV": "LAS VEGAS RAIDERS", "LAC": "LOS ANGELES CHARGERS", "LA": "LOS ANGELES RAMS", "MIA": "MIAMI DOLPHINS",
        "MIN": "MINNESOTA VIKINGS", "NE": "NEW ENGLAND PATRIOTS", "NO": "NEW ORLEANS SAINTS", "NYG": "NEW YORK GIANTS", "NYJ": "NEW YORK JETS",
        "PHI": "PHILADELPHIA EAGLES", "PIT": "PITTSBURGH STEELERS", "SF": "SAN FRANCISCO 49ERS", "SEA": "SEATTLE SEAHAWKS", "TB": "TAMPA BAY BUCCANEERS",
        "TEN": "TENNESSEE TITANS", "WAS": "WASHINGTON COMMANDERS"}


def pct(p):  # half-up integer percent
    return int(math.floor(p * 100 + 0.5))


def fair(p):
    if p <= 0:
        return "–"
    return f"{-100 * p / (1 - p):.0f}" if p >= 0.5 else f"+{100 * (1 - p) / p:.0f}"


def num(x, n=0):
    return "–" if pd.isna(x) else (f"{int(math.floor(x + 0.5))}" if n == 0 else f"{x:.{n}f}")


def rng(a, b):
    return "" if pd.isna(a) or (a == 0 and b == 0) else f"<span class='r'>{num(a)}–{num(b)}</span>"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run"); ap.add_argument("away"); ap.add_argument("home"); ap.add_argument("out")
    ap.add_argument("--label", default="ENGINE AVERAGE"); ap.add_argument("--players-json"); ap.add_argument("--notes-html", default="")
    ap.add_argument("--footer", default=""); ap.add_argument("--subtitle", default="FULL STAT PROJECTIONS")
    ap.add_argument("--kick", default=""); ap.add_argument("--css-from", required=True)
    a = ap.parse_args()
    R = Path(a.run); game = f"{a.away}@{a.home}"
    P = pd.read_pickle(R / "proj_all.pkl"); P = P[P.game == game].set_index("player")
    T = pd.read_csv(R / "w4_td_markets.csv"); T = T[T.game == game].pivot_table(index="player", columns="market", values="prob")
    P = P.join(T[["anytime_td", "first_td", "2plus_td"]], how="left")
    G = pd.read_csv(R / "w4_game_environment.csv"); g = G[(G.away == a.away) & (G.home == a.home)].iloc[0]
    GP = pd.read_csv(R / "w4_game_props.csv"); GP = GP[GP.game == game]
    gp = lambda c, m: float(GP[(GP.category == c) & (GP.market == m)].prob.iloc[0])
    order = json.loads(Path(a.players_json).read_text()) if a.players_json else None
    notes = Path(a.notes_html).read_text() if a.notes_html else ""
    sup = json.loads(Path(a.players_json).read_text()).get("_notes", {}) if a.players_json else {}
    rows = {}
    for t in (a.home, a.away):
        names = order[t] if order else P[P.team == t].sort_values("anytime_td", ascending=False).head(8).index.tolist()
        h = ""
        for p in names:
            r = P.loc[p]; tag = f"<sup>{sup[p]}</sup>" if p in sup else ""
            ps_ = (f"<b>{num(r.pass_yds_mean)}</b> yds {rng(r.pass_yds_p25, r.pass_yds_p75)}<em>{num(r.pass_cmp_mean, 1)} comp · {num(r.pass_td_mean, 1)} TD</em>"
                   if r.pos == "QB" else "<span class='dash'>–</span>")
            ru = (f"<b>{num(r.rush_yds_mean)}</b> yds {rng(r.rush_yds_p25, r.rush_yds_p75)}<em>{num(r.rush_att_mean, 1)} att</em>"
                  if r.rush_att_mean >= 1 else "<span class='dash'>–</span>")
            rc = (f"<b>{num(r.rec_yds_mean)}</b> yds {rng(r.rec_yds_p25, r.rec_yds_p75)}<em>{num(r.tgt_mean, 1)} tgt · {num(r.rec_mean, 1)} rec</em>"
                  if r.pos != "QB" and r.tgt_mean >= 1 else "<span class='dash'>–</span>")
            at = r.anytime_td; w = min(at / 0.5, 1) * 100
            h += (f"<tr><td class='pl'>{html.escape(p)}{tag}<em>{r.pos}</em></td><td>{ps_}</td><td>{ru}</td><td>{rc}</td>"
                  f"<td class='atd'><div class='bw'><div class='b' style='width:{w:.0f}%'></div></div><b>{pct(at)}%</b><em>fair {fair(at)}</em></td>"
                  f"<td class='c'><b>{pct(r.first_td)}%</b><em>{fair(r.first_td)}</em></td><td class='c'><b>{pct(r['2plus_td'])}%</b></td></tr>")
        rows[t] = h
    css_src = Path(a.css_from).read_text(); css = css_src[css_src.index("<style>") + 7:css_src.index("</style>")]
    hp, ap_ = g[f"{a.home}_pts_mean"], g[f"{a.away}_pts_mean"]
    fav = a.home if g.mean_margin_home > 0 else a.away; mg = abs(g.mean_margin_home)
    head = '<tr><th>PLAYER</th><th>PASSING</th><th>RUSHING</th><th>RECEIVING</th><th>ANYTIME TD</th><th class="c">FIRST TD</th><th class="c">2+ TD</th></tr>'
    first_team = a.home if gp("first_team_to_score", a.home) >= 0.5 else a.away
    out = f"""<!doctype html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet"><style>{css}
.st td{{padding:9px 10px;font-size:13.5px}} .st th{{padding:9px 10px}}
.st b{{font-family:Oswald;font-weight:600;font-size:18px;color:#fff;letter-spacing:.3px}}
.st em{{display:block;font-style:normal;font-size:11.3px;color:var(--mut);margin-top:1px}}
.st .r{{font-size:11.3px;color:var(--gold2);margin-left:4px}}
.st .pl{{font-weight:700;color:#fff;font-size:14.5px;width:170px}} .st .pl em{{font-weight:600;letter-spacing:1px}}
.st sup{{color:var(--gold2);font-size:10px;margin-left:2px}}
.st .dash{{color:#4c628f}} .st .c{{text-align:center}}
.st .atd{{width:175px}} .bw{{height:7px;background:rgba(255,255,255,.07);border-radius:5px;margin-bottom:4px;overflow:hidden}} .b{{height:100%;background:linear-gradient(90deg,#c9932a,#ffd76a)}}
.st .atd b{{color:var(--gold2)}} .st .atd em{{display:inline;margin-left:6px}}
.team{{font-family:Oswald;font-weight:700;letter-spacing:2px;font-size:15px;color:var(--gold2);background:rgba(242,193,78,.08);padding:7px 12px;border-bottom:1px solid var(--line)}}
.fn{{margin-top:14px;font-size:11.5px;color:#d6e0fb;line-height:1.55;border:1.5px solid var(--line);border-radius:12px;padding:10px 14px;background:rgba(10,26,64,.7)}}
.fn b{{color:var(--gold2)}}
</style></head><body><div class="wrap">
<div class="top"><div class="brand">DEEPDISH × APEX<small>{a.subtitle}</small></div>
<div class="game"><div class="m">{TEAM[a.away].split()[-1]} @ {TEAM[a.home].split()[-1]}</div><div class="s">{a.kick}</div></div></div>
<div class="score">
 <div class="k"><div class="l">PROJECTED SCORE</div><div class="v">{a.home} {num(hp)} – {a.away} {num(ap_)}</div><div class="x">{hp:.1f} – {ap_:.1f}</div></div>
 <div class="k"><div class="l">MARGIN</div><div class="v">{fav} {mg:.1f}</div><div class="x">median {abs(g.median_margin_home):.0f}</div></div>
 <div class="k"><div class="l">TOTAL</div><div class="v">{g.total_mean:.1f}</div><div class="x">range {num(g.total_p25)}–{num(g.total_p75)}</div></div>
 <div class="k"><div class="l">{a.home} WIN</div><div class="v">{pct(g.home_win_prob)}%</div><div class="x">{a.away} {pct(g.away_win_prob)}%</div></div>
 <div class="k"><div class="l">FIRST TO SCORE</div><div class="v">{first_team} {pct(gp('first_team_to_score', first_team))}%</div><div class="x">first score FG {pct(gp('first_scoring_play','FG'))}% · TD {pct(gp('first_scoring_play','TD'))}%</div></div>
</div>
<div class="card"><h2>PLAYER PROJECTIONS <span>· {a.label} · <span style="color:var(--gold2)">25th–75th percentile range</span></span></h2>
<table class="st">{head}<tr><td colspan="7" class="team">{TEAM[a.home]} · {hp:.1f} PTS</td></tr>{rows[a.home]}<tr><td colspan="7" class="team">{TEAM[a.away]} · {ap_:.1f} PTS</td></tr>{rows[a.away]}</table></div>
{('<div class="fn">' + notes + '</div>') if notes else ''}
<div class="foot"><div class="tl">FRESH LINES. DEEP READS.</div><div class="d">{a.footer}</div></div>
</div></body></html>"""
    Path(a.out).write_text(out); print("wrote", a.out)


if __name__ == "__main__":
    main()
