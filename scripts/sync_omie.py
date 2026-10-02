#!/usr/bin/env python3
"""
Le o Omie e grava data/actuals.json com o realizado ja agregado.

As credenciais vem SEMPRE do ambiente. Nunca escreva chave neste arquivo:
ele e publico.

    OMIE_APP_KEY      app key do aplicativo Omie
    OMIE_APP_SECRET   app secret do aplicativo Omie

No GitHub Actions os dois vem de Secrets do repositorio.

O arquivo gerado contem apenas numeros agregados por mes, linha de orcamento e
centro de custo. Nao exporta razao social de fornecedor, CNPJ, chave PIX, codigo
de barras nem o texto das observacoes, porque esses campos carregam dado bancario
e pessoal que nao precisa sair do ERP para alimentar um painel.
"""
import json, os, pathlib, sys, time, urllib.request, urllib.error
from collections import defaultdict
from datetime import datetime, timezone, timedelta

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "data" / "actuals.json"

APP_KEY = os.environ.get("OMIE_APP_KEY", "").strip()
APP_SECRET = os.environ.get("OMIE_APP_SECRET", "").strip()
BASE = "https://app.omie.com.br/api/v1/"
PAUSA = 1.6  # a API aceita uma chamada a cada 1,5 segundo

# as contas correntes sao lidas do Omie a cada execucao, nao fixadas aqui:
# a TAT abriu a conta do Inter em out/2026 e uma lista fixa deixaria o saldo
# dela fora do painel sem ninguem perceber

# categorias sob sigilo: pro-labore, distribuicao de lucros e mutuo dos socios.
# O Fred so divulga esses numeros depois de alinhar com o Podalka, entao o
# painel publicado nunca os carrega. SUPRIMIR_SIGILO controla isso e esta
# ligado por padrao: o repositorio e publico.
SIGILO = {"2.03.99", "2.03.94", "2.03.06", "2.08.98", "2.08.99"}
CONDICIONADO = {"2.08.98", "2.08.99"}
SUPRIMIR_SIGILO = os.environ.get("PAINEL_COMPLETO", "").strip().lower() not in ("1", "true", "sim")

# categoria do Omie -> linha do orcamento
CATEGORIA_LINHA = {
    "2.01.99": "folha_operacional",
    "2.01.98": "folha_operacional",
    "2.01.97": "folha_operacional",
    "2.01.95": "folha_operacional",
    "2.03.98": "folha_admin",
    "2.03.97": "folha_admin",
    "2.03.99": "pro_labore",
    "2.03.94": "pro_labore",
    "2.03.06": "pro_labore",
    "2.03.95": "consultores_pj",
    "2.01.92": "turnover",
    "2.01.94": "uniformes",
    "2.01.86": "viagens",
    "2.04.95": "opex",
    "2.04.96": "opex",
    "2.01.89": "devices",
    "2.01.87": "carros",
    "2.01.85": "aluguel",
    "2.04.01": "aluguel",
    "2.01.91": "credenciamento",
    "2.01.90": "treinamentos",
    "2.04.10": "contabilidade",
    "2.04.11": "juridico",
    "2.04.99": "juridico",
    "2.04.98": "ti",
    "2.02.99": "parceiros",
    "2.04.97": "direito_imagem",
    "2.08.98": "lucros",
    "2.08.99": "mutuo",
    "2.04.06": "outros",
    "2.03.12": "outros",
    "2.05.99": "outros",
    "2.05.04": "outros",
}


# cada consultor PJ tem contrato proprio, entao vira linha propria no painel.
# A categoria no Omie e a mesma para os tres; quem separa e o codigo de
# integracao do titulo, que ja carrega o nome.
PJ_POR_CODIGO = {"KARIN": "pj_karin", "LILI": "pj_lilian", "FROTA": "pj_frota"}


def linha_de(categoria, cod_integracao):
    """2.03.96 muda de significado entre 2026 e 2027, resolve pelo codigo."""
    ci = cod_integracao or ""
    if categoria == "2.03.96":
        return "folha_admin" if ci.startswith("F27ADM") else "ajuda_custo"
    if categoria == "2.04.98" and "CONSTI" in ci.upper():
        return "ti_consultor"
    if categoria == "2.03.95":
        for marca, linha in PJ_POR_CODIGO.items():
            if marca in ci.upper():
                return linha
        return "consultores_pj"
    return CATEGORIA_LINHA.get(categoria, "outros")


def call(servico, metodo, param):
    if not APP_KEY or not APP_SECRET:
        sys.exit(
            "OMIE_APP_KEY e OMIE_APP_SECRET precisam estar no ambiente.\n"
            "No GitHub Actions, cadastre os dois como Secrets do repositorio."
        )
    corpo = json.dumps(
        {"call": metodo, "app_key": APP_KEY, "app_secret": APP_SECRET, "param": [param]}
    ).encode()
    req = urllib.request.Request(
        BASE + servico + "/", data=corpo, headers={"Content-Type": "application/json"}
    )
    ultimo = None
    for tentativa in range(4):
        try:
            return json.load(urllib.request.urlopen(req, timeout=60))
        except urllib.error.HTTPError as e:
            try:
                r = json.loads(e.read().decode())
            except Exception:
                r = {}
            msg = r.get("faultstring", "") or ("HTTP %s" % e.code)
            if "REDUNDANT" in msg or "processada" in msg:
                time.sleep(30)
                continue
            # lista vazia e resposta legitima; o resto nao e
            if "nao existem registros" in _sem_acento(msg) or "nao foram encontrados" in _sem_acento(msg):
                return {}
            sys.exit(
                "O Omie recusou %s/%s: %s\n"
                "Se a mensagem fala de app_key, app_secret ou acesso negado, confira os\n"
                "Secrets do repositorio e se o aplicativo Omie tem restricao de IP: o\n"
                "GitHub Actions sai por um IP diferente do seu escritorio." % (servico, metodo, msg)
            )
        except Exception as e:
            ultimo = e
            time.sleep(5)
    sys.exit("O Omie nao respondeu %s/%s depois de 4 tentativas: %s" % (servico, metodo, ultimo))


def _sem_acento(s):
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", s.lower())
                   if unicodedata.category(c) != "Mn")


def paginar(servico, metodo, chave, por_pagina=200, campo_pag="pagina", campo_reg="registros_por_pagina", campo_total="total_de_paginas"):
    out, pg = [], 1
    while True:
        r = call(servico, metodo, {campo_pag: pg, campo_reg: por_pagina})
        out += r.get(chave, []) or []
        if pg >= (r.get(campo_total) or 1):
            break
        pg += 1
        time.sleep(PAUSA)
    return out


def mes(data_br):
    d = data_br.split("/")
    return d[2] + "-" + d[1]


def main():
    inicio = time.time()
    print("lendo o Omie...")

    deps = {
        str(d["codigo"]): d["descricao"]
        for d in call("geral/departamentos", "ListarDepartamentos", {"pagina": 1, "registros_por_pagina": 100}).get("departamentos", [])
    }
    time.sleep(PAUSA)
    rcc = call("geral/contacorrente", "ListarContasCorrentes", {"pagina": 1, "registros_por_pagina": 100})
    contas = {
        c["nCodCC"]: {"nome": c.get("descricao") or str(c["nCodCC"]),
                      "tipo": c.get("tipo_conta_corrente"),
                      "inativa": c.get("inativo") == "S"}
        for c in (rcc.get("ListarContasCorrentes") or rcc.get("conta_corrente_cadastro") or [])
    }
    time.sleep(PAUSA)
    pagar = paginar("financas/contapagar", "ListarContasPagar", "conta_pagar_cadastro")
    time.sleep(PAUSA)
    receber = paginar("financas/contareceber", "ListarContasReceber", "conta_receber_cadastro")
    time.sleep(PAUSA)
    lancamentos = paginar(
        "financas/contacorrentelancamentos", "ListarLancCC", "listaLancamentos",
        campo_pag="nPagina", campo_reg="nRegPorPagina", campo_total="nTotPaginas",
    )
    print("  %d titulos a pagar, %d a receber, %d lancamentos de conta" % (len(pagar), len(receber), len(lancamentos)))

    # trava de sanidade. Uma leitura que volta vazia nao e um painel zerado:
    # e uma leitura que falhou. Gravar zero por cima do arquivo bom esconde o
    # problema e o painel passa a mentir, entao o certo e abortar e manter o
    # arquivo anterior.
    if not pagar:
        sys.exit(
            "ABORTADO: o Omie respondeu sem nenhum titulo a pagar.\n"
            "Esta conta nunca fica sem titulos, entao isso e falha de leitura e nao\n"
            "ausencia de dado. O data/actuals.json anterior foi preservado."
        )

    # ------------------------------------------------------------------ sigilo
    # Pro-labore, distribuicao de lucros e mutuo dos socios nao saem daqui.
    # A supressao e feita na origem, removendo os titulos antes de qualquer
    # agregacao: assim nenhum total, centro de custo ou natureza carrega esses
    # valores, nem permite deduzi-los por subtracao. O painel passa a fechar
    # consigo mesmo, nao com o Omie, e diz isso na tela.
    suprimidos = [t for t in pagar if (t.get("codigo_categoria") or "") in SIGILO
                  and t.get("status_titulo") != "CANCELADO"]
    if SUPRIMIR_SIGILO:
        pagar = [t for t in pagar if (t.get("codigo_categoria") or "") not in SIGILO]
        print("  %d titulos suprimidos por sigilo (pro-labore, lucros e mutuo)" % len(suprimidos))

    # ------------------------------------------------- realizado por linha e mes
    por_linha = defaultdict(lambda: defaultdict(float))
    por_centro = defaultdict(lambda: defaultdict(float))
    por_natureza = defaultdict(lambda: defaultdict(float))
    detalhe_cc = {}

    for t in pagar:
        if t.get("status_titulo") == "CANCELADO":
            continue
        cat = t.get("codigo_categoria") or ""
        ci = t.get("codigo_lancamento_integracao") or ""
        v = float(t.get("valor_documento") or 0)
        m = mes(t["data_vencimento"])
        linha = linha_de(cat, ci)
        por_linha[linha][m] += v

        provisao = (t.get("codigo_tipo_documento") == "PROV")
        if cat in CONDICIONADO:
            nat = "condicionado"
        elif provisao:
            nat = "provisao"
        else:
            nat = "firme"
        por_natureza[nat][m] += v

    # centro de custo exige consultar titulo a titulo
    print("  lendo centro de custo...")
    for i, t in enumerate(pagar, 1):
        if t.get("status_titulo") == "CANCELADO":
            continue
        q = call("financas/contapagar", "ConsultarContaPagar", {"codigo_lancamento_omie": t["codigo_lancamento_omie"]})
        m = mes(t["data_vencimento"])
        for d in (q.get("distribuicao") or []):
            nome = d.get("cDesDep") or deps.get(str(d.get("cCodDep")), "sem centro de custo")
            por_centro[nome][m] += float(d.get("nValDep") or 0)
            detalhe_cc[nome] = d.get("cCodDep")
        if not (q.get("distribuicao") or []):
            por_centro["sem centro de custo"][m] += float(t.get("valor_documento") or 0)
        time.sleep(0.8)
        if i % 50 == 0:
            print("    %d de %d" % (i, len(pagar)))

    # ------------------------------------------------------------- contas a pagar
    status = defaultdict(lambda: defaultdict(float))
    for t in pagar:
        s = (t.get("status_titulo") or "").lower()
        status[s][mes(t["data_vencimento"])] += float(t.get("valor_documento") or 0)

    # ------------------------------------------------------------------- caixa
    saldos = defaultdict(float)
    extrato = defaultdict(list)
    for l in lancamentos:
        c = l.get("cabecalho", {})
        cc = c.get("nCodCC")
        nat = (l.get("diversos") or {}).get("cNatureza", "P")
        v = float(c.get("nValorLanc") or 0)
        v = v if nat == "R" else -v
        saldos[cc] += v
        extrato[cc].append({"data": c.get("dDtLanc"), "valor": round(v, 2)})

    # ------------------------------------------------------------------ receber
    receber_resumo = defaultdict(lambda: defaultdict(float))
    for t in receber:
        s = (t.get("status_titulo") or "").lower()
        receber_resumo[s][mes(t["data_vencimento"])] += float(t.get("valor_documento") or 0)

    agora = datetime.now(timezone(timedelta(hours=-3)))
    doc = {
        "gerado_em": agora.isoformat(timespec="seconds"),
        "fonte": "API Omie, conta TAT OPERATING LTDA",
        "titulos": {"a_pagar": len(pagar), "a_receber": len(receber), "lancamentos": len(lancamentos)},
        "sigilo": {
            "ativo": SUPRIMIR_SIGILO,
            "titulos_suprimidos": len(suprimidos) if SUPRIMIR_SIGILO else 0,
            "o_que": "pró-labore dos sócios, distribuição de lucros e mútuo dos sócios",
            "por_que": "só divulgados após alinhamento entre os sócios; nenhum valor sai neste arquivo",
        },
        "realizado_por_linha": {k: {m: round(v, 2) for m, v in sorted(d.items())} for k, d in sorted(por_linha.items())},
        "realizado_por_centro": {k: {m: round(v, 2) for m, v in sorted(d.items())} for k, d in sorted(por_centro.items())},
        "por_natureza": {k: {m: round(v, 2) for m, v in sorted(d.items())} for k, d in sorted(por_natureza.items())},
        "contas_a_pagar_por_status": {k: {m: round(v, 2) for m, v in sorted(d.items())} for k, d in sorted(status.items())},
        "contas_a_receber_por_status": {k: {m: round(v, 2) for m, v in sorted(d.items())} for k, d in sorted(receber_resumo.items())},
        "saldos": {
            # conta corrente ativa aparece mesmo zerada: a do Inter nasceu em
            # out/2026 sem movimento, e some-la do painel seria esconder que ela
            # existe. Cartao e caixinha so entram se tiverem saldo.
            "por_conta": [
                {"nome": c["nome"], "saldo": round(saldos.get(cc, 0.0), 2)}
                for cc, c in sorted(contas.items(), key=lambda x: -abs(saldos.get(x[0], 0.0)))
                if (c["tipo"] == "CC" and not c["inativa"]) or round(saldos.get(cc, 0.0), 2)
            ],
            "total": round(sum(saldos.values()), 2),
        },
        "centros_de_custo": detalhe_cc,
    }

    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print("actuals.json gerado em %.0fs" % (time.time() - inicio))
    for c in doc["saldos"]["por_conta"]:
        print("  {:<28} R$ {:>12,.2f}".format(c["nome"], c["saldo"]))


if __name__ == "__main__":
    main()
