#!/usr/bin/env python3
"""
Gera data/budget.json a partir do orcamento aprovado.

O painel mostra uma camada so: o orcamento vigente, ja com as revisoes
aprovadas. A camada da planilha original foi retirada em 03/10/2026 por
decisao do Fred, para o painel comparar apenas orcado contra lancado.

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
    # chave, rotulo, grupo, natureza, vigente, nota
    dict(
        chave="pro_labore",
        rotulo="Pró-labore dos sócios",
        grupo="Pessoas",
        natureza="firme",
        vigente={**mensal(M26, 50225.46), **mensal(M27, 50400.00)},
        nota="Bruto mais INSS patronal. Compromisso firme.",
    ),
    dict(
        chave="folha_operacional",
        rotulo="Folha operacional",
        grupo="Pessoas",
        natureza="firme",
        vigente={**{m: 208110.95 for m in M27[:6]}, **{m: 215805.90 for m in M27[6:]}},
        nota="27 pessoas em VCP, REC, CNF e CWB. Promoção dos supervisores a partir de jul/27.",
    ),
    dict(
        chave="folha_admin",
        rotulo="Folha administrativa",
        grupo="Pessoas",
        natureza="firme",
        vigente=mensal(M27, 52631.77),
        nota="5 pessoas. Financeiro, RH e Administrativo.",
    ),
    # Um contrato por linha: o realizado e separado pelo codigo de integracao
    # de cada titulo, que ja carrega o nome do consultor.
    dict(
        chave="pj_karin",
        rotulo="Consultoria PJ · Karin Grunfeld",
        grupo="Pessoas",
        natureza="firme",
        vigente=mensal(M26, 3000.00),
        nota="Contrato PJ. Razão social e CNPJ ainda a confirmar no cadastro.",
    ),
    dict(
        chave="pj_lilian",
        rotulo="Consultoria PJ · Lilian Bordignon",
        grupo="Pessoas",
        natureza="firme",
        vigente=mensal(M26, 3000.00),
        nota="Contrato PJ. Razão social e CNPJ ainda a confirmar no cadastro.",
    ),
    dict(
        chave="pj_frota",
        rotulo="Consultoria PJ · Claudio Frota",
        grupo="Pessoas",
        natureza="firme",
        vigente=mensal(M26, 5000.00),
        nota="Contrato PJ. Razão social e CNPJ ainda a confirmar no cadastro.",
    ),
    dict(
        chave="ajuda_custo",
        rotulo="Ajuda de custo",
        grupo="Pessoas",
        natureza="firme",
        vigente=mensal(M26, 3000.00),
        nota="Criado em 02/10/2026. R$ 1.000 por consultor PJ, via cartão Flash.",
    ),
    dict(
        chave="turnover",
        rotulo="Turnover",
        grupo="Pessoas",
        natureza="firme",
        vigente={**{m: 7822.28 for m in M27[:6]}, **{m: 8053.13 for m in M27[6:]}},
        nota="3% sobre a folha mensal.",
    ),
    dict(
        chave="uniformes",
        rotulo="Uniformes e EPI",
        grupo="Operação",
        natureza="firme",
        vigente={**mensal(M26, 2000.00), **mensal(M27, 2666.67)},
        nota="Revisado em 03/10/2026: R$ 2.000 por mês em 2026. Em 2027 segue 1/12 de R$ 1.000 por pessoa ao ano.",
    ),
    # OPEX de 2026 aberto por componente: cada um tem titulo proprio no Omie,
    # identificado no codigo de integracao, entao o realizado cai na linha certa.
    dict(
        chave="opex_hospedagem",
        rotulo="Hospedagem",
        grupo="Operação",
        natureza="firme",
        vigente=mensal(M26, 9000.00),
        nota="Equipes em campo durante a implantação.",
    ),
    dict(
        chave="opex_alimentacao",
        rotulo="Alimentação",
        grupo="Operação",
        natureza="firme",
        vigente=mensal(M26, 3000.00),
        nota="",
    ),
    dict(
        chave="opex_transporte",
        rotulo="Transporte",
        grupo="Operação",
        natureza="firme",
        vigente=mensal(M26, 3000.00),
        nota="",
    ),
    dict(
        chave="opex_taxa_embarque",
        rotulo="Taxas de embarque",
        grupo="Operação",
        natureza="firme",
        vigente=mensal(M26, 1000.00),
        nota="",
    ),
    dict(
        chave="opex_credenciais",
        rotulo="Credenciais de acesso",
        grupo="Operação",
        natureza="firme",
        vigente=mensal(M26, 1000.00),
        nota="",
    ),
    dict(
        chave="opex",
        rotulo="OPEX de campo",
        grupo="Operação",
        natureza="firme",
        vigente=mensal(M27, 4000.00),
        nota="Em 2027 volta a ser uma linha só, com a operação já estabilizada. Em 2026 está aberta por componente nas linhas acima.",
    ),
    dict(
        chave="viagens",
        rotulo="Viagens operacionais",
        grupo="Operação",
        natureza="firme",
        vigente=mensal(M27, 8000.00),
        nota="",
    ),
    dict(
        chave="devices",
        rotulo="Equipamentos de campo",
        grupo="Operação",
        natureza="firme",
        vigente=mensal(M27, 25000.00),
        nota="Maior linha não-pessoal de 2027.",
    ),
    dict(
        chave="carros",
        rotulo="Veículos locados",
        grupo="Operação",
        natureza="firme",
        vigente=mensal(M27, 5000.00),
        nota="5 veículos.",
    ),
    dict(
        chave="aluguel",
        rotulo="Aluguel e ocupação",
        grupo="Operação",
        natureza="firme",
        vigente=mensal(M27, 8000.00),
        nota="",
    ),
    dict(
        chave="credenciamento",
        rotulo="Credenciamento aeroportuário",
        grupo="Operação",
        natureza="firme",
        vigente=mensal(M27, 3000.00),
        nota="",
    ),
    dict(
        chave="treinamentos",
        rotulo="Treinamentos de terceiros",
        grupo="Operação",
        natureza="firme",
        vigente=mensal(M27, 3000.00),
        nota="",
    ),
    dict(
        chave="ti_consultor",
        rotulo="Consultoria de TI · Luciano Mazzetto",
        grupo="Overhead",
        natureza="firme",
        vigente={"2026-10": 10000.00},
        nota="Mazzetto Desenvolvimento e Manutenção de Sistemas. Contrato PJ, out/26.",
    ),
    dict(
        chave="ti",
        rotulo="TI e software",
        grupo="Overhead",
        natureza="firme",
        vigente={
            "2026-10": 10000.00,  # Pacer parcela 3/3, antecipada
            "2026-11": 10000.00,  # Pacer parcela 1/3
            "2026-12": 10000.00,  # Pacer parcela 2/3
        },
        nota="Revisado em 03/10/2026: os R$ 30.000 do desenvolvimento da Pacer ficam inteiros em 2026, entre out e dez. Nenhuma despesa da PoC em 2027.",
    ),
    dict(
        chave="diversos",
        rotulo="Despesas administrativas diversas",
        grupo="Overhead",
        natureza="firme",
        vigente=mensal(M26, 240.00),
        nota="Criada em 03/10/2026 para absorver material de escritório, vale refeição e IOF, que até então apareciam como fora do orçamento. R$ 720 no trimestre, arredondado a partir dos R$ 715 já realizados. Não existe em 2027.",
    ),
    dict(
        chave="contabilidade",
        rotulo="Contabilidade",
        grupo="Overhead",
        natureza="firme",
        vigente={**mensal(M26, 2099.00), **mensal(M27, 2099.00)},
        nota="Revisado em 02/10/2026: mantido o contrato vigente da CDIX em vez dos R$ 6.500 do orçamento.",
    ),
    dict(
        chave="juridico",
        rotulo="Jurídico e propriedade intelectual",
        grupo="Overhead",
        natureza="firme",
        vigente={"2026-10": 1020.00, "2026-11": 1020.00},
        nota="Revisado em 02/10/2026: fora de 2027 por não haver contrato. Em 2026 são as parcelas 3/4 e 4/4 do Licks.",
    ),
    dict(
        chave="parceiros",
        rotulo="Parceiros estratégicos",
        grupo="Comercial",
        natureza="firme",
        vigente=mensal(M26, 23333.33),
        nota="Antonio Flávio Costa. R$ 70.000 no trimestre.",
    ),
    dict(
        chave="direito_imagem",
        rotulo="Direito de imagem",
        grupo="Comercial",
        natureza="firme",
        vigente={"2026-10": 9000.00, "2026-12": 9000.00,
                 "2027-10": 9000.00, "2027-12": 9000.00},
        nota="Revisado em 03/10/2026: duas parcelas por ano, em outubro e dezembro, R$ 3.000 para cada um. Flávio Costa, Roberto Hobeika e Rodrigo Cortes. Falta o documento do Rodrigo para cadastrar o terceiro.",
    ),
    dict(
        chave="lucros",
        rotulo="Distribuição de lucros",
        grupo="Sócios",
        natureza="condicionado",
        vigente=mensal(M26, 40000.00),
        nota="Condicionado a lucro apurado em balanço pela CDIX e ata de distribuição.",
    ),
    dict(
        chave="mutuo",
        rotulo="Mútuo dos sócios",
        grupo="Sócios",
        natureza="condicionado",
        vigente={"2026-10": 28814.55},
        nota="Saldo a devolver aos sócios. Condicionado a caixa.",
    ),
]

RECEITA = [
    dict(
        chave="receita_azul_implantacao",
        rotulo="Azul, implantação",
        vigente={"2026-10": 200000.00, "2026-11": 150000.00, "2026-12": 150000.00},
        nota="Fora do Omie até o contrato ser assinado.",
    ),
    dict(
        chave="receita_azul_recorrente",
        rotulo="Azul, recorrente",
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
    if SUPRIMIR_SIGILO:
        print("  %d linhas suprimidas por sigilo" % (len(LINHAS) - len(linhas)))
    print("budget.json gerado")
    print("  linhas de despesa : %d" % len(linhas))
    print("  total vigente     : R$ {:,.2f}".format(tv))


if __name__ == "__main__":
    main()
