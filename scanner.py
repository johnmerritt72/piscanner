#!/usr/bin/env python3
from time import sleep
import RPi.GPIO as GPIO
import sys
import tty
import time
import picamera
import pygame
import io
import sqlite3

conn = sqlite3.connect('scanner2.db')
c = conn.cursor()
c.execute('SELECT frameNumber, savePath, iso, shutterSpeed, brightness, AwbMode, awb1, awb2, isoWidth FROM ScanSettings WHERE id=1')
data = c.fetchall()
for row in data:
    frameNumber = row[0]
    path = row[1]
    #path = '/home/pi/media/'
    iso = row[2]
    shutterSpeed = row[3]
    brightness = row[4]
    awb_mode = row[5]
    awb1 = row[6]
    awb2 = row[7]
    isoWidth = row[8]

DIR = 20     # Direction GPIO pin
STEP = 21    # Step GPIO Pin
CW = 1       # Clockwise Rotation
CCW = 0      # Couterclockwise Rotation
SPR = 200     # Steps per Revolution

unsaved = 0
step_count = SPR
delay = .003
WIDTH = 1024
HEIGHT = 768


#INIT GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)
GPIO.output(DIR, CW)


# INIT CAMERA
camera = picamera.PiCamera()
camera.vflip = False
camera.hflip = False
cameraResX = 2592
cameraResY = 1944
camera.resolution = (cameraResX, cameraResY)
camera.zoom = (0.1, 0, 0.9, 0.9)
camera.framerate = 15
camera.shutter_speed = int(shutterSpeed)
camera.brightness = int(brightness)
camera.exposure_mode = 'auto'
camera.awb_mode = 'off' #'flash' #awb_mode
camera.awb_gains = (awb1, awb2)
camera.iso = int(iso)

# BUILD A SCREEN
pygame.init()
screen = pygame.display.set_mode((WIDTH,HEIGHT))
black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)
textcolor = pygame.Color(255, 255, 0)
pygame.display.set_caption('RASPBERRY PI 8mm SCANNER')
screen.fill(black)
#screen = screen.convert()

x = (screen.get_width() - camera.resolution[0]) / 2
y = (screen.get_height() - camera.resolution[1]) / 2

# Init buffer
rgb1 = bytearray(camera.resolution[0] * camera.resolution[1] * 3)
rgb2 = bytearray(camera.resolution[0] * camera.resolution[1] * 3)
rgb3 = bytearray(camera.resolution[0] * camera.resolution[1] * 3)


def getTitle():
    global unsaved
    title = "RASPBERRY PI 8mm SCANNER"
    if unsaved == 1:
         title = title + '*'
    return title

def displayMenu():
    # Instructions for when the user has an interface
    ypos = 20
    xpos = 20
    yspacing = 60
    font = pygame.font.Font(None, 40)

    title = getTitle()
    text = font.render(title, True, textcolor, black)
    screen.blit(text, (xpos, ypos))
    ypos += yspacing
    font = pygame.font.Font(None, 30)
    yspacing = 30

    text = font.render("a: Advance film one image", True, textcolor, black)
    screen.blit(text, (xpos, ypos))
    ypos += yspacing

    text = font.render("r: Rewind film one image", True, textcolor, black)
    screen.blit(text, (xpos, ypos))
    ypos += yspacing

    text = font.render("n: Change FrameNumber ({})".format(frameNumber), True, textcolor, black)
    screen.blit(text, (xpos, ypos))
    ypos += yspacing

    text = font.render("s: Save photo", True, textcolor, black)
    screen.blit(text, (xpos, ypos))
    ypos += yspacing

    text = font.render("c: Start Capture!", True, textcolor, black)
    screen.blit(text, (xpos, ypos))
    ypos += yspacing

    text = font.render("w: Write settings to DB", True, textcolor, black)
    screen.blit(text, (xpos, ypos))
    ypos += yspacing

    text = font.render("q: Quit", True, textcolor, black)
    screen.blit(text, (xpos, ypos))
    ypos += yspacing

    font = pygame.font.Font(None, 20)
    text = font.render("iso: " + str(iso) + ", shutterSpeed: " + str(shutterSpeed) + ", brightness: " + str(brightness) + ", AWB: " + str(awb1) + ", " + str(awb2) + ", path: " + path , True, textcolor, black)
    screen.blit(text, (xpos, 740))

    pygame.display.update()


def captureMenu():
    # Instructions for when the user has an interface
    ypos = 20
    xpos = 20
    yspacing = 60
    font = pygame.font.Font(None, 40)
    title = getTitle()
    text = font.render(title, True, textcolor, black)

    screen.blit(text, (xpos, ypos))
    ypos += yspacing
    font = pygame.font.Font(None, 30)
    yspacing = 30

    text = font.render("Capturing: frame {}".format(frameNumber), True, textcolor, black)
    screen.blit(text, (xpos, ypos))
    ypos += yspacing

    text = font.render("s: Stop (can resume)", True, textcolor, black)
    screen.blit(text, (xpos, ypos))
    ypos += yspacing

    font = pygame.font.Font(None, 20)
    text = font.render("iso: " + str(iso) + ", shutterSpeed: " + str(shutterSpeed) + ", brightness: " + str(brightness), True, textcolor, black)
    screen.blit(text, (xpos, 740))

    pygame.display.update()


def TakePhoto():
     # TAKE A PHOTO
    #camera.zoom = (0.2, 0.2, 0.8, 0.8)
    #camera.zoom = (0.15, 0.05, 0.7, 0.7)
    camera.start_preview()
    sleep(0.5)
    filename = "frame{:05d}.jpg".format(frameNumber)
    camera.capture(path + filename, format='jpeg', quality=100)
    screen.fill(black)
    pygame.display.update()
    camera.stop_preview()

    #READ IMAGE AND PUT ON SCREEN
    img = pygame.image.load(path + filename)
    screen.blit(img, (0, 0))
    font = pygame.font.Font(None, 20)
    text = font.render(filename, True, textcolor, black)
    screen.blit(text, (850, 740))
    displayMenu()
    pygame.display.update()


def TakePhotos():
     # TAKE THREE PHOTOS
    #camera.zoom = (0.2, 0.2, 0.8, 0.8)
    #camera.zoom = (0.15, 0.05, 0.7, 0.7)
    camera.start_preview()

    camera.shutter_speed = getShutterSpeed(1)
    sleep(0.5)
    filename = "frame{:05d}A.jpg".format(frameNumber)
    camera.capture(path + filename, format='jpeg', quality=100)
    screen.fill(black)
    pygame.display.update()

    camera.shutter_speed = getShutterSpeed(2)
    sleep(0.5)
    filename = "frame{:05d}B.jpg".format(frameNumber)
    camera.capture(path + filename, format='jpeg', quality=100)
    screen.fill(black)
    pygame.display.update()

    camera.shutter_speed = getShutterSpeed(3)
    sleep(0.5)
    filename = "frame{:05d}C.jpg".format(frameNumber)
    camera.capture(path + filename, format='jpeg', quality=100)
    screen.fill(black)
    pygame.display.update()

    camera.stop_preview()




    
def CapturePhotos():
    quitPressed = 0
    global frameNumber
    global unsaved
    global shutterSpeed
    global iso
    global path
    #camera.zoom = (0.2, 0.2, 0.8, 0.8)
    #camera.zoom = (0.14, 0, 0.8, 0.8)
    #camera.zoom = (0.15, 0, 0.9, 0.9)
    camera.start_preview()
    camera.shutter_speed = getShutterSpeed(2)
    camera.iso = int(iso)
    sleep(0.5)

    while (quitPressed == 0):
        camera.shutter_speed = getShutterSpeed(2)
        camera.iso = int(iso)
        odd = 'A'
        #if (frameNumber % 1) == 0:
        #    odd = 'B'
        #if frameNumber == 20000:
        #    path = path[0:-1]+"b/"
        filename = "frame"+odd+"{:05d}.jpg".format(frameNumber)
        camera.capture(path + filename, format='jpeg', quality=100)
	frameNumber = frameNumber + 1
        c.execute('UPDATE ScanSettings SET savePath="' + path + '", frameNumber=' + str(frameNumber) +' WHERE id=1')
        conn.commit()
        screen.fill(black)
        #pygame.display.update()

        img = pygame.image.load(path + filename)
        screen.blit(img, (-200, 100))
        font = pygame.font.Font(None, 20)
        text = font.render(filename, True, textcolor, black)
        screen.blit(text, (850, 740))
        captureMenu()
        pygame.display.update()
        AdvanceFrame()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quitPressed = 1
            if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                quitPressed = 1
            if event.type == pygame.KEYDOWN and event.key == pygame.K_5:
                shutterSpeed = int(shutterSpeed) + 500
                unsaved = 1
            if event.type == pygame.KEYDOWN and event.key == pygame.K_6:
                shutterSpeed = int(shutterSpeed) - 500
                unsaved = 1
            if event.type == pygame.KEYDOWN and event.key == pygame.K_7:
                iso = int(iso) + 100
                unsaved = 1
            if event.type == pygame.KEYDOWN and event.key == pygame.K_8:
                iso = int(iso) - 100
                unsaved = 1
            if event.type == pygame.KEYDOWN and event.key == pygame.K_w:
                saveSettings()
            pygame.event.pump()

    camera.stop_preview()


def CapturePhotosBracketed():
    quitPressed = 0
    #camera.zoom = (0.15, 0.05, 0.7, 0.7)
    camera.start_preview()
    sleep(0.5)
    global frameNumber
    while (quitPressed == 0):
        camera.shutter_speed = getShutterSpeed(1)
        frameNumber = frameNumber + 1
        filename = "frame{:05d}a.jpg".format(frameNumber)
        camera.capture(path + filename, format='jpeg', quality=100)

        camera.shutter_speed = getShutterSpeed(2)
        filename = "frame{:05d}b.jpg".format(frameNumber)
        camera.capture(path + filename, format='jpeg', quality=100)

        img = pygame.image.load(path + filename)
        screen.blit(img, (0, 0))
        font = pygame.font.Font(None, 20)
        text = font.render(filename, True, textcolor, black)
        screen.blit(text, (850, 740))
        captureMenu()

        camera.shutter_speed = getShutterSpeed(3)
        filename = "frame{:05d}c.jpg".format(frameNumber)
        camera.capture(path + filename, format='jpeg', quality=100)

        screen.fill(black)
        pygame.display.update()

        c.execute('UPDATE ScanSettings SET frameNumber=' + frameNumber +' WHERE id=1')
        conn.commit()
        AdvanceFrame()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quitPressed = 1
            if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                quitPressed = 1
            pygame.event.pump()

    camera.stop_preview()



def saveSettings():
    global unsaved
    global awb1
    global awb2
    global shutterSpeed
    c.execute('INSERT INTO ScanSettings (frameNumber,savePath,iso,shutterSpeed,brightness,AwbMode,awb1,awb2,isoWidth,ModifiedTS) SELECT frameNumber,savePath,iso,shutterSpeed,brightness,AwbMode,awb1,awb2,isoWidth,ModifiedTS FROM ScanSettings WHERE id=1')
    conn.commit()
    c.execute('UPDATE ScanSettings SET iso=' + str(iso) + ', awb1=' + str(awb1) +', awb2=' + str(awb2) + ', shutterSpeed=' + str(shutterSpeed) + ', ModifiedTS=CURRENT_TIMESTAMP WHERE id=1')
    conn.commit()
    unsaved = 0



def AdvanceFrame(count = 1):
    GPIO.output(DIR, CW)
    for y in range(count):
        for x in range(step_count):
            GPIO.output(STEP, GPIO.HIGH)
            sleep(delay)
            GPIO.output(STEP, GPIO.LOW)
            sleep(delay)

def RewindFrame(count = 1):
    GPIO.output(DIR, CCW)
    for y in range(count):
        for x in range(step_count):
            GPIO.output(STEP, GPIO.HIGH)
            sleep(delay)
            GPIO.output(STEP, GPIO.LOW)
            sleep(delay)

def getShutterSpeed(i):
    return int(shutterSpeed) + (i-1)*isoWidth

def main_loop():
    quitPressed = 0
    # This is the main loop - do forever
    font = pygame.font.Font(None, 20)
    global awb1
    global awb2
    global shutterSpeed
    global unsaved
    global iso

    camera.iso = int(iso)
    camera.shutter_speed = getShutterSpeed(2)
    camera.start_preview()
    sleep(1.5)

    while (quitPressed == 0):
        
        #camera.zoom = (0.14, 0.1, 0.8, 0.8)
        x = 20
        y = 260
        xsize = 800
        ysize = 480
        screen.fill(0)
        stream2 = io.BytesIO()
        camera.iso = int(iso)
        camera.shutter_speed = getShutterSpeed(2)

        camera.capture(stream2, use_video_port=True, format='rgb')
        stream2.seek(0)
        stream2.readinto(rgb2)

        img2 = pygame.image.frombuffer(rgb2[0:
          (camera.resolution[0] * camera.resolution[1] * 3)],
           camera.resolution, 'RGB')
        if img2:
            screen.blit(pygame.transform.scale(img2, (xsize, ysize)), (x+xsize*(1-1),y))

        displayMenu()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quitPressed = 1
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                quitPressed = 1
            if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
                AdvanceFrame()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                RewindFrame()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                TakePhotos()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                CapturePhotos()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_1:
                awb1 = awb1 + 0.01
                unsaved = 1
                camera.awb_gains = (awb1, awb2)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_2:
                awb1 = awb1 - 0.05
                unsaved = 1
                camera.awb_gains = (awb1, awb2)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_3:
                awb2 = awb2 + 0.01
                unsaved = 1
                camera.awb_gains = (awb1, awb2)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_4:
                awb2 = awb2 - 0.05
                unsaved = 1
                camera.awb_gains = (awb1, awb2)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_5:
                shutterSpeed = int(shutterSpeed) + 500
                unsaved = 1
            if event.type == pygame.KEYDOWN and event.key == pygame.K_6:
                shutterSpeed = int(shutterSpeed) - 500
                unsaved = 1
            if event.type == pygame.KEYDOWN and event.key == pygame.K_7:
                iso = int(iso) + 100
                unsaved = 1
            if event.type == pygame.KEYDOWN and event.key == pygame.K_8:
                iso = int(iso) - 100
                unsaved = 1
            if event.type == pygame.KEYDOWN and event.key == pygame.K_w:
                saveSettings()
            pygame.event.pump()


main_loop()

# Shutdown things after mail_loop exit
camera.close()
pygame.quit()



