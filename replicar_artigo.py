"""Replica Pereira & Rennó (2001), "O que é que o reeleito tem?", com a 57ª legislatura e a eleição de 2026,
sem as variáveis de emendas/pork barrel (Emendas, Pork, MédiaExecução, TotalEmendas).

Entrada: dados/leg57/reeleicao_painel.parquet (python montar_painel.py)
Saída:   resultados/replicacao/*.csv e resultados.json (lidos por gerar_relatorio.py)

Tabelas do artigo reproduzidas:
  Tabela 1    regressões auxiliares: Concentração e Competição explicadas pela atuação do deputado (endogeneidade)
  Tabelas 2-3 diferença de médias (teste Z) entre reeleitos e não reeleitos: variáveis locais e nacionais
  Tabelas 4-5 gastos de campanha: média, mediana, desvio-padrão, variância (absoluto e por eleitor)
  Tabela 6    probit com seleção de Heckman: decisão de concorrer -> sucesso eleitoral (+ probit simples, nota 24)

Uso: python replicar_artigo.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import optimize, stats
from statsmodels.tools.numdiff import approx_hess3

PAINEL = Path("dados/leg57/reeleicao_painel.parquet")
SAIDA = Path("resultados/replicacao")

ROTULOS = {
    "const": "Constante", "concentracao_2022": "Concentração 2022", "concentracao_2026": "Concentração 2026",
    "competicao_2022": "Competição 2022", "competicao_2026": "Competição 2026", "mesma_base": "MesmaBase",
    "gastos_2026": "Gastos 2026 (R$)", "gastos_por_eleitor_2026": "Gastos 2026 por eleitor (R$)",
    "governador": "Governador", "projetos": "Projetos", "ausencia": "Ausência (nº)", "ausencia_pct": "Ausência (%)",
    "indice": "Índice (lealdade ao governo)", "mesa": "Mesa", "permanente": "Permanente", "especial": "Especial",
    "partpos": "Partpos", "senior": "Senior", "histleg": "Histleg", "histexec": "Histexec",
    "burocracia": "Burocracia", "empresa": "Empresa", "entrar_coalizao": "EntrarCoalizão",
    "sair_coalizao": "SairCoalizão", "esquerda": "Esquerda", "centro": "Centro", "direita": "Direita",
    "eleito_2022": "Eleito titular em 2022", "anos_exercicio": "Anos em exercício",
}

# --------------------------------------------------------------------- especificações
NACIONAIS = ["projetos", "ausencia_pct", "indice", "mesa", "permanente", "especial", "partpos", "senior",
             "histleg", "histexec", "entrar_coalizao", "sair_coalizao", "centro", "direita"]
SELECAO = ["concentracao_2022", "governador"] + NACIONAIS + ["burocracia", "empresa"]   # carreira só na seleção
RESULTADO = ["concentracao_2022", "mesma_base", "governador"] + NACIONAIS
CONTROLES = ["eleito_2022", "anos_exercicio"]
AUX = ["concentracao_2022", "governador", "projetos", "ausencia_pct", "indice", "mesa", "permanente", "especial",
       "partpos", "senior"]


def carregar():
    p = pd.read_parquet(PAINEL)
    p["eleito_2022"] = (p["condicao_2022"] == "eleito").astype(int)
    p["anos_exercicio"] = p["dias_exercicio"] / 365.25
    excl = {
        "saída definitiva antes da eleição (renúncia, cassação, morte)": p["saida_definitiva"].notna(),
        "eleito prefeito em 2024": p["eleito_prefeito_2024"] == 1,
        "Distrito Federal (um só município)": p["siglaUf"] == "DF",
        "partido sem classificação ideológica": p["ideologia"].isna(),
        "sem votações nominais em exercício": p["indice"].isna(),
    }
    fora = pd.Series(False, index=p.index)
    contagem = {}
    for motivo, m in excl.items():
        contagem[motivo] = int((m & ~fora).sum())
        fora |= m
    amostra = p[~fora].copy()
    return p, amostra, contagem


# -------------------------------------------------------------- probit com seleção (Heckman)
def bvn_cdf(h, k, rho):
    """Φ2(h, k; rho) - normal bivariada padrão (algoritmo de Genz, via scipy)."""
    rho = float(np.clip(rho, -0.999999, 0.999999))
    mvn = stats.multivariate_normal(mean=[0.0, 0.0], cov=[[1.0, rho], [rho, 1.0]])
    return np.atleast_1d(mvn.cdf(np.column_stack([h, k])))


def heckprobit(df, sel_vars, out_vars, dep_sel="concorreu_reeleicao", dep_out="reeleito"):
    """Probit bivariado com seleção amostral (equivalente ao heckprobit do Stata), por máxima verossimilhança."""
    d = df.dropna(subset=sel_vars + [dep_sel]).copy()
    sel = d[dep_sel].astype(int).to_numpy()
    d = d[(sel == 0) | d[out_vars + [dep_out]].notna().all(axis=1).to_numpy()]
    s = d[dep_sel].astype(int).to_numpy()
    Z = sm.add_constant(d[sel_vars].astype(float)).to_numpy()
    X = sm.add_constant(d[out_vars].astype(float).fillna(0)).to_numpy()
    y = d[dep_out].fillna(0).astype(int).to_numpy()
    kz, kx = Z.shape[1], X.shape[1]

    def negll(theta):
        g, b, at = theta[:kz], theta[kz:kz + kx], theta[-1]
        rho = np.tanh(at)
        zg, xb = Z @ g, X @ b
        ll = np.where(s == 0, stats.norm.logcdf(-zg), 0.0)
        q = 2 * y - 1
        m = s == 1
        for sinal in (1, -1):                       # y=1: Φ2(xb, zg; ρ); y=0: Φ2(-xb, zg; -ρ)
            mm = m & (q == sinal)
            pr = bvn_cdf(sinal * xb[mm], zg[mm], sinal * rho)
            ll[mm] = np.log(np.clip(pr, 1e-300, None))
        return -ll.sum()

    # valores iniciais: probits separados
    ps = sm.Probit(s, Z).fit(disp=0)
    po = sm.Probit(y[s == 1], X[s == 1]).fit(disp=0)
    theta0 = np.concatenate([ps.params, po.params, [0.0]])
    res = optimize.minimize(negll, theta0, method="BFGS", options={"maxiter": 5000, "gtol": 1e-6})
    res = optimize.minimize(negll, res.x, method="Nelder-Mead",
                            options={"maxiter": 20000, "xatol": 1e-8, "fatol": 1e-10}) if not res.success else res
    H = approx_hess3(res.x, negll)
    cov = np.linalg.pinv(H)
    se = np.sqrt(np.clip(np.diag(cov), 0, None))
    nomes = ["const"] + sel_vars
    nomes_o = ["const"] + out_vars
    tab = []
    for eq, nm, sl in (("seleção", nomes, slice(0, kz)), ("resultado", nomes_o, slice(kz, kz + kx))):
        for n, c, e in zip(nm, res.x[sl], se[sl]):
            z = c / e if e > 0 else np.nan
            tab.append({"equacao": eq, "variavel": n, "coef": c, "ep": e, "z": z,
                        "p": 2 * stats.norm.sf(abs(z))})
    at, at_se = res.x[-1], se[-1]
    ll_ind = ps.llf + po.llf          # rho = 0: as duas equações são independentes
    lr = 2 * (-res.fun - ll_ind)
    # verossimilhança perfilada em rho (demais parâmetros reotimizados)
    perfil = []
    for r in (-0.9, -0.5, 0.0, 0.5, 0.9, 0.99, 0.999):
        f = lambda th: negll(np.concatenate([th, [np.arctanh(r)]]))  # noqa: E731
        rr = optimize.minimize(f, res.x[:-1], method="BFGS", options={"maxiter": 2000})
        perfil.append({"rho": r, "loglik": float(-rr.fun)})
    return {
        "perfil_rho": perfil,
        "tabela": pd.DataFrame(tab),
        "rho": float(np.tanh(at)), "atanh_rho": float(at), "atanh_rho_ep": float(at_se),
        "rho_ic95": [float(np.tanh(at - 1.96 * at_se)), float(np.tanh(at + 1.96 * at_se))],
        "lr_rho0": float(lr), "p_lr_rho0": float(stats.chi2.sf(max(lr, 0), 1)),
        "loglik": float(-res.fun), "n": int(len(s)), "n_selecionados": int(s.sum()),
        "n_reeleitos": int(y[s == 1].sum()), "convergiu": bool(res.success),
    }


def probit_simples(df, vars_, dep="reeleito"):
    d = df[df["concorreu_reeleicao"] == 1].dropna(subset=vars_ + [dep])
    m = sm.Probit(d[dep].astype(int), sm.add_constant(d[vars_].astype(float))).fit(disp=0)
    t = pd.DataFrame({"variavel": m.params.index, "coef": m.params.values, "ep": m.bse.values,
                      "z": m.tvalues.values, "p": m.pvalues.values})
    return {"tabela": t, "n": int(m.nobs), "pseudo_r2": float(m.prsquared), "loglik": float(m.llf)}


# -------------------------------------------------------------------------- tabelas
def tabela1(a):
    """OLS (EP robustos HC1) entre os que concorreram à reeleição."""
    d = a[a["concorreu_reeleicao"] == 1]
    out = []
    for dep in ("concentracao_2026", "competicao_2026"):
        dd = d.dropna(subset=AUX + [dep])
        m = sm.OLS(dd[dep], sm.add_constant(dd[AUX].astype(float))).fit(cov_type="HC1")
        for v in m.params.index:
            out.append({"dependente": dep, "variavel": v, "coef": m.params[v], "ep": m.bse[v], "p": m.pvalues[v],
                        "n": int(m.nobs), "r2": m.rsquared})
    return pd.DataFrame(out)


def teste_medias(a, variaveis):
    """Z = (X̄1 - X̄2) / sqrt(s1²/n1 + s2²/n2), reeleitos (1) x não reeleitos (2), entre os candidatos."""
    d = a[a["concorreu_reeleicao"] == 1]
    g1, g2 = d[d["reeleito"] == 1], d[d["reeleito"] == 0]
    out = []
    for v in variaveis:
        x1, x2 = g1[v].dropna().astype(float), g2[v].dropna().astype(float)
        ep = np.sqrt(x1.var() / len(x1) + x2.var() / len(x2))
        z = (x1.mean() - x2.mean()) / ep if ep > 0 else np.nan
        out.append({"variavel": v, "media_reeleitos": x1.mean(), "dp_reeleitos": x1.std(), "n_reeleitos": len(x1),
                    "media_nao_reeleitos": x2.mean(), "dp_nao_reeleitos": x2.std(), "n_nao_reeleitos": len(x2),
                    "z": z, "p": 2 * stats.norm.sf(abs(z)) if pd.notna(z) else np.nan})
    return pd.DataFrame(out)


def tabela_gastos(a):
    d = a[a["concorreu_reeleicao"] == 1]
    out = []
    for v in ("gastos_2026", "gastos_por_eleitor_2026"):
        for nome, g in (("reeleitos", d[d["reeleito"] == 1]), ("não reeleitos", d[d["reeleito"] == 0])):
            x = g[v]
            dec = x[x > 0]
            out.append({"variavel": v, "grupo": nome, "n": len(x), "pct_declarou": len(dec) / len(x),
                        "media": dec.mean(), "mediana": dec.median(), "dp": dec.std(), "variancia": dec.var(),
                        "cv": dec.std() / dec.mean()})
    return pd.DataFrame(out)


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    p, a, excl = carregar()
    print(f"painel {len(p)} -> amostra {len(a)}; concorreram {int(a['concorreu_reeleicao'].sum())}, "
          f"reeleitos {int(a['reeleito'].sum())}")

    t1 = tabela1(a)
    t2 = teste_medias(a, ["concentracao_2022", "concentracao_2026", "competicao_2022", "competicao_2026",
                          "mesma_base", "gastos_2026", "governador"])
    t3 = teste_medias(a, ["projetos", "ausencia", "ausencia_pct", "indice", "mesa", "permanente", "especial",
                          "partpos", "senior", "histleg", "histexec", "burocracia", "empresa", "entrar_coalizao",
                          "sair_coalizao", "esquerda", "centro", "direita"])
    t45 = tabela_gastos(a)

    modelos = {}
    print("Heckman probit: especificação do artigo...")
    modelos["artigo"] = heckprobit(a, SELECAO, RESULTADO)
    print("Heckman probit: com controles de mandato...")
    sel_c = SELECAO + CONTROLES
    out_c = RESULTADO + CONTROLES
    modelos["controles"] = heckprobit(a, sel_c, out_c)
    print("Heckman probit: titulares empossados em fev/2023...")
    modelos["titulares"] = heckprobit(a[a["titular_posse_fev2023"] == 1], SELECAO, RESULTADO)
    probit = probit_simples(a, RESULTADO)

    t1.to_csv(SAIDA / "tabela1_auxiliares.csv", index=False)
    t2.to_csv(SAIDA / "tabela2_medias_locais.csv", index=False)
    t3.to_csv(SAIDA / "tabela3_medias_nacionais.csv", index=False)
    t45.to_csv(SAIDA / "tabelas4_5_gastos.csv", index=False)
    for k, m in modelos.items():
        m["tabela"].to_csv(SAIDA / f"tabela6_heckprobit_{k}.csv", index=False)
    probit["tabela"].to_csv(SAIDA / "nota24_probit_simples.csv", index=False)

    resumo = {
        "amostra": {"painel": len(p), "analise": len(a), "exclusoes": excl,
                    "concorreram": int(a["concorreu_reeleicao"].sum()), "reeleitos": int(a["reeleito"].sum()),
                    "cargo_disputado": a["cargo_disputado_2026"].value_counts().to_dict()},
        "rotulos": ROTULOS,
        "tabela1": t1.to_dict("records"), "tabela2": t2.to_dict("records"), "tabela3": t3.to_dict("records"),
        "tabelas4_5": t45.to_dict("records"),
        "tabela6": {k: {**{x: y for x, y in m.items() if x != "tabela"}, "coefs": m["tabela"].to_dict("records")}
                    for k, m in modelos.items()},
        "probit_simples": {"n": probit["n"], "pseudo_r2": probit["pseudo_r2"],
                           "coefs": probit["tabela"].to_dict("records")},
    }
    (SAIDA / "resultados.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=1, default=float))
    for k, m in modelos.items():
        print(f"  {k}: n={m['n']} sel={m['n_selecionados']} rho={m['rho']:.3f} "
              f"LR(rho=0)={m['lr_rho0']:.2f} p={m['p_lr_rho0']:.3f} convergiu={m['convergiu']}")
    print(f"resultados em {SAIDA}/")


if __name__ == "__main__":
    main()
