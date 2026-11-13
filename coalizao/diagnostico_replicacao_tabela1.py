"""Diagnóstico: tenta reproduzir a proporcionalidade da Tabela 1 de Bertholini & Pereira (2017)
com variações da coalescência de Amorim Neto (denominador das cadeiras, termo dos não partidários,
termo da oposição) e de bases de ministérios (planilha de ministros com/sem secretarias, com postos
extras não partidários). Nenhuma variação reproduz os cinco valores do artigo (RMSE mínimo ~5,7)."""
import sys; sys.path.insert(0,'.')
import pandas as pd, numpy as np, itertools, indicadores_coalizao as ic
alm=ic.comp_almeida()
d=pd.read_csv('dados_brutos/partido_gabinete_ministerio.csv',sep=';',encoding='utf-8-sig')
d.columns=['gov','gini','gfim','classe','pasta','ppasta','ministro','ini','fim','pmin']
for c in ['gini','gfim','ini','fim']: d[c]=pd.to_datetime(d[c],dayfirst=True)
d['fim']=d['fim'].fillna(pd.Timestamp('2026-12-31'))
d['p']=d.ppasta.replace(ic.NORM)
art={'Cardoso 1':59.6,'Cardoso 2':61.7,'Lula 1':49.3,'Lula 2':52.1,'Rousseff 1':43.7}
artT={'Cardoso 1':4.1,'Cardoso 2':4.3,'Lula 1':7.7,'Lula 2':9.1,'Rousseff 1':7.8}
def seats(t,p):
    for _,r in alm[alm.inicio<=t].iloc[::-1].iterrows():
        dd={a:s for a,_,s in r.comp}
        if p in dd: return dd[p]
    for _,r in alm[alm.inicio>t].iterrows():
        dd={a:s for a,_,s in r.comp}
        if p in dd: return dd[p]
    return 0
def idx(comp,den,npt,opp):
    M=sum(m for _,m,_ in comp); Sc=sum(s for _,_,s in comp)
    D=Sc if den=='coal' else 513
    tot=sum(abs(s/D-m/M) for p,m,s in comp if p!='np')
    if npt: tot+=sum(m for p,m,_ in comp if p=='np')/M
    if opp: tot+=(513-Sc)/513
    return 100*(1-.5*tot)
ts=pd.date_range('1995-01-01','2013-12-01',freq='MS')+pd.Timedelta(days=14)
comps={}
for filt in ['todos','sem_orgaoPR','so_ministerios']:
    for t in ts:
        a=d[(d.ini<=t)&(d.fim>t)]
        if filt=='sem_orgaoPR': a=a[a['classe']!='Órgão da PR']
        if filt=='so_ministerios': a=a[a['classe']=='Ministério']
        a=a.drop_duplicates('pasta',keep='last')
        vc=a.p.replace({'sfp':'np','ind':'np'}).fillna('np').value_counts()
        comps[(filt,t)]=[(p,int(n),0 if p=='np' else seats(t,p)) for p,n in vc.items()]
rows=[]
for filt in ['todos','sem_orgaoPR','so_ministerios']:
  for den,npt,opp in [('coal',1,0),('513',1,1),('513',0,1),('coal',0,0)]:
    r={};sz={};nm={}
    for t in ts:
        mand=next(n for n,i,f in ic.MANDATOS if pd.Timestamp(i)<=t<pd.Timestamp(f)); c=comps[(filt,t)]
        r.setdefault(mand,[]).append(idx(c,den,npt,opp)); sz.setdefault(mand,[]).append(sum(p!='np' for p,_,_ in c)); nm.setdefault(mand,[]).append(sum(m for _,m,_ in c))
    m={k:np.mean(v) for k,v in r.items()}
    rows.append(dict(base=filt,den=den,np=npt,opp=opp,**{k:round(m[k],1) for k in art},rmse=round(np.sqrt(np.mean([(m[k]-art[k])**2 for k in art])),1)))
  print(filt,'tamanho',{k:round(np.mean(v),1) for k,v in sz.items()},'n postos',{k:round(np.mean(v),1) for k,v in nm.items()})
print(pd.DataFrame(rows).to_string(index=False)); print(art, artT)
print('--- adicionando k postos np (AGU, CGU, BCB, GSI, Secom...) a base "todos"')
for k in [0,2,4,6,8]:
  for den,npt,opp in [('coal',1,0),('513',1,1)]:
    r={}
    for t in ts:
        mand=next(n for n,i,f in ic.MANDATOS if pd.Timestamp(i)<=t<pd.Timestamp(f)); c=[(p,(m+k if p=='np' else m),s) for p,m,s in comps[('todos',t)]]
        r.setdefault(mand,[]).append(idx(c,den,npt,opp))
    m={kk:np.mean(v) for kk,v in r.items()}
    print(k,den,opp,{kk:round(m[kk],1) for kk in art},'rmse',round(np.sqrt(np.mean([(m[kk]-art[kk])**2 for kk in art])),1))
