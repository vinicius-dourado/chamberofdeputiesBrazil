"""Diagnóstico 2: regra da tese de Bertholini (2015) - todos os cargos com status de ministro
e partido = filiação do ministro (coluna "Partido do Ministro"), com/sem postos extras não partidários
(AGU, CGU, BCB, GSI, Secom, ausentes da planilha)."""
import sys; sys.path.insert(0,'.')
import pandas as pd, numpy as np, indicadores_coalizao as ic
alm=ic.comp_almeida()
d=pd.read_csv('dados_brutos/partido_gabinete_ministerio.csv',sep=';',encoding='utf-8-sig')
d.columns=['gov','gini','gfim','classe','pasta','ppasta','ministro','ini','fim','pmin']
for c in ['gini','gfim','ini','fim']: d[c]=pd.to_datetime(d[c],dayfirst=True)
d['fim']=d['fim'].fillna(pd.Timestamp('2026-12-31'))
art={'Cardoso 1':59.6,'Cardoso 2':61.7,'Lula 1':49.3,'Lula 2':52.1,'Rousseff 1':43.7}
artT={'Cardoso 1':4.1,'Cardoso 2':4.3,'Lula 1':7.7,'Lula 2':9.1,'Rousseff 1':7.8}
def seats(t,p):
    for _,r in alm[alm.inicio<=t].iloc[::-1].iterrows():
        dd={a:s for a,_,s in r.comp}
        if p in dd: return dd[p]
    for _,r in alm[alm.inicio>t].iterrows():
        dd={a:s for a,_,s in r.comp}
        if p in dd: return dd[p]
    return None
def idx(comp,npt):
    M=sum(m for _,m,_ in comp); Sc=sum(s for _,_,s in comp)
    tot=sum(abs(s/Sc-m/M) for p,m,s in comp if p!='np')
    if npt: tot+=sum(m for p,m,_ in comp if p=='np')/M
    return 100*(1-.5*tot)
ts=pd.date_range('1995-01-01','2013-12-01',freq='MS')+pd.Timedelta(days=14)
for col in ['ppasta','pmin']:
  for extra in [0,3,5]:
    res={};sz={};nt={};semseat=set()
    for t in ts:
        a=d[(d.ini<=t)&(d.fim>t)].drop_duplicates('pasta',keep='last')
        vc=a[col].fillna('sfp').replace({'sfp':'np','ind':'np'}).replace(ic.NORM).value_counts()
        comp=[]
        for p,n in vc.items():
            if p=='np': comp.append(('np',int(n)+extra,0)); continue
            s=seats(t,p)
            if s is None: semseat.add(p); comp.append(('np',int(n),0))  # partido fora da coalizão -> np
            else: comp.append((p,int(n),s))
        if extra and not any(p=='np' for p,_,_ in comp): comp.append(('np',extra,0))
        mand=next(n for n,i,f in ic.MANDATOS if pd.Timestamp(i)<=t<pd.Timestamp(f))
        for npt in [0,1]: res.setdefault((npt,mand),[]).append(idx(comp,npt))
        sz.setdefault(mand,[]).append(sum(p!='np' for p,_,_ in comp)); nt.setdefault(mand,[]).append(sum(m for _,m,_ in comp))
    for npt in [0,1]:
        m={k:np.mean(res[(npt,k)]) for k in art}
        print(col,'extra',extra,'np_term',npt,{k:round(v,1) for k,v in m.items()},'rmse',round(np.sqrt(np.mean([(m[k]-art[k])**2 for k in art])),1))
    print('   tamanho',{k:round(np.mean(v),1) for k,v in sz.items() if k in art},'postos',{k:round(np.mean(v),1) for k,v in nt.items() if k in art},'sem cadeira->np',semseat)

# Verificação com os números que a própria tese/artigo dá no texto
c_lula = [("PT",21,91),("PMDB",2,78),("PL",1,44),("PSB",1,20),("PPS",1,20),("PCdoB",2,9),("PTB",1,52),("PV",1,6),("np",5,0)]
c_dilma = [("PT",17,88),("PMDB",6,78),("PR",1,40),("PSB",2,31),("PCdoB",1,15),("PP",1,41),("PDT",1,27),("np",8,0)]
print("Lula 1 (35 cargos, PT 21, PMDB 2):", round(ic.coalescencia(c_lula),1), "| Tabela 1: 49.3")
print("Rousseff 1 (37 cargos, PT 17, PMDB 6):", round(ic.coalescencia(c_dilma),1), "| Tabela 1: 43.7")
