# Observatorio de Turismo Sostenible · Guatemala

Tablero interactivo del Laboratorio 10 (CC3066 Data Science, UVG). Explora las llegadas de
visitantes internacionales a Guatemala (2009 – jun 2026) y los pronósticos de los modelos del
Laboratorio 1.

## Ejecutar

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Estructura

```
app.py                  Punto de entrada y navegación
paginas/                Una página por sección del tablero
utils/datos.py          Carga y preparación de la base (Lab1/migracion_guatemala_2009_2026.csv)
utils/modelos.py        Reproduce los 3 modelos finales del Lab 1 (sin modelos nuevos)
utils/estilo.py         Paleta, tipografía y plantilla de Plotly
docs/                   Documento de diseño
Lab1/, Lab2/            Material de los laboratorios anteriores
```

## Convenciones para agregar una página o gráfica

Todo lo compartido está en `utils/estilo.py`; úsenlo en lugar de repetir código:

| Necesito… | Uso |
|---|---|
| Dibujar una gráfica de Plotly | `mostrar_grafica(fig, key=...)`. **No usar `st.plotly_chart` directo**: Streamlit cambia el fondo y la fuente si no se fijan en la figura, y sin `automargin` se cortan los nombres de los ejes. |
| Que el usuario elija qué gráficas ver | `visibles = selector_graficas({"v7": "7. Vías", "v8": "8. Puestos"}, key="graficas_<pagina>")`, debajo del título. Luego cada gráfica va dentro de `if "v7" in visibles:`. |
| Poner gráficas lado a lado | `columnas_visibles(cantidad)`: con una sola gráfica visible usa todo el ancho; en el celular se apilan solas. |
| Nombres largos en un eje (países, puestos fronterizos) | `y=etiquetas_cortas(nombres)` y el nombre completo en el tooltip (`customdata`). |
| Encabezado de una gráfica | `encabezado_visualizacion(numero, pregunta, descripcion, uso)`. |
| Colores | Constantes `AZUL_OBSERVADO`, `VERDE_HW`, `AQUA_SARIMA`, `GRIS_REFERENCIA`, `ESCALA_AZUL`. No escribir códigos hex a mano. |

Reglas:
- Si se oculta una gráfica enlazada, la siguiente debe seguir funcionando: usar un valor por defecto
  o mostrar un control alternativo (ver V6 en `paginas/estacionalidad.py`).
- Si una selección no tiene datos, mostrar `st.info` / `st.warning` con un mensaje claro, nunca una gráfica vacía.
- No dejar etiquetas fijas pegadas al borde derecho (con `xanchor="left"` al final de la serie): en el celular se cortan.
