from PIL import Image, ImageDraw, ImageFont
import os
import textwrap

# --- Config ---
OUTPUT_FOLDER = "output"
LOGO_PATH = "static/LCB 5K logo.png"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# --- Poster layout ---
width, height = 1080, 1350  # Instagram portrait ratio
bg_top = (0, 0, 0)          # top color (black)
bg_bottom = (40, 0, 60)     # bottom color (deep purple)
accent_color = (180, 0, 255)
highlight_color = (40, 0, 60)
text_color = (255, 255, 255)

# --- Create gradient background ---
flyer = Image.new("RGB", (width, height), bg_top)
draw = ImageDraw.Draw(flyer)

for y in range(height):
    ratio = y / height
    r = int(bg_top[0] * (1 - ratio) + bg_bottom[0] * ratio)
    g = int(bg_top[1] * (1 - ratio) + bg_bottom[1] * ratio)
    b = int(bg_top[2] * (1 - ratio) + bg_bottom[2] * ratio)
    draw.line([(0, y), (width, y)], fill=(r, g, b))

# --- Fonts ---
try:
    title_font = ImageFont.truetype("arialbd.ttf", 70)
    header_font = ImageFont.truetype("arialbd.ttf", 48)
    body_font = ImageFont.truetype("arial.ttf", 32)
except:
    title_font = ImageFont.load_default()
    header_font = ImageFont.load_default()
    body_font = ImageFont.load_default()

# --- Helper ---
def draw_wrapped_centered(draw, text, font, y, fill, max_width=width-160, spacing=8):
    """Draws wrapped centered text that fits inside section boxes"""
    lines = textwrap.wrap(text, width=38)
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x = (width - w) // 2
        draw.text((x, y), line, font=font, fill=fill)
        y += h + spacing
    return y

# === Logo + Title ===
current_y = 70

try:
    logo = Image.open(LOGO_PATH).convert("RGBA")
    logo.thumbnail((140, 140))
    flyer.paste(logo, ((width // 2) - 80, current_y), logo)
    current_y += 150
except:
    print("⚠️ Logo not found, skipping logo.")
    current_y += 50

title_text = "LCB 5K 2025 Recap"
bbox = draw.textbbox((0, 0), title_text, font=title_font)
w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
draw.text(((width - w) // 2, current_y), title_text, font=title_font, fill=text_color)
current_y += h + 60

# === Cause Section ===
section_height = 190
draw.rectangle([(100, current_y - 10), (width - 100, current_y + section_height)], fill=highlight_color, outline=accent_color, width=3)
text_y = current_y + 25
text_y = draw_wrapped_centered(draw, "OUR CAUSE", header_font, text_y, text_color)
draw_wrapped_centered(draw,
    "Supporting families facing the financial burdens of cancer",
    body_font, text_y + 20, text_color)
current_y += section_height + 50

# === Event Highlights ===
section_height = 180
draw.rectangle([(100, current_y), (width - 100, current_y + section_height)], fill=highlight_color, outline=accent_color, width=3)
text_y = current_y + 20
text_y = draw_wrapped_centered(draw, "EVENT HIGHLIGHTS", header_font, text_y, text_color)
draw_wrapped_centered(draw,
    "Raised $4,000 in donations having over 110 participants/donors",
    body_font, text_y + 20, text_color)
current_y += section_height + 50

# === Sponsors ===
section_height = 225
draw.rectangle([(100, current_y), (width - 100, current_y + section_height)], fill=highlight_color, outline=accent_color, width=3)
text_y = current_y + 20
text_y = draw_wrapped_centered(draw, "SPONSORS", header_font, text_y, text_color)
draw_wrapped_centered(draw,
    "Cooper’s Hawk Winery  •  Nuun Hydration  •  Schaumburg Boomers  •  LMNT  •  Lumey Photobooth",
    body_font, text_y + 20, text_color)
current_y += section_height + 50

# === Thank You Section ===
section_height = 225
draw.rectangle([(100, current_y), (width - 100, current_y + section_height)], fill=highlight_color, outline=accent_color, width=3)
text_y = current_y + 25
text_y = draw_wrapped_centered(draw, "THANK YOU", header_font, text_y, text_color)
draw_wrapped_centered(draw,
    "Thank you to everyone who made this event possible!\nBigger and better things ahead — follow along for more!",
    body_font, text_y + 20, text_color)

# --- Save Poster ---
output_path = os.path.join(OUTPUT_FOLDER, "LCB_5K_Results_Poster_Dark.png")
flyer.save(output_path, dpi=(300, 300))
print(f"✅ Dark themed poster saved at {output_path}")
