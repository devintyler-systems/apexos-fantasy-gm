"""DECISIONS #91: market-anchored player draws (engine/weekly/anchor.py, APEX_ANCHOR_XLSX)."""
import numpy as np
import pandas as pd
import pytest

import anchor

N = 4000


def _pl(name, pos, rec_yds, rush_yds, pass_yds=0.0, td_p=0.3, seed=0):
    r = np.random.default_rng(seed)
    act = r.random(N) < 0.95
    def draw(mu):
        x = np.where(r.random(N) < 0.85, r.gamma(2.0, mu / 2.0, N), 0.0) if mu > 0 else np.zeros(N)
        return np.where(act, np.round(x), 0.0)
    td = np.where(act, (r.random(N) < td_p).astype(float), 0.0)
    pl = dict(player=name, pos=pos, mask=act, p_active=float(act.mean()), rec=np.zeros(N), rec_yds=draw(rec_yds), rush_yds=draw(rush_yds),
              rush_att=np.zeros(N), pass_yds=draw(pass_yds), rec_td=td * (pos in ("WR", "TE")), rush_td=td * (pos not in ("WR", "TE")))
    pl["fp"] = 0.1 * (pl["rec_yds"] + pl["rush_yds"]) + 0.04 * pl["pass_yds"] + 6 * (pl["rec_td"] + pl["rush_td"])
    return pl


def _game():
    return {"AAA": [_pl("Quinn Back", "QB", 0, 20, 240, 0.1, 1), _pl("Rob Runner", "RB", 15, 60, 0, 0.4, 2),
                    _pl("Will Wide", "WR", 70, 0, 0, 0.35, 3), _pl("Ted Tight", "TE", 30, 0, 0, 0.2, 4)],
            "BBB": [_pl("Other Guy", "WR", 50, 0, 0, 0.3, 5)]}


def _lines(tmp_path, monkeypatch, rows):
    f = tmp_path / "lines.csv"
    pd.DataFrame(rows, columns=["season", "week", "away", "home", "nkey", "market", "line", "p"]).to_csv(f, index=False)
    monkeypatch.setenv("APEX_ANCHOR_XLSX", str(f)); monkeypatch.setenv("APEX_SEASON", "2025"); monkeypatch.setenv("APEX_TARGET_WEEK", "6")
    anchor._CACHE.clear()


def test_off_and_no_lines_leave_draws_untouched(tmp_path, monkeypatch):
    monkeypatch.delenv("APEX_ANCHOR_XLSX", raising=False); anchor._CACHE.clear()
    g = _game(); ref = {k: [dict(p) for p in v] for k, v in g.items()}
    assert anchor.apply(g, "AAA", "BBB") == 0
    _lines(tmp_path, monkeypatch, [(2025, 6, "XXX", "YYY", "will wide", "rec_yds", 60.5, 0.5)])   # lines for another game only
    assert anchor.apply(g, "AAA", "BBB") == 0
    for t in g:
        for a, b in zip(g[t], ref[t]):
            for k in ("rec_yds", "rush_yds", "pass_yds", "rec_td", "rush_td", "fp"):
                assert np.array_equal(a[k], b[k])


def test_yardage_and_td_hit_the_market_probability(tmp_path, monkeypatch):
    _lines(tmp_path, monkeypatch, [(2025, 6, "AAA", "BBB", "will wide", "rec_yds", 80.5, 0.45), (2025, 6, "AAA", "BBB", "will wide", "anytime_td", np.nan, 0.50),
                                   (2025, 6, "AAA", "BBB", "rob runner", "anytime_td", np.nan, 0.25)])
    g = _game(); anchor.apply(g, "AAA", "BBB")
    w = g["AAA"][2]; m = w["mask"]
    assert (w["rec_yds"][m] > 80.5).mean() == pytest.approx(0.45, abs=0.01)
    assert (w["rec_yds"] >= 0).all() and np.array_equal(w["rec_yds"][m] == 0, w["raw"]["rec_yds"][m] == 0)   # 0-yard games stay 0
    assert ((w["rec_td"] + w["rush_td"])[m] >= 1).mean() == pytest.approx(0.50, abs=0.02)
    r = g["AAA"][1]; assert ((r["rec_td"] + r["rush_td"])[r["mask"]] >= 1).mean() == pytest.approx(0.25, abs=0.02)
    assert {"rec_yds", "anytime_td"} <= w["anchored"]
    assert np.allclose(w["fp"] - w["raw"]["fp"], 0.1 * (w["rec_yds"] - w["raw"]["rec_yds"]) + 6 * ((w["rec_td"] + w["rush_td"]) - (w["raw"]["rec_td"] + w["raw"]["rush_td"])))
    assert not g["BBB"][0].get("anchored")                                     # other team has no lines: unchanged


def test_lineless_rush_rescale_counts_an_unanchored_qb_as_fixed(tmp_path, monkeypatch):
    """team rushing total is held; the QB's own (unanchored) rushing must not be pushed onto the free rushers."""
    _lines(tmp_path, monkeypatch, [(2025, 6, "AAA", "BBB", "will wide", "rec_yds", 60.5, 0.5)])
    g = _game()
    tot = lambda pls, k: sum(float(p[k][p["mask"]].mean()) * p["p_active"] for p in pls)
    r0 = tot(g["AAA"], "rush_yds"); anchor.apply(g, "AAA", "BBB")
    assert tot(g["AAA"], "rush_yds") == pytest.approx(r0, rel=1e-9)            # nothing anchored on rushing: factor 1, untouched
    assert "rush_yds_team" not in g["AAA"][1].get("anchored", ())
