# Ronda final: modelo de uso con más encogimiento + TD por volumen; búsqueda local completa y prueba de significancia contra el modelo de uso actual.
import sys; sys.path.insert(0,'/home/user/scripts')
import search as S
import numpy as np, pandas as pd, time
B9=pd.read_pickle('/home/user/data/bt9_raw.pkl').reset_index(drop=True)
assert (B9.pid.values==S.B.pid.values).all()
U={K:(B9[f'u{K}_m'].values,B9[f'u{K}_e'].values) for K in [20,50,100,200,400]}
TDV=B9.td_vol.values; isTD=S.kind=='td'
def probs_v(p):
    base=np.where(S.mean>0, S.mu0*((1-p['A'])+p['A']*S.EW[p['H']]/np.where(S.mean>0,S.mean,1)), S.mu0)
    um,ue=U[p['K']]; has=~np.isnan(um); vol=(1-p['A'])*np.where(has,um,0)+p['A']*np.where(has,ue,0)
    base=np.where(has&(vol>0),(1-p['u'])*base+p['u']*vol,base)
    tdok=isTD&~np.isnan(TDV)
    base=np.where(tdok,(1-p['tb'])*base+p['tb']*np.nan_to_num(TDV),base)
    return S.probs(p,base)
SP=dict(S.SPACE); SP['u']=[0.4,0.5,0.6,0.7,0.8]; SP['K']=[50,100,200,400]; SP['tb']=[0.0,0.25,0.5,0.75]
CUR=dict(pri='_05_12',wr=0.65,wp=1.0,wt=0.8,H=2,A=0.5,bru=-0.06,gt=0.0,gc=1.0,dvw=False,ic=0.9,in_=0.9,bg=0.0,bh=0.0,u=0.6,K=100,tb=0.0)
cache={}
def score(p):
    key=tuple(p[k] for k in SP)
    if key not in cache: cache[key]=S.lowo(probs_v(S.fix(p)))
    return cache[key]
if __name__=='__main__':
    t0=time.time(); print('actual',score(CUR),flush=True)
    rng=np.random.default_rng(5); starts=[dict(CUR)]
    for _ in range(5):
        q=dict(CUR)
        for k in ['u','K','tb','A','H','wr','wp','wt','pri']: q[k]=SP[k][rng.integers(len(SP[k]))]
        starts.append(q)
    res=[]
    for s0 in starts:
        cur=dict(s0); cs=score(cur); imp=True
        while imp:
            imp=False
            for k,vals in SP.items():
                for v in vals:
                    if v==cur[k]: continue
                    q=dict(cur); q[k]=v; sc=score(q)
                    if sc<cs-1e-7: cur,cs,imp=q,sc,True
        res.append((cs,cur)); print(round(time.time()-t0),round(cs,5),{k:cur[k] for k in ['u','K','tb','A','H','wr','wp','wt','pri','gc','bru']},flush=True)
    res.sort(key=lambda x:x[0]); pd.to_pickle(res,'/home/user/data/search10.pkl'); print('MEJOR',res[0])
