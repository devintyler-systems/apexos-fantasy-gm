"""R-24 (DECISIONS #73, owner-approved 2026-11-24, provisional): players on reserve with a designated-for-return roster code who are listed Questionable are not hard-zeroed.

2026 W11: five players were RES on the Sunday roster and Questionable on the Friday report (Brooks CAR, Pittman PIT, R. Wilson PIT, Shipley PHI, Croskey-Merritt WAS). The engine forced all five Out;
three played (Wilson 49 snaps, Croskey-Merritt 28, Shipley 19). Roster history is too sparse to backtest, so this is a flat provisional probability (APEX_R48_P, default 0.5; 'off' restores the hard Out)
and every week's outcomes go to docs/weekly/r48_log.csv for a later refit.

exempt_keys(roster_rows, injury_rows): {(nkey, team): (game_status, practice)} for roster rows with status RES and code R48 that also appear on the injury report as Questionable with
any practice status. Out, Doubtful, a different reserve code, or no report row all stay Out. Practice status is not a condition: in W11 Shipley was DNP and played 19 snaps, while Brooks and Pittman
practiced fully and did not play."""
import os

CODE = "R48"


def prob():
    v = os.environ.get("APEX_R48_P", "0.5")
    return None if str(v).lower() in ("off", "none", "") else float(v)


def exempt_keys(r, o):
    """r: roster rows (nkey, team, status, status_description_abbr); o: injury frame from build_inj (nkey, team, game_status, practice)."""
    if prob() is None or "status_description_abbr" not in r:
        return {}
    res = r[(r.status == "RES") & (r.status_description_abbr == CODE)]
    keys = set(zip(res.nkey, res.team))
    out = {}
    for row in o.itertuples():
        k = (row.nkey, row.team)
        if k in keys and row.game_status == "Questionable":
            out[k] = (row.game_status, getattr(row, "practice", ""))
    return out
