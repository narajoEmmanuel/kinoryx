"""Study-only live EMG viewer mounted at /lab/ on the local KINORYX Dash server.

The first view always shows original samples. Filtering and RMS are explicitly
optional previews, NOT validated clinical processing or production defaults.
This module exists only on the disposable research branch.
"""

from functools import lru_cache
from pathlib import Path

from dash import Dash, Input, Output, dcc, html
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.signal import butter, sosfiltfilt

from kinoryx.io.xsens_emg import EmgRecording, read_mvne
from kinoryx.plot_layout import plan_subplot_layout

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "research/source_data/EMG2_Squats-200714130240.mvne"
ASSETS = ROOT / "apps/biomechanics_dashboard/assets"
RAW_COLOR = "#235D86"
PREVIEW_COLOR = "#A65D3F"
CONFIG = {
    "displaylogo": False,
    "responsive": True,
    "toImageButtonOptions": {
        "format": "svg",
        "filename": "kinoryx_research_emg",
        "scale": 1,
    },
}


@lru_cache(maxsize=1)
def load_source() -> EmgRecording:
    """Read once from the verified tracked research path, never from an upload."""
    if not SOURCE.is_file():
        raise FileNotFoundError(
            "EMG recording is missing. Run git pull on the research branch."
        )
    return read_mvne(SOURCE)


def preview_transform(samples: np.ndarray, fs: float, mode: str) -> np.ndarray:
    """A descriptive preview, not a standardized or validated EMG pipeline."""
    x = np.asarray(samples, dtype=float)
    if mode == "raw":
        return x.copy()
    if mode == "bandpass":
        if fs <= 900:
            raise ValueError("Sampling rate is too low for the 20 to 450 Hz preview")
        sos = butter(4, (20.0, 450.0), btype="bandpass", fs=fs, output="sos")
        return sosfiltfilt(sos, x)
    if mode == "rms":
        n = max(1, round(fs * 0.25))
        # Fixed 250 ms moving window, edges use available neighboring samples.
        squares = x * x
        cumulative = np.concatenate(([0.0], np.cumsum(squares)))
        indices = np.arange(x.size)
        left = np.maximum(indices - n // 2, 0)
        right = np.minimum(indices + (n + 1) // 2, x.size)
        return np.sqrt(np.maximum(0, (cumulative[right] - cumulative[left]) / (right - left)))
    raise ValueError("Unknown preview mode")


def academic_channel_name(name: str) -> str:
    """Display anatomy as 'Right rectus femoris', without changing source metadata."""
    parts = name.strip().split()
    if len(parts) > 1 and parts[-1].lower() in ("left", "right"):
        return f"{parts[-1].capitalize()} {' '.join(parts[:-1]).lower()}"
    return name


def comparison_label(mode: str) -> str:
    return {
        "raw": "Raw EMG",
        "bandpass": "Band-pass filter (20 to 450 Hz)",
        "rms": "RMS amplitude (250 ms window)",
    }[mode]


def make_emg_figure(
    recording: EmgRecording,
    selected: str,
    start_seconds: float,
    window_seconds: float,
    mode: str,
) -> go.Figure:
    """Keep each original signal separately visible next to any transformed view."""
    if selected != "all" and selected not in {str(ch.id) for ch in recording.channels}:
        raise ValueError("Unknown channel selection")
    fs = recording.sampling_hz
    total = recording.sample_count / fs
    start = float(start_seconds)
    window = float(window_seconds)
    if not np.isfinite(start) or not np.isfinite(window) or start < 0 or window <= 0:
        raise ValueError("Invalid time window")
    if start >= total:
        raise ValueError("Window starts after the end of the recording")
    first = min(recording.sample_count - 1, int(start * fs))
    last = min(recording.sample_count, max(first + 1, int((start + window) * fs)))
    visible = [(ch, np.asarray(raw, dtype=float))
               for ch, raw in zip(recording.channels, recording.samples)
               if selected == "all" or str(ch.id) == selected]
    comparative = mode != "raw"
    cols = 2 if comparative else 1
    labels = [
        title
        for ch, _ in visible
        for title in (
            [
                f"{academic_channel_name(ch.name)} | Raw EMG",
                f"{academic_channel_name(ch.name)} | {comparison_label(mode)}",
            ] if comparative else [f"{academic_channel_name(ch.name)} | Raw EMG"]
        )
    ]
    geometry = plan_subplot_layout(labels, cols=cols, minimum_height=460)
    figure = make_subplots(
        rows=geometry.rows,
        cols=cols,
        shared_xaxes="all",
        horizontal_spacing=0.085 if comparative else 0.0,
        vertical_spacing=geometry.vertical_spacing,
        subplot_titles=geometry.titles,
    )
    t = np.arange(first, last) / fs
    for row, (ch, raw) in enumerate(visible, start=1):
        figure.add_trace(
            go.Scattergl(
                x=t, y=raw[first:last], mode="lines",
                line={"color": RAW_COLOR, "width": 1},
                name=f"{academic_channel_name(ch.name)}, raw EMG",
                hovertemplate="Time: %{x:.4f} s<br>Raw EMG: %{y:.3f} (unit unknown)<extra></extra>",
            ), row=row, col=1,
        )
        if comparative:
            transformed = preview_transform(raw, fs, mode)
            figure.add_trace(
                go.Scattergl(
                    x=t, y=transformed[first:last], mode="lines",
                    line={"color": PREVIEW_COLOR, "width": 1.3},
                    name=f"{academic_channel_name(ch.name)}, {comparison_label(mode)}",
                    hovertemplate="Time: %{x:.4f} s<br>Preview: %{y:.3f} (uncalibrated)<extra></extra>",
                ), row=row, col=2,
            )
    figure.update_layout(
        template="plotly_white",
        height=geometry.height,
        margin={
            "l": 130,
            "r": 32,
            "t": 76 + 21 * (geometry.title_lines - 1),
            "b": 88,
        },
        showlegend=False,
        hovermode="x",
        font={"family": "Arial, sans-serif", "color": "#34383A", "size": 12},
        paper_bgcolor="#fff",
        plot_bgcolor="#fff",
    )
    figure.update_annotations(font={"family": "Arial, sans-serif", "size": 12})
    # A single shared label avoids four long, vertically overlapping axis labels.
    figure.update_yaxes(
        title_text=None, zeroline=True, automargin=True,
        showgrid=True, gridcolor="#edf0f0",
    )
    figure.update_xaxes(
        title_text=None, showgrid=True, gridcolor="#edf0f0",
        automargin=True,
    )
    for column in range(1, cols + 1):
        figure.update_xaxes(
            title_text="Relative time (s)",
            title_standoff=16,
            row=geometry.rows, col=column,
        )
    figure.add_annotation(
        x=-0.10, y=0.5, xref="paper", yref="paper",
        text="EMG amplitude (unit not established)",
        textangle=-90, showarrow=False,
        font={"family": "Arial, sans-serif", "size": 12, "color": "#34383A"},
    )
    return figure


def build_layout() -> html.Main:
    try:
        recording = load_source()
    except (OSError, ValueError) as exc:
        return html.Main(
            [
                html.H1("KINORYX | EMG Research Laboratory"),
                html.P(f"Research data unavailable: {exc}"),
                html.A("Return to dashboard", href="/"),
            ],
            className="app-shell lab-shell",
        )
    channel_options = [{"label": "All four EMG channels", "value": "all"}]
    channel_options.extend(
        {"label": f"{ch.id} | {academic_channel_name(ch.name)}", "value": str(ch.id)}
        for ch in recording.channels
    )
    return html.Main(
        [
            html.Header(
                [
                    html.A("← Back to gait dashboard", href="/", className="lab-back"),
                    html.Div("KINORYX / RESEARCH ONLY", className="brand-kicker"),
                    html.H1("EMG Research Laboratory", className="page-title"),
                    html.P(
                        "Interactive visualization of the original Cometa EMG recording. "
                        "Inspect the unprocessed signal before evaluating any transformation.",
                        className="page-subtitle",
                    ),
                    html.P(
                        "Research only · Localhost · Source files remain unchanged · "
                        "Not merged into main",
                        className="lab-caution",
                    ),
                ],
                className="hero-panel",
            ),
            html.Section(
                [
                    html.Div(
                        [
                            html.H2("Recording", className="section-title"),
                            html.P(SOURCE.name, className="lab-source"),
                            html.Div(
                                [
                                    html.Div([html.Small("Channels"), html.Strong(str(len(recording.channels)))]),
                                    html.Div([html.Small("Sampling rate"), html.Strong(f"{recording.sampling_hz:g} Hz")]),
                                    html.Div([html.Small("Samples per channel"), html.Strong(f"{recording.sample_count:,}")]),
                                    html.Div([html.Small("Recording span"), html.Strong(f"{recording.sample_span_s:.3f} s")]),
                                ], className="lab-metrics",
                            ),
                            html.P(
                                "Muscle labels are taken from the source XML; "
                                "amplitude units, calibration and synchronization are unverified.",
                                className="lab-help",
                            ),
                        ],
                        className="lab-source-pane",
                    ),
                    html.Div(
                        [
                            html.H2("Signal explorer", className="section-title"),
                            html.Label("EMG channel", htmlFor="lab-channel", className="control-label"),
                            dcc.Dropdown(
                                id="lab-channel", options=channel_options, value="all",
                                clearable=False,
                            ),
                            html.Label("Window start (s)", htmlFor="lab-start", className="control-label"),
                            dcc.Slider(
                                id="lab-start", min=0, max=8, step=0.1, value=0,
                                marks={0: "0", 2: "2", 4: "4", 6: "6", 8: "8"},
                                tooltip={"placement": "bottom", "always_visible": False},
                            ),
                            html.Label("Window duration", htmlFor="lab-window", className="control-label"),
                            dcc.RadioItems(
                                id="lab-window",
                                options=[
                                    {"label": "0.25 s", "value": 0.25},
                                    {"label": "1 s", "value": 1.0},
                                    {"label": "2 s", "value": 2.0},
                                    {"label": "Full recording", "value": 8.3},
                                ],
                                value=8.3, inline=True,
                                className="lab-inline",
                            ),
                            html.Label("Signal view", htmlFor="lab-transform", className="control-label"),
                            dcc.RadioItems(
                                id="lab-transform",
                                options=[
                                    {"label": "Raw EMG", "value": "raw"},
                                    {"label": "Compare band-pass, 20 to 450 Hz", "value": "bandpass"},
                                    {"label": "Compare RMS, 250 ms window", "value": "rms"},
                                ],
                                value="raw", className="lab-inline",
                            ),
                            html.P(
                                "Signal processing previews are exploratory and not validated "
                                "for this recording. The unprocessed signal is always displayed "
                                "alongside any transformed preview.",
                                className="lab-help",
                            ),
                        ],
                        className="lab-controls-pane",
                    ),
                ],
                className="lab-top-grid",
            ),
            html.Section(
                [
                    html.H2("EMG signals and exploratory comparisons", className="section-title"),
                    html.Div(id="lab-status", className="status-banner", role="status"),
                    dcc.Loading(
                        dcc.Graph(id="lab-figure", config=CONFIG, className="lab-figure"),
                        type="circle",
                    ),
                    html.P(
                        "Time is relative to the first sample. EMG amplitudes have no confirmed "
                        "physical unit or normalization reference. These comparisons do not "
                        "establish muscle force, activation levels or a clinical diagnosis.",
                        className="lab-help",
                    ),
                ], className="lab-plot-section",
            ),
            html.Footer(
                [
                    html.P(
                        "Experimental workspace for assessing methods and validating evidence "
                        "before changing the production application."
                    ),
                ], className="page-footer",
            ),
        ], className="app-shell lab-shell",
    )


def mount_research_lab(flask_server) -> Dash:
    """Share the existing localhost server, without replacing the gait dashboard."""
    lab = Dash(
        "kinoryx.research_lab",
        server=flask_server,
        url_base_pathname="/lab/",
        assets_folder=str(ASSETS),
        title="KINORYX | EMG Research Laboratory",
        suppress_callback_exceptions=True,
    )
    lab.layout = build_layout()

    @lab.callback(
        Output("lab-figure", "figure"),
        Output("lab-status", "children"),
        Input("lab-channel", "value"),
        Input("lab-start", "value"),
        Input("lab-window", "value"),
        Input("lab-transform", "value"),
    )
    def refresh(channel: str, start: float, window: float, mode: str):
        try:
            recording = load_source()
            figure = make_emg_figure(recording, channel, start, window, mode)
            label = "Raw, unprocessed EMG" if mode == "raw" else (
                f"Raw EMG compared with {comparison_label(mode)} (exploratory)"
            )
            return figure, f"{label}. Original recording preserved."
        except (ValueError, OSError) as exc:
            return go.Figure(), f"Unable to display requested view: {exc}"

    return lab
