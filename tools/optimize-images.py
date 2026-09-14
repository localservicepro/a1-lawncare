#!/usr/bin/env python3
"""
Turn the Google Drive originals in assets/img/_src/ into the responsive,
properly-compressed WebP files the site actually serves.

    python3 tools/optimize-images.py

The Drive files are web-format but not web-weight: the hero was 158 KiB of
1920px photograph being painted behind a 90%-opaque scrim on a 366px phone
screen, and the 300x300 logo was rendering at 46px. PageSpeed flagged ~296 KiB
of waste on mobile.

For each source this writes `<name>-<width>.webp` at a handful of widths, and
`build.py` emits them as srcset so a phone downloads the phone-sized file.
Originals stay in _src/ untouched, so re-running is lossless — never re-encode
a WebP from a WebP you already re-encoded.
"""

import os
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow is required:  pip install Pillow")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets", "img", "_src")
OUT = os.path.join(ROOT, "assets", "img")

# name -> (widths to emit, quality, kind)
#
# Widths are driven by how large the image actually renders:
#   hero        full-bleed; on phones it sits under a 90% scrim, so 480 is ample
#   card        ~540px in a hero card / ~370px in a grid, source is only 600px
#   wide        ~540px in the about two-column block
#   graphic     logos — small, flat colour, needs higher quality to stay crisp
PLAN = {
    "gardener-at-work":              ([480, 960, 1440, 1920], 62, "photo"),
    "about-a1-lawn-care":            ([480, 900, 1400], 66, "photo"),
    "gallery-01":                    ([400, 600], 66, "photo"),
    "gallery-02":                    ([400, 600], 66, "photo"),
    "gallery-03":                    ([400, 600], 66, "photo"),
    "gallery-04":                    ([400, 600], 66, "photo"),
    "gallery-05":                    ([400, 600], 66, "photo"),
    "gallery-06":                    ([400, 600], 66, "photo"),
    "gallery-07":                    ([400, 600], 66, "photo"),
    "gallery-08":                    ([400, 600], 66, "photo"),
    "a1-lawn-care-logo":             ([112, 224], 88, "graphic"),
    "ndis-registered-provider-logo": ([180, 360], 88, "graphic"),
}


def emit(name, widths, quality, kind):
    src_path = os.path.join(SRC, name + ".webp")
    if not os.path.exists(src_path):
        print("  skip   %-32s (no source — run fetch-drive-images.sh)" % name)
        return 0, 0

    img = Image.open(src_path)
    has_alpha = img.mode in ("RGBA", "LA") or "transparency" in img.info
    img = img.convert("RGBA" if has_alpha else "RGB")
    sw, sh = img.size
    before = os.path.getsize(src_path)
    after = 0

    for width in widths:
        # Never upscale — an enlarged source is bytes with no detail in them.
        w = min(width, sw)
        h = max(1, round(sh * w / sw))
        resized = img if (w, h) == (sw, sh) else img.resize((w, h), Image.LANCZOS)

        dest = os.path.join(OUT, "%s-%d.webp" % (name, width))
        resized.save(
            dest,
            "WEBP",
            quality=quality,
            method=6,                      # slowest encode, smallest file
            lossless=False,
            exact=has_alpha,
        )
        size = os.path.getsize(dest)
        after += size
        print("  write  %-32s %5dx%-4d %6.1f KiB" % (os.path.basename(dest), w, h, size / 1024))

    return before, after


def main():
    if not os.path.isdir(SRC):
        sys.exit("No originals in %s — run tools/fetch-drive-images.sh first." % SRC)

    os.makedirs(OUT, exist_ok=True)
    total_before = total_after = 0

    for name in sorted(PLAN):
        widths, quality, kind = PLAN[name]
        before, after = emit(name, widths, quality, kind)
        total_before += before
        total_after += after

    print()
    print("originals   %7.1f KiB" % (total_before / 1024))
    print("derivatives %7.1f KiB across all widths" % (total_after / 1024))


if __name__ == "__main__":
    main()
