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

