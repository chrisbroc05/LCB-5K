"""
generate_event_day_graphics.py — Event-day raffle & sponsor signage for LCB 5K 2026.

Layout matches last year's donor flyers (DonationCompanies_InfoforEvent.py):
dark purple-to-black gradient, bright purple border, centered white type, logo with shadow.
No long donor description. Includes ticket-bag drop zone for raffles.

Outputs high-res PNG + PDF to event-day-graphics/
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from difflib import get_close_matches
from typing import Sequence

from PIL import Image, ImageDraw, ImageFilter, ImageFont

# --- Last-year flyer theme (DonationCompanies_InfoforEvent.py) ---
THEME = {
    "size": (1080, 1350),
    "bg_top": (40, 0, 60),
    "bg_bottom": (0, 0, 0),
    "text": (255, 255, 255),
    "text_muted": (200, 190, 210),
    "border": (180, 0, 255),
    "logo_shadow": (0, 0, 0, 150),
    "padding": 80,
    "border_width": 12,
}

FEATURED_ACCENT = (255, 215, 120)
FEATURED_BORDER_WIDTH = 20

ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(ROOT, "event-day-graphics")
LOGO_DIR = os.path.join(ROOT, "In-Kind Donations", "Sponsors")
FONTS = {
    "bold": os.path.join(ROOT, "fonts", "Montserrat-Bold.ttf"),
    "regular": os.path.join(ROOT, "fonts", "Montserrat-Regular.ttf"),
}
LCB_LOGO_CANDIDATES = [
    os.path.join(ROOT, "website", "assets", "images", "lcb-logo.png"),
    os.path.join(ROOT, "static", "LCB 5K logo.png"),
]

DPI = 300

LOGO_SEARCH_DIRS = [
    LOGO_DIR,
    os.path.join(ROOT, "website", "assets", "images", "sponsors"),
    os.path.join(ROOT, "static"),
    ROOT,
]

PLACEHOLDERS: list[str] = []


@dataclass
class RaffleItem:
    slug: str
    donor: str
    prize: str
    logo_hints: Sequence[str] = field(default_factory=list)
    location: str = ""
    sample_note: str = ""
    sample_detail: str = ""
    discount_code: str = ""
    discount_note: str = ""


STANDARD_RAFFLES = [
    RaffleItem("raffle-01-townhouse-cafe", "TownHouse Books & Cafe", "$30 gift card", ["TownHouseLogo.png"]),
    RaffleItem(
        "raffle-02-woodies-flat",
        "Woodie's Flat",
        "$50 gift card",
        ["WoodiesFlatLogo.png"],
        location="Located in Chicago (Old Town)",
    ),
    RaffleItem(
        "raffle-03-kala-modern-greek",
        "KALA Modern Greek",
        "$100 digital gift card (winner will receive via email)",
        ["KALAModernGreekLogo.png"],
        location="Located in Chicago",
    ),
    RaffleItem(
        "raffle-04-goebberts-farm",
        "Goebbert's Farm (South Barrington)",
        "Fall Family Day for 4 — $250 value. Includes: 4 entry tickets, 4 pumpkins, "
        "4 animal ride tickets, $50 in food dollars",
        ["GoebbertsLogo.png"],
    ),
    RaffleItem(
        "raffle-05-ocean-prime",
        "Ocean Prime",
        "$200 gift card",
        ["OceanPrimeLogo.png"],
        location="Located in Chicago",
    ),
    RaffleItem(
        "raffle-06-amrin-custom-art",
        "Amrin Mathews",
        "Free custom art piece",
        ["AmrinCustomArtLogo1.jpg", "AmrinCustomArtLogo2.jpg"],
    ),
    RaffleItem(
        "raffle-07-coopers-hawk",
        "Cooper's Hawk",
        "Lux Wine Tasting for 4, plus 2 bonus bottles of wine",
        ["CoopersHawkLogo.jpeg"],
    ),
    RaffleItem(
        "raffle-08-energy-product-basket",
        "Energy Product Basket",
        "Energy Product Basket (electrolyte drink mixes, energy gum, energy gels/chews)",
        [
            "FamilyReachLogo.png",
            "LiquidIVLogo.png",
            "LMNTLogo.png",
            "NeuroGumLogo.png",
            "GULogo.png",
        ],
    ),
    RaffleItem(
        "raffle-09-schaumburg-boomers",
        "Schaumburg Boomers",
        "4 home Schaumburg Boomers tickets for the 2027 season",
        ["BoomersLogo.jpeg"],
    ),
    RaffleItem(
        "raffle-10-city-winery",
        "City Winery",
        "Winery Tour & Tasting for 4 — $200 value (certificate)",
        ["CityWineryLogo.png"],
        location="Located in Chicago",
    ),
    RaffleItem(
        "raffle-11-il-porcellino",
        "IL Porcellino",
        "$100 gift card",
        ["ILPorcellinoLogo.png"],
        location="Located in Chicago",
    ),
    RaffleItem(
        "raffle-12-schaumburg-high-school",
        "Schaumburg High School",
        "SHS Apparel & Gear Haul (shirts, hats, and more)",
        ["SHSLogo.jpeg"],
    ),
    RaffleItem(
        "raffle-13-wildfire",
        "Wildfire",
        "$200 gift card",
        ["WildfireLogo.png"],
        location="Located in Schaumburg",
    ),
    RaffleItem(
        "raffle-14-blumaka",
        "Blumaka",
        "Free pair of insoles",
        ["BlumakaLogo.png"],
        sample_note="Try a sample!",
        sample_detail="Physical sample product on display here",
        discount_code="LCB20",
        discount_note="Use on their website for a discounted purchase.",
    ),
]

FEATURED_RAFFLE = RaffleItem(
    "featured-bears-tickets",
    "Dennis L. Marach, C.P.A.",
    "4 Chicago Bears tickets — Bears vs. Detroit Lions, January 3rd, 3:25 PM",
    ["ChicagoBearsLogo2.png", "ChicagoBearsLogo.jpg", "ChicagoBearsLogo.jpeg"],
)

SPONSOR_TIERS = [
    ("Community Sponsors", [("Chicago Air Cargo", "ChicagoAirCargoLogo.png")]),
    ("Supporting Sponsors", [("Home Doctors For You, LLC", "HomeDoctorsForYouLogo.png")]),
]

# Per-raffle logo scale boost (1.0 = default auto-fit)
LOGO_SCALE: dict[str, float] = {
    "raffle-07-coopers-hawk": 1.18,
}

# Per-slug upscale targets (inner px) for small or wide source assets
LOGO_TARGET_INNER: dict[str, tuple[int, int]] = {
    "raffle-01-townhouse-cafe": (428, 428),  # match Woodie's Flat
    "raffle-04-goebberts-farm": (827, 400),  # wide logo — fill width, taller height
    "raffle-09-schaumburg-boomers": (428, 428),
    "raffle-13-wildfire": (827, 400),  # wide logo — fill width, taller height
    "raffle-14-blumaka": (827, 400),
    "featured-bears-tickets": (456, 450),  # max fit in featured card logo band
}


def load_font(kind: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONTS[kind], size)


def create_gradient(size, top_color, bottom_color):
    base = Image.new("RGB", size, top_color)
    top = Image.new("RGB", size, bottom_color)
    mask = Image.linear_gradient("L").resize(size)
    return Image.composite(base, top, mask)


def text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    return draw.textbbox((0, 0), text, font=font)[2]


def wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        if text_width(draw, test, font) > max_width:
            if current:
                lines.append(current)
            current = word
        else:
            current = test
    if current:
        lines.append(current)
    return lines or [text]


def draw_text_centered(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    y: int,
    image_width: int,
    fill,
    max_width: int | None = None,
    line_gap: int = 20,
) -> int:
    lines = wrap_text(draw, text, font, max_width) if max_width else [text]

    for line in lines:
        tw = text_width(draw, line, font)
        draw.text(((image_width - tw) // 2, y), line, font=font, fill=fill)
        y += draw.textbbox((0, 0), line, font=font)[3] + line_gap
    return y


def normalize_key(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def all_logo_files() -> dict[str, str]:
    found: dict[str, str] = {}
    for directory in LOGO_SEARCH_DIRS:
        if not os.path.isdir(directory):
            continue
        for entry in os.listdir(directory):
            if not entry.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                continue
            path = os.path.join(directory, entry)
            found[normalize_key(entry)] = path
            found[normalize_key(os.path.splitext(entry)[0])] = path
    return found


LOGO_INDEX = all_logo_files()


def find_logo(hint: str) -> str | None:
    candidate = os.path.join(LOGO_DIR, hint)
    if os.path.exists(candidate):
        return candidate
    for directory in LOGO_SEARCH_DIRS:
        if directory == LOGO_DIR:
            continue
        path = os.path.join(directory, hint)
        if os.path.exists(path):
            return path
    stem = normalize_key(os.path.splitext(hint)[0])
    # Fuzzy match only within sponsor logo folder to avoid wrong static/ assets
    if os.path.isdir(LOGO_DIR):
        local_keys = {
            normalize_key(entry): os.path.join(LOGO_DIR, entry)
            for entry in os.listdir(LOGO_DIR)
            if entry.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
        }
        if stem in local_keys:
            return local_keys[stem]
        match = get_close_matches(stem, list(local_keys.keys()), n=1, cutoff=0.72)
        if match:
            return local_keys[match[0]]
    if stem in LOGO_INDEX and LOGO_DIR in LOGO_INDEX[stem]:
        return LOGO_INDEX[stem]
    return None


def resolve_logo_paths(hints: Sequence[str], donor: str, *, single: bool = False) -> list[str]:
    paths: list[str] = []
    for hint in hints:
        path = find_logo(hint)
        if path:
            paths.append(path)
            if single:
                break
        else:
            PLACEHOLDERS.append(f"{donor}: requested '{hint}' — no match found")
    return paths


LOGO_PAD = 28


def resize_logo_to_fit(
    logo: Image.Image,
    max_inner: tuple[int, int],
    *,
    allow_upscale: bool = False,
) -> Image.Image:
    w, h = logo.size
    mw, mh = max_inner
    scale = min(mw / w, mh / h)
    if not allow_upscale:
        scale = min(1.0, scale)
    nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
    if (nw, nh) == logo.size:
        return logo
    return logo.resize((nw, nh), Image.Resampling.LANCZOS)


def logo_box_dimensions(
    path: str,
    max_inner: tuple[int, int],
    *,
    allow_upscale: bool = False,
) -> tuple[int, int, int, int]:
    """Return inner_w, inner_h, box_w, box_h for a logo scaled into max_inner bounds."""
    logo = Image.open(path).convert("RGBA")
    logo = resize_logo_to_fit(logo, max_inner, allow_upscale=allow_upscale)
    box_w = logo.width + LOGO_PAD * 2
    box_h = logo.height + LOGO_PAD * 2
    return logo.width, logo.height, box_w, box_h


def draw_logo_with_shadow(
    img: Image.Image,
    logo_path: str,
    center_x: int,
    y: int,
    logo_size: tuple[int, int],
    shadow_offset: int = 10,
):
    logo = Image.open(logo_path).convert("RGBA")
    logo = resize_logo_to_fit(logo, logo_size, allow_upscale=True)

    pad = LOGO_PAD
    box_w = logo.width + pad * 2
    box_h = logo.height + pad * 2
    box_x = center_x - box_w // 2
    box_y = y
    draw = ImageDraw.Draw(img)
    draw.rectangle((box_x, box_y, box_x + box_w, box_y + box_h), fill=(0, 0, 0))

    paste_y = box_y + pad
    shadow = Image.new("RGBA", logo.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rectangle([0, 0, logo.width, logo.height], fill=THEME["logo_shadow"])
    shadow = shadow.filter(ImageFilter.GaussianBlur(8))
    img.paste(
        shadow,
        (center_x - logo.width // 2 + shadow_offset, paste_y + shadow_offset),
        shadow,
    )
    img.paste(logo, (center_x - logo.width // 2, paste_y), logo)
    return box_h


def draw_logo_placeholder_block(
    draw: ImageDraw.ImageDraw,
    img: Image.Image,
    center_x: int,
    y: int,
    width: int,
    height: int,
    label: str,
):
    x0 = center_x - width // 2
    box = (x0, y, x0 + width, y + height)
    draw.rectangle(box, outline=THEME["border"], width=3)
    font = load_font("bold", 32)
    draw_text_centered(draw, "LOGO PLACEHOLDER", font, y + 30, img.width, THEME["text_muted"])
    draw_text_centered(draw, label, load_font("regular", 28), y + 80, img.width, THEME["text"], max_width=width - 40)
    return height


def draw_border(draw: ImageDraw.ImageDraw, width: int, height: int, featured: bool = False):
    bw = FEATURED_BORDER_WIDTH if featured else THEME["border_width"]
    color = FEATURED_ACCENT if featured else THEME["border"]
    draw.rectangle(
        [bw // 2, bw // 2, width - bw // 2, height - bw // 2],
        outline=color,
        width=bw,
    )
    if featured:
        inset = bw + 10
        draw.rectangle(
            [inset, inset, width - inset, height - inset],
            outline=THEME["border"],
            width=4,
        )


def drop_label_height(featured: bool = False) -> int:
    font = load_font("bold", 34 if featured else 30)
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    return probe.textbbox((0, 0), "DROP YOUR TICKETS HERE", font=font)[3]


def raffle_footer_height(item: RaffleItem, featured: bool = False) -> int:
    """Total vertical space reserved above the bottom padding for drop + extras."""
    drop_lh = drop_label_height(featured)
    h = drop_lh + 36
    if item.discount_code:
        h += 82
    return h


def sample_note_height() -> int:
    """Space reserved beneath the logo for a centered sample callout."""
    return 52


def draw_ticket_drop_label(
    draw: ImageDraw.ImageDraw,
    width: int,
    height: int,
    featured: bool = False,
) -> int:
    pad = THEME["padding"]
    label_font = load_font("bold", 34 if featured else 30)
    lh = drop_label_height(featured)
    y = height - pad - lh - 6
    draw_text_centered(draw, "DROP YOUR TICKETS HERE", label_font, y, width, THEME["text"])
    return y


def draw_text_in_box(
    draw: ImageDraw.ImageDraw,
    lines: Sequence[str],
    fonts: Sequence[ImageFont.FreeTypeFont],
    box: tuple[int, int, int, int],
    colors: Sequence[tuple[int, int, int]],
    *,
    line_gap: int = 6,
):
    x0, y0, x1, y1 = box
    cx = (x0 + x1) // 2
    max_w = x1 - x0 - 16
    total_h = 0
    line_metrics: list[tuple[str, ImageFont.FreeTypeFont, tuple[int, int, int], int]] = []
    for text, font, color in zip(lines, fonts, colors):
        if not text:
            continue
        wrapped = wrap_text(draw, text, font, max_w) if text_width(draw, text, font) > max_w else [text]
        for segment in wrapped:
            bbox = draw.textbbox((0, 0), segment, font=font)
            seg_h = bbox[3] - bbox[1]
            line_metrics.append((segment, font, color, seg_h))
            total_h += seg_h + line_gap
    if line_metrics:
        total_h -= line_gap
    y = y0 + max(0, (y1 - y0 - total_h) // 2)
    for segment, font, color, seg_h in line_metrics:
        tw = text_width(draw, segment, font)
        draw.text((cx - tw // 2, y), segment, font=font, fill=color)
        y += seg_h + line_gap


def draw_raffle_footer(
    draw: ImageDraw.ImageDraw,
    width: int,
    height: int,
    item: RaffleItem,
    featured: bool = False,
) -> None:
    pad = THEME["padding"]
    drop_font = load_font("bold", 34 if featured else 30)
    drop_text = "DROP YOUR TICKETS HERE"
    drop_lh = drop_label_height(featured)
    drop_y = height - pad - 6 - drop_lh
    content_bottom = drop_y - 20

    if item.discount_code:
        code_font = load_font("bold", 38)
        note_font = load_font("regular", 26)
        note = item.discount_note or "Use on their website for a discounted purchase."
        note_lines = wrap_text(draw, note, note_font, width - 2 * pad)
        note_lh = draw.textbbox((0, 0), "Ag", font=note_font)[3]
        note_block_h = len(note_lines) * (note_lh + 8) - 8
        code_lh = draw.textbbox((0, 0), "Ag", font=code_font)[3]
        discount_block_h = code_lh + 8 + note_block_h
        discount_y = content_bottom - discount_block_h
        draw_text_centered(
            draw,
            f"Use code {item.discount_code}",
            code_font,
            discount_y,
            width,
            THEME["border"],
        )
        note_y = discount_y + code_lh + 8
        for line in note_lines:
            tw = text_width(draw, line, note_font)
            draw.text(((width - tw) // 2, note_y), line, font=note_font, fill=THEME["text_muted"])
            note_y += note_lh + 8

    tw = text_width(draw, drop_text, drop_font)
    draw.text(((width - tw) // 2, drop_y), drop_text, font=drop_font, fill=THEME["text"])


def plan_energy_basket_layout(logo_paths: list[str], area_w: int, area_h: int) -> dict:
    """Family Reach large on top, other four in a 2×2 grid below."""
    gap, row_gap = 16, 18
    max_w = int(area_w * 0.96)

    top_share = 0.48
    top_h = int(area_h * top_share)
    bottom_h = area_h - top_h - row_gap

    fr_inner = (max_w - LOGO_PAD * 2, top_h - LOGO_PAD * 2)
    fr_iw, fr_ih, _, fr_box_h = logo_box_dimensions(logo_paths[0], fr_inner)

    cell_inner_w = max(90, (max_w - gap) // 2 - LOGO_PAD * 2)
    cell_inner_h = max(70, (bottom_h - row_gap) // 2 - LOGO_PAD * 2)
    small_dims = [logo_box_dimensions(p, (cell_inner_w, cell_inner_h)) for p in logo_paths[1:5]]
    cell_box_w = max(d[2] for d in small_dims)
    cell_box_h = max(d[3] for d in small_dims)
    small_inners = [(d[0], d[1]) for d in small_dims]

    grid_h = 2 * cell_box_h + row_gap
    total_h = fr_box_h + row_gap + grid_h
    y_offset = max(0, (area_h - total_h) // 2)

    return {
        "mode": "energy_basket",
        "y_offset": y_offset,
        "fr_inner": (fr_iw, fr_ih),
        "fr_box_h": fr_box_h,
        "row_gap": row_gap,
        "gap": gap,
        "cell_box_w": cell_box_w,
        "cell_box_h": cell_box_h,
        "small_inners": small_inners,
    }


def plan_logo_layout(
    logo_paths: list[str],
    area_w: int,
    area_h: int,
    *,
    multi_grid: bool = False,
    dual: bool = False,
    energy_basket: bool = False,
    scale: float = 1.0,
    target_inner: tuple[int, int] | None = None,
) -> dict:
    """Size logos to fill the middle band and center them vertically."""
    if energy_basket and len(logo_paths) >= 5:
        return plan_energy_basket_layout(logo_paths, area_w, area_h)

    fill = min(0.99, 0.96 * scale)
    max_w = int(area_w * fill)
    max_h = int(area_h * fill)

    if not logo_paths:
        ph_h = min(260, max_h)
        return {"mode": "placeholder", "y_offset": (area_h - ph_h) // 2, "ph_h": ph_h}

    if multi_grid and len(logo_paths) > 1:
        cols = 3 if len(logo_paths) > 3 else len(logo_paths)
        rows = (len(logo_paths) + cols - 1) // cols
        gap, row_gap = 14, 18
        cell_inner_w = max(70, (max_w - (cols - 1) * gap) // cols - LOGO_PAD * 2)
        cell_inner_h = max(55, (max_h - (rows - 1) * row_gap) // rows - LOGO_PAD * 2)

        box_sizes = [logo_box_dimensions(p, (cell_inner_w, cell_inner_h)) for p in logo_paths]
        cell_box_w = max(b[2] for b in box_sizes)
        cell_box_h = max(b[3] for b in box_sizes)
        inner_sizes = [(cell_box_w - LOGO_PAD * 2, cell_box_h - LOGO_PAD * 2)] * len(logo_paths)

        grid_w = cols * cell_box_w + (cols - 1) * gap
        grid_h = rows * cell_box_h + (rows - 1) * row_gap
        return {
            "mode": "grid",
            "y_offset": max(0, (area_h - grid_h) // 2),
            "cols": cols,
            "gap": gap,
            "row_gap": row_gap,
            "cell_box_w": cell_box_w,
            "cell_box_h": cell_box_h,
            "inner_sizes": inner_sizes,
        }

    if dual and len(logo_paths) >= 2:
        spacing = 28
        half_inner_w = max(80, (max_w - spacing) // 2 - LOGO_PAD * 2)
        inner = (half_inner_w, max_h - LOGO_PAD * 2)
        dims = [logo_box_dimensions(p, inner) for p in logo_paths[:2]]
        box_w = [d[2] for d in dims]
        box_h = max(d[3] for d in dims)
        inner_sizes = [(dims[i][0], dims[i][1]) for i in range(2)]
        block_w = box_w[0] + spacing + box_w[1]
        return {
            "mode": "dual",
            "y_offset": max(0, (area_h - box_h) // 2),
            "spacing": spacing,
            "inner_sizes": inner_sizes,
            "box_w": box_w,
            "box_h": box_h,
            "block_w": block_w,
        }

    inner = (max_w - LOGO_PAD * 2, max_h - LOGO_PAD * 2)
    allow_upscale = False
    if target_inner:
        inner = (
            min(inner[0], target_inner[0]),
            min(inner[1], target_inner[1]),
        )
        allow_upscale = True
    _, _, box_w, box_h = logo_box_dimensions(logo_paths[0], inner, allow_upscale=allow_upscale)
    return {
        "mode": "single",
        "y_offset": max(0, (area_h - box_h) // 2),
        "inner_size": (box_w - LOGO_PAD * 2, box_h - LOGO_PAD * 2),
    }


def draw_logos_section(
    img: Image.Image,
    draw: ImageDraw.ImageDraw,
    logo_paths: list[str],
    donor: str,
    center_x: int,
    area_top: int,
    layout: dict,
) -> int:
    y = area_top + layout.get("y_offset", 0)

    if layout["mode"] == "placeholder":
        ph_h = layout["ph_h"]
        ph_w = min(420, img.width - 2 * THEME["padding"])
        return y + draw_logo_placeholder_block(draw, img, center_x, y, ph_w, ph_h, donor)

    if layout["mode"] == "energy_basket":
        y_top = y
        cx = center_x
        fr_h = draw_logo_with_shadow(img, logo_paths[0], cx, y_top, layout["fr_inner"])
        y_grid = y_top + layout["fr_box_h"] + layout["row_gap"]
        gap = layout["gap"]
        row_gap = layout["row_gap"]
        cell_box_w = layout["cell_box_w"]
        cell_box_h = layout["cell_box_h"]
        grid_w = 2 * cell_box_w + gap
        start_x = cx - grid_w // 2
        max_bottom = y_grid
        for idx, path in enumerate(logo_paths[1:5]):
            r, c = divmod(idx, 2)
            cell_cx = start_x + c * (cell_box_w + gap) + cell_box_w // 2
            cell_y = y_grid + r * (cell_box_h + row_gap)
            h = draw_logo_with_shadow(img, path, cell_cx, cell_y, layout["small_inners"][idx])
            max_bottom = max(max_bottom, cell_y + h)
        return max_bottom

    if layout["mode"] == "grid":
        cols = layout["cols"]
        gap = layout["gap"]
        row_gap = layout["row_gap"]
        cell_box_w = layout["cell_box_w"]
        cell_box_h = layout["cell_box_h"]
        grid_w = cols * cell_box_w + (cols - 1) * gap
        start_x = center_x - grid_w // 2
        max_bottom = y
        for idx, path in enumerate(logo_paths):
            r, c = divmod(idx, cols)
            cx = start_x + c * (cell_box_w + gap) + cell_box_w // 2
            cy = y + r * (cell_box_h + row_gap)
            inner = layout["inner_sizes"][idx]
            h = draw_logo_with_shadow(img, path, cx, cy, inner)
            max_bottom = max(max_bottom, cy + h)
        return max_bottom

    if layout["mode"] == "dual":
        spacing = layout["spacing"]
        block_w = layout["block_w"]
        left_cx = center_x - block_w // 2 + layout["box_w"][0] // 2
        right_cx = center_x + block_w // 2 - layout["box_w"][1] // 2
        h1 = draw_logo_with_shadow(img, logo_paths[0], left_cx, y, layout["inner_sizes"][0])
        h2 = draw_logo_with_shadow(img, logo_paths[1], right_cx, y, layout["inner_sizes"][1])
        return y + max(h1, h2)

    inner = layout["inner_size"]
    h = draw_logo_with_shadow(img, logo_paths[0], center_x, y, inner)
    return y + h


def build_raffle_card(item: RaffleItem, featured: bool = False) -> Image.Image:
    width, height = THEME["size"]
    img = create_gradient((width, height), THEME["bg_top"], THEME["bg_bottom"])
    draw = ImageDraw.Draw(img)
    pad = THEME["padding"]
    max_text = width - 2 * pad
    cx = width // 2

    y = pad

    if featured:
        banner_font = load_font("bold", 38)
        y = draw_text_centered(draw, "FEATURED RAFFLE", banner_font, y, width, FEATURED_ACCENT)
        y += 20
        sub_font = load_font("regular", 26)
        y = draw_text_centered(draw, "Provided by", sub_font, y, width, THEME["text_muted"])
        y += 8

    name_font = load_font("bold", 88 if featured else 72)
    y = draw_text_centered(draw, item.donor, name_font, y, width, THEME["text"], max_width=max_text, line_gap=14)
    y += 36 if featured else 28

    prize_font = load_font("bold", 58 if featured else 48)
    y = draw_text_centered(draw, item.prize, prize_font, y, width, THEME["text"], max_width=max_text, line_gap=16)

    if item.location:
        y += 10
        loc_font = load_font("regular", 32 if featured else 28)
        y = draw_text_centered(
            draw,
            item.location,
            loc_font,
            y,
            width,
            THEME["text_muted"],
            max_width=max_text,
            line_gap=12,
        )

    energy_basket = item.slug == "raffle-08-energy-product-basket"
    dual = item.slug == "raffle-06-amrin-custom-art"
    logo_paths = resolve_logo_paths(item.logo_hints, item.donor, single=featured)
    if not energy_basket and not dual and logo_paths:
        logo_paths = logo_paths[:1]

    footer_h = raffle_footer_height(item, featured)
    sample_h = sample_note_height() if item.sample_note else 0
    logo_area_top = y + 20
    logo_area_bottom = height - pad - footer_h
    logo_area_h = max(200, logo_area_bottom - logo_area_top - sample_h)
    logo_area_w = width - 2 * pad
    logo_scale = LOGO_SCALE.get(item.slug, 1.0)
    target_inner = LOGO_TARGET_INNER.get(item.slug)

    layout = plan_logo_layout(
        logo_paths,
        logo_area_w,
        logo_area_h,
        multi_grid=False,
        dual=dual,
        energy_basket=energy_basket,
        scale=logo_scale,
        target_inner=target_inner,
    )
    logo_bottom = draw_logos_section(img, draw, logo_paths, item.donor, cx, logo_area_top, layout)
    if item.sample_note:
        sample_y = logo_bottom + 14
        draw_text_centered(
            draw,
            item.sample_note,
            load_font("bold", 30),
            sample_y,
            width,
            THEME["border"],
        )
    if item.sample_note or item.discount_code:
        draw_raffle_footer(draw, width, height, item, featured=featured)
    else:
        draw_ticket_drop_label(draw, width, height, featured=featured)
    draw_border(draw, width, height, featured=featured)
    return img


def build_sponsor_graphic() -> Image.Image:
    width, height = THEME["size"]
    img = create_gradient((width, height), THEME["bg_top"], THEME["bg_bottom"])
    draw = ImageDraw.Draw(img)
    pad = THEME["padding"]

    y = pad
    y = draw_text_centered(draw, "OUR SPONSORS", load_font("bold", 72), y, width, THEME["text"])
    y += 12
    y = draw_text_centered(
        draw,
        "LCB 5K 2026",
        load_font("regular", 32),
        y,
        width,
        THEME["text_muted"],
    )
    y += 8
    y = draw_text_centered(
        draw,
        "Thank you for supporting families facing cancer",
        load_font("regular", 28),
        y,
        width,
        THEME["text_muted"],
        max_width=width - 2 * pad,
    )
    y += 48

    cols = 2
    card_w = (width - 2 * pad - 24) // cols
    card_h = 260

    for tier_name, sponsors in SPONSOR_TIERS:
        tier_font = load_font("bold", 40)
        y = draw_text_centered(draw, tier_name.upper(), tier_font, y, width, THEME["border"])
        y += 36

        row_start = y
        gap = 24
        for idx, (name, hint) in enumerate(sponsors):
            col = idx % cols
            row = idx // cols
            row_start_idx = row * cols
            n_in_row = min(cols, len(sponsors) - row_start_idx)
            block_w = n_in_row * card_w + (n_in_row - 1) * gap
            row_x_start = (width - block_w) // 2
            x0 = row_x_start + col * (card_w + gap)
            y0 = row_start + row * (card_h + gap)
            x1 = x0 + card_w
            y1 = y0 + card_h
            draw.rectangle((x0, y0, x1, y1), outline=THEME["border"], width=2)

            path = find_logo(hint)
            logo_box_cx = (x0 + x1) // 2
            if path:
                draw_logo_with_shadow(img, path, logo_box_cx, y0 + 24, (card_w - 60, 150))
            else:
                PLACEHOLDERS.append(f"{name}: requested '{hint}' — no match found")
                draw_logo_placeholder_block(draw, img, logo_box_cx, y0 + 24, card_w - 60, 140, name)

            name_font = load_font("bold", 24)
            tw = text_width(draw, name, name_font)
            if tw > card_w - 24:
                name_font = load_font("bold", 20)
                tw = text_width(draw, name, name_font)
            draw.text((x0 + (card_w - tw) // 2, y1 - 44), name, font=name_font, fill=THEME["text"])

        rows = max(1, (len(sponsors) + cols - 1) // cols)
        y = row_start + rows * (card_h + 28) + 40

    note_y = height - pad - 30
    draw_text_centered(
        draw,
        "Additional sponsors may be added to each tier.",
        load_font("regular", 22),
        note_y,
        width,
        THEME["text_muted"],
    )

    draw_border(draw, width, height, featured=False)
    return img


def save_outputs(img: Image.Image, base_path: str):
    os.makedirs(os.path.dirname(base_path), exist_ok=True)
    png_path = f"{base_path}.png"
    pdf_path = f"{base_path}.pdf"
    img.save(png_path, "PNG", dpi=(DPI, DPI))
    img.convert("RGB").save(pdf_path, "PDF", resolution=DPI)
    print(f"  ✓ {os.path.basename(png_path)}")
    print(f"  ✓ {os.path.basename(pdf_path)}")


def main():
    global PLACEHOLDERS
    PLACEHOLDERS = []
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Generating event-day graphics (last-year flyer style) → {OUTPUT_DIR}/\n")

    print("Standard raffles:")
    for item in STANDARD_RAFFLES:
        save_outputs(build_raffle_card(item), os.path.join(OUTPUT_DIR, item.slug))

    print("\nFeatured raffle:")
    save_outputs(build_raffle_card(FEATURED_RAFFLE, featured=True), os.path.join(OUTPUT_DIR, FEATURED_RAFFLE.slug))

    print("\nSponsor graphic:")
    save_outputs(build_sponsor_graphic(), os.path.join(OUTPUT_DIR, "sponsor-graphic"))

    total = len(STANDARD_RAFFLES) + 2
    print(f"\n--- Summary ---")
    print(f"Generated {total} graphics ({total * 2} files) at {THEME['size'][0]}×{THEME['size'][1]}px, {DPI} DPI.")
    if PLACEHOLDERS:
        print("\nPlaceholders used:")
        for entry in PLACEHOLDERS:
            print(f"  • {entry}")
    else:
        print("\nAll logos matched — no placeholders needed.")


if __name__ == "__main__":
    main()
