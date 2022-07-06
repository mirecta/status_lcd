# Mini display for RatRig or Moonraker

## LCD
I use 240x240 IPS LCD 


## Raspi SPI
dtoverlay spi6-2cs

## Install
put it all to /home/pi
```
sudo cp status-lcd.service /lib/systemd/system/
chmod +x /home/pi/status_lcd/status-lcd.py
sudo systemctl daemon-reload
sudo systemctl enable status-lcd.service
sudo systemctl start status-lcd.service
```
