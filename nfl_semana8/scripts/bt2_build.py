import sys; sys.path.insert(0,'/home/user/scripts')
import pandas as pd, numpy as np, math, time
from props_model import *
from model2 import Ratings, ol_out_cached, OLGRP
t0=time.time(); rows=[]
for t in [4,5,6,7,8]:
    ctx=Ctx(t); R=Ratings(t); cur=pw[pw.week==t]; cands=[]
    for pid,grp in cur.groupby('player_id'):
        r=grp.iloc[0]; pos=r.pgrp
        if pos=='QB' and r.attempts<15: continue
        prior=pw[(pw.player_id==pid)&(pw.week<t)]; teams=list(pd.unique(prior.team))
        if r.team not in teams: continue
        games=player_games(pid,pos,teams,maxweek=t)
        if len(games)<3: continue
        cands.append((pid,pos,r,games))
    cv0=cv_priors([(c[1],c[3]) for c in cands])
    for pid,pos,r,games in cands:
        P=params(pos,games,r.opponent_team,ctx,cv0,0.0)
        olnow=ol_out_cached(r.team,r.game_id,t)
        # equipo del jugador en cada juego previo
        tm_of={g['game_id']:(res[(res.game_id==g['game_id'])&(res.opp==g['opp'])].team.iloc[0]) for g in games}
        olh=np.mean([ol_out_cached(tm_of[g['game_id']],g['game_id'],t) for g in games])
        for key,c,lab,kind in STATS[pos]:
            d=P[key]; m=d['mean_raw']
            if kind=='td': lines=[1] if pos!='QB' else [1,2,3]
            else:
                if m<=0: continue
                lines=sorted({(math.floor(m*q)+0.5) if kind=='cont' else max(1,round(m*q)) for q in (0.5,0.75,1.0,1.25,1.5)})
            actual=float(getattr(r,c))
            dr=R.d(pos,c,r.opponent_team); df_=float(np.mean([R.d(pos,c,g['opp']) for g in games]))
            for L in lines:
                thr=L if kind=='cont' else math.ceil(L-1e-9)
                rows.append(dict(week=t,pid=pid,pos=pos,stat=key,c=c,kind=kind,L=L,y=int(actual>=thr),actual=actual,mu0=d['mu'],sd0=d.get('sd',np.nan),
                    rv=d['rival_allows'],sos=d['sos'],dr=dr,dfaced=df_,olnow=olnow,olh=olh,grp=OLGRP.get(c,'mix')))
    print(t,len(rows),round(time.time()-t0))
B=pd.DataFrame(rows); B.to_pickle('/home/user/data/bt2_raw.pkl'); print(len(B))
