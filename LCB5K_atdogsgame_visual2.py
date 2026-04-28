from PIL import Image, ImageDraw, ImageFont
import os

CONFIG = {
    "dogs_logo_path": "static/chicago_dogs.jpg",
    "lcb_logo_path": "static/LCB 5K logo.png",
    "lcb5k_website_qr_path": "static/LCB 5K QR Code.png",
    "lcb5K_insta_qr_path": "static/lcb5k_qr.png",
    "family_reach_path": "static/family_reach_logo.png",
    "header_title": "",
    "event_info": [
    "Help support the Family Reach",
    "Foundation. Together we strive to",
    "stand beside those facing the emotional",
    "and financial burdens of cancer"
],
    "contest_title": "SCAN THE QR CODE BELOW TO\n SIGN UP FOR OUR 5K OR DONATE\nAND BE ENTERED FOR A CHANCE\nTO WIN A $100 AMAZON GIFT CARD!",
    "contest_steps": [
        "Winner will be announced in the 7th inning"
    ],
    "colors": {
        "bg_top": (255, 255, 255),
        "bg_bottom": (255, 255, 255),
        "highlight_bar": (230, 220, 255),   # Light purple fill
        "highlight_border": (120, 50, 150), # Rich purple border
        "text": (0, 0, 0),              # Black text
        "shadow": None                  # No shadow for print
    },
    "image_size": (2550, 3300),  # 8.5 x 11 inches at 300 DPI
    "fonts": {
        "bold": "fonts/Montserrat-Bold.ttf",
        "regular": "fonts/Montserrat-Regular.ttf",
        "slogan": "fonts/BebasNeue-Regular.ttf"
    },
    "slogan": "Love. Care. Believe.  |  LCB 5K – 9/27/25  | Follow us for more @lcb5K"
}

def draw_text(draw, position, text, font, fill):
    draw.text(position, text, font=font, fill=fill)

def center_text(draw, text, font, y, image_width, fill):
    text_width = font.getbbox(text)[2]
    x = (image_width - text_width) // 2
    draw.text((x, y), text, font=font, fill=fill)
    return y + font.getbbox(text)[3] + 10

def create_gradient(size, top_color, bottom_color):
    base = Image.new('RGB', size, top_color)
    top = Image.new('RGB', size, bottom_color)
    mask = Image.linear_gradient("L").resize(size)
    return Image.composite(base, top, mask)

def generate_graphic(config):
    img = create_gradient(config["image_size"], config["colors"]["bg_top"], config["colors"]["bg_bottom"])
    draw = ImageDraw.Draw(img)

    # Fonts (scaled up for print)
    bold_font = ImageFont.truetype(config["fonts"]["bold"], 100)
    regular_font = ImageFont.truetype(config["fonts"]["regular"], 100)
    small_font = ImageFont.truetype(config["fonts"]["regular"], 85)
    slogan_font = ImageFont.truetype(config["fonts"]["slogan"], 86)
    small_bold_font = ImageFont.truetype(config["fonts"]["bold"], 82)

    current_y = 120

    # Title
    current_y = center_text(draw, config["header_title"], bold_font, current_y,
                            config["image_size"][0], fill=config["colors"]["text"])
    current_y += 80

    # Logos
    dogs_logo = Image.open(config["dogs_logo_path"]).convert("RGBA").resize((500, 500), Image.LANCZOS)
    lcb_logo = Image.open(config["lcb_logo_path"]).convert("RGBA").resize((500, 500), Image.LANCZOS)
    logos_y = current_y
    logos_padding = 600
    img.paste(dogs_logo, (logos_padding, logos_y), dogs_logo)
    img.paste(lcb_logo, (config["image_size"][0] - 500 - logos_padding, logos_y), lcb_logo)
    current_y += 700

    # Event Info
    current_y += 25
    family_reach_logo = Image.open(config["family_reach_path"]).convert("RGBA").resize((450, 450), Image.LANCZOS)
    logo_x = 175
    logo_padding_right = 80

    # Move logo up to align with text
    logo_y = current_y - 25
    img.paste(family_reach_logo, (logo_x, logo_y), family_reach_logo)

    # Draw all text next to logo
    text_x = logo_x + family_reach_logo.width + logo_padding_right
    text_y = current_y
    line_height = small_font.getbbox("Ay")[3] + 10

    for line in config["event_info"]:
        if line.strip():  # skip empty lines
            draw_text(draw, (text_x, text_y), line, small_font, fill=config["colors"]["text"])
            text_y += line_height

    # Move current_y below the taller of logo or text
    current_y = max(logo_y + family_reach_logo.height, text_y) + 100

    # === Contest Box ===
    box_height = 850
    box_width = config["image_size"][0] - 300
    box_x = (config["image_size"][0] - box_width) // 2
    box_y = current_y

    # Draw contest box
    draw.rectangle(
        [box_x, box_y, box_x + box_width, box_y + box_height],
        fill=config["colors"]["highlight_bar"],
        outline=config["colors"]["highlight_border"],
        width=12
    )

    # Inside box spacing
    y_inside = box_y + 40  # padding from top of box

    # Contest title (split into lines)
    for title_line in config["contest_title"].split("\n"):
        y_inside = center_text(draw, title_line, bold_font, y_inside,
                               config["image_size"][0], fill=config["colors"]["text"])

    y_inside += 120  # gap before steps

    # Contest steps
    for line in config["contest_steps"]:
        if "Enter to win!" in line or "Winner will be announced" in line:
            y_inside = center_text(draw, line, small_bold_font, y_inside,
                                   config["image_size"][0], fill=config["colors"]["text"])
        elif line.strip() == "":
            y_inside += 20
        else:
            y_inside = center_text(draw, line, regular_font, y_inside,
                                   config["image_size"][0], fill=config["colors"]["text"])

    # Website QR BELOW the box
    qr_size = 550
    website_qr = Image.open(config["lcb5k_website_qr_path"]).convert("RGBA").resize((qr_size, qr_size), Image.LANCZOS)

    # Center QR under the contest box
    qr_x = (config["image_size"][0] - qr_size) // 2
    qr_y = box_y + box_height + 140  # space below contest box

    img.paste(website_qr, (qr_x, qr_y), website_qr)

    # Move current_y for the next section
    current_y = qr_y + qr_size + 150

    # Slogan at bottom
    slogan_width = slogan_font.getbbox(config["slogan"])[2]
    insta_qr_size = 200  # smaller so it fits nicely next to slogan
    total_width = slogan_width + 20 + insta_qr_size  # 20 px spacing between slogan and QR

    slogan_x = (config["image_size"][0] - total_width) // 2
    slogan_y = config["image_size"][1] - 200  # adjust vertical position as needed
    draw_text(draw, (slogan_x, slogan_y), config["slogan"], slogan_font, fill=config["colors"]["text"])

    # Instagram QR to the right of slogan
    insta_qr = Image.open(config["lcb5K_insta_qr_path"]).convert("RGBA").resize((insta_qr_size, insta_qr_size),
                                                                                Image.LANCZOS)
    insta_qr_x = slogan_x + slogan_width + 20  # 20 px spacing
    insta_qr_y = slogan_y - (
                insta_qr_size - slogan_font.getbbox(config["slogan"])[3]) // 2  # vertically center with slogan
    img.paste(insta_qr, (insta_qr_x, insta_qr_y), insta_qr)

    # Save at 300 DPI
    os.makedirs("output", exist_ok=True)
    output_path = os.path.join("output", "lcb5k_chicago_dogs_flyer_print.png")
    img.save(output_path, dpi=(300, 300))
    print(f"✅ Print-friendly flyer saved to {output_path}")

if __name__ == "__main__":
    generate_graphic(CONFIG)



