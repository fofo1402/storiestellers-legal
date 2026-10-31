import sys; sys.path.insert(0,'/home/user/scripts')
import pandas as pd, numpy as np, pickle, time
from props_model import *
from model2 import ratings_2025, RatingsP
PRI=ratings_2025(); pickle.dump(PRI,open('/home/user/data/prior2025.pkl','wb'))
B=pd.read_pickle('/home/user/data/bt5_raw.pkl')
VAR=[(0.3,4),(0.5,4),(0.5,8),(0.7,8)]
t0=time.time(); feats={}
for t in [4,5,6,7,8]:
    RS={v:RatingsP(t,PRI,rho=v[0],kp=v[1]) for v in VAR}
    sub=B[B.week==t]
    for pid,grp in sub.groupby('pid'):
        r=pw[(pw.player_id==pid)&(pw.week==t)].iloc[0]; pos=r.pgrp
        teams=list(pd.unique(pw[(pw.player_id==pid)&(pw.week<t)].team))
        games=player_games(pid,pos,teams,maxweek=t)
        for c in grp.c.unique():
            for v,R in RS.items():
                feats[(t,pid,c,v)]=(R.d(pos,c,r.opponent_team), float(np.mean([R.d(pos,c,g['opp']) for g in games])))
    print(t,round(time.time()-t0),flush=True)
for v in VAR:
    B[f'dr_{v[0]}_{v[1]}']=[feats[(a,b,c,v)][0] for a,b,c in zip(B.week,B.pid,B.c)]
    B[f'df_{v[0]}_{v[1]}']=[feats[(a,b,c,v)][1] for a,b,c in zip(B.week,B.pid,B.c)]
B.to_pickle('/home/user/data/bt6_raw.pkl'); print('ok')
