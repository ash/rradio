import Adafruit_Nokia_LCD as LCD
import Adafruit_GPIO.SPI as SPI

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

import RPi.GPIO as GPIO

import urllib.request
import re
import time
import JSON

font1 = ImageFont.truetype("Minecraftia-Regular.ttf", 8)
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

def genre_name_msg(name):
    ret = [[0, 0, "Выбор жанра", font1]]
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
disp.begin(contrast=60)

disp.clear()
disp.display()

led_pin = 21
#GPIO.setmode(GPIO.BOARD)
GPIO.setup(led_pin, GPIO.OUT)
GPIO.output(led_pin, 1)

btn_genre_less = 26
btn_genre_more = 19

print_msg([[20, 0, 'Привет!', font1], [2, 35, 'Ищу  жанры . . .', font1]])

genres_html = urllib.request.urlopen("https://www.internet-radio.com/stations/").read().decode('utf-8')
genres = re.findall(r'href="/stations/([^/]+)/"', genres_html)

print_msg([[20, 0, 'Привет!', font1], [2, 25, 'Ищу  жанры . . .', font1], [2, 35, 'Ищу   станции . . .', font1]])
#print_msg([[20, 0, 'Привет!', font1], [2, 10, 'Жанров:   ' + str(len(genres)), font2], [2, 35, 'Ищу   станции . . .', font1]])

radio = dict()
all_stations = dict()

done_genres = 0
for genre in genres:
    url = "https://www.internet-radio.com/stations/" + genre.replace(' ', '%20') + '/'
    print(url)
    html = urllib.request.urlopen(url).read().decode('utf-8')
    stations = re.findall(r'href="/station/([^/]+)/"', html)
    stations.sort()

    if len(stations):
        radio[genre] = stations
        for station in stations:
            all_stations[station] = 1

    done_genres += 1
    status = int(100 * done_genres / len(genres))
    print(print_msg([[20, 0, 'Привет!', font1], [2, 15, 'Ищу  жанры . . .', font1], [2, 25, 'Ищу   станции . . .', font1],
    [0, 35, str(status) + ' %', font1]]))

genres = sorted(radio.keys())

station_names = all_stations.keys()
stations_count = len(station_names)

print_msg([[20, 0, 'Готово!', font1], [2, 15, 'Жанров:  ' + str(len(genres)), font1], [2, 25, 'Станций:  ' + str(stations_count), font1]])

GPIO.setup(btn_genre_less, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(btn_genre_more, GPIO.IN, pull_up_down=GPIO.PUD_UP)

curr_genre = -1

while 1:
    genre_less = GPIO.input(btn_genre_less);
    if genre_less == 0:        
        curr_genre -= 1
        if curr_genre < 0:
            curr_genre = len(genres) - 1
        print_msg(genre_name_msg(genres[curr_genre]))

    genre_more = GPIO.input(btn_genre_more);
    if genre_more == 0:        
        curr_genre += 1
        if curr_genre >= len(genres):
            curr_genre = 0
        print_msg(genre_name_msg(genres[curr_genre]))

    time.sleep(0.1)
