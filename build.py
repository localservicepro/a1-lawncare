#!/usr/bin/env python3
"""
Static site generator for a1lawncare.net.au

Every page, meta title, meta description, H1 and target keyword below comes
from the "A1 Lawn Care — SEO Website Strategy" research document (Local Service
Pro, 10 September 2026). Nothing here is re-derived: the strings are deployed
exactly as specified.

    python3 build.py

writes the static site into the repository root. The generated HTML is
committed alongside this script, so the site can be uploaded to any host with
no build step required.
"""

import hashlib
import html
import os
import re
import shutil
import textwrap
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
TODAY = date.today().isoformat()

# ---------------------------------------------------------------------------
# Business details (NAP). Source: research document, section 01.
# ---------------------------------------------------------------------------
SITE = {
    "legal_name": "A1 Lawn Care Pty Ltd",
    "name": "A1 Lawn Care",
    "owner": "Steve Cope",
    "phone_display": "0456 198 080",
    "phone_href": "tel:+61456198080",
    "phone_e164": "+61456198080",
    "email": "info@a1lawncare.net.au",
    "street": "1593 Logan Rd",
    "suburb": "Mount Gravatt",
    "state": "QLD",
    "postcode": "4122",
    "country": "AU",
    # Approximate coordinates for 1593 Logan Rd, Mount Gravatt.
    # See README.md — confirm against Google Business Profile before launch.
    "lat": -27.5406,
    "lng": 153.0776,
    "origin": "https://www.a1lawncare.net.au",
    "founded": "2019",
    "abn_note": "NDIS registered provider",
    "facebook": "https://www.facebook.com/NDISmowing",
}
SITE["address_one_line"] = "{street}, {suburb} {state} {postcode}".format(**SITE)

OPENING_HOURS = [
    ("Mo,Tu,We,Th,Fr", "07:00", "17:00", "Monday – Friday", "7:00am – 5:00pm"),
    ("Sa", "07:00", "13:00", "Saturday", "7:00am – 1:00pm"),
]

# ---------------------------------------------------------------------------
# Service areas — research section 04: "listing every suburb as readable text,
# grouped by region". 150+ suburbs across the four regions A1 covers.
# ---------------------------------------------------------------------------
SUBURBS = {
    "Brisbane South": [
        "Mount Gravatt", "Mount Gravatt East", "Upper Mount Gravatt", "Wishart",
        "Mansfield", "Holland Park", "Holland Park West", "Tarragindi",
        "Greenslopes", "Coorparoo", "Camp Hill", "Carina", "Carina Heights",
        "Annerley", "Fairfield", "Yeronga", "Yeerongpilly", "Tennyson",
        "Moorooka", "Salisbury", "Rocklea", "Coopers Plains", "Robertson",
        "Sunnybank", "Sunnybank Hills", "Macgregor", "Eight Mile Plains",
        "Runcorn", "Kuraby", "Stretton", "Calamvale", "Algester", "Parkinson",
        "Drewvale", "Acacia Ridge", "Archerfield", "Willawong", "Larapinta",
        "Pallara", "Heathwood", "Doolandella", "Durack", "Inala", "Richlands",
        "Ellen Grove", "Forest Lake", "Oxley", "Darra", "Wacol", "Sherwood",
        "Corinda", "Graceville", "Chelmer", "Jindalee", "Mount Ommaney",
        "Sinnamon Park", "Seventeen Mile Rocks", "Sumner", "Riverhills",
        "Westlake", "Middle Park", "Jamboree Heights", "Nathan", "Dutton Park",
        "Highgate Hill", "Rochedale", "Mackenzie", "Burbank",
    ],
    "Bayside": [
        "Carindale", "Cannon Hill", "Tingalpa", "Wakerley", "Gumdale",
        "Chandler", "Belmont", "Ransome", "Murarrie", "Hemmant", "Lytton",
        "Wynnum", "Wynnum West", "Wynnum North", "Manly", "Manly West",
        "Lota", "Bulimba", "Hawthorne", "Balmoral", "Morningside",
        "Norman Park", "Seven Hills", "East Brisbane",
    ],
    "Logan": [
        "Springwood", "Slacks Creek", "Daisy Hill", "Shailer Park",
        "Tanah Merah", "Loganholme", "Cornubia", "Carbrook", "Underwood",
        "Rochedale South", "Priestdale", "Kingston", "Woodridge",
        "Logan Central", "Marsden", "Crestmead", "Berrinba", "Browns Plains",
        "Hillcrest", "Regents Park", "Heritage Park", "Boronia Heights",
        "Forestdale", "Greenbank", "Park Ridge", "Munruben", "Logan Reserve",
        "Waterford", "Waterford West", "Loganlea", "Meadowbrook", "Bethania",
        "Holmview", "Edens Landing", "Eagleby", "Beenleigh",
        "Mount Warren Park", "Windaroo", "Bannockburn", "Yarrabilba",
        "Jimboomba", "Cedar Vale", "Flagstone",
    ],
    "Redlands & surrounds": [
        "Capalaba", "Cleveland", "Alexandra Hills", "Birkdale", "Ormiston",
        "Thornlands", "Thorneside", "Victoria Point", "Wellington Point",
        "Redland Bay", "Sheldon", "Mount Cotton", "Coochiemudlo Island",
        "Macleay Island", "Russell Island", "Karragarra Island",
        "Lamb Island",
    ],
}
SUBURB_COUNT = len({s for group in SUBURBS.values() for s in group})

# ---------------------------------------------------------------------------
# Inline SVG icon set
# ---------------------------------------------------------------------------
ICONS = {
    "phone": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.2a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2Z"/>',
    "mail": '<path d="M4 4h16a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2Z"/><path d="m22 6-10 7L2 6"/>',
    "pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "check": '<path d="m20 6-11 11-5-5"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/><path d="m9 12 2 2 4-4"/>',
    "arrow": '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
    "chevron": '<path d="m6 9 6 6 6-6"/>',
    "up": '<path d="m18 15-6-6-6 6"/>',
    "mower": '<path d="M3 17h11a3 3 0 0 0 3-3V9"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="18" r="3"/><path d="M17 9h4V5h-4"/><path d="M3 17V9h7v5"/>',
    "leaf": '<path d="M11 20A7 7 0 0 1 4 13c0-6 7-10 16-10 0 9-4 16-10 16Z"/><path d="M4 20c3-4 6-6 10-8"/>',
    "hedge": '<path d="M4 20V9a4 4 0 0 1 8 0v11"/><path d="M12 20V11a4 4 0 0 1 8 0v9"/><path d="M2 20h20"/>',
    "palm": '<path d="M12 22V11"/><path d="M12 11c0-3-3-5-6-4 1-3 5-4 7-2 1-3 5-3 7 0-3-1-5 1-5 3"/><path d="M12 11c2-2 5-2 7 0"/>',
    "truck": '<path d="M3 16V6h11v10"/><path d="M14 9h4l3 3v4h-7"/><circle cx="7" cy="18" r="2"/><circle cx="17" cy="18" r="2"/>',
    "sprout": '<path d="M12 22V9"/><path d="M12 9C12 5 9 3 5 3c0 4 3 6 7 6Z"/><path d="M12 12c0-3 2-5 6-5 0 3-2 5-6 5Z"/>',
    "heart": '<path d="M20.8 5.6a5 5 0 0 0-7.1 0L12 7.3l-1.7-1.7a5 5 0 1 0-7.1 7.1L12 21.5l8.8-8.8a5 5 0 0 0 0-7.1Z"/>',
    "star": '<path d="m12 2 3.1 6.3 6.9 1-5 4.9 1.2 6.9-6.2-3.3-6.2 3.3L7 14.2l-5-4.9 6.9-1L12 2Z"/>',
    "calendar": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 11h18"/>',
    "camera": '<path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2Z"/><circle cx="12" cy="13" r="4"/>',
}


# ---------------------------------------------------------------------------
# Asset versioning. Every CSS/JS/image URL carries ?v=<content hash>, so the
# host can serve them with a one-year immutable cache (see vercel.json) and a
# changed file still busts the cache the moment its contents change.
# ---------------------------------------------------------------------------
_ASSET_HASHES = {}


def asset_url(path):
    """`/assets/css/site.css` -> `/assets/css/site.css?v=1a2b3c4d`."""
    if path not in _ASSET_HASHES:
        disk = os.path.join(ROOT, path.lstrip("/"))
        try:
            with open(disk, "rb") as fh:
                _ASSET_HASHES[path] = hashlib.sha1(fh.read()).hexdigest()[:8]
        except OSError:
            _ASSET_HASHES[path] = ""
    stamp = _ASSET_HASHES[path]
    return (path + "?v=" + stamp) if stamp else path


# ---------------------------------------------------------------------------
# Responsive images. Widths must match tools/optimize-images.py.
# ---------------------------------------------------------------------------
IMAGE_WIDTHS = {
    "gardener-at-work": [480, 960, 1440, 1920],
    "about-a1-lawn-care": [480, 900, 1400],
    "a1-lawn-care-logo": [112, 224],
    "ndis-registered-provider-logo": [180, 360],
}
for _n in range(1, 9):
    IMAGE_WIDTHS["gallery-0%d" % _n] = [400, 600]

# Intrinsic size of each source, so width/height on the tag match the real
# aspect ratio and the browser reserves the right box (CLS stays at 0).
IMAGE_RATIO = {
    "gardener-at-work": (1920, 907),
    "about-a1-lawn-care": (1700, 800),
    "a1-lawn-care-logo": (300, 300),
    "ndis-registered-provider-logo": (672, 155),
}
for _n in range(1, 9):
    IMAGE_RATIO["gallery-0%d" % _n] = (600, 480)


def img_tag(name, alt, sizes, css_class="", style="", priority=False,
            display_width=None, extra=""):
    """
    <img> with srcset across the generated widths.

    `sizes` tells the browser how wide the image renders so it can pick the
    smallest file that will do — without it srcset is close to useless.
    """
    widths = IMAGE_WIDTHS[name]
    iw, ih = IMAGE_RATIO[name]
    srcset = ", ".join(
        "%s %dw" % (asset_url("/assets/img/%s-%d.webp" % (name, w)), min(w, iw))
        for w in widths
    )
    fallback = asset_url("/assets/img/%s-%d.webp" % (name, widths[-1]))

    w = display_width or min(widths[-1], iw)
    h = round(ih * w / iw)

    return (
        '<img src="{fallback}" srcset="{srcset}" sizes="{sizes}"'
        ' width="{w}" height="{h}" alt="{alt}"{cls}{style} decoding="async"{load}{extra}>'
    ).format(
        fallback=fallback, srcset=srcset, sizes=sizes, w=w, h=h, alt=e(alt),
        cls=(' class="%s"' % css_class) if css_class else "",
        style=(' style="%s"' % style) if style else "",
        load=' fetchpriority="high"' if priority else ' loading="lazy"',
        extra=(" " + extra) if extra else "",
    )


def icon(name, cls=""):
    """Return a stroked inline SVG icon."""
    body = ICONS[name]
    filled = name == "star"
    attrs = (
        'viewBox="0 0 24 24" fill="currentColor" stroke="none"'
        if filled
        else 'viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"'
    )
    class_attr = ' class="%s"' % cls if cls else ""
    return '<svg %s aria-hidden="true"%s>%s</svg>' % (attrs, class_attr, body)


def e(text):
    """Escape for HTML text nodes / attributes."""
    return html.escape(text, quote=True)


# ---------------------------------------------------------------------------
# Service pages — research section 07. H1 / meta title / target keyword are
# deployed verbatim from the strategy table.
# ---------------------------------------------------------------------------
SERVICES = [
    {
        "slug": "lawn-mowing",
        "nav": "Lawn Mowing",
        "short": "Lawn Mowing",
        "h1": "Lawn Mowing Mount Gravatt — Domestic, Acreage & Commercial",
        "title": "Lawn Mowing Mount Gravatt | A1 Lawn Care Brisbane",
        "description": (
            "Lawn mowing in Mount Gravatt and across Brisbane’s southside. "
            "Domestic, acreage and commercial mowing, edged and cleaned up. "
            "Call 0456 198 080."
        ),
        "keyword": "lawn mowing mount gravatt",
        "audience": "Homeowners and body corporates in Mount Gravatt, Holland Park and Wishart",
        "icon": "mower",
        "image": "gallery-06.webp",
        "alt": "Lawn mowing Mount Gravatt - freshly mown backyard lawn and trimmed hedge line by A1 Lawn Care",
        "blurb": (
            "Regular or one-off mowing, edged, whipper-snipped and blown down. "
            "Domestic blocks, acreage and commercial grounds across the southside."
        ),
        "hero_lede": (
            "A1 Lawn Care is based at 1593 Logan Rd, Mount Gravatt. Lawn mowing in "
            "Mount Gravatt is the job we do most, and the suburbs around it — Holland "
            "Park, Wishart, Mansfield, Upper Mount Gravatt — are a few minutes from "
            "the door."
        ),
        "intro": [
            "Lawn mowing in Mount Gravatt sounds simple until you have tried to keep a "
            "south-east Queensland lawn under control through a wet summer. Couch and "
            "buffalo put on growth fast between November and March, and a fortnight of "
            "rain can turn a tidy yard into a paddock. A1 Lawn Care mows on a schedule "
            "that matches the season instead of a fixed calendar, so the lawn never gets "
            "away from you.",
            "Every mow is a complete job: cut at the right height for the grass type, "
            "edges cut along paths, driveways and garden beds, whipper-snipper around "
            "fence lines, trees and letterboxes, then the whole lot blown down so paths "
            "and driveways are left clean. Clippings go with us unless you want them "
            "left for mulch.",
        ],
        "sections": [
            {
                "h2": "Domestic lawn mowing across Brisbane’s southside",
                "body": [
                    "Most of our work is standard suburban blocks — a front and back lawn, "
                    "a strip of nature strip, and edges that need doing properly. We mow "
                    "weekly, fortnightly, monthly or as a one-off, and we are happy to lift "
                    "the frequency through the growing season and drop it back over winter.",
                    "If you are renting the property out or preparing it for sale, we can "
                    "invoice an agent directly and work to their inspection dates.",
                ],
                "ticks": [
                    "Weekly, fortnightly, monthly or one-off mowing",
                    "Edging along paths, driveways, beds and fence lines",
                    "Paths and driveways blown down before we leave",
                    "Clippings removed — or left as mulch if you prefer",
                    "Photos on request if you are not home",
                ],
            },
            {
                "h2": "Acreage mowing Brisbane — the bigger blocks",
                "body": [
                    "Acreage mowing in Brisbane is a different job to a suburban lawn. Ride-on "
                    "work on half-acre and larger blocks around Rochedale, Burbank, Greenbank, "
                    "Munruben and out towards Jimboomba needs the right machine and a bit of "
                    "planning around wet ground and slopes.",
                    "We quote acreage by the block rather than by the hour, so you know the "
                    "cost before we start, and we will tell you honestly if a paddock needs a "
                    "slasher pass before a mow will make any difference.",
                ],
            },
            {
                "h2": "Commercial mowing Brisbane — grounds, complexes and common areas",
                "body": [
                    "Commercial mowing in Brisbane covers body corporate common areas, small "
                    "business frontages, childcare centres, church grounds and rental "
                    "portfolios. These sites need to look presentable every week, not every "
                    "time somebody remembers to book.",
                    "We work to a fixed schedule, carry public liability insurance, and send "
                    "one consolidated invoice for multiple sites when that is easier for your "
                    "bookkeeping.",
                ],
            },
        ],
        "faqs": [
            (
                "How much does lawn mowing cost in Brisbane?",
                "Most standard suburban blocks on Brisbane’s southside sit between $50 and "
                "$90 per visit, depending on block size, how much edging is involved and "
                "whether clippings are taken away. Acreage and first-time catch-up mows are "
                "quoted individually. A1 Lawn Care quotes the price before any work starts, "
                "and it does not change on the day.",
            ),
            (
                "How often should I have my lawn mowed in Brisbane?",
                "Through the growing season — roughly October to April — most Brisbane "
                "lawns need mowing every one to two weeks. Over the cooler months growth "
                "slows and every three to four weeks is usually enough. We adjust the "
                "schedule with the season rather than charging for visits the lawn does not "
                "need.",
            ),
            (
                "Do you mow lawns in Mount Gravatt East and Upper Mount Gravatt?",
                "Yes. A1 Lawn Care is based on Logan Rd at Mount Gravatt, so Mount Gravatt "
                "East, Upper Mount Gravatt, Wishart, Mansfield, Holland Park and Tarragindi "
                "are all a short drive away and are serviced regularly.",
            ),
            (
                "Do you take the grass clippings away?",
                "Yes. Clippings and green waste go with us as part of the mow at no extra "
                "charge. If you would rather keep them for compost or mulch, just say so and "
                "we will leave them bagged or spread.",
            ),
        ],
    },
    {
        "slug": "ndis-lawn-mowing",
        "nav": "NDIS Yard & Garden",
        "short": "NDIS Yard & Garden Maintenance",
        "h1": "NDIS Registered Lawn Mowing & Yard Maintenance in Brisbane",
        "title": "NDIS Lawn Mowing Brisbane | A1 Lawn Care",
        "description": (
            "NDIS registered lawn mowing and yard maintenance in Brisbane. A1 Lawn "
            "Care works with participants, plan managers and support coordinators."
        ),
        "keyword": "ndis mowing",
        "audience": "NDIS participants, plan managers and support coordinators",
        "icon": "heart",
        "image": "gallery-07.webp",
        "alt": "NDIS yard maintenance Brisbane - side path and access kept clear by A1 Lawn Care",
        "blurb": (
            "A registered NDIS provider for lawn mowing and yard maintenance, working "
            "directly with participants, plan managers and support coordinators."
        ),
        "hero_lede": (
            "A1 Lawn Care is an NDIS registered provider. We mow lawns and maintain yards "
            "for participants right across Brisbane south, Bayside, Logan and the Redlands, "
            "and we invoice plan managers and the NDIA directly."
        ),
        "intro": [
            "NDIS mowing should be the easy part of a plan. In practice, finding a lawn "
            "contractor who is actually registered, who turns up on the same day each "
            "fortnight, and who knows how to invoice a plan manager correctly is harder "
            "than it should be.",
            "A1 Lawn Care is an NDIS registered provider based at Mount Gravatt. We have "
            "been doing NDIS lawn mowing in Brisbane for years — our Facebook page is "
            "literally facebook.com/NDISmowing — and we work with self-managed, plan-managed "
            "and NDIA-managed participants.",
        ],
        "sections": [
            {
                "h2": "NDIS lawn mowing Brisbane — what is covered",
                "body": [
                    "Yard maintenance usually sits under Core Supports, in Assistance with "
                    "Daily Life, where it is funded as a support that helps a participant "
                    "maintain their home safely. It is typically approved where a participant "
                    "cannot safely mow or maintain the yard themselves and there is no one in "
                    "the household who can.",
                    "Every plan is different and only the NDIA or your plan manager can "
                    "confirm what your funding covers. What we can do is give you a clear "
                    "written quote with the service, frequency and price set out, which is "
                    "usually what a plan manager or support coordinator needs to approve it.",
                ],
                "ticks": [
                    "Registered NDIS provider — not just ‘NDIS friendly’",
                    "Self-managed, plan-managed and NDIA-managed participants",
                    "Invoices sent directly to plan managers",
                    "Written quotes formatted for plan approval",
                    "Same crew each visit wherever possible",
                    "Reliable fortnightly or monthly schedule",
                ],
            },
            {
                "h2": "Working with support coordinators and plan managers",
                "body": [
                    "Support coordinators tell us the same thing repeatedly: the problem is "
                    "not finding someone to mow, it is finding someone who stays. We schedule "
                    "NDIS work the same way we schedule commercial contracts — a fixed run, "
                    "a set day, and a call if anything changes.",
                    "Send us the participant’s address and the frequency you need, and we "
                    "will send back a quote you can attach to a service agreement. If the "
                    "yard has been left a while, we will quote the initial clean-up separately "
                    "from the ongoing maintenance so the budget is easy to read.",
                ],
            },
            {
                "h2": "What we do on an NDIS yard maintenance visit",
                "body": [
                    "A standard NDIS yard maintenance visit covers mowing, edging, "
                    "whipper-snipping and blowing down. Where the plan allows, we also handle "
                    "garden bed weeding, hedge trimming, pruning back overgrowth from paths "
                    "and doorways, and removing the green waste.",
                    "Keeping paths and access clear matters more on these properties than "
                    "anywhere else, so overhanging branches and grass creeping across a path "
                    "get dealt with as part of the job rather than left for a separate visit.",
                ],
            },
        ],
        "faqs": [
            (
                "Is A1 Lawn Care an NDIS registered provider, and how do I book with my plan?",
                "Yes, A1 Lawn Care Pty Ltd is an NDIS registered provider. Call 0456 198 080 "
                "or send an enquiry with the property address and how often you need the "
                "yard done. We will send a written quote you can pass to your plan manager "
                "or support coordinator, and once it is approved we book you into a regular "
                "run. Self-managed, plan-managed and NDIA-managed participants are all "
                "welcome.",
            ),
            (
                "What is the NDIS lawn mowing rate in Brisbane?",
                "Yard maintenance is quoted per visit rather than at a fixed NDIS line-item "
                "hourly rate, because the work depends on block size and how overgrown the "
                "yard is. Most Brisbane southside properties fall between $50 and $90 a "
                "visit for mowing, edging and clean-up. You get the price in writing before "
                "anything is booked, so there are no surprises against the plan budget.",
            ),
            (
                "Do you invoice my plan manager directly?",
                "Yes. Send us your plan manager’s details when you book and we invoice them "
                "directly after each service, with the participant name, service date and "
                "description set out the way plan managers need it.",
            ),
            (
                "Which suburbs do you cover for NDIS yard maintenance?",
                "We cover more than 150 suburbs across Brisbane south, Bayside, Logan and "
                "the Redlands — including Mount Gravatt, Sunnybank, Carindale, Springwood, "
                "Browns Plains, Wynnum, Capalaba and Beenleigh. If you are unsure whether "
                "your suburb is in range, call and ask.",
            ),
        ],
    },
    {
        "slug": "garden-maintenance",
        "nav": "Garden Maintenance",
        "short": "Garden Maintenance",
        "h1": "Garden Maintenance Brisbane — Pruning, Weeding & Edging",
        "title": "Garden Maintenance Brisbane | A1 Lawn Care",
        "description": (
            "Garden maintenance in Brisbane - pruning, weeding, mulching and edging "
            "for homeowners, strata and rentals. A1 Lawn Care, Mount Gravatt."
        ),
        "keyword": "garden maintenance brisbane",
        "audience": "Homeowners, strata managers and rental property managers",
        "icon": "leaf",
        "image": "gallery-05.webp",
        "alt": "Garden maintenance Brisbane - mulched garden beds and edged lawn by A1 Lawn Care",
        "blurb": (
            "Pruning, weeding, mulching and bed edging that keeps a garden looking "
            "deliberate instead of merely cut back."
        ),
        "hero_lede": (
            "Garden maintenance services in Brisbane for homeowners, strata managers and "
            "rental property managers — the ongoing work that keeps beds sharp, plants "
            "healthy and weeds out."
        ),
        "intro": [
            "A mown lawn with overgrown beds still reads as a neglected yard. Garden "
            "maintenance in Brisbane is what makes the difference: clean bed edges, plants "
            "pruned to shape, weeds pulled before they seed, and mulch topped up so the "
            "soil holds moisture through summer.",
            "A1 Lawn Care does garden maintenance as a standalone service or alongside a "
            "regular mow. Most clients on the southside book a full garden tidy each season "
            "and keep the lawn on a fortnightly run in between.",
        ],
        "sections": [
            {
                "h2": "What a garden maintenance visit covers",
                "body": [
                    "The work is shaped around what the garden actually needs on the day. In "
                    "a wet January that usually means weeding and cutting back; in August it "
                    "is more likely pruning, mulching and preparing beds for spring.",
                ],
                "ticks": [
                    "Weeding garden beds by hand and spot-spraying regrowth",
                    "Pruning shrubs, natives and ornamentals to shape",
                    "Cutting clean edges between lawn and beds",
                    "Mulch supplied and spread to hold moisture and suppress weeds",
                    "Cutting back overgrowth from paths, windows and driveways",
                    "All green waste removed",
                ],
            },
            {
                "h2": "Strata, rentals and property managers",
                "body": [
                    "Rental property managers and body corporates have a different problem to "
                    "homeowners: the garden has to pass an inspection on a date, and the "
                    "invoice has to be clean enough to pass on. We work to inspection dates, "
                    "photograph the finished job on request, and invoice the agency directly.",
                    "For strata common areas we quote an annual schedule — so many visits a "
                    "year at a fixed price — rather than pricing each call-out separately.",
                ],
            },
            {
                "h2": "Low maintenance gardens for Brisbane blocks",
                "body": [
                    "If the garden has become more work than it is worth, we can reshape it "
                    "into something that survives a Brisbane summer without constant "
                    "attention: fewer thirsty ornamentals, more hardy natives, wider mulched "
                    "beds and simpler edges.",
                    "It is not a landscaping rebuild — it is pulling out what keeps failing "
                    "and replacing it with what actually grows here.",
                ],
            },
        ],
        "faqs": [
            (
                "What does garden maintenance include?",
                "A standard garden maintenance visit from A1 Lawn Care includes weeding beds, "
                "pruning shrubs and small trees to shape, cutting clean edges between lawn "
                "and garden beds, cutting back overgrowth from paths and windows, and "
                "removing all green waste. Mulching and spot weed spraying can be added.",
            ),
            (
                "How often does a Brisbane garden need maintenance?",
                "Most gardens on Brisbane’s southside need a proper tidy every six to eight "
                "weeks through the growing season and every three months over winter. "
                "Gardens with a lot of bed area or fast-growing hedges usually sit at the "
                "shorter end of that range.",
            ),
            (
                "Do you supply the mulch?",
                "Yes. We supply and spread mulch as part of a garden maintenance visit, "
                "charged at cost plus spreading. We will tell you how many cubic metres the "
                "beds need before you commit to it.",
            ),
            (
                "Can you maintain gardens at a rental property I don’t live at?",
                "Yes — a large share of our garden maintenance work is rentals and strata "
                "common areas. We can work to inspection dates, send photos when the job is "
                "done, and invoice the property manager or body corporate directly.",
            ),
        ],
    },
    {
        "slug": "palm-tree-removal",
        "nav": "Tree & Palm Removal",
        "short": "Tree & Palm Removal",
        "h1": "Palm Tree Removal Brisbane — Fast, Insured, Fully Cleaned Up",
        "title": "Palm Tree Removal Brisbane | A1 Lawn Care",
        "description": (
            "Palm tree removal in Brisbane - insured, fully cleaned up and the stump "
            "handled. Cocos, Alexander and Bangalow palms. Call 0456 198 080."
        ),
        "keyword": "palm tree removal brisbane",
        "audience": "Homeowners, acreage owners and commercial site managers",
        "icon": "palm",
        "image": "gallery-03.webp",
        "alt": "Tree and palm removal Brisbane - tidy backyard left clean by A1 Lawn Care",
        "blurb": (
            "Cocos, Alexander and Bangalow palms and small trees removed, cut down, "
            "chipped and carted away — with the site left clean."
        ),
        "hero_lede": (
            "Palm tree removal in Brisbane, done in a day and cleaned up properly. Insured, "
            "with the fronds, trunk and debris taken away rather than stacked on your "
            "nature strip."
        ),
        "intro": [
            "Cocos palms are the single most common removal we are called about on "
            "Brisbane’s southside. They drop fronds and fruit constantly, they block gutters, "
            "the seed is a problem for wildlife, and once they get above roof height the job "
            "stops being a weekend project.",
            "A1 Lawn Care removes palms and small trees across Brisbane south, Bayside, "
            "Logan and the Redlands. We are insured, we cut it down safely, and the fronds, "
            "trunk sections and debris leave with us.",
        ],
        "sections": [
            {
                "h2": "Palms we remove",
                "body": [
                    "Cocos (Queen) palms, Alexander palms, Bangalow palms, Golden Cane "
                    "clumps and Foxtail palms are all routine work. Clumping palms that have "
                    "spread into a thicket along a fence line are usually quicker and cheaper "
                    "to remove than people expect.",
                ],
                "ticks": [
                    "Cocos, Alexander, Bangalow, Foxtail and Golden Cane palms",
                    "Small trees and self-seeded volunteers",
                    "Fully insured — public liability cover on every job",
                    "Fronds, trunk and debris removed from site",
                    "Stump ground down or cut flush on request",
                    "Access-tight jobs between houses and over fences",
                ],
            },
            {
                "h2": "What palm tree removal costs in Brisbane",
                "body": [
                    "Price comes down to three things: height, access, and what happens to "
                    "the stump. A single mid-height cocos palm in an open backyard is a "
                    "straightforward job. The same palm hard against a fence, with a pool on "
                    "one side and powerlines on the other, is not.",
                    "We quote on site so the figure is real. If a palm is close enough to "
                    "powerlines that it needs an Energex-approved contractor, we will tell "
                    "you that rather than take the job on.",
                ],
            },
            {
                "h2": "Site clean-up is part of the job",
                "body": [
                    "A palm removal generates a surprising volume of green waste. Fronds go "
                    "through the chipper, trunk sections are cut down to manageable lengths "
                    "and loaded, and the ground is raked and blown down before we leave.",
                    "You should not be able to tell where the palm was, apart from the gap.",
                ],
            },
        ],
        "faqs": [
            (
                "How much does palm tree removal cost in Brisbane?",
                "Most single palm removals on Brisbane’s southside fall between $250 and "
                "$900, depending on the height of the palm, how tight the access is and "
                "whether the stump is ground out. Tall cocos palms with restricted access "
                "sit at the higher end. A1 Lawn Care quotes on site and the price includes "
                "removing all the debris.",
            ),
            (
                "Do I need council approval to remove a palm in Brisbane?",
                "Most palms on residential land in Brisbane can be removed without approval, "
                "but Brisbane City Council protects some vegetation, and some properties "
                "carry a vegetation protection order or a covenant on the title. Check with "
                "the council before booking if you are unsure — we will flag it if "
                "something looks like it may be protected.",
            ),
            (
                "Do you remove the stump as well?",
                "We can cut the stump flush to ground level as part of the removal, or grind "
                "it out so the area can be turfed or planted over. Stump grinding is quoted "
                "separately because it depends on the diameter and how close it sits to "
                "paths, pipes and fences.",
            ),
            (
                "Do you take away the fronds and trunk?",
                "Yes. Everything the removal generates goes with us — fronds, trunk sections "
                "and debris. The area is raked and blown down before we leave.",
            ),
        ],
    },
    {
        "slug": "green-waste-removal",
        "nav": "Green Waste & Clean-Ups",
        "short": "Green Waste & Site Clean-Ups",
        "h1": "Green Waste Removal Brisbane — Yard & Site Clean-Ups",
        "title": "Green Waste Removal Brisbane | A1 Lawn Care",
        "description": (
            "Green waste removal and yard clean-ups in Brisbane. Overgrown blocks, "
            "end-of-lease and site clean-ups cleared away. Call 0456 198 080."
        ),
        "keyword": "green waste removal brisbane",
        "audience": "Vendors preparing to sell, landlords, builders and tenants at end of lease",
        "icon": "truck",
        "image": "gallery-04.webp",
        "alt": "Green waste removal Brisbane - overgrown yard before and after an A1 Lawn Care clean-up",
        "blurb": (
            "Overgrown blocks, end-of-lease tidy-ups and site clean-ups cleared, loaded "
            "and taken away in one visit."
        ),
        "hero_lede": (
            "Green waste removal in Brisbane for yards that have got away from you — "
            "overgrown blocks, end-of-lease clean-ups, and builders’ sites that need to be "
            "clear before handover."
        ),
        "intro": [
            "There is a point where a yard stops being a mowing job. Grass to your knees, "
            "a pile of prunings that has been there since autumn, lantana along the back "
            "fence and a trailer-load of branches from the last storm — that is a clean-up, "
            "and it needs a truck.",
            "A1 Lawn Care clears and removes green waste across Brisbane south, Bayside, "
            "Logan and the Redlands. We cut it, load it and take it away in the same visit, "
            "and we leave the block in a state where normal fortnightly mowing can take over.",
        ],
        "sections": [
            {
                "h2": "Clean-ups we do most",
                "body": [
                    "The four jobs that come up again and again are pre-sale tidy-ups, "
                    "end-of-lease clean-ups, storm clean-ups, and blocks that have been "
                    "vacant for a few months.",
                ],
                "ticks": [
                    "Overgrown blocks slashed, mown and cleared",
                    "Pre-sale tidy-ups before photos and open homes",
                    "End-of-lease yard clean-ups for tenants and agents",
                    "Storm debris, fallen limbs and branch piles removed",
                    "Builders’ and renovation site green waste cleared",
                    "Lantana, camphor laurel and weed-tree thickets cut out",
                ],
            },
            {
                "h2": "Selling? Do the yard before the photos",
                "body": [
                    "Buyers make a decision about a property from the listing photos, and an "
                    "overgrown yard tells them there is deferred maintenance everywhere else "
                    "too. A clean-up before the photographer arrives is one of the cheapest "
                    "things you can do to a property before it goes to market.",
                    "We can turn a clean-up around quickly when there is a photography date "
                    "to hit — tell us the deadline when you call.",
                ],
            },
            {
                "h2": "End of lease, without the argument",
                "body": [
                    "Yard condition is one of the most common bond disputes in Queensland. "
                    "Getting the yard back to the state it was handed over in — mown, edged, "
                    "beds weeded, green waste gone — is usually cheaper than the deduction.",
                    "We can photograph the finished job so you have something to attach to "
                    "the exit condition report.",
                ],
            },
        ],
        "faqs": [
            (
                "Do you take away the green waste and clippings after a job?",
                "Yes. A1 Lawn Care removes all green waste as part of the job — clippings, "
                "prunings, fronds, branches and cleared undergrowth are loaded and taken "
                "away. You do not need a skip bin and nothing is left stacked on the nature "
                "strip.",
            ),
            (
                "How much does a yard clean-up cost in Brisbane?",
                "Clean-ups are quoted per job rather than per hour, because the variable is "
                "volume, not time. A standard overgrown suburban backyard usually lands "
                "between $300 and $800 including removal. We quote on site or from clear "
                "photos, and the price is fixed before we start.",
            ),
            (
                "Can you clear a block that hasn’t been touched in months?",
                "Yes. Long-neglected blocks are routine work — they get slashed first, then "
                "mown, then edged and cleared. Once it is back under control, a normal "
                "fortnightly or monthly mow keeps it that way for a fraction of the price.",
            ),
            (
                "Do you do builders’ site clean-ups?",
                "We handle the green waste side — vegetation, cleared undergrowth, stumps "
                "and branch piles on renovation and construction sites. General builders’ "
                "rubble and construction waste are not something we cart.",
            ),
        ],
    },
    {
        "slug": "hedge-trimming-lawn-treatments",
        "nav": "Hedging & Lawn Treatments",
        "short": "Hedging & Lawn Treatments",
        "h1": "Hedge Trimming & Lawn Treatments — Brisbane Southside",
        "title": "Hedge Trimming Services Brisbane | A1 Lawn Care",
        "description": (
            "Hedge trimming services in Brisbane southside, plus lawn coring, top "
            "dressing and weed control. A1 Lawn Care, Mount Gravatt."
        ),
        "keyword": "hedge trimming services brisbane",
        "audience": "Homeowners wanting coring, top dressing, weed control and hedging",
        "icon": "hedge",
        "image": "gallery-01.webp",
        "alt": "Lawn treatments Brisbane - patchy lawn before and after coring and top dressing by A1 Lawn Care",
        "blurb": (
            "Hedges cut straight and squared off, plus the lawn treatments that fix a "
            "tired lawn: coring, top dressing and weed control."
        ),
        "hero_lede": (
            "Hedge trimming services across the Brisbane southside, together with the lawn "
            "treatments that actually repair a struggling lawn — coring, top dressing and "
            "weed control."
        ),
        "intro": [
            "Two jobs sit on this page because the same visit usually covers both. Hedges "
            "on the southside grow fast — murraya, photinia, viburnum and lilly pilly will "
            "put on half a metre in a wet summer — and the lawn underneath them is often "
            "the part of the yard doing worst.",
            "Hedge trimming in Brisbane southside is precision work. A hedge cut by eye "
            "with a line trimmer never looks right again. We cut to a line, taper the face "
            "slightly so light reaches the bottom, and take the clippings with us.",
        ],
        "sections": [
            {
                "h2": "Hedge trimming Brisbane southside",
                "body": [
                    "We trim formal hedges, screening hedges and overgrown boundary hedges "
                    "that have not been touched in years. Height reductions on an established "
                    "hedge are staged over two visits where cutting it back hard in one go "
                    "would kill the plant.",
                ],
                "ticks": [
                    "Murraya, photinia, viburnum, lilly pilly and box hedges",
                    "Formal hedges cut to a line, faces tapered for light",
                    "Screening hedges reduced and reshaped",
                    "Overgrown boundary hedges brought back over staged visits",
                    "Clippings removed — nothing left in the beds",
                ],
            },
            {
                "h2": "Lawn coring and top dressing",
                "body": [
                    "Brisbane’s clay soils compact hard, especially on new estates where "
                    "topsoil is thin over builder’s fill. A compacted lawn sheds water instead "
                    "of absorbing it, roots stay shallow, and the lawn browns off at the first "
                    "hot week.",
                    "Coring pulls plugs out of the soil so water, air and fertiliser reach the "
                    "root zone. Top dressing on top of that levels out hollows and gives the "
                    "runners something to grow into. Done together, in the right season, it "
                    "is the single most effective thing you can do for a tired couch or "
                    "buffalo lawn.",
                ],
            },
            {
                "h2": "Weed control Brisbane",
                "body": [
                    "Bindii, nutgrass, clover, mullumbimby couch and winter grass each need a "
                    "different approach and a different timing. Bindii in particular has to be "
                    "treated in late autumn or early winter, well before the prickle forms — "
                    "by the time you feel it underfoot in spring, the season for treating it "
                    "has passed.",
                    "We identify what is actually in the lawn before spraying anything, and "
                    "we will tell you when a weed problem is really a soil or mowing-height "
                    "problem wearing a disguise.",
                ],
            },
        ],
        "faqs": [
            (
                "When is the best time to top dress a lawn in Brisbane?",
                "Late spring through early summer — roughly October to January — is the best "
                "time to top dress a lawn in Brisbane. The grass is actively growing and warm, "
                "wet conditions let it grow through the sand mix quickly. Top dressing in "
                "winter, while couch and buffalo are dormant, smothers the lawn instead of "
                "levelling it.",
            ),
            (
                "How often should a lawn be cored?",
                "Once a year is enough for most Brisbane lawns, and it is best done in the "
                "warm months just before top dressing. Lawns on heavy clay, in high-traffic "
                "yards or over builder’s fill benefit from coring every year without fail; "
                "sandier, healthier lawns can stretch to every second year.",
            ),
            (
                "How often do hedges need trimming?",
                "Fast-growing screening hedges such as murraya and lilly pilly need trimming "
                "two to three times a year on the Brisbane southside. Formal, tightly clipped "
                "hedges look best on three to four cuts a year. Slower box and native hedges "
                "are usually fine with one or two.",
            ),
            (
                "Can you get rid of bindii in my lawn?",
                "Yes. Bindii is treated with a selective herbicide in late autumn or early "
                "winter, before the seed head hardens into the prickle. One correctly timed "
                "treatment normally clears it; a lawn with a long-running bindii problem may "
                "need it two seasons in a row to exhaust the seed bank.",
            ),
        ],
    },
]

SERVICE_BY_SLUG = {s["slug"]: s for s in SERVICES}


# ---------------------------------------------------------------------------
# Global copy blocks
# ---------------------------------------------------------------------------
SERVICE_OPTIONS = [
    "Lawn mowing",
    "NDIS yard & garden maintenance",
    "Garden maintenance",
    "Tree & palm removal",
    "Green waste removal / yard clean-up",
    "Hedge trimming",
    "Lawn coring & top dressing",
    "Weed control",
    "Something else",
]

PROPERTY_SIZES = [
    "Small yard / courtyard",
    "Standard suburban block (up to 600m\u00b2)",
    "Large block (600\u20131000m\u00b2)",
    "Acreage (1000m\u00b2+)",
    "Commercial / body corporate",
    "Not sure",
]

# Research section 10 — "FAQ set to deploy", written as final copy.
HOME_FAQS = [
    (
        "How much does lawn mowing cost in Brisbane?",
        "Lawn mowing in Brisbane typically costs between $50 and $90 per visit for a "
        "standard suburban block. The price depends on block size, how much edging is "
        "involved, how long the grass has been left and whether clippings are taken "
        "away. A1 Lawn Care quotes every property before the first visit, and the price "
        "is fixed \u2014 it does not change on the day.",
    ),
    (
        "Is A1 Lawn Care an NDIS registered provider, and how do I book with my plan?",
        "Yes. A1 Lawn Care Pty Ltd is a registered NDIS provider for lawn mowing and "
        "yard maintenance. Call 0456 198 080 or send an enquiry with the property "
        "address and how often you need the yard done, and we will send a written quote "
        "you can pass to your plan manager or support coordinator. We work with "
        "self-managed, plan-managed and NDIA-managed participants, and we invoice plan "
        "managers directly.",
    ),
    (
        "Do you mow lawns in Sunnybank, Carindale and Springwood?",
        "Yes. A1 Lawn Care mows lawns in Sunnybank, Carindale and Springwood, along with "
        "more than 150 other suburbs across Brisbane south, Bayside, Logan and the "
        "Redlands. Our base is at 1593 Logan Rd, Mount Gravatt, so the whole southside "
        "is within easy reach.",
    ),
    (
        "How much does palm tree removal cost in Brisbane?",
        "Palm tree removal in Brisbane generally costs between $250 and $900 per palm. "
        "The three things that move the price are the height of the palm, how tight the "
        "access is, and whether the stump is ground out or cut flush. A1 Lawn Care quotes "
        "on site, and the quote includes removing every frond and trunk section from the "
        "property.",
    ),
    (
        "When is the best time to top dress a lawn in Brisbane?",
        "The best time to top dress a lawn in Brisbane is late spring to early summer \u2014 "
        "roughly October through January. The grass is growing hard and the warm, wet "
        "conditions let it push through the sand mix within a few weeks. Top dressing in "
        "winter, while couch and buffalo lawns are dormant, smothers the lawn instead of "
        "levelling it.",
    ),
    (
        "Do you take away the green waste and clippings after a job?",
        "Yes. Clippings, prunings, palm fronds and cleared undergrowth all go with us as "
        "part of the job, at no extra charge. You do not need a skip bin and nothing is "
        "left stacked on the nature strip. If you would rather keep the clippings for "
        "compost or mulch, tell us and we will leave them.",
    ),
]

# PLACEHOLDER REVIEWS — see README.md, "Confirm before launch".
# These are NOT real customer reviews. They are layout placeholders and are
# rendered with a visible "sample" label so nothing invented can be published
# by accident. Replace each one with a genuine Google review (text, first name,
# suburb), delete the label in build.py, and add AggregateRating to the
# LocalBusiness schema at that point — not before.
TESTIMONIALS = [
    (
        "Paste a real Google review here. Keep it to two or three sentences and "
        "leave the suburb in \u2014 a review that names Wishart or Carindale is worth "
        "more to local search than one that names nothing.",
        "First name + initial",
        "Suburb",
    ),
    (
        "Paste a second real review here. Reviews that mention a specific service "
        "\u2014 palm removal, a pre-sale clean-up, fortnightly mowing \u2014 reinforce the "
        "service pages they sit alongside.",
        "First name + initial",
        "Suburb",
    ),
    (
        "Paste a third real review here. If you have one from a support "
        "coordinator or plan manager, use it: it is the hardest kind of proof for "
        "a competitor to copy.",
        "First name + initial",
        "Suburb",
    ),
]


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------
# The tracking script was render-blocking: PageSpeed measured 2,340ms of the
# critical path waiting on it, which is most of a 3.0s First Contentful Paint.
# `defer` removes it from the critical path while keeping document order, so it
# still executes before site.js and still registers its submit listener before
# DOMContentLoaded — which is all the form capture depends on.
TRACKING = (
    '<link rel="preconnect" href="https://link.msgsndr.com" crossorigin>\n'
    '    <script\n'
    '      defer\n'
    '      src="https://link.msgsndr.com/js/external-tracking.js"\n'
    '      data-tracking-id="tk_6582cb70c3d84289821c555a3d8691f9"\n'
    '    ></script>'
)


def local_business_schema():
    """LocalBusiness JSON-LD with full NAP, geo, hours, areaServed, priceRange."""
    areas = [
        '{"@type":"City","name":"Brisbane","addressRegion":"QLD","addressCountry":"AU"}',
        '{"@type":"City","name":"Logan City","addressRegion":"QLD","addressCountry":"AU"}',
        '{"@type":"City","name":"Redland City","addressRegion":"QLD","addressCountry":"AU"}',
    ]
    for group in SUBURBS.values():
        for suburb in group:
            areas.append('{"@type":"Place","name":"%s, QLD"}' % suburb)

    hours = ",".join(
        '{"@type":"OpeningHoursSpecification","dayOfWeek":[%s],"opens":"%s","closes":"%s"}'
        % (",".join('"%s"' % d for d in _days(spec)), opens, closes)
        for spec, opens, closes, _, _ in OPENING_HOURS
    )

    offers = ",".join(
        '{"@type":"Offer","itemOffered":{"@type":"Service","name":"%s","url":"%s/services/%s/"}}'
        % (s["short"], SITE["origin"], s["slug"])
        for s in SERVICES
    )

    return (
        '{"@context":"https://schema.org","@type":"LandscapingBusiness",'
        '"@id":"%(origin)s/#business",'
        '"name":"%(legal_name)s","alternateName":"%(name)s",'
        '"url":"%(origin)s/","telephone":"%(phone_e164)s","email":"%(email)s",'
        '"image":"%(origin)s/assets/img/a1-lawn-care-logo-224.webp",'
        '"logo":"%(origin)s/assets/img/a1-lawn-care-logo-224.webp",'
        '"priceRange":"$$","currenciesAccepted":"AUD",'
        '"paymentAccepted":"Cash, Bank transfer, Credit card, NDIS plan managed",'
        '"foundingDate":"%(founded)s",'
        '"description":"NDIS registered lawn mowing, garden maintenance, hedging, '
        'palm removal and green waste removal across Brisbane south, Bayside, Logan '
        'and the Redlands. Based at %(address_one_line)s.",'
        '"address":{"@type":"PostalAddress","streetAddress":"%(street)s",'
        '"addressLocality":"%(suburb)s","addressRegion":"%(state)s",'
        '"postalCode":"%(postcode)s","addressCountry":"%(country)s"},'
        '"geo":{"@type":"GeoCoordinates","latitude":%(lat)s,"longitude":%(lng)s},'
        '"hasMap":"https://www.google.com/maps/search/?api=1&query=%(street_q)s",'
        '"sameAs":["%(facebook)s"],'
        '"openingHoursSpecification":[%(hours)s],'
        '"areaServed":[%(areas)s],'
        '"hasOfferCatalog":{"@type":"OfferCatalog","name":"Lawn and garden services",'
        '"itemListElement":[%(offers)s]},'
        '"founder":{"@type":"Person","name":"%(owner)s"},'
        '"knowsAbout":["Lawn mowing","NDIS yard maintenance","Garden maintenance",'
        '"Palm tree removal","Green waste removal","Hedge trimming","Lawn coring",'
        '"Lawn top dressing","Weed control"]}'
        % dict(
            SITE,
            hours=hours,
            areas=",".join(areas),
            offers=offers,
            street_q=(SITE["address_one_line"]).replace(" ", "+").replace(",", ""),
        )
    )


_DAY_MAP = {
    "Mo": "Monday", "Tu": "Tuesday", "We": "Wednesday", "Th": "Thursday",
    "Fr": "Friday", "Sa": "Saturday", "Su": "Sunday",
}


def _days(spec):
    return [_DAY_MAP[d] for d in spec.split(",")]


def faq_schema(faqs):
    items = ",".join(
        '{"@type":"Question","name":%s,"acceptedAnswer":{"@type":"Answer","text":%s}}'
        % (_json_str(q), _json_str(a))
        for q, a in faqs
    )
    return '{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[%s]}' % items


def breadcrumb_schema(trail):
    items = ",".join(
        '{"@type":"ListItem","position":%d,"name":%s,"item":"%s%s"}'
        % (i + 1, _json_str(name), SITE["origin"], path)
        for i, (name, path) in enumerate(trail)
    )
    return (
        '{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[%s]}'
        % items
    )


def _json_str(value):
    return (
        '"'
        + value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")
        + '"'
    )


def _og_variant(filename):
    """Map an og:image name onto the largest generated variant of it."""
    name = filename.replace(".webp", "")
    widths = IMAGE_WIDTHS.get(name)
    if not widths:
        return filename
    return "%s-%d.webp" % (name, widths[-1])


def head(page):
    """<head> block. One canonical, one title, one description per page."""
    robots = (
        '<meta name="robots" content="noindex, follow">'
        if page.get("noindex")
        else '<meta name="robots" content="index, follow, max-image-preview:large, '
        'max-snippet:-1, max-video-preview:-1">'
    )
    og_image = SITE["origin"] + "/assets/img/" + _og_variant(
        page.get("og_image", "a1-lawn-care-logo.webp")
    )
    schemas = "".join(
        '\n    <script type="application/ld+json">%s</script>' % s
        for s in page.get("schema", [])
    )
    return """<meta charset="utf-8">
    <!-- Pinch-zoom deliberately left enabled (research section 04) -->
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <link rel="canonical" href="{canonical}">
    {robots}
    <meta name="author" content="{legal_name}">
    <meta name="geo.region" content="AU-QLD">
    <meta name="geo.placename" content="{suburb}, Queensland">
    <meta name="geo.position" content="{lat};{lng}">
    <meta name="ICBM" content="{lat}, {lng}">

    <meta property="og:type" content="website">
    <meta property="og:locale" content="en_AU">
    <meta property="og:site_name" content="{legal_name}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:url" content="{canonical}">
    <meta property="og:image" content="{og_image}">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{description}">
    <meta name="twitter:image" content="{og_image}">

    <meta name="theme-color" content="#05301A">
    <link rel="icon" href="@@ASSET:/assets/img/a1-lawn-care-logo-224.webp@@" type="image/webp">
    <link rel="apple-touch-icon" href="@@ASSET:/assets/img/a1-lawn-care-logo-224.webp@@">

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="preload" as="style" href="{fonts}">
    <link rel="stylesheet" href="{fonts}" media="print" onload="this.media='all'">
    <noscript><link rel="stylesheet" href="{fonts}"></noscript>
    <link rel="stylesheet" href="@@ASSET:/assets/css/site.css@@">
    <script>document.documentElement.className += " js";</script>

    <!-- Conversion tracking: installed once, globally. Detects form submissions. -->
    {tracking}{schemas}""".format(
        title=e(page["title"]),
        description=e(page["description"]),
        canonical=SITE["origin"] + page["path"],
        robots=robots,
        og_image=og_image,
        tracking=TRACKING,
        schemas=schemas,
        fonts=(
            "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600"
            "&family=Outfit:wght@500;600;700;800&display=swap"
        ),
        **SITE
    )


def nav_link(label, href, current):
    aria = ' aria-current="page"' if href == current else ""
    return '<li><a href="%s"%s>%s</a></li>' % (href, aria, e(label))


def header(current):
    subs = "".join(
        '<li><a href="/services/%s/"%s>%s<span class="sub-desc">%s</span></a></li>'
        % (
            s["slug"],
            ' aria-current="page"' if "/services/%s/" % s["slug"] == current else "",
            e(s["short"]),
            e(s["keyword"]),
        )
        for s in SERVICES
    )
    services_open = current.startswith("/services/")
    # On /contact/ the quote form is the page, so the CTA jumps to it.
    # Everywhere else it opens the quote modal without leaving the page.
    quote_cta = (
        '<a class="btn" href="#contact-quote">Free quote</a>'
        if current == "/contact/"
        else '<button class="btn" type="button" data-quote-open>Free quote</button>'
    )
    return """<a class="skip-link" href="#main">Skip to content</a>

    <div class="topbar">
      <div class="container topbar-inner">
        <span>NDIS registered provider</span>
        <span class="dot" aria-hidden="true"></span>
        <span>{suburb} based &middot; 150+ suburbs serviced</span>
        <span class="dot" aria-hidden="true"></span>
        <span>Free quotes &mdash; <a href="{phone_href}">{phone_display}</a></span>
      </div>
    </div>

    <header class="site-header">
      <div class="container header-inner">
        <a class="brand" href="/">
          <img src="@@ASSET:/assets/img/a1-lawn-care-logo-112.webp@@"
               srcset="@@ASSET:/assets/img/a1-lawn-care-logo-112.webp@@ 112w,
                       @@ASSET:/assets/img/a1-lawn-care-logo-224.webp@@ 224w"
               sizes="52px" width="52" height="52" fetchpriority="high"
               alt="A1 Lawn Care Pty Ltd logo - lawn mowing Brisbane">
          <span class="brand-text">
            <span class="brand-name">A1 Lawn Care</span>
            <span class="brand-tag">Mount Gravatt &middot; Brisbane</span>
          </span>
        </a>

        <nav class="primary-nav" aria-label="Primary">
          <ul>
            {home}
            <li class="has-sub{open_cls}">
              <button type="button" aria-expanded="{expanded}">Services {chev}</button>
              <ul class="submenu">
                <li><a href="/services/">All services<span class="sub-desc">The full list</span></a></li>
                {subs}
              </ul>
            </li>
            {about}
            {contact}
          </ul>
        </nav>

        <div class="header-cta">
          <a class="header-phone" href="{phone_href}">{phone_icon}<span class="txt">{phone_display}</span></a>
          {quote_cta}
          <button class="nav-toggle" type="button" aria-label="Open menu" aria-expanded="false">
            <span></span>
          </button>
        </div>
      </div>
    </header>
    <div class="nav-scrim"></div>""".format(
        home=nav_link("Home", "/", current),
        about=nav_link("About", "/about/", current),
        contact=nav_link("Contact", "/contact/", current),
        subs=subs,
        open_cls=" is-open" if False else "",
        quote_cta=quote_cta,
        expanded="true" if services_open else "false",
        chev=icon("chevron"),
        phone_icon=icon("phone"),
        **SITE
    )


def footer(current=""):
    service_links = "".join(
        '<li><a href="/services/%s/">%s</a></li>' % (s["slug"], e(s["short"]))
        for s in SERVICES
    )
    hours_rows = "".join(
        "<div>%s<span><strong>%s</strong><br>%s</span></div>" % (icon("clock"), label, hours)
        if i == 0
        else "<div><span style=\"padding-left:1.7em\"><strong>%s</strong><br>%s</span></div>"
        % (label, hours)
        for i, (_, _, _, label, hours) in enumerate(OPENING_HOURS)
    )
    mobile_quote_cta = (
        '<a class="primary" href="#contact-quote">%sFree quote</a>' % icon("mail")
        if current == "/contact/"
        else '<button class="primary" type="button" data-quote-open>%sFree quote</button>'
        % icon("mail")
    )
    return """<footer class="site-footer">
      <div class="container">
        <div class="footer-main">
          <div>
            <a class="footer-brand" href="/">
              <img src="@@ASSET:/assets/img/a1-lawn-care-logo-112.webp@@"
                   srcset="@@ASSET:/assets/img/a1-lawn-care-logo-112.webp@@ 112w,
                           @@ASSET:/assets/img/a1-lawn-care-logo-224.webp@@ 224w"
                   sizes="54px" width="54" height="54" loading="lazy"
                   alt="A1 Lawn Care Pty Ltd logo">
              <span>A1 Lawn Care</span>
            </a>
            <p>NDIS registered lawn mowing and garden maintenance, based at Mount
               Gravatt and covering more than 150 suburbs across Brisbane south,
               Bayside, Logan and the Redlands.</p>
            <img class="footer-ndis" src="@@ASSET:/assets/img/ndis-registered-provider-logo-180.webp@@"
                 srcset="@@ASSET:/assets/img/ndis-registered-provider-logo-180.webp@@ 180w,
                         @@ASSET:/assets/img/ndis-registered-provider-logo-360.webp@@ 360w"
                 sizes="150px" width="150" height="35" loading="lazy"
                 alt="NDIS registered provider - A1 Lawn Care Brisbane">
          </div>

          <div>
            <h3>Services</h3>
            <ul>{service_links}</ul>
          </div>

          <div>
            <h3>Company</h3>
            <ul>
              <li><a href="/">Home</a></li>
              <li><a href="/about/">About A1 Lawn Care</a></li>
              <li><a href="/services/">All services</a></li>
              <li><a href="/#areas">Areas we service</a></li>
              <li><a href="/contact/">Contact &amp; free quote</a></li>
            </ul>
          </div>

          <div>
            <h3>Get in touch</h3>
            <div class="footer-nap">
              <div>{pin}<span><strong>{legal_name}</strong><br>{address_one_line}</span></div>
              <div>{phone}<a href="{phone_href}">{phone_display}</a></div>
              <div>{mail}<a href="mailto:{email}">{email}</a></div>
              {hours_rows}
            </div>
          </div>
        </div>

        <div class="footer-bottom">
          <span>&copy; {year} {legal_name}. All rights reserved.</span>
          <span>{address_one_line} &middot; ABN held by {legal_name}</span>
        </div>
      </div>
    </footer>

    <button class="to-top" type="button" aria-label="Back to top">{up}</button>

    <div class="mobile-bar">
      <a href="{phone_href}">{phone}Call now</a>
      {mobile_quote_cta}
    </div>

    <!-- defer: runs after the deferred tracking script in <head>, before DOMContentLoaded -->
    <script src="@@ASSET:/assets/js/site.js@@" defer></script>""".format(
        service_links=service_links,
        hours_rows=hours_rows,
        mobile_quote_cta=mobile_quote_cta,
        year=date.today().year,
        pin=icon("pin"),
        phone=icon("phone"),
        mail=icon("mail"),
        up=icon("up"),
        **SITE
    )


# ---------------------------------------------------------------------------
# Shared page sections
# ---------------------------------------------------------------------------
def quote_form(form_id, heading, sub, preselect=None, compact=False, heading_id=None):
    """
    Quote form. Field names map straight onto the CRM contact record:

        full_name        -> {{contact.full_name}}
        email            -> {{contact.email}}
        phone            -> {{contact.phone}}
        property_address -> {{contact.property_address}}
        property_size    -> {{contact.property_size}}
        service_needed   -> {{contact.service_needed}}
        job_notes        -> {{contact.job_notes}}

    Plus an `a1_hp` honeypot, which must NOT be mapped to a CRM field. The
    name matters: it was `company_website` with a label to match, and Chrome's
    organisation/URL autofill filled it in for real people, whose submissions
    were then silently dropped as bots. Anything that looks like a real field
    name will hit the same problem.

    The global LeadConnector external-tracking script captures the submit
    event; site.js then redirects to /thank-you/.
    """
    options = "".join(
        '<option value="%s"%s>%s</option>'
        % (e(opt), " selected" if opt == preselect else "", e(opt))
        for opt in SERVICE_OPTIONS
    )
    sizes = "".join('<option value="%s">%s</option>' % (e(s), e(s)) for s in PROPERTY_SIZES)
    notes_rows = "" if compact else ""

    return """<form class="js-quote-form" id="{form_id}" data-redirect="/thank-you/"
            action="/thank-you/" method="post" novalidate>
        <h2{heading_id_attr}>{heading}</h2>
        <p class="quote-sub">{sub}</p>

        <!-- Honeypot -->
        <div class="hp-field" aria-hidden="true">
          <label for="{form_id}-hp">Leave this field empty</label>
          <input type="text" id="{form_id}-hp" name="a1_hp" tabindex="-1"
                 autocomplete="off" aria-hidden="true">
        </div>

        <div class="field-row">
          <div class="field">
            <label for="{form_id}-name">Name <span class="req" aria-hidden="true">*</span></label>
            <input type="text" id="{form_id}-name" name="full_name" autocomplete="name"
                   placeholder="Your full name" required>
            <span class="err" role="alert"></span>
          </div>
          <div class="field">
            <label for="{form_id}-phone">Phone <span class="req" aria-hidden="true">*</span></label>
            <input type="tel" id="{form_id}-phone" name="phone" autocomplete="tel"
                   placeholder="04__ ___ ___" required>
            <span class="err" role="alert"></span>
          </div>
        </div>

        <div class="field">
          <label for="{form_id}-email">Email <span class="req" aria-hidden="true">*</span></label>
          <input type="email" id="{form_id}-email" name="email" autocomplete="email"
                 placeholder="you@example.com.au" required>
          <span class="err" role="alert"></span>
        </div>

        <div class="field">
          <label for="{form_id}-address">Property address <span class="req" aria-hidden="true">*</span></label>
          <input type="text" id="{form_id}-address" name="property_address"
                 autocomplete="street-address"
                 placeholder="Street, suburb — e.g. 12 Example St, Sunnybank" required>
          <span class="err" role="alert"></span>
        </div>

        <div class="field-row">
          <div class="field">
            <label for="{form_id}-size">Property size</label>
            <select id="{form_id}-size" name="property_size">
              <option value="">Select a size&hellip;</option>
              {sizes}
            </select>
          </div>
          <div class="field">
            <label for="{form_id}-service">Service needed <span class="req" aria-hidden="true">*</span></label>
            <select id="{form_id}-service" name="service_needed" required>
              <option value="">Select a service&hellip;</option>
              {options}
            </select>
            <span class="err" role="alert"></span>
          </div>
        </div>

        <div class="field">
          <label for="{form_id}-notes">Job notes</label>
          <textarea id="{form_id}-notes" name="job_notes"{notes_rows}
                    placeholder="Anything we should know — gate access, dogs, how long it has been, NDIS plan details&hellip;"></textarea>
        </div>

        <button class="btn btn--lg btn--block" type="submit">
          <span class="btn-spinner" aria-hidden="true"></span>
          <svg class="btn-tick" viewBox="0 0 24 24" fill="none" stroke="currentColor"
               stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"
               aria-hidden="true"><path d="m20 6-11 11-5-5"/></svg>
          <span class="btn-text">Get my free quote</span>
          <span class="btn-arrow">{arrow}</span>
        </button>
        <p class="form-status" role="status" aria-live="polite"></p>
        <p class="form-fineprint">No obligation. We usually reply the same day, and
           always within one business day.</p>
      </form>""".format(
        form_id=form_id,
        heading_id_attr=(' id="%s"' % heading_id) if heading_id else "",
        heading=e(heading),
        sub=e(sub),
        options=options,
        sizes=sizes,
        notes_rows=notes_rows,
        arrow=icon("arrow"),
    )


def faq_block(faqs, heading="Frequently asked questions", intro=None):
    items = "".join(
        """<details>
          <summary>{q}</summary>
          <div class="answer"><div><p>{a}</p></div></div>
        </details>"""
        .format(q=e(q), a=e(a))
        for q, a in faqs
    )
    intro_html = "<p>%s</p>" % e(intro) if intro else ""
    return """<section class="section section--sand" id="faq">
      <div class="container container--narrow">
        <div class="section-head section-head--center reveal">
          <span class="eyebrow">Answers</span>
          <h2>{heading}</h2>
          {intro}
        </div>
        <div class="faq reveal">{items}</div>
      </div>
    </section>""".format(heading=e(heading), intro=intro_html, items=items)


def areas_section(dark=False):
    groups = ""
    for region, suburbs in SUBURBS.items():
        lis = "".join("<li>%s</li>" % e(s) for s in suburbs)
        groups += """<div class="area-group reveal">
          <h3>{region} <span class="chip">{n} suburbs</span></h3>
          <ul class="suburb-list">{lis}</ul>
        </div>""".format(region=e(region), n=len(suburbs), lis=lis)

    return """<section class="section{dark}" id="areas">
      <div class="container">
        <div class="section-head reveal">
          <span class="eyebrow">Areas we service</span>
          <h2>Lawn mowing across {n}+ suburbs in Brisbane south, Bayside, Logan &amp; the Redlands</h2>
          <p>A1 Lawn Care is based at {address}. If your suburb is on this list,
             we already drive past it. If it is not, call {phone} and ask &mdash; we
             often can.</p>
        </div>
        {groups}
      </div>
    </section>""".format(
        dark=" section--dark" if dark else " section--sand",
        n=(SUBURB_COUNT // 10) * 10,
        address=e(SITE["address_one_line"]),
        phone=e(SITE["phone_display"]),
        groups=groups,
    )


def cta_band(heading, body, service=None):
    href = "/contact/" + ("?service=%s" % service.replace(" ", "+") if service else "")
    return """<section class="cta-band">
      <div class="container cta-inner">
        <div class="copy reveal">
          <h2>{heading}</h2>
          <p>{body}</p>
        </div>
        <div class="btn-row reveal">
          <a class="btn btn--light btn--lg" href="{href}">Get a free quote {arrow}</a>
          <a class="btn btn--outline-light btn--lg" href="{phone_href}">{phone_icon} {phone_display}</a>
        </div>
      </div>
    </section>""".format(
        heading=e(heading),
        body=e(body),
        href=href,
        arrow=icon("arrow"),
        phone_icon=icon("phone"),
        **SITE
    )


def services_grid(exclude=None, limit=None):
    cards = ""
    shown = [s for s in SERVICES if s["slug"] != exclude]
    if limit:
        shown = shown[:limit]
    for s in shown:
        cards += """<a class="card service-card" href="/services/{slug}/">
          <div class="media">{img}</div>
          <div class="body">
            <h3>{short}</h3>
            <p>{blurb}</p>
            <span class="more">Read more {arrow}</span>
          </div>
        </a>""".format(
            slug=s["slug"],
            img=img_tag(s["image"].replace(".webp", ""), s["alt"], "(max-width: 700px) calc(100vw - 44px), (max-width: 1100px) 45vw, 33vw"),
            short=e(s["short"]),
            blurb=e(s["blurb"]),
            arrow=icon("arrow"),
        )
    return '<div class="grid grid--3 reveal-stagger">%s</div>' % cards


def hero_photo(image, alt, priority=False):
    """
    Full-bleed hero photograph, layered behind a readability scrim
    (.hero-photo::after). Only used where a large source image exists.
    """
    name = image.replace(".webp", "")
    # Below 940px the scrim over this photo is 90% opaque, so resolution buys
    # nothing there — pin phones to the smallest file instead of letting srcset
    # pick a 2x-density one for an image nobody can really see.
    return """<div class="hero-photo">
          <picture>
            <source media="(max-width: 940px)" srcset="{small}">
            {img}
          </picture>
        </div>""".format(
        small=asset_url("/assets/img/%s-480.webp" % name),
        img=img_tag(name, alt, "100vw", priority=priority),
    )


def hero_media(image, alt, width=600, height=480):
    """
    Hero photograph as a card beside the heading. The job photos are 600x480,
    so a card keeps them at roughly native size instead of upscaling them
    across a full-bleed background.
    """
    return """<figure class="page-hero-media">
            {img}
          </figure>""".format(
        img=img_tag(
            image.replace(".webp", ""), alt,
            "(max-width: 940px) calc(100vw - 44px), 46vw",
            priority=True,
        ),
    )


def quote_modal():
    """
    Quote form in a dialog. Rendered on every page except /contact/, where the
    form is already the main content. Opened by any [data-quote-open] control.
    """
    return """<div class="modal" id="quote-modal" hidden>
      <div class="modal-backdrop" data-modal-close></div>
      <div class="modal-panel quote-card" role="dialog" aria-modal="true"
           aria-labelledby="quote-modal-title">
        <button class="modal-close" type="button" data-modal-close aria-label="Close quote form">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"
               stroke-linecap="round" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12"/></svg>
        </button>
        {form}
        <div class="ndis-note">{shield}
          <span><strong>NDIS participants welcome.</strong> We are a registered
          provider and invoice plan managers directly &mdash; just mention it in the
          job notes.</span>
        </div>
      </div>
    </div>""".format(
        form=quote_form(
            "modal-quote",
            "Get a free quote",
            "Tell us about the property and we will come back with a fixed price.",
            heading_id="quote-modal-title",
        ),
        shield=icon("shield"),
    )


def page(page_meta, body):
    return """<!DOCTYPE html>
<html lang="en-AU">
  <head>
    {head}
  </head>
  <body>
    {header}

    <main id="main">
{body}
    </main>

    {footer}
{modal}
  </body>
</html>
""".format(
        head=head(page_meta),
        header=header(page_meta["path"]),
        body=body,
        footer=footer(page_meta["path"]),
        modal="" if page_meta["path"] == "/contact/" else quote_modal(),
    )


# ---------------------------------------------------------------------------
# Homepage — research section 04, deployed exactly as specified.
# ---------------------------------------------------------------------------
def build_home():
    meta = {
        "path": "/",
        "title": "Lawn Mowing Services Brisbane | A1 Lawn Care Mt Gravatt",
        "description": (
            "Lawn mowing services in Brisbane by A1 Lawn Care - an NDIS registered "
            "provider covering Mount Gravatt, Sunnybank, Bayside & Logan. Get a free "
            "quote today."
        ),
        "og_image": "gallery-01.webp",
        "schema": [
            local_business_schema(),
            faq_schema(HOME_FAQS),
            '{"@context":"https://schema.org","@type":"WebSite","@id":"%s/#website",'
            '"url":"%s/","name":"%s","inLanguage":"en-AU",'
            '"publisher":{"@id":"%s/#business"}}'
            % (SITE["origin"], SITE["origin"], SITE["legal_name"], SITE["origin"]),
        ],
    }

    marquee_words = [
        "Lawn mowing", "NDIS yard maintenance", "Garden maintenance",
        "Palm tree removal", "Hedge trimming", "Green waste removal",
        "Lawn coring", "Top dressing", "Weed control", "Acreage mowing",
        "Commercial mowing", "Site clean-ups",
    ]
    marquee = "".join("<span>%s</span>" % e(w) for w in marquee_words)

    steps = [
        ("Tell us about the property",
         "Call 0456 198 080 or send the form. We need the address, roughly how big the "
         "block is and what you want done."),
        ("Get a fixed quote",
         "We quote on the property, not by the hour. You get the price in writing before "
         "anything is booked, and it does not change on the day."),
        ("We book you into the run",
         "Weekly, fortnightly, monthly or one-off. Regular clients get the same day each "
         "cycle so you know when to expect us."),
        ("Yard done, waste gone",
         "Mown, edged, whipper-snipped, blown down. Clippings and green waste leave with "
         "us unless you want them kept."),
    ]
    steps_html = "".join(
        '<div class="step reveal"><h3>%s</h3><p>%s</p></div>' % (e(t), e(b))
        for t, b in steps
    )

    why = [
        ("shield", "NDIS registered provider",
         "Not “NDIS friendly” — actually registered. We invoice plan managers "
         "directly and quote in a format support coordinators can approve."),
        ("pin", "Genuinely local to the southside",
         "Based at 1593 Logan Rd, Mount Gravatt. Sunnybank, Carindale, Springwood and "
         "Wynnum are a short drive, not a travel surcharge."),
        ("calendar", "Same day, every cycle",
         "Regular clients get a fixed day in the run. If something changes, you get a "
         "call rather than an empty driveway."),
        ("truck", "The waste leaves with us",
         "Clippings, prunings, palm fronds and cleared undergrowth are taken away as "
         "part of the job. No skip bin, nothing on the nature strip."),
        ("check", "Fixed quotes, not hourly guesses",
         "You get a price for the job in writing before we start. It does not move "
         "because the grass was longer than expected."),
        ("sprout", "Seven services, one contractor",
         "Mowing, gardens, hedging, palms, coring, top dressing and clean-ups — "
         "one number for the whole yard."),
    ]
    why_html = "".join(
        '<div class="card reveal"><div class="card-icon">%s</div><h3>%s</h3><p>%s</p></div>'
        % (icon(ic), e(t), e(b))
        for ic, t, b in why
    )

    quotes_html = "".join(
        """<div class="quote-item reveal">
          <div class="stars" role="img" aria-label="5 out of 5 stars">{stars}</div>
          <blockquote>&ldquo;{text}&rdquo;</blockquote>
          <cite>{who}</cite>
          <span class="where">{where}</span>
          <span class="where" style="display:block;margin-top:10px;color:#B06A00">
            Sample placeholder &mdash; replace with a real Google review before launch.
          </span>
        </div>""".format(
            stars=icon("star") * 5, text=e(text), who=e(who), where=e(where)
        )
        for text, who, where in TESTIMONIALS
    )

    # Genuine A1 job photos. Captions describe what is in frame — the source
    # files carry no location data, so no suburb is claimed for a single shot.
    gallery_imgs = [
        ("gallery-08.webp",
         "Edged lawn with rock border, mown by A1 Lawn Care Brisbane",
         "Edged lawn and rock border"),
        ("gallery-02.webp",
         "Front lawn and trimmed hedges on a Brisbane southside street frontage",
         "Front lawn and hedge line"),
        ("gallery-04.webp",
         "Overgrown yard before and after a green waste clean-up by A1 Lawn Care",
         "Overgrown slope \u2014 before and after"),
        ("gallery-01.webp",
         "Patchy lawn before and after coring and top dressing by A1 Lawn Care",
         "Lawn repair \u2014 before and after"),
        ("gallery-06.webp",
         "Backyard lawn mown and hedge trimmed by A1 Lawn Care Brisbane",
         "Backyard mow and hedge line"),
        ("gallery-05.webp",
         "Mulched garden beds and freshly edged lawn by A1 Lawn Care Brisbane",
         "Mulched beds and edged lawn"),
    ]
    gallery_html = "".join(
        """<figure class="reveal">
          {img}
          <figcaption>{cap}</figcaption>
        </figure>""".format(
            img=img_tag(
                fname.replace(".webp", ""), alt,
                "(max-width: 700px) calc(100vw - 44px), (max-width: 1100px) 45vw, 33vw",
            ),
            cap=e(cap),
        )
        for fname, alt, cap in gallery_imgs
    )

    body = """
      <!-- ============================ HERO ============================ -->
      <section class="hero hero--photo">
        {hero_photo}
        <div class="container hero-inner">
          <div>
            <div class="hero-badges reveal">
              <span class="pill pill--solid">{shield} NDIS registered provider</span>
              <span class="pill">{pin} Mount Gravatt based</span>
              <span class="pill">{check} Free, fixed quotes</span>
            </div>

            <h1 class="reveal">Professional Lawn Mowing Services in
              <span class="accent">Brisbane</span> &amp; Surrounding Suburbs</h1>

            <p class="hero-lede reveal">A1 Lawn Care provides lawn mowing services in
              Brisbane from our base at 1593 Logan Rd, Mount Gravatt &mdash; covering
              Sunnybank, Carindale, Springwood, Wynnum, Browns Plains and more than
              150 suburbs across Brisbane south, Bayside, Logan and the Redlands.
              We are a registered NDIS provider, we quote a fixed price before we
              start, and the green waste leaves with us.</p>

            <div class="btn-row reveal">
              <a class="btn btn--lg" href="#quote">Get my free quote {arrow}</a>
              <a class="btn btn--outline-light btn--lg" href="{phone_href}">{phone} {phone_display}</a>
            </div>

            <div class="hero-proof reveal">
              <div><span class="num" data-count-to="{n_suburbs}" data-count-suffix="+">0</span>
                   <span class="lbl">suburbs serviced</span></div>
              <div><span class="num" data-count-to="7">0</span>
                   <span class="lbl">services, one contractor</span></div>
              <div><span class="num">NDIS</span>
                   <span class="lbl">registered provider</span></div>
              <div><span class="num" data-count-to="6" data-count-suffix=" yrs+">0</span>
                   <span class="lbl">on Brisbane’s southside</span></div>
            </div>
          </div>

          <div class="quote-card reveal" id="quote">
            {form}
            <div class="ndis-note">{shield}
              <span><strong>NDIS participants welcome.</strong> We are a registered
              provider and invoice plan managers directly &mdash; just mention it in the
              job notes.</span>
            </div>
          </div>
        </div>
      </section>

      <div class="marquee" aria-hidden="true">
        <div class="marquee-track">{marquee}{marquee}</div>
      </div>

      <!-- ========================== SERVICES ========================== -->
      <section class="section" id="services">
        <div class="container">
          <div class="section-head section-head--center reveal">
            <span class="eyebrow">What we do</span>
            <h2>Six services, built around what a Brisbane yard actually needs</h2>
            <p>From a fortnightly mow to clearing a block that has not been touched in
               a year. Every job is quoted up front and cleaned up before we leave.</p>
          </div>
          {services}
          <div class="btn-row reveal" style="justify-content:center;margin-top:36px">
            <a class="btn btn--ghost" href="/services/">See all services {arrow}</a>
          </div>
        </div>
      </section>

      <!-- =========================== NDIS ============================= -->
      <section class="section section--dark">
        <div class="container">
          <div class="grid grid--2" style="align-items:center">
            <div class="reveal">
              <span class="eyebrow">The difference</span>
              <h2>A registered NDIS provider for lawn mowing and yard maintenance</h2>
              <p>Plenty of contractors will say they take NDIS work. Far fewer are
                 actually registered providers &mdash; and that is the part that matters
                 when a plan manager asks for the paperwork.</p>
              <p>A1 Lawn Care works with self-managed, plan-managed and NDIA-managed
                 participants across Brisbane south, Logan, Bayside and the Redlands.
                 We send written quotes formatted for plan approval, we invoice plan
                 managers directly, and we keep participants on a fixed run so the
                 same crew turns up on the same day.</p>
              <div class="btn-row" style="margin-top:1.6rem">
                <a class="btn" href="/services/ndis-lawn-mowing/">NDIS yard &amp; garden maintenance {arrow}</a>
              </div>
            </div>
            <div class="reveal">
              <ul class="ticks">
                <li>{check}<span><strong>Registered NDIS provider</strong> &mdash; not simply &ldquo;NDIS friendly&rdquo;</span></li>
                <li>{check}<span>Self-managed, plan-managed and NDIA-managed participants</span></li>
                <li>{check}<span>Invoices sent directly to plan managers</span></li>
                <li>{check}<span>Written quotes formatted for plan approval</span></li>
                <li>{check}<span>Paths, doorways and access kept clear as part of every visit</span></li>
                <li>{check}<span>Same crew, same day, every cycle wherever possible</span></li>
              </ul>
              <img src="@@ASSET:/assets/img/ndis-registered-provider-logo-180.webp@@"
                   srcset="@@ASSET:/assets/img/ndis-registered-provider-logo-180.webp@@ 180w,
                           @@ASSET:/assets/img/ndis-registered-provider-logo-360.webp@@ 360w"
                   sizes="180px" width="180" height="42" loading="lazy" style="margin-top:26px"
                   alt="NDIS registered provider logo - A1 Lawn Care Brisbane">
            </div>
          </div>
        </div>
      </section>

      <!-- ============================ WHY ============================= -->
      <section class="section">
        <div class="container">
          <div class="section-head section-head--center reveal">
            <span class="eyebrow">Why A1</span>
            <h2>What you actually get when you book us</h2>
            <p>Nothing here is remarkable. It is simply what a lawn contractor should do,
               done consistently.</p>
          </div>
          <div class="grid grid--3">{why}</div>
        </div>
      </section>

      <!-- =========================== PROCESS ========================== -->
      <section class="section section--sand">
        <div class="container">
          <div class="section-head reveal">
            <span class="eyebrow">How it works</span>
            <h2>From first call to a finished yard, in four steps</h2>
          </div>
          <div class="grid grid--2 steps">{steps}</div>
        </div>
      </section>

      <!-- =========================== GALLERY ========================== -->
      <section class="section">
        <div class="container">
          <div class="section-head section-head--center reveal">
            <span class="eyebrow">Our recent work</span>
            <h2>Jobs from around Brisbane’s southside</h2>
            <p>Real properties across Brisbane south, Bayside, Logan and the
               Redlands — photographed on the day.</p>
          </div>
          <div class="gallery">{gallery}</div>
        </div>
      </section>

      <!-- ======================== TESTIMONIALS ======================== -->
      <section class="section section--sand">
        <div class="container">
          <div class="section-head section-head--center reveal">
            <span class="eyebrow">What clients say</span>
            <h2>Homeowners, agents and support coordinators</h2>
            <p>Review slots are ready and waiting on real Google reviews \u2014
               see README.md.</p>
          </div>
          <div class="grid grid--3">{quotes}</div>
        </div>
      </section>

{areas}

{cta}

{faq}
""".format(
        hero_photo=hero_photo(
            "gardener-at-work.webp",
            "Established garden bed in a Brisbane southside yard maintained by "
            "A1 Lawn Care",
            priority=True,
        ),
        shield=icon("shield"),
        pin=icon("pin"),
        check=icon("check"),
        arrow=icon("arrow"),
        phone=icon("phone"),
        n_suburbs=SUBURB_COUNT,
        form=quote_form(
            "hero-quote",
            "Get a free quote",
            "Tell us about the property and we will come back with a fixed price.",
        ),
        marquee=marquee,
        services=services_grid(),
        why=why_html,
        steps=steps_html,
        gallery=gallery_html,
        quotes=quotes_html,
        areas=areas_section(dark=True),
        cta=cta_band(
            "Ready to get the yard off your list?",
            "Free quote, fixed price, green waste taken away. Call Steve on "
            "0456 198 080 or send the form and we will come back to you the same day.",
        ),
        faq=faq_block(
            HOME_FAQS,
            "Lawn mowing in Brisbane — your questions answered",
            "The questions we get asked most, answered straight.",
        ),
        **SITE
    )
    return meta, body


# ---------------------------------------------------------------------------
# Services hub
# ---------------------------------------------------------------------------
def build_services_hub():
    meta = {
        "path": "/services/",
        "title": "Lawn & Garden Services Brisbane | A1 Lawn Care Mt Gravatt",
        "description": (
            "Lawn and garden services across Brisbane southside - mowing, NDIS yard "
            "care, gardens, palm removal, green waste and hedging. Free quotes."
        ),
        "og_image": "gallery-02.webp",
        "schema": [
            local_business_schema(),
            breadcrumb_schema([("Home", "/"), ("Services", "/services/")]),
        ],
    }

    body = """
      <section class="page-hero page-hero--split">
        <div class="container page-hero-grid">
          <div class="page-hero-inner">
            <nav class="breadcrumb" aria-label="Breadcrumb">
              <ol><li><a href="/">Home</a></li><li aria-current="page">Services</li></ol>
            </nav>
            <h1>Lawn &amp; Garden Services in Brisbane</h1>
            <p>Six services covering everything a south-east Queensland yard throws at you
               &mdash; from a fortnightly mow in Mount Gravatt to clearing an overgrown
               block in Logan. All quoted up front, all cleaned up before we leave.</p>
            <div class="btn-row">
              <a class="btn btn--lg" href="/contact/">Get a free quote {arrow}</a>
              <a class="btn btn--outline-light btn--lg" href="{phone_href}">{phone} {phone_display}</a>
            </div>
          </div>
          {hero_photo}
        </div>
      </section>

      <section class="section">
        <div class="container">
          <div class="section-head section-head--center reveal">
            <span class="eyebrow">What we do</span>
            <h2>Six lawn and garden services for Brisbane’s southside</h2>
            <p>Each one has its own page, its own fixed-price quote and its own
               crew notes. Pick the job you need doing.</p>
          </div>
          {grid}
        </div>
      </section>

      <section class="section section--sand">
        <div class="container">
          <div class="section-head section-head--center reveal">
            <span class="eyebrow">Also covered</span>
            <h2>The smaller jobs that come with the bigger ones</h2>
          </div>
          <div class="grid grid--4 reveal-stagger">
            <div class="card"><div class="card-icon">{sprout}</div><h3>Lawn coring</h3>
              <p>Breaking up compacted Brisbane clay so water and fertiliser reach the roots.</p></div>
            <div class="card"><div class="card-icon">{leaf}</div><h3>Top dressing</h3>
              <p>Levelling hollows and giving couch and buffalo runners something to grow into.</p></div>
            <div class="card"><div class="card-icon">{shield}</div><h3>Weed control</h3>
              <p>Bindii, nutgrass, clover and winter grass, treated at the right time of year.</p></div>
            <div class="card"><div class="card-icon">{truck}</div><h3>Acreage &amp; commercial</h3>
              <p>Ride-on work on larger blocks, body corporate common areas and business frontages.</p></div>
          </div>
        </div>
      </section>

{areas}

{cta}
""".format(
        hero_photo=hero_media(
            "gallery-05.webp",
            "Mulched garden beds and freshly edged lawn by A1 Lawn Care Brisbane",
        ),
        arrow=icon("arrow"),
        phone=icon("phone"),
        grid=services_grid(),
        sprout=icon("sprout"),
        leaf=icon("leaf"),
        shield=icon("shield"),
        truck=icon("truck"),
        areas=areas_section(),
        cta=cta_band(
            "Not sure which service you need?",
            "Describe the yard and we will tell you. Call 0456 198 080 or send the "
            "form and we will come back with a fixed price.",
        ),
        **SITE
    )
    return meta, body


# ---------------------------------------------------------------------------
# Individual service pages
# ---------------------------------------------------------------------------
def build_service(service):
    path = "/services/%s/" % service["slug"]
    service_schema = (
        '{"@context":"https://schema.org","@type":"Service",'
        '"name":%s,"serviceType":%s,'
        '"url":"%s%s",'
        '"provider":{"@id":"%s/#business"},'
        '"areaServed":[%s],'
        '"description":%s,'
        '"audience":{"@type":"Audience","audienceType":%s},'
        '"offers":{"@type":"Offer","priceCurrency":"AUD","availability":'
        '"https://schema.org/InStock","url":"%s/contact/"}}'
        % (
            _json_str(service["short"]),
            _json_str(service["keyword"]),
            SITE["origin"],
            path,
            SITE["origin"],
            ",".join(
                '{"@type":"City","name":"%s","addressRegion":"QLD","addressCountry":"AU"}' % c
                for c in ("Brisbane", "Logan City", "Redland City")
            ),
            _json_str(service["blurb"]),
            _json_str(service["audience"]),
            SITE["origin"],
        )
    )

    meta = {
        "path": path,
        "title": service["title"],
        "description": service["description"],
        "og_image": service["image"],
        "schema": [
            local_business_schema(),
            service_schema,
            faq_schema(service["faqs"]),
            breadcrumb_schema(
                [("Home", "/"), ("Services", "/services/"), (service["short"], path)]
            ),
        ],
    }

    sections_html = ""
    for sec in service["sections"]:
        ticks = ""
        if sec.get("ticks"):
            ticks = '<ul class="ticks" style="margin-top:1.4rem">%s</ul>' % "".join(
                "<li>%s<span>%s</span></li>" % (icon("check"), e(t)) for t in sec["ticks"]
            )
        paras = "".join("<p>%s</p>" % e(p) for p in sec["body"])
        sections_html += '<h2>%s</h2>%s%s' % (e(sec["h2"]), paras, ticks)

    intro_html = "".join("<p>%s</p>" % e(p) for p in service["intro"])

    # Rotate the related pair so each service page cross-links a different two.
    _i = SERVICES.index(service)
    others = [SERVICES[(_i + n) % len(SERVICES)] for n in (1, 2)]
    related = "".join(
        '<li><a href="/services/%s/">%s</a></li>' % (s["slug"], e(s["short"]))
        for s in SERVICES
    )

    body = """
      <section class="page-hero page-hero--split">
        <div class="container page-hero-grid">
          <div class="page-hero-inner">
            <nav class="breadcrumb" aria-label="Breadcrumb">
              <ol>
                <li><a href="/">Home</a></li>
                <li><a href="/services/">Services</a></li>
                <li aria-current="page">{short}</li>
              </ol>
            </nav>
            <h1>{h1}</h1>
            <p>{lede}</p>
            <div class="btn-row">
              <a class="btn btn--lg" href="#quote">Get a free quote {arrow}</a>
              <a class="btn btn--outline-light btn--lg" href="{phone_href}">{phone} {phone_display}</a>
            </div>
          </div>
          {hero_photo}
        </div>
      </section>

      <section class="section">
        <div class="container with-aside">
          <div class="prose reveal">
            {intro}
            {sections}

            <div class="callout">
              <p><strong>Who this is for:</strong> {audience}.</p>
            </div>

            <h2>Book {short_lower} with A1 Lawn Care</h2>
            <p>Call Steve on <a href="{phone_href}">{phone_display}</a> or send the form
               and we will come back with a fixed price. We are based at
               {address_one_line} and cover more than 150 suburbs across Brisbane south,
               Bayside, Logan and the Redlands.</p>
          </div>

          <aside class="aside-sticky">
            <div class="aside-card quote-card" id="quote" style="padding:24px">
              {form}
            </div>
            <div class="aside-card">
              <h3>All services</h3>
              <ul>{related}</ul>
            </div>
            <div class="aside-card">
              <h3>Talk to Steve</h3>
              <div class="footer-nap" style="color:var(--body)">
                <div>{phone_ic}<a href="{phone_href}">{phone_display}</a></div>
                <div>{mail_ic}<a href="mailto:{email}">{email}</a></div>
                <div>{pin_ic}<span>{address_one_line}</span></div>
              </div>
            </div>
          </aside>
        </div>
      </section>

{faq}

      <section class="section">
        <div class="container">
          <div class="section-head section-head--center reveal">
            <span class="eyebrow">Related services</span>
            <h2>Other jobs we do on the same visit</h2>
          </div>
          {others}
        </div>
      </section>

{cta}
""".format(
        short=e(service["short"]),
        short_lower=e(service["short"].lower()),
        h1=e(service["h1"]),
        lede=e(service["hero_lede"]),
        hero_photo=hero_media(service["image"], service["alt"]),
        intro=intro_html,
        sections=sections_html,
        audience=e(service["audience"]),
        arrow=icon("arrow"),
        phone=icon("phone"),
        phone_ic=icon("phone"),
        mail_ic=icon("mail"),
        pin_ic=icon("pin"),
        form=quote_form(
            "svc-quote",
            "Free quote",
            "Fixed price, no obligation.",
            preselect=_preselect_for(service),
            compact=True,
        ),
        related=related,
        faq=faq_block(service["faqs"], "%s — common questions" % service["short"]),
        others='<div class="grid grid--3 reveal-stagger">%s</div>'
        % "".join(_service_card(s) for s in others),
        cta=cta_band(
            "Get a fixed price for %s" % service["short"].lower(),
            "Call Steve on 0456 198 080 or send the form. Same-day reply, no obligation, "
            "and the green waste leaves with us.",
        ),
        **SITE
    )
    return meta, body


def _preselect_for(service):
    mapping = {
        "lawn-mowing": "Lawn mowing",
        "ndis-lawn-mowing": "NDIS yard & garden maintenance",
        "garden-maintenance": "Garden maintenance",
        "palm-tree-removal": "Tree & palm removal",
        "green-waste-removal": "Green waste removal / yard clean-up",
        "hedge-trimming-lawn-treatments": "Hedge trimming",
    }
    return mapping.get(service["slug"])


def _service_card(s):
    return """<a class="card service-card" href="/services/{slug}/">
      <div class="media">{img}</div>
      <div class="body">
        <h3>{short}</h3>
        <p>{blurb}</p>
        <span class="more">Read more {arrow}</span>
      </div>
    </a>""".format(
        slug=s["slug"],
        img=img_tag(s["image"].replace(".webp", ""), s["alt"], "(max-width: 700px) calc(100vw - 44px), (max-width: 1100px) 45vw, 33vw"),
        short=e(s["short"]), blurb=e(s["blurb"]), arrow=icon("arrow"),
    )


# ---------------------------------------------------------------------------
# About
# ---------------------------------------------------------------------------
ABOUT_FAQS = [
    (
        "Who owns A1 Lawn Care?",
        "A1 Lawn Care Pty Ltd is owned and run by Steve Cope, working out of 1593 Logan "
        "Rd, Mount Gravatt. Steve quotes the jobs himself, which is why the price you "
        "are given is the price you pay.",
    ),
    (
        "Is A1 Lawn Care insured?",
        "Yes. A1 Lawn Care carries public liability insurance, which matters most on "
        "palm and tree removals and on commercial and body corporate sites. Certificates "
        "of currency are available on request.",
    ),
    (
        "How long has A1 Lawn Care been operating?",
        "A1 Lawn Care has been servicing Brisbane’s southside since 2019, and is a "
        "registered NDIS provider for lawn mowing and yard maintenance.",
    ),
    (
        "What areas does A1 Lawn Care cover?",
        "More than 150 suburbs across four regions — Brisbane south, Bayside, Logan and "
        "the Redlands. That runs from Sherwood and Forest Lake in the west through Mount "
        "Gravatt and Sunnybank, out to Wynnum and Cleveland on the bay, and south "
        "through Springwood, Browns Plains and Beenleigh.",
    ),
]


def build_about():
    meta = {
        "path": "/about/",
        "title": "About A1 Lawn Care | NDIS Lawn Mowing Mount Gravatt",
        "description": (
            "A1 Lawn Care is a Mount Gravatt based, NDIS registered lawn and garden "
            "business run by Steve Cope, servicing 150+ suburbs across Brisbane."
        ),
        "og_image": "about-a1-lawn-care.webp",
        "schema": [
            local_business_schema(),
            faq_schema(ABOUT_FAQS),
            breadcrumb_schema([("Home", "/"), ("About", "/about/")]),
            '{"@context":"https://schema.org","@type":"AboutPage",'
            '"url":"%s/about/","name":"About A1 Lawn Care",'
            '"mainEntity":{"@id":"%s/#business"}}' % (SITE["origin"], SITE["origin"]),
        ],
    }

    values = [
        ("check", "We quote the job, not the hour",
         "An hourly rate rewards taking longer. A fixed price for the job rewards "
         "turning up with the right gear and getting it done."),
        ("calendar", "We turn up when we said",
         "The most common complaint about lawn contractors is not price or quality — "
         "it is that they stopped coming. Regular clients get a fixed day in the run."),
        ("shield", "We are actually registered",
         "Being an NDIS registered provider means audits, paperwork and standards. It "
         "is the reason support coordinators keep sending us work."),
        ("truck", "We clean up after ourselves",
         "Driveways blown down, clippings gone, nothing stacked on the nature strip. "
         "It should not be a selling point, but here we are."),
    ]
    values_html = "".join(
        '<div class="card reveal"><div class="card-icon">%s</div><h3>%s</h3><p>%s</p></div>'
        % (icon(ic), e(t), e(b))
        for ic, t, b in values
    )

    body = """
      <section class="page-hero page-hero--split">
        <div class="container page-hero-grid">
          <div class="page-hero-inner">
            <nav class="breadcrumb" aria-label="Breadcrumb">
              <ol><li><a href="/">Home</a></li><li aria-current="page">About</li></ol>
            </nav>
            <h1>About A1 Lawn Care</h1>
            <p>A Mount Gravatt lawn and garden business, run by Steve Cope, servicing more
               than 150 suburbs across Brisbane south, Bayside, Logan and the Redlands
               &mdash; and a registered NDIS provider.</p>
            <div class="btn-row">
              <a class="btn btn--lg" href="/contact/">Get a free quote {arrow}</a>
              <a class="btn btn--outline-light btn--lg" href="{phone_href}">{phone} {phone_display}</a>
            </div>
          </div>
          {hero_photo}
        </div>
      </section>

      <section class="section">
        <div class="container">
          <div class="grid grid--2" style="align-items:center">
            <div class="prose reveal">
              <span class="eyebrow">Who we are</span>
              <h2>A local business, on the southside, doing the whole yard</h2>
              <p>A1 Lawn Care Pty Ltd operates out of {address_one_line}. That is not a
                 registered office in a different city &mdash; it is where the trailers
                 leave from each morning, which is why Sunnybank, Carindale, Wishart,
                 Holland Park and Springwood are all short drives rather than travel
                 surcharges.</p>
              <p>Steve Cope started A1 Lawn Care to do the whole yard rather than just
                 the lawn. Most clients started with a mow, then asked about the hedge,
                 then the palms, then the beds. Seven services later, the idea is that
                 one phone number covers the lot.</p>
              <p>Somewhere in there, A1 became a registered NDIS provider &mdash; and it
                 turned into the part of the business we are proudest of. Support
                 coordinators kept telling us the same story: plenty of contractors will
                 take the first job, very few are still turning up six months later.
                 Being registered, and being reliable, is a low bar that is surprisingly
                 hard to clear.</p>
            </div>
            <div class="reveal">
              {about_img}
            </div>
          </div>
        </div>
      </section>

      <section class="section section--sand">
        <div class="container">
          <div class="grid grid--4">
            <div class="stat reveal"><span class="num" data-count-to="{n}" data-count-suffix="+">0</span>
              <span class="lbl">suburbs serviced</span></div>
            <div class="stat reveal"><span class="num" data-count-to="7">0</span>
              <span class="lbl">services offered</span></div>
            <div class="stat reveal"><span class="num" data-count-to="4">0</span>
              <span class="lbl">regions covered</span></div>
            <div class="stat reveal"><span class="num">NDIS</span>
              <span class="lbl">registered provider</span></div>
          </div>
        </div>
      </section>

      <section class="section">
        <div class="container">
          <div class="section-head section-head--center reveal">
            <span class="eyebrow">How we work</span>
            <h2>Four things we will not compromise on</h2>
          </div>
          <div class="grid grid--4">{values}</div>
        </div>
      </section>

      <section class="section section--dark">
        <div class="container">
          <div class="grid grid--2" style="align-items:center">
            <div class="reveal">
              <span class="eyebrow">Find us</span>
              <h2>1593 Logan Rd, Mount Gravatt QLD 4122</h2>
              <p>We are a mobile service &mdash; we come to you &mdash; but we are a real
                 business at a real address, which is more than can be said for a lot of
                 the listings you will find searching for a mower.</p>
              <div class="footer-nap" style="margin-top:1.6rem">
                <div>{pin_ic}<span>{address_one_line}</span></div>
                <div>{phone_ic}<a href="{phone_href}">{phone_display}</a></div>
                <div>{mail_ic}<a href="mailto:{email}">{email}</a></div>
                <div>{clock_ic}<span><strong>Monday &ndash; Friday</strong> 7:00am &ndash; 5:00pm<br>
                     <strong>Saturday</strong> 7:00am &ndash; 1:00pm</span></div>
              </div>
            </div>
            <div class="reveal">
              <ul class="ticks">
                <li>{check}<span>Registered NDIS provider for lawn and yard maintenance</span></li>
                <li>{check}<span>Public liability insured &mdash; certificate on request</span></li>
                <li>{check}<span>Domestic, acreage, commercial and body corporate work</span></li>
                <li>{check}<span>Fixed written quotes before any work starts</span></li>
                <li>{check}<span>All green waste removed as part of the job</span></li>
                <li>{check}<span>Servicing Brisbane south, Bayside, Logan and the Redlands</span></li>
              </ul>
            </div>
          </div>
        </div>
      </section>

{areas}

{faq}

{cta}
""".format(
        about_img=img_tag(
            "about-a1-lawn-care",
            "Lawn mower on a freshly mown green lawn - A1 Lawn Care Brisbane",
            "(max-width: 940px) calc(100vw - 44px), 46vw",
            style="border-radius:24px",
        ),
        hero_photo=hero_media(
            "gallery-02.webp",
            "Front lawn and trimmed hedges maintained by A1 Lawn Care on a "
            "Brisbane southside street",
        ),
        arrow=icon("arrow"),
        phone=icon("phone"),
        pin_ic=icon("pin"),
        phone_ic=icon("phone"),
        mail_ic=icon("mail"),
        clock_ic=icon("clock"),
        check=icon("check"),
        values=values_html,
        n=SUBURB_COUNT,
        areas=areas_section(),
        faq=faq_block(ABOUT_FAQS, "About A1 Lawn Care — common questions"),
        cta=cta_band(
            "Let’s get your yard sorted",
            "Call Steve on 0456 198 080 or send the form for a free, fixed quote.",
        ),
        **SITE
    )
    return meta, body


# ---------------------------------------------------------------------------
# Contact
# ---------------------------------------------------------------------------
def build_contact():
    meta = {
        "path": "/contact/",
        "title": "Contact A1 Lawn Care | Free Quote Brisbane 0456 198 080",
        "description": (
            "Get a free lawn mowing quote in Brisbane. Call A1 Lawn Care on "
            "0456 198 080 or send the form. NDIS registered, based at Mount Gravatt."
        ),
        "og_image": "gallery-05.webp",
        "schema": [
            local_business_schema(),
            breadcrumb_schema([("Home", "/"), ("Contact", "/contact/")]),
            '{"@context":"https://schema.org","@type":"ContactPage",'
            '"url":"%s/contact/","name":"Contact A1 Lawn Care",'
            '"mainEntity":{"@id":"%s/#business"}}' % (SITE["origin"], SITE["origin"]),
        ],
    }

    map_q = SITE["address_one_line"].replace(" ", "%20").replace(",", "%2C")

    body = """
      <section class="page-hero page-hero--split">
        <div class="container page-hero-grid">
          <div class="page-hero-inner">
            <nav class="breadcrumb" aria-label="Breadcrumb">
              <ol><li><a href="/">Home</a></li><li aria-current="page">Contact</li></ol>
            </nav>
            <h1>Get a Free Lawn Care Quote in Brisbane</h1>
            <p>Tell us the address and what needs doing. You will get a fixed price back,
               usually the same day. No obligation, and no hourly-rate surprises.</p>
          </div>
          {hero_photo}
        </div>
      </section>

      <section class="section">
        <div class="container with-aside">
          <div class="quote-card reveal" style="box-shadow:var(--shadow)">
            {form}
          </div>

          <aside class="aside-sticky">
            <div class="aside-card">
              <h3>Call or email direct</h3>
              <div class="footer-nap" style="color:var(--body)">
                <div>{phone_ic}<span><strong>Phone</strong><br>
                     <a href="{phone_href}">{phone_display}</a></span></div>
                <div>{mail_ic}<span><strong>Email</strong><br>
                     <a href="mailto:{email}">{email}</a></span></div>
                <div>{pin_ic}<span><strong>Address</strong><br>{address_one_line}</span></div>
                <div>{clock_ic}<span><strong>Hours</strong><br>
                     Mon &ndash; Fri 7:00am &ndash; 5:00pm<br>
                     Sat 7:00am &ndash; 1:00pm</span></div>
              </div>
              <div class="btn-row" style="margin-top:1.4rem">
                <a class="btn btn--block" href="{phone_href}">{phone_ic2} Call {phone_display}</a>
              </div>
            </div>

            <div class="aside-card">
              <h3>NDIS enquiries</h3>
              <p style="font-size:.94rem;color:var(--muted)">We are a registered NDIS
                 provider. Mention your plan manager or support coordinator in the job
                 notes and we will send a quote formatted for plan approval.</p>
              <a class="btn btn--ghost btn--block" href="/services/ndis-lawn-mowing/">
                NDIS yard maintenance {arrow}</a>
            </div>
          </aside>
        </div>
      </section>

      <section class="section section--sand">
        <div class="container">
          <div class="section-head section-head--center reveal">
            <span class="eyebrow">Where we are</span>
            <h2>1593 Logan Rd, Mount Gravatt QLD 4122</h2>
            <p>A mobile service covering more than 150 suburbs &mdash; but a real
               business at a real address on the southside.</p>
          </div>
          <div class="reveal" style="border-radius:24px;overflow:hidden;box-shadow:var(--shadow)">
            <iframe
              title="Map showing A1 Lawn Care at 1593 Logan Rd, Mount Gravatt QLD 4122"
              src="https://www.google.com/maps?q={map_q}&output=embed"
              width="100%" height="420" style="border:0;display:block"
              loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
          </div>
        </div>
      </section>

{areas}

{cta}
""".format(
        form=quote_form(
            "contact-quote",
            "Request your free quote",
            "Every field marked with an asterisk helps us price the job accurately "
            "first time.",
        ),
        hero_photo=hero_media(
            "gallery-08.webp",
            "Freshly mown lawn with a rock border, maintained by A1 Lawn Care Brisbane",
        ),
        phone_ic=icon("phone"),
        phone_ic2=icon("phone"),
        mail_ic=icon("mail"),
        pin_ic=icon("pin"),
        clock_ic=icon("clock"),
        arrow=icon("arrow"),
        map_q=map_q,
        areas=areas_section(),
        cta=cta_band(
            "Prefer to just call?",
            "Steve answers the phone. 0456 198 080, Monday to Saturday.",
        ),
        **SITE
    )
    return meta, body


# ---------------------------------------------------------------------------
# Thank you — every form submission redirects here.
# ---------------------------------------------------------------------------
def build_thank_you():
    meta = {
        "path": "/thank-you/",
        "title": "Thank You | A1 Lawn Care Brisbane",
        "description": (
            "Thanks for contacting A1 Lawn Care. Your quote request has been received "
            "and we will be in touch shortly."
        ),
        "noindex": True,
        "schema": [],
    }

    next_steps = [
        ("clock", "We read it within the hour",
         "Enquiries land straight on Steve’s phone during business hours."),
        ("phone", "We call or email you back",
         "Usually the same day, and always within one business day."),
        ("check", "You get a fixed price",
         "In writing, before anything is booked. It does not change on the day."),
    ]
    steps_html = "".join(
        '<div class="card reveal"><div class="card-icon">%s</div><h3>%s</h3><p>%s</p></div>'
        % (icon(ic), e(t), e(b))
        for ic, t, b in next_steps
    )

    body = """
      <section class="section" style="padding-top:clamp(60px,8vw,110px)">
        <div class="container container--narrow text-center">
          <div class="ty-mark">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6"
                 stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="m20 6-11 11-5-5"/>
            </svg>
          </div>
          <h1 data-lead-name>Thank you!</h1>
          <p style="font-size:1.12rem;max-width:56ch;margin-inline:auto">
            Your quote request has reached A1 Lawn Care. Steve will come back to you with
            a fixed price &mdash; usually the same day, and always within one business day.
          </p>
          <div class="btn-row" style="justify-content:center;margin-top:2rem">
            <a class="btn btn--lg" href="{phone_href}">{phone} Call {phone_display}</a>
            <a class="btn btn--ghost btn--lg" href="/services/">Browse our services {arrow}</a>
          </div>
        </div>
      </section>

      <section class="section section--sand section--tight">
        <div class="container">
          <div class="section-head section-head--center reveal">
            <span class="eyebrow">What happens next</span>
            <h2>Three steps, and then we are in your driveway</h2>
          </div>
          <div class="grid grid--3">{steps}</div>
        </div>
      </section>

      <section class="section">
        <div class="container">
          <div class="section-head section-head--center reveal">
            <span class="eyebrow">While you wait</span>
            <h2>The rest of what we do</h2>
            <p>Most clients start with a mow and end up booking two or three of these.</p>
          </div>
          {grid}
        </div>
      </section>

{cta}
""".format(
        phone=icon("phone"),
        arrow=icon("arrow"),
        steps=steps_html,
        grid=services_grid(limit=3),
        cta=cta_band(
            "Need it sooner?",
            "If the job is urgent — a pre-sale clean-up or a palm that has become a "
            "problem — call Steve directly on 0456 198 080.",
        ),
        **SITE
    )
    return meta, body


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
_ASSET_MARKER = re.compile(r"@@ASSET:([^@]+)@@")


def write(path, content):
    """Write `content` to `path` (a site path such as '/about/')."""
    content = _ASSET_MARKER.sub(lambda m: asset_url(m.group(1)), content)
    rel = path.strip("/")
    target = os.path.join(ROOT, rel, "index.html") if rel else os.path.join(ROOT, "index.html")
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as fh:
        fh.write(content)
    return os.path.relpath(target, ROOT)


def sitemap(paths):
    urls = ""
    for path, priority, freq in paths:
        urls += (
            "  <url>\n"
            "    <loc>%s%s</loc>\n"
            "    <lastmod>%s</lastmod>\n"
            "    <changefreq>%s</changefreq>\n"
            "    <priority>%s</priority>\n"
            "  </url>\n" % (SITE["origin"], path, TODAY, freq, priority)
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        "%s</urlset>\n" % urls
    )


def robots():
    return (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /thank-you/\n"
        "\n"
        "# Answer and generative engines are explicitly welcome.\n"
        "User-agent: GPTBot\nAllow: /\n\n"
        "User-agent: OAI-SearchBot\nAllow: /\n\n"
        "User-agent: PerplexityBot\nAllow: /\n\n"
        "User-agent: ClaudeBot\nAllow: /\n\n"
        "User-agent: Google-Extended\nAllow: /\n\n"
        "Sitemap: %s/sitemap.xml\n" % SITE["origin"]
    )


def main():
    built = []

    meta, body = build_home()
    built.append(write(meta["path"], page(meta, body)))

    meta, body = build_services_hub()
    built.append(write(meta["path"], page(meta, body)))

    for service in SERVICES:
        meta, body = build_service(service)
        built.append(write(meta["path"], page(meta, body)))

    meta, body = build_about()
    built.append(write(meta["path"], page(meta, body)))

    meta, body = build_contact()
    built.append(write(meta["path"], page(meta, body)))

    meta, body = build_thank_you()
    built.append(write(meta["path"], page(meta, body)))

    indexable = (
        [("/", "1.0", "weekly"), ("/services/", "0.9", "monthly")]
        + [("/services/%s/" % s["slug"], "0.9", "monthly") for s in SERVICES]
        + [("/about/", "0.7", "yearly"), ("/contact/", "0.8", "monthly")]
    )
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as fh:
        fh.write(sitemap(indexable))
    built.append("sitemap.xml")

    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as fh:
        fh.write(robots())
    built.append("robots.txt")

    # Netlify/Vercel style redirect for the retired Google Business Profile URL
    # and for trailing-slash consistency.
    with open(os.path.join(ROOT, "_redirects"), "w", encoding="utf-8") as fh:
        fh.write(
            "# Legacy paths from the previous WordPress site\n"
            "/services/*   /services/:splat   301\n"
            "/contact-us/  /contact/          301\n"
            "/about-us/    /about/            301\n"
            "/thank-you    /thank-you/        301\n"
        )
    built.append("_redirects")

    print("Built %d files:" % len(built))
    for f in built:
        print("  " + f)
    print("\n%d suburbs across %d regions." % (SUBURB_COUNT, len(SUBURBS)))


if __name__ == "__main__":
    main()
