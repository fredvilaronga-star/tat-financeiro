#!/usr/bin/env python3
"""
Trava de seguranca. Roda no CI depois do sync e antes do commit.

Falha o workflow se o JSON publicado contiver qualquer coisa que nao deveria
sair do ERP: credencial da API, CNPJ, CPF, chave PIX, codigo de barras, linha
digitavel ou IBAN. O painel vive num repositorio que pode ficar publico, entao
a verificacao e automatica e nao depende de alguem lembrar.
"""
import json, os, pathlib, re, sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
ALVOS = [RAIZ / "data" / "actuals.json", RAIZ / "data" / "budget.json"]

SEGREDOS = [v for v in (os.environ.get("OMIE_APP_KEY"), os.environ.get("OMIE_APP_SECRET")) if v]

PADROES = [
    ("CNPJ", re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b")),
    ("CPF", re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b")),
    ("linha digitável de boleto", re.compile(r"\b\d{5}\.\d{5}\s+\d{5}\.\d{6}\s+\d{5}\.\d{6}\b")),
    ("código de barras", re.compile(r"\b\d{44,48}\b")),
    ("payload PIX copia e cola", re.compile(r"\b0002012[0-9]{20,}")),
    ("IBAN", re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b")),
]


# o repositorio e publico: pro-labore, lucros e mutuo nao podem estar nos
# arquivos, em nenhuma das tres formas em que apareceriam
CHAVES_SIGILO = ["pro_labore", "lucros", "mutuo"]
CENTROS_SIGILO = ["Diretoria e Sócios"]
NATUREZA_SIGILO = ["condicionado"]


def checar_sigilo(doc, nome):
    """Falha se o arquivo publicado carregar valor sob sigilo."""
    out = []
    for secao in ("realizado_por_linha", "despesas"):
        d = doc.get(secao)
        if isinstance(d, dict):
            achadas = [k for k in CHAVES_SIGILO if k in d]
        elif isinstance(d, list):
            achadas = [l.get("chave") for l in d if l.get("chave") in CHAVES_SIGILO]
        else:
            continue
        for k in achadas:
            out.append("%s: linha sob sigilo publicada em %s (%s)" % (nome, secao, k))
    for centro in (doc.get("realizado_por_centro") or {}):
        for s in CENTROS_SIGILO:
            if s in centro:
                out.append("%s: centro de custo sob sigilo publicado (%s)" % (nome, centro))
    for nat in (doc.get("por_natureza") or {}):
        if nat in NATUREZA_SIGILO:
            out.append("%s: natureza sob sigilo publicada (%s)" % (nome, nat))
    if "sigilo" in doc and doc["sigilo"].get("ativo") is not True:
        out.append("%s: a supressão de sigilo está desligada" % nome)
    return out


def main():
    problemas = []
    for alvo in ALVOS:
        if not alvo.exists():
            continue
        texto = alvo.read_text(encoding="utf-8")

        for s in SEGREDOS:
            if s and s in texto:
                problemas.append("%s: credencial da API Omie encontrada no arquivo" % alvo.name)

        for nome, rx in PADROES:
            achados = rx.findall(texto)
            if achados:
                problemas.append("%s: %s (%d ocorrência%s)" % (alvo.name, nome, len(achados), "s" if len(achados) > 1 else ""))

        # o JSON so deve ter numeros agregados: nenhuma chave de texto longo
        try:
            doc = json.loads(texto)
        except json.JSONDecodeError as e:
            problemas.append("%s: JSON inválido (%s)" % (alvo.name, e))
            continue
        for s in textos_longos(doc):
            problemas.append("%s: texto livre de %d caracteres onde só deveria haver número agregado" % (alvo.name, len(s)))
        problemas += checar_sigilo(doc, alvo.name)

    if problemas:
        print("TRAVA DE SEGURANÇA: o arquivo gerado não pode ser publicado.")
        for p in problemas:
            print("  -", p)
        sys.exit(1)
    print("trava de segurança: nada sensível nos arquivos de dados")


def textos_longos(no, limite=400):
    """Observacao de titulo do Omie e longa e carrega dado de pagamento."""
    if isinstance(no, str):
        if len(no) > limite:
            yield no
    elif isinstance(no, dict):
        for v in no.values():
            yield from textos_longos(v, limite)
    elif isinstance(no, list):
        for v in no:
            yield from textos_longos(v, limite)


if __name__ == "__main__":
    main()
