import pandas as pd
import plotly.graph_objects as go
import plotly.colors as pc
import warnings
from scipy.stats import norm


def plot_mean_with_ci(
    means_df: pd.DataFrame,
    stds_df: pd.DataFrame,
    alpha: float = 1.96,
    title: str = "",
    xaxis_title: str = "",
    yaxis_title: str = "",
):
    """
    Plot each column of means_df with confidence intervals using Plotly.

    Parameters:
        means_df (pd.DataFrame): DataFrame of means, indexed by time or observation.
        stds_df (pd.DataFrame): DataFrame of standard deviations (same shape as means_df).
        alpha (float): Significance level for Normal two-sided CI
    """
    assert means_df.shape == stds_df.shape, "Shape of means and stds df do not match..."

    ci_multiplier = norm.ppf(1 - alpha / 2)

    fig = go.Figure()
    color_cycle = pc.qualitative.Plotly  # 10-color palette
    if len(means_df.columns) > 10:
        warnings.warn("More than 10 columns to plot - may duplicate colors.")

    for i, col in enumerate(means_df.columns):
        mean = means_df[col]
        std = stds_df[col]
        upper = mean + ci_multiplier * std
        lower = mean - ci_multiplier * std
        color = color_cycle[i % len(color_cycle)]

        # Add mean line
        fig.add_trace(
            go.Scatter(
                x=means_df.index,
                y=mean,
                mode="lines",
                name=f"{col}",
                line=dict(color=color),
                legendgroup=col,  # Group line + CI
                showlegend=True,  # Show only for the line
                visible=True,
            )
        )

        # Add confidence interval as filled area
        fig.add_trace(
            go.Scatter(
                x=pd.concat(
                    [means_df.index.to_series(), means_df.index.to_series()[::-1]]
                ),
                y=pd.concat([upper, lower[::-1]]),
                fill="toself",
                fillcolor=color,
                opacity=0.2,
                line=dict(color="rgba(255,255,255,0)"),
                hoverinfo="skip",
                legendgroup=col,  # Belongs to same group
                showlegend=False,
                name=f"{col} CI",
                visible=True,
            )
        )

    fig.update_layout(
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
    )

    fig.show()

    return fig
