# KINORYX

**Human Motion Intelligence | Open science. Accessible biomechanics.**

KINORYX is a vendor-neutral, pre-alpha open-source project composed of two independently usable components:

- **Gait Detection Engine**, Python scientific signal processing and exploratory candidate extraction.
- **Biomechanics Dashboard**, a local interactive Dash/Plotly interface built on the engine.

**Scientific status (v0.1.0):** the current peak finder is a demonstration, **not** a validated gait-event detector. It cannot reliably identify initial contact, toe-off or pathological gait phases. Do not use the output for clinical decisions.

## Start locally

Python 3.11+ required.

```sh
git clone https://github.com/narajoEmmanuel/kinoryx.git
cd kinoryx
python -m venv .venv
# Activate your virtual environment before continuing.
python -m pip install -e ".[dashboard,dev]"
kinoryx demo
kinoryx inspect data_local/demo_synthetic.csv
kinoryx explore data_local/demo_synthetic.csv
python apps/biomechanics_dashboard/app.py
```

Open http://127.0.0.1:8050 . Demo data are synthetic and no sensor equipment is needed.

## Repository

- `src/kinoryx/`: headless scientific Python package, Gait Detection Engine
- `apps/biomechanics_dashboard/`: independently maintained local UI
- `tests/`: scientific infrastructure and integration tests
- `docs/`: data contract, architecture, scientific validation, roadmap, privacy
- `examples/`: reproducible open demonstrations

The dashboard imports the engine. The engine must never import the dashboard or Plotly. Real Xsens exports are **not supported yet** until formats, coordinate frames, units and metadata are verified. The starter CSV contract uses explicit `time_s` and `left_gyro_y_deg_s` / `right_gyro_y_deg_s`, for demonstration only.

## License and privacy

MIT licensed code. The KINORYX name and third-party data are not licensed by MIT. Commercial use of MIT licensed code is permitted subject to the license. No trademark clearance has been performed. **Never commit real patient files, identifiers or private sensor recordings.** A local CSV processing workflow does not itself establish medical-device validation.

See [architecture](docs/ARCHITECTURE.md), [data contract](docs/DATA_CONTRACT.md), [validation](docs/SCIENTIFIC_VALIDATION.md), [security](docs/SECURITY_AND_PRIVACY.md) and [contributing](CONTRIBUTING.md).
