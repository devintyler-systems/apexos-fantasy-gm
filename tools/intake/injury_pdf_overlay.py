"""Build an APEX_STATUS_OVERLAY csv from the operator's Sharp 'NFL Injury Report ... Practice Reports, All 32 Teams' PDF text.
python tools/intake/injury_pdf_overlay.py TEXT_FILE OUT_CSV --as-of 2026-11-21T00:50Z --source "D052 ..."
Records end with OUT / DOUBTFUL / QUESTIONABLE / No designation; the team comes from the week roster (unique name match).
Ambiguous or unmatched names are listed, never guessed. The NFL feed (nflverse) still governs any team it carries (status_overlay.py).
"""
import argparse, re
import pandas as pd

POS = {"QB","RB","FB","WR","TE","T","G","C","OL","OT","OG","DL","DE","DT","NT","LB","ILB","OLB","MLB","CB","S","SS","FS","DB","K","P","LS","EDGE","C/G","G/T"}
NICK = {"Cardinals","Falcons","Ravens","Bills","Panthers","Bears","Bengals","Browns","Cowboys","Broncos","Lions","Packers","Texans","Colts","Jaguars","Chiefs","Raiders","Chargers","Rams","Dolphins","Vikings","Patriots","Saints","Giants","Jets","Eagles","Steelers","49ers","Seahawks","Buccaneers","Titans","Commanders"}
STAT = re.compile(r"\b(OUT|DOUBTFUL|QUESTIONABLE|No designation)\b")


def norm(s):
    s = re.sub(r"[.’']", "", str(s)).lower(); s = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b", "", s); return re.sub(r"\s+", " ", s).strip()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("text"); ap.add_argument("out"); ap.add_argument("--as-of", required=True); ap.add_argument("--source", required=True)
    ap.add_argument("--season", type=int, default=2026); ap.add_argument("--week", type=int, default=11); a = ap.parse_args()
    raw = open(a.text).read()
    raw = re.sub(r"===== PAGE \d+ \[\w+\] =====", " ", raw)
    toks = " ".join(raw.split())
    R = pd.read_parquet(f"var/nflverse/roster_{a.season}.parquet"); R = R[R.week == R.week.max()]
    R["nkey"] = R.full_name.map(norm); byname = R.groupby("nkey").team.agg(lambda x: sorted(set(x)))
    rows, unmatched, pos_ = [], [], 0
    for m in STAT.finditer(toks):
        seg = toks[pos_:m.start()].strip(); pos_ = m.end()
        words = seg.split()
        # name = the run of capitalised words immediately before the first position token in the segment's tail
        idx = None
        for k in range(len(words) - 1, -1, -1):
            if words[k] in POS and k >= 2:
                idx = k
        if idx is None:
            continue
        j = idx; name = []
        while j - 1 >= 0 and re.match(r"^[A-Z0-9][A-Za-z0-9.'\-]*$", words[j - 1]) and len(name) < 4 and words[j - 1] not in ("ET", "PM", "AM", "TOP", "BACK", "LISTED", "WK"):
            name.insert(0, words[j - 1]); j -= 1
            if len(name) >= 2 and (j - 1 < 0 or not re.match(r"^[A-Z][a-z]", words[j - 1])):
                break
        if len(name) < 2:
            continue
        while name and name[0] in NICK:      # a team header ("Lions", "49ers") can run into the first name of the next row
            name = name[1:]
        if len(name) < 2:
            continue
        nm = " ".join(name); status = m.group(1)
        if status == "No designation":
            continue
        teams = byname.get(norm(nm))
        if not teams or len(teams) != 1:
            unmatched.append((nm, words[idx], status, teams)); continue
        rows.append(dict(player=nm, team=teams[0], pos=words[idx], report_status=status.title(), source=a.source, as_of_utc=a.as_of))
    o = pd.DataFrame(rows).drop_duplicates(["player", "team"])
    o.to_csv(a.out, index=False)
    print(f"{len(o)} designations ({o.report_status.value_counts().to_dict()}) across {o.team.nunique()} teams; unmatched/ambiguous: {len(unmatched)}")
    for u in unmatched[:20]:
        print("  unmatched:", u)


if __name__ == "__main__":
    main()
