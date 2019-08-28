#!/usr/bin/env python3

import faulthandler
faulthandler.enable()
from PIL import Image, ImageFont, ImageDraw

# text = "بسم الله الرحمن الرحيم"
# font_path = "NotoNastaliqUrdu-Regular"
# text = "Benjamin"
# font_path = "NotoSans-Regular"
# text = "ཨོཾ་མ་ཎི་པདྨེ་ཧཱུྃ"
# font_path = "NotoSansTibetan-Regular"
text = "𗙫𗏵𗐱𗴟𗘺𗦀"
font_path = "NotoSerifTangut-Regular"

def fitted_text(text, font_path, max_height, index=0):
    size = 1
    font = ImageFont.truetype(font_path, size, index)
    prev_mask = mask = font.getmask(text, mode="1")
    while True:
        dimensions = mask.size
        if dimensions[1] <= max_height:
            size += 1
            font = font.font_variant(size=size)
            prev_mask = mask
            mask = font.getmask(text, mode="1")
        else:
            return prev_mask

def label(text, font_path, index=0):
    mask = fitted_text(text, font_path, 64, index)
    dimensions = mask.size
    image = Image.new("1", (dimensions[0], 128), 0)
    draw = ImageDraw.Draw(image)
    draw.draw.draw_bitmap((0, 32), mask, 1)
    return image.transpose(Image.ROTATE_270)
