"""O-3: operator odds upload -> priced touchdown board in one command (ROADMAP O-3).

python tools/intake/price_upload.py <folder or zip of Sharp odds/props PDFs> --track market|model --week 12 [--keep-stale]

1. Copies the PDFs into var/odds_w<week>/<stamp>/ (never committed) and reads each page's "updated <Day> <h:mm> <AM|PM> ET" stamp.
2. Prints the age of every file against the real clock (never pinned) and the 2-hour rule verdict BEFORE pricing.
3. Parses them (parse_market_pdfs.py, snapshot = the OLDEST stamp, so no file is treated as fresher than it is).
4. Prices against the finished run in var/out_<track> with price_odds.py, passing APEX_MANUAL_OUT and APEX_STATUS_OVERLAY through
   (price_odds re-simulates each game; DECISIONS #67) and APEX_ODDS_TZ_OFFSET (8 after the November clock change).
Stale rows are excluded by price_odds unless --keep-stale (reference only, never plays).
"""
import argparse, datetime as dt, os, re, shutil, subprocess, sys, zipfile
from pathlib import Path
from zoneinfo import ZoneInfo

import pymupdf

ROOT = Path(__file__).resolve().parents[2]
ET = ZoneInfo("America/New_York")
STAMP = re.compile(r"updated\s+(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\w*,?\s+(?:(\d{1,2})/(\d{1,2}),?\s+)?(\d{1,2}):(\d{2})\s*(AM|PM)\s*ET", re.I)
DOW = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
MARKET_KEYS = ("ANYTIME TD", "PASSING YARDS", "RECEIVING YARDS", "RUSHING YARDS", "MONEYLINE", "SPREAD", "TOTAL")


def stamp_of(pdf, now_et):
    txt = " ".join(p.get_text() for p in pymupdf.open(pdf))
    m = STAMP.search(txt)
    if not m:
        return None
    day, mo, dd, hh, mm, ap = m.groups()
    h = int(hh) % 12 + (12 if ap.upper() == "PM" else 0)
    if mo and dd:
        d = dt.date(now_et.year, int(mo), int(dd))
    else:      # day name only: the most recent such day on or before today
        back = (now_et.weekday() - DOW.index(day.lower()[:3])) % 7
        d = (now_et - dt.timedelta(days=back)).date()
    t = dt.datetime(d.year, d.month, d.day, h, int(mm), tzinfo=ET)
    return t if t <= now_et else t - dt.timedelta(days=7)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("src"); ap.add_argument("--track", default="market"); ap.add_argument("--week", type=int, required=True)
    ap.add_argument("--season", type=int, default=2026); ap.add_argument("--keep-stale", action="store_true"); a = ap.parse_args()
    now = dt.datetime.now(dt.timezone.utc); now_et = now.astimezone(ET)
    dest = ROOT / f"var/odds_w{a.week:02d}" / now.strftime("%Y%m%dT%H%MZ"); dest.mkdir(parents=True, exist_ok=True)
    src = Path(a.src)
    if src.suffix == ".zip":
        with zipfile.ZipFile(src) as z:
            for n in z.namelist():
                if n.lower().endswith(".pdf") and any(k in n.upper() for k in MARKET_KEYS):
                    (dest / Path(n).name).write_bytes(z.read(n))
    else:
        for f in src.glob("*.pdf"):
            if any(k in f.name.upper() for k in MARKET_KEYS):
                shutil.copy2(f, dest / f.name)
    files = sorted(dest.glob("*.pdf"))
    if not files:
        raise SystemExit(f"no odds/props PDFs found in {src}")
    stamps = {}
    print(f"now {now:%Y-%m-%d %H:%MZ} ({now_et:%a %I:%M %p} ET)")
    for f in files:
        s = stamp_of(f, now_et); stamps[f] = s
        age = (now_et - s).total_seconds() / 3600 if s else None
        print(f"  {'NO STAMP' if s is None else s.strftime('%a %m/%d %I:%M %p ET')}  age {'?' if age is None else f'{age:5.2f} h'}  {'STALE' if age is None or age > 2 else 'fresh'}  {f.name}")
    known = [s for s in stamps.values() if s]
    if not known:
        raise SystemExit("no updated-stamp found on any file: cannot price (never assume a time)")
    oldest = min(known)
    fresh_for = 2 - (now_et - oldest).total_seconds() / 3600
    print(f"oldest stamp {oldest:%a %I:%M %p ET}; " + (f"fresh for {fresh_for * 60:.0f} more minutes" if fresh_for > 0 else f"STALE by {-fresh_for:.2f} h: every row is excluded from plays"))
    xlsx = dest / "sharp_upload.xlsx"
    py = sys.executable
    sched = ROOT / f"docs/weekly/w{a.week:02d}/schedule_w{a.week:02d}.csv"
    subprocess.run([py, "-I", str(ROOT / "tools/intake/parse_market_pdfs.py"), str(xlsx), "--snapshot-et", oldest.strftime("%Y-%m-%d %H:%M"), "--orig", str(dest),
                    "--schedule", str(sched), "--week", str(a.week)], check=True)
    env = dict(os.environ, APEX_ODDS_XLSX=str(xlsx), APEX_ENV=a.track, APEX_SEASON=str(a.season), APEX_TARGET_WEEK=str(a.week), APEX_THROUGH_WEEK=str(a.week - 1),
               APEX_OUT=str(ROOT / f"var/out_{a.track}"), APEX_ODDS_TZ_OFFSET=os.environ.get("APEX_ODDS_TZ_OFFSET", "8"))
    env.pop("APEX_NOW_UTC", None)      # never pinned (DECISIONS #67)
    if a.keep_stale:
        env["APEX_ODDS_KEEP_STALE"] = "1"
    for k in ("APEX_MANUAL_OUT", "APEX_STATUS_OVERLAY"):
        print(f"{k}={env.get(k, '(not set: price_odds re-simulates WITHOUT it; set it to the run value)')}")
    subprocess.run([py, "price_odds.py"], cwd=ROOT / "engine/weekly", env=env, check=True)
    print(f"priced -> {env['APEX_OUT']}/edges_all_rows.csv (odds stay under var/, never committed)")


if __name__ == "__main__":
    main()
