import pandas as pd, numpy as np, json
O='/home/user/data/'
W=0.6
res=pd.read_csv(O+'results.csv'); dg=pd.read_csv(O+'def_game_pos.csv'); s=pd.read_csv(O+'player_week.csv',low_memory=False)
a=pd.read_csv(O+'player_season.csv'); sch=pd.read_csv(O+'schedule_w8.csv'); dt=pd.read_csv(O+'defense_totals.csv').set_index('team')
METRIC={'QB':('pass_yds','QB'),'RB':('rush_yds','RB'),'WR':('rec_yds','WR'),'TE':('rec_yds','TE')}
# allowed per defense per game, per position metric (0 when absent)
games=res[['team','game_id','opp','week']]
def allowed_table(grp,col):
    x=dg[dg.pgrp==grp][['opponent_team','game_id',col]].rename(columns={'opponent_team':'team'})
    t=games.merge(x,on=['team','game_id'],how='left').fillna({col:0})
    return t  # one row per defense-game
AL={p:allowed_table(g,c) for p,(c,g) in METRIC.items()}
def_pg={p:AL[p].groupby('team')[METRIC[p][0]].mean() for p in METRIC}
league={p:AL[p][METRIC[p][0]].mean() for p in METRIC}
rank={p:def_pg[p].rank(ascending=False,method='min').astype(int) for p in METRIC}
def loo(defteam,game_id,p):
    t=AL[p]; c=METRIC[p][0]; x=t[(t.team==defteam)&(t.game_id!=game_id)][c]
    return x.mean()
# team-level SOS (all games of team) for Calendario sheet
sos_rows=[]
for team,gr in res.groupby('team'):
    row={'team':team,'pj':len(gr),'rivales':', '.join(f"S{r.week} {r.ha} {r.opp} ({r.res} {r.pf}-{r.pa})" for r in gr.itertuples())}
    for p in METRIC: row[f'sos_{p}']=np.mean([loo(r.opp,r.game_id,p) for r in gr.itertuples()])
    sos_rows.append(row)
sos=pd.DataFrame(sos_rows); sos.to_csv(O+'sos_team.csv',index=False)
# defense table
D=pd.DataFrame({f'{p}_pg':def_pg[p] for p in METRIC})
for p in METRIC: D[f'{p}_rank']=rank[p]
D['pj']=dt.pj_def; D['pts_pg']=dt.pts_allowed/dt.pj_def; D['pts_rank']=D.pts_pg.rank(ascending=False,method='min').astype(int)
D['pass_net_pg']=(dt.team_pass_yds_gross+dt.team_sack_yds)/dt.pj_def; D['rush_pg']=dt.team_rush_yds/dt.pj_def
D['pass_gross_pg']=dt.team_pass_yds_gross/dt.pj_def
D.index.name='team'; D.to_csv(O+'defense_pos.csv')
json.dump({p:league[p] for p in METRIC},open(O+'league_avg.json','w'))
# opponents week 8
opp={}; ha={}
for r in sch.itertuples(): opp[r.away_team]=r.home_team; opp[r.home_team]=r.away_team; ha[r.away_team]='visitante'; ha[r.home_team]='local'
# candidates
a=a[a.team_w8.notna()].copy(); a['cur']=a.team_w8
a=a[a.cur.isin(opp.keys())]
a['pg']=a.pos.replace({'FB':'RB'})
rows=[]
for x in a.itertuples():
    p=x.pg
    pw=s[(s.player_id==x.player_id)]
    if p=='QB':
        pw=pw[pw.attempts>=15]
        if len(pw)==0: continue
    gids=set(pw.game_id)
    # include snap-only games (played, no stat) for non-QB
    if p!='QB':
        sn=pd.read_csv(O+'../raw/nflverse/snap_counts_2026.csv',low_memory=False) if 'SN' not in globals() else SN
        globals()['SN']=sn
    pj=len(gids) if p=='QB' else int(x.pj)
    col={'QB':'passing_yards','RB':'rushing_yards','WR':'receiving_yards','TE':'receiving_yards'}[p]
    tot=pw[col].sum()
    prod=tot/pj
    # opponents faced in games played (stat rows); snap-only games are added via results lookup
    gl=res[(res.game_id.isin(gids))]
    gl=gl[gl.team.isin(x.teams.split('/'))]
    sosv=np.mean([loo(r.opp,r.game_id,p) for r in gl.itertuples()]) if len(gl) else np.nan
    o=opp[x.cur]
    rows.append(dict(player_id=x.player_id,jugador=x.name,pos=p,equipo=x.cur,equipos_temp=x.teams,rival=o,condicion=ha[x.cur],pj=pj,
       semanas=','.join(map(str,sorted(pw.week.unique()))),snap_pct=x.snap_pct_avg,roster=x.roster_status_w8,
       att=pw.attempts.sum(),cmp=pw.completions.sum(),pass_yds=pw.passing_yards.sum(),pass_td=pw.passing_tds.sum(),ints=pw.passing_interceptions.sum(),
       car=pw.carries.sum(),rush_yds=pw.rushing_yards.sum(),rush_td=pw.rushing_tds.sum(),
       tgt=pw.targets.sum(),rec=pw.receptions.sum(),rec_yds=pw.receiving_yards.sum(),rec_td=pw.receiving_tds.sum(),
       prod_pg=prod,rival_permite=def_pg[p][o],rank=int(rank[p][o]),sos=sosv,liga=league[p]))
E=pd.DataFrame(rows)
E['tgt_pg']=E.tgt/E.pj; E['car_pg']=E.car/E.pj; E['rec_pg']=E.rec/E.pj
E['proy']=E.prod_pg*(1+W*(E.rival_permite/E.sos-1)); E['cambio']=E.proy/E.prod_pg-1
E['lectura']=np.where(E['rank']<=10,'Favorable',np.where(E['rank']<=21,'Neutral','Difícil'))
# keep relevant volume candidates
keep=((E.pos=='QB')&(E.att/E.pj>=15))|((E.pos=='RB')&(E.car_pg>=5))|((E.pos=='WR')&(E.tgt_pg>=3.5))|((E.pos=='TE')&(E.tgt_pg>=3))
E=E[keep].sort_values(['equipo','pos','prod_pg'],ascending=[True,True,False])
E.to_csv(O+'evaluated_raw.csv',index=False)
print(len(E)); print({p:round(league[p],2) for p in METRIC})
