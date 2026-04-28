from PIL import Image, ImageDraw, ImageFont
import os


WIDTH, HEIGHT = 1080, 1350

COLORS = {
    "bg_top": (38, 0, 62),
    "bg_bottom": (8, 8, 14),
    "text": (255, 255, 255),
    "accent": (170, 245, 170),
    "accent_2": (255, 230, 245),
    "card": (235, 225, 255),
    "card_text": (35, 10, 55),
    "shadow": (0, 0, 0),
}

FONTS = {
    "bold": "fonts/Montserrat-Bold.ttf",
    "regular": "fonts/Montserrat-Regular.ttf",
    "slogan": "fonts/BebasNeue-Regular.ttf",
}

ASSETS = {
    "lcb_logo": "static/LCB 5K logo.png",
    "family_reach_logo": "static/family_reach_logo.png",
}

OUTPUT_DIR = "output"


def load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def create_gradient(size, top_color, bottom_color):
    base = Image.new("RGB", size, top_color)
    top = Image.new("RGB", size, bottom_color)
    mask = Image.linear_gradient("L").resize(size)
    return Image.composite(base, top, mask)


def centered_x(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    text_width = draw.textbbox((0, 0), text, font=font)[2]
    return (WIDTH - text_width) // 2


def draw_text_with_shadow(draw, x, y, text, font, fill, shadow=COLORS["shadow"], offset=2):
    draw.text((x + offset, y + offset), text, font=font, fill=shadow)
    draw.text((x, y), text, font=font, fill=fill)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        width = draw.textbbox((0, 0), candidate, font=font)[2]
        if width <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_footer(draw: ImageDraw.ImageDraw, y: int):
    slogan_font = load_font(FONTS["slogan"], 54)
    footer = "Love. Care. Believe."
    x = centered_x(draw, footer, slogan_font)
    draw_text_with_shadow(draw, x, y, footer, slogan_font, COLORS["text"])


def generate_we_are_back():
    img = create_gradient((WIDTH, HEIGHT), COLORS["bg_top"], COLORS["bg_bottom"])
    draw = ImageDraw.Draw(img)

    big_font = load_font(FONTS["bold"], 138)
    medium_font = load_font(FONTS["bold"], 82)
    body_font = load_font(FONTS["regular"], 44)

    title = "WE ARE BACK"
    x = centered_x(draw, title, big_font)
    draw_text_with_shadow(draw, x, 120, title, big_font, COLORS["accent"])

    year_line = "LCB 5K 2026"
    x = centered_x(draw, year_line, medium_font)
    draw_text_with_shadow(draw, x, 280, year_line, medium_font, COLORS["text"])

    lcb_logo = Image.open(ASSETS["lcb_logo"]).convert("RGBA").resize((360, 360), Image.LANCZOS)
    img.paste(lcb_logo, ((WIDTH - 360) // 2, 410), lcb_logo)

    message_lines = [
        "Supporting families facing the",
        "emotional and financial burdens of cancer",
    ]
    current_y = 830
    for line in message_lines:
        x = centered_x(draw, line, body_font)
        draw_text_with_shadow(draw, x, current_y, line, body_font, COLORS["text"])
        current_y += 58

    fr_logo = Image.open(ASSETS["family_reach_logo"]).convert("RGBA").resize((220, 220), Image.LANCZOS)
    img.paste(fr_logo, ((WIDTH - 220) // 2, 980), fr_logo)

    draw_footer(draw, 1248)
    out = os.path.join(OUTPUT_DIR, "we_are_back_2026.png")
    img.save(out, quality=100)
    return out


def generate_save_the_date():
    img = Image.new("RGB", (WIDTH, HEIGHT), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Fonts
    title_font = load_font(FONTS["bold"], 112)
    line_font = load_font(FONTS["bold"], 66)
    date_font = load_font(FONTS["bold"], 70)
    body_font = load_font(FONTS["regular"], 42)
    small_font = load_font(FONTS["regular"], 36)

    # ===== HEADER =====
    header_height = 230
    draw.rectangle([(0, 0), (WIDTH, header_height)], fill=COLORS["bg_top"])

    title = "SAVE THE DATE"
    x = centered_x(draw, title, title_font)
    draw.text((x, 55), title, font=title_font, fill=COLORS["text"])

    # ===== LOGO (CENTERED ABOVE CARD) =====
    lcb_logo = Image.open(ASSETS["lcb_logo"]).convert("RGBA").resize((220, 220), Image.LANCZOS)
    logo_x = (WIDTH - lcb_logo.width) // 2
    logo_y = 240
    img.paste(lcb_logo, (logo_x, logo_y), lcb_logo)

    # ===== MAIN CARD (TALLER + CLEAN) =====
    card_left = 120
    card_right = WIDTH - 120
    card_top = 480
    card_bottom = 930  # ⬆️ taller card

    draw.rounded_rectangle(
        [(card_left, card_top), (card_right, card_bottom)],
        radius=32,
        fill=COLORS["card"],
        outline=COLORS["bg_top"],
        width=5,
    )

    card_center_x = (card_left + card_right) // 2
    y = card_top + 80

    # ===== EVENT TITLE =====
    event_text = "LCB 5K 2026"
    text_width = draw.textbbox((0, 0), event_text, font=line_font)[2]
    draw.text((card_center_x - text_width // 2, y), event_text, font=line_font, fill=COLORS["card_text"])
    y += 110

    # ===== DATE =====
    date_text = "Saturday, October 3rd"
    text_width = draw.textbbox((0, 0), date_text, font=date_font)[2]
    draw.text((card_center_x - text_width // 2, y), date_text, font=date_font, fill=COLORS["card_text"])
    y += 120

    # ===== LOCATION =====
    location_lines = ["Mallard Lake", "Hanover Park, IL"]

    for line in location_lines:
        text_width = draw.textbbox((0, 0), line, font=body_font)[2]
        draw.text((card_center_x - text_width // 2, y), line, font=body_font, fill=COLORS["card_text"])
        y += 80

    # ===== BENEFIT SECTION =====
    fr_logo = Image.open(ASSETS["family_reach_logo"]).convert("RGBA").resize((130, 130), Image.LANCZOS)

    benefit_text = "Benefiting Family Reach"
    text_width = draw.textbbox((0, 0), benefit_text, font=body_font)[2]

    total_width = fr_logo.width + 20 + text_width
    group_x = (WIDTH - total_width) // 2
    logo_y = 960

    img.paste(fr_logo, (group_x, logo_y), fr_logo)
    draw.text(
        (group_x + fr_logo.width + 20, logo_y + 38),
        benefit_text,
        font=body_font,
        fill=COLORS["card_text"]
    )

    # ===== NOTE =====
    qr_note = "Follow for updates • Registration opens soon"
    x = centered_x(draw, qr_note, small_font)
    draw.text((x, 1100), qr_note, font=small_font, fill=COLORS["card_text"])

    # ===== FOOTER =====
    draw.rectangle([(100, 1160), (WIDTH - 100, 1265)], fill=COLORS["bg_top"])

    footer_text = "Run • Walk • Support"
    x = centered_x(draw, footer_text, line_font)
    draw.text((x, 1180), footer_text, font=line_font, fill=COLORS["accent_2"])

    # ===== SAVE =====
    out = os.path.join(OUTPUT_DIR, "save_the_date_2026.png")
    img = img.convert("RGB")
    img.save(out, quality=100)

    return out


def generate_why_we_run():
    img = create_gradient((WIDTH, HEIGHT), COLORS["bg_top"], COLORS["bg_bottom"])
    draw = ImageDraw.Draw(img)

    title_font = load_font(FONTS["bold"], 110)
    subtitle_font = load_font(FONTS["bold"], 46)
    item_font = load_font(FONTS["regular"], 38)
    action_font = load_font(FONTS["bold"], 50)

    title = "WHY WE RUN"
    x = centered_x(draw, title, title_font)
    draw_text_with_shadow(draw, x, 90, title, title_font, COLORS["accent"])

    subtitle = "Every step helps a family breathe easier."
    x = centered_x(draw, subtitle, subtitle_font)
    draw_text_with_shadow(draw, x, 230, subtitle, subtitle_font, COLORS["text"])

    cards = [
        ("HOUSING", "Keep families housed during treatment"),
        ("FOOD", "Keep food on the table"),
        ("UTILITIES", "Cover essentials like power and heat"),
        ("TRAVEL", "Help with gas and transportation to care"),
    ]

    card_x = 95
    card_w = WIDTH - 190
    inner_x = 135
    inner_w = card_x + card_w - inner_x - 40
    card_h = 160
    card_gap = 24
    y = 370
    for header, body in cards:
        draw.rounded_rectangle(
            [(card_x, y), (card_x + card_w, y + card_h)],
            radius=22,
            fill=COLORS["card"],
            outline=COLORS["accent"],
            width=3,
        )
        draw.text((inner_x, y + 24), header, font=subtitle_font, fill=COLORS["card_text"])
        wrapped_lines = wrap_text(draw, body, item_font, inner_w)
        body_y = y + 92
        line_h = item_font.getbbox("Ay")[3] + 6
        for line in wrapped_lines:
            draw.text((inner_x, body_y), line, font=item_font, fill=COLORS["card_text"])
            body_y += line_h
        y += card_h + card_gap

    cta = "Join us in 2026: Run • Walk • Donate"
    x = centered_x(draw, cta, action_font)
    draw_text_with_shadow(draw, x, 1140, cta, action_font, COLORS["accent_2"])

    draw_footer(draw, 1248)
    out = os.path.join(OUTPUT_DIR, "why_we_run_2026.png")
    img.save(out, quality=100)
    return out


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    generated = [
        generate_we_are_back(),
        generate_save_the_date(),
        generate_why_we_run(),
    ]
    for file_path in generated:
        print(f"Created {file_path}")


if __name__ == "__main__":
    main()
