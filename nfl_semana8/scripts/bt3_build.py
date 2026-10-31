import sys; sys.path.insert(0,'/home/user/scripts')
import pandas as pd, numpy as np
from props_model import *
from model2 import team_shares, vacated, PRES
B=pd.read_pickle('/home/user/data/bt2_raw.pkl')
cache={}; feats={}
for (t,pid),grp in B.groupby(['week','pid']):
    r=pw[(pw.player_id==pid)&(pw.week==t)].iloc[0]
    team=r.team
    if (team,t) not in cache: cache[(team,t)]=team_shares(team,t)
    sh=cache[(team,t)]
    vt,vc=vacated(team,r.game_id,pid,sh)
    prior=pw[(pw.player_id==pid)&(pw.week<t)&(pw.team==team)]
    hv=[vacated(team,g,pid,sh) for g in prior.game_id]
    ht=np.mean([h[0] for h in hv]) if hv else 0; hc=np.mean([h[1] for h in hv]) if hv else 0
    feats[(t,pid)]=(vt-ht,vc-hc)
B['dvt']=[feats[(a,b)][0] for a,b in zip(B.week,B.pid)]; B['dvc']=[feats[(a,b)][1] for a,b in zip(B.week,B.pid)]
B.to_pickle('/home/user/data/bt3_raw.pkl'); print(B[['dvt','dvc']].describe().round(3).to_string()); print((B.drop_duplicates(['week','pid']).dvt.abs()>0.05).mean())
