# Etapa 3: búsqueda local (coordenada por coordenada) optimizando la validación por semana, desde los 10 mejores.
import sys; sys.path.insert(0,'/home/user/scripts')
from search import *
import time
S=pd.read_pickle('/home/user/data/search_stage2.pkl')
starts=[{kk:r[kk] for kk in SPACE} for r in S.head(10).to_dict('records')]
cache={}
def score(p):
    key=tuple(p[k_] for k_ in SPACE)
    if key not in cache: cache[key]=lowo(probs(fix(p)))
    return cache[key]
t0=time.time(); best=[]
for s0 in starts:
    cur=dict(s0); cs=score(cur); improved=True
    while improved:
        improved=False
        for kk,vals in SPACE.items():
            for v in vals:
                if v==cur[kk]: continue
                q=dict(cur); q[kk]=v; sc=score(q)
                if sc<cs-1e-7: cur,cs,improved=q,sc,True
    best.append(dict(cur,lowo=cs,hold=holdout(probs(fix(cur)))))
    print(round(time.time()-t0), cs, cur, flush=True)
Bst=pd.DataFrame(best).sort_values('lowo'); Bst.to_pickle('/home/user/data/search_stage3.pkl'); print(Bst.to_string())
