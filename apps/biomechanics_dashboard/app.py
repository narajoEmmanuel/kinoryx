
"""KINORYX Biomechanics Dashboard, an independent local scientific workspace.

Run from the repository root:
    python apps/biomechanics_dashboard/app.py
"""

import base64
import binascii
import io
from typing import Iterable

import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html

from kinoryx.demo.synthetic import generate_demo_dataset
from kinoryx.pipeline import ExploratoryResult, analyze_exploratory

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_UPLOAD_ROWS = 200_000
TITLE_FONT = "Arial Black, Arial, Helvetica, sans-serif"
FIGURE_FONT = "Arial, Helvetica, sans-serif"
COPY_FONT = "Georgia, 'Times New Roman', serif"
PAGE_BACKGROUND = "#F5F5F4"
FIGURE_BACKGROUND = "#ffffff"
PANEL_BACKGROUND = "#FFFFFF"
PANEL_BORDER = "#E1E4E3"
TEXT_DARK = "#34383A"
TEXT_SOFT = "#636A6B"
LEFT_COLOR = "#365d77"
RIGHT_COLOR = "#a65d3f"
RAW_ALPHA = 0.38
SIDE_META = {
    "left": {"label": "Left", "color": LEFT_COLOR, "dash": "solid", "marker": "circle-open"},
    "right": {"label": "Right", "color": RIGHT_COLOR, "dash": "dash", "marker": "diamond-open"},
}
GRAPH_CONFIG = {
    "displaylogo": False,
    "responsive": True,
    "toImageButtonOptions": {
        "format": "svg",
        "filename": "kinoryx_figure",
        "height": 720,
        "width": 1200,
        "scale": 1,
    },
}


def decode_csv(contents: str) -> pd.DataFrame:
    try:
        _, encoded = contents.split(",", 1)
        raw = base64.b64decode(encoded, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise ValueError("Invalid upload") from exc
    if len(raw) > MAX_UPLOAD_BYTES:
        raise ValueError("Maximum CSV upload is 10 MiB")
    frame = pd.read_csv(io.BytesIO(raw))
    if len(frame) > MAX_UPLOAD_ROWS:
        raise ValueError(f"Maximum number of rows is {MAX_UPLOAD_ROWS:,}")
    return frame


def _visible_sides(view_mode: str, available_channels: Iterable[str]) -> list[str]:
    available_sides = [channel.split("_", 1)[0] for channel in available_channels]
    if view_mode == "left":
        return ["left"] if "left" in available_sides else available_sides
    if view_mode == "right":
        return ["right"] if "right" in available_sides else available_sides
    return available_sides


def build_figure(
    result: ExploratoryResult,
    *,
    view_mode: str = "bilateral",
    visible_layers: tuple[str, ...] = ("raw", "filtered", "candidates"),
) -> go.Figure:
    figure = go.Figure()
    time = result.raw["time_s"]
    sides = _visible_sides(view_mode, result.info.available_channels)
    for side in sides:
        channel = f"{side}_gyro_y_deg_s"
        if channel not in result.info.available_channels:
            continue
        meta = SIDE_META[side]
        if "raw" in visible_layers:
            figure.add_trace(
                go.Scatter(
                    x=time,
                    y=result.raw[channel],
                    mode="lines",
                    name=f"{meta['label']} raw",
                    opacity=RAW_ALPHA,
                    line={"color": meta["color"], "dash": "dot", "width": 1.1},
                )
            )
        if "filtered" in visible_layers:
            figure.add_trace(
                go.Scatter(
                    x=time,
                    y=result.filtered[channel],
                    mode="lines",
                    name=f"{meta['label']} filtered",
                    line={"color": meta["color"], "dash": meta["dash"], "width": 2.2},
                )
            )
        if "candidates" in visible_layers:
            peaks = [peak for peak in result.peaks if peak.side == side]
            figure.add_trace(
                go.Scatter(
                    x=[peak.time_s for peak in peaks],
                    y=[peak.amplitude_deg_s for peak in peaks],
                    mode="markers",
                    name=f"{meta['label']} candidate peaks",
                    marker={
                        "color": meta["color"],
                        "size": 8,
                        "symbol": meta["marker"],
                        "line": {"color": meta["color"], "width": 1.2},
                    },
                )
            )
    figure.update_layout(
        template=None,
        paper_bgcolor=FIGURE_BACKGROUND,
        plot_bgcolor=FIGURE_BACKGROUND,
        height=650,
        margin={"l": 72, "r": 26, "t": 74, "b": 72},
        hovermode="x unified",
        font={"family": FIGURE_FONT, "size": 13, "color": TEXT_DARK},
        legend={
            "orientation": "h",
            "x": 0.0,
            "y": 1.02,
            "xanchor": "left",
            "yanchor": "bottom",
            "bgcolor": "rgba(255,255,255,0)",
            "borderwidth": 0,
            "traceorder": "normal",
            "font": {"family": FIGURE_FONT, "size": 12, "color": TEXT_DARK},
        },
    )
    figure.update_xaxes(
        title_text="Time (s)",
        showline=True,
        mirror=True,
        linewidth=1.3,
        linecolor=TEXT_DARK,
        ticks="outside",
        tickwidth=1.0,
        ticklen=5,
        tickcolor=TEXT_DARK,
        showgrid=False,
        zeroline=False,
        title_font={"family": FIGURE_FONT, "size": 14, "color": TEXT_DARK},
        tickfont={"family": FIGURE_FONT, "size": 12, "color": TEXT_DARK},
    )
    figure.update_yaxes(
        title_text="Angular velocity (deg/s)",
        showline=True,
        mirror=True,
        linewidth=1.3,
        linecolor=TEXT_DARK,
        ticks="outside",
        tickwidth=1.0,
        ticklen=5,
        tickcolor=TEXT_DARK,
        showgrid=False,
        zeroline=True,
        zerolinewidth=1.0,
        zerolinecolor="#BDC2C3",
        title_font={"family": FIGURE_FONT, "size": 14, "color": TEXT_DARK},
        tickfont={"family": FIGURE_FONT, "size": 12, "color": TEXT_DARK},
    )
    if not figure.data:
        figure.add_annotation(
            text="No visible traces for the current layer and side selection.",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            font={"family": FIGURE_FONT, "size": 14, "color": TEXT_SOFT},
        )
    return figure


def metric_card(label: str, value: str, detail: str = "") -> html.Div:
    children = [html.Div(label, className="metric-label"), html.Div(value, className="metric-value")]
    if detail:
        children.append(html.Div(detail, className="metric-detail"))
    return html.Div(children, className="metric-card")


def build_peak_table(result: ExploratoryResult, limit: int = 12) -> html.Table:
    header = html.Thead(
        html.Tr(
            [
                html.Th("Side"),
                html.Th("Time (s)"),
                html.Th("Amplitude (deg/s)"),
                html.Th("Sample"),
            ]
        )
    )
    body_rows = []
    for peak in result.peaks[:limit]:
        body_rows.append(
            html.Tr(
                [
                    html.Td(peak.side.capitalize()),
                    html.Td(f"{peak.time_s:.3f}"),
                    html.Td(f"{peak.amplitude_deg_s:.2f}"),
                    html.Td(str(peak.sample_index)),
                ]
            )
        )
    if not body_rows:
        body_rows.append(html.Tr([html.Td("No candidates available for this view.", colSpan=4)]))
    return html.Table([header, html.Tbody(body_rows)], className="scientific-table")


def build_caption(
    result: ExploratoryResult,
    source_label: str,
    view_mode: str,
    visible_layers: tuple[str, ...],
) -> html.Div:
    panel_descriptor = {
        "bilateral": "bilateral left-right comparison",
        "left": "left-foot focused view",
        "right": "right-foot focused view",
    }[view_mode]
    layer_phrase = ", ".join(layer.replace("candidates", "candidate peaks") for layer in visible_layers)
    warning_copy = (
        " Sampling irregularity warning: " + "; ".join(result.info.warnings)
        if result.info.warnings
        else ""
    )
    return html.Div(
        [
            html.Div("Figure note", className="caption-title"),
            html.P(
                [
                    html.Strong("Exploratory angular-velocity traces from KINORYX. "),
                    f"This {panel_descriptor} presents {layer_phrase} for {source_label.lower()} data. ",
                    "Signals were processed by the current exploratory pipeline and are shown for research inspection only. ",
                    f"The analysis detected {len(result.peaks)} unvalidated peak candidates; the table shows up to 12. ",
                    "These candidates are not equivalent to heel strikes, toe-offs, stance phases, or validated gait events.",
                    warning_copy,
                ],
                className="caption-copy",
            ),
        ],
        className="caption-block",
    )


def create_app() -> Dash:
    app = Dash(__name__, title="KINORYX | Biomechanics Dashboard")
    app.layout = html.Main(
        [
            html.Section(
                [
                    html.Div("KINORYX", className="brand-kicker"),
                    html.H1("Biomechanics Dashboard", className="page-title"),
                    html.P(
                        "Local-first workspace for article-ready signal inspection, figure export, and transparent exploratory reporting.",
                        className="page-subtitle",
                    ),
                    html.P(
                        "The visual system follows common figure conventions used by major scientific publishers: restrained typography, legible axes, accessible contrast, and concise legend-style narrative.",
                        className="page-intro",
                    ),
                ],
                className="hero-panel",
            ),
            html.Section(
                [
                    html.Div(
                        [
                            html.H2("Input", className="section-title"),
                            html.P(
                                "Load a canonical CSV or leave the default synthetic demonstration dataset in place.",
                                className="section-copy",
                            ),
                            dcc.Upload(
                                id="csv-upload",
                                children=html.Div(
                                    [
                                        html.Span("Drop a CSV here or click to select.", className="upload-title"),
                                        html.Span(
                                            " Accepted input is local, never uploaded to a remote service.",
                                            className="upload-note",
                                        ),
                                    ]
                                ),
                                multiple=False,
                                accept=".csv,text/csv",
                                className="upload-box",
                            ),
                        ],
                        className="workspace-card input-card",
                    ),
                    html.Div(
                        [
                            html.H2("Display controls", className="section-title"),
                            html.Div(
                                [
                                    html.Div("Comparison layout", className="control-label"),
                                    dcc.RadioItems(
                                        id="view-mode",
                                        options=[
                                            {"label": "Bilateral", "value": "bilateral"},
                                            {"label": "Left only", "value": "left"},
                                            {"label": "Right only", "value": "right"},
                                        ],
                                        value="bilateral",
                                        className="radio-grid",
                                        inputClassName="radio-input",
                                        labelClassName="radio-label",
                                    ),
                                ],
                                className="control-block",
                            ),
                            html.Div(
                                [
                                    html.Div("Visible figure layers", className="control-label"),
                                    dcc.Checklist(
                                        id="layer-selection",
                                        options=[
                                            {"label": "Raw", "value": "raw"},
                                            {"label": "Filtered", "value": "filtered"},
                                            {"label": "Candidate peaks", "value": "candidates"},
                                        ],
                                        value=["raw", "filtered", "candidates"],
                                        className="check-grid",
                                        inputClassName="check-input",
                                        labelClassName="check-label",
                                    ),
                                ],
                                className="control-block",
                            ),
                            html.Div(
                                "Use the Plotly export control to download an SVG figure for manuscript assembly.",
                                className="export-note",
                            ),
                        ],
                        className="workspace-card controls-card",
                    ),
                ],
                className="two-column-grid",
            ),
            html.Section(id="metrics-row", className="metrics-grid"),
            html.Section(
                [
                    html.Div(
                        [
                            html.H2("Signal figure", className="section-title"),
                            html.P(
                                "Axes, units, line styles, and text are intentionally restrained to support direct reuse in scientific figures.",
                                className="section-copy compact-copy",
                            ),
                            html.Div(id="status-banner", className="status-banner", role="status"),
                            dcc.Loading(
                                dcc.Graph(id="signal-graph", config=GRAPH_CONFIG, className="signal-graph")
                            ),
                        ],
                        className="workspace-card figure-card",
                    ),
                    html.Div(
                        [
                            html.H2("Legend-style context", className="section-title"),
                            html.Div(id="figure-caption"),
                            html.H2("Candidate peak table", className="section-title table-heading"),
                            html.Div(id="peak-table-container"),
                            html.Div(id="warning-box", className="warning-box"),
                        ],
                        className="workspace-card side-card",
                    ),
                ],
                className="main-grid",
            ),
            html.Footer(
                [
                    html.P(
                        "Pre-alpha research software. Unvalidated peak candidates are shown for exploratory inspection only; they are not clinical endpoints, gait phases, or diagnostic outputs.",
                        className="footer-copy",
                    )
                ],
                className="page-footer",
            ),
        ],
        className="app-shell",
    )

    @app.callback(
        Output("signal-graph", "figure"),
        Output("status-banner", "children"),
        Output("metrics-row", "children"),
        Output("peak-table-container", "children"),
        Output("figure-caption", "children"),
        Output("warning-box", "children"),
        Input("csv-upload", "contents"),
        Input("view-mode", "value"),
        Input("layer-selection", "value"),
    )
    def update_dashboard(contents: str | None, view_mode: str, layer_selection: list[str]):
        try:
            frame = generate_demo_dataset() if contents is None else decode_csv(contents)
            source_label = "Synthetic demo" if contents is None else "Local CSV"
            result = analyze_exploratory(frame)
            selected_layers = tuple(layer_selection) if layer_selection else tuple()
            figure = build_figure(result, view_mode=view_mode, visible_layers=selected_layers)
            duration_s = result.raw["time_s"].iloc[-1] - result.raw["time_s"].iloc[0]
            metrics = [
                metric_card("Data source", source_label, "Deterministic example" if contents is None else "Researcher-supplied file"),
                metric_card("Duration", f"{duration_s:.2f} s", "Time span represented"),
                metric_card("Sampling rate", f"{result.info.sampling_hz:.1f} Hz", "Estimated from time_s"),
                metric_card("Channels", str(len(result.info.available_channels)), ", ".join(result.info.available_channels)),
                metric_card("Candidate peaks", str(len(result.peaks)), "Exploratory, not validated events"),
            ]
            status = (
                f"{source_label} loaded. Use the export control to save the current figure as SVG for manuscript composition."
            )
            caption = build_caption(result, source_label, view_mode, selected_layers)
            warnings = result.info.warnings or [
                "No sampling or contract warnings detected for the current file."
            ]
            warning_children = [
                html.Div("Methodological notes", className="warning-title"),
                html.Ul([html.Li(note) for note in warnings], className="warning-list"),
            ]
            return figure, status, metrics, build_peak_table(result), caption, warning_children
        except (ValueError, pd.errors.ParserError, pd.errors.EmptyDataError) as exc:
            empty = go.Figure()
            empty.update_layout(
                paper_bgcolor=FIGURE_BACKGROUND,
                plot_bgcolor=FIGURE_BACKGROUND,
                font={"family": FIGURE_FONT, "size": 13, "color": TEXT_DARK},
                margin={"l": 72, "r": 26, "t": 74, "b": 72},
            )
            message = f"Input rejected: {exc}"
            fallback_metrics = [metric_card("Status", "Rejected", message)]
            return empty, message, fallback_metrics, html.Div(), html.Div(), html.Div()

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=8050, debug=False)
