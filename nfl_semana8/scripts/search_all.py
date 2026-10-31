# Búsqueda del mejor modelo usando TODOS los juegos por igual (sin ponderar recientes): A=0 fijo.
import sys; sys.path.insert(0,'/home/user/scripts')
import search as S
import numpy as np, pandas as pd, time
S.SPACE['A']=[0.0]; S.SPACE['H']=[4]
SP=S.SPACE; probs=S.probs; fix=S.fix; br=S.br; lowo=S.lowo; holdout=S.holdout
N=int(sys.argv[1]) if len(sys.argv)>1 else 30000
rng=np.random.default_rng(11); t0=time.time(); seen=set(); res=[]
for i in range(N):
    p={k:v[rng.integers(len(v))] for k,v in SP.items()}; key=tuple(p.values())
    if key in seen: continue
    seen.add(key); res.append(dict(p,raw=br(probs(fix(p)))))
R=pd.DataFrame(res).sort_values('raw'); print('etapa1',len(R),round(time.time()-t0),flush=True)
top=[{k:r[k] for k in SP} for r in R.head(300).to_dict('records')]
st2=sorted([(lowo(probs(fix(p))),p) for p in top],key=lambda x:x[0]); print('etapa2',round(time.time()-t0),st2[0][0],flush=True)
cache={}
def score(p):
    key=tuple(p[k] for k in SP)
    if key not in cache: cache[key]=lowo(probs(fix(p)))
    return cache[key]
best=[]
for sc0,p0 in st2[:8]:
    cur=dict(p0); cs=score(cur); imp=True
    while imp:
        imp=False
        for k,vals in SP.items():
            for v in vals:
                if v==cur[k]: continue
                q=dict(cur); q[k]=v; s_=score(q)
                if s_<cs-1e-7: cur,cs,imp=q,s_,True
    best.append((cs,cur))
best.sort(key=lambda x:x[0]); b=best[0][1]
NONE=dict(S.BASE,pri='',wr=0,wp=0,wt=0,A=0,bru=0,gt=0,gc=0,dvw=False,bg=0,bh=0,ic=1.0,in_=1.0)
PREV=dict(pri='_05_12',wr=0.65,wp=1.0,wt=0.8,H=2,A=0.5,bru=-0.06,gt=0.25,gc=1.0,dvw=True,ic=0.9,in_=0.9,bg=0.0,bh=0.0)
for nm,p in [('sin ajustes',NONE),('anterior (con forma reciente)',PREV),('elegido (todos los juegos)',b)]:
    pp=probs(fix(p)); print(nm, 'lowo %.5f hold %.5f'%(lowo(pp),holdout(pp)))
print('ELEGIDO',b); pd.to_pickle(dict(best=b,all=best),'/home/user/data/search_all.pkl'); print(round(time.time()-t0))
