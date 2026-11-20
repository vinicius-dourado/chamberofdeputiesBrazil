"""Replica Pereira & Rennó (2001), "O que é que o reeleito tem?", para a eleição de 2026 (57ª legislatura),
usando SÓ as variáveis aprovadas na validação com 1998 (python validar_1998.py).

Regra: uma variável entra aqui só se, com os dados de 1994/1998, o nosso cálculo chega ao mesmo resultado do artigo
(mesmo sinal e mesma significância a 10%) em todas as estatísticas que o artigo publica para ela. Ficam de fora as
variáveis sem dados de 1998 (Ausência, Índice, Mesa, Permanente, Especial, Partpos, Líder, Gastos), as reprovadas e
as de emendas (Emendas, Pork, MédiaExecução), fora do escopo.

Entradas: dados/leg57/reeleicao_painel.parquet; resultados/validacao_1998/variaveis_validadas.json
Saídas:   resultados/replicacao/*.csv e resultados.json (lidos por gerar_relatorio.py)

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
VALIDACAO = Path("resultados/validacao_1998/variaveis_validadas.json")
# nome na validação (1998) -> coluna do painel de 2026
PARA_2026 = {"concentracao_ant": "concentracao_2022", "concentracao_atual": "concentracao_2026",
             "competicao_atual": "competicao_2026", "mesma_base": "mesma_base", "senior": "senior",
             "histleg": "histleg", "histexec": "histexec", "sair_coalizao": "sair_coalizao",
             "governador": "governador", "projetos": "projetos", "burocracia": "burocracia", "empresa": "empresa",
             "entrar_coalizao": "entrar_coalizao", "esquerda": "esquerda", "centro": "centro"}


def especificacao():
    v = json.loads(VALIDACAO.read_text())
    sel = [PARA_2026[x] for x in v["selecao"]]
    out = [PARA_2026[x] for x in v["resultado"]]
    descr = [PARA_2026[x] for x in v["aprovadas"] if x != "ideologia"]
    return v, sel, out, descr


def carregar():
    p = pd.read_parquet(PAINEL)
    p["eleito_2022"] = (p["condicao_2022"] == "eleito").astype(int)
    p["anos_exercicio"] = p["dias_exercicio"] / 365.25
    excl = {
        "saída definitiva antes da eleição (renúncia, cassação, morte)": p["saida_definitiva"].notna(),
        "eleito prefeito em 2024": p["eleito_prefeito_2024"] == 1,
        "Distrito Federal (um só município)": p["siglaUf"] == "DF",
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
def tabela1(a, descr):
    """Tabela 1 do artigo: Concentração atual explicada pela anterior (+ variáveis aprovadas). MQO, EP robustos.
    A equação de Competição do artigo fica de fora: nenhum dos regressores dela foi aprovado."""
    d = a[a["concorreu_reeleicao"] == 1]
    xs = ["concentracao_2022"] + [v for v in ("senior", "histleg", "histexec", "sair_coalizao") if v in descr]
    dd = d.dropna(subset=xs + ["concentracao_2026"])
    m = sm.OLS(dd["concentracao_2026"], sm.add_constant(dd[xs].astype(float))).fit(cov_type="HC1")
    return pd.DataFrame([{"dependente": "concentracao_2026", "variavel": v, "coef": m.params[v], "ep": m.bse[v],
                          "p": m.pvalues[v], "n": int(m.nobs), "r2": m.rsquared, "r2_ajustado": m.rsquared_adj}
                         for v in m.params.index])


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


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    for f in SAIDA.glob("*.csv"):
        f.unlink()
    val, sel, out, descr = especificacao()
    p, a, excl = carregar()
    print(f"painel {len(p)} -> amostra {len(a)}; concorreram {int(a['concorreu_reeleicao'].sum())}, "
          f"reeleitos {int(a['reeleito'].sum())}")
    print(f"variáveis aprovadas na validação: {descr}")

    t1 = tabela1(a, descr)
    t23 = teste_medias(a, descr)
    print("Heckman probit (variáveis aprovadas)...")
    m = heckprobit(a, sel, out)
    probit = probit_simples(a, out)

    t1.to_csv(SAIDA / "tabela1_concentracao.csv", index=False)
    t23.to_csv(SAIDA / "tabelas2_3_medias.csv", index=False)
    m["tabela"].to_csv(SAIDA / "tabela6_heckprobit.csv", index=False)
    probit["tabela"].to_csv(SAIDA / "nota24_probit_simples.csv", index=False)
    resumo = {
        "amostra": {"painel": len(p), "analise": len(a), "exclusoes": excl,
                    "concorreram": int(a["concorreu_reeleicao"].sum()), "reeleitos": int(a["reeleito"].sum()),
                    "cargo_disputado": a["cargo_disputado_2026"].value_counts().to_dict()},
        "especificacao": {"selecao": sel, "resultado": out, "descritivas": descr},
        "rotulos": ROTULOS, "tabela1": t1.to_dict("records"), "tabelas2_3": t23.to_dict("records"),
        "tabela6": {**{k: v for k, v in m.items() if k != "tabela"}, "coefs": m["tabela"].to_dict("records")},
        "probit_simples": {"n": probit["n"], "pseudo_r2": probit["pseudo_r2"],
                           "coefs": probit["tabela"].to_dict("records")},
    }
    (SAIDA / "resultados.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=1, default=float))
    print(f"  n={m['n']} sel={m['n_selecionados']} rho={m['rho']:.3f} LR={m['lr_rho0']:.2f} p={m['p_lr_rho0']:.3f}")
    print(f"resultados em {SAIDA}/")


if __name__ == "__main__":
    main()
