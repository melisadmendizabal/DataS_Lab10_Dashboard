# Laboratorio 10 – Visualización interactiva · Avance

**Observatorio de Turismo Sostenible · Guatemala**
CC3066 Data Science · Semestre II 2026 · Entrega de avance: jueves 22 de octubre de 2026

Grupo 8 

---

## 1. Usuario objetivo y propósito

El tablero está dirigido a **directivos y tomadores de decisiones del sector turístico** sin
formación en estadística. Les permite explorar la llegada de visitantes internacionales a
Guatemala (enero 2009 – junio 2026), identificar sus mercados de origen y consultar
estimaciones de los modelos del Laboratorio 1, junto con su confiabilidad y sus limitaciones.

Fuente: la base de migración usada en los Laboratorios 1 y 2
(`Lab1/migracion_guatemala_2009_2026.csv`, 161 036 registros mensuales por vía, puesto
fronterizo, país de residencia y tipo de visitante).

## 2. Preguntas de gestión seleccionadas

| # | Pregunta de gestión | Decisión que apoya | Visualizaciones |
|---|---|---|---|
| P1 | ¿Se ha recuperado la llegada de visitantes después de la pandemia? ¿Cuál es la tendencia? | Metas anuales, presupuesto de promoción | V1 |
| P2 | ¿De qué regiones y países vienen los visitantes y qué tan concentrada está la demanda? | Priorizar mercados y reducir la dependencia de pocos mercados (sostenibilidad económica) | V2, V3 |
| P3 | ¿En qué meses se concentra la demanda? | Planificar capacidad, personal y presión sobre los destinos en temporada alta (sostenibilidad ambiental y social) | V5, V6 |
| P4 | ¿Por qué vías y puestos fronterizos ingresan los visitantes? | Inversión en infraestructura y control fronterizo | V7, V8 |
| P5 | ¿Cuántos visitantes se esperan y qué tan confiables son esas estimaciones? | Uso responsable de proyecciones en la planificación | V4, V9 |

## 3. Alcance del tablero

**Incluye**
- La exploración libre de las llegadas por período, tipo de visitante, vía, región y país de residencia.
- El cambio del nivel de detalle: granularidad anual / trimestral / mensual y desglose mundo → región → país.
- Gráficas enlazadas: un período seleccionado en el tiempo actualiza las regiones, y una región seleccionada actualiza los países.
- Los resultados de los **3 modelos del Laboratorio 1** (Holt-Winters, SARIMA(0,1,1)(0,0,1,12) e ingenuo estacional) en el período de prueba, con sus errores (MAE, RMSE, MAPE) explicados en lenguaje sencillo.
- Glosario, limitaciones y una distinción explícita entre los hallazgos observados y su interpretación.

**No incluye**
- Modelos nuevos ni reentrenamiento con otras especificaciones (Boris lo mencionó).
- Gasto turístico, ocupación hotelera, duración de la estadía o motivo del viaje (no están en la base).
- Atribución de causas: el tablero muestra asociaciones en el tiempo, no efectos causales.
- Actualización automática de datos: la base es estática, hasta junio de 2026.

## 4. Paleta de colores y justificación

| Color | Hex | Significado (fijo en toda la aplicación) |
|---|---|---|
| Azul | `#2a78d6` | **Datos observados**: lo que realmente ocurrió |
| Naranja | `#eb6834` | Estimación del modelo **Holt-Winters** |
| Aqua | `#1baf7a` | Estimación del modelo **SARIMA** |
| Gris medio | `#898781` | **Referencia**: el modelo ingenuo, que es una línea base y no un modelo real |
| Gris claro | `#f0efec` | **Contexto**: la franja de pandemia y los elementos no seleccionados |
| Tinta | `#0b0b0b` / `#52514e` | Textos principales y secundarios |
| Fondo | `#f9f9f7` / `#fcfcfb` | Plano de la página y superficie de las gráficas |

**Justificación**
- **Pocos colores, cada uno con un significado.** El azul transmite confianza y neutralidad, por eso
  representa los datos reales. Los modelos usan tonos claramente distintos del azul (cálido y
  verde azulado), así el usuario distingue de inmediato *lo que pasó* de *lo que se estimó*.
  El gris quita protagonismo a lo que es solo contexto o referencia.
- **Accesibilidad para daltonismo.** Azul, naranja y aqua se validaron con una simulación de
  protanopía y deuteranopía (Machado et al., 2009), midiendo la diferencia perceptual en el espacio
  OKLab. La terna supera el umbral de separación en **todos los pares**. Se probó un cuarto color
  para el modelo ingenuo (magenta, violeta y amarillo): todos fallaron el umbral de visión normal
  frente al naranja o el azul, por eso ese modelo se muestra en gris.
- **Codificación redundante.** Además del color, cada modelo tiene su propio estilo de línea
  (continua, guiones o puntos) y una etiqueta directa al final de la línea. El aqua tiene un
  contraste menor de 3:1 sobre el fondo, y esta etiqueta lo compensa.
- **Énfasis en las gráficas enlazadas.** La barra o el período seleccionado conserva su color, y el resto se atenúa.
- **Colores no usados a propósito.** El rojo y el verde semafóricos se reservan, así que no aparecen
  como colores de series y no sugieren "bueno o malo" donde no corresponde.
- **Tema claro fijo**, con un fondo cálido casi blanco y cuadrícula tenue, para que sea legible
  en proyectores y en documentos impresos.

**Tipografía.** Se usa la sans-serif del sistema / Source Sans (la de Streamlit): alta legibilidad
en pantalla, cifras claras y una sola familia en toda la interfaz. La jerarquía es: título de página
→ pregunta de gestión numerada (h4) → descripción → nota "Para qué le sirve" en gris. Los ejes y las
leyendas van a 13–14 px.

## 5. Bosquejo de la interfaz y navegación

**Navegación** (menú lateral, agrupado por la tarea del usuario):

```
Resumen   ── Inicio                     KPIs, preguntas que responde, cómo usarlo
Explorar  ── Llegadas y mercados        V1 → V2 → V3 (enlazadas)
          └─ Estacionalidad y vías      V5 → V6, V7 → V8 (enlazadas)  [entrega final]
Estimar   ── Pronósticos de modelos     V4, V9, tabla comparativa
Ayuda     ── Glosario y limitaciones
```

**Página "Llegadas y mercados"**

```
┌───────────────┬──────────────────────────────────────────────────────────────┐
│ MENÚ          │ Llegadas y mercados de origen                                │
│ Resumen       │ [Años ════●══════●]  [Tipo de visitante ▾]  [Vía ▾]          │
│  · Inicio     │──────────────────────────────────────────────────────────────│
│ Explorar      │ 1. ¿Cómo ha evolucionado la llegada de visitantes?           │
│  · Llegadas   │ [ Anual | Trimestral | Mensual ]                             │
│  · Estacion.  │   ▲ visitantes   ░pandemia░      ┊cambio metodológico        │
│ Estimar       │   │      ___/‾‾‾\__    ░  ░   __/‾‾                          │
│  · Pronóst.   │   │ ___/           \___░__░__/      ← arrastrar = período    │
│ Ayuda         │   └──────────────────────────────────────────▶ tiempo        │
│  · Glosario   │ ✓ Período seleccionado: Ene 2015 – Dic 2019                  │
│               │──────────────────────────────────────────────────────────────│
│ Fuente: ...   │ 2. ¿De qué regiones vienen?    │ 3. ¿Qué países lideran?     │
│               │ Europa       ████████ 31 %     │ [Cantidad de países ═●═]    │
│               │ Am. Centro   ██████   24 %  ◀clic│ El Salvador ███████        │
│               │ Am. Norte    ████     18 %     │ Honduras    ████           │
│               │ ...                            │ ...                        │
└───────────────┴──────────────────────────────────────────────────────────────┘
```

**Página "Pronósticos de modelos"**

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ Pronósticos de modelos – texto: aprendieron 2009–mar 2021, evaluados 2021–26  │
│ 4. ¿Qué tan cerca estuvieron los modelos de lo que realmente pasó?           │
│ [Modelos ▾ HW, SARIMA, Ingenuo]  (○ Ver datos de aprendizaje) (○ Incertidumbre)│
│   ▲            ___── Observado (azul)                                        │
│   │      ___──‾                     ── Holt-Winters (naranja)                │
│   │ ___─‾  - - - - - - - - - - - -  -- SARIMA (aqua)                         │
│   │ · · · · · · · · · · · · · · · · ·· Ingenuo (gris)                        │
│ Tabla: Posición | Modelo | Error promedio | Error fallos grandes | Error %   │
│ Lo que muestran los datos          │ Interpretación y limitaciones           │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Principios de HCI y UX aplicados**
- **Visión general primero, luego zoom y filtro, y detalle bajo demanda** (mantra de Shneiderman):
  la página Inicio muestra los KPIs; V1 da la vista general y las selecciones bajan al detalle;
  el *tooltip* muestra la cifra exacta.
- **Filtros en una sola fila arriba de las gráficas**, y cada gráfica encabezada por la pregunta de gestión que responde.
- **Retroalimentación inmediata**: un aviso indica el período seleccionado y cómo limpiarlo. Si una
  selección no tiene datos, aparece un mensaje claro en lugar de una gráfica vacía.
- **Lenguaje no técnico**: por ejemplo, "Error promedio (visitantes/mes)" en lugar de "MAE". Los
  términos técnicos se explican en un *tooltip* y en el glosario.
- **Separación entre los hallazgos observados y la interpretación**, con bloques diferenciados en la página de pronósticos.

## 6. Herramienta seleccionada y justificación

**Python + Streamlit + Plotly** (más pandas y statsmodels).

| Criterio | Streamlit + Plotly | Dash | R Shiny | Panel / Voilà |
|---|---|---|---|---|
| Reutilizar el código y los modelos de los Lab 1–2 (Python, statsmodels) | Directo | Directo | Requiere reescribir en R | Directo |
| Velocidad de desarrollo (3 días para la entrega final) | Muy alta: script lineal | Media: *callbacks* explícitos | Media | Media |
| Gráficas enlazadas | Sí: `on_select` de Plotly devuelve la selección (puntos o caja) al script | Sí, con *callbacks* | Sí | Sí |
| Multipágina y navegación | Nativa (`st.navigation`) | Manual / *pages* | Manual | Manual |
| Caché de datos y modelos | `st.cache_data` nativo | Manual | Manual | Manual |
| Familiaridad del equipo | Alta | Baja | Baja | Baja |
| Licencia | Apache 2.0 / MIT, gratuita | MIT | GPL | BSD |

Streamlit es la opción más adecuada por cuatro razones. Primero, los modelos y la preparación de
datos ya están en Python, así que se reutilizan sin traducir. Segundo, el modelo de ejecución de
arriba hacia abajo hace que el enlace entre gráficas sea simple: la selección de una gráfica es
una variable que filtra los datos de la siguiente. Tercero, Plotly aporta *tooltips*, zoom y
selección por caja o clic sin código adicional. Cuarto, el equipo ya conoce la herramienta, lo que
reduce el riesgo en un plazo corto.

## 7. Visualizaciones: estado al avance

| # | Visualización | Tipo | Interacción | Estado |
|---|---|---|---|---|
| V1 | Evolución de las llegadas | Línea con marcadores | Granularidad A/T/M, selección de período por caja → **V2 y V3** |  Funcional |
| V2 | Visitantes por región de residencia | Barras horizontales ordenadas | Clic en una región → **V3**; se actualiza con V1 |  Funcional |
| V3 | Principales países de la región | Barras horizontales (top N) | Control de cantidad; se actualiza con V1 y V2 |  Funcional |
| V4 | Estimaciones de los modelos vs. lo observado | Líneas múltiples | Elección de modelos, histórico, banda de incertidumbre |  Funcional |
| V5 | Estacionalidad año × mes | Mapa de calor (escala de azules) | Clic en un año → V6 | Entrega final |
| V6 | Perfil mensual del año vs. el promedio | Línea | Enlazada con V5 | Entrega final |
| V7 | Visitantes por vía de ingreso | Paneles pequeños de área | Selección de vía → V8 | Entrega final |
| V8 | Principales puestos fronterizos | Barras horizontales | Enlazada con V7 | Entrega final |
| V9 | Error mensual de cada modelo | Barras / línea de error | Selección de modelos | Entrega final |

La razón de cada tipo de gráfica en el avance:
- **V1, línea:** es la forma estándar de mostrar un cambio continuo en el tiempo. Los marcadores
  permiten seleccionar períodos. La franja gris de pandemia y la línea del cambio metodológico
  dan contexto sin agregar series.
- **V2 y V3, barras horizontales ordenadas:** comparan magnitudes entre categorías sin orden
  natural. La orientación horizontal permite leer nombres largos de regiones y países. El
  porcentaje junto a cada barra responde directamente a "qué tan concentrada está la demanda".
  Se usa un solo color, porque todas las barras son la misma medida observada.
- **V4, líneas superpuestas en un solo eje:** observado y estimado están en la misma unidad, así
  que superponerlos muestra a simple vista cuánto y cuándo se desvía cada modelo.



## 8. Ejecución

```bash
pip install -r requirements.txt
streamlit run app.py
```
