"""Rewrite notebook interpretation blocks from the executed result artifacts."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd


def pct(value: float, digits: int = 1) -> str:
    return f"{100 * float(value):.{digits}f}%"


def z(value: float) -> str:
    return f"{float(value):+.3f}"


def refresh(root: Path) -> None:
    artifacts = root / "artifacts"
    processed = root / "data/processed"
    config = json.loads((artifacts / "study_config.json").read_text(encoding="utf-8"))
    manifest = json.loads((artifacts / "panel_manifest.json").read_text(encoding="utf-8"))
    leagues = pd.read_csv(processed / "league_seasons.csv")
    team = pd.read_csv(processed / "team_timing_panel.csv")
    position = pd.read_csv(processed / "position_timing_panel.csv")
    eda = pd.read_csv(artifacts / "eda_timing_summary.csv")
    seasons = pd.read_csv(artifacts / "eda_timing_by_season.csv")
    associations = pd.read_csv(artifacts / "eda_timing_window_associations.csv")
    inference = pd.read_csv(artifacts / "inference_timing_intervals.csv")
    validation = pd.read_csv(artifacts / "validation_forward_seasons.csv")
    availability = pd.read_csv(artifacts / "availability_timing_summary.csv")
    availability_panel = pd.read_csv(processed / "position_availability_panel.csv")
    joint = pd.read_csv(artifacts / "joint_qb_te_timing.csv")
    recommendations = pd.read_csv(artifacts / "recommendations.csv")

    def erow(pos: str, window: str):
        return eda.loc[eda.position.eq(pos) & eda.timing_window.eq(window)].iloc[0]

    def irow(pos: str, window: str):
        return inference.loc[inference.position.eq(pos) & inference.timing_window.eq(window)].iloc[0]

    def arow(pos: str, window: str):
        return availability.loc[availability.position.eq(pos) & availability.timing_window.eq(window)].iloc[0]

    def association_row(pos: str):
        return associations.loc[associations.position.eq(pos)].iloc[0]

    source_by_year = leagues.groupby("season").size()
    primary_by_year = leagues.loc[leagues.primary_sample.astype(bool)].groupby("season").size()
    source_total = int(manifest["source_league_seasons"])
    primary_total = int(manifest["primary_league_seasons"])
    qb_early, qb_late = erow("QB", "1-3"), erow("QB", "12+")
    te_bad, te_best = erow("TE", "4-5"), erow("TE", "10-11")
    qb_i_early, qb_i_late = irow("QB", "1-3"), irow("QB", "12+")
    te_i_bad, te_i_best = irow("TE", "4-5"), irow("TE", "10-11")
    qb_association, te_association = association_row("QB"), association_row("TE")

    qb_season = seasons.loc[seasons.position.eq("QB") & seasons.timing_window.eq("12+") & seasons.season.ge(2019)]
    te_season = seasons.loc[seasons.position.eq("TE") & seasons.timing_window.eq("10-11") & seasons.season.ge(2019)]
    exact = position.groupby(["position", "first_round"], as_index=False).agg(
        n=("points_zscore", "size"), mean_points_zscore=("points_zscore", "mean")
    )
    exact = exact.loc[exact.n.ge(100)]
    qb_exact_best = exact.loc[exact.position.eq("QB")].sort_values("mean_points_zscore", ascending=False).iloc[0]
    te_exact_best = exact.loc[exact.position.eq("TE")].sort_values("mean_points_zscore", ascending=False).iloc[0]

    qb_tests = validation.loc[validation.position.eq("QB")]
    te_tests = validation.loc[validation.position.eq("TE")]
    qb_2025 = qb_tests.loc[qb_tests.test_season.eq(2025)].iloc[0]
    te_2024 = te_tests.loc[te_tests.test_season.eq(2024)].iloc[0]
    te_2025 = te_tests.loc[te_tests.test_season.eq(2025)].iloc[0]

    linked = availability_panel.groupby("position").availability_rate.count()
    total_position = availability_panel.groupby("position").size()
    available_n = availability_panel.groupby("position").available_75.sum()
    supported = joint.loc[joint.supported.astype(bool)]
    top_joint = supported.sort_values("mean_points_zscore", ascending=False).iloc[0]
    qb_rec = recommendations.loc[recommendations.position.eq("QB")].iloc[0]
    te_rec = recommendations.loc[recommendations.position.eq("TE")].iloc[0]

    interpretations = {
        "imports and chart helper": "The local Plotly bundle loaded successfully and all charts rendered with the study's dark theme. This cell changes presentation only; it does not affect any estimate.",
        "locked study configuration": f"The executed contract covers {config['source_seasons'][0]}-{config['source_seasons'][-1]}, uses six timing windows, and sets {config['bootstrap_replicates']:,} bootstrap replicates. The primary population remains 12-team, redraft, 1QB, non-superflex, non-TE-premium leagues.",
        "configuration chart": "The chart defines starts at rounds 1, 4, 6, 8, 10, and 12. The last category is deliberately open-ended (12+), so later results identify a broad late-draft strategy rather than claiming that round 12 itself is uniquely optimal.",
        "load source outcomes": f"The source contains {source_total:,} league-seasons and {source_total * 12:,} team-seasons from 2018-2025. Those rows are balanced at 12 teams per league before applying QB/TE format restrictions.",
        "load draft caches": f"Draft metadata and pick payloads were found for all {source_total:,} source drafts; {manifest['complete_boards']:,} boards were structurally complete. The remaining {source_total - int(manifest['complete_boards']):,} drafts cannot enter the primary analysis regardless of their outcomes.",
        "normalize leagues and picks": f"After intersecting board completeness with the redraft 1QB format gates, {primary_total:,} leagues remain. Exclusion reasons overlap, so their counts should not be summed as mutually exclusive losses.",
        "build team timing panel": f"The team panel contains {manifest['primary_team_seasons']:,} rows. Only {manifest['teams_without_drafted_qb']} teams lack a drafted QB and {manifest['teams_without_drafted_te']} lack a drafted TE; they are retained as 'Undrafted' but excluded from timing-window charts.",
        "build position timing panel": f"The long panel contains {len(position):,} rows: two position records for each of {len(team):,} teams. After removing undrafted-position rows, the EDA and inference models use {int(position.timing_window.isin(config['timing_windows']).sum()):,} observations.",
        "validate and save manifest": f"All {primary_total:,} retained leagues have exactly 12 team rows. Fractional credits sum to {team.top_6_points.sum():,.0f} top-six finishes and {team.top_regular_season_scorer.sum():,.0f} top scorers, exactly six and one per league.",
        "coverage chart": f"The primary sample retains {primary_total:,} of {source_total:,} source leagues ({pct(primary_total/source_total)}). Coverage is thin through 2021 (5, 42, 75, and 109 leagues), then rises to 222, 259, 367, and 343 in 2022-2025; pooled conclusions are therefore driven mainly by recent seasons.",
        "prepare eda summaries": f"The descriptive summaries cover {int(eda.n.sum()):,} position-team observations: {int(eda.loc[eda.position.eq('QB'),'n'].sum()):,} QB and {int(eda.loc[eda.position.eq('TE'),'n'].sum()):,} TE. These values are unadjusted and should be read alongside the later uncertainty and forward tests.",
        "eda points chart": f"QB round 12+ leads at {z(qb_late.mean_points_zscore)}, versus {z(qb_early.mean_points_zscore)} for rounds 1-3, a {z(qb_late.mean_points_zscore-qb_early.mean_points_zscore)} gap. TE rounds 10-11 lead at {z(te_best.mean_points_zscore)}, while rounds 4-5 are lowest at {z(te_bad.mean_points_zscore)}; these are descriptive associations, not causal gains from waiting.",
        "eda top six chart": f"Teams taking their first QB in round 12+ finish top six {pct(qb_late.top_6_rate)} of the time, compared with {pct(qb_early.top_6_rate)} for rounds 1-3 ({pct(qb_late.top_6_rate-qb_early.top_6_rate)} higher). TE rounds 10-11 reach {pct(te_best.top_6_rate)}, versus {pct(te_bad.top_6_rate)} for rounds 4-5.",
        "eda support chart": f"The QB 12+ estimate rests on {int(qb_late.n):,} teams, far fewer than the {int(eda.loc[eda.position.eq('QB'),'n'].max()):,} in the largest QB window. TE rounds 10-11 have {int(te_best.n):,} teams versus {int(eda.loc[eda.position.eq('TE'),'n'].max()):,} in the largest TE window, so the late-tail estimates carry visibly less support.",
        "eda qb season chart": f"QB round 12+ is positive in {int(qb_season.mean_points_zscore.gt(0).sum())} of 7 seasons from 2019-2025, ranging from {z(qb_season.mean_points_zscore.min())} in {int(qb_season.loc[qb_season.mean_points_zscore.idxmin(),'season'])} to {z(qb_season.mean_points_zscore.max())} in {int(qb_season.loc[qb_season.mean_points_zscore.idxmax(),'season'])}. The sharp reversals rule out a stable universal late-QB advantage.",
        "eda te season chart": f"TE rounds 10-11 are positive in {int(te_season.mean_points_zscore.gt(0).sum())} of 7 seasons from 2019-2025. The exception is 2022 at {z(te_season.loc[te_season.season.eq(2022),'mean_points_zscore'].iloc[0])}; the other six seasons range from {z(te_season.loc[te_season.mean_points_zscore.gt(0),'mean_points_zscore'].min())} to {z(te_season.mean_points_zscore.max())}, making this pattern more repeatable than the QB leader.",
        "eda exact round chart": f"Among exact rounds with at least 100 teams, QB round {int(qb_exact_best.first_round)} peaks at {z(qb_exact_best.mean_points_zscore)} (n={int(qb_exact_best.n):,}) and TE round {int(te_exact_best.first_round)} peaks at {z(te_exact_best.mean_points_zscore)} (n={int(te_exact_best.n):,}). Neighboring rounds move materially, confirming that an exact-round optimum would overstate precision.",
        "define inference model": f"The model uses {int(position.timing_window.isin(config['timing_windows']).sum()):,} position-team observations with categorical timing effects plus draft-slot and season controls. It estimates adjusted associations; it does not control for manager skill or make draft timing random.",
        "run clustered bootstrap": f"All 12 timing estimates were produced with {config['bootstrap_replicates']:,} whole-league bootstrap resamples. Three QB windows (6-7, 10-11, and 12+) and TE rounds 10-11 have intervals entirely above zero; QB rounds 1-3 and TE rounds 4-5 are entirely below zero.",
        "adjusted comparison chart": f"After season and slot adjustment, QB round 12+ remains highest at {z(qb_i_late.adjusted_points_zscore)} (95% interval {z(qb_i_late.ci_low)} to {z(qb_i_late.ci_high)}), while TE rounds 10-11 lead at {z(te_i_best.adjusted_points_zscore)} ({z(te_i_best.ci_low)} to {z(te_i_best.ci_high)}). Adjustment does not remove either pooled pattern.",
        "qb interval chart": f"QB round 12+ is {z(qb_i_late.adjusted_points_zscore-qb_i_early.adjusted_points_zscore)} above rounds 1-3 in point estimates, and both marginal intervals sit on opposite sides of zero. The late window has only {int(qb_i_late.n):,} teams, so the chart supports a late-QB hypothesis, not a precise round-12 rule.",
        "te interval chart": f"TE rounds 10-11 are {z(te_i_best.adjusted_points_zscore-te_i_bad.adjusted_points_zscore)} above rounds 4-5 in point estimates. Their interval is fully positive ({z(te_i_best.ci_low)} to {z(te_i_best.ci_high)}), whereas the 4-5 interval is fully negative ({z(te_i_bad.ci_low)} to {z(te_i_bad.ci_high)}).",
        "calculate forward tests": f"There are {len(qb_tests)} QB and {len(te_tests)} TE forward-season tests. The training-selected strategy beats the other windows in {int(qb_tests.test_z_difference.gt(0).sum())}/{len(qb_tests)} QB tests and {int(te_tests.test_z_difference.gt(0).sum())}/{len(te_tests)} TE tests, so pooled rankings do not transfer uniformly.",
        "forward scoring chart": f"QB's largest forward success is the 2025 round-12+ test at {z(qb_2025.test_z_difference)}, but selected QB strategies are negative in 2020, 2023, and 2024. TE rounds 10-11 fail in 2022 ({z(te_tests.loc[te_tests.test_season.eq(2022),'test_z_difference'].iloc[0])}) and then succeed in 2024 ({z(te_2024.test_z_difference)}) and 2025 ({z(te_2025.test_z_difference)}).",
        "forward top six chart": f"The selected QB window changes top-six probability by {pct(qb_2025.test_top6_difference)} in 2025 but by {pct(qb_tests.loc[qb_tests.test_season.eq(2024),'test_top6_difference'].iloc[0])} in 2024. TE rounds 10-11 add {pct(te_2024.test_top6_difference)} in 2024 and {pct(te_2025.test_top6_difference)} in 2025 after a {pct(te_tests.loc[te_tests.test_season.eq(2022),'test_top6_difference'].iloc[0])} result in 2022.",
        "selection stability chart": "QB training selects 8-9 once, 6-7 four times, and 12+ once; only three of those six choices test positively. TE training selects 1-3 three times and 10-11 three times; 10-11 succeeds in two of its three tests, which is why its evidence grade exceeds the QB 12+ grade.",
        "link player availability": f"Weekly participation links {int(linked['QB']):,}/{int(total_position['QB']):,} QB rows and {int(linked['TE']):,}/{int(total_position['TE']):,} TE rows. Availability is now capped to each league's fantasy regular-season weeks, eliminating the prior impossible rates above 100%.",
        "summarize availability sample": f"The 75% threshold retains {int(available_n['QB']):,} QB rows and {int(available_n['TE']):,} TE rows. Because availability occurs after the draft, this restricted sample describes durability-conditioned outcomes rather than the expected result of the original timing decision.",
        "availability chart": f"Among sufficiently available players, QB round 12+ still leads at {z(arow('QB','12+').mean_points_zscore)} with a {pct(arow('QB','12+').top_6_rate)} top-six rate. TE rounds 1-3 now lead at {z(arow('TE','1-3').mean_points_zscore)} and {pct(arow('TE','1-3').top_6_rate)}, narrowly ahead of rounds 10-11 at {z(arow('TE','10-11').mean_points_zscore)} and {pct(arow('TE','10-11').top_6_rate)}. The corrected availability screen therefore preserves the late-QB result but weakens the TE timing headline.",
        "build joint timing surface": f"The data contain {len(joint)} observed QB-by-TE cells; {len(supported)} clear the 100-team support gate and cover {int(supported.n.sum()):,}/{int(joint.n.sum()):,} team-seasons. Sparse cells are excluded from the recommendation heatmap rather than visually overstated.",
        "assemble recommendations": f"The evidence rubric labels QB {qb_rec.supported_round_window} exploratory because it was selected in only {int(qb_rec.forward_tests_selecting_window)} forward test. TE {te_rec.supported_round_window} is moderate because it was selected three times and tested positively twice.",
        "joint heatmap": f"The highest supported cell is QB {top_joint.qb_timing_window} with TE {top_joint.te_timing_window}: {z(top_joint.mean_points_zscore)}, {pct(top_joint.top_6_rate)}, n={int(top_joint.n):,}. Its support is modest and the surface is non-monotonic, so this combination is a hypothesis rather than the final recommendation.",
        "recommendation chart": f"The final chart reports QB {qb_rec.supported_round_window} at {z(qb_rec.adjusted_points_zscore)} ({z(qb_rec.ci_low)} to {z(qb_rec.ci_high)}) as exploratory, and TE {te_rec.supported_round_window} at {z(te_rec.adjusted_points_zscore)} ({z(te_rec.ci_low)} to {z(te_rec.ci_high)}) as moderate. The uncertainty bars support broad timing windows, not exact player or exact-round prescriptions.",
    }

    # Each interpretation closes the loop from executed result to draft decision.
    interpretations.update({
        "imports and chart helper": "The renderer produced readable dark-mode charts from the local Plotly bundle. You can inspect the evidence without an internet connection, and this setup step contributes no evidence about when to draft either position.",
        "locked study configuration": f"The study asks one narrow question across {config['source_seasons'][0]}-{config['source_seasons'][-1]} redraft leagues: when should you take your first QB and TE in a 12-team 1QB draft? Six round windows trade exact-round detail for enough observations to compare strategies, while {config['bootstrap_replicates']:,} bootstrap samples measure how much those comparisons move across leagues.",
        "configuration chart": "The decision points start at rounds 1, 4, 6, 8, 10, and 12. Treat 12+ as a late-QB or late-TE strategy, not a command to draft in round 12; the study lacks enough support to separate every round after 12.",
        "load source outcomes": f"The source contributes {source_total:,} leagues and {source_total * 12:,} teams, enough to test broad draft windows. Format filters still decide whether those leagues answer your question, since superflex and dynasty drafts assign different values to QB and TE.",
        "load draft caches": f"The pipeline recovered complete pick sequences for {manifest['complete_boards']:,} of {source_total:,} drafts. The missing {source_total - int(manifest['complete_boards']):,} boards reduce sample size but cannot bias a timing estimate through partial pick histories because the study excludes them before analysis.",
        "normalize leagues and picks": f"The final format gates leave {primary_total:,} comparable 1QB redraft leagues. Your recommendation therefore applies to that format; you should not carry it into superflex, TE-premium, keeper, dynasty, or IDP drafts.",
        "build team timing panel": f"The panel assigns an outcome to {manifest['primary_team_seasons']:,} draft strategies. Only {manifest['teams_without_drafted_qb']} teams omit QB and {manifest['teams_without_drafted_te']} omit TE, so missing position picks cannot explain the ranking of the six normal timing windows.",
        "build position timing panel": f"The model compares {int(position.timing_window.isin(config['timing_windows']).sum()):,} QB and TE decisions on one common scale. You can compare the timing patterns across positions without mixing them into one exposure or giving leagues with extra rows more weight.",
        "validate and save manifest": f"All {primary_total:,} leagues pass the 12-team and outcome-accounting checks. A top-six result now means the same thing in each league, so any timing gap reflects observed team outcomes rather than broken rank arithmetic or unequal slot counts.",
        "coverage chart": f"The clean sample keeps {primary_total:,} of {source_total:,} leagues ({pct(primary_total/source_total)}), and 2022-2025 supply {int(primary_by_year.loc[2022:2025].sum()):,} of them. Use the recommendation as a guide to recent 1QB drafting; the study has too little 2018-2021 coverage to claim a timeless positional rule.",
        "prepare eda summaries": f"The descriptive pass covers {int(eda.n.sum()):,} position decisions. It identifies candidate strategies for testing, but it cannot tell whether timing caused the outcome because strong managers may choose different rounds than weak managers.",
        "eda points chart": f"Teams waiting until round 12+ for QB score {z(qb_late.mean_points_zscore-qb_early.mean_points_zscore)} league standard deviations above teams taking one in rounds 1-3 on average; the absolute edge is small, but its direction favors spending early picks on other positions in 1QB drafts. TE rounds 10-11 lead rounds 4-5 by {z(te_best.mean_points_zscore-te_bad.mean_points_zscore)}, which argues against paying the middle-round TE price when you miss the elite early tier.",
        "eda practical points chart": f"The standardized QB result is modest in lineup terms. QB 12+ teams average {qb_late.mean_points_per_week_above_league:+.2f} points per week versus their league average, while QB 1-3 teams average {qb_early.mean_points_per_week_above_league:+.2f}; that is a {qb_late.mean_points_per_week_above_league-qb_early.mean_points_per_week_above_league:.2f}-point weekly gap, about {(qb_late.mean_points_per_week_above_league-qb_early.mean_points_per_week_above_league)*14:.0f} points over 14 weeks. Their raw season averages are {qb_late.mean_regular_season_points:,.1f} and {qb_early.mean_regular_season_points:,.1f}, but league-relative points are the better comparison because scoring settings differ. TE 10-11 versus 4-5 has a {te_best.mean_points_per_week_above_league-te_bad.mean_points_per_week_above_league:.2f}-point weekly gap, about {(te_best.mean_points_per_week_above_league-te_bad.mean_points_per_week_above_league)*14:.0f} points over 14 weeks. These are useful margins, not enough to override a major player-value fall in the draft.",
        "eda top six chart": f"Waiting until round 12+ for QB corresponds to a {pct(qb_late.top_6_rate-qb_early.top_6_rate)} increase in top-six finishes versus rounds 1-3, from {pct(qb_early.top_6_rate)} to {pct(qb_late.top_6_rate)}. That gap has more practical meaning than the z-score: about six additional top-half finishes per 100 teams. TE rounds 10-11 add {pct(te_best.top_6_rate-te_bad.top_6_rate)} versus rounds 4-5, about five per 100 teams.",
        "eda support chart": f"Late strategies have less evidence behind them: {int(qb_late.n):,} teams support QB 12+ and {int(te_best.n):,} support TE 10-11. You can use those windows as draft preferences, but the smaller tails make an exact-round recommendation fragile and raise the chance that a few seasons or manager types drive the lead.",
        "eda qb season chart": f"QB 12+ wins in only {int(qb_season.mean_points_zscore.gt(0).sum())} of 7 seasons and swings from {z(qb_season.mean_points_zscore.min())} to {z(qb_season.mean_points_zscore.max())}. A rigid 'wait until round 12' rule would have hurt in seasons such as 2021; use late QB as a default that yields when an elite value falls.",
        "eda te season chart": f"TE rounds 10-11 post positive scoring in 6 of 7 seasons from 2019-2025, with 2022 as the lone negative year at {z(te_season.loc[te_season.season.eq(2022),'mean_points_zscore'].iloc[0])}. That repeat pattern supports waiting on TE after the early elite options disappear, though the later availability test checks whether player durability explains part of it.",
        "eda exact round chart": f"Round {int(qb_exact_best.first_round)} has the highest supported QB average and round {int(te_exact_best.first_round)} has the highest TE average, but neighboring rounds change direction. You should draft from a value window rather than target those exact rounds; a single ADP move could otherwise turn a fitted optimum into a different result.",
        "qb categorical association chart": f"For categorical QB timing windows, the correlation-ratio analogue of r is η={qb_association.raw_points_eta:.3f}, and the six-window model has R-squared={qb_association.raw_points_r2:.4f} on raw total points. On the more comparable within-league scoring scale, η={qb_association.normalized_points_eta:.3f} and R-squared={qb_association.normalized_points_r2:.4f}. The windows explain only {100*qb_association.normalized_points_r2:.2f}% of team-scoring variation, so QB timing is a small roster-construction edge rather than a primary driver of results. The window means still favor waiting, but player selection, waivers, lineup decisions, injuries, and the rest of the roster dominate the outcome.",
        "te categorical association chart": f"For categorical TE timing windows, η={te_association.raw_points_eta:.3f} and R-squared={te_association.raw_points_r2:.4f} on raw total points; the within-league values are η={te_association.normalized_points_eta:.3f} and R-squared={te_association.normalized_points_r2:.4f}. The six windows explain only {100*te_association.normalized_points_r2:.2f}% of scoring variation. That keeps the TE result in proportion: avoiding rounds 4-5 and using an elite-early-or-late approach may improve expected value at the margin, but TE timing alone will not determine whether a team scores well.",
        "define inference model": f"The adjusted model asks whether timing retains an association after accounting for season and draft slot across {int(position.timing_window.isin(config['timing_windows']).sum()):,} decisions. It still omits manager skill and player value at the pick, so it can rank historical strategies but cannot prove that copying one causes the same outcome.",
        "run clustered bootstrap": f"QB windows 6-7, 10-11, and 12+ retain positive intervals, while rounds 1-3 remain negative; several ways of waiting outperform early QB in the pooled sample. TE has one positive window, rounds 10-11, and one negative window, rounds 4-5, which narrows the useful TE takeaway to 'wait past the middle tier' rather than 'later is always better.'",
        "adjusted comparison chart": f"Season and draft-slot controls leave QB 12+ at {z(qb_i_late.adjusted_points_zscore)} and TE 10-11 at {z(te_i_best.adjusted_points_zscore)}. Draft position and season mix do not explain the pooled leaders, so both remain viable timing preferences; the later forward tests determine how much confidence to place in them.",
        "qb interval chart": f"QB 12+ leads rounds 1-3 by {z(qb_i_late.adjusted_points_zscore-qb_i_early.adjusted_points_zscore)}, and their intervals do not overlap zero in the same direction. In a 1QB draft, the evidence favors using premium rounds on RB, WR, or an elite TE and building QB later. The {int(qb_i_late.n):,}-team sample and season reversals make this a flexible default, not a mandate.",
        "te interval chart": f"TE rounds 10-11 lead rounds 4-5 by {z(te_i_best.adjusted_points_zscore-te_i_bad.adjusted_points_zscore)}, with the leader's interval above zero and the 4-5 interval below zero. If you pass on the early elite TEs, the historical results favor waiting until rounds 10-11 instead of forcing a TE pick in rounds 4-5.",
        "calculate forward tests": f"Training-period winners beat the other windows in only 3 of {len(qb_tests)} QB tests and 3 of {len(te_tests)} TE tests. Historical leaders fail half their next-season tests, so you should combine the draft-timing preference with current ADP, projections, and value rather than follow it as a standalone rule.",
        "forward scoring chart": f"Late QB produces a strong {z(qb_2025.test_z_difference)} test result in 2025, but selected QB strategies lose in 2020, 2023, and 2024. TE 10-11 fails in 2022 and wins in 2024-2025. The out-of-sample record supports a mild late-round preference for both positions and rejects certainty about any fixed window.",
        "forward top six chart": f"The practical payoff changes sign by year: the selected QB window adds {pct(qb_2025.test_top6_difference)} to top-six probability in 2025 and loses {pct(abs(qb_tests.loc[qb_tests.test_season.eq(2024),'test_top6_difference'].iloc[0]))} in 2024. TE 10-11 adds {pct(te_2024.test_top6_difference)} and {pct(te_2025.test_top6_difference)} in the two latest tests after no useful gain in 2022. Treat timing as an edge measured in a few wins per 100 teams, not a dominant draft lever.",
        "selection stability chart": "The preferred QB window changes from 8-9 to 6-7 to 12+ as new seasons enter training. TE also switches between 1-3 and 10-11. You should frame both recommendations as tier-based choices: pay for an elite option when the price is right, otherwise wait, because the data do not select one stable round every year.",
        "link player availability": f"The participation link covers {int(linked['QB']):,}/{int(total_position['QB']):,} QB rows and {int(linked['TE']):,}/{int(total_position['TE']):,} TE rows after capping weeks to each fantasy season. The sensitivity test can now ask whether late strategies lead because their selected players stayed healthy, without impossible availability values distorting the answer.",
        "summarize availability sample": f"The durability screen retains {int(available_n['QB']):,} QB and {int(available_n['TE']):,} TE decisions. It answers a narrower question: among picks that remained available for at least 75% of fantasy weeks, which timing worked best? You cannot use it as the expected draft-day result because you do not know future availability.",
        "availability chart": f"Late QB strengthens among available players: round 12+ reaches {z(arow('QB','12+').mean_points_zscore)} and a {pct(arow('QB','12+').top_6_rate)} top-six rate, so injuries do not explain its pooled lead. TE changes: rounds 1-3 edge rounds 10-11, {z(arow('TE','1-3').mean_points_zscore)} versus {z(arow('TE','10-11').mean_points_zscore)}. Healthy elite TEs can justify the early cost, so the TE recommendation becomes conditional: draft an elite TE early or wait until 10-11; avoid the 4-5 middle tier.",
        "build joint timing surface": f"Thirty-five QB-TE combinations clear the 100-team support gate and cover {int(supported.n.sum()):,} teams. The study can compare common roster-building paths, while the gate prevents rare combinations from becoming recommendations because of a few strong teams.",
        "assemble recommendations": f"QB 12+ receives an exploratory grade because prior seasons select it for only one forward test. TE 10-11 receives a moderate grade after three selections and two wins. For your draft, wait on QB as a flexible preference; use TE 10-11 as the fallback after the elite early tier, with more confidence than the exact QB endpoint.",
        "joint heatmap": f"QB 12+ plus TE 1-3 has the best supported joint average at {z(top_joint.mean_points_zscore)} and a {pct(top_joint.top_6_rate)} top-six rate, but only {int(top_joint.n):,} teams used it. The combination fits a coherent build, elite TE early and QB late, yet the modest sample and non-monotonic surface keep it below recommendation-grade evidence.",
        "recommendation chart": f"The current decision rule is tiered. In 1QB redraft, prefer waiting on QB, with 12+ as the pooled leader but an exploratory grade. At TE, take an elite early option when value permits; otherwise target rounds 10-11 and avoid forcing the position in rounds 4-5. Neither result specifies which player to select, and both remain historical associations rather than causal guarantees.",
    })

    for notebook_path in sorted((root / "notebooks").glob("*.ipynb")):
        notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
        for index, cell in enumerate(notebook["cells"]):
            if cell.get("cell_type") != "code" or index + 1 >= len(notebook["cells"]):
                continue
            source = "".join(cell.get("source", []))
            match = re.match(r"# CELL \[([^\]]+)\]", source)
            if not match or match.group(1) not in interpretations:
                continue
            notebook["cells"][index + 1]["source"] = (
                "### Interpretation\n\n" + interpretations[match.group(1)] + "\n"
            ).splitlines(True)
        notebook_path.write_text(json.dumps(notebook, indent=1), encoding="utf-8")


if __name__ == "__main__":
    refresh(Path(__file__).resolve().parents[1])
