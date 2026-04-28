# arrow_signs.py
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

# ---------- CONFIG ----------
CONFIG = {
    "output_folder": "arrow_signs_output",
    "image_size": (2000, 1200),   # width x height for printing
    "dpi": (300, 300),
    "fonts": {
        "title": "fonts/Montserrat-Bold.ttf",
        "label": "fonts/Montserrat-Regular.ttf"
    },
    "colors": {
        "bg": (34, 0, 51),
        "accent": (186, 85, 211),
        "accent2": (211, 106, 211),  # medium orchid (purplish pink)
        "text": (255, 255, 255),
        "shadow": (0, 0, 0, 150)
    },
    "padding": 80,
    "logo_path": "static/LCB 5K logo.png",
    "logo_size": (200, 200)
}

# ---------- Helpers ----------
def make_canvas(size, color):
    return Image.new("RGB", size, color)

def draw_arrow_mask(size, arrow_width_ratio=0.35, shaft_height_ratio=0.28):
    w, h = size
    shaft_w = int(w * arrow_width_ratio)
    shaft_h = int(h * shaft_height_ratio)
    head_w = int(w * 0.30)
    center_y = h // 2

    left = int(w*0.15)
    right = left + shaft_w
    head_point = right + head_w

    points = [
        (left, center_y - shaft_h // 2),
        (right, center_y - shaft_h // 2),
        (right, center_y - shaft_h),
        (head_point, center_y),
        (right, center_y + shaft_h),
        (right, center_y + shaft_h // 2),
        (left, center_y + shaft_h // 2),
    ]
    return points

def paste_with_shadow(base_img, shape_img, position, shadow_offset=(10,10), blur=12, shadow_color=(0,0,0,120)):
    shadow = Image.new("RGBA", shape_img.size, (0,0,0,0))
    sd = ImageDraw.Draw(shadow)
    sd.rectangle([0,0,shape_img.size[0], shape_img.size[1]], fill=shadow_color)
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))

    base_img.paste(shadow, (position[0]+shadow_offset[0], position[1]+shadow_offset[1]), shadow)
    base_img.paste(shape_img, position, shape_img)

def draw_sign(direction="right", config=CONFIG, title_text="THIS WAY →"):
    w, h = config["image_size"]
    img = make_canvas((w,h), config["colors"]["bg"])
    draw = ImageDraw.Draw(img)

    # fonts
    try:
        title_font = ImageFont.truetype(config["fonts"]["title"], 86)
    except Exception:
        title_font = ImageFont.load_default()

    pad = config["padding"]

    # Title
    title_w = title_font.getbbox(title_text)[2]
    title_x = (w - title_w)//2
    title_y = pad
    draw.text((title_x, title_y), title_text, font=title_font, fill=config["colors"]["text"])

    # Arrow
    arrow_layer = Image.new("RGBA", (w, h), (0,0,0,0))
    adraw = ImageDraw.Draw(arrow_layer)
    poly = draw_arrow_mask((w, h), arrow_width_ratio=0.40, shaft_height_ratio=0.26)
    adraw.polygon(poly, fill=config["colors"]["accent"])
    highlight = [(x, y - int(h*0.03)) for (x,y) in poly]
    adraw.polygon(highlight, fill=config["colors"]["accent2"])

    bbox = arrow_layer.getbbox() or (0,0,w,h)
    arrow_cropped = arrow_layer.crop(bbox)

    rotate_map = {"right": 0, "left": 180, "up": 270, "down": 90}
    angle = rotate_map.get(direction.lower(), 0)
    arrow_rot = arrow_cropped.rotate(angle, expand=True)

    arrow_w, arrow_h = arrow_rot.size
    arrow_x = (w - arrow_w) // 2
    arrow_y = title_y + title_font.getbbox(title_text)[3] + 60
    paste_with_shadow(img, arrow_rot, (arrow_x, arrow_y), shadow_offset=(12,12), blur=18)

    # Logo (bottom-right)
    if os.path.exists(config["logo_path"]):
        logo = Image.open(config["logo_path"]).convert("RGBA")
        logo = logo.resize(config["logo_size"])
        logo_x = w - config["logo_size"][0] - 40
        logo_y = h - config["logo_size"][1] - 40
        img.paste(logo, (logo_x, logo_y), logo)

    # Border
    border_w = 10
    draw.rectangle([border_w//2, border_w//2, w-border_w//2, h-border_w//2], outline=config["colors"]["accent"], width=border_w)

    return img

# ---------- MAIN ----------
def generate_all_signs():
    os.makedirs(CONFIG["output_folder"], exist_ok=True)
    specs = [
        ("right", "THIS WAY →", "arrow_right.png"),
        ("left", "THIS WAY ←", "arrow_left.png"),
        ("up", "THIS WAY ↓", "arrow_up.png"),
        ("down", "THIS WAY ↑", "arrow_down.png"),
    ]

    for direction, title_text, fname in specs:
        img = draw_sign(direction=direction, config=CONFIG, title_text=title_text)
        out_path = os.path.join(CONFIG["output_folder"], fname)
        img.save(out_path, dpi=CONFIG["dpi"])
        print(f"Saved: {out_path}")

if __name__ == "__main__":
    generate_all_signs()

