# Handoff

Run the notebooks in numeric order. The original draft-order project is treated as read-only. Compact full-board caches live under `data/cache/`; do not replace them unless intentionally expanding the sample.

Primary outcomes match the source study: within-league points z-score, points rank, fractional top-six credit, and fractional top-scorer credit. The model adjusts timing-window comparisons for draft slot and season and uses a league-cluster bootstrap.

The retained primary panel contains 1,422 league-seasons and 17,064 team-seasons. Keep the format gates even though this is slightly below the planning target; expanding with structurally different league formats would bias the question rather than improve it. The main QB result remains exploratory, while the TE rounds 10-11 result has moderate evidence.

Standing presentation preference: lead with charts rather than tables. Preserve at least one chart in every notebook, at least five in EDA, and at least three result charts in inference and evaluation.

Notebook structure is also part of the contract: keep transformations, model fitting, and charts in distinct sections; emit no more than one chart from a code cell; and place explanatory markdown immediately before and interpretive markdown immediately after every code cell.

Interpretation markdown must report the executed result: actual leaders, gaps, sample sizes, intervals, season reversals, and the implication for the recommendation. Every interpretation must answer the project's decision question: what the result means for when to draft QB or TE, whether its practical size or uncertainty changes the recommendation, and what limitation prevents a stronger claim. Do not merely restate numbers or describe what a chart is intended to show. `tools/refresh_interpretations.py` rebuilds these blocks from the latest artifacts after every pipeline run.

When standardized effects are hard to interpret, translate them to league-relative points per week and retain raw season averages as context. For the categorical QB and TE timing windows, report correlation ratio eta and eta-squared/R-squared separately. Do not encode the windows as numbers and call the resulting Pearson statistic categorical correlation.
