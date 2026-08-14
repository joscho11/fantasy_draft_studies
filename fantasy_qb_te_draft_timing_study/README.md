# Fantasy QB and TE Draft Timing Study

**Question:** In completed 12-team redraft snake leagues, when should a team draft its first quarterback and first tight end?

This project reuses the validated Sleeper league outcomes from the sibling `fantasy_draft_order_study`. It studies descriptive adjusted associations, not causal effects.

## Primary population

- 12-team completed snake drafts, 2018-2025.
- One required QB, no superflex, and at least one required TE.
- Redraft scoring types (`ppr`, `half_ppr`, or `std`).
- At least 12 draft rounds, no keeper-tagged picks, no TE premium.
- Complete draft board and balanced 12-team outcome mapping.

## Run order

1. `tools/extract_complete_cache.py`
2. `tools/fetch_historic_full_boards.py` only when its resumable cache is incomplete
3. `tools/build_notebooks.py`
4. Notebooks `00` through `06`, in order

The notebooks are the executable analysis source of truth. `tools/run_notebooks.py` is a lightweight non-Jupyter verification runner.

## Main outputs

- `data/processed/league_seasons.csv`
- `data/processed/draft_picks.csv`
- `data/processed/team_timing_panel.csv`
- `data/processed/position_timing_panel.csv`
- `artifacts/recommendations.csv`
- `artifacts/joint_qb_te_timing.csv`
- `artifacts/eda_timing_window_associations.csv`

Recommendations are reported as supported round windows rather than a falsely precise single round.

## Visualization contract

Charts are the primary communication format. Every notebook writes and displays at least one interactive Plotly chart. EDA contains nine charts, including a practical points scale and separate QB/TE categorical-association diagnostics; inference contains three interval/result charts; forward-season evaluation contains three validation charts. Tables remain supporting export artifacts.

Each analytical operation is a separate notebook section. Every code cell is preceded by a short purpose statement and followed by an interpretation. Chart cells emit exactly one chart; transformations, model fitting, and validation calculations remain in their own cells.

Plotly is bundled under `assets/`, so saved notebook outputs and HTML artifacts render offline. Charts use an explicit dark theme with light text and high-contrast marks; notebook styling itself is not modified.

## Retained sample

The full-board recovery covers all 3,641 source league-seasons. Of these, 3,566 have structurally complete boards and 1,422 pass every primary format gate, producing 17,064 team-seasons from 2018 through 2025.

This is sufficient for broad two- or three-round timing windows. It is not sufficient to present a single exact round as universally optimal.

## Current results

The adjusted descriptive model currently ranks QB round 12+ highest (`+0.117` points z-score; 95% league-bootstrap interval `+0.057` to `+0.180`; 830 teams). This result is graded **exploratory** because forward-season selection chose that window only once.

For TE, rounds 10-11 rank highest (`+0.078`; interval `+0.036` to `+0.125`; 1,692 teams). This receives a **moderate** evidence grade: it was the training-period choice in three forward tests and remained positive in two.

These are associations among historical drafting strategies. They do not prove that delaying either position causes better results.
