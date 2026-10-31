# Bitácora del laboratorio (solo investigación)

Fecha de apertura: 2026-10-30. Rama: `study/xsens-cometa-qualisys-20261030`.

| Orden | Archivo | Conocimiento confirmado en el archivo | Incógnita a resolver | Estado |
| --- | --- | --- | --- | --- |
| 1 | `EMG2_Squats.mvns` | XML v2, etiqueta `EMG2_Walkig`, dos referencias a MVN/MVNE, offsets declarados cero | Ejercicio real y sincronización instrumental no verificados | Original en GitHub, guía disponible |
| 2 | `EMG2_Squats-200714130240.mvne` | 4 canales de Cometa, 2000 Hz, 16527 muestras/canal | Unidad, ganancia, filtrado, artefactos, electrodos, alineación temporal | Original en GitHub, análisis descriptivo disponible |
| 3 | `EMG2_Squats.mvn` | Archivo binario original inspeccionado fuera de GitHub y registrado mediante SHA-256 | Formato decodificado, unidades, frames, segmentos, tiempo, ángulos | Binario aún no transferido a GitHub |
| 4 | `EMG2_Squats_emg.csv` + `*.metadata.json` | Derivados locales del EMG original | Fidelidad, limitaciones de tiempo relativo y consistencia | Pendiente |
| 5 | Reporte Qualisys | URL documentada | Contenido verificable, permisos, relación con la sesión | Pendiente |

## Registro de sesiones

### Sesión 01: inventario y preservación

**Hipótesis:** podemos comprobar integridad y describir la estructura del material sin atribuir datos fisiológicos no verificados.

**Pasos:** verificar SHA-256, inspeccionar `.mvns`, identificar encabezados EMG, exportar estadísticas y gráficas locales.

**Resultados documentados desde el archivo original proporcionado:** índice XML de 291 bytes con etiqueta de sesión `EMG2_Walkig`, comentario idéntico y exactamente dos referencias: `EMG2_Squats.mvn` y `EMG2_Squats-200714130240.mvne`. Ambas entradas declaran `timeOffset=0` y `timeEndOffset=0`. Se registró discrepancia de nombre frente a `Squats`. Véase [Lección 01](lessons/01_MVNS.md).

**Ejecución en Cursor por el usuario:** pendiente. Este resumen se basa en la lectura del archivo adjunto, no en una ejecución confirmada en su PC.

**Preguntas abiertas:** ¿es caminata o sentadilla?, ¿hay exportación MVNX del movimiento?, ¿cómo fueron colocados los electrodos?, ¿es el mismo ensayo que el reporte Qualisys?

**Limitaciones:** no interpretar valores EMG como amplitud calibrada ni inferir cinemática de bytes no decodificados.
