import pandas as pd, numpy as np
O='/home/user/data/'
E=pd.read_csv(O+'evaluated_raw.csv'); rec=pd.read_csv(O+'records.csv').set_index('team'); rec['dif_pg']=(rec.pf-rec.pa)/rec.pj
TH={'QB':190,'RB':45,'WR':42,'TE':30}
E['umbral']=E.pos.map(TH)
E['vol_ok']=(E.prod_pg>=E.umbral)&((E.pos!='WR')|(E.tgt_pg>=5))
E['dif_pg']=E.equipo.map(rec.dif_pg); E['dif_rival']=E.rival.map(rec.dif_pg); E['gap']=E.dif_pg-E.dif_rival
E['R1']=(E.cambio>=0.10)&E.vol_ok
E['R2']=(E['rank']<=10)&(E.cambio>=0.05)&(E.prod_pg>=1.5*E.umbral)&((E.pos!='WR')|(E.tgt_pg>=5))
E['R3']=(E.pos=='RB')&(E.gap>=5)&(E['rank']<=10)&(E.cambio>=0)&(E.prod_pg>=60)
E['R4']=(E.prod_pg>=2*E.umbral)&(E.cambio>=0.05)&(E['rank']<=21)
E['alta_modelo']=(E.cambio>=0.05)|((E['rank']<=10)&(E.cambio>=0))
f=E[E.R1|E.R2|E.R3|E.R4]
pd.set_option('display.width',250)
print(f[['jugador','pos','equipo','rival','pj','prod_pg','tgt_pg','rank','cambio','gap','R1','R2','R3','R4','alta_modelo','roster']].round(3).to_string(index=False))
E.to_csv(O+'evaluated_rules.csv',index=False)
