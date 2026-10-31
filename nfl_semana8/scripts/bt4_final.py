import sys; sys.path.insert(0,'/home/user/scripts')
from bt4_eval import *
from scipy.optimize import minimize
import json
H,A=4,0.5
lg=lambda p: np.log(np.clip(p,1e-4,1-1e-4)/(1-np.clip(p,1e-4,1-1e-4))); sig=lambda z:1/(1+np.exp(-z))
B2=B.copy(); B2['p']=probs(B2,H,A)
def fit(x):
    f=lambda ab: np.mean((sig(ab[0]+ab[1]*lg(x.p.values))-x.y.values)**2)
    return minimize(f,[0.05,0.95],method='Nelder-Mead',options=dict(xatol=1e-5,fatol=1e-8)).x
t2=B2[B2.week<=6]; e2=B2[B2.week>=7].copy()
ct={k:fit(t2[t2.kind==k]) for k in ['cont','count','td']}
e2['pc']=[sig(ct[k][0]+ct[k][1]*lg(p)) for k,p in zip(e2.kind,e2.p)]
none=br(probs(te,None,1,w=0,bru=0,gt=0,gc=0),te.y)
print('TEST 7-8: sin ajuste %.4f | v3 crudo %.4f calibrado %.4f'%(none,br(e2.p,e2.y),br(e2.pc,e2.y)))
bins=[0,0.2,0.4,0.6,0.8,1.0001]; names=['Muy difícil','Difícil','Parejo','Fácil','Muy fácil']
t=e2.groupby(pd.cut(e2.pc,bins,right=False,labels=names),observed=False).agg(n=('y','size'),prob=('pc','mean'),acierto=('y','mean')).round(3); print(t.to_string())
ca={k:[float(v) for v in fit(B2[B2.kind==k])] for k in ['cont','count','td']}
B2['pca']=[sig(ca[k][0]+ca[k][1]*lg(p)) for k,p in zip(B2.kind,B2.p)]
ta=B2.groupby(pd.cut(B2.pca,bins,right=False,labels=names),observed=False).agg(n=('y','size'),acierto=('y','mean')).round(3); print(ta.to_string())
old=json.load(open('/home/user/data/model2_params.json'))
json.dump(dict(w=0.5,bru=-0.04,gt=0.25,gc=1.0,rec_h=H,rec_a=A,cal=ca,test=dict(sin_ajuste=none,v2=old['test']['v2'],v3=br(e2.pc,e2.y),anterior=0.1980),
  calib={str(k):dict(n=int(v.n),acierto=float(v.acierto)) for k,v in ta.iterrows()}),open('/home/user/data/model3_params.json','w'),indent=1)
print(ca)
