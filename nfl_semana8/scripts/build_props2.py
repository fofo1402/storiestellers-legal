# Recheck semana 8: genera props_data.json v2 (modelo calibrado con rival ajustado por ambos lados, línea ofensiva,
# compañeros ausentes y reporte final de lesiones del viernes). Incluye a todos los jugadores con participación probable.
import sys; sys.path.insert(0, '/home/user/scripts')
import pandas as pd, numpy as np, json, math
from props_model import pw, res, STATS, player_games, Ctx, params, cv_priors, dist_params, prob_ge, norm
from model2 import Ratings, RatingsP, team_shares, vacated, ol_out_cached, _sc
import pickle
from status_w8 import *
D = '/home/user/raw/nflverse/'; O = '/home/user/data/'
P2 = json.load(open(O + 'model7_params.json'))
BRU, GT, GC, CAL = P2['bru'], P2['gt'], P2['gc'], P2['cal']
RH, RA = P2['rec_h'], P2['rec_a']
VH, VA = 4, (0.5 if P2.get('dvw', True) else 0.0)   # historia de compañeros: ponderada (dvw) o promedio simple, igual que en la prueba
WG = {'rush': P2['w_rush'], 'pass': P2['w_pass'], 'td': P2['w_td']}
DISP = {'cont': P2['disp_cont'], 'count': P2['disp_count']}
REC = {'receptions', 'receiving_yards'}; RUSH = {'carries', 'rushing_yards'}
OLG = {'rushing_yards': 1.0, 'carries': 1.0, 'td_any': 0.5}
sig = lambda z: 1 / (1 + math.exp(-z))
lgt = lambda p: math.log(min(max(p, 1e-4), 1 - 1e-4) / (1 - min(max(p, 1e-4), 1 - 1e-4)))
def pcal(dp, kind, L):
    p = prob_ge(dp, L)
    if p >= 1: return 1.0
    if p <= 0: return 0.0
    a, b = CAL[kind]; return sig(a + b * lgt(p))

PRI = pickle.load(open(O + 'prior2025.pkl', 'rb'))
R = RatingsP(99, PRI, rho=P2['prior_rho'], kp=P2['prior_k']); ctx = Ctx(99); RK = ctx.rank_table()
sch = pd.read_csv(O + 'schedule_w8.csv')
J0 = json.load(open('/home/user/entrega_semana8/data.json'))
P0 = {p['partido']: p for p in J0['partidos']}
OPP = {}; GAME = {}; HA = {}
for r in sch.itertuples():
    k = f'{r.away_team} @ {r.home_team}'
    OPP[r.away_team] = r.home_team; OPP[r.home_team] = r.away_team; GAME[r.away_team] = GAME[r.home_team] = k
    HA[r.away_team] = 'visita'; HA[r.home_team] = 'local'
TEAMS = sorted(OPP)

# ---------- roster y participación ----------
ros = pd.read_csv(D + 'roster_weekly_2026.csv', low_memory=False); r8 = ros[(ros.week == 8)]
r8 = r8[r8.team.isin(TEAMS) & r8.position.isin(['QB', 'RB', 'FB', 'WR', 'TE'])]
nk = lambda s: norm(s)
OUTK = {nk(n): v for n, v in OUT.items()}; QK = {nk(n): v for n, v in QUESTIONABLE.items()}; CK = {nk(n): v for n, v in CLEARED.items()}
PK = {nk(n): v for n, v in PENDING_NOTES.items()}; RETK = {nk(n) for n in RETURNING}
sk = _sc[_sc.position.isin(['QB', 'RB', 'FB', 'HB', 'WR', 'TE'])].copy()
last3 = {t: list(res[res.team == t].sort_values('week').tail(3).game_id) for t in TEAMS}
lastg = {t: res[res.team == t].sort_values('week').tail(1).game_id.iloc[0] for t in TEAMS}

def starter_qb(t):
    if t in QB_STARTER: return QB_STARTER[t]
    q = pw[(pw.game_id == lastg[t]) & (pw.team == t) & (pw.position == 'QB')].sort_values('attempts', ascending=False)
    return q.player_display_name.iloc[0]

pool = []
for t in TEAMS:
    qbn = nk(starter_qb(t))
    for r in r8[r8.team == t].itertuples():
        if r.status != 'ACT': continue
        k = nk(r.full_name); pos = 'RB' if r.position == 'FB' else r.position
        if k in OUTK: continue
        s3 = sk[(sk.team == t) & sk.game_id.isin(last3[t]) & ((sk.gsis_id == r.gsis_id) | (sk.k == k))]
        mx3 = float(s3.offense_pct.max()) if len(s3) else 0.0
        sa = sk[(sk.team == t) & ((sk.gsis_id == r.gsis_id) | (sk.k == k)) & (sk.offense_snaps > 0)]
        avg = float(sa.offense_pct.mean()) if len(sa) else 0.0
        if pos == 'QB':
            if k != qbn: continue
        elif not (mx3 >= 0.20 or ((k in RETK or k in CK or k in QK) and avg >= 0.30)):
            continue
        pool.append(dict(pid=r.gsis_id, name=r.full_name, k=k, pos=pos, team=t, mx3=mx3, avg=avg, depth=getattr(r, 'depth_chart_position', '')))
POOL = pd.DataFrame(pool)
# nombre como aparece en estadísticas
nm = pw.drop_duplicates('player_id').set_index('player_id').player_display_name.to_dict()
POOL['jugador'] = [nm.get(p, n) for p, n in zip(POOL.pid, POOL.name)]
print('pool', len(POOL), POOL.groupby('team').size().to_dict())

# ---------- ausentes para compañeros ----------
SH = {t: team_shares(t, 99) for t in TEAMS}
rost_ok = {(r.gsis_id) for r in ros[(ros.week == 8) & (ros.status == 'ACT')].itertuples()}
team_now = ros[ros.week == 8].set_index('gsis_id').team.to_dict()
ABSENT = {}   # player_id -> peso de ausencia (1 = fuera seguro; 0.5 = duda que viene de perderse juegos o no practicó el viernes; 0.25 = duda)
from model2 import PRES
DNP_FRI = {nk('A.J. Brown'), nk('Jakobi Meyers'), nk('Tytus Howard')}
for t in TEAMS:
    ab = {}
    last2 = list(res[res.team == t].sort_values('week').tail(2).game_id)
    for q in SH[t]:
        qn = nk(nm.get(q, ''))
        missed2 = all((g, q) not in PRES for g in last2)
        if qn in OUTK or q not in rost_ok or team_now.get(q) != t: ab[q] = 1.0; continue
        if qn in QK: ab[q] = 0.5 if (missed2 or qn in DNP_FRI) else 0.25; continue
        if qn in RETK or qn in CK: continue
        if missed2: ab[q] = 1.0
    ABSENT[t] = ab

def vacated_w(team, pid, shares, absent):
    vt = vc = 0.0
    for q, (st_, sc_, pg) in shares.items():
        if q == pid or q not in absent: continue
        w = absent[q]
        if st_ >= 0.08: vt += w * st_
        if sc_ >= 0.15 and pg in ('RB', 'QB'): vc += w * sc_
    return vt, vc

# ---------- modelo por jugador ----------
games_all = {}
for x in POOL.itertuples():
    teams = list(pd.unique(pw[pw.player_id == x.pid].team))
    if x.team not in teams: teams.append(x.team)
    games_all[x.pid] = player_games(x.pid, x.pos, teams)
cv0 = cv_priors([(x.pos, games_all[x.pid]) for x in POOL.itertuples()])
TEAM_OF_GAME = res.set_index(['game_id', 'opp']).team.to_dict()

def fair_line(dp, kind, mu):
    if kind == 'td': return 0.5
    if kind == 'cont':
        cands = [math.floor(mu) + 0.5 + d for d in range(-int(mu) - 1, int(mu) + 60)]
        cands = [c for c in cands if c > 0]
    else:
        cands = [k - 0.5 for k in range(1, int(mu * 3) + 6)]
    return min(cands, key=lambda L: (abs(pcal(dp, kind, L) - 0.5), L))

def role(x):
    if x.pos == 'QB': return 'Titular'
    sh_ = max(x.mx3, x.avg) if (x.k in RETK or x.k in CK or x.k in QK) else x.mx3
    return 'Titular' if sh_ >= 0.60 else ('Rotación' if sh_ >= 0.35 else 'Rol menor')

def status_of(x):
    k = x.k
    if k in QK: return 'Duda', 'En duda (questionable): ' + QK[k][1] if QK[k][1] else 'En duda (questionable)'
    if k in CK: return 'OK', CK[k][1]
    if k in PK: return 'Pendiente', PK[k][1]
    if x.team in PENDING_TEAMS: return 'Pendiente', 'Juega el lunes: reporte final el sábado.'
    return 'OK', 'Sin designación en el reporte final del viernes.'

pct = lambda v: f"{v * 100:+.0f}%"
players = []; tests = []
for x in POOL.itertuples():
    g = games_all[x.pid]; rival = OPP[x.team]
    st_code, st_txt = status_of(x)
    base = dict(player_id=x.pid, jugador=x.jugador, pos=x.pos, equipo=x.team, rival=rival, partido=GAME[x.team], lado=HA[x.team],
                rol=role(x), snaps_ult3=round(x.mx3 * 100), jugo_ultimo=((lastg[x.team], x.pid) in PRES), pj=len(g), estado=st_code, estado_lesion=st_txt, regresa=x.k in RETK)
    if len(g) < 2:
        base.update(stats=[], muestra='sin datos', lectura_general=None, rank_general=None, factores=None)
        players.append(base); continue
    P = params(x.pos, g, rival, ctx, cv0, 0.0)
    olnow = OL_OUT_NOW[x.team][0]
    olh = float(np.mean([ol_out_cached(TEAM_OF_GAME[(gg['game_id'], gg['opp'])], gg['game_id'], 99) for gg in g]))
    sh = SH[x.team]
    vt_now, vc_now = vacated_w(x.team, x.pid, sh, ABSENT[x.team])
    prior_g = pw[(pw.player_id == x.pid) & (pw.team == x.team)].sort_values('week')
    hv = np.array([vacated(x.team, gid, x.pid, sh) for gid in prior_g.game_id]) if len(prior_g) else np.zeros((0, 2))
    if len(hv):
        nh = len(hv); wh = 0.5 ** ((nh - 1 - np.arange(nh)) / VH); wh = (1 - VA) / nh + VA * wh / wh.sum()
        ht, hc = (wh[:, None] * hv).sum(0)
    else: ht = hc = 0.0
    dvt = vt_now - ht; dvc = vc_now - hc
    stats_ = []
    for key, c, label, kind in STATS[x.pos]:
        d = P[key]; mu0 = d['mu']
        xs = np.array([gg['vals'][c] for gg in g]); n_ = len(xs); mraw = float(xs.mean())
        wts = 0.5 ** ((n_ - 1 - np.arange(n_)) / RH); ew = float((wts * xs).sum() / wts.sum())
        ffo = ((1 - RA) + RA * ew / mraw) if mraw > 0 else 1.0
        dr = R.d(x.pos, c, rival); dfc = float(np.mean([R.d(x.pos, c, gg['opp']) for gg in g]))
        gk = 'td' if kind == 'td' else ('rush' if c in RUSH else 'pass')
        fr = (dr / dfc) ** WG[gk] if dr > 0 and dfc > 0 else 1.0
        fo = max(0.5, 1 + BRU * OLG.get(c, 0) * (olnow - olh))
        fv = 1.0
        if x.pos != 'QB':
            if c in REC or c == 'td_any': fv *= min(1.5, max(0.7, 1 / (1 - dvt))) ** GT
            if c in RUSH or (c == 'td_any' and x.pos == 'RB'): fv *= min(1.5, max(0.7, 1 / (1 - min(dvc, 0.6)))) ** GC
        f = ffo * fr * fo * fv; mu = mu0 * f
        dd = dict(kind='td', mu=mu) if kind == 'td' else dict(kind=kind, mu=mu, sd=(d['sd'] / mu0 * mu * DISP[kind] if mu0 > 0 else 0.0))
        dp = dist_params(dd)
        if dp.get('dist') == 'poisson' and dp['lam'] <= 0: dp = dict(dist='zero')
        rk = int(R.rank_def(x.pos, c)[rival]); lect = 'Favorable' if rk <= 10 else ('Intermedio' if rk <= 21 else 'Difícil')
        fl = fair_line(dp, kind, mu)
        avg_line = (math.floor(d['mean_raw']) + 0.5) if kind == 'cont' else max(0.5, math.ceil(d['mean_raw'] - 1e-9) - 0.5)
        stats_.append(dict(key=key, etiqueta=label, tipo=kind, media_temporada=d['mean_raw'], proyeccion=mu, de=(d['sd'] / mu0 * mu * DISP[kind] if kind != 'td' and mu0 > 0 else None),
            rival_permite_pj=float(RK[x.pos + '_pg'][c][rival]), rival_indice=dr, rival_rank=rk, lectura=lect, calendario_indice=dfc,
            f_forma=ffo, ultimos3=[float(v) for v in xs[-3:]], prom_ult3=float(xs[-3:].mean()), f_rival=fr, f_linea=fo, f_companeros=fv, factor_total=f, dist=dp, linea_sugerida=fl,
            prob_superar_promedio=pcal(dp, kind, avg_line), linea_promedio=avg_line,
            registro=[dict(sem=gg['week'], rival=gg['opp'], cond='L' if gg['ha'] == 'vs' else 'V', valor=gg['vals'][c]) for gg in g]))
        for L in sorted({fl, avg_line, round(mu * 0.6, 1), round(mu * 1.4, 1)} if kind != 'td' else {0.5, 1.5}):
            if L > 0: tests.append(dict(player_id=x.pid, jugador=x.jugador, stat=key, linea=L, prob=pcal(dp, kind, L)))
    main = stats_[0]
    base.update(stats=stats_, muestra='corta' if len(g) < 4 else 'normal', lectura_general=main['lectura'], rank_general=main['rival_rank'],
                factores=dict(ol_fuera_hoy=olnow, ol_fuera_prom=olh, ol_nota=OL_OUT_NOW[x.team][1], compas_targets=dvt, compas_acarreos=dvc,
                              ausentes=[dict(jugador=nm.get(q, q), peso=w, targets=round(sh[q][0], 3), acarreos=round(sh[q][1], 3)) for q, w in ABSENT[x.team].items() if (sh[q][0] >= 0.08 or (sh[q][1] >= 0.15 and sh[q][2] in ('RB', 'QB')))]))
    players.append(base)

json.dump(dict(players=players, tests=tests), open(O + 'props2_raw.json', 'w'), ensure_ascii=False)
print(len(players), 'jugadores', len(tests), 'casos')
