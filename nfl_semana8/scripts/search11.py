# ¿Acercarse al mercado mejora? Puntos esperados del equipo (de la casa) y spread como factores, sobre el modelo final.
import sys; sys.path.insert(0,'/home/user/scripts')
import search as S, numpy as np, pandas as pd, time
import search10 as T
B11=pd.read_pickle('/home/user/data/bt11_raw.pkl').reset_index(drop=True)
assert (B11.pid.values==S.B.pid.values).all()
for K in [800,1600,100000]: T.U[K]=(B11[f'u{K}_m'].values,B11[f'u{K}_e'].values)
imp_r=np.nan_to_num(B11.imp_now.values/B11.imp_hist.values,nan=1.0); dspr=np.nan_to_num(B11.spr_now.values-B11.spr_hist.values)
skip=(S.B.pos.values=='QB')&(S.B.c.values=='passing_yards')
isR=np.isin(S.c,['carries','rushing_yards']); isPass=np.isin(S.c,['passing_yards','completions','receptions','receiving_yards'])
def probs_m(p):
    base=np.where(S.mean>0, S.mu0*((1-p['A'])+p['A']*S.EW[p['H']]/np.where(S.mean>0,S.mean,1)), S.mu0)
    um,ue=T.U[p['K']]; has=~np.isnan(um)&~skip; vol=(1-p['A'])*np.where(has,um,0)+p['A']*np.where(has,ue,0)
    base=np.where(has&(vol>0),(1-p['u'])*base+p['u']*vol,base)
    tdok=T.isTD&~np.isnan(T.TDV); base=np.where(tdok,(1-p['tb'])*base+p['tb']*np.nan_to_num(T.TDV),base)
    fm=np.where(T.isTD,imp_r**p['bit'],imp_r**p['biy'])
    fm*=np.where(isR,np.maximum(0.5,1+p['bsr']*dspr/10),np.where(isPass,np.maximum(0.5,1-p['bsp']*dspr/10),1))
    return S.probs(p,base*fm)
FIN=pd.read_pickle('/home/user/data/best_final.pkl'); FIN=dict(FIN,bit=0.0,biy=0.0,bsr=0.0,bsp=0.0)
SP={k:v for k,v in T.SP.items()}; SP['K']=[400,800,1600,100000]
SP.update(bit=[0,0.5,1.0,1.5,2.0],biy=[0,0.25,0.5,0.75,1.0],bsr=[0,0.05,0.1,0.15],bsp=[0,0.05,0.1,0.15])
cache={}
def score(p):
    key=tuple(p[k] for k in SP)
    if key not in cache: cache[key]=S.lowo(probs_m(S.fix(p)))
    return cache[key]
if __name__=='__main__':
    t0=time.time(); print('final sin mercado',round(score(FIN),5),flush=True)
    for k,vals in [('bit',SP['bit']),('biy',SP['biy']),('bsr',SP['bsr']),('bsp',SP['bsp'])]:
        print(k,[(v,round(score(dict(FIN,**{k:v})),5)) for v in vals],flush=True)
    cur=dict(FIN); cs=score(cur); imp=True
    while imp:
        imp=False
        for k,vals in SP.items():
            for v in vals:
                if v==cur[k]: continue
                q=dict(cur); q[k]=v; sc=score(q)
                if sc<cs-1e-7: cur,cs,imp=q,sc,True
    print('MEJOR',round(cs,5),{k:cur[k] for k in ['bit','biy','bsr','bsp','wr','wp','wt','u','K','tb','A','H','pri']},round(time.time()-t0))
    pd.to_pickle(cur,'/home/user/data/best_market.pkl')
