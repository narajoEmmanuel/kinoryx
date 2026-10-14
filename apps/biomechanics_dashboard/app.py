"""KINORYX Biomechanics Dashboard, an independent local scientific workspace.

Run from the repository root:
    python apps/biomechanics_dashboard/app.py

The dashboard only consumes Gait Detection Engine outputs. Its displayed peaks are
exploratory signal features, NOT validated gait events or clinical measurements.
"""

import base64
import binascii
import io
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html

from kinoryx.demo.synthetic import generate_demo_dataset
from kinoryx.pipeline import analyze_exploratory

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_UPLOAD_ROWS = 200_000
MAX_DISPLAY_POINTS = 6_000
COLORS = {"left": "#6CD8C0", "right": "#E6AE76"}
DEFAULT_LAYERS = ["raw", "filtered", "candidates"]


def decode_csv(contents: str) -> pd.DataFrame:
    """Decode a small in-memory UTF-8 CSV for a LOCAL-only research dashboard."""
    try:
        _, encoded = contents.split(",", 1)
        raw = base64.b64decode(encoded, validate=True)
    except (AttributeError, ValueError, binascii.Error) as exc:
        raise ValueError("The file upload could not be decoded.") from exc
    if len(raw) > MAX_UPLOAD_BYTES:
        raise ValueError("File exceeds the 10 MiB prototype limit.")
    try:
        frame = pd.read_csv(io.BytesIO(raw))
    except (pd.errors.ParserError, pd.errors.EmptyDataError, UnicodeDecodeError) as exc:
        raise ValueError("Unable to read the CSV. Use a UTF-8 encoded file.") from exc
    if len(frame) > MAX_UPLOAD_ROWS:
        raise ValueError("File exceeds the 200,000-row prototype limit.")
    return frame


def build_figure(result, side="both", layers=None):
    """Plot measured or synthetic signals and engine-generated peak candidates only."""
    if layers is None:
        layers = DEFAULT_LAYERS
    selected = set(layers)
    fig = go.Figure()
    for channel in result.info.available_channels:
        channel_side = channel.split("_", 1)[0]
        if side != "both" and channel_side != side:
            continue
        color = COLORS[channel_side]
        count = len(result.raw)
        stride = max(1, (count + MAX_DISPLAY_POINTS - 1) // MAX_DISPLAY_POINTS)
        indices = list(range(0, count, stride))
        if indices[-1] != count - 1:
            indices.append(count - 1)
        time = result.raw["time_s"].iloc[indices]
        if "raw" in selected:
            fig.add_trace(go.Scattergl(
                x=time, y=result.raw[channel].iloc[indices], mode="lines",
                name=f"{channel_side.title()} raw",
                line={"color": color, "width": 1.25, "dash": "dot"},
                opacity=0.38,
                hovertemplate="%{x:.3f} s<br>%{y:.2f} °/s<extra>Raw signal</extra>",
            ))
        if "filtered" in selected:
            fig.add_trace(go.Scattergl(
                x=time, y=result.filtered[channel].iloc[indices], mode="lines",
                name=f"{channel_side.title()} filtered",
                line={"color": color, "width": 2.5},
                hovertemplate="%{x:.3f} s<br>%{y:.2f} °/s<extra>Filtered signal</extra>",
            ))
        if "candidates" in selected:
            candidates = [p for p in result.peaks if p.side == channel_side]
            fig.add_trace(go.Scatter(
                x=[p.time_s for p in candidates],
                y=[p.amplitude_deg_s for p in candidates],
                mode="markers", name=f"{channel_side.title()} candidate peaks",
                marker={"size": 9, "symbol": "circle-open", "color": color,
                        "line": {"width": 2}},
                hovertemplate="%{x:.3f} s<br>%{y:.2f} °/s<extra>Unvalidated peak</extra>",
            ))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#121E23", plot_bgcolor="#121E23",
        font={"family": "Segoe UI, Arial, sans-serif", "color": "#BCCACE", "size": 12},
        xaxis={"title": "TIME (s)", "gridcolor": "#293B40", "zeroline": False,
               "linecolor": "#405157", "showspikes": True, "spikemode": "across"},
        yaxis={"title": "ANGULAR VELOCITY (°/s)", "gridcolor": "#293B40",
               "zerolinecolor": "#405157", "linecolor": "#405157"},
        legend={"orientation": "h", "y": -0.24, "x": 0, "font": {"size": 11}},
        margin={"l": 72, "r": 20, "t": 26, "b": 86},
        hovermode="x unified", height=490, uirevision="kinoryx-signal-v1",
    )
    return fig


def _metric(label: str, value: str, description: str = ""):
    return html.Div([
        html.P(label, className="metric-label"),
        html.Div(value, className="metric-value"),
        html.P(description, className="metric-desc"),
    ], className="metric-card")


def _candidate_table(result, side: str):
    peaks = [p for p in result.peaks if side == "both" or p.side == side]
    if not peaks:
        return html.P("No exploratory peaks in this view.", className="empty-copy")
    header = html.Thead(html.Tr([
        html.Th("SIDE"), html.Th("TIME (s)"), html.Th("AMP. (°/s)"), html.Th("SAMPLE"),
    ]))
    rows = []
    for candidate in peaks[:12]:
        rows.append(html.Tr([
            html.Td(candidate.side.upper(), className=f"side-{candidate.side}"),
            html.Td(f"{candidate.time_s:.3f}"),
            html.Td(f"{candidate.amplitude_deg_s:.2f}"),
            html.Td(str(candidate.sample_index)),
        ]))
    return html.Div([
        html.Table([header, html.Tbody(rows)], className="candidate-table"),
        html.P(f"Showing {min(12, len(peaks))} of {len(peaks)} signal peaks. "
               "These are not initial contacts or toe-offs.", className="table-footnote"),
    ], className="table-scroll")


def _dashboard_metrics(result):
    time = result.raw["time_s"]
    duration = float(time.iloc[-1] - time.iloc[0])
    return [
        _metric("RECORDING WINDOW", f"{duration:.2f} s", "From the supplied time axis"),
        _metric("SAMPLING RATE", f"{result.info.sampling_hz:.1f} Hz", "Estimated from sample times"),
        _metric("AVAILABLE CHANNELS", str(len(result.info.available_channels)), "Gyroscope demo contract"),
        _metric("PEAK CANDIDATES", str(len(result.peaks)), "Exploratory, unvalidated"),
    ]


def _source_panel(result, synthetic, filename):
    source = "SYNTHETIC DEMO" if synthetic else "LOCAL CSV"
    label = "Built-in demonstration" if synthetic else (filename or "Imported CSV")
    warnings = list(result.info.warnings)
    details = [
        ("DATA ORIGIN", source),
        ("SOURCE", label),
        ("RECORDS", f"{result.info.rows:,}"),
        ("VALIDATION", "NOT CLINICALLY VALIDATED"),
    ]
    return html.Div([
        *[html.Div([html.Span(key), html.Strong(value)], className="provenance-row")
          for key, value in details],
        html.Div(
            [html.Strong("Timing warning"), html.P(" ".join(warnings))]
            if warnings else [html.Strong("Basic timing check"),
                                   html.P("No sampling irregularity flag. This is not a data-quality certification.")],
            className="quality-notice" if warnings else "quality-notice quality-ok",
        ),
    ])


def _empty_figure(message):
    fig = go.Figure()
    fig.add_annotation(text=message, showarrow=False, font={"color": "#E6AE76", "size": 14})
    fig.update_layout(paper_bgcolor="#121E23", plot_bgcolor="#121E23", height=490,
                      xaxis={"visible": False}, yaxis={"visible": False})
    return fig


def create_app():
    assets_folder = str(Path(__file__).parent / "assets")
    app = Dash(__name__, title="KINORYX | Biomechanics Dashboard", assets_folder=assets_folder)
    app.layout = html.Div([
        html.A("Skip to workspace", href="#workspace", className="skip-link"),
        html.Aside([
            html.Div([
                html.Div("K", className="brand-mark"),
                html.Div([html.Strong("KINORYX"), html.Small("HUMAN MOTION INTELLIGENCE")],
                         className="brand-name"),
            ], className="brand-lockup"),
            html.Div("RESEARCH WORKSPACE", className="sidebar-label"),
            html.Div([html.Span("01", className="nav-index"), "Signal explorer"],
                     className="nav-item is-active"),
            html.Div("COMING LATER", className="sidebar-label sidebar-gap"),
            html.Div([html.Span("02", className="nav-index"), "Gait events"],
                     className="nav-item is-planned"),
            html.Div([html.Span("03", className="nav-index"), "Cycle analysis"],
                     className="nav-item is-planned"),
            html.Div([html.Span("04", className="nav-index"), "Reports"],
                     className="nav-item is-planned"),
            html.Div([
                html.Div("RESEARCH PRE-ALPHA", className="foot-heading"),
                html.P("Local-first tools for open biomechanics. No diagnostic use."),
                html.Span("VERSION 0.1 / DASHBOARD WORKSPACE", className="foot-version"),
            ], className="sidebar-foot"),
        ], className="sidebar", **{"aria-label": "Workspace navigation"}),
        html.Main([
            html.Header([
                html.Div([
                    html.Div("KINORYX  /  BIOMECHANICS DASHBOARD", className="eyebrow"),
                    html.H1("Signal explorer"),
                    html.P("Investigate movement data with transparent signals, source information and exploratory candidates.",
                           className="page-subtitle"),
                ]),
                html.Div([html.Span(className="status-dot"), "LOCAL WORKSPACE"],
                         className="session-status"),
            ], className="page-header"),
            html.Section([
                html.Div([
                    html.Div("01 / DATA INPUT", className="section-kicker"),
                    html.H2("Start with a recording"),
                    html.P("Explore synthetic demonstration data or import a compatible, non-identifying CSV.",
                           className="muted-copy"),
                ]),
                html.Div([
                    dcc.Upload(id="csv-upload", children=html.Div([
                        html.Span("↥", className="upload-icon"),
                        html.Span([html.Strong("Choose a CSV"), " or drop a file here"]),
                        html.Small("Canonical gyroscope columns, up to 10 MiB"),
                    ], className="upload-inner"), className="upload-area", multiple=False,
                               accept=".csv,text/csv"),
                    html.Button("Load synthetic demo", id="reset-demo", n_clicks=0,
                                className="secondary-button", type="button"),
                ], className="input-actions"),
            ], className="upload-section"),
            html.Div(id="status-alert", className="status-alert", role="status"),
            html.Section(id="workspace", children=[
                html.Div(id="metrics-grid", className="metrics-grid"),
                html.Div([
                    html.Section([
                        html.Div([
                            html.Div([html.Div("02 / SIGNAL VIEW", className="section-kicker"),
                                      html.H2("Angular velocity")]),
                            html.Div("RAW / FILTERED / CANDIDATES", className="chart-meta"),
                        ], className="section-heading"),
                        dcc.Loading(dcc.Graph(id="signal-graph", config={"displaylogo": False,
                            "scrollZoom": True, "modeBarButtonsToRemove": ["lasso2d", "select2d"]},
                                               className="signal-graph")),
                        html.P("Lines may be downsampled for display only. "
                               "Filtering and candidate extraction use the full imported series.",
                               className="figure-caption"),
                    ], className="panel chart-panel"),
                    html.Aside([
                        html.Div("DISPLAY CONTROLS", className="section-kicker"),
                        html.H3("Signal layers"),
                        dcc.Checklist(id="signal-layers", options=[
                            {"label": "Raw signal", "value": "raw"},
                            {"label": "Filtered signal", "value": "filtered"},
                            {"label": "Candidate peaks", "value": "candidates"},
                        ], value=DEFAULT_LAYERS, className="layer-checklist",
                                      inputClassName="layer-input", labelClassName="layer-label"),
                        html.Div("FOOT SELECTION", className="section-kicker control-divider"),
                        dcc.RadioItems(id="side-selector", options=[
                            {"label": "Both", "value": "both"},
                            {"label": "Left", "value": "left"},
                            {"label": "Right", "value": "right"},
                        ], value="both", className="side-selector",
                                       labelClassName="side-choice"),
                        html.Div("INTERPRETATION", className="section-kicker control-divider"),
                        html.P("Markers show amplitude peaks identified by the current engine. "
                               "They must not be interpreted as steps, initial contacts, or toe-offs.",
                               className="annotation-copy"),
                    ], className="panel controls-panel"),
                ], className="workspace-grid"),
                html.Div([
                    html.Section([
                        html.Div("03 / CANDIDATE INSPECTION", className="section-kicker"),
                        html.H2("Peak candidates"),
                        html.Div(id="candidate-table"),
                    ], className="panel inspection-panel"),
                    html.Section([
                        html.Div("04 / SOURCE AND QUALITY", className="section-kicker"),
                        html.H2("Recording context"),
                        html.Div(id="source-panel", className="source-panel"),
                    ], className="panel source-card"),
                ], className="bottom-grid"),
            ]),
            html.Footer("KINORYX IS EXPERIMENTAL RESEARCH SOFTWARE. NOT A MEDICAL DEVICE. "
                        "DO NOT UPLOAD IDENTIFIABLE PATIENT INFORMATION.", className="footer-note"),
        ], className="main-content"),
    ], className="app-shell")

    @app.callback(Output("csv-upload", "contents"), Input("reset-demo", "n_clicks"),
                  prevent_initial_call=True)
    def reset_to_demo(_clicks):
        return None

    @app.callback(
        Output("signal-graph", "figure"),
        Output("metrics-grid", "children"),
        Output("candidate-table", "children"),
        Output("source-panel", "children"),
        Output("status-alert", "children"),
        Output("status-alert", "className"),
        Input("csv-upload", "contents"),
        Input("csv-upload", "filename"),
        Input("side-selector", "value"),
        Input("signal-layers", "value"),
    )
    def update_workspace(contents, filename, side, layers):
        synthetic = contents is None
        try:
            frame = generate_demo_dataset() if synthetic else decode_csv(contents)
            result = analyze_exploratory(frame)
            label = "SYNTHETIC DATA" if synthetic else "LOCAL CSV"
            message = (f"{label}  |  {result.info.rows:,} samples  |  "
                       f"{len(result.peaks)} unvalidated signal peaks  |  "
                       "No clinical inference")
            return (
                build_figure(result, side=side, layers=layers),
                _dashboard_metrics(result),
                _candidate_table(result, side),
                _source_panel(result, synthetic, filename),
                message, "status-alert status-ok",
            )
        except (ValueError, TypeError, KeyError, pd.errors.ParserError) as exc:
            return (
                _empty_figure("No compatible data to display"),
                [_metric("SESSION STATUS", "Input rejected", "Check the CSV contract")],
                html.P("No candidates available.", className="empty-copy"),
                html.P("No valid recording loaded."),
                f"Unable to analyze input: {exc}", "status-alert status-error",
            )
    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=8050, debug=False)