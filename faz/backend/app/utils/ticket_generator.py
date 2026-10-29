# app/utils/ticket_generator.py
"""
FAZ football ticket generator (v3).

The PNG files in app/assets/templates/ are presentation templates.
This module only writes dynamic database data into the blank areas.

Supported templates:
    - open wing.png
    - grand stand.png
    - vip.png
    - vvip.png

Encoding rules:
    Both the printed ticket number AND the QR payload use the SAME
    short encoded value. The pipeline is:

        raw UUID
            -> "FAZ-<raw UUID>"
            -> base64 (stage 1)
            -> blake2b hash (stage 2, deterministic)
            -> base62 (stage 3)
            -> padded to exactly SHORT_CODE_LENGTH characters

    The literal "FAZ" never appears on the ticket or in the QR.
    The final short code is < 10 characters and is deterministic,
    so the same UUID always maps to the same short code.

    Because the pipeline includes a cryptographic hash, the short
    code is NOT reversible by pure decoding. Use
    `resolve_short_code()` to map a code back to its raw UUID
    (an in-memory registry is maintained automatically, and an
    optional DB-scanning fallback is provided).

Font colour rules:
    Text colour is chosen automatically based on the luminance
    of the background pixel-region where the text will sit.
    - Dark background -> bright text
    - Bright background -> dark text

Regeneration:
    By default every call regenerates the PNG and overwrites
    any existing file.

Fully customisable per-template layouts:
    See the LAYOUTS dictionary further down.
"""

import os
import io
import base64
import hashlib

import qrcode
import requests

from PIL import Image, ImageDraw, ImageFont, ImageFilter


# ============================================================================
# RUNTIME FLAGS
# ============================================================================

REGENERATE_ON_EACH_CALL = True

BACKGROUND_SAMPLE_SIZE = 40
LUMINANCE_THRESHOLD = 140

# Length of the final short code (must be < 10 to satisfy requirement).
SHORT_CODE_LENGTH = 8


# ============================================================================
# PATHS
# ============================================================================

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_APP_DIR = os.path.dirname(_CURRENT_DIR)

ASSETS_DIR = os.path.join(_APP_DIR, "assets")
TEMPLATES_DIR = os.path.join(ASSETS_DIR, "templates")
OUTPUT_DIR = os.path.join(ASSETS_DIR, "tickets")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(FONTS_DIR, exist_ok=True)


# ============================================================================
# TEMPLATE MAP
# ============================================================================

TEMPLATE_MAP = {
    "vvip": "vvip.png",
    "v.v.i.p": "vvip.png",
    "v.v.i.p.": "vvip.png",

    "vip": "vip.png",
    "v.i.p": "vip.png",
    "v.i.p.": "vip.png",

    "grand stand": "grand stand.png",
    "grandstand": "grand stand.png",
    "grand-stand": "grand stand.png",

    "open wing": "open wing.png",
    "openwing": "open wing.png",
    "open-wing": "open wing.png",
    "ow": "open wing.png",
}

DEFAULT_TEMPLATE = "grand stand.png"


def _tpl_path(filename):
    path = os.path.join(TEMPLATES_DIR, filename)
    if os.path.exists(path):
        return path
    fallback = os.path.join(TEMPLATES_DIR, DEFAULT_TEMPLATE)
    if os.path.exists(fallback):
        return fallback
    return None


def _template_path_for(ticket_type_name):
    key = str(ticket_type_name or "").strip().lower()

    if key in TEMPLATE_MAP:
        return _tpl_path(TEMPLATE_MAP[key])

    # IMPORTANT: VVIP before VIP.
    for needle in (
        "vvip", "vip",
        "grand stand", "grandstand",
        "open wing", "openwing",
    ):
        if needle in key:
            return _tpl_path(TEMPLATE_MAP[needle])

    return _tpl_path(DEFAULT_TEMPLATE)


def _ticket_category(ticket_type_name):
    key = str(ticket_type_name or "").strip().lower()

    if "vvip" in key or "v.v.i.p" in key:
        return "vvip"
    if "vip" in key or "v.i.p" in key:
        return "vip"
    if "grand" in key:
        return "grand stand"
    if "open" in key or key == "ow":
        return "open wing"

    return "grand stand"


# ============================================================================
# THEME
# ============================================================================

THEME = {
    "open wing": {
        "text":          "auto",
        "team":          "auto",
        "team_stroke":   (255, 255, 255),
        "value":         "auto",
        "stub_value":    "auto",
        "ticket_number": "auto",
        "qr_fill":       "black",
        "qr_back":       "white",
    },

    "grand stand": {
        "text":          "auto",
        "team":          "auto",
        "team_stroke":   (255, 255, 255),
        "value":         "auto",
        "stub_value":    "auto",
        "ticket_number": "auto",
        "qr_fill":       "black",
        "qr_back":       "white",
    },

    "vip": {
        "text":          "auto",
        "team":          "auto",
        "team_stroke":   (255, 255, 255),
        "value":         "auto",
        "stub_value":    "auto",
        "ticket_number": "auto",
        "qr_fill":       "black",
        "qr_back":       "white",
    },

    "vvip": {
        "text":          "auto",
        "team":          "auto",
        "team_stroke":   (60, 40, 0),
        "value":         "auto",
        "stub_value":    "auto",
        "ticket_number": "auto",
        "qr_fill":       "black",
        "qr_back":       "white",
    },
}

AUTO_LIGHT_TEXT = (255, 255, 255)
AUTO_DARK_TEXT = (18, 18, 18)


# ============================================================================
# FONTS
# ============================================================================

_FONT_CANDIDATES = {
    "regular": [
        "Montserrat-Regular.ttf",
        "Montserrat-Medium.ttf",
        "Montserrat.ttf",
        "Inter-Regular.ttf",
        "Inter.ttf",
        "Poppins-Regular.ttf",
        "Arial.ttf",
        "segoeui.ttf",
        "DejaVuSans.ttf",
    ],
    "bold": [
        "Montserrat-Bold.ttf",
        "Montserrat-SemiBold.ttf",
        "Inter-Bold.ttf",
        "Inter-SemiBold.ttf",
        "Poppins-Bold.ttf",
        "Poppins-SemiBold.ttf",
        "Arial Bold.ttf",
        "arialbd.ttf",
        "segoeuib.ttf",
        "DejaVuSans-Bold.ttf",
    ],
}

_SYSTEM_FONT_DIRS = [
    os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts"),
    "/usr/share/fonts/truetype/montserrat",
    "/usr/share/fonts/truetype/dejavu",
    "/usr/share/fonts/truetype/liberation2",
    "/usr/share/fonts/truetype",
    "/System/Library/Fonts",
    "/Library/Fonts",
]

_FONT_CACHE = {}


def _find_font_file(bold=False):
    group = "bold" if bold else "regular"

    for filename in _FONT_CANDIDATES[group]:
        path = os.path.join(FONTS_DIR, filename)
        if os.path.isfile(path):
            return path

    for directory in _SYSTEM_FONT_DIRS:
        if not os.path.isdir(directory):
            continue
        for filename in _FONT_CANDIDATES[group]:
            path = os.path.join(directory, filename)
            if os.path.isfile(path):
                return path

    if os.path.isdir(FONTS_DIR):
        preferred = (
            ("bold", "semibold", "medium") if bold
            else ("regular", "normal", "book")
        )
        for filename in sorted(os.listdir(FONTS_DIR)):
            low = filename.lower()
            if not low.endswith((".ttf", ".otf")):
                continue
            if any(word in low for word in preferred):
                return os.path.join(FONTS_DIR, filename)

    return None


_FONT_REGULAR_FILE = _find_font_file(False)
_FONT_BOLD_FILE = _find_font_file(True)


def _get_font(size, bold=False):
    size = max(8, int(size))
    key = (size, bool(bold))

    if key in _FONT_CACHE:
        return _FONT_CACHE[key]

    path = _FONT_BOLD_FILE if bold else _FONT_REGULAR_FILE

    if path:
        try:
            font = ImageFont.truetype(path, size)
            _FONT_CACHE[key] = font
            return font
        except Exception:
            pass

    fallback = (
        ["arialbd.ttf", "segoeuib.ttf", "DejaVuSans-Bold.ttf"] if bold
        else ["arial.ttf", "segoeui.ttf", "DejaVuSans.ttf"]
    )
    for filename in fallback:
        try:
            font = ImageFont.truetype(filename, size)
            _FONT_CACHE[key] = font
            return font
        except Exception:
            continue

    font = ImageFont.load_default()
    _FONT_CACHE[key] = font
    return font


# ============================================================================
# IMAGE HELPERS
# ============================================================================

_ORIGINAL_IMAGE_CACHE = {}

try:
    RESAMPLE_FILTER = Image.Resampling.LANCZOS
except AttributeError:
    RESAMPLE_FILTER = Image.LANCZOS


def _load_image(source, size):
    if not source:
        return None
    try:
        if source in _ORIGINAL_IMAGE_CACHE:
            img = _ORIGINAL_IMAGE_CACHE[source]
        elif (
            isinstance(source, str)
            and source.startswith(("http://", "https://"))
        ):
            response = requests.get(source, timeout=8)
            response.raise_for_status()
            img = Image.open(io.BytesIO(response.content)).convert("RGBA")
            _ORIGINAL_IMAGE_CACHE[source] = img
        else:
            candidates = [
                source,
                os.path.join(ASSETS_DIR, source),
                os.path.join(ASSETS_DIR, "..", source),
                os.path.join(os.getcwd(), source),
            ]
            path = next(
                (item for item in candidates if os.path.exists(item)),
                None,
            )
            if not path:
                return None
            img = Image.open(path).convert("RGBA")
            _ORIGINAL_IMAGE_CACHE[source] = img

        return img.resize(size, RESAMPLE_FILTER)
    except Exception as e:
        print(f"[ticket_gen] Could not load image '{source}': {e}")
        return None


def _fit_cover(img, size):
    target_w, target_h = size
    src_w, src_h = img.size
    scale = max(target_w / src_w, target_h / src_h)
    new_w = max(1, int(src_w * scale))
    new_h = max(1, int(src_h * scale))
    resized = img.resize((new_w, new_h), RESAMPLE_FILTER)
    left = max(0, (new_w - target_w) // 2)
    top = max(0, (new_h - target_h) // 2)
    return resized.crop((left, top, left + target_w, top + target_h))


def _paste_circular(base, img, center_xy, diameter,
                    border_color=None, border_width=0):
    if img is None:
        return
    diameter = int(diameter)
    fitted = _fit_cover(img, (diameter, diameter))

    mask = Image.new("L", (diameter, diameter), 0)
    ImageDraw.Draw(mask).ellipse(
        (0, 0, diameter - 1, diameter - 1), fill=255
    )
    mask = mask.filter(ImageFilter.GaussianBlur(0.5))

    x = int(center_xy[0] - diameter / 2)
    y = int(center_xy[1] - diameter / 2)

    base.paste(fitted, (x, y), mask)

    if border_color is not None and border_width > 0:
        ImageDraw.Draw(base).ellipse(
            (x, y, x + diameter - 1, y + diameter - 1),
            outline=border_color,
            width=border_width,
        )


# ============================================================================
# BACKGROUND-AWARE COLOUR SELECTION
# ============================================================================

def _sample_background_color(source_image, center_xy, sample_size=None):
    if sample_size is None:
        sample_size = BACKGROUND_SAMPLE_SIZE

    x, y = center_xy
    w, h = source_image.size

    x1 = max(0, x - sample_size // 2)
    y1 = max(0, y - sample_size // 2)
    x2 = min(w, x + sample_size // 2)
    y2 = min(h, y + sample_size // 2)

    if x1 >= x2 or y1 >= y2:
        return (255, 255, 255)

    try:
        region = source_image.crop((x1, y1, x2, y2)).convert("RGB")
        region = region.resize((8, 8), RESAMPLE_FILTER)
        pixels = list(region.getdata())
    except Exception:
        return (255, 255, 255)

    if not pixels:
        return (255, 255, 255)

    r = sum(p[0] for p in pixels) // len(pixels)
    g = sum(p[1] for p in pixels) // len(pixels)
    b = sum(p[2] for p in pixels) // len(pixels)
    return (r, g, b)


def _relative_luminance(rgb):
    r, g, b = rgb[:3]
    return 0.299 * r + 0.587 * g + 0.114 * b


def _contrast_color(background_rgb):
    lum = _relative_luminance(background_rgb)
    if lum < LUMINANCE_THRESHOLD:
        return AUTO_LIGHT_TEXT
    return AUTO_DARK_TEXT


def _resolve_fill(fill, source_image, center_xy):
    if fill == "auto":
        bg = _sample_background_color(source_image, center_xy)
        return _contrast_color(bg)
    return fill


# ============================================================================
# TEAM LOOKUP
# ============================================================================

def _resolve_team(team_id):
    if not team_id:
        return ("TBD", None)

    from app.models import NationalTeam, Club

    nt = NationalTeam.query.get(team_id)
    if nt:
        country_name = None
        if getattr(nt, "country", None):
            country_name = getattr(nt.country, "name", None)

        display_name = (
            country_name or getattr(nt, "name", None) or "TBD"
        )
        img = getattr(nt, "flag_image_url", None)
        if not img and getattr(nt, "country", None):
            img = getattr(nt.country, "flag_image_url", None)
        return (display_name, img)

    club = Club.query.get(team_id)
    if club:
        return (
            getattr(club, "name", None) or "TBD",
            getattr(club, "logo_url", None),
        )

    return ("TBD", None)


# ============================================================================
# LAYOUTS  (one block per template)
# ============================================================================

REF_W = 1774
REF_H = 887


_DEFAULT_LAYOUT = {
    "home_flag_center": (270, 410),
    "away_flag_center": (720, 410),
    "flag_diameter": 122,
    "home_name_center": (270, 515),
    "away_name_center": (720, 515),
    "team_name_max_width": 275,

    "date_center": (1140, 375),
    "time_center": (1140, 465),
    "venue_center": (1120, 580),
    "match_value_max_width": 230,

    "qr_box": (1230, 635, 1360, 765),

    "section_center": (1570, 320),
    "row_center": (1570, 420),
    "seat_center": (1570, 515),
    "ticket_no_center": (1610, 630),
    "stub_value_max_width": 195,

    "bottom_ticket_number_center": (315, 800),
    "bottom_ticket_number_max_width": 430,
}


def _copy_layout(src):
    return dict(src)


LAYOUTS = {
    # ------------------------------------------------------------------
    # OPEN WING
    # ------------------------------------------------------------------
    "open wing": _copy_layout({
        "home_flag_center": (270, 410),
        "away_flag_center": (720, 410),
        "flag_diameter": 122,
        "home_name_center": (270, 515),
        "away_name_center": (720, 515),
        "team_name_max_width": 275,

        "date_center": (1140, 375),
        "time_center": (1140, 465),
        "venue_center": (1120, 580),
        "match_value_max_width": 230,

        "qr_box": (1230, 635, 1360, 765),

        "section_center": (1570, 320),
        "row_center": (1570, 420),
        "seat_center": (1570, 515),
        "ticket_no_center": (1610, 630),
        "stub_value_max_width": 195,

        "bottom_ticket_number_center": (315, 800),
        "bottom_ticket_number_max_width": 430,
    }),

    # ------------------------------------------------------------------
    # GRAND STAND
    # ------------------------------------------------------------------
    "grand stand": _copy_layout({
        "home_flag_center": (270, 410),
        "away_flag_center": (720, 410),
        "flag_diameter": 122,
        "home_name_center": (270, 515),
        "away_name_center": (720, 515),
        "team_name_max_width": 275,

        "date_center": (1140, 375),
        "time_center": (1140, 465),
        "venue_center": (1120, 570),
        "match_value_max_width": 230,

        "qr_box": (1230, 635, 1360, 765),

        "section_center": (1570, 310),
        "row_center": (1570, 415),
        "seat_center": (1570, 515),
        "ticket_no_center": (1610, 620),
        "stub_value_max_width": 195,

        "bottom_ticket_number_center": (475, 775),
        "bottom_ticket_number_max_width": 430,
    }),

    # ------------------------------------------------------------------
    # VIP
    # ------------------------------------------------------------------
    "vip": _copy_layout({
        "home_flag_center": (270, 410),
        "away_flag_center": (720, 410),
        "flag_diameter": 122,
        "home_name_center": (270, 515),
        "away_name_center": (720, 515),
        "team_name_max_width": 275,

        "date_center": (1140, 375),
        "time_center": (1140, 465),
        "venue_center": (1120, 570),
        "match_value_max_width": 230,

        "qr_box": (1230, 635, 1360, 765),

        "section_center": (1570, 320),
        "row_center": (1570, 420),
        "seat_center": (1570, 515),
        "ticket_no_center": (1610, 615),
        "stub_value_max_width": 195,

        "bottom_ticket_number_center": (475, 750),
        "bottom_ticket_number_max_width": 430,
    }),

    # ------------------------------------------------------------------
    # VVIP
    # ------------------------------------------------------------------
    "vvip": _copy_layout({
        "home_flag_center": (270, 410),
        "away_flag_center": (720, 410),
        "flag_diameter": 122,
        "home_name_center": (270, 515),
        "away_name_center": (720, 515),
        "team_name_max_width": 275,

        "date_center": (1140, 375),
        "time_center": (1140, 465),
        "venue_center": (1120, 580),
        "match_value_max_width": 230,

        "qr_box": (1230, 635, 1360, 765),

        "section_center": (1570, 340),
        "row_center": (1570, 430),
        "seat_center": (1570, 520),
        "ticket_no_center": (1610, 620),
        "stub_value_max_width": 195,

        "bottom_ticket_number_center": (475, 770),
        "bottom_ticket_number_max_width": 430,
    }),
}


def _layout_for(category):
    return LAYOUTS.get(category) or _copy_layout(_DEFAULT_LAYOUT)


# ============================================================================
# SCALING
# ============================================================================

def _sx(x, width):
    return int(x * width / REF_W)


def _sy(y, height):
    return int(y * height / REF_H)


def _ss(value, width):
    return int(value * width / REF_W)


def _point(point, width, height):
    return (_sx(point[0], width), _sy(point[1], height))


# ============================================================================
# TEXT HELPERS
# ============================================================================

def _fit_text(draw, text, font, max_width):
    text = str(text or "").strip()
    if not text:
        return font, text

    size = getattr(font, "size", 20)
    is_bold = True

    while size > 10:
        bbox = draw.textbbox((0, 0), text, font=font)
        if bbox[2] - bbox[0] <= max_width:
            return font, text
        size -= 1
        font = _get_font(size, bold=is_bold)

    bbox = draw.textbbox((0, 0), text, font=font)
    while bbox[2] - bbox[0] > max_width and len(text) > 3:
        text = text[:-2] + "…"
        bbox = draw.textbbox((0, 0), text, font=font)

    return font, text


def _draw_centered(draw, text, center_xy, font, fill,
                   max_width=None, stroke_width=0, stroke_fill=None):
    if text is None:
        return
    text = str(text).strip()
    if not text:
        return

    if max_width:
        font, text = _fit_text(draw, text, font, max_width)

    bbox = draw.textbbox(
        (0, 0), text, font=font, stroke_width=stroke_width,
    )
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]

    x = center_xy[0] - width / 2 - bbox[0]
    y = center_xy[1] - height / 2 - bbox[1]

    kwargs = {"font": font, "fill": fill}
    if stroke_width:
        kwargs["stroke_width"] = stroke_width
        kwargs["stroke_fill"] = (
            stroke_fill if stroke_fill is not None else fill
        )

    draw.text((int(x), int(y)), text, **kwargs)


# ============================================================================
# FORMATTERS
# ============================================================================

def _format_date(dt):
    if not dt:
        return "—"
    try:
        return dt.strftime("%d %b %Y")
    except Exception:
        return str(dt)


def _format_time(dt):
    if not dt:
        return "—"
    try:
        return dt.strftime("%H:%M")
    except Exception:
        return str(dt)


def _clean_value(value):
    if value is None:
        return "—"
    value = str(value).strip()
    return value or "—"


def _first_attr(obj, *names):
    for name in names:
        value = getattr(obj, name, None)
        if value not in (None, ""):
            return value
    return None


# ============================================================================
# SHORT CODE ENCODING (multi-stage)
# ============================================================================
#
# Base62 alphabet: 0-9A-Za-z  (62 characters, URL-safe, no padding).
#
# The pipeline:
#
#   raw UUID           e.g. "3f2504e0-4f89-11d3-9a0c-0305e82c3301"
#   -------------------------------------------------------------------
#   stage 1: "FAZ-" + raw
#   stage 2: base64(stage1)                 -> ~55 chars
#   stage 3: blake2b(stage2, digest_size=5) -> 5 bytes (40 bits)
#   stage 4: base62(stage 3 bytes)          -> up to 7 chars
#   stage 5: zfill to SHORT_CODE_LENGTH     -> exactly 8 chars
#
# The resulting 8-character code is:
#   - deterministic (same UUID -> same code)
#   - uniformly distributed (from the hash)
#   - collision-safe enough for a ticket system
#       (2^40 = ~1.1 trillion possible values)
#   - completely opaque (the "FAZ" prefix never appears)

_BASE62_ALPHABET = (
    "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
)
_BASE62_INDEX = {c: i for i, c in enumerate(_BASE62_ALPHABET)}


def _base62_encode(num: int) -> str:
    if num < 0:
        raise ValueError("Cannot base62-encode negative integers")
    if num == 0:
        return _BASE62_ALPHABET[0]

    out = []
    while num > 0:
        num, rem = divmod(num, 62)
        out.append(_BASE62_ALPHABET[rem])
    return "".join(reversed(out))


def _base62_decode(text: str) -> int:
    num = 0
    for ch in text:
        if ch not in _BASE62_INDEX:
            raise ValueError(f"Invalid base62 character: {ch!r}")
        num = num * 62 + _BASE62_INDEX[ch]
    return num


# ---------------------------------------------------------------------------
# In-memory registry: short code -> raw UUID.
#
# Populated automatically during encoding. Use `resolve_short_code()`
# to look up a raw UUID from a short code (for verification, ticket
# scanner, etc.).
#
# NOTE: This registry is process-local. For a multi-process deployment
# (gunicorn, multiple workers), persist the mapping in the database
# (e.g. a `ticket_short_code` table) and use that inside
# `resolve_short_code()`.
# ---------------------------------------------------------------------------

_SHORT_CODE_REGISTRY: dict = {}


def _raw_ticket_number(ticket):
    """
    Return the raw ticket number from the database.
    Falls back to the primary key if the model doesn't supply one.
    """
    value = getattr(ticket, "ticket_number", None)
    if value not in (None, ""):
        return str(value).strip()
    return str(getattr(ticket, "id", "")).strip()


def _encode_ticket_number(raw_ticket_number, short_length=None):
    """
    Produce the short, deterministic, opaque code for a ticket.

    The literal "FAZ" never appears on the ticket or inside the QR.
    It is embedded in stage 1, then hidden behind the base64 and
    hash layers.

    Parameters
    ----------
    raw_ticket_number : str
        The raw UUID / long value pulled from the database.
    short_length : int, optional
        Target length. Defaults to SHORT_CODE_LENGTH (8).

    Returns
    -------
    str
        A code of exactly `short_length` characters.
    """
    if short_length is None:
        short_length = SHORT_CODE_LENGTH

    raw = f"FAZ-{raw_ticket_number}"

    # Stage 1: base64 encode the FAZ-prefixed value.
    stage1 = base64.b64encode(raw.encode("utf-8")).decode("ascii")

    # Stage 2: deterministic hash of the base64 string.
    #   5 bytes = 40 bits, which fits comfortably inside 8 base62
    #   characters (62^8 = ~2.18e14, i.e. ~47.6 bits).
    digest = hashlib.blake2b(
        stage1.encode("ascii"),
        digest_size=5,
    ).digest()

    # Stage 3: base62 encode the digest bytes.
    code = _base62_encode(int.from_bytes(digest, "big"))

    # Stage 4: normalise to exactly `short_length` characters.
    if len(code) > short_length:
        code = code[:short_length]
    else:
        code = code.zfill(short_length)

    # Remember the mapping (best-effort; helps same-process lookups).
    _SHORT_CODE_REGISTRY[code] = raw_ticket_number

    return code


def _qr_payload(encoded_ticket_number):
    """
    The QR code holds the SAME short code that is printed on the
    ticket. There is no separate prefix.
    """
    return encoded_ticket_number


def resolve_short_code(short_code, db_session=None):
    """
    Resolve a short code back to the original raw ticket number.

    Lookup order:
      1. In-memory registry (fast, same-process).
      2. Database scan via `db_session` (slow, but works across
         restarts).

    Parameters
    ----------
    short_code : str
        The short code printed on the ticket / held in the QR.
    db_session : SQLAlchemy Session, optional
        If provided, enables the DB fallback.

    Returns
    -------
    str or None
        The raw ticket number, or None if it cannot be resolved.
    """
    if not short_code:
        return None

    # 1. Fast path: in-memory registry.
    cached = _SHORT_CODE_REGISTRY.get(short_code)
    if cached is not None:
        return cached

    # 2. Fallback: scan tickets and re-encode each one.
    if db_session is not None:
        try:
            from app.models import Ticket
            for ticket in db_session.query(Ticket).yield_per(500):
                raw = _raw_ticket_number(ticket)
                computed = _encode_ticket_number(
                    raw, short_length=len(short_code)
                )
                if computed == short_code:
                    _SHORT_CODE_REGISTRY[short_code] = raw
                    return raw
        except Exception as e:
            print(f"[ticket_gen] resolve_short_code DB error: {e}")

    return None


def _generate_qr(payload, fill_color="black", back_color="white"):
    try:
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=1,
        )
        qr.add_data(payload)
        qr.make(fit=True)
        return qr.make_image(
            fill_color=fill_color, back_color=back_color
        ).convert("RGBA")
    except Exception as e:
        print(f"[ticket_gen] QR generation failed: {e}")
        return None


# ============================================================================
# MAIN GENERATOR
# ============================================================================

def generate_ticket_image(ticket, force=None):
    """
    Render one ticket and always overwrite any existing PNG.

    Returns:
        /assets/tickets/<ticket-id>.png
    or None if generation fails.
    """
    if force is None:
        force = REGENERATE_ON_EACH_CALL

    if not ticket:
        return None
    if not getattr(ticket, "id", None):
        return None

    output_filename = f"{ticket.id}.png"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    if not force and os.path.exists(output_path):
        return f"/assets/tickets/{output_filename}"

    ticket_type = getattr(ticket, "ticket_type", None)
    match = getattr(ticket, "match", None)
    if not ticket_type or not match:
        return None

    ticket_type_name = getattr(ticket_type, "name", "")
    category = _ticket_category(ticket_type_name)
    theme = THEME[category]
    layout = _layout_for(category)

    # ------------------------------------------------------------------
    # TEMPLATE
    # ------------------------------------------------------------------

    template_path = _template_path_for(ticket_type_name)
    if not template_path:
        print(f"[ticket_gen] No template for '{ticket_type_name}'")
        return None

    try:
        original = Image.open(template_path).convert("RGBA")
    except Exception as e:
        print(f"[ticket_gen] Cannot open template {template_path}: {e}")
        return None

    # `original` is used ONLY for background sampling.
    # `base` is the working image we draw on.
    base = original.copy()
    width, height = base.size
    draw = ImageDraw.Draw(base)

    # ------------------------------------------------------------------
    # TEAMS
    # ------------------------------------------------------------------

    home_name, home_img_src = _resolve_team(
        getattr(match, "home_team_id", None)
    )
    away_name, away_img_src = _resolve_team(
        getattr(match, "away_team_id", None)
    )

    home_center = _point(layout["home_flag_center"], width, height)
    away_center = _point(layout["away_flag_center"], width, height)
    flag_diameter = _ss(layout["flag_diameter"], width)

    home_flag = (
        _load_image(home_img_src, (flag_diameter, flag_diameter))
        if home_img_src else None
    )
    away_flag = (
        _load_image(away_img_src, (flag_diameter, flag_diameter))
        if away_img_src else None
    )

    if home_flag:
        _paste_circular(base, home_flag, home_center, flag_diameter)
    if away_flag:
        _paste_circular(base, away_flag, away_center, flag_diameter)

    draw = ImageDraw.Draw(base)

    # ------------------------------------------------------------------
    # TEAM NAMES
    # ------------------------------------------------------------------

    team_font = _get_font(_ss(32, width), bold=True)
    team_max_width = _ss(layout["team_name_max_width"], width)

    home_name_center = _point(layout["home_name_center"], width, height)
    away_name_center = _point(layout["away_name_center"], width, height)

    home_name_fill = _resolve_fill(theme["team"], original, home_name_center)
    away_name_fill = _resolve_fill(theme["team"], original, away_name_center)

    team_stroke = theme.get("team_stroke")

    _draw_centered(
        draw, home_name, home_name_center, team_font, home_name_fill,
        max_width=team_max_width,
        stroke_width=_ss(2, width) if team_stroke else 0,
        stroke_fill=team_stroke,
    )
    _draw_centered(
        draw, away_name, away_name_center, team_font, away_name_fill,
        max_width=team_max_width,
        stroke_width=_ss(2, width) if team_stroke else 0,
        stroke_fill=team_stroke,
    )

    # ------------------------------------------------------------------
    # MATCH INFORMATION
    # ------------------------------------------------------------------

    value_font = _get_font(_ss(25, width), bold=True)
    value_max_width = _ss(layout["match_value_max_width"], width)

    date_center = _point(layout["date_center"], width, height)
    time_center = _point(layout["time_center"], width, height)
    venue_center = _point(layout["venue_center"], width, height)

    date_fill = _resolve_fill(theme["value"], original, date_center)
    time_fill = _resolve_fill(theme["value"], original, time_center)
    venue_fill = _resolve_fill(theme["value"], original, venue_center)

    _draw_centered(
        draw, _format_date(getattr(match, "match_date", None)),
        date_center, value_font, date_fill, max_width=value_max_width,
    )
    _draw_centered(
        draw, _format_time(getattr(match, "match_date", None)),
        time_center, value_font, time_fill, max_width=value_max_width,
    )
    _draw_centered(
        draw, _clean_value(getattr(match, "venue", None)),
        venue_center, value_font, venue_fill, max_width=value_max_width,
    )

    # ------------------------------------------------------------------
    # TICKET NUMBER -> SHORT CODE
    # ------------------------------------------------------------------

    raw_ticket = _raw_ticket_number(ticket)
    encoded_ticket = _encode_ticket_number(raw_ticket)

    # ------------------------------------------------------------------
    # QR CODE
    # ------------------------------------------------------------------

    qr_payload = _qr_payload(encoded_ticket)

    qr_img = _generate_qr(
        qr_payload,
        fill_color=theme["qr_fill"],
        back_color=theme["qr_back"],
    )

    if qr_img is not None:
        qx1 = _sx(layout["qr_box"][0], width)
        qy1 = _sy(layout["qr_box"][1], height)
        qx2 = _sx(layout["qr_box"][2], width)
        qy2 = _sy(layout["qr_box"][3], height)

        side = max(20, min(qx2 - qx1, qy2 - qy1))
        qr_img = qr_img.resize((side, side), RESAMPLE_FILTER)

        pad = _ss(7, width)
        draw.rectangle(
            (qx1 - pad, qy1 - pad, qx1 + side + pad, qy1 + side + pad),
            fill=(255, 255, 255, 255),
        )
        base.paste(qr_img, (qx1, qy1), qr_img)
        draw = ImageDraw.Draw(base)

    # ------------------------------------------------------------------
    # STUB VALUES
    # ------------------------------------------------------------------

    stub_font = _get_font(_ss(21, width), bold=True)
    stub_max_width = _ss(layout["stub_value_max_width"], width)

    section = _first_attr(ticket, "section")
    row = _first_attr(ticket, "row")
    seat = _first_attr(ticket, "seat")

    if section is None:
        section = _first_attr(
            getattr(ticket, "order_item", None), "section"
        )
    if row is None:
        row = _first_attr(
            getattr(ticket, "order_item", None), "row"
        )
    if seat is None:
        seat = _first_attr(
            getattr(ticket, "order_item", None), "seat"
        )

    section_center = _point(layout["section_center"], width, height)
    row_center = _point(layout["row_center"], width, height)
    seat_center = _point(layout["seat_center"], width, height)
    ticket_no_center = _point(layout["ticket_no_center"], width, height)

    section_fill = _resolve_fill(
        theme["stub_value"], original, section_center
    )
    row_fill = _resolve_fill(theme["stub_value"], original, row_center)
    seat_fill = _resolve_fill(
        theme["stub_value"], original, seat_center
    )
    stub_ticket_fill = _resolve_fill(
        theme["stub_value"], original, ticket_no_center
    )

    _draw_centered(
        draw, _clean_value(section), section_center,
        stub_font, section_fill, max_width=stub_max_width,
    )
    _draw_centered(
        draw, _clean_value(row), row_center,
        stub_font, row_fill, max_width=stub_max_width,
    )
    _draw_centered(
        draw, _clean_value(seat), seat_center,
        stub_font, seat_fill, max_width=stub_max_width,
    )

    # Stub ticket number (short code).
    _draw_centered(
        draw, encoded_ticket, ticket_no_center,
        stub_font, stub_ticket_fill, max_width=stub_max_width,
    )

    # ------------------------------------------------------------------
    # SECOND TICKET NUMBER (BOTTOM)
    # ------------------------------------------------------------------

    bottom_center = _point(
        layout["bottom_ticket_number_center"], width, height
    )
    bottom_fill = _resolve_fill(
        theme["ticket_number"], original, bottom_center
    )
    bottom_font = _get_font(_ss(23, width), bold=True)

    _draw_centered(
        draw, encoded_ticket, bottom_center, bottom_font, bottom_fill,
        max_width=_ss(
            layout["bottom_ticket_number_max_width"], width
        ),
    )

    # ------------------------------------------------------------------
    # SAVE (always replace)
    # ------------------------------------------------------------------

    if os.path.exists(output_path):
        try:
            os.remove(output_path)
        except Exception:
            pass

    try:
        base.convert("RGB").save(output_path, "PNG", optimize=True)
    except Exception as e:
        print(f"[ticket_gen] Cannot save {output_path}: {e}")
        return None

    return f"/assets/tickets/{output_filename}"


# ============================================================================
# ORDER GENERATOR
# ============================================================================

def generate_order_tickets(order, force=None):
    """
    Generate images for every ticket in an order.
    Returns { ticket_id: public_url }.
    """
    if force is None:
        force = REGENERATE_ON_EACH_CALL

    result = {}
    for item in (getattr(order, "items", None) or []):
        for ticket in (getattr(item, "tickets", None) or []):
            url = generate_ticket_image(ticket, force=force)
            if url:
                result[str(ticket.id)] = url
    return result