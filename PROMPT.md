# Prompt — paper visual de destaques (formato "Destaques da Saúde")

> Cole este prompt no início da conversa, anexe as imagens do Figma (fonte, cores, cards, gráficos) e indique a fonte de dados. Referência viva do formato: `papers criados/paper-destaques-secretario.html` e o gerador em `pipeline/paper-secretario/` (`geo.py`, `build.py`, `fonte.html`).

---

Preciso de um paper visual para **[autoridade]** sobre **[temas]**. A fonte principal é **[arquivo]**. Use a skill `paper-dados-saude-ses` para o fluxo de trabalho (ler tudo, perguntar antes de produzir), mas **a identidade visual e o formato são os descritos abaixo, que prevalecem sobre a skill**.

## 1. Antes de produzir
- Me entreviste primeiro sobre formato, ênfase de cada tema e o marco de comparação.
- Leia a fonte inteira e cruze com as planilhas de `dados/`. Traga, numa lista numerada com uma sugestão para cada ponto, os números que não batem, os dados que faltam e as manchetes que os dados não sustentam. Não invente dado e não some valores que se sobrepõem.
- Depois de entregar, diga o que você presumiu ou calculou.

## 2. Entrega
- **Um único HTML autocontido**, sem CDN: fonte Inter embutida (`pipeline/destaques-municipios/assets/inter-inline.css`) e mapas embutidos.
- **Pensado primeiro para celular**: coluna de no máximo 480 px e margem lateral de 16 px.
- Gerado por script (template + build), com commit no repositório.

## 3. Identidade visual (Figma)
- **Fonte:** Inter. Black (900) para títulos e números, ExtraBold/Bold para botões e rótulos, Medium (500) para o texto.
- **Cores:**

  | Papel | Cor | Degradê |
  |---|---|---|
  | Verde | `#8DC63F` | → `#4F7A24` |
  | Azul | `#007FB6` | → `#005B8E` |
  | Laranja | `#F58220` | → `#D96C14` |
  | Azul-claro | `#60A5FA` | — |
  | Vermelho | `#EF4444` | — |

  Cinzas: `#CBD5E1`, `#F1F5F9` (fundo) e o texto em `#445266` / `#212C3E`.
- **Uma cor por tema**, alternando entre verde, laranja e azul.
- **Cards (Figma):** cabeçalho em degradê com um quadrado de ícone translúcido (vidro), mais a versão "menos destaque", com cabeçalho na cor clara do tema e título na cor escura. Cantos de 20 px e sombra suave.
- **Anel de progresso** ("215 de 445") sobre um bloco claro, ao lado de blocos de número.
- **Ícones** em linha (estilo Lucide), desenhados em SVG dentro do arquivo.

## 4. Estrutura
1. **Cabeçalho principal só com o título** (ex.: "Destaques da Saúde"), sem subtítulo nem selo.
2. **Menu de temas** fixo no topo, com rolagem lateral, que destaca o tema visível.
3. **Cada tema:** um cabeçalho com ícone e nome (sem "Tema 01", sem subtítulo, sem "marco zero"), seguido de cards.
4. Rodapé simples, **sem lista de fontes**.

## 5. Texto
- **Gráficos e mapas são o principal**; o texto só complementa.
- **Não use blocos de texto soltos.** Cada frase fica dentro do card que ela explica. Exemplos: a frase sobre cobertura vai logo abaixo do mapa de cobertura; o contexto das obras paradas abre o card das obras.
- O desafio entra só para dar contexto e o foco fica nos avanços. Tom direto, de briefing.
- Termos técnicos ganham uma definição curta em destaque (ex.: "Custeio hospitalar é…").

## 6. Gráficos
- **Toda comparação antes × depois é um par de barras verticais lado a lado no mesmo gráfico**, largas e na largura toda do card, com o valor em cima e o rótulo embaixo. A barra de "antes" fica cinza e a de "depois" na cor do tema. Embaixo, um selo centralizado com o ganho ("3,9× mais", "+655 leitos").
- **Nunca coloque dois gráficos lado a lado.** Várias comparações ficam uma embaixo da outra, cada uma com seu título curto, em uma linha, centralizado.
- **Séries anuais** em colunas verticais. Ano parcial ou valor de outra fonte leva hachura.
- **A altura da barra é proporcional ao valor** (escala real, a partir do zero). Nada de barra horizontal "100%" nem de largura mínima que distorça a escala.
- Uma composição do total (ex.: 6/9/13) vai numa barra empilhada, com legenda.

## 7. Mapas (MG)
- Malha municipal do IBGE simplificada, com as macrorregiões montadas a partir da regionalização do PDR (`geo.py`).
- **Interativos**: tocar numa região ou ponto mostra um cartão com o nome e os números.
- Tipos já prontos:
  - mapa coroplético por município;
  - pontos por status (gotas para hemodiálise, alfinetes para hospitais);
  - mapa de macros com seletor de ano (2018 | 2025);
  - lista "antes → depois" por macro.

## 8. Hierarquia, simetria e tipografia
- **Hierarquia:** o cabeçalho de seção é o elemento mais forte (título de 27 px). Em cada seção, o primeiro card tem cabeçalho em degradê e os demais usam a versão suave.
- **Escala de tamanhos:**

  | Elemento | Tamanho |
  |---|---|
  | Título principal | 32 |
  | Título de seção | 27 |
  | Manchete | 21 |
  | Título de card | 17 |
  | Texto | 15 |
  | Rótulos | 12–13 |

  Os números grandes ficam entre 56 e 28.
- **Nada em caixa alta.** Títulos e números grandes com espaçamento entre letras levemente negativo e algarismos de largura igual.
- **Alinhamento:** selos, legendas, notas e títulos de gráfico centralizados sob o gráfico. O anel tem a mesma altura dos números ao lado. Nenhum título quebra em duas linhas sem necessidade.
- **Conferência:** abra no tamanho de um iPhone, sem erro no console, e verifique se nada fica espremido, encostado ou cortado.
