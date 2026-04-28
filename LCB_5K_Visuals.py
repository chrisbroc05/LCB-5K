from PIL import Image, ImageDraw, ImageFont
import os

CONFIG = {
    "top_logo_path": "static/family_reach_logo.png",
    "bottom_logo_path": "static/LCB 5K logo.png",
    "header_title": "Supporting Families Facing Cancer",
    "sub_header_lines": [
        "Donations from the LCB 5K will benefit the",
        "Family Reach Foundation, a nonprofit",
        "organization dedicated to easing the",
        "financial burdens of cancer."
    ],
    "mission_intro": "Together, we strive to:",
    "mission_points": [
    "Remove the financial barriers to treatment",
    "Keep families housed, fed, and safe",
    "Provide critical support for transportation & utilities",
    "Ensure no one chooses between care and basic needs",
    "Stand beside families during their hardest fight"
    ],
    "cta_box": {
        "title": "How You Can Join",
        "points": [
            "Sign up to walk or run (Signup deadline Sept. 3rd)",
            "Submit a loved one to our Memory Wall",
            "Can’t make it? Donate online to support the cause"
        ]
    },
    "colors": {
        "bg_top": (40, 0, 60),
        "bg_bottom": (10, 10, 10),
        "highlight_bar": (144, 238, 144),
        "text": (255, 255, 255),
        "accent": (186, 85, 211),
        "shadow": (20, 20, 20)
    },
    "image_size": (1080, 1350),
    "fonts": {
        "bold": "fonts/Montserrat-Bold.ttf",
        "regular": "fonts/Montserrat-Regular.ttf",
        "slogan": "fonts/BebasNeue-Regular.ttf"
    }
}

def draw_text(draw, position, text, font, fill, shadow=None, offset=(2, 2)):
    x, y = position
    if shadow:
        draw.text((x + offset[0], y + offset[1]), text, font=font, fill=shadow)
    draw.text((x, y), text, font=font, fill=fill)

def center_text(draw, text, font, y, image_width, fill, shadow=None):
    text_width = font.getbbox(text)[2]
    x = (image_width - text_width) // 2
    draw_text(draw, (x, y), text, font=font, fill=fill, shadow=shadow)
    return y + font.getbbox(text)[3] + 10  # next line Y position

def create_gradient(size, top_color, bottom_color):
    base = Image.new('RGB', size, top_color)
    top = Image.new('RGB', size, bottom_color)
    mask = Image.linear_gradient("L").resize(size)
    return Image.composite(base, top, mask)

def generate_graphic(config):
    img = create_gradient(config["image_size"], config["colors"]["bg_top"], config["colors"]["bg_bottom"])
    draw = ImageDraw.Draw(img)

    # Fonts
    bold_font = ImageFont.truetype(config["fonts"]["bold"], 40)
    regular_font = ImageFont.truetype(config["fonts"]["regular"], 38)
    small_font = ImageFont.truetype(config["fonts"]["regular"], 34)
    subheader_font = ImageFont.truetype(config["fonts"]["regular"], 32)

    padding_x = 80
    current_y = 80

    # === Top Title (Centered Across the Top) ===
    current_y = 50
    center_text(draw, config["header_title"], bold_font, current_y,
                config["image_size"][0], fill=config["colors"]["text"], shadow=config["colors"]["shadow"])
    current_y += bold_font.getbbox(config["header_title"])[3] + 30

    # === Top Left: Family Reach Logo ===
    logo = Image.open(config["top_logo_path"]).convert("RGBA").resize((200, 200), Image.LANCZOS)
    img.paste(logo, (padding_x, current_y + 20), logo)  # logo placed below title

    # === Right of Logo: Subheaders ===
    text_x = padding_x + 240
    subheader_y = current_y + 30
    for line in config["sub_header_lines"]:
        draw_text(draw, (text_x, subheader_y), line, font=subheader_font,
                  fill=config["colors"]["text"], shadow=config["colors"]["shadow"])
        subheader_y += 50  # spacing between lines

    # Update current_y to move content below logo
    current_y += max(logo.size[1], subheader_y - current_y) + 30

    # === Add some vertical space before mission section ===
    current_y += 40

    # === Mission Statement Intro (Centered) ===
    current_y = center_text(draw, config["mission_intro"], regular_font, current_y,
                            config["image_size"][0], fill=config["colors"]["text"], shadow=config["colors"]["shadow"])
    current_y += 10

    # === Mission Points (Centered) ===
    for point in config["mission_points"]:
        current_y = center_text(draw, point, small_font, current_y,
                                config["image_size"][0], fill=config["colors"]["text"], shadow=config["colors"]["shadow"])
        current_y += 20

    # === CTA Box ===
    current_y += 40
    box_height = 250
    box_width = 950
    box_x = (config["image_size"][0] - box_width) // 2

    # Draw CTA box background
    draw.rectangle([box_x, current_y, box_x + box_width, current_y + box_height],
                   fill=config["colors"]["highlight_bar"])

    # Center and underline CTA Title
    cta_title = config["cta_box"]["title"]
    title_font = bold_font
    title_width = title_font.getbbox(cta_title)[2]
    title_x = box_x + (box_width - title_width) // 2
    title_y = current_y + 20

    draw_text(draw, (title_x, title_y), cta_title, font=title_font, fill=(0, 0, 0))

    # Draw underline
    underline_y = title_y + title_font.getbbox(cta_title)[3] + 5
    draw.line([(title_x, underline_y), (title_x + title_width, underline_y)], fill=(0, 0, 0), width=2)

    # Bullet points (centered)
    current_y = underline_y + 30
    for point in config["cta_box"]["points"]:
        point_width = small_font.getbbox(point)[2]
        point_x = box_x + (box_width - point_width) // 2
        draw_text(draw, (point_x, current_y), point, font=small_font, fill=(0, 0, 0))
        current_y += 50

    # === Bottom Center: Slogan and LCB 5K Logo ===
    slogan_font = ImageFont.truetype(config["fonts"]["slogan"], 40)
    slogan_lines = [
        "Love.                             Mallard Lake in Hanover Park, IL",
        "Care.                              Saturday September 27th, 2025",
        "Believe.                                       Check in 9:30 AM"
    ]

    slogan_x = 80  # Adjust as needed
    slogan_y = 1180  # Adjust vertically to align nicely with logo

    for line in slogan_lines:
        draw_text(draw, (slogan_x, slogan_y), line,
                  font=slogan_font,
                  fill=config["colors"]["text"], shadow=config["colors"]["shadow"])
        slogan_y += slogan_font.getbbox(line)[3] + 10

    # Bottom right logo
    bottom_logo = Image.open(config["bottom_logo_path"]).convert("RGBA").resize((200, 200), Image.LANCZOS)
    img.paste(bottom_logo, (840, 1140), bottom_logo)

    # === Save ===
    os.makedirs("output", exist_ok=True)
    output_path = os.path.join("output", "lcb5k_charity_post.png")
    img.save(output_path, quality=100)
    print(f"✅ Charity graphic saved to {output_path}")

if __name__ == "__main__":
    generate_graphic(CONFIG)