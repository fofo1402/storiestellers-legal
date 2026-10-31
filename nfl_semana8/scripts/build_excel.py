# -*- coding: utf-8 -*-
import pandas as pd, numpy as np, json, sys
sys.path.insert(0,'/home/user/scripts')
from notes import SEL, EXCL_FLAGGED, EXCL_NOTES, GAMES, CORTE
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.workbook.defined_name import DefinedName
O='/home/user/data/'; RAW='/home/user/raw/nflverse/'; OUT='/home/user/entrega_semana8/'
import os; os.makedirs(OUT,exist_ok=True)
W=0.6
E=pd.read_csv(O+'evaluated_rules.csv'); D=pd.read_csv(O+'defense_pos.csv').set_index('team')
res=pd.read_csv(O+'results.csv'); sch=pd.read_csv(O+'schedule_w8.csv'); rec=pd.read_csv(O+'records.csv').set_index('team'); rec['dif_pg']=(rec.pf-rec.pa)/rec.pj
ol=pd.read_csv(O+'ol_proxy.csv').set_index('team'); pw=pd.read_csv(O+'player_week.csv',low_memory=False)
inj=pd.read_csv(RAW+'injuries_2026.csv',low_memory=False); ros=pd.read_csv(RAW+'roster_weekly_2026.csv',low_memory=False)
dg=pd.read_csv(O+'def_game_pos.csv'); league=json.load(open(O+'league_avg.json'))
POS=['QB','RB','WR','TE']
# ---------------- DefJuego (defense-game rows) ----------------
pwk=pw.copy(); pwk['pgrp']=pwk.position.map({'QB':'QB','RB':'RB','FB':'RB','WR':'WR','TE':'TE'})
rows=[]
for r in res.sort_values(['team','week']).itertuples():
    x=pwk[(pwk.game_id==r.game_id)&(pwk.opponent_team==r.team)]
    g=lambda grp,col: float(x[x.pgrp==grp][col].sum())
    rows.append(dict(def_=r.team,game_id=r.game_id,week=r.week,off=r.opp,QB=g('QB','passing_yards'),RB=g('RB','rushing_yards'),WR=g('WR','receiving_yards'),TE=g('TE','receiving_yards'),pts=r.pa,
        QBtd=g('QB','passing_tds'),RBtd=g('RB','rushing_tds'),WRtd=g('WR','receiving_tds'),TEtd=g('TE','receiving_tds')))
DJ=pd.DataFrame(rows); NDJ=len(DJ); DJ_LAST=NDJ+1
# python mirror of excel calcs
tot=DJ.groupby('def_').agg(pj=('game_id','count'),QB=('QB','sum'),RB=('RB','sum'),WR=('WR','sum'),TE=('TE','sum'),pts=('pts','sum'),QBtd=('QBtd','sum'),RBtd=('RBtd','sum'),WRtd=('WRtd','sum'),TEtd=('TEtd','sum'))
for p in POS+['pts']: tot[p+'_pg']=tot[p]/tot.pj; tot[p+'_rk']=tot[p+'_pg'].rank(ascending=False,method='min').astype(int)
for p in POS: tot[p+'td_pg']=tot[p+'td']/tot.pj; tot[p+'td_rk']=tot[p+'td_pg'].rank(ascending=False,method='min').astype(int)
LG={p:tot[p].sum()/tot.pj.sum() for p in POS}
for p in POS: assert abs(LG[p]-league[p])<1e-9 and np.allclose(tot[p+'_pg'].values,D.loc[tot.index,p+'_pg'].values)
def loo(defteam,gid,p):
    t=DJ[DJ.def_==defteam]; return (t[p].sum()-t[t.game_id==gid][p].sum())/(len(t)-1)
# ---------------- player game detail (SOS) ----------------
sosrows=[]
for x in E.itertuples():
    q=pw[pw.player_id==x.player_id]
    if x.pos=='QB': q=q[q.attempts>=15]
    teams=x.equipos_temp.split('/')
    for r in res[(res.game_id.isin(q.game_id))&(res.team.isin(teams))].sort_values('week').itertuples():
        sosrows.append(dict(pid=x.player_id,name=x.jugador,pos=x.pos,week=r.week,game_id=r.game_id,opp=r.opp,val=loo(r.opp,r.game_id,x.pos)))
SD=pd.DataFrame(sosrows)
E['sos_chk']=E.player_id.map(SD.groupby('pid').val.mean()); assert np.allclose(E.sos,E.sos_chk)
# ---------------- injuries text ----------------
i8=inj[(inj.week==8)]; i7=inj[(inj.week==7)]
r8=ros[ros.week==8].set_index('gsis_id')
def injtxt(pid,team):
    st=r8.status.get(pid,None) if pid in r8.index else None
    if isinstance(st,pd.Series): st=st.iloc[0]
    if st=='RES': return 'Reserva de lesionados (roster nflverse S8)'
    a=i8[i8.gsis_id==pid]; b=i7[(i7.gsis_id==pid)&(i7.report_status.notna())]
    s7=f"; S7: {b.report_status.iloc[0]} ({b.report_primary_injury.iloc[0]})" if len(b) and b.report_status.iloc[0] in ('Out','Doubtful','Questionable') else ''
    if len(a):
        ps=a.practice_status.iloc[0]; ps={'Full Participation in Practice':'Completo','Limited Participation in Practice':'Limitado','Did Not Participate In Practice':'No practicó'}.get(ps,ps)
        inj_=a.practice_primary_injury.iloc[0]
        if 'Not injury related' in str(inj_): return f"Práctica jue 29-oct: {ps} (descanso, no lesión){s7}"
        return f"Práctica jue 29-oct: {ps} ({inj_}); designación final sin verificar{s7}"
    if team=='SEA': return 'Sin reporte S8 de SEA en la fuente (juego del lunes); estatus con corte del viernes'+s7
    return 'No figura en el reporte de práctica del jue 29-oct'+s7
E['lesion']=[injtxt(r.player_id,r.equipo) for r in E.itertuples()]
# ---------------- verdicts ----------------
def verdict(r):
    if r.jugador in SEL: return 'Incluido-'+SEL[r.jugador]['conf']
    return 'Descartado'
E['veredicto']=E.apply(verdict,axis=1)
def motivo(r):
    if r.jugador in SEL: return 'Seleccionado por '+SEL[r.jugador]['regla']+'. Ver hoja Resumen.'
    if r.jugador in EXCL_FLAGGED: return EXCL_FLAGGED[r.jugador]
    if r.jugador in EXCL_NOTES: return EXCL_NOTES[r.jugador]
    parts=[]
    if not r.vol_ok: parts.append(f"volumen bajo el umbral ({r.prod_pg:.1f} yds/j vs {r.umbral}" + (f"; {r.tgt_pg:.1f} targets/j" if r.pos=='WR' else '')+")")
    if r.cambio<0.10: parts.append(f"ajuste {r.cambio*100:+.1f}% (< +10%)")
    parts.append(f"matchup {r.lectura.lower()} (rank {r['rank']})")
    return 'No cumple reglas de inclusión: '+'; '.join(parts)+'.'
E['motivo']=E.apply(motivo,axis=1)
assert set(SEL)<=set(E.jugador), set(SEL)-set(E.jugador)
for n in SEL: 
    r=E[E.jugador==n].iloc[0]; assert r.R1 or r.R2 or r.R3 or r.R4, n
    if SEL[n]['conf']=='Alta': assert r.alta_modelo, n
# ---------------- team info ----------------
QBT={'BAL':('Lamar Jackson','Titular S1-S4; fuera S5-S7 (esguince alto); práctica completa jue 29-oct y entrenador optimista (prensa 26-oct). Designación final sin verificar. Suplente: Tyler Huntley (S4-S7).'),
 'PHI':('Tanner McKee','Jalen Hurts en reserva de lesionados desde S6 (roster nflverse); McKee titular S6-S7.'),
 'TB':('Baker Mayfield','Regresó en S7 (11 intentos en victoria 43-13) tras dislocarse el pulgar en S3; práctica completa jue 29-oct. Jalon Daniels fue titular S4-S6.'),
 'WAS':('Jayden Daniels','Titular S1-S2 y S5-S6 (Mariota S3-S4); WAS descansó en S7; práctica completa jue 29-oct (codo).'),
 'CHI':('Caleb Williams','Titular S1-S2 y S6-S7 (Bagent/Keenum S3-S5); fuera del reporte de práctica.'),
 'MIN':('Kyler Murray','Titular (salió en S1 y faltó en S2 por conmoción; Wentz S2); fuera del reporte de práctica.'),
 'SEA':('Sam Darnold','Titular S3-S7 (Drew Lock S1-S2 parcial/total); SEA sin reporte S8 en la fuente.'),
 'ATL':('Michael Penix Jr.','Titular desde S3 (Rush/Strand S1-S2).'),
 'MIA':('Malik Willis','Titular en los 6 juegos con 15+ intentos.')}
def qb_default(t):
    q=pw[(pw.team==t)&(pw.position=='QB')&(pw.attempts>=15)]
    last=q[q.week==q.week.max()].sort_values('attempts').iloc[-1]
    n=q.groupby('player_display_name').game_id.nunique()
    return last.player_display_name, f"Titular en el último juego (S{int(last.week)}); {n.get(last.player_display_name)} titularidades con 15+ intentos; sin cambio reportado."
TRADES={'IND':'Salidas 27-oct: G Quenton Nelson (a SEA) y DT DeForest Buckner (a SF; AP: pendiente de examen físico, roster nflverse aún lo lista en IND).',
 'SEA':'Llegó G Quenton Nelson (27-oct, desde IND; irá de guardia izquierda según prensa). Salió G Christian Haynes (a MIA, roster S8).',
 'CHI':'Llegó DT Jeffery Simmons (29-oct, desde TEN).','TEN':'Salió DT Jeffery Simmons (29-oct, a CHI). Llegó DL Jonah Laulu (desde LV, roster S8).',
 'SF':'Llegó DT DeForest Buckner (27-oct).','ARI':'Salió WR Marvin Harrison Jr. (a HOU, roster S6). Llegó OL Jedrick Wills (S5).',
 'DAL':'Llegó CB Joey Porter Jr. (desde PIT, roster S4).','PIT':'Salió CB Joey Porter Jr. (a DAL, S4); llegó DB Sean Murphy-Bunting (S5).',
 'BAL':'Llegó OL Cam Jurgens (desde PHI, roster S5; inactivo S5-S6, activo en roster S7-S8; rol sin verificar).','PHI':'Salió OL Cam Jurgens (a BAL, S5).',
 'MIA':'Llegaron WR Jared Wayne (desde HOU, S7) y OL Christian Haynes (desde SEA, S8).','LV':'Salió DL Jonah Laulu (a TEN, S8).'}
def injlist(t,side):
    off=['QB','RB','WR','TE','FB','T','G','C','OL']
    a=i8[(i8.team==t)&(~i8.practice_primary_injury.fillna('').str.contains('Not injury'))]
    a=a[a.position.isin(off)] if side=='off' else a[~a.position.isin(off+['K','P','LS'])]
    a=a[a.practice_status.str.contains('Did Not|Limited',na=False)]
    if t=='SEA': return 'Sin reporte S8 en la fuente.'
    return '; '.join(f"{r.full_name} {r.position} ({r.practice_primary_injury}, {'no practicó' if 'Did Not' in r.practice_status else 'limitado'})" for r in a.itertuples()) or 'Ninguno DNP/limitado el jue 29-oct.'
T26=sorted(set(sch.away_team)|set(sch.home_team))
TEAM={}
for t in T26:
    n,b=QBT.get(t,qb_default(t))
    res_t=ros[(ros.week==8)&(ros.team==t)&(ros.status=='RES')&(ros.position.isin(['QB','RB','WR','TE']))].full_name.tolist()
    TEAM[t]=dict(qb=n,qb_base=b,tier=ol.tier[t],sack=ol.sack_rate[t],hit=ol.hit_rate[t],rsucc=ol.rush_success[t],stuff=ol.stuff_rate[t],
       inj_off=injlist(t,'off'),inj_def=injlist(t,'def'),trades=TRADES.get(t,'Sin movimientos relevantes detectados en S1-S8.'),ir=', '.join(res_t) or '—')
for t,v in TEAM.items():
    v['situacion']=f"QB: {v['qb']}. Línea tier proxy {v['tier']}. Ofensiva tocada: {v['inj_off']} Reserva (QB/RB/WR/TE): {v['ir']}. Movimientos: {v['trades']}"
# ---------------- selections data ----------------
opp={}; hora={}; part={}
for s in sch.itertuples():
    p=f"{s.away_team} @ {s.home_team}"
    for t in (s.away_team,s.home_team): part[t]=p; hora[t]=f"{s.fecha_mty.replace('Sun','Dom').replace('Mon','Lun').replace('Nov','nov')} {s.hora_mty}"
TDK={'QB':'QBtd','RB':'RBtd','WR':'WRtd','TE':'TEtd'}
QBPROD={t:E[(E.equipo==t)&(E.pos=='QB')&(E.jugador==TEAM[t]['qb'])].prod_pg.max() for t in T26}
SELROWS=[]
for n,v in SEL.items():
    r=E[E.jugador==n].iloc[0]; p=r.pos; o=r.rival
    ctx=dict(rp=r.rival_permite,rk=int(r['rank']),td=f"{tot.loc[o,TDK[p]+'_pg']:.2f}",tdr=int(tot.loc[o,TDK[p]+'_rk']),tgt=r.tgt_pg,rec=r.rec_pg,car=r.car_pg,prod=r.prod_pg,
             dif=rec.dif_pg[r.equipo],difr=rec.dif_pg[o],cp=r.cambio*100,qb=QBPROD.get(r.equipo,np.nan),qbrp=tot.loc[o,'QB_pg'])
    f=lambda s: s.format(**ctx)
    if p=='QB': base=f"{r.prod_pg:.1f} yds de pase/j en {int(r.pj)} titularidades ({int(r.pass_td)} TD, {int(r.ints)} INT)."
    elif p=='RB': base=f"{r.prod_pg:.1f} yds por tierra/j en {int(r.pj)} PJ ({r.car_pg:.1f} acarreos, {r.rec_pg:.1f} rec/j, {int(r.rush_td+r.rec_td)} TD)."
    else: base=f"{r.prod_pg:.1f} yds recibidas/j en {int(r.pj)} PJ ({r.rec_pg:.1f} rec y {r.tgt_pg:.1f} targets/j, {int(r.rec_td)} TD)."
    porque=(base+f" {o} permite {r.rival_permite:.1f} yds/j a {p} (rank {int(r['rank'])}/32, {r.lectura}). Calendario previo: sus rivales permitían {r.sos:.1f} vs {r.liga:.1f} de la liga. Proyección ajustada {r.proy:.1f} ({r.cambio*100:+.1f}%) con w = {W}."
            + (" Muestra corta (≤ 5 PJ)." if r.pj<=5 else ''))
    blk=f"(a) Qué la sube: {f(v['sube'])}\n(b) Qué la frena: {f(v['frena'])}\n(c) Regla aplicada: {f(v['regla_conf'])}"
    SELROWS.append(dict(pid=r.player_id,hora=hora[r.equipo],partido=part[r.equipo],jugador=n,equipo=r.equipo,rival=o,pos=p,cats=v['cats'],conf=v['conf'],
       rival_permite=r.rival_permite,rank=int(r['rank']),lectura=r.lectura,pts_rival=float(tot.loc[o,'pts_pg']),prob='n/d',porque=porque,
       a=f(v['sube']),b=f(v['frena']),c=f(v['regla_conf']),bloque=blk,riesgo=f(v['riesgo'])+' Contexto propio: '+TEAM[r.equipo]['situacion'],
       tier=TEAM[r.equipo]['tier'],situacion=TEAM[r.equipo]['situacion'],sos=r.sos,liga=r.liga,prod=r.prod_pg,proy=r.proy,cambio=r.cambio,regla=v['regla'],lesion=r.lesion,pj=int(r.pj)))
SR=pd.DataFrame(SELROWS)
order={'Alta':0,'Media':1}; SR['o']=SR.conf.map(order); SR['h']=SR.hora
SR=SR.sort_values(['h','partido','o','cambio'],ascending=[True,True,True,False]).drop(columns=['o','h']).reset_index(drop=True)
# ============================ EXCEL ============================
wb=Workbook()
AR='Arial'
F_IN=Font(name=AR,size=10,color='0000FF'); F_LK=Font(name=AR,size=10,color='008000'); F_FM=Font(name=AR,size=10,color='000000')
F_H=Font(name=AR,size=10,bold=True,color='FFFFFF'); F_T=Font(name=AR,size=14,bold=True); F_B=Font(name=AR,size=10,bold=True)
FILL_H=PatternFill('solid',fgColor='1F3864'); FILL_A=PatternFill('solid',fgColor='C6EFCE'); FILL_M=PatternFill('solid',fgColor='FFEB9C'); FILL_D=PatternFill('solid',fgColor='F2F2F2')
WR_=Alignment(wrap_text=True,vertical='top')
def hdr(ws,row,cols,widths=None):
    for j,c in enumerate(cols,1):
        cell=ws.cell(row=row,column=j,value=c); cell.font=F_H; cell.fill=FILL_H; cell.alignment=Alignment(wrap_text=True,vertical='center')
    if widths:
        for j,w_ in enumerate(widths,1): ws.column_dimensions[L(j)].width=w_
    ws.freeze_panes=ws.cell(row=row+1,column=1)
def put(ws,r,c,v,kind='in',fmt=None,wrap=False):
    cell=ws.cell(row=r,column=c,value=v); cell.font={'in':F_IN,'lk':F_LK,'fm':F_FM,'b':F_B,'t':F_T}[kind]
    if fmt: cell.number_format=fmt
    if wrap: cell.alignment=WR_
    return cell
ws0=wb.active; ws0.title='Resumen'
names=['Partidos','Cara a cara','Todos los evaluados','Calendario','Defensa','Equipo','Datos','Descartados','Fuentes','DefJuego','SOS_detalle']
WS={n:wb.create_sheet(n) for n in names}; WS['Resumen']=ws0
# ---- DefJuego ----
ws=WS['DefJuego']; hdr(ws,1,['Defensa','game_id','Semana','Ofensiva rival','Yds pase QB permitidas','Yds tierra RB permitidas','Yds rec. WR permitidas','Yds rec. TE permitidas','Pts permitidos','TD pase QB permitidos','TD tierra RB permitidos','TD rec. WR permitidos','TD rec. TE permitidos'],[9,18,8,9,12,12,12,12,10,10,10,10,10])
for i,r in enumerate(DJ.itertuples(),2):
    for j,v in enumerate([r.def_,r.game_id,r.week,r.off,r.QB,r.RB,r.WR,r.TE,r.pts,r.QBtd,r.RBtd,r.WRtd,r.TEtd],1): put(ws,i,j,v)
DJR=lambda col: f"DefJuego!${col}$2:${col}${DJ_LAST}"
PCOL={'QB':'E','RB':'F','WR':'G','TE':'H'}
# ---- Defensa ----
ws=WS['Defensa']; teams32=sorted(tot.index)
cols=['Equipo','PJ','Yds pase QB (total)','Yds tierra RB (total)','Yds rec. WR (total)','Yds rec. TE (total)','Pts permitidos (total)',
 'QB yds/j','Rank QB','RB yds/j','Rank RB','WR yds/j','Rank WR','TE yds/j','Rank TE','Pts/j','Rank Pts',
 'TD pase QB (total)','TD pase/j','Rank TD QB','TD tierra RB (total)','TD tierra RB/j','Rank TD RB','TD WR (total)','TD WR/j','Rank TD WR','TD TE (total)','TD TE/j','Rank TD TE',
 'Validación: yds pase netas/j (equipo)','Validación: yds tierra/j (equipo, todas las posiciones)']
hdr(ws,1,cols,[8,5]+[11]*29)
DT=pd.read_csv(O+'defense_pos.csv').set_index('team')
for i,t in enumerate(teams32,2):
    put(ws,i,1,t)
    put(ws,i,2,f'=COUNTIF({DJR("A")},$A{i})','lk')
    for j,c in zip(range(3,8),['E','F','G','H','I']): put(ws,i,j,f'=SUMIF({DJR("A")},$A{i},{DJR(c)})','lk')
    for j,src in zip([8,10,12,14,16],['C','D','E','F','G']):
        put(ws,i,j,f'={src}{i}/$B{i}','fm','0.00'); put(ws,i,j+1,f'=RANK({L(j)}{i},{L(j)}$2:{L(j)}$33,0)','fm','0')
    for j,c in zip([18,21,24,27],['J','K','L','M']):
        put(ws,i,j,f'=SUMIF({DJR("A")},$A{i},{DJR(c)})','lk'); put(ws,i,j+1,f'={L(j)}{i}/$B{i}','fm','0.00'); put(ws,i,j+2,f'=RANK({L(j+1)}{i},{L(j+1)}$2:{L(j+1)}$33,0)','fm','0')
    put(ws,i,30,float(DT.pass_net_pg[t]),'in','0.0'); put(ws,i,31,float(DT.rush_pg[t]),'in','0.0')
put(ws,35,1,'Promedio liga (yds por juego de defensa)','b')
for j,src in zip([8,10,12,14,16],['C','D','E','F','G']): put(ws,35,j,f'=SUM({src}2:{src}33)/SUM($B$2:$B$33)','fm','0.00')
put(ws,37,1,'Rank: 1 = la defensa que MÁS permite (matchup más blando); 32 = la que menos permite. Lectura: 1-10 Favorable, 11-21 Neutral, 22-32 Difícil. Yds por posición = suma de lo producido por jugadores de esa posición (QB: yds de pase brutas de QBs; RB incluye FB). Fuente: estadísticas por jugador nflverse (ESPN no accesible desde este entorno).','in',wrap=False)
DROW={t:i for i,t in enumerate(teams32,2)}
DPG={'QB':'H','RB':'J','WR':'L','TE':'N'}; DRK={'QB':'I','RB':'K','WR':'M','TE':'O'}; DAVG={'QB':'$H$35','RB':'$J$35','WR':'$L$35','TE':'$N$35'}
# ---- Calendario (detail + summary) ----
ws=WS['Calendario']
hdr(ws,1,['Equipo','Semana','L/V','Rival','PF','PC','Resultado','game_id','Rival permitía a QB (sin este juego)','a RB','a WR','a TE'],[8,7,5,7,6,6,9,18,14,10,10,10])
R2=res.sort_values(['team','week']).reset_index(drop=True); CAL_LAST=len(R2)+1
for i,r in enumerate(R2.itertuples(),2):
    for j,v in enumerate([r.team,r.week,'L' if r.ha=='vs' else 'V',r.opp,r.pf,r.pa],1): put(ws,i,j,v)
    put(ws,i,7,f'=IF(E{i}>F{i},"G",IF(E{i}<F{i},"P","E"))','fm'); put(ws,i,8,r.game_id)
    for j,p in zip(range(9,13),POS):
        c=PCOL[p]; put(ws,i,j,f'=(SUMIF({DJR("A")},$D{i},{DJR(c)})-SUMIFS({DJR(c)},{DJR("A")},$D{i},{DJR("B")},$H{i}))/(COUNTIF({DJR("A")},$D{i})-1)','lk','0.0')
CR=lambda col: f"${col}$2:${col}${CAL_LAST}"
sc=14
for j,h in enumerate(['Equipo (resumen)','PJ','G','P','E','Rivales ya enfrentados (resultado, PF-PC)','Dureza QB (yds/j que permitían sus rivales)','vs liga QB','Dureza RB','vs liga RB','Dureza WR','vs liga WR','Dureza TE','vs liga TE'],sc):
    c=ws.cell(row=1,column=j,value=h); c.font=F_H; c.fill=FILL_H; c.alignment=Alignment(wrap_text=True)
ws.column_dimensions[L(sc+5)].width=70
for k,w_ in zip(range(sc,sc+14),[9,5,4,4,4,70,12,9,10,9,10,9,10,9]): ws.column_dimensions[L(k)].width=w_
CALROW={}
for i,t in enumerate(teams32,2):
    CALROW[t]=i; gr=R2[R2.team==t]
    put(ws,i,sc,t); put(ws,i,sc+1,f'=COUNTIF({CR("A")},{L(sc)}{i})','fm')
    for k,res_ in zip(range(2,5),['G','P','E']): put(ws,i,sc+k,f'=COUNTIFS({CR("A")},{L(sc)}{i},{CR("G")},"{res_}")','fm')
    put(ws,i,sc+5,', '.join(f"S{r.week} {'vs' if r.ha=='vs' else '@'} {r.opp} ({r.res} {r.pf}-{r.pa})" for r in gr.itertuples()))
    for k,(p,col) in enumerate(zip(POS,['I','J','K','L'])):
        cc=sc+6+2*k; put(ws,i,cc,f'=AVERAGEIF({CR("A")},{L(sc)}{i},{CR(col)})','fm','0.0'); put(ws,i,cc+1,f'={L(cc)}{i}/Defensa!{DAVG[p]}-1','lk','+0.0%;-0.0%')
put(ws,36,sc,'Lectura: "vs liga" positivo = sus rivales permitían MÁS que el promedio (calendario fácil, números posiblemente inflados); negativo = calendario duro. Se excluye el propio juego del rival (leave-one-out) para no contar dos veces la producción del equipo evaluado.','in')
# Python mirror for calendario summary
CALPY={}
for t in teams32:
    gr=R2[R2.team==t]; CALPY[t]={p:float(np.mean([loo(r.opp,r.game_id,p) for r in gr.itertuples()])) for p in POS}
# ---- Equipo ----
ws=WS['Equipo']
hdr(ws,1,['Equipo','Récord (G-P-E)','PF','PC','PJ','Dif. pts/j','QB titular (verificado)','Base de la verificación','Tier línea ofensiva (proxy)','Tasa de capturas','Tasa de golpes al QB','Éxito en carreras diseñadas','Tasa de tapones (≤0 yds)','Ofensiva: no practicó/limitado (jue 29-oct)','Defensa: no practicó/limitado (jue 29-oct)','QB/RB/WR/TE en reserva de lesionados','Traspasos y movimientos','Situación (resumen)'],[7,10,6,6,5,8,18,45,9,9,9,9,9,50,50,30,45,80])
EROW={}
for i,t in enumerate(T26,2):
    EROW[t]=i; v=TEAM[t]; cr=CALROW[t]
    put(ws,i,1,t); put(ws,i,2,f'=Calendario!P{cr}&"-"&Calendario!Q{cr}&"-"&Calendario!R{cr}','lk')
    put(ws,i,3,f'=SUMIF(Calendario!{CR("A")},$A{i},Calendario!{CR("E")})','lk'); put(ws,i,4,f'=SUMIF(Calendario!{CR("A")},$A{i},Calendario!{CR("F")})','lk')
    put(ws,i,5,f'=COUNTIF(Calendario!{CR("A")},$A{i})','lk'); put(ws,i,6,f'=(C{i}-D{i})/E{i}','fm','+0.0;-0.0')
    put(ws,i,7,v['qb']); put(ws,i,8,v['qb_base'],wrap=True); put(ws,i,9,v['tier'])
    for j,k in zip(range(10,14),['sack','hit','rsucc','stuff']): put(ws,i,j,float(v[k]),'in','0.0%')
    put(ws,i,14,v['inj_off'],wrap=True); put(ws,i,15,v['inj_def'],wrap=True); put(ws,i,16,v['ir'],wrap=True); put(ws,i,17,v['trades'],wrap=True)
    put(ws,i,18,f'="QB: "&G{i}&". Línea tier proxy "&I{i}&". Ofensiva tocada: "&N{i}&" Reserva (QB/RB/WR/TE): "&P{i}&". Movimientos: "&Q{i}','fm',wrap=True)
put(ws,30,1,'Tier de línea = PROXY calculado por el analista con jugada por jugada nflverse (no es el tier de PFN, que no fue accesible): promedio de puntajes z de (−tasa de capturas, −tasa de golpes al QB, +éxito en carreras diseñadas, −tasa de tapones). Cortes por percentil: S > 90, A > 72, B > 50, C > 28, D > 10, F ≤ 10. No incorpora lesiones de esta semana; esas se anotan aparte.','in')
# ---- Datos ----
ws=WS['Datos']
hdr(ws,1,['ID (gsis)','Jugador','Pos','Equipo actual','Equipos en 2026','PJ','Semanas con estadística','Snap% ofensivo promedio','Intentos','Completos','Yds pase','TD pase','INT','Acarreos','Yds tierra','TD tierra','Targets','Recepciones','Yds recibidas','TD recepción','Métrica de la posición (yds)','Nota'],[12,22,5,7,9,5,16,9,8,8,8,7,6,8,8,7,8,8,8,7,10,40])
DAT_LAST=len(E)+1; DROWP={}
for i,r in enumerate(E.sort_values(['equipo','pos','jugador']).itertuples(),2):
    DROWP[r.player_id]=i
    vals=[r.player_id,r.jugador,r.pos,r.equipo,r.equipos_temp,int(r.pj),str(r.semanas),None if pd.isna(r.snap_pct) else float(r.snap_pct),int(r.att),int(r.cmp),int(r.pass_yds),int(r.pass_td),int(r.ints),int(r.car),int(r.rush_yds),int(r.rush_td),int(r.tgt),int(r.rec),int(r.rec_yds),int(r.rec_td)]
    for j,v in enumerate(vals,1): put(ws,i,j,v)
    put(ws,i,21,f'=IF(C{i}="QB",K{i},IF(C{i}="RB",O{i},S{i}))','fm')
    put(ws,i,22,'QB: totales solo de titularidades con 15+ intentos (PJ = titularidades).' if r.pos=='QB' else ('PJ = juegos con snaps ofensivos o estadística.' ))
DR=lambda col: f"Datos!${col}$2:${col}${DAT_LAST}"
# ---- SOS_detalle ----
ws=WS['SOS_detalle']; SD_LAST=len(SD)+1
hdr(ws,1,['ID (gsis)','Jugador','Pos','Semana','game_id','Defensa enfrentada','Lo que esa defensa permitía a la posición (yds/j, sin contar este juego)'],[12,22,5,7,18,9,22])
for i,r in enumerate(SD.itertuples(),2):
    for j,v in enumerate([r.pid,r.name,r.pos,r.week,r.game_id,r.opp],1): put(ws,i,j,v)
    c=PCOL[r.pos]; put(ws,i,7,f'=(SUMIF({DJR("A")},$F{i},{DJR(c)})-SUMIFS({DJR(c)},{DJR("A")},$F{i},{DJR("B")},$E{i}))/(COUNTIF({DJR("A")},$F{i})-1)','lk','0.00')
# ---- Todos los evaluados ----
ws=WS['Todos los evaluados']
EH=['ID (gsis)','Jugador','Pos','Equipo','Rival','Partido','PJ','Yds métrica (total)','Producción/j (yds)','Rival permite (yds/j a la pos.)','Rank rival (1 = más blando)','Lectura','Dureza del calendario (yds/j que permitían sus rivales)','Promedio liga','Calendario vs liga','Proyección ajustada/j','Cambio %','Targets/j','Recepciones/j','Acarreos/j','TD (de su métrica)','Estado de lesión (fuente y fecha)','Umbral de volumen','Volumen OK','Dif. pts/j equipo','Dif. pts/j rival','Brecha de guion','R1 base','R2 ampliada','R3 RB favorito','R4 volumen élite','Condición ALTA del modelo','Veredicto','Motivo']
hdr(ws,1,EH,[12,20,5,6,6,10,5,8,9,10,8,9,11,9,8,10,8,7,7,7,6,40,7,7,7,7,7,6,6,6,6,8,13,60])
E2=E.sort_values(['equipo','pos','prod_pg'],ascending=[True,True,False]).reset_index(drop=True); EV_LAST=len(E2)+1; EVROW={}
for i,r in enumerate(E2.itertuples(),2):
    EVROW[r.player_id]=i; dr=DROWP[r.player_id]; p=r.pos
    put(ws,i,1,r.player_id); put(ws,i,2,r.jugador); put(ws,i,3,p); put(ws,i,4,r.equipo); put(ws,i,5,r.rival); put(ws,i,6,part[r.equipo])
    put(ws,i,7,f'=Datos!F{dr}','lk'); put(ws,i,8,f'=Datos!U{dr}','lk'); put(ws,i,9,f'=H{i}/G{i}','fm','0.0')
    put(ws,i,10,f'=INDEX(Defensa!${DPG[p]}$2:${DPG[p]}$33,MATCH($E{i},Defensa!$A$2:$A$33,0))','lk','0.0')
    put(ws,i,11,f'=INDEX(Defensa!${DRK[p]}$2:${DRK[p]}$33,MATCH($E{i},Defensa!$A$2:$A$33,0))','lk','0')
    put(ws,i,12,f'=IF(K{i}<=10,"Favorable",IF(K{i}<=21,"Neutral","Difícil"))','fm')
    put(ws,i,13,f'=AVERAGEIF(SOS_detalle!$A$2:$A${SD_LAST},$A{i},SOS_detalle!$G$2:$G${SD_LAST})','lk','0.0')
    put(ws,i,14,f'=Defensa!{DAVG[p]}','lk','0.0'); put(ws,i,15,f'=M{i}/N{i}-1','fm','+0.0%;-0.0%')
    put(ws,i,16,f'=I{i}*(1+w*(J{i}/M{i}-1))','fm','0.0'); put(ws,i,17,f'=P{i}/I{i}-1','fm','+0.0%;-0.0%')
    put(ws,i,18,f'=Datos!Q{dr}/G{i}','lk','0.0'); put(ws,i,19,f'=Datos!R{dr}/G{i}','lk','0.0'); put(ws,i,20,f'=Datos!N{dr}/G{i}','lk','0.0')
    tdc={'QB':'L','RB':'P','WR':'T','TE':'T'}[p]; put(ws,i,21,f'=Datos!{tdc}{dr}','lk')
    put(ws,i,22,r.lesion,wrap=False)
    put(ws,i,23,f'=IF(C{i}="QB",190,IF(C{i}="RB",45,IF(C{i}="WR",42,30)))','fm')
    put(ws,i,24,f'=AND(I{i}>=W{i},OR(C{i}<>"WR",R{i}>=5))','fm')
    put(ws,i,25,f'=INDEX(Equipo!$F$2:$F$27,MATCH($D{i},Equipo!$A$2:$A$27,0))','lk','+0.0;-0.0'); put(ws,i,26,f'=INDEX(Equipo!$F$2:$F$27,MATCH($E{i},Equipo!$A$2:$A$27,0))','lk','+0.0;-0.0'); put(ws,i,27,f'=Y{i}-Z{i}','fm','+0.0;-0.0')
    put(ws,i,28,f'=AND(Q{i}>=0.1,X{i})','fm'); put(ws,i,29,f'=AND(K{i}<=10,Q{i}>=0.05,I{i}>=1.5*W{i},OR(C{i}<>"WR",R{i}>=5))','fm')
    put(ws,i,30,f'=AND(C{i}="RB",AA{i}>=5,K{i}<=10,Q{i}>=0,I{i}>=60)','fm'); put(ws,i,31,f'=AND(I{i}>=2*W{i},Q{i}>=0.05,K{i}<=21)','fm')
    put(ws,i,32,f'=OR(Q{i}>=0.05,AND(K{i}<=10,Q{i}>=0))','fm')
    c=put(ws,i,33,r.veredicto); c.fill=FILL_A if r.veredicto.endswith('Alta') else (FILL_M if r.veredicto.endswith('Media') else FILL_D)
    put(ws,i,34,r.motivo)
# ---- Resumen ----
ws=WS['Resumen']
put(ws,1,1,'NFL 2026 · Semana 8 · Jugadores con el matchup más favorable (yardas, recepciones, acarreos y TD)','t')
put(ws,2,1,f'Datos al {CORTE}. Tipo de corrida: PRIMERA CORRIDA (no existía versión previa). Recheck previsto: domingo 1-nov 10:40 (Monterrey) con inactivos oficiales; CHI @ SEA quedará "con estatus del viernes".','b')
put(ws,3,1,'Análisis de patrones, no garantía ni recomendación de apuesta. Solo mayores de 18 años. Sin líneas, cuotas ni parlays.','b')
put(ws,4,1,'Peso w (editable):','b'); put(ws,4,3,W,'in','0.00')
wb.defined_names['w']=DefinedName('w',attr_text='Resumen!$C$4')
put(ws,5,1,'Proyección = Producción/j × (1 + w × (Rival permite ÷ Dureza del calendario − 1)). w < 1 porque lo que permite cada defensa depende a su vez de a quién enfrentó (y de muestras de 6-8 juegos): se toma solo el 60% de la señal. Los textos de "Por qué" se calcularon con w = 0.60; si cambias w, las columnas numéricas y las reglas en "Todos los evaluados" se recalculan, pero no los textos ni los veredictos.','in')
put(ws,6,1,'Fuente principal: nflverse (datos oficiales de juego de la NFL). ESPN y demás sitios estuvieron bloqueados por la red del entorno: ver hoja Fuentes. Probabilidad de victoria: n/d (sin fuente accesible; no se usan líneas de apuestas).','in')
put(ws,7,1,'Selecciones ALTA','b'); put(ws,7,3,'=COUNTIF($H$12:$H$60,"Alta")','fm')
put(ws,8,1,'Selecciones MEDIA','b'); put(ws,8,3,'=COUNTIF($H$12:$H$60,"Media")','fm')
put(ws,9,1,'Total','b'); put(ws,9,3,'=C7+C8','fm')
RH=['Hora (Monterrey)','Partido','Jugador','Equipo','Rival','Pos','En qué puede sobresalir','Confianza','Rival permite (yds/j a su pos.)','Rank (1 = más blando)','Lectura','Pts/j permitidos por el rival','Prob. de victoria','Por qué (datos)','Por qué ALTA/MEDIA: (a) sube, (b) frena, (c) regla','Riesgo principal y contexto del equipo propio','Tier línea (proxy)','Situación del equipo','Dureza del calendario','Promedio liga','Producción/j','Proyección ajustada/j','Cambio %','Regla de inclusión','Estado de lesión']
hdr(ws,11,RH,[15,11,20,7,6,5,26,9,10,8,9,9,8,60,70,60,8,50,10,9,10,10,8,14,40]); ws.freeze_panes='D12'
for i,r in enumerate(SR.itertuples(),12):
    er=EVROW[r.pid]
    put(ws,i,1,r.hora); put(ws,i,2,r.partido); put(ws,i,3,r.jugador); put(ws,i,4,r.equipo); put(ws,i,5,r.rival); put(ws,i,6,r.pos); put(ws,i,7,r.cats,wrap=True)
    c=put(ws,i,8,r.conf); c.fill=FILL_A if r.conf=='Alta' else FILL_M; c.font=Font(name=AR,size=10,bold=True,color='0000FF')
    put(ws,i,9,f"='Todos los evaluados'!J{er}",'lk','0.0'); put(ws,i,10,f"='Todos los evaluados'!K{er}",'lk','0'); put(ws,i,11,f"='Todos los evaluados'!L{er}",'lk')
    put(ws,i,12,f'=INDEX(Defensa!$P$2:$P$33,MATCH($E{i},Defensa!$A$2:$A$33,0))','lk','0.0'); put(ws,i,13,'n/d')
    put(ws,i,14,r.porque,wrap=True); put(ws,i,15,r.bloque,wrap=True); put(ws,i,16,r.riesgo,wrap=True)
    put(ws,i,17,f'=INDEX(Equipo!$I$2:$I$27,MATCH($D{i},Equipo!$A$2:$A$27,0))','lk'); put(ws,i,18,f'=INDEX(Equipo!$R$2:$R$27,MATCH($D{i},Equipo!$A$2:$A$27,0))','lk',wrap=True)
    for j,col,fmt in [(19,'M','0.0'),(20,'N','0.0'),(21,'I','0.0'),(22,'P','0.0'),(23,'Q','+0.0%;-0.0%')]: put(ws,i,j,f"='Todos los evaluados'!{col}{er}",'lk',fmt)
    put(ws,i,24,r.regla); put(ws,i,25,r.lesion,wrap=True)
    ws.row_dimensions[i].height=150
SEL_LAST=11+len(SR)
cr=SEL_LAST+2
put(ws,cr,1,'Conclusión','b')
alta=SR[SR.conf=='Alta']
concl=[
 f"1. Lo más fuerte (ALTA, {len(alta)}): "+'; '.join(f"{r.jugador} ({r.equipo} vs {r.rival}, {r.cats.lower()}, {r.cambio*100:+.0f}%)" for r in alta.itertuples())+". En todos, el rival está en el top 10 de lo que permite a esa posición, el jugador tiene volumen y no figura con lesión, y el guion no lo frena.",
 "2. Patrón principal: los TE con defensas blandas a la posición (DET rank 1, MIA rank 4, WAS rank 5, DEN rank 8) dan los ajustes más altos (+17% a +46%). Por tierra, los rivales más permisivos de esta semana son LV (rank 1), PHI (3), DAL y NYJ (5), TEN (7), LAC (8) y CLE (9).",
 "3. Ajuste por calendario: la 'dureza' se calcula con lo que permitía cada rival previo SIN contar el juego contra el equipo evaluado (leave-one-out). Ejemplo: JAX permite 210 yds/j a WR (+41% sobre la liga, 148.7); contra la liga el ajuste con w = 0.6 sería ~+25%, pero los WR de IND ya enfrentaron rivales que permitían ~160 (más que la liga), así que queda en +18/19%. Además, Hunter Henry bajó de ALTA a MEDIA en la auditoría por aplicar de forma uniforme la regla de guion (receptor de favorito claro).",
 "4. Las bajas del rival se usaron a favor del otro lado (criterio 5): secundarias de BAL, ATL, MIA y PHI; frente de CLE; traspasos de Simmons (TEN) y Nelson/Buckner (IND). Ninguna baja propia se usó para descartar un partido completo.",
 "5. Lados descartados completos: TEN, DET, JAX, LV, CLE, ATL, LAC, DEN, MIA y CHI (ajustes negativos o sin volumen). CHI enfrenta a la defensa que menos permite a QB/WR/TE (SEA).",
 "6. Qué cambió: es la primera corrida (sin versión previa). Pendiente para el recheck del domingo 10:40: designaciones finales e inactivos de Lamar Jackson, Kelce, Michael Wilson, Breece Hall, DeVonta Smith/Wicks, Egbuka y las DL de NYJ; CHI @ SEA con estatus del viernes.",
 "7. Limitaciones: ESPN no fue accesible (red bloqueada); se usó nflverse como fuente principal. Sin probabilidad de victoria (n/d). Tier de línea = proxy propio, no PFN. Muestras cortas marcadas (≤ 5 PJ)."]
for k,t_ in enumerate(concl,cr+1): put(ws,k,1,t_)
# ---- Partidos ----
ws=WS['Partidos']
hdr(ws,1,['Hora (Monterrey)','Partido','Visitante','Local','Récord visitante','Récord local','Prob. de victoria','Decisión','Por qué','Qué lo puede romper','Conclusión de ambos lados','Selecciones ALTA','Selecciones MEDIA'],[15,11,8,8,10,10,10,18,60,45,70,9,9])
for i,s in enumerate(sch.itertuples(),2):
    p=f"{s.away_team} @ {s.home_team}"; g=GAMES[p]
    put(ws,i,1,hora[s.away_team]); put(ws,i,2,p); put(ws,i,3,s.away_team); put(ws,i,4,s.home_team)
    put(ws,i,5,f'=INDEX(Equipo!$B$2:$B$27,MATCH(C{i},Equipo!$A$2:$A$27,0))','lk'); put(ws,i,6,f'=INDEX(Equipo!$B$2:$B$27,MATCH(D{i},Equipo!$A$2:$A$27,0))','lk')
    put(ws,i,7,'n/d'); put(ws,i,8,g['dec']); put(ws,i,9,g['pq'],wrap=True); put(ws,i,10,g['romper'],wrap=True); put(ws,i,11,g['concl'],wrap=True)
    put(ws,i,12,f'=COUNTIFS(Resumen!$B$12:$B${SEL_LAST},B{i},Resumen!$H$12:$H${SEL_LAST},"Alta")','lk'); put(ws,i,13,f'=COUNTIFS(Resumen!$B$12:$B${SEL_LAST},B{i},Resumen!$H$12:$H${SEL_LAST},"Media")','lk')
    ws.row_dimensions[i].height=90
put(ws,16,1,'Partido del jueves 29-oct (CAR @ GB, 19-27) ya jugado: fuera del análisis. Descansan en S8: HOU, NO, NYG y SF.','in')
# ---- Cara a cara ----
ws=WS['Cara a cara']
hdr(ws,1,['Hora (Monterrey)','Partido','Ofensiva','Defensa rival','Pos','Defensa permite (yds/j)','Rank (1 = más blando)','Lectura','Promedio liga','Tier línea ofensiva (proxy)','Jugadores evaluados: producción/j → proyección (ajuste) [veredicto]'],[15,11,8,8,5,10,8,9,9,9,110])
k=2
for s in sch.itertuples():
    p=f"{s.away_team} @ {s.home_team}"
    for off,de in [(s.away_team,s.home_team),(s.home_team,s.away_team)]:
        for pos in POS:
            put(ws,k,1,hora[off]); put(ws,k,2,p); put(ws,k,3,off); put(ws,k,4,de); put(ws,k,5,pos)
            put(ws,k,6,f'=INDEX(Defensa!${DPG[pos]}$2:${DPG[pos]}$33,MATCH($D{k},Defensa!$A$2:$A$33,0))','lk','0.0')
            put(ws,k,7,f'=INDEX(Defensa!${DRK[pos]}$2:${DRK[pos]}$33,MATCH($D{k},Defensa!$A$2:$A$33,0))','lk','0')
            put(ws,k,8,f'=IF(G{k}<=10,"Favorable",IF(G{k}<=21,"Neutral","Difícil"))','fm'); put(ws,k,9,f'=Defensa!{DAVG[pos]}','lk','0.0')
            put(ws,k,10,f'=INDEX(Equipo!$I$2:$I$27,MATCH($C{k},Equipo!$A$2:$A$27,0))','lk')
            x=E2[(E2.equipo==off)&(E2.pos==pos)]
            put(ws,k,11,'; '.join(f"{r.jugador}: {r.prod_pg:.1f} → {r.proy:.1f} ({r.cambio*100:+.1f}%) [{r.veredicto}]" for r in x.itertuples()) or '—')
            k+=1
put(ws,k+1,1,'Texto de la columna K calculado con w = 0.60 (ver Todos los evaluados para valores vivos).','in')
# ---- Descartados ----
ws=WS['Descartados']
hdr(ws,1,['Jugador','Equipo','Rival','Pos','Producción/j','Cambio %','Rank rival','Motivo del descarte'],[22,7,7,5,10,9,8,110])
DS=E2[E2.veredicto=='Descartado'].copy()
DS['pri']=DS.jugador.map(lambda n: 0 if n in EXCL_FLAGGED else (1 if n in EXCL_NOTES else 2)); DS=DS.sort_values(['pri','equipo'])
for i,r in enumerate(DS.itertuples(),2):
    er=EVROW[r.player_id]
    put(ws,i,1,r.jugador); put(ws,i,2,r.equipo); put(ws,i,3,r.rival); put(ws,i,4,r.pos)
    put(ws,i,5,f"='Todos los evaluados'!I{er}",'lk','0.0'); put(ws,i,6,f"='Todos los evaluados'!Q{er}",'lk','+0.0%;-0.0%'); put(ws,i,7,f"='Todos los evaluados'!K{er}",'lk','0')
    put(ws,i,8,r.motivo)
n=len(DS)+3
put(ws,n,1,'Partidos: ninguno se excluyó por completo (los 13 tienen al menos una selección). Lados sin selección: TEN, DET, JAX, LV, CLE, ATL, LAC, DEN, MIA y CHI — ver hoja Partidos.','b')
put(ws,n+1,1,'Criterio de descarte por salud: se excluye a quien no practicó, está en reserva o no juega desde hace semanas sin confirmación de regreso. "Prefiere dejar fuera una selección dudosa".','in')
# ---- Fuentes ----
ws=WS['Fuentes']
hdr(ws,1,['Fuente','URL','Fecha (dato / consulta)','Qué se tomó','Limitaciones'],[30,60,28,60,70])
FU=[
 ('ESPN (fuente principal pedida por el usuario)','https://www.espn.com/nfl/ (stats, injuries, schedule) y site.api.espn.com','Intento 30-oct-2026 17:10 MTY','Nada: no accesible.','La red del entorno bloqueó www.espn.com y site.api.espn.com (proxy 403 / DNS). Por eso NO se pudo aplicar la regla "prevalece ESPN". Todas las cifras vienen de nflverse.'),
 ('nflverse – calendario y resultados (games.csv)','https://raw.githubusercontent.com/nflverse/nfldata/master/data/games.csv','Consulta 30-oct-2026 17:12 MTY','Calendario S8 (horario ET → Monterrey), marcadores S1-S8, QB de cada juego, ID de juego ESPN.','Marcadores verificados contra el play-by-play de nflverse: 108/108 juegos sin discrepancias. Las columnas de líneas de apuestas del archivo NO se usaron.'),
 ('nflverse – estadísticas por jugador y semana','github.com/nflverse/nflverse-data/releases/download/stats_player/stats_player_week_2026.csv','Archivo actualizado 30-oct-2026 09:54 MTY','Pase, carrera y recepción por juego; base de PJ, producción y yardas permitidas por posición.','Derivadas del play-by-play oficial (GSIS). Pueden diferir por pocas yardas de ESPN por correcciones de anotación.'),
 ('nflverse – play-by-play 2026','github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2026.csv.gz','Consulta 30-oct-2026','Verificación de marcadores; métricas de línea ofensiva (capturas, golpes al QB, éxito y tapones en carrera).','El tier de línea es un proxy propio, no el tier de PFN.'),
 ('nflverse – reportes de lesiones','github.com/nflverse/nflverse-data/releases/download/injuries/injuries_2026.csv','Archivo actualizado 30-oct-2026 07:59 MTY (práctica hasta el jue 29-oct)','Participación en práctica S8; designaciones finales de S7.','No incluye aún las designaciones finales del viernes (Out/Questionable) ni el reporte S8 de SEA. Todo estatus de S8 queda "sin verificar" hasta el recheck.'),
 ('nflverse – rosters semanales y snaps','roster_weekly_2026.csv y snap_counts_2026.csv (nflverse-data releases)','Archivo actualizado 30-oct-2026 08:07 MTY','Equipo actual, reserva de lesionados (RES), movimientos entre equipos, PJ por snaps.','El roster aún lista a Buckner en IND aunque la prensa (AP, 27-oct) reporta su traspaso a SF: prevalece la noticia más reciente.'),
 ('AP vía clickondetroit.com / news4jax.com','https://www.clickondetroit.com/sports/2026/10/27/colts-trade-all-pro-guard-quenton-nelson-to-seahawks-ap-source-says/','27-oct-2026','Traspaso de Quenton Nelson (IND → SEA).','Leído vía resumen de búsqueda web (las páginas no se pudieron abrir).'),
 ('AP vía news4jax.com / ajc.com','https://www.news4jax.com/sports/2026/10/27/the-49ers-bring-back-deforest-buckner-in-trade-with-the-colts-ap-source-says/','27-oct-2026','Traspaso de DeForest Buckner (IND → SF), pendiente de examen físico.','Leído vía resumen de búsqueda web.'),
 ('ESPN / NFL.com / chicagobears.com (resultados de búsqueda)','https://www.chicagobears.com/news/chicago-bears-acquire-all-pro-dl-jeffery-simmons-via-trade-roster-moves','29-oct-2026','Traspaso de Jeffery Simmons (TEN → CHI). Coincide con el roster nflverse S8.','Leído vía resumen de búsqueda web.'),
 ('Prensa sobre Lamar Jackson (Rapoport/NFL.com, CBS, ground.news)','https://ground.news/article/minter-hopeful-jackson-will-play-vs-bills','26-29 oct 2026','Optimismo del entrenador y expectativa de que juegue en S8.','No es designación oficial; se mantiene "sin verificar".'),
 ('Búsqueda de tiers de línea PFN S8','https://www.profootballnetwork.com/','30-oct-2026','Nada.','No se encontró/abrió el tier PFN S8; se usó proxy propio.'),
 ('Probabilidad de victoria (ESPN Matchup Predictor)','—','30-oct-2026','Nada: n/d.','ESPN bloqueado. No se convirtieron líneas de apuestas en probabilidades (prohibido por el usuario).'),
]
for i,f_ in enumerate(FU,2):
    for j,v in enumerate(f_,1): put(ws,i,j,v,wrap=True)

# ---- Auditoría ----
ws=wb.create_sheet('Auditoría',10)
hdr(ws,1,['#','Hallazgo del auditor independiente','Corrección aplicada'],[4,80,80])
AUD=[
 ('Resultado global: 21 selecciones con equipo, rival, estadísticas, defensas, calendario, dureza, reglas y estatus de lesión verificados contra los archivos crudos; 0 errores de fórmula; sin PPR ni líneas.','—'),
 ('Texto BAL: Cam Jurgens figuraba como "inactivo"; el roster lo marca activo en S7-S8.','Texto corregido (inactivo S5-S6, activo S7-S8).'),
 ('Conclusión 3 atribuía mal el efecto del calendario en el ejemplo de JAX.','Reescrita: +41% sobre la liga → ~+25% con w → +18/19% tras el calendario.'),
 ('Conclusión 2 decía que TEN, CLE y LAC eran los frentes más permisivos de la liga (PHI, CAR y DAL permiten más).','Reformulada como "rivales más permisivos de esta semana" con sus ranks.'),
 ('Partidos (BAL @ BUF): "BUF frena bien a RB" exageraba (rank 20, neutral).','Corregido: BAL frena bien (rank 26); BUF neutral (rank 20).'),
 ('PJ de Bam Knight (no seleccionado) mal contado: el emparejamiento de snaps por nombre falló ("Zonovan").','Snaps ahora se emparejan por ID (pfr → gsis), con respaldo por nombre. Se recalculó todo.'),
 ('Cooper Rush evaluado aunque no está en el roster de S7-S8.','Solo se evalúan jugadores en el roster de S8.'),
 ('Downs: mención de rumor de traspaso sin fuente.','Ahora citado: AP (27-oct) vía búsqueda web, marcado "sin confirmar".'),
 ('Downs: traspaso de Buckner afirmado sin la salvedad del examen físico.','Agregado "pendiente de examen físico según AP".'),
 ('Criterio de guion inconsistente: Henry ALTA siendo receptor de un favorito claro, mientras Higgins quedó MEDIA por lo mismo.','Regla explícita: receptor/QB de favorito claro (brecha ≥ +10 pts/j) → el guion frena → máximo MEDIA. Henry pasa de ALTA a MEDIA. Hockenson (brecha +5.3) se mantiene ALTA con juicio explícito.'),
 ('Estatus de compañeros usados como argumento (A.J. Brown DNP, Jayden Daniels práctica completa) sin marca "sin verificar".','Marcados "designación final sin verificar".'),
 ('Flowers e Higgins también cumplen R4.','Regla de inclusión actualizada a "R2 y R4".'),
]
for i,(a,b) in enumerate(AUD,2):
    put(ws,i,1,i-1); put(ws,i,2,a,wrap=True); put(ws,i,3,b,wrap=True)

# fonts default for all remaining cells
for wsx in wb.worksheets:
    for row in wsx.iter_rows():
        for c in row:
            if c.value is not None and (c.font is None or c.font.name!='Arial'): c.font=Font(name=AR,size=10)
fn=OUT+'NFL_2026_S8_matchups.xlsx'; wb.save(fn)
# save python mirror for json
pd.to_pickle(dict(E2=E2,SR=SR,tot=tot,LG=LG,DJ=DJ,TEAM=TEAM,CALPY=CALPY,R2=R2,SD=SD,hora=hora,part=part),O+'mirror.pkl')
print('saved',fn,len(SR),'selecciones;',(SR.conf=='Alta').sum(),'Alta')
