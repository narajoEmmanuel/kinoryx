# Decisiones para orientar KINORYX

Este documento es un registro de ideas y experimentos, **no** la hoja de ruta aprobada del producto.

## Candidatos a investigar

| Tema | Evidencia necesaria | Riesgo o incertidumbre | Decisión |
| --- | --- | --- | --- |
| Importar EMG de otras fuentes | Especificaciones y archivos reales de varios proveedores | Escalas/unidades y sincronización distintas | Pendiente |
| Visualizar EMG por músculo y pierna | Identidad de canales y escala reproducible | Confundir amplitud bruta con activación normalizada | Pendiente |
| Integrar cinemática Xsens | Exportación MVNX/C3D válida y contrato de ejes | Binario MVN no interpretado | Pendiente |
| Combinar cinemática y EMG | Relojes, offsets verificados y ensayo común | Correlaciones engañosas | Pendiente |
| Comparar con Qualisys | Exportación autorizada, métricas y procedencia | No sabemos si corresponde a la misma sesión | Pendiente |
| Informes para usuarios | Medidas reproducibles y verificación científica | Reportar como validado lo que solo es exploratorio | Pendiente |

## Criterio de salida del laboratorio

Cuando un experimento produzca un resultado defendible, registrar: propósito, fuente, contrato de datos, procedimiento reproducible, métricas/limitaciones y recomendaciones. Abrir *una nueva rama desde main* para su implementación si se aprueba. **Nunca fusionar directamente esta rama de estudio.**
