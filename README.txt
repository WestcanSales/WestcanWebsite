WESTCAN GREENHOUSES — STATIC SITE
=================================

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
  Westcan_Catalog_Master.json
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
