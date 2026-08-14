# Fantasy Draft Studies

This folder groups three related retrospective studies of completed Sleeper fantasy-football drafts. The grouping is organizational: each study keeps its own notebooks, data, artifacts, tooling, and methodology.

| Study | Question |
| --- | --- |
| [`fantasy_draft_order_study/`](fantasy_draft_order_study/) | How draft slot relates to regular-season performance, player availability, and first-two-pick snake pairs. |
| [`fantasy_qb_te_draft_timing_study/`](fantasy_qb_te_draft_timing_study/) | When teams draft their first quarterback and tight end, and how broad timing windows relate to performance. |
| [`fantasy_rb_wr_draft_strategy_study/`](fantasy_rb_wr_draft_strategy_study/) | How early RB/WR allocation and first-round position choice relate to performance. |

## Dependency order

The studies form a one-way data dependency chain:

`draft order -> QB/TE timing -> RB/WR strategy`

- The QB/TE study reads validated outcomes and draft data from the draft-order study.
- The RB/WR study reads the draft-order study and the QB/TE study.
- The draft-order study does not depend on the other two.

Keep the three study directories as immediate siblings with their current names unless the `ROOT.parent` source paths in the downstream tools and notebooks are updated at the same time.

## Running the studies

Run a study from its own project root, not from this parent folder. Follow that study's README for its exact notebook and tooling order:

- [Draft-order run order](fantasy_draft_order_study/README.md#run-order)
- [QB/TE run order](fantasy_qb_te_draft_timing_study/README.md#run-order)
- [RB/WR run order](fantasy_rb_wr_draft_strategy_study/README.md#run-order)

The notebooks are the executable analysis source of truth. Results are descriptive associations and sensitivity analyses, not causal estimates of universally optimal draft strategy.

## Version control

This parent directory is the Git repository. The study folders are ordinary subdirectories, not nested repositories.

Large API and draft-board caches, local dependency environments, Python bytecode, and Jupyter scratch files remain on disk but are intentionally excluded from Git. Each study's own `.gitignore` may exclude additional generated outputs.
