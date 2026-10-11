import re
from PIL import Image, ImageDraw, ImageFont

def strip_ansi(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def render_terminal_image():
    # Read docker info output
    with open("docker_info.log", "r", encoding="utf-8", errors="replace") as f:
        raw_lines = f.readlines()

    clean_lines = [strip_ansi(line).rstrip() for line in raw_lines]

    # Prepend prompt
    display_lines = [
        "PS C:\\IT_209\\Session10\\Bai1__Session10> docker info"
    ] + clean_lines

    # Fonts
    font_path = "C:/Windows/Fonts/consola.ttf"
    font_bold_path = "C:/Windows/Fonts/consolab.ttf"
    font_size = 15
    line_spacing = 6
    font = ImageFont.truetype(font_path, font_size)
    font_bold = ImageFont.truetype(font_bold_path, font_size)

    # Calculate dimensions
    max_line_len = max(len(l) for l in display_lines)
    char_w = 9
    line_h = font_size + line_spacing
    padding_x = 30
    padding_top = 55
    padding_bottom = 30

    width = max(900, max_line_len * char_w + padding_x * 2)
    height = len(display_lines) * line_h + padding_top + padding_bottom

    # Create background image
    img = Image.new("RGBA", (width, height), (30, 30, 30, 255))
    draw = ImageDraw.Draw(img)

    # Title bar background
    draw.rectangle([0, 0, width, 40], fill=(45, 45, 48, 255))
    
    # Title buttons
    draw.ellipse([18, 14, 30, 26], fill=(255, 95, 86, 255))   # Red
    draw.ellipse([38, 14, 50, 26], fill=(255, 189, 46, 255))  # Yellow
    draw.ellipse([58, 14, 70, 26], fill=(39, 201, 63, 255))   # Green

    # Title text
    title_text = "PowerShell - docker info log verification"
    draw.text((width // 2 - 140, 12), title_text, fill=(200, 200, 200, 255), font=font)

    # Draw content
    y = padding_top
    for i, line in enumerate(display_lines):
        if i == 0:
            # Command prompt
            draw.text((padding_x, y), line, fill=(78, 201, 176, 255), font=font_bold)
        elif any(key in line for key in ["Server Version:", "Cgroup Driver:", "Cgroup Version:", "Containers:", "Images:", "Storage Driver:"]):
            # Key parameters highlighted in golden-yellow
            draw.text((padding_x, y), line, fill=(255, 215, 0, 255), font=font_bold)
        elif line.strip() in ["Server:", "Client:"]:
            draw.text((padding_x, y), line, fill=(86, 156, 214, 255), font=font_bold)
        elif ":" in line and not line.strip().startswith("-") and not line.strip().startswith("http"):
            parts = line.split(":", 1)
            draw.text((padding_x, y), parts[0] + ":", fill=(156, 220, 254, 255), font=font)
            if len(parts) > 1:
                prefix_w = draw.textlength(parts[0] + ":", font=font)
                draw.text((padding_x + prefix_w, y), parts[1], fill=(212, 212, 212, 255), font=font)
        else:
            draw.text((padding_x, y), line, fill=(204, 204, 204, 255), font=font)
        y += line_h

    # Convert to RGB and save
    final_img = img.convert("RGB")
    final_img.save("docker_info.png", "PNG", quality=95)
    print("Saved clean docker_info.png successfully! Size:", width, "x", height)

if __name__ == "__main__":
    render_terminal_image()
