from PIL import Image, ImageDraw, ImageFont
import os

# --- CONFIG ---
width, height = 1080, 1350
bg_top = (180, 120, 255)        # soft pink
bg_bottom = (180, 120, 255)     # vibrant purple
accent_color = (200, 80, 255)   # bright purple-pink accent
text_color = (40, 0, 60)        # deep purple for readable contrast
highlight_color = (255, 245, 255)  # off-white boxes
#shadow_color = (100, 100, 100, 100)  # shadow for text

# --- OUTPUT FOLDER ---
output_folder = r"familystories_output"
os.makedirs(output_folder, exist_ok=True)

# --- INPUT DATA ---
name = "Ashley"
story_context = (
    "As a single mom, Ashley faced the unimaginable when her young daughter was diagnosed with cancer. "
    "Forced to leave her job to care for her child, Ashley suddenly found herself struggling to keep up with everyday expenses. "
    "Thanks to your generosity, she was able to keep a roof over their heads, put food on the table, and focus on her daughter’s healing — not the bills."
)
story_quote = (
    "My deepest gratitude goes out to you. Your assistance has been a blessing during this overwhelming journey. "
    "You didn’t just give us financial relief — you renewed our hope."
)
attribution = f"- {name}"

# --- CREATE GRADIENT BACKGROUND ---
flyer = Image.new("RGB", (width, height), bg_top)
draw = ImageDraw.Draw(flyer)
for y in range(height):
    r = int(bg_top[0] + (bg_bottom[0] - bg_top[0]) * (y / height))
    g = int(bg_top[1] + (bg_bottom[1] - bg_top[1]) * (y / height))
    b = int(bg_top[2] + (bg_bottom[2] - bg_top[2]) * (y / height))
    draw.line([(0, y), (width, y)], fill=(r, g, b))

# --- FONTS ---
try:
    title_font = ImageFont.truetype("arialbd.ttf", 80)
    header_font = ImageFont.truetype("arialbd.ttf", 65)
    body_font = ImageFont.truetype("arial.ttf", 38)
    italic_font = ImageFont.truetype("ariali.ttf", 36)
    big_italic_font = ImageFont.truetype("ariali.ttf", 65)
except:
    title_font = ImageFont.load_default()
    header_font = ImageFont.load_default()
    body_font = ImageFont.load_default()
    italic_font = ImageFont.load_default()
    big_italic_font = ImageFont.load_default()

# --- HELPER FUNCTIONS ---
def wrap_text(text, font, max_width):
    words = text.split()
    lines, current_line = [], ""
    for word in words:
        test_line = f"{current_line} {word}".strip()
        if draw.textlength(test_line, font=font) <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    return lines

def draw_centered_text_block(y, height, text, font, box_color, text_color, accent, radius=25):
    """Draw a rounded box with centered text and drop shadow."""
    box_margin = 80
    # Rounded rectangle
    draw.rounded_rectangle([(box_margin, y), (width - box_margin, y + height)],
                           radius=radius, fill=box_color, outline=accent, width=3)
    # Wrap text
    lines = wrap_text(text, font, width - 2 * (box_margin + 50))
    line_height = 50
    total_text_height = len(lines) * line_height
    text_y = y + (height - total_text_height) // 2

    # Draw shadow + text
    for line in lines:
        text_x = (width - draw.textlength(line, font=font)) // 2
        # Shadow
        draw.text((text_x + 3, text_y + 3), line, font=font)
        # Text
        draw.text((text_x, text_y), line, font=font, fill=text_color)
        text_y += line_height
    return y + height + 40

# --- LOGO ---
logo_path = r"static/LCB 5K logo.png"  # Replace with your logo path
try:
    logo = Image.open(logo_path).convert("RGBA")
    logo = logo.resize((200, 200))
except FileNotFoundError:
    logo = None

# --- HEADER ---
draw.rectangle([(0, 0), (width, 200)], fill=bg_top)
title_text = "LCB 5K IMPACT"
title_x = 80
draw.text((title_x, 90), title_text, fill=text_color, font=title_font)

# Name section
draw.rectangle([(0, 200), (width, 320)], fill=bg_top)
name_text = f"{name}'s Story"
draw.text((title_x + 100, 200), name_text, fill=text_color, font=big_italic_font)

# Draw logo last
if logo:
    logo_x = width - logo.width - 100
    logo_y = 85
    flyer.paste(logo, (logo_x, logo_y), logo)

# --- STORY ---
current_y = 360
current_y = draw_centered_text_block(
    y=current_y,
    height=500,
    text=story_context,
    font=body_font,
    box_color=highlight_color,
    text_color=text_color,
    accent=accent_color
)

# --- QUOTE ---
quote_height = 345
box_margin = 80
draw.rounded_rectangle([(box_margin, current_y), (width - box_margin, current_y + quote_height)],
                       radius=25, fill=highlight_color, outline=accent_color, width=3)
# Quote with shadows
full_quote = f"“{story_quote}”"
quote_lines = wrap_text(full_quote, body_font, width - 2 * (box_margin + 50))
line_height = 50
total_quote_height = len(quote_lines) * line_height
y_quote = current_y + (quote_height - total_quote_height) // 2 - 10
for line in quote_lines:
    text_x = (width - draw.textlength(line, font=body_font)) // 2
    draw.text((text_x + 2, y_quote + 2), line, font=body_font)
    draw.text((text_x, y_quote), line, font=body_font, fill=text_color)
    y_quote += line_height

# Attribution italic
draw.text((width // 2 - draw.textlength(attribution, font=italic_font)//2, y_quote + 10),
          attribution, font=italic_font, fill=accent_color)

# --- FOOTER ---
footer_text = "Love • Care • Believe  |  LCB 5K"
footer_x = (width - draw.textlength(footer_text, font=body_font)) // 2
draw.text((footer_x, height - 70), footer_text, fill=text_color, font=body_font)

# --- SAVE ---
output_path = os.path.join(output_folder, f"hope_spotlight_{name.lower().replace(' ', '_')}.png")
flyer.save(output_path, dpi=(300, 300))
print(f"✅ Hope Spotlight saved at {output_path}")
