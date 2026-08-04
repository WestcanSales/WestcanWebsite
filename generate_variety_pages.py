#!/usr/bin/env python3
"""Generate static SEO pages for Westcan Greenhouses:
  - varieties/<slug>.html  (one per catalog ROWS entry — unique title/meta/H1, Product JSON-LD)
  - 5 category landing pages (perennial-liners.html, ornamental-grass-plugs.html,
    fern-liners.html, ground-cover-plugs.html, shrub-conifer-liners.html)
  - sitemap.xml (all pages)

Run after update_site.py refreshes catalog.html ROWS (availability chips also
self-update in the browser from /availability_feed.json, so pages stay accurate
between rebuilds).

Usage: python3 generate_variety_pages.py [SRC] [OUT]
  SRC: repo dir containing catalog.html + images/ (default: script's own dir)
  OUT: output dir (default: SRC — writes in place)
"""
import sys, os, re, json, html

SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[2] if len(sys.argv) > 2 else SRC
os.makedirs(f'{OUT}/varieties', exist_ok=True)

BASE = 'https://westcangrhs.com'

# ---------- data ----------
ch = open(f'{SRC}/catalog.html', encoding='utf-8').read()
ROWS = json.loads(re.search(r'const ROWS\s*=\s*(\[.*?\]);', ch, re.S).group(1))

# photos: prefer live images/ dir; fall back to photo_slugs.txt
photo_slugs = set()
imgdir = os.path.join(SRC, 'images')
if os.path.isdir(imgdir) and any(f.endswith('-1.jpg') for f in os.listdir(imgdir)):
    photo_slugs = {f[:-6] for f in os.listdir(imgdir) if f.endswith('-1.jpg')}
elif os.path.exists(os.path.join(SRC, 'photo_slugs.txt')):
    photo_slugs = set(open(os.path.join(SRC, 'photo_slugs.txt')).read().split())

def esc(s): return html.escape(s or '', quote=True)

CAT_PAGE = {
    'Perennials':    ('perennial-liners.html', 'Perennial Liners'),
    'Grasses':       ('ornamental-grass-plugs.html', 'Ornamental Grass Plugs'),
    'Ferns':         ('fern-liners.html', 'Fern Liners'),
    'Ground Covers': ('ground-cover-plugs.html', 'Ground Cover Plugs'),
    'Shrubs':        ('shrub-conifer-liners.html', 'Shrub & Conifer Liners'),
    'Conifers':      ('shrub-conifer-liners.html', 'Shrub & Conifer Liners'),
    'Heathers':      ('shrub-conifer-liners.html', 'Shrub & Conifer Liners'),
}
def cat_link(cat):
    if cat in CAT_PAGE:
        return '/' + CAT_PAGE[cat][0], CAT_PAGE[cat][1]
    from urllib.parse import quote
    return '/catalog.html?cat=' + quote(cat), cat

# ---------- shared chrome ----------
def head(title, desc, canon, ogimg, extra=''):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon.png"><link rel="shortcut icon" href="/favicon.ico"><link rel="apple-touch-icon" href="/favicon.png">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Westcan Greenhouses">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{ogimg}">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Young+Serif&family=Archivo:wght@400;500;600;700&family=Spline+Sans+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{{--navy:#1F2A5C;--navy-deep:#16204A;--green:#2B7D43;--green-soft:#E3F0E7;--cream:#F7F2E8;--gold:#C9A24A;--gold-soft:#F6EDD9;--ink:#23262E;--muted:#5C6270;--line:#E4DDCE;--white:#FFFFFF;--ff-display:'Young Serif',Georgia,serif;--ff-body:'Archivo',system-ui,sans-serif;--ff-data:'Spline Sans Mono',ui-monospace,monospace}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:var(--ff-body);color:var(--ink);background:var(--cream);line-height:1.6;font-size:16px}}
img{{max-width:100%;display:block}}a{{color:inherit;text-decoration:none}}
.wrap{{max-width:1180px;margin:0 auto;padding:0 24px}}
.utilbar{{background:var(--navy-deep);color:#C9D0E8;font-size:13.5px}}
.utilbar .wrap{{display:flex;justify-content:space-between;align-items:center;min-height:36px;gap:16px;flex-wrap:wrap}}
.utilbar a:hover{{color:var(--white)}}
header{{background:var(--white);border-bottom:1px solid var(--line)}}
.nav{{display:flex;align-items:center;justify-content:space-between;min-height:72px;gap:20px}}
.brand img{{height:44px;width:auto}}
.nav nav{{display:flex;gap:26px;font-weight:500;flex-wrap:wrap}}
.nav nav a:hover{{color:var(--green)}}
.btn{{display:inline-block;padding:13px 26px;border-radius:8px;font-weight:600;border:2px solid transparent}}
.btn-primary{{background:var(--green);color:var(--white)}}
.btn-primary:hover{{background:#236636}}
.btn-ghost{{border-color:var(--navy);color:var(--navy)}}
.btn-ghost:hover{{background:var(--navy);color:var(--white)}}
.crumbs{{font-size:13.5px;color:var(--muted);padding:18px 0}}
.crumbs a:hover{{color:var(--green)}}
main{{padding-bottom:70px}}
h1{{font-family:var(--ff-display);color:var(--navy);line-height:1.15}}
.chip{{display:inline-block;font-family:var(--ff-data);font-size:12px;padding:4px 12px;border-radius:99px;font-weight:600;letter-spacing:.04em}}
.chip-now{{background:var(--green-soft);color:var(--green)}}
.chip-ahead{{background:var(--gold-soft);color:#8a6b1f}}
.chip-none{{background:#ECEDF2;color:var(--muted)}}
.chip-us{{background:var(--navy);color:#fff}}
footer{{background:var(--navy-deep);color:#C9D0E8;padding:44px 0;font-size:14.5px}}
footer a:hover{{color:#fff}}
.fcols{{display:flex;justify-content:space-between;gap:30px;flex-wrap:wrap}}
{extra}
</style>
</head>'''

UTILBAR = '''<div class="utilbar"><div class="wrap">
<div class="creds"><span>GCP Certified&nbsp;&nbsp;·&nbsp;&nbsp;Ball Rooting Station</span></div>
<div class="contact"><a href="tel:+16045309298">+1 604-530-9298</a> &nbsp;·&nbsp; <a href="mailto:sales@westcangrhs.com">sales@westcangrhs.com</a></div>
</div></div>'''

def header_nav():
    return f'''{UTILBAR}
<header><div class="wrap nav">
<a class="brand" href="/"><img src="/logo_green.jpg" alt="Westcan Greenhouses Ltd." style="height:44px"></a>
<nav>
<a href="/about.html">Who We Are</a>
<a href="/catalog.html">Catalog</a>
<a href="/availability.html">Current Availability</a>
<a href="/shipping.html">Shipping</a>
<a href="/contact.html">Contact</a>
</nav>
<a class="btn btn-primary" href="/quote.html">My Quote</a>
</div></header>'''

FOOTER = f'''<footer><div class="wrap fcols">
<div><strong style="color:#fff">Westcan Greenhouses Ltd.</strong><br>2527 – 210 Street, Langley, BC V2Z 2A9<br>Wholesale plug &amp; liner propagators since 1981</div>
<div><a href="/catalog.html">Catalog</a> · <a href="/availability.html">Availability</a> · <a href="/shipping.html">Shipping</a> · <a href="/about.html">Who We Are</a> · <a href="/contact.html">Contact</a></div>
<div><a href="tel:+16045309298">+1 604-530-9298</a><br><a href="mailto:sales@westcangrhs.com">sales@westcangrhs.com</a></div>
</div></footer>'''

# live availability chip updater (reads weekly feed; keyed by slug)
AV_JS = '''<script>
(function(){var el=document.getElementById('avchip');if(!el)return;var slug=el.getAttribute('data-slug');
fetch('/availability_feed.json').then(function(r){return r.json()}).then(function(f){
var rs=(f.items||[]).filter(function(i){return i.slug===slug});if(!rs.length)return;
var now=rs.filter(function(i){return i.status==='now'});
if(now.length){var q=now.reduce(function(a,i){return a+(i.now_qty||0)},0);el.className='chip chip-now';el.textContent='AVAILABLE NOW — '+q.toLocaleString()+' plugs';return}
var soon=rs.filter(function(i){return i.status==='soon'});
if(soon.length){var s=soon.sort(function(a,b){return (a.first_year-b.first_year)||(a.first_wk-b.first_wk)})[0];el.className='chip chip-ahead';el.textContent='FIRST AVAILABLE WK'+s.first_wk+' '+s.first_year;return}
el.className='chip chip-none';el.textContent='GROWN TO ORDER';}).catch(function(){});})();
</script>'''

def av_chip(av):
    k = (av or {}).get('k', 'none')
    if k == 'now':
        q = av.get('q')
        return 'chip-now', 'AVAILABLE NOW' + (f' — {q:,} plugs' if q else '')
    if k == 'ahead':
        return 'chip-ahead', f"FIRST AVAILABLE {av.get('wk','')} {av.get('y','')}".strip()
    return 'chip-none', 'GROWN TO ORDER'

# ---------- variety pages ----------
# duplicate names (typo-variant or -2 slugs): shortest slug is primary; the
# others canonical to it and stay out of the sitemap so Google sees one page.
primary_slug = {}
for r in ROWS:
    cur = primary_slug.get(r['n'])
    if cur is None or (len(r['slug']), r['slug']) < (len(cur), cur):
        primary_slug[r['n']] = r['slug']
DUP_SLUGS = {r['slug'] for r in ROWS if primary_slug[r['n']] != r['slug']}

by_genus, by_cat = {}, {}
for r in ROWS:
    if r['slug'] in DUP_SLUGS:
        continue
    by_genus.setdefault(r['g'], []).append(r)
    by_cat.setdefault(r['cat'], []).append(r)

VAR_CSS = '''
.vgrid{display:grid;grid-template-columns:minmax(0,480px) 1fr;gap:44px;align-items:start}
@media(max-width:860px){.vgrid{grid-template-columns:1fr}}
.vphoto{border-radius:14px;overflow:hidden;background:var(--white);border:1px solid var(--line)}
.vphoto img{width:100%;aspect-ratio:4/3;object-fit:cover}
.vphoto .noimg{aspect-ratio:4/3;display:flex;align-items:center;justify-content:center;color:var(--muted);font-family:var(--ff-data);font-size:13px;background:var(--green-soft)}
.common{color:var(--muted);font-size:17px;margin:6px 0 16px}
.facts{margin:22px 0;border-top:1px solid var(--line)}
.facts div{display:flex;justify-content:space-between;gap:18px;padding:10px 0;border-bottom:1px solid var(--line);font-size:15px}
.facts dt{color:var(--muted)}.facts dd{font-weight:600;text-align:right}
.ctas{display:flex;gap:14px;flex-wrap:wrap;margin-top:26px}
.note{font-size:14px;color:var(--muted);margin-top:18px}
.rel{margin-top:64px}
.rel h2{font-family:var(--ff-display);color:var(--navy);font-size:26px;margin-bottom:18px}
.relgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:14px}
.relgrid a{background:var(--white);border:1px solid var(--line);border-radius:10px;padding:14px 16px;font-size:14.5px;font-weight:500}
.relgrid a:hover{border-color:var(--green);color:var(--green)}
.relgrid .rc{display:block;font-family:var(--ff-data);font-size:11.5px;color:var(--muted);font-weight:400;margin-top:3px}
'''

def variety_desc(r):
    name, common, z, us = r['n'], (r.get('common') or '').strip(), (r.get('z') or '').strip(), r.get('us')
    d = f"Wholesale {name}"
    if common: d += f" ({common})"
    d += " plugs & liners from Westcan Greenhouses, Langley BC."
    if z: d += f" Hardy in zones {z}."
    if us == 'yes': d += " US-export eligible."
    d += " Book by the tray or request a quote."
    return d[:158] + '…' if len(d) > 160 else d

def related(r, n=6):
    sib = [x for x in by_genus.get(r['g'], []) if x['slug'] != r['slug']]
    if len(sib) < n:
        extra = [x for x in by_cat.get(r['cat'], []) if x['slug'] != r['slug'] and x not in sib]
        sib += extra[:n - len(sib)]
    return sib[:n]

count = 0
for r in ROWS:
    slug, name = r['slug'], r['n']
    common, cat, z, us = (r.get('common') or '').strip(), r['cat'], (r.get('z') or '').strip(), r.get('us')
    canon = f'{BASE}/varieties/{primary_slug[name]}.html'
    has_photo = slug in photo_slugs
    photo = f'/images/{slug}-1.jpg' if has_photo else None
    ogimg = f'{BASE}{photo}' if photo else f'{BASE}/og-image.jpg'
    title = f"{name} — Wholesale Plugs & Liners | Westcan Greenhouses"
    desc = variety_desc(r)
    cl, ct = av_chip(r.get('av'))
    cpl, cpn = cat_link(cat)

    ld = {"@context": "https://schema.org", "@type": "Product",
          "name": name, "url": canon, "image": ogimg, "description": desc, "category": cat,
          "brand": {"@type": "Organization", "name": "Westcan Greenhouses",
                    "url": BASE + "/"}}
    if common: ld["alternateName"] = common
    bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE + "/"},
        {"@type": "ListItem", "position": 2, "name": cpn, "item": BASE + cpl.split('?')[0]},
        {"@type": "ListItem", "position": 3, "name": name, "item": canon}]}

    photo_html = (f'<img src="{photo}" alt="{esc(name)} — wholesale plug/liner" loading="lazy">'
                  if photo else f'<div class="noimg">Photo coming soon — see live page for details</div>')
    facts = []
    facts.append(f'<div><dt>Botanical name</dt><dd>{esc(name)}</dd></div>')
    if common: facts.append(f'<div><dt>Common name</dt><dd>{esc(common)}</dd></div>')
    facts.append(f'<div><dt>Category</dt><dd><a href="{cpl}" style="color:var(--green)">{esc(cpn)}</a></dd></div>')
    if z: facts.append(f'<div><dt>Hardiness zones</dt><dd>{esc(z)}</dd></div>')
    facts.append(f'<div><dt>US export</dt><dd>{"Eligible" if us=="yes" else ("Not eligible" if us=="no" else "Ask us")}</dd></div>')
    facts.append('<div><dt>Sold as</dt><dd>Wholesale plug/liner trays</dd></div>')

    rel_html = ''.join(
        f'<a href="/varieties/{x["slug"]}.html">{esc(x["n"])}<span class="rc">{esc(x["cat"])}</span></a>'
        for x in related(r))

    page = f'''{head(title, desc, canon, ogimg, VAR_CSS)}
<body>
{header_nav()}
<div class="wrap crumbs"><a href="/">Home</a> › <a href="{cpl}">{esc(cpn)}</a> › {esc(name)}</div>
<main class="wrap">
<div class="vgrid">
<div class="vphoto">{photo_html}</div>
<div>
<span id="avchip" data-slug="{esc(slug)}" class="chip {cl}">{ct}</span>
<h1 style="font-size:clamp(28px,3.6vw,42px);margin-top:14px">{esc(name)}</h1>
<p class="common">{esc(common) + " · " if common else ""}Wholesale {esc(cpn.lower() if cat in CAT_PAGE else "plugs & liners")} grown in Langley, BC</p>
<p>{esc(name)}{f" ({esc(common)})" if common else ""} is propagated by Westcan Greenhouses as a wholesale plug/liner for growers, landscapers and re-wholesalers across Canada{" and the US" if us == "yes" else ""}. {"Hardy in zones " + esc(z) + ". " if z else ""}We custom-grow to your specs and ship from our Langley, BC greenhouses — boxed FedEx or freight pallets.</p>
<dl class="facts">{''.join(facts)}</dl>
<div class="ctas">
<a class="btn btn-primary" href="/variety.html?v={esc(slug)}">Check availability &amp; book</a>
<a class="btn btn-ghost" href="/contact.html">Ask a question</a>
</div>
<p class="note">Weekly availability is updated every Monday — the live booking page always shows current stock, plug sizes and delivery weeks. <a href="/shipping.html" style="text-decoration:underline">Estimate freight</a> to your location.</p>
</div>
</div>
<div class="rel"><h2>More from our range</h2><div class="relgrid">{rel_html}</div>
<p style="margin-top:18px"><a href="/catalog.html" style="color:var(--green);font-weight:600">Browse the full catalog ({len(ROWS)} varieties) →</a></p></div>
</main>
{FOOTER}
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(bc, ensure_ascii=False)}</script>
{AV_JS}
</body>
</html>'''
    open(f'{OUT}/varieties/{slug}.html', 'w', encoding='utf-8').write(page)
    count += 1
print(f'wrote {count} variety pages ({sum(1 for r in ROWS if r["slug"] in photo_slugs)} with photos)')

# ---------- category landing pages ----------
CAT_COPY = {
 'perennial-liners.html': dict(
   cats=['Perennials'], img='/images/cat-perennials.jpg',
   title='Wholesale Perennial Plugs & Liners — Westcan Greenhouses',
   h1='Perennial Liners, Wholesale',
   desc='Wholesale perennial plugs & liners — {n} varieties propagated in Langley, BC and shipped to growers across Canada & the US. Book by the tray.',
   intro=[
    'Perennials are the heart of what we grow. Our current range runs to {n} varieties — from workhorse genera like Hosta, Heuchera, Echinacea, Salvia, Rudbeckia and Geum to newer breeder introductions from partners including Terra Nova Nurseries, Darwin Perennials, Jelitto and Ball Seed.',
    'Every liner starts in our Langley, BC propagation houses and ships as a uniform, well-rooted plug ready for your finishing program. Most varieties are offered in multiple cell sizes, and our booking program lets you lock in delivery weeks up to a season ahead — or pull from the weekly availability list when you need product now.',
    'Ordering is simple: browse the varieties below or the full catalog, add trays to your quote, and send it through your broker or direct. We ship across Canada and to US growers (US-eligible varieties are flagged on every page), boxed FedEx or on freight pallets.']),
 'ornamental-grass-plugs.html': dict(
   cats=['Grasses'], img='/images/cat-grasses.jpg',
   title='Wholesale Ornamental Grass Plugs — Westcan Greenhouses',
   h1='Ornamental Grass &amp; Sedge Plugs, Wholesale',
   desc='Wholesale ornamental grass and sedge plugs — {n} varieties including Carex, Calamagrostis, Miscanthus, Festuca and Panicum. Grown in Langley, BC.',
   intro=[
    'From Calamagrostis ‘Karl Foerster’ to the full EverColor® Carex series, we propagate {n} ornamental grass and sedge varieties as wholesale plugs. The range covers the landscape staples — Miscanthus, Panicum, Pennisetum, Festuca, Deschampsia, Stipa and Juncus — plus shade-tolerant Carex and Hakonechloa for finished container programs.',
    'Grass plugs are among our fastest-turning items: they bulk quickly, finish predictably, and our weekly availability usually carries strong numbers through the season. For larger landscape jobs or contract grows, book trays ahead and we’ll gate deliveries to your schedule.',
    'Every variety page shows hardiness zone and US-export eligibility. Add trays to a quote and send it through your broker or direct — we ship from Langley, BC across Canada and to the US.']),
 'fern-liners.html': dict(
   cats=['Ferns'], img='/images/cat-ferns.jpg',
   title='Wholesale Fern Liners — Westcan Greenhouses',
   h1='Fern Liners, Wholesale',
   desc='Wholesale fern liners — {n} varieties including Dryopteris, Athyrium, Polystichum, Blechnum and Matteuccia, propagated in Langley, BC.',
   intro=[
    'Ferns do well on the coast, and they do well for us: we propagate {n} fern varieties as wholesale liners, including Dryopteris ‘Brilliance’ and Autumn Fern, Athyrium (lady and Japanese painted ferns), Polystichum, Blechnum spicant (deer fern) and Matteuccia (ostrich fern).',
    'Fern liners from our Langley houses arrive hardened and evenly rooted, ready to bump into quarts, gallons or shade-garden programs. Note that a few native ferns are not US-export eligible — eligibility is flagged clearly on every variety page and in the catalog filters.',
    'Check the live availability list for what ships this week, or book trays ahead for spring shade programs. Quotes go through your broker or direct, whichever you prefer.']),
 'ground-cover-plugs.html': dict(
   cats=['Ground Covers'], img='/images/cat-groundcovers.jpg',
   title='Wholesale Ground Cover Plugs — Westcan Greenhouses',
   h1='Ground Cover Plugs, Wholesale',
   desc='Wholesale ground cover plugs — {n} varieties including Ajuga, Sedum, Thymus, Sagina, Pachysandra and Arctostaphylos. Grown in Langley, BC.',
   intro=[
    'We grow {n} ground cover varieties as wholesale plugs — the fillers, spillers and mat-formers that landscape contracts and container programs burn through: Ajuga, Sedum, Thymus, Sagina (Irish and Scotch moss), Pachysandra, Lamium, Lysimachia, Delosperma and native Arctostaphylos uva-ursi among them.',
    'Ground covers ship as dense, well-established plugs that knit in fast. For big landscape takeoffs, send us the plant schedule — we’ll quote the full list and gate deliveries by phase. For garden centre programs, mixed orders across varieties are no problem.',
    'Browse the range below, check what’s on the truck this week on the availability list, or book ahead for spring. US-export eligibility is flagged on every variety.']),
 'shrub-conifer-liners.html': dict(
   cats=['Shrubs', 'Conifers', 'Heathers'], img='/images/cat-shrubs.jpg',
   title='Wholesale Shrub & Conifer Liners — Westcan Greenhouses',
   h1='Shrub &amp; Conifer Liners, Wholesale',
   desc='Wholesale shrub and conifer liners — {n} varieties including Nandina, Pieris, Hydrangea, Spiraea, Buxus, Cupressus and Chamaecyparis. Langley, BC.',
   intro=[
    'Our shrub and conifer program covers {n} varieties of starter liners for nursery finishing: Nandina, Pieris, Hydrangea, Spiraea, Weigela, Physocarpus, Buxus and broadleaf staples, alongside conifers like Cupressus macrocarpa, Chamaecyparis and heathers.',
    'Shrub liners leave Langley well-rooted and uniform — sized to bump straight into 1- and 2-gallon production. Because we propagate in-house, we can also contract-grow specific varieties and quantities for future seasons; talk to us about multi-year programs.',
    'Every variety page flags hardiness zone and US-export eligibility. Build a quote from the varieties below or the full catalog, and our team will confirm availability, pricing and freight.']),
}

CAT_CSS = '''
.cathero{display:grid;grid-template-columns:1.2fr 1fr;gap:44px;align-items:center;padding:36px 0 10px}
@media(max-width:860px){.cathero{grid-template-columns:1fr}}
.cathero img{border-radius:14px;border:1px solid var(--line);width:100%;aspect-ratio:4/3;object-fit:cover}
.cathero p{margin-bottom:14px}
.vlist{margin-top:44px}
.vlist h2{font-family:var(--ff-display);color:var(--navy);font-size:28px;margin-bottom:20px}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:16px}
.card{background:var(--white);border:1px solid var(--line);border-radius:12px;overflow:hidden}
.card:hover{border-color:var(--green)}
.card img{width:100%;aspect-ratio:4/3;object-fit:cover}
.card .cb{padding:13px 15px;font-weight:600;font-size:14.5px}
.card .cb span{display:block;font-family:var(--ff-data);font-weight:400;font-size:11.5px;color:var(--muted);margin-top:3px}
.morelinks{margin-top:34px;display:flex;gap:12px;flex-wrap:wrap}
'''

for fname, c in CAT_COPY.items():
    rows = [r for r in ROWS if r['cat'] in c['cats']]
    n = len(rows)
    canon = f'{BASE}/{fname}'
    title, desc = c['title'], c['desc'].format(n=n)
    with_photo = [r for r in rows if r['slug'] in photo_slugs]
    featured = (with_photo + [r for r in rows if r not in with_photo])[:12]
    cards = ''.join(
        f'''<a class="card" href="/varieties/{r["slug"]}.html">{f'<img loading="lazy" src="/images/{r["slug"]}-1.jpg" alt="{esc(r["n"])}">' if r["slug"] in photo_slugs else ''}<div class="cb">{esc(r["n"])}<span>{esc(r.get("common") or r["cat"])}</span></div></a>'''
        for r in featured)
    genera = sorted({r['g'] for r in rows})
    intro_html = ''.join(f'<p>{p.format(n=n)}</p>' for p in c['intro'])
    other_cats = ''.join(f'<a class="btn btn-ghost" href="/{f2}">{CAT_COPY[f2]["h1"].replace(", Wholesale","")}</a>'
                         for f2 in CAT_COPY if f2 != fname)
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": title,
          "url": canon, "description": desc,
          "mainEntity": {"@type": "ItemList", "numberOfItems": n, "itemListElement": [
              {"@type": "ListItem", "position": i + 1, "name": r['n'],
               "url": f'{BASE}/varieties/{r["slug"]}.html'} for i, r in enumerate(featured)]}}
    from urllib.parse import quote as _q
    cat_filter_link = '/catalog.html?cat=' + _q(c['cats'][0])
    page = f'''{head(title, desc, canon, f'{BASE}/og-image.jpg', CAT_CSS)}
<body>
{header_nav()}
<div class="wrap crumbs"><a href="/">Home</a> › {c['h1'].replace(', Wholesale','')}</div>
<main class="wrap">
<div class="cathero">
<div>
<h1 style="font-size:clamp(30px,4vw,46px);margin-bottom:18px">{c['h1']}</h1>
{intro_html}
<div class="morelinks"><a class="btn btn-primary" href="{cat_filter_link}">Browse all {n} in the catalog</a>
<a class="btn btn-ghost" href="/availability.html">What ships this week</a></div>
</div>
<img src="{c['img']}" alt="{esc(c['h1'].replace('&amp;','&'))} — Westcan Greenhouses" loading="lazy">
</div>
<div class="vlist">
<h2>Featured varieties</h2>
<div class="cards">{cards}</div>
<p style="margin-top:22px;color:var(--muted);font-size:14.5px">Genera in this range: {esc(', '.join(genera))}.</p>
<div class="morelinks">{other_cats}</div>
</div>
</main>
{FOOTER}
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</body>
</html>'''
    open(f'{OUT}/{fname}', 'w', encoding='utf-8').write(page)
    print(f'wrote {fname} ({n} varieties, {len(with_photo)} with photos)')

# ---------- sitemap ----------
static_pages = [('', 'weekly', '1.0'), ('catalog.html', 'weekly', '0.9'), ('availability.html', 'weekly', '0.9'),
                ('about.html', 'monthly', '0.7'), ('shipping.html', 'monthly', '0.6'),
                ('contact.html', 'monthly', '0.6'), ('quote.html', 'monthly', '0.5')]
static_pages += [(f, 'weekly', '0.8') for f in CAT_COPY]
urls = [f'  <url><loc>{BASE}/{p}</loc><changefreq>{cf}</changefreq><priority>{pr}</priority></url>'
        for p, cf, pr in static_pages]
urls += [f'  <url><loc>{BASE}/varieties/{r["slug"]}.html</loc><changefreq>monthly</changefreq><priority>0.6</priority></url>'
         for r in ROWS if r['slug'] not in DUP_SLUGS]
open(f'{OUT}/sitemap.xml', 'w', encoding='utf-8').write(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + '\n'.join(urls) + '\n</urlset>\n')
print(f'wrote sitemap.xml ({len(urls)} URLs)')
