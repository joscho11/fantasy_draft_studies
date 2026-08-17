"""cowork_OS workspace data roots for fantasy draft studies."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_ws():
    for parent in Path(__file__).resolve().parents:
        cand = parent / "workspace" / "paths.py"
        if cand.exists():
            spec = importlib.util.spec_from_file_location("cowork_workspace_paths", cand)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
    raise FileNotFoundError("workspace/paths.py not found")


WS = _load_ws()
DRAFT_ORDER_ART = WS.NFL_ARTIFACTS / "draft_order"
DRAFT_ORDER_DATA = WS.NFL_RAW / "draft_order"
DRAFT_QB_TE_ART = WS.NFL_ARTIFACTS / "draft_qb_te"
DRAFT_QB_TE_DATA = WS.NFL_RAW / "draft_qb_te"
DRAFT_RB_WR_ART = WS.NFL_ARTIFACTS / "draft_rb_wr"
DRAFT_RB_WR_DATA = WS.NFL_RAW / "draft_rb_wr"
