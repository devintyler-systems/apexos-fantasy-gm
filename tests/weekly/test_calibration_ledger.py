import pandas as pd

import calibration_ledger as L


def test_ledger_rows_aggregate_and_replace_a_week(tmp_path):
    d = pd.DataFrame(dict(market=["rec", "rec", "rush_yds"], model_p=[.62, .66, .81], hit=[1, 0, 1], gap=[.05, .12, .3]))
    r = L.ledger_rows(d, 7, "screen_50")
    assert r[(r.market == "rec") & (r.bucket_type == "raw")].n.sum() == 2 and int(r.hits.sum()) == 4      # raw + gap tables each count the two hits and the third line's hit
    p = tmp_path / "l.csv"; L.append(p, r); L.append(p, r)
    assert len(pd.read_csv(p)) == len(r)      # re-running a week replaces, not duplicates
