# -*- coding: utf-8 -*-
import os
from PIL import Image, ImageDraw, ImageFont

def get_font(size):
    # Try finding standard Thai-supported fonts on Windows
    fonts = [
        "C:\\Windows\\Fonts\\tahoma.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\segoeui.ttf",
    ]
    for font_path in fonts:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except:
                pass
    return ImageFont.load_default()

def draw_card(filepath, thai_label, drawing_func):
    # 400x300 canvas size
    width, height = 400, 300
    # Background color: #1b2234 (dark card background)
    image = Image.new("RGBA", (width, height), (27, 34, 52, 255))
    draw = ImageDraw.Draw(image)
    
    # Draw border in Swedish Yellow #FFCD00
    border_color = (255, 205, 0, 255)
    draw.rectangle([10, 10, width - 10, height - 10], outline=border_color, width=3)
    
    # Call the specific drawing function to render the graphic icon
    drawing_func(draw, width, height)
    
    # Draw Thai label in high-contrast white
    font = get_font(22)
    # Estimate text width and center it
    text_bbox = draw.textbbox((0, 0), thai_label, font=font)
    text_w = text_bbox[2] - text_bbox[0]
    text_x = (width - text_w) // 2
    text_y = height - 45
    draw.text((text_x, text_y), thai_label, fill=(248, 250, 252, 255), font=font)
    
    # Save the card
    image.save(filepath, "PNG")

# Specific drawing routines
def draw_char_A_ring(draw, w, h):
    # Lesson 1: Å
    draw.ellipse([170, 60, 230, 120], outline=(255, 255, 255, 255), width=4)
    font = get_font(70)
    draw.text((172, 105), "A", fill=(255, 255, 255, 255), font=font)

def draw_char_A_dots(draw, w, h):
    # Lesson 1: Ä
    draw.ellipse([175, 75, 190, 90], fill=(255, 255, 255, 255))
    draw.ellipse([210, 75, 225, 90], fill=(255, 255, 255, 255))
    font = get_font(70)
    draw.text((172, 105), "A", fill=(255, 255, 255, 255), font=font)

def draw_char_O_dots(draw, w, h):
    # Lesson 1: Ö
    draw.ellipse([175, 75, 190, 90], fill=(255, 255, 255, 255))
    draw.ellipse([210, 75, 225, 90], fill=(255, 255, 255, 255))
    font = get_font(70)
    draw.text((172, 105), "O", fill=(255, 255, 255, 255), font=font)

def draw_hello(draw, w, h):
    # Lesson 2: Hej
    draw.ellipse([170, 70, 230, 130], outline=(0, 75, 135, 255), width=5)
    draw.line([200, 130, 200, 190], fill=(255, 255, 255, 255), width=6)
    draw.line([200, 150, 170, 110], fill=(255, 255, 255, 255), width=5)
    draw.line([200, 150, 230, 110], fill=(255, 255, 255, 255), width=5)

def draw_tack(draw, w, h):
    # Lesson 2: Tack (Heart/Thanks)
    # Simple heart shape
    draw.ellipse([160, 90, 210, 140], fill=(244, 63, 94, 255))
    draw.ellipse([190, 90, 240, 140], fill=(244, 63, 94, 255))
    draw.polygon([(162, 126), (238, 126), (200, 180)], fill=(244, 63, 94, 255))

def draw_bye(draw, w, h):
    # Lesson 2: Hejdå (Walking out door)
    draw.rectangle([160, 70, 240, 180], outline=(255, 255, 255, 255), width=4)
    draw.ellipse([170, 120, 180, 130], fill=(255, 205, 0, 255)) # Knob

def draw_id_card(draw, w, h):
    # Lesson 3: Name
    draw.rectangle([140, 80, 260, 170], outline=(255, 255, 255, 255), width=4)
    draw.ellipse([160, 105, 190, 135], fill=(0, 75, 135, 255))
    draw.line([205, 110, 245, 110], fill=(255, 255, 255, 255), width=4)
    draw.line([205, 130, 245, 130], fill=(255, 255, 255, 255), width=4)

def draw_cake(draw, w, h):
    # Lesson 3: Age
    draw.rectangle([150, 130, 250, 180], fill=(255, 205, 0, 255))
    draw.line([175, 90, 175, 130], fill=(239, 68, 68, 255), width=4)
    draw.line([200, 90, 200, 130], fill=(239, 68, 68, 255), width=4)
    draw.line([225, 90, 225, 130], fill=(239, 68, 68, 255), width=4)

def draw_flag_sweden(draw, w, h):
    # Lesson 3: Sverige
    draw.rectangle([140, 80, 260, 160], fill=(0, 75, 135, 255))
    draw.rectangle([175, 80, 195, 160], fill=(255, 205, 0, 255))
    draw.rectangle([140, 110, 260, 130], fill=(255, 205, 0, 255))

def draw_num5(draw, w, h):
    # Lesson 4: 5
    font = get_font(80)
    draw.text((180, 70), "5", fill=(255, 205, 0, 255), font=font)

def draw_num10(draw, w, h):
    # Lesson 4: 10
    font = get_font(80)
    draw.text((160, 70), "10", fill=(255, 205, 0, 255), font=font)

def draw_num20(draw, w, h):
    # Lesson 4: 20
    font = get_font(80)
    draw.text((160, 70), "20", fill=(255, 205, 0, 255), font=font)

def draw_clock(draw, w, h):
    # Lesson 5: Clock
    draw.ellipse([150, 60, 250, 160], outline=(255, 255, 255, 255), width=5)
    draw.line([200, 110, 200, 80], fill=(255, 205, 0, 255), width=4)
    draw.line([200, 110, 230, 110], fill=(255, 205, 0, 255), width=4)

def draw_calendar(draw, w, h):
    # Lesson 5: Calendar
    draw.rectangle([150, 70, 250, 170], outline=(255, 255, 255, 255), width=4)
    draw.rectangle([150, 70, 250, 100], fill=(239, 68, 68, 255))
    font = get_font(30)
    draw.text((185, 110), "31", fill=(255, 255, 255, 255), font=font)

def draw_snowflake(draw, w, h):
    # Lesson 5: Vinter
    # Snowflake lines
    cx, cy = 200, 110
    draw.line([cx - 40, cy, cx + 40, cy], fill=(56, 189, 248, 255), width=4)
    draw.line([cx, cy - 40, cx, cy + 40], fill=(56, 189, 248, 255), width=4)
    draw.line([cx - 28, cy - 28, cx + 28, cy + 28], fill=(56, 189, 248, 255), width=4)
    draw.line([cx - 28, cy + 28, cx + 28, cy - 28], fill=(56, 189, 248, 255), width=4)

def draw_red_block(draw, w, h):
    # Lesson 6: Röd
    draw.ellipse([150, 60, 250, 160], fill=(239, 68, 68, 255))

def draw_blue_block(draw, w, h):
    # Lesson 6: Blå
    draw.ellipse([150, 60, 250, 160], fill=(59, 130, 246, 255))

def draw_yellow_block(draw, w, h):
    # Lesson 6: Gul
    draw.ellipse([150, 60, 250, 160], fill=(253, 224, 71, 255))

def draw_mom(draw, w, h):
    # Lesson 7: Mamma
    draw.ellipse([200, 70, 230, 100], fill=(244, 63, 94, 255))
    draw.polygon([(185, 160), (245, 160), (215, 105)], fill=(244, 63, 94, 255))

def draw_dad(draw, w, h):
    # Lesson 7: Pappa
    draw.ellipse([200, 70, 230, 100], fill=(59, 130, 246, 255))
    draw.rectangle([190, 105, 240, 160], fill=(59, 130, 246, 255))

def draw_child(draw, w, h):
    # Lesson 7: Barn
    draw.ellipse([200, 80, 220, 100], fill=(253, 224, 71, 255))
    draw.rectangle([195, 105, 225, 150], fill=(253, 224, 71, 255))

def draw_cat(draw, w, h):
    # Lesson 8: Katt
    # Head circle
    draw.ellipse([150, 80, 250, 160], fill=(156, 163, 175, 255))
    # Ear triangles
    draw.polygon([(150, 90), (170, 50), (190, 80)], fill=(156, 163, 175, 255))
    draw.polygon([(250, 90), (230, 50), (210, 80)], fill=(156, 163, 175, 255))

def draw_dog(draw, w, h):
    # Lesson 8: Hund
    # Simplified dog body and head
    draw.rectangle([140, 110, 220, 170], fill=(161, 98, 7, 255)) # body
    draw.rectangle([210, 80, 250, 120], fill=(161, 98, 7, 255)) # head
    draw.rectangle([160, 170, 180, 190], fill=(161, 98, 7, 255)) # leg 1
    draw.rectangle([200, 170, 220, 190], fill=(161, 98, 7, 255)) # leg 2

def draw_bird(draw, w, h):
    # Lesson 8: Fågel
    # Flight wings shape
    draw.arc([130, 90, 200, 150], 180, 360, fill=(255, 255, 255, 255), width=5)
    draw.arc([200, 90, 270, 150], 180, 360, fill=(255, 255, 255, 255), width=5)

def draw_apple(draw, w, h):
    # Lesson 9: Äpple
    draw.ellipse([150, 80, 250, 170], fill=(220, 38, 38, 255)) # red body
    draw.line([200, 80, 210, 60], fill=(120, 113, 108, 255), width=4) # stem

def draw_bread(draw, w, h):
    # Lesson 9: Bröd
    draw.rectangle([140, 100, 260, 160], fill=(180, 130, 70, 255))
    # Slices cuts
    draw.line([170, 100, 170, 160], fill=(100, 70, 30, 255), width=3)
    draw.line([200, 100, 200, 160], fill=(100, 70, 30, 255), width=3)
    draw.line([230, 100, 230, 160], fill=(100, 70, 30, 255), width=3)

def draw_milk(draw, w, h):
    # Lesson 9: Mjölk
    # Milk carton shape
    draw.rectangle([160, 90, 240, 180], outline=(255, 255, 255, 255), width=4)
    draw.polygon([(160, 90), (200, 60), (240, 90)], outline=(255, 255, 255, 255), width=4)

def draw_bed(draw, w, h):
    # Lesson 10: Säng
    draw.line([140, 160, 260, 160], fill=(255, 255, 255, 255), width=6) # mattress
    draw.line([140, 100, 140, 190], fill=(156, 163, 175, 255), width=6) # headboard
    draw.line([260, 130, 260, 190], fill=(156, 163, 175, 255), width=6) # footboard
    draw.rectangle([150, 130, 180, 160], fill=(59, 130, 246, 255)) # pillow

def draw_kitchen_pot(draw, w, h):
    # Lesson 10: Kök
    draw.rectangle([150, 110, 250, 180], fill=(156, 163, 175, 255)) # pot body
    draw.line([120, 130, 150, 130], fill=(156, 163, 175, 255), width=6) # handle
    draw.line([170, 100, 230, 100], fill=(255, 255, 255, 255), width=5) # lid

def draw_chair(draw, w, h):
    # Lesson 10: Stol
    draw.line([160, 140, 220, 140], fill=(255, 255, 255, 255), width=6) # seat
    draw.line([160, 90, 160, 190], fill=(255, 255, 255, 255), width=6) # backrest & backleg
    draw.line([220, 140, 220, 190], fill=(255, 255, 255, 255), width=6) # front leg

def draw_shoes(draw, w, h):
    # Lesson 11: Skor
    draw.rectangle([150, 130, 190, 170], fill=(79, 70, 229, 255))
    draw.rectangle([210, 130, 250, 170], fill=(79, 70, 229, 255))

def draw_sweater(draw, w, h):
    # Lesson 11: Tröja
    draw.rectangle([160, 90, 240, 170], fill=(219, 39, 119, 255)) # torso
    draw.rectangle([120, 90, 160, 130], fill=(219, 39, 119, 255)) # left sleeve
    draw.rectangle([240, 90, 280, 130], fill=(219, 39, 119, 255)) # right sleeve

def draw_beanie(draw, w, h):
    # Lesson 11: Mössa
    draw.ellipse([150, 80, 250, 180], fill=(16, 185, 129, 255))
    draw.ellipse([190, 65, 210, 85], fill=(255, 255, 255, 255)) # pompom
    draw.rectangle([130, 140, 270, 180], fill=(27, 34, 52, 255)) # mask out bottom

def draw_blackboard(draw, w, h):
    # Lesson 12: Lärare
    draw.rectangle([140, 70, 260, 170], outline=(120, 113, 108, 255), width=6)
    draw.rectangle([145, 75, 255, 165], fill=(6, 78, 59, 255))
    font = get_font(28)
    draw.text((165, 95), "A B C", fill=(255, 255, 255, 255), font=font)

def draw_red_cross(draw, w, h):
    # Lesson 12: Läkare
    draw.rectangle([185, 65, 215, 155], fill=(239, 68, 68, 255))
    draw.rectangle([155, 95, 245, 125], fill=(239, 68, 68, 255))

def draw_grad_cap(draw, w, h):
    # Lesson 12: Student
    draw.polygon([(200, 70), (270, 100), (200, 130), (130, 100)], fill=(0, 0, 0, 255))
    draw.rectangle([170, 115, 230, 140], fill=(0, 0, 0, 255))
    draw.line([270, 100, 280, 140], fill=(255, 205, 0, 255), width=3) # tassel

def draw_arrow_left(draw, w, h):
    # Lesson 13: Jag (Me / Arrow Left)
    draw.line([140, 120, 260, 120], fill=(255, 255, 255, 255), width=6)
    draw.polygon([(140, 120), (170, 95), (170, 145)], fill=(255, 255, 255, 255))

def draw_arrow_right(draw, w, h):
    # Lesson 13: Du (You / Arrow Right)
    draw.line([140, 120, 260, 120], fill=(255, 255, 255, 255), width=6)
    draw.polygon([(260, 120), (230, 95), (230, 145)], fill=(255, 255, 255, 255))

def draw_group(draw, w, h):
    # Lesson 13: Vi (We)
    draw.ellipse([150, 90, 190, 130], fill=(59, 130, 246, 255))
    draw.ellipse([210, 90, 250, 130], fill=(59, 130, 246, 255))
    draw.ellipse([180, 70, 220, 110], fill=(255, 205, 0, 255))

def draw_cutlery(draw, w, h):
    # Lesson 14: Äta
    # Fork
    draw.line([160, 80, 160, 160], fill=(255, 255, 255, 255), width=5)
    draw.line([150, 80, 170, 80], fill=(255, 255, 255, 255), width=5)
    draw.line([150, 70, 150, 80], fill=(255, 255, 255, 255), width=4)
    draw.line([160, 70, 160, 80], fill=(255, 255, 255, 255), width=4)
    draw.line([170, 70, 170, 80], fill=(255, 255, 255, 255), width=4)
    # Knife
    draw.polygon([(230, 80), (245, 80), (245, 140), (230, 140)], fill=(255, 255, 255, 255))
    draw.line([238, 140, 238, 170], fill=(156, 163, 175, 255), width=5)

def draw_cup(draw, w, h):
    # Lesson 14: Dricka
    # Glass outline
    draw.polygon([(160, 80), (240, 80), (220, 170), (180, 170)], outline=(255, 255, 255, 255), width=4)
    # Drink level
    draw.polygon([(168, 110), (232, 110), (220, 170), (180, 170)], fill=(56, 189, 248, 255))

def draw_open_book(draw, w, h):
    # Lesson 14: Läsa
    draw.rectangle([140, 90, 200, 170], fill=(255, 255, 255, 255))
    draw.rectangle([200, 90, 260, 170], fill=(255, 255, 255, 255))
    # Book spine line
    draw.line([200, 90, 200, 170], fill=(0, 75, 135, 255), width=4)

def draw_question_mark(draw, w, h):
    # Lesson 15: Fråga
    font = get_font(100)
    draw.text((180, 60), "?", fill=(255, 205, 0, 255), font=font)

def draw_checkmark(draw, w, h):
    # Lesson 15: Ja
    draw.line([150, 120, 190, 160], fill=(34, 197, 94, 255), width=10)
    draw.line([190, 160, 260, 80], fill=(34, 197, 94, 255), width=10)

def draw_cross_mark(draw, w, h):
    # Lesson 15: Nej
    draw.line([150, 80, 250, 180], fill=(239, 68, 68, 255), width=10)
    draw.line([250, 80, 150, 180], fill=(239, 68, 68, 255), width=10)

def draw_big_square(draw, w, h):
    # Lesson 16: Stor
    draw.rectangle([130, 60, 270, 200], outline=(255, 255, 255, 255), width=5)

def draw_small_square(draw, w, h):
    # Lesson 16: Liten
    draw.rectangle([185, 115, 215, 145], outline=(255, 255, 255, 255), width=5)

def draw_smile(draw, w, h):
    # Lesson 16: Glad
    draw.ellipse([150, 60, 250, 160], outline=(255, 205, 0, 255), width=5)
    draw.ellipse([175, 90, 190, 105], fill=(255, 205, 0, 255))
    draw.ellipse([210, 90, 225, 105], fill=(255, 205, 0, 255))
    draw.arc([175, 100, 225, 140], 0, 180, fill=(255, 205, 0, 255), width=5)

def draw_price_tag(draw, w, h):
    # Lesson 17: Pris
    draw.polygon([(150, 120), (180, 80), (250, 80), (250, 160), (180, 160)], outline=(255, 255, 255, 255), width=4)
    draw.ellipse([180, 115, 190, 125], fill=(255, 205, 0, 255))

def draw_money(draw, w, h):
    # Lesson 17: Pengar
    draw.rectangle([140, 80, 260, 160], outline=(16, 185, 129, 255), width=4)
    font = get_font(50)
    draw.text((185, 90), "$", fill=(16, 185, 129, 255), font=font)

def draw_coffee_mug(draw, w, h):
    # Lesson 17: Kaffe
    draw.rectangle([150, 100, 230, 180], fill=(234, 179, 8, 255)) # cup
    draw.arc([210, 115, 255, 165], 270, 90, fill=(255, 255, 255, 255), width=5) # handle
    # Steam lines
    draw.line([170, 70, 170, 90], fill=(156, 163, 175, 255), width=3)
    draw.line([190, 60, 190, 90], fill=(156, 163, 175, 255), width=3)
    draw.line([210, 70, 210, 90], fill=(156, 163, 175, 255), width=3)

def draw_bus(draw, w, h):
    # Lesson 18: Buss
    draw.rectangle([140, 90, 260, 160], fill=(219, 39, 119, 255)) # bus body
    draw.ellipse([160, 155, 185, 180], fill=(0, 0, 0, 255)) # wheel 1
    draw.ellipse([215, 155, 240, 180], fill=(0, 0, 0, 255)) # wheel 2
    # Windows
    draw.rectangle([150, 100, 180, 120], fill=(255, 255, 255, 255))
    draw.rectangle([190, 100, 220, 120], fill=(255, 255, 255, 255))

def draw_train(draw, w, h):
    # Lesson 18: Tåg
    draw.rectangle([140, 100, 260, 160], fill=(30, 41, 59, 255), outline=(255, 255, 255, 255), width=3)
    draw.line([120, 170, 280, 170], fill=(156, 163, 175, 255), width=4) # rail

def draw_airplane(draw, w, h):
    # Lesson 18: Flygplan
    draw.line([140, 130, 260, 130], fill=(255, 255, 255, 255), width=8) # fuselage
    draw.line([200, 80, 200, 180], fill=(255, 255, 255, 255), width=8) # wings
    draw.polygon([(140, 130), (130, 115), (130, 145)], fill=(255, 255, 255, 255)) # tail

def draw_orange(draw, w, h):
    # Lesson 19: Apelsin (Orange)
    draw.ellipse([150, 70, 250, 170], fill=(249, 115, 22, 255)) # Orange circle
    draw.ellipse([195, 60, 205, 70], fill=(34, 197, 94, 255)) # Leaf

def draw_small_house(draw, w, h):
    # Lesson 19: Ett hus
    draw.rectangle([150, 120, 250, 180], fill=(239, 68, 68, 255)) # red body
    draw.polygon([(140, 120), (200, 70), (260, 120)], fill=(120, 113, 108, 255)) # roof
    draw.rectangle([185, 140, 215, 180], fill=(255, 255, 255, 255)) # door

def draw_girl_silhouette(draw, w, h):
    # Lesson 19: En flicka
    draw.ellipse([190, 70, 210, 90], fill=(244, 63, 94, 255)) # head
    draw.polygon([(170, 150), (230, 150), (200, 95)], fill=(244, 63, 94, 255)) # dress triangle

def draw_clock_now(draw, w, h):
    # Lesson 20: Nutid
    draw.ellipse([150, 60, 250, 160], outline=(255, 255, 255, 255), width=4)
    draw.line([200, 110, 200, 70], fill=(34, 197, 94, 255), width=4) # hand pointing straight up (12)

def draw_clock_past(draw, w, h):
    # Lesson 20: Dåtid
    draw.ellipse([150, 60, 250, 160], outline=(255, 255, 255, 255), width=4)
    draw.line([200, 110, 165, 110], fill=(239, 68, 68, 255), width=4) # hand pointing left (9)

def draw_clock_future(draw, w, h):
    # Lesson 20: Framtid
    draw.ellipse([150, 60, 250, 160], outline=(255, 255, 255, 255), width=4)
    draw.line([200, 110, 235, 110], fill=(59, 130, 246, 255), width=4) # hand pointing right (3)

def draw_plate_utensils(draw, w, h):
    # Lesson 21: Restaurang
    draw.ellipse([160, 80, 240, 160], outline=(255, 255, 255, 255), width=4) # plate
    draw.line([145, 90, 145, 150], fill=(255, 255, 255, 255), width=4) # fork
    draw.line([255, 90, 255, 150], fill=(255, 255, 255, 255), width=4) # knife

def draw_hotel_bed(draw, w, h):
    # Lesson 21: Hotell
    draw.rectangle([140, 110, 260, 170], fill=(59, 130, 246, 255))
    draw.rectangle([140, 110, 160, 170], fill=(156, 163, 175, 255)) # wall board
    font = get_font(20)
    draw.text((180, 75), "HOTEL", fill=(255, 205, 0, 255), font=font)

def draw_hospital(draw, w, h):
    # Lesson 21: Sjukhus
    draw.rectangle([140, 100, 260, 180], fill=(156, 163, 175, 255)) # building
    draw.rectangle([185, 120, 215, 160], fill=(239, 68, 68, 255)) # red cross
    draw.rectangle([195, 110, 205, 170], fill=(239, 68, 68, 255))

def draw_laptop(draw, w, h):
    # Lesson 22: Dator
    draw.rectangle([140, 80, 260, 150], outline=(255, 255, 255, 255), width=4) # screen
    draw.line([120, 160, 280, 160], fill=(156, 163, 175, 255), width=6) # keyboard base

def draw_phone(draw, w, h):
    # Lesson 22: Telefon
    # Telephone receiver curved tube
    draw.arc([140, 90, 260, 190], 180, 360, fill=(255, 255, 255, 255), width=10)

def draw_meeting(draw, w, h):
    # Lesson 22: Möte
    draw.ellipse([160, 100, 240, 150], fill=(120, 113, 108, 255)) # table
    draw.ellipse([150, 120, 165, 135], fill=(255, 255, 255, 255)) # person 1
    draw.ellipse([235, 120, 250, 135], fill=(255, 255, 255, 255)) # person 2
    draw.ellipse([192, 85, 207, 100], fill=(255, 255, 255, 255)) # person 3

def draw_newspaper(draw, w, h):
    # Lesson 23: Tidning
    draw.rectangle([140, 80, 260, 170], outline=(255, 255, 255, 255), width=4)
    draw.line([150, 95, 250, 95], fill=(156, 163, 175, 255), width=4) # headline
    draw.line([150, 115, 250, 115], fill=(156, 163, 175, 255), width=2)
    draw.line([150, 135, 210, 135], fill=(156, 163, 175, 255), width=2)

def draw_signboard(draw, w, h):
    # Lesson 23: Skylt
    draw.line([200, 140, 200, 190], fill=(156, 163, 175, 255), width=6) # pole
    draw.rectangle([130, 70, 270, 140], outline=(255, 255, 255, 255), width=4) # sign board

def draw_microphone(draw, w, h):
    # Lesson 23: Nyheter
    draw.rectangle([185, 110, 215, 180], fill=(75, 85, 99, 255)) # grip
    draw.ellipse([175, 70, 225, 120], fill=(209, 213, 219, 255)) # mic head

def draw_blocks(draw, w, h):
    # Lesson 24: Ord
    # Three word blocks side-by-side
    draw.rectangle([120, 100, 170, 150], outline=(255, 255, 255, 255), width=3)
    draw.rectangle([175, 100, 225, 150], outline=(255, 255, 255, 255), width=3)
    draw.rectangle([230, 100, 280, 150], outline=(255, 255, 255, 255), width=3)
    font = get_font(30)
    draw.text((135, 110), "A", fill=(255, 205, 0, 255), font=font)
    draw.text((190, 110), "B", fill=(255, 205, 0, 255), font=font)
    draw.text((245, 110), "C", fill=(255, 205, 0, 255), font=font)

def draw_pillars(draw, w, h):
    # Lesson 24: Grammatik
    # Structural pillars
    draw.line([160, 160, 240, 160], fill=(255, 255, 255, 255), width=6) # base
    draw.line([180, 80, 180, 160], fill=(255, 255, 255, 255), width=6) # pillar 1
    draw.line([220, 80, 220, 160], fill=(255, 255, 255, 255), width=6) # pillar 2
    draw.line([160, 80, 240, 80], fill=(255, 205, 0, 255), width=6) # arch roof

def draw_pencil(draw, w, h):
    # Lesson 24: Skriva
    # Stylized diagonal pencil drawing line
    draw.line([150, 150, 230, 70], fill=(253, 224, 71, 255), width=8) # body
    draw.polygon([(150, 150), (135, 165), (155, 165)], fill=(255, 255, 255, 255)) # tip

# 24 lessons x 3 matches
ASSETS_DATA = [
    # Lesson 1
    (1, 1, "เสียง โอ (Å)", draw_char_A_ring),
    (1, 2, "เสียง แอ (Ä)", draw_char_A_dots),
    (1, 3, "เสียง เออ (Ö)", draw_char_O_dots),
    # Lesson 2
    (2, 1, "สวัสดี (Hej)", draw_hello),
    (2, 2, "ขอบคุณ (Tack)", draw_tack),
    (2, 3, "ลาก่อน (Hejdå)", draw_bye),
    # Lesson 3
    (3, 1, "ชื่อ (Namn)", draw_id_card),
    (3, 2, "อายุ (Ålder)", draw_cake),
    (3, 3, "ประเทศสวีเดน (Sverige)", draw_flag_sweden),
    # Lesson 4
    (4, 1, "ห้า (Fem)", draw_num5),
    (4, 2, "สิบ (Tio)", draw_num10),
    (4, 3, "ยี่สิบ (Tjugo)", draw_num20),
    # Lesson 5
    (5, 1, "นาฬิกา (Klocka)", draw_clock),
    (5, 2, "วัน (Dag)", draw_calendar),
    (5, 3, "ฤดูหนาว (Vinter)", draw_snowflake),
    # Lesson 6
    (6, 1, "สีแดง (Röd)", draw_red_block),
    (6, 2, "สีน้ำเงิน (Blå)", draw_blue_block),
    (6, 3, "สีเหลือง (Gul)", draw_yellow_block),
    # Lesson 7
    (7, 1, "แม่ (Mamma)", draw_mom),
    (7, 2, "พ่อ (Pappa)", draw_dad),
    (7, 3, "ลูก/เด็ก (Barn)", draw_child),
    # Lesson 8
    (8, 1, "แมว (Katt)", draw_cat),
    (8, 2, "สุนัข (Hund)", draw_dog),
    (8, 3, "นก (Fågel)", draw_bird),
    # Lesson 9
    (9, 1, "แอปเปิ้ล (Äpple)", draw_apple),
    (9, 2, "ขนมปัง (Bröd)", draw_bread),
    (9, 3, "นม (Mjölk)", draw_milk),
    # Lesson 10
    (10, 1, "เตียงนอน (Säng)", draw_bed),
    (10, 2, "ห้องครัว (Kök)", draw_kitchen_pot),
    (10, 3, "เก้าอี้ (Stol)", draw_chair),
    # Lesson 11
    (11, 1, "รองเท้า (Skor)", draw_shoes),
    (11, 2, "เสื้อกันหนาว (Tröja)", draw_sweater),
    (11, 3, "หมวกไหมพรม (Mössa)", draw_beanie),
    # Lesson 12
    (12, 1, "ครู (Lärare)", draw_blackboard),
    (12, 2, "หมอ (Läkare)", draw_red_cross),
    (12, 3, "นักเรียน (Student)", draw_grad_cap),
    # Lesson 13
    (13, 1, "ฉัน (Jag)", draw_arrow_left),
    (13, 2, "คุณ (Du)", draw_arrow_right),
    (13, 3, "พวกเรา (Vi)", draw_group),
    # Lesson 14
    (14, 1, "กิน (Äta)", draw_cutlery),
    (14, 2, "ดื่ม (Dricka)", draw_cup),
    (14, 3, "อ่าน (Läsa)", draw_open_book),
    # Lesson 15
    (15, 1, "คำถาม (Fråga)", draw_question_mark),
    (15, 2, "ใช่ (Ja)", draw_checkmark),
    (15, 3, "ไม่ (Nej)", draw_cross_mark),
    # Lesson 16
    (16, 1, "ใหญ่ (Stor)", draw_big_square),
    (16, 2, "เล็ก (Liten)", draw_small_square),
    (16, 3, "ดีใจ/มีความสุข (Glad)", draw_smile),
    # Lesson 17
    (17, 1, "ราคา (Pris)", draw_price_tag),
    (17, 2, "เงิน (Pengar)", draw_money),
    (17, 3, "กาแฟ (Kaffe)", draw_coffee_mug),
    # Lesson 18
    (18, 1, "รถเมล์ (Buss)", draw_bus),
    (18, 2, "รถไฟ (Tåg)", draw_train),
    (18, 3, "เครื่องบิน (Flygplan)", draw_airplane),
    # Lesson 19
    (19, 1, "ส้ม (Apelsin)", draw_orange),
    (19, 2, "บ้านหลังหนึ่ง (Ett hus)", draw_small_house),
    (19, 3, "เด็กผู้หญิงคนหนึ่ง (En flicka)", draw_girl_silhouette),
    # Lesson 20
    (20, 1, "ปัจจุบัน (Nutid)", draw_clock_now),
    (20, 2, "อดีต (Dåtid)", draw_clock_past),
    (20, 3, "อนาคต (Framtid)", draw_clock_future),
    # Lesson 21
    (21, 1, "ร้านอาหาร (Restaurang)", draw_plate_utensils),
    (21, 2, "โรงแรม (Hotell)", draw_hotel_bed),
    (21, 3, "โรงพยาบาล (Sjukhus)", draw_hospital),
    # Lesson 22
    (22, 1, "คอมพิวเตอร์ (Dator)", draw_laptop),
    (22, 2, "โทรศัพท์ (Telefon)", draw_phone),
    (22, 3, "ประชุม (Möte)", draw_meeting),
    # Lesson 23
    (23, 1, "หนังสือพิมพ์ (Tidning)", draw_newspaper),
    (23, 2, "ป้ายประกาศ (Skylt)", draw_signboard),
    (23, 3, "ข่าวสาร (Nyheter)", draw_microphone),
    # Lesson 24
    (24, 1, "คำศัพท์ (Ord)", draw_blocks),
    (24, 2, "ไวยากรณ์ (Grammatik)", draw_pillars),
    (24, 3, "เขียน (Skriva)", draw_pencil),
]

def main():
    assets_dir = "assets"
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
        print(f"Created directory: {assets_dir}")
        
    print("Generating 72 graphic assets...")
    count = 0
    for lesson_id, index, label, draw_func in ASSETS_DATA:
        filename = f"lesson_{lesson_id}_{index}.png"
        filepath = os.path.join(assets_dir, filename)
        draw_card(filepath, label, draw_func)
        count += 1
        
    print(f"Successfully generated {count} visual assets!")

if __name__ == "__main__":
    main()
