# Modelo v2 (recheck): ajuste de rival por AMBOS lados + línea ofensiva.
#  - Cada defensa recibe un índice D (1 = promedio) ajustado por la calidad de las ofensivas que enfrentó.
#  - Cada ofensiva recibe un índice A ajustado por las defensas que enfrentó.
#    Modelo multiplicativo por posición y estadística: esperado(ofensiva o vs defensa d) = liga * A_o * D_d,
#    ajustado iterativamente y encogido hacia 1 con k juegos ficticios.
#  - El jugador se ajusta por las defensas (ya ajustadas) que enfrentó: factor = (D_rival / prom D_enfrentadas)^w.
#  - Línea ofensiva: titulares = los 5 OL con más snaps; ol_out = cuántos faltan. Efecto por titular faltante
#    relativo a los que faltaban en promedio en sus juegos previos.
import sys; sys.path.insert(0, '/home/user/scripts')
import pandas as pd, numpy as np, math
from props_model import pw, res, STATS, COLS, sc

K_RAT = {'cont': 3.0, 'count': 3.0, 'td': 6.0}
KIND = {c: k for p in STATS for (_, c, _, k) in STATS[p]}
for c in COLS: KIND.setdefault(c, 'count')

# totales por ofensiva-juego y posición (0 si no hubo jugadores de esa posición con estadística)
_og = pw.groupby(['team', 'game_id', 'pgrp'])[COLS].sum().reset_index()
TG = res[['team', 'opp', 'game_id', 'week']]
OG = {p: TG.merge(_og[_og.pgrp == p].drop(columns='pgrp'), on=['team', 'game_id'], how='left').fillna(0) for p in STATS}

class Ratings:
    def __init__(self, maxweek=99, iters=60):
        self.A = {}; self.D = {}; self.L = {}
        for p in STATS:
            x = OG[p][OG[p].week < maxweek]
            for c in COLS:
                y = x[c].values; o = x.team.values; d = x.opp.values
                L = y.mean() if len(y) else 0.0
                teams = sorted(set(o) | set(d))
                A = {t: 1.0 for t in teams}; Dd = {t: 1.0 for t in teams}
                k = K_RAT[KIND[c]]
                if L > 0:
                    df = pd.DataFrame({'y': y, 'o': o, 'd': d})
                    for _ in range(iters):
                        df['ea'] = L * df.d.map(Dd)
                        sa = df.groupby('o').agg(y=('y', 'sum'), e=('ea', 'sum'))
                        A = ((sa.y + k * L) / (sa.e + k * L)).to_dict()
                        df['ed'] = L * df.o.map(A)
                        sd = df.groupby('d').agg(y=('y', 'sum'), e=('ed', 'sum'))
                        Dd = ((sd.y + k * L) / (sd.e + k * L)).to_dict()
                        m = np.mean(list(Dd.values())); Dd = {t: v / m for t, v in Dd.items()}
                self.A[(p, c)] = A; self.D[(p, c)] = Dd; self.L[(p, c)] = L
    def d(self, p, c, team): return self.D[(p, c)].get(team, 1.0)
    def a(self, p, c, team): return self.A[(p, c)].get(team, 1.0)
    def rank_def(self, p, c):
        s = pd.Series(self.D[(p, c)]); return s.rank(ascending=False, method='min').astype(int).to_dict()

# ---------------- línea ofensiva ----------------
OLPOS = {'T', 'G', 'C', 'OL'}
_ol = sc[sc.position.isin(OLPOS)][['game_id', 'week', 'team', 'player', 'pfr_player_id', 'offense_snaps', 'offense_pct']]
def ol_starters(team, maxweek=99):
    x = _ol[(_ol.team == team) & (_ol.week < maxweek)]
    return list(x.groupby('pfr_player_id').offense_snaps.sum().sort_values(ascending=False).head(5).index)
def ol_out_game(team, game_id, starters):
    x = _ol[(_ol.team == team) & (_ol.game_id == game_id)].set_index('pfr_player_id').offense_pct
    return int(sum(1 for s in starters if x.get(s, 0) < 0.5))
_OLC = {}
def ol_out_cached(team, game_id, maxweek):
    k = (team, game_id, maxweek)
    if k not in _OLC: _OLC[k] = ol_out_game(team, game_id, ol_starters(team, maxweek))
    return _OLC[k]

# grupos de estadística afectados por la línea: 'pass' (pase/recepción) y 'rush' (tierra)
OLGRP = {'passing_yards': 'pass', 'completions': 'pass', 'passing_tds': 'pass', 'receiving_yards': 'pass', 'receptions': 'pass',
         'rushing_yards': 'rush', 'carries': 'rush', 'td_any': 'mix', 'targets': 'pass', 'attempts': 'pass'}

# ---------------- compañeros ausentes (targets / acarreos que quedan libres) ----------------
import unicodedata, re
def _norm(n):
    n = unicodedata.normalize('NFKD', str(n)).encode('ascii', 'ignore').decode().lower(); n = re.sub(r'[^a-z ]', '', n)
    n = re.sub(r'\b(jr|sr|ii|iii|iv|v)\b', '', n); return ' '.join(n.split())
_pl = pd.read_csv('/home/user/raw/nflverse/players.csv', low_memory=False)[['gsis_id', 'pfr_id']].dropna()
_sc = sc.copy()
if 'gsis_id' not in _sc.columns:
    _sc = _sc.merge(_pl.rename(columns={'pfr_id': 'pfr_player_id'}), on='pfr_player_id', how='left')
_sc['k'] = _sc.player.map(_norm)
# presencia: snaps ofensivos > 0 (por gsis o por nombre) o fila de estadística
PRES = set()
for r in _sc[_sc.offense_snaps > 0].itertuples():
    if isinstance(r.gsis_id, str): PRES.add((r.game_id, r.gsis_id))
_k2id = pw.drop_duplicates('player_id').set_index('k').player_id.to_dict() if 'k' in pw.columns else {}
for r in _sc[(_sc.offense_snaps > 0) & _sc.gsis_id.isna()].itertuples():
    pid = _k2id.get(r.k)
    if pid: PRES.add((r.game_id, pid))
for r in pw[['game_id', 'player_id']].itertuples(): PRES.add((r.game_id, r.player_id))
_tg = pw.groupby(['team', 'game_id']).agg(T=('targets', 'sum'), C=('carries', 'sum')).reset_index()
_TG = _tg.set_index(['team', 'game_id'])
def team_shares(team, maxweek):
    """participación de targets y acarreos de cada jugador del equipo en los juegos que jugó (antes de maxweek)."""
    x = pw[(pw.team == team) & (pw.week < maxweek)]
    out = {}
    for pid, g in x.groupby('player_id'):
        gids = list(g.game_id)
        if len(gids) < 2: continue
        T = _TG.loc[[(team, gg) for gg in gids], 'T'].sum(); C = _TG.loc[[(team, gg) for gg in gids], 'C'].sum()
        out[pid] = (g.targets.sum() / T if T else 0.0, g.carries.sum() / C if C else 0.0, g.pgrp.iloc[0])
    return out
def vacated(team, game_id, pid, shares, absent=None):
    """suma de participación de compañeros (>=8%) ausentes en ese juego. absent: set de player_id ausentes (pronóstico)."""
    vt = vc = 0.0
    for q, (st_, sc_, pg) in shares.items():
        if q == pid: continue
        out = (q in absent) if absent is not None else ((game_id, q) not in PRES)
        if not out: continue
        if st_ >= 0.08: vt += st_
        if sc_ >= 0.15 and pg in ('RB', 'QB'): vc += sc_
    return vt, vc
