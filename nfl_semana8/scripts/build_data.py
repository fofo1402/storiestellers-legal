import pandas as pd, numpy as np, re, json
from zoneinfo import ZoneInfo
from datetime import datetime
D='/home/user/raw/nflverse/'; O='/home/user/data/'
g=pd.read_csv(D+'games.csv',low_memory=False); g=g[(g.season==2026)&(g.game_type=='REG')]
# ---- Week 8 schedule (times in ET -> Monterrey) ----
w8=g[(g.week==8)&g.home_score.isna()].copy()
def mty(r):
    dt=datetime.fromisoformat(f"{r.gameday}T{r.gametime}").replace(tzinfo=ZoneInfo('America/New_York'))
    return dt.astimezone(ZoneInfo('America/Monterrey'))
w8['kick_mty']=w8.apply(mty,axis=1)
w8['fecha_mty']=w8.kick_mty.dt.strftime('%a %d-%b-%Y'); w8['hora_mty']=w8.kick_mty.dt.strftime('%H:%M')
w8[['game_id','gameday','weekday','gametime','fecha_mty','hora_mty','away_team','home_team','stadium','espn','roof']].to_csv(O+'schedule_w8.csv',index=False)
played=g[g.home_score.notna()].copy()
rows=[]
for _,r in played.iterrows():
    for side,opp,pf,pa,ha in [('home','away',r.home_score,r.away_score,'vs'),('away','home',r.away_score,r.home_score,'@')]:
        rows.append(dict(team=r[f'{side}_team'],week=r.week,game_id=r.game_id,opp=r[f'{opp}_team'],ha=ha,pf=int(pf),pa=int(pa),res='G' if pf>pa else ('P' if pf<pa else 'E'),qb=r[f'{side}_qb_name']))
res=pd.DataFrame(rows).sort_values(['team','week']); res.to_csv(O+'results.csv',index=False)
# ---- player weekly stats ----
s=pd.read_csv(D+'stats_player_week_2026.csv',low_memory=False); s=s[s.season_type=='REG']
s=s[s.game_id.isin(played.game_id)]
s.to_csv(O+'player_week.csv',index=False)
# ---- defense vs position (allowed by defense = opponent_team) ----
pos_map={'QB':'QB','RB':'RB','FB':'RB','WR':'WR','TE':'TE'}
s['pgrp']=s.position.map(pos_map)
gp=res.groupby('team').game_id.nunique().rename('pj_def')
agg=lambda col,grp: s[s.pgrp==grp].groupby('opponent_team')[col].sum()
dfn=pd.DataFrame(index=sorted(res.team.unique()))
dfn['pj_def']=gp
dfn['qb_pass_yds']=agg('passing_yards','QB')
dfn['rb_rush_yds']=agg('rushing_yards','RB'); dfn['rb_rush_att']=agg('carries','RB'); dfn['rb_rush_td']=agg('rushing_tds','RB')
dfn['rb_rec_yds']=agg('receiving_yards','RB')
for p in ['WR','TE']:
    dfn[f'{p.lower()}_rec_yds']=agg('receiving_yards',p); dfn[f'{p.lower()}_rec']=agg('receptions',p); dfn[f'{p.lower()}_tgt']=agg('targets',p); dfn[f'{p.lower()}_td']=agg('receiving_tds',p)
t=pd.read_csv(D+'stats_team_week_2026.csv',low_memory=False); t=t[(t.season_type=='REG')&t.game_id.isin(played.game_id)]
dfn['team_pass_yds_gross']=t.groupby('opponent_team').passing_yards.sum()
dfn['team_sack_yds']=t.groupby('opponent_team').sack_yards_lost.sum()
dfn['team_rush_yds']=t.groupby('opponent_team').rushing_yards.sum()
dfn['pts_allowed']=res.groupby('team').pa.sum()
dfn=dfn.fillna(0)
dfn.index.name='team'; dfn.to_csv(O+'defense_totals.csv')
# per-game opponent-level allowed in each game (for leave-one-out SOS)
pg=s.groupby(['opponent_team','game_id','pgrp']).agg(pass_yds=('passing_yards','sum'),rush_yds=('rushing_yards','sum'),rec_yds=('receiving_yards','sum')).reset_index()
pg.to_csv(O+'def_game_pos.csv',index=False)
print('ok', len(w8), 'juegos sem8;', len(played),'jugados')
