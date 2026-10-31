# KINORYX, laboratorio de estudio con Python y Cursor

> Esta es una **rama de investigación descartable**. No abrir PR, no fusionar ni trasladar automáticamente a `main`.

## Actualización de tu carpeta ya creada

```powershell
cd C:\dev\kinoryx-study
git pull --ff-only origin study/xsens-cometa-qualisys-20261030
```

No repitas `git worktree add`, ni reinstales Python. Tu entorno `.venv` con Python 3.13 ya pasó 33 pruebas.

## Qué se descarga de GitHub

Los originales `research/source_data/EMG2_Squats.mvns` y `research/source_data/EMG2_Squats-200714130240.mvne` ahora están **guardados directamente en la rama**, preservando exactamente sus bytes originales. Por tanto, no es necesario ningún ZIP para estudiar el índice MVNS y el EMG. Su integridad se verifica en `tests/test_research_committed_sources.py`.

El archivo binario `EMG2_Squats.mvn` **todavía no está guardado en GitHub**, debido a una limitación de transferencia binaria del conector disponible. La metadata y su SHA-256 se conservan en [el manifiesto](../examples/research/EMG2_Squats.manifest.json). No se ha decodificado su movimiento ni confirmado sincronización.

El reporte web de Qualisys está documentado en [research/qualisys](qualisys/README.md) y se puede abrir con [open_report.html](qualisys/open_report.html). Es un **enlace al sitio original**, no una copia offline de su contenido interactivo.

**Atención:** el repositorio de Kinoryx es público; los originales MVNS y MVNE que se subieron a esta rama pueden verse públicamente. Los datos EMG no adquieren licencia MIT por estar presentes en el repositorio.

## Ejecutar el primer estudio en Cursor

En la terminal de `C:\dev\kinoryx-study`:

```powershell
.\.venv\Scripts\python.exe research\lessons\01_mvns.py
.\.venv\Scripts\python.exe research\study_files.py --plots
.\.venv\Scripts\python.exe -m pytest
```

El primer comando enseña los atributos y las referencias del índice MVNS. El segundo analiza los 4 canales EMG desde el XML original, guarda un resumen JSON en `data_local/study_output/study_summary.json` y genera ocho gráficas en esa carpeta ignorada por Git. La falta del binario MVN se anota como pendiente, sin bloquear la exploración del EMG.

Si tienes una copia local de `EMG2_Squats.mvn`, la puedes colocar manualmente en `research/source_data/` para analizar su huella, pero **no** se requiere para la primera lección ni para las señales EMG. Ten presente que un binario colocado ahí aparecería como archivo nuevo en `git status` y no debe subirse sin revisar sus metadatos.

## Siguiente ejercicio: estudiar la EMG por intervalos

La lección 01 ya se ejecutó correctamente en Cursor el 2026-10-31. La captura MVN sigue ausente, pero eso no impide estudiar las cuatro señales EMG disponibles en GitHub.

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
