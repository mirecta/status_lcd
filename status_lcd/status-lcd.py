#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import time
from time import sleep
import logging
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import ST7789

import requests

THUMB_DIR="/home/pi/gcode_files/.thumbs"
LOGO="/home/pi/status_lcd/ratrig.jpg"
CROP_PERC_HEIGHT=8

class Display:

    def __init__(self):
        self.ds = ST7789.ST7789(
        height=240,
        rotation=180,
        port=6,
         # BG_SPI_CS_BACK or BG_SPI_CS_FRONT
        cs=0,
        dc=13,
        rst=26,
        mode=3,
        backlight=6,               # 18 for back BG slot, 19 for front BG slot.
        spi_speed_hz=80 * 1000 * 1000,
        offset_left=0,
        offset_top=0
        )
        self.ds.begin()
        self.img = img = Image.new('RGB', (self.ds.width,self.ds.height), color=(0, 0, 0))
        self.draw = ImageDraw.Draw(img)
        self.font10 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        self.font30 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 35)
        self.state = ""
        self.eraseHeight = self.ds.height


    def clear(self,full = False):
        if full == False:
            self.draw.rectangle((0, 0, self.ds.width, self.eraseHeight), (0, 0, 0))
        else:
            self.draw.rectangle((0, 0, self.ds.width, self.ds.height), (0, 0, 0))

    def sync(self):
        self.ds.display(self.img)
        

    def drawLogo(self):
        im = Image.open(LOGO)
        self.img.paste(im,(0,self.ds.height - 150))
        self.eraseHeight = self.ds.height - 150

    def drawThumb(self,img):
        im = Image.open(f"{THUMB_DIR}/{img}-400x300.png")
        cropHeight = int(im.height * (CROP_PERC_HEIGHT/100.))
        im = im.crop((0,cropHeight,im.width,im.height - cropHeight))

        aspect = im.height / im.width
        newHeight = int(aspect*self.ds.width)
        #print(f"{self.ds.width},{newHeight}")
        im = im.resize((self.ds.width,newHeight),Image.LANCZOS)
        self.img.paste(im,(0,self.ds.height - newHeight),mask = im.split()[3]) 
        self.eraseHeight = self.ds.height - newHeight

    def refresh(self):
        try:
            res = requests.get(url="http://localhost/printer/objects/query?print_stats&gcode_move&heater_bed&extruder&display_status")
            data = res.json()
            position = data['result']['status']['gcode_move']['position']
            stats =  data['result']['status']['print_stats']
            ex = data['result']['status']['extruder']
            hb = data['result']['status']['heater_bed']
            progress = int(data['result']['status']['display_status']['progress']*100)
            #print(data)  
            self.clear()
            #write position
            self.draw.text((0,0), f"X:{position[0]:4.1f}, Y:{position[1]:4.1f}, Z:{position[2]:4.1f} ", font=self.font10, fill=(255, 255, 255))
            self.draw.text((0,20), f"T:{ex['temperature']:.0f}/{ex['target']:.0f}°C, B:{hb['temperature']:.0f}/{hb['target']:.0f}°C", font=self.font10, fill=(255, 255, 255))
            if(stats['state'] == 'printing'):
                msg = f"{progress}%"
                size_x, size_y = self.draw.textsize(msg, self.font30)
                self.draw.text(((self.ds.width - size_x)/2,40), msg, font=self.font30, fill=(255, 255, 255))
                if(self.state != "printing"):
                    try:
                        self.drawThumb('.'.join(stats['filename'].split('.')[:-1]))
                    except:
                        self.drawLogo()
                        
                    self.state = "printing"
            else:
                if self.state != 'idle':
                    self.drawLogo()
                    self.state = 'idle'
            self.sync()
        except:
            raise


def main():
    dis = Display()
 
    try:
        while True:
            dis.refresh()
            sleep(1)
    except KeyboardInterrupt as  e:
            logging.info("Stopping...")

if __name__ == "__main__":
    main()
