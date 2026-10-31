"""Study-only workspace layout for inspecting original, unprocessed EMG signals.

Every selection is an independent recording channel, not a reconstructed muscle
activation. Values have unknown amplitude units, and no normalization is applied.
"""
from __future__ import annotations

import math
from typing import Any

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from kinoryx.io.xsens_emg import EmgRecording
from kinoryx.plot_layout import plan_subplot_layout


# Reuse the existing dashboard palette instead of introducing new colors.
# Each trace is still distinguishable when multiple channels are overlaid.
CHANNEL_COLORS = {
    "0": "#365d77",  # existing left-side blue
    "1": "#a65d3f",  # existing right-side terracotta
    "2": "#0847A6",  # existing dashboard heading blue
    "3": "#657073",  # existing neutral accent
}

DEFAULT_WORKSPACE = {"left": ["0"], "right": ["2"]}
VALID_MODES = ("side", "stack", "overlay")


def canonical_workspace(data: Any, recording: EmgRecording) -> dict[str, list[str]]:
    """Validate session state so the browser never chooses arbitrary file paths."""
    valid_ids = {str(ch.id) for ch in recording.channels}
    if not isinstance(data, dict):
        data = DEFAULT_WORKSPACE
    result: dict[str, list[str]] = {}
    for slot in ("left", "right"):
        raw = data.get(slot, [])
        if not isinstance(raw, list):
            raw = []
        result[slot] = []
        for value in raw:
            key = str(value)
            if key in valid_ids and key not in result[slot]:
                result[slot].append(key)
    return result


def academic_channel_name(name: str) -> str:
    parts = name.strip().split()
    if len(parts) > 1 and parts[-1].lower() in ("left", "right"):
        return f"{parts[-1].capitalize()} {' '.join(parts[:-1]).lower()}"
    return name


def build_workspace_figure(
    recording: EmgRecording,
    data: Any,
    *,
    mode: str = "side",
    start_seconds: float = 1.0,
    window_seconds: float = 1.0,
) -> go.Figure:
    """Render layout variants, preserving the precise selected original samples."""
    if mode not in VALID_MODES:
        raise ValueError("Invalid workspace arrangement")
    if not math.isfinite(start_seconds) or not math.isfinite(window_seconds):
        raise ValueError("Time selection must be finite")
    if start_seconds < 0 or window_seconds <= 0:
        raise ValueError("Invalid time selection")
    fs = recording.sampling_hz
    if start_seconds >= recording.sample_count / fs:
        raise ValueError("Start is beyond the recording")
    first = int(start_seconds * fs)
    last = min(recording.sample_count, max(first + 1, int((start_seconds + window_seconds) * fs)))
    t = np.arange(first, last) / fs
    selected = canonical_workspace(data, recording)
    channel_lookup = {
        str(ch.id): (ch, values)
        for ch, values in zip(recording.channels, recording.samples)
    }
    left, right = selected["left"], selected["right"]
    groups = (
        [("Overlaid channels", list(dict.fromkeys(left + right)))]
        if mode == "overlay"
        else [("Panel A", left), ("Panel B", right)]
    )
    cols = 2 if mode == "side" else 1
    rows = 1 if mode in ("side", "overlay") else 2
    titles = [label for label, _ in groups]
    geometry = plan_subplot_layout(titles, cols=cols, minimum_height=490,
                                   preferred_panel_height=360)
    figure = make_subplots(
        rows=rows, cols=cols, shared_xaxes="all",
        horizontal_spacing=0.13 if cols == 2 else 0.0,
        vertical_spacing=geometry.vertical_spacing,
        subplot_titles=geometry.titles,
    )
    for index, (label, channels) in enumerate(groups):
        row, col = (1, index + 1) if mode == "side" else (index + 1, 1)
        for channel_id in channels:
            ch, samples = channel_lookup[channel_id]
            figure.add_trace(
                go.Scattergl(
                    x=t,
                    y=np.asarray(samples[first:last], dtype=float),
                    mode="lines",
                    line={"width": 1.3, "color": CHANNEL_COLORS.get(channel_id, "#344C5B")},
                    name=academic_channel_name(ch.name),
                    legendgroup=channel_id,
                    showlegend=(mode == "overlay" or index == 0 or channel_id not in left),
                    hovertemplate=(
                        "%{fullData.name}<br>Relative time: %{x:.4f} s"
                        "<br>Raw EMG: %{y:.3f} (unit unknown)<extra></extra>"
                    ),
                ),
                row=row, col=col,
            )
        if not channels:
            figure.add_annotation(
                text="Drag an EMG channel here",
                x=0.5, y=0.5, xref=f"x{index + 1 if index else ''} domain",
                yref=f"y{index + 1 if index else ''} domain",
                showarrow=False, font={"color": "#7A838C", "size": 13},
            )
    figure.update_layout(
        template="plotly_white",
        height=geometry.height,
        margin={"l": 70, "r": 26, "t": 92, "b": 72},
        font={"family": "Arial, sans-serif", "size": 12, "color": "#2E3741"},
        legend={"orientation": "h", "x": 0, "y": 1.14, "yanchor": "bottom"},
        showlegend=True,
        hovermode="x",
        paper_bgcolor="#fff",
        plot_bgcolor="#fff",
    )
    figure.update_yaxes(
        title_text=None, automargin=True, zeroline=True,
        showgrid=True, gridcolor="#E9EDF0",
    )
    figure.update_xaxes(
        title_text="Relative time (s)", automargin=True,
        showgrid=True, gridcolor="#E9EDF0",
    )
    return figure
