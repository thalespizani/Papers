"""Funções e caminhos comuns do pipeline de destaques por município."""
import pathlib, re, unicodedata
import openpyxl

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
D = RAIZ / 'dados'
SAIDA = RAIZ / 'papers criados' / 'paper-destaques-municipios.html'
GERADOS = AQUI / 'gerados'


def n(s):
    """Texto sem acento, minúsculo e com espaços normalizados (para casar nomes)."""
    s = unicodedata.normalize('NFKD', str(s or ''))
    return re.sub(r'\s+', ' ', ''.join(c for c in s if not unicodedata.combining(c)).lower()).strip()


def num(v):
    try:
        f = float(v)
        return f if f > 0 else 0.0
    except Exception:
        return 0.0


def abrir(arq):
    return openpyxl.load_workbook(D / arq, read_only=True, data_only=True)


# ---------- lista-mestre: os 853 municípios (PDR 2023) ----------
MUNICIPIOS = []
for r in list(abrir('Regionalização PDR 2023.xlsx')['Plan1'].iter_rows(values_only=True))[1:]:
    if r and r[1]:
        MUNICIPIOS.append(dict(municipio=str(r[1]).strip(), ibge=r[0], micro=r[3], macro=r[4]))
NOMES = {n(m['municipio']): m['municipio'] for m in MUNICIPIOS}

# grafias das planilhas que diferem do nome oficial (conferidas uma a uma)
ALIAS = {
    'santa rita do ibitipoca': 'Santa Rita de Ibitipoca',
    'sem peixe': 'Sem-Peixe',
    'dona eusebia': 'Dona Euzébia',
    'dona euzebia': 'Dona Eusébia',
    'amparo da serra': 'Amparo do Serra',
    'brazopolis': 'Brasópolis',
    "olhos d'agua": "Olhos-d'Água",
    'passa vinte': 'Passa-Vinte',
    'sao tome das letras': 'São Thomé das Letras',
    'sao sabastiao do paraiso': 'São Sebastião do Paraíso',
}


def nome_muni(s):
    """Nome oficial do município, ou None se o texto não casar com nenhum dos 853."""
    k = n(s)
    if k in NOMES:
        return NOMES[k]
    if k in ALIAS:
        return NOMES.get(n(ALIAS[k]))  # o par cobre as duas grafias; vale a que estiver na lista-mestre
    return None
