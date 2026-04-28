from PIL import Image

def make_transparent(input_path, output_path, bg_color=(255, 255, 255)):
    # Open image and convert to RGBA
    img = Image.open(input_path).convert("RGBA")
    datas = img.getdata()

    new_data = []
    for item in datas:
        # If pixel matches background color, make it transparent
        if item[:3] == bg_color:
            new_data.append((255, 255, 255, 0))  # transparent
        else:
            new_data.append(item)

    img.putdata(new_data)
    img.save(output_path, "PNG")
    print(f"✅ Saved transparent logo at {output_path}")

# Example usage
make_transparent("static/LCB 5K logo.png", "static/LCB5Klogo_transparent.png", bg_color=(255, 255, 255))
