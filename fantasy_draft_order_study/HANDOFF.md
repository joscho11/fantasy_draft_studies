# Fantasy draft order study: handoff

## Objective

Estimate the association between draft slot and regular-season fantasy-football scoring in public, 12-team, season-long snake-draft leagues. The analysis deliberately excludes best ball, playoff outcomes, and format as a restriction.

Primary outcomes are:

- Within-league regular-season points z-score.
- Finish in the top six in regular-season points.
- Outright regular-season top scorer.

## Current data

The retained study panel contains 3,641 balanced league-seasons and 43,692 team-seasons from 2018 through 2025. Each draft slot has exactly 3,641 observations.

| Season | League-seasons |
| --- | ---: |
| 2018 | 9 |
| 2019 | 134 |
| 2020 | 367 |
| 2021 | 503 |
| 2022 | 526 |
| 2023 | 601 |
| 2024 | 762 |
| 2025 | 739 |

No 2017 candidates passed final validation. Historic validation added 1,013 league-seasons across 2018 to 2021. The prior 2022 to 2025 panel contributed 2,628 league-seasons.

## Local data retention

The project is self-contained and should not require continued Sleeper API access to reproduce the existing study.

| Path | Contents |
| --- | --- |
| `data/cache/sleeper_http_cache.json` | Current-era Sleeper API response cache, about 1.4 GB. |
| `data/cache/historic_user_leagues.jsonl` | Historic league-discovery responses. |
| `data/cache/historic_drafts_and_rosters.jsonl` | Historic draft and roster validation responses. |
| `data/processed/team_seasons.csv` | Validated league-team rows. |
| `data/processed/analysis_panel.csv` | Inference-ready outcome panel. |

Treat the cached API responses as the reproducibility source of record. Do not delete or regenerate them unless intentionally expanding the dataset.

## Notebook pipeline

1. `notebooks/00_configuration.ipynb`: configuration and locked study definitions.
2. `notebooks/01_data_acquisition_and_preparation.ipynb`: validation, outcome construction, and panel creation.
3. `notebooks/02_eda.ipynb`: descriptive analysis and interactive Plotly EDA charts.
4. `notebooks/03_statistical_inference_and_robustness.ipynb`: league-cluster bootstrap intervals and season sensitivity.
5. `notebooks/04_monte_carlo_season_finish_simulation.ipynb`: planned simulation of 17 straight regular-season weeks to forecast final points rank by draft slot. It must not use playoff outcomes.

The notebooks have intentionally cleared execution outputs so that old 2,628-league displays cannot be confused with the expanded panel. Rerun them to repopulate current results.

## Latest results

Pooled descriptive results from the 3,641-league panel:

| Draft slot | Points z-score | Top-six rate | Top-scorer rate |
| --- | ---: | ---: | ---: |
| 1 | -0.102 | 46.1% | 7.05% |
| 4 | +0.056 | 52.8% | 9.38% |

Slot 4 minus slot 1 is 0.158 z-score points, 6.74 percentage points in the top-six rate, and 2.33 percentage points in the top-scorer rate. These are descriptive, not causal, comparisons.

NB03 uses 2,000 league-cluster bootstrap replicates. Against the 50% top-six baseline, slot 4 is +2.80 percentage points with a 95% interval of +1.13 to +4.45, while slot 1 is -3.94 points with an interval of -5.52 to -2.28.

## Visuals

NB02 writes six interactive Plotly HTML artifacts under `artifacts/`, including `eda_06_year_over_year_points.html`. That figure shows the draft-slot to points relationship by individual season, with every available year next to the latest three years.

NB01 and NB03 still have SVG chart implementations. Convert those to Plotly if a fully consistent Plotly pipeline is desired.

## Planned NB04: Monte Carlo season-finish simulation

Add `notebooks/04_monte_carlo_season_finish_simulation.ipynb` to simulate a 17-week, no-playoff regular season and estimate the distribution of final league finish for each draft slot. The desired output is the probability of finishing in each final regular-season points rank, plus summaries such as expected finish, median finish, and probability of first overall by points.

The simulation should be explicitly model-based, not presented as an observed causal effect. Calibrate it from the saved historical panel, preserve the 12-team league structure, state all assumptions about weekly scoring variation and correlation, set a reproducible random seed, and include sensitivity scenarios. Use Plotly for the simulation visuals, including final-rank distributions and draft-slot comparisons.

## Operating conventions

- Keep the project notebook-only for executable work. Do not add `.py` helpers.
- Use Plotly by default for notebook visualizations.
- Keep at least one chart in each notebook, at least five in EDA, and at least three in inference/evaluation.
- Every code cell requires markdown immediately before and after it. Code cells begin with `# CELL [...]`.
- Interpretation markdown must state the actual executed result, its project implication, and what it does not prove. Do not write placeholder descriptions of what a chart will show.
- When reporting coverage, always give the total available league-seasons.
