"""Pre-build DraftKings pool audit (DECISIONS #93): every DK player who could score must be in our simulations.

A player is REQUIRED when his DK status is not OUT/IR/O and: a DST always; a K with any DK average (a second kicker with 0.0 is not);
a QB only if he is QB1 on the current depth chart (backups score only through the engine's in-sim backup draw); anyone else with AvgPointsPerGame >= 3.
A required player missing from the sims is a POOL GAP and blocks the lineup build (W12 GB@LA: LA's kicker McManus was
missing because the engine labelled the punter as kicker; he scored 17). Players zeroed on purpose by the manual-out
file (practice squad / not on the roster) are listed as explained, not as gaps. APEX_ALLOW_POOL_GAP=1 overrides (logged).
"""
import os
import pandas as pd

from load import norm_name

TM = {"LAR": "LA", "JAC": "JAX", "WSH": "WAS"}


def _qb1():
    try:
        import params
        q = params._DC_QB; return {(n, t) for n, t, r in zip(q.nkey, q.team, q.pos_rank) if int(r) == 1}
    except Exception:
        return None


def audit(sal, present, manual_out=None, qb1=None):
    """sal: DK salary frame; present: set of (nkey, team) keys (DST keyed by the DK name's nkey). Returns (gaps, explained) frames."""
    s = sal.copy()
    s["team"] = s.TeamAbbrev.replace(TM); s["nkey"] = s.Name.map(norm_name)
    if "Roster Position" in s:
        s = s[~s["Roster Position"].isin(["CPT"])]
    s = s.drop_duplicates(["nkey", "team"])
    st = s.Status.fillna("").astype(str).str.upper()
    avg = pd.to_numeric(s.AvgPointsPerGame, errors="coerce").fillna(0)
    qb1 = _qb1() if qb1 is None else qb1
    is_qb1 = pd.Series([qb1 is None or (a, b) in qb1 for a, b in zip(s.nkey, s.team)], index=s.index)
    elig = (s.Position == "DST") | ((s.Position == "K") & (avg > 0)) | ((s.Position == "QB") & is_qb1) | (~s.Position.isin(["DST", "K", "QB"]) & (avg >= 3))
    req = ~st.isin(["OUT", "IR", "O"]) & elig
    miss = s[req & ~pd.Series([(a, b) in present for a, b in zip(s.nkey, s.team)], index=s.index)]
    mo = set()
    if manual_out and os.path.exists(manual_out):
        m = pd.read_csv(manual_out, keep_default_na=False); mo = set(zip(m.player.map(norm_name), m.team.replace(TM)))
    expl = miss[pd.Series([(a, b) in mo for a, b in zip(miss.nkey, miss.team)], index=miss.index, dtype=bool)]
    gaps = miss.drop(expl.index)
    return gaps[["Name", "Position", "team", "Salary", "AvgPointsPerGame", "Status"]], expl[["Name", "Position", "team", "Salary", "AvgPointsPerGame", "Status"]]


def enforce(sal, present, label=""):
    gaps, expl = audit(sal, present, os.environ.get("APEX_MANUAL_OUT"))
    if len(expl):
        print(f"[pool audit {label}] zeroed by manual-out (explained): " + ", ".join(f"{r.Name} {r.team}" for r in expl.itertuples()))
    if len(gaps):
        print(f"[pool audit {label}] POOL GAP: {len(gaps)} DK player(s) who can score are missing from the simulations:\n" + gaps.to_string(index=False))
        if os.environ.get("APEX_ALLOW_POOL_GAP") != "1":
            raise SystemExit("pool audit failed: fix the mapping (kicker/DST/name/team) or rerun with APEX_ALLOW_POOL_GAP=1 and say why")
        print("[pool audit] APEX_ALLOW_POOL_GAP=1: continuing with the gap(s) above")
    else:
        print(f"[pool audit {label}] OK: every scoring-eligible DK player is in the simulations")
    return gaps
