import sys; sys.path.insert(0,'/home/user/scripts')
import pandas as pd, numpy as np, math, json
from props_model import *
rows=[]
for t in [4,5,6,7,8]:
    ctx=Ctx(t)
    cur=pw[pw.week==t]
    cands=[]
    for pid,grp in cur.groupby('player_id'):
        r=grp.iloc[0]; pos=r.pgrp
        if pos=='QB' and r.attempts<15: continue
        prior=pw[(pw.player_id==pid)&(pw.week<t)]
        teams=list(pd.unique(prior.team)) or [r.team]
        if r.team not in teams: continue  # traspasado justo esa semana: se omite
        games=player_games(pid,pos,teams,maxweek=t)
        if len(games)<3: continue
        cands.append((pid,pos,r,games))
    cv0=cv_priors([(c[1],c[3]) for c in cands])
    for pid,pos,r,games in cands:
        P={w:params(pos,games,r.opponent_team,ctx,cv0,w) for w in (0.0,0.6,1.0)}
        for key,c,lab,kind in STATS[pos]:
            m=P[0.6][key]['mean_raw']
            if kind=='td': lines=[1] if pos!='QB' else [1,2,3]
            else:
                if m<=0: continue
                lines=sorted({(math.floor(m*q)+0.5) if kind=='cont' else max(1,round(m*q)) for q in (0.5,0.75,1.0,1.25,1.5)})
            actual=float(getattr(r,c))
            xs=np.array([g['vals'][c] for g in games])
            for L in lines:
                y=1 if (actual>=L if kind=='cont' else actual>=math.ceil(L-1e-9)) else 0
                rec=dict(week=t,pid=pid,pos=pos,stat=key,kind=kind,L=L,y=y,n=len(games))
                for w in P: rec[f'p_w{w}']=prob_ge(dist_params(P[w][key]),L)
                thr=L if kind=='cont' else math.ceil(L-1e-9)
                rec['p_emp']=((xs>=thr).sum()+0.5)/(len(xs)+1)
                rows.append(rec)
B=pd.DataFrame(rows); B.to_csv('/home/user/data/backtest.csv',index=False)
print('predicciones',len(B),'jugador-juego',B.groupby(['week','pid']).ngroups)
def brier(p,y): return float(np.mean((p-y)**2))
def ll(p,y): p=np.clip(p,1e-4,1-1e-4); return float(-np.mean(y*np.log(p)+(1-y)*np.log(1-p)))
summ={}
for name in ['p_w0.0','p_w0.6','p_w1.0','p_emp']:
    summ[name]=dict(brier=brier(B[name],B.y),logloss=ll(B[name],B.y))
print(json.dumps(summ,indent=1))
for kind in ['cont','count','td']:
    x=B[B.kind==kind]; print(kind,len(x),{n:round(brier(x[n],x.y),4) for n in ['p_w0.0','p_w0.6','p_w1.0','p_emp']})
bins=[0,0.2,0.4,0.6,0.8,1.0001]; names=['Muy difícil (<20%)','Difícil (20-40%)','Parejo (40-60%)','Fácil (60-80%)','Muy fácil (≥80%)']
B['bin']=pd.cut(B['p_w0.6'],bins,right=False,labels=names)
cal=B.groupby('bin',observed=False).agg(n=('y','size'),prob_media=('p_w0.6','mean'),acierto=('y','mean'))
print(cal.round(3))
for kind in ['cont','count','td']:
    x=B[B.kind==kind]; print(kind); print(x.groupby(pd.cut(x['p_w0.6'],bins,right=False,labels=names),observed=False).agg(n=('y','size'),prob=('p_w0.6','mean'),hit=('y','mean')).round(3))
