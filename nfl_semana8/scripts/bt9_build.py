# Más variantes: eficiencia más encogida (K 200/400) y TD esperado por volumen (oportunidades × tasa de la posición).
import sys; sys.path.insert(0,'/home/user/scripts')
import pandas as pd, numpy as np, time
from props_model import *
B=pd.read_pickle('/home/user/data/bt8_raw.pkl')
KS=[200,400]
USE={'receiving_yards':('targets','receiving_yards'),'receptions':('targets','receptions'),'rushing_yards':('carries','rushing_yards'),
     'passing_yards':('attempts','passing_yards'),'completions':('attempts','completions')}
t0=time.time(); feats={}; tdf={}
for t in [4,5,6,7,8]:
    pv=pw[pw.week<t]; pri={}
    for p in ['QB','RB','WR','TE']:
        x=pv[pv.pgrp==p]
        if p=='QB': x=x[x.attempts>=15]
        for c,(vol,num) in USE.items(): pri[(p,c)]=x[num].sum()/max(x[vol].sum(),1)
    rb=pv[pv.pgrp=='RB']; r_car=rb.rushing_tds.sum()/rb.carries.sum(); r_rbt=rb.receiving_tds.sum()/max(rb.targets.sum(),1)
    rt={p:pv[pv.pgrp==p].td_any.sum()/max(pv[pv.pgrp==p].targets.sum(),1) for p in ['WR','TE']}
    q=pv[(pv.pgrp=='QB')&(pv.attempts>=15)]; r_att=q.passing_tds.sum()/q.attempts.sum()
    for pid,grp in B[B.week==t].groupby('pid'):
        r=pw[(pw.player_id==pid)&(pw.week==t)].iloc[0]; pos=r.pgrp
        teams=list(pd.unique(pw[(pw.player_id==pid)&(pw.week<t)].team))
        g=player_games(pid,pos,teams,maxweek=t); n=len(g)
        w2=0.5**((n-1-np.arange(n))/2); w2=w2/w2.sum()
        arr=lambda k: np.array([gg['vals'][k] for gg in g])
        for c in grp.c.unique():
            if c in USE:
                vol,num=USE[c]; V=arr(vol); N=arr(num)
                for K in KS:
                    eff=(N.sum()+K*pri[(pos,c)])/(V.sum()+K); feats[(t,pid,c,K)]=(V.mean()*eff,(w2*V).sum()*eff)
            elif c in ('td_any','passing_tds'):
                if pos=='QB': lam0=r_att*0.5*(arr('attempts').mean()+(w2*arr('attempts')).sum())
                elif pos=='RB': lam0=r_car*0.5*(arr('carries').mean()+(w2*arr('carries')).sum())+r_rbt*0.5*(arr('targets').mean()+(w2*arr('targets')).sum())
                else: lam0=rt[pos]*0.5*(arr('targets').mean()+(w2*arr('targets')).sum())
                tdf[(t,pid,c)]=lam0
    print(t,round(time.time()-t0),flush=True)
for K in KS:
    B[f'u{K}_m']=[feats.get((a,b,c,K),(np.nan,np.nan))[0] for a,b,c in zip(B.week,B.pid,B.c)]
    B[f'u{K}_e']=[feats.get((a,b,c,K),(np.nan,np.nan))[1] for a,b,c in zip(B.week,B.pid,B.c)]
B['td_vol']=[tdf.get((a,b,c),np.nan) for a,b,c in zip(B.week,B.pid,B.c)]
B.to_pickle('/home/user/data/bt9_raw.pkl'); print('ok', B.td_vol.describe().round(3).to_string())
