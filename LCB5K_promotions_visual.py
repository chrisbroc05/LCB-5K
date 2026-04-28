from PIL import Image, ImageDraw, ImageFont
import os

CONFIG = {
    "dogs_logo_path": "static/chicago_dogs.jpg",  # ADD THIS FILE
    "lcb_logo_path": "static/LCB 5K logo.png",
    "header_title": "We’re Coming to the Chicago Dogs Game!",
    "event_info": [
        "Friday, August 22nd | Gates Open at 5 PM",
        "Impact Field, Rosemont, IL",
        "Visit Our Table on the Concourse"
    ],
    "contest_title": "WIN A $100 AMAZON GIFT CARD!",
    "contest_steps": [
        "1. Sign up OR donate at our table",
        "2. Follow us on social media",
        "",
        "You’re entered to win!",
        "Winner will be announced in the 7th inning"
    ],
    "colors": {
        "bg_top": (40, 0, 60),
        "bg_bottom": (10, 10, 10),
        "highlight_bar": (255, 0, 0),  # Red contest box for visibility
        "text": (255, 255, 255),
        "shadow": (20, 20, 20)
    },
    "image_size": (1080, 1350),
    "fonts": {
        "bold": "fonts/Montserrat-Bold.ttf",
        "regular": "fonts/Montserrat-Regular.ttf",
        "slogan": "fonts/BebasNeue-Regular.ttf"
    },
    "slogan": "Love. Care. Believe.  |  LCB 5K – 9/27/25  | Supporting Families Facing Cancer"
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

def create_gradient(size, top_color, bottom_color):
    base = Image.new('RGB', size, top_color)
    top = Image.new('RGB', size, bottom_color)
    mask = Image.linear_gradient("L").resize(size)
    return Image.composite(base, top, mask)

def generate_graphic(config):
    img = create_gradient(config["image_size"], config["colors"]["bg_top"], config["colors"]["bg_bottom"])
    draw = ImageDraw.Draw(img)

    # Fonts
    bold_font = ImageFont.truetype(config["fonts"]["bold"], 46)
    regular_font = ImageFont.truetype(config["fonts"]["regular"], 42)
    small_font = ImageFont.truetype(config["fonts"]["regular"], 36)
    slogan_font = ImageFont.truetype(config["fonts"]["slogan"], 38)
    # Slightly smaller bold font for contest highlights
    small_bold_font = ImageFont.truetype(config["fonts"]["bold"], 36)

    current_y = 60

    # === Title ===
    current_y = center_text(draw, config["header_title"], bold_font, current_y,
                            config["image_size"][0], fill=config["colors"]["text"], shadow=config["colors"]["shadow"])
    current_y += 40

    # === Logos Side by Side ===
    dogs_logo = Image.open(config["dogs_logo_path"]).convert("RGBA").resize((300, 300), Image.LANCZOS)
    lcb_logo = Image.open(config["lcb_logo_path"]).convert("RGBA").resize((300, 300), Image.LANCZOS)

    logos_y = current_y
    logos_padding = 100
    img.paste(dogs_logo, (logos_padding, logos_y), dogs_logo)
    img.paste(lcb_logo, (config["image_size"][0] - 300 - logos_padding, logos_y), lcb_logo)
    current_y += 340

    # === Event Info ===
    current_y += 10
    for i, line in enumerate(config["event_info"]):
        if "Visit Our Table" in line:
            # Make the CTA line bolder and larger
            current_y = center_text(draw, line, bold_font, current_y,
                                    config["image_size"][0], fill=config["colors"]["text"],
                                    shadow=config["colors"]["shadow"])
        else:
            current_y = center_text(draw, line, regular_font, current_y,
                                    config["image_size"][0], fill=config["colors"]["text"],
                                    shadow=config["colors"]["shadow"])
    current_y += 80

    # === Contest Box ===
    box_height = 350
    box_width = config["image_size"][0] - 100
    box_x = (config["image_size"][0] - box_width) // 2
    box_y = current_y

    # Draw background box
    draw.rectangle([box_x, box_y, box_x + box_width, box_y + box_height],
                   fill=config["colors"]["highlight_bar"])

    # Contest title
    title_y = box_y + 20
    current_y = center_text(draw, config["contest_title"], bold_font, title_y,
                            config["image_size"][0], fill=(255, 255, 255))

    # === Contest Steps ===
    current_y += 10
    for i, line in enumerate(config["contest_steps"]):
        if "You’re entered to win!" in line or "Winner will be announced" in line:
            # Bold + slightly smaller so it fits better
            current_y = center_text(draw, line, small_bold_font, current_y,
                                    config["image_size"][0], fill=config["colors"]["text"],
                                    shadow=config["colors"]["shadow"])
        elif line.strip() == "":
            current_y += 20  # spacing for blank lines
        else:
            current_y = center_text(draw, line, regular_font, current_y,
                                    config["image_size"][0], fill=config["colors"]["text"],
                                    shadow=config["colors"]["shadow"])
    current_y += 60

    # === Bottom Slogan (Centered) ===
    slogan_width = slogan_font.getbbox(config["slogan"])[2]
    slogan_x = (config["image_size"][0] - slogan_width) // 2
    slogan_y = config["image_size"][1] - 80

    draw_text(draw, (slogan_x, slogan_y), config["slogan"],
              font=slogan_font, fill=config["colors"]["text"], shadow=config["colors"]["shadow"])

    # === Save ===
    os.makedirs("output", exist_ok=True)
    output_path = os.path.join("output", "lcb5k_chicago_dogs_post.png")
    img.save(output_path, quality=100)
    print(f"✅ Social media graphic saved to {output_path}")

if __name__ == "__main__":
    generate_graphic(CONFIG)
