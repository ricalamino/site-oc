#!/usr/bin/env python3
"""Verificações mínimas do site estático. Sai com 1 se algo falhar."""
import re, sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LANGS = ["en", "pt", "zh", "ja", "ko"]
PAGES = ["index", "rules"]
STRICT = {"html","head","body","div","section","article","nav","header","footer",
          "main","ul","ol","table","a","span","script","style","title","form",
          "button","h1","h2","h3","h4","h5","h6"}
errors = []

class Checker(HTMLParser):
    def __init__(self, name):
        super().__init__()
        self.name, self.stack, self.links = name, [], []
        self.has_title, self.lang = False, None
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html": self.lang = a.get("lang")
        if tag == "title": self.has_title = True
        if tag in ("a", "link") and a.get("href"): self.links.append(a["href"])
        if tag in STRICT: self.stack.append(tag)
    def handle_endtag(self, tag):
        if tag not in STRICT: return
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        elif tag in self.stack:
            errors.append(f"{self.name}: </{tag}> fecha fora de ordem (aberto: {self.stack[-1]})")
            while self.stack.pop() != tag: pass
        else:
            errors.append(f"{self.name}: </{tag}> sem abertura")

def check(path):
    c = Checker(path.name)
    c.feed(path.read_text(encoding="utf-8"))
    if c.stack: errors.append(f"{path.name}: tags não fechadas: {c.stack}")
    if not c.has_title: errors.append(f"{path.name}: sem <title>")
    if not c.lang: errors.append(f"{path.name}: <html> sem lang")
    for href in c.links:
        if href.startswith(("http://", "https://", "mailto:", "tel:", "#")): continue
        target = href.split("#")[0].split("?")[0]
        if target and not (ROOT / target).exists():
            errors.append(f"{path.name}: link quebrado -> {href}")

for page in PAGES:
    for lang in LANGS:
        if not (ROOT / f"{page}-{lang}.html").exists():
            errors.append(f"faltando {page}-{lang}.html (paridade de idiomas)")

for f in sorted(ROOT.glob("*.html")):
    check(f)

sm = ROOT / "sitemap.xml"
if sm.exists():
    for u in re.findall(r"<loc>\s*(.*?)\s*</loc>", sm.read_text(encoding="utf-8")):
        name = u.rstrip("/").split("/")[-1]
        if name.endswith(".html") and not (ROOT / name).exists():
            errors.append(f"sitemap.xml: aponta para inexistente -> {name}")
else:
    errors.append("sitemap.xml ausente")

if errors:
    print(f"FALHOU ({len(errors)}):")
    for e in errors: print("  -", e)
    sys.exit(1)
print("OK")
