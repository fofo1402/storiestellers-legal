import pandas as pd, numpy as np, re, unicodedata
D='/home/user/raw/nflverse/'; O='/home/user/data/'
s=pd.read_csv(O+'player_week.csv',low_memory=False)
s=s[s.position.isin(['QB','RB','FB','WR','TE'])]
def norm(n):
    n=unicodedata.normalize('NFKD',str(n)).encode('ascii','ignore').decode().lower()
    n=re.sub(r'[^a-z ]','',n); n=re.sub(r'\b(jr|sr|ii|iii|iv|v)\b','',n); return ' '.join(n.split())
sc=pd.read_csv(D+'snap_counts_2026.csv',low_memory=False); sc=sc[sc.game_type=='REG']
sc['k']=sc.player.map(norm)
pl=pd.read_csv(D+'players.csv',low_memory=False)[['gsis_id','pfr_id']].dropna()
sc=sc.merge(pl.rename(columns={'pfr_id':'pfr_player_id','gsis_id':'gsis'}),on='pfr_player_id',how='left')
r=pd.read_csv(D+'roster_weekly_2026.csv',low_memory=False)
r8=r[r.week==r.week.max()][['gsis_id','team','status','position','full_name']].rename(columns={'team':'team_w8','status':'roster_status_w8','position':'pos_roster'})
s['k']=s.player_display_name.map(norm)
# snaps per game for player rows
s=s.merge(sc[['game_id','k','team','offense_snaps','offense_pct']],on=['game_id','k','team'],how='left')
# games played by snap (offense_snaps>0) including games with no stat
snapgames=sc[sc.offense_snaps>0][['game_id','k','gsis','team','week','offense_pct']]
agg=s.groupby(['player_id']).agg(name=('player_display_name','last'),pos=('position','last'),
  teams=('team',lambda x:'/'.join(pd.unique(x))),last_team=('team','last'),
  g_stat=('game_id','nunique'),cmp=('completions','sum'),att=('attempts','sum'),pass_yds=('passing_yards','sum'),pass_td=('passing_tds','sum'),ints=('passing_interceptions','sum'),
  car=('carries','sum'),rush_yds=('rushing_yards','sum'),rush_td=('rushing_tds','sum'),
  rec=('receptions','sum'),tgt=('targets','sum'),rec_yds=('receiving_yards','sum'),rec_td=('receiving_tds','sum'),
  weeks=('week',lambda x:','.join(map(str,sorted(x)))),k=('k','last')).reset_index()
# snap-based games played across all teams
gm=[]
for _,a in agg.iterrows():
    sg=snapgames[((snapgames.gsis==a.player_id)|(snapgames.gsis.isna()&(snapgames.k==a.k)))&(snapgames.team.isin(a.teams.split('/')))]
    gm.append((sg.game_id.nunique(), round(sg.offense_pct.mean()*100,1) if len(sg) else np.nan, ','.join(map(str,sorted(sg.week.unique())))))
agg['g_snap']=[x[0] for x in gm]; agg['snap_pct_avg']=[x[1] for x in gm]; agg['weeks_snap']=[x[2] for x in gm]
agg['pj']=agg[['g_stat','g_snap']].max(axis=1)
agg=agg.merge(r8,left_on='player_id',right_on='gsis_id',how='left')
agg.to_csv(O+'player_season.csv',index=False)
print(agg.shape, (agg.g_snap<agg.g_stat).sum(),'jugadores con menos juegos por snaps que por stats')
