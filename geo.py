#!/usr/bin/env python3
"""Gera geometria simplificada de MG em coordenadas SVG (geo.json).

Entradas:
  - malha municipal de MG (geodata-br, IBGE):  geo/mg-mun.json
      curl -sS -o geo/mg-mun.json \
        https://raw.githubusercontent.com/tbrugz/geodata-br/master/geojson/geojs-31-mun.json
  - dados/nova planilha de dados - chefia de gabinete (1).xlsx  (aba PDR: município → macro 2025;
    aba COBERTURA APS: cobertura de ESF abr/2026)

Saída: geo/geo.json com
  - macros2025: {macro: path}
  - macros2018: {macro: path}  (Sul = Sul+Sudoeste+Extremo Sul; Vale do Aço dentro da Leste)
  - mun: [[ibge7, nome, path, cobertura]]
  - pts: {nome_normalizado: [x, y]}  (ponto representativo de cada município)
"""
import json, math, pathlib, unicodedata
import openpyxl
from shapely.geometry import shape, mapping
from shapely.ops import unary_union

AQUI = pathlib.Path(__file__).parent
RAIZ = AQUI.parent.parent
PLAN = RAIZ / "dados" / "nova planilha de dados - chefia de gabinete (1).xlsx"
W = 1000  # largura do viewBox


def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().upper()
    return " ".join(s.replace("-", " ").replace("'", " ").split())


feats = json.load(open(AQUI / "geo" / "mg-mun.json", encoding="utf-8"))["features"]
geoms = {f["properties"]["id"]: shape(f["geometry"]).buffer(0) for f in feats}
nomes = {f["properties"]["id"]: f["properties"]["name"] for f in feats}

# projeção equirretangular com correção do cosseno na latitude média de MG
uni = unary_union(list(geoms.values()))
minx, miny, maxx, maxy = uni.bounds
k = math.cos(math.radians((miny + maxy) / 2))
sx = W / ((maxx - minx) * k)
H = (maxy - miny) * sx


def xy(lon, lat):
    return ((lon - minx) * k * sx, (maxy - lat) * sx)


def path(g, tol):
    g = g.simplify(tol, preserve_topology=True)
    polys = [g] if g.geom_type == "Polygon" else list(g.geoms)
    out = []
    for p in polys:
        if p.area < (tol * tol * 4):
            continue
        for ring in [p.exterior] + list(p.interiors):
            pts = [xy(*c) for c in ring.coords]
            out.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in pts[:-1]) + "Z")
    return "".join(out)


wb = openpyxl.load_workbook(PLAN, read_only=True, data_only=True)
macro = {}
for r in wb["PDR"].iter_rows(min_row=3, values_only=True):
    if r[0]:
        macro[str(r[0]).strip()] = " ".join(str(r[6]).split()).title().replace(" Do ", " do ")
cob = {}
for r in wb["COBERTURA APS"].iter_rows(min_row=2, values_only=True):
    if r[0] and isinstance(r[2], (int, float)):
        cob[str(r[0])] = r[2]

faltam = [i for i in geoms if i not in macro]
assert not faltam, f"municípios sem macro: {faltam[:5]}"

grupos25 = {}
for i, g in geoms.items():
    grupos25.setdefault(macro[i], []).append(g)
m25 = {m: unary_union(gs) for m, gs in grupos25.items()}

junta18 = {"Sudoeste": "Sul", "Extremo Sul": "Sul", "Vale do Aço": "Leste"}
grupos18 = {}
for m, g in m25.items():
    grupos18.setdefault(junta18.get(m, m), []).append(g)
m18 = {m: unary_union(gs) for m, gs in grupos18.items()}

TOL_MACRO, TOL_MUN = 0.012, 0.012
saida = {
    "w": W,
    "h": round(H, 1),
    "macros2025": {m: path(g, TOL_MACRO) for m, g in sorted(m25.items())},
    "macros2018": {m: path(g, TOL_MACRO) for m, g in sorted(m18.items())},
    "contorno": path(uni, TOL_MACRO),
    "mun": [[i, nomes[i], path(g, TOL_MUN), round(cob.get(i[:6], -1), 4)] for i, g in sorted(geoms.items())],
    "pts": {norm(nomes[i]): [round(v, 1) for v in xy(*g.representative_point().coords[0])] for i, g in geoms.items()},
    "rot25": {m: [round(v, 1) for v in xy(*g.representative_point().coords[0])] for m, g in m25.items()},
}
(AQUI / "geo" / "geo.json").write_text(json.dumps(saida, ensure_ascii=False), encoding="utf-8")
print("macros 2025:", len(m25), "| 2018:", len(m18), "| municípios:", len(geoms),
      "| cobertura lida:", sum(1 for i in geoms if i[:6] in cob))
print(f"geo.json {(AQUI / 'geo' / 'geo.json').stat().st_size / 1024:.0f} KB")
