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
        "height": 1000,
        "width": 1500,
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
    figure = make_subplots(
        rows=len(visible),
        cols=2 if comparative else 1,
        shared_xaxes="all",
        horizontal_spacing=0.065,
        vertical_spacing=0.11 if len(visible) > 1 else 0,
        subplot_titles=[
            label
            for ch, _ in visible
            for label in (
                [f"{ch.name} | Original", f"{ch.name} | {mode.upper()}"]
                if comparative else [f"{ch.name} | Original"]
            )
        ],
    )
    t = np.arange(first, last) / fs
    for row, (ch, raw) in enumerate(visible, start=1):
        figure.add_trace(
            go.Scattergl(
                x=t, y=raw[first:last], mode="lines",
                line={"color": RAW_COLOR, "width": 1},
                name=f"{ch.name}, original",
                hovertemplate="t=%{x:.4f} s<br>Original=%{y:.3f} (unidades desconocidas)<extra></extra>",
            ), row=row, col=1,
        )
        if comparative:
            transformed = preview_transform(raw, fs, mode)
            figure.add_trace(
                go.Scattergl(
                    x=t, y=transformed[first:last], mode="lines",
                    line={"color": PREVIEW_COLOR, "width": 1.3},
                    name=f"{ch.name}, {mode}",
                    hovertemplate="t=%{x:.4f} s<br>Preview=%{y:.3f} (escala original)<extra></extra>",
                ), row=row, col=2,
            )
    figure.update_layout(
        template="plotly_white",
        height=max(380, len(visible) * (300 if comparative else 240)),
        margin={"l": 76, "r": 25, "t": 72, "b": 67},
        showlegend=False,
        hovermode="x",
        font={"family": "Arial, sans-serif", "color": "#34383A", "size": 12},
        paper_bgcolor="#fff",
        plot_bgcolor="#fff",
    )
    figure.update_yaxes(title_text="Valores originales (unidad no confirmada)", zeroline=True)
    figure.update_xaxes(title_text="Tiempo relativo (s)", showgrid=True, gridcolor="#edf0f0")
    return figure


def build_layout() -> html.Main:
    try:
        recording = load_source()
    except (OSError, ValueError) as exc:
        return html.Main(
            [
                html.H1("KINORYX | Laboratorio EMG"),
                html.P(f"Datos no disponibles: {exc}"),
                html.A("Volver al dashboard", href="/"),
            ],
            className="app-shell lab-shell",
        )
    channel_options = [{"label": "Los cuatro canales", "value": "all"}]
    channel_options.extend(
        {"label": f"{ch.id} | {ch.name}", "value": str(ch.id)}
        for ch in recording.channels
    )
    return html.Main(
        [
            html.Header(
                [
                    html.A("← Volver al dashboard de marcha", href="/", className="lab-back"),
                    html.Div("KINORYX / RESEARCH ONLY", className="brand-kicker"),
                    html.H1("Laboratorio EMG", className="page-title"),
                    html.P(
                        "Visualización interactiva del archivo Cometa original. "
                        "Antes de transformar una señal, observa cómo fue registrada.",
                        className="page-subtitle",
                    ),
                    html.P(
                        "Experimental · Solo localhost · No modifica las grabaciones · "
                        "No se incorpora a main",
                        className="lab-caution",
                    ),
                ],
                className="hero-panel",
            ),
            html.Section(
                [
                    html.Div(
                        [
                            html.H2("Registro", className="section-title"),
                            html.P(SOURCE.name, className="lab-source"),
                            html.Div(
                                [
                                    html.Div([html.Small("Canales"), html.Strong(str(len(recording.channels)))]),
                                    html.Div([html.Small("Muestreo"), html.Strong(f"{recording.sampling_hz:g} Hz")]),
                                    html.Div([html.Small("Muestras / canal"), html.Strong(f"{recording.sample_count:,}")]),
                                    html.Div([html.Small("Duración aprox."), html.Strong(f"{recording.sample_span_s:.3f} s")]),
                                ], className="lab-metrics",
                            ),
                            html.P(
                                "Las etiquetas musculares vienen del XML; "
                                "las unidades, calibración y sincronización siguen sin verificarse.",
                                className="lab-help",
                            ),
                        ],
                        className="lab-source-pane",
                    ),
                    html.Div(
                        [
                            html.H2("Explorar", className="section-title"),
                            html.Label("Canal", htmlFor="lab-channel", className="control-label"),
                            dcc.Dropdown(
                                id="lab-channel", options=channel_options, value="all",
                                clearable=False,
                            ),
                            html.Label("Inicio del intervalo (s)", htmlFor="lab-start", className="control-label"),
                            dcc.Slider(
                                id="lab-start", min=0, max=8, step=0.1, value=0,
                                marks={0: "0", 2: "2", 4: "4", 6: "6", 8: "8"},
                                tooltip={"placement": "bottom", "always_visible": False},
                            ),
                            html.Label("Duración del intervalo", htmlFor="lab-window", className="control-label"),
                            dcc.RadioItems(
                                id="lab-window",
                                options=[
                                    {"label": "0.25 s", "value": 0.25},
                                    {"label": "1 s", "value": 1.0},
                                    {"label": "2 s", "value": 2.0},
                                    {"label": "Completa", "value": 8.3},
                                ],
                                value=8.3, inline=True,
                                className="lab-inline",
                            ),
                            html.Label("Vista de procesamiento", htmlFor="lab-transform", className="control-label"),
                            dcc.RadioItems(
                                id="lab-transform",
                                options=[
                                    {"label": "Original", "value": "raw"},
                                    {"label": "Comparar filtro 20 a 450 Hz", "value": "bandpass"},
                                    {"label": "Comparar RMS 250 ms", "value": "rms"},
                                ],
                                value="raw", className="lab-inline",
                            ),
                            html.P(
                                "Los filtros son vistas experimentales y no un método "
                                "validado para este registro. Siempre se conserva "
                                "una gráfica original junto al resultado.",
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
                    html.H2("Señales y comparación", className="section-title"),
                    html.Div(id="lab-status", className="status-banner", role="status"),
                    dcc.Loading(
                        dcc.Graph(id="lab-figure", config=CONFIG, className="lab-figure"),
                        type="circle",
                    ),
                    html.P(
                        "Eje X: segundos relativos. Eje Y: valores registrados sin unidad "
                        "confirmada. La comparación no equivale a activación muscular, "
                        "normalización ni diagnóstico.",
                        className="lab-help",
                    ),
                ], className="lab-plot-section",
            ),
            html.Footer(
                [
                    html.P(
                        "Laboratorio temporal para decidir qué investigar y qué validar "
                        "antes de modificar la aplicación principal."
                    ),
                ], className="page-footer",
            ),
        ], className="app-shell lab-shell",
    )


def mount_research_lab(flask_server) -> Dash:
    """Share the existing localhost server, without replacing the gait dashboard."""
    lab = Dash(
        "kinoryx_emg_research",
        server=flask_server,
        url_base_pathname="/lab/",
        assets_folder=str(ASSETS),
        title="KINORYX | Laboratorio EMG",
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
            label = "Solo señal original" if mode == "raw" else (
                f"Original frente a {mode}, comparación experimental"
            )
            return figure, f"{label}. El archivo original no se modifica."
        except (ValueError, OSError) as exc:
            return go.Figure(), f"No se pudo mostrar la vista: {exc}"

    return lab
