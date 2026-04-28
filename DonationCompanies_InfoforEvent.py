from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

# === CONFIG ===
CONFIG = {
    "image_size": (1080, 1350),  # portrait flyer
    "fonts": {
        "bold": "fonts/Montserrat-Bold.ttf",
        "regular": "fonts/Montserrat-Regular.ttf"
    },
    "colors": {
        "bg_top": (40, 0, 60),  # dark purple
        "bg_bottom": (0, 0, 0),  # black
        "text": (255, 255, 255),  # white text
        "border": (180, 0, 255),  # bright purple border
        "logo_shadow": (0, 0, 0, 150)
    },
    "output_folder": "donor_visuals",
    "padding": 80  # top/bottom padding
}

# Example donor list
DONORS = [
    {
        "name": "TownHouse Books & Cafe",
        "info": "Serving fresh, wholesome meals since 1996, with daily soups, desserts, and in-house roasted meats. "
                "Convenient curbside pickup and a variety of quiches, pies, salads, and bakery items.",
        "donation": "$30 Gift Card",
        "logo_path": "static/TownHouse_Cafe_logo.jpg",
        "logo_size": (350, 350)
    },
    {
        "name": "Schaumburg Boomers",
        "info": "With multiple Frontier League Championships under their belt, the Boomers are known not only for their exciting gameplay "
        "but also for their commitment to creating memorable experiences for fans of all ages. ",
        "donation": "Four 2026 home tickets",
        "logo_path": "static/logo-boomers.png",
        "logo_size": (400, 200)
    },
    {
        "name": "LMNT",
        "info": "A tasty electrolyte drink mix formulated to support hydration needs. Perfect for anyone fasting or following low-carb, whole food diets, "
                "LMNT delivers essential electrolytes - on a mission to restore health through hydration and help people feel their "
                "best every day.",
        "donation": "Electrolyte Drink Mix Packs",
        "logo_path": "static/lmnt_logo.png",
        "logo_size": (350, 350)
    },
    {
        "name": "Nuun Hydration",
        "info": "Hydrates better than water alone with a better-for-you blend of electrolytes. "
                "Only 1g of sugar and packed with clean ingredients — gluten-free, non-GMO, vegan, and kosher. "
                "Formulated to replenish electrolytes and minerals lost in sweat, support water absorption, "
                "and keep your body in balance during exercise or on-the-go.",
        "donation": "Hydration Powder Packs",
        "logo_path": "static/nuun_logo.png",
        "logo_size": (400, 200)
    },
    {
        "name": "Cooper’s Hawk Winery & Restaurants",
        "info": "Cooper’s Hawk Winery & Restaurants, inspired by Napa Valley, is built on the belief that food and wine create lasting connections. "
                "Their award-winning wines are handcrafted from premium grapes sourced around the world.",
        "donation": "Four Lux Wine Tastings",
        "logo_path": "static/chawk_logo.jpg",
        "logo_size": (300, 300)
    },
    {
        "name": "LCB 5K",
        "info": "Founded in hopes of honoring those we have lost to cancer and helping families dealing with the financial and emotional burdens of cancer. " 
                "This donation was provided by my cousin, Ryan Jack, who helped make our custom fragrance sprays!",
        "donation": "Custom LCB 5K Fragrance Sprays",
        "logo_path": "static/LCB 5K logo.png",
        "logo_size": (350, 350)
    },
    {
        "name": "Premier Workspaces",
        "info": "Premier Workspaces® is a national leader in flexible workspace. With over 80 locations they "
                "provide a professional setting with well-appointed amenities and services, tailored to meet your individual business needs.",
        "donation": "Custom LCB 5K Mini Footballs",
        "logo_path": "static/Premier_Workspace_logo.png",
        "logo_size": (400, 150)
    },
    {
        "name": "SHIFT",
        "info": "Huge thank you to SHIFT for the production and design of our LCB 5K T-Shirts!  "
                "We are very lucky to have them as a partner to help make this day even more special. "
                "In addition they have also donated our LCB 5K Rally Towels and wristbands!",
        "donation": "Rally Towels and wristbands",
        "logo_path": "static/SHIFTLogo_White.png",
        "logo_size": (550, 350)
    }
]
# === FUNCTIONS ===
def create_gradient(size, top_color, bottom_color):
    base = Image.new('RGB', size, top_color)
    top = Image.new('RGB', size, bottom_color)
    mask = Image.linear_gradient("L").resize(size)
    return Image.composite(base, top, mask)

def draw_text_centered(draw, text, font, y, image_width, fill, max_width=None):
    """Draw multiline text centered horizontally with word wrap"""
    words = text.split(" ")
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + " " + word if current_line else word
        w = font.getbbox(test_line)[2]
        if max_width and w > max_width:
            lines.append(current_line)
            current_line = word
        else:
            current_line = test_line
    if current_line:
        lines.append(current_line)

    for line in lines:
        text_width = font.getbbox(line)[2]
        x = (image_width - text_width) // 2
        draw.text((x, y), line, font=font, fill=fill)
        y += font.getbbox(line)[3] + 20  # line spacing
    return y

def draw_logo_with_shadow(img, logo_path, center_x, y, logo_size=(400, 400), shadow_offset=10):
    """Paste logo with subtle shadow, using specific size"""
    logo = Image.open(logo_path).convert("RGBA")
    logo = logo.resize(logo_size, Image.LANCZOS)  # <-- use resize instead of thumbnail

    # Shadow
    shadow = Image.new("RGBA", logo.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rectangle([0, 0, logo.width, logo.height], fill=CONFIG["colors"]["logo_shadow"])
    shadow = shadow.filter(ImageFilter.GaussianBlur(8))
    img.paste(shadow, (center_x - logo.width // 2 + shadow_offset, y + shadow_offset), shadow)

    # Logo
    img.paste(logo, (center_x - logo.width // 2, y), logo)


def generate_donor_flyer(donor, config):
    width, height = config["image_size"]
    img = create_gradient(config["image_size"], config["colors"]["bg_top"], config["colors"]["bg_bottom"])
    draw = ImageDraw.Draw(img)

    # Fonts
    bold_font_size = 80
    regular_font_size = 40
    donation_font_size = 55

    bold_font = ImageFont.truetype(config["fonts"]["bold"], bold_font_size)
    regular_font = ImageFont.truetype(config["fonts"]["regular"], regular_font_size)
    donation_font = ImageFont.truetype(config["fonts"]["bold"], donation_font_size)

    # Dynamic layout
    top_y = config["padding"]

    # Company Name
    current_y = draw_text_centered(draw, donor["name"], bold_font, top_y, width, config["colors"]["text"],
                                   max_width=width - 2 * config["padding"])

    # Company Info
    current_y += 60
    current_y = draw_text_centered(draw, donor["info"], regular_font, current_y, width, config["colors"]["text"],
                                   max_width=width - 2 * config["padding"])

    # Donation
    current_y += 60
    current_y = draw_text_centered(draw, donor["donation"], donation_font, current_y, width, config["colors"]["text"])

    # Logo at bottom with donor-specific size
    logo_y = height - 410
    logo_size = donor.get("logo_size", (400, 400))
    draw_logo_with_shadow(img, donor["logo_path"], width // 2, logo_y, logo_size=logo_size)

    # Border
    border_width = 12
    draw.rectangle([border_width // 2, border_width // 2, width - border_width // 2, height - border_width // 2],
                   outline=config["colors"]["border"], width=border_width)

    # Save flyer
    os.makedirs(config["output_folder"], exist_ok=True)
    safe_name = donor["name"].replace(" ", "_")
    output_path = os.path.join(config["output_folder"], f"{safe_name}_flyer.png")
    img.save(output_path, dpi=(300, 300))
    print(f"✅ Saved flyer for {donor['name']} at {output_path}")

# === MAIN ===
if __name__ == "__main__":
    for donor in DONORS:
        generate_donor_flyer(donor, CONFIG)