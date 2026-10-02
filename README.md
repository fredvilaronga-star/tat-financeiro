# TAT Operating · painel financeiro

Painel de orçado contra realizado da TAT, alimentado pela API do Omie.

O desenho é o mais simples que resolve: um script lê o Omie, agrega os números e
grava dois arquivos JSON no próprio repositório; a página é HTML estático que lê
esses arquivos. Não há servidor, não há banco, e nenhuma credencial do Omie passa
pelo navegador.

```
Omie  ──(GitHub Actions, 2x por dia)──>  data/actuals.json  ──>  index.html
planilha do orçamento ──(rodado à mão)──>  data/budget.json  ──>
```

## O que o painel mostra

| Bloco | Conteúdo |
|---|---|
| Indicadores | saldo das duas contas, compromisso firme, condicionado a lucro e provisão orçamentária |
| Orçado contra realizado | mês a mês, orçamento vigente contra o que está lançado no Omie |
| Linha a linha | 21 linhas de despesa, com a coluna v9.3 (orçamento original) ao lado da vigente, e o desvio |
| Centro de custo | rateio registrado em cada título, do maior para o menor |
| Compromisso por natureza | firme, condicionado a lucro e provisão orçamentária, empilhados por mês |
| Situação dos títulos | a pagar e a receber por status, inclusive cancelados |

O filtro de período no topo vale para a página inteira.

### As três naturezas

A distinção é o que separa o que vai ser pago do que é só planejamento, e ela
está no Omie, não no painel:

- **firme** — título com documento fiscal ou contrato. Vence e vai para aprovação.
- **condicionado a lucro** — distribuição de lucros e mútuo dos sócios. Só sai com
  balanço apurado pela CDIX e ata de distribuição.
- **provisão orçamentária** — título com tipo de documento `PROV`, sem documento
  fiscal, lançado para que o orçamento apareça no fluxo de caixa. **Nunca vai para
  aprovação de pagamento.** É a maior parte de 2027 e é por isso que, naquele ano,
  a barra do realizado quase coincide com a do orçado.

## Arquivos

```
index.html                     o painel (sem dependência externa, SVG na mão)
data/budget.json               orçamento, duas camadas: v9_3 e vigente
data/actuals.json              realizado agregado, gerado pelo Actions
scripts/build_budget.py        gera budget.json a partir do orçamento aprovado
scripts/sync_omie.py           lê o Omie e gera actuals.json
scripts/check_leak.py          trava de segurança, roda antes de todo commit
.github/workflows/sync-omie.yml
```

## Como colocar no ar

1. **Criar o repositório.** Privado.

2. **Cadastrar as credenciais.** Em *Settings → Secrets and variables → Actions →
   New repository secret*, dois segredos:

   | Nome | Valor |
   |---|---|
   | `OMIE_APP_KEY` | app key do aplicativo Omie |
   | `OMIE_APP_SECRET` | app secret do aplicativo Omie |

   Nenhum dos dois pode aparecer em arquivo versionado. O `check_leak.py` falha o
   workflow se encontrar qualquer um deles dentro do JSON gerado.

3. **Publicar a página.** *Settings → Pages → Source: Deploy from a branch →
   `main` / root*. Leia a seção de acesso abaixo antes de fazer isso.

4. **Rodar a primeira sincronização.** Aba *Actions → Sincronizar Omie → Run
   workflow*. Leva por volta de 10 minutos, porque o centro de custo só vem na
   consulta título a título e a API aceita uma chamada por segundo e meio.

Depois disso o workflow roda sozinho às 13h e às 17h15 de Brasília, em dias úteis,
logo depois das rotinas financeiras das 12h e das 16h15.

## Este repositório é público, e por isso o painel é incompleto

No plano gratuito o GitHub Pages não funciona em repositório privado: ou o
repositório é público, ou não há página. A TAT optou pelo repositório público, e a
contrapartida é que três linhas não saem daqui.

**Fora do painel:** pró-labore dos sócios, distribuição de lucros e mútuo dos
sócios. Por decisão dos sócios, esses valores só circulam depois de alinhados entre
eles.

A supressão acontece **na origem**, em `sync_omie.py`: os títulos dessas categorias
são removidos antes de qualquer agregação. Com isso nenhum total, centro de custo ou
natureza os contém, e eles também não podem ser deduzidos por subtração. O centro
"1.01 Diretoria e Sócios" desaparece junto, porque é composto quase inteiramente por
eles, e o mesmo vale para a natureza "condicionado a lucro". O `build_budget.py`
remove as mesmas linhas do orçado, senão o valor planejado entregaria o realizado.

O painel **fecha consigo mesmo, não com o Omie**, e diz isso na tela.

O `check_leak.py` falha o workflow se qualquer uma dessas linhas, o centro de custo
ou a natureza aparecerem nos arquivos publicados. A trava é automática para não
depender de alguém lembrar.

### Rodar com os números completos

Para uso interno, fora do GitHub:

```bash
PAINEL_COMPLETO=1 python3 scripts/build_budget.py
PAINEL_COMPLETO=1 OMIE_APP_KEY=... OMIE_APP_SECRET=... python3 scripts/sync_omie.py
python3 -m http.server 8777
```

Os arquivos gerados assim **não podem ser commitados**: o `check_leak.py` recusa.

## Manutenção

**Mudou o orçamento.** Editar a lista `LINHAS` em `scripts/build_budget.py`, com a
nota explicando a revisão e a data, e rodar `python3 scripts/build_budget.py`. A
camada `v9_3` nunca muda: ela é o registro do que foi aprovado originalmente, e é o
que permite responder depois por que um número é diferente do da planilha.

**Criou categoria nova no Omie.** Acrescentar o código em `CATEGORIA_LINHA` dentro
de `scripts/sync_omie.py`. Categoria não mapeada cai em `outros` e aparece no painel
no bloco "Fora do orçamento" — de propósito, para que o buraco apareça em vez de
sumir.

**Criou centro de custo novo.** Nada a fazer: o script lê os departamentos do Omie a
cada execução.

## O que não sai do ERP

O `actuals.json` tem apenas números agregados por mês, linha de orçamento e centro
de custo. Não exporta razão social de fornecedor, CNPJ, chave PIX, código de barras
nem o texto das observações dos títulos, porque esses campos carregam dado bancário
e pessoal que não precisa sair do Omie para alimentar um painel.

O `check_leak.py` roda no CI depois do sync e antes do commit, e falha o workflow se
encontrar credencial da API, CNPJ, CPF, linha digitável, código de barras, payload
PIX, IBAN ou qualquer texto livre acima de 400 caracteres. A verificação é
automática justamente para não depender de alguém lembrar.
