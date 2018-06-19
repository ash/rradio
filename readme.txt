enable SPI in raspi-config

git clone https://github.com/adafruit/Adafruit_Nokia_LCD.git
cd Adafruit_Nokia_LCD/
sudo python3 setup.py install

cd ..
git clone https://github.com/adafruit/Adafruit_Python_GPIO.git
sudo python3 setup.py install
cd ..

sudo apt-get install python-imaging
