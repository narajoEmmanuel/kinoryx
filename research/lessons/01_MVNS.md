# Estudio 01: entender el archivo MVNS

**Rama:** `study/xsens-cometa-qualisys-20261030`. Esta lección es para investigación y no se mezcla con `main`.

## Objetivo

Comprender **cómo se organiza la sesión** antes de analizar señales eléctricas o movimiento. El MVNS no contiene por sí mismo las series de muestras: referencia otros dos archivos.

## Evidencia comprobada en el original suministrado

Archivo: `EMG2_Squats.mvns`, 291 bytes, SHA-256
`3e0550c05c372a17a94582d9117f34c94bcce04d39e582febbbc5e6101bbf463`.

| Elemento XML | Valor literal observado | Interpretación limitada |
| --- | --- | --- |
| `mvns/@version` | `2` | Versión indicada en el índice de sesión, no versión global del programa |
| `mvns/@sessionname` | `EMG2_Walkig` | Etiqueta escrita al guardar la sesión |
| `comment` | `EMG2_Walkig` | Repite esa etiqueta |
| Primer `file/@filename` | `EMG2_Squats.mvn` | Referencia al archivo binario de movimiento |
| Segundo `file/@filename` | `EMG2_Squats-200714130240.mvne` | Referencia a las señales externas EMG |
| `file/@timeOffset` | `0` en ambos | Valor declarado, **no** prueba de sincronización |
| `file/@timeEndOffset` | `0` en ambos | Valor declarado, **no** prueba de fin coincidente de señales |

**Contradicción importante:** el nombre de la sesión dice `Walkig`, pero los archivos se llaman `Squats`. No se puede saber solamente con este índice si el ejercicio real fue caminar, hacer sentadillas u otro.

## Ejecución en Cursor

Desde `C:\dev\kinoryx-study`, con los originales en `data_local\`:

```powershell
.\.venv\Scripts\python.exe -m kinoryx.cli verify-session data_local
.\.venv\Scripts\python.exe research\lessons\01_mvns.py
```

El primer comando verifica que los tres originales coinciden con los hashes aprobados. El segundo usa Python para mostrar la versión, la etiqueta, el comentario y las dos referencias **leídas del XML local**. No modifica archivos.

Para obtener además un análisis de todas las fuentes:

```powershell
.\.venv\Scripts\python.exe research\study_files.py --data-dir data_local --output-dir data_local\study_output
```

Abre `data_local/study_output/study_summary.json` y examina el objeto `session_index`.

## Preguntas para discutir

1. ¿Cuál es la diferencia entre un **índice de sesión** y un **archivo de señales**?
2. ¿Por qué el nombre `Walkig` no demuestra qué ejercicio se hizo?
3. Si ambos offsets son cero, ¿qué necesitaríamos para comprobar sincronización real?
4. ¿Qué información adicional debemos buscar en MVNE, MVN y el reporte Qualisys?

## Primeras conclusiones

- El archivo organiza exactamente dos referencias, una `.mvn` y una `.mvne`.
- Los dos archivos estaban disponibles junto con el índice en el conjunto original inspeccionado.
- Sus huellas están registradas en `examples/research/EMG2_Squats.manifest.json`.
- Aún falta interpretar el archivo binario MVN y la sincronización física de las mediciones.
- El reporte Qualisys se considera **independiente** hasta verificar su relación con esta sesión.

Al finalizar la lección, registra observaciones nuevas en `research/STUDY_LOG.md` y las decisiones sobre el producto en `research/DECISION_LOG.md`. No transfieras automáticamente este laboratorio a producción.
