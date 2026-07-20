import requests
from github import Github
from PIL import Image, ImageOps, ImageFilter
from io import BytesIO

ASCII_CHARS = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"

def get_ascii_char(brightness):
    char_index = min(int(brightness / 255 * (len(ASCII_CHARS) - 1)), len(ASCII_CHARS) - 1)
    return ASCII_CHARS[char_index]

def image_to_ascii(image, width=100) -> str:
    aspect_ratio = image.height / image.width
    height = int(width * aspect_ratio * 0.5)

    image = image.resize((width, height))
    image = image.convert('L')
    image = ImageOps.equalize(image)              # égalisation locale, fait ressortir les traits du visage
    image = image.filter(ImageFilter.SHARPEN)       # accentue les contours (yeux, nez, bouche)

    ascii_str = ""
    for y in range(height):
        for x in range(width):
            brightness = image.getpixel((x, y))
            ascii_str += get_ascii_char(brightness)
        ascii_str += "\n"

    return ascii_str

def generate_logo(g: Github, width=100) -> str:
    user_pfp = g.get_user().avatar_url
    response = requests.get(user_pfp)
    img = Image.open(BytesIO(response.content))
    return image_to_ascii(img, width)
