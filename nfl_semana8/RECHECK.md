# Recheck final · NFL 2026 Semana 8

Corrida del sábado 31-oct-2026 (madrugada, hora Monterrey). Lesiones: reporte final del viernes 30-oct (CHI-SEA pendiente; sale el sábado).

## Cómo se eligió el modelo

1. Tabla de prueba: 10,465 predicciones jugador-estadística-línea de las semanas 4 a 8, cada una hecha solo con datos anteriores a ese juego.
2. Etapa 1: 40,000 combinaciones aleatorias de 13 parámetros (forma reciente, peso del rival por tierra/pase/TD, referencia 2025, línea ofensiva, compañeros, dispersión, guion del partido, localía).
3. Etapa 2: las 300 mejores, con validación por semana (cada semana se predice calibrando solo con las demás).
4. Etapa 3: refinamiento local desde las 10 mejores.

| Modelo | Error (Brier, validación por semana) | Acierta el lado | Acierta el lado si la prob. es ≥60% o ≤40% |
|---|---|---|---|
| Sin ajustes | 0.2016 | 68.4% | 74.2% |
| Modelo v4 | 0.1982 | 69.2% | 74.7% |
| **Elegido** | **0.1978** | **69.2%** | **75.0%** |

La mejora contra no ajustar es estadísticamente segura (IC95 +0.0013 a +0.0063). Contra el v4 es pequeña (positiva en 87% de las simulaciones). El guion del partido y la localía no mejoraron y quedaron fuera.

**Parámetros elegidos:** forma reciente (vida media 2 juegos, mezcla 50/50 con el promedio de 2026); rival ajustado por ambos lados con la temporada 2025 como referencia (ρ 0.5, 12 juegos); peso del rival 1.0 en pase, 0.65 en tierra, 0.8 en TD; línea ofensiva −6% por titular (solo tierra); compañeros: targets ×0.25, acarreos ×1.0; dispersión ×0.9.

Calibración final: Muy difícil 12%, Difícil 30%, Parejo 50%, Fácil 70%, Muy fácil 88%.

## Reglas de favorito

Se evalúan todas las estadísticas del jugador (con mínimos: 30 yds recibidas, 3 recepciones, 40 yds por tierra, 10 acarreos, 0.5 TD/juego). Una estadística califica si: ≥55% de superar su propio promedio, ajuste total ≥ +4%, el matchup de esa estadística no es Difícil y el rival no resta. Alta: ≥60%, matchup Favorable, sano, 4+ juegos, uso reciente normal y sin mala racha.

## Favoritos

| Partido | Jugador | Confianza | Lo que más me convence | % de superar su promedio |
|---|---|---|---|---|
| BAL @ BUF | James Cook | Media | TD (tierra o recepción) 1 o más | 59% |
| BAL @ BUF | Khalil Shakir | Media | Recepciones 4 o más | 56% |
| TEN @ CIN | Cam Ward | Media | Yardas de pase 168.5+ yds | 58% |
| ARI @ DAL | Jacoby Brissett | Alta | Yardas de pase 228.5+ yds | 61% |
| ARI @ DAL | Dak Prescott | Media | TD de pase 2 o más | 59% |
| MIN @ DET | Kyler Murray | Alta | TD de pase 1 o más | 67% |
| IND @ JAX | Trevor Lawrence | Media | Pases completos 20 o más | 62% |
| CLE @ PIT | Deshaun Watson | Media | Pases completos 20 o más | 56% |
| ATL @ TB | Chris Godwin Jr. | Alta | Recepciones 4 o más | 65% |
| ATL @ TB | Bucky Irving | Alta | TD (tierra o recepción) 1 o más | 60% |
| ATL @ TB | Baker Mayfield | Media | TD de pase 1 o más | 69% |
| ATL @ TB | Michael Penix Jr. | Media | Pases completos 20 o más | 56% |
| NE @ MIA | Hunter Henry | Alta | Recepciones 4 o más | 64% |
| NE @ MIA | Malik Willis | Media | TD de pase 1 o más | 61% |
| NE @ MIA | Drake Maye | Media | TD de pase 2 o más | 60% |
| NE @ MIA | Rhamondre Stevenson | Media | Acarreos 11 o más | 55% |
| PHI @ WAS | Makai Lemon | Alta | Recepciones 4 o más | 61% |
| PHI @ WAS | Stefon Diggs | Media | Recepciones 5 o más | 56% |
| PHI @ WAS | Dallas Goedert | Media | Yardas recibidas 45.5+ yds | 55% |

Sin favorito claro: LV @ NYJ, LAC @ LA, KC @ DEN, CHI @ SEA.

Descartados por matchup: Tony Pollard (Acarreos: matchup intermedio (#21 de 32, efecto rival -3%); su ventaja viene de su forma reciente, no del rival); Bijan Robinson (Acarreos: matchup difícil (#31 de 32, efecto rival -7%); su ventaja viene de compañeros ausentes, no del rival); Greg Dulcich (Recepciones: matchup intermedio (#13 de 32, efecto rival -1%); su ventaja viene de su forma reciente, no del rival); Ollie Gordon II (Acarreos: matchup difícil (#29 de 32, efecto rival -6%); su ventaja viene de compañeros ausentes, no del rival); A.J. Brown (Recepciones: matchup difícil (#25 de 32, efecto rival +1%); su ventaja viene de otros factores, no del rival); Saquon Barkley (Yardas por tierra: matchup intermedio (#15 de 32, efecto rival -1%); su ventaja viene de compañeros ausentes, no del rival); D'Andre Swift (Acarreos: matchup difícil (#25 de 32, efecto rival -4%); su ventaja viene de compañeros ausentes, no del rival).

## Cómo regenerar

```bash
python3 -I scripts/build_data.py && python3 -I scripts/build_players.py
python3 -I scripts/bt2_build.py && python3 -I scripts/bt3_build.py && python3 -I scripts/bt4_build.py && python3 -I scripts/bt5_build.py && python3 -I scripts/bt6_build.py && python3 -I scripts/bt7_build.py
python3 -I scripts/search.py 40000 && python3 -I scripts/search2.py
python3 -I scripts/build_props2.py && python3 -I scripts/build_final.py && python3 -I app/build.py
```

Los scripts esperan los datos crudos de nflverse (2026 y 2025) en /home/user/raw/nflverse.

Análisis de patrones, no garantía ni recomendación de apuesta. Solo mayores de 18 años.
