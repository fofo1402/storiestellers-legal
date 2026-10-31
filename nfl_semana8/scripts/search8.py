# Compite "modelo de uso" (volumen × eficiencia encogida) mezclado con el modelo actual. Misma validación por semana.
import sys; sys.path.insert(0,'/home/user/scripts')
import search as S
import numpy as np, pandas as pd, time
B8=pd.read_pickle('/home/user/data/bt8_raw.pkl').reset_index(drop=True)
assert len(B8)==len(S.B) and (B8.pid.values==S.B.pid.values).all()
U={K:(B8[f'u{K}_m'].values,B8[f'u{K}_e'].values) for K in [20,50,100]}
_orig=S.probs
def probs_u(p):
    u=p.get('u',0); K=p.get('K',50)
    base_cur=np.where(S.mean>0, S.mu0*((1-p['A'])+p['A']*S.EW[p['H']]/np.where(S.mean>0,S.mean,1)), S.mu0)
    if u==0: return S.probs(p)
    um,ue=U[K]; has=~np.isnan(um)
    vol=(1-p['A'])*np.where(has,um,0)+p['A']*np.where(has,ue,0)
    newbase=np.where(has&(vol>0),(1-u)*base_cur+u*vol,base_cur)
    return S.probs(p, newbase)
BEST=dict(pri='_05_12',wr=0.65,wp=1.0,wt=0.8,H=2,A=0.5,bru=-0.06,gt=0.0,gc=1.0,dvw=False,ic=0.9,in_=0.9,bg=0.0,bh=0.0)
def ev(p): pp=probs_u(S.fix(p)); return S.lowo(pp), S.holdout(pp), S.br(pp)
if __name__=='__main__':
    t0=time.time()
    print('vigente', ev(BEST), flush=True)
    R=[]
    for K in [20,50,100]:
        for u in [0.25,0.5,0.75,1.0]:
            p=dict(BEST,u=u,K=K); l,h,r=ev(p); R.append(dict(K=K,u=u,lowo=l,hold=h,raw=r)); print(K,u,round(l,5),round(h,5),flush=True)
    R=pd.DataFrame(R).sort_values('lowo'); print(R.to_string()); print(round(time.time()-t0))
