# Agrega forma reciente al backtest: medias ponderadas por recencia (vida media H juegos) y media de los últimos 3.
import sys; sys.path.insert(0,'/home/user/scripts')
import pandas as pd, numpy as np
from props_model import *
B=pd.read_pickle('/home/user/data/bt3_raw.pkl')
HS=[2,3,4,6]
feat={}
for (t,pid),grp in B.groupby(['week','pid']):
    r=pw[(pw.player_id==pid)&(pw.week==t)].iloc[0]; pos=r.pgrp
    teams=list(pd.unique(pw[(pw.player_id==pid)&(pw.week<t)].team))
    g=player_games(pid,pos,teams,maxweek=t)
    for c in grp.c.unique():
        xs=np.array([gg['vals'][c] for gg in g]); n=len(xs); m=xs.mean()
        row={'last3':xs[-3:].mean()}
        for H in HS:
            w=0.5**((n-1-np.arange(n))/H); row[f'ew{H}']=float((w*xs).sum()/w.sum())
        row['mean']=m
        feat[(t,pid,c)]=row
for k in ['last3','mean']+[f'ew{H}' for H in HS]:
    B[k]=[feat[(a,b,c)][k] for a,b,c in zip(B.week,B.pid,B.c)]
B.to_pickle('/home/user/data/bt4_raw.pkl'); print(len(B)); print(B[['mean','ew3','last3','mu0']].describe().round(2).to_string())
