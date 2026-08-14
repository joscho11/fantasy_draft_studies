"""Resumably fetch full pick boards for retained 2018-2021 Sleeper drafts."""

from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "fantasy_draft_order_study"
OUTPUT = ROOT / "data/cache/historic_full_draft_picks.jsonl"


def required_historic_drafts() -> set[str]:
    result = set()
    with (SOURCE / "data/cache/two_round_pick_cache.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            if record.get("source") == "sleeper_api_two_round_backfill":
                result.add(str(record["draft_id"]))
    if len(result) != 1_013:
        raise RuntimeError(f"Expected 1,013 historic drafts; found {len(result)}")
    return result


def fetch(draft_id: str) -> dict:
    url = f"https://api.sleeper.app/v1/draft/{draft_id}/picks"
    request = Request(url, headers={"User-Agent": "fantasy-qb-te-draft-timing-study/0.1"})
    for attempt in range(6):
        try:
            with urlopen(request, timeout=45) as response:
                payload = json.loads(response.read().decode("utf-8"))
            return {"draft_id": draft_id, "source": "sleeper_api_historic_full_board", "picks": payload or []}
        except HTTPError as error:
            if error.code not in {429, 500, 502, 503, 504} or attempt == 5:
                raise
        except (TimeoutError, URLError):
            if attempt == 5:
                raise
        time.sleep(2**attempt)
    raise RuntimeError(f"Unreachable retry state for {draft_id}")


def main() -> None:
    required = required_historic_drafts()
    cached = {}
    if OUTPUT.exists():
        with OUTPUT.open(encoding="utf-8") as handle:
            for line in handle:
                record = json.loads(line)
                cached[str(record["draft_id"])] = record
    missing = sorted(required - set(cached))

    fetched = []
    if missing:
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {executor.submit(fetch, draft_id): draft_id for draft_id in missing}
            for future in as_completed(futures):
                fetched.append(future.result())
        fetched.sort(key=lambda item: item["draft_id"])
        with OUTPUT.open("a", encoding="utf-8") as handle:
            for record in fetched:
                handle.write(json.dumps(record) + "\n")
                cached[record["draft_id"]] = record

    manifest = {
        "historic_drafts_required": len(required),
        "historic_drafts_cached": len(cached),
        "fetched_this_run": len(fetched),
        "nonempty_boards": sum(bool(record.get("picks")) for record in cached.values()),
        "empty_boards": sum(not record.get("picks") for record in cached.values()),
    }
    (ROOT / "artifacts/historic_full_board_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2))
    if set(cached) != required:
        raise RuntimeError("Historic full-board cache is incomplete")


if __name__ == "__main__":
    main()
