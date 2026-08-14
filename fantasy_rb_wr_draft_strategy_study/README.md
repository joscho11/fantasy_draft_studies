# Fantasy RB/WR Draft Strategy Study

**Primary question:** In completed 12-team, conventional-lineup, 1QB redraft leagues, which RB/WR allocation through Round 6 is associated with the strongest regular-season points performance after accounting for draft slot, season, scoring format, lineup format, and early non-RB/WR investment?

**Prespecified side question:** Among teams selecting an RB or WR in Round 1, how does first-round position relate to regular-season performance, and how much of the difference remains when the selected player is available for at least 75% of the fantasy regular season?

This project reuses the validated outcomes and complete Sleeper draft boards from the sibling `fantasy_qb_te_draft_timing_study`. Results are descriptive adjusted associations, not causal strategy effects.

## Locked primary population

- Completed 12-team snake drafts, 2018-2025.
- Redraft with one required QB, no superflex, and at least one required TE.
- Exactly two starting RB slots, two or three starting WR slots, and at least one flex.
- PPR or half-PPR scoring; standard scoring is excluded because only six otherwise-eligible leagues are available.
- At least 12 rounds, no keeper-tagged picks, no TE premium, and a complete draft board.
- Exactly one owned selection per team in every round through Round 8; leagues with early traded-pick imbalance are excluded so each checkpoint has a fixed draft-capital budget.

## Locked strategy definitions

Round 6 is the primary checkpoint. Teams are classified by the number of RBs selected in the first six rounds:

| Strategy | RBs through Round 6 |
| --- | ---: |
| Zero RB | 0 |
| WR-heavy | 1 |
| Balanced | 2 |
| RB-heavy | 3 or more |

The adjusted model includes the number of non-RB/WR picks through Round 6. Conditional on that quantity, moving between RB-count categories represents replacing WR draft capital with RB draft capital. Rounds 2, 4, and 8 are secondary checkpoints.

## Outcomes and inference

- Primary: regular-season points-for z-score within league-season.
- Secondary: league-relative points per week, fractional top-six points finish, points rank, and fractional top-scorer credit.
- Adjustment: draft slot, season, PPR versus half-PPR, starting-WR count, flex count, and early non-RB/WR investment.
- Uncertainty: 2,000 league-cluster bootstrap replicates for headline models.
- Validation: expanding-window forward-season tests.
- Availability: post-draft sensitivity analysis only; it does not replace the injury-inclusive result.

## Run order

1. `tools/build_notebooks.py`
2. `tools/run_notebooks.py`
3. Notebooks `00` through `07`, in order, for interactive review.

The notebooks are the executable analysis source of truth. `tools/run_notebooks.py` executes their code cells without requiring Jupyter, embeds chart outputs, and refreshes the interpretation cell after every code cell from the values actually produced.

## Current results

The retained panel contains **1,371 league-seasons and 16,452 team-seasons** from 2018-2025. It excludes six otherwise-eligible standard leagues and 22 leagues with unequal early pick ownership.

### Round 6 allocation

The result is a supported tier, not a unique winner: **reach Round 6 with two or three RBs**. The prespecified RB-heavy group (3+) has the highest adjusted estimate, but it is not distinguishable from the balanced two-RB group.

| Round 6 build | Teams | Adjusted points z | 95% league-bootstrap interval |
| --- | ---: | ---: | ---: |
| Zero RB (0) | 254 | -0.162 | -0.283 to -0.033 |
| WR-heavy (1) | 2,229 | -0.049 | -0.090 to -0.008 |
| Balanced (2) | 8,666 | +0.001 | -0.015 to +0.017 |
| RB-heavy (3+) | 5,303 | +0.027 | +0.001 to +0.052 |

RB-heavy minus balanced is **+0.026 z** (95% CI **-0.013 to +0.064**), so the data do not support forcing a third RB over a second. Both two-RB and 3+-RB builds beat both 0-RB and 1-RB builds in the pooled pairwise scoring contrasts. The exact-count diagnostic ranks three RBs highest at +0.034 adjusted z, but three minus two is still uncertain (**+0.033**, CI **-0.006 to +0.072**); four or more RBs show no added measured benefit.

Practical magnitude remains modest. The pooled RB-heavy estimate corresponds to **+0.31 league-relative points per week** and a **50.9%** adjusted top-six rate, versus +0.06 points per week and 50.2% for balanced. Forward evidence is mixed: RB-heavy was selected in four expanding-window tests and was positive in two, with an average adjusted next-season scoring difference near zero. Treat “two or three RBs by Round 6” as a historical lean, not a universal rule.

### First-round RB versus WR

There is **no clear overall edge** on the primary scoring outcome. Adjusted first-round RB minus WR is **-0.024 z** (95% CI **-0.059 to +0.009**), or **-0.18 league-relative points per week** (CI **-0.60 to +0.22**). The secondary top-six outcome favors WR by **1.68 percentage points**, with an interval barely below zero (**-3.26 to -0.02 points** for RB minus WR), so the most defensible interpretation is a slight WR lean rather than a decisive position rule.

First-round unavailability is similar: **28.7% for RB and 27.7% for WR** at the 75% threshold. Among sufficiently available first-rounders, RB minus WR flips to **+0.026 z**, but its interval still crosses zero (**-0.012 to +0.064**). Availability therefore does not yield a stable first-round answer.

Final executed values are summarized in `artifacts/study_summary.json` and `artifacts/recommendations.csv`.

## Layout

```text
fantasy_rb_wr_draft_strategy_study/
  notebooks/       Executable source of truth
  data/processed/  Derived team, checkpoint, and early-pick panels
  artifacts/       Charts, manifests, inference, validation, recommendations
  tools/           Notebook generator and lightweight execution runner
```

The two sibling studies are read-only dependencies. Their caches and processed panels are not copied or modified.
