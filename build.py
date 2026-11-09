#!/usr/bin/env python3
"""Monta o paper autocontido de destaques para o Secretário.

    python3 geo.py     # só quando mudar a malha ou a planilha (gera geo/geo.json)
    python3 build.py   # injeta fonte Inter e geometria em fonte.html

Saída: papers criados/paper-destaques-secretario.html
"""
import pathlib, re

AQUI = pathlib.Path(__file__).parent
RAIZ = AQUI.parent.parent
INTER = RAIZ / "pipeline" / "destaques-municipios" / "assets" / "inter-inline.css"
SAIDA = RAIZ / "papers criados" / "paper-destaques-secretario.html"

html = (AQUI / "fonte.html").read_text(encoding="utf-8")
html = html.replace("/*__INTER__*/", INTER.read_text(encoding="utf-8"))
html = html.replace("/*__GEO__*/", (AQUI / "geo" / "geo.json").read_text(encoding="utf-8"))

# checagem de tags balanceadas nas estruturas principais
corpo = re.sub(r"<script>.*?</script>", "", html, flags=re.S)
corpo = re.sub(r"<style>.*?</style>", "", corpo, flags=re.S)
for tag in ("div", "section", "span", "svg", "p", "a", "nav", "header", "footer", "button"):
    a = len(re.findall(rf"<{tag}[\s>]", corpo))
    f = len(re.findall(rf"</{tag}>", corpo))
    assert a == f, f"<{tag}> desbalanceada: {a} aberturas, {f} fechamentos"

SAIDA.write_text(html, encoding="utf-8")
print(f"{SAIDA.relative_to(RAIZ)} — {SAIDA.stat().st_size / 1024:.0f} KB")
