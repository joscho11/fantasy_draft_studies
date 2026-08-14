"""Build notebooks/06_slot_points_and_snake_pairs.ipynb."""
from pathlib import Path

import nbformat as nbf

nb = nbf.v4.new_notebook()
nb["metadata"] = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "pygments_lexer": "ipython3"},
}


def md(text):
    return nbf.v4.new_markdown_cell(text)


def code(text):
    return nbf.v4.new_code_cell(text)


cells = []

cells.append(md("""# NB06: slot-points association and first-two-pick snake pairs

- **Purpose:** measure how much draft slot linearly explains regular-season team points, then compare the two players each seat actually drafted in rounds 1 and 2 (picks 1 and 24 versus 12 and 13, and the seats in between).
- **Pipeline:** retained team panel -> availability panel from NB05 -> rounds 1-2 Sleeper picks -> nflverse PPR points and availability for both picks -> four Plotly charts.
- **Inputs:** `data/processed/analysis_panel.csv`, `data/processed/first_round_availability_panel.csv`, Sleeper pick caches, nflverse weekly stats.
- **Outputs:** association tables, snake-pair panel, evaluation JSON, and four Plotly HTML charts under `artifacts/`.
- **Run:** execute after NB05.
- **Locked definitions:** Pearson r and R-squared come from a linear fit of within-league points z-score on draft slot. Snake pairs are that seat's round-1 and round-2 Sleeper picks (slot 1 is picks 1 and 24). Player production is nflverse regular-season PPR points inside that league's fantasy regular season. Availability is the NB05 75% rule. Injury-inclusive results stay primary.
- **Interpretation boundary:** a linear r does not capture the slot-1 hole or the slot-4 peak. Pair points use a common PPR scale, not each league's scoring settings.

| Gate | What it checks | Pass condition |
| ---: | --- | --- |
| 1 | Balanced team panel | 3,641 league-seasons, 12 slots, 3,641 rows per slot |
| 2 | Availability panel | Matches the 3,626-draft NB05 recoverable-pick panel |
| 3 | Snake-pair coverage | Complete round-1 and round-2 picks for at least 3,600 drafts |
| 4 | Pair linkage | At least 90% of pair rows have both players linked |
| 5 | Artifacts | Four HTML charts and the association tables are written |
"""))

cells.append(md("""### What this cell does

- Loads the retained team panel and the NB05 first-round availability panel.
- Imports the linear-fit helper so the r and R-squared formulas are not retyped later.
"""))

cells.append(code("""# CELL [1 load-panels]
from pathlib import Path
from IPython.display import display
import json
import math
import re
import sys
import time
import unicodedata
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

ROOT = Path.cwd().resolve().parent if Path.cwd().name == "notebooks" else Path.cwd().resolve()
sys.path.insert(0, str(ROOT))
from src.association import AVAILABILITY_THRESHOLD, linear_fit, pair_label, slot_means, snake_round2_pick_no

CACHE = ROOT / "data/cache"
PROCESSED = ROOT / "data/processed"
ARTIFACTS = ROOT / "artifacts"
ARTIFACTS.mkdir(exist_ok=True)

panel = pd.read_csv(PROCESSED / "analysis_panel.csv", dtype={"league_id": str, "draft_id": str, "roster_id": int})
avail = pd.read_csv(
    PROCESSED / "first_round_availability_panel.csv",
    dtype={"league_id": str, "draft_id": str, "roster_id": int, "sleeper_player_id": str},
)
assert len(panel) == 43_692
assert panel["draft_id"].nunique() == 3_641
assert panel.groupby("draft_slot").size().eq(3_641).all()
assert avail["draft_id"].nunique() == 3_626
assert avail.groupby("draft_slot").size().eq(3_626).all()
print({
    "team_seasons": int(len(panel)),
    "league_seasons": int(panel["draft_id"].nunique()),
    "availability_drafts": int(avail["draft_id"].nunique()),
    "availability_threshold": AVAILABILITY_THRESHOLD,
})
"""))

cells.append(md("""### Interpreting the output

- The team panel is the locked 3,641-league study. The availability panel is the 3,626-draft recoverable-pick subset from NB05.
- Gate 1 and gate 2 pass if those two counts print.
- Later snake-pair coverage can be smaller than 3,641 if round-2 picks are missing.
- This cell does not estimate r, R-squared, or player-level points.
"""))

cells.append(md("""### What this cell does

- Fits draft slot to within-league points z-score on every team-season, then again after keeping only first-rounders who cleared 75% availability.
- Also fits slot to raw regular-season points so the scoring-scale problem is visible.
"""))

cells.append(code("""# CELL [2 slot-points-association]
z_all = linear_fit(panel["draft_slot"], panel["points_zscore"])
raw_all = linear_fit(panel["draft_slot"], panel["regular_season_points"])
available_teams = avail.loc[avail["first_round_available"].astype(str).str.lower().isin(["true", "1"])].copy()
available_teams = available_teams.merge(
    panel[["draft_id", "draft_slot", "regular_season_points"]],
    on=["draft_id", "draft_slot"],
    how="left",
    validate="one_to_one",
)
z_avail = linear_fit(available_teams["draft_slot"], available_teams["points_zscore"])
raw_avail = linear_fit(available_teams["draft_slot"], available_teams["regular_season_points"])

slot_z = slot_means(panel, "points_zscore").rename(columns={"mean_value": "mean_zscore"})
slot_z_avail = slot_means(available_teams, "points_zscore").rename(columns={"mean_value": "mean_zscore"})
slot_pts = slot_means(panel, "regular_season_points").rename(columns={"mean_value": "mean_points"})
slot_pts_avail = slot_means(available_teams, "regular_season_points").rename(columns={"mean_value": "mean_points"})

assoc_rows = pd.DataFrame([
    {"sample": "All team-seasons", "outcome": "points_zscore", **z_all},
    {"sample": "All team-seasons", "outcome": "regular_season_points", **raw_all},
    {"sample": "First-round available", "outcome": "points_zscore", **z_avail},
    {"sample": "First-round available", "outcome": "regular_season_points", **raw_avail},
])
print(assoc_rows[["sample", "outcome", "n", "pearson_r", "r_squared", "spearman_rho", "slope"]].to_string(index=False))
print({
    "mean_z_slot1": round(float(slot_z.loc[slot_z["draft_slot"] == 1, "mean_zscore"].iloc[0]), 3),
    "mean_z_slot4": round(float(slot_z.loc[slot_z["draft_slot"] == 4, "mean_zscore"].iloc[0]), 3),
    "available_team_seasons": int(len(available_teams)),
})
"""))

cells.append(md("""### Interpreting the output

- Pearson r and R-squared are for a straight line through slot 1 through 12. Slot 1 is weak and slot 4 is the peak, so a line is a blunt summary.
- Raw-points r is mostly league scoring scale. The z-score fit is the comparable one.
- The availability sample drops teams whose actual first-round pick sat under 75% of that league's fantasy weeks. It is not a pure injury flag.
- A small R-squared means draft slot explains little of the team-to-team points spread. It does not mean the slot pattern is zero.
"""))

cells.append(md("""### What this cell does

- Draws mean within-league z-score by draft slot for the full panel, with the fitted line.
- Draws the same chart after the 75% first-round availability filter.
"""))

cells.append(code("""# CELL [3 charts-slot-points]
def z_chart(means, fit, title, filename):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=means["draft_slot"],
        y=means["mean_zscore"],
        mode="markers+lines",
        name="Mean z-score",
        marker={"size": 10, "color": "#3367d6"},
    ))
    x_line = np.array([1.0, 12.0])
    fig.add_trace(go.Scatter(
        x=x_line,
        y=fit["intercept"] + fit["slope"] * x_line,
        mode="lines",
        name="Linear fit",
        line={"color": "#d93025", "dash": "dash"},
    ))
    fig.update_layout(
        template="plotly_white",
        height=520,
        title=title,
        xaxis_title="Draft slot",
        yaxis_title="Mean within-league points z-score",
        annotations=[{
            "x": 0.99,
            "y": 0.02,
            "xref": "paper",
            "yref": "paper",
            "xanchor": "right",
            "yanchor": "bottom",
            "showarrow": False,
            "text": f"r = {fit['pearson_r']:.3f}    R^2 = {fit['r_squared']:.3f}    n = {fit['n']:,}",
        }],
    )
    fig.add_hline(y=0, line_dash="dot", line_color="#5f6368")
    fig.write_html(ARTIFACTS / filename, include_plotlyjs="cdn")
    fig.show()
    return filename

chart1 = z_chart(slot_z, z_all, "Draft slot vs team regular-season points (z-score)", "association_01_slot_points.html")
chart2 = z_chart(slot_z_avail, z_avail, "Draft slot vs team points, first-rounder available 75%+", "association_02_slot_points_available.html")
print({"charts": [chart1, chart2]})
"""))

cells.append(md("""### Interpreting the output

- Chart 1 is every retained team-season. The markers are slot means. The dashed line is the linear fit behind r and R-squared.
- Chart 2 keeps only seats whose actual first-round pick cleared 75% availability.
- If the markers stay arched after the filter, the linear summary is still a poor description of the seat pattern.
- These charts are team totals, not the two drafted players.
"""))

cells.append(md("""### What this cell does

- Builds a compact cache of each draft's round-1 and round-2 Sleeper picks.
- Streams the retained 1.4 GB cache only for drafts that are not already in the compact file, then fetches any remainder from the Sleeper API.
"""))

cells.append(code("""# CELL [4 two-round-pick-cache]
PICK_CACHE_PATH = CACHE / "two_round_pick_cache.jsonl"
SOURCE_CACHE_PATH = CACHE / "sleeper_http_cache.json"
needed_drafts = set(panel["draft_id"].astype(str))
draft_records = {}
if PICK_CACHE_PATH.exists():
    with PICK_CACHE_PATH.open(encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            draft_records[record["draft_id"]] = record

missing_drafts = needed_drafts - set(draft_records)
extracted_from_source = 0
fetched_records = []
if missing_drafts and SOURCE_CACHE_PATH.exists():
    import ijson
    source_records = []
    with SOURCE_CACHE_PATH.open("rb") as handle:
        for key, payload in ijson.kvitems(handle, ""):
            parts = key.split("/")
            if len(parts) == 3 and parts[0] == "draft" and parts[2] == "picks" and parts[1] in missing_drafts:
                two = [pick for pick in (payload or []) if int(pick.get("round") or 0) in {1, 2}]
                record = {"draft_id": parts[1], "source": "retained_sleeper_http_cache", "picks": two}
                draft_records[parts[1]] = record
                source_records.append(record)
                extracted_from_source += 1
    if source_records:
        with PICK_CACHE_PATH.open("a", encoding="utf-8") as handle:
            for record in source_records:
                handle.write(json.dumps(record) + chr(10))

missing_drafts = sorted(needed_drafts - set(draft_records))

def fetch_two_rounds(draft_id):
    url = f"https://api.sleeper.app/v1/draft/{draft_id}/picks"
    request = Request(url, headers={"User-Agent": "fantasy-draft-order-study/0.3"})
    for attempt in range(5):
        try:
            with urlopen(request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
            two = [pick for pick in (payload or []) if int(pick.get("round") or 0) in {1, 2}]
            return {"draft_id": draft_id, "source": "sleeper_api_two_round_backfill", "picks": two}
        except HTTPError as error:
            if error.code not in {429, 500, 502, 503, 504} or attempt == 4:
                raise
        except (TimeoutError, URLError):
            if attempt == 4:
                raise
        time.sleep(2 ** attempt)

if missing_drafts:
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(fetch_two_rounds, draft_id): draft_id for draft_id in missing_drafts}
        for future in as_completed(futures):
            fetched_records.append(future.result())
    fetched_records.sort(key=lambda record: record["draft_id"])
    with PICK_CACHE_PATH.open("a", encoding="utf-8") as handle:
        for record in fetched_records:
            handle.write(json.dumps(record) + chr(10))
            draft_records[record["draft_id"]] = record

def round_counts(record):
    counts = defaultdict(int)
    for pick in record.get("picks") or []:
        counts[int(pick.get("round") or 0)] += 1
    return counts

usable = {}
for draft_id, record in draft_records.items():
    counts = round_counts(record)
    if counts.get(1) == 12 and counts.get(2) == 12:
        usable[draft_id] = record

assert set(draft_records) == needed_drafts
assert len(usable) >= 3600
print({
    "drafts_required": len(needed_drafts),
    "drafts_cached": len(draft_records),
    "drafts_with_complete_two_rounds": len(usable),
    "extracted_from_source": extracted_from_source,
    "fetched_this_run": len(fetched_records),
})
"""))

cells.append(md("""### Interpreting the output

- A usable draft has exactly 12 round-1 picks and 12 round-2 picks.
- Drafts below that bar are dropped from the snake-pair charts only. The team-points charts above still use the full panel.
- Later reruns should print extracted_from_source = 0 and fetched_this_run = 0.
- Cache completeness does not prove the two players were scored on a common PPR scale in their leagues.
"""))

cells.append(md("""### What this cell does

- Links both snake picks to GSIS identifiers, measures 75% availability for each pick, and sums nflverse PPR points over that league's fantasy regular season.
"""))

cells.append(code("""# CELL [5 link-pairs-and-ppr]
import nflreadpy as nfl

def fold_name(value):
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(character for character in text if not unicodedata.combining(character))
    return re.sub(r"[^a-z0-9]", "", text.lower())

league_settings = pd.read_csv(CACHE / "league_regular_season_settings.csv", dtype={"league_id": str})
settings = league_settings[["league_id", "playoff_week_start", "regular_season_weeks"]]

pick_rows = []
for draft_id, record in usable.items():
    for pick in record["picks"]:
        metadata = pick.get("metadata") or {}
        pick_rows.append({
            "draft_id": draft_id,
            "draft_slot": int(pick["draft_slot"]),
            "round": int(pick["round"]),
            "pick_no": int(pick["pick_no"]),
            "sleeper_player_id": str(pick.get("player_id") or metadata.get("player_id") or ""),
            "player_name": f"{metadata.get('first_name', '')} {metadata.get('last_name', '')}".strip(),
            "player_position": metadata.get("position"),
        })
picks = pd.DataFrame(pick_rows)
assert picks.groupby("draft_id").size().eq(24).all()

ids = nfl.load_ff_playerids().to_pandas()
ids = ids.loc[ids["sleeper_id"].notna() & ids["gsis_id"].notna(), ["sleeper_id", "gsis_id", "name"]].copy()
ids["sleeper_id"] = ids["sleeper_id"].astype(int).astype(str)
ids["gsis_id"] = ids["gsis_id"].astype(str)
ids = ids.drop_duplicates("sleeper_id", keep="first")
picks = picks.merge(ids.rename(columns={"sleeper_id": "sleeper_player_id", "name": "crosswalk_name"}), on="sleeper_player_id", how="left")

points_path = CACHE / "nflverse_weekly_ppr_2018_2025.csv"
if points_path.exists():
    weekly = pd.read_csv(points_path)
else:
    weekly = nfl.load_player_stats(list(range(2018, 2026))).to_pandas()
    weekly = weekly.loc[weekly["season_type"].eq("REG"), ["player_id", "player_display_name", "position", "season", "week", "fantasy_points_ppr"]].copy()
    weekly.to_csv(points_path, index=False)
weekly["player_id"] = weekly["player_id"].astype(str)
weekly["season"] = weekly["season"].astype(int)
weekly["week"] = weekly["week"].astype(int)
weekly["fantasy_points_ppr"] = weekly["fantasy_points_ppr"].fillna(0.0).astype(float)
weekly["fold_name"] = weekly["player_display_name"].map(fold_name)

fallback = (
    weekly.sort_values(["season", "week"])
    .drop_duplicates(["season", "fold_name", "position"], keep="first")
    [["season", "fold_name", "position", "player_id"]]
    .rename(columns={"player_id": "gsis_id_fallback"})
)
picks["fold_name"] = picks["player_name"].map(fold_name)
teams = panel.loc[panel["draft_id"].isin(usable), ["league_id", "season", "draft_id", "draft_slot"]].copy()
picks = picks.merge(teams[["draft_id", "season", "league_id"]].drop_duplicates(), on="draft_id", how="left")
picks = picks.merge(fallback, left_on=["season", "fold_name", "player_position"], right_on=["season", "fold_name", "position"], how="left")
picks["gsis_id"] = picks["gsis_id"].fillna(picks["gsis_id_fallback"])
picks = picks.drop(columns=["position", "gsis_id_fallback"], errors="ignore")
picks = picks.merge(settings, on="league_id", how="left")

scored = weekly.merge(
    picks.loc[picks["gsis_id"].notna(), ["gsis_id", "season", "regular_season_weeks"]].drop_duplicates(),
    left_on=["player_id", "season"],
    right_on=["gsis_id", "season"],
    how="inner",
)
scored = scored.loc[scored["week"] < (scored["regular_season_weeks"] + 1)]
points = scored.groupby(["gsis_id", "season", "regular_season_weeks"], as_index=False).agg(
    active_weeks=("week", "size"),
    ppr_points=("fantasy_points_ppr", "sum"),
)
picks = picks.merge(points, on=["gsis_id", "season", "regular_season_weeks"], how="left")
picks["player_linked"] = picks["gsis_id"].notna()
picks["active_weeks"] = picks["active_weeks"].fillna(0).astype(int)
picks["ppr_points"] = np.where(picks["player_linked"], picks["ppr_points"].fillna(0.0), np.nan)
picks["availability_rate"] = np.where(picks["player_linked"], picks["active_weeks"] / picks["regular_season_weeks"], np.nan)
picks["available"] = pd.Series(pd.NA, index=picks.index, dtype="boolean")
picks.loc[picks["player_linked"], "available"] = picks.loc[picks["player_linked"], "availability_rate"] >= AVAILABILITY_THRESHOLD

r1 = picks.loc[picks["round"] == 1].copy()
r2 = picks.loc[picks["round"] == 2].copy()
pairs = r1.merge(
    r2,
    on=["draft_id", "draft_slot", "season", "league_id", "regular_season_weeks"],
    suffixes=("_r1", "_r2"),
    validate="one_to_one",
)
pairs["pair_label"] = pairs["draft_slot"].map(pair_label)
pairs["expected_r2_pick_no"] = pairs["draft_slot"].map(snake_round2_pick_no)
pairs["both_linked"] = pairs["player_linked_r1"] & pairs["player_linked_r2"]
pairs["pair_ppr"] = pairs["ppr_points_r1"] + pairs["ppr_points_r2"]
pairs["both_available"] = (pairs["available_r1"] == True) & (pairs["available_r2"] == True)
linked_pairs = pairs.loc[pairs["both_linked"]].copy()
available_pairs = linked_pairs.loc[linked_pairs["both_available"]].copy()

linked_share = float(pairs["both_linked"].mean())
assert linked_share >= 0.90
assert linked_pairs.groupby("draft_slot").size().min() >= 2000
print({
    "usable_drafts": int(len(usable)),
    "pair_rows": int(len(pairs)),
    "both_linked_share": round(linked_share, 4),
    "linked_pairs": int(len(linked_pairs)),
    "both_available_pairs": int(len(available_pairs)),
    "mean_pair_ppr": round(float(linked_pairs["pair_ppr"].mean()), 1),
    "slot1_label": pair_label(1),
    "slot12_label": pair_label(12),
})
"""))

cells.append(md("""### Interpreting the output

- Pair PPR is the sum of the two drafted players' nflverse PPR points in that league's regular-season window. It is not the team's Sleeper points-for.
- both_available requires each of those two players to clear 75% availability. That is stricter than NB05, which only conditioned on the first-rounder.
- Missing links are dropped, not scored as zero.
- This still does not separate injury from benchings, suspensions, or other absences.
"""))

cells.append(md("""### What this cell does

- Averages the two-pick PPR total by draft slot, with and without the availability filter, and draws those two charts.
- Labels seats as 1 and 24 through 12 and 13.
"""))

cells.append(code("""# CELL [6 charts-snake-pairs]
pair_all = linear_fit(linked_pairs["draft_slot"], linked_pairs["pair_ppr"])
pair_avail_fit = linear_fit(available_pairs["draft_slot"], available_pairs["pair_ppr"])
means_all = slot_means(linked_pairs, "pair_ppr")
means_avail = slot_means(available_pairs, "pair_ppr")

def pair_chart(means, fit, title, filename):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=means["pair_label"],
        y=means["mean_value"],
        marker_color="#3367d6",
        name="Mean combined PPR",
    ))
    x_num = means["draft_slot"].to_numpy(dtype=float)
    fig.add_trace(go.Scatter(
        x=means["pair_label"],
        y=fit["intercept"] + fit["slope"] * x_num,
        mode="lines",
        name="Linear fit vs slot",
        line={"color": "#d93025", "dash": "dash"},
    ))
    fig.update_layout(
        template="plotly_white",
        height=540,
        title=title,
        xaxis_title="Snake pair (round 1 and round 2)",
        yaxis_title="Mean combined regular-season PPR",
        annotations=[{
            "x": 0.99,
            "y": 0.02,
            "xref": "paper",
            "yref": "paper",
            "xanchor": "right",
            "yanchor": "bottom",
            "showarrow": False,
            "text": f"r = {fit['pearson_r']:.3f}    R^2 = {fit['r_squared']:.3f}    n = {fit['n']:,}",
        }],
    )
    fig.write_html(ARTIFACTS / filename, include_plotlyjs="cdn")
    fig.show()
    return filename

chart3 = pair_chart(means_all, pair_all, "First two picks combined PPR by snake seat", "association_03_snake_pairs.html")
chart4 = pair_chart(means_avail, pair_avail_fit, "First two picks combined PPR, both available 75%+", "association_04_snake_pairs_available.html")
print(means_all[["draft_slot", "pair_label", "n", "mean_value"]].to_string(index=False))
print({
    "pair_r": round(pair_all["pearson_r"], 4),
    "pair_r2": round(pair_all["r_squared"], 4),
    "pair_r_available": round(pair_avail_fit["pearson_r"], 4),
    "pair_r2_available": round(pair_avail_fit["r_squared"], 4),
    "charts": [chart3, chart4],
})
"""))

cells.append(md("""### Interpreting the output

- Each bar is the average combined PPR of that seat's first two drafted players.
- Slot 1 is picks 1 and 24. Slot 12 is picks 12 and 13. That is the usual snake-equity argument.
- The availability chart drops a seat-season unless both of those players cleared 75% of the fantasy regular season.
- Common PPR lets seats be compared across mixed league settings. It does not say those players scored that many points in their actual league.
"""))

cells.append(md("""### What these tests guard

- Writes the association table, snake-pair summaries, linked pair panel, evaluation JSON, and confirms four charts exist.
"""))

cells.append(code("""# CELL [7 write-artifacts]
assoc_path = ARTIFACTS / "association_slot_fits.csv"
pair_summary_path = ARTIFACTS / "association_snake_pair_summary.csv"
pair_panel_path = PROCESSED / "snake_pair_panel.csv"
evaluation_path = ARTIFACTS / "association_evaluation.json"

assoc_rows.to_csv(assoc_path, index=False)
pair_summary = pd.concat([
    means_all.assign(sample="All linked pairs"),
    means_avail.assign(sample="Both picks available"),
], ignore_index=True)
pair_summary.to_csv(pair_summary_path, index=False)
export_cols = [
    "league_id", "season", "draft_id", "draft_slot", "pair_label",
    "pick_no_r1", "pick_no_r2", "player_name_r1", "player_name_r2",
    "ppr_points_r1", "ppr_points_r2", "pair_ppr",
    "available_r1", "available_r2", "both_available",
]
linked_pairs[export_cols].to_csv(pair_panel_path, index=False)

figures = [
    "association_01_slot_points.html",
    "association_02_slot_points_available.html",
    "association_03_snake_pairs.html",
    "association_04_snake_pairs_available.html",
]
for name in figures:
    assert (ARTIFACTS / name).exists()

evaluation = {
    "team_panel_league_seasons": 3641,
    "zscore_pearson_r": z_all["pearson_r"],
    "zscore_r_squared": z_all["r_squared"],
    "zscore_pearson_r_available": z_avail["pearson_r"],
    "zscore_r_squared_available": z_avail["r_squared"],
    "snake_pair_drafts": int(len(usable)),
    "linked_pairs": int(len(linked_pairs)),
    "both_available_pairs": int(len(available_pairs)),
    "pair_pearson_r": pair_all["pearson_r"],
    "pair_r_squared": pair_all["r_squared"],
    "pair_pearson_r_available": pair_avail_fit["pearson_r"],
    "pair_r_squared_available": pair_avail_fit["r_squared"],
    "availability_threshold": AVAILABILITY_THRESHOLD,
    "player_points_scale": "nflverse regular-season PPR inside each league fantasy window",
    "primary_result_remains_injury_inclusive": True,
    "plotly_artifacts": figures,
}
evaluation_path.write_text(json.dumps(evaluation, indent=2), encoding="utf-8")

display_frame = assoc_rows[["sample", "outcome", "n", "pearson_r", "r_squared", "spearman_rho", "slope"]].copy()
try:
    from great_tables import GT
    display(GT(display_frame).fmt_number(columns=["pearson_r", "r_squared", "spearman_rho", "slope"], decimals=4))
except ImportError:
    try:
        from itables import init_notebook_mode, show
        init_notebook_mode(all_interactive=True)
        show(display_frame)
    except ImportError:
        display(display_frame)

print({
    "files_written": 3 + len(figures),
    "z_r2": round(z_all["r_squared"], 4),
    "pair_r2": round(pair_all["r_squared"], 4),
})
"""))

cells.append(md("""### Reading the test result

- The printed r and R-squared values are the ones to quote. They come from this run, not from a target.
- Four HTML charts plus the CSV and JSON sidecars should exist under artifacts/ and data/processed/.
- Injury-inclusive fits remain the headline. The availability rows are the filter Joseph asked for.
- This does not prove a causal draft-order effect, and it does not say snake pairs are equal after averaging.
"""))

cells.append(md("""## Conclusion

- NB06 adds the linear association Joseph asked for and the snake-pair comparison of each seat's first two picks.
- Team-points r and R-squared use within-league z-scores. Pair charts use combined nflverse PPR for picks such as 1 and 24 versus 12 and 13.
- Availability charts reuse the NB05 75% rule. Chart 2 filters on the first-rounder. Chart 4 requires both picks to clear it.
- Next notebook may run after these four charts exist. This notebook does not replace NB02 or NB05, and it does not settle causality.
"""))

nb["cells"] = cells
out = Path(__file__).resolve().parents[1] / "notebooks" / "06_slot_points_and_snake_pairs.ipynb"
nbf.write(nb, out)
print("wrote", out, "cells", len(cells))
