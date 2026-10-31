import sys; sys.path.insert(0,'/home/user/scripts')
import pandas as pd, numpy as np
from props_model import dist_params, prob_ge
B=pd.read_pickle('/home/user/data/bt4_raw.pkl')
REC={'receptions','receiving_yards'}; RUSH={'carries','rushing_yards'}
def probs(B,H=None,a=1.0,capc=1.5,capt=1.5,w=0.5,bru=-0.04,gt=0.25,gc=1.0):
    out=np.empty(len(B))
    for i,r in enumerate(B.itertuples()):
        base=r.mu0
        if H is not None and r.mean>0:
            ew=getattr(r,f'ew{H}'); base=r.mu0*((1-a)+a*ew/r.mean)
        f=(r.dr/r.dfaced)**w if r.dfaced>0 and r.dr>0 else 1
        if r.grp=='rush': f*=max(0.5,1+bru*(r.olnow-r.olh))
        elif r.grp=='mix': f*=max(0.5,1+0.5*bru*(r.olnow-r.olh))
        if r.pos!='QB':
            if r.c in REC or r.c=='td_any': f*=min(capt,max(0.7,1/(1-r.dvt)))**gt
            if r.c in RUSH or (r.c=='td_any' and r.pos=='RB'): f*=min(capc,max(0.7,1/(1-min(r.dvc,0.6))))**gc
        mu=base*f; sdr=(r.sd0/r.mu0) if r.mu0>0 and r.kind!='td' else 0
        d=dict(kind='td',mu=mu) if r.kind=='td' else dict(kind=r.kind,mu=mu,sd=sdr*mu)
        out[i]=prob_ge(dist_params(d),r.L)
    return out
br=lambda p,y: float(np.mean((p-y)**2))
tr=B[B.week<=6]; te=B[B.week>=7]
if __name__=='__main__':
    R=[]
    for H,a in [(None,1),(6,0.5),(6,1),(4,0.5),(4,1),(3,0.5),(3,1),(2,0.5)]:
        R.append(dict(H=H,a=a,cap=1.5,tr=br(probs(tr,H,a),tr.y),te=br(probs(te,H,a),te.y)))
    for cap in [1.3,1.2]:
        R.append(dict(H=None,a=1,cap=cap,tr=br(probs(tr,capc=cap),tr.y),te=br(probs(te,capc=cap),te.y)))
    print(pd.DataFrame(R).round(5).to_string())
