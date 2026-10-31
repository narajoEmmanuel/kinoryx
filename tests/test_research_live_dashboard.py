"""Research-only visualisation tests use synthetic samples, not participant data."""
import importlib.util
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("dash")
pytest.importorskip("plotly")

from kinoryx.io.xsens_emg import EmgChannel, EmgRecording
from kinoryx.research_lab import make_emg_figure, preview_transform
from kinoryx.plot_layout import plan_subplot_layout, wrap_plot_title


def _synthetic() -> EmgRecording:
    fs = 2000.0
    times = np.arange(2000) / fs
    left = np.sin(2 * np.pi * 80 * times)
    right = np.sin(2 * np.pi * 120 * times)
    return EmgRecording(
        channels=(
            EmgChannel(0, "Synthetic left", "test", "1", fs),
            EmgChannel(1, "Synthetic right", "test", "2", fs),
        ),
        samples=(tuple(left), tuple(right)),
        sample_count=2000,
        sampling_hz=fs,
        source_timestamp=None,
    )


def test_original_is_always_present_in_comparison():
    sample = _synthetic()
    raw = make_emg_figure(sample, "all", 0, 1, "raw")
    assert len(raw.data) == 2
    assert all("raw EMG" in trace.name for trace in raw.data)
    compared = make_emg_figure(sample, "all", 0.1, 0.25, "rms")
    assert len(compared.data) == 4
    assert sum("raw EMG" in trace.name for trace in compared.data) == 2
    assert all(len(trace.x) == 500 for trace in compared.data)


def test_synthetic_filter_changes_preview_without_changing_source():
    sample = _synthetic()
    original = np.asarray(sample.samples[0])
    before = original.copy()
    filtered = preview_transform(original, sample.sampling_hz, "bandpass")
    envelope = preview_transform(original, sample.sampling_hz, "rms")
    assert filtered.shape == original.shape
    assert envelope.shape == original.shape
    assert np.all(envelope >= 0)
    assert np.array_equal(original, before)


@pytest.mark.parametrize("mode", ["nonsense", "filtered"])
def test_unknown_preview_rejected(mode):
    with pytest.raises(ValueError, match="Unknown"):
        preview_transform(np.arange(1000, dtype=float), 2000, mode)


def test_invalid_channel_or_window_rejected():
    source = _synthetic()
    for ch, start, window in [
        ("3", 0, 1),
        ("all", -0.1, 1),
        ("all", 0, 0),
        ("all", 100, 1),
    ]:
        with pytest.raises(ValueError):
            make_emg_figure(source, ch, start, window, "raw")


def test_dashboard_serves_lab_on_same_localhost_server():
    file_path = Path(__file__).resolve().parents[1] / "apps/biomechanics_dashboard/app.py"
    spec = importlib.util.spec_from_file_location("kinoryx_visual_test_app", file_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    dashboard = module.create_app()
    client = dashboard.server.test_client()
    main_response = client.get("/")
    lab_response = client.get("/lab/")
    assert main_response.status_code == 200
    assert lab_response.status_code == 200
    assert b"Biomechanics Dashboard" in main_response.data
    assert b"EMG Research Laboratory" in lab_response.data
    assert b"Biomechanics Dashboard" not in lab_response.data


def test_emg_chart_has_one_shared_y_axis_label():
    recording = _synthetic()
    figure = make_emg_figure(recording, "all", 0, 1, "raw")
    assert all(axis.title.text is None for axis in (figure.layout.yaxis, figure.layout.yaxis2))
    captions = [note for note in figure.layout.annotations
                if "EMG amplitude (unit not established)" in note.text]
    assert len(captions) == 1
    assert figure.layout.height > 460


def test_plot_layout_expands_when_scientific_titles_are_long():
    short = plan_subplot_layout(["Right rectus femoris | Raw EMG"] * 4, cols=1)
    long_title = (
        "Right rectus femoris | Raw EMG | an unusually detailed scientific "
        "annotation covering an extended multi-line acquisition description "
        "that must never collide with another panel or axis label"
    )
    longer = plan_subplot_layout([long_title] * 4, cols=1)
    assert longer.height > short.height
    assert longer.vertical_spacing > short.vertical_spacing
    assert "<br>" in longer.titles[0]
    escaped, lines = wrap_plot_title("<test> & signal", 10)
    assert "&lt;" in escaped and "&amp;" in escaped
    assert lines >= 2



def test_local_server_enables_hot_reload(monkeypatch):
    """Ensure local development can keep the same server process workflow."""
    file_path = Path(__file__).resolve().parents[1] / "apps/biomechanics_dashboard/app.py"
    spec = importlib.util.spec_from_file_location("kinoryx_dev_reload_test_app", file_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    class StubApp:
        def __init__(self):
            self.kwargs = None

        def run(self, **kwargs):
            self.kwargs = kwargs

    app = StubApp()
    monkeypatch.setattr(module, "create_app", lambda: app)
    module.run_local_server()
    assert app.kwargs == {
        "host": "127.0.0.1",
        "port": 8050,
        "debug": True,
        "use_reloader": True,
        "dev_tools_hot_reload": True,
    }
