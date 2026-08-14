"""Generate the study notebooks. Notebook code is the executable source of truth."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def md(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(True)}


def code(text: str) -> dict:
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": text.splitlines(True)}


SECTION_NOTES = {
    "imports and chart helper": ("Load paths and define the shared offline Plotly renderer.", "The helper only controls chart rendering; it does not transform or analyze study data."),
    "locked study configuration": ("Declare the population gates, outcomes, timing windows, and reproducibility settings.", "These definitions are fixed before looking at timing results."),
    "configuration chart": ("Visualize the round windows used throughout the study.", "The broad windows preserve support and prevent false precision at the exact-round level."),
    "load source outcomes": ("Load the validated team-season outcomes inherited from the draft-order study.", "This is the full 3,641-league source panel before QB/TE-specific format restrictions."),
    "load draft caches": ("Load current and historic Sleeper draft metadata and full pick boards.", "Historic recovery expands coverage, but empty or structurally incomplete boards still fail later gates."),
    "normalize leagues and picks": ("Classify league formats and normalize every draft selection to one pick-level row.", "Primary eligibility requires a complete redraft 1QB board without superflex, keeper picks, IDP metadata, or TE premium."),
    "build team timing panel": ("Join each roster to its first drafted QB and TE and attach regular-season outcomes.", "The team-season table is the main analytical grain; roster ownership, not the original pick owner, determines exposure."),
    "build position timing panel": ("Reshape the team table to one row per team-position for position-specific models.", "QB and TE now share a common schema while retaining their selected player and timing window."),
    "validate and save manifest": ("Run balance and outcome-accounting gates and save the coverage manifest.", "Passing gates establish internal consistency, not causal identification."),
    "coverage chart": ("Compare source and retained league coverage by season.", "The clean panel grows substantially in later seasons; early-year standalone estimates remain sparse."),
    "prepare eda summaries": ("Create reusable timing-window and season summaries for the EDA charts.", "No model adjustment is applied here; these are descriptive views of the clean panel."),
    "eda points chart": ("Plot average within-league points performance by QB and TE timing window.", "Later QB windows and TE rounds 10–11 lead descriptively, but composition may explain part of the pattern."),
    "eda practical points chart": ("Translate standardized scoring into league-relative points per fantasy week.", "The hover details retain average raw season points, while the plotted scale controls for league scoring level and season length."),
    "eda top six chart": ("Plot the probability of finishing in the top half of the league by timing window.", "The top-six view translates standardized points into a directly interpretable team outcome."),
    "eda support chart": ("Show how many team-seasons support each timing estimate.", "The late-QB and late-TE tails have less support, which is why the study reports windows rather than a single exact round."),
    "eda qb season chart": ("Trace QB timing performance separately by season.", "Year-to-year movement shows why pooled QB rankings require forward validation."),
    "eda te season chart": ("Trace TE timing performance separately by season.", "TE timing is also heterogeneous; no pooled result should be read as universal across seasons."),
    "eda exact round chart": ("Inspect exact-round curves only where at least 100 team-seasons are available.", "The curve is diagnostic. Final recommendations remain based on supported multi-round windows."),
    "qb categorical association chart": ("Measure the association between categorical QB timing windows and total team points.", "Correlation ratio eta is the categorical analogue of r; eta-squared equals the one-way timing-window model's R-squared."),
    "te categorical association chart": ("Measure the association between categorical TE timing windows and total team points.", "Correlation ratio eta is the categorical analogue of r; eta-squared equals the one-way timing-window model's R-squared."),
    "define inference model": ("Load the position panel and define the season- and slot-adjusted least-squares model.", "Timing is modeled categorically because the observed relationship is not assumed to be linear."),
    "run clustered bootstrap": ("Fit QB and TE models and calculate 2,000 league-cluster bootstrap intervals.", "Resampling whole leagues preserves the dependence among the 12 teams drafted together."),
    "adjusted comparison chart": ("Compare adjusted QB and TE estimates with uncertainty intervals.", "QB round 12+ and TE rounds 10–11 rank highest in the pooled adjusted model."),
    "qb interval chart": ("Focus on QB timing estimates and their bootstrap uncertainty.", "The late-QB pooled estimate is positive, but its smaller sample and limited forward-selection history keep it exploratory."),
    "te interval chart": ("Focus on TE timing estimates and their bootstrap uncertainty.", "TE rounds 10–11 have a positive pooled interval and more repeat forward evidence than the QB leader."),
    "calculate forward tests": ("For each season, select a window using only earlier seasons and test it on the next season.", "This prevents the test season from influencing its own selected strategy."),
    "forward scoring chart": ("Plot forward-season scoring differences for the training-selected window.", "Sign changes across years show that the historical leader is not stable enough to call causal or universal."),
    "forward top six chart": ("Plot forward-season changes in top-six finish probability.", "This outcome broadly agrees with the scoring test while making the practical magnitude easier to read."),
    "selection stability chart": ("Show which window won in training and how it performed the following season.", "QB selections shifted more sharply; TE rounds 10–11 were selected in three tests and succeeded in two."),
    "link player availability": ("Link selected players to weekly participation and calculate regular-season availability.", "Name-based fallback linkage is useful for sensitivity analysis but is not treated as a primary injury measure."),
    "summarize availability sample": ("Restrict to selected QBs and TEs active for at least 75% of league weeks.", "Conditioning on availability is post-draft and therefore remains a sensitivity analysis, not the headline estimate."),
    "availability chart": ("Compare timing outcomes among sufficiently available selected players.", "Late QB and TE rounds 10–11 remain favorable after the availability screen."),
    "build joint timing surface": ("Aggregate team outcomes across every QB-by-TE timing combination.", "Cells with fewer than 100 teams are suppressed from recommendation graphics."),
    "assemble recommendations": ("Combine pooled inference and forward validation into position-level evidence grades.", "The grading deliberately distinguishes the exploratory late-QB result from the moderately supported TE result."),
    "joint heatmap": ("Visualize supported QB and TE timing combinations as a response surface.", "The heatmap is descriptive and can be affected by the types of managers who choose each combination."),
    "recommendation chart": ("Plot the leading position-specific windows with uncertainty and evidence metadata.", "This is the compact decision view: QB round 12+ is exploratory; TE rounds 10–11 have moderate evidence."),
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
        before, after = SECTION_NOTES.get(key, (f"Run the `{key}` section.", "Use this output with the surrounding study limitations."))
        cells.extend([
            md(f"## {key.title()}\n\n{before}\n"),
            code(section_source),
            md(f"### Interpretation\n\n{after}\n"),
        ])
    notebook = {
        "cells": cells,
        "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python", "version": "3.12"}},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    (ROOT / "notebooks" / name).write_text(json.dumps(notebook, indent=1), encoding="utf-8")


COMMON = '''# CELL [imports and chart helper]
from pathlib import Path
import json as _json
ROOT = Path.cwd()
if ROOT.name == "notebooks": ROOT = ROOT.parent
ARTIFACTS = ROOT / "artifacts"
PROCESSED = ROOT / "data/processed"
_PLOTLY_JS = (ROOT / "assets/plotly.min.js").read_text(encoding="utf-8")
_CHART_FILES = []
_CHART_COUNTER = 0
def write_chart(filename, traces, layout):
    global _CHART_COUNTER
    _CHART_COUNTER += 1
    chart_id = f"chart_{_CHART_COUNTER}"
    defaults = {"paper_bgcolor":"#111318","plot_bgcolor":"#111318","font":{"color":"#e5e7eb","family":"Arial, sans-serif","size":14},"title":{"font":{"color":"#f8fafc","size":22},"x":0.5},"margin":{"l":80,"r":40,"t":90,"b":80},"hoverlabel":{"bgcolor":"#1f2937","bordercolor":"#64748b","font":{"color":"#f8fafc"}},"xaxis":{"gridcolor":"#334155","linecolor":"#64748b","zerolinecolor":"#94a3b8"},"yaxis":{"gridcolor":"#334155","linecolor":"#64748b","zerolinecolor":"#94a3b8"},"legend":{"bgcolor":"rgba(17,19,24,0.75)","font":{"color":"#e5e7eb"}}}
    for key, value in layout.items():
        if isinstance(value, dict) and isinstance(defaults.get(key), dict):
            defaults[key].update(value)
        elif key == "title" and isinstance(value, str):
            defaults["title"]["text"] = value
        else:
            defaults[key] = value
    html = f"""<!doctype html><html><head><meta charset="utf-8"><style>html,body{{margin:0;background:#111318;color:#e5e7eb}}#{chart_id}{{width:100%;height:620px;background:#111318}}</style><script>{_PLOTLY_JS}</script></head><body><div id="{chart_id}"></div><script>Plotly.newPlot("{chart_id}",{_json.dumps(traces)},{_json.dumps(defaults)},{_json.dumps({"responsive": True, "displaylogo": False})})</script></body></html>"""
    (ARTIFACTS / filename).write_text(html, encoding="utf-8")
    _CHART_FILES.append(filename)
    try:
        from IPython.display import HTML, display
        display(HTML(html))
    except ImportError:
        pass
'''

write(
    "00_configuration.ipynb",
    "NB00: configuration and analysis contract",
    "Locks the population, outcomes, timing windows, support threshold, and uncertainty settings.",
    COMMON + '''# CELL [locked study configuration]
import json
CONFIG = {
    "source_seasons": list(range(2018, 2026)),
    "teams": 12,
    "allowed_scoring_types": ["ppr", "half_ppr", "std"],
    "minimum_draft_rounds": 12,
    "qb_slots": 1,
    "superflex_slots": 0,
    "minimum_te_slots": 1,
    "exclude_keeper_picks": True,
    "exclude_te_premium": True,
    "timing_windows": ["1-3", "4-5", "6-7", "8-9", "10-11", "12+"],
    "joint_minimum_cell_n": 100,
    "bootstrap_replicates": 2000,
    "random_seed": 20260813,
    "primary_outcome": "points_zscore",
    "secondary_outcomes": ["points_rank", "top_6_points", "top_regular_season_scorer"],
}
(ARTIFACTS / "study_config.json").write_text(json.dumps(CONFIG, indent=2), encoding="utf-8")
print(json.dumps(CONFIG, indent=2))
# CELL [configuration chart]
write_chart("configuration_01_timing_windows.html", [{"type":"bar","x":CONFIG["timing_windows"],"y":[1,4,6,8,10,12],"marker":{"color":"#3b82f6"},"text":["Starts 1","Starts 4","Starts 6","Starts 8","Starts 10","Starts 12"],"textposition":"outside","hovertemplate":"%{x}: starts at round %{y}<extra></extra>"}], {"title":"Starting round of each timing window","xaxis":{"title":"Draft-round window","type":"category","categoryorder":"array","categoryarray":CONFIG["timing_windows"]},"yaxis":{"title":"Starting round","dtick":1},"showlegend":False})
''',
)

write(
    "01_data_preparation.ipynb",
    "NB01: data preparation",
    "Combines the retained 2018-2025 outcome panel with complete Sleeper draft boards and creates the normalized study schema.",
    COMMON + '''# CELL [load source outcomes]
import json
from collections import Counter
import numpy as np
import pandas as pd

SOURCE = ROOT.parent / "fantasy_draft_order_study"
panel = pd.read_csv(SOURCE / "data/processed/analysis_panel.csv", dtype={"league_id": str, "draft_id": str, "roster_id": int})
week_settings = pd.read_csv(SOURCE / "data/cache/league_regular_season_settings.csv", dtype={"league_id": str})
# CELL [load draft caches]
drafts = {}
for path in [ROOT / "data/cache/current_draft_payloads.jsonl"]:
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line); drafts[str(record["draft_id"])] = record["payload"]
historic_needed = set(panel.loc[panel.season <= 2021, "draft_id"].astype(str))
with (SOURCE / "data/cache/historic_drafts_and_rosters.jsonl").open(encoding="utf-8") as handle:
    for line in handle:
        record = json.loads(line); parts = record["path"].split("/")
        if len(parts) == 2 and parts[0] == "draft" and parts[1] in historic_needed:
            drafts[parts[1]] = record["payload"]
boards = {}
for path in [ROOT / "data/cache/current_full_draft_picks.jsonl", ROOT / "data/cache/historic_full_draft_picks.jsonl"]:
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line); boards[str(record["draft_id"])] = record["picks"]

league_score = panel.groupby(["league_id", "season", "draft_id"], as_index=False).first()
score_map = {}
for row in league_score.itertuples(index=False):
    scoring = json.loads(row.scoring_settings)
    score_map[str(row.draft_id)] = {"reception_points": float(scoring.get("rec", 0)), "passing_td_points": float(scoring.get("pass_td", 0)), "te_premium": float(scoring.get("bonus_rec_te", 0))}

# CELL [normalize leagues and picks]
league_rows, pick_rows = [], []
allowed = {"ppr", "half_ppr", "std"}
for draft_id in sorted(set(panel.draft_id.astype(str))):
    draft = drafts.get(draft_id) or {}; board = boards.get(draft_id) or []; settings = draft.get("settings") or {}; metadata = draft.get("metadata") or {}
    teams = int(settings.get("teams") or 0); rounds = int(settings.get("rounds") or 0)
    pick_nos = [int(p.get("pick_no") or 0) for p in board]
    complete = teams == 12 and rounds >= 1 and len(board) == teams * rounds and set(pick_nos) == set(range(1, teams * rounds + 1))
    qb_slots = int(settings.get("slots_qb") or 0); sf_slots = int(settings.get("slots_super_flex") or 0); te_slots = int(settings.get("slots_te") or 0)
    keeper_count = sum(p.get("is_keeper") not in (None, False, 0, "0", "", "false", "False") for p in board)
    scoring_type = str(metadata.get("scoring_type") or "unknown").lower()
    score = score_map.get(draft_id, {"reception_points": np.nan, "passing_td_points": np.nan, "te_premium": np.nan})
    gates = {
        "incomplete_board": not complete,
        "not_completed_snake": draft.get("status") != "complete" or draft.get("type") != "snake",
        "not_1qb": qb_slots != 1 or sf_slots != 0,
        "no_required_te": te_slots < 1,
        "short_draft": rounds < 12,
        "keeper_picks": keeper_count > 0,
        "non_redraft_or_idp": scoring_type not in allowed,
        "te_premium": score["te_premium"] != 0,
    }
    primary = not any(gates.values())
    season = int(draft.get("season") or panel.loc[panel.draft_id.eq(draft_id), "season"].iloc[0])
    league_id = str(panel.loc[panel.draft_id.eq(draft_id), "league_id"].iloc[0])
    league_rows.append({"league_id": league_id, "season": season, "draft_id": draft_id, "team_count": teams, "draft_rounds": rounds, "qb_start_slots": qb_slots, "superflex_slots": sf_slots, "te_start_slots": te_slots, "scoring_type": scoring_type, "keeper_pick_count": keeper_count, "complete_pick_board": complete, **score, "primary_sample": primary, "exclusion_reason": "eligible" if primary else ";".join(k for k,v in gates.items() if v)})
    for p in board:
        meta = p.get("metadata") or {}; pick_no = int(p.get("pick_no") or 0)
        pick_rows.append({"league_id": league_id, "season": season, "draft_id": draft_id, "pick_no": pick_no, "round": int(p.get("round") or ((pick_no-1)//12+1)), "pick_in_round": (pick_no-1)%12+1, "draft_slot": int(p.get("draft_slot") or 0), "roster_id": int(p.get("roster_id") or 0), "sleeper_player_id": str(p.get("player_id") or meta.get("player_id") or ""), "player_name": f"{meta.get('first_name','')} {meta.get('last_name','')}".strip(), "player_position": str(meta.get("position") or ""), "is_keeper": bool(p.get("is_keeper"))})

leagues = pd.DataFrame(league_rows); picks = pd.DataFrame(pick_rows)
leagues.to_csv(PROCESSED / "league_seasons.csv", index=False); picks.to_csv(PROCESSED / "draft_picks.csv", index=False)
# CELL [build team timing panel]
eligible = set(leagues.loc[leagues.primary_sample, "draft_id"])
team = panel.loc[panel.draft_id.isin(eligible)].copy()
for pos in ["QB", "TE"]:
    first = (picks.loc[picks.draft_id.isin(eligible) & picks.player_position.eq(pos)].sort_values("pick_no").groupby(["draft_id", "roster_id"], as_index=False).first())
    first = first[["draft_id", "roster_id", "pick_no", "round", "pick_in_round", "sleeper_player_id", "player_name"]].rename(columns={c:f"first_{pos.lower()}_{c}" for c in ["pick_no","round","pick_in_round","sleeper_player_id","player_name"]})
    team = team.merge(first, on=["draft_id", "roster_id"], how="left")
team = team.merge(leagues[["draft_id","scoring_type","reception_points","passing_td_points","te_premium"]], on="draft_id", how="left")
team = team.merge(week_settings[["league_id","regular_season_weeks"]].drop_duplicates("league_id"), on="league_id", how="left")
team["league_mean_regular_season_points"] = team.groupby("draft_id").regular_season_points.transform("mean")
team["points_per_week"] = team.regular_season_points / team.regular_season_weeks
team["points_per_week_above_league"] = (team.regular_season_points - team.league_mean_regular_season_points) / team.regular_season_weeks
team["qb_before_te"] = team.first_qb_pick_no < team.first_te_pick_no
def window(value):
    if pd.isna(value): return "Undrafted"
    value=int(value)
    if value<=3:return "1-3"
    if value<=5:return "4-5"
    if value<=7:return "6-7"
    if value<=9:return "8-9"
    if value<=11:return "10-11"
    return "12+"
team["qb_timing_window"] = team.first_qb_round.map(window); team["te_timing_window"] = team.first_te_round.map(window)
team.to_csv(PROCESSED / "team_timing_panel.csv", index=False)
# CELL [build position timing panel]
long=[]
for pos in ["qb","te"]:
    temp=team.copy(); temp["position"]=pos.upper(); temp["first_pick_no"]=temp[f"first_{pos}_pick_no"]; temp["first_round"]=temp[f"first_{pos}_round"]; temp["selected_player_id"]=temp[f"first_{pos}_sleeper_player_id"]; temp["selected_player_name"]=temp[f"first_{pos}_player_name"]; temp["timing_window"]=temp[f"{pos}_timing_window"]
    long.append(temp[["league_id","season","draft_id","roster_id","draft_slot","position","first_pick_no","first_round","selected_player_id","selected_player_name","timing_window","regular_season_points","regular_season_weeks","points_per_week","points_per_week_above_league","points_zscore","points_rank","top_6_points","top_regular_season_scorer","scoring_type","reception_points","passing_td_points"]])
position=pd.concat(long,ignore_index=True); position.to_csv(PROCESSED / "position_timing_panel.csv",index=False)
# CELL [validate and save manifest]
manifest={"source_league_seasons":int(panel.draft_id.nunique()),"draft_payloads":len(drafts),"pick_payloads":len(boards),"complete_boards":int(leagues.complete_pick_board.sum()),"primary_league_seasons":int(len(eligible)),"primary_team_seasons":int(len(team)),"teams_without_drafted_qb":int(team.first_qb_round.isna().sum()),"teams_without_drafted_te":int(team.first_te_round.isna().sum()),"primary_by_season":{str(k):int(v) for k,v in team.groupby("season").draft_id.nunique().items()},"exclusions":dict(Counter(reason for reasons in leagues.loc[~leagues.primary_sample,"exclusion_reason"] for reason in reasons.split(";")))}
(ARTIFACTS/"panel_manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
assert len(team)==12*len(eligible) and team.groupby("draft_id").size().eq(12).all()
assert team.regular_season_weeks.notna().all() and team.regular_season_weeks.gt(0).all()
assert team.first_qb_round.notna().mean()>.995 and team.first_te_round.notna().mean()>.995
assert np.isclose(team.top_6_points.sum(),6*len(eligible)) and np.isclose(team.top_regular_season_scorer.sum(),len(eligible))
print(json.dumps(manifest,indent=2))
# CELL [coverage chart]
season_source=panel.groupby("season").draft_id.nunique(); season_primary=team.groupby("season").draft_id.nunique()
write_chart("preparation_01_coverage_by_season.html", [{"type":"bar","name":"Source leagues","x":season_source.index.astype(str).tolist(),"y":season_source.tolist(),"marker":{"color":"#94a3b8"}},{"type":"bar","name":"Primary eligible","x":season_primary.index.astype(str).tolist(),"y":season_primary.tolist(),"marker":{"color":"#3b82f6"}}], {"title":"Source and retained league-seasons by year","barmode":"group","xaxis":{"title":"Season","type":"category"},"yaxis":{"title":"League-seasons"}})
''',
)

write(
    "02_eda.ipynb",
    "NB02: exploratory analysis",
    "Measures support and unadjusted outcomes across QB and TE timing windows.",
    COMMON + '''# CELL [prepare eda summaries]
import json
import numpy as np
import pandas as pd
position=pd.read_csv(PROCESSED/"position_timing_panel.csv")
order=["1-3","4-5","6-7","8-9","10-11","12+"]
position=position.loc[position.timing_window.isin(order)].copy()
summary=(position.groupby(["position","timing_window"],as_index=False).agg(n=("points_zscore","size"),leagues=("draft_id","nunique"),mean_regular_season_points=("regular_season_points","mean"),mean_points_per_week=("points_per_week","mean"),mean_points_per_week_above_league=("points_per_week_above_league","mean"),mean_points_zscore=("points_zscore","mean"),mean_finish=("points_rank","mean"),top_6_rate=("top_6_points","mean"),top_scorer_rate=("top_regular_season_scorer","mean")))
summary["timing_window"]=pd.Categorical(summary.timing_window,order,ordered=True); summary=summary.sort_values(["position","timing_window"]); summary.to_csv(ARTIFACTS/"eda_timing_summary.csv",index=False)
season=(position.groupby(["position","season","timing_window"],as_index=False).agg(n=("points_zscore","size"),mean_points_zscore=("points_zscore","mean"),top_6_rate=("top_6_points","mean"))); season.to_csv(ARTIFACTS/"eda_timing_by_season.csv",index=False)
def categorical_association(df,outcome):
    x=df[["timing_window",outcome]].dropna(); y=x[outcome]; grand=y.mean()
    ss_between=x.groupby("timing_window",observed=True)[outcome].agg(lambda values: len(values)*(values.mean()-grand)**2).sum()
    ss_total=((y-grand)**2).sum(); r2=ss_between/ss_total; groups=x.timing_window.nunique()
    return len(x),np.sqrt(r2),r2,1-(1-r2)*(len(x)-1)/(len(x)-groups)
association_rows=[]
for pos in ["QB","TE"]:
    x=position.loc[position.position.eq(pos)]
    raw_n,raw_eta,raw_r2,raw_adjusted_r2=categorical_association(x,"regular_season_points")
    _,normalized_eta,normalized_r2,normalized_adjusted_r2=categorical_association(x,"points_zscore")
    _,relative_eta,relative_r2,relative_adjusted_r2=categorical_association(x,"points_per_week_above_league")
    association_rows.append({"position":pos,"n":raw_n,"raw_points_eta":raw_eta,"raw_points_r2":raw_r2,"raw_points_adjusted_r2":raw_adjusted_r2,"normalized_points_eta":normalized_eta,"normalized_points_r2":normalized_r2,"normalized_points_adjusted_r2":normalized_adjusted_r2,"relative_points_per_week_eta":relative_eta,"relative_points_per_week_r2":relative_r2,"relative_points_per_week_adjusted_r2":relative_adjusted_r2})
associations=pd.DataFrame(association_rows); associations.to_csv(ARTIFACTS/"eda_timing_window_associations.csv",index=False)
colors={"QB":"#2563eb","TE":"#f97316"}
def grouped_traces(value,kind="bar"):
    traces=[]
    for pos in ["QB","TE"]:
        x=summary.loc[summary.position.eq(pos)].sort_values("timing_window"); traces.append({"type":kind,"name":pos,"x":x.timing_window.astype(str).tolist(),"y":x[value].round(4).tolist(),"marker":{"color":colors[pos]},"customdata":x.n.tolist(),"hovertemplate":"%{x}<br>%{y:.3f}<br>n=%{customdata}<extra>%{fullData.name}</extra>"})
    return traces
palette=["#60a5fa","#a78bfa","#22d3ee","#34d399","#fb923c","#f87171"]
def season_traces(pos):
    traces=[]
    for i,w in enumerate(order):
        x=season.loc[season.position.eq(pos) & season.timing_window.eq(w)].sort_values("season"); traces.append({"type":"scatter","mode":"lines+markers","name":w,"x":x.season.astype(str).tolist(),"y":x.mean_points_zscore.round(4).tolist(),"marker":{"color":palette[i]},"line":{"color":palette[i]},"customdata":x.n.tolist(),"hovertemplate":"%{x}<br>z=%{y:.3f}<br>n=%{customdata}<extra>Rounds %{fullData.name}</extra>"})
    return traces
def categorical_association_traces(pos,color):
    x=position.loc[position.position.eq(pos),["timing_window","regular_season_points"]].dropna()
    means=x.groupby("timing_window",as_index=False).agg(n=("regular_season_points","size"),mean_points=("regular_season_points","mean"),sem=("regular_season_points","sem"))
    means["timing_window"]=pd.Categorical(means.timing_window,order,ordered=True); means=means.sort_values("timing_window")
    overall=float(x.regular_season_points.mean())
    return [{"type":"scatter","mode":"markers","name":"Window mean","x":means.timing_window.astype(str).tolist(),"y":means.mean_points.round(1).tolist(),"marker":{"color":color,"size":11},"error_y":{"type":"data","array":(1.96*means["sem"]).round(1).tolist(),"color":color,"thickness":1},"customdata":means.n.tolist(),"hovertemplate":"Rounds %{x}<br>mean team points=%{y:,.1f}<br>n=%{customdata:,}<extra></extra>"},{"type":"scatter","mode":"lines","name":"Position-wide mean","x":order,"y":[round(overall,1)]*len(order),"line":{"color":"#e5e7eb","dash":"dash"},"hovertemplate":"overall mean=%{y:,.1f}<extra></extra>"}]
# CELL [eda points chart]
write_chart("eda_01_timing_points.html",grouped_traces("mean_points_zscore"),{"title":"Team scoring by first QB and TE timing","barmode":"group","xaxis":{"title":"Draft-round window","type":"category","categoryorder":"array","categoryarray":order},"yaxis":{"title":"Mean within-league points z-score","zeroline":True}})
# CELL [eda practical points chart]
traces=[]
for pos,color in [("QB","#2563eb"),("TE","#f97316")]:
    x=summary.loc[summary.position.eq(pos)].sort_values("timing_window")
    custom=np.column_stack([x.mean_regular_season_points.round(1),x.mean_points_zscore.round(3),x.n])
    traces.append({"type":"bar","name":pos,"x":x.timing_window.astype(str).tolist(),"y":x.mean_points_per_week_above_league.round(3).tolist(),"marker":{"color":color},"customdata":custom.tolist(),"hovertemplate":"Rounds %{x}<br>%{y:+.2f} points/week vs league average<br>raw season average=%{customdata[0]:,.1f}<br>mean z=%{customdata[1]:+.3f}<br>n=%{customdata[2]:,}<extra>%{fullData.name}</extra>"})
write_chart("eda_02_practical_points_scale.html",traces,{"title":"Team points per week relative to league average","barmode":"group","xaxis":{"title":"Draft-round window","type":"category","categoryorder":"array","categoryarray":order},"yaxis":{"title":"Mean points per week above/below league average","zeroline":True}})
# CELL [eda top six chart]
write_chart("eda_03_top6_rates.html",grouped_traces("top_6_rate"),{"title":"Top-six finish rate by QB and TE timing","barmode":"group","xaxis":{"title":"Draft-round window","type":"category","categoryorder":"array","categoryarray":order},"yaxis":{"title":"Top-six rate","tickformat":".0%"}})
# CELL [eda support chart]
write_chart("eda_04_timing_support.html",grouped_traces("n"),{"title":"Observed sample support by timing window","barmode":"group","xaxis":{"title":"Draft-round window","type":"category","categoryorder":"array","categoryarray":order},"yaxis":{"title":"Team-seasons"}})
# CELL [eda qb season chart]
write_chart("eda_05_qb_season_stability.html",season_traces("QB"),{"title":"QB timing performance by season","xaxis":{"title":"Season","type":"category"},"yaxis":{"title":"Mean points z-score","zeroline":True}})
# CELL [eda te season chart]
write_chart("eda_06_te_season_stability.html",season_traces("TE"),{"title":"TE timing performance by season","xaxis":{"title":"Season","type":"category"},"yaxis":{"title":"Mean points z-score","zeroline":True}})
# CELL [eda exact round chart]
exact=(position.groupby(["position","first_round"],as_index=False).agg(n=("points_zscore","size"),mean_points_zscore=("points_zscore","mean"))); exact=exact.loc[exact.n>=100]
traces=[]
for pos in ["QB","TE"]:
    x=exact.loc[exact.position.eq(pos)].sort_values("first_round"); traces.append({"type":"scatter","mode":"lines+markers","name":pos,"x":x.first_round.astype(int).tolist(),"y":x.mean_points_zscore.round(4).tolist(),"line":{"color":colors[pos]},"customdata":x.n.tolist(),"hovertemplate":"Round %{x}<br>z=%{y:.3f}<br>n=%{customdata}<extra>%{fullData.name}</extra>"})
write_chart("eda_07_exact_round_curve.html",traces,{"title":"Exact-round scoring curve (rounds with at least 100 teams)","xaxis":{"title":"Round of first QB or TE","dtick":1},"yaxis":{"title":"Mean points z-score","zeroline":True}})
# CELL [qb categorical association chart]
qb_association=associations.loc[associations.position.eq("QB")].iloc[0]
write_chart("eda_08_qb_timing_window_association.html",categorical_association_traces("QB","#3b82f6"),{"title":f"QB timing windows vs total team points | η={qb_association.raw_points_eta:.3f}, R²={qb_association.raw_points_r2:.4f}","xaxis":{"title":"First-QB timing window","type":"category","categoryorder":"array","categoryarray":order},"yaxis":{"title":"Mean regular-season team points"}})
# CELL [te categorical association chart]
te_association=associations.loc[associations.position.eq("TE")].iloc[0]
write_chart("eda_09_te_timing_window_association.html",categorical_association_traces("TE","#f97316"),{"title":f"TE timing windows vs total team points | η={te_association.raw_points_eta:.3f}, R²={te_association.raw_points_r2:.4f}","xaxis":{"title":"First-TE timing window","type":"category","categoryorder":"array","categoryarray":order},"yaxis":{"title":"Mean regular-season team points"}})
''',
)

write(
    "03_inference_and_robustness.ipynb",
    "NB03: inference and robustness",
    "Fits timing-window models adjusted for draft slot and season, with league-cluster bootstrap intervals.",
    COMMON + '''# CELL [define inference model]
import json
import numpy as np
import pandas as pd
position=pd.read_csv(PROCESSED/"position_timing_panel.csv",dtype={"draft_id":str})
windows=["1-3","4-5","6-7","8-9","10-11","12+"]; rng=np.random.default_rng(20260813)
def design(df):
    cats=pd.Categorical(df.timing_window,windows); timing=pd.get_dummies(cats,dtype=float)
    slot=pd.get_dummies(df.draft_slot,prefix="slot",drop_first=True,dtype=float); season=pd.get_dummies(df.season,prefix="season",drop_first=True,dtype=float)
    return np.column_stack([np.ones(len(df)),timing.values,slot.values,season.values]), timing.columns.tolist()
def estimates_xy(X,y,n_names):
    beta=np.linalg.lstsq(X,y,rcond=None)[0]; common=float(beta[0]+X[:,1+n_names:].mean(axis=0)@beta[1+n_names:]); return np.array([common+beta[1+i] for i in range(n_names)])
# CELL [run clustered bootstrap]
rows=[]
for pos in ["QB","TE"]:
    df=position.loc[position.position.eq(pos) & position.timing_window.isin(windows)].copy(); X,names=design(df); y=df.points_zscore.to_numpy(float); point=estimates_xy(X,y,len(names)); leagues=df.draft_id.unique(); group_indices=[np.flatnonzero(df.draft_id.to_numpy()==key) for key in leagues]; boots=[]
    for _ in range(2000):
        chosen=rng.integers(0,len(leagues),size=len(leagues)); idx=np.concatenate([group_indices[i] for i in chosen]); boots.append(estimates_xy(X[idx],y[idx],len(names)))
    boots=np.asarray(boots)
    for i,w in enumerate(windows):
        sub=df.loc[df.timing_window.eq(w)]; rows.append({"position":pos,"timing_window":w,"n":len(sub),"adjusted_points_zscore":point[i],"ci_low":np.quantile(boots[:,i],.025),"ci_high":np.quantile(boots[:,i],.975),"top_6_rate":sub.top_6_points.mean()})
result=pd.DataFrame(rows); result.to_csv(ARTIFACTS/"inference_timing_intervals.csv",index=False)
best=result.sort_values(["position","adjusted_points_zscore"],ascending=[True,False]).groupby("position").first().reset_index(); (ARTIFACTS/"inference_best_windows.json").write_text(best.to_json(orient="records",indent=2),encoding="utf-8")
print(result.to_string(index=False))
# CELL [adjusted comparison chart]
traces=[]
for pos,color in [("QB","#2563eb"),("TE","#f97316")]:
    x=result.loc[result.position.eq(pos)]; traces.append({"type":"bar","name":pos,"x":x.timing_window.tolist(),"y":x.adjusted_points_zscore.round(4).tolist(),"marker":{"color":color},"error_y":{"type":"data","symmetric":False,"array":(x.ci_high-x.adjusted_points_zscore).round(4).tolist(),"arrayminus":(x.adjusted_points_zscore-x.ci_low).round(4).tolist()},"customdata":x.n.tolist(),"hovertemplate":"%{x}<br>adjusted z=%{y:.3f}<br>n=%{customdata}<extra>%{fullData.name}</extra>"})
write_chart("inference_01_adjusted_comparison.html",traces,{"title":"Adjusted QB and TE timing estimates with 95% intervals","barmode":"group","xaxis":{"title":"Draft-round window","type":"category","categoryorder":"array","categoryarray":windows},"yaxis":{"title":"Adjusted points z-score","zeroline":True}})
def interval_trace(pos,color):
    x=result.loc[result.position.eq(pos)]
    return {"type":"scatter","mode":"markers","name":pos,"x":x.adjusted_points_zscore.round(4).tolist(),"y":x.timing_window.tolist(),"marker":{"color":color,"size":11},"error_x":{"type":"data","symmetric":False,"array":(x.ci_high-x.adjusted_points_zscore).round(4).tolist(),"arrayminus":(x.adjusted_points_zscore-x.ci_low).round(4).tolist()},"customdata":x.n.tolist(),"hovertemplate":"Rounds %{y}<br>adjusted z=%{x:.3f}<br>n=%{customdata}<extra></extra>"}
# CELL [qb interval chart]
write_chart("inference_02_qb_intervals.html",[interval_trace("QB","#3b82f6")],{"title":"QB timing estimates and league-bootstrap uncertainty","xaxis":{"title":"Adjusted points z-score","zeroline":True},"yaxis":{"title":"Draft-round window","type":"category","categoryorder":"array","categoryarray":windows}})
# CELL [te interval chart]
write_chart("inference_03_te_intervals.html",[interval_trace("TE","#f97316")],{"title":"TE timing estimates and league-bootstrap uncertainty","xaxis":{"title":"Adjusted points z-score","zeroline":True},"yaxis":{"title":"Draft-round window","type":"category","categoryorder":"array","categoryarray":windows}})
''',
)

write(
    "04_out_of_sample_validation.ipynb",
    "NB04: forward-season validation",
    "Tests whether a timing window selected from earlier seasons retains an advantage in the next season.",
    COMMON + '''# CELL [calculate forward tests]
import pandas as pd
position=pd.read_csv(PROCESSED/"position_timing_panel.csv")
rows=[]
for pos in ["QB","TE"]:
    df=position.loc[position.position.eq(pos) & position.timing_window.isin(["1-3","4-5","6-7","8-9","10-11","12+"])]
    for year in sorted(df.season.unique())[1:]:
        train=df.loc[df.season<year]; test=df.loc[df.season.eq(year)]
        means=train.groupby("timing_window").filter(lambda x: len(x)>=100).groupby("timing_window").points_zscore.mean()
        if means.empty: continue
        best=means.idxmax(); selected=test.loc[test.timing_window.eq(best)]; other=test.loc[~test.timing_window.eq(best)]
        rows.append({"position":pos,"test_season":year,"selected_window":best,"train_n":len(train),"test_selected_n":len(selected),"test_z_difference":selected.points_zscore.mean()-other.points_zscore.mean(),"test_top6_difference":selected.top_6_points.mean()-other.top_6_points.mean()})
result=pd.DataFrame(rows); result.to_csv(ARTIFACTS/"validation_forward_seasons.csv",index=False)
print(result.to_string(index=False))
# CELL [forward scoring chart]
traces=[]
for pos,color in [("QB","#2563eb"),("TE","#f97316")]:
    x=result.loc[result.position.eq(pos)]; traces.append({"type":"bar","name":pos,"x":x.test_season.astype(str).tolist(),"y":x.test_z_difference.round(4).tolist(),"marker":{"color":color},"customdata":x.selected_window.tolist(),"hovertemplate":"%{x}<br>z difference=%{y:.3f}<br>selected=%{customdata}<extra>%{fullData.name}</extra>"})
write_chart("validation_01_forward_z_differences.html",traces,{"title":"Forward-season scoring difference for the selected strategy","barmode":"group","xaxis":{"title":"Test season","type":"category"},"yaxis":{"title":"Selected minus other teams: points z-score","zeroline":True}})
# CELL [forward top six chart]
traces=[]
for pos,color in [("QB","#2563eb"),("TE","#f97316")]:
    x=result.loc[result.position.eq(pos)]; traces.append({"type":"bar","name":pos,"x":x.test_season.astype(str).tolist(),"y":x.test_top6_difference.round(4).tolist(),"marker":{"color":color},"customdata":x.selected_window.tolist(),"hovertemplate":"%{x}<br>top-six difference=%{y:.1%}<br>selected=%{customdata}<extra>%{fullData.name}</extra>"})
write_chart("validation_02_forward_top6_differences.html",traces,{"title":"Forward-season top-six difference for the selected strategy","barmode":"group","xaxis":{"title":"Test season","type":"category"},"yaxis":{"title":"Selected minus other teams: top-six rate","tickformat":".0%","zeroline":True}})
# CELL [selection stability chart]
traces=[]
for pos,symbol in [("QB","circle"),("TE","diamond")]:
    x=result.loc[result.position.eq(pos)]; traces.append({"type":"scatter","mode":"markers+text","name":pos,"x":x.test_season.astype(str).tolist(),"y":x.selected_window.tolist(),"text":[f"{v:+.2f}" for v in x.test_z_difference],"textposition":"top center","marker":{"symbol":symbol,"size":14,"color":x.test_z_difference.round(4).tolist(),"colorscale":"RdBu","cmid":0,"showscale":pos=="QB","colorbar":{"title":"Test z diff"}},"hovertemplate":"%{x}<br>selected rounds %{y}<br>%{text}<extra>%{fullData.name}</extra>"})
write_chart("validation_03_selected_window_stability.html",traces,{"title":"Which timing window won in training, and how it tested next year","xaxis":{"title":"Test season","type":"category"},"yaxis":{"title":"Training-selected round window","type":"category"}})
''',
)

write(
    "05_availability_sensitivity.ipynb",
    "NB05: availability sensitivity",
    "Links drafted QBs and TEs to weekly participation by normalized name and repeats timing summaries among players active for at least 75% of the fantasy regular season.",
    COMMON + '''# CELL [link player availability]
import re,unicodedata
import pandas as pd
SOURCE=ROOT.parent/"fantasy_draft_order_study"
position=pd.read_csv(PROCESSED/"position_timing_panel.csv",dtype={"selected_player_id":str,"league_id":str})
participation=pd.read_csv(SOURCE/"data/cache/nflverse_weekly_participation_2018_2025.csv")
def fold(x): return re.sub(r"[^a-z0-9]","",unicodedata.normalize("NFKD",str(x)).encode("ascii","ignore").decode().lower())
position["fold_name"]=position.selected_player_name.map(fold); participation["fold_name"]=participation.player_display_name.map(fold)
keys=["league_id","season","draft_id","roster_id","position"]
eligible_weeks=position.merge(participation[["season","position","fold_name","week"]],on=["season","position","fold_name"],how="left")
eligible_weeks=eligible_weeks.loc[eligible_weeks.week.le(eligible_weeks.regular_season_weeks)]
active=eligible_weeks.groupby(keys,as_index=False).week.nunique().rename(columns={"week":"active_weeks"})
result=position.merge(active,on=keys,how="left")
result["availability_rate"]=result.active_weeks/result.regular_season_weeks; result["available_75"]=result.availability_rate>=.75
# CELL [summarize availability sample]
summary=(result.loc[result.available_75].groupby(["position","timing_window"],as_index=False).agg(n=("points_zscore","size"),mean_points_zscore=("points_zscore","mean"),top_6_rate=("top_6_points","mean")))
summary.to_csv(ARTIFACTS/"availability_timing_summary.csv",index=False); result[["league_id","season","draft_id","roster_id","position","timing_window","availability_rate","available_75"]].to_csv(PROCESSED/"position_availability_panel.csv",index=False)
print(summary.to_string(index=False))
# CELL [availability chart]
traces=[]
for pos,color in [("QB","#2563eb"),("TE","#f97316")]:
    x=summary.loc[summary.position.eq(pos)]; traces.append({"type":"bar","name":pos,"x":x.timing_window.tolist(),"y":x.mean_points_zscore.round(4).tolist(),"marker":{"color":color},"customdata":x.n.tolist(),"hovertemplate":"%{x}<br>z=%{y:.3f}<br>available n=%{customdata}<extra>%{fullData.name}</extra>"})
write_chart("availability_01_timing_points.html",traces,{"title":"Timing results when the selected QB or TE was available 75%+","barmode":"group","xaxis":{"title":"Draft-round window","type":"category","categoryorder":"array","categoryarray":["1-3","4-5","6-7","8-9","10-11","12+"]},"yaxis":{"title":"Mean points z-score","zeroline":True}})
''',
)

write(
    "06_joint_qb_te_recommendations.ipynb",
    "NB06: joint QB/TE timing and recommendations",
    "Builds the supported QB-by-TE response surface and combines inference and validation evidence into the final recommendation table.",
    COMMON + '''# CELL [build joint timing surface]
import json
import pandas as pd
team=pd.read_csv(PROCESSED/"team_timing_panel.csv"); inference=pd.read_csv(ARTIFACTS/"inference_timing_intervals.csv"); validation=pd.read_csv(ARTIFACTS/"validation_forward_seasons.csv")
joint=(team.groupby(["qb_timing_window","te_timing_window"],as_index=False).agg(n=("points_zscore","size"),leagues=("draft_id","nunique"),mean_points_zscore=("points_zscore","mean"),top_6_rate=("top_6_points","mean")))
joint["supported"]=joint.n>=100; joint.to_csv(ARTIFACTS/"joint_qb_te_timing.csv",index=False)
# CELL [assemble recommendations]
rows=[]
for pos in ["QB","TE"]:
    sub=inference.loc[inference.position.eq(pos)].sort_values("adjusted_points_zscore",ascending=False); best=sub.iloc[0]; val=validation.loc[validation.position.eq(pos) & validation.selected_window.eq(best.timing_window)]
    rows.append({"position":pos,"supported_round_window":best.timing_window,"n":int(best.n),"adjusted_points_zscore":best.adjusted_points_zscore,"ci_low":best.ci_low,"ci_high":best.ci_high,"top_6_rate":best.top_6_rate,"forward_tests_selecting_window":len(val),"positive_forward_tests":int((val.test_z_difference>0).sum()),"evidence_grade":"moderate" if len(val)>=2 and (val.test_z_difference>0).mean()>=.5 else "exploratory"})
recommendations=pd.DataFrame(rows); recommendations.to_csv(ARTIFACTS/"recommendations.csv",index=False)
best_joint=joint.loc[joint.supported].sort_values("mean_points_zscore",ascending=False).head(10); best_joint.to_csv(ARTIFACTS/"joint_supported_top10.csv",index=False)
print(recommendations.to_string(index=False)); print("\\nSupported joint cells:\\n",best_joint.to_string(index=False))
# CELL [joint heatmap]
order=["1-3","4-5","6-7","8-9","10-11","12+"]; supported=joint.loc[joint.supported].copy(); matrix=supported.pivot(index="qb_timing_window",columns="te_timing_window",values="mean_points_zscore").reindex(index=order,columns=order); counts=supported.pivot(index="qb_timing_window",columns="te_timing_window",values="n").reindex(index=order,columns=order)
z=matrix.astype(object).where(matrix.notna(),None).values.tolist(); custom=counts.astype(object).where(counts.notna(),None).values.tolist()
write_chart("recommendations_01_joint_heatmap.html",[{"type":"heatmap","x":order,"y":order,"z":z,"customdata":custom,"colorscale":"RdBu","zmid":0,"colorbar":{"title":"Mean z"},"hovertemplate":"QB %{y}<br>TE %{x}<br>mean z=%{z:.3f}<br>n=%{customdata}<extra></extra>"}],{"title":"Supported QB-by-TE timing combinations","xaxis":{"title":"First TE round window","type":"category","categoryorder":"array","categoryarray":order},"yaxis":{"title":"First QB round window","type":"category","categoryorder":"array","categoryarray":order}})
# CELL [recommendation chart]
write_chart("recommendations_02_position_summary.html",[{"type":"bar","x":recommendations.position.tolist(),"y":recommendations.adjusted_points_zscore.round(4).tolist(),"marker":{"color":["#2563eb","#f97316"]},"error_y":{"type":"data","symmetric":False,"array":(recommendations.ci_high-recommendations.adjusted_points_zscore).round(4).tolist(),"arrayminus":(recommendations.adjusted_points_zscore-recommendations.ci_low).round(4).tolist()},"customdata":recommendations[["supported_round_window","evidence_grade","n"]].values.tolist(),"hovertemplate":"%{x}<br>rounds %{customdata[0]}<br>adjusted z=%{y:.3f}<br>%{customdata[1]}, n=%{customdata[2]}<extra></extra>"}],{"title":"Current supported timing recommendation by position","xaxis":{"title":"Position"},"yaxis":{"title":"Adjusted points z-score","zeroline":True}})
''',
)

print("Generated 7 notebooks")
