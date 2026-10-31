# Genera props_data.json (datos de la app) con el modelo calibrado: w_prob=0.3 + recalibración logística por tipo
import sys; sys.path.insert(0,'/home/user/scripts')
import pandas as pd, numpy as np, json, pickle, math
from props_model import *
WP=0.3
CAL={k:[float(v[0]),float(v[1])] for k,v in pickle.load(open('/home/user/data/calib.pkl','rb'))[WP].items()}
J=json.load(open('/home/user/entrega_semana8/data.json'))
ctx=Ctx(99); RK=ctx.rank_table()
EV=J['evaluados']; ros8=pd.read_csv('/home/user/raw/nflverse/roster_weekly_2026.csv',low_memory=False); ros8=ros8[ros8.week==8].set_index('gsis_id')
games_all={}
for e in EV:
    teams=list(pd.unique(pw[pw.player_id==e['player_id']].team)) or [e['equipo']]
    games_all[e['player_id']]=player_games(e['player_id'],e['pos'],teams)
cv0=cv_priors([(e['pos'],games_all[e['player_id']]) for e in EV])
sig=lambda z:1/(1+math.exp(-z)); lgt=lambda p: math.log(min(max(p,1e-4),1-1e-4)/(1-min(max(p,1e-4),1-1e-4)))
def p_final(dp,kind,L):
    p=prob_ge(dp,L); a,b=CAL[kind]
    if p>=1.0: return 1.0
    if p<=0.0: return 0.0
    return sig(a+b*lgt(p))
players=[]; tests=[]
sel={s['player_id']:s for s in J['selecciones']}
for e in EV:
    pid=e['player_id']; g=games_all[pid]; P=params(e['pos'],g,e['rival'],ctx,cv0,WP)
    stats_=[]
    for key,c,label,kind in STATS[e['pos']]:
        d=P[key]; dp=dist_params(d)
        rk=int(RK[e['pos']][c][e['rival']]); pg=float(RK[e['pos']+'_pg'][c][e['rival']])
        lect='Favorable' if rk<=10 else ('Intermedio' if rk<=21 else 'Difícil')
        mu=d['mu']
        default=(math.floor(mu)+0.5) if kind=='cont' else (max(1,round(mu)) if kind=='count' else 1)
        stats_.append(dict(key=key,etiqueta=label,tipo=kind,media_temporada=d['mean_raw'],proyeccion=mu,de=d.get('sd'),
            rival_permite_pj=pg,rival_rank=rk,lectura=lect,dureza=d['sos'],factor_matchup=d['factor'],dist=dp,
            linea_sugerida=default,registro=[dict(sem=gg['week'],rival=gg['opp'],cond='L' if gg['ha']=='vs' else 'V',valor=gg['vals'][c]) for gg in g]))
        # casos de prueba
        for L in ([default, round(mu*0.6,1), round(mu*1.4,1)] if kind!='td' else [1,2]):
            if L<=0: continue
            tests.append(dict(player_id=pid,jugador=e['jugador'],stat=key,linea=L,prob=p_final(dp,kind,L)))
    s=sel.get(pid)
    players.append(dict(player_id=pid,jugador=e['jugador'],pos=e['pos'],equipo=e['equipo'],rival=e['rival'],partido=e['partido'],pj=e['pj'],
        lectura_general=e['lectura'].replace('Neutral','Intermedio'),rank_general=e['rank'],estado_lesion=e['lesion'],veredicto=e['veredicto'],
        seleccion=(dict(confianza=s['confianza'],categorias=s['categorias'],por_que=s['por_que'],a=s['por_que_confianza']['a_sube'],b=s['por_que_confianza']['b_frena'],c=s['por_que_confianza']['c_regla']) if s else None),
        stats=stats_))
meta=dict(J['metadatos']); meta.update(peso_w_probabilidad=WP,recalibracion=CAL,
  etiquetas=[dict(desde=0.80,etiqueta='Muy fácil'),dict(desde=0.60,etiqueta='Fácil'),dict(desde=0.40,etiqueta='Parejo'),dict(desde=0.20,etiqueta='Difícil'),dict(desde=0.0,etiqueta='Muy difícil')])
out=dict(metadatos=meta,partidos=J['partidos'],selecciones=J['selecciones'],jugadores=players)
json.dump(out,open('/home/user/entrega_semana8/props_data.json','w'),ensure_ascii=False,separators=(',',':'))
json.dump(tests,open('/home/user/entrega_semana8/casos_prueba.json','w'),ensure_ascii=False,indent=0)
print(len(players),'jugadores',len(tests),'casos de prueba'); print(CAL)
x=[p for p in players if p['jugador'] in ('T.J. Hockenson','Zay Flowers','Jaylen Warren','Lamar Jackson')]
for p in x:
    for s_ in p['stats']: print(p['jugador'],s_['key'],round(s_['proyeccion'],2),s_['linea_sugerida'],s_['dist']['dist'],s_['lectura'],s_['rival_rank'])
