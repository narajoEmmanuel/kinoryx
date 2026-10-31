# Bitácora del laboratorio (solo investigación)

Fecha de apertura: 2026-10-30. Rama: `study/xsens-cometa-qualisys-20261030`.

| Orden | Archivo | Conocimiento confirmado en el archivo | Incógnita a resolver | Estado |
| --- | --- | --- | --- | --- |
| 1 | `EMG2_Squats.mvns` | Índice XML v2 con referencias a MVN/MVNE y offsets declarados cero | Etiqueta `EMG2_Walkig` vs nombres `Squats`; significado de offsets en origen | Iniciar |
| 2 | `EMG2_Squats-200714130240.mvne` | 4 canales de Cometa, 2000 Hz, 16527 muestras/canal | Unidad, ganancia, filtrado, artefactos, electrodos, alineación temporal | Pendiente |
| 3 | `EMG2_Squats.mvn` | Archivo binario presente y registrado mediante SHA-256 | Formato decodificado, unidades, frames, segmentos, tiempo, ángulos | Pendiente |
| 4 | `EMG2_Squats_emg.csv` + `*.metadata.json` | Derivados locales del EMG original | Fidelidad, limitaciones de tiempo relativo y consistencia | Pendiente |
| 5 | Reporte Qualisys | URL documentada | Contenido verificable, permisos, relación con la sesión | Pendiente |

## Registro de sesiones

### Sesión 01: inventario y preservación

**Hipótesis:** podemos comprobar integridad y describir la estructura del material sin atribuir datos fisiológicos no verificados.

**Pasos:** verificar SHA-256, inspeccionar `.mvns`, identificar encabezados EMG, exportar estadísticas y gráficas locales.

**Resultados observados:** completar después de ejecutar el script en Cursor.

**Preguntas abiertas:** ¿es caminata o sentadilla?, ¿hay exportación MVNX del movimiento?, ¿cómo fueron colocados los electrodos?, ¿es el mismo ensayo que el reporte Qualisys?

**Limitaciones:** no interpretar valores EMG como amplitud calibrada ni inferir cinemática de bytes no decodificados.
