# KINORYX: laboratorio temporal de estudio

> **RAMA EXCLUSIVAMENTE EXPERIMENTAL. NO ABRIR PR, NO MERGE, NO CHERRY-PICK AUTOMÁTICO A MAIN.**

Propósito: comprender el conjunto suministrado Xsens/Cometa (`.mvns`, `.mvn`, `.mvne`, CSV y metadatos) mediante Python en Cursor y conservar conclusiones sobre la dirección futura de KINORYX. Ningún experimento de esta rama representa funcionalidad aprobada del producto.

## Actualizar el laboratorio ya creado (tu caso, Cursor en Windows)

La rama y el worktree ya están creados en `C:\dev\kinoryx-study`. **No** vuelvas a ejecutar `git worktree add`; solo actualiza la rama experimental:

```powershell
cd C:\dev\kinoryx-study
git pull --ff-only origin study/xsens-cometa-qualisys-20261030
```

Ya cuentas con Python 3.13.5 en el entorno local y completaste 33 pruebas con éxito y 1 omitida. La carpeta `.venv` no se modifica por el pull.

**Primer estudio guiado:** [Lección 01, MVNS](lessons/01_MVNS.md) y su programa [`01_mvns.py`](lessons/01_mvns.py). Ejecuta desde la raíz:

```powershell
.\.venv\Scripts\python.exe -m kinoryx.cli verify-session data_local
.\.venv\Scripts\python.exe research\lessons\01_mvns.py
```

## Abrir sin alterar tu carpeta de producción (Windows PowerShell)

En una terminal **dentro de la carpeta existente de Kinoryx**:

```powershell
git fetch origin
git worktree add -b study/xsens-cometa-qualisys-20261030 ..\kinoryx-study origin/study/xsens-cometa-qualisys-20261030
cd ..\kinoryx-study
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pip install -r research\requirements.txt
cursor research\kinoryx-study.code-workspace
```

Si `cursor` no existe como comando, abre Cursor y utiliza **File > Open Workspace from File**, escogiendo `research/kinoryx-study.code-workspace`. Selecciona el intérprete `.venv/Scripts/python.exe` en Cursor. Si ya existe esa rama local, utiliza `git worktree add ..\kinoryx-study study/xsens-cometa-qualisys-20261030` en lugar del comando con `-b`.

## Archivos originales: locales, no publicados

Extrae el ZIP privado entregado en el chat dentro de **esta** carpeta de estudio, de modo que los datos originales estén en `data_local/`:

```text
kinoryx-study/
  data_local/
    EMG2_Squats.mvns
    EMG2_Squats.mvn
    EMG2_Squats-200714130240.mvne
    EMG2_Squats_emg.csv                 (opcional, ya convertido)
    EMG2_Squats_emg.metadata.json       (opcional)
  research/
    study_files.py
    STUDY_LOG.md
    DECISION_LOG.md
```

La carpeta `data_local/` está excluida de Git; **no** agregues archivos reales con `git add -f`, no pegues muestras de datos identificables en issues y no subas capturas de un participante a GitHub.

## Primer experimento, sin modificación de los originales

```powershell
.\.venv\Scripts\python.exe -m kinoryx.cli verify-session data_local
.\.venv\Scripts\python.exe research\study_files.py --data-dir data_local --output-dir data_local\study_output --plots
```

La primera orden comprueba las tres huellas digitales y referencias originales con el manifiesto aprobado. La segunda produce `data_local/study_output/study_summary.json` y ocho figuras PNG de EMG (4 señales crudas y 4 curvas RMS en ventanas de 250 ms), sin procesar el binario MVN como cinemática validada.

## Orden de estudio

1. **MVNS**. Leer nombres, referencias y offsets. Pregunta: ¿qué fuentes organiza la sesión y qué contradicciones de etiquetas hay?
2. **MVNE**. Examinar estructura de canales, valores originales, integridad, ventanas RMS y artefactos. Pregunta: ¿qué se puede describir sin inventar unidades, calibraciones o actividad muscular normalizada?
3. **MVN**. Inventariar el archivo binario. No atribuirle ángulos, movimientos o frecuencia hasta obtener una exportación legible del software del fabricante.
4. **CSV/JSON derivados**. Verificar fidelidad respecto de MVNE, forma de tabla y trazabilidad de fuentes.
5. **Qualisys**. Tratar el enlace de reporte como una fuente externa separada. No inferir que corresponde a la misma persona o adquisición.

Anota resultados, incertidumbres, decisiones y próximos experimentos en [STUDY_LOG](STUDY_LOG.md) y [DECISION_LOG](DECISION_LOG.md). Cualquier funcionalidad futura que merezca pasar a producción se rediseñará y probará por separado, en otra rama creada desde `main`, nunca fusionando el historial de este laboratorio.

## Cautelas científicas

- `EMG2_Walkig` es el nombre en `.mvns`, mientras los archivos dicen `Squats`; el ejercicio no está demostrado.
- El EMG tiene cuatro canales etiquetados a 2.000 Hz, 16.527 muestras por canal.
- El formato MVNE no establece por sí solo unidades de amplitud ni sincronización con Qualisys.
- El programa produce estadística descriptiva, **no** diagnóstico, fuerza, validación biomecánica ni segmentación confiable del ejercicio.
