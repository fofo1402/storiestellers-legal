import sys; sys.path.insert(0,'/home/user/scripts')
import pandas as pd, numpy as np, math, itertools
from props_model import dist_params, prob_ge
B=pd.read_pickle('/home/user/data/bt2_raw.pkl')
def probs(B,mode,w,bol=0.0,bru=None):
    out=np.empty(len(B))
    for i,r in enumerate(B.itertuples()):
        if mode=='old': f=1+w*(r.rv/r.sos-1) if r.sos>0 else 1
        elif mode=='new': f=(r.dr/r.dfaced)**w if r.dfaced>0 and r.dr>0 else 1
        else: f=1
        if bol or bru:
            b=bol if r.grp=='pass' else ((bru if bru is not None else bol) if r.grp=='rush' else 0.5*(bol+(bru if bru is not None else bol)))
            f*=max(0.5,1+b*(r.olnow-r.olh))
        mu=r.mu0*f
        d=dict(kind='td',mu=mu) if r.kind=='td' else dict(kind=r.kind,mu=mu,sd=r.sd0*f)
        out[i]=prob_ge(dist_params(d),r.L)
    return out
br=lambda p,y: float(np.mean((p-y)**2))
tr=B[B.week<=6]; te=B[B.week>=7]
if __name__=='__main__':
    R=[]
    R.append(dict(mode='none',w=0,bol=0,tr=br(probs(tr,'none',0),tr.y),te=br(probs(te,'none',0),te.y)))
    for w in [0.15,0.3,0.45,0.6]:
        R.append(dict(mode='old',w=w,bol=0,tr=br(probs(tr,'old',w),tr.y),te=br(probs(te,'old',w),te.y)))
    for w in [0.15,0.3,0.45,0.6,0.8,1.0]:
        R.append(dict(mode='new',w=w,bol=0,tr=br(probs(tr,'new',w),tr.y),te=br(probs(te,'new',w),te.y)))
    print(pd.DataFrame(R).round(5).to_string())
    print('olnow dist', B.drop_duplicates(['week','pid']).olnow.value_counts().to_dict())
