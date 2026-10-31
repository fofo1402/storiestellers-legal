# Instrucciones para la sesión LOCAL de Claude Code (con navegador integrado)

**Cómo usar este archivo:**
1. En la app de escritorio de Claude, abre una sesión nueva de **Code en modo local**, en una carpeta de tu disco (por ejemplo `Documentos/nfl_semana8`).
2. Copia a esa carpeta estos archivos: `props_data.json`, `props.js`, `casos_prueba.json`, `INSTRUCCIONES_SESION_LOCAL.md` (y opcionalmente `data.json`, `NFL_2026_S8_matchups.xlsx`).
3. Escríbele a esa sesión: **"Lee INSTRUCCIONES_SESION_LOCAL.md y ejecútalo."**

---

## PARTE 1 · Instrucciones para el Claude local (tú eres el "jefe" de Claude Design)

Tu trabajo: usar el navegador integrado para abrir **Claude Design** (claude.ai/design), pedirle la app descrita en la PARTE 2, revisar lo que construya y pedir correcciones hasta que pase todas las pruebas de la PARTE 3. No cambies números ni metodología: la verdad está en `props_data.json` y `props.js`.

Pasos:
1. Abre claude.ai/design en el navegador integrado (el usuario ya inició sesión). Crea un proyecto nuevo llamado "NFL 2026 · S8 · Qué tan difícil es llegar".
2. Adjunta `props_data.json` y `props.js`. Si Claude Design no acepta archivos, pega primero `props.js` completo y luego dile que cargue los datos desde un archivo que tú le subas; si no hay forma de subir el JSON (≈ 0.5 MB), pídele que la app tenga un botón "Cargar datos (props_data.json)" y cárgalo tú desde la carpeta.
3. Pega el prompt de la PARTE 2 tal cual.
4. Cuando entregue, **prueba tú** la app en el navegador con la PARTE 3. Toma capturas. Si algo falla, explícale exactamente qué falló (jugador, estadística, línea, valor esperado vs. mostrado) y pide la corrección. Repite.
5. Al terminar, reporta al usuario: link del proyecto, capturas (celular y escritorio), resultado de cada prueba y cualquier limitación.
6. Reglas: no inventes datos; no agregues líneas de casas de apuestas, cuotas, parlays ni PPR; el aviso legal debe verse siempre. Si algo no se puede hacer, avísale al usuario en vez de improvisar.

---

## PARTE 2 · Prompt para Claude Design (pegar tal cual)

Construye una **app web en español (México)**, móvil primero, llamada **"¿Qué tan difícil es llegar? · NFL 2026 · Semana 8"**. Usa EXCLUSIVAMENTE los datos de `props_data.json` y, para cualquier probabilidad, la función `Props.probLlegar(stat, linea, metadatos)` y `Props.etiquetaDificultad(p, metadatos)` de `props.js` **copiadas sin modificar** (están verificadas; no reimplementes la matemática).

### Qué hace
El usuario elige un partido y un jugador. La app le dice:
1. Si el **matchup** del jugador es **Favorable, Intermedio o Difícil** (campo `lectura_general`; y por estadística, `stats[i].lectura`).
2. Elige una **estadística** según su posición y mueve una **línea** (control deslizante + botones − / + + campo numérico). La app muestra la **probabilidad de alcanzar o superar esa línea** y una **etiqueta de dificultad**:
   - ≥ 80% **Muy fácil** · 60-80% **Fácil** · 40-60% **Parejo** · 20-40% **Difícil** · < 20% **Muy difícil** (vienen en `metadatos.etiquetas`).

Estadísticas por posición (ya vienen en `stats[]` de cada jugador, en este orden):
- **QB:** Yardas de pase · Pases completos · TD de pase.
- **RB:** Yardas por tierra · Acarreos · Recepciones · TD (tierra o recepción).
- **WR:** Yardas recibidas · Recepciones · TD (recepción o tierra).
- **TE:** Yardas recibidas · Recepciones · TD (recepción o tierra).

### Estructura (pestañas; en móvil, barra inferior)
**1. Partidos (inicio).** Lista de los 13 partidos (`partidos[]`) agrupados por horario de Monterrey (`fecha_hora_monterrey`): Dom 12:00, 15:05, 15:25, 19:20 y Lun 19:15. Al tocar un partido: dos columnas (visitante / local) con sus jugadores (`jugadores[]` filtrando por `partido` y `equipo`), cada uno con posición y una insignia de matchup (Favorable/Intermedio/Difícil). Buscador global por nombre.

**2. Ficha del jugador** (pantalla de detalle):
- Encabezado: nombre, posición, "EQUIPO vs RIVAL", insignia grande de matchup general (`lectura_general`, rank `rank_general`/32), estado de lesión (`estado_lesion`) con etiqueta ámbar **"Estatus sin verificar"** si el texto contiene "sin verificar" o "Sin reporte", y "Muestra corta" si `pj` ≤ 5.
- Selector de estadística (pestañas tipo segmento con las de su posición).
- **Línea:** valor inicial = `linea_sugerida`. Paso 0.5. Rango: 0 hasta max(2.5 × `proyeccion`, máximo del `registro` + 10, 3 para TD). Para estadísticas de conteo y TD, explica en texto que "llegar a 5.5 recepciones" = 6 o más.
- **Resultado grande:** probabilidad en % (1 decimal) + etiqueta de dificultad con color (escala de 5 colores, del azul "Muy fácil" al naranja oscuro "Muy difícil"; no uses rojo/verde solos; acompaña con texto e ícono). Se recalcula en vivo al mover la línea.
- **Curva:** gráfica de la probabilidad de llegar vs. línea (calculada con `probLlegar` en ~60 puntos del rango) con un marcador en la línea actual y franjas de fondo por dificultad.
- **Historial:** barras de `registro[]` (un valor por juego: semana, rival, L/V) con una línea horizontal en la línea elegida; texto "Llegó o superó la línea en X de N juegos".
- **Contexto del matchup para esa estadística:** "RIVAL permite `rival_permite_pj` por juego a su posición (rank `rival_rank`/32, `lectura`)", "Promedio del jugador `media_temporada`", "Proyección para este juego `proyeccion`".
- Si el jugador tiene `seleccion` (no nulo): tarjeta "Selección del análisis" con `confianza` (Alta/Media), `categorias`, `por_que` y el bloque (a) qué la sube, (b) qué la frena, (c) regla aplicada.

**3. Partidos favorables.** Lista de las 21 selecciones (`selecciones[]`) agrupadas por partido y horario, con insignia Alta/Media, categorías y `cambio` (en %). Arriba, un texto: "Jugadores con el matchup más favorable según el análisis (3 Alta, 18 Media)". Cada tarjeta abre la ficha del jugador. Recalca que el usuario puede investigar libremente a cualquier otro jugador desde la pestaña Partidos.

**4. Cómo se calcula.** Explica en lenguaje simple:
- Proyección = promedio del jugador × factor de matchup, con factor = 1 + w × (lo que permite el rival ÷ lo que permitían los rivales que ya enfrentó − 1), w = `metadatos.peso_w_probabilidad` (0.3).
- La probabilidad usa la variabilidad juego a juego del jugador (yardas: distribución gamma; conteos: binomial negativa o binomial; TD: Poisson) y una recalibración probada con datos reales.
- **Prueba hacia atrás** (semanas 4-8, solo con datos previos a cada juego, 10,465 predicciones): el ajuste por matchup ayuda poco (error Brier 0.1998 sin ajuste vs. 0.1985 con w = 0.3 en semanas 7-8). Calibración en semanas 7-8: cuando dice Muy difícil → ocurrió 11%; Difícil → 30%; Parejo → 48%; Fácil → 71%; Muy fácil → 90%.
- Limitaciones: `metadatos.avisos[]`. Fuente: nflverse (ESPN bloqueado en el entorno de análisis). Muestras de 3 a 8 juegos.
- Datos al: `metadatos.datos_al`.

### Reglas
- Aviso fijo visible en todas las pantallas: **"Análisis de patrones, no garantía ni recomendación de apuesta. Solo mayores de 18 años."**
- Nada de líneas de casas de apuestas, cuotas, spreads, parlays, PPR ni puntos de fantasy. La línea la decide el usuario.
- No inventes datos ni texto analítico; si falta un valor, "n/d".
- Sin logos ni fotos de equipos o jugadores; usa siglas en pastillas.
- Estilo: panel deportivo sobrio (no estética de casino), tipografía con cifras tabulares, modo claro y oscuro, contraste AA, accesible con teclado.

---

## PARTE 3 · Pruebas de aceptación (el Claude local las verifica en la app)

1. 13 partidos; 188 jugadores; pestaña Partidos favorables con 21 tarjetas (3 Alta: T.J. Hockenson, Jaylen Warren, Zay Flowers).
2. Matchup general: Hockenson = Favorable (rank 1); Jared Goff = Difícil; Jonathan Taylor = Difícil; Kenneth Walker III = Intermedio.
3. Probabilidades exactas (deben mostrarse con 1 decimal):
   - T.J. Hockenson · Yardas recibidas · línea 48.5 → **44.0% · Parejo**
   - T.J. Hockenson · Recepciones · línea 5 → **52.7% · Parejo**
   - T.J. Hockenson · TD · línea 1 → **33.9% · Difícil**
   - Además, verifica 10 casos al azar de `casos_prueba.json` (campo `prob`, en fracción): la app debe mostrar el mismo % redondeado a 1 decimal.
4. Mover la línea hacia arriba nunca sube la probabilidad (monótona).
5. Línea 0 → 100%; línea muy alta → cerca de 0% y "Muy difícil".
6. Estatus sin verificar etiquetado (por ejemplo Lamar Jackson, Travis Kelce, Michael Wilson; todos los de SEA).
7. El aviso legal aparece en todas las pantallas; no hay ninguna cuota ni línea de apuestas.
8. Se ve bien a 390 px de ancho y a 1440 px.
