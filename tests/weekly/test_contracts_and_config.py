import glob
import json
import os
import re

import pandas as pd
import yaml

from conftest import ROOT, WEEKLY

CONF = os.path.join(ROOT, "config", "weekly")


def test_weekly_contracts_parse():
    files = glob.glob(os.path.join(ROOT, "contracts", "weekly", "*.yaml"))
    assert len(files) >= 4
    for f in files:
        d = yaml.safe_load(open(f))
        assert d["contract"].startswith("weekly_") and "contract_version" in d


def test_availability_tables_are_probabilities_and_ordered():
    for name in ("availability_by_status.csv", "availability_by_status_pos.csv"):
        df = pd.read_csv(os.path.join(CONF, name), keep_default_na=False)
        num = df.select_dtypes("number")
        for c in [c for c in num.columns if c in ("p_parent", "p")]:
            assert df[c].between(0, 1).all(), (name, c)
    root = pd.read_csv(os.path.join(CONF, "availability_by_status.csv"), keep_default_na=False)
    s = root.groupby("rs").apply(lambda g: g["sum"].sum() / g["size"].sum())
    if {"Doubtful", "Questionable"} <= set(s.index):
        assert s["Doubtful"] < s["Questionable"]


def test_calibration_params_schema():
    cal = json.load(open(os.path.join(CONF, "calibration_params.json")))
    for k in ("qb_share", "qb_td", "team_ypc", "other_tgt", "other_car", "share_mult"):
        assert k in cal
    assert 0.5 < cal["qb_share"] <= 1.0 and 0.5 < cal["qb_td"] <= 1.0
    for v in cal["share_mult"].values():
        assert 0.5 < v < 2.0


def test_fit_files_present_and_valid_json():
    for n in ("team_prior_fit", "player_prior_fit", "calibration", "weather_effects", "opportunity_fit"):
        json.load(open(os.path.join(CONF, n + ".json")))
    tp = json.load(open(os.path.join(CONF, "team_prior_fit.json")))
    assert 0 <= tp["market_weight"] <= 1


def test_no_hardcoded_machine_paths_or_secrets():
    pat_path = re.compile(r"/home/user|/root/\.claude|C:\\\\")
    pat_secret = re.compile(r"(sk-ant-[A-Za-z0-9]|AKIA[0-9A-Z]{12}|ghp_[A-Za-z0-9]{20}|api[_-]?key\s*=\s*['\"][A-Za-z0-9]{16})")
    for f in glob.glob(os.path.join(WEEKLY, "*")):
        if os.path.isfile(f):
            txt = open(f, encoding="utf-8", errors="ignore").read()
            assert not pat_path.search(txt), f
            assert not pat_secret.search(txt), f


def test_weekly_package_does_not_import_draft_engine():
    for f in glob.glob(os.path.join(WEEKLY, "*.py")):
        txt = open(f).read()
        assert not re.search(r"^\s*(from|import)\s+engine\.(draft|canonical|ingestion|recommendation|projections)", txt, re.M), f


def test_projection_stages_never_read_book_lines():
    for f in ("run_all.py", "sim.py", "params.py", "prep_nv.py", "projections_report.py", "build_projection_tables.py"):
        txt = open(os.path.join(WEEKLY, f)).read()
        assert "props_lines" not in txt and "odds_american" not in txt, f
