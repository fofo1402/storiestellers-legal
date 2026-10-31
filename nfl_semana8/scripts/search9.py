# Ajuste fino conjunto: modelo actual + modelo de uso (u, K) con validación por semana.
import sys; sys.path.insert(0,'/home/user/scripts')
import search as S
from search8 import probs_u, BEST
import numpy as np, pandas as pd, time
SP=dict(S.SPACE); SP['u']=[0.25,0.4,0.5,0.6,0.75]; SP['K']=[20,50,100]
cache={}
def score(p):
    key=tuple(p[k] for k in SP)
    if key not in cache: cache[key]=S.lowo(probs_u(S.fix(p)))
    return cache[key]
t0=time.time(); res=[]
starts=[dict(BEST,u=0.5,K=100),dict(BEST,u=0.75,K=50),dict(BEST,u=0.5,K=50,A=0.25),dict(BEST,u=0.6,K=100,dvw=True,gt=0.25)]
for s0 in starts:
    cur=dict(s0); cs=score(cur); imp=True
    while imp:
        imp=False
        for k,vals in SP.items():
            for v in vals:
                if v==cur[k]: continue
                q=dict(cur); q[k]=v; sc=score(q)
                if sc<cs-1e-7: cur,cs,imp=q,sc,True
    pp=probs_u(S.fix(cur)); res.append((cs,S.holdout(pp),cur)); print(round(time.time()-t0),round(cs,5),round(res[-1][1],5),cur,flush=True)
res.sort(key=lambda x:x[0]); pd.to_pickle(res,'/home/user/data/search9.pkl'); print('MEJOR',res[0])
