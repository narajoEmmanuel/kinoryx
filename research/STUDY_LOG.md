# Bitácora del laboratorio (solo investigación)

Fecha de apertura: 2026-10-30. Rama: `study/xsens-cometa-qualisys-20261030`.

| Orden | Archivo | Conocimiento confirmado en el archivo | Incógnita a resolver | Estado |
| --- | --- | --- | --- | --- |
| 1 | `EMG2_Squats.mvns` | XML v2, etiqueta `EMG2_Walkig`, dos referencias a MVN/MVNE, offsets declarados cero | Ejercicio real y sincronización instrumental no verificados | Lección 01 ejecutada en Cursor, lectura correcta |
| 2 | `EMG2_Squats-200714130240.mvne` | 4 canales de Cometa, 2000 Hz, 16527 muestras/canal | Unidad, ganancia, filtrado, artefactos, electrodos, alineación temporal | Inspección ejecutada en Cursor, guía 02 disponible |
| 3 | `EMG2_Squats.mvn` | Archivo binario original inspeccionado fuera de GitHub y registrado mediante SHA-256 | Formato decodificado, unidades, frames, segmentos, tiempo, ángulos | Binario incorporado a GitHub con tamaño y SHA-256 verificados; decodificación pendiente |
| 4 | `EMG2_Squats_emg.csv` + `*.metadata.json` | Derivados locales del EMG original | Fidelidad, limitaciones de tiempo relativo y consistencia | Pendiente |
| 5 | Reporte Qualisys | Vista de resultados inspeccionada y documentada, sin relación probada con Xsens | Página Findings, datos numéricos de curvas y controles interactivos no verificados | Auditoría separada completada dentro del acceso de lectura |

## Registro de sesiones

### Sesión 01: inventario y preservación

**Hipótesis:** podemos comprobar integridad y describir la estructura del material sin atribuir datos fisiológicos no verificados.

**Pasos:** verificar SHA-256, inspeccionar `.mvns`, identificar encabezados EMG, exportar estadísticas y gráficas locales.

**Resultados documentados desde el archivo original proporcionado:** índice XML de 291 bytes con etiqueta de sesión `EMG2_Walkig`, comentario idéntico y exactamente dos referencias: `EMG2_Squats.mvn` y `EMG2_Squats-200714130240.mvne`. Ambas entradas declaran `timeOffset=0` y `timeEndOffset=0`. Se registró discrepancia de nombre frente a `Squats`. Véase [Lección 01](lessons/01_MVNS.md).

**Ejecución en Cursor por el usuario:** confirmada el 2026-10-31. `research/lessons/01_mvns.py` leyó correctamente el índice y confirmó `EMG2_Walkig`, 2 referencias, offsets `0`, EMG presente y binario MVN ausente. `research/study_files.py --plots` confirmó cuatro canales, 2000 Hz, 16527 muestras por canal, y generó las salidas bajo `data_local/study_output`. El resultado de `pytest` previo fue 33 aprobadas, 1 omitida.

### Sesión 02: lectura experimental de EMG

**Estado:** guía y programa listos; ejecución de `02_emg.py` por el usuario todavía no confirmada.

**Instrucciones:** [Lección 02](lessons/02_EMG.md), `research/lessons/02_emg.py`. Empezar con ventanas de 0,25 s, documentar estadísticos originales y comparar vistas sin equipararlos con fuerza ni activación normalizada.

**Limitaciones:** unidades y calibración desconocidas, relación física con MVN y Qualisys sin verificar.

**Preguntas abiertas:** ¿es caminata o sentadilla?, ¿hay exportación MVNX del movimiento?, ¿cómo fueron colocados los electrodos?, ¿es el mismo ensayo que el reporte Qualisys?

**Limitaciones:** no interpretar valores EMG como amplitud calibrada ni inferir cinemática de bytes no decodificados.

### Sesión 03: archivo MVN y auditoría del reporte web

**MVN:** incorporación completada el 2026-10-31 en `research/source_data/EMG2_Squats.mvn`. Verificación de Git blob `90760d5756b2e4c60f9426341ad43d57cd95863b`, tamaño 4,672,353 bytes, SHA-256 comprobado durante restauración en GitHub Actions. **Sin decodificar todavía.**

**Qualisys:** inspección directa de la página `Test results` del reporte GaitCAST Full body (Visual3D). Informe detallado [REPORT_AUDIT_2026-10-31.md](qualisys/REPORT_AUDIT_2026-10-31.md). Se identifican siete grupos de análisis, tres ensayos visibles, EMG bilateral tibial anterior, panel video/3D, referencias y opciones de PDF. La página `Findings` y algunas interacciones requieren comprobación adicional. **No existe prueba de que Qualisys corresponda a la misma sesión Xsens/Cometa.**

**Decisión de orden:** no comenzar la siguiente lección sobre análisis fisiológico EMG hasta resolver el alcance restante del reporte web solicitado por el usuario.
