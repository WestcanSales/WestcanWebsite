VARIETY PHOTO SLIDESHOW + AUTO-DETECT (Jul 21 2026):
- variety.html photos are now an auto-advancing SLIDESHOW (prev/next arrows, dot
  indicators, swipe on mobile, 4.5s autoplay that pauses on hover). Single-photo
  varieties show just the image with no controls.
- AUTO-DETECT by naming convention: the page probes images/{slug}-1.jpg, -2.jpg,
  -3.jpg ... in order and stops at the first missing number (max 12). To add photos
  to ANY variety in the future, just drop numbered files into /images named after
  the slug — no variety-images.json editing needed. 21 existing varieties that
  already had -1/-2/-3 files (Acorus 'Ogon', Karl Foerster, Hakonechloa, Festuca
  'Elijah Blue', Hosta 'Francee', etc.) automatically became slideshows.
- variety-images.json is now only needed for (a) photo CREDIT lines (Terra Nova
  images require it) or (b) externally-hosted http image URLs; local numbered files
  and any external srcs are merged. Existing slug->file string entries are harmless.
- Fixes the old file:// test quirk too: photos now auto-probe even if the JSON
  fetch fails, so they resolve from local files directly.
- Verified over HTTP: multi-photo varieties show controls and advance; single-photo
  don't; no JS errors.

WEEK 30 AVAILABILITY + LAVENDER PHOTOS (Jul 21 2026):
- Rebuilt availability from WESTCAN_FORECAST_AVAILABILITY_2026WK30-2027.xlsx (Table 1).
  87 AVAILABLE NOW (40,078 plugs) + 1,245 soonest. Week label WK28 -> WK30 everywhere.
  Download link -> westcan-availability-wk30.xlsx (wk28 removed).
- Forecast hygiene handled in the build: several lavenders (Munstead, Hidcote Blue,
  Primavera, Silver Anouk, Grosso, Provence) appear as DUPLICATE rows in the forecast
  (one 0-qty, one real, with a "102 Cell"/"72 CELL" suffix); collapsed by name.
  Also a new "FINISHED GRASS" group with 4IN Miscanthus/Pennisetum -> mapped to
  "Grasses & Sedges" and the "4IN" suffix stripped from display names.
- Re-applied the Tier-1 name fixes to the feed (forecast still carries the old typos
  from GrowPoint). Residual typos in feed after rebuild: none.
- 4 lavender photos added (Matt's greenhouse shots), registered in variety-images.json:
    lavandula-angustifolia-munstead, lavandula-stoechas-primavera,
    lavandula-stoechas-silver-anouk, and the "Hidcote Blue" photo -> existing
    lavandula-angustifolia-hidcote (Matt confirmed Hidcote Blue == Hidcote).
  Silver Anouk was already a catalog entry (no new row needed).
- Top Picks set to the 3 in-stock lavenders: Munstead / Primavera / Silver Anouk
  (all verified in the WK30 now-list, all with photos). Homepage table refreshed.
- Verified over HTTP: all 4 variety pages load their photo (file:// fetch fails in
  testing but works in production); Top Pick card images load; no JS errors.

NAME / TYPO CLEANUP — TIER 1 (Jul 16 2026):
Audited all 1,168 catalog varieties for name errors. Applied 72 renames + 6 quote-style
normalisations to BOTH catalog.html ROWS and variety.html DB (and 1 in the availability
feed), keyed on slug so the two stores cannot drift apart.

  - 34 broken cultivar quotes fixed (missing open/close, doubled quote, backtick).
      e.g. "Salvia nemorosa 'Noche"  ->  "Salvia nemorosa 'Noche'"
           "Gaura lindheimeri Belleza White'" -> "... 'Belleza White'"
  - 16 stray/double spaces removed (also cleaned double spaces in `common`).
  - 27 botanical epithet misspellings corrected:
      Matteuccia strutipteris->struthiopteris; Veronica armstronguii->armstrongii;
      Veronica longigolia->longifolia; Hebe armtrongii->armstrongii;
      Iberis sempervivens->sempervirens (x4); Lavandula intermediata->x intermedia (x5);
      Gaura linderheimeri->lindheimeri (x2); Armeria pseudoarmeria->pseudarmeria (x2);
      Hedera Helix->helix (x2); Cortaderia sellona->selloana;
      Gaillardia grandiflorus->grandiflora; Geum hybrdia->hybrida;
      Ophiopogon planiscapens->planiscapus; Arctostaphylos uva ursi->uva-ursi (x2)
  - 6 cultivar spellings corrected against Terra Nova's own list:
      Heuchera 'Odsidian'->'Obsidian'; Agastache 'Kudos Siver Blue'->'Kudos Silver Blue';
      Agastache 'Princess Plume'->"Prince's Plume"; Polemonium 'Huricane Ridge'->'Hurricane Ridge';
      Bergenia 'VINTAGE Bouquete'->'Bouquet'; Monstera 'Thai Constalation'->'Thai Constellation'
      plus Arctostaphylos 'Massachussets'->'Massachusetts' (x2)
  - curly quotes normalised to straight apostrophes (6 rows).

SLUGS WERE NOT CHANGED — display name and slug are independent, so no variety-page links
broke and no Details links went dead. Slugs still carry the old spelling (e.g.
heuchera-hybrida-odsidian); that is cosmetic only and safe to leave.

LEFT ALONE (Tier 2 — needs Matt's decision), see Catalog_Name_Audit.md:
  - genus field problems: Kahori, Actaeasimplex, Buddleia vs Buddleja, Rhododendron(azalea)
  - 5 same-plant-twice pairs (incl. an exact duplicate Panicum virgatum 'Heavy Metal')
  - truncated names: "Geranium Rozanne (" and "Geranium Purple Glow ("
  - 10 rows using a common name as the cultivar
  - hybrid notation inconsistency (hybrida vs x hybrida)
  NOTE: fixing Gaillardia grandiflorus->grandiflora means the two 'Arizona Sun' rows are
  now spelled identically (they were already flagged as a Tier 2 duplicate).

UPSTREAM: the same typos appear in the forecast/availability spreadsheets, so they very
likely live in GrowPoint/GreenStock. The website is fixed; the item master is not.

HARDINESS ZONES ON VARIETY PAGES (Jul 13 2026):
- Root cause of "only some varieties show a zone": the site has TWO data stores.
  catalog.html ROWS already had zones for 1,166/1,168 varieties (the pills on the
  catalog page), but the variety detail pages read from a SEPARATE `const DB` whose
  `culture` field was null for all but ~9 varieties — so most detail pages showed
  no Hardiness row.
- Fix: ported the zone from catalog ROWS into each variety.html DB entry's culture
  object (culture:null -> {zone:"X-Y"}; existing culture blocks kept as-is).
  1,157 newly added + 9 already present = 1,166 detail pages now show Hardiness.
- The only 2 still blank are the Calendula 'Cheers' annuals (correctly blank - no
  meaningful perennial zone). No zones were re-fetched; existing catalog data reused.
- If any specific zone looks wrong, it lives in catalog.html ROWS (`z`) and now also
  in variety.html DB culture.zone for the same slug - fix both to keep them in sync.

WESTCAN GREENHOUSES — STATIC SITE
=================================

WEEK 28 AVAILABILITY (Jul 9 2026) — from the FORECAST file:
- Source: WESTCAN_FORECAST_AVAILABILITY_2026WK28-2027.xlsx (sheet "Table 1").
  This is the correct input for the website feed. Current week = the FIRST WK
  column (WK28) — which matches today's real ISO week.
- Rebuilt with scripts/build_feed.py logic (see westcan-website-availability-update
  skill): qty>0 in current week -> AVAILABLE NOW; else first WK column with qty>0
  -> SOONEST (with year when it lands in 2027); no qty anywhere -> not listed.
- 1,344 feed items: 105 AVAILABLE NOW (42,034 plugs) + 1,239 forward weeks.
  253 items' soonest week falls in 2027.
- NEW: availability_feed.json (full feed, keyed on WCAN code — ready for the
  GreenStock swap). availability.html carries the 105 available-now items.
- Download link -> westcan-availability-wk28.xlsx (generated from the feed).
- Homepage highlights table + Top Picks refreshed to real WK28 stock.
  All three original Top Picks (Brunnera 'Jack Frost', Dryopteris 'Autumn Fern',
  Lavandula 'Primavera') ARE in stock in WK28 and were restored.
- Slug hygiene (unchanged rule): slugs are validated against catalog.html's live
  ROWS array (1,168 rows) before being written; anything not found shows quick-add
  only, never a dead "Details" link. 76 of 105 now-items link to a variety page.
  (Westcan_Catalog_Master.json, the old 864-row master, was DELETED this build —
  it was stale and unused at runtime. catalog.html ROWS is the only catalog source.)

NOTE ON THE BROKER FILE: PLUG_AVAILABILITY_BROKER_29.xlsx (week of July 12) is
the broker-facing sheet for the FOLLOWING week and is NOT the website input.
The website feed comes from the WESTCAN_FORECAST_AVAILABILITY_* file.

UI CHANGES (Jul 9 2026):
- contact.html: "Send us a message" subtitle reworded.
- "Request a Booking" -> "Request a Quote" (catalog.html, variety.html).
- CTA ROUTING: header/mobile "Book or Request a Quote" and "Request a Quote"
  buttons jump to quote.html when the visitor already has items in their quote,
  otherwise catalog.html as before. Self-contained block before </body> on
  index/catalog/variety/availability/contact/shipping (reads window.name directly
  so it works on contact + shipping, which don't load the Cart object).
  quote.html intentionally excluded.

HOMEPAGE PHOTOS + BOOKING SECTION (Jul 9 2026):
- Category grid: all 10 tiles now carry real plug/liner photos
  (images/cat-*.jpg). One representative variety per category —
  swap any tile by replacing its file, same name, same 4:3 crop.
    perennials=Geranium 'Rozanne'   grasses=Calamagrostis 'Karl Foerster'
    ferns=Dryopteris 'Brilliance'   groundcovers=Arctostaphylos 'Massachusetts'
    shrubs=Nandina 'Firepower'      conifers=Cupressus 'Wilma'
    succulents=Echeveria 'Azul'     tropicals=Monstera 'Thai Constellation'
    herbs=Lavandula 'Primavera'     annuals=Coleus
- "Genetics from the world's best breeders" feature: the blank right
  panel now holds the trial-garden photo (images/genetics-feature.jpg);
  "Browse Full Catalog" button shrunk (.btn-sm) and left-aligned.
- Booking section (id still #specialty-catalogs): eyebrow renamed to
  "Booking Program Highlights", heading is now "Structured booking
  programs to draw inspiration from." A navy callout links the complete
  list: catalogs/Westcan_2027_Plant_List.pdf (Full 2027 Plant List).
  NOTE: footer nav still labels this link "Specialty Catalogs" (anchor
  unchanged, still works) — rename across all pages if desired.
- All new images are resized/compressed (~140-210KB) and lazy-loaded.



Seven pages, all nav/footer in sync (Shipping in nav; no Contract Growing;
no Terra Nova grower ribbon; single mobile menu on every page):

  index.html         home
  catalog.html       864 varieties, hardiness zones (Z pills), filters
  variety.html       variety detail template (variety.html?v=SLUG)
  availability.html  current availability + subscribe
  shipping.html      shipping estimator
  contact.html       contact
  quote.html         multi-item quote cart (Book vs Quote split)

CART: items added from variety.html carry av:'order' so quote.html files
them as "Quote / grown to order". Availability-now items should carry
av:'now' to show as "Book".

ASSETS YOU SUPPLY (not in this zip):
  westcan-reel.mp4, catalogs/*.pdf, logo_green.jpg,
Drop this folder's HTML on top of those.

ZONES: 810 varieties carry a USDA zone; ~54 left blank for manual review
(see manual_check_zones.txt from the catalog build). variety.html zones
were intentionally deferred.

DEPLOY: drag the whole folder to app.netlify.com/drop.

DESIGN PASS (Jul 2 2026), benchmarked vs Van Belle / Van Wingerden / PPL:
- Homepage availability table now shows REAL WK26 items (was sample data);
  labeled "FROM THIS WEEK'S LIST - WK 26 - 2026". Update alongside the
  weekly availability refresh.
- Hero video compressed 18MB -> 5.5MB (1280px, muted-ready, faststart).
- Open Graph + Twitter card tags on all 7 pages (link previews).
- Skip-to-content link + lazy-loaded below-fold images (perf/accessibility).

AVAILABILITY ENGINE (Jul 2 2026) — Ball Webtrack 2027 rules:
- catalog.html + variety.html now auto-compute each variety's SOONEST READY
  week from its genus rule + the live ISO week (BUFFER = 1 safety week).
  No weekly edit needed for these two pages — the "current week" updates
  itself from the calendar (currently WK27). Change BUFFER in the engine
  block if you want more/less safety margin.
- 123 Ball rules built in (genus lead times, grass/fern windows 5-25,
  Terra Nova blanket lead30, Heuchera/Hellebore/Rose/Erica special weeks,
  Brunnera/Nandina cycles).
- 54 genera (~92 varieties) have NO Ball rule — mostly woody shrubs &
  conifers (Thuja, Buddleja, Viburnum, etc.) plus Agapanthus/Anemone.
  These show "Contact for availability" per your instruction.
- availability.html (the weekly ready-now list) is still driven by the
  forecast .xlsx upload — that workflow is unchanged.

CATALOG + AVAILABILITY UX (Jul 2 2026):
- Catalog title is now "Our Catalog" (applies to 2026 + 2027).
- Catalog filters reworked: plant-type + toggles moved to a left sidebar;
  A-Z jump bar is horizontal directly under the search; legend below it.
  Sidebar collapses to a horizontal row on tablet/mobile.
- Current Availability page now has QUICK ADD: each row has a Trays input +
  "+ Add" button that drops the item straight into the quote cart (stamped
  av:'now' so it books as available stock). "Details" link opens the variety
  page. No more bouncing to the general catalog.
- All "Subscribe" buttons renamed to "Subscribe Now" (section heading kept).

QA PASS (Jul 2 2026):
- Homepage hero "Available this week" cards: WK label fixed (24->26); all
  3 cards now feature genuinely in-stock items whose links resolve
  (Echinacea Sunmagic Vintage Pearl White / Carex Evergold / Athyrium Red
  Beauty). NOTE: refresh these cards weekly along with the tables.
- Availability "Details" links: 20 slugs remapped to the 2027 catalog;
  30 items not in the 2027 catalog now show quick-add only (no dead link).
- "Download this week's list (.xlsx)" now downloads a real file:
  westcan-availability-wk26.xlsx (regenerate weekly with the feed).
- variety.html nav aligned with all other pages (Specialty Catalogs
  removed from its desktop nav + mobile menu).

VARIETY PHOTOS (Jul 2 2026):
- variety-images.json maps slug -> image (local file in /images or full URL).
- Drop photos from your breeder trade portals (Terra Nova licensed-grower
  media library, Ball WebTrack assets, Darwin/Selecta/PanAm trade
  libraries) into /images, add one line per variety to the json, redeploy.
- Unmapped varieties show the "Photography coming soon" placeholder;
  a broken/missing image safely falls back to the placeholder too.

HOSTA PROGRAM + TERRA NOVA PHOTOS (Jul 2026):
- Hosta broker booking PDF added: catalogs/Westcan_Hosta_Booking.pdf + card
  in Specialty Catalogs.
- variety-images.json now supports multi-photo entries with a credit line:
  {"srcs":[url1,url2], "credit":"Photo(s) courtesy of TERRA NOVA(R)..."}.
  Variety pages show the photo, a credit bar, and thumbnails to swap.
- TERRA NOVA image terms (from their Hi-Res tabs): photos may be used for
  promotional material related to TERRA NOVA products WITH the credit
  "Photo(s) courtesy of TERRA NOVA(R) Nurseries, Inc." Only use TN photos
  for TN-bred varieties. Demo wired: Echinacea 'Fringe Festival'.
- For production, prefer downloading each variety's 2 Hi-Res files into
  /images (via the Download links on its TN product page) over hotlinking.
