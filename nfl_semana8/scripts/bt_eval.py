import sys; sys.path.insert(0,'/home/user/scripts')
import pandas as pd, numpy as np, math
from props_model import dist_params, prob_ge
B=pd.read_pickle('/home/user/data/bt_raw.pkl')
def probs(B,w,infl,inflc=None):
    out=np.empty(len(B))
    for i,r in enumerate(B.itertuples()):
        f=1+w*(r.rv/r.sos-1) if r.sos>0 else 1
        k=r.kind; mu=r.mu0*f
        if k=='td': d=dict(kind='td',mu=mu)
        else:
            m_inf=infl if k=='cont' else (inflc if inflc is not None else infl)
            d=dict(kind=k,mu=mu,sd=r.sd0*f*m_inf)
        out[i]=prob_ge(dist_params(d),r.L)
    return out
br=lambda p,y: float(np.mean((p-y)**2))
tr=B[B.week<=6]; te=B[B.week>=7]
res=[]
for w in [0,0.15,0.3,0.45,0.6]:
    for infl in [1.0,1.15,1.3,1.45]:
        ptr=probs(tr,w,infl); pte=probs(te,w,infl)
        res.append(dict(w=w,infl=infl,brier_tr=br(ptr,tr.y),brier_te=br(pte,te.y)))
R=pd.DataFrame(res); print(R.round(4).to_string()); R.to_csv('/home/user/data/bt_grid.csv',index=False)
