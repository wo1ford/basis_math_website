import json, math
from fractions import Fraction

def solve(data):
    eps=1e-9
    n=len(data['c']); rows=[]; signs=[]; bs=[]
    for r in data['rows']:
        a=[float(v) for v in r['a']]; b=float(r['b']); op=r['op']
        if b<0:
            a=[-v for v in a];b=-b;op={'≤':'≥','≥':'≤','=':'='}[op]
        rows.append(a);bs.append(b);signs.append(op)
    names=['x_{%d}'%(j+1) for j in range(n)]; basis=[]; arts=[]
    def col(i, val, name):
        names.append(name)
        for k,row in enumerate(rows):row.append(val if i==k else 0.)
        return len(names)-1
    for i,op in enumerate(signs):
        if op=='≤':basis.append(col(i,1.,'s_{%d}'%(i+1)))
        else:
            if op=='≥':col(i,-1.,'s_{%d}'%(i+1))
            j=col(i,1.,'a_{%d}'%(i+1));arts.append(j);basis.append(j)
    snaps=[]
    def run(cost,phase):
        for it in range(500):
            red=[cost[j]-sum(cost[basis[i]]*rows[i][j] for i in range(len(rows))) for j in range(len(names))]
            enter=next((j for j,v in enumerate(red) if v>eps),None)
            ratios=[bs[i]/row[enter] if enter is not None and row[enter]>eps else None for i,row in enumerate(rows)]
            viable=[i for i,v in enumerate(ratios) if v is not None]
            leave=min(viable,key=lambda i:(ratios[i],basis[i])) if viable else None
            snap={'phase':phase,'table':[r[:] + [bs[i]] for i,r in enumerate(rows)],'basis':basis[:],'names':names[:],'reduced':red[:], 'enter':enter,'leave':leave,'ratios':ratios,'value':sum(cost[basis[i]]*bs[i] for i in range(len(rows)))}
            snaps.append(snap)
            if enter is None:return 'optimal'
            if leave is None:return 'unbounded'
            pivot=rows[leave][enter]; old=[r[:] for r in rows]; oldb=bs[:]
            rows[leave]=[v/pivot for v in rows[leave]];bs[leave]/=pivot
            for i in range(len(rows)):
                if i!=leave:
                    f=old[i][enter];rows[i]=[old[i][j]-f*rows[leave][j] for j in range(len(names))];bs[i]=oldb[i]-f*bs[leave]
            basis[leave]=enter
        return 'limit'
    if arts:
        state=run([-1. if j in arts else 0. for j in range(len(names))],1)
        if state!='optimal' or abs(snaps[-1]['value'])>eps:return {'status':'infeasible','snapshots':snaps}
        for i in range(len(rows)-1,-1,-1):
            if basis[i] in arts:
                j=next((j for j in range(len(names)) if j not in arts and abs(rows[i][j])>eps),None)
                if j is None:
                    rows.pop(i);bs.pop(i);basis.pop(i);continue
                p=rows[i][j];rows[i]=[v/p for v in rows[i]];bs[i]/=p
                for k in range(len(rows)):
                    if k!=i:
                        f=rows[k][j];rows[k]=[v-f*w for v,w in zip(rows[k],rows[i])];bs[k]-=f*bs[i]
                basis[i]=j
        keep=[j for j in range(len(names)) if j not in arts];basis=[keep.index(j) for j in basis];rows=[[r[j] for j in keep] for r in rows];names=[names[j] for j in keep]
    cost=[float(v)*(1 if data['direction']=='max' else -1) for v in data['c']]+[0.]*(len(names)-n)
    status=run(cost,2);x=[0.]*n
    for i,j in enumerate(basis):
        if j<n:x[j]=bs[i]
    value=sum(float(c)*v for c,v in zip(data['c'],x))
    checks=[]
    for r in data['rows']:
        lhs=sum(float(a)*v for a,v in zip(r['a'],x));delta=lhs-float(r['b']);op=r['op']
        violation=abs(delta) if op=='=' else max(0,delta if op=='≤' else -delta)
        checks.append({'lhs':lhs,'rhs':float(r['b']),'delta':delta,'violation':violation})
    return {'status':status,'snapshots':snaps,'x':x,'value':value,'checks':checks,'error':max([q['violation'] for q in checks]+[max(0,-v) for v in x]+[0])}

result_json=json.dumps(solve(json.loads(input_json)),allow_nan=False)
