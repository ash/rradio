import Adafruit_Nokia_LCD as LCD
import Adafruit_GPIO.SPI as SPI

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

import RPi.GPIO as GPIO

import urllib.request
import re
import time
import json
import os

font1 = ImageFont.truetype("fonts/Minecraftia-Regular.ttf", 8)
font2 = font1

def print_msg(msg):
    disp.clear()
    #disp.display()

    image = Image.new('1', (LCD.LCDWIDTH, LCD.LCDHEIGHT))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, LCD.LCDWIDTH,LCD.LCDHEIGHT), outline=255, fill=255)

    for m in msg:        
        draw.text((m[0], m[1]), m[2], font=m[3])

    disp.image(image)
    disp.display()

def genre_name_msg(name, direction):
    ret = [[0, 0, "Выбор жанра " + direction, font1]]
    y = 15
    if len(name) > 15:
        for word in name.split():
            ret.append([0, y, word.title(), font2])
            y += 9
    else:
        ret.append([0, y, name.title(), font2])
    return ret

def station_name_msg(name):
    ret = [[0, 0, "Выбор станции", font1],
           [0, 35, "~" + genres[curr_genre].title() + "~", font1]]
    y = 15
    if len(name) > 15:
        for word in name.split():
            ret.append([0, y, word.title(), font2])
            y += 9
    else:
        ret.append([0, y, name.title(), font2])
    return ret

DC = 23
RST = 24
SPI_PORT = 0
SPI_DEVICE = 0

disp = LCD.PCD8544(DC, RST, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=4000000))
disp.begin(contrast=200)

disp.clear()
disp.display()

led_pin = 21
#GPIO.setmode(GPIO.BOARD)
GPIO.setup(led_pin, GPIO.OUT)
GPIO.output(led_pin, 1)

light = GPIO.PWM(led_pin, 300)
light.start(100)

btn_genre_less = 19
btn_genre_more = 26
GPIO.setup(btn_genre_less, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(btn_genre_more, GPIO.IN, pull_up_down=GPIO.PUD_UP)

btn_station_less = 6
btn_station_more = 13
GPIO.setup(btn_station_less, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(btn_station_more, GPIO.IN, pull_up_down=GPIO.PUD_UP)


radio = dict()
stations = dict()

with open('stations.json') as json_file:
    radio = json.load(json_file)

genres = sorted(radio.keys())

for genre in genres:
    genre_stations = radio[genre]
    for station in genre_stations:
        stations[station[0]] = station[1]

print_msg([[20, 0, 'Готово!', font1], 
           [2, 15, 'Жанров:  ' + str(len(genres)), font1],
           [2, 25, 'Станций:  ' + str(len(stations)), font1]
         ])

curr_genre = 0
curr_station = 0

idle_time = 0
light_time = 0
idle_max = 5
is_in_selection = 0
station_chosen = 0
stations_in_genre = radio[genres[curr_genre]]

state_file = 'rradio.json'

if os.path.exists(state_file):
    print('???')
    with open(state_file) as json_file:
        state = json.load(json_file)
        curr_genre = state["genre"]
        curr_station = state["station"]
        stations_in_genre = radio[genres[curr_genre]]

        print_msg([
            [0, 0, 'Вы слушаете', font1],
            [0, 15, stations_in_genre[curr_station][0].title(), font1]
        ])
        time.sleep(2)
        os.system("/usr/bin/mplayer -ao alsa:device=hw=1,0 " + stations_in_genre[curr_station][1] + " & ")

while 1:
    genre_less = GPIO.input(btn_genre_less);
    if genre_less == 0:
        idle_time = 0
        idle_max = 30
        is_in_selection = 0

        light_time = 0
        light.start(100)

        curr_genre -= 1
        if curr_genre < 0:
            curr_genre = len(genres) - 1
        print_msg(genre_name_msg(genres[curr_genre], '←'))
        curr_station = 0
        stations_in_genre = radio[genres[curr_genre]]

    genre_more = GPIO.input(btn_genre_more);
    if genre_more == 0:
        idle_time = 0
        idle_max = 30
        is_in_selection = 0

        light_time = 0
        light.start(100)

        curr_genre += 1
        if curr_genre >= len(genres):
            curr_genre = 0
        print_msg(genre_name_msg(genres[curr_genre], '→'))
        curr_station = 0
        stations_in_genre = radio[genres[curr_genre]]

    station_less = GPIO.input(btn_station_less);
    if station_less == 0:
        idle_time = 0
        idle_max = 5
        is_in_selection = 1

        light_time = 0
        light.start(100)

        curr_station -= 1
        if curr_station < 0:
            curr_station = len(stations_in_genre) - 1
        print_msg(station_name_msg(stations_in_genre[curr_station][0]))

    station_more = GPIO.input(btn_station_more);
    if station_more == 0:
        idle_time = 0
        idle_max = 5
        is_in_selection = 1
        
        light_time = 0
        light.start(100)

        curr_station += 1
        if curr_station >= len(stations_in_genre):
            curr_station = 0
        print_msg(station_name_msg(stations_in_genre[curr_station][0]))

    time.sleep(0.2)
    idle_time += 1
    light_time += 1

    if idle_time > idle_max:   
        idle_time = 0
        if station_chosen:
            print_msg([
                [0, 0, 'Вы слушаете', font1],
                [0, 15, stations_in_genre[curr_station][0].title(), font1],
                #[0, 35, genres[curr_genre].title(), font1]
            ])

        if is_in_selection:
            is_in_selection = 0
            station_chosen = 1

            print("/usr/bin/mplayer " + stations_in_genre[curr_station][1])
            os.system("/usr/bin/killall mplayer");
            os.system("/usr/bin/mplayer -ao alsa:device=hw=1,0 " + stations_in_genre[curr_station][1] + " & ")

            state = {"genre": curr_genre, "station": curr_station}
            with open(state_file, 'w') as json_file:
               json.dump(state, json_file)

    if light_time > idle_max * 3:        
        duty = 100 - (light_time - idle_max * 3)
        if duty > 100:
            duty = 100
        elif duty < 0:
            duty = 0
            light.start(0)
        elif duty > 0:
            light.start(duty)        
