"""Generate the RB/WR study notebooks. Notebook code is the executable source of truth."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
(ROOT / "notebooks").mkdir(parents=True, exist_ok=True)
(ROOT / "data" / "processed").mkdir(parents=True, exist_ok=True)
(ROOT / "artifacts").mkdir(parents=True, exist_ok=True)


def md(text: str, metadata: dict | None = None) -> dict:
    return {"cell_type": "markdown", "metadata": metadata or {}, "source": text.splitlines(True)}


def code(text: str) -> dict:
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": text.splitlines(True)}


SECTION_NOTES = {
    "imports and chart helper": "Load paths and define the shared offline Plotly renderer.",
    "locked study configuration": "Declare the population, strategy bins, checkpoints, outcomes, support thresholds, and bootstrap settings before examining results.",
    "configuration chart": "Visualize the prespecified draft checkpoints and mark Round 6 as primary.",
    "load inherited panels": "Load the validated league outcomes and complete draft boards from the read-only QB/TE sibling study.",
    "recover lineup settings": "Recover RB, WR, and flex lineup requirements from current and historical Sleeper draft payloads.",
    "apply population gates": "Restrict to conventional PPR or half-PPR lineups so format differences do not define the apparent strategy effect.",
    "build team strategy panel": "Count RB, WR, and non-RB/WR selections through each checkpoint and attach the first-round choice.",
    "build checkpoint and pick panels": "Reshape the team data for checkpoint analysis and retain every early RB/WR selection for availability linkage.",
    "validate and save manifest": "Run balance, composition, and outcome-accounting gates and save the retained-sample manifest.",
    "preparation coverage chart": "Show retained league coverage by season and scoring format.",
    "prepare eda summaries": "Create the descriptive strategy, exact-count, checkpoint, season, and scoring-format summaries.",
    "strategy scoring chart": "Compare regular-season scoring across the four prespecified Round 6 builds.",
    "practical points chart": "Translate standardized performance into league-relative points per fantasy week.",
    "top six chart": "Compare the share of teams finishing in the top half of league scoring.",
    "strategy support chart": "Show the amount of team and league support behind every headline build.",
    "exact rb count chart": "Inspect the uncollapsed Round 6 RB-count curve without treating it as the prespecified headline test.",
    "checkpoint heatmap": "Show how the RB-count association develops after Rounds 2, 4, 6, and 8.",
    "season stability chart": "Check whether pooled strategy rankings persist across seasons.",
    "format interaction chart": "Compare strategy patterns in PPR and half-PPR leagues.",
    "categorical association chart": "Quantify the unadjusted categorical association without imposing an ordinal linear trend.",
    "define inference model": "Define the adjusted least-squares and efficient league-cluster bootstrap used for headline estimates.",
    "run primary inference": "Estimate adjusted Round 6 strategy outcomes with 2,000 league-cluster bootstrap replicates.",
    "adjusted strategy chart": "Plot covariate-standardized scoring estimates and their clustered intervals.",
    "balanced contrast chart": "Plot each build's adjusted difference from the balanced two-RB reference.",
    "run robustness models": "Repeat the adjusted comparison by scoring format, draft-slot band, and exact common lineup.",
    "robustness chart": "Display how strategy estimates move across prespecified subgroups.",
    "checkpoint inference": "Estimate supported exact RB counts at the secondary Round 4 and Round 8 checkpoints.",
    "checkpoint inference chart": "Compare adjusted RB-count estimates across early and late checkpoints.",
    "calculate forward tests": "Select a strategy only from prior seasons, then test it in the next season.",
    "forward scoring chart": "Plot out-of-sample scoring differences for the training-selected strategy.",
    "forward top six chart": "Plot out-of-sample top-six differences for the selected strategy.",
    "selection stability chart": "Show which strategy won in each expanding training window and how it tested next year.",
    "link early pick availability": "Link early drafted RBs and WRs to weekly participation and calculate fantasy-window availability.",
    "summarize availability": "Aggregate availability by position, round, team, and strategy.",
    "availability by round chart": "Compare RB and WR unavailability rates at each early round.",
    "run availability sensitivity": "Repeat the adjusted strategy comparison where every linked early RB/WR was active in at least 75% of fantasy weeks.",
    "availability strategy chart": "Compare the injury-inclusive strategy estimates with the all-available sensitivity sample.",
    "prepare first round sample": "Restrict the prespecified side question to teams selecting an RB or WR in Round 1.",
    "run first round inference": "Estimate the adjusted RB-versus-WR Round 1 association with exact draft-slot controls.",
    "first round adjusted chart": "Plot adjusted team outcomes for first-round RB and WR selections.",
    "first round slot chart": "Repeat the Round 1 comparison within early, middle, and late draft slots.",
    "first round season chart": "Show whether the first-round RB-minus-WR difference is stable by season.",
    "first round availability chart": "Compare first-round unavailability by position using the validated direct player linkage.",
    "first round available sensitivity": "Repeat the Round 1 comparison among first-rounders active for at least 75% of fantasy weeks.",
    "assemble recommendations": "Combine pooled inference, pairwise contrasts, validation, robustness, and availability into evidence-graded conclusions.",
    "recommendation chart": "Show the primary adjusted build comparison with the evidence grade in one decision view.",
    "first round answer chart": "Show the full-sample and availability-conditioned answer to the Round 1 side question.",
    "write study summary": "Write a machine-readable summary of the executed findings and limitations.",
}


def write(name: str, title: str, purpose: str, source: str) -> None:
    matches = list(re.finditer(r"(?m)^# CELL \[([^\]]+)\]\n", source))
    if not matches:
        raise ValueError(f"{name} has no section markers")
    cells = [md(f"# {title}\n\n{purpose}\n")]
    for index, match in enumerate(matches):
        key = match.group(1)
        end = matches[index + 1].start() if index + 1 < len(matches) else len(source)
        section_source = source[match.start():end].rstrip() + "\n"
        before = SECTION_NOTES.get(key, f"Run the `{key}` section.")
        cells.extend([
            md(f"## {key.title()}\n\n{before}\n"),
            code(section_source),
            md("### Interpretation\n\nPending execution.\n", {"role": "interpretation", "section_key": key}),
        ])
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.11"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    (ROOT / "notebooks" / name).write_text(json.dumps(notebook, indent=1), encoding="utf-8")


COMMON = '''# CELL [imports and chart helper]
from pathlib import Path
import json as _json
ROOT = Path.cwd()
if ROOT.name == "notebooks":
    ROOT = ROOT.parent
ARTIFACTS = ROOT / "artifacts"
PROCESSED = ROOT / "data/processed"
SOURCE_QBTE = ROOT.parent / "fantasy_qb_te_draft_timing_study"
SOURCE_DRAFT = ROOT.parent / "fantasy_draft_order_study"
_PLOTLY_JS = (ROOT / "assets/plotly.min.js").read_text(encoding="utf-8")
_CHART_FILES = []
_CHART_COUNTER = 0
def _plain(value):
    if hasattr(value, "item"):
        return value.item()
    raise TypeError(type(value).__name__)
def write_chart(filename, traces, layout):
    global _CHART_COUNTER
    _CHART_COUNTER += 1
    chart_id = f"chart_{_CHART_COUNTER}"
    defaults = {"paper_bgcolor":"#111318","plot_bgcolor":"#111318","font":{"color":"#e5e7eb","family":"Arial, sans-serif","size":14},"title":{"font":{"color":"#f8fafc","size":22},"x":0.5},"margin":{"l":85,"r":45,"t":95,"b":90},"hoverlabel":{"bgcolor":"#1f2937","bordercolor":"#64748b","font":{"color":"#f8fafc"}},"xaxis":{"gridcolor":"#334155","linecolor":"#64748b","zerolinecolor":"#94a3b8"},"yaxis":{"gridcolor":"#334155","linecolor":"#64748b","zerolinecolor":"#94a3b8"},"legend":{"bgcolor":"rgba(17,19,24,0.75)","font":{"color":"#e5e7eb"}}}
    for key, value in layout.items():
        if isinstance(value, dict) and isinstance(defaults.get(key), dict):
            defaults[key].update(value)
        elif key == "title" and isinstance(value, str):
            defaults["title"]["text"] = value
        else:
            defaults[key] = value
    html = f"""<!doctype html><html><head><meta charset="utf-8"><style>html,body{{margin:0;background:#111318;color:#e5e7eb}}#{chart_id}{{width:100%;height:640px;background:#111318}}</style><script>{_PLOTLY_JS}</script></head><body><div id="{chart_id}"></div><script>Plotly.newPlot("{chart_id}",{_json.dumps(traces,default=_plain)},{_json.dumps(defaults,default=_plain)},{_json.dumps({"responsive":True,"displaylogo":False})})</script></body></html>"""
    (ARTIFACTS / filename).write_text(html, encoding="utf-8")
    _CHART_FILES.append(filename)
_SECTION_INTERPRETATION = "The shared helper changes presentation only; it does not transform study data or affect any estimate."
'''


MODEL_HELPERS = '''
def _design_matrix(df, treatment, levels, reference, controls):
    import numpy as np
    columns = [np.ones(len(df), dtype=float)]
    names = ["intercept"]
    for level in levels:
        if level == reference:
            continue
        columns.append(df[treatment].eq(level).to_numpy(dtype=float))
        names.append(f"treat::{level}")
    for control in controls:
        series = df[control].astype(str).fillna("Missing")
        values = sorted(series.unique().tolist())
        for value in values[1:]:
            columns.append(series.eq(value).to_numpy(dtype=float))
            names.append(f"{control}::{value}")
    return np.column_stack(columns), names

def clustered_model(df, treatment, levels, reference, controls, outcomes, reps, seed):
    import numpy as np
    import pandas as pd
    use = df.loc[df[treatment].isin(levels)].dropna(subset=outcomes + [treatment, "draft_id"]).copy()
    X, names = _design_matrix(use, treatment, levels, reference, controls)
    Y = use[outcomes].to_numpy(dtype=float)
    beta = np.linalg.pinv(X.T @ X) @ (X.T @ Y)
    cluster_codes, cluster_names = pd.factorize(use["draft_id"], sort=True)
    groups = len(cluster_names)
    p, q = X.shape[1], Y.shape[1]
    sxx = np.zeros((groups, p, p), dtype=float)
    sxy = np.zeros((groups, p, q), dtype=float)
    for group in range(groups):
        mask = cluster_codes == group
        xg, yg = X[mask], Y[mask]
        sxx[group] = xg.T @ xg
        sxy[group] = xg.T @ yg
    rng = np.random.default_rng(seed)
    boot = np.empty((reps, p, q), dtype=float)
    for draw in range(reps):
        sampled = rng.integers(0, groups, size=groups)
        weights = np.bincount(sampled, minlength=groups).astype(float)
        a = np.tensordot(weights, sxx, axes=(0, 0))
        b = np.tensordot(weights, sxy, axes=(0, 0))
        boot[draw] = np.linalg.pinv(a) @ b
    xbar = X.mean(axis=0)
    treat_indices = {level:names.index(f"treat::{level}") for level in levels if level != reference}
    for index in treat_indices.values():
        xbar[index] = 0.0
    predictions = {}
    for level in levels:
        vector = xbar.copy()
        if level != reference:
            vector[treat_indices[level]] = 1.0
        predictions[level] = (vector @ beta, np.einsum("rpq,p->rq", boot, vector))
    rows = []
    reference_point, reference_boot = predictions[reference]
    for level in levels:
        point, sampled = predictions[level]
        count = int(use[treatment].eq(level).sum())
        leagues = int(use.loc[use[treatment].eq(level), "draft_id"].nunique())
        for outcome_index, outcome in enumerate(outcomes):
            diff = point[outcome_index] - reference_point[outcome_index]
            diff_boot = sampled[:, outcome_index] - reference_boot[:, outcome_index]
            rows.append({"level":level,"outcome":outcome,"n":count,"leagues":leagues,"estimate":float(point[outcome_index]),"ci_low":float(np.quantile(sampled[:,outcome_index],.025)),"ci_high":float(np.quantile(sampled[:,outcome_index],.975)),"reference":reference,"difference_vs_reference":float(diff),"difference_ci_low":float(np.quantile(diff_boot,.025)),"difference_ci_high":float(np.quantile(diff_boot,.975))})
    contrasts = []
    for left_index, left in enumerate(levels):
        for right in levels[left_index + 1:]:
            left_point, left_boot = predictions[left]
            right_point, right_boot = predictions[right]
            for outcome_index, outcome in enumerate(outcomes):
                values = left_boot[:, outcome_index] - right_boot[:, outcome_index]
                contrasts.append({"left":left,"right":right,"outcome":outcome,"difference":float(left_point[outcome_index]-right_point[outcome_index]),"ci_low":float(np.quantile(values,.025)),"ci_high":float(np.quantile(values,.975))})
    return pd.DataFrame(rows), pd.DataFrame(contrasts)

def point_model(df, treatment, levels, reference, controls, outcomes):
    import numpy as np
    use = df.loc[df[treatment].isin(levels)].dropna(subset=outcomes + [treatment]).copy()
    X, names = _design_matrix(use, treatment, levels, reference, controls)
    Y = use[outcomes].to_numpy(dtype=float)
    beta = np.linalg.pinv(X.T @ X) @ (X.T @ Y)
    xbar = X.mean(axis=0)
    treat_indices = {level:names.index(f"treat::{level}") for level in levels if level != reference}
    for index in treat_indices.values():
        xbar[index] = 0.0
    result = {}
    for level in levels:
        vector = xbar.copy()
        if level != reference:
            vector[treat_indices[level]] = 1.0
        result[level] = vector @ beta
    return result
'''


write(
    "00_configuration.ipynb",
    "NB00: configuration and analysis contract",
    "Locks the RB/WR population, primary Round 6 strategy definitions, secondary checkpoints, first-round side question, outcomes, and uncertainty settings.",
    COMMON + '''# CELL [locked study configuration]
import json
CONFIG = {
    "source_seasons": list(range(2018, 2026)),
    "teams": 12,
    "allowed_scoring_types": ["ppr", "half_ppr"],
    "required_rb_slots": 2,
    "allowed_wr_slots": [2, 3],
    "minimum_flex_slots": 1,
    "checkpoints": [2, 4, 6, 8],
    "primary_checkpoint": 6,
    "primary_strategies": ["Zero RB (0)", "WR-heavy (1)", "Balanced (2)", "RB-heavy (3+)"],
    "primary_reference": "Balanced (2)",
    "minimum_cell_n": 100,
    "bootstrap_replicates": 2000,
    "robustness_bootstrap_replicates": 750,
    "random_seed": 20260814,
    "availability_threshold": 0.75,
    "primary_outcome": "points_zscore",
    "secondary_outcomes": ["points_per_week_above_league", "top_6_points", "points_rank", "top_regular_season_scorer"],
    "first_round_positions": ["WR", "RB"],
}
(ARTIFACTS / "study_config.json").write_text(json.dumps(CONFIG, indent=2), encoding="utf-8")
print(json.dumps(CONFIG, indent=2))
_SECTION_INTERPRETATION = "Round 6 is the sole headline checkpoint; Rounds 2, 4, and 8 are diagnostics. Strategy labels are mechanical RB counts, and the first-round RB/WR comparison is prespecified as secondary, preventing either result from being chosen after inspecting outcomes."
# CELL [configuration chart]
write_chart("configuration_01_checkpoints.html", [{"type":"bar","x":[str(x) for x in CONFIG["checkpoints"]],"y":CONFIG["checkpoints"],"marker":{"color":["#64748b","#64748b","#f97316","#64748b"]},"text":["secondary","secondary","PRIMARY","secondary"],"textposition":"outside","hovertemplate":"Round %{x}<br>%{text}<extra></extra>"}], {"title":"Prespecified RB/WR allocation checkpoints","xaxis":{"title":"Checkpoint round","type":"category"},"yaxis":{"title":"Rounds of draft capital observed","dtick":1},"showlegend":False})
_SECTION_INTERPRETATION = "The analysis asks how roster construction evolves, but only the Round 6 classification can drive the headline recommendation. This limits multiple-comparison flexibility while retaining earlier and later checkpoints for interpretation."
''',
)


write(
    "01_data_preparation.ipynb",
    "NB01: data preparation",
    "Builds the conventional-lineup PPR/half-PPR team panel, checkpoint panel, and early-pick panel from validated sibling-study inputs.",
    COMMON + '''# CELL [load inherited panels]
import json
from collections import Counter
import numpy as np
import pandas as pd
leagues = pd.read_csv(SOURCE_QBTE / "data/processed/league_seasons.csv", dtype={"league_id":str,"draft_id":str})
teams = pd.read_csv(SOURCE_QBTE / "data/processed/team_timing_panel.csv", dtype={"league_id":str,"draft_id":str,"roster_id":int,"manager_hash":str})
picks = pd.read_csv(SOURCE_QBTE / "data/processed/draft_picks.csv", dtype={"league_id":str,"draft_id":str,"roster_id":int,"sleeper_player_id":str})
print(f"Inherited {leagues.draft_id.nunique():,} league-seasons, {len(teams):,} team-seasons, and {len(picks):,} picks.")
_SECTION_INTERPRETATION = f"The new study begins from the already-validated QB/TE panel rather than reacquiring outcomes: {leagues.draft_id.nunique():,} league-seasons and {len(teams):,} teams are available before RB/WR-specific lineup and scoring gates. This preserves comparability with the prior study."
# CELL [recover lineup settings]
settings = {}
with (SOURCE_QBTE / "data/cache/current_draft_payloads.jsonl").open(encoding="utf-8") as handle:
    for line in handle:
        record = json.loads(line)
        settings[str(record["draft_id"])] = record["payload"].get("settings") or {}
needed = set(leagues.loc[leagues.primary_sample, "draft_id"].astype(str)) - set(settings)
with (SOURCE_DRAFT / "data/cache/historic_drafts_and_rosters.jsonl").open(encoding="utf-8") as handle:
    for line in handle:
        record = json.loads(line); parts = record["path"].split("/")
        if len(parts) == 2 and parts[0] == "draft" and parts[1] in needed:
            settings[parts[1]] = record["payload"].get("settings") or {}
def slot_value(draft_id, key):
    return int((settings.get(str(draft_id)) or {}).get(key) or 0)
leagues["rb_start_slots"] = leagues.draft_id.map(lambda x: slot_value(x, "slots_rb"))
leagues["wr_start_slots"] = leagues.draft_id.map(lambda x: slot_value(x, "slots_wr"))
leagues["flex_start_slots"] = leagues.draft_id.map(lambda x: slot_value(x, "slots_flex"))
coverage = leagues.loc[leagues.primary_sample, "draft_id"].isin(settings).mean()
assert coverage == 1.0
print(f"Recovered lineup settings for {coverage:.1%} of the inherited primary leagues.")
_SECTION_INTERPRETATION = "Lineup metadata is complete after recovering the older draft payloads from the persisted source cache. RB/WR starter requirements can therefore be used as actual eligibility gates rather than inferred from draft behavior."
# CELL [apply population gates]
eligible_leagues = leagues.loc[
    leagues.primary_sample
    & leagues.scoring_type.isin(["ppr", "half_ppr"])
    & leagues.rb_start_slots.eq(2)
    & leagues.wr_start_slots.isin([2, 3])
    & leagues.flex_start_slots.ge(1)
].copy()
eligible_ids = set(eligible_leagues.draft_id)
excluded_standard = int((leagues.primary_sample & leagues.scoring_type.eq("std") & leagues.rb_start_slots.eq(2) & leagues.wr_start_slots.isin([2,3]) & leagues.flex_start_slots.ge(1)).sum())
team = teams.loc[teams.draft_id.isin(eligible_ids)].copy()
team = team.merge(eligible_leagues[["draft_id","rb_start_slots","wr_start_slots","flex_start_slots"]], on="draft_id", how="left")
draft_picks = picks.loc[picks.draft_id.isin(eligible_ids)].copy()
print(f"Retained {len(eligible_ids):,} leagues and {len(team):,} teams; excluded {excluded_standard} otherwise-eligible standard leagues.")
_SECTION_INTERPRETATION = f"The locked population retains {len(eligible_ids):,} conventional-lineup leagues ({len(team):,} teams). Only {excluded_standard} otherwise-eligible standard leagues exist, so excluding them prevents an unsupported standard-versus-PPR claim while sacrificing negligible coverage."
# CELL [build team strategy panel]
keys = ["draft_id", "roster_id"]
for checkpoint in [2, 4, 6, 8]:
    subset = draft_picks.loc[draft_picks["round"].le(checkpoint)]
    counts = subset.assign(position_group=np.where(subset.player_position.isin(["RB","WR"]), subset.player_position, "NON_RBWR")).groupby(keys + ["position_group"]).size().unstack(fill_value=0)
    counts = counts.reindex(columns=["RB","WR","NON_RBWR"], fill_value=0).reset_index()
    counts = counts.rename(columns={"RB":f"rb_count_r{checkpoint}","WR":f"wr_count_r{checkpoint}","NON_RBWR":f"non_rbwr_count_r{checkpoint}"})
    team = team.merge(counts, on=keys, how="left")
    for column in [f"rb_count_r{checkpoint}",f"wr_count_r{checkpoint}",f"non_rbwr_count_r{checkpoint}"]:
        team[column] = team[column].fillna(0).astype(int)
balanced_early = pd.Series(True, index=team.index)
for checkpoint in [2,4,6,8]:
    balanced_early &= (team[f"rb_count_r{checkpoint}"] + team[f"wr_count_r{checkpoint}"] + team[f"non_rbwr_count_r{checkpoint}"]).eq(checkpoint)
unbalanced_drafts = set(team.loc[~balanced_early, "draft_id"])
team = team.loc[~team.draft_id.isin(unbalanced_drafts)].copy()
draft_picks = draft_picks.loc[~draft_picks.draft_id.isin(unbalanced_drafts)].copy()
eligible_leagues = eligible_leagues.loc[~eligible_leagues.draft_id.isin(unbalanced_drafts)].copy()
eligible_ids = set(eligible_leagues.draft_id)
first = draft_picks.sort_values("pick_no").groupby(keys, as_index=False).first()
first = first[["draft_id","roster_id","pick_no","round","sleeper_player_id","player_name","player_position"]].rename(columns={"pick_no":"first_round_pick_no","round":"first_round_round","sleeper_player_id":"first_round_player_id","player_name":"first_round_player_name","player_position":"first_round_position"})
team = team.merge(first, on=keys, how="left")
def strategy(value):
    value = int(value)
    if value == 0: return "Zero RB (0)"
    if value == 1: return "WR-heavy (1)"
    if value == 2: return "Balanced (2)"
    return "RB-heavy (3+)"
team["strategy_r6"] = team.rb_count_r6.map(strategy)
team["draft_slot_band"] = pd.cut(team.draft_slot, bins=[0,4,8,12], labels=["Early (1-4)","Middle (5-8)","Late (9-12)"]).astype(str)
team.to_csv(PROCESSED / "team_strategy_panel.csv", index=False)
counts = team.strategy_r6.value_counts().reindex(["Zero RB (0)","WR-heavy (1)","Balanced (2)","RB-heavy (3+)"])
print(f"Excluded {len(unbalanced_drafts)} leagues with early traded-pick imbalance.")
print(counts.to_string())
_SECTION_INTERPRETATION = f"Excluding {len(unbalanced_drafts)} leagues with unequal early pick ownership preserves a fixed six-pick Round 6 budget. All four prespecified builds still clear the support gate; the smallest is {counts.idxmin()} with {int(counts.min()):,} teams."
# CELL [build checkpoint and pick panels]
checkpoint_rows = []
base_columns = ["league_id","season","draft_id","roster_id","manager_hash","draft_slot","draft_slot_band","scoring_type","rb_start_slots","wr_start_slots","flex_start_slots","regular_season_points","regular_season_weeks","points_per_week","points_per_week_above_league","points_zscore","points_rank","top_6_points","top_regular_season_scorer"]
for checkpoint in [2, 4, 6, 8]:
    temp = team[base_columns].copy()
    temp["checkpoint"] = checkpoint
    temp["rb_count"] = team[f"rb_count_r{checkpoint}"]
    temp["wr_count"] = team[f"wr_count_r{checkpoint}"]
    temp["non_rbwr_count"] = team[f"non_rbwr_count_r{checkpoint}"]
    temp["rb_count_label"] = temp.rb_count.map(lambda x: "4+" if x >= 4 else str(int(x)))
    checkpoint_rows.append(temp)
checkpoint_panel = pd.concat(checkpoint_rows, ignore_index=True)
checkpoint_panel.to_csv(PROCESSED / "team_checkpoint_panel.csv", index=False)
early = draft_picks.loc[draft_picks["round"].le(8) & draft_picks.player_position.isin(["RB","WR"])].copy()
early = early.merge(team[base_columns + ["strategy_r6"]], on=["league_id","season","draft_id","roster_id"], how="inner")
early.to_csv(PROCESSED / "early_rb_wr_picks.csv", index=False)
print(f"Wrote {len(checkpoint_panel):,} checkpoint rows and {len(early):,} early RB/WR pick rows.")
_SECTION_INTERPRETATION = "The checkpoint panel preserves one row per team per prespecified round, while the pick panel preserves one row per early RB/WR selection. This separates the team-level strategy estimand from the player-level availability mechanism."
# CELL [validate and save manifest]
assert len(team) == 12 * len(eligible_ids)
assert team.groupby("draft_id").size().eq(12).all()
for checkpoint in [2,4,6,8]:
    total = team[f"rb_count_r{checkpoint}"] + team[f"wr_count_r{checkpoint}"] + team[f"non_rbwr_count_r{checkpoint}"]
    assert total.eq(checkpoint).all()
assert np.isclose(team.top_6_points.sum(), 6 * len(eligible_ids))
assert np.isclose(team.top_regular_season_scorer.sum(), len(eligible_ids))
manifest = {
    "source_primary_leagues": int(leagues.primary_sample.sum()),
    "retained_league_seasons": int(len(eligible_ids)),
    "retained_team_seasons": int(len(team)),
    "excluded_otherwise_eligible_standard_leagues": excluded_standard,
    "excluded_early_pick_trade_leagues": int(len(unbalanced_drafts)),
    "retained_by_season": {str(k):int(v) for k,v in team.groupby("season").draft_id.nunique().items()},
    "retained_by_scoring": {str(k):int(v) for k,v in eligible_leagues.groupby("scoring_type").draft_id.nunique().items()},
    "strategy_support": {str(k):int(v) for k,v in team.strategy_r6.value_counts().items()},
    "first_round_rb_wr_teams": int(team.first_round_position.isin(["RB","WR"]).sum()),
    "lineup_settings_coverage": coverage,
}
(ARTIFACTS / "panel_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(json.dumps(manifest, indent=2))
_SECTION_INTERPRETATION = f"All accounting gates pass for {manifest['retained_league_seasons']:,} balanced league-seasons and {manifest['retained_team_seasons']:,} teams. These checks establish internal consistency; they do not remove manager-selection confounding or turn the associations into causal effects."
# CELL [preparation coverage chart]
coverage_table = team.groupby(["season","scoring_type"]).draft_id.nunique().unstack(fill_value=0)
traces = []
for scoring, color in [("ppr","#2563eb"),("half_ppr","#f97316")]:
    values = coverage_table[scoring] if scoring in coverage_table else pd.Series(0,index=coverage_table.index)
    traces.append({"type":"bar","name":scoring.replace("_"," ").upper(),"x":coverage_table.index.astype(str).tolist(),"y":values.astype(int).tolist(),"marker":{"color":color}})
write_chart("preparation_01_coverage_by_season.html", traces, {"title":"Retained conventional-lineup leagues by season","barmode":"stack","xaxis":{"title":"Season","type":"category"},"yaxis":{"title":"League-seasons"}})
latest = int(coverage_table.sum(axis=1).idxmax()); latest_n = int(coverage_table.sum(axis=1).max())
_SECTION_INTERPRETATION = f"Coverage is concentrated in recent seasons, peaking at {latest_n:,} leagues in {latest}. Pooled estimates therefore reflect the modern draft environment more heavily; season-specific and forward tests are necessary before treating the pooled leader as stable."
''',
    )


write(
    "02_eda.ipynb",
    "NB02: exploratory analysis",
    "Describes Round 6 strategy performance, practical magnitude, support, exact RB counts, checkpoint development, season stability, scoring-format variation, and categorical association strength.",
    COMMON + '''# CELL [prepare eda summaries]
import json
import numpy as np
import pandas as pd
team = pd.read_csv(PROCESSED / "team_strategy_panel.csv", dtype={"league_id":str,"draft_id":str,"first_round_player_id":str})
checkpoint = pd.read_csv(PROCESSED / "team_checkpoint_panel.csv", dtype={"league_id":str,"draft_id":str})
order = ["Zero RB (0)","WR-heavy (1)","Balanced (2)","RB-heavy (3+)"]
summary = team.groupby("strategy_r6", as_index=False).agg(n=("points_zscore","size"),leagues=("draft_id","nunique"),mean_points_zscore=("points_zscore","mean"),mean_points_per_week_above_league=("points_per_week_above_league","mean"),top_6_rate=("top_6_points","mean"),top_scorer_rate=("top_regular_season_scorer","mean"),mean_finish=("points_rank","mean"))
summary["strategy_r6"] = pd.Categorical(summary.strategy_r6, order, ordered=True); summary = summary.sort_values("strategy_r6")
exact = team.groupby("rb_count_r6", as_index=False).agg(n=("points_zscore","size"),leagues=("draft_id","nunique"),mean_points_zscore=("points_zscore","mean"),mean_points_per_week_above_league=("points_per_week_above_league","mean"),top_6_rate=("top_6_points","mean"))
checkpoint_summary = checkpoint.groupby(["checkpoint","rb_count_label"],as_index=False).agg(n=("points_zscore","size"),leagues=("draft_id","nunique"),mean_points_zscore=("points_zscore","mean"),top_6_rate=("top_6_points","mean"))
by_season = team.groupby(["season","strategy_r6"],as_index=False).agg(n=("points_zscore","size"),mean_points_zscore=("points_zscore","mean"),top_6_rate=("top_6_points","mean"))
by_format = team.groupby(["scoring_type","strategy_r6"],as_index=False).agg(n=("points_zscore","size"),mean_points_zscore=("points_zscore","mean"),top_6_rate=("top_6_points","mean"))
summary.to_csv(ARTIFACTS / "eda_strategy_summary.csv", index=False); exact.to_csv(ARTIFACTS / "eda_exact_rb_count.csv", index=False); checkpoint_summary.to_csv(ARTIFACTS / "eda_checkpoint_summary.csv", index=False); by_season.to_csv(ARTIFACTS / "eda_strategy_by_season.csv", index=False); by_format.to_csv(ARTIFACTS / "eda_strategy_by_format.csv", index=False)
print(summary.to_string(index=False))
leader = summary.sort_values("mean_points_zscore",ascending=False).iloc[0]
laggard = summary.sort_values("mean_points_zscore").iloc[0]
_SECTION_INTERPRETATION = f"Descriptively, {leader.strategy_r6} leads at {leader.mean_points_zscore:+.3f} z while {laggard.strategy_r6} trails at {laggard.mean_points_zscore:+.3f}, a {leader.mean_points_zscore-laggard.mean_points_zscore:.3f}-z spread. That is large enough to investigate, but no recommendation changes until draft slot, season, scoring, lineup, and early QB/TE spending are adjusted."
# CELL [strategy scoring chart]
write_chart("eda_01_strategy_points.html", [{"type":"bar","x":summary.strategy_r6.astype(str).tolist(),"y":summary.mean_points_zscore.round(4).tolist(),"marker":{"color":["#a855f7","#3b82f6","#14b8a6","#f97316"]},"customdata":summary[["n","leagues"]].values.tolist(),"hovertemplate":"%{x}<br>mean z=%{y:.3f}<br>teams=%{customdata[0]:,}<br>leagues=%{customdata[1]:,}<extra></extra>"}], {"title":"Round 6 RB/WR build and regular-season scoring","xaxis":{"title":"RBs selected through Round 6"},"yaxis":{"title":"Mean within-league points z-score","zeroline":True},"showlegend":False})
leader = summary.loc[summary.mean_points_zscore.idxmax()]
_SECTION_INTERPRETATION = f"The unadjusted scoring leader is {leader.strategy_r6} ({leader.mean_points_zscore:+.3f} z). This is the first indication of which allocation may be preferable, but it can still reflect where teams drafted, how often they selected QB/TE early, and which seasons favored each build."
# CELL [practical points chart]
write_chart("eda_02_practical_points_per_week.html", [{"type":"bar","x":summary.strategy_r6.astype(str).tolist(),"y":summary.mean_points_per_week_above_league.round(3).tolist(),"marker":{"color":["#a855f7","#3b82f6","#14b8a6","#f97316"]},"customdata":summary.mean_finish.round(2).tolist(),"hovertemplate":"%{x}<br>points/week vs league=%{y:+.2f}<br>mean finish=%{customdata:.2f}<extra></extra>"}], {"title":"Practical scoring scale of each Round 6 build","xaxis":{"title":"Strategy"},"yaxis":{"title":"Points per week above league average","zeroline":True},"showlegend":False})
best = summary.loc[summary.mean_points_per_week_above_league.idxmax()]; worst = summary.loc[summary.mean_points_per_week_above_league.idxmin()]
_SECTION_INTERPRETATION = f"The descriptive best-to-worst gap is {best.mean_points_per_week_above_league-worst.mean_points_per_week_above_league:.2f} league-relative points per week. That is practically meaningful over a season, so even a modest standardized gap could affect draft construction; observational confounding still prevents reading this as points caused by the strategy."
# CELL [top six chart]
write_chart("eda_03_strategy_top6.html", [{"type":"bar","x":summary.strategy_r6.astype(str).tolist(),"y":summary.top_6_rate.round(4).tolist(),"marker":{"color":["#a855f7","#3b82f6","#14b8a6","#f97316"]},"hovertemplate":"%{x}<br>top-six rate=%{y:.1%}<extra></extra>"}], {"title":"Top-half scoring rate by Round 6 build","xaxis":{"title":"Strategy"},"yaxis":{"title":"Top-six points finish","tickformat":".0%","zeroline":False},"shapes":[{"type":"line","x0":-0.5,"x1":3.5,"y0":0.5,"y1":0.5,"line":{"color":"#f8fafc","dash":"dash"}}],"showlegend":False})
best = summary.loc[summary.top_6_rate.idxmax()]; worst = summary.loc[summary.top_6_rate.idxmin()]
_SECTION_INTERPRETATION = f"{best.strategy_r6} has the highest descriptive top-six rate ({best.top_6_rate:.1%}), {best.top_6_rate-worst.top_6_rate:+.1%} above {worst.strategy_r6}. This outcome translates the scoring difference into the project's decision target, but the adjusted and forward tests determine whether the advantage survives."
# CELL [strategy support chart]
write_chart("eda_04_strategy_support.html", [{"type":"bar","x":summary.strategy_r6.astype(str).tolist(),"y":summary.n.astype(int).tolist(),"marker":{"color":"#64748b"},"customdata":summary.leagues.astype(int).tolist(),"hovertemplate":"%{x}<br>teams=%{y:,}<br>leagues=%{customdata:,}<extra></extra>"}], {"title":"Support behind each Round 6 build","xaxis":{"title":"Strategy"},"yaxis":{"title":"Team-seasons"},"showlegend":False})
small = summary.loc[summary.n.idxmin()]
_SECTION_INTERPRETATION = f"The least common build, {small.strategy_r6}, still has {int(small.n):,} teams from {int(small.leagues):,} leagues. It is estimable, but its interval should be wider and its season/subgroup results should carry less weight than the larger balanced and WR-heavy groups."
# CELL [exact rb count chart]
supported_exact = exact.loc[exact.n.ge(100)].copy()
write_chart("eda_05_exact_rb_count.html", [{"type":"scatter","mode":"lines+markers+text","x":supported_exact.rb_count_r6.astype(int).tolist(),"y":supported_exact.mean_points_zscore.round(4).tolist(),"text":[f"n={n:,}" for n in supported_exact.n.astype(int)],"textposition":"top center","line":{"color":"#38bdf8","width":3},"marker":{"size":11},"hovertemplate":"%{x} RBs<br>mean z=%{y:.3f}<br>%{text}<extra></extra>"}], {"title":"Exact RB count through Round 6","xaxis":{"title":"RBs selected in Rounds 1-6","dtick":1},"yaxis":{"title":"Mean points z-score","zeroline":True},"showlegend":False})
best = supported_exact.loc[supported_exact.mean_points_zscore.idxmax()]
_SECTION_INTERPRETATION = f"The supported exact-count curve peaks at {int(best.rb_count_r6)} RBs ({best.mean_points_zscore:+.3f} z). This diagnoses whether a broad category hides curvature, but exact counts were not the headline bins and should not be promoted over the prespecified strategy comparison."
# CELL [checkpoint heatmap]
supported = checkpoint_summary.loc[checkpoint_summary.n.ge(100)].copy()
labels = ["0","1","2","3","4+"]
matrix = supported.pivot(index="checkpoint",columns="rb_count_label",values="mean_points_zscore").reindex(index=[2,4,6,8],columns=labels)
counts = supported.pivot(index="checkpoint",columns="rb_count_label",values="n").reindex(index=[2,4,6,8],columns=labels)
z = matrix.astype(object).where(matrix.notna(),None).values.tolist(); custom = counts.astype(object).where(counts.notna(),None).values.tolist()
write_chart("eda_06_checkpoint_heatmap.html", [{"type":"heatmap","x":labels,"y":["Round 2","Round 4","Round 6","Round 8"],"z":z,"customdata":custom,"colorscale":"RdBu","zmid":0,"colorbar":{"title":"Mean z"},"hovertemplate":"%{y}<br>%{x} RBs<br>mean z=%{z:.3f}<br>n=%{customdata:,}<extra></extra>"}], {"title":"How the RB-count association develops across the draft","xaxis":{"title":"RBs selected by checkpoint"},"yaxis":{"title":"Checkpoint"}})
leaders = supported.sort_values(["checkpoint","mean_points_zscore"],ascending=[True,False]).groupby("checkpoint").first().reset_index()
leader_text = "; ".join(f"R{int(r.checkpoint)}: {r.rb_count_label} RB" for r in leaders.itertuples())
_SECTION_INTERPRETATION = f"The descriptive leader changes across checkpoints ({leader_text}). That means the study should answer a Round 6 allocation question, not claim that one positional rule applies unchanged from the opening turn through Round 8."
# CELL [season stability chart]
traces=[]
colors={"Zero RB (0)":"#a855f7","WR-heavy (1)":"#3b82f6","Balanced (2)":"#14b8a6","RB-heavy (3+)":"#f97316"}
for label in order:
    x=by_season.loc[by_season.strategy_r6.eq(label)]
    traces.append({"type":"scatter","mode":"lines+markers","name":label,"x":x.season.astype(str).tolist(),"y":x.mean_points_zscore.round(4).tolist(),"line":{"color":colors[label],"width":2},"customdata":x.n.astype(int).tolist(),"hovertemplate":"%{x}<br>mean z=%{y:.3f}<br>n=%{customdata:,}<extra>%{fullData.name}</extra>"})
write_chart("eda_07_strategy_by_season.html",traces,{"title":"Round 6 strategy performance by season","xaxis":{"title":"Season","type":"category"},"yaxis":{"title":"Mean points z-score","zeroline":True}})
season_winners=by_season.sort_values(["season","mean_points_zscore"],ascending=[True,False]).groupby("season").first().strategy_r6
pooled=summary.loc[summary.mean_points_zscore.idxmax(),"strategy_r6"]; wins=int(season_winners.eq(pooled).sum())
_SECTION_INTERPRETATION = f"The pooled descriptive leader, {pooled}, leads in {wins} of {season_winners.size} individual seasons. Any reversals matter directly: a pooled edge that does not repeat forward should be graded as exploratory rather than a universal draft rule."
# CELL [format interaction chart]
traces=[]
for scoring,color in [("ppr","#2563eb"),("half_ppr","#f97316")]:
    x=by_format.loc[by_format.scoring_type.eq(scoring)].copy(); x["strategy_r6"]=pd.Categorical(x.strategy_r6,order,ordered=True); x=x.sort_values("strategy_r6")
    traces.append({"type":"bar","name":scoring.replace("_"," ").upper(),"x":x.strategy_r6.astype(str).tolist(),"y":x.mean_points_zscore.round(4).tolist(),"customdata":x.n.astype(int).tolist(),"marker":{"color":color},"hovertemplate":"%{x}<br>mean z=%{y:.3f}<br>n=%{customdata:,}<extra>%{fullData.name}</extra>"})
write_chart("eda_08_strategy_by_format.html",traces,{"title":"Round 6 strategy by reception scoring","barmode":"group","xaxis":{"title":"Strategy"},"yaxis":{"title":"Mean points z-score","zeroline":True}})
format_leaders=by_format.sort_values(["scoring_type","mean_points_zscore"],ascending=[True,False]).groupby("scoring_type").first().strategy_r6.to_dict()
_SECTION_INTERPRETATION = f"The descriptive PPR leader is {format_leaders.get('ppr')} and the half-PPR leader is {format_leaders.get('half_ppr')}. A format-specific recommendation is justified only if the adjusted subgroup intervals preserve that separation; these bars alone do not."
# CELL [categorical association chart]
grand=team.points_zscore.mean(); total=((team.points_zscore-grand)**2).sum(); between=sum(len(group)*(group.points_zscore.mean()-grand)**2 for _,group in team.groupby("strategy_r6")); eta2=float(between/total); eta=float(np.sqrt(eta2))
association={"eta":eta,"eta_squared":eta2,"n":len(team),"groups":len(order)}
(ARTIFACTS/"eda_categorical_association.json").write_text(json.dumps(association,indent=2),encoding="utf-8")
write_chart("eda_09_categorical_association.html",[{"type":"bar","x":["Eta","Eta-squared"],"y":[eta,eta2],"marker":{"color":["#38bdf8","#f97316"]},"text":[f"{eta:.3f}",f"{eta2:.3%}"],"textposition":"outside","hovertemplate":"%{x}=%{y:.4f}<extra></extra>"}],{"title":"Unadjusted categorical association with team scoring","xaxis":{"title":"Association measure"},"yaxis":{"title":"Value","rangemode":"tozero"},"showlegend":False})
_SECTION_INTERPRETATION = f"Round 6 strategy has categorical eta {eta:.3f}, corresponding to eta-squared {eta2:.3%}. Thus the raw build labels explain only {eta2:.2%} of team scoring variation; even a real average edge is small relative to player outcomes, injuries, waivers, and manager decisions."
''',
)


write(
    "03_inference_and_robustness.ipynb",
    "NB03: adjusted inference and robustness",
    "Estimates the prespecified Round 6 strategy comparison with league-cluster uncertainty, then checks scoring formats, draft-slot bands, exact common lineups, and secondary checkpoints.",
    COMMON + '''# CELL [define inference model]
import json
import numpy as np
import pandas as pd
team = pd.read_csv(PROCESSED / "team_strategy_panel.csv", dtype={"league_id":str,"draft_id":str,"first_round_player_id":str})
checkpoint = pd.read_csv(PROCESSED / "team_checkpoint_panel.csv", dtype={"league_id":str,"draft_id":str})
config = json.loads((ARTIFACTS / "study_config.json").read_text(encoding="utf-8"))
strategy_order = config["primary_strategies"]
controls = ["non_rbwr_count_r6","draft_slot","season","scoring_type","wr_start_slots","flex_start_slots"]
''' + MODEL_HELPERS + '''
_SECTION_INTERPRETATION = "The model treats strategy and every adjustment variable categorically. At a fixed number of non-RB/WR selections, changing the RB category necessarily replaces WR draft capital; resampling complete leagues preserves dependence among the 12 teams sharing a draft board."
# CELL [run primary inference]
outcomes=["points_zscore","points_per_week_above_league","top_6_points"]
inference, contrasts = clustered_model(team,"strategy_r6",strategy_order,"Balanced (2)",controls,outcomes,config["bootstrap_replicates"],config["random_seed"])
inference.to_csv(ARTIFACTS/"inference_strategy_intervals.csv",index=False); contrasts.to_csv(ARTIFACTS/"inference_strategy_contrasts.csv",index=False)
z=inference.loc[inference.outcome.eq("points_zscore")].sort_values("estimate",ascending=False)
winner=z.iloc[0]; runner=z.iloc[1]
row=contrasts.loc[contrasts.outcome.eq("points_zscore") & (((contrasts.left==winner.level)&(contrasts.right==runner.level))|((contrasts.left==runner.level)&(contrasts.right==winner.level)))].iloc[0]
if row.left != winner.level:
    gap,lo,hi=-row.difference,-row.ci_high,-row.ci_low
else:
    gap,lo,hi=row.difference,row.ci_low,row.ci_high
print(z.to_string(index=False)); print(f"\\nWinner minus runner-up: {gap:+.3f} [{lo:+.3f}, {hi:+.3f}]")
_SECTION_INTERPRETATION = f"After adjustment, {winner.level} ranks first at {winner.estimate:+.3f} z. Its gap over {runner.level} is {gap:+.3f} z (95% league-bootstrap interval {lo:+.3f} to {hi:+.3f}). {'The interval excludes zero, so the pooled association distinguishes the top two builds.' if lo>0 else 'The interval includes zero, so the data do not distinguish the top two builds and the recommendation must remain a supported range rather than a single winner.'}"
# CELL [adjusted strategy chart]
z=z.set_index("level").reindex(strategy_order).reset_index()
write_chart("inference_01_adjusted_strategy.html",[{"type":"bar","x":z.level.tolist(),"y":z.estimate.round(4).tolist(),"marker":{"color":["#a855f7","#3b82f6","#14b8a6","#f97316"]},"error_y":{"type":"data","symmetric":False,"array":(z.ci_high-z.estimate).round(4).tolist(),"arrayminus":(z.estimate-z.ci_low).round(4).tolist()},"customdata":z.n.astype(int).tolist(),"hovertemplate":"%{x}<br>adjusted z=%{y:.3f}<br>n=%{customdata:,}<extra></extra>"}],{"title":"Adjusted Round 6 strategy estimates","xaxis":{"title":"Strategy"},"yaxis":{"title":"Covariate-standardized points z-score","zeroline":True},"showlegend":False})
best=z.loc[z.estimate.idxmax()]
_SECTION_INTERPRETATION = f"The adjusted chart places {best.level} highest, but the interval overlap shows the uncertainty around ranking whole strategies. The practical recommendation depends on pairwise contrasts and forward stability, not on choosing the tallest bar by eye."
# CELL [balanced contrast chart]
diff=inference.loc[inference.outcome.eq("points_zscore")].copy(); diff=diff.set_index("level").reindex(strategy_order).reset_index()
write_chart("inference_02_contrasts_vs_balanced.html",[{"type":"bar","x":diff.level.tolist(),"y":diff.difference_vs_reference.round(4).tolist(),"marker":{"color":["#a855f7","#3b82f6","#14b8a6","#f97316"]},"error_y":{"type":"data","symmetric":False,"array":(diff.difference_ci_high-diff.difference_vs_reference).round(4).tolist(),"arrayminus":(diff.difference_vs_reference-diff.difference_ci_low).round(4).tolist()},"hovertemplate":"%{x}<br>difference vs 2 RB=%{y:+.3f}<extra></extra>"}],{"title":"Adjusted difference from a balanced two-RB start","xaxis":{"title":"Strategy"},"yaxis":{"title":"Points z-score difference","zeroline":True},"showlegend":False})
furthest=diff.loc[diff.difference_vs_reference.abs().idxmax()]
_SECTION_INTERPRETATION = f"Relative to two RBs through Round 6, the largest adjusted departure is {furthest.level} at {furthest.difference_vs_reference:+.3f} z (95% interval {furthest.difference_ci_low:+.3f} to {furthest.difference_ci_high:+.3f}). This is the direct RB-for-WR allocation contrast; intervals crossing zero do not justify declaring that build better or worse."
# CELL [run robustness models]
specs=[("PPR",team.scoring_type.eq("ppr")),("Half-PPR",team.scoring_type.eq("half_ppr")),("Early slot",team.draft_slot_band.eq("Early (1-4)")),("Middle slot",team.draft_slot_band.eq("Middle (5-8)")),("Late slot",team.draft_slot_band.eq("Late (9-12)")),("2RB/2WR/2FLEX",team.rb_start_slots.eq(2)&team.wr_start_slots.eq(2)&team.flex_start_slots.eq(2))]
robust=[]
for index,(name,mask) in enumerate(specs):
    data=team.loc[mask].copy(); counts=data.strategy_r6.value_counts(); levels=[x for x in strategy_order if counts.get(x,0)>=100]
    if "Balanced (2)" not in levels or len(levels)<2: continue
    local_controls=[x for x in controls if data[x].nunique()>1]
    result,_=clustered_model(data,"strategy_r6",levels,"Balanced (2)",local_controls,["points_zscore"],config["robustness_bootstrap_replicates"],config["random_seed"]+100+index)
    result["specification"]=name; robust.append(result)
robustness=pd.concat(robust,ignore_index=True); robustness.to_csv(ARTIFACTS/"inference_robustness_subgroups.csv",index=False)
winners=robustness.sort_values(["specification","estimate"],ascending=[True,False]).groupby("specification").first().reset_index()[["specification","level","estimate"]]
print(winners.to_string(index=False))
winner_counts=winners.level.value_counts(); stable=winner_counts.index[0]; stable_n=int(winner_counts.iloc[0])
_SECTION_INTERPRETATION = f"{stable} leads in {stable_n} of {len(winners)} prespecified robustness specifications. Subgroup leadership is evidence about transportability, not a license to select whichever slice favors a preferred strategy; wide subgroup intervals remain important."
# CELL [robustness chart]
traces=[]
colors={"Zero RB (0)":"#a855f7","WR-heavy (1)":"#3b82f6","Balanced (2)":"#14b8a6","RB-heavy (3+)":"#f97316"}
for level in strategy_order:
    x=robustness.loc[robustness.level.eq(level)]
    traces.append({"type":"scatter","mode":"markers","name":level,"x":x.specification.tolist(),"y":x.estimate.round(4).tolist(),"marker":{"size":11,"color":colors[level]},"error_y":{"type":"data","symmetric":False,"array":(x.ci_high-x.estimate).round(4).tolist(),"arrayminus":(x.estimate-x.ci_low).round(4).tolist()},"hovertemplate":"%{x}<br>adjusted z=%{y:.3f}<extra>%{fullData.name}</extra>"})
write_chart("inference_03_robustness.html",traces,{"title":"Adjusted strategy estimates across prespecified subgroups","xaxis":{"title":"Specification","tickangle":-20},"yaxis":{"title":"Adjusted points z-score","zeroline":True}})
_SECTION_INTERPRETATION = "The robustness chart tests whether the pooled ordering survives plausible draft contexts. A format or slot-specific separation only changes the recommendation when its own interval is informative and the direction is not an isolated subgroup reversal."
# CELL [checkpoint inference]
checkpoint_results=[]
for index,cp in enumerate([4,6,8]):
    data=checkpoint.loc[checkpoint.checkpoint.eq(cp)].copy(); counts=data.rb_count_label.value_counts(); levels=[x for x in ["0","1","2","3","4+"] if counts.get(x,0)>=100]
    reference="2" if "2" in levels else levels[np.argmax([counts[x] for x in levels])]
    local_controls=["non_rbwr_count","draft_slot","season","scoring_type","wr_start_slots","flex_start_slots"]
    result,_=clustered_model(data,"rb_count_label",levels,reference,local_controls,["points_zscore"],config["robustness_bootstrap_replicates"],config["random_seed"]+300+index)
    result["checkpoint"]=cp; checkpoint_results.append(result)
checkpoint_inference=pd.concat(checkpoint_results,ignore_index=True); checkpoint_inference.to_csv(ARTIFACTS/"inference_checkpoint_intervals.csv",index=False)
leaders=checkpoint_inference.sort_values(["checkpoint","estimate"],ascending=[True,False]).groupby("checkpoint").first().reset_index()
print(leaders[["checkpoint","level","estimate","ci_low","ci_high"]].to_string(index=False))
_SECTION_INTERPRETATION = "; ".join(f"At Round {int(row.checkpoint)}, {row.level} RBs has the highest adjusted estimate ({row.estimate:+.3f} z)" for row in leaders.itertuples()) + ". These secondary checkpoints explain when the allocation pattern emerges; they cannot supersede the prespecified Round 6 test."
# CELL [checkpoint inference chart]
traces=[]
for cp,color in [(4,"#38bdf8"),(6,"#14b8a6"),(8,"#f97316")]:
    x=checkpoint_inference.loc[checkpoint_inference.checkpoint.eq(cp)]
    traces.append({"type":"scatter","mode":"lines+markers","name":f"Round {cp}","x":x.level.tolist(),"y":x.estimate.round(4).tolist(),"line":{"color":color,"width":3},"marker":{"size":10},"error_y":{"type":"data","symmetric":False,"array":(x.ci_high-x.estimate).round(4).tolist(),"arrayminus":(x.estimate-x.ci_low).round(4).tolist()},"hovertemplate":"%{x} RBs<br>adjusted z=%{y:.3f}<extra>%{fullData.name}</extra>"})
write_chart("inference_04_checkpoint_intervals.html",traces,{"title":"Adjusted RB counts at secondary checkpoints","xaxis":{"title":"RBs selected by checkpoint","type":"category","categoryorder":"array","categoryarray":["0","1","2","3","4+"]},"yaxis":{"title":"Adjusted points z-score","zeroline":True}})
_SECTION_INTERPRETATION = "The checkpoint curves show whether an early allocation edge persists or reverses by Round 8. Because the supported categories and available alternatives change over the draft, these are trajectory diagnostics rather than interchangeable estimates of the Round 6 strategy effect."
''',
    )


write(
    "04_out_of_sample_validation.ipynb",
    "NB04: forward-season validation",
    "Uses expanding training windows to select a supported Round 6 strategy without access to the next season, then measures its next-season scoring and top-six differences.",
    COMMON + '''# CELL [calculate forward tests]
import json
import numpy as np
import pandas as pd
team=pd.read_csv(PROCESSED/"team_strategy_panel.csv",dtype={"league_id":str,"draft_id":str,"first_round_player_id":str})
config=json.loads((ARTIFACTS/"study_config.json").read_text(encoding="utf-8"))
strategy_order=config["primary_strategies"]
controls=["non_rbwr_count_r6","draft_slot","season","scoring_type","wr_start_slots","flex_start_slots"]
''' + MODEL_HELPERS + '''
rows=[]
for year in sorted(team.season.unique())[1:]:
    train=team.loc[team.season.lt(year)].copy(); test=team.loc[team.season.eq(year)].copy()
    counts=train.strategy_r6.value_counts(); supported=[x for x in strategy_order if counts.get(x,0)>=config["minimum_cell_n"]]
    if len(supported)<2: continue
    reference="Balanced (2)" if "Balanced (2)" in supported else supported[np.argmax([counts[x] for x in supported])]
    training_estimates=point_model(train,"strategy_r6",supported,reference,controls,["points_zscore"])
    selected=max(supported,key=lambda x:training_estimates[x][0])
    selected_test=test.loc[test.strategy_r6.eq(selected)]; other_test=test.loc[~test.strategy_r6.eq(selected)]
    if len(selected_test)<20 or len(other_test)<20: continue
    test=test.copy(); test["selected_flag"]=np.where(test.strategy_r6.eq(selected),"Selected","Other")
    test_controls=[x for x in controls if test[x].nunique()>1]
    adjusted=point_model(test,"selected_flag",["Other","Selected"],"Other",test_controls,["points_zscore","top_6_points"])
    adjusted_diff=adjusted["Selected"]-adjusted["Other"]
    rows.append({"test_season":int(year),"selected_strategy":selected,"supported_training_strategies":" | ".join(supported),"train_n":len(train),"test_n":len(test),"test_selected_n":len(selected_test),"test_z_difference":float(selected_test.points_zscore.mean()-other_test.points_zscore.mean()),"test_adjusted_z_difference":float(adjusted_diff[0]),"test_top6_difference":float(selected_test.top_6_points.mean()-other_test.top_6_points.mean()),"test_adjusted_top6_difference":float(adjusted_diff[1])})
validation=pd.DataFrame(rows); validation.to_csv(ARTIFACTS/"validation_forward_seasons.csv",index=False)
print(validation.to_string(index=False))
positive=int(validation.test_adjusted_z_difference.gt(0).sum())
_SECTION_INTERPRETATION = f"The expanding-window procedure produces {len(validation)} genuine next-season tests; the training-selected build is positive after adjustment in {positive}. This is the main protection against mistaking a pooled historical winner for a repeatable draft rule."
# CELL [forward scoring chart]
colors=["#14b8a6" if value>0 else "#ef4444" for value in validation.test_adjusted_z_difference]
write_chart("validation_01_forward_scoring.html",[{"type":"bar","x":validation.test_season.astype(str).tolist(),"y":validation.test_adjusted_z_difference.round(4).tolist(),"marker":{"color":colors},"customdata":validation[["selected_strategy","test_selected_n"]].values.tolist(),"hovertemplate":"%{x}<br>adjusted z difference=%{y:+.3f}<br>selected=%{customdata[0]}<br>selected n=%{customdata[1]:,}<extra></extra>"}],{"title":"Forward-season scoring difference for the training-selected build","xaxis":{"title":"Test season","type":"category"},"yaxis":{"title":"Selected minus other teams: adjusted points z","zeroline":True},"showlegend":False})
mean_diff=float(validation.test_adjusted_z_difference.mean()); positive=int(validation.test_adjusted_z_difference.gt(0).sum())
_SECTION_INTERPRETATION = f"Across forward tests, the selected build averages {mean_diff:+.3f} adjusted z and is positive in {positive} of {len(validation)} seasons. Reversals reduce confidence even when the average is favorable, because a usable draft strategy should survive changes in the player pool and ADP environment."
# CELL [forward top six chart]
colors=["#14b8a6" if value>0 else "#ef4444" for value in validation.test_adjusted_top6_difference]
write_chart("validation_02_forward_top6.html",[{"type":"bar","x":validation.test_season.astype(str).tolist(),"y":validation.test_adjusted_top6_difference.round(4).tolist(),"marker":{"color":colors},"customdata":validation.selected_strategy.tolist(),"hovertemplate":"%{x}<br>adjusted top-six difference=%{y:+.1%}<br>selected=%{customdata}<extra></extra>"}],{"title":"Forward-season top-six difference for the selected build","xaxis":{"title":"Test season","type":"category"},"yaxis":{"title":"Selected minus other teams: top-six rate","tickformat":".0%","zeroline":True},"showlegend":False})
mean_top6=float(validation.test_adjusted_top6_difference.mean())
_SECTION_INTERPRETATION = f"The training-selected build changes next-season top-six probability by {mean_top6:+.1%} on average. This is the practical decision scale; if its sign or season pattern disagrees with scoring z, the evidence grade should fall rather than privileging the more favorable outcome."
# CELL [selection stability chart]
positions={label:index for index,label in enumerate(strategy_order)}
write_chart("validation_03_selection_stability.html",[{"type":"scatter","mode":"markers+text","x":validation.test_season.astype(str).tolist(),"y":[positions[x] for x in validation.selected_strategy],"text":[f"{x:+.2f}" for x in validation.test_adjusted_z_difference],"textposition":"top center","marker":{"size":14,"color":validation.test_adjusted_z_difference.round(4).tolist(),"colorscale":"RdBu","cmid":0,"showscale":True,"colorbar":{"title":"Test z diff"}},"customdata":validation.selected_strategy.tolist(),"hovertemplate":"%{x}<br>selected=%{customdata}<br>test z=%{text}<extra></extra>"}],{"title":"Training-selected strategy and next-season result","xaxis":{"title":"Test season","type":"category"},"yaxis":{"title":"Selected strategy","tickmode":"array","tickvals":list(positions.values()),"ticktext":list(positions.keys())},"showlegend":False})
selection_counts=validation.selected_strategy.value_counts(); most=selection_counts.index[0]; count=int(selection_counts.iloc[0])
_SECTION_INTERPRETATION = f"{most} is selected in {count} of {len(validation)} expanding training windows. Frequent selection plus positive tests would support a stable recommendation; shifting selections or negative tests indicate that the best build depends on era rather than representing a fixed positional law."
''',
)


write(
    "05_availability_sensitivity.ipynb",
    "NB05: early-pick availability sensitivity",
    "Links every RB and WR selected in Rounds 1-8 to nflverse weekly participation, describes positional availability, and repeats the Round 6 comparison among teams whose linked early RB/WR picks were all sufficiently available.",
    COMMON + '''# CELL [link early pick availability]
import json
import re
import unicodedata
import numpy as np
import pandas as pd
early=pd.read_csv(PROCESSED/"early_rb_wr_picks.csv",dtype={"league_id":str,"draft_id":str,"sleeper_player_id":str})
team=pd.read_csv(PROCESSED/"team_strategy_panel.csv",dtype={"league_id":str,"draft_id":str,"first_round_player_id":str})
participation=pd.read_csv(SOURCE_DRAFT/"data/cache/nflverse_weekly_participation_2018_2025.csv")
def fold(value):
    return re.sub(r"[^a-z0-9]","",unicodedata.normalize("NFKD",str(value)).encode("ascii","ignore").decode().lower())
early["fold_name"]=early.player_name.map(fold); participation["fold_name"]=participation.player_display_name.map(fold)
join_columns=["season","player_position","fold_name"]
names=participation.rename(columns={"position":"player_position"})[join_columns].drop_duplicates(); names["player_linked"]=True
linked=early.merge(names,on=join_columns,how="left")
weeks=early.merge(participation.rename(columns={"position":"player_position"})[["season","player_position","fold_name","week"]],on=join_columns,how="left")
weeks=weeks.loc[weeks.week.isna()|weeks.week.le(weeks.regular_season_weeks)]
pick_keys=["league_id","season","draft_id","roster_id","pick_no","player_position","player_name"]
active=weeks.groupby(pick_keys,as_index=False).week.nunique().rename(columns={"week":"active_weeks"})
linked=linked.merge(active,on=pick_keys,how="left"); linked["player_linked"]=linked.player_linked.fillna(False); linked["active_weeks"]=linked.active_weeks.fillna(0).astype(int)
linked["availability_rate"]=np.where(linked.player_linked,linked.active_weeks/linked.regular_season_weeks,np.nan); linked["available_75"]=linked.player_linked & linked.availability_rate.ge(.75)
linked.to_csv(PROCESSED/"early_pick_availability_panel.csv",index=False)
link_rate=float(linked.player_linked.mean())
print(f"Linked {link_rate:.1%} of {len(linked):,} early RB/WR picks.")
_SECTION_INTERPRETATION = f"Normalized name, season, and position link {link_rate:.1%} of early RB/WR picks to weekly participation. Unlinked picks are retained as unknown rather than mislabeled unavailable; availability conclusions apply only where this fallback linkage succeeds."
# CELL [summarize availability]
round_position=linked.loc[linked.player_linked].groupby(["round","player_position"],as_index=False).agg(n=("pick_no","size"),mean_availability=("availability_rate","mean"),unavailable_rate=("available_75",lambda x:1-x.mean()))
round_position.to_csv(ARTIFACTS/"availability_by_round_position.csv",index=False)
first6=linked.loc[linked["round"].le(6)].copy()
team_availability=first6.groupby(["league_id","season","draft_id","roster_id"],as_index=False).agg(early_rbwr_picks=("pick_no","size"),linked_picks=("player_linked","sum"),available_picks=("available_75","sum"),mean_availability=("availability_rate","mean"))
team_availability["all_linked"]=team_availability.linked_picks.eq(team_availability.early_rbwr_picks)
team_availability["all_available_75"]=team_availability.all_linked & team_availability.available_picks.eq(team_availability.early_rbwr_picks)
team_availability.to_csv(PROCESSED/"team_early_availability.csv",index=False)
analysis=team.merge(team_availability,on=["league_id","season","draft_id","roster_id"],how="left")
analysis["all_linked"]=analysis.all_linked.fillna(False).astype(bool)
analysis["all_available_75"]=analysis.all_available_75.fillna(False).astype(bool)
full=analysis.groupby("strategy_r6",as_index=False).agg(full_n=("points_zscore","size"),full_mean_z=("points_zscore","mean"),all_linked_rate=("all_linked","mean"),all_available_rate=("all_available_75","mean"))
available=analysis.loc[analysis.all_available_75].groupby("strategy_r6",as_index=False).agg(available_n=("points_zscore","size"),available_mean_z=("points_zscore","mean"),available_top6=("top_6_points","mean"))
availability_summary=full.merge(available,on="strategy_r6",how="left"); availability_summary.to_csv(ARTIFACTS/"availability_strategy_summary.csv",index=False)
print(availability_summary.to_string(index=False))
lowest=availability_summary.loc[availability_summary.all_available_rate.idxmin()]
_SECTION_INTERPRETATION = f"{lowest.strategy_r6} has the lowest share of teams with every linked early RB/WR available ({lowest.all_available_rate:.1%}). This can explain part of a build's real-world performance, but filtering on health changes the estimand and cannot replace the injury-inclusive headline."
# CELL [availability by round chart]
traces=[]
for pos,color in [("RB","#f97316"),("WR","#3b82f6")]:
    x=round_position.loc[round_position.player_position.eq(pos)]
    traces.append({"type":"scatter","mode":"lines+markers","name":pos,"x":x["round"].astype(int).tolist(),"y":x.unavailable_rate.round(4).tolist(),"line":{"color":color,"width":3},"customdata":x.n.astype(int).tolist(),"hovertemplate":"Round %{x}<br>unavailable=%{y:.1%}<br>n=%{customdata:,}<extra>%{fullData.name}</extra>"})
write_chart("availability_01_by_round_position.html",traces,{"title":"Early-pick unavailability by position and round","xaxis":{"title":"Draft round","dtick":1},"yaxis":{"title":"Active in fewer than 75% of fantasy weeks","tickformat":".0%"}})
pooled=linked.loc[linked.player_linked].groupby("player_position").available_75.mean(); rb_unavail=1-float(pooled["RB"]); wr_unavail=1-float(pooled["WR"])
_SECTION_INTERPRETATION = f"Across linked picks in Rounds 1-8, RB unavailability is {rb_unavail:.1%} versus {wr_unavail:.1%} for WR, a {rb_unavail-wr_unavail:+.1%} difference. This quantifies the durability mechanism behind RB/WR allocation, but it does not measure replacement value or prove that avoiding RBs improves team scoring."
# CELL [run availability sensitivity]
config=json.loads((ARTIFACTS/"study_config.json").read_text(encoding="utf-8")); strategy_order=config["primary_strategies"]
controls=["non_rbwr_count_r6","draft_slot","season","scoring_type","wr_start_slots","flex_start_slots"]
''' + MODEL_HELPERS + '''
available_data=analysis.loc[analysis.all_available_75].copy(); counts=available_data.strategy_r6.value_counts(); levels=[x for x in strategy_order if counts.get(x,0)>=100]
available_inference,available_contrasts=clustered_model(available_data,"strategy_r6",levels,"Balanced (2)",controls,["points_zscore","top_6_points"],config["robustness_bootstrap_replicates"],config["random_seed"]+500)
available_inference.to_csv(ARTIFACTS/"availability_strategy_inference.csv",index=False); available_contrasts.to_csv(ARTIFACTS/"availability_strategy_contrasts.csv",index=False)
z=available_inference.loc[available_inference.outcome.eq("points_zscore")].sort_values("estimate",ascending=False); leader=z.iloc[0]
print(z.to_string(index=False))
_SECTION_INTERPRETATION = f"When every linked early RB/WR clears the 75% availability threshold, {leader.level} leads at {leader.estimate:+.3f} adjusted z. If this differs from the injury-inclusive leader, availability is a plausible mechanism; because health is post-draft, the conditional result is not the strategy a drafter can guarantee."
# CELL [availability strategy chart]
full_inf=pd.read_csv(ARTIFACTS/"inference_strategy_intervals.csv"); full_z=full_inf.loc[full_inf.outcome.eq("points_zscore"),["level","estimate"]].rename(columns={"estimate":"Full sample"}); avail_z=available_inference.loc[available_inference.outcome.eq("points_zscore"),["level","estimate"]].rename(columns={"estimate":"All early picks available"}); compare=full_z.merge(avail_z,on="level",how="inner")
traces=[]
for column,color in [("Full sample","#64748b"),("All early picks available","#14b8a6")]:
    traces.append({"type":"bar","name":column,"x":compare.level.tolist(),"y":compare[column].round(4).tolist(),"marker":{"color":color},"hovertemplate":"%{x}<br>adjusted z=%{y:.3f}<extra>%{fullData.name}</extra>"})
write_chart("availability_02_strategy_comparison.html",traces,{"title":"Injury-inclusive and all-available strategy estimates","barmode":"group","xaxis":{"title":"Round 6 strategy"},"yaxis":{"title":"Adjusted points z-score","zeroline":True}})
full_leader=compare.loc[compare["Full sample"].idxmax(),"level"]; available_leader=compare.loc[compare["All early picks available"].idxmax(),"level"]
_SECTION_INTERPRETATION = f"The injury-inclusive leader is {full_leader}; the all-available leader is {available_leader}. {'The change in ranking makes availability part of the practical story, but the real-world recommendation remains injury-inclusive.' if full_leader!=available_leader else 'The ranking survives the health screen, so differential availability does not by itself explain the pooled ordering.'}"
''',
)


write(
    "06_first_round_rb_vs_wr.ipynb",
    "NB06: first-round RB versus WR",
    "Answers the prespecified side question overall, by draft-slot band and season, and after conditioning on first-round availability.",
    COMMON + '''# CELL [prepare first round sample]
import json
import numpy as np
import pandas as pd
team=pd.read_csv(PROCESSED/"team_strategy_panel.csv",dtype={"league_id":str,"draft_id":str,"first_round_player_id":str})
first=team.loc[team.first_round_position.isin(["RB","WR"])].copy()
direct=pd.read_csv(SOURCE_DRAFT/"data/processed/first_round_availability_panel.csv",dtype={"league_id":str,"draft_id":str,"roster_id":int,"sleeper_player_id":str})
direct=direct[["league_id","season","draft_id","roster_id","player_linked","availability_rate","first_round_available"]].drop_duplicates(["league_id","season","draft_id","roster_id"])
first=first.merge(direct,on=["league_id","season","draft_id","roster_id"],how="left")
summary=first.groupby("first_round_position",as_index=False).agg(n=("points_zscore","size"),leagues=("draft_id","nunique"),mean_points_zscore=("points_zscore","mean"),top_6_rate=("top_6_points","mean"),linked_rate=("player_linked","mean"),available_rate=("first_round_available","mean"))
summary.to_csv(ARTIFACTS/"first_round_descriptive_summary.csv",index=False)
print(summary.to_string(index=False))
coverage=float(first.player_linked.notna().mean())
_SECTION_INTERPRETATION = f"The first-round side question contains {len(first):,} RB-or-WR teams, with validated availability records for {coverage:.1%}. Exact draft slot must be adjusted because the opportunity set at 1.01 is fundamentally different from the turn."
# CELL [run first round inference]
config=json.loads((ARTIFACTS/"study_config.json").read_text(encoding="utf-8"))
controls=["draft_slot","season","scoring_type","wr_start_slots","flex_start_slots"]
''' + MODEL_HELPERS + '''
fr_inference,fr_contrasts=clustered_model(first,"first_round_position",["WR","RB"],"WR",controls,["points_zscore","points_per_week_above_league","top_6_points"],config["bootstrap_replicates"],config["random_seed"]+600)
fr_inference.to_csv(ARTIFACTS/"first_round_inference.csv",index=False); fr_contrasts.to_csv(ARTIFACTS/"first_round_contrasts.csv",index=False)
contrast=fr_contrasts.loc[fr_contrasts.outcome.eq("points_zscore")].iloc[0]
rb_minus_wr=-contrast.difference if contrast.left=="WR" else contrast.difference
lo=-contrast.ci_high if contrast.left=="WR" else contrast.ci_low; hi=-contrast.ci_low if contrast.left=="WR" else contrast.ci_high
print(fr_inference.to_string(index=False)); print(f"RB minus WR: {rb_minus_wr:+.3f} [{lo:+.3f}, {hi:+.3f}]")
_SECTION_INTERPRETATION = f"After exact slot and format adjustment, first-round RB is {rb_minus_wr:+.3f} z relative to first-round WR (95% league-bootstrap interval {lo:+.3f} to {hi:+.3f}). {'The interval excludes zero, supporting a pooled positional association.' if lo>0 or hi<0 else 'The interval includes zero, so the historical data do not establish a clear overall first-round position edge.'} Player identity and manager skill remain unmeasured confounders."
# CELL [first round adjusted chart]
z=fr_inference.loc[fr_inference.outcome.eq("points_zscore")].set_index("level").reindex(["WR","RB"]).reset_index()
write_chart("first_round_01_adjusted_outcomes.html",[{"type":"bar","x":z.level.tolist(),"y":z.estimate.round(4).tolist(),"marker":{"color":["#3b82f6","#f97316"]},"error_y":{"type":"data","symmetric":False,"array":(z.ci_high-z.estimate).round(4).tolist(),"arrayminus":(z.estimate-z.ci_low).round(4).tolist()},"customdata":z.n.astype(int).tolist(),"hovertemplate":"Round 1 %{x}<br>adjusted z=%{y:.3f}<br>n=%{customdata:,}<extra></extra>"}],{"title":"Adjusted team scoring after a first-round RB or WR","xaxis":{"title":"First-round position"},"yaxis":{"title":"Covariate-standardized points z-score","zeroline":True},"showlegend":False})
leader=z.loc[z.estimate.idxmax()]
_SECTION_INTERPRETATION = f"{leader.level} is the higher adjusted first-round bar. The actionable magnitude is the RB-minus-WR contrast and its interval, not either absolute standardized mean; drafters still choose individual players from slot-dependent opportunity sets."
# CELL [first round slot chart]
slot_rows=[]
for index,band in enumerate(["Early (1-4)","Middle (5-8)","Late (9-12)"]):
    data=first.loc[first.draft_slot_band.eq(band)].copy()
    result,contrast_table=clustered_model(data,"first_round_position",["WR","RB"],"WR",[x for x in controls if data[x].nunique()>1],["points_zscore"],config["robustness_bootstrap_replicates"],config["random_seed"]+700+index)
    rb=result.loc[result.level.eq("RB")].iloc[0]
    slot_rows.append({"slot_band":band,"n":len(data),"rb_minus_wr":rb.difference_vs_reference,"ci_low":rb.difference_ci_low,"ci_high":rb.difference_ci_high})
slot_result=pd.DataFrame(slot_rows); slot_result.to_csv(ARTIFACTS/"first_round_by_slot.csv",index=False)
write_chart("first_round_02_by_slot.html",[{"type":"bar","x":slot_result.slot_band.tolist(),"y":slot_result.rb_minus_wr.round(4).tolist(),"marker":{"color":"#f97316"},"error_y":{"type":"data","symmetric":False,"array":(slot_result.ci_high-slot_result.rb_minus_wr).round(4).tolist(),"arrayminus":(slot_result.rb_minus_wr-slot_result.ci_low).round(4).tolist()},"customdata":slot_result.n.astype(int).tolist(),"hovertemplate":"%{x}<br>RB minus WR=%{y:+.3f}<br>n=%{customdata:,}<extra></extra>"}],{"title":"First-round RB minus WR by draft-slot band","xaxis":{"title":"Draft slot"},"yaxis":{"title":"Adjusted points z difference","zeroline":True},"showlegend":False})
positive=int(slot_result.rb_minus_wr.gt(0).sum())
_SECTION_INTERPRETATION = f"The RB-minus-WR estimate is positive in {positive} of three draft-slot bands. Differences across bands matter because 'RB or WR?' is constrained by which players reach each seat; overlapping intervals argue against turning one band's result into a universal Round 1 rule."
# CELL [first round season chart]
season=first.groupby(["season","first_round_position"],as_index=False).agg(n=("points_zscore","size"),mean_points_zscore=("points_zscore","mean"),top_6_rate=("top_6_points","mean"))
pivot=season.pivot(index="season",columns="first_round_position",values="mean_points_zscore"); season_diff=(pivot["RB"]-pivot["WR"]).rename("rb_minus_wr").reset_index(); season_diff.to_csv(ARTIFACTS/"first_round_by_season.csv",index=False)
write_chart("first_round_03_by_season.html",[{"type":"bar","x":season_diff.season.astype(str).tolist(),"y":season_diff.rb_minus_wr.round(4).tolist(),"marker":{"color":["#f97316" if x>0 else "#3b82f6" for x in season_diff.rb_minus_wr]},"hovertemplate":"%{x}<br>raw RB minus WR z=%{y:+.3f}<extra></extra>"}],{"title":"First-round RB-minus-WR scoring difference by season","xaxis":{"title":"Season","type":"category"},"yaxis":{"title":"Unadjusted points z difference","zeroline":True},"showlegend":False})
positive=int(season_diff.rb_minus_wr.gt(0).sum())
_SECTION_INTERPRETATION = f"First-round RB beats WR descriptively in {positive} of {len(season_diff)} seasons. Season reversals mean the pooled comparison is partly era-dependent; the result should guide positional lean, not override current player projections or the board at a specific pick."
# CELL [first round availability chart]
availability=first.loc[first.player_linked.eq(True)].groupby("first_round_position",as_index=False).agg(n=("points_zscore","size"),unavailable_rate=("first_round_available",lambda x:1-x.mean()),mean_availability=("availability_rate","mean")); availability.to_csv(ARTIFACTS/"first_round_availability_by_position.csv",index=False)
write_chart("first_round_04_unavailability.html",[{"type":"bar","x":availability.first_round_position.tolist(),"y":availability.unavailable_rate.round(4).tolist(),"marker":{"color":["#3b82f6" if x=="WR" else "#f97316" for x in availability.first_round_position]},"customdata":availability.n.astype(int).tolist(),"hovertemplate":"%{x}<br>unavailable=%{y:.1%}<br>linked n=%{customdata:,}<extra></extra>"}],{"title":"First-round player unavailability by position","xaxis":{"title":"First-round position"},"yaxis":{"title":"Active in fewer than 75% of fantasy weeks","tickformat":".0%"},"showlegend":False})
rates=availability.set_index("first_round_position").unavailable_rate
_SECTION_INTERPRETATION = f"First-round RB unavailability is {rates['RB']:.1%} versus {rates['WR']:.1%} for WR, a {rates['RB']-rates['WR']:+.1%} gap. This directly tests the durability mechanism, but injury-inclusive team outcomes remain the decision-relevant headline because availability is unknown on draft day."
# CELL [first round available sensitivity]
available=first.loc[first.player_linked.eq(True)&first.first_round_available.eq(True)].copy()
available_inference,available_contrasts=clustered_model(available,"first_round_position",["WR","RB"],"WR",controls,["points_zscore","top_6_points"],config["robustness_bootstrap_replicates"],config["random_seed"]+800)
available_inference.to_csv(ARTIFACTS/"first_round_available_inference.csv",index=False); available_contrasts.to_csv(ARTIFACTS/"first_round_available_contrasts.csv",index=False)
full_rb=fr_inference.loc[(fr_inference.level=="RB")&(fr_inference.outcome=="points_zscore")].iloc[0]; avail_rb=available_inference.loc[(available_inference.level=="RB")&(available_inference.outcome=="points_zscore")].iloc[0]
compare=pd.DataFrame([{"sample":"Full injury-inclusive","difference":full_rb.difference_vs_reference,"ci_low":full_rb.difference_ci_low,"ci_high":full_rb.difference_ci_high},{"sample":"First-rounder available 75%+","difference":avail_rb.difference_vs_reference,"ci_low":avail_rb.difference_ci_low,"ci_high":avail_rb.difference_ci_high}]); compare.to_csv(ARTIFACTS/"first_round_full_vs_available.csv",index=False)
write_chart("first_round_05_available_sensitivity.html",[{"type":"bar","x":compare["sample"].tolist(),"y":compare.difference.round(4).tolist(),"marker":{"color":["#64748b","#14b8a6"]},"error_y":{"type":"data","symmetric":False,"array":(compare.ci_high-compare.difference).round(4).tolist(),"arrayminus":(compare.difference-compare.ci_low).round(4).tolist()},"hovertemplate":"%{x}<br>RB minus WR=%{y:+.3f}<extra></extra>"}],{"title":"First-round RB minus WR: full and available-only samples","xaxis":{"title":"Sample"},"yaxis":{"title":"Adjusted points z difference","zeroline":True},"showlegend":False})
_SECTION_INTERPRETATION = f"The adjusted RB-minus-WR association moves from {full_rb.difference_vs_reference:+.3f} z in the real-world sample to {avail_rb.difference_vs_reference:+.3f} z when the first-rounder stays sufficiently available. The change estimates a health-conditioned mechanism, not a draft-day guarantee, and must not replace the full-sample answer."
''',
)


write(
    "07_recommendations.ipynb",
    "NB07: recommendations and study summary",
    "Combines the prespecified headline model, pairwise uncertainty, forward validation, subgroup robustness, availability sensitivity, and first-round side analysis into final evidence-graded answers.",
    COMMON + '''# CELL [assemble recommendations]
import json
import math
import numpy as np
import pandas as pd
inference=pd.read_csv(ARTIFACTS/"inference_strategy_intervals.csv"); contrasts=pd.read_csv(ARTIFACTS/"inference_strategy_contrasts.csv"); validation=pd.read_csv(ARTIFACTS/"validation_forward_seasons.csv"); robustness=pd.read_csv(ARTIFACTS/"inference_robustness_subgroups.csv"); availability=pd.read_csv(ARTIFACTS/"availability_strategy_inference.csv"); first_round=pd.read_csv(ARTIFACTS/"first_round_inference.csv"); first_available=pd.read_csv(ARTIFACTS/"first_round_available_inference.csv")
z=inference.loc[inference.outcome.eq("points_zscore")].sort_values("estimate",ascending=False).reset_index(drop=True); winner=z.iloc[0]; runner=z.iloc[1]
pair=contrasts.loc[contrasts.outcome.eq("points_zscore") & (((contrasts.left==winner.level)&(contrasts.right==runner.level))|((contrasts.left==runner.level)&(contrasts.right==winner.level)))].iloc[0]
if pair.left==winner.level: gap,lo,hi=pair.difference,pair.ci_low,pair.ci_high
else: gap,lo,hi=-pair.difference,-pair.ci_high,-pair.ci_low
def oriented(left, right):
    row=contrasts.loc[contrasts.outcome.eq("points_zscore") & (((contrasts.left==left)&(contrasts.right==right))|((contrasts.left==right)&(contrasts.right==left)))].iloc[0]
    return (float(row.difference),float(row.ci_low),float(row.ci_high)) if row.left==left else (-float(row.difference),-float(row.ci_high),-float(row.ci_low))
supported=[]
for level in z.level:
    if level==winner.level:
        supported.append(level)
    else:
        _,level_lo,level_hi=oriented(winner.level,level)
        if level_lo<=0<=level_hi:
            supported.append(level)
lower=[level for level in z.level if level not in supported]
tier_separated=bool(lower) and all(oriented(high,low)[1]>0 for high in supported for low in lower)
strategy_answer=" or ".join(supported)
forward_selected=validation.loc[validation.selected_strategy.eq(winner.level)]; forward_positive=int(forward_selected.test_adjusted_z_difference.gt(0).sum())
robust_winners=robustness.sort_values(["specification","estimate"],ascending=[True,False]).groupby("specification").first().reset_index(); robust_wins=int(robust_winners.level.eq(winner.level).sum())
if tier_separated: strategy_grade="moderate pooled; mixed forward"
elif lo>0 and len(forward_selected)>=2 and forward_positive>=math.ceil(len(forward_selected)/2): strategy_grade="moderate"
elif lo>0: strategy_grade="limited"
else: strategy_grade="inconclusive"
ppw=inference.loc[inference.outcome.eq("points_per_week_above_league")].set_index("level"); top6=inference.loc[inference.outcome.eq("top_6_points")].set_index("level")
fr_rb=first_round.loc[(first_round.level=="RB")&(first_round.outcome=="points_zscore")].iloc[0]; fr_avail=first_available.loc[(first_available.level=="RB")&(first_available.outcome=="points_zscore")].iloc[0]
if fr_rb.difference_ci_low>0: first_answer="RB"
elif fr_rb.difference_ci_high<0: first_answer="WR"
else: first_answer="No clear edge"
first_grade="moderate" if first_answer!="No clear edge" and np.sign(fr_avail.difference_vs_reference)==np.sign(fr_rb.difference_vs_reference) else "inconclusive"
recommendations=pd.DataFrame([
    {"question":"RB/WR allocation through Round 6","answer":strategy_answer,"pooled_leader":winner.level,"evidence_grade":strategy_grade,"adjusted_points_zscore":winner.estimate,"ci_low":winner.ci_low,"ci_high":winner.ci_high,"gap_vs_runner_up":gap,"gap_ci_low":lo,"gap_ci_high":hi,"points_per_week_above_league":ppw.loc[winner.level,"estimate"],"top_6_rate":top6.loc[winner.level,"estimate"],"forward_tests_selecting_answer":len(forward_selected),"positive_forward_tests":forward_positive,"robustness_specifications_won":robust_wins},
    {"question":"First-round RB versus WR","answer":first_answer,"pooled_leader":np.nan,"evidence_grade":first_grade,"adjusted_points_zscore":fr_rb.difference_vs_reference,"ci_low":fr_rb.difference_ci_low,"ci_high":fr_rb.difference_ci_high,"gap_vs_runner_up":np.nan,"gap_ci_low":np.nan,"gap_ci_high":np.nan,"points_per_week_above_league":first_round.loc[(first_round.level=="RB")&(first_round.outcome=="points_per_week_above_league"),"difference_vs_reference"].iloc[0],"top_6_rate":first_round.loc[(first_round.level=="RB")&(first_round.outcome=="top_6_points"),"difference_vs_reference"].iloc[0],"forward_tests_selecting_answer":np.nan,"positive_forward_tests":np.nan,"robustness_specifications_won":np.nan},
])
recommendations.to_csv(ARTIFACTS/"recommendations.csv",index=False)
print(recommendations.to_string(index=False))
_SECTION_INTERPRETATION = f"The supported Round 6 tier is {strategy_answer}. {winner.level} is tallest, but its {gap:+.3f}-z gap over {runner.level} has a 95% interval of {lo:+.3f} to {hi:+.3f}, so the data do not distinguish those two. Both supported builds separate from both 0-1 RB builds in pooled pairwise contrasts; forward selection is mixed ({forward_positive} positive of {len(forward_selected)} tests selecting the pooled leader). The first-round answer is {first_answer.lower()}."
# CELL [recommendation chart]
order=["Zero RB (0)","WR-heavy (1)","Balanced (2)","RB-heavy (3+)"]; chart=z.set_index("level").reindex(order).reset_index()
write_chart("recommendations_01_round6.html",[{"type":"bar","x":chart.level.tolist(),"y":chart.estimate.round(4).tolist(),"marker":{"color":["#a855f7","#3b82f6","#14b8a6","#f97316"]},"error_y":{"type":"data","symmetric":False,"array":(chart.ci_high-chart.estimate).round(4).tolist(),"arrayminus":(chart.estimate-chart.ci_low).round(4).tolist()},"customdata":["supported tier" if x in supported else "lower pooled tier" for x in chart.level],"hovertemplate":"%{x}<br>adjusted z=%{y:.3f}<br>%{customdata}<extra></extra>"}],{"title":"Round 6 answer: draft at least two RBs","xaxis":{"title":"Strategy"},"yaxis":{"title":"Adjusted points z-score","zeroline":True},"showlegend":False})
_SECTION_INTERPRETATION = f"The decision view supports {strategy_answer}, not a forced choice between them. The pooled data argue against reaching Round 6 with only zero or one RB; mixed forward results prevent elevating the tier into a universal causal rule."
# CELL [first round answer chart]
round_compare=pd.DataFrame([{"sample":"Injury-inclusive","difference":fr_rb.difference_vs_reference,"ci_low":fr_rb.difference_ci_low,"ci_high":fr_rb.difference_ci_high},{"sample":"Available 75%+","difference":fr_avail.difference_vs_reference,"ci_low":fr_avail.difference_ci_low,"ci_high":fr_avail.difference_ci_high}])
write_chart("recommendations_02_first_round.html",[{"type":"bar","x":round_compare["sample"].tolist(),"y":round_compare.difference.round(4).tolist(),"marker":{"color":["#64748b","#14b8a6"]},"error_y":{"type":"data","symmetric":False,"array":(round_compare.ci_high-round_compare.difference).round(4).tolist(),"arrayminus":(round_compare.difference-round_compare.ci_low).round(4).tolist()},"hovertemplate":"%{x}<br>RB minus WR=%{y:+.3f}<extra></extra>"}],{"title":f"First-round answer: {first_answer}","xaxis":{"title":"Sample"},"yaxis":{"title":"Adjusted RB-minus-WR points z","zeroline":True},"showlegend":False})
_SECTION_INTERPRETATION = f"The first-round injury-inclusive estimate is {fr_rb.difference_vs_reference:+.3f} z (95% interval {fr_rb.difference_ci_low:+.3f} to {fr_rb.difference_ci_high:+.3f}); among sufficiently available first-rounders it is {fr_avail.difference_vs_reference:+.3f}. The draft-day answer remains {first_answer.lower()} because availability is unknown when the pick is made."
# CELL [write study summary]
manifest=json.loads((ARTIFACTS/"panel_manifest.json").read_text(encoding="utf-8"))
availability_winner=availability.loc[availability.outcome.eq("points_zscore")].sort_values("estimate",ascending=False).iloc[0]
study_summary={
    "sample":{"league_seasons":manifest["retained_league_seasons"],"team_seasons":manifest["retained_team_seasons"],"seasons":"2018-2025","formats":["PPR","half-PPR"]},
    "primary":{"question":"RB/WR allocation through Round 6","supported_tier":supported,"pooled_leader":winner.level,"adjusted_points_zscore":float(winner.estimate),"ci":[float(winner.ci_low),float(winner.ci_high)],"runner_up":runner.level,"leader_minus_runner":float(gap),"leader_minus_runner_ci":[float(lo),float(hi)],"adjusted_points_per_week_above_league":float(ppw.loc[winner.level,"estimate"]),"adjusted_top_6_rate":float(top6.loc[winner.level,"estimate"]),"evidence_grade":strategy_grade,"availability_conditioned_leader":availability_winner.level},
    "first_round":{"answer":first_answer,"rb_minus_wr_points_zscore":float(fr_rb.difference_vs_reference),"ci":[float(fr_rb.difference_ci_low),float(fr_rb.difference_ci_high)],"available_only_rb_minus_wr":float(fr_avail.difference_vs_reference),"evidence_grade":first_grade},
    "limitations":["Public Sleeper leagues are a convenience sample.","Draft strategy is not randomized and manager skill is unmeasured.","Availability conditioning is post-draft.","The study estimates team-level regular-season scoring associations, not player value or playoff wins."],
}
(ARTIFACTS/"study_summary.json").write_text(json.dumps(study_summary,indent=2),encoding="utf-8")
print(json.dumps(study_summary,indent=2))
_SECTION_INTERPRETATION = "The machine-readable summary records the executed numbers and the limits on their use. The study can support a historical draft lean when uncertainty and validation agree; it cannot establish that forcing the same positional build will cause better results in a future league."
''',
)
