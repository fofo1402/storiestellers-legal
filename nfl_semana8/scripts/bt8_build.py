# Variables del "modelo de uso": volumen (targets/acarreos/intentos, con y sin peso reciente) × eficiencia encogida al promedio de la posición.
import sys; sys.path.insert(0,'/home/user/scripts')
import pandas as pd, numpy as np, time
from props_model import *
B=pd.read_pickle('/home/user/data/bt7_raw.pkl')
KS=[20,50,100]
# qué volumen y eficiencia usa cada estadística: (volumen, numerador)
USE={'receiving_yards':('targets','receiving_yards'),'receptions':('targets','receptions'),'rushing_yards':('carries','rushing_yards'),
     'passing_yards':('attempts','passing_yards'),'completions':('attempts','completions')}
t0=time.time(); feats={}
for t in [4,5,6,7,8]:
    pv=pw[pw.week<t]
    pri={}
    for p in ['QB','RB','WR','TE']:
        x=pv[pv.pgrp==p]
        if p=='QB': x=x[x.attempts>=15]
        for c,(vol,num) in USE.items():
            pri[(p,c)]=x[num].sum()/max(x[vol].sum(),1)
    for pid,grp in B[B.week==t].groupby('pid'):
        r=pw[(pw.player_id==pid)&(pw.week==t)].iloc[0]; pos=r.pgrp
        teams=list(pd.unique(pw[(pw.player_id==pid)&(pw.week<t)].team))
        g=player_games(pid,pos,teams,maxweek=t); n=len(g)
        w2=0.5**((n-1-np.arange(n))/2); w2=w2/w2.sum()
        for c in grp.c.unique():
            if c not in USE: continue
            vol,num=USE[c]
            V=np.array([gg['vals'][vol] for gg in g]); N=np.array([gg['vals'][num] for gg in g])
            vm=V.mean(); vew=(w2*V).sum()
            for K in KS:
                eff=(N.sum()+K*pri[(pos,c)])/(V.sum()+K)
                feats[(t,pid,c,K)]=(vm*eff, vew*eff)
    print(t,round(time.time()-t0),flush=True)
for K in KS:
    B[f'u{K}_m']=[feats.get((a,b,c,K),(np.nan,np.nan))[0] for a,b,c in zip(B.week,B.pid,B.c)]
    B[f'u{K}_e']=[feats.get((a,b,c,K),(np.nan,np.nan))[1] for a,b,c in zip(B.week,B.pid,B.c)]
B.to_pickle('/home/user/data/bt8_raw.pkl'); print('ok', B[[f'u50_m','mean']].describe().round(2).to_string())
