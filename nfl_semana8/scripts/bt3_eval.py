import sys; sys.path.insert(0,'/home/user/scripts')
import pandas as pd, numpy as np
from props_model import dist_params, prob_ge
B=pd.read_pickle('/home/user/data/bt3_raw.pkl')
REC={'receptions','receiving_yards'}; RUSH={'carries','rushing_yards'}
def probs(B,w=0.5,bru=-0.04,gt=0.0,gc=0.0):
    out=np.empty(len(B))
    for i,r in enumerate(B.itertuples()):
        f=(r.dr/r.dfaced)**w if r.dfaced>0 and r.dr>0 else 1
        if r.grp=='rush': f*=max(0.5,1+bru*(r.olnow-r.olh))
        elif r.grp=='mix': f*=max(0.5,1+0.5*bru*(r.olnow-r.olh))
        if r.pos!='QB':
            if r.c in REC or r.c=='td_any': f*=min(1.5,max(0.7,1/(1-r.dvt)))**gt
            if r.c in RUSH or (r.c=='td_any' and r.pos=='RB'): f*=min(1.5,max(0.7,1/(1-min(r.dvc,0.6))))**gc
        mu=r.mu0*f
        d=dict(kind='td',mu=mu) if r.kind=='td' else dict(kind=r.kind,mu=mu,sd=r.sd0*f)
        out[i]=prob_ge(dist_params(d),r.L)
    return out
br=lambda p,y: float(np.mean((p-y)**2))
tr=B[B.week<=6]; te=B[B.week>=7]
if __name__=='__main__':
  R=[]
  for gt,gc in [(0,0),(0.25,0),(0.5,0),(0.75,0),(1,0),(0,0.25),(0,0.5),(0,0.75),(0,1),(0.5,0.5)]:
    R.append(dict(gt=gt,gc=gc,tr=br(probs(tr,gt=gt,gc=gc),tr.y),te=br(probs(te,gt=gt,gc=gc),te.y),all=br(probs(B,gt=gt,gc=gc),B.y)))
  print(pd.DataFrame(R).round(5).to_string())
