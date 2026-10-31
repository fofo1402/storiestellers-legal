# PROMPT PARA CLAUDE DESIGN · Tablero interactivo "NFL 2026 · Semana 8 · Matchups"

> Copia este documento completo en Claude Design y **adjunta `data.json`** (y opcionalmente el Excel `NFL_2026_S8_matchups.xlsx` y `LEEME.txt`). Si no puedes adjuntar archivos, usa los datos de los Apéndices B a E, que son un extracto exacto de `data.json` generado por código.

---

## 1. Rol y objetivo

Eres un diseñador de producto y de visualización de datos de primer nivel, con criterio editorial deportivo. Construye un **tablero web interactivo, en español, de una sola página con navegación por pestañas**, que convierta el análisis de matchups de la Semana 8 de la NFL 2026 en algo que se entienda en 10 segundos y se pueda auditar en 10 minutos.

El usuario vive en Monterrey, México (UTC-6, sin horario de verano). Revisa el tablero desde el celular el domingo antes de los partidos y desde la computadora para profundizar. El tablero debe responder, en este orden:

1. **¿Quién tiene el matchup más favorable hoy y en qué categoría?** (yardas por tierra, recepciones, yardas recibidas, yardas por pase, acarreos, TD).
2. **¿Por qué?** Con datos: lo que permite la defensa rival a su posición, el ranking de esa defensa, la dureza de su calendario previo y la proyección ajustada.
3. **¿Qué tan confiable es?** (Alta/Media), qué la sube, qué la frena y qué regla se aplicó.
4. **¿Qué se descartó y por qué?**
5. **¿Qué puede cambiar antes del partido?** (lesiones sin verificar, recheck del domingo).

Es **análisis informativo de patrones, no consejo de apuestas.**

---

## 2. Reglas no negociables (cúmplelas todas)

1. **Cero información inventada.** Todo número, nombre, estatus o texto sale de `data.json` (o de los apéndices). Si un dato no existe, muestra "n/d". No completes huecos con conocimiento propio sobre la NFL ni sobre la temporada 2026.
2. **Métricas solo en yardas, recepciones, targets, acarreos y TD.** Nunca puntos de fantasy, PPR ni nada parecido.
3. **Nada de apuestas:** sin líneas, cuotas, spreads, totales, parlays, montos, logos ni enlaces a casas de apuestas, ni botones tipo "apostar". La probabilidad de victoria es "n/d" en todos los partidos: muéstrala así y no la estimes.
4. **Aviso visible y permanente** (en el pie de la página y en el encabezado móvil): *"Análisis de patrones, no garantía ni recomendación de apuesta. Solo mayores de 18 años."*
5. **Mismos números que el JSON.** Redondea solo al mostrar: yardas a 1 decimal, porcentajes a 1 decimal con signo (+13.9%), ranks enteros. No recalcules nada salvo en el simulador de w (sección 6.7), y ahí con la fórmula exacta.
6. **Etiqueta lo incierto.** Todo estatus de lesión que contenga "sin verificar" o "Sin reporte" lleva una etiqueta visible ("Estatus sin verificar") y un ícono. Las muestras cortas (pj ≤ 5) llevan la etiqueta "Muestra corta".
7. **Distingue hecho, estimación y juicio.** Las proyecciones son estimaciones; los bloques (a)/(b)/(c) incluyen juicio del analista. Usa microetiquetas: "Dato", "Estimación", "Juicio".
8. **Todo el texto de la interfaz va en español** (México). Los nombres de jugadores y las siglas de equipos (BAL, BUF, etc.) se quedan como vienen.
9. **Sin logos oficiales ni marcas de la NFL o de los equipos.** Usa siglas en "pastillas" tipográficas con colores neutros. No uses fotos de jugadores (aunque haya URLs disponibles en otras fuentes, no las uses).

---

## 3. Fuente de datos: estructura de `data.json`

Raíz:

| Clave | Tipo | Contenido |
|---|---|---|
| `metadatos` | objeto | `temporada` (2026), `semana` (8), `tipo_corrida` ("PRIMERA CORRIDA"), `datos_al` (texto con fecha y hora de corte), `peso_w` (0.6), `zona_horaria`, `avisos[]` (6 textos), `promedio_liga_yds_por_juego{QB,RB,WR,TE}`, `formula` (texto) |
| `partidos[]` | 13 objetos | `partido` ("BAL @ BUF"), `visitante`, `local`, `fecha_hora_monterrey` ("Dom 01-nov-2026 12:00"), `hora_et`, `estadio`, `espn_game_id`, `record_visitante`, `record_local`, `prob_victoria` ("n/d"), `decision`, `por_que`, `que_lo_puede_romper`, `conclusion`, `selecciones[]` (nombres) |
| `defensas{EQUIPO}` | 32 objetos | `pj`, `pts_permitidos_pj`, `rank_pts`, `QB_yds_pj`, `RB_yds_pj`, `WR_yds_pj`, `TE_yds_pj`, `QB_rank`…`TE_rank`, `QB_td_pj`…`TE_td_pj`, `QB_td_rank`…`TE_td_rank` |
| `calendario_jugado{EQUIPO}` | 32 objetos | `juegos[]` (`semana`, `condicion` L/V, `rival`, `pf`, `pc`, `resultado` G/P/E), `dureza{QB,RB,WR,TE}`, `dureza_vs_liga{QB,RB,WR,TE}` (fracción; positivo = sus rivales permitían MÁS que la liga = calendario fácil) |
| `equipos{EQUIPO}` | 26 objetos (equipos que juegan en S8) | `qb`, `qb_base`, `tier` (S/A/B/C/D/F, proxy), `sack`, `hit`, `rsucc`, `stuff` (fracciones), `inj_off`, `inj_def`, `trades`, `ir`, `situacion`, `dif_pts_pj`, `record` |
| `evaluados[]` | 188 objetos | `player_id`, `jugador`, `pos`, `equipo`, `rival`, `partido`, `pj`, `semanas`, totales (`att`, `cmp`, `pass_yds`, `pass_td`, `ints`, `car`, `rush_yds`, `rush_td`, `tgt`, `rec`, `rec_yds`, `rec_td`), `produccion_pj`, `rival_permite`, `rank`, `lectura`, `dureza_calendario`, `promedio_liga`, `proyeccion`, `cambio` (fracción), `tgt_pg`, `rec_pg`, `car_pg`, `lesion`, `umbral`, `vol_ok`, `dif_pg`, `dif_rival`, `gap`, `R1`, `R2`, `R3`, `R4`, `alta_modelo` (booleanos), `veredicto` ("Incluido-Alta" / "Incluido-Media" / "Descartado"), `motivo` |
| `selecciones[]` | 21 objetos | `hora_monterrey`, `partido`, `jugador`, `player_id`, `equipo`, `rival`, `pos`, `categorias`, `confianza` ("Alta"/"Media"), `rival_permite`, `rank`, `lectura`, `pts_pj_permitidos_rival`, `prob_victoria`, `por_que`, `por_que_confianza{a_sube, b_frena, c_regla}`, `riesgo`, `tier_linea`, `situacion_equipo`, `dureza_calendario`, `promedio_liga`, `produccion_pj`, `proyeccion`, `cambio`, `regla_inclusion`, `estado_lesion`, `pj` |
| `conteos` | objeto | `alta` (3), `media` (18), `total` (21) |

Notas de interpretación:
- **QB:** `produccion_pj` = yardas de pase por titularidad (solo juegos con 15+ intentos); `pj` = titularidades.
- **RB:** yardas por tierra por juego. **WR/TE:** yardas recibidas por juego.
- **`rank`:** 1 = la defensa que MÁS permite a esa posición (matchup más blando); 32 = la que menos. **`lectura`:** 1-10 "Favorable", 11-21 "Neutral", 22-32 "Difícil".
- **`cambio`** está en fracción (0.461 = +46.1%).
- El diseño debe poder leer **un `data.json` nuevo** (el recheck del domingo) sin tocar código. Si aparece una clave `cambios[]` (hoja "Cambios vs la versión anterior"), muestra la sección de cambios descrita en 6.9.

---

## 4. Metodología que el tablero debe explicar (y usar en el simulador)

**Fórmula (estimación):**

```
proyeccion = produccion_pj × (1 + w × (rival_permite ÷ dureza_calendario − 1))
cambio     = proyeccion ÷ produccion_pj − 1
w = 0.6 por defecto
```

- **rival_permite:** yardas por juego que la defensa rival permitió a esa posición en la temporada.
- **dureza_calendario:** promedio de lo que permitían a esa posición los rivales que el jugador ya enfrentó, sin contar el juego contra su propio equipo (leave-one-out). Si es mayor que el promedio de la liga, sus números pueden estar inflados por un calendario fácil, y viceversa.
- **w < 1:** lo que permite cada defensa depende a su vez de a quién enfrentó, y las muestras son de 6 a 8 juegos; por eso se toma solo el 60% de la señal.

**Umbrales de volumen:** QB ≥ 190 yds/j · RB ≥ 45 · WR ≥ 42 y ≥ 5 targets/j · TE ≥ 30.

**Reglas de inclusión:**
- **R1 base:** cambio ≥ +10% y volumen OK.
- **R2 ampliada:** rank ≤ 10, cambio ≥ +5%, producción ≥ 1.5× umbral (WR con ≥ 5 targets/j).
- **R3 RB de favorito claro (tope MEDIA):** RB, `gap` (diferencial de puntos por juego del equipo menos el del rival) ≥ 5, rank ≤ 10, cambio ≥ 0, ≥ 60 yds/j.
- **R4 volumen élite (tope MEDIA):** producción ≥ 2× umbral, cambio ≥ +5%, rank ≤ 21.
- Además se exige estar sano: se descarta a quien no practicó, está en reserva o no juega desde hace semanas sin regreso confirmado.

**Confianza:**
- **ALTA** solo si el modelo da ventaja (cambio ≥ +5%, o rank ≤ 10 con cambio ≥ 0) y además acompañan volumen, guion y salud. Es condición necesaria, no suficiente.
- **MEDIA:** ventaja con frenos (reparto de carga, muestra corta, QB suplente, línea débil, lesión o regreso de lesión) o buen volumen con matchup neutral.
- **Regla de guion (agregada en la auditoría):** QB/WR/TE de un favorito claro (brecha ≥ +10 pts/j) → máximo MEDIA.

**Fuentes y limitaciones** (muéstralas siempre en la pestaña Metodología y resumidas en un banner plegable arriba):
- ESPN no fue accesible desde el entorno de análisis (red bloqueada); la fuente principal fue nflverse (datos oficiales de juego de la NFL). Marcadores verificados: 108/108 juegos coinciden con la jugada por jugada.
- Lesiones: práctica hasta el jueves 29-oct; designaciones finales del viernes sin verificar. Seattle sin reporte S8 en la fuente.
- Probabilidad de victoria: n/d. Tier de línea ofensiva: proxy propio calculado con jugada por jugada, no PFN.
- Traspasos recientes (Q. Nelson IND→SEA 27-oct; D. Buckner IND→SF 27-oct, pendiente de examen físico; J. Simmons TEN→CHI 29-oct) confirmados vía resúmenes de búsqueda web.
- Auditoría independiente: 11 correcciones menores; Hunter Henry bajó de ALTA a MEDIA por la regla de guion.

---

## 5. Arquitectura de información

Navegación (pestañas en escritorio; barra inferior fija con íconos + texto en móvil):

1. **Hoy** (inicio)
2. **Partidos**
3. **Cara a cara**
4. **Explorador**
5. **Defensas**
6. **Calendario**
7. **Simulador**
8. **Metodología**

Encabezado global (siempre visible, compacto al hacer scroll):
- Título: "NFL 2026 · Semana 8 · Matchups favorables".
- Subtítulo: `metadatos.datos_al` + pastilla `tipo_corrida`.
- Contadores: "3 Alta · 18 Media · 21 en total" (leídos de `conteos`).
- Píldora "w = 0.60" (al tocarla lleva al Simulador).
- Banner plegable "Limitaciones de esta corrida" con los `avisos[]`.
- Aviso legal (regla 2.4).

---

## 6. Especificación de cada vista

### 6.1 Hoy (pantalla principal)
- **Línea de tiempo por horario de Monterrey**, agrupando por `hora_monterrey`: Dom 12:00 (8 partidos), 15:05, 15:25, 19:20 y Lun 19:15 (CHI @ SEA, con la etiqueta "Estatus con corte del viernes").
- **Héroe:** las 3 selecciones ALTA en tarjetas grandes arriba (Hockenson, Warren, Flowers).
- **Tarjeta de selección** (componente central; diséñalo con cuidado):
  - Fila 1: nombre del jugador · pastilla de posición · "EQUIPO vs RIVAL" (o "@") · insignia de confianza (Alta/Media).
  - Fila 2: **chips de categorías** a partir de `categorias` (separa por comas e "y"): "Yardas recibidas", "Recepciones", "TD", "Yardas por tierra", "Acarreos", "Yardas por pase", "Targets".
  - Fila 3, "barra de matchup": un indicador horizontal 1-32 con la posición del rival (`rank`), con color de `lectura` y el texto "BUF permite 173.8 yds/j a WR · rank 7/32".
  - Fila 4, "mini-puente de proyección": producción/j → proyección/j con flecha y `cambio` grande (+46.1%). Etiqueta "Estimación".
  - Fila 5: etiquetas de alerta: "Estatus sin verificar" (si `estado_lesion` contiene "sin verificar" o "Sin reporte"), "Muestra corta" (pj ≤ 5), "Regla R3/R4 (tope Media)".
  - Al expandir: `por_que` (Dato), bloque **(a) Qué la sube / (b) Qué la frena / (c) Regla aplicada** (Juicio) en tres columnas o acordeón, `riesgo`, `tier_linea`, `situacion_equipo`, `estado_lesion`, `regla_inclusion`, mini comparativo "rival permite vs dureza vs liga" (3 barras horizontales en la misma escala).
- Filtros rápidos (chips): Todas · Alta · Media · por posición (QB/RB/WR/TE) · por categoría · "Solo estatus verificado".
- Orden por defecto: hora → confianza (Alta primero) → cambio descendente. Opción de ordenar por cambio %.

### 6.2 Partidos
- 13 tarjetas (una por `partidos[]`) en orden de horario: "VISITANTE @ LOCAL", récords, hora de Monterrey, estadio, "Prob. de victoria: n/d" (en gris, con un tooltip que explique por qué no hay dato).
- Pastilla de `decision` (por ejemplo "Incluido (lado CIN)").
- Secciones: "Por qué" (`por_que`), "Qué lo puede romper" (`que_lo_puede_romper`), "Conclusión de ambos lados" (`conclusion`).
- Lista de selecciones del partido como mini-tarjetas que enlazan a la vista Hoy.
- Una nota fija abajo: "TNF CAR @ GB (19-27) ya jugado. Descansan: HOU, NO, NYG, SF."

### 6.3 Cara a cara
- Selector de partido (segmentado o desplegable).
- **Matriz espejo:** a la izquierda, la ofensiva visitante contra la defensa local; a la derecha, la ofensiva local contra la defensa visitante. Filas: QB, RB, WR, TE. Celdas: yds/j que permite la defensa (`defensas[RIVAL][POS_yds_pj]`), su rank y su lectura, coloreadas por lectura; además, el TD/j permitido y su rank en texto pequeño.
- Debajo de cada fila, los jugadores evaluados de esa posición (de `evaluados[]` filtrando por equipo y pos) con "producción → proyección (cambio)" y una insignia del veredicto.
- Pie de cada lado: tier de línea ofensiva (proxy) del equipo atacante y su QB titular (`equipos[EQ].qb`).

### 6.4 Explorador (los 188 evaluados)
- **Gráfica de dispersión principal:** eje X = `rank` del rival (1 a la izquierda, "más blando"); eje Y = `cambio` %. Tamaño = `produccion_pj` normalizado por posición (o filtra una posición a la vez). Color/forma = veredicto (Alta, Media, Descartado). Líneas de referencia: y = +10% (R1), y = +5%, x = 10 (frontera Favorable) y x = 21. Anota los 21 incluidos con su nombre; al pasar el cursor sobre los demás, muestra tooltip.
- **Tabla** con búsqueda, filtros (pos, equipo, partido, veredicto, R1-R4, lectura, "volumen OK") y orden por cualquier columna. Columnas: jugador, pos, equipo, rival, pj, producción/j, rival permite, rank, lectura, dureza, liga, proyección, cambio, targets/j, rec/j, acarreos/j, R1-R4 (como puntitos), veredicto y motivo (truncado con "ver más").
- Resalta en la tabla los 4 que cumplían regla pero se descartaron por salud o rol (Jeremiyah Love, Tyler Huntley, Breece Hall, Terry McLaurin) con la etiqueta "Cumple regla, descartado por salud/rol".

### 6.5 Defensas
- **Mapa de calor 32 × 4** (equipos × QB/RB/WR/TE) coloreado por rank (1 = más blando). Muestra el valor en yds/j dentro de cada celda. Permite cambiar a "TD/j permitidos" y a "Puntos permitidos/j".
- Ordenable por cualquier columna; resalta los 26 equipos que juegan en S8 y atenúa los que descansan (HOU, NO, NYG, SF) y los que ya jugaron el jueves (CAR, GB).
- Fila de referencia con el promedio de la liga (`metadatos.promedio_liga_yds_por_juego`).

### 6.6 Calendario (dureza)
- **Barras divergentes** por equipo con `dureza_vs_liga` para la posición elegida (selector QB/RB/WR/TE): a la derecha (+) "calendario fácil, números posiblemente inflados", a la izquierda (−) "calendario duro". Centro = promedio de la liga.
- Al tocar un equipo: lista de `juegos[]` con semana, L/V, rival, marcador y resultado (G/P/E), más su récord.
- Texto guía con el ejemplo del usuario: "Un equipo que pasó por rivales fáciles y ahora enfrenta uno fuerte no debe valorarse por números inflados".

### 6.7 Simulador de w
- Control deslizante w de 0.00 a 1.00 (paso 0.05; valor inicial `metadatos.peso_w`) y botón "Volver a 0.60".
- Recalcula en vivo, para los 188 evaluados, `proyeccion` y `cambio` con la fórmula exacta, y R1, R2 y R4 con los umbrales de la sección 4. R3 usa cambio ≥ 0 y `gap`, que no depende de w; recalcula solo su condición de cambio.
- Muestra: (1) cuántos jugadores cumplen alguna regla con el w actual frente a w = 0.6; (2) una lista "Entrarían / Saldrían por regla" respecto de w = 0.6.
- **Advertencia fija:** "Los veredictos y textos se definieron con w = 0.60 e incluyen juicio del analista (salud, guion, reparto). El simulador solo muestra la sensibilidad del modelo; no cambia la confianza oficial."
- Gráfica pequeña: cambio % de las 21 selecciones vs w (líneas finas, resaltando la seleccionada).

### 6.8 Metodología
- Fórmula renderizada, glosario (producción/j, rival permite, rank, lectura, dureza, liga, w, gap, R1-R4, ALTA/MEDIA, regla de guion, tier proxy de línea), fuentes y limitaciones (sección 4), registro de la auditoría (11 correcciones; Henry Alta→Media), y el aviso legal.
- Diagrama de flujo simple: Datos → Defensa vs posición → Dureza (leave-one-out) → Proyección → Reglas R1-R4 → Filtro de salud → Confianza (Alta/Media) → Selección.

### 6.9 Modo RECHECK (preparado aunque hoy no se use)
- Si `metadatos.tipo_corrida` = "RECHECK" o existe `cambios[]`, aparece una pestaña o banner "Cambios vs la versión anterior": entradas (verde), salidas (gris tachado), cambios de confianza (flecha ↑/↓), cada una con su motivo.
- En las tarjetas de selección, una insignia "Nuevo", "Subió" o "Bajó".
- El partido del lunes muestra "con estatus del viernes" hasta que haya inactivos (~17:45 del lunes, hora Monterrey).

---

## 7. Lenguaje visual

- **Tono:** editorial deportivo sobrio, tipo panel de análisis de una cadena seria; nada de estética de casino ni de casas de apuestas (sin neón verde/dorado, sin fichas ni dados).
- **Tema:** claro por defecto con modo oscuro opcional; ambos con contraste AA como mínimo.
- **Tipografía:** sans de alta legibilidad para números (cifras tabulares). Jerarquía: nombre del jugador grande y en negritas, número clave (cambio %) muy grande, contexto en tamaño pequeño.
- **Semántica de color** (no dependas solo del color: usa también ícono y texto):
  - Confianza: Alta = verde profundo con ícono ●●; Media = ámbar con ●○; Descartado = gris.
  - Lectura del matchup: Favorable = azul intenso; Neutral = gris azulado; Difícil = naranja quemado. Evita el par rojo/verde para el matchup, pensando en daltonismo.
  - Cambio %: escala divergente centrada en 0 (positivo azul, negativo naranja).
  - Estatus sin verificar: ícono de reloj o de alerta en ámbar con texto.
- **Chips de categoría** con íconos lineales simples: tierra (flecha horizontal), recepción (manos o balón), yardas por pase (trayectoria), TD (bandera o zona de anotación), acarreos (contador).
- **Densidad:** tarjetas aireadas en "Hoy"; tablas densas pero legibles en "Explorador".
- **Movimiento:** transiciones breves (150-250 ms) al expandir tarjetas y al filtrar; respeta "reducir movimiento".

---

## 8. Responsivo y accesibilidad

- **Móvil primero** (360-430 px): tarjetas a una columna, barra de navegación inferior, encabezado compacto con los contadores, matriz Cara a cara apilada (visitante arriba, local abajo), Explorador con la tabla en modo "lista de tarjetas" y la dispersión en pantalla completa con zoom.
- **Escritorio** (≥ 1280 px): Hoy en 2-3 columnas; panel lateral de detalle al seleccionar una tarjeta.
- Navegable con teclado, foco visible, etiquetas ARIA en gráficas (resumen textual de cada gráfica), tooltips accesibles también por toque.
- Formato numérico es-MX: punto decimal y separador de miles con coma; porcentajes con signo; horas en 24 h con "h" opcional (12:00).

---

## 9. Estados y casos borde

- Carga, vacío ("No hay selecciones con estos filtros") y error de lectura del JSON (mensaje claro y sin inventar datos).
- Textos largos (`situacion_equipo`, `riesgo`): trunca a 3 líneas con "ver más".
- `null`, "n/d" o campos ausentes: muestra "n/d" en gris.
- Jugadores con `pj` ≤ 5: etiqueta "Muestra corta".
- Equipos sin reporte (SEA): etiqueta "Sin reporte S8".

---

## 10. Criterios de aceptación (verifícalos antes de entregar)

1. Los contadores muestran **3 Alta, 18 Media, 21 total**.
2. Las 3 ALTA son **T.J. Hockenson (MIN @ DET, +46.1%)**, **Jaylen Warren (CLE @ PIT, local PIT, +10.8%)** y **Zay Flowers (BAL @ BUF, +7.5%)**.
3. Hunter Henry aparece como **Media** (+34.1%).
4. Las cifras de cada tarjeta coinciden con la tabla del Apéndice B (producción, rival permite, rank, dureza, proyección, cambio).
5. Hay 13 partidos; CHI @ SEA es el lunes 02-nov a las 19:15 hora Monterrey; los demás son el domingo 01-nov a las 12:00, 15:05, 15:25 o 19:20.
6. En ningún lugar aparecen líneas, cuotas, spreads, parlays, PPR, fantasy ni probabilidades inventadas; "Prob. de victoria" = n/d en los 13 partidos.
7. El aviso legal está visible en todas las vistas.
8. Con w = 0.60, el simulador reproduce exactamente `proyeccion` y `cambio` del JSON (diferencia < 0.05 al mostrar con 1 decimal).
9. Todo estatus "sin verificar" está etiquetado.
10. La vista Defensas ordena por rank con 1 = la que más permite.

---

## 11. Entregables que te pido

1. El prototipo interactivo funcional, conectado a `data.json` (o, si no es posible, con los datos de los apéndices incrustados en un único objeto JSON dentro del código, sin modificar valores).
2. Una hoja breve de sistema de diseño: colores con su significado, tipografía, componentes (tarjeta de selección, barra de matchup, chip de categoría, insignia de confianza, celda de mapa de calor) y estados.
3. Variantes de la tarjeta de selección: compacta (lista), estándar (Hoy) y expandida (detalle).
4. Una captura o vista de móvil y otra de escritorio de "Hoy".

No agregues funciones de apuestas, de registro de usuarios ni de compartir en redes. No uses datos externos.

---


## APÉNDICE A · Resumen ejecutivo del análisis (contexto integrado)

- Corte: viernes 30-oct-2026, 17:10 hora Monterrey (UTC-6) · PRIMERA CORRIDA · w = 0.6 · zona: America/Monterrey (UTC-6).
- Promedio de la liga (yds por juego de defensa): QB 235.1 · RB 91.5 · WR 148.7 · TE 53.8.
- Selecciones: 3 Alta, 18 Media, 21 en total, sobre 188 jugadores evaluados de los 26 equipos que juegan en S8.
- Patrón principal: los TE contra defensas débiles ante su posición (DET, MIA, WAS, DEN) dan los ajustes más altos; los receptores de IND contra JAX (la defensa que más permite a WR); por tierra, LV es la defensa que más permite a RB.
- Lados sin selección: TEN, DET, JAX, LV, CLE, ATL, LAC, DEN, MIA y CHI (CHI enfrenta a SEA, la defensa que menos permite a QB, WR y TE).
- Pendiente para el recheck (domingo 10:40, Monterrey): inactivos oficiales; estatus de Lamar Jackson, Kelce, Michael Wilson, Breece Hall, DeVonta Smith/Wicks, Egbuka y la DL de NYJ; vigilar a Tuten, Nacua y Rachaad White.
- Avisos de la corrida:
  - Análisis de patrones, no garantía ni recomendación de apuesta. Solo mayores de 18 años.
  - ESPN no fue accesible desde el entorno (red bloqueada); fuente principal: nflverse (datos oficiales de juego de la NFL).
  - Estatus de lesiones: práctica hasta el jueves 29-oct; designaciones finales del viernes sin verificar. SEA sin reporte S8 en la fuente.
  - Probabilidad de victoria: n/d (sin fuente accesible; no se usan líneas de apuestas).
  - Tier de línea ofensiva: proxy propio calculado con play-by-play (no PFN).
  - Los textos explicativos se calcularon con w = 0.6.

## APÉNDICE B · Las 21 selecciones (extracto exacto de `selecciones[]`)

| # | Hora MTY | Partido | Jugador | Eq | Rival | Pos | Categorías | Conf. | Prod/j | Rival permite | Rank | Lectura | Dureza | Liga | Proy/j | Cambio | PJ | Regla | Tier línea |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Dom 01-nov-2026 12:00 | ARI @ DAL | Michael Wilson | ARI | DAL | WR | Recepciones (targets) y yardas recibidas | Media | 53.6 | 163.1 | 9 | Favorable | 132.5 | 148.7 | 61.0 | +13.9% | 7 | R1 (base) | C |
| 2 | Dom 01-nov-2026 12:00 | ARI @ DAL | Javonte Williams | DAL | ARI | RB | Yardas por tierra, acarreos y TD | Media | 67.4 | 103.6 | 10 | Favorable | 90.1 | 91.5 | 73.5 | +9.0% | 7 | R3 (RB de favorito claro) | S |
| 3 | Dom 01-nov-2026 12:00 | ATL @ TB | Baker Mayfield | TB | ATL | QB | Yardas por pase | Media | 205.0 | 271.4 | 4 | Favorable | 220.7 | 235.1 | 233.3 | +13.8% | 3 | R1 (base) | B |
| 4 | Dom 01-nov-2026 12:00 | BAL @ BUF | Zay Flowers | BAL | BUF | WR | Recepciones, yardas recibidas y TD | Alta | 101.3 | 173.8 | 7 | Favorable | 154.5 | 148.7 | 109.0 | +7.5% | 6 | R2 y R4 | C |
| 5 | Dom 01-nov-2026 12:00 | BAL @ BUF | Lamar Jackson | BAL | BUF | QB | Yardas por pase (y TD por pase) | Media | 241.8 | 298.7 | 2 | Favorable | 236.5 | 235.1 | 279.9 | +15.8% | 4 | R1 (base) | C |
| 6 | Dom 01-nov-2026 12:00 | BAL @ BUF | Khalil Shakir | BUF | BAL | WR | Recepciones y yardas recibidas | Media | 48.3 | 181.6 | 5 | Favorable | 153.7 | 148.7 | 53.6 | +10.9% | 6 | R1 (base) | A |
| 7 | Dom 01-nov-2026 12:00 | CLE @ PIT | Jaylen Warren | PIT | CLE | RB | Yardas por tierra y acarreos (y recepciones como extra) | Alta | 80.1 | 104.0 | 9 | Favorable | 88.2 | 91.5 | 88.8 | +10.8% | 7 | R1 y R2 | C |
| 8 | Dom 01-nov-2026 12:00 | IND @ JAX | Keenan Allen | IND | JAX | WR | Recepciones y yardas recibidas | Media | 43.0 | 210.0 | 1 | Favorable | 159.4 | 148.7 | 51.2 | +19.0% | 6 | R1 (base) | B |
| 9 | Dom 01-nov-2026 12:00 | IND @ JAX | Josh Downs | IND | JAX | WR | Recepciones y yardas recibidas | Media | 43.9 | 210.0 | 1 | Favorable | 161.1 | 148.7 | 51.8 | +18.2% | 7 | R1 (base) | B |
| 10 | Dom 01-nov-2026 12:00 | LV @ NYJ | Braelon Allen | NYJ | LV | RB | Yardas por tierra, acarreos y TD | Media | 59.7 | 124.9 | 1 | Favorable | 92.4 | 91.5 | 72.3 | +21.1% | 7 | R1 (base) | F |
| 11 | Dom 01-nov-2026 12:00 | MIN @ DET | T.J. Hockenson | MIN | DET | TE | Yardas recibidas, recepciones y TD | Alta | 39.5 | 100.3 | 1 | Favorable | 56.7 | 53.8 | 57.7 | +46.1% | 6 | R1 (base) | D |
| 12 | Dom 01-nov-2026 12:00 | MIN @ DET | Kyler Murray | MIN | DET | QB | Yardas por pase (y TD por pase) | Media | 198.5 | 312.3 | 1 | Favorable | 243.0 | 235.1 | 232.5 | +17.1% | 4 | R1 (base) | D |
| 13 | Dom 01-nov-2026 12:00 | MIN @ DET | Justin Jefferson | MIN | DET | WR | Yardas recibidas y recepciones | Media | 60.4 | 186.8 | 3 | Favorable | 149.8 | 148.7 | 69.4 | +14.8% | 5 | R1 (base) | D |
| 14 | Dom 01-nov-2026 12:00 | TEN @ CIN | Chase Brown | CIN | TEN | RB | Yardas por tierra, acarreos y recepciones | Media | 47.5 | 104.9 | 7 | Favorable | 78.5 | 91.5 | 57.1 | +20.1% | 6 | R1 (base) | B |
| 15 | Dom 01-nov-2026 12:00 | TEN @ CIN | Tee Higgins | CIN | TEN | WR | Yardas recibidas y recepciones | Media | 95.2 | 175.6 | 6 | Favorable | 157.5 | 148.7 | 101.7 | +6.9% | 6 | R2 y R4 | B |
| 16 | Dom 01-nov-2026 15:05 | LAC @ LA | Kyren Williams | LA | LAC | RB | Yardas por tierra, acarreos y recepciones | Media | 70.3 | 104.8 | 8 | Favorable | 98.7 | 91.5 | 72.9 | +3.7% | 7 | R3 (RB de favorito claro) | S |
| 17 | Dom 01-nov-2026 15:25 | KC @ DEN | Travis Kelce | KC | DEN | TE | Yardas recibidas y recepciones | Media | 57.2 | 65.3 | 8 | Favorable | 50.6 | 53.8 | 67.1 | +17.4% | 6 | R1 y R2 | A |
| 18 | Dom 01-nov-2026 15:25 | NE @ MIA | Hunter Henry | NE | MIA | TE | Yardas recibidas, recepciones y TD | Media | 42.3 | 74.7 | 4 | Favorable | 47.6 | 53.8 | 56.7 | +34.1% | 7 | R1 (base) | C |
| 19 | Dom 01-nov-2026 19:20 | PHI @ WAS | Dallas Goedert | PHI | WAS | TE | Recepciones, yardas recibidas y TD | Media | 45.6 | 73.5 | 5 | Favorable | 48.0 | 53.8 | 60.2 | +32.0% | 5 | R1 y R2 | D |
| 20 | Dom 01-nov-2026 19:20 | PHI @ WAS | Stefon Diggs | WAS | PHI | WR | Recepciones (targets) y yardas recibidas | Media | 42.8 | 184.0 | 4 | Favorable | 139.1 | 148.7 | 51.1 | +19.4% | 5 | R1 (base) | C |
| 21 | Lun 02-nov-2026 19:15 | CHI @ SEA | Jaxon Smith-Njigba | SEA | CHI | WR | Recepciones, yardas recibidas y targets | Media | 123.9 | 149.4 | 16 | Neutral | 132.2 | 148.7 | 133.6 | +7.8% | 7 | R4 (volumen élite) | D |

### B.2 Textos de cada selección

**1. Michael Wilson (ARI vs DAL) · Media**
- Por qué (dato): 53.6 yds recibidas/j en 7 PJ (5.3 rec y 9.4 targets/j, 1 TD). DAL permite 163.1 yds/j a WR (rank 9/32, Favorable). Calendario previo: sus rivales permitían 132.5 vs 148.7 de la liga. Proyección ajustada 61.0 (+13.9%) con w = 0.6.
- (a) Qué la sube: DAL permite 163.1 yds/j a WR (rank 9). ARI es no favorito claro (dif. -9.4 vs +1.3) → pasa mucho (Brissett ~40 intentos/j). Wilson recibe 9.4 targets/j. Ajuste +13.9%.
- (b) Qué la frena: Costillas: practicó limitado el jueves (designación final sin verificar). Solo 5.7 yds/target. McBride acapara 11.1 targets/j.
- (c) Regla aplicada: Modelo con ventaja (+13.9%, rank 9), pero lesión en curso e ineficiencia → MEDIA.
- Riesgo: Que juegue mermado o quede fuera.
- Estado de lesión: Práctica jue 29-oct: Limitado (Ribs); designación final sin verificar
- Pts/j que permite el rival: 25.7 · Prob. de victoria: n/d

**2. Javonte Williams (DAL vs ARI) · Media**
- Por qué (dato): 67.4 yds por tierra/j en 7 PJ (15.7 acarreos, 2.7 rec/j, 9 TD). ARI permite 103.6 yds/j a RB (rank 10/32, Favorable). Calendario previo: sus rivales permitían 90.1 vs 91.5 de la liga. Proyección ajustada 73.5 (+9.0%) con w = 0.6.
- (a) Qué la sube: ARI permite 103.6 yds/j a RB (rank 10); su DT Walter Nolen no practicó. DAL es favorito claro (dif. +1.3 vs -9.4). Javonte: 15.7 acarreos/j, 8 TD terrestres, 155 yds en S7. Línea DAL tier proxy S.
- (b) Qué la frena: Ajuste +9.0% (< +10%). 4.3 yds/acarreo.
- (c) Regla aplicada: Modelo con ventaja (≥ +5%, rank 10), pero entra por R3 (tope MEDIA).
- Riesgo: Que DAL resuelva por aire con Lamb/Pickens.
- Estado de lesión: No figura en el reporte de práctica del jue 29-oct
- Pts/j que permite el rival: 29.7 · Prob. de victoria: n/d

**3. Baker Mayfield (TB vs ATL) · Media**
- Por qué (dato): 205.0 yds de pase/j en 3 titularidades (2 TD, 2 INT). ATL permite 271.4 yds/j a QB (rank 4/32, Favorable). Calendario previo: sus rivales permitían 220.7 vs 235.1 de la liga. Proyección ajustada 233.3 (+13.8%) con w = 0.6. Muestra corta (≤ 5 PJ).
- (a) Qué la sube: ATL permite 271.4 yds de pase/j (rank 4) y su secundaria trae 4 CB limitados (A.J. Terrell, Henderson, Bowman, Avieon Terrell). Practicó completo (pulgar). Ajuste +13.8%.
- (b) Qué la frena: Muestra corta: 3 titularidades completas (S7 solo 11 intentos tras regresar). Egbuka limitado (conmoción) y RT Goedeke no practicó.
- (c) Regla aplicada: Modelo con ventaja (+13.8%, rank 4), pero muestra corta y regreso de lesión → MEDIA.
- Riesgo: Volumen bajo si TB domina por tierra.
- Estado de lesión: Práctica jue 29-oct: Completo (Thumb); designación final sin verificar; S7: Questionable (Thumb)
- Pts/j que permite el rival: 24.7 · Prob. de victoria: n/d

**4. Zay Flowers (BAL vs BUF) · Alta**
- Por qué (dato): 101.3 yds recibidas/j en 6 PJ (6.7 rec y 8.8 targets/j, 3 TD). BUF permite 173.8 yds/j a WR (rank 7/32, Favorable). Calendario previo: sus rivales permitían 154.5 vs 148.7 de la liga. Proyección ajustada 109.0 (+7.5%) con w = 0.6.
- (a) Qué la sube: BUF permite 173.8 yds/j a WR (rank 7/32) y es la defensa que más TD permite a WR (1.83 por juego, rank 1). Volumen élite: 8.8 targets y 6.7 rec/j. BAL llega como no favorito (dif. +0.3 vs +4.3 pts/j) → guion de más pases. Su producción no depende del QB: 137 yds con Huntley en S7.
- (b) Qué la frena: Lamar regresa de esguince alto (designación final sin verificar). Línea BAL con tier proxy C. Ajuste +7.5% (debajo del +10% base).
- (c) Regla aplicada: Modelo con ventaja (ajuste ≥ +5% y rank ≤ 10) + volumen élite + guion de pase + receptor sano → ALTA. Entra por regla ampliada R2.
- Riesgo: Si Lamar no juega o se le limita la movilidad, baja la calidad de los envíos profundos.
- Estado de lesión: No figura en el reporte de práctica del jue 29-oct
- Pts/j que permite el rival: 28.5 · Prob. de victoria: n/d

**5. Lamar Jackson (BAL vs BUF) · Media**
- Por qué (dato): 241.8 yds de pase/j en 4 titularidades (6 TD, 1 INT). BUF permite 298.7 yds/j a QB (rank 2/32, Favorable). Calendario previo: sus rivales permitían 236.5 vs 235.1 de la liga. Proyección ajustada 279.9 (+15.8%) con w = 0.6. Muestra corta (≤ 5 PJ).
- (a) Qué la sube: BUF permite 298.7 yds de pase/j a QB (rank 2) y 2.50 TD de pase/j (rank 2). Lamar promedió 241.8 yds/j en 4 titularidades. BAL no favorito → más pases. Practicó completo el jueves (tobillo).
- (b) Qué la frena: Regresa de esguince alto de tobillo (no juega desde la S4; fuera S5-S7). Muestra corta (4 PJ). Línea tier proxy C. Designación final del viernes sin verificar.
- (c) Regla aplicada: Modelo con ventaja (+15.8%, rank 2), pero regreso de lesión y muestra corta → MEDIA.
- Riesgo: Que no juegue (entraría Huntley) o que juegue limitado.
- Estado de lesión: Práctica jue 29-oct: Completo (Ankle); designación final sin verificar; S7: Out (Ankle)
- Pts/j que permite el rival: 28.5 · Prob. de victoria: n/d

**6. Khalil Shakir (BUF vs BAL) · Media**
- Por qué (dato): 48.3 yds recibidas/j en 6 PJ (3.7 rec y 5.3 targets/j, 1 TD). BAL permite 181.6 yds/j a WR (rank 5/32, Favorable). Calendario previo: sus rivales permitían 153.7 vs 148.7 de la liga. Proyección ajustada 53.6 (+10.9%) con w = 0.6.
- (a) Qué la sube: BAL permite 181.6 yds/j a WR (rank 5); su secundaria llega mermada (S Jaylinn Hawkins no practicó; Kyle Hamilton y Roquan Smith limitados). Ajuste +10.9% con Josh Allen sano.
- (b) Qué la frena: Reparto de targets en BUF (Coleman, DJ Moore, Kincaid): Shakir promedia 5.3 targets/j; techo moderado (48.3 yds/j).
- (c) Regla aplicada: Modelo con ventaja (+10.9%, rank 5), pero el reparto de targets frena → MEDIA.
- Riesgo: Que el volumen se vaya a Coleman/Moore o a la carrera de Cook.
- Estado de lesión: No figura en el reporte de práctica del jue 29-oct
- Pts/j que permite el rival: 23.9 · Prob. de victoria: n/d

**7. Jaylen Warren (PIT vs CLE) · Alta**
- Por qué (dato): 80.1 yds por tierra/j en 7 PJ (14.6 acarreos, 3.4 rec/j, 2 TD). CLE permite 104.0 yds/j a RB (rank 9/32, Favorable). Calendario previo: sus rivales permitían 88.2 vs 91.5 de la liga. Proyección ajustada 88.8 (+10.8%) con w = 0.6.
- (a) Qué la sube: CLE permite 104.0 yds/j a RB (rank 9). Warren: 80.1 yds/j, 14.6 acarreos y 4.9 targets/j, con 4 juegos de 90+ yds. El frente de CLE practicó limitado el jueves (Verse, Graham, Hall Jr., Schwesinger). PIT juega en casa con mejor diferencial (+2.1 vs -1.9).
- (b) Qué la frena: Rico Dowdle le quita ~7.8 acarreos/j cuando juega; línea PIT tier proxy C; CLE permite pocos TD terrestres a RB (rank 21).
- (c) Regla aplicada: Modelo con ventaja (+10.8%, rank 9 favorable) + volumen alto + guion neutral-favorable + sano → ALTA.
- Riesgo: Partido cerrado entre equipos 5-2 que se vuelva de pases, o reparto mayor con Dowdle.
- Estado de lesión: No figura en el reporte de práctica del jue 29-oct
- Pts/j que permite el rival: 20.9 · Prob. de victoria: n/d

**8. Keenan Allen (IND vs JAX) · Media**
- Por qué (dato): 43.0 yds recibidas/j en 6 PJ (4.8 rec y 7.2 targets/j, 1 TD). JAX permite 210.0 yds/j a WR (rank 1/32, Favorable). Calendario previo: sus rivales permitían 159.4 vs 148.7 de la liga. Proyección ajustada 51.2 (+19.0%) con w = 0.6.
- (a) Qué la sube: JAX permite 210.0 yds/j a WR (rank 1). Allen recibe 7.2 targets/j (el más alto entre los WR de IND). IND no favorito → pasa. Ajuste +19.0%.
- (b) Qué la frena: Mismo QB ineficiente; IND perdió a Nelson (OL); 43.0 yds/j apenas sobre el umbral; correlacionado con Downs.
- (c) Regla aplicada: Modelo con ventaja (+19.0%, rank 1), con frenos de QB y línea → MEDIA.
- Riesgo: Si Tyler Warren (TE) juega sano, le quita targets.
- Estado de lesión: No figura en el reporte de práctica del jue 29-oct
- Pts/j que permite el rival: 17.3 · Prob. de victoria: n/d

**9. Josh Downs (IND vs JAX) · Media**
- Por qué (dato): 43.9 yds recibidas/j en 7 PJ (3.7 rec y 6.6 targets/j, 0 TD). JAX permite 210.0 yds/j a WR (rank 1/32, Favorable). Calendario previo: sus rivales permitían 161.1 vs 148.7 de la liga. Proyección ajustada 51.8 (+18.2%) con w = 0.6.
- (a) Qué la sube: JAX es la defensa que más yardas permite a WR (210.0/j, rank 1); S Antonio Johnson no practicó. IND no favorito (dif. -3.7 vs +8.3) → guion de pase. 6.6 targets/j. Ajuste +18.2%.
- (b) Qué la frena: Daniel Jones rinde poco (5.8 yds/intento). IND traspasó a Quenton Nelson (OL) el 27-oct (y a DeForest Buckner, DL, pendiente de examen físico según AP). Reparto con K. Allen y Warren. Ningún juego de 80+ yds.
- (c) Regla aplicada: Modelo con ventaja (+18.2%, rank 1), pero QB ineficiente y equipo en desmantelamiento → MEDIA.
- Riesgo: Producción repartida. Según AP (27-oct), IND podría ofrecer a Downs antes de la fecha límite de traspasos (sin confirmar).
- Estado de lesión: No figura en el reporte de práctica del jue 29-oct
- Pts/j que permite el rival: 17.3 · Prob. de victoria: n/d

**10. Braelon Allen (NYJ vs LV) · Media**
- Por qué (dato): 59.7 yds por tierra/j en 7 PJ (13.0 acarreos, 2.1 rec/j, 2 TD). LV permite 124.9 yds/j a RB (rank 1/32, Favorable). Calendario previo: sus rivales permitían 92.4 vs 91.5 de la liga. Proyección ajustada 72.3 (+21.1%) con w = 0.6.
- (a) Qué la sube: LV es la defensa que más yardas permite a RB (124.9/j, rank 1) y está entre las que más TD terrestres conceden (1.00/j, rank 4). Allen promedió 19.3 acarreos y 99.3 yds en S5-S7 como titular. Ajuste +21.1%.
- (b) Qué la frena: Breece Hall (cuádriceps) practicó limitado y podría volver a repartir (inactivo S4-S7). Línea NYJ tier proxy F (T Max Mitchell no practicó).
- (c) Regla aplicada: Modelo con ventaja (+21.1%, rank 1), pero posible reparto con Hall y línea débil → MEDIA.
- Riesgo: Regreso de Hall con carga relevante.
- Estado de lesión: Práctica jue 29-oct: Completo (Ankle); designación final sin verificar
- Pts/j que permite el rival: 28.1 · Prob. de victoria: n/d

**11. T.J. Hockenson (MIN vs DET) · Alta**
- Por qué (dato): 39.5 yds recibidas/j en 6 PJ (4.5 rec y 5.3 targets/j, 2 TD). DET permite 100.3 yds/j a TE (rank 1/32, Favorable). Calendario previo: sus rivales permitían 56.7 vs 53.8 de la liga. Proyección ajustada 57.7 (+46.1%) con w = 0.6.
- (a) Qué la sube: DET es la defensa que más yardas (100.3/j, rank 1) y más TD (1.67/j, rank 1) permite a TE. Ajuste +46.1%. Hockenson es el 2.º en targets de MIN (5.3/j) y está fuera del reporte de lesiones. Kyler Murray sano.
- (b) Qué la frena: MIN lanza poco (defensa élite, permite 12.3 pts/j) y su línea (tier proxy D) concede 9% de capturas. Producción irregular (S4: 119 yds; S5: 7 yds).
- (c) Regla aplicada: Modelo con ventaja muy amplia (+46.1%, rank 1 en yardas y TD a TE), volumen ≥ 30 yds/j, sano, QB titular sano; brecha de guion +5.3 (< +10, no aplica freno de favorito). JUICIO: el bajo volumen de pase de MIN frena a Jefferson y Kyler (+15/17%), pero en Hockenson la magnitud del matchup lo compensa → ALTA.
- Riesgo: Que MIN controle con la carrera y lance menos de 25 pases.
- Estado de lesión: No figura en el reporte de práctica del jue 29-oct
- Pts/j que permite el rival: 27.5 · Prob. de victoria: n/d

**12. Kyler Murray (MIN vs DET) · Media**
- Por qué (dato): 198.5 yds de pase/j en 4 titularidades (3 TD, 1 INT). DET permite 312.3 yds/j a QB (rank 1/32, Favorable). Calendario previo: sus rivales permitían 243.0 vs 235.1 de la liga. Proyección ajustada 232.5 (+17.1%) con w = 0.6. Muestra corta (≤ 5 PJ).
- (a) Qué la sube: DET es la defensa que más yardas de pase (312.3/j, rank 1) y más TD de pase (2.67/j, rank 1) permite. Ajuste +17.1%. Sin lesión en el reporte.
- (b) Qué la frena: Solo 198.5 yds/j en 4 titularidades completas (muestra corta). MIN es ofensiva conservadora con defensa élite y su línea (tier D) concede 9% de capturas.
- (c) Regla aplicada: Modelo con ventaja (+17.1%, rank 1), pero volumen bajo, muestra corta y línea débil → MEDIA.
- Riesgo: Que MIN no necesite lanzar.
- Estado de lesión: No figura en el reporte de práctica del jue 29-oct
- Pts/j que permite el rival: 27.5 · Prob. de victoria: n/d

**13. Justin Jefferson (MIN vs DET) · Media**
- Por qué (dato): 60.4 yds recibidas/j en 5 PJ (4.6 rec y 6.2 targets/j, 3 TD). DET permite 186.8 yds/j a WR (rank 3/32, Favorable). Calendario previo: sus rivales permitían 149.8 vs 148.7 de la liga. Proyección ajustada 69.4 (+14.8%) con w = 0.6. Muestra corta (≤ 5 PJ).
- (a) Qué la sube: DET permite 186.8 yds/j a WR (rank 3) y 312.3 yds de pase/j (rank 1). Ajuste +14.8%. Fuera del reporte de lesiones.
- (b) Qué la frena: MIN tiene poco volumen de pase; Jefferson promedia solo 6.2 targets/j y 60.4 yds/j; Hockenson y Addison reparten.
- (c) Regla aplicada: Modelo con ventaja (+14.8%, rank 3), pero volumen de equipo bajo → MEDIA.
- Riesgo: Partido de carrera/defensas que deje a MIN con menos de 25 pases.
- Estado de lesión: No figura en el reporte de práctica del jue 29-oct
- Pts/j que permite el rival: 27.5 · Prob. de victoria: n/d

**14. Chase Brown (CIN vs TEN) · Media**
- Por qué (dato): 47.5 yds por tierra/j en 6 PJ (13.7 acarreos, 4.7 rec/j, 1 TD). TEN permite 104.9 yds/j a RB (rank 7/32, Favorable). Calendario previo: sus rivales permitían 78.5 vs 91.5 de la liga. Proyección ajustada 57.1 (+20.1%) con w = 0.6.
- (a) Qué la sube: TEN permite 104.9 yds/j a RB (rank 7) y acaba de traspasar a Jeffery Simmons (DT All-Pro) a CHI el 29-oct. CIN es favorito claro (dif. +6.8 vs -6.9) → guion de carrera. Brown suma 13.7 acarreos y 4.7 recepciones/j. Ajuste +20.1%.
- (b) Qué la frena: Eficiencia baja (3.5 yds/acarreo; 39 yds en S5 y S7). Perine toma ~5 acarreos/j. Producción (47.5 yds/j) apenas sobre el umbral de 45.
- (c) Regla aplicada: Modelo con ventaja (+20.1%, rank 7), pero eficiencia y volumen justos → MEDIA.
- Riesgo: Que CIN gane por aire y Brown vuelva a quedarse en ~40 yds.
- Estado de lesión: No figura en el reporte de práctica del jue 29-oct
- Pts/j que permite el rival: 22.3 · Prob. de victoria: n/d

**15. Tee Higgins (CIN vs TEN) · Media**
- Por qué (dato): 95.2 yds recibidas/j en 6 PJ (5.5 rec y 8.3 targets/j, 2 TD). TEN permite 175.6 yds/j a WR (rank 6/32, Favorable). Calendario previo: sus rivales permitían 157.5 vs 148.7 de la liga. Proyección ajustada 101.7 (+6.9%) con w = 0.6.
- (a) Qué la sube: TEN permite 175.6 yds/j a WR (rank 6). Higgins: 95.2 yds/j y 8.3 targets/j con Burrow sano (275.5 yds/j). TEN acaba de traspasar a su mejor DL (Simmons) y es 1-6.
- (b) Qué la frena: Guion: CIN es favorito claro (dif. +6.8 vs -6.9) y podría correr en la 2.ª mitad. Ja'Marr Chase comparte targets (7.5/j). Ajuste +6.9% (debajo del +10% base).
- (c) Regla aplicada: El modelo da ventaja (≥ +5%, rank ≤ 10), pero aplica la regla de guion (receptor de un favorito claro, brecha ≥ +10 pts/j) y Chase reparte targets → MEDIA.
- Riesgo: Ventaja temprana de CIN que reduzca el volumen de pase.
- Estado de lesión: No figura en el reporte de práctica del jue 29-oct
- Pts/j que permite el rival: 22.3 · Prob. de victoria: n/d

**16. Kyren Williams (LA vs LAC) · Media**
- Por qué (dato): 70.3 yds por tierra/j en 7 PJ (13.7 acarreos, 4.6 rec/j, 6 TD). LAC permite 104.8 yds/j a RB (rank 8/32, Favorable). Calendario previo: sus rivales permitían 98.7 vs 91.5 de la liga. Proyección ajustada 72.9 (+3.7%) con w = 0.6.
- (a) Qué la sube: LAC permite 104.8 yds/j a RB (rank 8) y 1.00 TD terrestres/j (rank 4). LA es favorito claro: LAC es 0-6 con dif. -10.2 pts/j. Kyren: 13.7 acarreos y 5.9 targets/j. Línea LA tier proxy S.
- (b) Qué la frena: Ajuste solo +3.7% (< +5%); Blake Corum toma ~9 acarreos/j.
- (c) Regla aplicada: Matchup favorable (rank ≤ 10) con ajuste ≥ 0 cumple la condición del modelo, pero entra por R3, que tiene tope de MEDIA.
- Riesgo: Reparto con Corum en un juego decidido.
- Estado de lesión: No figura en el reporte de práctica del jue 29-oct
- Pts/j que permite el rival: 25.2 · Prob. de victoria: n/d

**17. Travis Kelce (KC vs DEN) · Media**
- Por qué (dato): 57.2 yds recibidas/j en 6 PJ (4.0 rec y 5.8 targets/j, 2 TD). DEN permite 65.3 yds/j a TE (rank 8/32, Favorable). Calendario previo: sus rivales permitían 50.6 vs 53.8 de la liga. Proyección ajustada 67.1 (+17.4%) con w = 0.6.
- (a) Qué la sube: DEN permite 65.3 yds/j a TE (rank 8); S Hufanga no practicó y S Brandon Jones limitado. Mahomes sano (245.7 yds/j). Ajuste +17.4%.
- (b) Qué la frena: Tobillo: practicó limitado el jueves; designación final sin verificar.
- (c) Regla aplicada: El modelo permitiría ALTA, pero la salud del jugador frena → MEDIA.
- Riesgo: Que juegue limitado o quede fuera.
- Estado de lesión: Práctica jue 29-oct: Limitado (Ankle); designación final sin verificar
- Pts/j que permite el rival: 20.1 · Prob. de victoria: n/d

**18. Hunter Henry (NE vs MIA) · Media**
- Por qué (dato): 42.3 yds recibidas/j en 7 PJ (3.7 rec y 4.4 targets/j, 2 TD). MIA permite 74.7 yds/j a TE (rank 4/32, Favorable). Calendario previo: sus rivales permitían 47.6 vs 53.8 de la liga. Proyección ajustada 56.7 (+34.1%) con w = 0.6.
- (a) Qué la sube: MIA permite 74.7 yds/j a TE (rank 4) y 1.00 TD/j a TE (rank 4); su secundaria trae 4 limitados (Taylor, Brents, Trader, Taaffe). Henry va en alza (62, 44, 48, 71 yds en S4-S7) y Drake Maye promedia 254.9 yds/j. A.J. Brown no practicó el jueves (tobillo; designación final sin verificar) y Doubs/Hollins están en reserva → más targets.
- (b) Qué la frena: Solo 4.4 targets/j. NE es favorito (dif. +2.4 vs -9.8) y podría correr más al final.
- (c) Regla aplicada: Modelo con ventaja amplia (+34.1%, rank 4), pero aplica la regla de guion: receptor de un favorito claro (brecha ≥ +10 pts/j) → el guion frena → MEDIA.
- Riesgo: Guion de paliza temprana que reduzca los pases en la 2.ª mitad.
- Estado de lesión: No figura en el reporte de práctica del jue 29-oct
- Pts/j que permite el rival: 26.2 · Prob. de victoria: n/d

**19. Dallas Goedert (PHI vs WAS) · Media**
- Por qué (dato): 45.6 yds recibidas/j en 5 PJ (4.4 rec y 6.2 targets/j, 2 TD). WAS permite 73.5 yds/j a TE (rank 5/32, Favorable). Calendario previo: sus rivales permitían 48.0 vs 53.8 de la liga. Proyección ajustada 60.2 (+32.0%) con w = 0.6. Muestra corta (≤ 5 PJ).
- (a) Qué la sube: WAS permite 73.5 yds/j a TE (rank 5) y 1.33 TD/j a TE (rank 2). DeVonta Smith y Wicks no practicaron (fuera en S7) → Goedert concentra targets (6.2/j; 8 y 7 con McKee). Ajuste +32.0%.
- (b) Qué la frena: QB suplente: Hurts en reserva de lesionados, Tanner McKee titular (213 yds/j en 2 juegos). Línea tier proxy D.
- (c) Regla aplicada: El modelo permitiría ALTA, pero el equipo propio llega sin su QB titular → MEDIA (criterio 4 del usuario).
- Riesgo: Ofensiva PHI sin ritmo con McKee.
- Estado de lesión: Práctica jue 29-oct: Completo (Knee); designación final sin verificar
- Pts/j que permite el rival: 28.7 · Prob. de victoria: n/d

**20. Stefon Diggs (WAS vs PHI) · Media**
- Por qué (dato): 42.8 yds recibidas/j en 5 PJ (4.8 rec y 7.6 targets/j, 4 TD). PHI permite 184.0 yds/j a WR (rank 4/32, Favorable). Calendario previo: sus rivales permitían 139.1 vs 148.7 de la liga. Proyección ajustada 51.1 (+19.4%) con w = 0.6. Muestra corta (≤ 5 PJ).
- (a) Qué la sube: PHI permite 184.0 yds/j a WR (rank 4) y 1.29 TD/j a WR (rank 3); CB Jonathan Jones y LB Jihaad Campbell no practicaron y 6 defensivos más están limitados. McLaurin en reserva → Diggs es el WR1 (7.6 targets/j). Jayden Daniels practicó completo el jue 29-oct (designación final sin verificar) y fue titular en S5-S6. Ajuste +19.4%.
- (b) Qué la frena: Solo 5.6 yds/target; 42.8 yds/j apenas sobre el umbral de 42.
- (c) Regla aplicada: Modelo con ventaja (+19.4%, rank 4), pero eficiencia baja → MEDIA.
- Riesgo: Baja eficiencia: mucho volumen con pocas yardas.
- Estado de lesión: Práctica jue 29-oct: Completo (Hand); designación final sin verificar
- Pts/j que permite el rival: 25.0 · Prob. de victoria: n/d

**21. Jaxon Smith-Njigba (SEA vs CHI) · Media**
- Por qué (dato): 123.9 yds recibidas/j en 7 PJ (8.3 rec y 11.1 targets/j, 8 TD). CHI permite 149.4 yds/j a WR (rank 16/32, Neutral). Calendario previo: sus rivales permitían 132.2 vs 148.7 de la liga. Proyección ajustada 133.6 (+7.8%) con w = 0.6.
- (a) Qué la sube: El receptor más productivo del grupo evaluado: 123.9 yds/j, 8.3 rec y 11.1 targets/j, 8 TD. Ajuste +7.8%. SEA suma a Quenton Nelson (OL) desde el 27-oct.
- (b) Qué la frena: Matchup neutral: CHI permite 149.4 yds/j a WR (rank 16). CHI agregó a Jeffery Simmons (más presión). Juego del lunes: sin reporte de práctica de SEA en la fuente; estatus con corte del viernes.
- (c) Regla aplicada: El modelo da ≥ +5%, pero el matchup es neutral; entra por R4 (tope MEDIA).
- Riesgo: Presión de CHI con Simmons; doble cobertura.
- Estado de lesión: Sin reporte S8 de SEA en la fuente (juego del lunes); estatus con corte del viernes
- Pts/j que permite el rival: 20.4 · Prob. de victoria: n/d

## APÉNDICE C · Partidos (extracto de `partidos[]`)

**BAL @ BUF** · Dom 01-nov-2026 12:00 (Monterrey) · Highmark Stadium · récords BAL 4-3-0 / BUF 5-1-0 · Prob. victoria: n/d
- Decisión: Incluido (ambos lados)
- Por qué: BUF permite mucho por aire a QB (rank 2) y a WR (rank 7; la que más TD a WR concede). BAL permite mucho a WR (rank 5) y llega con la secundaria tocada.
- Qué lo puede romper: Estatus de Lamar (regresa de esguince alto) y un guion de carrera con Henry/Cook.
- Conclusión: BAL: Flowers (ALTA) y Lamar (MEDIA). BUF: Shakir (MEDIA). Henry y Cook descartados (BAL frena bien a RB, rank 26; BUF es neutral, rank 20; ajustes −9%/−10%).
- Selecciones: Zay Flowers, Lamar Jackson, Khalil Shakir

**TEN @ CIN** · Dom 01-nov-2026 12:00 (Monterrey) · Paycor Stadium · récords TEN 1-6-0 / CIN 4-2-0 · Prob. victoria: n/d
- Decisión: Incluido (lado CIN)
- Por qué: TEN permite mucho a RB (rank 7) y a WR (rank 6), y acaba de traspasar a Jeffery Simmons. CIN es favorito claro.
- Qué lo puede romper: Que CIN resuelva temprano y reparta el balón; la eficiencia baja de Chase Brown.
- Conclusión: CIN: Higgins (MEDIA) y Chase Brown (MEDIA). TEN: ningún jugador con ventaja (Ward < 190 yds/j; Pollard y Tate con ajuste negativo); las bajas de la defensa de CIN (Dugger, Giles-Harris) no compensan.
- Selecciones: Chase Brown, Tee Higgins

**ARI @ DAL** · Dom 01-nov-2026 12:00 (Monterrey) · AT&T Stadium · récords ARI 2-5-0 / DAL 3-4-0 · Prob. victoria: n/d
- Decisión: Incluido (ambos lados)
- Por qué: DAL permite mucho a RB (rank 5) y a WR (rank 9); ARI no favorito pasará mucho. ARI permite a RB (rank 10) y DAL es favorito claro.
- Qué lo puede romper: Costillas de Michael Wilson; reparto de pases hacia McBride.
- Conclusión: ARI: Michael Wilson (MEDIA); Love descartado por lesión y guion. DAL: Javonte Williams (MEDIA, R3). Lamb/Pickens/Dak con ajuste ~0%.
- Selecciones: Michael Wilson, Javonte Williams

**MIN @ DET** · Dom 01-nov-2026 12:00 (Monterrey) · Ford Field · récords MIN 6-0-0 / DET 4-2-0 · Prob. victoria: n/d
- Decisión: Incluido (lado MIN)
- Por qué: DET es la defensa más blanda contra QB (rank 1), TE (rank 1) y top 3 contra WR.
- Qué lo puede romper: Que MIN (6-0, defensa élite) juegue a correr y lance poco.
- Conclusión: MIN: Hockenson (ALTA), Jefferson y Kyler (MEDIA). DET: todo descartado; MIN permite muy poco a QB, WR y TE (ranks 31, 28, 28).
- Selecciones: T.J. Hockenson, Kyler Murray, Justin Jefferson

**IND @ JAX** · Dom 01-nov-2026 12:00 (Monterrey) · EverBank Stadium · récords IND 2-5-0 / JAX 4-2-0 · Prob. victoria: n/d
- Decisión: Incluido (lado IND)
- Por qué: JAX es la defensa que más permite a WR (rank 1) y la 3.ª contra QB; IND no favorito pasará.
- Qué lo puede romper: Ineficiencia de Daniel Jones y una línea sin Quenton Nelson.
- Conclusión: IND: Downs y K. Allen (MEDIA). Taylor descartado (JAX es la mejor contra RB). JAX: Tuten neutral (0%) pese a la salida de Buckner; Lawrence y receptores con ajuste negativo.
- Selecciones: Keenan Allen, Josh Downs

**LV @ NYJ** · Dom 01-nov-2026 12:00 (Monterrey) · MetLife Stadium · récords LV 3-4-0 / NYJ 2-5-0 · Prob. victoria: n/d
- Decisión: Incluido (lado NYJ)
- Por qué: LV es la defensa que más permite a RB (rank 1).
- Qué lo puede romper: Regreso de Breece Hall y la línea NYJ (tier proxy F).
- Conclusión: NYJ: Braelon Allen (MEDIA). LV: Jeanty +6% y Bowers +2%, descartados; vigilar las 3 bajas de la DL de NYJ.
- Selecciones: Braelon Allen

**CLE @ PIT** · Dom 01-nov-2026 12:00 (Monterrey) · Acrisure Stadium · récords CLE 5-2-0 / PIT 5-2-0 · Prob. victoria: n/d
- Decisión: Incluido (lado PIT)
- Por qué: CLE permite a RB (rank 9) y su frente llega con varios limitados.
- Qué lo puede romper: Partido cerrado entre equipos 5-2 que se vuelva de pases.
- Conclusión: PIT: Jaylen Warren (ALTA). CLE: receptores con ajuste negativo (PIT rank 17 contra WR) pese a las bajas en CB de PIT; línea CLE tier proxy F.
- Selecciones: Jaylen Warren

**ATL @ TB** · Dom 01-nov-2026 12:00 (Monterrey) · Raymond James Stadium · récords ATL 3-4-0 / TB 2-5-0 · Prob. victoria: n/d
- Decisión: Incluido (lado TB)
- Por qué: ATL permite mucho a QB (rank 4) y a WR (rank 8), con 4 CB limitados.
- Qué lo puede romper: Muestra corta de Mayfield tras su regreso.
- Conclusión: TB: Mayfield (MEDIA); Egbuka (conmoción) y Otton (bajo volumen) fuera. ATL: Bijan −14% (TB es 2.ª mejor contra RB); Pitts bajo volumen.
- Selecciones: Baker Mayfield

**LAC @ LA** · Dom 01-nov-2026 15:05 (Monterrey) · SoFi Stadium · récords LAC 0-6-0 / LA 3-4-0 · Prob. victoria: n/d
- Decisión: Incluido (lado LA)
- Por qué: LAC (0-6) permite a RB (rank 8); LA es favorito claro.
- Qué lo puede romper: Reparto Kyren–Corum.
- Conclusión: LA: Kyren Williams (MEDIA, R3). Nacua −11% (LAC rank 25 contra WR), vigilar sus bajas en DB. LAC: todo descartado (LA permite muy poco por aire).
- Selecciones: Kyren Williams

**KC @ DEN** · Dom 01-nov-2026 15:25 (Monterrey) · Empower Field at Mile High · récords KC 5-1-0 / DEN 5-2-0 · Prob. victoria: n/d
- Decisión: Incluido (lado KC)
- Por qué: DEN permite a TE (rank 8) y llega sin S Hufanga en práctica.
- Qué lo puede romper: Tobillo de Kelce.
- Conclusión: KC: Kelce (MEDIA). Mahomes +6% y Walker +4% sin llegar al umbral. DEN: Engram +21% pero 19.4 yds/j; resto negativo.
- Selecciones: Travis Kelce

**NE @ MIA** · Dom 01-nov-2026 15:25 (Monterrey) · Hard Rock Stadium · récords NE 4-3-0 / MIA 1-5-0 · Prob. victoria: n/d
- Decisión: Incluido (lado NE)
- Por qué: MIA permite mucho a TE (rank 4) y su secundaria está tocada.
- Qué lo puede romper: Paliza temprana de NE que baje el volumen de pase.
- Conclusión: NE: Hunter Henry (MEDIA; bajó de ALTA en la auditoría por la regla de guion). Stevenson +15% pero bajo volumen. MIA: Willis < 190 yds/j; nada con ventaja.
- Selecciones: Hunter Henry

**PHI @ WAS** · Dom 01-nov-2026 19:20 (Monterrey) · Northwest Stadium · récords PHI 2-5-0 / WAS 1-4-1 · Prob. victoria: n/d
- Decisión: Incluido (ambos lados)
- Por qué: WAS permite mucho a QB (rank 5) y a TE (rank 5); PHI permite mucho a WR (rank 4) y a RB (rank 3) y tiene 8 defensivos tocados.
- Qué lo puede romper: QB suplente en PHI (McKee) y la ineficiencia de Diggs.
- Conclusión: PHI: Goedert (MEDIA). WAS: Diggs (MEDIA). Rachaad White hereda carga (Croskey-Merritt en reserva), pero sin volumen comprobado (29 yds/j); revisar en el recheck.
- Selecciones: Dallas Goedert, Stefon Diggs

**CHI @ SEA** · Lun 02-nov-2026 19:15 (Monterrey) · Lumen Field · récords CHI 5-2-0 / SEA 4-3-0 · Prob. victoria: n/d
- Decisión: Incluido (lado SEA)
- Por qué: SEA tiene la defensa que menos permite a QB, WR y TE (rank 32 en las tres): todo CHI descartado. JSN entra por volumen élite.
- Qué lo puede romper: Simmons recién llegado a CHI; estatus del lunes (inactivos ~17:45 del lunes, hora Monterrey).
- Conclusión: SEA: JSN (MEDIA, R4). CHI: todos con ajuste negativo (Caleb −17%, Burden −23%).
- Selecciones: Jaxon Smith-Njigba

## APÉNDICE D · Defensas (yds/j permitidas por posición y rank; 1 = la que más permite)

| Def | PJ | QB yds/j (rk) | RB yds/j (rk) | WR yds/j (rk) | TE yds/j (rk) | Pts/j (rk) | TD/j QB·RB·WR·TE (rk) |
|---|---|---|---|---|---|---|---|
| ARI | 7 | 243.7 (12) | 103.6 (10) | 152.6 (11) | 59.7 (11) | 29.7 (1) | 2.43 (4) · 0.71 (12) · 1.43 (2) · 0.71 (5) |
| ATL | 7 | 271.4 (4) | 81.7 (21) | 169.9 (8) | 62.7 (9) | 24.7 (13) | 1.57 (9) · 1.00 (4) · 0.57 (22) · 0.57 (12) |
| BAL | 7 | 235.1 (17) | 77.4 (26) | 181.6 (5) | 39.0 (27) | 23.9 (15) | 1.29 (21) · 0.86 (9) · 0.57 (22) · 0.71 (5) |
| BUF | 6 | 298.7 (2) | 82.8 (20) | 173.8 (7) | 77.5 (3) | 28.5 (3) | 2.50 (2) · 1.00 (4) · 1.83 (1) · 0.17 (26) |
| CAR | 7 | 219.6 (26) | 115.6 (4) | 144.4 (18) | 47.3 (18) | 27.6 (6) | 1.43 (16) · 1.43 (2) · 0.57 (22) · 0.71 (5) |
| CHI | 7 | 241.3 (13) | 73.6 (28) | 149.4 (16) | 56.6 (14) | 20.4 (23) | 1.57 (9) · 0.43 (27) · 0.86 (14) · 0.43 (16) |
| CIN | 6 | 253.8 (7) | 80.5 (22) | 137.5 (21) | 84.8 (2) | 20.3 (25) | 1.00 (28) · 0.50 (23) · 1.00 (9) · 0.00 (31) |
| CLE | 7 | 220.7 (25) | 104.0 (9) | 150.3 (13) | 49.3 (16) | 20.9 (21) | 1.57 (9) · 0.57 (21) · 1.00 (9) · 0.57 (12) |
| DAL | 7 | 235.1 (17) | 106.6 (5) | 163.1 (9) | 46.6 (19) | 25.7 (9) | 1.71 (8) · 1.00 (4) · 1.00 (9) · 0.43 (16) |
| DEN | 7 | 236.0 (16) | 102.0 (12) | 135.9 (22) | 65.3 (8) | 20.1 (26) | 1.14 (26) · 0.71 (12) · 0.43 (31) · 0.57 (12) |
| DET | 6 | 312.3 (1) | 79.7 (23) | 186.8 (3) | 100.3 (1) | 27.5 (7) | 2.67 (1) · 0.67 (18) · 0.83 (18) · 1.67 (1) |
| GB | 8 | 220.9 (24) | 93.5 (15) | 152.0 (12) | 35.2 (30) | 20.5 (22) | 1.25 (23) · 1.25 (3) · 0.88 (13) · 0.25 (25) |
| HOU | 7 | 262.7 (6) | 90.7 (16) | 187.4 (2) | 46.0 (20) | 24.3 (14) | 1.43 (16) · 0.86 (9) · 0.86 (14) · 0.14 (28) |
| IND | 7 | 227.4 (22) | 95.6 (14) | 141.6 (20) | 45.3 (21) | 25.7 (9) | 1.57 (9) · 0.71 (12) · 0.71 (20) · 0.71 (5) |
| JAX | 6 | 280.3 (3) | 51.5 (32) | 210.0 (1) | 34.7 (31) | 17.3 (30) | 1.17 (24) · 0.50 (23) · 0.50 (28) · 0.67 (10) |
| KC | 6 | 229.5 (21) | 73.0 (29) | 122.0 (29) | 70.8 (6) | 17.2 (31) | 0.83 (31) · 0.67 (18) · 0.17 (32) · 0.67 (10) |
| LA | 7 | 191.1 (30) | 85.7 (17) | 106.0 (31) | 41.7 (26) | 22.7 (17) | 1.43 (16) · 0.29 (31) · 1.14 (6) · 0.14 (28) |
| LAC | 6 | 216.2 (27) | 104.8 (8) | 132.8 (25) | 57.5 (13) | 25.2 (11) | 1.17 (24) · 1.00 (4) · 0.83 (18) · 0.17 (26) |
| LV | 7 | 245.1 (11) | 124.9 (1) | 149.9 (14) | 57.9 (12) | 28.1 (4) | 2.29 (6) · 1.00 (4) · 1.14 (6) · 1.14 (3) |
| MIA | 6 | 236.2 (15) | 102.5 (11) | 115.5 (30) | 74.7 (4) | 26.2 (8) | 2.33 (5) · 0.50 (23) · 0.50 (28) · 1.00 (4) |
| MIN | 6 | 180.8 (31) | 83.8 (18) | 123.8 (28) | 38.8 (28) | 12.3 (32) | 0.50 (32) · 0.50 (23) · 0.50 (28) · 0.00 (31) |
| NE | 7 | 239.0 (14) | 83.4 (19) | 149.9 (14) | 53.7 (15) | 20.4 (23) | 1.29 (21) · 0.71 (12) · 1.00 (9) · 0.29 (18) |
| NO | 7 | 249.7 (8) | 120.4 (2) | 143.6 (19) | 68.4 (7) | 27.7 (5) | 1.57 (9) · 1.57 (1) · 0.86 (14) · 0.57 (12) |
| NYG | 7 | 192.1 (29) | 101.6 (13) | 126.9 (27) | 44.7 (22) | 23.0 (16) | 2.00 (7) · 0.43 (27) · 1.29 (3) · 0.29 (18) |
| NYJ | 7 | 202.9 (28) | 106.6 (5) | 133.3 (24) | 48.0 (17) | 21.4 (20) | 1.57 (9) · 0.71 (12) · 1.14 (6) · 0.14 (28) |
| PHI | 7 | 247.9 (9) | 116.7 (3) | 184.0 (4) | 43.0 (24) | 25.0 (12) | 1.57 (9) · 0.71 (12) · 1.29 (3) · 0.29 (18) |
| PIT | 7 | 230.0 (20) | 75.4 (27) | 147.3 (17) | 41.9 (25) | 19.7 (28) | 1.00 (28) · 0.43 (27) · 0.57 (22) · 0.29 (18) |
| SEA | 7 | 158.0 (32) | 71.0 (30) | 91.7 (32) | 34.4 (32) | 17.9 (29) | 1.14 (26) · 0.57 (21) · 0.57 (22) · 0.29 (18) |
| SF | 7 | 223.9 (23) | 78.6 (24) | 129.7 (26) | 43.6 (23) | 19.9 (27) | 1.43 (16) · 0.29 (31) · 0.86 (14) · 0.29 (18) |
| TB | 7 | 233.7 (19) | 64.9 (31) | 134.7 (23) | 62.0 (10) | 21.6 (19) | 1.43 (16) · 0.43 (27) · 0.71 (20) · 0.71 (5) |
| TEN | 7 | 245.7 (10) | 104.9 (7) | 175.6 (6) | 38.0 (29) | 22.3 (18) | 0.86 (30) · 0.86 (9) · 0.57 (22) · 0.29 (18) |
| WAS | 6 | 265.7 (5) | 77.7 (25) | 158.3 (10) | 73.5 (5) | 28.7 (2) | 2.50 (2) · 0.67 (18) · 1.17 (5) · 1.33 (2) |

## APÉNDICE E · Equipos que juegan en S8 (extracto de `equipos{}` y `calendario_jugado{}`)

| Eq | Récord | Dif pts/j | QB titular | Tier línea (proxy) | Dureza vs liga QB · RB · WR · TE |
|---|---|---|---|---|---|
| ARI | 2-5-0 | -9.4 | Jacoby Brissett | C | -7.8% · -1.3% · -10.9% · -9.1% |
| ATL | 3-4-0 | -0.3 | Michael Penix Jr. | A | -0.0% · -7.9% · +2.5% · -9.8% |
| BAL | 4-3-0 | +0.3 | Lamar Jackson | C | +3.6% · +7.2% · +2.6% · +5.1% |
| BUF | 5-1-0 | +4.3 | Josh Allen | A | +3.7% · +0.7% · +3.4% · +11.1% |
| CHI | 5-2-0 | +5.3 | Caleb Williams | B | -5.9% · +0.9% · -0.1% · -14.1% |
| CIN | 4-2-0 | +6.8 | Joe Burrow | B | +2.5% · -14.2% · +5.9% · -7.6% |
| CLE | 5-2-0 | -1.9 | Deshaun Watson | F | +1.9% · -4.2% · +11.3% · -16.8% |
| DAL | 3-4-0 | +1.3 | Dak Prescott | S | -1.2% · -1.6% · +1.8% · -3.2% |
| DEN | 5-2-0 | +0.4 | Bo Nix | S | -3.1% · -9.4% · -5.4% · -2.1% |
| DET | 4-2-0 | +3.2 | Jared Goff | B | -2.3% · +12.1% · -2.5% · +2.2% |
| IND | 2-5-0 | -3.7 | Daniel Jones | B | +3.2% · -13.2% · +8.4% · -3.9% |
| JAX | 4-2-0 | +8.3 | Trevor Lawrence | A | +3.4% · +4.3% · +6.5% · +5.9% |
| KC | 5-1-0 | +6.7 | Patrick Mahomes | A | -8.5% · +4.4% · -13.5% · -6.0% |
| LA | 3-4-0 | +1.6 | Matthew Stafford | S | -0.8% · +7.9% · -0.5% · -1.5% |
| LAC | 0-6-0 | -10.2 | Justin Herbert | F | +3.5% · +2.1% · -5.1% · +20.1% |
| LV | 3-4-0 | -2.0 | Kirk Cousins | D | -2.0% · +5.3% · -6.3% · +0.3% |
| MIA | 1-5-0 | -9.8 | Malik Willis | C | -1.4% · +0.9% · -9.4% · +12.9% |
| MIN | 6-0-0 | +8.5 | Kyler Murray | D | +3.6% · -0.8% · -2.3% · +5.4% |
| NE | 4-3-0 | +2.4 | Drake Maye | C | -0.8% · -10.0% · +0.9% · -11.6% |
| NYJ | 2-5-0 | -1.9 | Geno Smith | F | +5.2% · +1.0% · +4.9% · +9.5% |
| PHI | 2-5-0 | -6.9 | Tanner McKee | D | +5.5% · -0.8% · +8.4% · -7.0% |
| PIT | 5-2-0 | +2.1 | Aaron Rodgers | C | +3.0% · -3.6% · -0.3% · +15.9% |
| SEA | 4-3-0 | +6.1 | Sam Darnold | D | -0.3% · -3.6% · -11.1% · +22.2% |
| TB | 2-5-0 | +1.6 | Baker Mayfield | B | -1.4% · -0.1% · +0.6% · -2.5% |
| TEN | 1-6-0 | -6.9 | Cam Ward | A | +0.7% · +11.5% · +9.0% · -7.6% |
| WAS | 1-4-1 | -6.7 | Jayden Daniels | C | -8.9% · +6.8% · -7.7% · -17.2% |

## APÉNDICE F · Los 188 evaluados (CSV compacto; cambio en %)

```csv
jugador,pos,equipo,rival,pj,prod_pj,rival_permite,rank,lectura,dureza,proyeccion,cambio_pct,tgt_pj,rec_pj,car_pj,R1,R2,R3,R4,veredicto
Jacoby Brissett,QB,ARI,DAL,7,228.6,235.1,17,Neutral,216.7,240.3,+5.1,0.1,0.1,3.7,0,0,0,0,Descartado
Jeremiyah Love,RB,ARI,DAL,5,49.0,106.6,5,Favorable,88.8,54.9,+12.0,2.8,2.2,13.4,1,0,0,0,Descartado
Bam Knight,RB,ARI,DAL,5,32.0,106.6,5,Favorable,87.2,36.3,+13.3,1.4,1.0,5.0,0,0,0,0,Descartado
Tyler Allgeier,RB,ARI,DAL,7,25.1,106.6,5,Favorable,90.3,27.9,+10.8,2.4,2.3,8.7,0,0,0,0,Descartado
Trey McBride,TE,ARI,DAL,7,67.4,46.6,19,Neutral,48.9,65.5,-2.9,11.1,8.4,0.0,0,0,0,0,Descartado
Michael Wilson,WR,ARI,DAL,7,53.6,163.1,9,Favorable,132.5,61.0,+13.9,9.4,5.3,0.3,1,0,0,0,Incluido-Media
Kendrick Bourne,WR,ARI,DAL,7,33.4,163.1,9,Favorable,132.9,38.0,+13.6,5.1,3.6,0.0,0,0,0,0,Descartado
Michael Penix Jr.,QB,ATL,TB,5,231.4,233.7,19,Neutral,233.7,231.4,+0.0,0.0,0.0,2.4,0,0,0,0,Descartado
Jack Strand,QB,ATL,TB,1,59.0,233.7,19,Neutral,232.0,59.3,+0.4,0.0,0.0,2.0,0,0,0,0,Descartado
Bijan Robinson,RB,ATL,TB,7,100.6,64.9,31,Difícil,84.3,86.7,-13.8,4.6,3.6,18.7,0,0,0,0,Descartado
Brian Robinson,RB,ATL,TB,6,35.2,64.9,31,Difícil,85.0,30.2,-14.2,1.0,0.8,8.8,0,0,0,0,Descartado
Kyle Pitts,TE,ATL,TB,7,27.3,62.0,10,Favorable,48.5,31.8,+16.6,3.9,2.9,0.0,0,0,0,0,Descartado
Drake London,WR,ATL,TB,7,88.0,134.7,23,Difícil,152.4,81.9,-7.0,8.0,5.4,0.3,0,0,0,0,Descartado
Jahan Dotson,WR,ATL,TB,7,34.6,134.7,23,Difícil,152.4,32.2,-7.0,3.6,1.7,0.0,0,0,0,0,Descartado
Lamar Jackson,QB,BAL,BUF,4,241.8,298.7,2,Favorable,236.5,279.9,+15.8,0.0,0.0,4.8,1,0,0,0,Incluido-Media
Tyler Huntley,QB,BAL,BUF,3,221.3,298.7,2,Favorable,252.7,245.5,+10.9,0.0,0.0,4.7,1,0,0,0,Descartado
Derrick Henry,RB,BAL,BUF,7,82.7,82.8,20,Neutral,98.1,75.0,-9.3,1.7,1.4,21.0,0,0,0,0,Descartado
Mark Andrews,TE,BAL,BUF,7,29.1,77.5,3,Favorable,56.5,35.6,+22.3,5.3,3.7,0.0,0,0,0,0,Descartado
Zay Flowers,WR,BAL,BUF,6,101.3,173.8,7,Favorable,154.5,109.0,+7.5,8.8,6.7,0.5,0,1,0,1,Incluido-Alta
Rashod Bateman,WR,BAL,BUF,7,38.0,173.8,7,Favorable,152.6,41.2,+8.3,3.7,2.6,0.0,0,0,0,0,Descartado
Ja'Kobi Lane,WR,BAL,BUF,3,25.3,173.8,7,Favorable,135.9,29.6,+16.8,4.3,2.7,0.0,0,0,0,0,Descartado
Josh Allen,QB,BUF,BAL,6,250.7,235.1,17,Neutral,243.8,245.3,-2.1,0.2,0.2,8.0,0,0,0,0,Descartado
James Cook,RB,BUF,BAL,6,104.5,77.4,26,Difícil,92.1,94.5,-9.6,2.3,1.7,19.5,0,0,0,0,Descartado
Dalton Kincaid,TE,BUF,BAL,6,52.5,39.0,27,Difícil,59.8,41.6,-20.9,4.8,3.8,0.0,0,0,0,0,Descartado
Khalil Shakir,WR,BUF,BAL,6,48.3,181.6,5,Favorable,153.7,53.6,+10.9,5.3,3.7,0.0,1,0,0,0,Incluido-Media
Keon Coleman,WR,BUF,BAL,6,47.2,181.6,5,Favorable,153.7,52.3,+10.9,4.0,3.2,0.0,0,0,0,0,Descartado
DJ Moore,WR,BUF,BAL,4,44.5,181.6,5,Favorable,165.0,47.2,+6.0,5.0,3.0,0.5,0,0,0,0,Descartado
Caleb Williams,QB,CHI,SEA,4,255.0,158.0,32,Difícil,220.8,211.5,-17.1,0.0,0.0,6.0,0,0,0,0,Descartado
Case Keenum,QB,CHI,SEA,2,177.5,158.0,32,Difícil,236.3,142.2,-19.9,0.0,0.0,2.5,0,0,0,0,Descartado
Tyson Bagent,QB,CHI,SEA,2,177.5,158.0,32,Difícil,208.3,151.8,-14.5,0.0,0.0,3.5,0,0,0,0,Descartado
Kyle Monangai,RB,CHI,SEA,4,81.0,71.0,30,Difícil,96.1,68.3,-15.7,1.2,1.2,15.0,0,0,0,0,Descartado
D'Andre Swift,RB,CHI,SEA,7,68.0,71.0,30,Difícil,92.3,58.6,-13.8,3.6,3.1,16.6,0,0,0,0,Descartado
Colston Loveland,TE,CHI,SEA,7,34.9,34.4,32,Difícil,46.2,29.5,-15.3,6.0,3.7,0.0,0,0,0,0,Descartado
Luther Burden III,WR,CHI,SEA,7,70.1,91.7,32,Difícil,148.6,54.0,-23.0,6.7,5.0,1.1,0,0,0,0,Descartado
Rome Odunze,WR,CHI,SEA,7,54.4,91.7,32,Difícil,148.6,41.9,-23.0,5.4,3.4,0.0,0,0,0,0,Descartado
Kalif Raymond,WR,CHI,SEA,7,34.9,91.7,32,Difícil,148.6,26.8,-23.0,4.4,3.7,0.1,0,0,0,0,Descartado
Joe Burrow,QB,CIN,TEN,6,275.5,245.7,10,Favorable,240.9,278.8,+1.2,0.0,0.0,2.8,0,0,0,0,Descartado
Chase Brown,RB,CIN,TEN,6,47.5,104.9,7,Favorable,78.5,57.1,+20.1,5.5,4.7,13.7,1,0,0,0,Incluido-Media
Samaje Perine,RB,CIN,TEN,6,21.0,104.9,7,Favorable,78.5,25.2,+20.1,1.7,1.2,5.2,0,0,0,0,Descartado
Mike Gesicki,TE,CIN,TEN,6,27.5,38.0,29,Difícil,49.1,23.8,-13.5,3.0,2.2,0.0,0,0,0,0,Descartado
Tee Higgins,WR,CIN,TEN,6,95.2,175.6,6,Favorable,157.5,101.7,+6.9,8.3,5.5,0.0,0,1,0,1,Incluido-Media
Ja'Marr Chase,WR,CIN,TEN,6,58.5,175.6,6,Favorable,157.5,62.5,+6.9,7.5,5.3,0.0,0,0,0,0,Descartado
Deshaun Watson,QB,CLE,PIT,7,211.7,230.0,20,Neutral,239.6,206.6,-2.4,0.0,0.0,6.9,0,0,0,0,Descartado
Quinshon Judkins,RB,CLE,PIT,6,52.8,75.4,27,Difícil,88.9,48.0,-9.1,3.5,3.2,15.0,0,0,0,0,Descartado
Audric Estimé,RB,CLE,PIT,1,19.0,75.4,27,Difícil,80.0,18.3,-3.4,0.0,0.0,9.0,0,0,0,0,Descartado
Harold Fannin Jr.,TE,CLE,PIT,7,36.7,41.9,25,Difícil,44.8,35.3,-3.9,5.6,3.6,0.0,0,0,0,0,Descartado
Denzel Boston,WR,CLE,PIT,7,53.1,147.3,17,Neutral,165.4,49.6,-6.6,6.0,2.9,0.0,0,0,0,0,Descartado
KC Concepcion,WR,CLE,PIT,7,45.0,147.3,17,Neutral,165.4,42.0,-6.6,6.4,4.3,1.3,0,0,0,0,Descartado
Dak Prescott,QB,DAL,ARI,7,264.4,243.7,12,Neutral,232.3,272.2,+2.9,0.0,0.0,2.3,0,0,0,0,Descartado
Javonte Williams,RB,DAL,ARI,7,67.4,103.6,10,Favorable,90.1,73.5,+9.0,3.1,2.7,15.7,0,0,1,0,Incluido-Media
Jake Ferguson,TE,DAL,ARI,7,16.4,59.7,11,Neutral,52.1,17.9,+8.8,3.6,2.4,0.0,0,0,0,0,Descartado
CeeDee Lamb,WR,DAL,ARI,7,93.0,152.6,11,Neutral,151.4,93.4,+0.5,11.6,7.6,0.3,0,0,0,0,Descartado
George Pickens,WR,DAL,ARI,7,69.3,152.6,11,Neutral,151.4,69.6,+0.5,8.3,5.3,0.0,0,0,0,0,Descartado
Ryan Flournoy,WR,DAL,ARI,7,43.4,152.6,11,Neutral,151.4,43.6,+0.5,5.7,3.9,0.0,0,0,0,0,Descartado
Bo Nix,QB,DEN,KC,7,181.6,229.5,21,Neutral,227.7,182.4,+0.5,0.0,0.0,4.1,0,0,0,0,Descartado
J.K. Dobbins,RB,DEN,KC,7,41.9,73.0,29,Difícil,82.9,38.9,-7.2,1.3,1.1,12.4,0,0,0,0,Descartado
Jonah Coleman,RB,DEN,KC,3,31.0,73.0,29,Difícil,76.8,30.1,-3.0,1.7,1.7,6.3,0,0,0,0,Descartado
Evan Engram,TE,DEN,KC,7,19.4,70.8,6,Favorable,52.7,23.4,+20.7,3.1,1.9,0.0,0,0,0,0,Descartado
Jaylen Waddle,WR,DEN,KC,7,39.4,122.0,29,Difícil,140.6,36.3,-7.9,6.4,3.7,0.3,0,0,0,0,Descartado
Courtland Sutton,WR,DEN,KC,7,24.0,122.0,29,Difícil,140.6,22.1,-7.9,4.7,2.3,0.0,0,0,0,0,Descartado
Jared Goff,QB,DET,MIN,6,298.0,180.8,31,Difícil,229.6,260.0,-12.7,0.0,0.0,2.0,0,0,0,0,Descartado
Jahmyr Gibbs,RB,DET,MIN,6,103.3,83.8,18,Neutral,102.5,92.0,-10.9,6.7,5.3,22.3,0,0,0,0,Descartado
Sam LaPorta,TE,DET,MIN,6,55.7,38.8,28,Difícil,55.0,45.9,-17.6,6.5,4.7,0.0,0,0,0,0,Descartado
Amon-Ra St. Brown,WR,DET,MIN,6,87.5,123.8,28,Difícil,144.9,79.9,-8.7,11.3,7.7,0.2,0,0,0,0,Descartado
Jameson Williams,WR,DET,MIN,6,61.2,123.8,28,Difícil,144.9,55.8,-8.7,6.3,3.8,0.0,0,0,0,0,Descartado
Isaac TeSlaa,WR,DET,MIN,6,32.8,123.8,28,Difícil,144.9,30.0,-8.7,3.5,1.7,0.0,0,0,0,0,Descartado
Daniel Jones,QB,IND,JAX,7,199.7,280.3,3,Favorable,242.7,218.3,+9.3,0.0,0.0,3.0,0,0,0,0,Descartado
Jonathan Taylor,RB,IND,JAX,7,83.9,51.5,32,Difícil,79.4,66.2,-21.1,3.7,2.4,20.0,0,0,0,0,Descartado
Tyler Warren,TE,IND,JAX,5,42.6,34.7,31,Difícil,55.6,33.0,-22.6,7.2,6.0,0.6,0,0,0,0,Descartado
Will Mallory,TE,IND,JAX,2,10.0,34.7,31,Difícil,41.9,9.0,-10.4,4.5,1.0,0.0,0,0,0,0,Descartado
Josh Downs,WR,IND,JAX,7,43.9,210.0,1,Favorable,161.1,51.8,+18.2,6.6,3.7,0.1,1,0,0,0,Incluido-Media
Keenan Allen,WR,IND,JAX,6,43.0,210.0,1,Favorable,159.4,51.2,+19.0,7.2,4.8,0.0,1,0,0,0,Incluido-Media
Alec Pierce,WR,IND,JAX,2,36.0,210.0,1,Favorable,153.4,44.0,+22.1,3.5,2.5,0.0,0,0,0,0,Descartado
Laquon Treadwell,WR,IND,JAX,7,28.1,210.0,1,Favorable,161.1,33.3,+18.2,3.7,2.1,0.0,0,0,0,0,Descartado
Trevor Lawrence,QB,JAX,IND,6,246.7,227.4,22,Difícil,242.9,237.2,-3.8,0.0,0.0,2.8,0,0,0,0,Descartado
Bhayshul Tuten,RB,JAX,IND,6,64.7,95.6,14,Neutral,95.4,64.7,+0.1,2.3,2.2,15.7,0,0,0,0,Descartado
Chris Rodriguez Jr.,RB,JAX,IND,6,28.0,95.6,14,Neutral,95.4,28.0,+0.1,0.3,0.2,6.5,0,0,0,0,Descartado
Brenton Strange,TE,JAX,IND,6,46.5,45.3,21,Neutral,57.0,40.8,-12.3,5.5,4.3,0.0,0,0,0,0,Descartado
Parker Washington,WR,JAX,IND,6,69.3,141.6,20,Neutral,158.3,64.9,-6.3,7.7,4.3,0.2,0,0,0,0,Descartado
Jakobi Meyers,WR,JAX,IND,6,47.5,141.6,20,Neutral,158.3,44.5,-6.3,4.7,3.3,0.2,0,0,0,0,Descartado
Patrick Mahomes,QB,KC,DEN,6,245.7,236.0,16,Neutral,215.1,260.0,+5.8,0.0,0.0,3.2,0,0,0,0,Descartado
Kenneth Walker III,RB,KC,DEN,6,116.8,102.0,12,Neutral,95.5,121.6,+4.1,4.5,3.0,20.0,0,0,0,0,Descartado
Travis Kelce,TE,KC,DEN,6,57.2,65.3,8,Favorable,50.6,67.1,+17.4,5.8,4.0,0.0,1,1,0,0,Incluido-Media
Tyquan Thornton,WR,KC,DEN,4,54.8,135.9,22,Difícil,134.8,55.0,+0.5,3.8,2.8,0.0,0,0,0,0,Descartado
Rashee Rice,WR,KC,DEN,4,47.5,135.9,22,Difícil,131.5,48.4,+2.0,4.2,3.2,0.0,0,0,0,0,Descartado
Xavier Worthy,WR,KC,DEN,6,36.2,135.9,22,Difícil,128.6,37.4,+3.4,5.8,4.0,0.0,0,0,0,0,Descartado
Matthew Stafford,QB,LA,LAC,7,284.1,216.2,27,Difícil,233.2,271.7,-4.4,0.0,0.0,2.0,0,0,0,0,Descartado
Kyren Williams,RB,LA,LAC,7,70.3,104.8,8,Favorable,98.7,72.9,+3.7,5.9,4.6,13.7,0,0,1,0,Incluido-Media
Blake Corum,RB,LA,LAC,7,45.1,104.8,8,Favorable,98.7,46.8,+3.7,2.0,1.4,9.1,0,0,0,0,Descartado
Ronnie Rivers,RB,LA,LAC,1,19.0,104.8,8,Favorable,72.7,24.0,+26.6,1.0,1.0,5.0,0,0,0,0,Descartado
Tyler Higbee,TE,LA,LAC,7,37.1,57.5,13,Neutral,55.2,38.1,+2.4,4.6,3.7,0.0,0,0,0,0,Descartado
Terrance Ferguson,TE,LA,LAC,3,21.0,57.5,13,Neutral,48.8,23.3,+10.7,4.0,2.3,0.0,0,0,0,0,Descartado
Colby Parkinson,TE,LA,LAC,6,17.2,57.5,13,Neutral,55.3,17.6,+2.3,3.2,2.3,0.0,0,0,0,0,Descartado
Puka Nacua,WR,LA,LAC,5,97.0,132.8,25,Difícil,161.1,86.8,-10.5,12.4,9.0,1.0,0,0,0,0,Descartado
Davante Adams,WR,LA,LAC,6,80.0,132.8,25,Difícil,145.8,75.7,-5.3,8.2,5.0,0.0,0,0,0,0,Descartado
Justin Herbert,QB,LAC,LA,6,190.2,191.1,30,Difícil,243.2,165.7,-12.8,0.2,0.0,4.8,0,0,0,0,Descartado
Omarion Hampton,RB,LAC,LA,6,48.2,85.7,17,Neutral,93.4,45.8,-5.0,1.7,1.5,13.3,0,0,0,0,Descartado
Keaton Mitchell,RB,LAC,LA,6,23.2,85.7,17,Neutral,93.4,22.0,-5.0,2.5,2.0,5.8,0,0,0,0,Descartado
David Njoku,TE,LAC,LA,2,33.5,41.7,26,Difícil,57.1,28.1,-16.2,4.0,3.0,0.0,0,0,0,0,Descartado
Charlie Kolar,TE,LAC,LA,4,19.5,41.7,26,Difícil,65.2,15.3,-21.6,3.2,2.2,0.0,0,0,0,0,Descartado
Oronde Gadsden II,TE,LAC,LA,6,17.2,41.7,26,Difícil,64.6,13.5,-21.3,3.5,2.0,0.2,0,0,0,0,Descartado
Tre Harris,WR,LAC,LA,5,45.0,106.0,31,Difícil,145.1,37.7,-16.2,5.0,3.0,0.0,0,0,0,0,Descartado
Ladd McConkey,WR,LAC,LA,5,40.0,106.0,31,Difícil,139.4,34.3,-14.4,3.6,2.6,0.0,0,0,0,0,Descartado
Quentin Johnston,WR,LAC,LA,5,33.0,106.0,31,Difícil,139.4,28.3,-14.4,4.4,1.6,0.4,0,0,0,0,Descartado
KeAndre Lambert-Smith,WR,LAC,LA,1,32.0,106.0,31,Difícil,121.0,29.6,-7.4,9.0,5.0,0.0,0,0,0,0,Descartado
Kirk Cousins,QB,LV,NYJ,7,268.1,202.9,28,Difícil,230.4,248.9,-7.2,0.0,0.0,2.1,0,0,0,0,Descartado
Ashton Jeanty,RB,LV,NYJ,7,46.9,106.6,5,Favorable,96.3,49.9,+6.4,6.3,4.9,15.1,0,0,0,0,Descartado
Mike Washington Jr.,RB,LV,NYJ,7,27.9,106.6,5,Favorable,96.3,29.6,+6.4,0.9,0.4,5.7,0,0,0,0,Descartado
Brock Bowers,TE,LV,NYJ,5,91.0,48.0,17,Neutral,46.5,92.8,+1.9,10.2,6.8,0.0,0,0,0,0,Descartado
Michael Mayer,TE,LV,NYJ,7,42.6,48.0,17,Neutral,54.0,39.7,-6.7,5.3,4.4,0.0,0,0,0,0,Descartado
Tre Tucker,WR,LV,NYJ,7,67.7,133.3,24,Difícil,139.3,65.9,-2.6,6.7,4.1,0.3,0,0,0,0,Descartado
Malik Willis,QB,MIA,NE,6,176.2,239.0,14,Neutral,231.7,179.5,+1.9,0.0,0.0,5.8,0,0,0,0,Descartado
Ollie Gordon II,RB,MIA,NE,6,56.5,83.4,19,Neutral,82.8,56.7,+0.4,1.3,1.0,12.0,0,0,0,0,Descartado
De'Von Achane,RB,MIA,NE,3,42.3,83.4,19,Neutral,97.4,38.7,-8.6,4.0,2.3,11.3,0,0,0,0,Descartado
Greg Dulcich,TE,MIA,NE,6,35.5,53.7,15,Neutral,64.2,32.0,-9.8,3.7,3.0,0.0,0,0,0,0,Descartado
Caleb Douglas,WR,MIA,NE,3,61.0,149.9,14,Neutral,136.5,64.6,+5.9,4.3,3.0,0.0,0,0,0,0,Descartado
Malik Washington,WR,MIA,NE,6,48.2,149.9,14,Neutral,134.7,51.4,+6.7,6.5,4.3,1.3,0,0,0,0,Descartado
Kyler Murray,QB,MIN,DET,4,198.5,312.3,1,Favorable,243.0,232.5,+17.1,0.0,0.0,5.8,1,0,0,0,Incluido-Media
Carson Wentz,QB,MIN,DET,2,138.0,312.3,1,Favorable,244.3,161.1,+16.7,0.0,0.0,4.0,0,0,0,0,Descartado
Aaron Jones,RB,MIN,DET,6,72.7,79.7,23,Difícil,90.8,67.3,-7.3,3.2,2.2,17.5,0,0,0,0,Descartado
Jordan Mason,RB,MIN,DET,2,63.5,79.7,23,Difícil,94.3,57.6,-9.3,1.0,0.0,15.0,0,0,0,0,Descartado
T.J. Hockenson,TE,MIN,DET,6,39.5,100.3,1,Favorable,56.7,57.7,+46.1,5.3,4.5,0.0,1,0,0,0,Incluido-Alta
Justin Jefferson,WR,MIN,DET,5,60.4,186.8,3,Favorable,149.8,69.4,+14.8,6.2,4.6,0.2,1,0,0,0,Incluido-Media
Jordan Addison,WR,MIN,DET,5,36.6,186.8,3,Favorable,146.1,42.7,+16.7,5.0,2.6,0.4,0,0,0,0,Descartado
Drake Maye,QB,NE,MIA,7,254.9,236.2,15,Neutral,233.2,256.8,+0.8,0.0,0.0,5.4,0,0,0,0,Descartado
Rhamondre Stevenson,RB,NE,MIA,7,40.7,102.5,11,Neutral,82.3,46.7,+14.7,3.4,2.9,11.0,0,0,0,0,Descartado
TreVeyon Henderson,RB,NE,MIA,6,33.8,102.5,11,Neutral,84.0,38.3,+13.2,1.2,0.8,8.7,0,0,0,0,Descartado
Corey Kiner,RB,NE,MIA,7,21.6,102.5,11,Neutral,82.3,24.7,+14.7,0.3,0.3,5.0,0,0,0,0,Descartado
Hunter Henry,TE,NE,MIA,7,42.3,74.7,4,Favorable,47.6,56.7,+34.1,4.4,3.7,0.0,1,0,0,0,Incluido-Media
Mack Hollins,WR,NE,MIA,4,52.2,115.5,30,Difícil,156.5,44.0,-15.7,5.0,3.8,0.0,0,0,0,0,Descartado
Romeo Doubs,WR,NE,MIA,6,43.5,115.5,30,Difícil,148.4,37.7,-13.3,4.0,2.3,0.0,0,0,0,0,Descartado
DeMario Douglas,WR,NE,MIA,7,36.6,115.5,30,Difícil,150.0,31.5,-13.8,4.9,3.3,0.0,0,0,0,0,Descartado
A.J. Brown,WR,NE,MIA,3,33.7,115.5,30,Difícil,126.1,32.0,-5.0,6.7,3.0,0.0,0,0,0,0,Descartado
Geno Smith,QB,NYJ,LV,7,231.9,245.1,11,Neutral,247.2,230.7,-0.5,0.0,0.0,3.1,0,0,0,0,Descartado
Braelon Allen,RB,NYJ,LV,7,59.7,124.9,1,Favorable,92.4,72.3,+21.1,2.9,2.1,13.0,1,0,0,0,Incluido-Media
Breece Hall,RB,NYJ,LV,3,54.3,124.9,1,Favorable,95.6,64.3,+18.4,3.3,3.3,17.0,1,0,0,0,Descartado
Kenyon Sadiq,TE,NYJ,LV,7,23.4,57.9,12,Neutral,58.9,23.2,-1.1,3.6,2.3,0.1,0,0,0,0,Descartado
Mason Taylor,TE,NYJ,LV,5,23.4,57.9,12,Neutral,55.8,23.9,+2.2,3.6,2.8,0.0,0,0,0,0,Descartado
Omar Cooper Jr.,WR,NYJ,LV,3,82.7,149.9,14,Neutral,144.6,84.5,+2.2,4.3,4.0,0.0,0,0,0,0,Descartado
Garrett Wilson,WR,NYJ,LV,7,63.4,149.9,14,Neutral,156.0,61.9,-2.4,7.3,5.3,0.0,0,0,0,0,Descartado
Adonai Mitchell,WR,NYJ,LV,3,41.0,149.9,14,Neutral,145.9,41.7,+1.6,6.0,3.0,0.0,0,0,0,0,Descartado
Tanner McKee,QB,PHI,WAS,2,213.0,265.7,5,Favorable,229.8,233.0,+9.4,0.0,0.0,1.0,0,0,0,0,Descartado
Jalen Hurts,QB,PHI,WAS,5,186.6,265.7,5,Favorable,255.4,191.1,+2.4,0.0,0.0,4.6,0,0,0,0,Descartado
Saquon Barkley,RB,PHI,WAS,5,48.8,77.7,25,Difícil,89.7,44.9,-8.1,1.8,1.2,8.6,0,0,0,0,Descartado
Dameon Pierce,RB,PHI,WAS,3,32.0,77.7,25,Difícil,97.0,28.2,-12.0,3.7,2.3,12.3,0,0,0,0,Descartado
Tank Bigsby,RB,PHI,WAS,4,22.8,77.7,25,Difícil,86.1,21.4,-5.9,1.0,0.8,7.0,0,0,0,0,Descartado
Dallas Goedert,TE,PHI,WAS,5,45.6,73.5,5,Favorable,48.0,60.2,+32.0,6.2,4.4,0.0,1,1,0,0,Incluido-Media
DeVonta Smith,WR,PHI,WAS,4,77.5,158.3,10,Favorable,158.0,77.6,+0.1,10.2,6.5,0.0,0,0,0,0,Descartado
Dontayvion Wicks,WR,PHI,WAS,6,47.3,158.3,10,Favorable,159.9,47.1,-0.6,5.3,3.2,0.0,0,0,0,0,Descartado
Makai Lemon,WR,PHI,WAS,7,27.7,158.3,10,Favorable,161.2,27.4,-1.0,5.1,3.6,0.1,0,0,0,0,Descartado
Aaron Rodgers,QB,PIT,CLE,7,242.7,220.7,25,Difícil,242.0,229.9,-5.3,0.0,0.0,1.7,0,0,0,0,Descartado
Jaylen Warren,RB,PIT,CLE,7,80.1,104.0,9,Favorable,88.2,88.8,+10.8,4.9,3.4,14.6,1,1,0,0,Incluido-Alta
Rico Dowdle,RB,PIT,CLE,4,29.5,104.0,9,Favorable,86.6,33.1,+12.0,4.2,3.2,7.8,0,0,0,0,Descartado
Pat Freiermuth,TE,PIT,CLE,7,28.6,49.3,16,Neutral,62.4,25.0,-12.6,4.7,3.3,0.4,0,0,0,0,Descartado
Darnell Washington,TE,PIT,CLE,7,22.9,49.3,16,Neutral,62.4,20.0,-12.6,3.3,2.3,0.0,0,0,0,0,Descartado
DK Metcalf,WR,PIT,CLE,7,53.4,150.3,13,Neutral,148.3,53.9,+0.8,8.3,4.6,0.1,0,0,0,0,Descartado
Roman Wilson,WR,PIT,CLE,5,37.6,150.3,13,Neutral,152.3,37.3,-0.8,5.0,2.8,0.0,0,0,0,0,Descartado
Germie Bernard,WR,PIT,CLE,7,36.3,150.3,13,Neutral,143.4,37.3,+2.9,5.3,3.9,0.1,0,0,0,0,Descartado
Michael Pittman,WR,PIT,CLE,3,29.7,150.3,13,Neutral,150.7,29.6,-0.2,4.0,2.3,0.0,0,0,0,0,Descartado
Sam Darnold,QB,SEA,CHI,5,255.4,241.3,13,Neutral,230.1,262.9,+2.9,0.0,0.0,1.8,0,0,0,0,Descartado
Drew Lock,QB,SEA,CHI,2,211.0,241.3,13,Neutral,245.3,208.9,-1.0,0.0,0.0,1.0,0,0,0,0,Descartado
Emanuel Wilson,RB,SEA,CHI,7,57.6,73.6,28,Difícil,88.2,51.9,-9.9,1.3,0.9,15.9,0,0,0,0,Descartado
Jadarian Price,RB,SEA,CHI,3,39.7,73.6,28,Difícil,87.8,35.8,-9.7,2.3,1.3,9.3,0,0,0,0,Descartado
George Holani,RB,SEA,CHI,7,15.4,73.6,28,Difícil,88.2,13.9,-9.9,2.0,1.7,5.1,0,0,0,0,Descartado
AJ Barner,TE,SEA,CHI,7,25.7,56.6,14,Neutral,65.8,23.6,-8.4,4.1,2.7,0.6,0,0,0,0,Descartado
Jaxon Smith-Njigba,WR,SEA,CHI,7,123.9,149.4,16,Neutral,132.2,133.6,+7.8,11.1,8.3,0.4,0,0,0,1,Incluido-Media
Cooper Kupp,WR,SEA,CHI,7,28.4,149.4,16,Neutral,132.2,30.7,+7.8,3.9,2.6,0.0,0,0,0,0,Descartado
Rashid Shaheed,WR,SEA,CHI,7,23.3,149.4,16,Neutral,132.2,25.1,+7.8,4.3,2.3,0.6,0,0,0,0,Descartado
Baker Mayfield,QB,TB,ATL,3,205.0,271.4,4,Favorable,220.7,233.3,+13.8,0.0,0.0,3.7,1,0,0,0,Incluido-Media
Jalon Daniels,QB,TB,ATL,3,167.0,271.4,4,Favorable,238.4,180.9,+8.3,0.3,0.3,6.3,0,0,0,0,Descartado
Bucky Irving,RB,TB,ATL,7,79.7,81.7,21,Neutral,91.4,74.6,-6.4,3.3,2.6,17.1,0,0,0,0,Descartado
Cade Otton,TE,TB,ATL,7,26.6,62.7,9,Favorable,52.5,29.7,+11.7,4.3,2.7,0.0,0,0,0,0,Descartado
Emeka Egbuka,WR,TB,ATL,6,40.0,169.9,8,Favorable,148.2,43.5,+8.8,8.2,4.7,0.3,0,0,0,0,Descartado
Chris Godwin Jr.,WR,TB,ATL,7,34.7,169.9,8,Favorable,149.7,37.5,+8.1,4.9,3.9,0.4,0,0,0,0,Descartado
Cam Ward,QB,TEN,CIN,7,168.4,253.8,7,Favorable,236.7,175.7,+4.3,0.0,0.0,2.7,0,0,0,0,Descartado
Tony Pollard,RB,TEN,CIN,7,68.3,80.5,22,Difícil,102.0,59.7,-12.6,2.3,1.6,16.0,0,0,0,0,Descartado
Carnell Tate,WR,TEN,CIN,7,59.0,137.5,21,Neutral,162.0,53.6,-9.1,7.3,4.9,0.0,0,0,0,0,Descartado
Wan'Dale Robinson,WR,TEN,CIN,7,29.3,137.5,21,Neutral,162.0,26.6,-9.1,6.1,4.1,0.1,0,0,0,0,Descartado
Jayden Daniels,QB,WAS,PHI,4,189.8,247.9,9,Favorable,226.0,200.8,+5.8,0.0,0.0,6.2,0,0,0,0,Descartado
Athan Kaliakmanis,QB,WAS,PHI,1,186.0,247.9,9,Favorable,226.7,196.4,+5.6,0.0,0.0,3.0,0,0,0,0,Descartado
Marcus Mariota,QB,WAS,PHI,2,147.0,247.9,9,Favorable,196.8,169.9,+15.6,0.0,0.0,3.0,0,0,0,0,Descartado
Jacory Croskey-Merritt,RB,WAS,PHI,5,47.8,116.7,3,Favorable,100.3,52.5,+9.8,1.4,1.0,13.4,0,0,0,0,Descartado
Rachaad White,RB,WAS,PHI,5,29.0,116.7,3,Favorable,96.6,32.6,+12.5,3.0,2.8,7.2,0,0,0,0,Descartado
Jeremy McNichols,RB,WAS,PHI,1,13.0,116.7,3,Favorable,84.5,16.0,+22.9,0.0,0.0,5.0,0,0,0,0,Descartado
Chig Okonkwo,TE,WAS,PHI,4,37.5,43.0,24,Difícil,44.5,36.7,-2.0,5.0,3.8,0.0,0,0,0,0,Descartado
Terry McLaurin,WR,WAS,PHI,5,46.0,184.0,4,Favorable,137.2,55.4,+20.5,5.4,3.0,0.0,1,0,0,0,Descartado
Stefon Diggs,WR,WAS,PHI,5,42.8,184.0,4,Favorable,139.1,51.1,+19.4,7.6,4.8,0.0,1,0,0,0,Incluido-Media
Antonio Williams,WR,WAS,PHI,6,34.2,184.0,4,Favorable,137.2,41.2,+20.5,4.3,3.0,0.0,0,0,0,0,Descartado
```

_Fin del prompt. Recuerda: análisis de patrones, no garantía ni recomendación de apuesta. Solo mayores de 18 años._
