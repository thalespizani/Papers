# Executado dentro de build.py (usa SVG, esc, slug, moeda).
IPCA = 1.36151040

IC = {
 'voltar': f'<svg {SVG}><path d="m12 19-7-7 7-7"/><path d="M19 12H5"/></svg>',
 'entregas': f'<svg {SVG}><path d="M11 21.73a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73z"/><path d="M12 22V12"/><path d="m3.3 7 7.703 4.734a2 2 0 0 0 1.994 0L20.7 7"/></svg>',
 'barras': f'<svg {SVG}><path d="M5 21v-6"/><path d="M12 21V3"/><path d="M19 21V9"/></svg>',
 'banco': f'<svg {SVG}><path d="M10 18v-7"/><path d="M11.119 2.205a2 2 0 0 1 1.762 0l7.84 3.846A.5.5 0 0 1 20.5 7h-17a.5.5 0 0 1-.22-.949z"/><path d="M14 18v-7"/><path d="M18 18v-7"/><path d="M3 22h18"/><path d="M6 18v-7"/></svg>',
 'balanca': f'<svg {SVG}><path d="M12 3v18"/><path d="m19 8 3 8a5 5 0 0 1-6 0zV7"/><path d="M3 7h1a17 17 0 0 0 8-2 17 17 0 0 0 8 2h1"/><path d="m5 8 3 8a5 5 0 0 1-6 0zV7"/><path d="M7 21h10"/></svg>',
 'alerta': f'<svg {SVG}><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>',
 'relogio': f'<svg {SVG}><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>',
 'coracao': f'<svg {SVG}><path d="M2 9.5a5.5 5.5 0 0 1 9.591-3.676.56.56 0 0 0 .818 0A5.49 5.49 0 0 1 22 9.5c0 2.29-1.5 4-3 5.5l-5.492 5.313a2 2 0 0 1-3 .019L5 15c-1.5-1.5-3-3.2-3-5.5"/><path d="M3.22 13H9.5l.5-1 2 4.5 2-7 1.5 3.5h5.27"/></svg>',
}

def br(v, casas=1):
    return f'{v:,.{casas}f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

def mi(v):
    if v >= 1e6: return f'R$ {br(v / 1e6, 2 if v < 1e7 else 1)} mi'
    return f'R$ {br(v / 1e3, 0)} mil'

def reais(v): return 'R$ ' + br(v, 0)

def vezes(x): return br(x, 1) + 'x'

def secao(icone, titulo, corpo):
    return (f'<section class="ses-card pag__secao"><div class="pag__cab"><div class="ses-tile pag__tile">{IC[icone]}</div>'
            f'<h2 class="pag__h2">{titulo}</h2></div>{corpo}</section>')

def rotulo(icone, texto):
    return f'<div class="pag__rotulo">{IC[icone]}<span>{texto}</span><i></i></div>'

def selos(origens):
    return ''.join(f'<span class="selo-origem">{esc(o)}</span>' for o in origens or [])

def chip_status(st):
    ponto = 'concluido' if st == 'Entregue' else 'andamento'
    return f'<span class="ses-chip"><span class="ses-ponto ses-ponto--{ponto}"></span>{esc(st)}</span>'

def linha(entrega, texto, valor, nota, origens, marca, destaque=False):
    v = ''
    if valor:
        v = f'<p class="ent__valor tnum">{moeda(valor)}' + (f'<small>{esc(nota)}</small>' if nota else '') + '</p>'
    return (f'<div class="ent{" ent--destaque" if destaque else ""}"><div class="ent__corpo">'
            f'<div class="ent__topo">{marca}<p class="ent__nome">{esc(entrega)}</p></div>'
            f'<p class="ent__texto">{esc(texto)}</p></div>'
            f'<div class="ent__lado">{v}<div class="ent__selos">{selos(origens)}</div></div></div>')


SIGLAS = {'ubs', 'upa', 'uti', 'samu', 'caps', 'ceo', 'apae', 'hpp', 'fms', 'sus', 'raps', 'cti', 'rue', 'aps', 'esf', 'cer', 'ses', 'mg', 'ii', 'iii', 'iv'}

def frase(t, nomes=()):
    """TEXTO EM CAIXA ALTA -> 'Texto em caixa alta'. Siglas e nomes próprios (palavras do
    beneficiário e do município, em `nomes`) ficam com a grafia certa."""
    t = re.sub(r'\s+', ' ', str(t)).strip()
    if t != t.upper(): return t
    proprios = {}
    for nm in nomes:
        for w in titulo(nm).split(' '):
            if w.lower() not in MIN: proprios[n(w)] = w
    ws = []
    for w in t.lower().split(' '):
        k = re.sub(r'\W', '', n(w))
        ws.append(w.upper() if k in SIGLAS else proprios.get(n(w), w))
    return cap(' '.join(ws))

def bloco_atencao(det):
    itens = det.get('atencao') or []
    if not itens: return ''
    h = ''
    for a in itens:
        meta = ' · '.join(x for x in (a['origem'], a['data']) if x)
        h += (f'<div class="ent ent--atencao"><div class="ent__corpo"><p class="ent__nome">{esc(a["texto"])}</p>'
              + (f'<p class="ent__texto">{esc(meta)}</p>' if meta else '') + '</div></div>')
    return secao('alerta', 'Ponto de atenção', f'<div class="ent-lista">{h}</div>')

def bloco_tramitacao(det, muni=''):
    tr = det.get('tramitacao') or []
    if not tr: return ''
    tr = sorted(tr, key=lambda t: (t['status'] != 'Em tramitação', -t['valor']))
    tot = sum(t['valor'] for t in tr)
    h = ''
    for t in tr:
        marca = f'<span class="ses-chip"><span class="ses-ponto ses-ponto--andamento"></span>{esc(t["status"])}</span>'
        if t['valor']:
            v = f'<p class="ent__valor tnum">{moeda(t["valor"])}</p>'
        else:
            v = '<p class="ent__valor ent__valor--def">Valor a definir</p>'
        sel = selos([t['instrumento']] if t['instrumento'] else [])
        ben = benef_txt([t['benef']])
        h += (f'<div class="ent"><div class="ent__corpo"><div class="ent__topo">{marca}<p class="ent__nome">{esc(frase(t["objeto"], (t["benef"], muni)))}</p></div>'
              + (f'<p class="ent__texto">{esc(ben[0])}</p>' if ben else '') + '</div>'
              f'<div class="ent__lado">{v}<div class="ent__selos">{sel}</div></div></div>')
    n_ = len(tr)
    nota = (f'<p class="pag__nota">{n_} {"pleito" if n_ == 1 else "pleitos"} ainda sem pagamento'
            + (f', somando {mi(tot)} com valor definido' if tot else '') + '. Convênios e resoluções em análise ou em preparação.</p>')
    return secao('relogio', 'Em tramitação', f'<div class="ent-lista">{h}</div>{nota}')

def bloco_entregas(d, det):
    if d['tipo'] == 'Pendente':
        return ''  # sem entrega exclusiva: a página fica só com os números
    marca = chip_status(d['status']) if d.get('status') else '<span class="marca marca--destaque">Destaque</span>'
    h = linha(d['entrega'], d['texto'], d.get('valor'), d.get('nota'), d.get('origens'), marca, True)
    for l in det['entregas']:
        m = chip_status(l['rotulo']) if l.get('status') else f'<span class="marca">{esc(l["rotulo"])}</span>'
        h += linha(l['entrega'], l['texto'], l['valor'], l.get('nota'), l['origens'], m)
    return secao('entregas', 'Principais entregas', f'<div class="ent-lista">{h}</div>')

def comparativo(titulo, rot_at, rot_an, c, sem_msg):
    at, an = c['atual'], c['anterior']
    if not at and not an:
        return f'<div class="cmp cmp--vazio"><p class="cmp__titulo">{titulo}</p><p class="cmp__nota">{sem_msg}</p></div>'
    corr = an * IPCA
    if an:
        pills = (f'<span class="pill-x pill-x--sem">{vezes(at / an)} sem correção</span>'
                 f'<span class="pill-x pill-x--com">{vezes(at / corr)} com correção</span>')
    else:
        pills = '<span class="pill-x pill-x--com">Sem repasses no governo anterior</span>'
    mx = max(at, corr)
    w_at = at / mx * 100
    w_nom = an / mx * 100
    w_cor = (corr - an) / mx * 100
    return (f'<div class="cmp"><div class="cmp__topo"><p class="cmp__titulo">{titulo}</p><div class="cmp__pills">{pills}</div></div>'
            f'<div class="cmp__linha"><div class="cmp__leg"><span>{rot_at}</span><b class="tnum">{mi(at) if at else "R$ 0"}</b></div>'
            f'<div class="cmp__trilho"><div class="cmp__at" style="width:{w_at:.1f}%"></div></div></div>'
            f'<div class="cmp__linha"><div class="cmp__leg"><span>{rot_an}</span><b class="tnum">{mi(corr) if an else "R$ 0"}</b></div>'
            f'<div class="cmp__trilho cmp__trilho--flex"><div class="cmp__nom" style="width:{w_nom:.1f}%"></div>'
            f'<div class="cmp__cor" style="width:{w_cor:.1f}%"></div></div></div></div>')

def bloco_comparativo(det):
    leg = ('<div class="cmp-leg"><span><i class="bola bola--nom"></i>Governo anterior, valor nominal</span>'
           '<span><i class="bola bola--cor"></i>Correção monetária (IPCA-E)</span></div>')
    corpo = rotulo('barras', 'Recursos pagos ao município, governo atual × anterior') + leg
    corpo += '<div class="cmp-lista">'
    corpo += comparativo('Atenção Primária à Saúde', 'Governo atual (2022–2025)', 'Governo anterior (2015–2018)', det['aps'],
                         'Não há valores de Atenção Primária registrados para o município.')
    corpo += comparativo('Atenção Hospitalar', 'Valora Minas (2022–2025)', 'Pro-Hosp (2015–2018)', det['valora'],
                         'Não há valores repassados para o município no Valora Minas.')
    corpo += '</div>'
    return secao('balanca', 'Comparativo entre governos', corpo)

def bloco_investimento(det):
    anos = {int(a): v for a, v in det['anos'].items()}
    total = sum(anos.values())
    mx = max(anos.values()) or 1
    em_mi = mx >= 1e6
    cols = ''
    for a in sorted(anos):
        v = anos[a]
        lab = br(v / 1e6, 1) if em_mi else br(v / 1e3, 0)
        parc = a == 2026
        cols += (f'<div class="gr__col" title="{a}{" (parcial)" if parc else ""}: {reais(v)}">'
                 f'<span class="gr__val tnum">{lab}</span>'
                 f'<div class="gr__barra{" gr__barra--parcial" if parc else ""}" style="height:{max(v / mx * 100, .5):.1f}%"></div>'
                 f'<span class="gr__ano">{a}{"<small>parcial</small>" if parc else ""}</span></div>')
    corpo = (f'<div class="kpi-total"><p class="kpi-total__rot">Total repassado ao município, 2019–2026</p>'
             f'<p class="kpi-total__val tnum">{mi(total)}</p></div>'
             + rotulo('barras', 'Repassado por ano') +
             f'<div class="gr" role="img" aria-label="Valor repassado por ano, de 2019 a 2026">{cols}</div>'
             f'<p class="pag__nota">Valores em R$ {"milhões" if em_mi else "mil"}. Custeio e investimento somados. 2026 considera os repasses até a data de atualização da base.</p>')
    f = det.get('fes')
    if f and f['divida']:
        pct = f['pago'] / f['divida'] * 100
        corpo += (rotulo('balanca', 'Acordo FES: dívida do Estado com o município') +
                  f'<div class="fes"><div class="fes__leg"><span>Já pago pelo Estado: <b class="tnum">{mi(f["pago"])}</b></span>'
                  f'<span>Dívida total: <b class="tnum">{mi(f["divida"])}</b></span></div>'
                  f'<div class="fes__trilho"><div class="fes__fill" style="width:{pct:.1f}%"></div></div>'
                  f'<p class="fes__pct">{br(pct, 1)}% pago</p>')
        if f.get('ultima_parcela'):
            d_ = f.get('data_ultima_parcela')
            quando = (' em ' + d_.strftime('%m/%Y') if hasattr(d_, 'strftime') else (f' em {d_}' if d_ else ''))
            corpo += f'<p class="fes__ultima">Última parcela paga: <b class="tnum">{reais(f["ultima_parcela"])}</b>{esc(quando)}</p>'
        corpo += '</div>'
    return secao('banco', 'Investimento total', corpo)

def pagina_html(d, det):
    sid = 'p' + slug(d['municipio'])[1:]
    volta = slug(d['municipio'])
    h = f'<section class="pag" id="{sid}" aria-label="{esc(d["municipio"])}">'
    h += f'<a class="pag__voltar" href="#{volta}">{IC["voltar"]}Todos os municípios</a>'
    h += ('<div class="ses-hero pag__hero"><div class="ses-onda"></div><div class="ses-orbe ses-orbe--clara"></div><div class="ses-orbe ses-orbe--escura"></div>'
          f'<div class="ses-hero__conteudo"><div class="ses-hero__titulo"><div class="ses-glass">{IC["coracao"]}</div><div style="min-width:0">'
          '<p class="ses-eyebrow ses-eyebrow--claro">Secretaria de Estado de Saúde de Minas Gerais · SES-MG</p>'
          '<h2 class="pag__titulo">Entregas e Investimentos em Saúde</h2>'
          f'<p class="pag__muni">{esc(d["municipio"])}</p></div></div></div></div>')
    h += bloco_atencao(det) + bloco_entregas(d, det) + bloco_tramitacao(det, d['municipio']) + bloco_comparativo(det) + bloco_investimento(det)
    return h + '</section>'
