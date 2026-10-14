# Biomechanics Dashboard | Workspace v0.2 design baseline

**Status:** exploratory user interface proposal, separate from the Gait Detection Engine.

## Product responsibility

The Dashboard enables researchers to inspect, interact with, and contextualize available biomechanics signals. It consumes output from the engine but does not implement filtering or gait-event detection algorithms. KINORYX remains local-first, vendor-neutral, free to run, and without a hosted patient-data service.

## User experience

1. Open the application locally. The default, clearly labeled example uses **synthetic** foot-gyro-like data.
2. Optionally load a canonical CSV. The application validates it using the existing engine ingestion contract.
3. Review recording duration, estimated sampling rate, available demo channels and number of **unvalidated peak candidates**.
4. Inspect raw and filtered signals with independent visibility controls, selecting both feet or one side, and zooming on the time axis.
5. Examine a short table of candidate peaks and inspect provenance and timing warnings.
6. Return to the synthetic example without restarting the app.

## Screen architecture

- Persistent brand and workspace navigation, with unimplemented areas explicitly labeled as planned.
- Session/input section with a local CSV dropzone and synthetic-demo action.
- Contextual metrics cards describing recording metadata, not clinical outcomes.
- Primary signal explorer with raw/filtered/candidate traces.
- Layer and foot visibility controls.
- Candidate table and source/quality details.
- Persistent research and patient-data handling notice.

## Scientific and technical boundaries

- Peak markers are signal features, not independently verified steps, IC, TO or gait phases.
- The dashboard cannot claim patient metrics, spatiotemporal gait measures, clinical classifications or real Xsens compatibility.
- Downsampling, when triggered, applies to chart display only, not engine processing. The plots explicitly disclose this.
- Each CSV is processed in memory. The app binds to `127.0.0.1` and is not safe to expose directly to the internet.
- No remote fonts, SaaS dependencies, telemetry or analytics are added.
- The only engine dependency is `analyze_exploratory` and the synthetic fixture provider. The engine remains fully independent.

## Testing and acceptance

- The original six-trace synthetic plot remains the default.
- Foot and layer controls change the visible traces without changing source data.
- Corrupted upload content is rejected.
- Synthetic demo can be loaded with no CSV.
- No claims of clinical validation appear in data readouts.
- Validate lint, Python tests and GitHub Actions before merging into `main`.

## Future workspace modules (not implemented)

- Session library and metadata editor
- Independent event annotation, correction and review
- Gait cycle visualization and legitimate metrics
- Multi-session and patient-level comparisons
- Reproducible reports and secure export
- Accessibility/keyboard interaction and dedicated interaction tests