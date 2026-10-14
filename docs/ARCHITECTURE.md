# Architecture

KINORYX has one modular repository and two public components.

**Gait Detection Engine** is a vendor-neutral, headless Python package in `src/kinoryx`. It owns data parsing, preprocessing, exploratory detection, eventual event inference, metrics and scientific validation.

**Biomechanics Dashboard** lives in `apps/biomechanics_dashboard`, imports the engine and owns visualization, local file loading, user feedback, future human annotation and reporting.

Dependency direction: `dashboard -> engine`, never the reverse.

Version 0.1 is a local-only research scaffold. No cloud backend, user account, database, Xsens dependency or paid product is needed. Web deployment comes later, only after privacy/access requirements are established.

Future ingestion adapters can normalize Xsens, generic IMUs and other supported devices into typed internal sensor records. Never assume sensor axis meaning from generic column names.
