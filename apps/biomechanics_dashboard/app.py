"""Local Biomechanics Dashboard. Run with python apps/biomechanics_dashboard/app.py."""
import base64
import binascii
import io

import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html

from kinoryx.demo.synthetic import generate_demo_dataset
from kinoryx.pipeline import analyze_exploratory

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
COLORS = {"left": "#15927a", "right": "#dc7961"}


def build_figure(result):
    figure = go.Figure()
    for channel in result.info.available_channels:
        side = channel.split("_", 1)[0]
        figure.add_trace(go.Scatter(
            x=result.raw["time_s"], y=result.raw[channel], mode="lines",
            name=f"{side} raw", opacity=0.35, line={"color": COLORS[side], "dash": "dot"},
        ))
        figure.add_trace(go.Scatter(
            x=result.filtered["time_s"], y=result.filtered[channel], mode="lines",
            name=f"{side} filtered", line={"color": COLORS[side], "width": 2.5},
        ))
        peaks = [p for p in result.peaks if p.side == side]
        figure.add_trace(go.Scatter(
            x=[p.time_s for p in peaks], y=[p.amplitude_deg_s for p in peaks],
            mode="markers", name=f"{side} candidate peaks",
            marker={"color": COLORS[side], "size": 9, "symbol": "circle-open"},
        ))
    figure.update_layout(
        template="plotly_white", xaxis_title="Time (s)",
        yaxis_title="Angular velocity (deg/s)", height=490,
        hovermode="x unified", margin={"l": 65, "r": 25, "t": 20, "b": 70},
    )
    return figure


def decode_csv(contents):
    try:
        _, encoded = contents.split(",", 1)
        raw = base64.b64decode(encoded, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise ValueError("Invalid upload") from exc
    if len(raw) > MAX_UPLOAD_BYTES:
        raise ValueError("Maximum CSV upload is 10 MiB")
    frame = pd.read_csv(io.BytesIO(raw))
    if len(frame) > 200_000:
        raise ValueError("Maximum number of rows is 200,000")
    return frame


def create_app():
    app = Dash(__name__, title="KINORYX | Biomechanics Dashboard")
    app.layout = html.Main([
        html.H1("KINORYX"),
        html.P("BIOMECHANICS DASHBOARD | Human Motion Intelligence"),
        html.H2("Explore human movement signals"),
        html.P("Research pre-alpha. Peak candidates are NOT validated gait events."),
        dcc.Upload(
            id="csv-upload",
            children=html.Div("Drop a canonical CSV here, or click to select. Synthetic demo loads by default."),
            multiple=False, accept=".csv,text/csv",
            style={"padding": "24px", "border": "2px dashed #15927a", "cursor": "pointer"},
        ),
        html.Div(id="summary", role="status"),
        dcc.Loading(dcc.Graph(id="signal-graph", config={"displaylogo": False})),
        html.Small("Not a medical device. Do not upload identifiable participant data."),
    ], style={
        "maxWidth": "1120px", "padding": "40px 24px", "margin": "auto",
        "fontFamily": "Arial, sans-serif", "background": "#fffdfa",
    })

    @app.callback(Output("signal-graph", "figure"), Output("summary", "children"),
                  Input("csv-upload", "contents"))
    def update(contents):
        try:
            frame = generate_demo_dataset() if contents is None else decode_csv(contents)
            result = analyze_exploratory(frame)
            summary = (
                f"{'SYNTHETIC DEMO' if contents is None else 'Local CSV'} | "
                f"{result.info.rows} rows | {result.info.sampling_hz:.1f} Hz | "
                f"{len(result.peaks)} UNVALIDATED peak candidates. "
                + " ".join(result.info.warnings)
            )
            return build_figure(result), summary
        except (ValueError, pd.errors.ParserError, pd.errors.EmptyDataError) as exc:
            return go.Figure(), f"Input rejected: {exc}"
    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=8050, debug=False)
