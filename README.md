# Destaques por município (853 municípios de MG)

Gera `papers criados/paper-destaques-municipios.html`: um card por município, com busca por nome. Cada card abre a página "Entregas e Investimentos em Saúde" do município, com as seções, nesta ordem: Ponto de atenção (só quando houver), Principais entregas, Em tramitação, Comparativo entre governos e Investimento total. É um arquivo único, que funciona offline e sem JavaScript.

## Como atualizar
1. Troque as planilhas em `dados/` pelas novas versões, mantendo os mesmos nomes de arquivo e de aba.
2. Rode `python3 pipeline/destaques-municipios/build.py`. Precisa de `openpyxl`.
3. Confira os arquivos em `gerados/`:
   - `revisao.csv`: destaques automáticos que vale olhar (fracos, genéricos ou de valor baixo).
   - `pills_alteradas.csv`: municípios curados cuja pill de origem mudou pela regra.
4. Se o script avisar de um nome que não casa, acrescente a grafia em `ALIAS`, no arquivo `comum.py`.

## Regras
- **Principais entregas (já pagas):** aba CONSOLIDADO de `Monitoramento de Pleitos NGTPL.xlsx` (status PAGO), somada às emendas, convênios celebrados, UBS, UPA e hemodiálise da planilha da chefia de gabinete. Sem teto de linhas.
- **Em tramitação:** pleitos da aba CONSOLIDADO que não estão pagos, menos os SUSPENSO. Mostra objeto, beneficiário, valor ("Valor a definir" quando não houver), instrumento e status geral (Em tramitação ou Pré-tramitação). A coluna de status é achada pelo prefixo "STATUS", então a data no nome não importa.
- **Ponto de atenção:** `dados/Pontos de Atenção.xlsx`, aba `pontos_atencao` (colunas `cod_ibge`, `ponto_atencao`, `origem`, `data`, `exibir_no_paper`). Só linhas com "sim" aparecem; sem linha, a seção some. A aba `instruções` do arquivo explica o preenchimento.
- **Dívida FES, última parcela:** a linha aparece quando a aba ACORDO FES ganhar uma coluna com "parcela" no nome (valor) e outra com "parcela" e "data" (data). Hoje a aba só traz o pago acumulado.
- **Comparativo:** lido dos CSVs `Exercício_2022-2025 - APS.csv` e `... - Valora Minas.csv`.
- **Lista-mestre:** `dados/Regionalização PDR 2023.xlsx`, aba Plan1 (853 municípios).
- **Destaque:** a entrada manual de `curadoria.py`, se houver. Senão, Novo Centro de Hemodiálise (Apuração Física, R$ 4 mi). Senão, Construção de UBS. Senão, a ordem de `ORDEM` em `dados.py`, com UPA habilitada por último. Pró-Consórcios não entram.
- **Origem:** a pill mostra uma única origem, na ordem Convênio > Resolução > Emenda. Emenda aparece só quando não há outro instrumento.
- **Comparativo:** valores de 2015–2018 corrigidos pelo IPCA-E (fator 1,36151040).

## Arquivos
- `comum.py`: caminhos, normalização de nomes, lista-mestre e `ALIAS`.
- `dados.py`: leitura das planilhas e padronização das entregas.
- `curadoria.py`: destaques revisados à mão.
- `build.py`: monta os destaques e gera o HTML.
- `paginas.py`: HTML das páginas de município.
- `fonte.html`: o esqueleto da página.
- `assets/`: identidade SES-MG (fonte Inter e base.css).
