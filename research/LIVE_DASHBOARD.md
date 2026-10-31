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

## Pulido visual aprobado para revisión, azul oficial y legibilidad

**2026-10-31:** se mantiene el diseño y las familias tipográficas previas de KINORYX. La barra superior de Laboratory usa el azul oficial `--heading-blue: #0847A6` con textos blancos. Las cuatro etapas conservan su navegación y tienen curvas superiores más visibles, como pestañas de cuaderno. La etapa actual usa fondo azul y letras blancas, y las selecciones de controles del laboratorio siguen el mismo azul.

La tipografía de toda la interfaz web no baja de **12 px** en los estilos propios del proyecto (base de 16 px y mínimo de 0.75 rem). Las figuras Plotly de Dashboard y Laboratory declaran tamaños de texto para ejes, anotaciones y tooltips de **10 px o superiores**. No se alteró ninguna familia tipográfica ni se crearon colores nuevos.

En Home, Dashboard y Laboratory, el pie de página muestra únicamente **KINORYX**, centrado, separado por una línea discreta. El resto de controles y funciones de comparación continúa sin cambios. No modificar las medidas, las grabaciones o la rama `main`.

## Navegación compacta y vistas EMG (ajuste de interfaz)

**2026-10-31, revisión del usuario:** la cabecera de Laboratory es una barra de trabajo baja, con KINORYX a la izquierda, el nombre de la subpágina centrado, y Home/Dashboard a la derecha. Las cuatro subpestañas permanecen centradas con un borde fino, esquinas superiores suavemente redondeadas y selección discreta, como hojas de un cuaderno. Se conservan exclusivamente las variables de fuentes y colores originales del proyecto.

En **Exploratory Analysis**, el selector `Channels` restablece tres vistas sin procesar:
- `All channels` muestra los cuatro canales del XML en sus gráficas individuales, como en el laboratorio inicial.
- `Single channel` muestra un selector del canal y **una gráfica a ancho completo**.
- `Compare` habilita la biblioteca arrastrable de señales, Panel A y las opciones `Side by side`, `Stacked` y `Overlay`.

**Panel B es condicional:** no se dibuja su gráfica ni un cuadro de tamaño completo mientras esté vacío. En vista de comparación, se muestra una zona pequeña para soltar un canal en B, o se puede utilizar el botón `B` de cualquier señal. Cuando B contiene canales, aparece como un segundo panel; al quitar su última señal vuelve a ocultarse. `Reset` regresa a Panel A con solo el primer canal y B vacío. Las tres vistas comparten los controles temporales `Window` y `Start (s)`.

El modo exploratorio sigue mostrando **solo muestras originales**. El proceso de comparación de señales filtradas permanece reservado a etapas posteriores, sin alterar los datos originales ni añadir supuestos fisiológicos.

## Regla visual, corrección solicitada por el usuario

**2026-10-31:** la variante inicial del rediseño tenía exceso de bloques de texto e introdujo colores y tipografías no autorizados. Se corrigió la página \`Exploratory Analysis\` para recuperar la jerarquía anterior: título original de KINORYX, resumen \`Recording\` y controles \`View\` en una franja superior, biblioteca compacta de señales y **gráficas a ancho completo**. La navegación de cuatro etapas y las capacidades de arrastrar, comparar lado a lado, apilar o superponer siguen activas.

**Norma para cambios posteriores:** no alterar la paleta, las familias tipográficas ni la jerarquía visual establecidas en \`apps/biomechanics_dashboard/assets/workspace.css\` sin aprobación expresa. Los nuevos estilos deben reutilizar \`--page-bg\`, \`--ink\`, \`--muted\`, \`--panel-border\`, \`--left\`, \`--right\`, \`--accent\`, \`--heading-blue\`, \`--title-font\`, \`--figure-font\` y \`--copy-font\`. Las cuatro trazas reutilizan exclusivamente colores ya existentes en ese sistema, sin inventar una paleta nueva.

Reducir el texto en pantalla: dejar los detalles científicos en \`research/laboratory/\` y \`research/experiments/\`, con enlaces discretos desde la interfaz. Nunca ocultar las cuatro etapas ni eliminar los canales originales; el análisis exploratorio continúa mostrando únicamente datos crudos.

## Navegación del sistema, primer ajuste de arquitectura

A partir de esta revisión, KINORYX utiliza tres rutas en el servidor local:

| Página | Dirección | Contenido |
| --- | --- | --- |
| Home | http://127.0.0.1:8050/ | Portada mínima con accesos Laboratory y Dashboard |
| Dashboard | http://127.0.0.1:8050/dashboard/ | El dashboard de marcha anterior, sin eliminar sus controles ni sus análisis |
| Laboratory | http://127.0.0.1:8050/lab/ | Laboratorio con cuatro etapas navegables y espacio flexible de señales |

**Subpáginas reales del laboratorio:**
- `/lab/exploration`: `Exploratory Analysis`, señales crudas, biblioteca de canales, gráficos movibles y enlace al primer experimento documentado.
- `/lab/quality`: `Signal Quality Assessment`, lista metodológica y estado aún no evaluado.
- `/lab/experimentation`: `Signal Processing Experiments`, plan de comparación y parámetros pendientes de validar.
- `/lab/evaluation`: `Evaluation & Reporting`, criterios de decisión y enlace a la bitácora.

En esta iteración, solo la etapa exploratoria incluye gráficos de investigación. Las demás pantallas **no afirman análisis realizados** y servirán para colocar resultados posteriores. El informe Qualisys es una referencia documental independiente y no se confunde con los registros originales.

### Montar y organizar canales en Exploratory Analysis

Los canales originales son elementos arrastrables de `Signal library`; también se pueden agregar sin arrastrar usando `Add to A` y `Add to B` (accesible en equipos táctiles). Arrastrar un canal sobre `Panel A` o `Panel B` lo añade a esa zona. Un canal colocado se puede arrastrar al panel opuesto, y la `×` lo quita del panel sin afectar el archivo de origen. `Reset workspace` restaura la comparación inicial entre recto femoral derecho e izquierdo.

El selector `Arrangement` admite:
- `Side by side`, dos gráficos adyacentes con sus propias series.
- `Stacked`, dos gráficos uno encima del otro.
- `Overlay`, todas las series seleccionadas superpuestas en un gráfico, cada canal con su color fijo.

No se realizan transformaciones en la etapa exploratoria. Los valores reflejan las **muestras originales**, y la escala desconocida del instrumento se declara claramente. El selector de ventana permite estudiar un intervalo local de la señal. Los paneles y arreglos están guardados por pestaña/sesión en `dcc.Store`; actualizar o cambiar de etapa conserva los canales elegidos mientras dure la sesión del navegador.

**Compatibilidad:** se utiliza drag and drop HTML5 y `dash_clientside.set_props` disponible en Dash 2.16+. El proyecto declara Dash 2.17 o superior. Si el navegador no admite arrastre, los botones `Add to A/B` siguen disponibles.

**Comportamiento de trabajo:** el servidor local conserva el mecanismo de recarga automática ya configurado; evita solicitar reinicios manuales repetidos. Las rutas anteriores y la estructura nueva siguen aisladas en la rama experimental; `main` permanece intacta.

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
