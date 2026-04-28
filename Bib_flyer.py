from PIL import Image, ImageDraw, ImageFont
import os

# --- Config ---
OUTPUT_FOLDER = "output"  # or any folder you want
LOGO_PATH = "static/LCB 5K logo.png"     # <-- update with your logo path
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# --- Flyer Settings ---
width, height = 2000, 1200  # Match arrow sign size for printing
background_color = "white"
title_color = (106, 13, 173)  # purplish color
text_color = "black"

# --- Create Image ---
flyer = Image.new("RGB", (width, height), background_color)
draw = ImageDraw.Draw(flyer)

# --- Load Fonts ---
try:
    title_font = ImageFont.truetype("arialbd.ttf", 120)  # Bigger title
    body_font = ImageFont.truetype("arial.ttf", 64)
except:
    title_font = ImageFont.load_default()
    body_font = ImageFont.load_default()

# --- Text Content ---
title_text = "Personalize Your Bib!"
body_text = (
    "Take a moment to make your bib special!\n\n"
    "Write the name of a loved one, a type of cancer,\n"
    "or a foundation you are honoring today\n"
    "on the line that says:\n\n"
    "“I'm here for ______”"
)

# --- Helper to Measure Text Size ---
def get_text_size(text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    return width, height

# --- Draw Title ---
title_w, title_h = get_text_size(title_text, title_font)
title_x = (width - title_w) // 2
title_y = 100
draw.text((title_x, title_y), title_text, font=title_font, fill=title_color)

# --- Add Logo ---
logo_y = title_y + title_h + 90
try:
    logo = Image.open(LOGO_PATH).convert("RGBA")
    # Scale logo to fit nicely (about 30% of width)
    max_logo_width = int(width * 0.15)
    logo_ratio = max_logo_width / logo.width
    logo = logo.resize((max_logo_width, int(logo.height * logo_ratio)), Image.LANCZOS)
    logo_x = (width - logo.width) // 2
    flyer.paste(logo, (logo_x, logo_y), logo)
    logo_y += logo.height + 40  # push body text below logo
except FileNotFoundError:
    print(f"⚠️ Logo not found at {LOGO_PATH}, skipping logo placement.")

# --- Draw Body Text (Centered Below Logo) ---
current_y = logo_y
for line in body_text.split("\n"):
    line_w, line_h = get_text_size(line, body_font)
    line_x = (width - line_w) // 2
    draw.text((line_x, current_y), line, font=body_font, fill=text_color)
    current_y += line_h + 15

# --- Save Flyer ---
output_path = os.path.join(OUTPUT_FOLDER, "LCB_5K_Bib_Flyer.png")
flyer.save(output_path, dpi=(300, 300))

print(f"✅ Flyer saved as {output_path}")