# Ensambla props_data.json v2 para la app: partidos (nombres completos, visita/local, bajas), jugadores, favoritos por partido,
# cambios frente al análisis anterior y metadatos del modelo. También genera casos_prueba.json.
import sys; sys.path.insert(0, '/home/user/scripts')
import json, math
from collections import defaultdict
from status_w8 import OUT, QUESTIONABLE, FUENTES, TEAM_NAME, OL_OUT_NOW, PENDING_TEAMS
O = '/home/user/data/'; E = '/home/user/entrega_semana8/'
RAW = json.load(open(O + 'props2_raw.json')); P2 = json.load(open(O + 'model10_params.json'))
V2 = json.load(open(O + 'props_data_v6.json'))
OLD = json.load(open(O + 'props_data_v1.json'))
players = RAW['players']
byp = {p['player_id']: p for p in players}
MAIN = {'QB': 'pass_yds', 'RB': 'rush_yds', 'WR': 'rec_yds', 'TE': 'rec_yds'}
TH = {'QB': 180, 'RB': 40, 'WR': 35, 'TE': 25}
sm = lambda p, k: next(s for s in p['stats'] if s['key'] == k)
pc = lambda v: f"{(v - 1) * 100:+.0f}%"

def main_stat(p):
    s = sm(p, MAIN[p['pos']])
    if p['pos'] == 'RB' and s['proyeccion'] < TH['RB'] and sm(p, 'rec')['proyeccion'] >= 3: return sm(p, 'rec')
    return s

SUF = {'Jr.', 'Sr.', 'II', 'III', 'IV', 'V'}
def surname(n):
    w = [x for x in n.split() if x not in SUF]; return w[-1] if w else n
def pcs(v):
    x = round((v - 1) * 100); return '0%' if x == 0 else f"{x:+d}%"
RUSHK = {'rush_yds', 'car'}
def reasons(p, s):
    r = []
    rv = s['rival_indice']; cal = s['calendario_indice']
    r.append(f"{p['rival']} permite {pcs(rv)} vs. el promedio en {s['etiqueta'].lower()} a {p['pos']} (#{s['rival_rank']} de 32 que más permite; 1 = la más blanda), ya ajustado por las ofensivas que enfrentó; "
             f"los rivales previos de {surname(p['jugador'])} permitían {pcs(cal)}. Efecto del rival: {pcs(s['f_rival'])}.")
    vals = [r_['valor'] for r_ in s['registro']]
    over = sum(1 for v in vals if v > s['linea_promedio'])
    r.append(f"Todos sus juegos de 2026: {', '.join(f'{v:.0f}' for v in vals)} (promedio {s['media_temporada']:.1f}); superó esa línea en {over} de {len(vals)}.")
    if abs(s['f_companeros'] - 1) >= 0.03:
        if s['key'] in RUSHK: aus = [a['jugador'] for a in p['factores']['ausentes'] if a['acarreos'] >= 0.15]
        else: aus = [a['jugador'] for a in p['factores']['ausentes'] if a['targets'] >= 0.08]
        quien = ', '.join(aus[:4]) if aus else 'regresos de compañeros'
        r.append(f"{'Más' if s['f_companeros'] > 1 else 'Menos'} volumen por compañeros ({quien}): {pcs(s['f_companeros'])}.")
    if abs(s['f_linea'] - 1) >= 0.02:
        fx = p['factores']; nota = fx['ol_nota'] or f"{p['equipo']} tiene completos a sus 5 titulares de la línea"
        r.append(f"Línea ofensiva: {nota} (en sus juegos previos faltaban {fx['ol_fuera_prom']:.1f} en promedio): {pcs(s['f_linea'])} en tierra.")
    return r

# ---------- mejor opción por jugador y favoritos por partido ----------
# Para cada jugador con participación decente (titular o rotación, 3+ juegos) se evalúan TODAS sus estadísticas:
# probabilidad de superar su propio promedio con el modelo final. "Lo más probable" = la de mayor probabilidad.
# Una estadística CALIFICA para favorito si: >= 55% de superar su promedio, ajuste total >= +4%, el matchup de ESA estadística
# no es Difícil (#22-32) y el rival no le resta (efecto rival >= 0%). Favorito = jugador con al menos una estadística que califica;
# "lo que más me convence" = la que califica con mayor probabilidad. Alta: esa estadística >= 60%, matchup Favorable (#1-10),
# sano, 4+ juegos y uso reciente normal. Todo con todos los juegos de 2026 (sin ponderar los recientes).
def decent(p):
    return p['stats'] and p['pj'] >= 3 and p['rol'] in ('Titular', 'Rotación') and main_stat(p)['proyeccion'] >= 0.5 * TH[p['pos']]
def stat_view(s):
    return dict(stat=s['key'], etiqueta=s['etiqueta'], prob=s['prob_superar_promedio'], linea=s['linea_promedio'], promedio=s['media_temporada'],
                proyeccion=s['proyeccion'], factor=s['factor_total'], lectura=s['lectura'], rival_rank=s['rival_rank'], juegos=[r_['valor'] for r_ in s['registro']])
MINS = {'rec_yds': 30, 'rec': 3, 'rush_yds': 40, 'car': 10, 'pass_yds': 150, 'cmp': 12, 'pass_td': 0.5, 'td': 0.5}
MINS_RB = {'rec_yds': 15, 'rec': 2}   # en RB las recepciones son secundarias: mínimos propios
for _p in players:
    for _s in _p['stats']: _s['pos'] = _p['pos']
def meaningful(s):
    m = MINS_RB.get(s['key'], MINS[s['key']]) if s.get('pos') == 'RB' else MINS[s['key']]
    return s['media_temporada'] >= m
def qualifies(s):
    return meaningful(s) and s['prob_superar_promedio'] >= 0.55 and s['factor_total'] >= 1.04 and s['lectura'] != 'Difícil' and s['f_rival'] >= 0.995
fav = defaultdict(list); near = {}; blocked = defaultdict(list)
for p in players:
    p['mejor'] = None; p['ranking'] = []
    if not decent(p): continue
    ss = [s for s in p['stats'] if s['dist'].get('dist') != 'zero' and meaningful(s)]
    rk = sorted(ss, key=lambda s: -s['prob_superar_promedio'])
    p['ranking'] = [stat_view(s) for s in rk]
    p['mejor'] = stat_view(rk[0]) if rk else None
    q = [s for s in rk if qualifies(s)] if main_stat(p)['proyeccion'] >= TH[p['pos']] or meaningful(main_stat(p)) else []
    if not q:
        hot = [s for s in rk if s['prob_superar_promedio'] >= 0.55 and s['factor_total'] >= 1.04 and meaningful(s)]
        if hot and main_stat(p)['proyeccion'] >= TH[p['pos']]:
            s = hot[0]
            blocked[p['partido']].append(dict(stat_view(s), player_id=p['player_id'], jugador=p['jugador'], pos=p['pos'], equipo=p['equipo'],
                motivo=f"{s['etiqueta']}: matchup {s['lectura'].lower()} (#{s['rival_rank']} de 32 que más permite, efecto rival {pcs(s['f_rival'])}); su ventaja viene de "
                       + ('compañeros ausentes' if s['f_companeros'] > 1.03 else 'otros factores') + ', no del rival'))
        elif rk and rk[0]['lectura'] != 'Difícil' and main_stat(p)['proyeccion'] >= TH[p['pos']]:
            cand = dict(stat_view(rk[0]), player_id=p['player_id'], jugador=p['jugador'], pos=p['pos'], equipo=p['equipo'])
            if near.get(p['partido']) is None or cand['prob'] > near[p['partido']]['prob']: near[p['partido']] = cand
        continue
    s = q[0]
    missed_last = (not p['jugo_ultimo']) or p['regresa'] or p['snaps_ult3'] < 40
    alta = s['prob_superar_promedio'] >= 0.60 and s['lectura'] == 'Favorable' and p['estado'] == 'OK' and p['pj'] >= 4 and not missed_last
    riesgos = []
    if p['estado'] != 'OK': riesgos.append(p['estado_lesion'])
    if missed_last: riesgos.append('Regresa de lesión: su volumen puede venir limitado.' if (not p['jugo_ultimo'] or p['regresa'])
                                   else f"Uso reciente bajo ({p['snaps_ult3']}% de snaps máx. en los últimos 3 juegos).")
    if p['pj'] < 4: riesgos.append('Muestra corta (menos de 4 juegos).')
    if s['lectura'] == 'Intermedio': riesgos.append(f"Matchup intermedio en {s['etiqueta'].lower()} (#{s['rival_rank']} de 32 que más permite), no favorable.")
    cand = dict(stat_view(s), player_id=p['player_id'], jugador=p['jugador'], pos=p['pos'], equipo=p['equipo'], estado=p['estado'],
                confianza='Alta' if alta else 'Media', por_que=reasons(p, s), riesgo=' '.join(riesgos),
                tambien=[stat_view(x) for x in q[1:]])
    fav[p['partido']].append(cand)
for g in fav: fav[g].sort(key=lambda c: (c['confianza'] != 'Alta', -c['prob']))
# aviso de backfield compartido: dos RB favoritos del mismo equipo se reparten la carga
for g, lst in fav.items():
    for c in lst:
        mates = [o['jugador'] for o in lst if o is not c and o['equipo'] == c['equipo'] and o['pos'] == 'RB' == c['pos']]
        if mates: c['riesgo'] = (c['riesgo'] + ' ' if c['riesgo'] else '') + f"Comparte el backfield con {', '.join(mates)} (también favorito): si uno acapara la carga, el otro baja."


# ---------- partidos ----------
def def_summary(team, opp):
    """dónde es blanda/dura la defensa de `team` (índices ajustados por las ofensivas enfrentadas)."""
    soft, hard = [], []
    for pos in ['QB', 'RB', 'WR', 'TE']:
        ps = [p for p in players if p['rival'] == opp and False]
    return soft, hard
partidos = []
for g in OLD['partidos']:
    v, l = g['visitante'], g['local']
    outs = defaultdict(list)
    for n, (t, why) in OUT.items():
        if t in (v, l): outs[t].append(f"{n} ({why})")
    # índices de defensa por posición desde cualquier jugador del rival
    def idx(defteam):
        out = {}
        for p in players:
            if p['rival'] == defteam and p['stats']:
                s = sm(p, MAIN[p['pos']]); out[p['pos']] = (s['rival_indice'], s['rival_rank'])
        return out
    dv, dl = idx(v), idx(l)
    def lect(rk): return 'Favorable' if rk <= 10 else ('Intermedio' if rk <= 21 else 'Difícil')
    mapa = [dict(ataca=atk, defiende=dfn, celdas=[dict(pos=pos, rank=d[pos][1], indice=d[pos][0], lectura=lect(d[pos][1])) for pos in ['QB', 'RB', 'WR', 'TE'] if pos in d])
            for atk, dfn, d in [(v, l, dl), (l, v, dv)]]
    def txt(defteam, d):
        soft = [f"{pos} (#{rk}, {pc(ix)})" for pos, (ix, rk) in sorted(d.items(), key=lambda kv: kv[1][1]) if rk <= 8]
        hard = [f"{pos} (#{rk}, {pc(ix)})" for pos, (ix, rk) in sorted(d.items(), key=lambda kv: -kv[1][1]) if rk >= 25]
        s = f"La defensa de {defteam} "
        s += ("es blanda contra " + ", ".join(soft)) if soft else "no es especialmente blanda contra ninguna posición"
        s += ("; es dura contra " + ", ".join(hard) + "." if hard else ".")
        return s
    partidos.append(dict(partido=g['partido'], visitante=v, local=l, nombre_visitante=TEAM_NAME[v], nombre_local=TEAM_NAME[l],
        fecha_hora_monterrey=g['fecha_hora_monterrey'], hora_et=g['hora_et'], estadio=g['estadio'],
        record_visitante=g['record_visitante'], record_local=g['record_local'],
        defensas=[txt(l, dl), txt(v, dv)],
        linea_ofensiva={v: OL_OUT_NOW[v][1], l: OL_OUT_NOW[l][1]},
        no_juegan={v: outs[v], l: outs[l]}, reporte_pendiente=(v in PENDING_TEAMS or l in PENDING_TEAMS),
        favoritos=fav.get(g['partido'], []), mas_cercano=(None if fav.get(g['partido']) else near.get(g['partido'])),
        descartados=blocked.get(g['partido'], []), mapa=mapa))

# ---------- cambios frente al análisis anterior (21 selecciones) ----------
favids = {c['player_id']: c for g in fav.values() for c in g}
cambios = []
for s in OLD['selecciones']:
    p = byp.get(s['player_id'])
    if p is None:
        cambios.append(dict(jugador=s['jugador'], antes=s['confianza'], ahora='Fuera de la lista', motivo='No está en el plantel probable de la semana 8 (lesión o sin rol).')); continue
    m = main_stat(p) if p['stats'] else None
    if s['player_id'] in favids:
        c = favids[s['player_id']]
        cambios.append(dict(jugador=s['jugador'], antes=s['confianza'], ahora='Favorito ' + c['confianza'],
            motivo=f"Se mantiene: {c['prob'] * 100:.1f}% de superar su promedio ({c['etiqueta'].lower()}), ajuste total {pcs(c['factor'])}."))
    else:
        why = []
        if m:
            if m['f_rival'] < 1.04: why.append(f"al ajustar por ambos lados, el rival solo mueve {pcs(m['f_rival'])}")
            if m['f_companeros'] < 0.97: why.append(f"compañeros que regresan le quitan volumen ({pcs(m['f_companeros'])})")
            if m['prob_superar_promedio'] < 0.5: why.append(f"{m['prob_superar_promedio'] * 100:.1f}% de superar su promedio")
            if m['f_rival'] >= 1.04 and m['prob_superar_promedio'] < 0.5 and m['dist'].get('dist') == 'gamma' and m['dist']['shape'] < 2:
                why.append('su producción es muy irregular: tiene juegos muy altos que suben su promedio, pero en un juego típico queda por debajo')
        if p['estado'] != 'OK': why.append(p['estado_lesion'])
        cambios.append(dict(jugador=s['jugador'], antes=s['confianza'], ahora='Ya no es favorito', motivo='; '.join(why) or 'No cumple las reglas de favorito.'))

prev = {c['player_id']: c for g in V2['partidos'] for c in g['favoritos']}
cambios_v2 = []
for pid, c in prev.items():
    now = favids.get(pid); p = byp.get(pid); m = main_stat(p) if p and p['stats'] else None
    if now: cambios_v2.append(dict(jugador=c['jugador'], antes=c['confianza'], ahora='Favorito ' + now['confianza'], motivo=(now['riesgo'] or 'Se mantiene.')))
    else:
        why = []
        if m and (m['lectura'] == 'Difícil' or m['f_rival'] < 0.995): why.append(f"matchup {m['lectura'].lower()} (#{m['rival_rank']} de 32 que más permite, efecto rival {pcs(m['f_rival'])}): su ventaja venía de los compañeros ausentes, no del rival")
        if m and m['prob_superar_promedio'] < 0.5: why.append(f"baja a {m['prob_superar_promedio'] * 100:.1f}% de superar su promedio")
        if m and m['factor_total'] < 1.04: why.append(f"ajuste total {pcs(m['factor_total'])} (< +4%)")
        cambios_v2.append(dict(jugador=c['jugador'], antes=c['confianza'], ahora='Ya no es favorito', motivo='; '.join(why) or 'No cumple las reglas.'))
for pid, c in favids.items():
    if pid not in prev: cambios_v2.append(dict(jugador=c['jugador'], antes='—', ahora='Favorito ' + c['confianza'], motivo='Entra con el modelo final (todos los juegos): ' + f"{c['prob'] * 100:.1f}% de superar su promedio."))
meta = dict(OLD['metadatos'])
meta.update(tipo_corrida='RECHECK FINAL', datos_al='lesiones al vie 30-oct · corrida sáb 31-oct',
    recalibracion=P2['cal'], peso_w_probabilidad=P2['w_pass'],
    modelo=dict(w_rival=dict(tierra=P2['w_rush'], pase=P2['w_pass'], td=P2['w_td']), referencia_2025=dict(rho=P2['prior_rho'], juegos=P2['prior_k']),
                linea_ofensiva_por_titular=P2['bru'], companeros_targets=P2['gt'], companeros_acarreos=P2['gc'],
                forma_reciente=dict(vida_media_juegos=P2['rec_h'], mezcla=P2['rec_a']), busqueda=P2['busqueda'],
                prueba=dict(sin_ajuste=P2['test']['sin_ajuste'], anterior=P2['test']['anterior_v4'], v2=P2['test']['final'],
                            acierto_lado=P2['test']['acierto_lado'], acierto_lado_confiado=P2['test']['acierto_lado_confiado']),
                calibracion={k: round(v['acierto'] * 100) for k, v in P2['calib'].items()}),
    fuentes_lesiones=[dict(nombre=n, url=u) for n, u in FUENTES],
    avisos=['Análisis de patrones, no garantía ni recomendación de apuesta. Solo mayores de 18 años.',
            'Lesiones: reporte final del viernes 30-oct (equipos y medios). CHI-SEA juega el lunes: su reporte final sale el sábado.',
            'Fuente de estadísticas: nflverse (datos oficiales de juego de la NFL). Sin cuotas ni líneas de casas de apuestas.'])
meta.pop('formula', None); meta.pop('peso_w', None)
# ---------- Top 5 del modelo: 2 de confianza alta + complementos más probables y confiables ----------
allfav = [dict(c, partido=g['partido']) for g in partidos for c in g['favoritos']]
alta5 = sorted([c for c in allfav if c['confianza'] == 'Alta'], key=lambda c: -c['prob'])
media_ok = sorted([c for c in allfav if c['confianza'] != 'Alta' and c['estado'] == 'OK' and byp[c['player_id']]['pj'] >= 4], key=lambda c: -c['prob'])
top = alta5[:5] + media_ok[:max(0, 5 - len(alta5[:5]))]
cut = top[-1]['prob'] if top else 1
excl = [dict(jugador=c['jugador'], partido=c['partido'], prob=c['prob'], motivo=('muestra corta (' + str(byp[c['player_id']]['pj']) + ' juegos)' if byp[c['player_id']]['pj'] < 4 else c['riesgo'] or 'riesgo de lesión'))
        for c in allfav if c not in top and c['confianza'] != 'Alta' and c['prob'] > cut and (c['estado'] != 'OK' or byp[c['player_id']]['pj'] < 4)]
pall = 1.0
for c in top: pall *= c['prob']
top5 = dict(picks=[dict(rank=i + 1, rol=('Alta' if c['confianza'] == 'Alta' else 'Complemento'), player_id=c['player_id'], jugador=c['jugador'], pos=c['pos'], equipo=c['equipo'],
                       partido=c['partido'], stat=c['stat'], etiqueta=c['etiqueta'], linea=c['linea'], prob=c['prob'], lectura=c['lectura'], rival_rank=c['rival_rank'],
                       por_que=(c['por_que'][0] if c['por_que'] else ''), riesgo=c['riesgo']) for i, c in enumerate(top)],
            prob_todos=pall, esperados=sum(c['prob'] for c in top), excluidos=excl,
            nota='Son los 5 con mayor probabilidad según el modelo, no apuestas seguras: cada uno se cumple aprox. 6 a 7 de cada 10 veces y los 5 juntos mucho menos.')
# ---------- Parlays del modelo ----------
# Piernas posibles: jugadores con participación decente, sanos (sin designación), 4+ juegos, estadística con volumen mínimo,
# matchup no Difícil en esa estadística y >= 55% de superar su promedio. Reglas para no juntar piernas que se estorban:
# una pierna por jugador; no dos RB del mismo equipo; no un QB con un receptor de su mismo equipo (van juntos y el % real se infla).
# Probabilidad conjunta = producto (aprox., asumiendo independencia).
def legs_of(game, flexible=False):
    out = []
    for pl in players:
        if pl['partido'] != game or not pl['stats'] or not decent(pl): continue
        if flexible:
            if pl['estado'] == 'Duda' or pl['pj'] < 3: continue
        elif pl['estado'] != 'OK' or pl['pj'] < 4: continue
        for s in pl['stats']:
            if s['dist'].get('dist') == 'zero' or not meaningful(s) or s['lectura'] == 'Difícil' or s['prob_superar_promedio'] < (0.50 if flexible else 0.55): continue
            out.append(dict(player_id=pl['player_id'], jugador=pl['jugador'], pos=pl['pos'], equipo=pl['equipo'], partido=game, stat=s['key'], etiqueta=s['etiqueta'],
                            linea=s['linea_promedio'], prob=s['prob_superar_promedio'], lectura=s['lectura'], rival_rank=s['rival_rank'],
                            nota=('' if (pl['estado'] == 'OK' and pl['pj'] >= 4) else (pl['estado_lesion'] if pl['estado'] != 'OK' else 'muestra corta'))))
    return out
def compatible(a, b):
    if a['player_id'] == b['player_id']: return False
    if a['equipo'] == b['equipo'] and a['pos'] == 'RB' and b['pos'] == 'RB': return False
    if a['equipo'] == b['equipo'] and 'QB' in (a['pos'], b['pos']) and a['pos'] != b['pos']: return False
    return True
def best_combo(pool, n):
    pool = sorted(pool, key=lambda l: -l['prob'])[:14]
    best = None
    from itertools import combinations
    for combo in combinations(pool, n):
        if all(compatible(x, y) for x, y in combinations(combo, 2)):
            pr = 1.0
            for l in combo: pr *= l['prob']
            if best is None or pr > best[0]: best = (pr, list(combo))
    return best
UMBRAL = {2: 0.40, 3: 0.27}   # cumple la expectativa: 2 piernas >= 40%; 3 piernas >= 27%
parlays = []
for g in partidos:
    b = best_combo(legs_of(g['partido']), 2); flex = False
    if not b: b = best_combo(legs_of(g['partido'], True), 2); flex = True
    if b: parlays.append(dict(tipo='Por partido', partido=g['partido'], piernas=b[1], prob=b[0], cuota_justa=1 / b[0], cumple=(b[0] >= UMBRAL[2] and not flex), flexible=flex))
    else: parlays.append(dict(tipo='Por partido', partido=g['partido'], piernas=[], prob=None, cuota_justa=None, cumple=False, flexible=True))
    g['parlay'] = parlays[-1]
# generales: mejores piernas de partidos distintos (una por partido)
best_by_game = {}
for g in partidos:
    for l in legs_of(g['partido']):
        if g['partido'] not in best_by_game or l['prob'] > best_by_game[g['partido']]['prob']: best_by_game[g['partido']] = l
cross = sorted(best_by_game.values(), key=lambda l: -l['prob'])
gen = []
for n in (2, 3):
    if len(cross) >= n:
        pr = 1.0
        for l in cross[:n]: pr *= l['prob']
        gen.append(dict(tipo=f'General de {n}', partido='Varios partidos', piernas=cross[:n], prob=pr, cuota_justa=1 / pr, cumple=pr >= UMBRAL[n]))
cands = [x for x in parlays if x['piernas']] + gen
ok = sorted([x for x in cands if x['cumple']], key=lambda x: -x['prob'])
mejor = max(cands, key=lambda x: x['prob']) if cands else None
eleccion = dict(cumplen=ok, ninguno=(len(ok) == 0), me_quedaria=(None if ok else mejor),
                regla='Cumple la expectativa si el parlay de 2 tiene 40% o más (o el de 3, 27% o más) según el modelo.')
parlay_info = dict(por_partido=parlays, generales=gen, eleccion=eleccion,
                   nota='Un parlay no es seguro: todas las piernas tienen que cumplirse. La probabilidad conjunta asume que las piernas son independientes; dentro de un mismo partido puede variar. La cuota justa es 1 / probabilidad: si la casa paga menos que eso, el modelo no le ve valor.')
out = dict(metadatos=meta, partidos=partidos, jugadores=players, cambios=cambios, cambios_v2=cambios_v2, top5=top5, parlays=parlay_info)
json.dump(out, open(E + 'props_data.json', 'w'), ensure_ascii=False, separators=(',', ':'))
json.dump(RAW['tests'], open(E + 'casos_prueba.json', 'w'), ensure_ascii=False, indent=0)
nf = sum(len(v) for v in fav.values())
print('partidos', len(partidos), 'jugadores', len(players), 'favoritos', nf, 'casos', len(RAW['tests']))
for g in partidos:
    print(g['partido'], [(c['jugador'], c['confianza'], round(c['prob'], 2)) for c in g['favoritos']] or ('cercano', g['mas_cercano']['jugador'], round(g['mas_cercano']['prob'], 2)))
for c in cambios_v2: print(' ', c['jugador'], c['antes'], '->', c['ahora'], '|', c['motivo'][:160])
for g in partidos:
    for x in g['descartados']: print('  DESCARTADO', g['partido'], x['jugador'], x['motivo'])
