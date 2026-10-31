# Vista local interactiva de investigación EMG

Esta interfaz existe **únicamente en** `study/xsens-cometa-qualisys-20261030` y se ejecuta en el mismo servidor Dash del dashboard de marcha. No implica modificación ni despliegue a `main`.

## Abrir en Windows, con Cursor

En la terminal de la carpeta del laboratorio:

```powershell
cd C:\dev\kinoryx-study
git pull --ff-only
.\.venv\Scripts\python.exe -m pip install -e ".[dashboard,dev]"
.\.venv\Scripts\python.exe apps\biomechanics_dashboard\app.py
```

Abre en el navegador:
- **Dashboard de marcha existente:** http://127.0.0.1:8050/
- **Laboratorio EMG temporal:** http://127.0.0.1:8050/lab/

Hay un enlace a la vista de EMG en el encabezado del dashboard original, y un enlace de retorno dentro del laboratorio. Si el puerto 8050 ya está ocupado por un servidor anterior, detenlo con Ctrl+C en aquella terminal antes de iniciarlo.

## Display language and adaptive chart layout

**Interface language:** academic English throughout the existing gait dashboard and the temporary EMG laboratory. This includes navigation, controls, figure headings, axis captions, hover details and status messages. Muscle labels use conventional `Right/Left rectus femoris` and `Right/Left biceps femoris` wording for display only; the original labels and source bytes remain untouched.

**Figure typography and spacing:** subplot headings are wrapped and HTML-escaped, figure height and spacing between rows scale to the longest wrapped title, and a single shared EMG amplitude caption replaces the four overlapping vertical labels. Time is labeled `Relative time (s)` on the bottom row. The SVG export follows the computed figure size rather than forcing a fixed height. Headings and control text in the layout can wrap without fixed-height clipping.

**Scientific nomenclature:** `Raw EMG`, `EMG amplitude (unit not established)`, `Sampling rate`, `Relative time`, `Band-pass filter`, and `RMS amplitude`. The distinction between original, non-normalized signal and derived amplitude measures follows the CEDE consensus nomenclature. See https://cede.isek.org/method_detail/42/ and https://doi.org/10.1016/j.jelekin.2020.102438 . This does not imply physiological calibration.

## Actualización sin reinicios manuales repetidos

El servidor del worktree experimental usa **Dash hot reload y Werkzeug auto-reload**, siempre vinculado a `127.0.0.1:8050`. Cuando se actualiza un archivo Python importado por la aplicación, el proceso de desarrollo vuelve a cargar su código automáticamente. Para CSS y archivos de interfaz, Dash también intenta actualizar el navegador sin intervención. En casos aislados puede ser necesaria una recarga de la pestaña (F5), **no detener el servidor manualmente**.

Hay una única transición al activar esta capacidad desde la versión anterior con `debug=False`:

```powershell
# Solo una vez, detener el servidor antiguo con Ctrl+C.
cd C:\dev\kinoryx-study
git pull --ff-only
.\.venv\Scripts\python.exe apps\biomechanics_dashboard\app.py
```

Después, mantener esa terminal abierta mientras se investiga. En actualizaciones normales:
1. Los cambios se guardan en GitHub y se prueban primero.
2. Se hace `git pull --ff-only` desde **otra terminal** de Cursor, sin detener la que aloja Dash.
3. El servidor de desarrollo detecta cambios de código y se reinicia por sí mismo; el navegador debería refrescar el contenido. Si solo quedó la página antigua, pulsar F5.

No se garantiza que las conexiones interactivas permanezcan sin interrupción durante el reinicio automático del worker. Cambios de dependencias, instalación de paquetes o fallos del recargador pueden exigir una intervención excepcional, no un reinicio en cada cambio. La recarga automática es adecuada **solo para el desarrollo local**, nunca para publicar este laboratorio.

## Qué puede visualizar el laboratorio

1. El registro original Cometa `EMG2_Squats-200714130240.mvne`, leído desde `research/source_data`. No usa ninguna subida de archivos ni modifica el original.
2. Cuatro canales con las etiquetas proporcionadas en el XML: Rectus Femoris Right, Biceps Femoris Right, Rectus Femoris Left y Biceps Femoris Left.
3. Los 16.527 valores de cada canal a 2.000 Hz, en el orden grabado.
4. Selección de todos los canales o de uno, inicio de ventana y longitud de segmento (0,25 s, 1 s, 2 s o registro completo).
5. Interacción Plotly: zoom, desplazamiento, lectura de valores y exportación de figura SVG.
6. Dos **previsualizaciones opcionales** para comparar visualmente contra el original, siempre con paneles separados:
   - **Pasabanda exploratorio:** Butterworth de orden 4, 20 a 450 Hz, aplicación `sosfiltfilt`, sin desfase nominal en muestras interiores. Los efectos de borde no están validados.
   - **RMS exploratorio:** raíz de la media de cuadrados, ventana centrada de 250 ms con ajuste de bordes. No es RMS normalizado ni activación muscular calibrada.

La vista inicial es **Original**. Ninguna transformación se aplica automáticamente, y el usuario nunca pierde el panel original en una comparación. Los filtros no quedan aprobados para análisis de producción simplemente por poder verse aquí.

## Qué todavía NO hace

- No interpreta el binario `.mvn` como ángulos, trayectorias o eventos de marcha.
- No representa fuerza muscular, MVC, porcentaje de activación ni asimetría fisiológica.
- No comprueba unidades de amplitud o calibración.
- No prueba sincronización entre MVN, MVNE o el reporte Qualisys.
- No utiliza ni importa señales del reporte Qualisys, cuya auditoría documental independiente ya se cerró.

## Orden metodológico y aprendizaje

**Etapa 01:** observar los cuatro originales y las ventanas temporales sin activar filtros.  
**Etapa 02:** evaluar ruido y calidad de adquisición.  
**Etapa 03:** habilitar comparaciones pasabanda/RMS para entender sus efectos y estudiar métodos y parámetros.  
**Etapas posteriores:** evaluar patrones, cinemática y criterios de diseño del producto.

Por tanto, los controles de comparación se incorporaron como **herramientas didácticas opcionales** para las siguientes etapas, no como procesamiento definitivo.

## Desarrollo y pruebas

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Se incluye `tests/test_research_live_dashboard.py` con señales sintéticas para comprobar la retención de datos originales, la previsualización, ventanas y la ruta `/lab/`. El servidor escucha solo en `127.0.0.1` y no debe exponerse públicamente.

La rama es experimental y descartable; **no abrir PR, no fusionar ni trasladar automáticamente a `main`**.
