from PIL import Image, ImageDraw, ImageFont
import os

CONFIG = {
    "your_logo_path": "static/LCB 5K logo.png",
    "company_logo_path": "static/nuun_logo.png",  # Replace with actual company logo path
    "header_title": "Thank You for Supporting the LCB 5K!",
    "donation_message": "A huge thank you to Nuun Hydration for their generous donation of 30 tablet samples in support of our event!",
    "cta_text": "Want an extra hydration boost? Sign up now to try out Nuun Hydration at the LCB 5K!",
    "colors": {
        "bg_top": (40, 0, 60),
        "bg_bottom": (10, 10, 10),
        "highlight_bar": (186, 85, 211),
        "text": (255, 255, 255),
        "shadow": (20, 20, 20)
    },
    "image_size": (1080, 1350),
    "fonts": {
        "header": "fonts/Montserrat-Bold.ttf",
        "regular": "fonts/Montserrat-Regular.ttf",
        "cta": "fonts/Montserrat-Bold.ttf"
    },
    "mission_intro": "Together, we strive to:",
    "mission_points": [
    "Remove the financial barriers to cancer treatment",
    "Keep families housed, fed, and safe",
    "Provide critical support for transportation & utilities",
    "Ensure no one chooses between care and basic needs",
    "Stand beside families during their hardest fight"
],
    "slogan": "Love. Care. Believe.  |  LCB 5K – 9/27/25  | Sign Up Now"
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
    return y + font.getbbox(text)[3] + 10

def wrap_text(text, font, max_width, draw):
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        w = draw.textlength(test_line, font=font)
        if w <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

def create_gradient(size, top_color, bottom_color):
    base = Image.new('RGB', size, top_color)
    top = Image.new('RGB', size, bottom_color)
    mask = Image.linear_gradient("L").resize(size)
    return Image.composite(base, top, mask)

def generate_graphic(config):
    img = create_gradient(config["image_size"], config["colors"]["bg_top"], config["colors"]["bg_bottom"])
    draw = ImageDraw.Draw(img)

    # Fonts
    header_font = ImageFont.truetype(config["fonts"]["header"], 48)
    regular_font = ImageFont.truetype(config["fonts"]["regular"], 38)
    cta_font = ImageFont.truetype(config["fonts"]["cta"], 36)
    small_font = ImageFont.truetype(config["fonts"]["regular"], 32)  # Added small_font
    mission_intro_font = ImageFont.truetype(config["fonts"]["header"], 40)  # smaller than header_font
    mission_point_font = ImageFont.truetype(config["fonts"]["regular"], 32)  # smaller than regular_font

    padding_x = 80
    current_y = 80

    # === Header Title (Centered at Top) ===
    current_y = center_text(draw, config["header_title"], header_font, current_y,
                            config["image_size"][0], fill=config["colors"]["text"], shadow=config["colors"]["shadow"])
    current_y += 40

    # === Logos side by side ===
    your_logo = Image.open(config["your_logo_path"]).convert("RGBA").resize((300, 300), Image.LANCZOS)
    company_logo = Image.open(config["company_logo_path"]).convert("RGBA").resize((400,300), Image.LANCZOS)

    logos_y = current_y
    logos_padding = 150
    img.paste(your_logo, (logos_padding, logos_y), your_logo)
    img.paste(company_logo, (config["image_size"][0] - 335 - logos_padding, logos_y + 5), company_logo)
    current_y += 320

    # === Donation Message (Centered, wrapped if needed) ===
    message_max_width = config["image_size"][0] - 2 * padding_x
    donation_lines = wrap_text(config["donation_message"], regular_font, message_max_width, draw)

    for line in donation_lines:
        current_y = center_text(draw, line, regular_font, current_y, config["image_size"][0],
                                fill=config["colors"]["text"], shadow=config["colors"]["shadow"])
    current_y += 40

    # === Call to Action Box ===
    box_height = 160
    box_width = config["image_size"][0] - 160
    box_x = (config["image_size"][0] - box_width) // 2
    box_y = current_y

    draw.rectangle([box_x, box_y, box_x + box_width, box_y + box_height],
                   fill=config["colors"]["highlight_bar"])

    # Wrap CTA text to fit inside the box (with padding)
    cta_max_width = box_width - 40
    cta_lines = wrap_text(config["cta_text"], cta_font, cta_max_width, draw)
    line_height = cta_font.getbbox("Ay")[3] + 8
    total_text_height = line_height * len(cta_lines)

    start_y = box_y + (box_height - total_text_height) // 2

    for i, line in enumerate(cta_lines):
        line_width = cta_font.getbbox(line)[2]
        x = box_x + (box_width - line_width) // 2
        y = start_y + i * line_height
        draw_text(draw, (x, y), line, font=cta_font, fill=(255, 255, 255), shadow=config["colors"]["shadow"])

    current_y = box_y + box_height + 50

    # Mission Intro (centered)
    current_y = center_text(draw, config["mission_intro"], mission_intro_font, current_y,
                            config["image_size"][0], fill=config["colors"]["text"], shadow=config["colors"]["shadow"])
    current_y += 8

    # Mission Points (no bullets)
    line_spacing = 6
    line_height = mission_point_font.getbbox("Ay")[3] + line_spacing
    for point in config["mission_points"]:
        wrapped_lines = wrap_text(point, mission_point_font, config["image_size"][0] - 160, draw)
        for line in wrapped_lines:
            line_width = mission_point_font.getbbox(line)[2]
            x = (config["image_size"][0] - line_width) // 2
            draw_text(draw, (x, current_y), line, font=mission_point_font,
                      fill=config["colors"]["text"], shadow=config["colors"]["shadow"])
            current_y += line_height
    current_y += 15

    # === Bottom Slogan (Centered) ===
    slogan_font = ImageFont.truetype(config["fonts"]["regular"], 24)
    slogan_text = config["slogan"]
    slogan_width = slogan_font.getbbox(slogan_text)[2]
    slogan_x = (config["image_size"][0] - slogan_width) // 2
    slogan_y = config["image_size"][1] - slogan_font.getbbox(slogan_text)[3] - 30  # 30 px padding from bottom

    draw_text(draw, (slogan_x, slogan_y), slogan_text,
              font=slogan_font, fill=config["colors"]["text"], shadow=config["colors"]["shadow"])


    # === Save ===
    os.makedirs("donation_output", exist_ok=True)
    output_path = os.path.join("donation_output", "donation_thankyou_Nuun.png")
    img.save(output_path, quality=100)
    print(f"✅ Donation visual saved to {output_path}")

if __name__ == "__main__":
    generate_graphic(CONFIG)
