# KINORYX, laboratorio de estudio con Python y Cursor

> Esta es una **rama de investigación descartable**. No abrir PR, no fusionar ni trasladar automáticamente a `main`.

## Actualización de tu carpeta ya creada

```powershell
cd C:\dev\kinoryx-study
git pull --ff-only origin study/xsens-cometa-qualisys-20261030
```

No repitas `git worktree add`, ni reinstales Python. Tu entorno `.venv` con Python 3.13 ya pasó 33 pruebas.

## Qué se descarga de GitHub

Los **tres originales** `.mvns`, `.mvne` y `.mvn` están guardados íntegros en [research/source_data](source_data/README.md). El binario MVN se transfirió con una restauración verificada por SHA-256, sin intervención de tu PC. No se necesita ningún ZIP.

El reporte web de Qualisys está documentado en [research/qualisys](qualisys/README.md) y se puede abrir con [open_report.html](qualisys/open_report.html). Es un **enlace al sitio original**, no una copia offline de su contenido interactivo.

**Atención:** el repositorio de Kinoryx es público; los tres originales que se subieron a esta rama pueden verse públicamente. Los datos EMG no adquieren licencia MIT por estar presentes en el repositorio.

## Visualizar la investigación en el servidor local

La entrada principal ya no contiene las gráficas. Los dos espacios comparten el mismo servidor local:

| Página | Ruta | Función |
| --- | --- | --- |
| **Home** | http://127.0.0.1:8050/ | Inicio limpio con enlaces Laboratory y Dashboard |
| **Dashboard** | http://127.0.0.1:8050/dashboard/ | La interfaz de marcha existente, conservada |
| **Laboratory** | http://127.0.0.1:8050/lab/ | Cuatro subpáginas de investigación |

En Laboratory: `/lab/exploration`, `/lab/quality`, `/lab/experimentation`, `/lab/evaluation`.

La etapa Exploratory Analysis permite arrastrar canales a Panel A/B y elegir **Side by side**, **Stacked** o **Overlay**. La grabación original siempre queda intacta y la visualización exploratoria no realiza filtros. Las otras etapas disponen de sus propios espacios para registrar resultados conforme se investigue.

Los archivos de progreso y evidencia se mantienen en `research/laboratory/01_exploratory_analysis.md`, `02_signal_quality.md`, `03_processing_experiments.md`, `04_evaluation_reporting.md`; los experimentos específicos continúan en `research/experiments/`.

El servidor de desarrollo ya tiene hot reload. Para aplicar cambios ordinarios basta `git pull --ff-only` desde otra terminal sin detener el servidor. Solo si el proceso está detenido:

```powershell
cd C:\dev\kinoryx-study
.\.venv\Scripts\python.exe apps\biomechanics_dashboard\app.py
```

[Manual detallado del servidor y de la nueva navegación](LIVE_DASHBOARD.md)

**Primero estudiar señales originales, después evaluar calidad y experimentar con filtros.** La referencia Qualisys permanece separada de los archivos Cometa/Xsens.

## Ejecutar el primer estudio en Cursor

En la terminal de `C:\dev\kinoryx-study`:

```powershell
.\.venv\Scripts\python.exe research\lessons\01_mvns.py
.\.venv\Scripts\python.exe research\study_files.py --plots
.\.venv\Scripts\python.exe -m pytest
```

El primer comando enseña los atributos y referencias del MVNS. El segundo analiza las 4 señales EMG y examina solo la huella y cabecera binaria del MVN, **sin decodificar cinemática**. El resumen y las gráficas se guardan localmente bajo `data_local/study_output/`.

Verifica los tres archivos originales, ya presentes en GitHub:

```powershell
.\.venv\Scripts\python.exe -m kinoryx.cli verify-session research/source_data
```

## Estado del estudio: pausa antes de interpretar señales

**Auditoría documental Qualisys cerrada el 2026-10-31.** El archivo MVN ya está incorporado y verificado. Las vistas `Test results` y `Findings` se inspeccionaron directamente, y el informe independiente [REPORT_AUDIT_2026-10-31.md](qualisys/REPORT_AUDIT_2026-10-31.md) explica el contenido observado. `Findings` muestra `Impairments` sin entradas visibles; no implica un resultado clínico normal. La lectura de gráficos internos, exportaciones y pruebas detalladas de controles no se completó y está identificada como limitación, sin bloquear el cierre documental.

La auditoría documental web ya se cerró. Se puede comenzar el estudio gradual de EMG, iniciando por la señal original en el servidor local antes de probar transformaciones.

## Siguiente ejercicio: estudiar la EMG por intervalos

La lección 01 ya se ejecutó correctamente en Cursor el 2026-10-31. La captura MVN ya está presente y su integridad se verificó, pero aún no se decodificó; esto no impide estudiar las cuatro señales EMG disponibles en GitHub.

```powershell
.\.venv\Scripts\python.exe research\lessons\02_emg.py
.\.venv\Scripts\python.exe research\lessons\02_emg.py --channel 0 --start 1 --duration 0.25 --plot
```

La lección 02 explica RMS, frecuencia de muestreo, ventanas y precauciones al interpretar la magnitud de la señal. La gráfica se guarda únicamente bajo `data_local/study_output/`. Para otras opciones consulta [02_EMG.md](lessons/02_EMG.md).

## Orden del estudio

1. [MVNS, organización de la sesión](lessons/01_MVNS.md)
2. [MVNE, canales EMG y estadísticas sin asumir unidades físicas](lessons/02_EMG.md)
3. MVN, analizar formato binario cuando esté disponible; buscar exportación cinemática interpretable
4. Revisar CSV y JSON derivados de EMG
5. Reporte Qualisys, métricas y procedencia cuando sean accesibles

Registra observaciones en [STUDY_LOG.md](STUDY_LOG.md) y decisiones para Kinoryx en [DECISION_LOG.md](DECISION_LOG.md). La futura funcionalidad aprobada deberá implementarse desde una rama nueva basada en `main`.

## Límites científicos

La sesión está etiquetada `EMG2_Walkig`, mientras los nombres de archivo dicen `Squats`. No se ha demostrado qué ejercicio se ejecutó. Los offsets declarados como cero no prueban sincronización, y el formato MVNE no confirma unidades ni normalización de EMG. El informe Qualisys no se ha vinculado científicamente a esta captura.
