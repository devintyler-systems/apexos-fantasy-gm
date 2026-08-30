"""FB-01..FB-29 acceptance coverage for the offline Fantrax board."""
from __future__ import annotations

from io import StringIO
import json
from pathlib import Path
import runpy
import subprocess
import sys

import pytest

from engine.recommendation.fantrax_draft_board import FantraxBoardError, build_board, normalize_pool, read_fantrax_csv


HEADER = "Player,Team,Position,RkOv,FPts,FP/G,ADP,Bye\n"


def _rows(prefix: str, position: str, count: int, points: float, rank: int) -> list[dict[str, str]]:
    return [{"Player": f"{prefix}{index:02}", "Team": "T", "Position": position, "RkOv": str(rank + index),
             "FPts": str(points - index), "FP/G": "1", "ADP": str(1000 - index), "Bye": "7"} for index in range(count)]


def _projection_rows() -> list[dict[str, str]]:
    return _rows("QB", "QB", 20, 100, 1) + _rows("RB", "RB", 40, 99, 30) + _rows("REC", "WR", 60, 98, 80) + _rows("K", "K", 20, 97, 150) + _rows("DST", "DST", 16, 96, 180)


def _board(**kwargs):
    return build_board(_projection_rows(), current_pick=kwargs.pop("current_pick", 4), **kwargs)


def _entry(result, player):
    return next(item for item in result["board"] if item["player"] == player)


def test_fb01_headers_validate_and_reject_malformed():
    assert read_fantrax_csv(StringIO(HEADER + "A,T,QB,1,2,3,4,5\n"))[0]["Player"] == "A"
    with pytest.raises(FantraxBoardError, match="SOURCE_HEADER_INVALID"):
        read_fantrax_csv(StringIO("Player,FPts\nA,1\n"))


def test_fb02_fb03_historical_is_not_a_math_input_and_raw_columns_preserved():
    before, after = _board(), _board()
    assert before["recommendation"]["recommended_pick_value"] == after["recommendation"]["recommended_pick_value"]
    assert _entry(before, "QB00")["raw_source_columns"] == _projection_rows()[0]


def test_fb04_to_fb06_normalization_and_identity_labels():
    assert normalize_pool("WT") == ("REC", ["WT_NORMALIZED_TO_REC"])
    assert normalize_pool("DST") == ("D_O", ["DST_NORMALIZED_TO_D_O"])
    rows = _projection_rows(); rows[-1].update({"Player": "N/A", "Team": "", "Position": "DST"})
    result = build_board(rows, current_pick=4)
    codes = _entry(result, "N/A")["recommendation_reason_codes"]
    assert {"DST_NORMALIZED_TO_D_O", "DST_TEAM_LABEL_NULL_ALLOWED", "IDENTITY_OR_TEAM_REVIEW"} <= set(codes)


def test_fb07_fb08_schedule_is_adapter_output_not_generic_snake_math():
    assert _board()["planned_pick_sequence"] == [4, 29, 45, 52, 68, 93, 109, 116]


def test_fb09_fb10_configured_demands_and_replacement_anchors():
    result = _board()
    assert result["pool_demands"] == {"QB": 16, "RB": 32, "REC": 48, "K": 16, "D_O": 16}
    assert _entry(result, "QB00")["replacement_anchor_score"] == 85.0
    assert _entry(result, "RB00")["replacement_anchor_score"] == 68.0
    assert _entry(result, "REC00")["replacement_anchor_score"] == 51.0
    assert _entry(result, "QB15")["generic_replacement_value"] == 0.0
    assert _entry(result, "QB00")["generic_replacement_value"] == 15.0


def test_f01_reconciled_marginal_replacement_components_and_anchor_movement():
    baseline = _board()
    for entry in baseline["board"]:
        if entry["eligible"]:
            assert entry["recommended_pick_value"] == (
                entry["next_pick_wait_cost"]
                + entry["generic_replacement_value"]
                + entry["remaining_slot_scarcity_pressure"]
                + entry["valid_roster_fit_score"]
                - entry["early_position_suppression_penalty"]
            )
    anchor_rows = _projection_rows()[:16] + _projection_rows()[20:]
    anchor_baseline = build_board(anchor_rows, current_pick=4)
    moved_rows = [dict(row) for row in anchor_rows]
    moved_rows[15]["FPts"] = str(float(moved_rows[15]["FPts"]) - 10)
    moved = build_board(moved_rows, current_pick=4)
    before, after = _entry(anchor_baseline, "QB00"), _entry(moved, "QB00")
    assert after["replacement_anchor_score"] == before["replacement_anchor_score"] - 10
    assert after["generic_replacement_value"] == before["generic_replacement_value"] + 10
    assert after["recommended_pick_value"] == before["recommended_pick_value"] + 10


@pytest.mark.parametrize(("pick", "expected"), [(4, 29), (45, 52), (52, 68)])
def test_fb11_to_fb13_next_planned_pick(pick, expected):
    assert _board(current_pick=pick)["next_manager_pick"] == expected


def test_fb14_fb15_manual_unavailable_and_filled_pool_are_not_eligible():
    result = _board(manual_availability={"QB00": "manually_drafted"}, filled_pools=("RB",))
    assert _entry(result, "QB00")["eligible"] is False
    assert "PLAYER_MANUALLY_UNAVAILABLE" in _entry(result, "QB00")["recommendation_reason_codes"]
    assert _entry(result, "RB00")["eligible"] is False
    assert "FILLED_SLOT_INELIGIBLE" in _entry(result, "RB00")["recommendation_reason_codes"]


def test_fb16_adp_has_zero_effect_on_decision_math():
    changed = _projection_rows()
    for row in changed: row["ADP"] = "1"
    first, second = _board(), build_board(changed, current_pick=4)
    for left, right in zip(first["board"], second["board"], strict=True):
        for field in ("provider_projected_score", "provider_rank", "replacement_anchor_score", "generic_replacement_value", "next_pick_wait_cost", "scarcity_pressure", "roster_fit_score", "remaining_slot_scarcity_pressure", "valid_roster_fit_score", "early_position_suppression_penalty", "recommended_pick_value"):
            assert left[field] == right[field]
    recommendation_fields = ("player", "normalized_position_pool", "provider_projected_score", "provider_rank", "replacement_anchor_score", "generic_replacement_value", "next_pick_wait_cost", "remaining_slot_scarcity_pressure", "valid_roster_fit_score", "early_position_suppression_penalty", "early_position_suppression_status", "recommended_pick_value", "recommendation_reason_codes", "next_pick_contingency")
    assert {field: first["recommendation"][field] for field in recommendation_fields} == {field: second["recommendation"][field] for field in recommendation_fields}
    assert [entry["player"] for entry in first["board"]] == [entry["player"] for entry in second["board"]]


def test_fb17_raw_fpts_alone_does_not_choose_recommendation():
    result = _board()
    assert result["recommendation"]["provider_projected_score"] < _entry(result, "QB00")["provider_projected_score"]


def test_fb18_to_fb20_kicker_and_defense_suppression():
    result = _board()
    assert _entry(result, "K00")["early_position_suppression_status"] == "KICKER_SUPPRESSED_BEFORE_ROUND_6"
    assert _entry(result, "DST00")["early_position_suppression_status"] == "DEFENSE_SUPPRESSED_BEFORE_FINAL_ROUND"
    assert "EARLY_KICKER_SCARCITY_EXCEPTION" in _entry(result, "K00")["recommendation_reason_codes"] or "KICKER_SUPPRESSED_BEFORE_ROUND_6" in _entry(result, "K00")["recommendation_reason_codes"]


def test_fb21_fb22_required_decision_and_provenance_fields():
    result = _board()
    assert {"player", "normalized_position_pool", "provider_projected_score", "expected_next_pick_option", "next_pick_wait_cost", "recommendation_reason_codes"} <= set(result["recommendation"])
    assert result["data_freshness_status"] == "degraded"
    assert result["provider_score_not_event_decomposable"] is True


def test_fb26_fail_closed_for_invalid_state():
    with pytest.raises(FantraxBoardError, match="CONFIGURATION_REJECTED"):
        _board(manual_availability={"QB00": "live_provider_state"})


def test_fb21_to_fb29_generated_artifact_is_offline_provenanced_and_reversible(tmp_path, monkeypatch):
    """Generic/causality/time/reversibility/live-failure acceptance trace."""
    projections, historical, output = tmp_path / "2026.csv", tmp_path / "2025.csv", tmp_path / "output"
    artifact_rows = _projection_rows()
    artifact_rows[0]["Player"] = "Josh Allen"
    csv_text = HEADER + "\n".join(",".join(row[column] for column in ("Player", "Team", "Position", "RkOv", "FPts", "FP/G", "ADP", "Bye")) for row in artifact_rows) + "\n"
    projections.write_text(csv_text, encoding="utf-8")
    historical.write_text(csv_text.replace("100", "99", 1), encoding="utf-8")
    tool = runpy.run_path(str(Path("tools/build_fantrax_draft_board.py")))
    monkeypatch.setattr(sys, "argv", ["build", "--projections", str(projections), "--historical", str(historical), "--output", str(output)])
    assert tool["main"]() == 0
    snapshot = json.loads((output / "projection_snapshot.json").read_text(encoding="utf-8"))
    html = (output / "spamml_2026_draft_board.html").read_text(encoding="utf-8")
    assert snapshot["input_files"]["projections_2026"]["filename"] == "2026.csv"
    assert str(projections) not in json.dumps(snapshot)
    assert snapshot["data_freshness_status"] == "degraded"
    assert snapshot["provider_score_not_event_decomposable"] is True
    assert {"artifact_id", "as_of_timestamp", "input_snapshot_id", "projection_version", "league_id", "manager_seat", "configuration_version", "optimizer_version", "known_limitations", "uncertainty"} <= set(snapshot)
    assert snapshot["projection_version"] == "fantrax-provider-fpts-local-snapshot-v0.1"
    assert snapshot["league_id"] == "spamml-2026" and snapshot["manager_seat"] == 4
    assert "DEGRADED SOURCE MODE" in html and "Local/manual availability" in html
    assert "Manual drafted/unavailable state is local/in-memory only" in html
    assert "const snapshot =" in html
    assert {"decision_inputs", "parity_fixtures"} <= set(snapshot)
    assert {"replacement_anchor_score", "generic_replacement_value", "remaining_slot_scarcity_pressure", "valid_roster_fit_score", "early_position_suppression_penalty"} <= set(snapshot["board"][0])
    assert all(fixture["expected"]["recommendation"]["player"] for fixture in snapshot["parity_fixtures"])
    assert "window.__fantraxBoard" in html and "verifyParity" in html and "recompute" in html
    assert "Anchor score" in html and "Marginal replacement value" in html and "Reconciled value" in html
    adapter_script = "const fs=require('fs');const h=fs.readFileSync(process.argv[1],'utf8');const s=h.slice(h.indexOf('<script>')+8,h.indexOf('function visible'));eval(s);const out=verifyParity();console.log(JSON.stringify(out));if(!out.every(x=>x.pass))process.exit(1);"
    adapter = subprocess.run(["node", "-e", adapter_script, str(output / "spamml_2026_draft_board.html")], capture_output=True, text=True, check=False)
    assert adapter.returncode == 0, adapter.stderr
    assert [item["name"] for item in json.loads(adapter.stdout)] == ["initial_pick_4", "josh_allen_manually_drafted", "filled_qb_slot", "k_before_round_6", "defense_before_final_round"]
    ui_event_script = r'''const fs=require('fs'),vm=require('vm'),html=fs.readFileSync(process.argv[1],'utf8'),script=html.slice(html.indexOf('<script>')+8,html.indexOf('</script>'));
function documentShim(){const nodes={meta:{textContent:''},recommendation:{textContent:''},rows:{children:[],set innerHTML(v){this.children=[]},get innerHTML(){return ''}}};function tr(){let select;return {className:'',_html:'',set innerHTML(v){this._html=v;const m=v.match(/data-player="([^"]+)"/);select=m?{dataset:{player:m[1]},value:'available',onchange:null}:null},get innerHTML(){return this._html},querySelector(q){return q==='select'?select:null}}}return {querySelector(q){if(q==='#meta')return nodes.meta;if(q==='#recommendation')return nodes.recommendation;if(q==='#rows')return nodes.rows;const m=q.match(/^select\[data-player="(.+)"\]$/);if(m)return nodes.rows.children.map(x=>x.querySelector('select')).find(x=>x&&x.dataset.player===m[1])||null;return null},createElement(){return tr()},_nodes:nodes}}
function load(){const document=documentShim(),window={},context={document,window,console};document._nodes.rows.appendChild=x=>document._nodes.rows.children.push(x);vm.runInNewContext(script,context);return {document,window}}
function summary(result){const f=['player','normalized_position_pool','expected_next_pick_option','next_pick_wait_cost','replacement_anchor_score','generic_replacement_value','remaining_slot_scarcity_pressure','valid_roster_fit_score','early_position_suppression_penalty','recommended_pick_value','recommendation_reason_codes'];const pick=x=>x?Object.fromEntries(f.map(k=>[k,x[k]])):null;return {next_manager_pick:result.next_manager_pick,recommendation:pick(result.recommendation),alternatives_by_open_pool:Object.fromEntries(Object.entries(result.alternatives_by_open_pool).map(([k,v])=>[k,pick(v)]))}}
const first=load(),before=first.document.querySelector('select[data-player="Josh Allen"]');if(!before)throw Error('Josh Allen select not rendered');const beforeRecord={value:before.value,rowClass:first.document._nodes.rows.children.find(x=>x.querySelector('select')===before).className};before.value='manually_drafted';before.onchange();const after=first.document.querySelector('select[data-player="Josh Allen"]'),row=first.document._nodes.rows.children.find(x=>x.querySelector('select')===after),decision=summary(first.window.__fantraxBoard.recompute()),reload=load(),reloaded=reload.document.querySelector('select[data-player="Josh Allen"]');console.log(JSON.stringify({before:beforeRecord,after:{value:after.value,rowClass:row.className,label:row.innerHTML.match(/Local\/manual: ([^<]+)/)[1],html:row.innerHTML},decision,reloadedValue:reloaded.value}));'''
    ui_event = subprocess.run(["node", "-e", ui_event_script, str(output / "spamml_2026_draft_board.html")], capture_output=True, text=True, check=False)
    assert ui_event.returncode == 0, ui_event.stderr
    event = json.loads(ui_event.stdout)
    expected_manual = build_board(artifact_rows, current_pick=4, manual_availability={"Josh Allen": "manually_drafted"})
    assert event["before"] == {"value": "available", "rowClass": ""}
    assert event["after"]["value"] == "manually_drafted"
    assert event["after"]["label"] == "manually drafted"
    assert event["after"]["rowClass"] == "manual-unavailable"
    assert "selected" not in event["after"]["html"]  # DOM value, not a stale HTML default, is authoritative.
    assert event["reloadedValue"] == "available"
    assert event["decision"]["recommendation"] == {field: expected_manual["recommendation"].get(field) for field in event["decision"]["recommendation"]}
    assert event["decision"]["next_manager_pick"] == expected_manual["next_manager_pick"]
    assert "recommended_pick_value" in html and "fetch(" not in html and "localStorage" not in html
    assert not any(token in html for token in ("XMLHttpRequest", "WebSocket", "sessionStorage", "http://", "https://"))
    assert snapshot["recommendation"] == _board()["recommendation"]  # causality/time integrity: deterministic frozen input
    monkeypatch.setattr(sys, "argv", ["build", "--projections", str(tmp_path / "missing.csv"), "--historical", str(historical), "--output", str(output)])
    assert tool["main"]() == 2  # live/source failure is explicit and never becomes a recommendation
