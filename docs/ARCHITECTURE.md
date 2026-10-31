# Architecture

KINORYX has one modular repository and two public components.

**Gait Detection Engine** is a vendor-neutral, headless Python package in `src/kinoryx`. It owns data parsing, preprocessing, exploratory detection, eventual event inference, metrics and scientific validation.

Filtering is configured through immutable `FilterSpec` values. The engine
stores a resolved `FilterReport` per channel so filter family, frequencies,
order, phase behavior, coefficient form and independently processed segments
remain auditable. See [Filtering engine](FILTERING_ENGINE.md).

**Biomechanics Dashboard** lives in `apps/biomechanics_dashboard`, imports the engine and owns visualization, local file loading, user feedback, future human annotation and reporting.

Dependency direction: `dashboard -> engine`, never the reverse.

Version 0.1 is a local-only research scaffold. No cloud backend, user account, database, Xsens dependency or paid product is needed. Web deployment comes later, only after privacy/access requirements are established.

Future ingestion adapters can normalize Xsens, generic IMUs and other supported devices into typed internal sensor records. Never assume sensor axis meaning from generic column names.

## External EMG ingestion boundary

The independent `src/kinoryx/io/xsens_emg.py` adapter reads scalar channel samples from local MVNE XML recordings. It preserves source-scale values and exposes local CSV export plus provenance metadata. It does **not** read the binary MVN recording, align streams with Qualisys, normalize EMG, or implement an EMG-specific analysis pipeline. The dashboard and existing exploratory gait engine remain separate. Research references and uncertainties are catalogued in [Research sources](RESEARCH_SOURCES.md).
