# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import ChristmasTree, BlindMaster, BlindTeam
import ledstrip.glob_var

############################################################################ LED
import time
from .utils import is_raspberry_pi

if is_raspberry_pi:
    # noinspection PyUnresolvedReferences
    import RPi.GPIO as GPIO
    import Adafruit_WS2801
    import Adafruit_GPIO.SPI as SPI
    from ledstrip.led_light import wheel

import threading
import pygame  # Need also to do: sudo apt-get install git curl libsdl2-mixer-2.0-0 libsdl2-image-2.0-0 libsdl2-2.0-0

# Configure the count of pixels:
PIXEL_COUNT = 6
 
# Alternatively specify a hardware SPI connection on /dev/spidev0.0:
SPI_PORT   = 0
SPI_DEVICE = 0

thread_running = False
thread_stop = False


def unicolor(color):
    if is_raspberry_pi:
        LED_power_off()

        for i in range(96):
            pixels.set_pixel(i, color)
            pixels.show()

def rainbow_cycle(pixels, wait=0.005):
    global thread_stop

    for j in range(256): # one cycle of all 256 colors in the wheel
        for i in range(pixels.count()):
            pixels.set_pixel(i, wheel(((i * 256 // pixels.count()) + j) % 256))
        pixels.show()
        if wait > 0:
            time.sleep(wait)
        if thread_stop == True:
            break

def blink_color(pixels, blink_times=5, wait=0.5, color=(255, 0, 0)):
    global thread_stop

    for i in range(blink_times):
        # blink two times, then wait
        pixels.clear()
        for j in range(2):
            for k in range(pixels.count()):
                pixels.set_pixel(k, Adafruit_WS2801.RGB_to_color( color[0], color[1], color[2]))
            pixels.show()
            time.sleep(0.08)
            pixels.clear()
            pixels.show()
            time.sleep(0.08)
        time.sleep(wait)
        if thread_stop == True:
            break

def moving(pixels):
    nb_pixels = 5
    list_led = list(range(96 - nb_pixels)) + list(range(96 - nb_pixels, 0, -1))
    for i2 in list_led:
        pixels.clear()

        for i in range(96 - nb_pixels):
            if i == i2:
                pixels.set_pixel(i + 0, ledstrip.glob_var.blue)
                pixels.set_pixel(i + 1, ledstrip.glob_var.blue)
                pixels.set_pixel(i + 2, ledstrip.glob_var.white)
                pixels.set_pixel(i + 3, ledstrip.glob_var.white)
                pixels.set_pixel(i + 4, ledstrip.glob_var.red)
                pixels.set_pixel(i + 5, ledstrip.glob_var.red) # update nb_pixels accordingly
        pixels.show()
        time.sleep(0.02)
        if thread_stop == True:
            break

def doCycle(effect):
    global pixels, thread_running, thread_stop

    thread_running = True
    thread_stop = False
    print("thread started")

    while thread_stop == False:
        if effect == 'rainbow':
            rainbow_cycle(pixels, wait=0.01)
        elif effect == 'blink':
            blink_color(pixels, color=(255, 255, 255))
        elif effect == 'moving':
            moving(pixels)

    thread_running = False
    print("thread stopped")

def LED_power_on(effect):
    if is_raspberry_pi:
        if thread_running == False:
            t = threading.Thread(target=doCycle, daemon=True, args=(effect,))
            t.start()

def LED_power_off():
    if is_raspberry_pi:
        global pixels, thread_stop, thread_running

        thread_stop = True
        while thread_running == True:
            time.sleep(0.1)

        pixels.clear()
        pixels.show()

############################################################################ MUSIC
def play_music(filepath):
    pygame.mixer.music.load(filepath)
    print("playing", filepath)
    pygame.mixer.music.play()

def stop_music():
    print("stop music")
    pygame.mixer.music.pause()

def continue_music():
    print("continue music")
    pygame.mixer.music.unpause()

def set_volume(volume):
    ''' Set the volume of the music playback.
    The volume argument is a float between 0.0 and 1.0 that sets volume.
    '''
    print(f"set volume {volume}%")
    pygame.mixer.music.set_volume(volume / 100)

############################################################################
# Create your views here

def home_page(request):

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding)
        form = ChristmasTree(request.POST)

        # Check if the form is valid
        if form.is_valid():
            print(form.cleaned_data['LED_effect'])
            if form.cleaned_data['LED_effect'] == 'off':
                LED_power_off()
            elif form.cleaned_data['LED_effect'] != '':
                LED_power_off()
                LED_power_on(form.cleaned_data['LED_effect'])

            if form.cleaned_data['music'] == 'off':
                stop_music()
            elif form.cleaned_data['music'] != '':
                play_music(form.cleaned_data['music'])

            if form.cleaned_data['volume'] != None:
                set_volume(form.cleaned_data['volume'])

            # redirect to a new URL:
            return HttpResponseRedirect('/')

    # If this is a GET (or any other method) create the default form
    else:
        form = ChristmasTree()

    return render(request, 'ledstrip/home_page.html', context={'form': form})

def master(request):
    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding)
        form = BlindMaster(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            if form.cleaned_data['blind_music'] == 'off':
                stop_music()
            elif form.cleaned_data['blind_music'] != '':
                ledstrip.glob_var.faster_team_to_answer = None
                unicolor(ledstrip.glob_var.white)
                play_music(form.cleaned_data['blind_music'])

            if form.cleaned_data['volume'] != None:
                set_volume(form.cleaned_data['volume'])

            if form.cleaned_data['bad_answer_continue'] == True:
                ledstrip.glob_var.faster_team_to_answer = None
                unicolor(ledstrip.glob_var.white)
                continue_music()

            # redirect to a new URL
            return HttpResponseRedirect('/master')

    # If this is a GET (or any other method) create the default form
    else:
        form = BlindMaster()

    context = {'form': form, 'team': 'master', 'faster_team_to_answer': ledstrip.glob_var.faster_team_to_answer,
               'blue_score': ledstrip.glob_var.blue_score, 'red_score': ledstrip.glob_var.red_score}
    return render(request, 'ledstrip/master.html', context=context)

def blueteam(request):
    return team(request, 'blue', ledstrip.glob_var.blue)

def redteam(request):
    return team(request, 'red', ledstrip.glob_var.red)

def team(request, color, rgb_color):
    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding)
        form = BlindTeam(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            if ledstrip.glob_var.faster_team_to_answer == None:
                ledstrip.glob_var.faster_team_to_answer = color
                stop_music()
                unicolor(rgb_color)

            # redirect to a new URL
            return HttpResponseRedirect(f'/{color}team')

    # If this is a GET (or any other method) create the default form
    else:
        form = BlindTeam()

    context = {'form': form, 'team': color, 'faster_team_to_answer': ledstrip.glob_var.faster_team_to_answer,
               'blue_score': ledstrip.glob_var.blue_score, 'red_score': ledstrip.glob_var.red_score}
    return render(request, 'ledstrip/team.html', context=context)


############################################################################ INIT

#if __name__ == '__main__':
# Executed when app is loaded:
# - With Apache, as soon as the first request is received, triggering the application start
# - In development, as soon as the server is started
print("init pygame mixer")
pygame.mixer.init()

if is_raspberry_pi:
    print("init Adafruit_WS2801")
    pixels = Adafruit_WS2801.WS2801Pixels(96, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE), gpio=GPIO)

    LED_power_on('rainbow')