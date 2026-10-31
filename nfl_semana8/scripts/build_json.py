# -*- coding: utf-8 -*-
import pandas as pd, numpy as np, json, sys
sys.path.insert(0,'/home/user/scripts')
from notes import CORTE, GAMES
O='/home/user/data/'; OUT='/home/user/entrega_semana8/'
M=pd.read_pickle(O+'mirror.pkl'); E2,SR,tot,LG,TEAM,CALPY,R2,hora,part=M['E2'],M['SR'],M['tot'],M['LG'],M['TEAM'],M['CALPY'],M['R2'],M['hora'],M['part']
sch=pd.read_csv(O+'schedule_w8.csv'); rec=pd.read_csv(O+'records.csv').set_index('team'); rec['dif_pg']=(rec.pf-rec.pa)/rec.pj
def clean(v):
    if isinstance(v,(np.integer,)): return int(v)
    if isinstance(v,(np.floating,)): return None if np.isnan(v) else float(v)
    if isinstance(v,(np.bool_,)): return bool(v)
    if isinstance(v,float) and np.isnan(v): return None
    return v
POS=['QB','RB','WR','TE']
meta=dict(temporada=2026,semana=8,tipo_corrida='PRIMERA CORRIDA',datos_al=CORTE,peso_w=0.6,zona_horaria='America/Monterrey (UTC-6)',
  avisos=['Análisis de patrones, no garantía ni recomendación de apuesta. Solo mayores de 18 años.',
          'ESPN no fue accesible desde el entorno (red bloqueada); fuente principal: nflverse (datos oficiales de juego de la NFL).',
          'Estatus de lesiones: práctica hasta el jueves 29-oct; designaciones finales del viernes sin verificar. SEA sin reporte S8 en la fuente.',
          'Probabilidad de victoria: n/d (sin fuente accesible; no se usan líneas de apuestas).',
          'Tier de línea ofensiva: proxy propio calculado con play-by-play (no PFN).',
          'Los textos explicativos se calcularon con w = 0.6.'],
  promedio_liga_yds_por_juego={p:float(LG[p]) for p in POS},
  formula='proyeccion = produccion_pj * (1 + w * (rival_permite / dureza_calendario - 1)); cambio = proyeccion / produccion_pj - 1')
partidos=[]
for s in sch.itertuples():
    p=f"{s.away_team} @ {s.home_team}"; g=GAMES[p]
    partidos.append(dict(partido=p,visitante=s.away_team,local=s.home_team,fecha_hora_monterrey=hora[s.away_team],hora_et=s.gametime,estadio=s.stadium,espn_game_id=str(s.espn),
       record_visitante=f"{int(rec.G[s.away_team])}-{int(rec.P[s.away_team])}-{int(rec.E[s.away_team])}",record_local=f"{int(rec.G[s.home_team])}-{int(rec.P[s.home_team])}-{int(rec.E[s.home_team])}",
       prob_victoria='n/d',decision=g['dec'],por_que=g['pq'],que_lo_puede_romper=g['romper'],conclusion=g['concl'],
       selecciones=[r.jugador for r in SR.itertuples() if r.partido==p]))
defensas={t:dict(pj=int(tot.pj[t]),pts_permitidos_pj=float(tot.pts_pg[t]),rank_pts=int(tot.pts_rk[t]),
   **{f'{p}_yds_pj':float(tot[p+'_pg'][t]) for p in POS},**{f'{p}_rank':int(tot[p+'_rk'][t]) for p in POS},
   **{f'{p}_td_pj':float(tot[p+'td_pg'][t]) for p in POS},**{f'{p}_td_rank':int(tot[p+'td_rk'][t]) for p in POS}) for t in tot.index}
calendario={}
for t in sorted(R2.team.unique()):
    gr=R2[R2.team==t]
    calendario[t]=dict(juegos=[dict(semana=int(r.week),condicion='L' if r.ha=='vs' else 'V',rival=r.opp,pf=int(r.pf),pc=int(r.pa),resultado=r.res) for r in gr.itertuples()],
        dureza={p:CALPY[t][p] for p in POS},dureza_vs_liga={p:CALPY[t][p]/LG[p]-1 for p in POS})
equipos={t:{k:clean(v) for k,v in d.items()} for t,d in TEAM.items()}
for t in equipos: equipos[t]['dif_pts_pj']=float(rec.dif_pg[t]); equipos[t]['record']=f"{int(rec.G[t])}-{int(rec.P[t])}-{int(rec.E[t])}"
cols=['player_id','jugador','pos','equipo','rival','pj','semanas','att','cmp','pass_yds','pass_td','ints','car','rush_yds','rush_td','tgt','rec','rec_yds','rec_td','prod_pg','rival_permite','rank','lectura','sos','liga','proy','cambio','tgt_pg','rec_pg','car_pg','lesion','umbral','vol_ok','dif_pg','dif_rival','gap','R1','R2','R3','R4','alta_modelo','veredicto','motivo']
ev=[{('dureza_calendario' if k=='sos' else 'promedio_liga' if k=='liga' else 'produccion_pj' if k=='prod_pg' else 'proyeccion' if k=='proy' else k):clean(getattr(r,k)) for k in cols} for r in E2.itertuples()]
for d in ev: d['partido']=part[d['equipo']]; d['semanas']=str(d['semanas'])
sel=[]
for r in SR.itertuples():
    sel.append(dict(hora_monterrey=r.hora,partido=r.partido,jugador=r.jugador,player_id=r.pid,equipo=r.equipo,rival=r.rival,pos=r.pos,categorias=r.cats,confianza=r.conf,
      rival_permite=float(r.rival_permite),rank=int(r.rank),lectura=r.lectura,pts_pj_permitidos_rival=float(r.pts_rival),prob_victoria='n/d',por_que=r.porque,
      por_que_confianza=dict(a_sube=r.a,b_frena=r.b,c_regla=r.c),riesgo=r.riesgo,tier_linea=r.tier,situacion_equipo=r.situacion,dureza_calendario=float(r.sos),
      promedio_liga=float(r.liga),produccion_pj=float(r.prod),proyeccion=float(r.proy),cambio=float(r.cambio),regla_inclusion=r.regla,estado_lesion=r.lesion,pj=int(r.pj)))
J=dict(metadatos=meta,partidos=partidos,defensas=defensas,calendario_jugado=calendario,equipos=equipos,evaluados=ev,selecciones=sel,
  conteos=dict(alta=int((SR.conf=='Alta').sum()),media=int((SR.conf=='Media').sum()),total=len(SR)))
json.dump(J,open(OUT+'data.json','w'),ensure_ascii=False,indent=1)
print('data.json ok', len(ev),'evaluados', len(sel),'selecciones')
