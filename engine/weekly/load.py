"""APEX-OS Week 4 loader: parse sportsref HTML-xls, odds xlsx, injury PDF text.
Team convention follows apexos-fantasy-gm weekly_export.TEAM_SLUG_TO_ABBR (nflverse abbrs: LA, GB, KC, LV, NE, NO, SF, TB, WAS).
"""
from paths import OUT, NFLV, DELIV, CONF
import glob, os, re, io, warnings
import pandas as pd, numpy as np
from lxml import html as LH
warnings.filterwarnings("ignore")
U = os.environ.get("APEX_INPUTS", "inputs/").rstrip("/") + "/"   # operator-supplied files (odds workbook, legacy sportsref); never committed
OUT = OUT

FULL2ABBR = {
 "Arizona Cardinals":"ARI","Atlanta Falcons":"ATL","Baltimore Ravens":"BAL","Buffalo Bills":"BUF","Carolina Panthers":"CAR",
 "Chicago Bears":"CHI","Cincinnati Bengals":"CIN","Cleveland Browns":"CLE","Dallas Cowboys":"DAL","Denver Broncos":"DEN",
 "Detroit Lions":"DET","Green Bay Packers":"GB","Houston Texans":"HOU","Indianapolis Colts":"IND","Jacksonville Jaguars":"JAX",
 "Kansas City Chiefs":"KC","Los Angeles Rams":"LA","Los Angeles Chargers":"LAC","Las Vegas Raiders":"LV","Miami Dolphins":"MIA",
 "Minnesota Vikings":"MIN","New England Patriots":"NE","New Orleans Saints":"NO","New York Giants":"NYG","New York Jets":"NYJ",
 "Philadelphia Eagles":"PHI","Pittsburgh Steelers":"PIT","Seattle Seahawks":"SEA","San Francisco 49ers":"SF",
 "Tampa Bay Buccaneers":"TB","Tennessee Titans":"TEN","Washington Commanders":"WAS"}
PFR2ABBR = {"GNB":"GB","KAN":"KC","LAR":"LA","LVR":"LV","NOR":"NO","NWE":"NE","SFO":"SF","TAM":"TB","OAK":"LV","SDG":"LAC","STL":"LA"}
NICK2ABBR = {"Cardinals":"ARI","Falcons":"ATL","Ravens":"BAL","Bills":"BUF","Panthers":"CAR","Bears":"CHI","Bengals":"CIN","Browns":"CLE",
 "Cowboys":"DAL","Broncos":"DEN","Lions":"DET","Packers":"GB","Texans":"HOU","Colts":"IND","Jaguars":"JAX","Chiefs":"KC","Rams":"LA",
 "Chargers":"LAC","Raiders":"LV","Dolphins":"MIA","Vikings":"MIN","Patriots":"NE","Saints":"NO","Giants":"NYG","Jets":"NYJ","Eagles":"PHI",
 "Steelers":"PIT","Seahawks":"SEA","49ers":"SF","Buccaneers":"TB","Titans":"TEN","Commanders":"WAS"}

def abbr(x):
    if x is None or (isinstance(x,float) and np.isnan(x)): return None
    x=str(x).strip()
    return FULL2ABBR.get(x) or PFR2ABBR.get(x) or NICK2ABBR.get(x) or x

def norm_name(s):
    s=str(s).replace("*","").replace("+","").strip()
    s=re.sub(r"[.’']","",s).lower()
    s=re.sub(r"\b(jr|sr|ii|iii|iv|v)\b","",s)
    return re.sub(r"\s+"," ",s).strip()

def _flat(cols): return [c[1] if isinstance(c,tuple) else c for c in cols]

def read_sr(key, with_ids=False):
    f = glob.glob(U+f"*sportsref_download_{key}_week4.xls")[0]
    raw = open(f,encoding="utf-8",errors="ignore").read()
    t = pd.read_html(io.StringIO(raw))[0]
    # disambiguate duplicate column names with group prefix
    cols=[]; seen={}
    for c in t.columns:
        g,n = (c if isinstance(c,tuple) else ("",c))
        g = "" if str(g).startswith("Unnamed") else str(g)
        cols.append((g+"_"+str(n)) if g else str(n))
    t.columns=cols
    if with_ids:
        doc = LH.fromstring(raw)
        ids=[]
        for tr in doc.xpath("//table//tbody/tr"):
            if "thead" in (tr.get("class") or ""): continue
            a = tr.xpath(".//*[@data-append-csv]/@data-append-csv")
            ids.append(a[0] if a else None)
        if len(ids)==len(t): t["pfr_id"]=ids
    return t

def num(df, skip=()):
    for c in df.columns:
        if c in skip: continue
        df[c]=pd.to_numeric(df[c],errors="ignore") if df[c].dtype==object else df[c]
    return df

def clean_player(t, namecol="Player", teamcol="Team"):
    t=t[t[namecol].notna()].copy()
    t=t[~t[namecol].astype(str).isin([namecol,"Player"])]
    t[namecol]=t[namecol].astype(str).str.replace(r"[*+]","",regex=True).str.strip()
    t["team"]=t[teamcol].map(abbr)
    t["nkey"]=t[namecol].map(norm_name)
    return t

# -------- injury report --------
POS = {"QB","RB","WR","TE","T","G","C","OL","DT","DE","DL","LB","OLB","ILB","CB","S","FS","SS","K","P","LS","NT","EDGE","FB","DB"}
PRAC = ["Did Not Participate In Practice","Limited Participation in Practice","Full Participation in Practice"]
def parse_injury(path=None):
    txt = open(path or OUT+"injury_raw.txt").read().splitlines()
    rows=[]; game=None; team=None; date=None; time=None; sched=[]
    mre = re.compile(r"^(?:[A-Z0-9]+ )?\((\d+-\d+(?:-\d+)?)\) (\S+) (\S+) \((\d+-\d+(?:-\d+)?)\)$")
    dre = re.compile(r"^(THURSDAY|SUNDAY|MONDAY|FRIDAY|SATURDAY), ([A-Z]+ \d+)")
    tre = re.compile(r"^(\d+:\d+ ?[AP]M) ?EDT")
    for ln in txt:
        ln=ln.strip()
        if m:=dre.match(ln): date=m.group(2).title(); continue
        if m:=tre.match(ln): time=m.group(1); continue
        if m:=mre.match(ln):
            if m.group(2) in NICK2ABBR and m.group(3) in NICK2ABBR:
                game=(NICK2ABBR[m.group(2)],NICK2ABBR[m.group(3)]); team=None
                sched.append(dict(away=game[0],home=game[1],date=date,time_edt=time,away_rec=m.group(1),home_rec=m.group(4))); continue
        if ln in NICK2ABBR and game: team=NICK2ABBR[ln]; continue
        if ln.startswith("Player Position Injuries"): continue
        if game and team:
            toks=ln.split()
            idx=next((i for i,t in enumerate(toks) if t in POS and i>=2),None)
            if idx is None: continue
            name=" ".join(toks[:idx]); pos=toks[idx]; rest=" ".join(toks[idx+1:])
            prac=next((p for p in PRAC if p in rest),None)
            if prac is None:
                m2=re.search(r"\b(Out|Doubtful|Questionable)$",rest)
                if not m2: continue
                pre,gs,pk=rest[:m2.start()].strip(),m2.group(1),"NONE"
            else:
                pre,post=rest.split(prac,1); gs=post.strip() or None; pk={"Did":"DNP","Lim":"LP","Ful":"FP"}[prac[:3]]
            rows.append(dict(player=name,pos=pos,team=team,opp=game[1] if team==game[0] else game[0],injury=pre.strip() or None,
                             practice=pk,game_status=gs,nkey=norm_name(name)))
    return pd.DataFrame(rows), pd.DataFrame(sched)

if __name__=="__main__":
    inj,sch=parse_injury()
    print(sch.to_string()); print(len(inj)); print(inj.game_status.value_counts(dropna=False))
