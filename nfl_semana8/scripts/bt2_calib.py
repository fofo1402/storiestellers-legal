import sys; sys.path.insert(0,'/home/user/scripts')
from bt2_eval import *
from scipy.optimize import minimize
import pickle, json
W2=0.5; BRU=-0.04
lg=lambda p: np.log(np.clip(p,1e-4,1-1e-4)/(1-np.clip(p,1e-4,1-1e-4))); sig=lambda z:1/(1+np.exp(-z))
B=B.copy(); B['p']=probs(B,'new',W2,0.0,BRU); B['p_old']=probs(B,'old',0.3)
def fit(x):
    f=lambda ab: np.mean((sig(ab[0]+ab[1]*lg(x.p.values))-x.y.values)**2)
    return minimize(f,[0,1],method='Nelder-Mead').x
tr=B[B.week<=6]; te=B[B.week>=7].copy()
cal_tr={k:fit(tr[tr.kind==k]) for k in ['cont','count','td']}
te['pc']=[sig(cal_tr[k][0]+cal_tr[k][1]*lg(p)) for k,p in zip(te.kind,te.p)]
old=pickle.load(open('/home/user/data/calib.pkl','rb'))[0.3] if __import__('os').path.exists('/home/user/data/calib.pkl') else None
print('TEST semanas 7-8: v2 crudo %.4f  v2 calibrado %.4f | modelo anterior crudo %.4f'%(br(te.p,te.y),br(te.pc,te.y),br(te.p_old,te.y)))
bins=[0,0.2,0.4,0.6,0.8,1.0001]; names=['Muy difícil','Difícil','Parejo','Fácil','Muy fácil']
t=te.groupby(pd.cut(te.pc,bins,right=False,labels=names),observed=False).agg(n=('y','size'),prob=('pc','mean'),acierto=('y','mean')).round(3)
print(t.to_string())
cal_all={k:[float(v) for v in fit(B[B.kind==k])] for k in ['cont','count','td']}
B['pca']=[sig(cal_all[k][0]+cal_all[k][1]*lg(p)) for k,p in zip(B.kind,B.p)]
ta=B.groupby(pd.cut(B.pca,bins,right=False,labels=names),observed=False).agg(n=('y','size'),acierto=('y','mean')).round(3)
print('calibración final (semanas 4-8):'); print(ta.to_string())
json.dump(dict(w=W2,bru=BRU,cal=cal_all,test=dict(brier_v2=br(te.pc,te.y),brier_old_raw=br(te.p_old,te.y),brier_none=br(probs(te,'none',0),te.y)),
   calib_tabla={str(k):dict(n=int(v.n),acierto=float(v.acierto)) for k,v in ta.iterrows()},
   calib_test={str(k):dict(n=int(v.n),acierto=float(v.acierto)) for k,v in t.iterrows()}),open('/home/user/data/model2_params.json','w'),indent=1)
print(cal_all)
