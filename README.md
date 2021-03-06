# piscanner
This project is a film scanner for Raspberry Pi connected to a modified 8mm/16mm projector. 

[![Projector](/images/PXL_20211229_205324505.jpg)](https://raw.githubusercontent.com/johnmerritt72/piscanner/main/images/PXL_20211229_205324505.jpg)
The scanner runs on a Raspberry Pi 3 Model B with an attached v1 camera.  The camera uses a 9-22mm zoom lens in order to magnify the tiny 8mm film sufficiently. The film runs through a modified Bell & Howell Super 8/8mm film projector.  The Pi and camera are mounted to the projector, which has been stripped of its motor, fan, light, and other non-essential parts.  A small LED light is aimed through the front of the projector lens to illuminate the film.  The use of LED reduces power and more importantly the heat generated by the original projector lightbulb, which could literally melt the film if left focused on one frame for very long.

An Adafruit NEMA-17 stepper motor is connected to the Raspberry Pi using a small breadboard and a DRV8825 stepper motor driver and mounted to the projector such that one revolution of the motor advances exactly one frame of film.

The Pi runs the Python script in this repository, which captures a frame of the film and writes it as a JPEG file to a specified folder on an external hard drive. It then advances the film by one frame using the stepper motor, increments the filename by one number, and repeats the process.  The python code uses the Pygame package for its user interface.  Pygame is helpful as it allows a preview of the camera to be visible over VNC/remote desktop and can composite text and images together on the display.  The script uses a SQLlite database to store several user-customizable settings as well as keep track of the current frame number when capturing the film.

The capture process runs at about 26 frames per minute, which for 8mm film at 16 fps means over one and half minutes of footage is captured per hour.

Once all frames have been captured, a separate script using ffmpeg is called that crops the captured images and converts them into an mp4 video file.

#### References:
https://makersportal.com/blog/raspberry-pi-stepper-motor-control-with-nema-17

#### Products purchased:
Raspberry Pi: https://www.amazon.com/gp/product/B01LPLPBS8/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1  
Pi Camera: https://www.amazon.com/gp/product/B07PQ63D2S/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1  
Pi Heatsink: https://www.amazon.com/gp/product/B076ZH6X9L/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1  
Standoffs: https://www.amazon.com/gp/product/B07KM27KC6/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1  
Stepper motor: https://www.amazon.com/gp/product/B01N30ISYC/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1  
DRV8825 stepper driver: https://www.amazon.com/gp/product/B07KZ6K11H/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1  
Stepper motor bracket: https://www.amazon.com/gp/product/B07F8RLPBC/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1  
Stepepr motor heatsink: https://www.amazon.com/gp/product/B01HSBM72W/ref=ppx_yo_dt_b_asin_title_o08_s00?ie=UTF8&psc=1  
Motor shaft coupler: https://www.amazon.com/gp/product/B06X9W7V75/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1  
LED Clamp Light: https://www.amazon.com/gp/product/B078V111B7/ref=ppx_yo_dt_b_asin_title_o06_s00?ie=UTF8&psc=1  
