from PIL import Image, ImageDraw, ImageFont
import os

# --- CONFIG ---
width, height = 1080, 1350
bg_top = (255, 230, 250)
bg_bottom = (180, 120, 255)
accent_color = (200, 80, 255)
text_color = (40, 0, 60)
highlight_color = (255, 245, 255)

# --- OUTPUT FOLDER ---
output_folder = r"familystories_output"
os.makedirs(output_folder, exist_ok=True)

# --- CREATE GRADIENT BACKGROUND ---
cover = Image.new("RGB", (width, height), bg_top)
draw = ImageDraw.Draw(cover)
for y in range(height):
    r = int(bg_top[0] + (bg_bottom[0] - bg_top[0]) * (y / height))
    g = int(bg_top[1] + (bg_bottom[1] - bg_top[1]) * (y / height))
    b = int(bg_top[2] + (bg_bottom[2] - bg_top[2]) * (y / height))
    draw.line([(0, y), (width, y)], fill=(r, g, b))

# --- FONTS ---
def load_font(name, size):
    try:
        return ImageFont.truetype(name, size)
    except:
        return ImageFont.load_default()

title_font = load_font("arialbd.ttf", 80)
subtitle_font = load_font("arialbd.ttf", 50)
body_font = load_font("arial.ttf", 40)
italic_font = load_font("ariali.ttf", 50)

# --- LOGO ---
logo_path = r"static/LCB_Alt_Logo.png"
try:
    logo = Image.open(logo_path).convert("RGBA")
    logo = logo.resize((200, 200))
except FileNotFoundError:
    logo = None

# --- HELPER: Wrap text ---
def wrap_text(text, font, max_width):
    words = text.split()
    lines, current = [], ""
    for word in words:
        test = f"{current} {word}".strip()
        if draw.textlength(test, font=font) <= max_width:
            current = test
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines

# --- HEADER ---
title_text = "YOUR IMPACT IN ACTION"
title_w = draw.textlength(title_text, font=title_font)
draw.text(((width - title_w) // 2, 150), title_text, fill=text_color, font=title_font)

# --- TWO-LINE SUBTITLE ---
subtitle_text = "See how your support this year\nchanged Ashley’s life for the better"
subtitle_lines = subtitle_text.split("\n")
subtitle_y = 290
for line in subtitle_lines:
    line_w = draw.textlength(line, font=subtitle_font)
    draw.text(((width - line_w) // 2, subtitle_y), line, fill=accent_color, font=subtitle_font)
    subtitle_y += 60  # spacing between lines

# --- MESSAGE BOX ---
box_margin = 100
box_top = 480
box_height = 460
draw.rounded_rectangle(
    [(box_margin, box_top), (width - box_margin, box_top + box_height)],
    radius=40,
    fill=highlight_color,
    outline=accent_color,
    width=3
)

# --- MESSAGE TEXT ---
message = (
    "Because of your generosity, families like Ashley’s are able to focus on what truly matters — "
    "healing, hope, and time together — instead of financial stress. "
    "Every donation, every step, and every show of support helps create stories like hers."
)

wrapped_lines = wrap_text(message, body_font, width - 2 * (box_margin + 60))
line_height = 55
total_height = len(wrapped_lines) * line_height
text_y = box_top + (box_height - total_height) // 2

for line in wrapped_lines:
    text_x = (width - draw.textlength(line, font=body_font)) // 2
    draw.text((text_x, text_y), line, font=body_font, fill=text_color)
    text_y += line_height

# --- SWIPE MESSAGE ---
swipe_text = "Swipe to read Ashley’s Story → "
swipe_w = draw.textlength(swipe_text, font=italic_font)
draw.text(((width - swipe_w) // 2, 1030), swipe_text, fill=text_color, font=italic_font)

# --- FOOTER ---
footer_text = "Love • Care • Believe  |  LCB 5K"
footer_w = draw.textlength(footer_text, font=body_font)
draw.text(((width - footer_w) // 2, height - 90), footer_text, fill=text_color, font=body_font)

# # --- LOGO ---
# if logo:
#     logo_x = width - logo.width - 80
#     logo_y = height - logo.height - 120
#     cover.paste(logo, (logo_x, logo_y), logo)

# --- SAVE ---
output_path = os.path.join(output_folder, "hope_spotlight_cover_centered.png")
cover.save(output_path, dpi=(300, 300))
print(f"✅ Centered cover visual saved at {output_path}")

