# Fantasy RB/WR draft strategy study: handoff

Run `tools/build_notebooks.py`, then `tools/run_notebooks.py`. The sibling draft-order and QB/TE projects are read-only inputs.

The primary estimand is the adjusted association between the number of RBs selected through Round 6 and regular-season team performance. Leagues with unequal early pick ownership are excluded, and the model controls for the number of non-RB/WR selections, so RB-count differences represent RB-for-WR substitutions at a fixed six-pick budget and fixed amount of QB/TE/other draft capital. Zero RB, WR-heavy, balanced, and RB-heavy are prespecified mechanical labels.

The first-round RB-versus-WR comparison is prespecified but secondary. It adjusts for exact draft slot and is repeated among first-rounders active in at least 75% of league fantasy weeks. Availability conditioning is post-treatment and must remain a mechanism/sensitivity result.

Every code cell has a preceding purpose cell and a following interpretation cell. The execution runner replaces those interpretations with the executed result. Every result interpretation must answer the decision question, state practical magnitude, say whether it changes the recommendation, and name the observational or support limitation blocking a stronger claim.

Charts are the primary communication format. Keep at least one chart in every notebook and preserve the league-cluster bootstrap, forward-season validation, format/slot robustness, and availability sensitivity if the project is extended.

Current executed result: 1,371 league-seasons and 16,452 teams. The pooled supported Round 6 tier is balanced (two RBs) or RB-heavy (3+); RB-heavy ranks first, but its +0.026-z gap over balanced has a -0.013 to +0.064 interval. Both 0-RB and 1-RB builds trail both members of the supported tier in pairwise pooled scoring contrasts. Forward selection is mixed, so present this as “two or three RBs by Round 6,” not “Robust RB wins.”

The first-round RB-minus-WR estimate is -0.024 z (95% CI -0.059 to +0.009), so the primary side-question answer is no clear edge. Top-six rate gives WR a slight 1.68-point advantage. First-round unavailability differs by only 1.0 percentage point, and the available-only scoring comparison also remains inconclusive.
