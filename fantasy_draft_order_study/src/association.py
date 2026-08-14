"""Association helpers for NB06. Importable so the notebook does not retype formulas."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd


N_TEAMS = 12
AVAILABILITY_THRESHOLD = 0.75


def snake_round2_pick_no(slot: int, n_teams: int = N_TEAMS) -> int:
    return 2 * n_teams + 1 - int(slot)


def pair_label(slot: int, n_teams: int = N_TEAMS) -> str:
    return f"{int(slot)} and {snake_round2_pick_no(slot, n_teams)}"


def linear_fit(x, y) -> dict:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    x = x[mask]
    y = y[mask]
    n = int(x.size)
    if n < 3:
        raise ValueError("linear_fit needs at least 3 finite pairs")
    x_mean = float(x.mean())
    y_mean = float(y.mean())
    ss_xx = float(np.dot(x - x_mean, x - x_mean))
    ss_yy = float(np.dot(y - y_mean, y - y_mean))
    ss_xy = float(np.dot(x - x_mean, y - y_mean))
    slope = ss_xy / ss_xx if ss_xx else math.nan
    intercept = y_mean - slope * x_mean
    pearson_r = ss_xy / math.sqrt(ss_xx * ss_yy) if ss_xx and ss_yy else math.nan
    r_squared = pearson_r * pearson_r if math.isfinite(pearson_r) else math.nan
    spearman = float(pd.Series(x).corr(pd.Series(y), method="spearman"))
    return {
        "n": n,
        "slope": slope,
        "intercept": intercept,
        "pearson_r": pearson_r,
        "r_squared": r_squared,
        "spearman_rho": spearman,
        "x_mean": x_mean,
        "y_mean": y_mean,
    }


def slot_means(frame: pd.DataFrame, value_col: str, slot_col: str = "draft_slot") -> pd.DataFrame:
    out = (
        frame.groupby(slot_col, as_index=False)
        .agg(n=(value_col, "size"), mean_value=(value_col, "mean"))
        .sort_values(slot_col)
    )
    out["pair_label"] = out[slot_col].map(pair_label)
    return out
