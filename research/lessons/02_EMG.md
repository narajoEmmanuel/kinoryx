# Estudio 02: entender el archivo MVNE (EMG)

> Rama de estudio exclusivamente. Los resultados son descriptivos. Nunca interpretar una amplitud de EMG como fuerza, diagnóstico o activación normalizada.

## 1. ¿Qué archivo estamos estudiando?

`research/source_data/EMG2_Squats-200714130240.mvne` es un archivo XML de señales externas asociado en el índice `.mvns`.

Encabezado comprobado directamente del archivo:
- Fuente de los cuatro canales: `Cometa`
- Frecuencia declarada: **2.000 muestras/segundo por canal**
- Número de muestras por canal: **16.527**
- Tiempo entre primera y última muestra usando esa frecuencia: `(16527 - 1) / 2000 = 8.263 s`
- El XML indica una marca de tiempo, pero no está validado su significado o zona horaria.
- El encabezado no confirma unidades de amplitud, colocación de electrodos, amplificación, filtros aplicados ni sincronización con el archivo MVN o con Qualisys.

| Canal | Nombre literal del encabezado | Fuente | Frecuencia |
| --- | --- | --- | --- |
| 0 | Rectus Femoris Right | Cometa, sourceChannel 1 | 2000 Hz |
| 1 | Biceps Femoris Right | Cometa, sourceChannel 2 | 2000 Hz |
| 2 | Rectus Femoris Left | Cometa, sourceChannel 3 | 2000 Hz |
| 3 | Biceps Femoris Left | Cometa, sourceChannel 4 | 2000 Hz |

Estos nombres son etiquetas del archivo, no confirmación independiente de la ubicación de los electrodos.

## 2. Conceptos que debemos distinguir

**Señal cruda**: la serie de valores positivos y negativos tal como está grabada. No asumir microvoltios, milivoltios ni porcentajes.

**Frecuencia de muestreo**: 2.000 Hz implica un intervalo nominal de `1/2000 = 0.0005 s`, equivalente a 0,5 ms. No es la frecuencia de contracción del músculo.

**RMS**: raíz de la media de los cuadrados. Para una ventana de N muestras, `RMS = sqrt(sum(x_i^2) / N)`. Es una estadística descriptiva de magnitud que elimina cancelación entre signos. No mide fuerza y su escala depende de la adquisición.

**Ventana temporal**: elegimos un fragmento de la captura, por ejemplo de 1,00 s a 1,25 s, y calculamos estadísticos solo sobre ese segmento. Diferentes longitudes de ventana pueden cambiar la interpretación visual.

**Artefactos**: movimientos de cables o electrodos, interferencia eléctrica, saturación y otros fenómenos pueden modificar una señal EMG. No se deben identificar artefactos específicos sin investigar las características reales de la adquisición.

## 3. Primeros experimentos en Cursor

Desde `C:\dev\kinoryx-study`:

```powershell
# Ver los cuatro canales y un resumen sin generar archivos
.\.venv\Scripts\python.exe research\lessons\02_emg.py

# Estudiar el canal 0 desde 1.0 s durante 0.25 s
.\.venv\Scripts\python.exe research\lessons\02_emg.py --channel 0 --start 1 --duration 0.25

# Guardar una gráfica local del canal 2 en la misma ventana
.\.venv\Scripts\python.exe research\lessons\02_emg.py --channel 2 --start 1 --duration 0.25 --plot

# Explorar los demás canales, sin necesidad de ZIP ni MVN
.\.venv\Scripts\python.exe research\lessons\02_emg.py --channel 1 --start 1 --duration 0.25
.\.venv\Scripts\python.exe research\lessons\02_emg.py --channel 3 --start 1 --duration 0.25
```

El gráfico se guardará en `data_local/study_output/`, que está ignorado por Git. Para generar las ocho gráficas de la captura completa se mantiene `research/study_files.py --plots`.

## 4. Preguntas de investigación

1. ¿Por qué una señal bipolar puede tener media cercana a cero y RMS alto?
2. ¿Qué cambia al observar 0,1 s, 0,25 s o 1 s?
3. ¿Qué diferencias *descriptivas* observamos entre canales y cuáles no son comparables sin calibración o normalización?
4. ¿Qué metadatos de Cometa necesitaríamos para expresar amplitudes en unidades físicas?
5. ¿Qué exportación de Xsens nos permitiría estudiar movimiento junto con EMG?

## 5. Para la futura aplicación

Un explorador seguro debería mostrar **señal original**, frecuencia, nombres de canales, ventanas temporales, origen de archivo, unidades no verificadas y advertencias claras. Antes de promover cualquier medida fisiológica hay que documentar adquisición, filtros, electrodos, normalización y validación.

Anotar hallazgos reproducibles en `research/STUDY_LOG.md` y propuestas aún no aprobadas en `research/DECISION_LOG.md`. Esta rama **no se fusionará** con `main`.
