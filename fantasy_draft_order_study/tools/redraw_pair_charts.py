from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

from src.association import linear_fit, slot_means

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"
pairs = pd.read_csv(ROOT / "data/processed/snake_pair_panel.csv")
available = pairs.loc[pairs["both_available"].astype(str).str.lower().isin(["true", "1"])]


def draw(frame, title, filename, y_range):
    fit = linear_fit(frame["draft_slot"], frame["pair_ppr"])
    means = slot_means(frame, "pair_ppr")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=means["pair_label"],
        y=means["mean_value"],
        marker_color="#3367d6",
        name="Mean combined PPR",
        text=means["mean_value"].map(lambda v: f"{v:.1f}"),
        textposition="outside",
        cliponaxis=False,
    ))
    x_num = means["draft_slot"].to_numpy(float)
    fig.add_trace(go.Scatter(
        x=means["pair_label"],
        y=fit["intercept"] + fit["slope"] * x_num,
        mode="lines",
        name="Linear fit vs slot",
        line={"color": "#d93025", "dash": "dash"},
    ))
    fig.update_layout(
        template="plotly_white",
        height=560,
        title=title,
        xaxis_title="Snake pair (round 1 and round 2)",
        yaxis_title="Mean combined regular-season PPR (axis cropped)",
        yaxis={"range": y_range},
        margin={"t": 80, "b": 80},
        annotations=[{
            "x": 0.99,
            "y": 0.02,
            "xref": "paper",
            "yref": "paper",
            "xanchor": "right",
            "yanchor": "bottom",
            "showarrow": False,
            "text": f"r = {fit['pearson_r']:.3f}    R^2 = {fit['r_squared']:.3f}    n = {fit['n']:,}",
        }],
    )
    fig.write_html(ART / filename, include_plotlyjs="cdn")
    print(filename, "n", fit["n"], "range", y_range)


draw(pairs, "First two picks combined PPR by snake seat", "association_03_snake_pairs.html", [340, 400])
draw(available, "First two picks combined PPR, both available 75%+", "association_04_snake_pairs_available.html", [430, 465])
