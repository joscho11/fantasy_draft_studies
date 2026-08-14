"""Compact retained full Sleeper responses needed by the QB/TE timing study."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "fantasy_draft_order_study"
VENDOR = ROOT / ".vendor"
sys.path.insert(0, str(VENDOR))

import ijson  # noqa: E402


def retained_current_ids() -> tuple[set[str], set[str]]:
    current_drafts: set[str] = set()
    with (SOURCE / "data/cache/first_round_pick_cache.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            if record.get("source") == "retained_sleeper_http_cache":
                current_drafts.add(str(record["draft_id"]))

    draft_to_league: dict[str, str] = {}
    with (SOURCE / "data/processed/analysis_panel.csv").open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            draft_id = str(row["draft_id"])
            if draft_id in current_drafts:
                draft_to_league[draft_id] = str(row["league_id"])
    if len(current_drafts) != 2_628 or len(draft_to_league) != 2_628:
        raise RuntimeError(
            f"Expected 2,628 retained current drafts; found {len(current_drafts)} drafts "
            f"and {len(draft_to_league)} league mappings"
        )
    return current_drafts, set(draft_to_league.values())


def main() -> None:
    current_drafts, current_leagues = retained_current_ids()
    cache_dir = ROOT / "data/cache"
    league_path = cache_dir / "current_league_payloads.jsonl"
    draft_path = cache_dir / "current_draft_payloads.jsonl"
    picks_path = cache_dir / "current_full_draft_picks.jsonl"

    counts = {"league": 0, "draft": 0, "picks": 0}
    source_cache = SOURCE / "data/cache/sleeper_http_cache.json"
    with (
        source_cache.open("rb") as source_handle,
        league_path.open("w", encoding="utf-8") as league_handle,
        draft_path.open("w", encoding="utf-8") as draft_handle,
        picks_path.open("w", encoding="utf-8") as picks_handle,
    ):
        for key, payload in ijson.kvitems(source_handle, ""):
            parts = key.split("/")
            if len(parts) == 2 and parts[0] == "league" and parts[1] in current_leagues:
                league_handle.write(json.dumps({"league_id": parts[1], "payload": payload}) + "\n")
                counts["league"] += 1
            elif len(parts) == 2 and parts[0] == "draft" and parts[1] in current_drafts:
                draft_handle.write(json.dumps({"draft_id": parts[1], "payload": payload}) + "\n")
                counts["draft"] += 1
            elif len(parts) == 3 and parts[0] == "draft" and parts[2] == "picks" and parts[1] in current_drafts:
                picks_handle.write(json.dumps({"draft_id": parts[1], "picks": payload or []}) + "\n")
                counts["picks"] += 1

    manifest = {
        "source_cache": str(source_cache),
        "source_cache_bytes": source_cache.stat().st_size,
        "required_drafts": len(current_drafts),
        "required_leagues": len(current_leagues),
        **{f"extracted_{key}_responses": value for key, value in counts.items()},
    }
    (ROOT / "artifacts/cache_extraction_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2))

    if counts["draft"] != 2_628 or counts["picks"] != 2_628:
        raise RuntimeError(f"Incomplete retained-cache extraction: {counts}")


if __name__ == "__main__":
    main()
