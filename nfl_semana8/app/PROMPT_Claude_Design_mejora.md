# Prompt para Claude Design: rediseño de "La Línea · NFL Semana 8" (recheck final)

**Cómo usarlo:** abre Claude Design, adjunta `index.html` (la app completa, con datos y cálculo incluidos) y pega todo lo que está debajo de la línea.

---

Te adjunto `index.html`: "La Línea · NFL Semana 8", una app en español que ya funciona y ya pasó todas sus pruebas. Quiero que **rediseñes lo visual y la experiencia de uso** para que se vea y se sienta de primer nivel. La lógica, los cálculos y los datos deben quedar **exactamente iguales**.

## Qué hace la app (no cambies el funcionamiento)

### 1. Pestaña "Partidos"
- A la izquierda están los 13 partidos de la semana 8. Cada uno muestra cuántos favoritos tiene. Hay un buscador para los 269 jugadores con participación probable.
- Al elegir un partido, el encabezado muestra los **nombres completos** con visita y local. Ejemplo: "Tennessee Titans (visita) @ Cincinnati Bengals (local)". También muestra fecha, hora de Monterrey, estadio y récords, y debajo dos líneas sobre dónde es blanda o dura cada defensa.
- Debajo hay **dos columnas**:
  - **Visita**, con el nombre completo del equipo.
  - **Local**, con el nombre completo del equipo.
- Cada columna muestra:
  - "No juegan" (bajas del reporte final).
  - "Línea ofensiva" (titulares que faltan).
  - **Todos** los jugadores con participación probable (QB, RB, WR, TE). Cada uno con su rol (Titular, Rotación o Rol menor), % de snaps, etiqueta de matchup (Favorable, Intermedio o Difícil), marcas de estado (★ ALTA o MEDIA si es favorito, "Duda", "Pendiente" y "Regresa") y, si tiene participación decente, la línea **"Lo más probable"** (su estadística con mayor probabilidad de superar su promedio).
- Al final del partido va la sección **"Mis favoritos para sobresalir"**. Cada tarjeta muestra:
  - **"Lo que más me convence"**: la estadística elegida y su línea, más "También califican" si hay otras;
  - el % de superar su propio promedio y todos sus juegos de la temporada;
  - la línea y la proyección;
  - las razones (rival ajustado, compañeros, línea ofensiva);
  - el riesgo;
  - un botón para abrir la ficha.
- Si el partido no tiene favorito, se muestra "Sin favorito claro" y el más cercano. Hay 4 partidos así; es intencional.
- Debajo puede aparecer **"Descartados por matchup"**: jugadores con buen % que no entran porque su ventaja no viene del rival.

### 2. Ficha del jugador
- Encabezado con estado de lesión y si es favorito.
- Pestañas de estadística según la posición:
  - QB: yardas de pase, pases completos y TD de pase.
  - RB: yardas por tierra, acarreos, recepciones, **yardas recibidas** y TD (5 pestañas).
  - WR y TE: yardas recibidas, recepciones y TD.
- Datos clave: promedio, proyección, lo que permite el rival (ajustado) y el matchup en esa estadística.
- **Desglose de factores** en 4 cajas: Rival (ajustado por ambos lados), Línea ofensiva, Compañeros y Ajuste total. El promedio usa todos los juegos de 2026.
- **"Lo que más le gusta al modelo"**: lista de sus estadísticas ordenadas por probabilidad de superar su promedio; al tocar una se cambia la pestaña.
- **"Tu línea"**: se mueve con un deslizador, con − y +, o escribiendo el número, en pasos de 0.5. Arranca en la **línea justa** (la más cercana a 50%) y tiene un botón para volver a ella.
- **Veredicto**: el % de llegar a la línea o superarla y la etiqueta (Muy fácil, Fácil, Parejo, Difícil o Muy difícil). Debe conservar la frase de calibración ("cuando el modelo dijo X, se cumplió el Y%").
- Dos gráficas:
  - la distribución del modelo con la línea amarilla y la proyección;
  - los valores juego por juego contra la línea.

### 3. Pestaña "Mis favoritos"
- Todos los favoritos, primero los de confianza alta y luego los de confianza media.
- Dos tablas: "Cambios frente a mi lista anterior" y "Las 21 selecciones de la primera corrida".
- Las fuentes del reporte de lesiones, con enlaces.

## Reglas que NO puedes romper

- **No toques la matemática.** El primer `<script>` (el objeto `window.Props`: `probLlegar`, `etiquetaDificultad`, `probRaw`) se queda tal cual, carácter por carácter. Está verificado contra Python/SciPy en 2,773 casos.
- **No toques los datos.** El `<script id="data" type="application/json">` se queda igual: sin redondear, filtrar, reordenar ni inventar nada.
- **No cambies qué se calcula ni cómo.** El % siempre sale de `Props.probLlegar(stat, linea, metadatos)` y la etiqueta, de `Props.etiquetaDificultad`.
- **Mantén todos los textos informativos:**
  - El aviso en todas las pantallas: "Análisis de patrones, no garantía ni recomendación de apuesta. Solo mayores de 18 años."
  - La nota de lesiones (CHI-SEA juega el lunes y su reporte final sale el sábado).
  - Las razones y riesgos de cada favorito.
  - La explicación de cómo se calcula.
  - Los números de la prueba del modelo en el pie.
- **No agregues** cuotas, momios, líneas de casas de apuestas, parlays, PPR ni botones de "apostar".
- Mantén las rutas `#partidos`, `#favoritos` y `#jugador-<id>`.
- Todo en español. Sin librerías externas, salvo Google Fonts.
- Debe verse impecable en el celular, desde 390 px de ancho y sin scroll horizontal, y en modo claro y oscuro.

## Pruebas para confirmar que no rompiste nada

Abre cada jugador y revisa:

| Jugador | Estadística | Línea | Debe dar |
|---|---|---|---|
| Kyler Murray | Yardas de pase | 215.5 (línea justa) | **50% Parejo** |
| Kyler Murray | Yardas de pase | 250.5 | **33% Difícil** |
| Jacoby Brissett | Yardas de pase | 228.5 | **59% Parejo** |
| Chris Godwin Jr. | Recepciones | 3.5 | **65% Fácil** |
| Rhamondre Stevenson | Yardas recibidas (RB) | 23.5 (línea justa) | **50% Parejo** |
| Bijan Robinson | Yardas por tierra | 100.5 | **53% Parejo** |

Revisa también:
- El encabezado de TEN @ CIN dice "Tennessee Titans (visita) @ Cincinnati Bengals (local)".
- Cada RB tiene 5 pestañas: yardas por tierra, acarreos, recepciones, yardas recibidas y TD.
- Hay 14 favoritos. Los 2 de confianza alta son Kyler Murray y Chris Godwin Jr.
- CLE @ PIT, LAC @ LA, KC @ DEN, PHI @ WAS y CHI @ SEA muestran "Sin favorito claro".
- En ATL @ TB, Bijan Robinson aparece en "Descartados por matchup".
- El ranking de defensas se lee como "#X de 32 que más permite" (1 = la más blanda, 32 = la más dura). Conserva esa aclaración.

## Lo que sí quiero que mejores

- **El partido como protagonista:** que el enfrentamiento visita contra local se lea como un marcador de estadio. Nombres completos grandes, quién es visita y quién es local muy claro, y las dos columnas fáciles de comparar.
- **Lista de jugadores:** que se escanee rápido por posición. Destaca a los titulares, a los favoritos (★) y las alertas (Duda, Pendiente, Regresa) sin saturar.
- **"Mis favoritos para sobresalir":** que se sienta como la sección estrella de cada partido. "Lo que más me convence" bien destacado, el % grande, las razones en lenguaje claro y el riesgo visible. "Lo más probable" de cada jugador debe leerse fácil en la lista sin saturarla.
- **Ficha:** el % y la etiqueta son lo más importante y deben leerse al instante. Al mover la línea, el cambio debe sentirse vivo, con una animación sutil del número que respete `prefers-reduced-motion`. El desglose de factores debe entenderse de un vistazo, en verde si suma y en rojo si resta.
- **Control de la línea:** la idea es la "línea amarilla de primera y diez" de la TV. Hazlo táctil, con marcas de yardas, y con la proyección y la línea justa marcadas.
- **Gráficas:** limpias, con etiquetas que no choquen y "llegó" contra "no llegó" muy claro.
- **Celular:** la ficha cómoda con el pulgar (línea y % visibles a la vez) y la lista de partidos recorrible con el dedo.
- **Pestañas de estadística:** los RB tienen 5 (yardas por tierra, acarreos, recepciones, yardas recibidas y TD) y los demás 3 o 4. Diseña el selector para que 5 pestañas quepan completas y legibles en 390 px, sin cortar texto ni obligar a deslizar de lado. Por ejemplo, en dos filas o como botones segmentados que se acomodan. Los nombres deben verse completos. La lista "Lo que más le gusta al modelo" también puede tener hasta 5 filas: que no empuje el % y la línea fuera de la vista.
- **Identidad:** conserva el nombre "La Línea", el amarillo de primera y diez y el verde de césped. Refina tipografía, espaciado y jerarquía. Que no parezca plantilla genérica ni casa de apuestas.

Entrégame un solo `index.html` completo, con el mismo primer `<script>` y el mismo bloque de datos sin cambios.
