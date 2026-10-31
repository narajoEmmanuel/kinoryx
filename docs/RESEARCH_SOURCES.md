# Research reference sources, EMG example and Qualisys

Status: **reference material plus a verified local EMG ingestion example, NOT scientific ground truth**. Do not use these assets to claim validated gait events, normalized muscle activation, joint loading, diagnostic performance, or agreement between systems.

## Qualisys web report (user-supplied reference)

- URL: https://report.qualisys.com/r/f8pMFlrTA/details
- Role in KINORYX: a **reference for the future reporting and biomechanics validation workflow**, kept separate from the raw Xsens/Cometa recording below.
- Verification status as of 2026-10-30: the public-facing URL resolves to a client-rendered Qualisys Web Report, but its session details, charts, numeric outputs, attachments, study protocol and permission to redistribute have **not been retrieved or verified**. No measurements from it are incorporated as facts.
- Do not assume this Qualisys report belongs to the same participant, session, exercise or acquisition as the attached Xsens files. Establish provenance before linking them.
- To promote this to a reproducible data reference, archive an authorized report export locally, record software/pipeline versions, metric definitions and units, date and subject pseudonym, and separately document consent/license and synchronization. Do not commit identifiable exports.

Qualisys describes interactive reports with synchronized charts/video/3D visualizations, comparison tools and PDF export: https://www.qualisys.com/analysis/online-reporting/ . These are vendor capabilities, **not verified properties or results of the specific linked report**.

## Locally inspected Xsens/Cometa example (originals private)

The three user-provided files are a **single locally supplied example bundle**, not part of the public repository. Hashes below identify the exact inspected versions, without republishing signal values.

| Filename | Size (bytes) | SHA-256 | Interpretation |
| --- | ---: | --- | --- |
| `EMG2_Squats.mvn` | 4672353 | `2881fe6feb8c274bbfcbd50b92ca44d29f8469dad5cb9294af1716b87620692d` | Proprietary binary recording, not parsed by KINORYX |
| `EMG2_Squats.mvns` | 291 | `3e0550c05c372a17a94582d9117f34c94bcce04d39e582febbbc5e6101bbf463` | XML session file that references the `.mvn` and `.mvne` files |
| `EMG2_Squats-200714130240.mvne` | 2545030 | `17bf9261d73db6b3d94b36b5f334555c3cad6e87ecbce17f422cd62891b9101f` | MVN external-channel XML with Cometa EMG samples |

The `.mvns` attributes say `sessionname="EMG2_Walkig"` and its comment repeats this string, which **does not match** the `Squats` filenames. This is unresolved source metadata, not evidence of walking or squatting. The `.mvne` contains an `mvn ts` attribute of `1594724599.767`, but its exact timestamp meaning/time zone has not been independently verified.

### EMG header inventory

| ID | Source | Source channel | Header name | Sampling frequency | Samples |
| --- | --- | --- | --- | ---: | ---: |
| 0 | Cometa | 1 | Rectus Femoris Right | 2000 Hz | 16527 |
| 1 | Cometa | 2 | Biceps Femoris Right | 2000 Hz | 16527 |
| 2 | Cometa | 3 | Rectus Femoris Left | 2000 Hz | 16527 |
| 3 | Cometa | 4 | Biceps Femoris Left | 2000 Hz | 16527 |

The nominal span between first and last samples is **8.263 seconds** per channel, inferred as `(16527 - 1) / 2000`. The header does **not** establish amplitude units, calibration, acquisition filtering, channel placement protocol, synchronization with motion sensors, or ground-truth muscle activation. The channel names are labels from the source file, not independently verified anatomy.

## Supported local workflow

Place the `.mvne` and other raw files in the git-ignored `data_local/` directory, with appropriate access controls. Then run:

```sh
kinoryx inspect-emg data_local/EMG2_Squats-200714130240.mvne
kinoryx export-emg data_local/EMG2_Squats-200714130240.mvne
```

The second command creates `data_local/EMG2_Squats-200714130240_emg.csv` and an adjacent `.metadata.json` containing the SHA-256, channel mappings and preservation caveats. CSV columns are `time_s` (relative sample index / reported sampling rate) and `emg_ch0_raw` to `emg_ch3_raw`. Values are not scaled, filtered or normalized. This EMG contract is **separate** from the gyroscope demonstration CSV contract and is not accepted by the gait-event detector.

The binary `.mvn` and `.mvns` are catalogued, **not decoded or synchronized**. The linked Qualisys report is a research reference, **not ingested or verified**. A future comparison requires independently verified provenance, axes/units, synchronized time bases, and scientifically defined reference outputs.

## Reuse and privacy

Do not commit the uploaded recordings, converted CSV files, report exports, personal metadata or subject identifiers. Third-party software and datasets are not granted the repository's MIT license by inclusion in this reference list. Confirm participant consent, authorized reuse and applicable licensing before distributing derived data.
