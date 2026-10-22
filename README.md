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
