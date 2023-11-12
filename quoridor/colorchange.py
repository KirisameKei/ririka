import os

from PIL import Image, ImageDraw

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def main():
    bg = Image.new("RGB", size=(50, 50), color=0x001932)
    null = Image.new("RGB", size=(40, 40), color=0x0065cb)

    bg.paste(null, (5, 5))
    bg.save("null.png")

    red = Image.open("null.png")
    blue = Image.open("null.png")
    can = Image.open("null.png")

    red_draw = ImageDraw.Draw(red)
    blue_draw = ImageDraw.Draw(blue)
    can_draw = ImageDraw.Draw(can)

    red_color = 0xff55ff
    blue_color = 0x00e0ae
    can_color = 0x538dcb

    red_draw.ellipse((10, 10, 40, 40), fill=red_color)
    blue_draw.ellipse((10, 10, 40, 40), fill=blue_color)
    can_draw.ellipse((10, 10, 40, 40), fill=can_color)

    square_red_yoko = Image.new("RGB", size=(40, 10), color=red_color)
    square_blue_yoko = Image.new("RGB", size=(40, 10), color=blue_color)

    square_red_tate = Image.new("RGB", size=(10, 40), color=red_color)
    square_blue_tate = Image.new("RGB", size=(10, 40), color=blue_color)

    square_red_midium = Image.new("RGB", size=(10, 10), color=red_color)
    square_blue_midium = Image.new("RGB", size=(10, 10), color=blue_color)

    red.save("red.png")
    blue.save("blue.png")
    can.save("can.png")
    square_red_yoko.save("square_red_yoko.png")
    square_blue_yoko.save("square_blue_yoko.png")
    square_red_tate.save("square_red_tate.png")
    square_blue_tate.save("square_blue_tate.png")
    square_red_midium.save("square_red_midium.png")
    square_blue_midium.save("square_blue_midium.png")

main()