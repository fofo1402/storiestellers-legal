import json, pandas as pd, numpy as np
from openpyxl import load_workbook
J=json.load(open('/home/user/entrega_semana8/data.json'))
wb=load_workbook('/tmp/recalc/NFL_2026_S8_matchups.xlsx',data_only=True)
ev=wb['Todos los evaluados']; hdr=[c.value for c in ev[1]]
X={}
for row in ev.iter_rows(min_row=2,values_only=True):
    if row[0]: X[row[0]]=dict(zip(hdr,row))
mp={'pj':'PJ','produccion_pj':'Producción/j (yds)','rival_permite':'Rival permite (yds/j a la pos.)','rank':'Rank rival (1 = más blando)','dureza_calendario':'Dureza del calendario (yds/j que permitían sus rivales)','promedio_liga':'Promedio liga','proyeccion':'Proyección ajustada/j','cambio':'Cambio %','tgt_pg':'Targets/j','rec_pg':'Recepciones/j','car_pg':'Acarreos/j','lectura':'Lectura','R1':'R1 base','R2':'R2 ampliada','R3':'R3 RB favorito','R4':'R4 volumen élite','alta_modelo':'Condición ALTA del modelo','veredicto':'Veredicto','dif_pg':'Dif. pts/j equipo','gap':'Brecha de guion','vol_ok':'Volumen OK'}
bad=0; n=0
for d in J['evaluados']:
    x=X[d['player_id']]
    for k,h in mp.items():
        a,b=d[k],x[h]; n+=1
        if isinstance(a,float) or isinstance(b,float):
            if abs(float(a)-float(b))>1e-6*max(1,abs(float(a))): bad+=1; print('DIF',d['jugador'],k,a,b)
        elif a!=b: bad+=1; print('DIF',d['jugador'],k,a,b)
r=wb['Resumen']; rh=[c.value for c in r[11]]
for i,s in enumerate(J['selecciones'],12):
    row={h:r.cell(i,j+1).value for j,h in enumerate(rh)}
    assert row['Jugador']==s['jugador'] and row['Confianza']==s['confianza'], (row['Jugador'],s['jugador'])
    for k,h in [('rival_permite','Rival permite (yds/j a su pos.)'),('rank','Rank (1 = más blando)'),('pts_pj_permitidos_rival','Pts/j permitidos por el rival'),('dureza_calendario','Dureza del calendario'),('promedio_liga','Promedio liga'),('produccion_pj','Producción/j'),('proyeccion','Proyección ajustada/j'),('cambio','Cambio %')]:
        n+=1
        if abs(float(s[k])-float(row[h]))>1e-6*max(1,abs(float(s[k]))): bad+=1; print('DIF sel',s['jugador'],k,s[k],row[h])
    n+=1
    if row['Tier línea (proxy)']!=s['tier_linea']: bad+=1; print('DIF tier',s['jugador'])
dfn=wb['Defensa']
for i in range(2,34):
    t=dfn.cell(i,1).value; d=J['defensas'][t]
    for k,col in [('QB_yds_pj',8),('QB_rank',9),('RB_yds_pj',10),('RB_rank',11),('WR_yds_pj',12),('WR_rank',13),('TE_yds_pj',14),('TE_rank',15),('pts_permitidos_pj',16),('rank_pts',17),('pj',2)]:
        n+=1
        if abs(float(d[k])-float(dfn.cell(i,col).value))>1e-9: bad+=1; print('DIF def',t,k)
c=wb['Calendario']
for i in range(2,34):
    t=c.cell(i,14).value; d=J['calendario_jugado'][t]
    for k,col in zip(['QB','RB','WR','TE'],[20,22,24,26]):
        n+=1
        if abs(d['dureza'][k]-c.cell(i,col).value)>1e-9: bad+=1; print('DIF cal',t,k)
print(f'comparaciones {n}, diferencias {bad}')
print('conteos', J['conteos'], r['C7'].value, r['C8'].value)
