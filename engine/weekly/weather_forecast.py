"""Kickoff weather for the target week from the National Weather Service hourly forecast (api.weather.gov; Open-Meteo is not reachable from the cloud container).

Writes OUT/w4_weather_forecast.csv (the name params.py reads): game, roof, wind_mph, gust_mph, temp_f, precip_pct, total_adj_pts, note. total_adj_pts uses config/weekly/weather_effects.json
(fitted by weather.py on 2016-25 closing totals). It moves the MODEL-ONLY track's game total; the market-anchored track is pinned to the line, which already includes the weather.
Indoor/closed roofs, neutral-site games outside the US and games whose forecast fails are written with a note and no adjustment (never a guess).
Usage: APEX_SEASON=2026 APEX_TARGET_WEEK=7 python weather_forecast.py
"""
import ast
import json
import os
import re
import time
from zoneinfo import ZoneInfo

import httpx
import pandas as pd

from paths import CONF, NFLV, OUT

SEASON = int(os.environ.get("APEX_SEASON", 2026)); WEEK = int(os.environ.get("APEX_TARGET_WEEK", 7))
H = {"User-Agent": "apex-weekly (github.com/devintyler-systems/apexos-fantasy-gm)"}
STAD = {"ARI": (33.528, -112.263), "ATL": (33.755, -84.401), "BAL": (39.278, -76.623), "BUF": (42.774, -78.787), "CAR": (35.226, -80.853), "CHI": (41.862, -87.617), "CIN": (39.095, -84.516),
        "CLE": (41.506, -81.699), "DAL": (32.748, -97.093), "DEN": (39.744, -105.020), "DET": (42.340, -83.046), "GB": (44.501, -88.062), "HOU": (29.685, -95.411), "IND": (39.760, -86.164),
        "JAX": (30.324, -81.637), "KC": (39.049, -94.484), "LA": (33.953, -118.339), "LAC": (33.953, -118.339), "LV": (36.091, -115.184), "MIA": (25.958, -80.239), "MIN": (44.974, -93.258),
        "NE": (42.091, -71.264), "NO": (29.951, -90.081), "NYG": (40.813, -74.074), "NYJ": (40.813, -74.074), "PHI": (39.901, -75.168), "PIT": (40.447, -80.016), "SEA": (47.595, -122.332),
        "SF": (37.403, -121.970), "TB": (27.976, -82.503), "TEN": (36.166, -86.771), "WAS": (38.908, -76.864)}      # home stadium lat/lon (weather.py's table is partial and has WAS in London)
INDOOR = {"ARI", "ATL", "DAL", "DET", "HOU", "IND", "LV", "MIN", "NO", "LA", "LAC"}      # domes, retractable roofs and the SoFi canopy: wind and cold do not reach the field
EFF = json.load(open(CONF + "weather_effects.json"))


DOWN = False      # circuit breaker: if the first game's forecast cannot be fetched the service is treated as down and the rest are skipped (no long retry loops in CI)


def get(url, tries=2):
    if DOWN:
        return None
    for i in range(tries):
        try:
            r = httpx.get(url, headers=H, timeout=20, follow_redirects=True)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
        time.sleep(2 + 3 * i)
    return None


def mph(s):
    n = [float(x) for x in re.findall(r"\d+", s or "")]
    return max(n) if n else float("nan")      # "5 to 10 mph" -> 10 (the upper bound: a windy-side forecast)


g = pd.read_parquet(NFLV + "games.parquet"); g = g[(g.season == SEASON) & (g.week == WEEK)]
rows = []
for r in g.itertuples():
    k = f"{r.away_team}@{r.home_team}"; roof = r.roof if isinstance(r.roof, str) else ""
    if roof in ("dome", "closed") or r.home_team in INDOOR:
        rows.append(dict(game=k, roof=roof, note="indoor")); continue
    if str(getattr(r, "location", "")).lower() == "neutral" or r.home_team not in STAD:
        rows.append(dict(game=k, roof=roof, note="neutral site or unknown stadium: no forecast, no adjustment")); continue
    lat, lon = STAD[r.home_team]
    pt = get(f"https://api.weather.gov/points/{lat},{lon}")
    fc = get(pt["properties"]["forecastHourly"]) if pt else None
    if not fc:
        DOWN = True
        rows.append(dict(game=k, roof=roof, note="forecast unavailable: no adjustment")); continue
    hh, mm = map(int, str(r.gametime).split(":")); ko = pd.Timestamp(f"{r.gameday} {hh:02d}:{mm:02d}", tz=ZoneInfo("America/New_York")).tz_convert("UTC")
    per = fc["properties"]["periods"]
    best = min(per, key=lambda p: abs((pd.Timestamp(p["startTime"]).tz_convert("UTC") - (ko + pd.Timedelta(hours=1))).total_seconds()))      # mid-game hour
    if abs((pd.Timestamp(best["startTime"]).tz_convert("UTC") - ko).total_seconds()) > 6 * 3600:
        rows.append(dict(game=k, roof=roof, note="kickoff outside the 7-day forecast: no adjustment")); continue
    w = mph(best["windSpeed"]); t = float(best["temperature"]); pp = (best.get("probabilityOfPrecipitation") or {}).get("value")
    adj = EFF["wind_per_mph_over10"] * max(w - 10, 0) + EFF["cold_per_deg_below40"] * max(40 - t, 0)
    rows.append(dict(game=k, roof=roof, wind_mph=round(w, 1), gust_mph=float("nan"), temp_f=round(t, 1), precip_pct=pp, total_adj_pts=round(adj, 2), note="NWS hourly, mid-game hour"))
W = pd.DataFrame(rows); W.to_csv(OUT + "w4_weather_forecast.csv", index=False); print(W.to_string(index=False))
