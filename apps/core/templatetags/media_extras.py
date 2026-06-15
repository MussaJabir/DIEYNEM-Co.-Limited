"""Responsive-image helpers backed by easy-thumbnails.

``{% responsive_image image alt="…" img_class="…" sizes="…" ratio="16:9" %}``
renders a ``<picture>`` with a WebP ``<source>`` plus an original-format
``<img>`` fallback, each carrying a width-described ``srcset`` so the browser
downloads only the size it needs. Derivatives are generated on first use and
cached by easy-thumbnails; originals are never upscaled.
"""

from django import template
from easy_thumbnails.files import get_thumbnailer

register = template.Library()

# Width breakpoints generated for every responsive image (CSS picks via sizes).
DEFAULT_WIDTHS = (480, 768, 1200)


def _height_for(width: int, ratio: str | None) -> int:
    """Target height for a width given an ``"W:H"`` ratio (0 = scale by width)."""
    if not ratio:
        return 0
    try:
        rw, rh = (int(part) for part in ratio.split(":"))
        return round(width * rh / rw)
    except (ValueError, ZeroDivisionError):
        return 0


@register.inclusion_tag("public/_responsive_image.html")
def responsive_image(
    image,
    alt="",
    img_class="",
    sizes="100vw",
    ratio=None,
    widths=DEFAULT_WIDTHS,
    loading="lazy",
    fetchpriority="",
):
    """Build WebP + fallback srcsets for ``image`` (an ImageField file).

    ``ratio`` like ``"16:9"`` centre-crops to that shape; without it the image
    is scaled by width, preserving its aspect ratio. Returns empty context when
    there is no usable image so the partial renders nothing.
    """
    if not image:
        return {"sources": None}

    # Two thumbnailers: one forced to .webp (easy-thumbnails derives the encoder
    # from the extension, not from an option), one left at the default extension
    # for the original-format fallback.
    webp_thumbnailer = get_thumbnailer(image)
    webp_thumbnailer.thumbnail_extension = "webp"
    fallback_thumbnailer = get_thumbnailer(image)

    crop = bool(ratio)
    webp_set, fallback_set = [], []
    fallback_src = ""
    width_attr = height_attr = None
    for width in widths:
        options = {"size": (width, _height_for(width, ratio)), "crop": crop, "upscale": False}
        try:
            webp = webp_thumbnailer.get_thumbnail(options)
            fallback = fallback_thumbnailer.get_thumbnail(options)
        except Exception:
            # A missing/corrupt source must not 500 a whole page — fall back to
            # the original file so the image still renders.
            return {
                "sources": None,
                "fallback_src": image.url,
                "alt": alt,
                "img_class": img_class,
                "loading": loading,
                "fetchpriority": fetchpriority,
            }
        webp_set.append(f"{webp.url} {width}w")
        fallback_set.append(f"{fallback.url} {width}w")
        fallback_src = fallback.url
        # Intrinsic size of the largest derivative — emitted as width/height so
        # the browser reserves the right aspect-ratio box and avoids layout
        # shift (CLS) while the image loads.
        width_attr, height_attr = fallback.width, fallback.height

    return {
        "sources": True,
        "webp_srcset": ", ".join(webp_set),
        "fallback_srcset": ", ".join(fallback_set),
        "fallback_src": fallback_src,
        "sizes": sizes,
        "alt": alt,
        "img_class": img_class,
        "loading": loading,
        "fetchpriority": fetchpriority,
        "width": width_attr,
        "height": height_attr,
    }
