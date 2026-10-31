# Prompt para Claude Design: mejorar el diseño de "La Línea · NFL Semana 8"

**Cómo usarlo:** abre Claude Design, adjunta `index.html` (la app completa, con los datos y el cálculo incluidos) y pega todo lo que está debajo de la línea.

---

Te adjunto `index.html`. Es una app en español que ya funciona: "La Línea · NFL Semana 8". Quiero que **mejores el diseño visual y la experiencia de uso**. La lógica y los datos deben quedar exactamente igual.

## Qué hace la app (no cambiar el funcionamiento)

1. **Pestaña Partidos:** a la izquierda están los 13 partidos de la semana 8 y un buscador para los 188 jugadores. Al elegir un partido aparecen los jugadores de ambos equipos (QB, RB, WR, TE), con filtro por posición. Cada jugador tiene una etiqueta de matchup: Favorable, Intermedio o Difícil.
2. **Ficha del jugador:**
   - El usuario elige la estadística según la posición:
     - QB: yardas de pase, pases completos y TD de pase.
     - RB: yardas por tierra, acarreos, recepciones y TD.
     - WR y TE: yardas recibidas, recepciones y TD.
   - Mueve "Tu línea" con un deslizador, con los botones − y +, o escribiendo el número.
   - La app muestra el % de llegar a esa línea o superarla y una etiqueta de dificultad: Muy fácil, Fácil, Parejo, Difícil o Muy difícil.
   - También muestra dos gráficas:
     - la distribución del modelo con la línea marcada;
     - los valores del jugador juego por juego contra la línea.
3. **Pestaña Partidos favorables:** las 21 selecciones del análisis, agrupadas por partido. Cada una muestra el % en sus líneas sugeridas, el "Por qué" desplegable y un botón para abrir la ficha.

## Reglas que NO puedes romper

- **No toques la matemática.** El primer `<script>` (el objeto `window.Props`: `probLlegar`, `etiquetaDificultad`, `probRaw`) se queda tal cual, carácter por carácter. Está verificado contra Python/SciPy en 1,648 casos.
- **No toques los datos.** El `<script id="data" type="application/json">` se queda igual. No redondees, no filtres ni inventes valores.
- **Mantén los textos y avisos:**
  - Este aviso debe verse en todas las pantallas: "Análisis de patrones, no garantía ni recomendación de apuesta. Solo mayores de 18 años."
  - Mantén la nota de lesiones (práctica hasta el jueves 29-oct; designaciones finales sin verificar; SEA sin reporte).
  - Mantén la frase de calibración ("Cuando la app dijo X en las semanas 7 y 8, se cumplió el Y%").
- **No agregues** cuotas, momios, líneas de casas de apuestas, parlays, PPR ni botones de "apostar".
- Mantén las rutas `#partidos`, `#favorables` y `#jugador-<id>`, y el paso de 0.5 en la línea.
- Todo en español. Sin librerías externas, salvo Google Fonts.
- Debe verse bien en el celular, desde 390 px de ancho y sin scroll horizontal, y en modo claro y oscuro.

## Pruebas para confirmar que no rompiste nada

Busca "Hockenson" en la app. Con las líneas sugeridas debe dar:

| Estadística | Línea | Resultado |
|---|---|---|
| Yardas recibidas | 48.5 | **44% Parejo** |
| Recepciones | 5 | **53% Parejo** |
| TD | 1 | **34% Difícil** |

Si sube las yardas a 80, debe dar **29% Difícil**.

## Lo que sí quiero que mejores

- **Jerarquía de la ficha:** el % y la etiqueta de dificultad son lo más importante. Deben leerse al instante, y el cambio al mover la línea debe sentirse vivo (animación sutil del número; respeta `prefers-reduced-motion`).
- **El control de la línea:** la idea es la "línea amarilla de primera y diez" de la TV. Hazlo más táctil y claro. Por ejemplo, que el deslizador se vea como una franja de campo con marcas de yardas, con la proyección y la línea sugerida marcadas encima.
- **Gráficas:** más limpias y legibles, con etiquetas que no choquen con la línea amarilla. En la gráfica juego por juego, distingue claramente "llegó" y "no llegó".
- **Lista de jugadores:** que se escanee mejor. Destaca a los de las 21 selecciones (ALTA y MEDIA) y a los que tienen alerta de lesión.
- **Partidos favorables:** que funcione como un tablero. Pon arriba un resumen (las 3 de confianza ALTA) y luego el detalle por partido.
- **Celular:** que la ficha sea cómoda con el pulgar (la línea y el % visibles a la vez) y que la lista de partidos se pueda recorrer con el dedo.
- **Identidad:** conserva el nombre "La Línea", el amarillo de la línea de primera y diez y el verde de césped. Puedes refinar tipografía, espaciado y detalles. Evita que parezca una plantilla genérica o una casa de apuestas.

Entrégame un solo `index.html` completo, con el mismo primer `<script>` y el mismo bloque de datos sin cambios.
