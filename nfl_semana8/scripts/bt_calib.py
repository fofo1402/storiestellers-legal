import sys; sys.path.insert(0,'/home/user/scripts')
import pandas as pd, numpy as np
from bt_eval import probs, B, br
from scipy.optimize import minimize
lg=lambda p: np.log(np.clip(p,1e-4,1-1e-4)/(1-np.clip(p,1e-4,1-1e-4)))
sig=lambda z: 1/(1+np.exp(-z))
bins=[0,0.2,0.4,0.6,0.8,1.0001]; names=['Muy difícil','Difícil','Parejo','Fácil','Muy fácil']
out={}
for w in [0.15,0.3]:
    tr=B[B.week<=6].copy(); te=B[B.week>=7].copy()
    tr['p']=probs(tr,w,1.0); te['p']=probs(te,w,1.0)
    cal={}
    for kind in ['cont','count','td']:
        x=tr[tr.kind==kind]
        f=lambda ab: np.mean((sig(ab[0]+ab[1]*lg(x.p.values))-x.y.values)**2)
        cal[kind]=minimize(f,[0,1],method='Nelder-Mead').x
    for d in (tr,te): d['pc']=[sig(cal[k][0]+cal[k][1]*lg(p)) for k,p in zip(d.kind,d.p)]
    print(f'w={w} test brier raw {br(te.p,te.y):.4f} calibrado {br(te.pc,te.y):.4f}; train raw {br(tr.p,tr.y):.4f} cal {br(tr.pc,tr.y):.4f}')
    print({k:np.round(v,3).tolist() for k,v in cal.items()})
    for col in ['p','pc']:
        t=te.groupby(pd.cut(te[col],bins,right=False,labels=names),observed=False).agg(n=('y','size'),prob=(col,'mean'),acierto=('y','mean')).round(3)
        print(col); print(t.to_string())
    out[w]=(cal,te)
import pickle; pickle.dump({w:out[w][0] for w in out},open('/home/user/data/calib.pkl','wb'))
