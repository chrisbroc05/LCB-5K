from PIL import Image, ImageDraw, ImageFont
import os
import textwrap

# --- Config ---
OUTPUT_FOLDER = "donation_output"
LOGO_PATH = "static/LCB 5K logo.png"  # update with your logo path
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Flyer settings (portrait orientation)
width, height = 1200, 1500  # taller than wide
bg_color = (106, 13, 173)      # LCB purple
title_color = (255, 255, 255)  # white
body_color = (255, 240, 245)   # light pink/white for contrast
padding = 100

# Create canvas
flyer = Image.new("RGB", (width, height), bg_color)
draw = ImageDraw.Draw(flyer)

# Load fonts
try:
    title_font = ImageFont.truetype("fonts/Montserrat-Bold.ttf", 90)
    body_font = ImageFont.truetype("fonts/Montserrat-Regular.ttf", 75)
except:
    title_font = ImageFont.load_default()
    body_font = ImageFont.load_default()

# --- Helper function for centered wrapped text ---
def draw_wrapped_text(draw, text, font, max_width, start_y, fill, line_spacing=20):
    lines = textwrap.wrap(text, width=25)  # narrower line width for vertical layout
    y = start_y
    for line in lines:
        bbox = draw.textbbox((0,0), line, font=font)
        line_w = bbox[2] - bbox[0]
        line_h = bbox[3] - bbox[1]
        x = (width - line_w) // 2
        draw.text((x, y), line, font=font, fill=fill)
        y += line_h + line_spacing  # spacing between lines
    return y

# --- Title ---
title_text = "Complimentary LCB 5K Fragrance Sprays!"
current_y = padding
current_y = draw_wrapped_text(draw, title_text, title_font, width - 2*padding, current_y, title_color, line_spacing=60)

# --- Logo ---
try:
    logo = Image.open(LOGO_PATH).convert("RGBA")
    max_logo_width = int(width * 0.35)  # slightly larger for vertical layout
    logo_ratio = max_logo_width / logo.width
    logo = logo.resize((max_logo_width, int(logo.height * logo_ratio)), Image.LANCZOS)
    logo_x = (width - logo.width) // 2
    flyer.paste(logo, (logo_x, current_y), logo)
    current_y += logo.height + 60
except FileNotFoundError:
    print(f"⚠️ Logo not found at {LOGO_PATH}, skipping logo placement.")

# --- Body Text ---
line1 = "Feel free to test out and take one of our custom LCB 5K fragrance sprays!"
line2 = "12 available — while supplies last!"

# Draw first line
current_y = draw_wrapped_text(draw, line1, body_font, width - 2*padding, current_y, body_color)

# Add extra spacing before second line
current_y += 60  # adjust spacing as needed

# Draw second line
current_y = draw_wrapped_text(draw, line2, body_font, width - 2*padding, current_y, body_color)

# --- Optional border ---
border_w = 12
draw.rectangle([border_w//2, border_w//2, width-border_w//2, height-border_w//2], outline=title_color, width=border_w)

# --- Save Flyer ---
output_path = os.path.join(OUTPUT_FOLDER, "LCB_5K_Fragrance_Flyer_Portrait.png")
flyer.save(output_path, dpi=(300,300))

print(f"✅ Flyer saved at {output_path}")
