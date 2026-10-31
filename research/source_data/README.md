# Source data preserved in the study branch

This branch belongs to a **public** GitHub repository. The supplying user explicitly instructed that original research sources be uploaded to GitHub.

| Source | Tracked here? | Integrity |
| --- | --- | --- |
| `EMG2_Squats.mvns` | Yes | Exact original Git blob SHA `9932edd24d8d8f9020277aa335ce15826d3ec542` |
| `EMG2_Squats-200714130240.mvne` | Yes | Exact original Git blob SHA `29896e94e9568294566eae798ef62cb88274eb09` |
| `EMG2_Squats.mvn` | **No** | Original SHA-256 recorded in `examples/research/EMG2_Squats.manifest.json` |

The original binary `.mvn` is not tracked because the available connected GitHub upload action accepts text or base64 content rather than a local binary file, and this session's binary attachment could not be transferred using that action. Do **not** mistake this partial upload for a verified complete three-file bundle.

Run the study with the two files already present in this directory:

```powershell
.\.venv\Scripts\python.exe research\lessons\01_mvns.py
.\.venv\Scripts\python.exe research\study_files.py --plots
```

These commands inspect session labels and EMG directly from GitHub. The second produces local figures under `data_local/study_output/`. Full three-file verification is only possible when all three original files are present in the same directory.

External web reference: [Qualisys](../qualisys/README.md). The interactive website itself is not embedded in this GitHub repository.

## Scientific and publishing limits

The EMG source contains a genuine human sensor recording with 4 raw channels, which is now publicly accessible through this research branch. It is not covered by the repository's MIT code license by default. Do not infer calibrated physiological units, subject identity, exercise type or synchronization from the files.
