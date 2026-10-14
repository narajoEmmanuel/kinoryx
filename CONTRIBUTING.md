# Contributing to KINORYX

KINORYX welcomes reproducible, scientifically grounded community contributions.

1. Open an issue describing the need and how the improvement can be verified.
2. Submit focused pull requests with tests and documentation.
3. Keep the Gait Detection Engine independent from the Biomechanics Dashboard.
4. Mark synthetic or estimated outputs transparently. Do not claim event accuracy without an independently annotated reference.
5. Do not upload or commit clinical participant information, raw Xsens sessions, private datasets or proprietary vendor exports.
6. Never introduce mandatory paid accounts or services for the local workflow without discussion.

Run `python -m pip install -e ".[dashboard,dev]"`, `ruff check src apps tests` and `pytest -q` before opening a pull request.

By contributing, you agree to release your contribution under the repository MIT license. Scientific validation and clinical applicability require separate evidence.
