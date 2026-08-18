# Fantasy Draft Order Study

**Question:** In completed season-long 12-team standard snake leagues, how does draft slot relate to regular-season points performance?

Public GitHub: [joscho11/fantasy_draft_studies](https://github.com/joscho11/fantasy_draft_studies) (this study is a subdirectory).

Results are descriptive associations in a convenience sample of public Sleeper leagues. They are not a causal draft-order effect, and they do not speak to best ball, head-to-head record, or playoffs.

## Locked study population

- 12 teams
- Completed NFL season
- Season-long league, not best ball
- Standard snake draft
- Any scoring or roster format
- Complete draft-slot mapping and regular-season points-for records

Best-ball, incomplete, and structurally invalid leagues are excluded. Scoring and roster format may vary.

## Locked outcomes

- Regular-season points-for z-score within league-season
- Regular-season points rank
- Top-six points share, with fractional credit for exact cutoff ties
- Top-scorer share, with fractional credit for exact first-place ties

Sleeper states that its roster points-for totals cover the regular season only. A deterministic sample is independently audited against weekly matchup totals before the acquisition gate can pass.

## Sample

Retained panel: **3,641** balanced league-seasons and **43,692** team-seasons, 2018-2025, with **3,641** observations per draft slot. No 2017 candidate passed validation.

| Season | League-seasons |
| ---: | ---: |
| 2018 | 9 |
| 2019 | 134 |
| 2020 | 367 |
| 2021 | 503 |
| 2022 | 526 |
| 2023 | 601 |
| 2024 | 762 |
| 2025 | 739 |

Historic validation added 1,013 league-seasons across 2018-2021. The prior 2022-2025 panel contributed 2,628.

## Observed slot pattern (NB02)

Source: `artifacts/eda_slot_summary.csv`. Rates use fractional tie credit.

| Slot | Points z-score | Mean finish | Top-six | Top scorer |
| ---: | ---: | ---: | ---: | ---: |
| 1 | -0.102 | 6.83 | 46.1% | 7.05% |
| 2 | -0.006 | 6.48 | 49.8% | 7.90% |
| 3 | +0.039 | 6.36 | 51.5% | 8.83% |
| 4 | +0.056 | 6.29 | 52.8% | 9.38% |
| 5 | +0.030 | 6.39 | 51.3% | 8.42% |
| 6 | +0.030 | 6.40 | 50.9% | 9.11% |
| 7 | +0.015 | 6.43 | 51.3% | 9.02% |
| 8 | +0.025 | 6.42 | 50.3% | 8.33% |
| 9 | -0.017 | 6.55 | 49.2% | 7.18% |
| 10 | -0.045 | 6.64 | 48.8% | 8.91% |
| 11 | -0.007 | 6.53 | 49.1% | 8.11% |
| 12 | -0.019 | 6.58 | 49.0% | 7.76% |

- Slot 4 is the strongest seat on all three headline outcomes. Slot 1 is the weakest.
- Slots 2-8 finish top six **51.1%** of the time (mean finish 6.40). Slots 9-12 finish top six **49.0%** (mean finish 6.57).
- Slot 4 minus slot 1 is **6.74** percentage points in the top-six rate on this 3,641-league panel. Do not mix that figure with the 6.80 point gap on the 3,626-league availability panel in NB05.

## Inference (NB03)

2,000 league-cluster bootstrap replicates, vs a 50% top-six baseline and an 8.33% top-scorer baseline.

- Slot 4 top-six: **+2.80** percentage points (95% CI **+1.13 to +4.45**).
- Slot 1 top-six: **-3.94** percentage points (95% CI **-5.52 to -2.28**).
- Slot 4 points z-score: **+0.056** (95% CI **+0.023 to +0.089**). Slot 1: **-0.102** (95% CI **-0.133 to -0.069**).
- The slot 4 minus slot 1 top-six gap is negative in **2020** and **2021**. It is a tie in 2018 (n=9).

## Season-finish simulation (NB04)

100,000 simulated 17-week, 12-team league-seasons per scenario. Rank target is final regular-season points only. Weekly matchup scores are not in the retained panel, so week-to-week persistence is an assumed ICC (0.05, 0.15, 0.30), not an estimated parameter. The simulation is model-based. It is not a causal estimate.

Pooled 2018-2025 effects, ICC 0.15:

| Slot | Expected finish | Top-six | First overall |
| ---: | ---: | ---: | ---: |
| 1 | 6.816 | 46.19% | 7.17% |
| 4 | 6.316 | 52.32% | 9.05% |

Rank-accounting, null-symmetry, and Monte Carlo precision gates passed. Maximum first-place Monte Carlo SE was 0.093 percentage points.

## First-round availability (NB05)

Mechanism check, not a replacement for the injury-inclusive primary result.

- Recovers actual Sleeper first-round picks for **3,626 of 3,641** drafts (15 drafts have no recoverable pick list).
- A first-rounder is "available" if that player appeared in at least **75%** of that league's fantasy regular-season weeks.
- Slot 1 unavailability is **42.3%**, the highest of any seat.
- After dropping unavailable first-rounders, slot 1 top-six rises from **46.1% to 53.3%**. The slot 4 minus slot 1 gap shrinks from **6.80 to 2.84** percentage points (this 6.80 is the 3,626-league panel, not the 6.74 EDA gap above).
- Keep the injury-inclusive 3,641-league result as the real-world headline.

## Slot-points association and snake pairs (NB06)

Linear Pearson r of draft slot vs within-league points z-score is **-0.0009** (R-squared **0.0000008**, n = 43,692). A straight line through seats 1-12 does not describe the pattern. Slot 1 is still weak and slot 4 is still the peak.

After the NB05 75% first-rounder filter (n = 31,018), z-score r is **-0.021** (R-squared **0.0004**).

Snake pairs are each seat's round-1 and round-2 Sleeper picks, scored in nflverse regular-season PPR inside that league's fantasy window. 3,624 drafts have complete two-round picks.

| Seat | Picks | Mean combined PPR | Both available |
| --- | --- | ---: | ---: |
| 1 | 1 and 24 | 352.9 | 448.9 |
| 4 | 4 and 21 | 387.8 | 453.3 |
| 12 | 12 and 13 | 380.3 | 446.0 |

Picks 12 and 13 beat 1 and 24 on the injury-inclusive average. That gap mostly closes when both players stay available. Pair-level linear R-squared is still ~0. Charts: `association_01` through `association_04` HTML files.

## What this does not prove

- A causal effect of draft slot. Public-league assignment is not a randomized experiment.
- Results for best ball, head-to-head wins, or playoff outcomes.
- That every season looks like the pooled table. 2020 and 2021 go the other way on slot 4 vs slot 1.
- An estimated weekly-scoring correlation. NB04 tests assumed ICC values because weekly scores were not retained.
- That injury is the only reason slot 1 is weak. NB05 conditions on availability. It does not separate injury from other absences.

## Run order

| # | Notebook | Purpose | Writes |
|---|---|---|---|
| 00 | `notebooks/00_configuration.ipynb` | Study definitions and analysis contract | Configuration workflow chart |
| 01 | `notebooks/01_data_acquisition_and_preparation.ipynb` | Validate Sleeper output and prepare the analysis panel | `data/processed/analysis_panel.csv`, panel manifest |
| 02 | `notebooks/02_eda.ipynb` | Coverage and descriptive draft-slot patterns | Six Plotly EDA charts and summaries |
| 03 | `notebooks/03_statistical_inference_and_robustness.ipynb` | Clustered uncertainty intervals and season sensitivity | Inference tables and interval charts |
| 04 | `notebooks/04_monte_carlo_season_finish_simulation.ipynb` | Model-based 17-week final points-rank simulation | Rank probabilities, scenario summaries, and four Plotly charts |
| 05 | `notebooks/05_first_round_availability_sensitivity.ipynb` | First-round availability sensitivity using actual Sleeper picks | Availability-conditioned slot summaries and interval charts |
| 06 | `notebooks/06_slot_points_and_snake_pairs.ipynb` | Linear r / R-squared of slot vs points, plus first-two-pick snake pairs | Four Plotly charts, association tables, snake-pair panel |

Open and run the notebooks in order in Jupyter or VS Code. Executable work stays in notebooks. There is no `src/` helper package.

`artifacts/model_*.csv` / `model_*.json` / `model_*.svg` are from the pre-expansion 2,628-league panel. Use `inference_*`, `eda_*`, `simulation_*`, and `availability_*` for the 3,641-league study.

## Layout

```text
fantasy_draft_order_study/
  notebooks/       Executable source of truth
  data/cache/      Resumable HTTP response cache (reproducibility source)
  data/processed/  Team-season and analysis-panel data
  artifacts/       Manifests, charts, and inference summaries
  catonsville/     Catonsville FF 2023-2025 application (canvas copy)
```

Treat the files under `data/cache/` as the reproducibility source of record. Do not delete or regenerate them unless intentionally expanding the study. The current panel can be rebuilt from cache without further Sleeper API calls.
