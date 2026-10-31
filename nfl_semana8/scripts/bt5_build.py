# Compañeros ausentes medidos contra la historia ponderada igual que la forma reciente (evita contar dos veces una ausencia que ya está en sus últimos juegos).
import sys; sys.path.insert(0,'/home/user/scripts')
import pandas as pd, numpy as np
from props_model import *
from model2 import team_shares, vacated
B=pd.read_pickle('/home/user/data/bt4_raw.pkl')
H,A=4,0.5
cache={}; feats={}
for (t,pid),grp in B.groupby(['week','pid']):
    r=pw[(pw.player_id==pid)&(pw.week==t)].iloc[0]; team=r.team
    if (team,t) not in cache: cache[(team,t)]=team_shares(team,t)
    sh=cache[(team,t)]
    vt,vc=vacated(team,r.game_id,pid,sh)
    prior=pw[(pw.player_id==pid)&(pw.week<t)&(pw.team==team)].sort_values('week')
    hv=np.array([vacated(team,g,pid,sh) for g in prior.game_id]) if len(prior) else np.zeros((0,2))
    if len(hv):
        n=len(hv); w=0.5**((n-1-np.arange(n))/H); w=(1-A)/n+A*w/w.sum()
        ht,hc=(w[:,None]*hv).sum(0)
    else: ht=hc=0
    feats[(t,pid)]=(vt-ht,vc-hc)
B['dvt_w']=[feats[(a,b)][0] for a,b in zip(B.week,B.pid)]; B['dvc_w']=[feats[(a,b)][1] for a,b in zip(B.week,B.pid)]
B.to_pickle('/home/user/data/bt5_raw.pkl'); print(B[['dvt','dvt_w','dvc','dvc_w']].describe().round(3).to_string())
