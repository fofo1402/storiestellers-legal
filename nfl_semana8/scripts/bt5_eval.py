import sys; sys.path.insert(0,'/home/user/scripts')
import pandas as pd, numpy as np, itertools
from props_model import dist_params, prob_ge
B=pd.read_pickle('/home/user/data/bt5_raw.pkl')
REC={'receptions','receiving_yards'}; RUSH={'carries','rushing_yards'}
GRP=lambda r: 'td' if r.kind=='td' else ('rush' if r.c in RUSH else 'pass')
def probs(B,wr=0.5,wp=0.5,wt=0.5,dvw=False,gt=0.25,gc=1.0,H=4,A=0.5,bru=-0.04,cons=False):
    out=np.empty(len(B))
    for i,r in enumerate(B.itertuples()):
        base=r.mu0*((1-A)+A*getattr(r,f'ew{H}')/r.mean) if r.mean>0 else r.mu0
        g=GRP(r); w={'rush':wr,'pass':wp,'td':wt}[g]
        fr=(r.dr/r.dfaced)**w if r.dfaced>0 and r.dr>0 else 1
        f=fr
        if r.grp=='rush': f*=max(0.5,1+bru*(r.olnow-r.olh))
        elif r.grp=='mix': f*=max(0.5,1+0.5*bru*(r.olnow-r.olh))
        dvt=r.dvt_w if dvw else r.dvt; dvc=r.dvc_w if dvw else r.dvc
        fv=1.0
        if r.pos!='QB':
            if r.c in REC or r.c=='td_any': fv*=min(1.5,max(0.7,1/(1-dvt)))**gt
            if r.c in RUSH or (r.c=='td_any' and r.pos=='RB'): fv*=min(1.5,max(0.7,1/(1-min(dvc,0.6))))**gc
        if cons and fr<0.97 and fv>1: fv=1+(fv-1)*0.5   # consistencia: con rival duro, el volumen extra cuenta a la mitad
        f*=fv
        mu=base*f; sdr=(r.sd0/r.mu0) if r.mu0>0 and r.kind!='td' else 0
        d=dict(kind='td',mu=mu) if r.kind=='td' else dict(kind=r.kind,mu=mu,sd=sdr*mu)
        out[i]=prob_ge(dist_params(d),r.L)
    return out
br=lambda p,y: float(np.mean((p-y)**2))
tr=B[B.week<=6]; te=B[B.week>=7]
if __name__=='__main__':
    R=[]
    def run(**k): R.append(dict(**k,tr=br(probs(tr,**k),tr.y),te=br(probs(te,**k),te.y))); print(R[-1],flush=True)
    run(); run(dvw=True)
    for wr in [0.75,1.0]: run(dvw=True,wr=wr)
    for wp in [0.75]: run(dvw=True,wp=wp)
    for wt in [0.75,1.0]: run(dvw=True,wt=wt)
    run(dvw=True,gc=0.75); run(dvw=True,cons=True)
