# Security and privacy

KINORYX intends to support affordable, reproducible research without making patient data public.

- Keep recordings and identifiers out of GitHub, CI logs, documentation and issue attachments.
- Local recordings belong in ignored `data_local/`, preferably with de-identification and access controls; `.gitignore` cannot ensure privacy.
- The dashboard binds to `127.0.0.1` and processes CSV uploads in memory by default.
- Do not assume future web upload services are permitted without security, storage, retention, access and legal reviews.
- Never commit API tokens or credentials.
- Limit file upload sizes and reject unsupported formats.
- Public examples should be synthetic or legally redistributable, clearly labeled.
- MIT licensing covers project code, not restricted recordings, Xsens vendor technology, patient consent or trademarks.
- Clinical use would require independent scientific, usability, privacy and regulatory validation.
