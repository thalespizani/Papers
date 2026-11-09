"""Gera o paper "Destaques por município" (853 municípios de MG).

Uso:  python3 build.py
Lê as planilhas de dados/, grava gerados/ (dados intermediários e revisao.csv)
e o HTML final em "papers criados/paper-destaques-municipios.html".
"""
import collections, csv, html, json, re, subprocess, sys, unicodedata
from comum import AQUI, GERADOS, SAIDA, MUNICIPIOS, n, nome_muni
import dados
from dados import monta_linhas, registros, ubs_obras, HEMO_NOVOS, PRIO_ORIGEM, numeros, HOSP, cap, benef_txt, titulo, MIN
import curadoria as cur

GERADOS.mkdir(exist_ok=True)
CUR = {nome_muni(k): v for k, v in cur.CUR.items()}
VALORES = {nome_muni(k): v for k, v in cur.VALORES.items()}

TIPO_DE_GRUPO = {'hemo': 'Hemodiálise', 'ubs': 'UBS', 'upa': 'Urgência', 'upa_hab': 'Urgência', 'bucal': 'Saúde Bucal', 'veic': 'Veículos'}
SEM_ENTREGA = dict(entrega='Sem entrega individual registrada', tipo='Pendente',
                   texto='Não há entrega exclusiva do município nas bases consultadas. Abra para ver os repasses e o comparativo entre governos.',
                   origens=[], status=None, valor=None, nota=None)


def melhor_origem(tem):
    return [o for o in PRIO_ORIGEM if o in tem][:1]


def origem_curada(m, d):
    """Origem do destaque curado pela regra Convênio > Resolução > Emenda,
    somando o que a curadoria marcou ao que os dados mostram para o mesmo item."""
    tem = set(d['origens'])
    if d['tipo'] == 'UBS':
        tem |= {o['origem'] for o in ubs_obras.get(m, [])}
    elif d.get('valor'):
        for r in registros:
            if r['muni'] == m and abs(r['valor'] - d['valor']) < 1:
                tem |= r['origem']
    return melhor_origem(tem)


def de_linha(l):
    d = dict(entrega=l['entrega'], tipo=TIPO_DE_GRUPO.get(l['g'], 'Equipamentos'), texto=l['texto'],
             origens=l['origens'], status=l['rotulo'] if l.get('status') else None,
             valor=round(l['valor'], 2) if l['valor'] else None, nota=l.get('nota'))
    if l['g'] == 'upa_hab':
        d['entrega'] = 'Nova UPA 24h' if l.get('nova') else 'Ampliação de UPA 24h'
    return d


PD, DET, REVISAO, MUDOU_PILL = [], {}, [], []
for mm in MUNICIPIOS:
    m = mm['municipio']
    if m in CUR:
        ent, tipo, txt, org, st, vo, nota = CUR[m]
        d = dict(entrega=ent, tipo=tipo, texto=txt, origens=org, status=st,
                 valor=round(vo if vo else VALORES.get(m) or 0, 2) or None, nota=nota, curado=True)
        nova = origem_curada(m, d)
        if nova != d['origens']: MUDOU_PILL.append((m, '/'.join(d['origens']), '/'.join(nova)))
        d['origens'] = nova
        linhas = monta_linhas(m, d)
    elif m in HEMO_NOVOS:
        d = dict(entrega='Novo Centro de Hemodiálise', tipo='Hemodiálise', texto=cur.t_hemo, origens=['Resolução'],
                 status=None, valor=4000000, nota=None, curado=False)
        linhas = monta_linhas(m, d)
        REVISAO.append((m, d, 'novo centro de hemodiálise (Apuração Física), valor padrão de R$ 4 mi'))
    else:
        todas = monta_linhas(m, None, None)
        # prioridade do destaque: Novo Centro de Hemodiálise > Construção de UBS > demais (ordem de ORDEM)
        todas.sort(key=lambda l: l['g'] != 'ubs')
        if todas:
            d = dict(de_linha(todas[0]), curado=False)
            linhas = todas[1:]
            g = todas[0]['g']
            motivo = []
            if g in ('veic', 'aps', 'upa_hab'): motivo.append('destaque fraco (' + g + ')')
            if g == 'eq' and todas[0]['texto'].lower().startswith('equipamentos e materiais permanentes'): motivo.append('equipamento genérico')
            if d['valor'] and d['valor'] < 150000 and g != 'upa_hab': motivo.append('valor abaixo de R$ 150 mil')
            if motivo: REVISAO.append((m, d, '; '.join(motivo)))
        else:
            d = dict(SEM_ENTREGA, curado=False)
            linhas = []
    PD.append(dict(municipio=m, ibge=mm['ibge'], macro=mm['macro'], **d))
    DET[m] = dict(entregas=linhas, **numeros(m))

json.dump(PD, open(GERADOS / 'paper_data.json', 'w'), ensure_ascii=False, indent=1)
json.dump(DET, open(GERADOS / 'detalhe_data.json', 'w'), ensure_ascii=False, indent=1, default=list)
with open(GERADOS / 'revisao.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f, delimiter=';')
    w.writerow(['Município', 'Motivo', 'Entrega', 'Valor', 'Origem', 'Texto'])
    for m, d, motivo in sorted(REVISAO, key=lambda x: n(x[0])):
        w.writerow([m, motivo, d['entrega'], f"{d['valor'] or 0:.2f}".replace('.', ','), '/'.join(d['origens']), d['texto']])
with open(GERADOS / 'pills_alteradas.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f, delimiter=';')
    w.writerow(['Município', 'Antes', 'Depois'])
    w.writerows(MUDOU_PILL)

# ---------- HTML ----------
SVG = 'xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
ICONES = {
 'Hemodiálise': f'<svg {SVG}><path d="M7 16.3c2.2 0 4-1.83 4-4.05 0-1.16-.57-2.26-1.71-3.19S7.29 6.75 7 5.3c-.29 1.45-1.14 2.84-2.29 3.76S3 11.1 3 12.25c0 2.22 1.8 4.05 4 4.05z"/><path d="M12.56 6.6A10.97 10.97 0 0 0 14 3.02c.5 2.5 2 4.9 4 6.5s3 3.5 3 5.5a6.98 6.98 0 0 1-11.91 4.97"/></svg>',
 'UBS': f'<svg {SVG}><path d="M10 12h4"/><path d="M10 8h4"/><path d="M14 21v-3a2 2 0 0 0-4 0v3"/><path d="M6 10H4a2 2 0 0 0-2 2v7a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-2"/><path d="M6 21V5a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v16"/></svg>',
 'Urgência': f'<svg {SVG}><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/><path d="M3.22 12H9.5l.5-1 2 4.5 2-7 1.5 3.5h5.27"/></svg>',
 'Saúde Bucal': f'<svg {SVG}><circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><line x1="9" x2="9.01" y1="9" y2="9"/><line x1="15" x2="15.01" y1="9" y2="9"/></svg>',
 'Equipamentos': f'<svg {SVG}><path d="M11 2v2"/><path d="M5 2v2"/><path d="M5 3H4a2 2 0 0 0-2 2v4a6 6 0 0 0 12 0V5a2 2 0 0 0-2-2h-1"/><path d="M8 15a6 6 0 0 0 12 0v-3"/><circle cx="20" cy="10" r="2"/></svg>',
 'Veículos': f'<svg {SVG}><path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"/><path d="M15 18H9"/><path d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.624l-3.48-4.35A1 1 0 0 0 17.52 8H14"/><circle cx="17" cy="18" r="2"/><circle cx="7" cy="18" r="2"/></svg>',
 'Pendente': f'<svg {SVG}><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>',
}
TIPOS = ['Hemodiálise', 'UBS', 'Urgência', 'Saúde Bucal', 'Equipamentos', 'Veículos', 'Pendente']

def sem_acento(s):
    s = unicodedata.normalize('NFKD', s or '')
    return ''.join(c for c in s if not unicodedata.combining(c)).lower()

def esc(s):
    return html.escape(str(s), quote=True)

def slug(s):
    return 'm-' + sem_acento(s).replace(' ', '-').replace('--', '-')

def moeda(v):
    if v >= 1e6:
        return 'R$ ' + f'{v/1e6:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.') + ' mi'
    return 'R$ ' + f'{round(v/1e3):,}'.replace(',', '.') + ' mil'

def card_html(d):
    pend = d['tipo'] == 'Pendente'
    nome_busca = esc(sem_acento(d['municipio']))
    h = f'<a class="muni-link" id="{slug(d["municipio"])}" href="#p{slug(d["municipio"])[1:]}" data-nome="{nome_busca}">'
    h += f'<article class="ses-card muni{" muni--pendente" if pend else ""}">'
    h += f'<div class="muni__topo"><div class="ses-tile ses-tile--sus">{ICONES[d["tipo"]]}</div><div style="min-width:0">'
    h += f'<h3 class="ses-titulo-card muni__nome">{esc(d["municipio"])}</h3>'
    h += f'<p class="muni__tema">{esc("Sem entrega" if pend else d["tipo"])}</p></div></div>'
    status_na_ubs = d['tipo'] == 'UBS' and d.get('status')
    status_chip = ''
    if d.get('status'):
        ponto = 'concluido' if d['status'] == 'Entregue' else 'andamento'
        status_chip = f'<span class="ses-chip"><span class="ses-ponto ses-ponto--{ponto}"></span>{esc(d["status"])}</span>'

    h += f'<div class="muni__meio">'
    if status_na_ubs:
        h += f'<div class="muni__entrega-linha"><p class="muni__entrega">{esc(d["entrega"])}</p>{status_chip}</div>'
    else:
        h += f'<p class="muni__entrega">{esc(d["entrega"])}</p>'
    h += f'<p class="ses-corpo-denso muni__texto">{esc(d["texto"])}</p></div>'
    h += '<div class="muni__lado">'
    if d.get('valor'):
        nota = f'<small>{esc(d["nota"])}</small>' if d.get('nota') else ''
        h += f'<p class="muni__valor tnum">{moeda(d["valor"])}{nota}</p>'
    selos = [f'<span class="selo-origem">{esc(o)}</span>' for o in (d.get('origens') or [])]
    if d.get('status') and not status_na_ubs:
        selos.append(status_chip)
    if selos:
        h += f'<div class="muni__selos">{"".join(selos)}</div>'
    return h + f'</div><span class="muni__seta" aria-hidden="true"><svg {SVG}><path d="m9 18 6-6-6-6"/></svg></span></article></a>'

DADOS_ORD = sorted(PD, key=lambda d: sem_acento(d['municipio']))
cards_html = '\n'.join(card_html(d) for d in DADOS_ORD)
exec(open(AQUI / 'paginas.py', encoding='utf-8').read())
paginas_html = '\n'.join(pagina_html(d, DET[d['municipio']]) for d in DADOS_ORD)

fonte = (AQUI / 'fonte.html').read_text(encoding='utf-8')
fonte = fonte.replace('/*__CARDS__*/', cards_html).replace('/*__PAGINAS__*/', paginas_html)
(GERADOS / 'fonte_render.html').write_text(fonte, encoding='utf-8')
subprocess.run([sys.executable, str(AQUI / 'assets' / 'montar.py'), str(GERADOS / 'fonte_render.html'), str(SAIDA)], check=True)

c = collections.Counter(d['tipo'] for d in PD)
print(len(PD), 'municípios |', dict(c))
print('para revisar:', len(REVISAO), '| pills alteradas nos curados:', len(MUDOU_PILL))
