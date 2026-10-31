# Recheck final · NFL 2026 Semana 8

Corrida del sábado 31-oct-2026 (madrugada, hora Monterrey). Reemplaza a la primera corrida (props_data v1 en el historial de git).

## Qué se revisó y qué cambió

| Factor | Antes | Ahora |
|---|---|---|
| Rival | Lo que permite la defensa (crudo) ÷ lo que permitían los rivales previos del jugador (crudo), peso 0.3 | **Ajuste por ambos lados**: índice de cada defensa ajustado por la calidad de las ofensivas que enfrentó (modelo multiplicativo ofensiva × defensa por posición y estadística), y el jugador ajustado por esas mismas defensas ya corregidas. Peso 0.5 |
| Línea ofensiva | Solo texto | Titulares (5 OL con más snaps) que faltan hoy vs. los que faltaban en sus juegos previos: −4% por titular en estadísticas terrestres (en pase no hubo efecto medible) |
| Compañeros ausentes | No | Participación de targets y acarreos que queda libre (o que se pierde cuando un compañero regresa). Targets ×0.25, acarreos ×1.0 (elasticidades ajustadas con la prueba) |
| Lesiones | Práctica del jueves | Reporte final del viernes 30-oct (equipos y medios; ver fuentes en la app). CHI-SEA pendiente (sábado) |
| Jugadores | 188 con filtro de volumen | 269: todos con participación probable (≥20% de snaps en alguno de los últimos 3 juegos, o confirmados que regresan) |
| Línea sugerida | Redondeo de la proyección | **Línea justa**: la línea de .5 cuya probabilidad queda más cerca de 50% |
| Favoritos | 21 selecciones por reglas del Excel | Por partido: ajuste total ≥ +4% y ≥ 50% de superar su propio promedio; confianza Alta si ≥ 56%, sano, 4+ juegos y uso reciente normal |

## Prueba con resultados reales (semanas 4 a 8, solo datos previos a cada juego)

Error de predicción (Brier, menos es mejor) en semanas 7-8: sin ajustes 0.1998 · modelo anterior 0.1980 · **modelo nuevo 0.1959**.

Calibración (cuánto se cumplió cada etiqueta): Muy difícil 12%, Difícil 31%, Parejo 49%, Fácil 71%, Muy fácil 87%.

## Favoritos

| Partido | Jugador | Confianza | % de superar su promedio |
|---|---|---|---|
| BAL @ BUF | Lamar Jackson | Media | 54.8% |
| TEN @ CIN | Chase Brown | Media | 52.6% |
| MIN @ DET | Kyler Murray | Alta | 59.0% |
| IND @ JAX | Daniel Jones | Media | 54.9% |
| LV @ NYJ | Breece Hall | Media | 50.8% |
| ATL @ TB | Bijan Robinson | Alta | 58.2% |
| ATL @ TB | Baker Mayfield | Media | 54.8% |
| ATL @ TB | Chris Godwin Jr. | Media | 51.8% |
| NE @ MIA | Rhamondre Stevenson | Media | 53.5% |
| NE @ MIA | Ollie Gordon II | Media | 51.1% |
| NE @ MIA | Hunter Henry | Media | 50.1% |
| PHI @ WAS | Rachaad White | Alta | 69.8% |
| PHI @ WAS | Saquon Barkley | Media | 58.9% |
| PHI @ WAS | Dallas Goedert | Media | 53.8% |
| CHI @ SEA | D'Andre Swift | Media | 50.1% |

Sin favorito claro: ARI @ DAL, CLE @ PIT, LAC @ LA, KC @ DEN.

## Cómo regenerar

```bash
python3 -I scripts/build_data.py && python3 -I scripts/build_players.py
python3 -I scripts/bt2_build.py && python3 -I scripts/bt3_build.py && python3 -I scripts/bt3_final.py
python3 -I scripts/build_props2.py && python3 -I scripts/build_final.py
python3 -I app/build.py
```

Los scripts esperan los datos crudos de nflverse en /home/user/raw/nflverse y escriben en /home/user/data y /home/user/entrega_semana8.

Análisis de patrones, no garantía ni recomendación de apuesta. Solo mayores de 18 años.
