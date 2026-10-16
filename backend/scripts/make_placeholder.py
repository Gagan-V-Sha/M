from PIL import Image, ImageDraw, ImageFont
import os

logo_path = r'd:\With Hosting in my Laptop - Copy\frontend\src\assets\LogoBlack.png'
# Create a 200x50 placeholder image
img = Image.new('RGB', (200, 50), color = (73, 109, 137))
d = ImageDraw.Draw(img)
d.text((10,15), "Placeholder Logo", fill=(255,255,0))
img.save(logo_path)
