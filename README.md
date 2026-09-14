# A1 Lawn Care Pty Ltd — website

Static marketing site for **A1 Lawn Care Pty Ltd**, 1593 Logan Rd, Mount Gravatt QLD 4122.

Built against the *A1 Lawn Care — SEO Website Strategy* research document
(Local Service Pro, 10 September 2026). Every meta title, meta description, H1
and target keyword is deployed exactly as that document specifies — none of it
was re-derived.

---

## Pages

| Path | H1 | Target keyword |
|---|---|---|
| `/` | Professional Lawn Mowing Services in Brisbane & Surrounding Suburbs | lawn mowing services brisbane |
| `/services/` | Lawn & Garden Services in Brisbane | — (hub) |
| `/services/lawn-mowing/` | Lawn Mowing Mount Gravatt — Domestic, Acreage & Commercial | lawn mowing mount gravatt |
| `/services/ndis-lawn-mowing/` | NDIS Registered Lawn Mowing & Yard Maintenance in Brisbane | ndis mowing |
| `/services/garden-maintenance/` | Garden Maintenance Brisbane — Pruning, Weeding & Edging | garden maintenance brisbane |
| `/services/palm-tree-removal/` | Palm Tree Removal Brisbane — Fast, Insured, Fully Cleaned Up | palm tree removal brisbane |
| `/services/green-waste-removal/` | Green Waste Removal Brisbane — Yard & Site Clean-Ups | green waste removal brisbane |
| `/services/hedge-trimming-lawn-treatments/` | Hedge Trimming & Lawn Treatments — Brisbane Southside | hedge trimming services brisbane |
| `/about/` | About A1 Lawn Care | — |
| `/contact/` | Get a Free Lawn Care Quote in Brisbane | — |
| `/thank-you/` | Thank you! | `noindex` — form destination |

No two pages target the same primary keyword, so none of them compete.

---

## Build

The site is plain static HTML — **you can upload it as-is, no build step
required.** `build.py` exists so the header, footer, forms, schema and the
152-suburb service-area block stay identical across all 11 pages.

```bash
python3 build.py        # regenerates every .html, sitemap.xml, robots.txt, _redirects
```

No dependencies beyond the Python 3 standard library.

Edit content in `build.py`, not in the generated HTML — a rebuild overwrites it.

```
build.py                     content + templates (the source of truth)
assets/css/site.css          design system and animations
assets/js/site.js            nav, scroll reveal, counters, FAQ, forms, quote modal
assets/img/                  photography (see below)
tools/fetch-drive-images.sh  pulls the client photos from Google Drive
index.html, services/…       generated output — committed, do not hand-edit
```

---

## Forms and conversion tracking

The LeadConnector tracking script is installed **once, globally**, in the
`<head>` of every page:

```html
<script src="https://link.msgsndr.com/js/external-tracking.js"
        data-tracking-id="tk_6582cb70c3d84289821c555a3d8691f9"></script>
```

It detects form submissions itself, so no endpoint is posted to.

Every quote form uses these `name` attributes, mapping 1:1 onto the CRM contact
record:

| Form label | `name` attribute | CRM field |
|---|---|---|
| Name | `full_name` | `{{contact.full_name}}` |
| Email | `email` | `{{contact.email}}` |
| Phone | `phone` | `{{contact.phone}}` |
| Property Address | `property_address` | `{{contact.property_address}}` |
| Property Size | `property_size` | `{{contact.property_size}}` |
| Service Needed | `service_needed` | `{{contact.service_needed}}` |
| Job Notes | `job_notes` | `{{contact.job_notes}}` |

Plus a honeypot field, `a1_hp`, hidden from people. If it is filled in, the
submission is dropped silently — **do not map it to a CRM field.**

> The honeypot was originally named `company_website` with a label to match.
> Chrome's organisation/URL autofill filled it in for real visitors, whose
> submissions were then silently dropped as bots — no animation, no redirect.
> Keep the name meaningless; anything that reads like a real field will hit the
> same problem.

**Submit flow.** On submit `site.js` stops the native POST, validates, and —
the tracking script's listener having already captured the fields — shows a
spinner and "Sending…", then a tick and "Sent", then navigates to
`/thank-you/` at about 950 ms.

Guards worth knowing about:

- A `busy` flag means repeated clicks fire once.
- The redirect is resolved with `new URL(target, location.href)`, so it
  survives a `<base>` tag or a deploy that is not at the domain root.
- If navigation has not happened after 4 seconds, the form resets itself and
  the status line offers a plain link to `/thank-you/` — a visitor never ends
  up looking at a dead button.

**Where the forms are.** Inline on the homepage, `/contact/` and all six
service pages. On top of that, every page *except* `/contact/` carries the same
form again inside a **quote modal** — the header "Free quote" button and the
mobile bottom bar open it rather than navigating away. On `/contact/` those two
controls are plain anchors to `#contact-quote`, since the form is already the
page. Every form redirects to `/thank-you/`.

The modal is `#quote-modal`, built by `quote_modal()` in `build.py`; any control
carrying `data-quote-open` opens it. It traps focus, closes on Escape, backdrop
click or the close button, locks body scroll, and restores focus to whatever
opened it.

Service pages pre-select the matching option in *Service Needed*.
`/contact/?service=Lawn+mowing` also pre-selects from the query string, which
is handy for ad landing URLs.

---

## Images

Photography comes from the client's shared Google Drive folder:
<https://drive.google.com/drive/folders/1T1C1f4PuEdVM7r1dQ7ACiwBtlWEUJccK>

```bash
bash tools/fetch-drive-images.sh      # originals  -> assets/img/_src/
python3 tools/optimize-images.py      # served set -> assets/img/
```

`assets/img/_src/` holds the untouched Drive originals and is the source of
truth. `tools/optimize-images.py` (needs `Pillow`) resizes and re-compresses
them into the responsive set the site actually serves —
`gallery-06-400.webp`, `gallery-06-600.webp` and so on. Re-running is lossless
because it always starts from `_src/`; never re-encode a WebP you already
re-encoded.

Widths live in one place, `PLAN` in the optimiser and `IMAGE_WIDTHS` in
`build.py` — change both together. `.github/workflows/fetch-drive-images.yml`
runs the pair and commits the result.

`gallery-01` … `gallery-08` are genuine A1 job photos and are assigned to the
service page each one actually illustrates — the overgrown-slope before/after
sits on green waste removal, the patchy-to-lush before/after sits on lawn
treatments, and so on. Alt text follows the pattern the research specifies
(`Lawn mowing Mount Gravatt - … - A1 Lawn Care`).

`about-a1-lawn-care.webp` and `gardener-at-work.webp` are stock, not A1's own
work, so they are used decoratively only (the homepage hero backdrop and the
about page) and their alt text does not claim otherwise. Captions in the "Our recent work"
gallery describe what is in frame and deliberately name no suburb — the source
files carry no location data.

> **Worth adding:** there is no genuine palm-removal photo in the folder. The
> tree & palm removal page currently uses a finished-backyard shot. A real
> before/after of a cocos palm coming out would be the single most valuable
> photo to add, given that page targets the highest-CPC keyword in the research
> ($12.42 a click).

---

## Hero images

The homepage hero uses a full-bleed photograph behind a readability scrim
(`.hero-photo`). The interior pages use a split hero instead — heading left,
photograph in a card on the right (`.page-hero--split`) — because the job photos
are 600x480 and a card keeps them near native size rather than upscaling them
across a full-width background. On narrow screens the card stacks under the
heading.

---

## Performance

PageSpeed mobile flagged two things on the first deploy, both now fixed:

**The tracking script was render-blocking** — 2,340 ms of the critical path, on
a 3.0 s First Contentful Paint. It now carries `defer`, plus a `preconnect`.
Deferred scripts still execute in document order, so it runs before `site.js`
and still registers its submit listener before `DOMContentLoaded`, which is all
the form capture depends on.

**Images were wildly oversized** — a 158 KiB, 1920px hero painted behind a
90%-opaque scrim on a 366px phone, and a 300x300 logo rendering at 46px.
Everything is now served through `srcset`/`sizes` at the width it actually
renders. The homepage hero additionally uses `<picture>` to pin phones to the
480px file, because below 940px the scrim makes resolution irrelevant.

Measured with Lighthouse 13.4.1, mobile, identical conditions, third party
stubbed at its real size and latency:

| | before | after |
|---|---|---|
| Performance | 92 | **99** |
| Accessibility | 90 | **100** |
| First Contentful Paint | 1.8 s | **1.2 s** |
| Largest Contentful Paint | 2.8 s | **2.2 s** |
| Speed Index | 4.4 s | **1.2 s** |
| Page weight | 377 KiB | **232 KiB** |

Local numbers run better than PageSpeed's because there is no real network in
between; the deltas are the meaningful part.

Accessibility went to 100 by fixing three genuine faults: the footer column
headings were rendering near-black on the near-black footer (they moved from
`h4` to `h3` for heading order and the old `h4`-only rule stopped applying),
the header phone link lost its accessible name when its label was hidden below
1020px, and the review star rows used `aria-label` on a bare `div`.

**Caching.** Every CSS, JS and image URL carries `?v=<content hash>`, so
`vercel.json` can serve `/assets/*` with a one-year immutable cache and a
changed file still busts it. If you host somewhere other than Vercel, port
those headers — without them repeat visits refetch everything.

---

## Confirm before launch

Everything below is either an estimate or a claim that needs Steve's sign-off.
Nothing here is fabricated to look like fact, but nothing here is verified
either.

| Item | Where | Status |
|---|---|---|
| **Review quotes** | homepage testimonials | **Placeholders**, labelled as such on the page. Replace with real Google reviews, delete the label in `build.py`, and only then add `AggregateRating` to the schema. |
| Geo coordinates `-27.5406, 153.0776` | `SITE` in `build.py`, LocalBusiness schema | Approximate for 1593 Logan Rd. Confirm against Google Business Profile. |
| Opening hours Mon–Fri 7–5, Sat 7–1 | `OPENING_HOURS`, footer, contact, schema | Assumed. Confirm actual hours. |
| Price ranges ($50–$90 mow, $250–$900 palm, $300–$800 clean-up) | FAQ answers | Estimates. The research strategy calls for answering price openly, but these need Steve's numbers. |
| "Public liability insured" | `/about/` | Confirm cover is current. |
| "Since 2019" | `/about/`, schema `foundingDate` | Research says "in business since at least 2019". Confirm the real date. |
| Service-area suburb list (152) | `SUBURBS` in `build.py` | Compiled to match the research's "150+ suburbs across Brisbane south, Bayside, Logan and Redlands". Trim anything A1 does not actually drive to. |

---

## Post-launch checklist

From the research document, the items that live outside this repository:

1. **Fix the dead Google Business Profile link.** The profile still points at
   `a1lawncarebrisbane.business.site`, which returns 404. Change it to
   `https://www.a1lawncare.net.au/`. Highest-impact single fix available.
2. Verify the property in Google Search Console and submit `/sitemap.xml`.
3. Install GA4 with conversion events on `tel:` clicks and form submits.
4. Baseline the 16 suburb keywords in rank tracking *before* this goes live.
5. Request indexing on each service page as it ships.
6. Keep NAP identical across the site, GBP and every directory listing.

Already handled in this build: one H1 per page, clean H1→H2→H3 order,
self-referencing canonicals, unique title and description within limits,
`en-AU`, pinch-zoom re-enabled, `LocalBusiness` + `Service` + `FAQPage` +
`BreadcrumbList` schema, the address in text on every page, a quote form on the
homepage, descriptive alt text, and all 152 suburbs as readable text.

### Answer / generative engines

`robots.txt` explicitly allows GPTBot, OAI-SearchBot, PerplexityBot, ClaudeBot
and Google-Extended. The research scored the old site 33/100 on agentic
browsing; the fixes for that are here — NDIS registration stated in readable
text rather than buried in a logo image, the address and service area written
out, and an `FAQPage` block on every page in direct-question / direct-answer
form.

---

## Deploying

Any static host works. The site is plain HTML with no server-side anything.

- **Netlify / Cloudflare Pages** — publish directory `/`. `_redirects` is
  already written for the legacy WordPress paths.
- **Apache** — `_redirects` will not be read; port those four rules to
  `.htaccess`.
- **Nginx** — same, port them to your server block.

Point `www.a1lawncare.net.au` at it, keep `https://www.a1lawncare.net.au/` as
the canonical host (that is what the canonical tags and schema use), and make
sure the non-`www` host 301s to `www`.
