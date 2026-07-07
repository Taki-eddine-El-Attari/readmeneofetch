import json, os, re 
from src.draw_ascii import generate_logo
from src.fetch_info import fetch_stats
from PIL import Image, ImageDraw, ImageFont
from github import Github

def generate_fetch(g:Github) -> str:
    with open("config.json", "r") as f:
        config = json.load(f)

    pfp = generate_logo(g)

    if config.get("logo_only", False):
        return pfp

    user = fetch_stats(g)
    stats = f"{user['username']}@github.com\n------------------------------\n"
    for stat in config['display_stats']:
        if stat in user:
            stats += f"{stat.replace('_', ' ').title()}: {user[stat]}\n"
    stats += f"\n{config['additional_info']}\n"

    pfp_lines = pfp.split("\n")
    stats_lines = stats.split("\n")

    max_lines = max(len(pfp_lines), len(stats_lines))
    pfp_lines += [""] * (max_lines - len(pfp_lines))
    stats_lines += [""] * (max_lines - len(stats_lines))

    combined = "\n".join(f"{pfp_line:<50} {stats_line}" for pfp_line, stats_line in zip(pfp_lines, stats_lines))
    
    return combined

def return_preffered_color() -> tuple:
    with open("config.json", "r") as f:
        config = json.load(f)
    
    color = config['preferred_color']
    color_map = {
        "red": (255, 0, 0), "green": (0, 128, 0), "blue": (0, 0, 255),
        "yellow": (255, 255, 0), "purple": (128, 0, 128), "orange": (255, 165, 0),
        "pink": (255, 192, 203), "white": (255, 255, 255), "lightblue": (173, 216, 230),
    }
    return color_map.get(color, color_map["lightblue"])


def gen_image(g: Github):
    with open("config.json", "r") as f:
        config = json.load(f)

    logo_only = config.get("logo_only", False)
    bg_color = (0, 0, 0)
    value_color = return_preffered_color()
    font_size = 16

    font = None
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/ubuntu/UbuntuMono-R.ttf",
        "/usr/share/fonts/liberation-mono/LiberationMono-Regular.ttf",
        "monospace",
        "consola.ttf"
    ]
    for font_path in font_paths:
        try:
            font = ImageFont.truetype(font_path, font_size)
            break
        except IOError:
            continue
    if font is None:
        print("No suitable fonts found. Aborting!")
        return

    fetch = generate_fetch(g)
    line_spacing = font_size + 4

    if logo_only:
        ascii_lines = fetch.split("\n")
        width = 450
        height = len(ascii_lines) * line_spacing + 20

        image = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(image)

        y_offset = 10
        for ascii_line in ascii_lines:
            draw.text((10, y_offset), ascii_line, fill=value_color, font=font)
            y_offset += line_spacing

        os.makedirs("out", exist_ok=True)
        image.save("out/fetch.png")
        return

    # --- comportement original (avec stats) inchangé en dessous ---
    width, initial_height = 1200, 550
    ascii_width = 450
    text_margin = 60
    text_color = (255, 255, 255)

    image = Image.new("RGB", (width, initial_height), bg_color)
    draw = ImageDraw.Draw(image)

    lines = fetch.split("\n")
    ascii_lines = [line[:50] for line in lines]

    y_offset = 10
    for ascii_line in ascii_lines:
        draw.text((10, y_offset), ascii_line, fill=value_color, font=font)
        y_offset += line_spacing

    os.makedirs("out", exist_ok=True)
    image.save("out/fetch.png")


def generate_readme(g: Github):
    gen_image(g)

    image_pattern = r'<div align=\'center\'>\s*<img src=\'out/fetch\.png\' alt=\'Github Fetch\'>\s*</div>'
    image_content = "\n## Example Output\n<div align='center'>\n  <img src='out/fetch.png' alt='Github Fetch'>\n</div>\n"

    try:
        with open("README.md", "r", encoding="utf-8") as f:
            content = f.read()

        start_comment = "<!--- START OF DELETION --->"
        end_comment = "<!--- END OF DELETION --->"
        pattern = re.compile(f"{start_comment}.*?{end_comment}", re.DOTALL)
        content = re.sub(pattern, "", content)

        with open("config.json", "r") as f:
            config = json.load(f)
        append_automatic = config.get("append_automatic", True)

        if append_automatic and not re.search(image_pattern, content):
            content = content.rstrip() + "\n\n" + image_content
    except FileNotFoundError:
        content = image_content

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)
