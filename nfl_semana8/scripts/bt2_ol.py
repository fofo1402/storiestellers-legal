import sys; sys.path.insert(0,'/home/user/scripts')
from bt2_eval import *
R=[]
for w in [0.45,0.5,0.6]:
    for bol,bru in [(0,0),(-0.02,-0.02),(-0.04,-0.04),(-0.06,-0.06),(-0.04,0),(0,-0.04),(-0.08,-0.08)]:
        R.append(dict(w=w,bol=bol,bru=bru,tr=br(probs(tr,'new',w,bol,bru),tr.y),te=br(probs(te,'new',w,bol,bru),te.y),all=br(probs(B,'new',w,bol,bru),B.y)))
print(pd.DataFrame(R).round(5).to_string())
