# Búsqueda de modelo: evaluador vectorizado + búsqueda aleatoria (etapa 1) + validación por semana con calibración (etapa 2).
import sys; sys.path.insert(0,'/home/user/scripts')
import pandas as pd, numpy as np, json, time
from scipy import stats as st
from scipy.optimize import minimize
B=pd.read_pickle('/home/user/data/bt7_raw.pkl').reset_index(drop=True)
y=B.y.values.astype(float); L=B.L.values.astype(float); kind=B.kind.values; pos=B.pos.values; c=B.c.values
mu0=B.mu0.values; mean=B['mean'].values; cv=np.where((mu0>0)&(kind!='td'),B.sd0.values/np.where(mu0>0,mu0,1),0)
grp=B.grp.values; dol=(B.olnow-B.olh).values; gap=B.gap.values; home=B.home.values; week=B.week.values
isR=np.isin(c,['carries','rushing_yards']); isRec=np.isin(c,['receptions','receiving_yards']); isTD=kind=='td'; isPassQB=np.isin(c,['passing_yards','completions','passing_tds'])
isRBtd=(c=='td_any')&(pos=='RB')
G={'rush':isR,'td':isTD,'pass':~isR&~isTD}
PRI=['']+['_'+t for t in ['03_4','05_4','05_8','07_8','07_12','09_8','09_12','10_16','05_12']]
EW={h:B[f'ew{h}'].values for h in [2,3,4,6]}
k=np.ceil(L-1e-9)
def probs(p):
    base=np.where(mean>0, mu0*((1-p['A'])+p['A']*EW[p['H']]/np.where(mean>0,mean,1)), mu0)
    dr=B['dr'+p['pri']].values; df=B[('dfaced' if p['pri']=='' else 'df'+p['pri'])].values
    ratio=np.where((dr>0)&(df>0),dr/np.where(df>0,df,1),1)
    w=np.where(G['rush'],p['wr'],np.where(G['td'],p['wt'],p['wp']))
    f=ratio**w
    f*=np.where(grp=='rush',np.maximum(0.5,1+p['bru']*dol),np.where(grp=='mix',np.maximum(0.5,1+0.5*p['bru']*dol),1))
    dvt=B.dvt_w.values if p['dvw'] else B.dvt.values; dvc=B.dvc_w.values if p['dvw'] else B.dvc.values
    ft=np.clip(1/(1-dvt),0.7,1.5)**p['gt']; fc=np.clip(1/(1-np.minimum(dvc,0.6)),0.7,1.5)**p['gc']
    nq=pos!='QB'
    f*=np.where(nq&(isRec|(c=='td_any')),ft,1)*np.where(nq&(isR|isRBtd),fc,1)
    g10=np.clip(gap,-20,20)/10
    f*=np.where(isR,1+p['bg']*g10,np.where(isRec|isPassQB,1-p['bg']*g10,1))
    f*=1+p['bh']*(home-0.5)*2
    mu=np.maximum(base*f,0)
    out=np.zeros(len(B))
    zero=mu<=1e-9
    # continuas: gamma
    m=(kind=='cont')&~zero
    sd=cv*mu*p['ic']; v=np.maximum(sd**2,1e-9)
    out[m]=st.gamma.sf(L[m],a=(mu[m]**2/v[m]),scale=v[m]/mu[m])
    # conteos
    m2=(kind=='count')&~zero
    v2=(cv*mu*p['in'])**2
    nb=m2&(v2>mu*1.0001); bi=m2&(v2<mu*0.9999); po=m2&~nb&~bi
    r=mu[nb]**2/(v2[nb]-mu[nb]); out[nb]=st.nbinom.sf(k[nb]-1,r,r/(r+mu[nb]))
    nn=np.maximum(np.ceil(mu[bi]+1e-9),np.round(mu[bi]**2/(mu[bi]-v2[bi]))); out[bi]=st.binom.sf(k[bi]-1,nn,mu[bi]/nn)
    out[po]=st.poisson.sf(k[po]-1,mu[po])
    m3=isTD&~zero; out[m3]=st.poisson.sf(k[m3]-1,mu[m3])
    out[zero]=(L[zero]<=0).astype(float)
    return np.clip(out,0,1)
br=lambda pp,m=None: float(np.mean((pp-y)**2)) if m is None else float(np.mean((pp[m]-y[m])**2))
lg=lambda q: np.log(np.clip(q,1e-4,1-1e-4)/(1-np.clip(q,1e-4,1-1e-4))); sig=lambda z:1/(1+np.exp(-z))
def calfit(pp,m):
    out={}
    for kd in ['cont','count','td']:
        mm=m&(kind==kd); x=lg(pp[mm]); yy=y[mm]
        f=lambda ab: np.mean((sig(ab[0]+ab[1]*x)-yy)**2); out[kd]=minimize(f,[0.05,0.95],method='Nelder-Mead',options=dict(xatol=1e-4,fatol=1e-8)).x
    return out
def calapply(pp,cal):
    q=pp.copy()
    for kd,(a,b) in cal.items(): mm=kind==kd; q[mm]=sig(a+b*lg(pp[mm]))
    return q
def lowo(pp):
    q=np.zeros(len(pp))
    for wk in [4,5,6,7,8]:
        tr=week!=wk; cal=calfit(pp,tr); qa=calapply(pp,cal); q[week==wk]=qa[week==wk]
    return br(q)
def holdout(pp):
    cal=calfit(pp,week<=6); return br(calapply(pp,cal),week>=7)
SPACE=dict(pri=PRI,wr=[0.3,0.5,0.65,0.8,1.0],wp=[0.3,0.5,0.65,0.8,1.0],wt=[0.3,0.5,0.65,0.8,1.0],H=[2,3,4,6],A=[0,0.25,0.5,0.75,1.0],
           bru=[0,-0.02,-0.04,-0.06],gt=[0,0.25,0.5],gc=[0,0.5,0.75,1.0],dvw=[False,True],ic=[0.9,1.0,1.1,1.2],in_=[0.9,1.0,1.1],bg=[0,0.02,0.04,0.06],bh=[0,0.02,0.04])
BASE=dict(pri='_07_8',wr=0.65,wp=0.65,wt=0.65,H=4,A=0.5,bru=-0.04,gt=0.25,gc=1.0,dvw=True,ic=1.0,in_=1.0,bg=0,bh=0)
def fix(p): q=dict(p); q['in']=q.pop('in_'); return q
if __name__=='__main__':
    rng=np.random.default_rng(7); N=int(sys.argv[1]) if len(sys.argv)>1 else 20000
    t0=time.time(); res=[]
    pb=probs(fix(BASE)); res.append(dict(BASE,raw=br(pb)))
    seen=set()
    for i in range(N):
        p={kk:vv[rng.integers(len(vv))] for kk,vv in SPACE.items()}
        key=tuple(p.values())
        if key in seen: continue
        seen.add(key)
        res.append(dict(p,raw=br(probs(fix(p)))))
        if i%2000==0: print(i,round(time.time()-t0),flush=True)
    R=pd.DataFrame(res).sort_values('raw'); R.to_pickle('/home/user/data/search_stage1.pkl')
    print('etapa1', len(R), round(time.time()-t0)); print(R.head(10).to_string())
    # etapa 2: coordenada alrededor de los mejores + validación por semana
    top=R.head(300).to_dict('records')
    S=[]
    for p in top:
        p={kk:p[kk] for kk in SPACE}; pp=probs(fix(p)); S.append(dict(p,lowo=lowo(pp),hold=holdout(pp)))
    pp=probs(fix(BASE)); S.append(dict(BASE,lowo=lowo(pp),hold=holdout(pp),tag='v4'))
    S=pd.DataFrame(S).sort_values('lowo'); S.to_pickle('/home/user/data/search_stage2.pkl')
    print('etapa2', round(time.time()-t0)); print(S.head(15).to_string()); print(S[S.get('tag')=='v4'].to_string())
