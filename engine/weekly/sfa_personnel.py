"""Sharp Football Analysis play-level offensive personnel (2021-2026), decoded from the compact JSON the site's own stats page loads.

Source: https://rmsummerlin.github.io/SFAStatsPages/data/personnel_grouping_{season}.json (index lists the seasons). One row per run or dropback: team, week, quarter, down, distance, field zone,
score margin, yards, EPA, success, dropback flag and the RB/TE/WR counts on the field. No player names. 2026 is updated through the latest completed week. Cached under the nflverse cache dir (never committed).
Usage: python sfa_personnel.py [SEASON ...]   -> downloads and prints a one-line check per season.
"""
import json
import os
import sys

import httpx
import numpy as np
import pandas as pd

from paths import NFLV

BASE = "https://rmsummerlin.github.io/SFAStatsPages/data/"


def fetch(season):
    path = os.path.join(NFLV, f"sfa_personnel_{season}.json")
    r = httpx.get(BASE + f"personnel_grouping_{season}.json", timeout=120, follow_redirects=True)
    r.raise_for_status()
    open(path, "w").write(r.text)
    return path


def decode(path):
    d=json.load(open(path)); al=d["alphabet"]; inv={c:i for i,c in enumerate(al)}; B=len(al); n=d["plays"]
    col=lambda s: np.array([inv[c] for c in s],dtype=np.int64)
    pair=lambda hi,lo,off: col(hi)*B+col(lo)-off
    pers=np.array(d["pers"]); pi=col(d["cols"]["p"]); v=pers[pi]
    df=pd.DataFrame(dict(team=np.array(d["teams"])[col(d["cols"]["t"])], week=col(d["cols"]["w"]), qtr=col(d["cols"]["q"]), down=col(d["cols"]["d"]), dist=col(d["cols"]["n"]),
        zone=col(d["cols"]["z"]), dropback=col(d["cols"]["b"]), rb=v//100, te=(v//10)%10, wr=v%10, margin=pair(d["cols"]["mh"],d["cols"]["ml"],d["margin_offset"]),
        yds=pair(d["cols"]["yh"],d["cols"]["yl"],d["yds_offset"]), epa=pair(d["cols"]["eh"],d["cols"]["el"],d["epa_offset"])/d["epa_scale"], success=col(d["cols"]["sc"])))
    df["season"]=d["season"]; return df


if __name__ == "__main__":
    for y in [int(a) for a in sys.argv[1:]] or [2026]:
        df = decode(fetch(y)); c = df[df.team == "CHI"]
        print(y, f"{len(df)} plays, weeks {df.week.min()}-{df.week.max()}, CHI 11-personnel {((c.rb == 1) & (c.te == 1)).mean():.1%}, dropback rate {df.dropback.mean():.1%}")
