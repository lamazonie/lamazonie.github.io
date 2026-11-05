#!/usr/bin/env python3
"""Gera semana/anuncios/index.html: relatório de anúncios pro time (edição e design), sem números de venda.
Dados do período ficam em data/anuncios/AAAA-MM-DD.json. Uso: python3 tools/gerar-anuncios.py 2026-10-31
"""
import json, sys, html, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
per = sys.argv[1] if len(sys.argv) > 1 else sorted(p.stem for p in (ROOT/'data/anuncios').glob('*.json'))[-1]
D = json.load(open(ROOT/'data/anuncios'/f'{per}.json', encoding='utf-8'))
CAT = {c['codigo']: c for c in json.load(open(ROOT/'data/catalogo-ads.json', encoding='utf-8'))}
e = html.escape

def band(k, v):
    if v is None: return ''
    o, b, hi = {'g': (35, 25, True), 'h': (40, 25, True), 'c': (1.5, 1.0, True), 'cpm': (30, 50, False), 'f': (2, 3, False)}[k]
    if hi: return 'ok' if v >= o else 'warn' if v >= b else 'bad'
    return 'ok' if v <= o else 'warn' if v <= b else 'bad'
def fmt(k, v):
    if v is None: return '—'
    if k in ('g', 'h'): return f'{v:.0f}%'
    if k == 'c': return f'{v:.2f}%'.replace('.', ',')
    if k == 'cpm': return f'R$ {v:.0f}'
    return f'{v:.1f}'.replace('.', ',')
def chips(m):
    out = []
    for k, lbl in [('g', 'gancho'), ('h', 'história'), ('c', 'CTR'), ('cpm', 'CPM'), ('f', 'freq')]:
        v = m.get(k)
        if v is None: continue
        out.append(f'<span class="ch {band(k, v)}"><small>{lbl}</small>{fmt(k, v)}</span>')
    return ''.join(out)
def thumb(code, cls='th'):
    p = ROOT/'media'/f'{code}.jpg'
    return f'<span class="{cls}"><img src="../media/{code}.jpg" alt=""></span>' if p.exists() else f'<span class="{cls} nocap">sem capa</span>'
def meta(code):
    c = CAT.get(code, {})
    parts = [c.get('quem'), c.get('formato'), f"{c['duracao']} s" if c.get('duracao') else None, c.get('angulo')]
    return ' · '.join(e(p) for p in parts if p)
TAG = {'scale': 'Replicar', 'keep': 'Manter', 'watch': 'Observar', 'new': 'Versão nova', 'pause': 'Pausar', 'off': 'Pausado'}
CATCLS = {'Campeão': 'ok', 'Abaixo do ideal': 'warn', 'Não repetir': 'bad', 'Estreia': 'new', 'Pouca verba': 'na', 'Remarketing': 'na'}

def card_ad(a):
    tags = ''.join(f'<span class="tag {t}">{e(TAG[t] if t in TAG else t)}</span>' for t in a['tags'])
    extra = f' <span class="tagx">{e(a["tagx"])}</span>' if a.get('tagx') else ''
    st = '<span class="tag off">pausado</span>' if a.get('pausado') else ''
    return f'''<li class="ad">
  {thumb(a['codigo'])}
  <div class="body">
    <div class="l1"><b>{e(a['codigo'])}</b><span class="cat {CATCLS.get(a['categoria'],'na')}">{e(a['categoria'])}</span>{st}</div>
    <div class="meta">{meta(a['codigo'])}</div>
    <div class="chips">{chips(a.get('m', {}))}</div>
    <div class="dec">{tags}{extra}</div>
    <p class="why">{a['why']}</p>
  </div>
</li>'''

def hook(hk):
    return f'''<div class="hk">{thumb(hk['codigo'])}<div><span class="rank">{e(hk['rank'])}</span><div class="q">{e(hk['q'])}</div><div class="w">{e(hk['w'])}</div><div class="chips">{chips(hk.get('m', {}))}</div></div></div>'''

def pedido(p, i):
    moldes = ''.join(f'<span class="mo">{thumb(c, "th")}<b>{e(c)}</b><span>{e(l)}</span></span>' for c, l in p['moldes'])
    spec = ''.join(f'<span class="sp {cls}"><small>{e(k)}</small>{e(v)}</span>' for k, v, cls in p['spec'])
    ing = ''.join(f'<li>{e(x)}</li>' for x in p['ing'])
    return f'''<article class="pr">
  <div class="hd"><span class="num">{i}</span><div><h3>{e(p['t'])}</h3><p class="sub">{e(p['sub'])}</p></div></div>
  <div class="molde"><span class="lbl">Molde{'s' if len(p['moldes'])>1 else ''}</span>{moldes}</div>
  <div class="spec">{spec}</div>
  <ul class="ing">{ing}</ul>
  <p class="why"><b>Por quê:</b> {e(p['why'])}</p>
</article>'''

ads = '\n'.join(card_ad(a) for a in D['anuncios'])
hooks_a = '\n'.join(hook(h) for h in D['ganchos_atencao'])
hooks_v = '\n'.join(hook(h) for h in D['ganchos_venda'])
peds = '\n'.join(pedido(p, i + 1) for i, p in enumerate(D['pedidos']))
prontos = ''.join(f'<div class="r"><div><b>{e(r[0])}</b><span>{e(r[1])}</span></div><span class="st {r[3]}">{e(r[2])}</span></div>' for r in D['prontos'])
nao = ''.join(f'<div class="it">{thumb(n[0], "th")}<span class="x">{e(n[1])}</span><span>{e(n[2])}</span></div>' for n in D['nao_repetir'])
regras = ''.join(f'<div><b>{e(r[0])}</b><span>{e(r[1])}</span></div>' for r in D['nao_repetir_regras'])
resumo = ''.join(f'<li><b>{e(r[0])}</b> {e(r[1])}</li>' for r in D['resumo'])
levas = ''.join(f'<div class="leva {l[3]}"><span class="w">{e(l[0])}</span><b>{e(l[1])}</b><span>{e(l[2])}</span></div>' for l in D['levas'])

page = f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Anúncios · {e(D['periodo'])}</title>
<meta name="robots" content="noindex, nofollow">
<meta name="description" content="Decisão por anúncio, ganchos e o que produzir agora. Pro time de edição e design.">
<meta name="theme-color" content="#0e423a">
<meta name="color-scheme" content="light only">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600&family=Roboto+Condensed:wght@300;400;500&display=swap">
<style>
:root{{color-scheme:light only;--bg:#faf8f3;--surface:#fff;--ink:#0e2a25;--muted:#5e6f69;--line:#e8e6df;--brand:#0e423a;--cream:#f2ecdd;--gold:#8a6b2e;
--ok:#1f8a55;--warn:#b7791f;--bad:#c2453a;--neutral:#8a948e;--ok-bg:#e6f4ec;--warn-bg:#f8efdc;--bad-bg:#f9e7e4;--na-bg:#eef0ed;--new-bg:#e8eef9;--new:#2f6ed1;
--display:"Roboto Condensed","Arial Narrow",system-ui,sans-serif;--sans:"Sora",ui-sans-serif,system-ui,sans-serif;--r:14px}}
*{{box-sizing:border-box;margin:0}}
html{{-webkit-text-size-adjust:100%;scroll-behavior:smooth;scroll-padding-top:70px}}
body{{background:var(--bg);color:var(--ink);font:300 16px/1.55 var(--sans);-webkit-font-smoothing:antialiased}}
img{{display:block;max-width:100%}} a{{color:inherit}}
.wrap{{max-width:760px;margin:0 auto;padding-inline:max(20px,env(safe-area-inset-left)) max(20px,env(safe-area-inset-right))}}
header.top{{background:var(--brand);color:var(--cream)}}
header.top .wrap{{padding-block:22px 24px;display:grid;gap:10px}}
.logo{{height:26px;width:auto}}
.eyebrow{{font:400 12px/1.3 var(--display);letter-spacing:.2em;text-transform:uppercase;opacity:.8}}
h1{{font:300 30px/1.1 var(--display);letter-spacing:-.005em;text-transform:uppercase}}
.lead{{font:400 17px/1.45 var(--sans);max-width:36ch}}
.note{{font-size:13px;opacity:.8;max-width:60ch}}
nav.tabs{{position:sticky;top:0;z-index:5;background:color-mix(in srgb,var(--bg) 92%,transparent);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}}
nav.tabs .wrap{{display:flex;gap:6px;overflow-x:auto;scrollbar-width:none;padding-block:8px}}
nav.tabs a{{flex:0 0 auto;text-decoration:none;font:500 13px var(--sans);padding:8px 14px;border-radius:999px;border:1px solid var(--line);background:var(--surface);min-height:36px;display:inline-flex;align-items:center}}
section{{padding-block:28px}} section+section{{border-top:1px solid var(--line)}}
h2{{font:400 22px/1.15 var(--display);text-transform:uppercase;letter-spacing:.01em;margin-bottom:6px}}
.sub{{color:var(--muted);font-size:14px;line-height:1.5;max-width:64ch;margin-bottom:16px}}
.resumo{{list-style:none;padding:0;display:grid;gap:10px}}
.resumo li{{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:12px 14px;font-size:15px}}
.resumo b{{font-weight:600;display:block;margin-bottom:2px}}
.levas{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin-top:14px}}
.leva{{display:flex;flex-direction:column;gap:3px;padding:10px 12px;border-radius:var(--r);background:var(--surface);border:1px solid var(--line);font-size:12.5px;color:var(--muted)}}
.leva::before{{content:"";height:4px;border-radius:99px;background:var(--line);margin-bottom:4px}}
.leva.now::before{{background:var(--brand)}} .leva.next::before{{background:color-mix(in srgb,var(--brand) 45%,#fff)}} .leva.bf::before{{background:var(--gold)}}
.leva b{{color:var(--ink);font-size:15px;font-weight:500}} .leva .w{{font:500 12px var(--display);letter-spacing:.04em}}
@media (max-width:640px){{.levas{{grid-template-columns:repeat(2,minmax(0,1fr))}}}}
.ads{{list-style:none;padding:0;display:grid;gap:12px}}
.ad{{display:grid;grid-template-columns:72px minmax(0,1fr);gap:14px;background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:14px}}
.th{{width:72px;aspect-ratio:4/5;border-radius:10px;overflow:hidden;background:var(--na-bg);display:block}}
.th img{{width:100%;height:100%;object-fit:cover}}
.th.nocap{{display:grid;place-items:center;font-size:11px;color:var(--muted);text-align:center}}
.body{{display:grid;gap:7px;min-width:0}}
.l1{{display:flex;flex-wrap:wrap;gap:6px;align-items:center}} .l1 b{{font-weight:600;font-size:17px}}
.meta{{font-size:13px;color:var(--muted)}}
.cat,.tag,.tagx,.st{{font-size:12px;font-weight:500;padding:2px 9px;border-radius:999px;line-height:1.6;white-space:nowrap}}
.cat.ok{{background:var(--ok-bg);color:var(--ok)}} .cat.warn{{background:var(--warn-bg);color:var(--warn)}} .cat.bad{{background:var(--bad-bg);color:var(--bad)}} .cat.na{{background:var(--na-bg);color:var(--muted)}} .cat.new{{background:var(--new-bg);color:var(--new)}}
.tag{{border:1px solid currentColor}} .tag.scale{{color:var(--ok);background:var(--ok-bg)}} .tag.keep{{color:var(--ok)}} .tag.watch{{color:var(--warn)}} .tag.new{{color:var(--ink)}} .tag.pause{{color:var(--bad)}} .tag.off{{color:var(--muted);border-style:dashed}}
.tagx{{color:var(--muted)}}
.chips{{display:flex;flex-wrap:wrap;gap:5px}}
.ch{{display:inline-flex;align-items:baseline;gap:4px;padding:2px 8px;border-radius:7px;font-size:12.5px;font-weight:500;background:var(--na-bg);color:var(--ink);font-variant-numeric:tabular-nums}}
.ch small{{font-size:10px;color:var(--muted);letter-spacing:.03em}}
.ch.ok{{background:var(--ok-bg);color:var(--ok)}} .ch.warn{{background:var(--warn-bg);color:var(--warn)}} .ch.bad{{background:var(--bad-bg);color:var(--bad)}} .ch.ok small,.ch.warn small,.ch.bad small{{color:inherit;opacity:.8}}
.dec{{display:flex;flex-wrap:wrap;gap:5px;align-items:center}}
.why{{font-size:14px;color:var(--muted);line-height:1.5}} .why b{{color:var(--ink);font-weight:500}}
@media (max-width:480px){{.ad{{grid-template-columns:60px minmax(0,1fr);gap:10px;padding:12px}} .th{{width:60px}}}}
.hooks{{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,15rem),1fr));gap:10px;margin-bottom:10px}}
.hk{{display:grid;grid-template-columns:56px minmax(0,1fr);gap:10px;align-items:start;padding:10px;border-radius:var(--r);background:var(--surface);border:1px solid var(--line)}}
.hk .th{{width:56px}} .hk .rank{{font:500 12px var(--display);color:var(--muted);letter-spacing:.04em}}
.hk .q{{font-size:15px;font-weight:500;line-height:1.3}} .hk .w{{font-size:12.5px;color:var(--muted);margin:3px 0 6px}}
h3{{font:500 17px/1.3 var(--sans);margin-bottom:4px}}
.pat{{font-size:13px;color:var(--muted);padding:8px 12px;border:1px dashed var(--line);border-radius:10px;margin:4px 0 18px}} .pat b{{color:var(--ink);font-weight:500}}
.prs{{display:grid;gap:12px}}
.pr{{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:16px;display:grid;gap:12px}}
.pr .hd{{display:grid;grid-template-columns:auto minmax(0,1fr);gap:12px;align-items:start}}
.pr .num{{font:300 40px/.9 var(--display);color:var(--muted);min-width:1.1em}}
.pr h3{{font-size:19px}} .pr .sub{{margin:2px 0 0;font-size:13.5px}}
.molde{{display:flex;gap:10px;flex-wrap:wrap;align-items:flex-start}} .molde .lbl{{flex:1 1 100%;font-size:12px;color:var(--muted)}}
.mo{{display:flex;flex-direction:column;align-items:center;gap:3px;width:64px;font-size:10px;color:var(--muted);text-align:center;line-height:1.2}} .mo .th{{width:64px}} .mo b{{color:var(--ink);font-size:12px;font-weight:500}}
.spec{{display:flex;flex-wrap:wrap;gap:6px}}
.sp{{display:inline-flex;align-items:center;gap:5px;padding:4px 9px;border-radius:999px;font-size:12.5px;background:var(--na-bg);white-space:nowrap}} .sp small{{color:var(--muted);font-size:10px;letter-spacing:.03em}}
.sp.l1{{background:var(--brand);color:var(--cream)}} .sp.l1 small{{color:inherit;opacity:.75}} .sp.l2{{border:1px solid var(--brand);background:transparent}}
.ing{{margin:0;padding:0;list-style:none;display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,13rem),1fr));gap:6px 12px;font-size:13.5px;color:var(--muted)}}
.ing li{{display:flex;gap:7px;align-items:flex-start;line-height:1.4}} .ing li::before{{content:"";flex:none;width:13px;height:13px;border-radius:50%;margin-top:3px;background:var(--ok-bg);box-shadow:inset 0 0 0 1.5px var(--ok)}}
.pr .why{{border-top:1px solid var(--line);padding-top:10px}}
.ready{{display:grid}} .ready .r{{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:6px 12px;padding:10px 0;border-bottom:1px solid var(--line);align-items:center;font-size:13px}} .ready .r:last-child{{border:0}}
.ready b{{display:block;font-size:15px;font-weight:500;color:var(--ink)}} .ready span{{color:var(--muted)}}
.st{{border:1px solid currentColor}} .st.wait{{color:var(--warn)}} .st.ok{{color:var(--ok)}} .st.no{{color:var(--muted);border-style:dashed}}
.nao{{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(30%,7rem),1fr));gap:12px;margin-bottom:14px}}
.nao .it{{display:flex;flex-direction:column;gap:5px;font-size:12.5px;color:var(--muted);line-height:1.35}}
.nao .th{{width:100%;position:relative;filter:saturate(.35)}} .nao .th::after{{content:"";position:absolute;inset:0;background:linear-gradient(to top,rgba(194,69,58,.55),transparent 55%)}}
.nao .x{{color:var(--bad);font-weight:500;display:flex;gap:4px;overflow-wrap:anywhere;hyphens:auto}} .nao .x::before{{content:"×"}}
.regras{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,12rem),1fr));gap:10px}} .regras div{{display:flex;flex-direction:column;gap:2px;font-size:13px;color:var(--muted)}} .regras b{{color:var(--ink);font-weight:500;font-size:14px}}
.faixas{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,14rem),1fr));gap:6px 20px;font-size:13px}} .faixas div{{display:flex;flex-direction:column;gap:2px;padding-block:8px;border-bottom:1px solid var(--line)}} .faixas b{{font-weight:500}} .faixas span{{color:var(--muted)}}
footer{{padding:24px 0 40px;color:var(--muted);font-size:13px}}
</style>
</head>
<body>
<header class="top"><div class="wrap">
  <img class="logo" src="../brand/logo-creme.png" alt="L'Amazonie">
  <span class="eyebrow">Anúncios · {e(D['periodo'])}</span>
  <h1>Decisão por anúncio e <em>o que produzir</em></h1>
  <p class="lead">{e(D['manchete'])}</p>
  <p class="note">{e(D['nota'])}</p>
</div></header>
<nav class="tabs"><div class="wrap"><a href="#resumo">Resumo</a><a href="#anuncios">Anúncios</a><a href="#ganchos">Ganchos</a><a href="#produzir">Produzir</a><a href="#nao">Não repetir</a><a href="#faixas">Como ler</a></div></nav>
<main class="wrap">
<section id="resumo"><h2>O que o período mostrou</h2><ul class="resumo">{resumo}</ul><div class="levas">{levas}</div></section>
<section id="anuncios"><h2>Decisão por anúncio</h2><p class="sub">{e(D['anuncios_sub'])}</p><ul class="ads">
{ads}
</ul></section>
<section id="ganchos"><h2>Os melhores ganchos</h2>
<h3>Ganchos que param o dedo</h3><p class="sub">Gancho = quem viu 3 s ÷ impressões. Abrem a porta; a visita deles compra menos.</p><div class="hooks">{hooks_a}</div><p class="pat"><b>Padrão:</b> {e(D['pat_atencao'])}</p>
<h3>Ganchos que vendem</h3><p class="sub">CTR baixo é parte do mecanismo: só clica quem já quer. São os que mais fecham venda.</p><div class="hooks">{hooks_v}</div><p class="pat"><b>Padrão:</b> {e(D['pat_venda'])}</p>
</section>
<section id="produzir"><h2>O que produzir agora</h2><p class="sub">{e(D['produzir_sub'])}</p><div class="prs">
{peds}
</div>
<h3 style="margin-top:22px">Já pronto na pasta</h3><div class="ready">{prontos}</div>
</section>
<section id="nao"><h2>Não repetir</h2><p class="sub">Ângulos e formatos que falharam duas vezes ou ficaram abaixo da média da campanha.</p><div class="nao">{nao}</div><div class="regras">{regras}</div></section>
<section id="faixas"><h2>Como ler as cores</h2><p class="sub">Verde é ótimo, amarelo é bom e vermelho é ruim. Gancho é quem viu 3 segundos dividido pelas impressões; história é quem viu até o fim (ThruPlay) dividido por quem viu 3 segundos; CTR é clique de saída dividido por impressões. Números de venda ficam no painel interno.</p>
<div class="faixas"><div><b>Gancho</b><span>ótimo ≥ 35% · bom 25–35% · ruim &lt; 25%</span></div><div><b>História</b><span>ótimo ≥ 40% · bom 25–40% · ruim &lt; 25%</span></div><div><b>CTR de saída</b><span>ótimo ≥ 1,5% · bom 1–1,5% · ruim &lt; 1%</span></div><div><b>CPM</b><span>ótimo ≤ R$ 30 · bom R$ 30–50 · ruim &gt; R$ 50</span></div><div><b>Frequência</b><span>ótimo &lt; 2 · bom 2–3 · ruim &gt; 3 (remarketing até 8)</span></div></div>
</section>
</main>
<footer class="wrap">Atualizado em {e(D['atualizado'])}. Categoria do período: Campeão = na meta com verba relevante; Não repetir = abaixo da média da campanha nos dois modelos; Abaixo do ideal = o resto; Pouca verba = sem base pra veredito. Criativos: <a href="../time/">página do time</a>.</footer>
</body>
</html>
'''
out = ROOT/'anuncios'/'index.html'
out.parent.mkdir(exist_ok=True)
out.write_text(page, encoding='utf-8')
print(out, len(page))
