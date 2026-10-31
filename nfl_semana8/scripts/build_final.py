# Ensambla props_data.json v2 para la app: partidos (nombres completos, visita/local, bajas), jugadores, favoritos por partido,
# cambios frente al análisis anterior y metadatos del modelo. También genera casos_prueba.json.
import sys; sys.path.insert(0, '/home/user/scripts')
import json, math
from collections import defaultdict
from status_w8 import OUT, QUESTIONABLE, FUENTES, TEAM_NAME, OL_OUT_NOW, PENDING_TEAMS
O = '/home/user/data/'; E = '/home/user/entrega_semana8/'
RAW = json.load(open(O + 'props2_raw.json')); P2 = json.load(open(O + 'model2_params.json'))
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
    r.append(f"{p['rival']} permite {pcs(rv)} vs. el promedio en {s['etiqueta'].lower()} a {p['pos']} (#{s['rival_rank']} de 32), ya ajustado por las ofensivas que enfrentó; "
             f"los rivales previos de {surname(p['jugador'])} permitían {pcs(cal)}. Efecto del rival: {pcs(s['f_rival'])}.")
    if abs(s['f_companeros'] - 1) >= 0.03:
        if s['key'] in RUSHK: aus = [a['jugador'] for a in p['factores']['ausentes'] if a['acarreos'] >= 0.15]
        else: aus = [a['jugador'] for a in p['factores']['ausentes'] if a['targets'] >= 0.08]
        quien = ', '.join(aus[:4]) if aus else 'regresos de compañeros'
        r.append(f"{'Más' if s['f_companeros'] > 1 else 'Menos'} volumen por compañeros ({quien}): {pcs(s['f_companeros'])}.")
    if abs(s['f_linea'] - 1) >= 0.02:
        fx = p['factores']; nota = fx['ol_nota'] or f"{p['equipo']} tiene completos a sus 5 titulares de la línea"
        r.append(f"Línea ofensiva: {nota} (en sus juegos previos faltaban {fx['ol_fuera_prom']:.1f} en promedio): {pcs(s['f_linea'])} en tierra.")
    return r

# ---------- favoritos por partido ----------
fav = defaultdict(list); near = {}
for p in players:
    if not p['stats'] or p['pj'] < 3: continue
    s = main_stat(p)
    if s['proyeccion'] < TH[p['pos']] and not (s['key'] == 'rec'): continue
    pr = s['prob_superar_promedio']; f = s['factor_total']
    cand = dict(player_id=p['player_id'], jugador=p['jugador'], pos=p['pos'], equipo=p['equipo'], stat=s['key'], etiqueta=s['etiqueta'],
                prob=pr, linea=s['linea_promedio'], promedio=s['media_temporada'], proyeccion=s['proyeccion'], factor=f, estado=p['estado'])
    best = near.get(p['partido'])
    if best is None or pr > best['prob']: near[p['partido']] = cand
    if pr >= 0.50 and f >= 1.04:
        missed_last = (not p['jugo_ultimo']) or p['regresa'] or p['snaps_ult3'] < 40
        alta = pr >= 0.56 and p['estado'] == 'OK' and p['pj'] >= 4 and not missed_last
        cand.update(confianza='Alta' if alta else 'Media', por_que=reasons(p, s),
                    riesgo=(p['estado_lesion'] if p['estado'] != 'OK' else (('Regresa de lesión: su volumen puede venir limitado.' if (not p['jugo_ultimo'] or p['regresa']) else f"Uso reciente bajo ({p['snaps_ult3']}% de snaps máx. en los últimos 3 juegos): su carga puede venir limitada.") if missed_last else
                            ('Muestra corta (menos de 4 juegos).' if p['pj'] < 4 else ''))))
        fav[p['partido']].append(cand)
for g in fav: fav[g].sort(key=lambda c: (c['confianza'] != 'Alta', -c['prob']))

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
        favoritos=fav.get(g['partido'], []), mas_cercano=(None if fav.get(g['partido']) else near.get(g['partido']))))

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

meta = dict(OLD['metadatos'])
meta.update(tipo_corrida='RECHECK FINAL (v2)', datos_al='viernes 30-oct-2026, reporte final de lesiones; corrida del sábado 31-oct (madrugada, hora Monterrey)',
    recalibracion=P2['cal'], peso_w_probabilidad=P2['w'],
    modelo=dict(w_rival=P2['w'], linea_ofensiva_por_titular=P2['bru'], companeros_targets=P2['gt'], companeros_acarreos=P2['gc'],
                prueba=dict(sin_ajuste=round(P2['test']['sin_ajuste'], 4), anterior=0.1980, v2=round(P2['test']['v2'], 4)),
                calibracion={k: round(v['acierto'] * 100) for k, v in P2['calib'].items()}),
    fuentes_lesiones=[dict(nombre=n, url=u) for n, u in FUENTES],
    avisos=['Análisis de patrones, no garantía ni recomendación de apuesta. Solo mayores de 18 años.',
            'Lesiones: reporte final del viernes 30-oct (equipos y medios). CHI-SEA juega el lunes: su reporte final sale el sábado.',
            'Fuente de estadísticas: nflverse (datos oficiales de juego de la NFL). Sin cuotas ni líneas de casas de apuestas.'])
meta.pop('formula', None); meta.pop('peso_w', None)
out = dict(metadatos=meta, partidos=partidos, jugadores=players, cambios=cambios)
json.dump(out, open(E + 'props_data.json', 'w'), ensure_ascii=False, separators=(',', ':'))
json.dump(RAW['tests'], open(E + 'casos_prueba.json', 'w'), ensure_ascii=False, indent=0)
nf = sum(len(v) for v in fav.values())
print('partidos', len(partidos), 'jugadores', len(players), 'favoritos', nf, 'casos', len(RAW['tests']))
for g in partidos:
    print(g['partido'], [(c['jugador'], c['confianza'], round(c['prob'], 2)) for c in g['favoritos']] or ('cercano', g['mas_cercano']['jugador'], round(g['mas_cercano']['prob'], 2)))
for c in cambios: print(' ', c['jugador'], c['antes'], '->', c['ahora'], '|', c['motivo'][:110])
