"""Build an offline static Fantrax SPAMML draft board from local CSVs only."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.recommendation.fantrax_draft_board import FantraxBoardError, build_board, read_fantrax_csv

PROJECTION_VERSION = "fantrax-provider-fpts-local-snapshot-v0.1"
LEAGUE_ID = "spamml-2026"
MANAGER_SEAT = 4


def _metadata(path: Path) -> dict[str, object]:
    content = path.read_bytes()
    return {"filename": path.name, "sha256": sha256(content).hexdigest().upper(), "byte_length": len(content)}


def _parity_summary(result: dict) -> dict:
    fields = ("player", "normalized_position_pool", "provider_projected_score", "expected_next_pick_option", "next_pick_wait_cost", "replacement_anchor_score", "generic_replacement_value", "remaining_slot_scarcity_pressure", "valid_roster_fit_score", "early_position_suppression_status", "recommended_pick_value", "recommendation_reason_codes")
    return {"next_manager_pick": result["next_manager_pick"], "recommendation": {field: result["recommendation"].get(field) for field in fields}, "alternatives_by_open_pool": {pool: ({field: entry.get(field) for field in fields} if entry else None) for pool, entry in result["alternatives_by_open_pool"].items()}}


def _parity_fixtures(projection_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    states = (("initial_pick_4", {}, ()), ("josh_allen_manually_drafted", {"Josh Allen": "manually_drafted"}, ()), ("filled_qb_slot", {}, ("QB",)), ("k_before_round_6", {}, ()), ("defense_before_final_round", {}, ()))
    return [{"name": name, "state": {"current_pick": 4, "manual_availability": manual, "filled_pools": list(filled)}, "expected": _parity_summary(build_board(projection_rows, current_pick=4, manual_availability=manual, filled_pools=filled))} for name, manual, filled in states]


def _html(snapshot: dict) -> str:
    data = json.dumps(snapshot, separators=(",", ":")).replace("</", "<\\/")
    return '''<!doctype html><html><head><meta charset="utf-8"><title>SPAMML Fantrax Draft Board</title>
<style>body{font-family:system-ui;margin:1rem}#banner{background:#5b1d1d;color:#fff;padding:1rem;font-weight:700}table{border-collapse:collapse;width:100%}td,th{border:1px solid #bbb;padding:.35rem;text-align:left}button{margin:.2rem}.manual-unavailable{background:#fff4cc;font-weight:600}.state-label{font-weight:700}</style></head><body>
<div id="banner">DEGRADED SOURCE MODE — user-provided local snapshot; manual live-state entry required. Provider FPts is not event-decomposable.</div>
<h1>SPAMML 2026 Fantrax Draft Board</h1><p id="meta"></p><div id="recommendation"></div>
<p id="manual-state">Manual drafted/unavailable state is local/in-memory only, is not validated live-platform state, and is discarded on reload.</p>
<p>Local/manual availability: <button onclick="filter('ALL')">All</button><button onclick="filter('QB')">QB</button><button onclick="filter('RB')">RB</button><button onclick="filter('REC')">REC</button><button onclick="filter('K')">K</button><button onclick="filter('D_O')">D/O</button><button onclick="filter('AVAILABLE')">Available only</button><button onclick="filter('MANUAL')">Manual drafted / excluded</button></p>
<p>K/D_O explanation: K is suppressed before round 6 unless its documented marginal wait-cost exception passes. D/O is suppressed before the final round unless its documented marginal advantage exception passes.</p>
<table><thead><tr><th>Player</th><th>Pool</th><th>FPts</th><th>RkOv</th><th>ADP</th><th>Anchor score</th><th>Marginal replacement value</th><th>Scarcity component</th><th>Roster-fit component</th><th>Suppression penalty</th><th>Reconciled value</th><th>Local/manual availability</th></tr></thead><tbody id="rows"></tbody></table>
<script>const snapshot = ''' + data + r''';let active='ALL';const manual={};const POOLS=['QB','RB','REC','K','D_O'];const SUPPRESSED=new Set(['KICKER_SUPPRESSED_BEFORE_ROUND_6','DEFENSE_SUPPRESSED_BEFORE_FINAL_ROUND']);
function rank(a,b){return b.provider_projected_score-a.provider_projected_score||a.provider_rank-b.provider_rank||a.player.localeCompare(b.player)}
function recompute(overrides={}){const input=snapshot.decision_inputs,currentPick=overrides.current_pick??snapshot.current_pick,availability={...manual,...(overrides.manual_availability||{})},filled=new Set(overrides.filled_pools||[]),slots={...input.starter_slots};filled.forEach(p=>slots[p]=0);const players=input.players.map(p=>({...p,availability_state:availability[p.player]||p.availability_state}));const by=Object.fromEntries(POOLS.map(p=>[p,players.filter(x=>x.normalized_position_pool===p).sort(rank)]));const anchor=Object.fromEntries(POOLS.map(p=>[p,by[p].length?by[p][Math.min(input.pool_demands[p],by[p].length)-1].provider_projected_score:0]));const next=input.planned_pick_sequence.find(p=>p>currentPick)??null,gap=next?next-currentPick-1:0,openDemand=POOLS.reduce((n,p)=>n+(slots[p]?input.pool_demands[p]:0),0),taken=Object.fromEntries(POOLS.map(p=>[p,gap&&openDemand?Math.max(1,Math.ceil(gap*input.pool_demands[p]/openDemand)):0]));const core=['QB','RB','REC'],waits=[];for(const p of core){const a=by[p].filter(x=>x.availability_state==='available');if(slots[p]&&a.length){const e=a[Math.min(taken[p],a.length-1)];waits.push(a[0].provider_projected_score-e.provider_projected_score)}}const maxCore=Math.max(0,...waits),normalFilled=core.every(p=>!slots[p]),round=Math.floor((currentPick-1)/16)+1,entries=[];
for(const pool of POOLS){const avail=by[pool].filter(x=>x.availability_state==='available');by[pool].forEach((item,index)=>{const e={...item,position_rank:index+1,replacement_anchor_score:anchor[pool],generic_replacement_value:Math.max(0,item.provider_projected_score-anchor[pool]),remaining_slot_demand:slots[pool],available_player_count_by_pool:avail.length,scarcity_pressure:avail.length?slots[pool]/avail.length:0,roster_fit_score:slots[pool]?1/slots[pool]:0,ADP_market_context_only:true,eligible:item.availability_state==='available'&&!!slots[pool]};let codes=[...input.base_reason_codes,...item.source_reason_codes],nextOption=null,wait=0;if(item.availability_state!=='available')codes.push('PLAYER_MANUALLY_UNAVAILABLE');if(!slots[pool])codes.push('FILLED_SLOT_INELIGIBLE');if(e.eligible){const alt=avail.filter(x=>x.player!==item.player);if(alt.length){nextOption=alt[Math.min(taken[pool],alt.length-1)];wait=item.provider_projected_score-nextOption.provider_projected_score}codes.push('NEXT_PICK_WAIT_COST','REPLACEMENT_VALUE','ROSTER_FIT');if(e.scarcity_pressure>=1)codes.push('REMAINING_SLOT_SCARCITY')}e.expected_next_pick_option=nextOption?{player:nextOption.player,provider_projected_score:nextOption.provider_projected_score}:null;e.next_pick_wait_cost=wait;e.early_position_suppression_status='NOT_SUPPRESSED';let penalty=0;if(e.eligible&&pool==='K'&&round<6){const exception=(normalFilled||wait>maxCore)&&wait>=input.options.early_kicker_wait_cost_threshold;if(exception){codes.push('EARLY_KICKER_SCARCITY_EXCEPTION');e.early_position_suppression_status='EARLY_KICKER_SCARCITY_EXCEPTION'}else{codes.push('KICKER_SUPPRESSED_BEFORE_ROUND_6');e.early_position_suppression_status='KICKER_SUPPRESSED_BEFORE_ROUND_6';penalty=1000000}}if(e.eligible&&pool==='D_O'&&round<8){const exception=wait>=maxCore+input.options.early_defense_advantage_threshold;if(exception){codes.push('EARLY_DEFENSE_SCARCITY_EXCEPTION');e.early_position_suppression_status='EARLY_DEFENSE_SCARCITY_EXCEPTION'}else{codes.push('DEFENSE_SUPPRESSED_BEFORE_FINAL_ROUND');e.early_position_suppression_status='DEFENSE_SUPPRESSED_BEFORE_FINAL_ROUND';penalty=1000000}}e.remaining_slot_scarcity_pressure=input.options.scarcity_weight*e.scarcity_pressure;e.valid_roster_fit_score=input.options.roster_fit_weight*e.roster_fit_score;e.early_position_suppression_penalty=penalty;e.recommended_pick_value=e.eligible?wait+e.generic_replacement_value+e.remaining_slot_scarcity_pressure+e.valid_roster_fit_score-penalty:null;e.recommendation_reason_codes=[...new Set(codes)].sort();e.next_pick_contingency=nextOption&&next?'If unavailable at planned pick '+next+', use '+nextOption.player+'.':'No later planned manager pick.';entries.push(e)})}
entries.sort((a,b)=>(a.recommended_pick_value===null)-(b.recommended_pick_value===null)||-((a.recommended_pick_value??-1000001)-(b.recommended_pick_value??-1000001))||a.provider_rank-b.provider_rank||a.player.localeCompare(b.player));const recommendation=entries.find(x=>x.eligible&&!SUPPRESSED.has(x.early_position_suppression_status))||null,alternatives=Object.fromEntries(POOLS.filter(p=>slots[p]).map(p=>[p,entries.find(x=>x.normalized_position_pool===p&&x.eligible&&x.early_position_suppression_status==='NOT_SUPPRESSED')||null]));return {current_pick:currentPick,next_manager_pick:next,board:entries,recommendation,alternatives_by_open_pool:alternatives}}
const parityFields=['player','normalized_position_pool','provider_projected_score','expected_next_pick_option','next_pick_wait_cost','replacement_anchor_score','generic_replacement_value','remaining_slot_scarcity_pressure','valid_roster_fit_score','early_position_suppression_status','recommended_pick_value','recommendation_reason_codes'];function summary(x){const pick=o=>o?Object.fromEntries(parityFields.map(k=>[k,o[k]])):null;return {next_manager_pick:x.next_manager_pick,recommendation:pick(x.recommendation),alternatives_by_open_pool:Object.fromEntries(Object.entries(x.alternatives_by_open_pool).map(([p,e])=>[p,pick(e)]))}}function verifyParity(){return snapshot.parity_fixtures.map(f=>({name:f.name,pass:JSON.stringify(summary(recompute(f.state)))===JSON.stringify(f.expected)}))}
function visible(x){return active==='ALL'||(active==='AVAILABLE'&&x.availability_state==='available')||(active==='MANUAL'&&x.availability_state!=='available')||x.normalized_position_pool===active}function stateLabel(x){return 'Local/manual: '+(x.availability_state==='manually_drafted'?'manually drafted':x.availability_state==='manually_excluded'?'manually excluded':'available')}function render(){const result=recompute(),top=result.recommendation;document.querySelector('#recommendation').textContent='Current manual overall pick '+result.current_pick+'; next planned Professor FleX pick '+result.next_manager_pick+'; recommendation: '+(top?top.player:'none')+' ('+(top?top.normalized_position_pool:'n/a')+'). Local/manual state only.';const body=document.querySelector('#rows');body.innerHTML='';result.board.filter(visible).forEach(x=>{const tr=document.createElement('tr');tr.className=x.availability_state==='available'?'':'manual-unavailable';tr.innerHTML='<td>'+x.player+'</td><td>'+x.normalized_position_pool+'</td><td>'+x.provider_projected_score+'</td><td>'+x.provider_rank+'</td><td>'+x.ADP+'</td><td>'+x.replacement_anchor_score+'</td><td>'+x.generic_replacement_value+'</td><td>'+x.remaining_slot_scarcity_pressure+'</td><td>'+x.valid_roster_fit_score+'</td><td>'+x.early_position_suppression_penalty+'</td><td>'+x.recommended_pick_value+'</td><td><span class="state-label" role="status">'+stateLabel(x)+'</span><select data-player="'+x.player+'"><option value="available">available</option><option value="manually_drafted">manually drafted</option><option value="manually_excluded">manually excluded</option></select></td>';const select=tr.querySelector('select');select.value=x.availability_state;select.onchange=()=>{manual[x.player]=select.value;render()};body.appendChild(tr)})}function filter(v){active=v;render()}window.__fantraxBoard={recompute,verifyParity,parityFixtures:snapshot.parity_fixtures};document.querySelector('#meta').textContent='Artifact '+snapshot.artifact_id+' | '+snapshot.as_of_timestamp+' | no network, API, storage, current provider sync, or automatic draft action.';render();</script></body></html>'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--projections", required=True); parser.add_argument("--historical", required=True); parser.add_argument("--output", required=True)
    args = parser.parse_args()
    projections, historical, output = Path(args.projections), Path(args.historical), Path(args.output)
    try:
        if not projections.is_file() or not historical.is_file(): raise FantraxBoardError("SOURCE_INPUT_MISSING")
        projection_rows, historical_rows = read_fantrax_csv(projections), read_fantrax_csv(historical)
        snapshot = build_board(projection_rows, current_pick=4)
    except FantraxBoardError as exc:
        print(exc); return 2
    output.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    projection_meta, historical_meta = _metadata(projections), _metadata(historical)
    snapshot.update({
        "artifact_id": str(uuid4()),
        "as_of_timestamp": timestamp,
        "build_timestamp_utc": timestamp,
        "input_snapshot_id": sha256((projection_meta["sha256"] + historical_meta["sha256"]).encode()).hexdigest(),
        "projection_version": PROJECTION_VERSION,
        "league_id": LEAGUE_ID,
        "manager_seat": MANAGER_SEAT,
        "known_limitations": list(snapshot["limitations"]),
        "uncertainty": ["Provider FPts is a frozen local snapshot, not live provider synchronization."],
        "input_files": {"projections_2026": projection_meta, "historical_2025_calibration_only": historical_meta},
        "historical_row_count": len(historical_rows),
        "parity_fixtures": _parity_fixtures(projection_rows),
    })
    (output / "projection_snapshot.json").write_text(json.dumps(snapshot, indent=2, sort_keys=True), encoding="utf-8")
    report = {"status": "valid", "headers": list(projection_rows[0].keys()), "historical_calibration_only": True, "reason_codes": snapshot["reason_codes"], "projection_version": PROJECTION_VERSION, "league_id": LEAGUE_ID, "manager_seat": MANAGER_SEAT}
    (output / "validation_report.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    (output / "spamml_2026_draft_board.html").write_text(_html(snapshot), encoding="utf-8")
    print(output / "projection_snapshot.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
