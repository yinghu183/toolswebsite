import os
import math
from PIL import Image, ImageFont, ImageDraw, ImageEnhance, ImageChops, ImageOps

def set_opacity(im, opacity):
    assert opacity >= 0 and opacity <= 1
    alpha = im.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    im.putalpha(alpha)
    return im

def crop_image(im):
    bg = Image.new(mode='RGBA', size=im.size)
    diff = ImageChops.difference(im, bg)
    del bg
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)
    return im

def gen_mark(mark_text, color, font_family, font_size, opacity, font_height_crop):
    is_height_crop_float = '.' in str(font_height_crop)
    width = len(mark_text) * font_size
    if is_height_crop_float:
        height = round(font_size * float(font_height_crop))
    else:
        height = int(font_height_crop)

    mark = Image.new(mode='RGBA', size=(width, height))

    draw_table = ImageDraw.Draw(im=mark)
    draw_table.text(xy=(0, 0),
                    text=mark_text,
                    fill=color,
                    font=ImageFont.truetype(font_family, size=font_size))
    del draw_table

    mark = crop_image(mark)
    set_opacity(mark, opacity)

    return mark

def add_watermark(image_path, mark_text, color, font_family, font_size, opacity, angle, space):
    im = Image.open(image_path)
    im = ImageOps.exif_transpose(im)

    mark = gen_mark(mark_text, color, font_family, font_size, opacity, 1.2)

    c = int(math.sqrt(im.size[0] * im.size[0] + im.size[1] * im.size[1]))
    mark2 = Image.new(mode='RGBA', size=(c, c))

    y, idx = 0, 0
    while y < c:
        x = -int((mark.size[0] + space) * 0.5 * idx)
        idx = (idx + 1) % 2

        while x < c:
            mark2.paste(mark, (x, y))
            x = x + mark.size[0] + space
        y = y + mark.size[1] + space

    mark2 = mark2.rotate(angle)

    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    im.paste(mark2, (int((im.size[0] - c) / 2), int((im.size[1] - c) / 2)), mask=mark2.split()[3])
    del mark2

    output_path = os.path.join('static', 'watermarked', os.path.basename(image_path))
    if not os.path.exists(os.path.dirname(output_path)):
        os.makedirs(os.path.dirname(output_path))

    if os.path.splitext(output_path)[1].lower() != '.png':
        im = im.convert('RGB')
    im.save(output_path, quality=80)

    return output_path