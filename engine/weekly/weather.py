"""Weather: historical effect on totals (nflverse games, vs the closing total) + Open-Meteo forecast at kickoff for outdoor games."""
from paths import OUT, NFLV, DELIV, CONF
import numpy as np, pandas as pd, requests, json, warnings; warnings.filterwarnings("ignore")
N=NFLV; O=OUT
g=pd.read_parquet(N+"games.parquet"); h=g[(g.game_type=="REG")&(g.season>=2016)&(g.season<=2025)&g.total_line.notna()&g.wind.notna()&g.temp.notna()&g.roof.isin(["outdoors","open"])].copy()
h["res"]=h.total-h.total_line
h["wb"]=pd.cut(h.wind,[-1,9,14,20,60],labels=["<10","10-14","15-20",">20"]); h["tb"]=pd.cut(h.temp,[-50,32,45,60,120],labels=["<=32","33-45","46-60",">60"])
print("games",len(h),"mean residual (actual total - closing total):",round(h.res.mean(),2))
print(h.groupby("wb").res.agg(["mean","count"]).round(2).T.to_string()); print(h.groupby("tb").res.agg(["mean","count"]).round(2).T.to_string())
# simple regression of residual on wind over 10 mph and cold
X=np.c_[np.ones(len(h)),np.clip(h.wind-10,0,None),np.clip(40-h.temp,0,None)]; b=np.linalg.lstsq(X,h.res.values,rcond=None)[0]; print("residual ~ %.2f %+.3f*(wind-10)+ %+.3f*(40-temp)"%tuple(b))
eff={"wind_per_mph_over10":float(b[1]),"cold_per_deg_below40":float(b[2])}
# forecast
STAD={"CLE":(41.506,-81.699),"WAS":(51.604,-0.066),"BAL":(39.278,-76.623),"BUF":(42.774,-78.787),"CHI":(41.862,-87.617),"CIN":(39.095,-84.516),"NYG":(40.813,-74.074),"PHI":(39.901,-75.168),"TB":(27.976,-82.503),"SEA":(47.595,-122.332),"SF":(37.403,-121.970),"CAR":(35.226,-80.853),"HOU":(29.685,-95.411),"MIN":(44.974,-93.258),"LV":(36.091,-115.184),"NO":(29.951,-90.081)}
sch=g[(g.season==2026)&(g.week==4)].copy(); rows=[]; import time
out=[r for r in sch.itertuples() if not ((r.roof if isinstance(r.roof,str) else "") in ("dome","closed")) and r.home_team in STAD]
lats=",".join(str(STAD[r.home_team][0]) for r in out); lons=",".join(str(STAD[r.home_team][1]) for r in out)
u=f"https://api.open-meteo.com/v1/forecast?latitude={lats}&longitude={lons}&hourly=temperature_2m,wind_speed_10m,wind_gusts_10m,precipitation&forecast_days=5&timezone=UTC"
J=None
for _try in range(6):
    try:
        resp=requests.get(u,timeout=60)
        if resp.status_code==200: J=resp.json(); break
        print("status",resp.status_code,resp.text[:80])
    except Exception as e: print("err",str(e)[:60])
    time.sleep(4+4*_try)
J=J if isinstance(J,list) else [J]
fc={}
if J[0] is not None:
    for r,j in zip(out,J):
        hh,mm=map(int,r.gametime.split(":")); ko=pd.Timestamp(f"{r.gameday} {hh:02d}:{mm:02d}")+pd.Timedelta(hours=4)
        hr=j["hourly"]; t=pd.to_datetime(hr["time"]); ix=int(np.argmin(np.abs(t-ko.floor("h"))))
        fc[(r.away_team,r.home_team)]=(hr["wind_speed_10m"][ix]*0.621371,hr["wind_gusts_10m"][ix]*0.621371,hr["temperature_2m"][ix]*9/5+32,hr["precipitation"][ix])
for r in sch.itertuples():
    roof=r.roof if isinstance(r.roof,str) else ""; k=(r.away_team,r.home_team)
    if k in fc:
        w,gu,tf,pr=fc[k]; adj=eff["wind_per_mph_over10"]*max(w-10,0)+eff["cold_per_deg_below40"]*max(40-tf,0)
        rows.append(dict(game=f"{k[0]}@{k[1]}",roof=roof,wind_mph=round(w,1),gust_mph=round(gu,1),temp_f=round(tf,1),precip_mm=pr,total_adj_pts=round(adj,2),note=""))
    else: rows.append(dict(game=f"{k[0]}@{k[1]}",roof=roof or "retractable/unknown",note="indoor/closed or no forecast"))
W=pd.DataFrame(rows); W.to_csv(O+"w4_weather_forecast.csv",index=False); json.dump(eff,open(CONF+"weather_effects.json","w")); print(W.to_string(index=False))
