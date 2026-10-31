"""Synthetic examples only. Real human recordings must stay out of git."""

from pathlib import Path

import pytest

from kinoryx.io.xsens_emg import export_mvne_csv, read_mvne


def _write(tmp_path: Path, samples: str, second_rate: int = 1000) -> Path:
    path = tmp_path / "test.mvne"
    path.write_text(
        '<mvnext><mvn ts="123"/><channels count="2">'
        '<channel id="0" name="Left" source="Synthetic" sourceChannel="1" frameRate="1000"/>'
        f'<channel id="1" name="Right" source="Synthetic" sourceChannel="2" frameRate="{second_rate}"/>'
        f'</channels><data>{samples}</data></mvnext>',
        encoding="utf-8",
    )
    return path


def test_read_export_interleaved_samples(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        '<sample id="0" value="1"/><sample id="1" value="-3"/>'
        '<sample id="0" value="2.5"/><sample id="1" value="4"/>',
    )
    recording = read_mvne(path)
    assert recording.sample_count == 2
    assert recording.sampling_hz == 1000
    assert recording.sample_span_s == 0.001
    assert recording.samples == ((1.0, 2.5), (-3.0, 4.0))
    output, metadata = export_mvne_csv(path, tmp_path / "data_local" / "emg.csv")
    assert output.read_text().splitlines() == [
        "time_s,emg_ch0_raw,emg_ch1_raw",
        "0.0,1.0,-3.0",
        "0.001,2.5,4.0",
    ]
    assert '"units": "unspecified in MVNE header; raw values preserved"' in metadata.read_text()


@pytest.mark.parametrize("samples", [
    '<sample id="0" value="1"/>',
    '<sample id="0" value="1"/><sample id="1" value="nan"/>',
    '<sample id="0" value="1"/><sample id="3" value="2"/>',
])
def test_invalid_samples_are_rejected(tmp_path: Path, samples: str) -> None:
    with pytest.raises(ValueError):
        read_mvne(_write(tmp_path, samples))


def test_mixed_rates_are_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Mixed"):
        read_mvne(_write(tmp_path, "", second_rate=2000))
