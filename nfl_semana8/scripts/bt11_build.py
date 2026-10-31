# Variables de mercado: puntos esperados del equipo (de spread y total de cierre) y spread, contra su historial.
import sys; sys.path.insert(0,'/home/user/scripts')
import pandas as pd, numpy as np
from props_model import *
B=pd.read_pickle('/home/user/data/bt10_raw.pkl')
g=pd.read_csv('/home/user/raw/nflverse/games.csv',low_memory=False); g=g[g.season==2026]
IMP={}; SPR={}
for r in g.itertuples():
    if pd.isna(r.total_line): continue
    IMP[(r.game_id,r.home_team)]=(r.total_line+r.spread_line)/2; IMP[(r.game_id,r.away_team)]=(r.total_line-r.spread_line)/2
    SPR[(r.game_id,r.home_team)]=r.spread_line; SPR[(r.game_id,r.away_team)]=-r.spread_line
TEAM_OF=res.set_index(['game_id','opp']).team.to_dict()
feat={}
for (t,pid),grp in B.groupby(['week','pid']):
    r=pw[(pw.player_id==pid)&(pw.week==t)].iloc[0]; pos=r.pgrp
    teams=list(pd.unique(pw[(pw.player_id==pid)&(pw.week<t)].team))
    gs=player_games(pid,pos,teams,maxweek=t)
    hi=[IMP.get((x['game_id'],TEAM_OF.get((x['game_id'],x['opp'])))) for x in gs]; hs=[SPR.get((x['game_id'],TEAM_OF.get((x['game_id'],x['opp'])))) for x in gs]
    hi=[v for v in hi if v is not None]; hs=[v for v in hs if v is not None]
    feat[(t,pid)]=(IMP.get((r.game_id,r.team),np.nan),np.mean(hi) if hi else np.nan,SPR.get((r.game_id,r.team),np.nan),np.mean(hs) if hs else np.nan)
for i,c in enumerate(['imp_now','imp_hist','spr_now','spr_hist']): B[c]=[feat[(a,b)][i] for a,b in zip(B.week,B.pid)]
B.to_pickle('/home/user/data/bt11_raw.pkl'); print(B[['imp_now','imp_hist','spr_now','spr_hist']].describe().round(2).to_string())
