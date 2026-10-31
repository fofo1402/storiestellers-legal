# Modelo de probabilidad por estadística: P(alcanzar o superar una línea elegida por el usuario)
import pandas as pd, numpy as np, re, unicodedata, math
from scipy import stats as st
D='/home/user/raw/nflverse/'; O='/home/user/data/'
W=0.6; K_SD=4; K_TDP=4; K_TDD=6
pw=pd.read_csv(O+'player_week.csv',low_memory=False)
pw=pw[pw.position.isin(['QB','RB','FB','WR','TE'])].copy()
pw['pgrp']=pw.position.replace({'FB':'RB'})
for c in ['rushing_tds','receiving_tds','passing_tds','completions','attempts','carries','targets','receptions','rushing_yards','receiving_yards','passing_yards']: pw[c]=pw[c].fillna(0)
pw['td_any']=pw.rushing_tds+pw.receiving_tds
res=pd.read_csv(O+'results.csv')
STATS={'QB':[('pass_yds','passing_yards','Yardas de pase','cont'),('cmp','completions','Pases completos','count'),('pass_td','passing_tds','TD de pase','td')],
 'RB':[('rush_yds','rushing_yards','Yardas por tierra','cont'),('car','carries','Acarreos','count'),('rec','receptions','Recepciones','count'),('rec_yds','receiving_yards','Yardas recibidas','cont'),('td','td_any','TD (tierra o recepción)','td')],
 'WR':[('rec_yds','receiving_yards','Yardas recibidas','cont'),('rec','receptions','Recepciones','count'),('td','td_any','TD (recepción o tierra)','td')],
 'TE':[('rec_yds','receiving_yards','Yardas recibidas','cont'),('rec','receptions','Recepciones','count'),('td','td_any','TD (recepción o tierra)','td')]}
COLS=['passing_yards','completions','passing_tds','attempts','rushing_yards','carries','receptions','targets','receiving_yards','td_any']
def norm(n):
    n=unicodedata.normalize('NFKD',str(n)).encode('ascii','ignore').decode().lower(); n=re.sub(r'[^a-z ]','',n); n=re.sub(r'\b(jr|sr|ii|iii|iv|v)\b','',n); return ' '.join(n.split())
sc=pd.read_csv(D+'snap_counts_2026.csv',low_memory=False); sc=sc[(sc.game_type=='REG')&(sc.offense_snaps>0)&sc.game_id.isin(res.game_id)]
pl=pd.read_csv(D+'players.csv',low_memory=False)[['gsis_id','pfr_id']].dropna()
sc=sc.merge(pl.rename(columns={'pfr_id':'pfr_player_id'}),on='pfr_player_id',how='left'); sc['k']=sc.player.map(norm)
pw['k']=pw.player_display_name.map(norm)
RES_BY=res.set_index(['game_id','team'])
def player_games(pid,pos,teams,maxweek=99):
    x=pw[(pw.player_id==pid)&(pw.week<maxweek)]
    if pos=='QB': x=x[x.attempts>=15]
    rows={r.game_id:r for r in x.itertuples()}
    gids=set(rows)
    if pos!='QB':
        k=norm(x.player_display_name.iloc[0]) if len(x) else None
        s=sc[((sc.gsis_id==pid)|(sc.gsis_id.isna()&(sc.k==k)))&sc.team.isin(teams)&(sc.week<maxweek)]
        gids|=set(s.game_id)
    out=[]
    for g in gids:
        tm=[t for t in teams if (g,t) in RES_BY.index]
        if not tm: continue
        rr=RES_BY.loc[(g,tm[0])]; r=rows.get(g)
        vals={c:(float(getattr(r,c)) if r is not None else 0.0) for c in COLS}
        out.append(dict(game_id=g,week=int(rr.week),opp=rr.opp,ha=rr.ha,vals=vals,has_stat=r is not None))
    return sorted(out,key=lambda d:d['week'])
DG=pw.groupby(['opponent_team','game_id','pgrp'])[COLS].sum().reset_index().rename(columns={'opponent_team':'def_'})
class Ctx:
    def __init__(s,maxweek=99):
        g=res[res.week<maxweek][['team','game_id']].rename(columns={'team':'def_'})
        s.DT={p:g.merge(DG[DG.pgrp==p].drop(columns='pgrp'),on=['def_','game_id'],how='left').fillna(0) for p in STATS}
        s.lg={p:{c:s.DT[p][c].mean() for c in COLS} for p in STATS}
        s.sum={p:s.DT[p].groupby('def_')[COLS].sum() for p in STATS}; s.cnt={p:s.DT[p].groupby('def_').size() for p in STATS}
        s.byg={p:s.DT[p].set_index(['def_','game_id']) for p in STATS}
        pv=pw[pw.week<maxweek]; s.pri={}
        rb=pv[pv.pgrp=='RB']; s.pri['RB_car']=rb.rushing_tds.sum()/rb.carries.sum(); s.pri['RB_tgt']=rb.receiving_tds.sum()/rb.targets.sum()
        for p in ['WR','TE']:
            x=pv[pv.pgrp==p]; s.pri[p+'_tgt']=x.td_any.sum()/x.targets.sum()
        q=pv[(pv.pgrp=='QB')&(pv.attempts>=15)]; s.pri['QB_att']=q.passing_tds.sum()/q.attempts.sum()
    def allowed(s,p,c,team,excl=None,td=False):
        S=s.sum[p].loc[team,c]; n=s.cnt[p].loc[team]
        if excl is not None and (team,excl) in s.byg[p].index: S-=s.byg[p].loc[(team,excl),c]; n-=1
        if td: return (S+K_TDD*s.lg[p][c])/(n+K_TDD)
        return S/n
    def rank_table(s):
        out={}
        for p in STATS:
            pg=s.sum[p].div(s.cnt[p],axis=0)
            out[p]={c:pg[c].rank(ascending=False,method='min').astype(int).to_dict() for c in COLS}
            out[p+'_pg']={c:pg[c].to_dict() for c in COLS}
        return out
def cv_priors(pg_list):
    acc={}
    for pos,games in pg_list:
        if len(games)<4: continue
        for key,c,_,kind in STATS[pos]:
            if kind=='td': continue
            xs=np.array([g['vals'][c] for g in games]); m=xs.mean()
            if m<=0: continue
            acc.setdefault((pos,key),[]).append(xs.std(ddof=1)/m)
    return {k:float(np.median(v)) for k,v in acc.items()}
def params(pos,games,rival,ctx,cv0,w=W):
    n=len(games); out={}
    sg=[g for g in games if g['has_stat']] or games
    for key,c,label,kind in STATS[pos]:
        xs=np.array([g['vals'][c] for g in games]); m=float(xs.mean())
        td=(kind=='td')
        sos=float(np.mean([ctx.allowed(pos,c,g['opp'],g['game_id'],td) for g in sg]))
        rv=float(ctx.allowed(pos,c,rival,None,td))
        f=1+w*(rv/sos-1) if sos>0 else 1.0
        d=dict(key=key,label=label,kind=kind,n=n,mean_raw=m,rival_allows=rv,sos=sos,factor=f)
        if td:
            opp=np.mean([g['vals']['attempts'] for g in games]) if pos=='QB' else None
            if pos=='QB': lam0=ctx.pri['QB_att']*opp
            elif pos=='RB': lam0=ctx.pri['RB_car']*np.mean([g['vals']['carries'] for g in games])+ctx.pri['RB_tgt']*np.mean([g['vals']['targets'] for g in games])
            else: lam0=ctx.pri[pos+'_tgt']*np.mean([g['vals']['targets'] for g in games])
            lamp=(xs.sum()+K_TDP*lam0)/(n+K_TDP)
            d.update(lam_prior=float(lam0),lam_player=float(lamp),mu=float(lamp*f))
        else:
            s2=float(xs.var(ddof=1)) if n>1 else 0.0
            c0=cv0.get((pos,key),0.6)
            v=((n-1)*s2+K_SD*(c0*m)**2)/((n-1)+K_SD)
            d.update(mu=float(m*f),sd=float(math.sqrt(v)*f),cv0=c0)
        out[key]=d
    return out
def dist_params(d):
    """parámetros finales de la distribución (lo que usará la app)."""
    k=d['kind']; mu=d['mu']
    if k=='td': return dict(dist='poisson',lam=mu)
    sd=d['sd']
    if mu<=0 or sd<=0: return dict(dist='zero')
    v=sd*sd
    if k=='cont': return dict(dist='gamma',shape=mu*mu/v,scale=v/mu)
    if v>mu*1.0001: r=mu*mu/(v-mu); return dict(dist='negbin',r=r,p=r/(r+mu))
    if v<mu*0.9999:
        nb=max(math.ceil(mu+1e-9),round(mu*mu/(mu-v))); return dict(dist='binom',n=int(nb),p=mu/nb)
    return dict(dist='poisson',lam=mu)
def prob_ge(dp,L):
    t=dp['dist']
    if t=='zero': return 1.0 if L<=0 else 0.0
    if t=='gamma': return float(st.gamma.sf(L,dp['shape'],scale=dp['scale'])) if L>0 else 1.0
    k=math.ceil(L-1e-9)
    if k<=0: return 1.0
    if t=='poisson': return float(st.poisson.sf(k-1,dp['lam']))
    if t=='negbin': return float(st.nbinom.sf(k-1,dp['r'],dp['p']))
    if t=='binom': return float(st.binom.sf(k-1,dp['n'],dp['p']))
LABELS=[(0.80,'Muy fácil'),(0.60,'Fácil'),(0.40,'Parejo'),(0.20,'Difícil'),(0.0,'Muy difícil')]
def label(p):
    for th,l in LABELS:
        if p>=th: return l
