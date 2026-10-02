#!/usr/bin/env python3
"""
Gera data/budget.json a partir do orcamento aprovado.

O orcado tem duas camadas, e o painel mostra as duas:
  v9_3      orcamento original da planilha TAT_Orcamento_GOL_AZUL_v9_3
  vigente   o orcamento depois das revisoes aprovadas pelo Fred

Rodar so quando o orcamento mudar. O resultado e versionado no repositorio,
para que qualquer pessoa consiga reproduzir de onde veio cada numero.
"""
import json, os, pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "data" / "budget.json"

# As mesmas linhas que o sync suprime do realizado precisam sair do orcado,
# senao o painel publica o valor planejado de pro-labore, lucros e mutuo e o
# sigilo nao serve para nada. Ligado por padrao: o repositorio e publico.
SIGILO = {"pro_labore", "lucros", "mutuo"}
SUPRIMIR_SIGILO = os.environ.get("PAINEL_COMPLETO", "").strip().lower() not in ("1", "true", "sim")

M26 = ["2026-10", "2026-11", "2026-12"]
M27 = ["2027-%02d" % i for i in range(1, 13)]


def mensal(meses, valor):
    return {m: round(valor, 2) for m in meses}


def serie(**kw):
    s = {}
    for meses, valor in kw.items():
        pass
    return s


# ---------------------------------------------------------------- orcamento
LINHAS = [
    # chave, rotulo, grupo, v9_3, vigente
    dict(
        chave="pro_labore",
        rotulo="Pró-labore dos sócios",
        grupo="Pessoas",
        natureza="firme",
        v9_3={**mensal(M26, 50225.46), **mensal(M27, 50400.00)},
        vigente={**mensal(M26, 50225.46), **mensal(M27, 50400.00)},
        nota="Bruto mais INSS patronal. Compromisso firme.",
    ),
    dict(
        chave="folha_operacional",
        rotulo="Folha operacional",
        grupo="Pessoas",
        natureza="firme",
        v9_3={**{m: 208110.95 for m in M27[:6]}, **{m: 215805.90 for m in M27[6:]}},
        vigente={**{m: 208110.95 for m in M27[:6]}, **{m: 215805.90 for m in M27[6:]}},
        nota="27 pessoas em VCP, REC, CNF e CWB. Promoção dos supervisores a partir de jul/27.",
    ),
    dict(
        chave="folha_admin",
        rotulo="Folha administrativa",
        grupo="Pessoas",
        natureza="firme",
        v9_3=mensal(M27, 52631.77),
        vigente=mensal(M27, 52631.77),
        nota="5 pessoas. Financeiro, RH e Administrativo.",
    ),
    dict(
        chave="consultores_pj",
        rotulo="Consultores PJ",
        grupo="Pessoas",
        natureza="firme",
        v9_3=mensal(M26, 20000.00),
        vigente=mensal(M26, 11000.00),
        nota="Revisado em 02/10/2026: Karin 3.000, Lili 3.000 e Claudio Frota 5.000.",
    ),
    dict(
        chave="ajuda_custo",
        rotulo="Ajuda de custo",
        grupo="Pessoas",
        natureza="firme",
        v9_3={},
        vigente=mensal(M26, 3000.00),
        nota="Criado em 02/10/2026. R$ 1.000 por consultor PJ, via cartão Flash.",
    ),
    dict(
        chave="turnover",
        rotulo="Turnover",
        grupo="Pessoas",
        natureza="firme",
        v9_3={**{m: 7822.28 for m in M27[:6]}, **{m: 8053.13 for m in M27[6:]}},
        vigente={**{m: 7822.28 for m in M27[:6]}, **{m: 8053.13 for m in M27[6:]}},
        nota="3% sobre a folha mensal.",
    ),
    dict(
        chave="uniformes",
        rotulo="Uniformes e EPI",
        grupo="Operação",
        natureza="firme",
        v9_3=mensal(M27, 2666.67),
        vigente=mensal(M27, 2666.67),
        nota="1/12 de R$ 1.000 por pessoa ao ano.",
    ),
    dict(
        chave="opex",
        rotulo="OPEX de campo",
        grupo="Operação",
        natureza="firme",
        v9_3={**mensal(M26, 10000.00), **mensal(M27, 4000.00)},
        vigente={**mensal(M26, 17000.00), **mensal(M27, 4000.00)},
        nota="Revisado em 02/10/2026: hospedagem 9.000, alimentação 3.000, transporte 3.000, taxa de embarque 1.000 e credenciais 1.000.",
    ),
    dict(
        chave="viagens",
        rotulo="Viagens operacionais",
        grupo="Operação",
        natureza="firme",
        v9_3=mensal(M27, 8000.00),
        vigente=mensal(M27, 8000.00),
        nota="",
    ),
    dict(
        chave="devices",
        rotulo="Equipamentos de campo",
        grupo="Operação",
        natureza="firme",
        v9_3=mensal(M27, 25000.00),
        vigente=mensal(M27, 25000.00),
        nota="Maior linha não-pessoal de 2027.",
    ),
    dict(
        chave="carros",
        rotulo="Veículos locados",
        grupo="Operação",
        natureza="firme",
        v9_3=mensal(M27, 5000.00),
        vigente=mensal(M27, 5000.00),
        nota="5 veículos.",
    ),
    dict(
        chave="aluguel",
        rotulo="Aluguel e ocupação",
        grupo="Operação",
        natureza="firme",
        v9_3=mensal(M27, 8000.00),
        vigente=mensal(M27, 8000.00),
        nota="",
    ),
    dict(
        chave="credenciamento",
        rotulo="Credenciamento aeroportuário",
        grupo="Operação",
        natureza="firme",
        v9_3=mensal(M27, 3000.00),
        vigente=mensal(M27, 3000.00),
        nota="",
    ),
    dict(
        chave="treinamentos",
        rotulo="Treinamentos de terceiros",
        grupo="Operação",
        natureza="firme",
        v9_3=mensal(M27, 3000.00),
        vigente=mensal(M27, 3000.00),
        nota="",
    ),
    dict(
        chave="ti",
        rotulo="TI e software",
        grupo="Overhead",
        natureza="firme",
        v9_3={**mensal(M26, 13333.33), **mensal(M27, 10000.00)},
        vigente={
            "2026-10": 10000.00,  # consultor Luciano Mazzetto
            "2026-11": 10000.00,  # Pacer parcela 1/3
            "2026-12": 10000.00,  # Pacer parcela 2/3
            **mensal(M27, 10000.00),
        },
        nota="Revisado em 02/10/2026: out é consultor de TI; nov, dez e jan são as parcelas do desenvolvimento da Pacer; de fev/27 em diante depende da segunda minuta.",
    ),
    dict(
        chave="contabilidade",
        rotulo="Contabilidade",
        grupo="Overhead",
        natureza="firme",
        v9_3=mensal(M27, 6500.00),
        vigente={**mensal(M26, 2099.00), **mensal(M27, 2099.00)},
        nota="Revisado em 02/10/2026: mantido o contrato vigente da CDIX em vez dos R$ 6.500 do orçamento.",
    ),
    dict(
        chave="juridico",
        rotulo="Jurídico e propriedade intelectual",
        grupo="Overhead",
        natureza="firme",
        v9_3=mensal(M27, 6500.00),
        vigente={"2026-10": 1020.00, "2026-11": 1020.00},
        nota="Revisado em 02/10/2026: fora de 2027 por não haver contrato. Em 2026 são as parcelas 3/4 e 4/4 do Licks.",
    ),
    dict(
        chave="parceiros",
        rotulo="Parceiros estratégicos",
        grupo="Comercial",
        natureza="firme",
        v9_3=mensal(M26, 23333.33),
        vigente=mensal(M26, 23333.33),
        nota="Antonio Flávio Costa. R$ 70.000 no trimestre.",
    ),
    dict(
        chave="direito_imagem",
        rotulo="Direito de imagem",
        grupo="Comercial",
        natureza="firme",
        v9_3={},
        vigente={"2026-11": 6000.00},
        nota="Flávio Costa e Roberto Hobeika, R$ 3.000 cada. Falta o CPF do Rodrigo Cortes para o terceiro.",
    ),
    dict(
        chave="lucros",
        rotulo="Distribuição de lucros",
        grupo="Sócios",
        natureza="condicionado",
        v9_3=mensal(M26, 40000.00),
        vigente=mensal(M26, 40000.00),
        nota="Condicionado a lucro apurado em balanço pela CDIX e ata de distribuição.",
    ),
    dict(
        chave="mutuo",
        rotulo="Mútuo dos sócios",
        grupo="Sócios",
        natureza="condicionado",
        v9_3={},
        vigente={"2026-10": 28814.55},
        nota="Saldo a devolver aos sócios. Condicionado a caixa.",
    ),
]

RECEITA = [
    dict(
        chave="receita_azul_implantacao",
        rotulo="Azul, implantação",
        v9_3={"2026-10": 200000.00, "2026-11": 150000.00, "2026-12": 150000.00},
        vigente={"2026-10": 200000.00, "2026-11": 150000.00, "2026-12": 150000.00},
        nota="Fora do Omie até o contrato ser assinado.",
    ),
    dict(
        chave="receita_azul_recorrente",
        rotulo="Azul, recorrente",
        v9_3=mensal(M27, 746866.67),
        vigente=mensal(M27, 746866.67),
        nota="Saving share de 34,95%. Fora do Omie até o contrato ser assinado.",
    ),
]


def main():
    linhas = [l for l in LINHAS if not (SUPRIMIR_SIGILO and l["chave"] in SIGILO)]
    doc = {
        "gerado_em": None,
        "sigilo": {
            "ativo": SUPRIMIR_SIGILO,
            "linhas_suprimidas": sorted(SIGILO) if SUPRIMIR_SIGILO else [],
        },
        "fonte": "TAT_Orcamento_GOL_AZUL_v9_3.xlsx, abas Resumo 2026 e Resumo 2027, com as revisões aprovadas pelo Fred em 02/10/2026",
        "meses": M26 + M27,
        "retencao_nf": 0.0815,
        "lucro_presumido": 0.1333,
        "despesas": linhas,
        "receitas": RECEITA,
    }
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")

    tv = sum(sum(l["vigente"].values()) for l in linhas)
    t9 = sum(sum(l["v9_3"].values()) for l in linhas)
    if SUPRIMIR_SIGILO:
        print("  %d linhas suprimidas por sigilo" % (len(LINHAS) - len(linhas)))
    print("budget.json gerado")
    print("  linhas de despesa : %d" % len(linhas))
    print("  total v9.3        : R$ {:,.2f}".format(t9))
    print("  total vigente     : R$ {:,.2f}".format(tv))


if __name__ == "__main__":
    main()
