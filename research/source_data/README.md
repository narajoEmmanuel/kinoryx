# Original research dataset, study branch only

All **three original supplied files** now reside under `research/source_data/` on the experimental branch `study/xsens-cometa-qualisys-20261030`.

| File | Bytes | Original SHA-256 | Git blob SHA |
| --- | ---: | --- | --- |
| `EMG2_Squats.mvns` | 291 | `3e0550c05c372a17a94582d9117f34c94bcce04d39e582febbbc5e6101bbf463` | `9932edd24d8d8f9020277aa335ce15826d3ec542` |
| `EMG2_Squats-200714130240.mvne` | 2,545,030 | `17bf9261d73db6b3d94b36b5f334555c3cad6e87ecbce17f422cd62891b9101f` | `29896e94e9568294566eae798ef62cb88274eb09` |
| `EMG2_Squats.mvn` | 4,672,353 | `2881fe6feb8c274bbfcbd50b92ca44d29f8469dad5cb9294af1716b87620692d` | `90760d5756b2e4c60f9426341ad43d57cd95863b` |

The MVN binary was reconstructed on GitHub Actions from uploaded transfer chunks. The job checked both the expected byte count and SHA-256, and a subsequent inspection confirmed its Git blob SHA matches the original. The transfer fragments were removed from the branch in the final recovery commit. See the [verified restoration run](https://github.com/narajoEmmanuel/kinoryx/actions/runs/41226384928).

Run full integrity verification from the repository root:

```powershell
.\.venv\Scripts\python.exe -m kinoryx.cli verify-session research/source_data
```

The actual motion data still **has not been decoded or interpreted**. An MVN file being present is not proof that its internal format, joint units, segment definitions, frame rate or synchronization are understood.

## Publishing and scientific cautions

This repository is **public** and these human measurement files are now publicly accessible because the supplying user explicitly instructed their inclusion in GitHub. Their presence does not grant third parties rights to redistribute the recordings under the repository's MIT license. Do not infer participant identity, exercise type, physiological units, calibrated EMG, or synchronization.

The Qualisys link is an **independent external dataset** and is audited separately under [research/qualisys](../qualisys/README.md). Do not merge its gait report with this Xsens/Cometa session.
