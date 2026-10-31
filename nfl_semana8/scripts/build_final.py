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
# ---------- Parlays del modelo (variados: posiciones y estadísticas distintas) ----------
# Piernas sólidas: jugador con participación decente, sano, 4+ juegos, estadística con volumen mínimo, matchup no Difícil y
# probabilidad de superar su promedio >= 55% (QB) o >= 53% (RB, WR, TE; sus estadísticas varían más). Reglas para no juntar
# piernas que se estorban: una pierna por jugador; no dos RB del mismo equipo; no QB con su propio receptor.
# Reglas de variedad: como máximo 1 de cada 3 piernas puede ser de QB y 1 de cada 3 de TD; no más de 2 piernas de la misma
# estadística; en parlays de 3+ piernas, al menos un WR o TE. Probabilidad conjunta = producto (asume independencia).
from itertools import combinations as _comb
import math as _m
TDK = {'td', 'pass_td'}
MINP = {'QB': 0.55, 'RB': 0.53, 'WR': 0.53, 'TE': 0.53}
def legs_of(game, flexible=False):
    out = []
    for pl in players:
        if (game and pl['partido'] != game) or not pl['stats'] or not decent(pl): continue
        if flexible:
            if pl['estado'] == 'Duda' or pl['pj'] < 3: continue
        elif pl['estado'] != 'OK' or pl['pj'] < 4: continue
        for s in pl['stats']:
            if s['dist'].get('dist') == 'zero' or not meaningful(s) or s['lectura'] == 'Difícil': continue
            if s['prob_superar_promedio'] < (0.50 if flexible else MINP[pl['pos']]): continue
            out.append(dict(player_id=pl['player_id'], jugador=pl['jugador'], pos=pl['pos'], equipo=pl['equipo'], partido=pl['partido'], stat=s['key'], etiqueta=s['etiqueta'],
                            linea=s['linea_promedio'], prob=s['prob_superar_promedio'], lectura=s['lectura'], rival_rank=s['rival_rank'],
                            nota=('' if (pl['estado'] == 'OK' and pl['pj'] >= 4) else (pl['estado_lesion'] if pl['estado'] != 'OK' else 'muestra corta'))))
    return out
def compatible(a, b):
    if a['player_id'] == b['player_id']: return False
    if a['equipo'] == b['equipo'] and a['pos'] == 'RB' and b['pos'] == 'RB': return False
    if a['equipo'] == b['equipo'] and 'QB' in (a['pos'], b['pos']) and a['pos'] != b['pos']: return False
    return True
def varied(legs):
    n = len(legs); cap = max(1, _m.ceil(n / 3))
    if sum(1 for l in legs if l['pos'] == 'QB') > cap or sum(1 for l in legs if l['stat'] in TDK) > cap: return False
    cnt = {}
    for l in legs: cnt[l['stat']] = cnt.get(l['stat'], 0) + 1
    if max(cnt.values()) > 2: return False
    if n >= 3 and not any(l['pos'] in ('WR', 'TE') for l in legs): return False
    return True
LAMBDA = 0.18   # cada repetición (misma posición, misma estadística, o TD extra) debe "pagarse" con ~20% más de probabilidad
def repeats(legs, extra=None):
    pc, sc = {}, {}
    for l in legs: pc[l['pos']] = pc.get(l['pos'], 0) + 1; sc[l['stat']] = sc.get(l['stat'], 0) + 1
    td = sum(1 for l in legs if l['stat'] in TDK)
    r = sum(max(0, c - 1) for c in pc.values()) + sum(max(0, c - 1) for c in sc.values()) + max(0, td - 1)
    if extra:   # repetir jugadores o estadísticas ya usados en otras opciones
        r += 0.5 * sum(1 for l in legs if (l['player_id'], l['stat']) in extra)
    return r
def score(legs, extra=None):
    return sum(_m.log(l['prob']) for l in legs) - LAMBDA * repeats(legs, extra)
def prod(legs):
    pr = 1.0
    for l in legs: pr *= l['prob']
    return pr
def best_combo(pool, n, need_var=True, distinct_games=False, extra=None):
    pool = sorted(pool, key=lambda l: -l['prob'])[:24]
    best = None
    for combo in _comb(pool, n):
        if distinct_games and len({l['partido'] for l in combo}) < n: continue
        if not all(compatible(x, y) for x, y in _comb(combo, 2)): continue
        sc = score(combo, extra) if need_var else sum(_m.log(l['prob']) for l in combo)
        if best is None or sc > best[2]: best = (prod(combo), list(combo), sc)
    return best[:2] if best else None
def mk(tipo, piernas, etiqueta=None, **kw):
    pr = prod(piernas)
    return dict(tipo=tipo, etiqueta=etiqueta, partido=kw.get('partido', 'Varios partidos'), piernas=piernas, prob=pr, cuota_justa=1 / pr,
                cumple=kw.get('cumple', False), flexible=kw.get('flexible', False), moderado=kw.get('moderado', False))
UMBRAL = {2: 0.40, 3: 0.27}
parlays = []
for g in partidos:
    strict = legs_of(g['partido']); b = best_combo(strict, 2); flex = False; note = None
    if not b: b = best_combo(legs_of(g['partido'], True), 2); flex = True
    if b: x = mk('Por partido', b[1], note, partido=g['partido'], cumple=(b[0] >= UMBRAL[2] and not flex), flexible=flex)
    else: x = dict(tipo='Por partido', partido=g['partido'], piernas=[], prob=None, cuota_justa=None, cumple=False, flexible=True)
    parlays.append(x); g['parlay'] = x
pool_all = sorted(legs_of(None), key=lambda l: -l['prob'])
gen = []
for n in (2, 3):
    b = best_combo(pool_all, n, distinct_games=True)
    if b: gen.append(mk(f'General de {n}', b[1], None, cumple=b[0] >= UMBRAL[n]))
seguros = []
for n in (2, 3):
    b = best_combo(pool_all, n, need_var=False, distinct_games=True)
    if b: seguros.append(dict(mk(f'Más seguro de {n}', b[1], 'Los más seguros · sin regla de variedad', cumple=b[0] >= UMBRAL[n]), seguro=True))
for x in gen: x['etiqueta'] = 'Variado · posiciones mezcladas' + (' · cumple la expectativa' if x['cumple'] else '')
cands = [x for x in parlays if x['piernas']] + gen + seguros
ok = sorted([x for x in cands if x['cumple']], key=lambda x: -x['prob'])
mejor = max(cands, key=lambda x: x['prob']) if cands else None
eleccion = dict(cumplen=ok, ninguno=(len(ok) == 0), me_quedaria=(None if ok else mejor),
                regla='Cumple la expectativa si el parlay de 2 tiene 40% o más (o el de 3, 27% o más) según el modelo. "Los más seguros" buscan solo la mayor probabilidad; los "variados" mezclan posiciones y estadísticas y por eso suelen tener un poco menos.')
# ---------- Más opciones: riesgo moderado, con preferencia de variedad (dentro de cada parlay y entre opciones) ----------
BANDA = {2: (0.28, 0.40), 3: (0.18, 0.27)}
top = pool_all[:30]
moderados = []; usados = set(); uso = {}; firmas = {}
for n, k in ((2, 5), (3, 4)):
    cands_n = []
    for combo in _comb(top, n):
        if len({l['partido'] for l in combo}) < n or not all(compatible(x, y) for x, y in _comb(combo, 2)): continue
        pr = prod(combo); lo, hi = BANDA[n]
        if lo <= pr < hi: cands_n.append(combo)
    for _ in range(k):
        best = None
        for combo in cands_n:
            if any(uso.get(l['player_id'], 0) >= 2 for l in combo): continue
            keys = {(l['player_id'], l['stat']) for l in combo}
            if any(keys == {(l['player_id'], l['stat']) for l in m['piernas']} for m in moderados): continue
            firma = tuple(sorted(l['pos'] for l in combo))
            sc = score(combo, usados) - 0.15 * firmas.get(firma, 0)
            if best is None or sc > best[0]: best = (sc, combo)
        if not best: break
        combo = best[1]
        for l in combo: uso[l['player_id']] = uso.get(l['player_id'], 0) + 1; usados.add((l['player_id'], l['stat']))
        firma = tuple(sorted(l['pos'] for l in combo)); firmas[firma] = firmas.get(firma, 0) + 1
        cnt = {}
        for l in combo: cnt[l['pos']] = cnt.get(l['pos'], 0) + 1
        posset = [(f"{cnt[q]} {q}" if cnt[q] > 1 else q) for q in ['QB', 'RB', 'WR', 'TE'] if q in cnt]
        moderados.append(mk(f'Moderado de {n}', list(combo), 'Riesgo moderado · ' + ' + '.join(posset), moderado=True))
moderados.sort(key=lambda m: (len(m['piernas']), -m['prob']))
# ---------- Parlays largos (4 a 6 piernas) con variedad ----------
def greedy_long(n, no_td=False):
    cand = [l for l in pool_all if not (no_td and l['stat'] in TDK)]
    chosen = []
    while len(chosen) < n:
        best = None
        for l in cand:
            if any(c['partido'] == l['partido'] for c in chosen) or not all(compatible(c, l) for c in chosen): continue
            sc = score(chosen + [l])
            if best is None or sc > best[0]: best = (sc, l)
        if not best: return None
        chosen.append(best[1])
    return chosen
largos = []
for no_td in (False, True):
    for n in (4, 5, 6):
        legs = greedy_long(n, no_td)
        if legs: largos.append(dict(mk(f'Largo de {n}', legs, f"{n} piernas · {'sin TD' if no_td else 'con variedad'}", moderado=True), largo=True))
# ---------- Puntos totales del partido (centro = total de la casa; variación real de 2026) ----------
import pandas as _pd
_g = _pd.read_csv('/home/user/raw/nflverse/games.csv', low_memory=False); _g = _g[(_g.season == 2026) & (_g.game_type == 'REG')]
_pl = _g[_g.home_score.notna() & _g.total_line.notna()]
SD_TOT = float(((_pl.home_score + _pl.away_score) - _pl.total_line).std())
for g in partidos:
    r = _g[(_g.week == 8) & (_g.away_team == g['visitante']) & (_g.home_team == g['local'])].iloc[0]
    g['total'] = dict(linea=float(r.total_line), media=float(r.total_line), sd=SD_TOT,
                      pts_visita=float((r.total_line - r.spread_line) / 2), pts_local=float((r.total_line + r.spread_line) / 2),
                      nota=f'Centro: total de la casa ({r.total_line}). Variación real en 2026: ±{SD_TOT:.1f} puntos. Mi estimación por equipos fue menos precisa que la línea de la casa, por eso no la uso.')
parlay_info = dict(por_partido=parlays, generales=gen, seguros=seguros, eleccion=eleccion, moderados=moderados, largos=largos,
                   regla_largo='Con más piernas el pago sube, pero la probabilidad cae rápido: aun con piernas de 55% a 70%, un parlay de 5 se cumple pocas veces.',
                   regla_moderado='Riesgo moderado: 2 piernas entre 28% y 40%, o 3 piernas entre 18% y 27%. Partidos distintos, piernas sólidas y posiciones variadas.',
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
