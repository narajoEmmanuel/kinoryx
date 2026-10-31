# Experiment 01, First EMG Burst, 1.000 to 2.000 s

**Status:** raw signal inspection, exploratory and descriptive only.  
**Dataset:** `research/source_data/EMG2_Squats-200714130240.mvne`  
**Source SHA-256:** `17bf9261d73db6b3d94b36b5f334555c3cad6e87ecbce17f422cd62891b9101f`  
**Acquisition metadata:** four Cometa channels, 2000 Hz, 16527 samples per channel.  
**Interval:** sample indices `[2000:4000]` in each channel (2000 samples, 1.000 s inclusive to 2.000 s exclusive).  
**Methods:** parse original MVNE XML and calculate descriptive minimum, maximum, mean, population standard deviation and 95th percentile of absolute values. No digital filtering, rectification, RMS transform, normalization or synchronization.

## How to view in local KINORYX

Open `http://127.0.0.1:8050/lab/`. Configure **EMG channel = All four EMG channels**, **Window start (s) = 1.0**, **Window duration = 1 s** and **Signal view = Raw EMG**. Review the four individual subplots; zoom the x-axis for detailed inspection as needed. No server restart is needed to adjust controls.

## Direct raw signal measurements

| XML channel ID | Channel label | Minimum | Maximum | Peak-to-peak | Mean | Std. dev. | 95th percentile of absolute samples | Time of max absolute sample (s) |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | Rectus Femoris Right | -1705.692 | +1542.041 | 3247.733 | +1.155 | 360.245 | 803.257 | 1.3890 |
| 1 | Biceps Femoris Right | -728.522 | +642.618 | 1371.140 | -1.959 | 75.655 | 117.556 | 1.9755 |
| 2 | Rectus Femoris Left | -1876.996 | +2454.153 | 4331.149 | -2.046 | 418.802 | 914.061 | 1.5120 |
| 3 | Biceps Femoris Left | -293.463 | +304.843 | 598.306 | -2.195 | 64.840 | 133.045 | 1.8540 |

**Units:** unverified source scale. Standard deviation is computed with population convention `ddof=0`; percentile is computed with NumPy's default linear interpolation. These statistics describe numbers recorded by the instrument, not muscle force or calibrated EMG in microvolts. Only the original 2000 raw samples per channel are used.

## Questions to investigate with the original plots

1. Do the rectus femoris channels show sustained amplitude excursions rather than just isolated samples? Compare their raw traces near 1.2 to 1.7 s.
2. Inspect the right biceps femoris near 1.98 s and the left biceps femoris near 1.85 s. Do these extremes belong to a cluster or a brief isolated event?
3. Are intervals near the beginning of the window more quiescent than near its end? Avoid calling them 'rest' without a protocol.
4. Which patterns repeat in later windows? Repetition might motivate hypotheses, not prove exercise type or gait events.

## Interpretation limits

- The peaks at 1.3890 s (right rectus femoris) and 1.5120 s (left rectus femoris) differ by 123 ms **as single-sample peak times**. This is **not** an estimate of EMG onset latency, neuromuscular delay or muscle coordination.
- Amplitude differences between channels do **not** establish physiological strength, activation level, asymmetry or muscle recruitment without channel calibration, electrode metadata, comparable acquisition conditions and a validated processing pipeline.
- Artifact identification, task type, signal quality and MVN synchronization remain unresolved. No conclusions should be drawn about the Qualisys web report from this unrelated raw Cometa session.
- **Next step:** inspect raw waveforms at narrower time windows and document whether apparent bursts consist of multiple high-amplitude samples or isolated spikes. Do not enable previews until the raw inspection is understood.

**Provenance:** measurements recalculated directly from the exact user-provided MVNE XML original and recorded on 2026-10-31. This document adds no new copies of participant recordings.
