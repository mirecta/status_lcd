
put it all to /home/pi



sudo cp status-lcd.service /lib/systemd/system/
chmod +x /home/pi/status_lcd/status-lcd.py
sudo systemctl daemon-reload
sudo systemctl enable status-lcd.service
sudo systemctl start status-lcd.service
