# Starter CSV contract (v0.1)

Exploratory data:

```csv
time_s,left_gyro_y_deg_s,right_gyro_y_deg_s
0.00,0.1,0.2
0.01,0.4,0.3
```

The excerpt is illustrative and too short for actual filtering. Use `kinoryx demo` to create a valid full dataset.

- `time_s`: strictly increasing seconds, nearly uniform sampling.
- At least one left/right gyro column is required; each is in degrees per second.
- Samples must be numeric and finite. At least 20 rows are required.
- The Y-axis convention and positive peaks are synthetic demo choices, **not** Xsens guarantees.
- Sampling frequency is inferred from the median time interval, with warnings for deviations.
- Large gaps are treated as independent filtering segments. Orientation frames,
  resampling, full tri-axial fields and vendor metadata are not implemented.
- These demo columns do not encode independent initial contact/toe-off ground truth.

Real Xsens MVNX or vendor CSV files should not be imported until exact schemas, sensor positioning, versions, units and coordinate frames are known.

## Local external EMG contract (research-only)

The independent `.mvne` XML reader in `kinoryx.io.xsens_emg` supports numeric scalar channels declared in the MVN external-channel XML header. It verifies declared channel count, channel IDs, sampling rates, finite values and equal sample counts. No proprietary binary `.mvn` parser is included.

The optional local export produces `time_s` as channel-local sample index divided by header sampling frequency, and one unscaled `emg_ch<ID>_raw` column per channel. A sidecar JSON records channel/source labels, the exact source SHA-256, reported sample rate, sample count and unresolved units/synchronization status.

These raw channels are **not** gyroscope columns and cannot be passed to the gait-event `inspect`/`explore` commands as though they were validated gait signals. No raw EMG unit, electrode placement, gain, filtering or absolute cross-system synchronization is inferred. See [Research sources](RESEARCH_SOURCES.md).

## Approved Xsens/Cometa research bundle verification

The supplied `.mvn`, `.mvns` and `.mvne` filenames, expected byte lengths and SHA-256 hashes are recorded in [the source manifest](../examples/research/EMG2_Squats.manifest.json). `kinoryx verify-session data_local` checks exact file integrity, ensures the `.mvns` XML indexes the expected names, and validates the `.mvne` scalar channels. Verification does not imply calibration, medical validity, correct exercise labels or synchronization with the independent Qualisys web report. The private source recordings themselves remain outside GitHub.
