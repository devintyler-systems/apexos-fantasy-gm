"""Parse Sharp Football Analysis Week-11 odds/props PDFs (operator intake D039-D045) into the Odds-API-style
workbook that engine/weekly/price_odds.py reads. Rows are rebuilt from word coordinates, never text order.

python tools/intake/parse_market_pdfs.py OUT.xlsx [--snapshot-et "2026-11-18 14:27"]
- Book columns from the page header (CONSENSUS is derived, written to a separate sheet, never priced as a book).
- "—" = book not offering; that cell is skipped.
- Timestamps written in US Pacific (PST after 2026-11-01): run price_odds.py with APEX_ODDS_TZ_OFFSET=8.
- Output is operator market data: write it under var/ only (never committed).
Validation sheet `check` lists counts per doc/market; spot-check values against the page image before use.
"""
import argparse, collections, glob, re
from pathlib import Path
import pandas as pd, pymupdf

ROOT = Path(__file__).resolve().parents[2]
ORIG = ROOT / "var/intake_2026_w09_w11/originals"
NICK = {"Cardinals": "Arizona Cardinals", "Falcons": "Atlanta Falcons", "Ravens": "Baltimore Ravens", "Bills": "Buffalo Bills", "Panthers": "Carolina Panthers",
        "Bears": "Chicago Bears", "Bengals": "Cincinnati Bengals", "Browns": "Cleveland Browns", "Cowboys": "Dallas Cowboys", "Broncos": "Denver Broncos",
        "Lions": "Detroit Lions", "Packers": "Green Bay Packers", "Texans": "Houston Texans", "Colts": "Indianapolis Colts", "Jaguars": "Jacksonville Jaguars",
        "Chiefs": "Kansas City Chiefs", "Raiders": "Las Vegas Raiders", "Chargers": "Los Angeles Chargers", "Rams": "Los Angeles Rams", "Dolphins": "Miami Dolphins",
        "Vikings": "Minnesota Vikings", "Patriots": "New England Patriots", "Saints": "New Orleans Saints", "Giants": "New York Giants", "Jets": "New York Jets",
        "Eagles": "Philadelphia Eagles", "Steelers": "Pittsburgh Steelers", "49ers": "San Francisco 49ers", "Seahawks": "Seattle Seahawks",
        "Buccaneers": "Tampa Bay Buccaneers", "Titans": "Tennessee Titans", "Commanders": "Washington Commanders"}
ABBR = {"ARI": "Arizona Cardinals", "ATL": "Atlanta Falcons", "BAL": "Baltimore Ravens", "BUF": "Buffalo Bills", "CAR": "Carolina Panthers", "CHI": "Chicago Bears",
        "CIN": "Cincinnati Bengals", "CLE": "Cleveland Browns", "DAL": "Dallas Cowboys", "DEN": "Denver Broncos", "DET": "Detroit Lions", "GB": "Green Bay Packers",
        "HOU": "Houston Texans", "IND": "Indianapolis Colts", "JAX": "Jacksonville Jaguars", "KC": "Kansas City Chiefs", "LV": "Las Vegas Raiders",
        "LAC": "Los Angeles Chargers", "LAR": "Los Angeles Rams", "LA": "Los Angeles Rams", "MIA": "Miami Dolphins", "MIN": "Minnesota Vikings", "NE": "New England Patriots",
        "NO": "New Orleans Saints", "NYG": "New York Giants", "NYJ": "New York Jets", "PHI": "Philadelphia Eagles", "PIT": "Pittsburgh Steelers", "SF": "San Francisco 49ers",
        "SEA": "Seattle Seahawks", "TB": "Tampa Bay Buccaneers", "TEN": "Tennessee Titans", "WAS": "Washington Commanders", "WSH": "Washington Commanders"}
BOOKS = {"CONSEN…": "consensus", "CONSENSUS": "consensus", "DRAFTKINGS": "draftkings", "FANDUEL": "fanduel", "BETMGM": "betmgm", "FANATICS": "fanatics", "CAESARS": "williamhill_us"}
DROPPED = []
NUM = re.compile(r"^[+-]?\d+(\.\d+)?$")
PROPS = {"QB-PASSING": "player_pass_yds", "REC YDS": "player_reception_yds", "RUSH YDS": "player_rush_yds", "ANYTIME TD": "player_anytime_td",
         "Passing": "player_pass_yds", "Receiving": "player_reception_yds", "Rushing": "player_rush_yds", "Touchdowns": "player_anytime_td", "AnytimeTD": "player_anytime_td"}
GAMES = {"MONEYLINE": "h2h", "SPREADS": "spreads", "TOTAL.pdf": "totals"}


def words(page):
    return [(round(x0), (y0 + y1) / 2, w) for x0, y0, x1, y1, w, *_ in page.get_text("words")]


def header_cols(doc):
    for page in doc:
        hdr = [(x, y, w) for x, y, w in words(page) if w in BOOKS]
        if len(hdr) >= 4:
            return sorted((x, BOOKS[w]) for x, _, w in hdr), max(y for _, y, _ in hdr)
    raise SystemExit("no book header")


def col_of(x, cols):
    c = [b for hx, b in cols if hx <= x + 22]
    return c[-1] if c else None


def all_words(path, hdr_y):
    """Every page in one coordinate space, stacked by CONTENT extent (page margins removed) so a block split by a
    page break has the same internal spacing as any other block."""
    out, off = [], 0.0
    for pn, page in enumerate(pymupdf.open(path)):
        ws = [t for t in words(page) if not (pn == 0 and t[1] <= hdr_y + 8)]
        if not ws:
            continue
        top, bot = min(y for _, y, _ in ws), max(y for _, y, _ in ws)
        out += [(x, y - top + off, w) for x, y, w in ws]
        off += (bot - top) + 9.0      # ~one text line between the last word of a page and the first of the next
    return out


def cluster_lines(ws, tol=3.0):
    """Group words into text lines: a word joins a line if its centre is within tol px (glyphs like '·' sit a fraction higher)."""
    lines = []
    for x, y, w in sorted(ws, key=lambda t: t[1]):
        if lines and abs(y - lines[-1][0]) <= tol:
            lines[-1][1].append((x, w))
        else:
            lines.append([y, [(x, w)]])
    return {round(y): toks for y, toks in lines}


def blocks(ws, anchors):
    anchors = sorted(anchors, key=lambda a: a[0])
    out = []
    for i, (y, info) in enumerate(anchors):
        gap_prev = (y - anchors[i - 1][0]) if i else (anchors[1][0] - y if len(anchors) > 1 else 60)
        gap_next = (anchors[i + 1][0] - y) if i + 1 < len(anchors) else gap_prev
        lo = y - gap_prev / 2 if i else -1e9
        hi = y + gap_next / 2 if i + 1 < len(anchors) else 1e12
        out.append((info, [(x, yy, w) for x, yy, w in ws if lo <= yy < hi]))
    return out


def parse_props(path, market, cols, hdr_y):
    rows = []
    for pn in (0,):
        ws = all_words(path, hdr_y)
        lines = cluster_lines(ws)
        anchors = []
        for y, toks in sorted(lines.items()):
            toks.sort(); left = [w for x, w in toks if x < 140]
            if len(left) >= 3 and left[1] == "·" and left[0] in ("QB", "RB", "WR", "TE", "FB") and left[2] in ABBR:
                anchors.append((y, (left[0], left[2])))
        for (ay, (pos, team)), b in zip(sorted(anchors, key=lambda a: a[0]), [bb for _, bb in blocks(ws, anchors)]):
            name_rows = cluster_lines([(x, y, w) for x, y, w in b if x < 140])
            name, m = None, None
            for y in sorted((y for y in name_rows if y < ay - 2), reverse=True):      # nearest name line ABOVE the anchor
                t = [w for _, w in sorted(name_rows[y])]
                if t and t[0] not in ("vs", "@", "BEST", pos) and "·" not in t and not NUM.match(t[0]):
                    name = " ".join(t); break
            for y in sorted(y for y in name_rows if y > ay + 2):                      # nearest opponent line BELOW the anchor
                t = " ".join(w for _, w in sorted(name_rows[y]))
                if t.startswith(("vs ", "@ ")):
                    m = re.match(r"(vs|@)\s+(\w+)", t); break
            if not name or not m:
                DROPPED.append((path.name, pos, team, name, round(ay)))
                continue
            opp = m.group(2); home, away = (team, opp) if m.group(1) == "vs" else (opp, team)
            marks = sorted((y, w) for x, y, w in b if w in ("O", "U") and 150 < x < 200)
            cells = collections.defaultdict(lambda: collections.defaultdict(list))
            for x, y, w in b:
                if x < 150 or not NUM.match(w):
                    continue
                if market == "player_anytime_td":
                    side = "Yes"
                else:      # side = nearest O/U marker at or above this number (markers sit on the line-value row)
                    above = [w for my, w in marks if my <= y + 4]
                    if not above:
                        continue
                    side = "Over" if above[-1] == "O" else "Under"
                cells[col_of(x, cols)][side].append((y, float(w)))
            for book, sides in cells.items():
                for side, vals in sides.items():
                    vals.sort()
                    if market == "player_anytime_td":
                        price = [v for _, v in vals if abs(v) >= 100]; point = None
                    else:
                        point = [v for _, v in vals if abs(v) < 100 or (abs(v) >= 100 and "." in str(v) and v % 1)]
                        price = [v for _, v in vals if abs(v) >= 100 and v not in point]
                        point = point[0] if point else None
                    if not price:
                        continue
                    rows.append(dict(src=path.name, page=None, bookmaker=book, market=market, label=side, description=name, team=team, pos=pos,
                                     home=home, away=away, price=price[0], point=point))
    return rows


def parse_games(path, market, cols, hdr_y):
    rows = []
    for pn in (0,):
        ws = all_words(path, hdr_y)
        anchors = [(y, w) for x, y, w in ws if x < 70 and w in NICK]
        bl = blocks(ws, anchors)
        for i in range(0, len(bl) - 1, 2):
            (away_n, ba), (home_n, bh) = bl[i], bl[i + 1]
            for team_n, b in ((away_n, ba), (home_n, bh)):
                cells = collections.defaultdict(list)
                for x, y, w in b:
                    if x >= 140 and NUM.match(w):
                        cells[col_of(x, cols)].append((y, float(w)))
                for book, vals in cells.items():
                    vals.sort(); v = [z for _, z in vals]
                    if market == "h2h":
                        price, point, label = v[0], None, NICK[team_n]
                    elif market == "spreads":
                        pts = [z for z in v if abs(z) < 60]; prs = [z for z in v if abs(z) >= 100]
                        if not pts or not prs:
                            continue
                        price, point, label = prs[0], pts[0], NICK[team_n]
                    else:
                        pts = [z for z in v if 20 < abs(z) < 90]; prs = [z for z in v if abs(z) >= 100]
                        if not pts or not prs:
                            continue
                        price, point, label = prs[0], pts[0], ("Over" if team_n == away_n else "Under")
                    rows.append(dict(src=path.name, page=None, bookmaker=book, market=market, label=label, description=None,
                                     home=NICK[home_n], away=NICK[away_n], price=price, point=point))
    return rows


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("out"); ap.add_argument("--snapshot-et", default="2026-11-18 14:27")
    ap.add_argument("--orig", default=str(ORIG), help="folder holding exactly one PDF per market (default: intake originals)")
    ap.add_argument("--schedule", default=str(ROOT / "docs/weekly/intake_2026_w09_w11/schedule_w09_w11.csv")); a = ap.parse_args()
    rows = []
    for key, mk in {**PROPS, **GAMES}.items():
        f = [Path(p) for p in glob.glob(str(Path(a.orig) / f"*{key}*"))]
        if not f:
            print(f"{key}: no file in {a.orig}, market skipped"); continue
        if len(f) != 1:
            raise SystemExit(f"{key}: expected 1 file, got {len(f)}")
        cols, hy = header_cols(pymupdf.open(f[0]))
        rows += (parse_props if mk.startswith("player") else parse_games)(f[0], mk, cols, hy)
    d = pd.DataFrame(rows)
    d["home_team"] = d.home.map(lambda t: ABBR.get(t, t)); d["away_team"] = d.away.map(lambda t: ABBR.get(t, t))
    sc = pd.read_csv(a.schedule); sc = sc[sc.week == 11]
    sc["home_team"] = sc.home.map(ABBR); sc["away_team"] = sc.away.map(ABBR)
    ko = {(r.away_team, r.home_team): pd.Timestamp(r.kickoff_utc).tz_localize(None) - pd.Timedelta(hours=8) for r in sc.itertuples()}
    d["commence_time"] = [ko.get((x, y)) for x, y in zip(d.away_team, d.home_team)]
    snap_pt = pd.Timestamp(a.snapshot_et) - pd.Timedelta(hours=3)        # ET -> PT (both standard time)
    d["last_update"] = snap_pt
    d["game_id"] = d.away_team.str.split().str[-1] + "@" + d.home_team.str.split().str[-1]
    bad = d[d.commence_time.isna()]
    books = d[d.bookmaker != "consensus"]
    cols = ["game_id", "commence_time", "bookmaker", "last_update", "home_team", "away_team", "market", "label", "description", "price", "point"]
    chk = d.groupby(["src", "market", "bookmaker"]).size().unstack(fill_value=0)
    books[cols].to_excel(a.out, sheet_name="Sheet1", index=False)      # price_odds.py reads EVERY sheet: odds only here
    with pd.ExcelWriter(a.out.replace(".xlsx", "_reference.xlsx")) as xw:
        d[d.bookmaker == "consensus"][cols + ["team", "pos", "page"]].to_excel(xw, sheet_name="consensus_reference", index=False)
        chk.to_excel(xw, sheet_name="check")
        bad.to_excel(xw, sheet_name="unmatched_game", index=False)
    print("dropped anchors:", DROPPED); print(chk.to_string()); print("rows to price:", len(books), "| unmatched game rows:", len(bad), "| players:", d.description.nunique())


if __name__ == "__main__":
    main()
