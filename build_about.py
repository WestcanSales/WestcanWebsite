#!/usr/bin/env python3
"""Rebuild about.html using the shared chrome from generate_variety_pages.py."""
import json, os, sys
sys.argv = ['build_about.py']
HERE = os.path.dirname(os.path.abspath(__file__)) or '.'
src = open(os.path.join(HERE, 'generate_variety_pages.py')).read()
pre = src.split('# ---------- variety pages ----------')[0].replace(
    "os.path.dirname(os.path.abspath(__file__))", repr(HERE))
ns = {}
exec(pre, ns)
head, header_nav, FOOTER, MENU_JS, esc = ns['head'], ns['header_nav'], ns['FOOTER'], ns['MENU_JS'], ns['esc']

ABOUT_CSS = '''
.story{display:grid;grid-template-columns:1.15fr 1fr;gap:44px;align-items:center;padding:36px 0}
@media(max-width:860px){.story{grid-template-columns:1fr}}
.story img{border-radius:14px;border:1px solid var(--line);width:100%;object-fit:cover}
.story p{margin-bottom:14px}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:16px;margin:26px 0 8px}
.stat{background:var(--white);border:1px solid var(--line);border-radius:12px;padding:20px 22px;text-align:center}
.stat b{font-family:var(--ff-display);font-size:30px;color:var(--green);display:block}
.stat span{font-family:var(--ff-data);font-size:12px;color:var(--muted);letter-spacing:.08em;text-transform:uppercase}
.band{background:var(--navy);color:#fff;border-radius:14px;padding:38px 36px;margin:44px 0}
.band h2{font-family:var(--ff-display);font-size:26px;margin-bottom:12px}
.band p{color:#C9D2EA;margin-bottom:8px}
.partners-list{display:flex;flex-wrap:wrap;gap:10px;margin-top:14px}
.partners-list span{background:rgba(255,255,255,.09);border:1px solid rgba(255,255,255,.16);border-radius:99px;padding:6px 16px;font-size:14px}
h2.sec{font-family:var(--ff-display);color:var(--navy);font-size:28px;margin:34px 0 14px}
.ctas{display:flex;gap:14px;flex-wrap:wrap;margin-top:26px}
main{padding-bottom:120px}
.growing{display:grid;grid-template-columns:1.15fr 1fr;gap:44px;align-items:start;margin-top:8px}
@media(max-width:860px){.growing{grid-template-columns:1fr}}
.growing img{border-radius:14px;border:1px solid var(--line);width:100%;aspect-ratio:3/4;object-fit:cover;max-height:520px}
.growing figcaption{font-family:var(--ff-data);font-size:12px;color:var(--muted);margin-top:8px}
'''
title = "Who We Are — Wholesale Propagators Since 1981 | Westcan Greenhouses"
desc = "Westcan Greenhouses — wholesale plug & liner propagators in Langley, BC since 1981. 1,100+ varieties, GCP certified, shipping to growers across Canada & the US."
canon = "https://westcangrhs.com/about.html"
ld = {"@context":"https://schema.org","@type":"AboutPage","name":title,"url":canon,
      "mainEntity":{"@id":"https://westcangrhs.com/#business"}}
partners = ["Terra Nova Nurseries","Ball Seed","Dümmen Orange","Selecta One","Darwin Perennials","Poulsen Roser A/S","PanAmerican Seed","Jelitto Perennial Seeds","Bull Plant Genetics"]

page = f'''{head(title, desc, canon, "https://westcangrhs.com/og-image.jpg", ABOUT_CSS)}
<body>
{header_nav()}
<div class="wrap crumbs"><a href="/">Home</a> › Who We Are</div>
<main class="wrap">
<div class="story">
<div>
<h1 style="font-size:clamp(30px,4vw,46px);margin-bottom:18px">Propagators since 1981.</h1>
<p>Westcan Greenhouses is a wholesale plug and liner propagator in Langley, British Columbia. For more than four decades we have done one thing: start plants well, so growers across Canada and the US can finish them profitably.</p>
<p>In addition to the thousands of annuals we offer, this site features more than 1,100 varieties — perennials, ornamental grasses and sedges, ferns, ground covers, shrubs, conifers, herbs and more — propagated in our Langley greenhouses and shipped as uniform, well-rooted trays: on carts, boxed, or as palletized freight.</p>
<p>We are GCP certified, which allows us to do phytosanitary checks in-house — so crossing the border is simple. No fees, no tariffs, no hassle; we do it every week. Availability is updated weekly from our production schedule, and our booking program lets customers lock in varieties and delivery weeks up to a season ahead — through their broker or direct.</p>
<div class="ctas">
<a class="btn btn-primary" href="/catalog.html">Browse the catalog</a>
<a class="btn btn-ghost" href="/contact.html">Talk to us</a>
</div>
</div>
<img src="/images/genetics-feature.jpg" alt="Westcan Greenhouses propagation — licensed breeder genetics" loading="lazy">
</div>
<div class="stats">
<div class="stat"><b>1981</b><span>Propagating since</span></div>
<div class="stat"><b>1,100+</b><span>Varieties on this site</span></div>
<div class="stat"><b>Weekly</b><span>Availability updates</span></div>
<div class="stat"><b>CA + US</b><span>Shipping coverage</span></div>
</div>
<div class="band">
<h2>Genetics from breeders you know</h2>
<p>We grow licensed varieties from leading breeders and seed houses, propagated under their specifications in our Langley facility:</p>
<div class="partners-list">{''.join(f'<span>{esc(p)}</span>' for p in partners)}</div>
</div>
<h2 class="sec">How we work with growers</h2>
<p>Most of our product moves two ways. The <strong>booking program</strong> reserves trays for future delivery weeks — the right fit for planned production, contract grows and spring programs. The <strong>weekly availability list</strong> is for product that's ready now; it's refreshed every Monday and can ship the same week. Either way, quotes flow through your broker or direct to us, and <a href="/shipping.html" style="text-decoration:underline">freight is estimated instantly</a> for boxed FedEx and pallet shipments across Canada and the US.</p>
<h2 class="sec">Come see what we're growing</h2>
<div class="growing">
<div>
<p>Start with the <a href="/catalog.html" style="text-decoration:underline">full catalog</a>, browse by range — <a href="/perennial-liners.html" style="text-decoration:underline">perennials</a>, <a href="/ornamental-grass-plugs.html" style="text-decoration:underline">grasses &amp; sedges</a>, <a href="/fern-liners.html" style="text-decoration:underline">ferns</a>, <a href="/ground-cover-plugs.html" style="text-decoration:underline">ground covers</a>, <a href="/shrub-conifer-liners.html" style="text-decoration:underline">shrubs &amp; conifers</a> — or jump straight to <a href="/availability.html" style="text-decoration:underline">what ships this week</a>.</p>
<p>Questions? <a href="/contact.html" style="text-decoration:underline">Ask us anything</a> — or call +1&nbsp;604-530-9298.</p>
</div>
<figure>
<img src="/images/about-iceplants.jpg" alt="Delosperma ice plant ground covers in full bloom at Westcan Greenhouses" loading="lazy">
<figcaption>Delosperma ground covers in bloom at the nursery.</figcaption>
</figure>
</div>
</main>
{FOOTER}
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
{MENU_JS}
</body>
</html>'''
open(os.path.join(HERE, 'about.html'), 'w', encoding='utf-8').write(page)
print('wrote about.html', len(page), 'bytes')
