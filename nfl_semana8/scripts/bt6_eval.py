import sys; sys.path.insert(0,'/home/user/scripts')
import pandas as pd, numpy as np
from props_model import dist_params, prob_ge
B=pd.read_pickle('/home/user/data/bt6_raw.pkl'); B.columns=[c.replace('.','') for c in B.columns]
REC={'receptions','receiving_yards'}; RUSH={'carries','rushing_yards'}
def probs(B,var=None,w=0.5,gt=0.25,gc=1.0,H=4,A=0.5,bru=-0.04):
    out=np.empty(len(B))
    drc,dfc=(f'dr_{str(var[0]).replace(".","")}_{var[1]}',f'df_{str(var[0]).replace(".","")}_{var[1]}') if var else ('dr','dfaced')
    for i,r in enumerate(B.itertuples()):
        base=r.mu0*((1-A)+A*getattr(r,f'ew{H}')/r.mean) if r.mean>0 else r.mu0
        dr=getattr(r,drc); dfa=getattr(r,dfc)
        f=(dr/dfa)**w if dfa>0 and dr>0 else 1
        if r.grp=='rush': f*=max(0.5,1+bru*(r.olnow-r.olh))
        elif r.grp=='mix': f*=max(0.5,1+0.5*bru*(r.olnow-r.olh))
        if r.pos!='QB':
            if r.c in REC or r.c=='td_any': f*=min(1.5,max(0.7,1/(1-r.dvt_w)))**gt
            if r.c in RUSH or (r.c=='td_any' and r.pos=='RB'): f*=min(1.5,max(0.7,1/(1-min(r.dvc_w,0.6))))**gc
        mu=base*f; sdr=(r.sd0/r.mu0) if r.mu0>0 and r.kind!='td' else 0
        d=dict(kind='td',mu=mu) if r.kind=='td' else dict(kind=r.kind,mu=mu,sd=sdr*mu)
        out[i]=prob_ge(dist_params(d),r.L)
    return out
br=lambda p,y: float(np.mean((p-y)**2))
tr=B[B.week<=6]; te=B[B.week>=7]
if __name__=='__main__':
    for var in [None,(0.3,4),(0.5,4),(0.5,8),(0.7,8)]:
        for w in ([0.5,0.75] if var else [0.5]):
            print(var,w,round(br(probs(tr,var,w),tr.y),5),round(br(probs(te,var,w),te.y),5),flush=True)
