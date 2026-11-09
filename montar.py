#!/usr/bin/env python3
"""Monta um HTML autocontido: injeta inter-inline.css e base.css no <style>.

Uso:  python3 montar.py <fonte.html> <saida.html>

A fonte precisa ter, dentro de um <style>, as duas marcas:
    /*__INTER__*/   e   /*__BASE__*/
Se a fonte nao usar Inter embutida, basta omitir a marca __INTER__.
"""
import sys, pathlib

aqui = pathlib.Path(__file__).parent
fonte, saida = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
html = fonte.read_text(encoding="utf-8")
for marca, arq in (("/*__INTER__*/", "inter-inline.css"), ("/*__BASE__*/", "base.css")):
    if marca in html:
        html = html.replace(marca, (aqui / arq).read_text(encoding="utf-8"))
saida.write_text(html, encoding="utf-8")
print(f"{saida} — {saida.stat().st_size/1024:.0f} KB")
