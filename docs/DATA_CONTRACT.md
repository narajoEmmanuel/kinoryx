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
- Large gaps, orientation frames, resampling, full tri-axial fields and vendor metadata are not implemented.
- These demo columns do not encode independent initial contact/toe-off ground truth.

Real Xsens MVNX or vendor CSV files should not be imported until exact schemas, sensor positioning, versions, units and coordinate frames are known.
