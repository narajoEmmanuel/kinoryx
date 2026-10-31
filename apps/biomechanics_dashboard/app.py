
"""KINORYX Biomechanics Dashboard, an independent local scientific workspace.

Run from the repository root:
    python apps/biomechanics_dashboard/app.py
"""

import base64
import binascii
import io
import math
from typing import Iterable

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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
        "height": 900,
        "width": 1500,
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
    panel_layout: str = "grid",
) -> go.Figure:
    """Separate raw and filtered angular velocity by side, with linked time axes."""
    if panel_layout not in ("grid", "stack"):
        raise ValueError("Unknown panel layout")
    layers = set(visible_layers)
    sides = _visible_sides(view_mode, result.info.available_channels)
    panels = []
    for stage in ("raw", "filtered"):
        if stage == "raw" and "raw" not in layers:
            continue
        if stage == "filtered" and not {"filtered", "candidates"}.intersection(layers):
            continue
        for side in sides:
            channel = f"{side}_gyro_y_deg_s"
            if channel in result.info.available_channels:
                panels.append((side, stage, channel))

    cols = 2 if panel_layout == "grid" and len(panels) > 1 else 1
    rows = max(1, math.ceil(len(panels) / cols))
    figure = make_subplots(
        rows=rows,
        cols=cols,
        shared_xaxes="all",
        subplot_titles=[f"{SIDE_META[s]['label']} · {stage.title()}" for s, stage, _ in panels],
        vertical_spacing=0.14 if rows > 1 else 0.0,
        horizontal_spacing=0.11 if cols > 1 else 0.0,
    )
    time = result.raw["time_s"]
    for i, (side, stage, channel) in enumerate(panels):
        row, col = divmod(i, cols)
        row += 1
        col += 1
        meta = SIDE_META[side]
        if stage == "raw":
            figure.add_trace(
                go.Scatter(
                    x=time, y=result.raw[channel], mode="lines",
                    name=f"{meta['label']} raw",
                    line={"color": meta["color"], "width": 1.4},
                    showlegend=False,
                    hovertemplate="Time %{x:.3f} s<br>Raw %{y:.2f} deg/s<extra></extra>",
                ),
                row=row, col=col,
            )
        else:
            if "filtered" in layers:
                figure.add_trace(
                    go.Scatter(
                        x=time, y=result.filtered[channel], mode="lines",
                        name=f"{meta['label']} filtered",
                        line={"color": meta["color"], "width": 2},
                        showlegend=False,
                        hovertemplate="Time %{x:.3f} s<br>Filtered %{y:.2f} deg/s<extra></extra>",
                    ),
                    row=row, col=col,
                )
            if "candidates" in layers:
                peaks = [p for p in result.peaks if p.side == side]
                figure.add_trace(
                    go.Scatter(
                        x=[p.time_s for p in peaks],
                        y=[p.amplitude_deg_s for p in peaks],
                        mode="markers",
                        name=f"{meta['label']} candidate peaks",
                        marker={
                            "color": meta["color"], "size": 7,
                            "symbol": meta["marker"],
                            "line": {"color": meta["color"], "width": 1},
                        },
                        showlegend=False,
                        hovertemplate="Time %{x:.3f} s<br>%{y:.2f} deg/s<extra>Unvalidated candidate</extra>",
                    ),
                    row=row, col=col,
                )
    figure.update_layout(
        template=None,
        paper_bgcolor=FIGURE_BACKGROUND,
        plot_bgcolor=FIGURE_BACKGROUND,
        height=405 if len(panels) < 3 else (750 if panel_layout == "grid" else 1040),
        margin={"l": 78, "r": 25, "t": 68, "b": 64},
        hovermode="closest",
        showlegend=False,
        font={"family": FIGURE_FONT, "size": 12, "color": TEXT_DARK},
    )
    figure.update_annotations(font={"family": FIGURE_FONT, "size": 14, "color": TEXT_DARK})
    figure.update_xaxes(
        showline=True, linewidth=1, linecolor=TEXT_DARK, ticks="outside",
        tickwidth=1, ticklen=4, tickcolor=TEXT_DARK,
        showgrid=False, zeroline=False,
        tickfont={"family": FIGURE_FONT, "size": 11, "color": TEXT_DARK},
    )
    figure.update_yaxes(
        title_text="Angular velocity (deg/s)",
        showline=True, linewidth=1, linecolor=TEXT_DARK, ticks="outside",
        tickwidth=1, ticklen=4, tickcolor=TEXT_DARK,
        showgrid=False, zeroline=True, zerolinecolor="#BDC2C3",
        title_font={"family": FIGURE_FONT, "size": 11, "color": TEXT_DARK},
        tickfont={"family": FIGURE_FONT, "size": 11, "color": TEXT_DARK},
    )
    for col in range(1, cols + 1):
        figure.update_xaxes(title_text="Time (s)", row=rows, col=col)
    if not panels:
        figure.add_annotation(
            text="Select a signal layer.", x=0.5, y=0.5, xref="paper", yref="paper",
            showarrow=False, font={"family": FIGURE_FONT, "size": 14, "color": TEXT_SOFT},
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
        "bilateral": "left and right channels",
        "left": "left channel",
        "right": "right channel",
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
                    html.Strong("Exploratory angular velocity. "),
                    f"{source_label}: {panel_descriptor}; layers: {layer_phrase or 'none'}. ",
                    f"{len(result.peaks)} unvalidated peak candidates (up to 12 shown). ",
                    "Candidates do not represent confirmed initial contacts, toe-offs or gait phases.",
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
                        "Explore movement signals. Export figures for research.",
                        className="page-subtitle",
                    ),
                    html.A(
                        "Abrir laboratorio EMG experimental",
                        href="/lab/",
                        className="lab-nav-link",
                    ),
                ],
                className="hero-panel",
            ),
            html.Section(
                [
                    html.Div(
                        [
                            html.H2("Dataset", className="section-title"),
                            dcc.Upload(
                                id="csv-upload",
                                children=html.Div(
                                    [
                                        html.Span("Import CSV", className="upload-title"),
                                        html.Span(
                                            "Or explore the synthetic example · Local processing",
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
                            html.H2("View", className="section-title"),
                            html.Div(
                                [
                                    html.Div("Side", className="control-label"),
                                    dcc.RadioItems(
                                        id="view-mode",
                                        options=[
                                            {"label": "Bilateral", "value": "bilateral"},
                                            {"label": "Left", "value": "left"},
                                            {"label": "Right", "value": "right"},
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
                                    html.Div("Panels", className="control-label"),
                                    dcc.RadioItems(
                                        id="panel-layout",
                                        options=[
                                            {"label": "2 columns", "value": "grid"},
                                            {"label": "Stacked", "value": "stack"},
                                        ],
                                        value="grid",
                                        className="radio-grid",
                                        inputClassName="radio-input",
                                        labelClassName="radio-label",
                                    ),
                                ],
                                className="control-block",
                            ),
                            html.Div(
                                [
                                    html.Div("Layers", className="control-label"),
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
                            html.H2("Signal explorer", className="section-title"),
                            html.P(
                                "Linked timelines · Zoom any panel · Export SVG",
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
                            html.Div(
                                [
                                    html.H2("Figure legend", className="section-title"),
                                    html.Div(id="figure-caption"),
                                    html.Div(id="warning-box", className="warning-box"),
                                ],
                                className="legend-column",
                            ),
                            html.Div(
                                [
                                    html.H2("Peak candidates", className="section-title table-heading"),
                                    html.Div(id="peak-table-container"),
                                ],
                                className="candidate-column",
                            ),
                        ],
                        className="workspace-card side-card",
                    ),
                ],
                className="main-grid",
            ),
            html.Footer(
                [
                    html.P(
                        "Research prototype · Exploratory peaks are not validated gait events or clinical measurements.",
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
        Input("panel-layout", "value"),
    )
    def update_dashboard(
        contents: str | None, view_mode: str, layer_selection: list[str], panel_layout: str
    ):
        try:
            frame = generate_demo_dataset() if contents is None else decode_csv(contents)
            source_label = "Synthetic demo" if contents is None else "Local CSV"
            result = analyze_exploratory(frame)
            selected_layers = tuple(layer_selection) if layer_selection else tuple()
            figure = build_figure(
                result, view_mode=view_mode, visible_layers=selected_layers, panel_layout=panel_layout
            )
            duration_s = result.raw["time_s"].iloc[-1] - result.raw["time_s"].iloc[0]
            metrics = [
                metric_card("Dataset", source_label),
                metric_card("Duration", f"{duration_s:.2f} s"),
                metric_card("Estimated frequency", f"{result.info.sampling_hz:.1f} Hz"),
                metric_card("Channels", str(len(result.info.available_channels))),
                metric_card("Unvalidated peaks", str(len(result.peaks))),
            ]
            status = f"{source_label} · {result.info.rows:,} samples"
            caption = build_caption(result, source_label, view_mode, selected_layers)
            warning_children = [
                html.Div("Data quality", className="warning-title"),
                html.Ul([html.Li(note) for note in result.info.warnings], className="warning-list"),
            ] if result.info.warnings else []
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

    # This dashboard and the optional EMG laboratory share one local Flask server.
    # These research-only files exist only in the non-merge study branch.
    from kinoryx.research_lab import mount_research_lab

    mount_research_lab(app.server)
    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=8050, debug=False)
