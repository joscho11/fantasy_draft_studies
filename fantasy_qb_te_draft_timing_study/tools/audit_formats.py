"""Audit format eligibility before locking the primary study population."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data/cache"


def truthy(value) -> bool:
    return value not in (None, False, 0, "0", "", "false", "False")


drafts = {}
with (CACHE / "current_draft_payloads.jsonl").open(encoding="utf-8") as handle:
    for line in handle:
        record = json.loads(line)
        drafts[str(record["draft_id"])] = record["payload"]

picks = {}
with (CACHE / "current_full_draft_picks.jsonl").open(encoding="utf-8") as handle:
    for line in handle:
        record = json.loads(line)
        picks[str(record["draft_id"])] = record["picks"]

rows = []
for draft_id, draft in drafts.items():
    settings = draft.get("settings") or {}
    metadata = draft.get("metadata") or {}
    board = picks.get(draft_id, [])
    teams = int(settings.get("teams") or 0)
    rounds = int(settings.get("rounds") or 0)
    pick_nos = [int(item.get("pick_no") or 0) for item in board]
    complete_board = (
        teams == 12
        and rounds > 0
        and len(board) == teams * rounds
        and len(set(pick_nos)) == len(pick_nos)
        and set(pick_nos) == set(range(1, teams * rounds + 1))
    )
    qb_slots = int(settings.get("slots_qb") or 0)
    sf_slots = int(settings.get("slots_super_flex") or 0)
    te_slots = int(settings.get("slots_te") or 0)
    keeper_picks = sum(truthy(item.get("is_keeper")) for item in board)
    primary = (
        complete_board
        and draft.get("status") == "complete"
        and draft.get("type") == "snake"
        and qb_slots == 1
        and sf_slots == 0
        and te_slots >= 1
        and rounds >= 12
        and keeper_picks == 0
    )
    rows.append(
        {
            "draft_id": draft_id,
            "season": int(draft.get("season")),
            "rounds": rounds,
            "qb_slots": qb_slots,
            "superflex_slots": sf_slots,
            "te_slots": te_slots,
            "keeper_picks": keeper_picks,
            "complete_board": complete_board,
            "scoring_type": str(metadata.get("scoring_type") or "unknown"),
            "primary": primary,
        }
    )

summary = {
    "drafts": len(rows),
    "complete_boards": sum(row["complete_board"] for row in rows),
    "primary_eligible_drafts": sum(row["primary"] for row in rows),
    "primary_team_seasons": 12 * sum(row["primary"] for row in rows),
    "by_season": dict(sorted(Counter(row["season"] for row in rows).items())),
    "eligible_by_season": dict(sorted(Counter(row["season"] for row in rows if row["primary"]).items())),
    "qb_superflex_combinations": {
        f"QB={key[0]},SF={key[1]}": value
        for key, value in sorted(Counter((row["qb_slots"], row["superflex_slots"]) for row in rows).items())
    },
    "draft_rounds": {str(key): value for key, value in sorted(Counter(row["rounds"] for row in rows).items())},
    "drafts_with_keeper_picks": sum(row["keeper_picks"] > 0 for row in rows),
    "eligible_by_scoring_type": dict(Counter(row["scoring_type"] for row in rows if row["primary"]).most_common()),
    "scoring_type": dict(Counter(row["scoring_type"] for row in rows).most_common()),
}
(ROOT / "artifacts/format_audit.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(json.dumps(summary, indent=2))
