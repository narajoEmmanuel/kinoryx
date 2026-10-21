# Filtering engine

## Scope

KINORYX provides a deliberately small filtering API for uniformly sampled gait
signals. It is an independent Python implementation built on NumPy and SciPy;
it does not contain MATLAB or EEGLAB source code.

The default remains an exploratory fourth-order Butterworth low-pass at 6 Hz,
applied forward and backward in second-order-section form. This preserves the
v0.1 demonstration, but the cutoff is **not** a universal gait-analysis value
and has not been validated for clinical event detection.

## Supported designs

- Butterworth low-pass, high-pass, band-pass and band-stop filters.
- Hamming-window linear-phase FIR equivalents.
- Narrow IIR notch filters when a known interference frequency is demonstrated.
- Offline zero-phase and causal forward-only application.
- Optional constant or linear detrending before filtering.
- Frequency-response calculation and a per-channel reproducibility report.
- Independent processing of continuous segments separated by large time gaps.

The public entry points are `FilterSpec`, `apply_filter`, `frequency_response`
and the backward-compatible `lowpass` helper in
`kinoryx.processing.filtering`. `analyze_exploratory` accepts an optional
`FilterSpec` and stores the resolved design report for every channel.

```python
from kinoryx.pipeline import analyze_exploratory
from kinoryx.processing import FilterSpec

spec = FilterSpec(
    kind="bandpass",
    cutoff_hz=(0.5, 12.0),
    family="butterworth",
    order=4,
    zero_phase=True,
)
result = analyze_exploratory(frame, spec)
print(result.filter_reports)
```

## Scientific boundaries

- Zero-phase processing uses future samples and is unsuitable for real-time
  feedback. Causal mode is available but has phase delay and needs separate
  validation.
- Filtering cannot repair missing samples, incorrect units, wrong sensor axes
  or coordinate-frame errors.
- Ordinary timing jitter still produces a data-quality warning. Large gaps are
  treated as boundaries, never bridged by filter state or padding.
- FIR cutoff frequencies are half-amplitude (-6 dB); Butterworth cutoff
  frequencies are half-power (-3 dB) before forward-backward application.
- Very sharp FIR transitions create long kernels and can spread transient
  artifacts. KINORYX therefore exposes the transition width and resolved tap
  count instead of hiding them.
- Notch filtering is opt-in. It should not be applied merely because 50 or 60
  Hz electrical power exists in the environment.

The selected filtering parameters must be validated against independently
annotated recordings for each sensor location, sampling rate, walking condition
and downstream event detector.

## Design basis

The implementation uses SciPy's documented second-order-section routines for
numerical robustness and its public filter-design functions:

- [SciPy signal-processing reference](https://docs.scipy.org/doc/scipy/reference/signal.html)
- [SciPy zero-phase filtering guidance](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.filtfilt.html)

The optional automatic FIR length follows the broad transition-width heuristic
documented by EEGLAB, while remaining an independent SciPy implementation:

- [EEGLAB filtering FAQ](https://eeglab.org/others/Firfilt_FAQ.html)

Published gait work reports materially different cutoffs according to sensor
placement and event-detection objective; this is why KINORYX exposes the design
instead of presenting 6 Hz as a universal preset:

- [Gait event detection using a rate gyroscope](https://pmc.ncbi.nlm.nih.gov/articles/PMC3247727/)
- [Marker displacement data filtering in gait analysis](https://doi.org/10.1016/j.bspc.2021.102974)
