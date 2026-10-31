import json
J=json.load(open('/home/user/entrega_semana8/data.json'))
M=J['metadatos']; out=[open('/home/user/scripts/prompt_body.md').read()]
f1=lambda x: f"{x:.1f}"; pc=lambda x: f"{x*100:+.1f}%"
out.append("## APÉNDICE A · Resumen ejecutivo del análisis (contexto integrado)\n")
out.append(f"- Corte: {M['datos_al']} · {M['tipo_corrida']} · w = {M['peso_w']} · zona: {M['zona_horaria']}.")
out.append(f"- Promedio de la liga (yds por juego de defensa): QB {f1(M['promedio_liga_yds_por_juego']['QB'])} · RB {f1(M['promedio_liga_yds_por_juego']['RB'])} · WR {f1(M['promedio_liga_yds_por_juego']['WR'])} · TE {f1(M['promedio_liga_yds_por_juego']['TE'])}.")
out.append(f"- Selecciones: {J['conteos']['alta']} Alta, {J['conteos']['media']} Media, {J['conteos']['total']} en total, sobre {len(J['evaluados'])} jugadores evaluados de los 26 equipos que juegan en S8.")
out.append("- Patrón principal: los TE contra defensas débiles ante su posición (DET, MIA, WAS, DEN) dan los ajustes más altos; los receptores de IND contra JAX (la defensa que más permite a WR); por tierra, LV es la defensa que más permite a RB.")
out.append("- Lados sin selección: TEN, DET, JAX, LV, CLE, ATL, LAC, DEN, MIA y CHI (CHI enfrenta a SEA, la defensa que menos permite a QB, WR y TE).")
out.append("- Pendiente para el recheck (domingo 10:40, Monterrey): inactivos oficiales; estatus de Lamar Jackson, Kelce, Michael Wilson, Breece Hall, DeVonta Smith/Wicks, Egbuka y la DL de NYJ; vigilar a Tuten, Nacua y Rachaad White.")
out.append("- Avisos de la corrida:")
for a in M['avisos']: out.append(f"  - {a}")
out.append("\n## APÉNDICE B · Las 21 selecciones (extracto exacto de `selecciones[]`)\n")
out.append("| # | Hora MTY | Partido | Jugador | Eq | Rival | Pos | Categorías | Conf. | Prod/j | Rival permite | Rank | Lectura | Dureza | Liga | Proy/j | Cambio | PJ | Regla | Tier línea |")
out.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for i,s in enumerate(J['selecciones'],1):
    out.append(f"| {i} | {s['hora_monterrey']} | {s['partido']} | {s['jugador']} | {s['equipo']} | {s['rival']} | {s['pos']} | {s['categorias']} | {s['confianza']} | {f1(s['produccion_pj'])} | {f1(s['rival_permite'])} | {s['rank']} | {s['lectura']} | {f1(s['dureza_calendario'])} | {f1(s['promedio_liga'])} | {f1(s['proyeccion'])} | {pc(s['cambio'])} | {s['pj']} | {s['regla_inclusion']} | {s['tier_linea']} |")
out.append("\n### B.2 Textos de cada selección\n")
for i,s in enumerate(J['selecciones'],1):
    c=s['por_que_confianza']
    out.append(f"**{i}. {s['jugador']} ({s['equipo']} vs {s['rival']}) · {s['confianza']}**")
    out.append(f"- Por qué (dato): {s['por_que']}")
    out.append(f"- (a) Qué la sube: {c['a_sube']}")
    out.append(f"- (b) Qué la frena: {c['b_frena']}")
    out.append(f"- (c) Regla aplicada: {c['c_regla']}")
    out.append(f"- Riesgo: {s['riesgo'].split(' Contexto propio:')[0]}")
    out.append(f"- Estado de lesión: {s['estado_lesion']}")
    out.append(f"- Pts/j que permite el rival: {f1(s['pts_pj_permitidos_rival'])} · Prob. de victoria: {s['prob_victoria']}\n")
out.append("## APÉNDICE C · Partidos (extracto de `partidos[]`)\n")
for p in J['partidos']:
    out.append(f"**{p['partido']}** · {p['fecha_hora_monterrey']} (Monterrey) · {p['estadio']} · récords {p['visitante']} {p['record_visitante']} / {p['local']} {p['record_local']} · Prob. victoria: {p['prob_victoria']}")
    out.append(f"- Decisión: {p['decision']}\n- Por qué: {p['por_que']}\n- Qué lo puede romper: {p['que_lo_puede_romper']}\n- Conclusión: {p['conclusion']}\n- Selecciones: {', '.join(p['selecciones']) or '—'}\n")
out.append("## APÉNDICE D · Defensas (yds/j permitidas por posición y rank; 1 = la que más permite)\n")
out.append("| Def | PJ | QB yds/j (rk) | RB yds/j (rk) | WR yds/j (rk) | TE yds/j (rk) | Pts/j (rk) | TD/j QB·RB·WR·TE (rk) |")
out.append("|---|---|---|---|---|---|---|---|")
for t,d in sorted(J['defensas'].items()):
    td=' · '.join(f"{d[p+'_td_pj']:.2f} ({d[p+'_td_rank']})" for p in ['QB','RB','WR','TE'])
    out.append(f"| {t} | {d['pj']} | {f1(d['QB_yds_pj'])} ({d['QB_rank']}) | {f1(d['RB_yds_pj'])} ({d['RB_rank']}) | {f1(d['WR_yds_pj'])} ({d['WR_rank']}) | {f1(d['TE_yds_pj'])} ({d['TE_rank']}) | {f1(d['pts_permitidos_pj'])} ({d['rank_pts']}) | {td} |")
out.append("\n## APÉNDICE E · Equipos que juegan en S8 (extracto de `equipos{}` y `calendario_jugado{}`)\n")
out.append("| Eq | Récord | Dif pts/j | QB titular | Tier línea (proxy) | Dureza vs liga QB · RB · WR · TE |")
out.append("|---|---|---|---|---|---|")
for t,e in sorted(J['equipos'].items()):
    dz=J['calendario_jugado'][t]['dureza_vs_liga']
    out.append(f"| {t} | {e['record']} | {e['dif_pts_pj']:+.1f} | {e['qb']} | {e['tier']} | {' · '.join(pc(dz[p]) for p in ['QB','RB','WR','TE'])} |")
out.append("\n## APÉNDICE F · Los 188 evaluados (CSV compacto; cambio en %)\n")
out.append("```csv\njugador,pos,equipo,rival,pj,prod_pj,rival_permite,rank,lectura,dureza,proyeccion,cambio_pct,tgt_pj,rec_pj,car_pj,R1,R2,R3,R4,veredicto")
for e in J['evaluados']:
    b=lambda k: '1' if e[k] else '0'
    out.append(f"{e['jugador']},{e['pos']},{e['equipo']},{e['rival']},{e['pj']},{f1(e['produccion_pj'])},{f1(e['rival_permite'])},{e['rank']},{e['lectura']},{f1(e['dureza_calendario'])},{f1(e['proyeccion'])},{e['cambio']*100:+.1f},{e['tgt_pg']:.1f},{e['rec_pg']:.1f},{e['car_pg']:.1f},{b('R1')},{b('R2')},{b('R3')},{b('R4')},{e['veredicto']}")
out.append("```\n\n_Fin del prompt. Recuerda: análisis de patrones, no garantía ni recomendación de apuesta. Solo mayores de 18 años._\n")
open('/home/user/entrega_semana8/PROMPT_Claude_Design.md','w').write('\n'.join(out))
print('ok')
