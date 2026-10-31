# Tabla única de variables para la búsqueda de modelos: agrega más variantes de referencia 2025, guion (diferencial de puntos) y localía.
import sys; sys.path.insert(0,'/home/user/scripts')
import pandas as pd, numpy as np, pickle, time
from props_model import *
from model2 import RatingsP
PRI=pickle.load(open('/home/user/data/prior2025.pkl','rb'))
B=pd.read_pickle('/home/user/data/bt6_raw.pkl'); B.columns=[c.replace('.','') for c in B.columns]
VAR=[(0.7,12),(0.9,8),(0.9,12),(1.0,16),(0.5,12)]
t0=time.time(); feats={}; ctxf={}
for t in [4,5,6,7,8]:
    RS={v:RatingsP(t,PRI,rho=v[0],kp=v[1]) for v in VAR}
    rr=res[res.week<t]; dif=(rr.groupby('team').pf.sum()-rr.groupby('team').pa.sum())/rr.groupby('team').size()
    for pid,grp in B[B.week==t].groupby('pid'):
        r=pw[(pw.player_id==pid)&(pw.week==t)].iloc[0]; pos=r.pgrp
        teams=list(pd.unique(pw[(pw.player_id==pid)&(pw.week<t)].team))
        games=player_games(pid,pos,teams,maxweek=t)
        x=res[(res.game_id==r.game_id)&(res.team==r.team)].iloc[0]
        ctxf[(t,pid)]=(float(dif.get(r.team,0)-dif.get(r.opponent_team,0)), 1 if x.ha=='vs' else 0)
        for c in grp.c.unique():
            for v,R in RS.items():
                feats[(t,pid,c,v)]=(R.d(pos,c,r.opponent_team), float(np.mean([R.d(pos,c,g['opp']) for g in games])))
    print(t,round(time.time()-t0),flush=True)
for v in VAR:
    tag=f"{str(v[0]).replace('.','')}_{v[1]}"
    B['dr_'+tag]=[feats[(a,b,c,v)][0] for a,b,c in zip(B.week,B.pid,B.c)]
    B['df_'+tag]=[feats[(a,b,c,v)][1] for a,b,c in zip(B.week,B.pid,B.c)]
B['gap']=[ctxf[(a,b)][0] for a,b in zip(B.week,B.pid)]; B['home']=[ctxf[(a,b)][1] for a,b in zip(B.week,B.pid)]
B.to_pickle('/home/user/data/bt7_raw.pkl'); print('ok', [c for c in B.columns if c.startswith('dr')])
