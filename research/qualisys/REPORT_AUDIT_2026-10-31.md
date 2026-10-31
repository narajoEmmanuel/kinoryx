# Auditoría independiente del reporte web Qualisys

**Fecha de inspección:** 2026-10-31  
**Fuente concreta:** https://report.qualisys.com/r/f8pMFlrTA/details  
**Alcance:** lectura del contenido renderizado de la pestaña del reporte en el navegador conectado, contrastada con la documentación oficial de Qualisys. **No** es una exportación de datos de origen ni una copia integral offline.  
**Estado:** CERRADO como auditoría documental de las dos vistas disponibles, `Test results` y `Findings`. No constituye una prueba completa de todas las interacciones ni una exportación de datos crudos.  
**Última comprobación:** 2026-10-31, lectura directa de `/summary` en la pestaña del usuario.  

**Regla de evidencia:** diferenciar el contenido efectivamente visible del comportamiento descrito por el fabricante y de las funcionalidades que no se probaron. No inventar curvas, extremos o valores que la inspección textual no expone.

## 1. Identificación del reporte observado

El título de la pestaña del navegador era **John Doe | Gait | Qualisys Web Report** y en el cuerpo aparecía **GaitCAST - Full body (Visual3D)**. El encabezado presentaba:

| Campo visible | Contenido tal como aparece | Notas |
| --- | --- | --- |
| Nombre | John Doe | Nombre mostrado por este reporte, no identidad verificada |
| Tipo | GaitCAST - Full body (Visual3D) | Informe de marcha, análisis de cuerpo completo |
| Fecha de evaluación | 2020-11-03 | Fecha declarada en el reporte |
| ID | 01 | Identificador mostrado, no clave técnica establecida |
| Fecha de nacimiento | 2020-11-03 | Coincide con la fecha de evaluación, no inferir edad ni corregir |
| Sexo | male | Campo mostrado |
| Peso | 75 kg | Campo mostrado |
| Estatura | 1.8 m | Campo mostrado |
| Condición de captura | Markerbased | Captura con marcadores declarada |
| GMFCS, FMS, Diagnosis | unspecified | No contiene datos interpretables en estos campos |
| Referral information | - | Sin información visible |
| Acceso | Read-only | Interfaz en modo solo lectura |
| Versión del visor | Web Report v3.23.1 | Versión visible en el pie del reporte |

**Cuidado:** «John Doe» parece ser un nombre de ejemplo, pero no se verificó la procedencia real del sujeto. No divulgar ni atribuir identidad. La coincidencia DOB/fecha de evaluación tampoco demuestra una edad.

La interfaz ofrece dos vistas diferentes:
- **Test results**: el apartado **inspeccionado** desde el enlace recibido.
- **Findings**: vista `/summary`, **inspeccionada directamente** el 2026-10-31. Presenta el encabezado `Impairments` y el mensaje literal **“There are no impairments to display yet.”** No se muestra una lista de alteraciones, prioridades, comentarios ni interpretaciones clínicas. Esto **no demuestra ausencia de alteraciones**, solo que esa sección no tiene elementos visibles en el reporte consultado.

## 2. Organización de los resultados

El reporte presenta siete grupos de resultados y un panel lateral de datos, video/3D y exportación. Los gráficos se identifican como **Highcharts 12.6.0**. Muchas curvas aparecen dentro de un lienzo dinámico: la vista textual revela títulos, ejes y algunos números, pero no entrega puntos completos de todas las curvas.

### 2.1 Lower Body Kinematics

Mide **ángulos** de segmentos y articulaciones, que en los gráficos se presentan frente a **0 %, 50 %, 100 %** del ciclo mostrado. Los ejes angulares se expresan en **grados**.

Las variables visibles son:

- **Pelvis:** Pelvic Anterior Tilt, Pelvic Up Obliquity, Pelvic Internal Rotation.
- **Cadera:** Hip Flexion, Hip Adduction, Hip Internal Rotation.
- **Rodilla:** Knee Flexion, Knee Varus, Knee Internal Rotation.
- **Tobillo:** Ankle Dorsiflexion, Ankle Inversion, Ankle Internal Rotation.
- **Pie:** Foot Pitch, Foot Internal Progression.

Los botones **Mean** y **Consistency** aparecen en la sección. La documentación del fabricante explica que el usuario puede visualizar curvas medias frente a ciclos individuales; esto sirve para distinguir patrón central y repetibilidad, pero **no se evaluó la interacción pulsando los botones en esta inspección de solo lectura**.

### 2.2 Lower Body Kinetics

Distingue tres familias, que no deben confundirse con ángulos:

**Moments** (etiquetas de eje en **Nm/kg**):
- Internal Hip Extensor Moment.
- Internal Hip Valgus Moment.
- Internal Knee Extensor Moment.
- Internal Knee Valgus Moment.
- Internal Ankle Plantarflexor Moment.
- Internal Ankle Eversion Moment.

**Power** (etiquetas de eje en **W/kg**):
- Hip Sagittal Power Generation.
- Hip Frontal Power Generation.
- Knee Sagittal Power Generation.
- Knee Frontal Power Generation.
- Ankle Sagittal Power Generation.
- Ankle Frontal Power Generation.

**Ground Reaction Force** (ejes en **N/BW**, y fase de apoyo `Stance phase`):
- Anterior GRF.
- Medial GRF.
- Vertical GRF.

Importante: los números visibles junto a los extremos de los ejes son **marcas del eje**, no picos medidos que podamos transcribir como resultados.

### 2.3 Upper Body Kinematics

Incluye:
- **Tórax respecto al laboratorio:** Thorax Anterior Tilt wrt Lab, Thorax Up Obliquity wrt Lab, Thorax Internal Rotation wrt Lab.
- **Tórax respecto a la pelvis:** Thorax Anterior Tilt wrt Pelvis, Thorax Up Obliquity wrt Pelvis, Thorax Internal Rotation wrt Pelvis.
- **Hombro:** Shoulder Flexion, Shoulder Adduction, Shoulder Internal Rotation.
- **Codo:** Elbow Flexion, Elbow Pronation.

La distinción **wrt Lab** y **wrt Pelvis** importa: compara referencias angulares diferentes. No se debe tratar todo como una misma señal sin saber el marco de referencia y convenciones.

### 2.4 Temporal & Spatial

Se recuperaron del contenido visible las siguientes cifras. Se preservan **tal cual** y **no se les asigna automáticamente** interpretación estadística adicional a `±` ni al número entre paréntesis. Algunas variables parecen mostrar resultados separados por lado, pero no fue posible leer de manera inequívoca qué cifra corresponde a qué lado.

| Variable | Valores/resumen visible |
| --- | --- |
| Stride Length (cm) | `153 ± 11 (13)` |
| Stride Width (cm) | `9 ± 1 (13)` |
| Step Length (cm) | `77 ± 6 (7)`, `76 ± 7 (9)` |
| Step Time (s) | `0.48 ± 0.013 (7)`, `0.48 ± 0.018 (9)` |
| Stance Time (%) | `61 ± 1 (7)`, `60 ± 1 (6)` |
| Initial Double Limb Support (s) | `0.1 ± 0.0095 (10)`, `0.097 ± 0.01 (9)` |
| Cadence (steps/min) | `125 ± 4 (16)` |
| Speed (m/s) | `1.60 ± 0.16 (3)` |

La vista presenta además valores por ensayo o ciclo en algunos gráficos. Los números de la tabla son textos recuperados de la interfaz, **no** recalculados desde series originales.

### 2.5 MAP

La sección se denomina **MAP**, con etiquetas:
- Gait Profile Score.
- Pelvis Tilt, Hip Fle/Ext, Knee Fle/Ext, Ankle Dor/Pla.
- Pelvis Obl, Hip Add/Abd, Pelvis Rot, Hip Rot, Foot Prog.

El gráfico muestra cifras seguidas de `±` y un número entre paréntesis; la inspección de texto no permitió vincular de forma inequívoca cada cifra a cada barra o a cada lado. **No** se atribuyen puntuaciones numéricas a categorías concretas sin una tabla accesible o exportación.

Como contexto biomecánico, el Gait Profile Score y las medidas asociadas pueden resumir desviaciones de patrones de marcha, pero la definición exacta, referencia normativa e interpretación del **MAP mostrado** requieren el protocolo y las referencias del informe. No diagnosticar a partir de esta sección.

### 2.6 EMG

En **este reporte Qualisys** figuran dos señales:
- **Left Tibialis Anterior**.
- **Right Tibialis Anterior**.

El gráfico muestra eje de amplitud en **µV** y el ciclo en porcentaje; aparecen las opciones **Mean**, **Consistency** y **raw**.

**Diferencia fundamental frente al archivo Cometa de KINORYX:** el MVNE suministrado registra **Rectus Femoris** y **Biceps Femoris** de ambos lados, no tibial anterior. Los conjuntos no deben confundirse, alinearse ni compararse como si provinieran de la misma captura.

La existencia de `raw` en la interfaz de Qualisys **no confirma** disponibilidad de exportación de muestras crudas o su frecuencia de muestreo. Tampoco se comprobó calibración o filtrado de estas señales.

### 2.7 Additional

Presenta **Hip flexion vs Knee Flexion**, gráfico **Angle-Angle** que relaciona dos medidas angulares en lugar de representar ambas exclusivamente contra el tiempo. Se muestran ejes en grados. No se extrajeron los puntos de la trayectoria.

## 3. Cómo funciona el reporte

### 3.1 Entrada y navegación

El reporte se abre por un enlace compartido en navegador, sin necesidad de instalar QTM para leerlo. Contiene navegación a **Test results** y **Findings**, además de accesos a las siete secciones. La lectura observada estaba marcada como `Read-only`.

Según la documentación oficial de Qualisys, los reportes forman parte de una plataforma de captura, procesamiento y entrega. QTM recopila información y el motor analítico puede incluir Calqulus o Visual3D según la configuración del módulo. **No** se conoce el pipeline exacto ni la versión de algoritmos que produjo esta sesión, salvo la etiqueta `Visual3D`.

### 3.2 Selección de ensayos y referencias

En **Report data** aparecen tres entradas activables con casillas:
- `Gait FB - CAST 1`.
- `Gait FB - CAST 2`.
- `Gait FB - CAST 3`.

También se ve la indicación `Hold Ctrl or Shift to select multiple items`, además de un bloque **Reference Data** que contiene `Qualisys Reference Data - Children`. Se observan textos `Markerbased vs. Markerless` y `Untitled`, pero no hay evidencia para afirmar que esa comparación específica esté calculada en esta vista ni de que la referencia «Children» sea pertinente para el sujeto.

La documentación del fabricante explica que seleccionar o deseleccionar ensayos altera las curvas y los resúmenes presentados. **Esto es una capacidad documentada del sistema; no se realizaron clics de prueba en el reporte abierto.**

### 3.3 Gráficas y comparación

Se muestran:
- Botones `Mean` y `Consistency` en cinemática, cinética, temporal/espacial y otros grupos.
- `raw` también en EMG.
- Acciones `Expand` para ampliar secciones y `Copy chart` en gráficos concretos.

Qualisys documenta la comparación de lados izquierdo/derecho, el uso de promedios o múltiples ciclos, filtrado de ensayos y sincronización de un indicador temporal con video/3D. La inspección no permite demostrar que todas esas funciones estuvieran activas simultáneamente en este reporte concreto.

### 3.4 Video y reconstrucción 3D

Se observó un panel **Video & 3D** con controles de reproducción y un deslizador temporal, además de perspectivas **Frontal** y **Sagittal**, indicación `1.0×` y botones de navegación, zoom `+` y `−`.

La documentación de Qualisys explica que el sistema puede sincronizar visualizadores, video y curvas mediante un indicador de reproducción. **No se inspeccionaron los fotogramas ni se comprobó aquí la precisión temporal de ese acoplamiento.**

### 3.5 Exportación

El panel **Export** muestra:
- Tamaño de papel **A4** o **Letter**.
- Estado **Not ready** en la inspección.
- Botón **Generate PDF**.

La plataforma admite exportaciones PDF según permisos/suscripción, pero **no se generó ni descargó PDF**, y la vista actual no demostró que el botón completara la exportación.

## 3.6 Findings, verificación final de la vista de resumen

**Acceso realmente observado:** el usuario abrió `Findings` y el navegador conectado mostró la ruta `https://report.qualisys.com/r/5fa134028746b70ebb5d8c7f/summary`. La interfaz conservó el título `John Doe | Gait | Qualisys Web Report`, la identificación GaitCAST, la fecha de evaluación y los tres ensayos del panel `Report data`. El enlace recibido originalmente usa otra cadena de ruta, `/r/f8pMFlrTA/details`; ambas vistas presentaron la misma identidad y datos visibles del reporte. No se deduce de ello la identidad externa del sujeto.

**Contenido específico de Findings:**
- Título de navegación: `Findings`.
- Apartado disponible: `Impairments`.
- Texto exacto: `There are no impairments to display yet.`
- No aparecen tarjetas ni descripciones de impairments en el contenido renderizado.
- Persisten los paneles `Report data`, `Video & 3D` y `Export`; el panel Export continúa mostrando `Not ready` y `Generate PDF`.

**Interpretación estricta:** la pestaña presenta una sección vacía, por lo que este reporte **no contiene hallazgos redactados visibles en Findings**. No equivale a un resultado clínico normal, no excluye alteraciones biomecánicas y no permite inferir cómo se generan o editan esos hallazgos.

**Qué quedó efectivamente comprobado:** apertura y lectura de las vistas `details` y `summary`. **Qué no se comprobó:** pulsar cada control, procesar/exportar el PDF, extraer los puntos internos de Highcharts, reproducir video y comprobar sincronía de fotogramas, ni analizar algoritmos privados. La auditoría documental queda cerrada con esos límites, que no deben presentarse como verificaciones efectuadas.

## 4. Diferencias entre esta web y los originales Xsens/Cometa

| Criterio | Reporte Qualisys observado | Material Xsens/Cometa en KINORYX |
| --- | --- | --- |
| Tarea etiquetada | `Gait`, cuerpo completo | `EMG2_Walkig` en índice y `Squats` en nombres |
| Análisis | Visual3D declarado | Datos brutos MVNE y binario MVN sin decodificar |
| Cinemática | Curvas angulares de múltiples articulaciones | MVN pendiente de interpretación |
| Cinética | Momentos, potencias y GRF | No disponibles en los archivos procesados |
| EMG | Tibial anterior bilateral | Recto femoral y bíceps femoral bilaterales |
| Unidades de EMG | µV en la gráfica | Unidades originales sin verificar |
| Ensayos | Tres entradas `Gait FB - CAST` | Una sesión referenciada en MVNS, sin desglose de ensayos |
| Sincronización | Plataforma permite video/3D/gráficas sincronizados | No verificada entre MVN y MVNE, ni con Qualisys |
| Salida actual | Reporte web interactivo | Resumen JSON, gráficas y scripts Python locales |

**Conclusión de procedencia:** no existe evidencia suficiente para afirmar que el enlace Qualisys y los archivos Xsens/Cometa corresponden a la misma persona, tarea, fecha o adquisición. **No se fusionan analíticamente.**

## 5. Qué podemos aprender para KINORYX sin copiar la web

Este estudio es una evaluación de producto y usabilidad, **no** una autorización para duplicar código, diseño propietario o algoritmos.

Las capacidades de referencia razonables son:
1. Organizar análisis por categorías separadas (cinemática, cinética, temporal/espacial, EMG).
2. Incorporar selección explícita de ensayo, lado y curva media/variabilidad **solo cuando los datos y el protocolo lo permitan**.
3. Mostrar unidades, ejes y procedencia al lado de las visualizaciones.
4. Proponer video, vista 3D y cursor sincronizado **únicamente después** de medir y documentar la sincronización real.
5. Conservar comparaciones, referencias y exportación como futuros requisitos, no como funciones ya implementadas.
6. Evitar métricas y puntuaciones diagnósticas si no hay normas, métodos y validación documentados.

Estas ideas son **hipótesis de diseño**, no cambios aprobados para `main`.

## 6. Alcance real, límites y verificaciones faltantes

**Se pudo inspeccionar directamente:** las vistas renderizadas **Test results** y **Findings**, incluida la sección vacía `Impairments`, además de la identidad presentada, estructura de siete grupos, nombres y unidades de gráficas, valores temporoespaciales legibles, canales EMG, lista de ensayos, panel Video & 3D, opciones de exportación y versión del visor.

**No se pudo verificar de manera completa:**
- Puntos numéricos de todas las curvas Highcharts, sus intervalos, sus picos y su tabla subyacente.
- Movimiento real de las animaciones o video y funcionamiento de cada control al hacer clic.
- Generación efectiva del PDF, descarga de datos crudos o acceso a exportación C3D/otros.
- Algoritmos concretos, convenciones angulares, filtros, referencia normativa o errores instrumentales.
- Identidad/procedencia del sujeto, consentimiento de publicación, ni relación con la sesión Xsens.
- Cualquier interpretación clínica de las curvas.

**Cierre formal:** auditoría de contenido y estructura **cerrada**, tras inspeccionar ambas vistas. **Auditoría funcional exhaustiva no realizada**, porque esta conexión solo permitió leer el contenido renderizado y no ejecutar una batería controlada de clics, descargas o validación de las curvas. Ese alcance no impide cerrar este informe de referencia, pero sí impide afirmar que todos los componentes interactivos fueron probados.

## 7. Fuentes

- Reporte concreto inspeccionado: https://report.qualisys.com/r/f8pMFlrTA/details
- Vista Findings inspeccionada directamente el 2026-10-31: https://report.qualisys.com/r/5fa134028746b70ebb5d8c7f/summary
- Plataforma oficial y descripción de funciones: https://www.qualisys.com/analysis/online-reporting/
- Módulo de Functional Assessment: https://www.qualisys.com/analysis/functional-assessment/
- Curso oficial de reportes web: https://www.qualisys.com/video-tutorials/online-web-report-course/

No se guarda una copia del HTML original, videos, ni datos personales completos fuera de esta síntesis descriptiva. El informe independiente de Qualisys no se mezcla con el estudio fisiológico de EMG.
