"""Lê as planilhas de dados/ e monta, para os 853 municípios, as entregas
padronizadas, os comparativos entre governos, o total por ano e o Acordo FES."""
import collections, csv, re, unicodedata
from comum import abrir, n, num, nome_muni, D, MUNICIPIOS

# ---------- nomes de entidades em caixa normal ----------
MIN = {'de', 'do', 'da', 'dos', 'das', 'e'}
SIG = {'apae', 'fms', 'hpp', 'ceo'}
ACE = {'sao':'São','saude':'Saúde','fundacao':'Fundação','antonio':'Antônio','conceicao':'Conceição','misericordia':'Misericórdia',
       'associacao':'Associação','joao':'João','jose':'José','sebastiao':'Sebastião','caridade':'Caridade','conferencia':'Conferência',
       'vicentina':'Vicentina','municipio':'Município','hospitalar':'Hospitalar','beneficencia':'Beneficência','santana':'Santana',
       'imaculada':'Imaculada','gricia':'Grícia','nsa':'Nsa','sra':'Sra','regiao':'Região','caritativa':'Caritativa','luis':'Luís'}
def titulo(s):
    s = re.sub(r'\s+', ' ', str(s)).strip()
    out = []
    for i, w in enumerate(s.lower().split(' ')):
        if w in SIG: out.append(w.upper())
        elif i and w in MIN: out.append(w)
        elif w in ACE: out.append(ACE[w])
        else: out.append(w[:1].upper() + w[1:])
    return ' '.join(out)

def acentos(s): return sum(1 for c in unicodedata.normalize('NFKD', s) if unicodedata.combining(c))

# ---------- itens padronizados ----------
# (regex, grupo, singular, plural)
ITENS = [
 (r'hemodialise.*poltrona|poltrona.*hemodialise', 'hemo', 'poltrona de hemodiálise', 'poltronas de hemodiálise'),
 (r'hemodialise', 'hemo', 'máquina de hemodiálise', 'máquinas de hemodiálise'),
 (r'construcao de ubs|construcao ubs|constucao ubs', 'ubs', 'UBS', 'UBS'),
 (r'uti adulto', 'obra', 'ampliação da UTI adulto', 'ampliações de UTI'),
 (r'centro cirurgico.*ampl|ampliacao de centro cirurgico', 'obra', 'ampliação do centro cirúrgico', 'ampliações de centro cirúrgico'),
 (r'tomograf', 'tomo', 'tomógrafo', 'tomógrafos'),
 (r'mamograf', 'mamo', 'mamógrafo', 'mamógrafos'),
 (r'odontologica movel', 'bucal', 'unidade odontológica móvel', 'unidades odontológicas móveis'),
 (r'extraoral', 'bucal', 'raio-X odontológico extraoral', 'raios-X odontológicos extraorais'),
 (r'saude bucal|\bceo\b', 'bucal', 'equipamentos de saúde bucal', 'equipamentos de saúde bucal'),
 (r'\bupa\b', 'upa', 'equipamentos para a UPA', 'equipamentos para a UPA'),
 (r'multissensorial|pessoa com deficiencia', 'pcd', 'equipamentos e mobiliário para o parque multissensorial', ''),
 (r'psicossocial', 'psico', 'equipamentos para a Rede de Atenção Psicossocial', 'equipamentos para a Rede de Atenção Psicossocial'),
 (r'ambulanc|^furgao|^furgoneta|^pick.?up 4x4|^pick-up 4x4', 'veic_amb', 'ambulância', 'ambulâncias'),
 (r'transporte sanitario|microoniu|micro.?onibus', 'veic_ts', 'veículo de transporte sanitário adaptado', 'veículos de transporte sanitário adaptados'),
 (r'pick.?up|minivan|passeio|veiculo', 'veic', 'veículo', 'veículos'),
 (r'anestesia', 'eq', 'aparelho de anestesia', 'aparelhos de anestesia'),
 (r'laringoscop', 'eq', 'videolaringoscópio', 'videolaringoscópios'),
 (r'foco cirurgico', 'eq', 'foco cirúrgico com câmera', 'focos cirúrgicos com câmera'),
 (r'arco cirurgico', 'eq', 'arco cirúrgico', 'arcos cirúrgicos'),
 (r'mesa cirurgica', 'eq', 'mesa cirúrgica elétrica', 'mesas cirúrgicas elétricas'),
 (r'kit 5 camas', 'eq', 'kit de 5 camas hospitalares', 'kits de 5 camas hospitalares'),
 (r'cama', 'eq', 'cama hospitalar', 'camas hospitalares'),
 (r'monitor', 'eq', 'kit de monitores multiparamétricos', 'kits de monitores multiparamétricos'),
 (r'ventilador', 'eq', 'ventilador pulmonar', 'ventiladores pulmonares'),
 (r'autoclave', 'eq', 'autoclave', 'autoclaves'),
 (r'digitalizador', 'eq', 'digitalizador de imagens radiográficas', 'digitalizadores de imagens radiográficas'),
 (r'raio', 'eq', 'aparelho de raio-X', 'aparelhos de raio-X'),
 (r'ultrassom', 'eq', 'aparelho de ultrassom', 'aparelhos de ultrassom'),
 (r'endoscop', 'eq', 'sistema de videoendoscopia', 'sistemas de videoendoscopia'),
 (r'gerador', 'eq', 'grupo gerador', 'grupos geradores'),
 (r'elevador', 'eq', 'elevadores para a UTI', 'elevadores para a UTI'),
 (r'kit hpp|pequeno porte', 'eq', 'kit de equipamentos para hospital de pequeno porte', 'kits de equipamentos para hospital de pequeno porte'),
 (r'kit rue', 'eq', 'kit de equipamentos da Rede de Urgência e Emergência', 'kits de equipamentos da Rede de Urgência e Emergência'),
 (r'kit valor em saude', 'eq', 'kit de equipamentos do Valora Minas', 'kits de equipamentos do Valora Minas'),
 (r'imunobiolog', 'aps', 'câmara de conservação de vacinas', 'câmaras de conservação de vacinas'),
 (r'academia da saude', 'aps', 'equipamentos para a Academia da Saúde', 'equipamentos para a Academia da Saúde'),
 (r'\baps\b|atencao primaria', 'aps', 'equipamentos e mobiliário', 'equipamentos e mobiliário'),
 (r'equipamento|bem permanente|bens permanentes|mobiliario', 'eq', 'equipamentos e materiais permanentes', 'equipamentos e materiais permanentes'),
]
GENERICOS = {'equipamentos e mobiliário para o parque multissensorial', 'equipamentos e materiais permanentes', 'equipamentos e mobiliário', 'equipamentos de saúde bucal',
             'equipamentos para a UPA', 'equipamentos para a Academia da Saúde',
             'equipamentos para a Rede de Atenção Psicossocial', 'UBS'}

def item(obj):
    o = re.sub(r'^fes\s+', '', n(obj))
    if re.search(r'custeio|medicament|material de consumo|materiais de consumo|insumo|transporte eletivo em saude na micro|componente basico', o):
        return None
    for pat, g, s, p in ITENS:
        if re.search(pat, o):
            return g, s, p
    return None

HOSP = re.compile(r'hospital|santa casa|irmandade|fundacao|casa de caridade|beneficen|misericordia|sociedade|instituto|associacao hospitalar')

# ordem da pill de origem: Emenda só quando não há outro instrumento
PRIO_ORIGEM = ('Convênio', 'Resolução', 'Emenda')


def instrumento(s):
    s = n(s)
    if 'convenio' in s: return 'Convênio'
    if 'resolucao' in s: return 'Resolução'
    return None


registros = []   # dicts: muni, grupo, s, p, valor, ano, origem(set), benef

# ---------- Emendas (dedup pela INDICAÇÃO) ----------
wb = abrir('nova planilha de dados - chefia de gabinete (1).xlsx')
emendas = {}
for r in list(wb['EMENDAS'].iter_rows(values_only=True))[3:]:
    if not r or r[3] is None: continue
    mnome = nome_muni(r[0])
    if not mnome: continue
    e = emendas.setdefault(r[3], {'muni': mnome, 'obj': r[6], 'benef': r[7], 'valor': 0.0, 'ano': None, 'origem': {'Emenda'}})
    e['valor'] = max(e['valor'], num(r[8]))
    if hasattr(r[9], 'year'): e['ano'] = r[9].year
    elif r[2] and not e['ano']: e['ano'] = r[2]
    if acentos(str(r[7] or '')) > acentos(str(e['benef'] or '')): e['benef'] = r[7]

# ---------- Monitoramento de Pleitos (aba CONSOLIDADO) ----------
# O nome da coluna de status muda ("STATUS - 25/09"): ela é achada pelo prefixo "STATUS".
_cons = list(abrir('Monitoramento de Pleitos NGTPL.xlsx')['CONSOLIDADO'].iter_rows(values_only=True))
_cab = [n(h) for h in _cons[0]]
def _col(prefixo):
    return next(i for i, h in enumerate(_cab) if h.startswith(prefixo))
C_ID, C_OBJ, C_BEN, C_MUN, C_INST, C_VAL = (_col(k) for k in ('numero da indicacao', 'objeto', 'beneficiario', 'municipio', 'instrumento', 'valor'))
C_STATUS, C_ENTRADA = _col('status'), _col('data de entrada')
_cons = [r for r in _cons[1:] if r and r[C_ID] is not None]

pleitos_so = []
for r in _cons:
    if n(r[C_STATUS]) != 'pago': continue
    mnome = nome_muni(r[C_MUN])
    if not mnome: continue
    orig = instrumento(r[C_INST]) or 'Resolução'
    if r[C_ID] in emendas:
        e = emendas[r[C_ID]]
        e['valor'] = max(e['valor'], num(r[C_VAL]))
        e['origem'].add(orig)   # a emenda foi paga por resolução/convênio
        continue
    pleitos_so.append({'muni': mnome, 'obj': r[C_OBJ], 'benef': r[C_BEN], 'valor': num(r[C_VAL]), 'ano': None, 'origem': {orig}})

# ---------- Em tramitação (pleitos ainda não pagos; suspensos ficam de fora) ----------
tramitacao = collections.defaultdict(list)
for r in _cons:
    st = n(r[C_STATUS])
    if st == 'pago' or 'suspenso' in st: continue
    mnome = nome_muni(r[C_MUN])
    if not mnome: continue
    tramitacao[mnome].append(dict(
        id=r[C_ID], objeto=str(r[C_OBJ] or '').strip(), benef=str(r[C_BEN] or '').strip(),
        valor=num(r[C_VAL]), instrumento=instrumento(r[C_INST]),
        status='Em tramitação' if 'em tramitacao' in st else 'Pré-tramitação'))

# pleito sem número de emenda, mas mesmo objeto e valor de uma emenda do município: é a mesma entrega
idx_em = {}
for e in emendas.values():
    it = item(e['obj'])
    if it:
        reg = dict(muni=e['muni'], grupo=it[0], s=it[1], p=it[2], valor=e['valor'], ano=e['ano'], origem=e['origem'], benef=e['benef'])
        registros.append(reg)
        idx_em.setdefault((e['muni'], it[0], round(e['valor'])), reg)
soma_em = collections.defaultdict(float)
for r in registros: soma_em[(r['muni'], r['grupo'])] += r['valor']
for p in pleitos_so:
    it = item(p['obj'])
    if not it: continue
    gemea = idx_em.get((p['muni'], it[0], round(p['valor'])))
    if gemea:
        gemea['origem'] |= p['origem']
        continue
    if abs(soma_em[(p['muni'], it[0])] - p['valor']) < 1:
        continue  # mesma entrega paga em duas emendas (ex.: parque multissensorial de Curvelo)
    if 'termo aditivo' in n(p['obj']):
        continue  # aditivo de valor de um item já contado
    registros.append(dict(muni=p['muni'], grupo=it[0], s=it[1], p=it[2], valor=p['valor'], ano=None, origem=p['origem'], benef=p['benef']))

# ---------- Convênios celebrados ----------
for r in list(wb['CONVÊNIOS CELEBRADOS'].iter_rows(values_only=True))[5:]:
    if not r or not r[3]: continue
    m = nome_muni(r[3])
    if not m or not r[5]: continue
    if 'consorcio' in n(r[4]): continue
    it = item(r[5])
    if not it or it[0] == 'ubs': continue
    if 'centro cirurgico' in n(r[5]): it = ('eq', 'equipamentos para o centro cirúrgico', 'equipamentos para o centro cirúrgico')
    registros.append(dict(muni=m, grupo=it[0], s=it[1], p=it[2], valor=num(r[6]), ano=r[1], origem={'Convênio'}, benef=str(r[4] or '').strip()))

# ---------- UBS (obras, com status) ----------
ubs_obras = collections.defaultdict(list)
for r in list(abrir('UBS por município.xlsx')['Planilha1'].iter_rows(values_only=True))[1:]:
    if not r or not r[0]: continue
    m = nome_muni(r[0])
    if not m: continue
    st = str(r[9] or '').strip()
    obs = n(r[10])
    ex = f"Endereço: {r[5]}; Status: {st}; % execução: {r[8]}; Obs: {r[10] or ''}"
    entregue = n(st) in ('entregue', 'inaugurado') or 'inaugurada em' in obs or 'inauguracao ocorrida' in obs
    bairro = re.search(r'(?:bairro|Bairro|BAIRRO|Distrito de|comunidade|Povoado de)\s+([^,;\-]+)', ex)
    orig = instrumento(r[1]) or ('Emenda' if 'emenda' in n(r[2]) else 'Resolução')
    ubs_obras[m].append(dict(valor=num(r[4]), entregue=entregue, local=bairro.group(1).strip() if bairro else None, origem=orig))

# ---------- UPA habilitada ----------
for r in list(wb['UPA'].iter_rows(values_only=True))[1:]:
    if not r or not r[0]: continue
    m = nome_muni(r[0])
    if not m: continue
    nova = n(r[2]) == 'nova'
    registros.append(dict(muni=m, grupo='upa_hab', s='UPA 24h ' + ('nova' if nova else 'ampliada'), p='', valor=num(r[7]),
                          ano=2025, origem={'Resolução'}, benef='', nota='por mês', nova=nova))

# ---------- Novos Centros de Hemodiálise (Apuração Física) ----------
HEMO_NOVOS = {}
with open(D / 'Apuração_Física(Apuracao_Fisica).csv', encoding='latin1') as f:
    for r in csv.DictReader(f, delimiter=';'):
        if r['Nome_Subproduto'] != 'Municípios beneficiados com recurso de investimento para abertura de Centros de Hemodiálise': continue
        try: v = float(r['Apuracao_Fisica'].replace(',', '.'))
        except Exception: v = 0
        m = nome_muni(r['Nome_Municipio'])
        if v > 0 and m: HEMO_NOVOS[m] = r['Ano'] or None

# ---------- montagem das linhas "principais entregas" ----------
ORDEM = ['hemo', 'ubs', 'obra', 'tomo', 'mamo', 'bucal', 'upa', 'eq_hosp', 'eq', 'aps', 'pcd', 'psico', 'veic', 'upa_hab']
TITULOS = {
 'hemo': 'Equipamentos para Hemodiálise', 'obra': 'Ampliação hospitalar', 'tomo': 'Tomógrafo', 'mamo': 'Mamógrafo',
 'bucal': 'Saúde Bucal', 'upa': 'Equipamentos para a UPA', 'eq_hosp': 'Equipamentos hospitalares',
 'eq': 'Equipamentos para a rede municipal de saúde', 'aps': 'Equipamentos para a Atenção Primária',
 'pcd': 'Rede de Cuidado à Pessoa com Deficiência', 'psico': 'Atenção Psicossocial', 'veic': 'Veículos para a saúde',
}
TIPO_GRUPO = {'Hemodiálise': 'hemo', 'UBS': 'ubs', 'Urgência': 'upa_hab', 'Veículos': 'veic', 'Saúde Bucal': 'bucal'}

def lista_pt(xs):
    xs = list(xs)
    return xs[0] if len(xs) == 1 else ', '.join(xs[:-1]) + ' e ' + xs[-1]

def qtd(c, s, p):
    if s in GENERICOS: return s
    if c == 1: return ('um ' if not s.startswith(('máquina', 'poltrona', 'ambul', 'unidade', 'câmara', 'cama', 'mesa', 'autoclave', 'ampliação')) else 'uma ') + s
    ext = {2: 'dois', 3: 'três'}
    fem = s.startswith(('máquina', 'poltrona', 'ambul', 'unidade', 'câmara', 'cama', 'mesa', 'autoclave', 'ampliação'))
    if c in ext: return (('duas' if fem and c == 2 else ext[c]) + ' ' + p)
    return f'{c} {p}'

def benef_txt(bs):
    bs = [b for b in bs if b and not re.search(r'fundo municipal|municipio de|prefeitura', n(b))]
    out = []
    for b in bs:
        t = titulo(b)
        if 'associacao de pais e amigos' in n(b) or n(b).startswith('apae'): t = 'APAE'
        if n(t) not in [n(x) for x in out]: out.append(t)
    return out

def anos(rs):
    a = sorted({r['ano'] for r in rs if r.get('ano')})
    if not a: return '2025–2026'
    return str(a[0]) if a[0] == a[-1] else f'{a[0]}–{a[-1]}'

def origens(rs):
    tem = set().union(*(r["origem"] if isinstance(r["origem"], set) else {r["origem"]} for r in rs)) if rs else set()
    return [o for o in PRIO_ORIGEM if o in tem][:1]

def cap(s): return s[:1].upper() + s[1:]

def monta_linhas(muni, destaque=None, limite=None):
    """Linhas de "Principais entregas". Com destaque, tira o que já está no card."""
    rs = [r for r in registros if r['muni'] == muni]
    for r in rs:
        if r['grupo'] == 'eq' and HOSP.search(n(r['benef'])): r['grupo'] = 'eq_hosp'
        if r['grupo'].startswith('veic'): r['sub'] = r['grupo']; r['grupo'] = 'veic'
    grupos = collections.defaultdict(list)
    for r in rs: grupos[r['grupo']].append(r)
    destaque = destaque or {'tipo': '', 'entrega': ''}
    pular = TIPO_GRUPO.get(destaque['tipo'])
    if destaque['entrega'] == 'Equipamentos para Hemodiálise': pular = 'hemo'
    if destaque['entrega'] in ('Construção de UPA',): pular = 'upa'
    if destaque['tipo'] == 'Equipamentos':
        # aqui o destaque é só UM item de um grupo que pode ter outros — em vez de
        # esconder o grupo inteiro (perdendo os outros itens), tira só o item do destaque.
        e = n(destaque['entrega'])
        txt = n(destaque.get('texto', ''))
        if 'atencao primaria' in e:
            alvo = 'aps'
        elif 'multissensorial' in e:
            alvo = 'pcd'
        elif 'hospitalar' in e or HOSP.search(e) or HOSP.search(txt):
            alvo = 'eq_hosp'
        else:
            alvo = 'eq'
        if alvo in grupos:
            dv = round(destaque.get('valor') or 0)
            restante = [r for r in grupos[alvo] if round(r['valor']) != dv]
            if restante: grupos[alvo] = restante
            else: del grupos[alvo]
        pular = None
    linhas = []
    # UBS vem da planilha de obras (com status)
    if muni in ubs_obras and pular != 'ubs':
        ob = ubs_obras[muni]
        ent = sum(o['entregue'] for o in ob)
        locais = [o['local'] for o in ob if o['local']]
        nome = 'Construção de UBS' if len(ob) == 1 else f'Construção de {len(ob)} UBS'
        det = ('Nova Unidade Básica de Saúde' if len(ob) == 1 else {2: 'Duas', 3: 'Três'}.get(len(ob), str(len(ob))) + ' novas Unidades Básicas de Saúde')
        if locais: det += (' no bairro ' if len(locais) == 1 else ' nos bairros ') + lista_pt([titulo(l) for l in locais])
        det += ', ampliando o acesso à Atenção Primária.'
        linhas.append(dict(g='ubs', entrega=nome, texto=det, valor=sum(o['valor'] for o in ob),
                           rotulo='Entregue' if ent == len(ob) else 'Em andamento', status=True,
                           origens=origens(ob)))
    for g in ORDEM:
        if g == pular or g == 'ubs' or g not in grupos: continue
        grs = grupos[g]
        tot = sum(r['valor'] for r in grs)
        if g == 'upa_hab':
            r = grs[0]
            linhas.append(dict(g=g, entrega='Nova UPA 24h' if r['nova'] else 'Ampliação de UPA 24h',
                               texto='Unidade habilitada, com custeio estadual mensal para o funcionamento.', valor=r['valor'], nota='por mês',
                               rotulo='2025', origens=['Resolução'], nova=r['nova']))
            continue
        if g == 'veic':
            c = collections.Counter(r['sub'] for r in grs)
            tot_v = sum(c.values())
            partes = []
            if c['veic_amb']: partes.append(qtd(c['veic_amb'], 'ambulância', 'ambulâncias'))
            if c['veic_ts']: partes.append(qtd(c['veic_ts'], 'veículo adaptado para transporte sanitário', 'veículos adaptados para transporte sanitário'))
            if tot_v == 1:
                det = cap(partes[0] if partes else 'um veículo') + ' para a rede municipal de saúde.'
            else:
                det = f'{tot_v} veículos para a rede municipal de saúde' + (', entre eles ' + lista_pt(partes) if partes else '') + '.'
            nome = 'Veículos para a saúde' if tot_v > 1 else ('Ambulância' if c['veic_amb'] else 'Veículo para a saúde')
            linhas.append(dict(g=g, entrega=nome, texto=det, valor=tot, rotulo=anos(grs), origens=origens(grs)))
            continue
        c = collections.Counter()
        val_it = collections.defaultdict(float)
        for r in grs: c[(r['s'], r['p'])] += 1; val_it[(r['s'], r['p'])] += r['valor']
        itens = sorted(c, key=lambda k: -val_it[k])
        esp = [k for k in itens if k[0] not in GENERICOS]
        gen = [k for k in itens if k[0] in GENERICOS]
        txt = [qtd(c[k], *k) for k in esp[:4]]
        if g == 'obra': txt = [k[0] for k in esp]
        if gen and len(txt) < 4: txt.append(gen[0][0] if len(esp) == 0 else 'outros equipamentos e materiais permanentes')
        if len(esp) > 4: txt.append('outros itens')
        bs = benef_txt(r['benef'] for r in grs)
        det = cap(lista_pt(txt))
        if g in ('eq_hosp', 'obra', 'tomo', 'mamo', 'pcd', 'psico') and bs:
            det += (' da ' if g == 'pcd' else ' para o ' if bs[0].lower().startswith(('hospital', 'instituto')) else ' para a ') + lista_pt(bs[:2])
        elif g == 'eq': det += ' para as unidades de saúde do município'
        elif g == 'aps': det += ' para as Unidades Básicas de Saúde'
        det += '.'
        nome = TITULOS[g]
        if g in ('tomo', 'mamo') and sum(c.values()) > 1: nome += 's'
        linhas.append(dict(g=g, entrega=nome, texto=det, valor=tot, rotulo=anos(grs), origens=origens(grs)))
    ordem = {g: i for i, g in enumerate(ORDEM)}
    linhas.sort(key=lambda l: ordem[l['g']])
    return linhas[:limite] if limite else linhas


# ---------- comparativos, total por ano, FES ----------
def reais_csv(t):
    """'R$ 2.057.421,34 ' -> 2057421.34"""
    t = re.sub(r'[^\d,]', '', str(t or '')).replace(',', '.')
    return float(t) if t else 0.0

def comp(arq):
    """Lê o CSV do exercício: município/valor do governo atual (colunas 0-1) e do anterior (4-5)."""
    at, an = {}, {}
    with open(D / arq, encoding='cp1252', newline='') as f:
        for r in csv.reader(f, delimiter=';'):
            r = r + [''] * (6 - len(r))
            m = nome_muni(r[0])
            if m: at[m] = num(reais_csv(r[1]))
            m = nome_muni(r[4])
            if m: an[m] = num(reais_csv(r[5]))
    return at, an
aps_at, aps_an = comp('Exercício_2022-2025 - APS.csv')
val_at, val_an = comp('Exercício_2022-2025 - Valora Minas.csv')

por_ano = collections.defaultdict(lambda: collections.defaultdict(float))
for r in list(abrir('Paper.xlsx')['Total Saúde'].iter_rows(values_only=True))[1:]:
    if r and nome_muni(r[3]): por_ano[nome_muni(r[3])][int(r[1])] += num(r[4])

# ---------- Acordo FES ----------
# "Última parcela paga": quando a aba ganhar colunas com "parcela" no nome (valor) e "parcela" + "data"
# (data), elas são lidas sozinhas e o paper mostra a linha. Hoje a aba não traz essa informação.
fes = {}
_fes = list(wb['ACORDO FES'].iter_rows(values_only=True))
_hf = [n(h) for h in _fes[5]]
_i_parc = next((i for i, h in enumerate(_hf) if 'parcela' in h and 'data' not in h), None)
_i_data = next((i for i, h in enumerate(_hf) if 'parcela' in h and 'data' in h), None)
for r in _fes[6:]:
    if r and r[2] and nome_muni(r[2]) and n(r[3]) == 'sim':
        f = dict(divida=num(r[4]), cancelado=num(r[5]), pago=num(r[6]), residual=num(r[7]))
        if _i_parc is not None and num(r[_i_parc]):
            f['ultima_parcela'] = num(r[_i_parc])
            f['data_ultima_parcela'] = r[_i_data] if _i_data is not None else None
        fes[nome_muni(r[2])] = f

# ---------- Pontos de atenção (dados/Pontos de Atenção.xlsx, aba "pontos_atencao") ----------
def _ponto_atencao():
    arq = D / 'Pontos de Atenção.xlsx'
    if not arq.exists(): return {}
    ws = abrir(arq.name)['pontos_atencao']
    rows = list(ws.iter_rows(values_only=True))
    cab = [n(h) for h in rows[0]]
    ix = {k: cab.index(k) for k in ('cod_ibge', 'ponto_atencao', 'origem', 'data', 'exibir_no_paper')}
    por_ibge = {str(m['ibge'])[:6]: m['municipio'] for m in MUNICIPIOS}
    out = collections.defaultdict(list)
    for r in rows[1:]:
        if not r or not r[ix['ponto_atencao']]: continue
        if n(r[ix['exibir_no_paper']]) not in ('sim', 's'): continue
        cod = re.sub(r'\D', '', str(r[ix['cod_ibge']] or ''))[:6]
        m = por_ibge.get(cod)
        if not m:
            print('AVISO: código IBGE sem município na lista-mestre em Pontos de Atenção:', r[ix['cod_ibge']])
            continue
        d = r[ix['data']]
        out[m].append(dict(texto=str(r[ix['ponto_atencao']]).strip(), origem=str(r[ix['origem']] or '').strip(),
                           data=d.strftime('%d/%m/%Y') if hasattr(d, 'strftime') else str(d or '').strip(),
                           _ord=d.strftime('%Y-%m-%d') if hasattr(d, 'strftime') else ''))
    for v in out.values():
        v.sort(key=lambda x: x['_ord'], reverse=True)
    return out
pontos_atencao = _ponto_atencao()


def numeros(m):
    return dict(
        aps=dict(atual=aps_at.get(m, 0.0), anterior=aps_an.get(m, 0.0)),
        valora=dict(atual=val_at.get(m, 0.0), anterior=val_an.get(m, 0.0)),
        anos={a: round(por_ano[m].get(a, 0.0), 2) for a in range(2019, 2027)},
        fes=fes.get(m),
        tramitacao=tramitacao.get(m, []),
        atencao=pontos_atencao.get(m, []),
    )
