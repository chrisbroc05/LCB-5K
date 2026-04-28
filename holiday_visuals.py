from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import random

CONFIG = {
    "lcb_logo_path": "static/LCB 5K logo.png",
    "image_size": (1080, 1350),  # portrait
    "fonts": {
        "bold": "fonts/Montserrat-Bold.ttf",
        "slogan": "fonts/BebasNeue-Regular.ttf"
    },
    "header_text": "HAPPY LABOR DAY!",
    "slogan": "Link in Bio – Help Support Families Facing Cancer",
    "middle_text": "Join us for the first annual\n LCB 5K - 9.27.25",
    "colors": {
        "bg_top": (40, 0, 60),         # dark purple
        "bg_bottom": (0, 0, 0),        # black
        "pink": (255, 20, 147),        # dark pink
        "purple": (180, 0, 255),       # bright purple
        "white": (255, 255, 255)
    }
}

def create_gradient(size, top_color, bottom_color):
    """Vertical gradient background"""
    base = Image.new('RGB', size, top_color)
    top = Image.new('RGB', size, bottom_color)
    mask = Image.linear_gradient("L").resize(size)
    return Image.composite(base, top, mask)

def draw_confetti(draw, width, height, colors, count=150):
    """Random circles as confetti"""
    for _ in range(count):
        x = random.randint(0, width)
        y = random.randint(0, height)
        r = random.randint(5, 20)
        color = random.choice(colors)
        draw.ellipse([x, y, x+r, y+r], fill=color)

def draw_glow(img, center, radius, color):
    """Radial glow behind logo"""
    glow = Image.new('RGBA', img.size, (0,0,0,0))
    draw = ImageDraw.Draw(glow)
    for i in range(radius, 0, -5):
        alpha = int(80 * (i / radius))
        draw.ellipse([center[0]-i, center[1]-i, center[0]+i, center[1]+i], fill=color + (alpha,))
    img.paste(glow, (0,0), glow)

def gradient_text(base_img, position, text, font, gradient_colors):
    """Draw text with vertical gradient on the base image"""
    x, y = position
    text_width = font.getbbox(text)[2]
    text_height = font.getbbox(text)[3]

    gradient = Image.new('RGB', (text_width, text_height), color=0)
    grad_draw = ImageDraw.Draw(gradient)
    for i, color in enumerate(gradient_colors):
        y0 = i * (text_height // len(gradient_colors))
        y1 = (i+1) * (text_height // len(gradient_colors))
        grad_draw.rectangle([0, y0, text_width, y1], fill=color)

    mask = Image.new('L', (text_width, text_height), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.text((0, 0), text, font=font, fill=255)

    base_img.paste(gradient, (x, y), mask)

def generate_labor_day_graphic(config):
    width, height = config["image_size"]
    img = create_gradient(config["image_size"], config["colors"]["bg_top"], config["colors"]["bg_bottom"])
    draw = ImageDraw.Draw(img)

    # Fonts
    header_font = ImageFont.truetype(config["fonts"]["bold"], 90)
    middle_font = ImageFont.truetype(config["fonts"]["bold"], 55)
    slogan_font = ImageFont.truetype(config["fonts"]["slogan"], 50)

    # === Confetti ===
    draw_confetti(draw, width, height, [config["colors"]["pink"], config["colors"]["purple"]], count=50)

    # === Header Text ===
    header_text = config["header_text"]
    header_width = header_font.getbbox(header_text)[2]
    header_x = (width - header_width) // 2
    header_y = 150  # moved down from top
    gradient_text(img, (header_x, header_y), header_text, header_font, [config["colors"]["white"]])

    # === Logo with Glow ===
    logo = Image.open(config["lcb_logo_path"]).convert("RGBA").resize((300, 300), Image.LANCZOS)
    logo_center = (width//2, header_y + header_font.getbbox(header_text)[3] + 300)
    draw_glow(img, logo_center, 250, config["colors"]["purple"])
    img.paste(logo, (logo_center[0]-150, logo_center[1]-150), logo)

    # === Middle Text ===
    middle_text = config["middle_text"]
    middle_font = ImageFont.truetype(config["fonts"]["bold"], 65)

    # Split into lines
    lines = middle_text.split("\n")

    # Calculate total height
    line_height = middle_font.getbbox("Ay")[3] + 10  # add small spacing
    total_height = line_height * len(lines)

    # Position: lower it and center vertically relative to logo
    middle_y = logo_center[1] + 350  # increased from 180 to lower it
    for i, line in enumerate(lines):
        middle_width = middle_font.getbbox(line)[2]
        middle_x = (width - middle_width) // 2
        draw.text((middle_x, middle_y + i * line_height), line, font=middle_font, fill=config["colors"]["white"])

    # === Slogan at Bottom ===
    slogan_text = config["slogan"]
    slogan_width = slogan_font.getbbox(slogan_text)[2]
    slogan_x = (width - slogan_width) // 2
    slogan_y = height - 120
    draw.text((slogan_x, slogan_y), slogan_text, font=slogan_font, fill=config["colors"]["white"])

    # Save
    os.makedirs("holiday_output", exist_ok=True)
    output_path = os.path.join("holiday_output", "labor_day_lcb5k_graphic.png")
    img.save(output_path, dpi=(300, 300))
    print(f"✅ Labor Day graphic saved to {output_path}")

if __name__ == "__main__":
    generate_labor_day_graphic(CONFIG)
