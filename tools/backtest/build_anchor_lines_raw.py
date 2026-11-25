"""Anchor-lines CSV straight from Odds API historical jsons, through the engine's own workbook parser (anchor.lines_from_rows), for the #91 live-equivalence check.

  python tools/backtest/build_anchor_lines_raw.py OUT.csv --games-from var/odds_hist/t2h DIR [DIR ...]
Every json in each DIR (non-recursive) whose game_id is in --games-from is flattened to the price_odds.py schema and parsed exactly as a live workbook would be:
main line by most books, two-way de-vig per book, anytime TD de-vigged with config/weekly/td_book_devig.json. Odds data stays in var/ and is never committed.
"""
import glob, json, os, sys
import pandas as pd

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(REPO, "engine", "weekly"))
import anchor  # noqa: E402

a = sys.argv[1:]; out = a[0]; i = a.index("--games-from"); keep_dir = a[i + 1]; dirs = a[1:i] + a[i + 2:]
keep = {os.path.basename(f)[:-5] for f in glob.glob(os.path.join(keep_dir, "*.json"))}
rows = []
for d in dirs:
    for f in sorted(glob.glob(os.path.join(d, "*.json"))):
        j = json.load(open(f)); gid = j["game_id"]
        if gid not in keep: continue
        ev = j.get("data") or {}
        for b in ev.get("bookmakers", []):
            for mk in b.get("markets", []):
                for o in mk.get("outcomes", []):
                    rows.append(dict(game_id=gid, bookmaker=b["key"], home_team=ev["home_team"], away_team=ev["away_team"], market=mk["key"], label=o["name"],
                                     description=o.get("description"), price=o["price"], point=o.get("point")))
R = pd.DataFrame(rows)
L = anchor.lines_from_rows(R)
gm = R.drop_duplicates("game_id").assign(away=lambda x: x.away_team.map(anchor.NICK), home=lambda x: x.home_team.map(anchor.NICK))
gm["season"] = gm.game_id.str[:4].astype(int); gm["week"] = gm.game_id.str[5:7].astype(int)
L = L.merge(gm[["away", "home", "season", "week"]], on=["away", "home"])
L[["season", "week", "away", "home", "nkey", "market", "line", "p"]].to_csv(out, index=False)
print(out, len(L), "lines;", L.market.value_counts().to_dict(), "games", L.groupby(["away", "home"]).ngroups)
