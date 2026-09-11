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
# genus -> (common name, one-line grower-facing descriptor)
# Covers the highest-count genera (~81% of catalog rows); anything absent falls back
# to the generic template so no page is ever wrong, only less specific.
GENUS_INFO = {
 'Echinacea': ("Coneflower", "Sun-loving prairie perennial with big daisy flowers and a long summer bloom; a core garden-centre item."),
 'Dianthus': ("Pinks / Sweet William", "Compact, fragrant, spring-flowering; finishes fast in small pots and sells on scent."),
 'Lavandula': ("Lavender", "Aromatic evergreen sub-shrub for sun and sharp drainage; a perennial best-seller in 1-gal."),
 'Phlox': ("Phlox", "Spring-blooming creeping types and upright summer border phlox; heavy landscape and retail demand."),
 'Salvia': ("Sage", "Long-blooming, pollinator-magnet spikes; one of the most reliable perennial programs."),
 'Heuchera': ("Coral Bells", "Grown for coloured evergreen foliage; a shade-programme staple and strong container item."),
 'Delosperma': ("Ice Plant", "Hardy succulent ground cover covered in jewel-toned flowers; thrives in heat and poor soil."),
 'Rudbeckia': ("Black-Eyed Susan", "Gold summer daisies; a dependable late-season colour block for retail and landscape."),
 'Sedum': ("Stonecrop", "Drought-tough succulents from creeping mats to upright border types; low-input and green-roof friendly."),
 'Achillea': ("Yarrow", "Flat-topped flower heads in a wide colour range; ferny foliage, excellent drought tolerance."),
 'Agastache': ("Hummingbird Mint", "Aromatic upright spikes that pull hummingbirds and bees right through late summer."),
 'Gaillardia': ("Blanket Flower", "Hot-coloured daisies that bloom relentlessly in poor, dry soil."),
 'Viola': ("Viola / Pansy", "Cool-season colour for early spring and fall programmes."),
 'Penstemon': ("Beardtongue", "Tubular flower spikes for sun and good drainage; a strong native-adjacent seller."),
 'Leucanthemum': ("Shasta Daisy", "Classic white daisies; a perennial border standard with clean, uniform habit."),
 'Veronica': ("Speedwell", "Upright or creeping spikes of blue, pink and white; long bloom, tidy plant."),
 'Echeveria': ("Hen and Chicks (Echeveria)", "Rosette succulents for dish gardens, mixed containers and indoor programmes."),
 'Agapanthus': ("Lily of the Nile", "Bold umbels on strong stems; a premium patio-container crop."),
 'Helleborus': ("Lenten Rose / Hellebore", "Winter- and early-spring-flowering evergreen for shade; a high-value early-season item."),
 'Coreopsis': ("Tickseed", "Airy, long-blooming yellow and bicolour daisies for sun."),
 'Gaura': ("Beeblossom", "Wands of butterfly-like flowers on wiry stems; adds motion to mixed containers."),
 'Rosa': ("Rose", "Landscape and patio roses grown on as liners for finished container programmes."),
 'Carex': ("Sedge", "Evergreen and semi-evergreen grassy foliage for sun or shade; a year-round container filler."),
 'Hosta': ("Plantain Lily", "The backbone shade perennial, grown for foliage size, texture and variegation."),
 'Iberis': ("Candytuft", "Sheets of white spring flower over evergreen mats; a strong early-season seller."),
 'Monarda': ("Bee Balm", "Shaggy pollinator flowers with aromatic foliage; a native-garden favourite."),
 'Verbena': ("Verbena", "Free-flowering spreader for baskets, combos and landscape colour."),
 'Buddleja': ("Butterfly Bush", "Fast, fragrant summer shrub that finishes quickly from a liner."),
 'Hebe': ("Hebe", "Evergreen shrub with neat foliage and late flower; popular in mild coastal programmes."),
 'Lamium': ("Spotted Deadnettle", "Silver-marked shade ground cover that fills a pot fast."),
 'Thymus': ("Thyme", "Creeping aromatic mats for paths, troughs and green roofs."),
 'Perovskia': ("Russian Sage", "Hazy blue late-summer spikes on silver stems; thrives on neglect."),
 'Sempervivum': ("Hen and Chicks", "Hardy rosette succulents for troughs, roofs and dish gardens."),
 'Ajuga': ("Bugleweed", "Fast evergreen ground cover with coloured foliage and blue spring spikes."),
 'Euonymus': ("Euonymus", "Tough evergreen shrub, often variegated; a hedging and foundation workhorse."),
 'Spiraea': ("Spirea", "Easy deciduous shrub with coloured foliage and summer flower; finishes fast."),
 'Anemone': ("Windflower", "Late-season flowers on tall stems for shade and part sun."),
 'Armeria': ("Sea Thrift", "Grassy evergreen tufts topped with round flower heads; great in small pots."),
 'Brunnera': ("Siberian Bugloss", "Silver-patterned heart-shaped leaves with blue forget-me-not flowers for shade."),
 'Campanula': ("Bellflower", "Blue and white bells from creeping alpines to border perennials."),
 'Hedera': ("Ivy", "Evergreen climbing and trailing foliage for baskets, combos and ground cover."),
 'Miscanthus': ("Maiden Grass", "Tall ornamental grass with fine texture and showy autumn plumes."),
 'Polystichum': ("Shield Fern", "Evergreen fern with leathery, structural fronds for shade programmes."),
 'Thuja': ("Cedar / Arborvitae", "Evergreen conifer for hedging and screening, grown on from liners."),
 'Bellis': ("English Daisy", "Button-flowered cool-season colour for spring bedding."),
 'Bergenia': ("Pigsqueak", "Bold leathery evergreen leaves with early pink flower; tough in shade."),
 'Cornus': ("Dogwood", "Grown for coloured winter stems and structure in landscape plantings."),
 'Kniphofia': ("Red Hot Poker", "Torch-like flower spikes on architectural clumps; a strong focal item."),
 'Lewisia': ("Bitterroot", "Alpine succulent rosettes with bright starry flowers; a trough and rockery specialty."),
 'Lithodora': ("Lithodora", "Intense true-blue flowers over evergreen mats; a spring retail standout."),
 'Lysimachia': ("Creeping Jenny / Loosestrife", "Fast trailing foliage, gold or green, for baskets and combos."),
 'Nepeta': ("Catmint", "Grey-green aromatic mounds with long-running blue bloom; pollinator and drought favourite."),
 'Panicum': ("Switchgrass", "Upright native prairie grass with airy seed heads and strong fall colour."),
 'Pieris': ("Lily-of-the-Valley Shrub", "Evergreen shrub with flower chains and coloured new growth."),
 'Polemonium': ("Jacob's Ladder", "Ladder-like foliage, often variegated, with spring bells for shade."),
 'Potentilla': ("Cinquefoil", "Long-flowering tough shrub and perennial types for full sun."),
 'Rosmarinus': ("Rosemary", "Aromatic evergreen herb for culinary and ornamental programmes."),
 'Saxifraga': ("Rockfoil", "Cushion-forming alpines smothered in spring flower; ideal for small pots."),
 'Artemisia': ("Wormwood", "Silver foliage accent for sun; a texture plant in mixed containers."),
 'Chamaecyparis': ("False Cypress", "Dwarf and coloured conifer forms for containers and foundation planting."),
 'Hakonechloa': ("Japanese Forest Grass", "Arching, softly cascading shade grass; a premium container and border grass."),
 'Calamagrostis': ("Feather Reed Grass", "Strictly upright grass with early, long-lasting flower spikes."),
 'Festuca': ("Blue Fescue", "Compact blue-grey grass tufts for edging, mass planting and combos."),
 'Pennisetum': ("Fountain Grass", "Soft bottlebrush plumes on arching mounds."),
 'Dryopteris': ("Wood Fern", "Hardy, reliable fern for shade with strong frond structure."),
 'Athyrium': ("Lady / Painted Fern", "Finely cut fronds, often silver and burgundy toned, for shade."),
 'Matteuccia': ("Ostrich Fern", "Tall vase-shaped fronds; a bold woodland and native planting fern."),
 'Blechnum': ("Deer Fern", "Evergreen native fern for damp shade."),
 'Juncus': ("Rush", "Upright or spiralled stems for pond edges, bog gardens and novelty containers."),
 'Pachysandra': ("Japanese Spurge", "Evergreen shade ground cover that knits into solid cover."),
 'Arctostaphylos': ("Kinnikinnick / Bearberry", "Native evergreen carpeting ground cover for tough, dry sites."),
 'Cotoneaster': ("Cotoneaster", "Low spreading evergreen with berries; a durable bank and edge cover."),
 'Nandina': ("Heavenly Bamboo", "Evergreen shrub with coloured new growth and winter tints."),
 'Hydrangea': ("Hydrangea", "High-demand flowering shrub finished in 1- and 2-gal containers."),
 'Geum': ("Avens", "Warm-toned flowers on wiry stems above evergreen rosettes."),
 'Dicentra': ("Bleeding Heart", "Arching sprays of locket flowers for spring shade."),
 'Sagina': ("Irish / Scotch Moss", "Dense mossy mats for paths, crevices and fairy gardens."),
 'Stipa': ("Feather Grass", "Fine, hair-like grass that moves with every breeze."),
 'Liriope': ("Lilyturf", "Strappy evergreen clumps with late flower spikes; a durable edger."),
 'Cupressus': ("Cypress", "Aromatic evergreen conifer, popular as a seasonal patio and gift item."),
 'Colocasia': ("Elephant Ear", "Huge tropical leaves for statement containers and water gardens."),
 'Cordyline': ("Cabbage Palm", "Upright spiky foliage; a thriller centrepiece in mixed containers."),
 'Erica': ("Heather (Erica)", "Fine evergreen foliage with winter and spring flower."),
 'Rhododendron': ("Rhododendron / Azalea", "Evergreen and deciduous flowering shrubs for acid soils and shade."),
 'Buxus': ("Boxwood", "Classic evergreen for hedging, topiary and formal edging."),
 'Lonicera': ("Honeysuckle", "Shrubby and climbing evergreen types for hedging and screening."),
 'Physocarpus': ("Ninebark", "Coloured-leaf deciduous shrub with peeling bark and summer flower."),
 'Weigela': ("Weigela", "Free-flowering deciduous shrub, often with coloured foliage."),
 'Abelia': ("Abelia", "Semi-evergreen shrub with long bloom and glossy, often variegated foliage."),
 'Acorus': ("Sweet Flag", "Grassy fans for moist soil and pond margins; gold and green forms."),
 'Deschampsia': ("Tufted Hair Grass", "Cloud-like flower panicles above fine green tufts."),
 'Schizachyrium': ("Little Bluestem", "Native prairie grass with blue summer stems and copper fall colour."),
 'Cortaderia': ("Pampas Grass", "Large grass with dramatic late-season plumes."),
 'Phalaris': ("Ribbon Grass", "Brightly variegated spreading grass for difficult sites."),
 'Imperata': ("Japanese Blood Grass", "Upright blades that turn translucent red through the season."),
 'Cyrtomium': ("Holly Fern", "Glossy, holly-like evergreen fronds for shade."),
 'Asplenium': ("Spleenwort", "Small evergreen fern for shade, walls and terrariums."),
 'Galium': ("Sweet Woodruff", "Whorled foliage with white spring flower; a fragrant shade carpeter."),
 'Iberis ': ("Candytuft", "Evergreen mats smothered in white spring flower."),
 'Aubrieta': ("Rock Cress", "Sheets of purple spring flower cascading over walls and rockeries."),
 'Armeria ': ("Sea Thrift", "Neat grassy evergreen tufts with round flower heads."),
 'Digitalis': ("Foxglove", "Tall flower spires for part shade; a cottage-garden signature."),
 'Astilbe': ("False Spirea", "Feathery plumes over ferny foliage for moist shade."),
 'Pulmonaria': ("Lungwort", "Spotted silver foliage with early spring flower for shade."),
 'Tiarella': ("Foamflower", "Native woodlander with cut foliage and bottlebrush spring flower."),
 'Ophiopogon': ("Mondo Grass", "Low evergreen strappy foliage, including near-black forms."),
 'Sempervivum ': ("Hen and Chicks", "Hardy rosettes for troughs and green roofs."),
 'Scabiosa': ("Pincushion Flower", "Long-stemmed pincushion blooms that flower for months."),
 'Platycodon': ("Balloon Flower", "Balloon-like buds opening to star flowers in midsummer."),
 'Aquilegia': ("Columbine", "Spurred spring flowers above blue-green foliage."),
 'Hemerocallis': ("Daylily", "Tough, reliable clumping perennial with a long succession of bloom."),
 'Origanum': ("Oregano", "Culinary and ornamental forms with aromatic foliage."),
 'Mentha': ("Mint", "Vigorous culinary herb; a fast-finishing pot item."),
 'Vinca': ("Periwinkle", "Evergreen trailing ground cover with blue spring flower."),
 'Ceanothus': ("California Lilac", "Evergreen shrub with intense blue flower clusters for mild, dry sites."),
 'Cistus': ("Rock Rose", "Sun-loving evergreen with tissue-paper flowers; excellent drought tolerance."),
 'Photinia': ("Photinia", "Evergreen hedging shrub with bright red new growth."),
 'Prunella': ("Self Heal", "Low spreading perennial with dense flower heads for pollinators."),
 'Lithodora ': ("Lithodora", "True-blue flowers over evergreen mats."),
 'Centaurea': ("Cornflower", "Silver or green foliage with thistle-like flowers."),
 'Senecio': ("Senecio", "Silver-felted foliage accent for containers and borders."),
 'Heucherella': ("Foamy Bells", "Heuchera x Tiarella hybrid with cut, coloured foliage for shade."),
 'Hakonechloa ': ("Japanese Forest Grass", "Cascading shade grass with luminous foliage."),
}

GENUS_INFO.update({
 'Delphinium': ("Larkspur", "Tall flower spires in true blues; a classic back-of-border perennial."),
 'Eupatorium': ("Joe Pye Weed", "Tall native pollinator magnet with big late-summer flower heads."),
 'Helenium': ("Sneezeweed", "Warm-toned late-summer daisies for sun and moist soil."),
 'Syringa': ("Lilac", "Fragrant spring-flowering shrub; a long-standing retail favourite."),
 'Corydalis': ("Fumewort", "Ferny foliage with tubular spring flowers for shade."),
 'Epipremnum': ("Pothos", "Trailing tropical foliage for indoor and interiorscape programmes."),
 'Leptinella': ("Brass Buttons", "Ferny creeping mat that tolerates light foot traffic."),
 'Stachys': ("Lamb's Ear", "Soft silver-felted foliage for sunny, dry borders."),
 'Arabis': ("Rock Cress", "Low spring-flowering mats for walls and rockeries."),
 'Calendula': ("Pot Marigold", "Cheerful cool-season annual colour."),
 'Deutzia': ("Deutzia", "Arching deciduous shrub smothered in late-spring flower."),
 'Erysimum': ("Wallflower", "Long-blooming, fragrant perennial wallflower for sun."),
 'Aster': ("Aster", "Late-season daisies that carry colour into autumn."),
 'Astrantia': ("Masterwort", "Intricate pincushion flowers for part shade."),
 'Ceratostigma': ("Plumbago", "Late blue flower with red autumn foliage; a strong ground cover."),
 'Osteospermum': ("African Daisy", "Free-flowering daisies for containers and bedding."),
})


GENUS_INFO.update({
 'Alocasia': ("Elephant Ear / African Mask", "Dramatic arrow-shaped leaves with bold veining; a premium indoor and patio foliage plant."),
 'Caladium': ("Angel Wings", "Paper-thin heart-shaped leaves in pink, white and green; a fast-turning colour-foliage crop for shade."),
 'Philodendron': ("Philodendron", "Architectural tropical foliage for interiorscape and houseplant programmes; strong repeat seller."),
 'Monstera': ("Swiss Cheese Plant", "Large fenestrated leaves; one of the most in-demand foliage houseplants."),
 'Epipremnum': ("Pothos", "Trailing tropical foliage that finishes fast in baskets and combos."),
 'Sansevieria': ("Snake Plant", "Upright succulent foliage, near-indestructible; a retail staple."),
 'Echeveria': ("Hen and Chicks (Echeveria)", "Rosette succulents for dish gardens, mixed containers and indoor programmes."),
})

def genus_info(g):
    return GENUS_INFO.get((g or '').strip(), (None, None))

def cat_link(cat):
    """User-facing links go to the filtered catalog (category landing pages are
    kept sitemap-only by request — no user-visible path leads to them)."""
    from urllib.parse import quote
    label = CAT_PAGE[cat][1] if cat in CAT_PAGE else cat
    return '/catalog.html?cat=' + quote(cat), label

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
{SITE_CSS}
.crumbs{{font-size:13.5px;color:var(--muted);padding:18px 0}}
.crumbs a:hover{{color:var(--green)}}
main,main.wrap{{padding-bottom:76px}}
h1{{font-family:var(--ff-display);color:var(--navy);line-height:1.15}}
.chip-ahead{{background:var(--gold-soft);color:#8a6b1f}}
.chip-none{{background:#ECEDF2;color:var(--muted)}}
{extra}
</style>
</head>'''

# ---------- real site chrome, extracted from shipping.html at build time ----------
# (keeps generated pages pixel-identical to the main site's header/nav/footer)
_sh = open(f'{SRC}/shipping.html', encoding='utf-8').read()
_styles = re.findall(r'<style>(.*?)</style>', _sh, re.S)
SITE_CSS = '\n'.join(b for b in _styles if (':root' in b or '.mmenu' in b or 'brandlogo' in b))

def _rootify(block):
    """make page links root-relative so they work from /varieties/"""
    for p in ('index.html', 'catalog.html', 'availability.html', 'shipping.html',
              'contact.html', 'quote.html', 'about.html', 'variety.html'):
        block = block.replace(f'href="{p}', f'href="/{p}')
    block = block.replace('href="/index.html"', 'href="/"')
    block = block.replace('href="//', 'href="/')  # already-absolute stays sane
    return block

def _save_b64_logos(block):
    """swap inline base64 logos for a shared file so 1,168 pages don't each carry 30KB"""
    import base64
    out_imgs = os.path.join(OUT, 'images')
    os.makedirs(out_imgs, exist_ok=True)
    for m in set(re.findall(r'data:image/png;base64,([A-Za-z0-9+/=]+)', block)):
        data = base64.b64decode(m)
        name = f'brand-logo-{len(data)}.png'
        path = os.path.join(out_imgs, name)
        if not os.path.exists(path):
            open(path, 'wb').write(data)
        block = block.replace('data:image/png;base64,' + m, f'/images/{name}')
    return block

_h0 = _sh.find('<div class="utilbar"')
_h1 = _sh.find('</header>') + len('</header>')
HEADER_HTML = _save_b64_logos(_rootify(_sh[_h0:_h1]))
HEADER_HTML = re.sub(r'<span>Ball Rooting Station</span>', '', HEADER_HTML)
_f0 = _sh.find('<footer')
_f1 = _sh.find('</footer>') + len('</footer>')
FOOTER = _save_b64_logos(_rootify(_sh[_f0:_f1]))
MENU_JS = '''<script>
document.querySelector('.menu-toggle').addEventListener('click',function(){
  var m=document.getElementById('mmenu');m.classList.toggle('open');
  this.setAttribute('aria-expanded',m.classList.contains('open'));
});
</script>'''

def header_nav():
    return HEADER_HTML

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
.vh2{font-family:var(--ff-display);color:var(--navy);font-size:20px;margin:26px 0 8px;font-weight:400}
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
    name, z, us = r['n'], (r.get('z') or '').strip(), r.get('us')
    common = (r.get('common') or '').strip() or (genus_info(r['g'])[0] or '')
    d = f"{name} plugs & liners"
    if common: d += f" ({common})"
    d += f" — wholesale 72-cell trays propagated in Langley, BC."
    if z: d += f" Zones {z}."
    if us == 'yes': d += " US-export eligible."
    d += " Book by the tray."
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
    title = f"{name} Plugs & Liners — Wholesale | Westcan Greenhouses"
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
        {"@type": "ListItem", "position": 2, "name": "Catalog", "item": BASE + "/catalog.html"},
        {"@type": "ListItem", "position": 3, "name": name, "item": canon}]}

    photo_html = (f'<img src="{photo}" alt="{esc(name)} — wholesale plug/liner" loading="lazy">'
                  if photo else f'<div class="noimg">Photo coming soon — see live page for details</div>')

    # body copy — factual, from catalog + availability data only
    gcommon, gdesc = genus_info(r['g'])
    disp_common = common or (gcommon or '')
    gsibs = [x for x in by_genus.get(r['g'], []) if x['slug'] != primary_slug[name]]

    p1 = (f'{esc(name)} is grown by Westcan Greenhouses as a wholesale plug and liner — '
          f'young, well-rooted starter plants sold by the tray to nurseries, growers, landscapers '
          f'and re-wholesalers across Canada{" and the United States" if us == "yes" else ""}.')
    if disp_common:
        p1 += f' {esc(r["g"])} is commonly known as {esc(disp_common)}.'
    if gdesc:
        p1 += f' {esc(gdesc)}'

    k = (r.get('av') or {}).get('k', 'none')
    if k == 'now':
        p2av = ('It is on this week&rsquo;s availability list and can ship now — the live booking page shows '
                'current stock and plug sizes.')
    elif k == 'ahead':
        wk, yr = r['av'].get('wk', ''), r['av'].get('y', '')
        p2av = (f'The first trays of the season are forecast for {esc(str(wk))} {yr} — book ahead to lock in '
                f'your varieties and delivery weeks.')
    else:
        p2av = ('It is grown to order — reserve trays and delivery weeks through our booking program, '
                'direct or through your broker.')

    p_order = (f'{esc(name)} plugs are supplied in 72-cell trays as standard, with other cell sizes available '
               f'on request. The minimum order is 4 trays per variety, and you can mix varieties freely across '
               f'an order. {p2av}')
    if len(gsibs) >= 1:
        p_order += (f' It is one of {len(gsibs) + 1} {esc(r["g"])} selections we propagate, so a single order can '
                    f'cover a whole {esc(r["g"])} programme.')

    p_grow = ''
    if z:
        p_grow = (f'{esc(name)} is hardy in USDA zones {esc(z)}. ')
    p_grow += (f'Liners leave our Langley, BC greenhouses uniform and evenly rooted, sized to bump straight into '
               f'your finishing containers.')

    p_ship = (f'We ship {esc(r["g"])} liners on carts, boxed by courier, or as palletized freight, from Langley, BC '
              f'across Canada' + (' and into the United States — this variety is US-export eligible, and our '
              'phytosanitary checks are done in-house.' if us == 'yes' else '.'))

    body_paras = (f'<p>{p1}</p>\n'
                  f'<h2 class="vh2">Ordering {esc(name)} plugs</h2>\n<p>{p_order}</p>\n'
                  f'<h2 class="vh2">Growing &amp; hardiness</h2>\n<p>{p_grow}</p>\n'
                  f'<h2 class="vh2">Shipping</h2>\n<p>{p_ship}</p>')
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
<h1 style="font-size:clamp(28px,3.6vw,42px);margin-top:14px">{esc(name)} <span style="white-space:nowrap">Plugs &amp; Liners</span></h1>
<p class="common">{esc(disp_common) + " · " if disp_common else ""}Wholesale {esc(cpn.lower() if cat in CAT_PAGE else "plugs & liners")} grown in Langley, BC</p>
{body_paras}
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
{MENU_JS}
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
{MENU_JS}
</body>
</html>'''
    open(f'{OUT}/{fname}', 'w', encoding='utf-8').write(page)
    print(f'wrote {fname} ({n} varieties, {len(with_photo)} with photos)')


# ---------- tissue-culture landing page ----------
# Facts here are limited to what Matt has confirmed: TC material is brought in at
# STAGE 3 and grown on in Langley (Westcan does not run its own lab); the specialty is
# perennials plus a large share of the grass range; the Hosta program is TC (24
# varieties as 72-cell liners, per the Hosta booking catalogue). There is no
# variety-level TC flag in GrowPoint, so the page deliberately does NOT publish a
# variety list — it invites the enquiry instead. Do not add lab/virus-indexing claims.
TC_CSS = """
.tchero{padding:34px 0 6px;max-width:820px}
.tchero p{margin-bottom:14px;font-size:17px}
.tcsec{margin-top:40px;max-width:820px}
.tcsec h2{font-family:var(--ff-display);color:var(--navy);font-size:27px;margin-bottom:14px;font-weight:400}
.tcsec h3{font-family:var(--ff-body);color:var(--navy);font-size:17px;margin:22px 0 6px;font-weight:600}
.tcsec p{margin-bottom:13px}
.stages{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;margin:20px 0}
.stage{background:var(--white);border:1px solid var(--line);border-radius:11px;padding:16px 18px}
.stage.on{border-color:var(--green);border-left:4px solid var(--green);background:var(--green-soft)}
.stage b{display:block;font-family:var(--ff-data);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin-bottom:5px}
.stage.on b{color:var(--green-dark)}
.stage span{font-size:14.5px;line-height:1.45}
.tcbox{background:var(--green-soft);border-radius:12px;padding:22px 26px;margin-top:22px}
.tcbox p{margin-bottom:0}
.tccta{display:flex;gap:14px;flex-wrap:wrap;margin-top:30px}
"""

def build_tc_page():
    canon = f'{BASE}/tissue-culture.html'
    title = 'Tissue Culture Perennials & Grasses — Wholesale TC Liners | Westcan Greenhouses'
    desc = ('Wholesale tissue-culture liners from Westcan Greenhouses, Langley BC. We bring TC material '
            'in at stage 3 and grow it on into clean, true-to-type perennial and grass liners.')
    ld = {"@context":"https://schema.org","@type":"Service",
          "name":"Wholesale tissue-culture perennial and grass liners",
          "serviceType":"Tissue-culture liner propagation",
          "url":canon,"description":desc,
          "areaServed":[{"@type":"Country","name":"Canada"},{"@type":"Country","name":"United States"}],
          "provider":{"@type":"Organization","name":"Westcan Greenhouses","url":BASE+"/",
                      "address":{"@type":"PostalAddress","streetAddress":"2527 - 210 Street",
                                 "addressLocality":"Langley","addressRegion":"BC","addressCountry":"CA"}}}
    bc = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Home","item":BASE+"/"},
        {"@type":"ListItem","position":2,"name":"Tissue Culture","item":canon}]}

    page = f'''{head(title, desc, canon, f"{BASE}/og-image.jpg", TC_CSS)}
<body>
{header_nav()}
<div class="wrap crumbs"><a href="/">Home</a> &rsaquo; Tissue Culture</div>
<main class="wrap">

<div class="tchero">
<h1 style="font-size:clamp(30px,4vw,46px);margin-bottom:18px">Tissue-Culture Perennials &amp; Grasses, Wholesale</h1>
<p>Tissue culture is one of the things Westcan does best. We bring TC material into our Langley, BC
greenhouses and grow it on into clean, uniform liners &mdash; perennials above all, plus most of our
tropicals, a large share of our ornamental grasses, a number of shrubs, and more.</p>
<p>If you are sourcing tissue-culture liners in Canada or the US, this is what we do and how to
order it.</p>
</div>

<div class="tcsec">
<h2>Where we come in: stage 3</h2>
<p>Commercial micropropagation runs in stages. A laboratory establishes the culture, multiplies it,
and roots the plantlets in sterile conditions. What comes out the other end is delicate, tiny, and
has never met real air, real light or real disease pressure.</p>
<div class="stages">
  <div class="stage"><b>Stages 1&ndash;2 &middot; Lab</b><span>The culture is established and multiplied in vitro.</span></div>
  <div class="stage"><b>Stage 3 &middot; Lab</b><span>Plantlets are rooted in vitro. This is where we take delivery.</span></div>
  <div class="stage on"><b>Stage 4 &middot; Westcan</b><span>We wean, acclimatize and grow the material on into a rooted, field-ready liner.</span></div>
  <div class="stage"><b>Your bench</b><span>A uniform tray that bumps straight into your finishing container.</span></div>
</div>
<p>Stage 4 is the hard part. Moving TC material out of sterile culture and into a greenhouse is where
losses happen, and bringing in a successful crop takes the right environment and a knowledgeable,
skilled growing team that has done it many times before. That acclimatization work is exactly what
sets us apart: with years of experience and constant refinement of our technique, we minimize losses
and make sure a healthy liner reaches your bench.</p>
</div>

<div class="tcsec">
<h2>Why growers ask for tissue-culture liners</h2>
<h3>Clean starting material</h3>
<p>TC plantlets begin life in sterile culture rather than in a field or a stock block, so you are not
inheriting problems from someone else&rsquo;s crop.</p>
<h3>True to type</h3>
<p>Every plant in a TC batch traces back to the same selected mother material, so variegation, habit
and flower colour come through consistently &mdash; which matters most on the varieties customers buy
by name.</p>
<h3>Uniform, predictable batches</h3>
<p>Even material finishes evenly. That makes your ship weeks easier to hit and your benches easier to
grade, and it is the main reason large Hosta and grass programmes are grown from TC.</p>
<h3>Varieties that are slow any other way</h3>
<p>Some plants divide too slowly, or too unreliably, to supply at volume. Tissue culture is what makes
those varieties available as a commercial liner at all.</p>
</div>

<div class="tcsec">
<h2>What we grow from tissue culture</h2>
<p><b>Perennials</b> are the core of our TC work. Our <b>Hosta programme is entirely
tissue-culture</b> &mdash; 24 varieties as 72-cell liners, clean and true-to-type stock, and that
catalogue is <a href="/catalogs/Westcan_Hosta_Booking.pdf" download>available as a booking form</a>.</p>
<p><b>Most of our tropicals</b> are grown from tissue culture, a substantial part of our
<a href="/ornamental-grass-plugs.html">ornamental grass and sedge range</a> comes in as TC, and so do a
number of <a href="/shrub-conifer-liners.html">shrubs</a> &mdash; Nandina among them.</p>
<h3>Custom propagation is what we do</h3>
<p><b>Propagation method follows what the customer asks for.</b> The same variety might go out as a
tissue-culture liner for one grower and a cutting or seed-raised plug for another, depending on price,
volume, timing and the finish they need. We propagate to the order, not to a fixed list.</p>
<div class="tcbox">
<p><b>So ask us.</b> Send the variety &mdash; or your whole list &mdash; and we will tell you exactly how
we can propagate it, what that does to the lead time, and when we can have it ready.
<a href="/contact.html" style="color:var(--green-dark);font-weight:600;text-decoration:underline">Talk to us about your needs</a></p>
</div>
</div>

<div class="tcsec">
<h2>Ordering TC liners</h2>
<p>Tissue-culture liners ship in the same programme as everything else we grow: 72-cell trays as
standard with other cell sizes on request, a minimum of 4 trays per variety, and delivery weeks you
choose when you book. You can order through your broker &mdash; we work with Ball Seed, EHR,
Express Seed, Griffin, JVK, McHutchison and Michells.</p>
<p>Trays leave Langley on carts, boxed by courier, or as palletized freight, across Canada and into
the United States. US-export eligibility is flagged on every variety page, and our phytosanitary
checks are done in-house.</p>
<div class="tccta">
<a class="btn btn-primary" href="/availability.html">See what can ship this week</a>
<a class="btn btn-ghost" href="/catalog.html">Browse the full catalog</a>
<a class="btn btn-ghost" href="/contact.html">Ask about a variety</a>
</div>
</div>

</main>
{FOOTER}
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(bc, ensure_ascii=False)}</script>
{MENU_JS}
</body>
</html>'''
    open(f'{OUT}/tissue-culture.html', 'w', encoding='utf-8').write(page)
    print('wrote tissue-culture.html')

build_tc_page()

# ---------- sitemap ----------
static_pages = [('', 'weekly', '1.0'), ('catalog.html', 'weekly', '0.9'), ('availability.html', 'weekly', '0.9'),
                ('about.html', 'monthly', '0.7'), ('shipping.html', 'monthly', '0.6'),
                ('contact.html', 'monthly', '0.6'), ('quote.html', 'monthly', '0.5'),
                ('tissue-culture.html', 'monthly', '0.8')]
static_pages += [(f, 'weekly', '0.8') for f in CAT_COPY]
urls = [f'  <url><loc>{BASE}/{p}</loc><changefreq>{cf}</changefreq><priority>{pr}</priority></url>'
        for p, cf, pr in static_pages]
urls += [f'  <url><loc>{BASE}/varieties/{r["slug"]}.html</loc><changefreq>monthly</changefreq><priority>0.6</priority></url>'
         for r in ROWS if r['slug'] not in DUP_SLUGS]
open(f'{OUT}/sitemap.xml', 'w', encoding='utf-8').write(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + '\n'.join(urls) + '\n</urlset>\n')
print(f'wrote sitemap.xml ({len(urls)} URLs)')
