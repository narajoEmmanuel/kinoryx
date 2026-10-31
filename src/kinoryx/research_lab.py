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


STAGES = (
    ("exploration", "Exploratory Analysis"),
    ("quality", "Signal Quality Assessment"),
    ("experimentation", "Signal Processing Experiments"),
    ("evaluation", "Evaluation & Reporting"),
)
GITHUB_ROOT = (
    "https://github.com/narajoEmmanuel/kinoryx/blob/"
    "study/xsens-cometa-qualisys-20261030/"
)


def stage_from_path(pathname: str | None) -> str:
    """Resolve only the four explicitly supported laboratory pages."""
    parts = (pathname or "/lab/").strip("/").split("/")
    candidate = parts[1] if len(parts) == 2 and parts[0] == "lab" else "exploration"
    return candidate if candidate in {stage[0] for stage in STAGES} else "exploration"


def stage_navigation(active: str):
    return [
        dcc.Link(
            [
                html.Span(f"{idx:02d}", className="lab-stage-index"),
                html.Span(title, className="lab-stage-title"),
            ],
            href=f"/lab/{slug}",
            className="lab-stage-link" + (" is-active" if slug == active else ""),
        )
        for idx, (slug, title) in enumerate(STAGES, start=1)
    ]


def recording_palette(rec: EmgRecording):
    from kinoryx.lab_workspace import CHANNEL_COLORS, academic_channel_name

    return [
        html.Div(
            [
                html.Span(
                    className="lab-color-dot",
                    style={"backgroundColor": CHANNEL_COLORS.get(str(ch.id), "#365d77")},
                ),
                html.Span(academic_channel_name(ch.name), className="lab-source-name"),
                html.Div(
                    [
                        html.Button(
                            "A", type="button", title="Add to panel A",
                            className="lab-add-button",
                            **{"data-channel": str(ch.id), "data-slot": "left"},
                        ),
                        html.Button(
                            "B", type="button", title="Add to panel B",
                            className="lab-add-button",
                            **{"data-channel": str(ch.id), "data-slot": "right"},
                        ),
                    ],
                    className="lab-add-actions",
                ),
            ],
            className="emg-palette-item",
            draggable="true",
            title=f"Drag {academic_channel_name(ch.name)} to panel A or B",
            **{"data-channel": str(ch.id)},
        )
        for ch in rec.channels
    ]


def workspace_slot(slot: str, label: str):
    return html.Div(
        [
            html.Span(f"Panel {label}", className="lab-drop-title"),
            html.Div(id=f"lab-{slot}-chips", className="lab-chip-list"),
        ],
        className="emg-dropzone",
        title="Drag a channel here",
        **{"data-slot": slot},
    )

def exploration_content(rec: EmgRecording):
    return html.Div(
        [
            html.Div(
                [
                    html.Div("CURRENT STAGE / 01", className="lab-kicker"),
                    html.H2("Exploratory Analysis", className="lab-stage-heading"),
                    html.P(
                        "Inspect unprocessed EMG before performing any filtering or "
                        "making physiological claims. Arrange signals for direct visual comparison.",
                        className="lab-stage-description",
                    ),
                ],
                className="lab-stage-intro",
            ),
            html.Div(
                [
                    html.A(
                        "Experiment 01: First burst, 1.0 to 2.0 s",
                        href=GITHUB_ROOT + "research/experiments/01_first_burst_raw.md",
                        target="_blank", rel="noopener noreferrer",
                    ),
                    html.Span("Source evidence and descriptive measurements saved in GitHub"),
                ],
                className="lab-progress-strip",
            ),
            html.P(
                html.A(
                    "Review all Stage 01 notes and progress",
                    href=GITHUB_ROOT + "research/laboratory/01_exploratory_analysis.md",
                    target="_blank", rel="noopener noreferrer",
                ),
                className="lab-stage-record",
            ),
            html.Div(
                [
                    html.Aside(
                        [
                            html.H3("Signal library", className="lab-section-title"),
                            html.P(
                                "Drag a channel into Panel A or B. Use Add buttons "
                                "for keyboard and touch-friendly placement.",
                                className="lab-muted",
                            ),
                            html.Div(recording_palette(rec), className="lab-source-list"),
                            html.Div(
                                [
                                    html.Div("SOURCE RECORDING", className="lab-kicker"),
                                    html.P(SOURCE.name, className="lab-filename"),
                                    html.P(
                                        f"{len(rec.channels)} channels · "
                                        f"{rec.sampling_hz:g} Hz · "
                                        f"{rec.sample_span_s:.3f} s",
                                        className="lab-muted",
                                    ),
                                    html.P(
                                        "Recorded amplitude units are not established. "
                                        "No synchronization has been verified.",
                                        className="lab-muted",
                                    ),
                                ],
                                className="lab-recording-info",
                            ),
                        ],
                        className="lab-sidebar",
                    ),
                    html.Section(
                        [
                            html.Div(
                                [
                                    html.H3("Signal workspace", className="lab-section-title"),
                                    html.Button(
                                        "Reset workspace",
                                        className="lab-workspace-reset",
                                        type="button",
                                    ),
                                ], className="lab-workspace-heading",
                            ),
                            html.Div(
                                [
                                    workspace_slot("left", "Panel A"),
                                    workspace_slot("right", "Panel B"),
                                ],
                                className="lab-drop-grid",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Label("Arrangement", className="control-label"),
                                            dcc.RadioItems(
                                                id="lab-mode",
                                                options=[
                                                    {"label": "Side by side", "value": "side"},
                                                    {"label": "Stacked", "value": "stack"},
                                                    {"label": "Overlay", "value": "overlay"},
                                                ],
                                                value="side",
                                                inline=True,
                                                className="lab-choice-list",
                                            ),
                                        ],
                                        className="lab-control-block",
                                    ),
                                    html.Div(
                                        [
                                            html.Label("Window duration", className="control-label"),
                                            dcc.RadioItems(
                                                id="lab-window",
                                                options=[
                                                    {"label": "0.25 s", "value": 0.25},
                                                    {"label": "1 s", "value": 1.0},
                                                    {"label": "2 s", "value": 2.0},
                                                    {"label": "Full", "value": 8.3},
                                                ],
                                                value=1.0,
                                                inline=True,
                                                className="lab-choice-list",
                                            ),
                                        ],
                                        className="lab-control-block",
                                    ),
                                ],
                                className="lab-options-grid",
                            ),
                            html.Div(
                                [
                                    html.Label("Window start (s)", className="control-label"),
                                    dcc.Slider(
                                        id="lab-start", min=0, max=8, step=0.1, value=1.0,
                                        marks={0: "0", 2: "2", 4: "4", 6: "6", 8: "8"},
                                        tooltip={"placement": "bottom"},
                                    ),
                                ],
                                className="lab-time-control",
                            ),
                            html.Div(id="lab-workspace-note", className="lab-status", role="status"),
                            dcc.Loading(
                                dcc.Graph(
                                    id="lab-comparison-graph",
                                    config=CONFIG,
                                    className="lab-comparison-graph",
                                ),
                                type="circle",
                            ),
                            html.P(
                                "Raw EMG only. Overlay uses the same original numeric scale; "
                                "panel autoscaling and electrode conditions can affect visual comparisons. "
                                "No force, normalized activation or validated event timing is inferred.",
                                className="lab-muted",
                            ),
                        ],
                        className="lab-workspace-main",
                    ),
                ],
                className="lab-exploration-grid",
            ),
        ],
        className="lab-stage-body",
    )


STAGE_CONTENT = {
    "quality": (
        "Signal Quality Assessment",
        "Evaluate the integrity of each recording and identify potential noise, "
        "motion artifacts, interference, baseline shifts and clipping before applying filters.",
        "Not yet assessed",
        (
            "Inspect short raw windows for isolated transients and baseline drift.",
            "Review spectral characteristics and acquisition metadata.",
            "Document limitations before changing signal-processing parameters.",
        ),
    ),
    "experimentation": (
        "Signal Processing Experiments",
        "Compare proposed processing methods to the original signal using explicit "
        "parameters and reproducible experiments.",
        "Planned, not validated",
        (
            "Compare a band-pass preview with the original signal.",
            "Study rectification, RMS and envelope windows separately.",
            "Evaluate sensitivity to assumptions and edge effects.",
        ),
    ),
    "evaluation": (
        "Evaluation & Reporting",
        "Review recorded evidence, validate interpretations and decide what can "
        "be responsibly incorporated into future KINORYX functionality.",
        "Planned, no conclusions approved",
        (
            "Summarize findings, figures, method settings and uncertainties.",
            "Review reproducibility and calibration requirements.",
            "Record accepted and rejected proposals in the decision log.",
        ),
    ),
}


def other_stage_content(stage: str):
    title, description, status, tasks = STAGE_CONTENT[stage]
    next_docs = {
        "quality": "research/laboratory/02_signal_quality.md",
        "experimentation": "research/laboratory/03_processing_experiments.md",
        "evaluation": "research/laboratory/04_evaluation_reporting.md",
    }
    return html.Section(
        [
            html.Div(f"RESEARCH STAGE / {1 + [key for key, _ in STAGES].index(stage):02d}",
                     className="lab-kicker"),
            html.H2(title, className="lab-stage-heading"),
            html.P(description, className="lab-stage-description"),
            html.Div(
                [
                    html.Span("Current progress", className="lab-muted"),
                    html.Strong(status),
                ], className="lab-progress-strip",
            ),
            html.H3("Research checklist", className="lab-section-title"),
            html.Ol([html.Li(item) for item in tasks], className="lab-research-checklist"),
            html.A(
                "Open research notes and methodology",
                href=GITHUB_ROOT + next_docs[stage],
                target="_blank", rel="noopener noreferrer",
                className="lab-document-link",
            ),
            html.P(
                "This page is deliberately reserved for stage-specific results. "
                "Unverified analysis is not presented as a completed finding.",
                className="lab-muted",
            ),
        ],
        className="lab-stage-body lab-planned-stage",
    )


def build_layout() -> html.Main:
    return html.Main(
        [
            dcc.Location(id="lab-location", refresh=False),
            dcc.Store(
                id="lab-workspace",
                storage_type="session",
                data={"left": ["0"], "right": ["2"]},
            ),
            html.Div(id="lab-workspace-hook", style={"display": "none"}),
            html.Header(
                [
                    html.Div(
                        [
                            html.A("KINORYX", href="/", className="lab-brand"),
                            html.Span("/", className="lab-breadcrumb-separator"),
                            html.Span("Laboratory", className="lab-breadcrumb"),
                        ], className="lab-header-brand",
                    ),
                    html.Nav(
                        [
                            html.A("Home", href="/"),
                            html.A("Dashboard", href="/dashboard/"),
                        ], className="lab-top-links",
                    ),
                ], className="lab-product-header",
            ),
            html.Div(
                [
                    html.H1("Laboratory", className="lab-page-title"),
                    html.P(
                        "A structured workflow for scientific signal research.",
                        className="lab-page-description",
                    ),
                ], className="lab-page-heading",
            ),
            html.Nav(id="lab-stage-nav", className="lab-stage-nav",
                     **{"aria-label": "Laboratory research stages"}),
            html.Div(id="lab-stage-content"),
            html.Footer(
                "KINORYX Research Laboratory · Experimental branch · "
                "Source recordings preserved",
                className="lab-footer",
            ),
        ],
        className="app-shell kinoryx-laboratory",
    )


def mount_research_lab(flask_server) -> Dash:
    """Create one permanent /lab/ Dash application with four URL-based stages."""
    from kinoryx.lab_workspace import (
        CHANNEL_COLORS, academic_channel_name,
        build_workspace_figure, canonical_workspace,
    )

    lab = Dash(
        "kinoryx.research_lab",
        server=flask_server,
        url_base_pathname="/lab/",
        assets_folder=str(ASSETS),
        title="KINORYX | Laboratory",
        suppress_callback_exceptions=True,
    )
    lab.layout = build_layout()

    @lab.callback(
        Output("lab-stage-nav", "children"),
        Output("lab-stage-content", "children"),
        Input("lab-location", "pathname"),
    )
    def render_stage(pathname):
        stage = stage_from_path(pathname)
        navigation = stage_navigation(stage)
        if stage != "exploration":
            return navigation, other_stage_content(stage)
        try:
            return navigation, exploration_content(load_source())
        except (ValueError, OSError) as exc:
            return navigation, html.P(
                f"Original recording unavailable: {exc}",
                className="lab-error",
            )

    @lab.callback(
        Output("lab-left-chips", "children"),
        Output("lab-right-chips", "children"),
        Output("lab-comparison-graph", "figure"),
        Output("lab-workspace-note", "children"),
        Input("lab-workspace", "data"),
        Input("lab-mode", "value"),
        Input("lab-start", "value"),
        Input("lab-window", "value"),
    )
    def refresh_workspace(state, mode, start, duration):
        rec = load_source()
        current = canonical_workspace(state, rec)

        def chips(slot):
            result = []
            for channel in current[slot]:
                original = next(ch for ch in rec.channels if str(ch.id) == channel)
                result.append(
                    html.Div(
                        [
                            html.Span(
                                academic_channel_name(original.name),
                                className="lab-chip-name",
                            ),
                            html.Button(
                                "×", type="button",
                                title="Remove channel",
                                className="emg-remove-item",
                                **{"data-channel": channel, "data-slot": slot},
                            ),
                        ],
                        className="emg-active-item",
                        draggable="true",
                        style={"borderLeftColor": CHANNEL_COLORS.get(channel, "#445")},
                        **{"data-channel": channel, "data-from-slot": slot},
                    )
                )
            return result

        try:
            figure = build_workspace_figure(
                rec, current, mode=mode, start_seconds=float(start),
                window_seconds=float(duration),
            )
            status = (
                f"{len(current['left']) + len(current['right'])} placements · "
                f"{mode.replace('side', 'side by side').title()} · "
                "Unprocessed channels, original scale"
            )
            return chips("left"), chips("right"), figure, status
        except (TypeError, ValueError) as exc:
            return chips("left"), chips("right"), go.Figure(), (
                f"Unable to display this workspace: {exc}"
            )

    lab.clientside_callback(
        """
        function(data) {
            window.__kinoryxWorkspaceState = data || {left: ["0"], right: ["2"]};
            return window.dash_clientside.no_update;
        }
        """,
        Output("lab-workspace-hook", "children"),
        Input("lab-workspace", "data"),
    )
    return lab
