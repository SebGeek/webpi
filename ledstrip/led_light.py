# coding: utf-8
# Simple demo of of the WS2801/SPI-like addressable RGB LED lights.
# LED strip BTF-LIGHTING WS2801 5050 SMD RGB 32Leds/m 96leds Adressable Individuel Non étanche Noir PCB Pixel Strip Light DC5V 3m 38€

# /// @remarks The WS2801 LED driver has three current controlled LED outputs with
# /// 8-bit precision (256 levels).  It is controlled over SPI by sending 24 bits
# /// of pixel data at up to 25MHz rate.  Additional data is then relayed to the output
# /// SPI pins to feed daisy-chained drivers.  Once the bus is quiescent for 500
# /// microseconds, the data is applied to the outputs and the chip is ready to
# /// receive more values.
# ///
# /// So a large number of of drivers can be fed on each channel, limited only by
# /// the overall refresh rate.  But the data must be fed without interruption to
# /// avoid prematurely ending the cycle.
# ///
# /// The actual color data sequence depends upon the wiring of the module; on one
# /// particular strip light tested the actual sequence was blue-red-green.
# ///
# /// Note that the relay scheme means that first three bytes output feed the
# /// first module, the second three the second module, etc.  In other words, the
# /// strand is not a shift register.  Extra data has no effect.
#
# /// This sketch assumes the following electrical connections from the Arduino to
# /// the first module in a chain:
#
# /// PIN11 (MOSI)  ->  DAT
# /// PIN13 (SCK)   ->  CLK
# /// GND           ->  GND


import time
# noinspection PyUnresolvedReferences
import RPi.GPIO as GPIO
 
# Import the WS2801 module.
import Adafruit_WS2801
import Adafruit_GPIO.SPI as SPI
 
# Configure the count of pixels:
PIXEL_COUNT = 6
 
# Alternatively specify a hardware SPI connection on /dev/spidev0.0:
SPI_PORT   = 0
SPI_DEVICE = 0

 
# Define the wheel function to interpolate between different hues.
def wheel(pos, intensity=0.1):
    if pos < 85:
        return Adafruit_WS2801.RGB_to_color(int(pos * 3 * intensity), int((255 - pos * 3) * intensity), 0)
    elif pos < 170:
        pos -= 85
        return Adafruit_WS2801.RGB_to_color(int((255 - pos * 3) * intensity), 0, int(pos * 3 * intensity))
    else:
        pos -= 170
        return Adafruit_WS2801.RGB_to_color(0, int(pos * 3 * intensity), int((255 - pos * 3) * intensity))
 
# Define rainbow cycle function to do a cycle of all hues.
def rainbow_cycle_successive(pixels, wait=0.1, intensity=256):
    for i in range(pixels.count()):
        # tricky math! we use each pixel as a fraction of the full 96-color wheel
        # (thats the i / strip.numPixels() part)
        # Then add in j which makes the colors go around per pixel
        # the % 96 is to make the wheel cycle around
        pixels.set_pixel(i, wheel((i * intensity // pixels.count()) % intensity))
        pixels.show()
        if wait > 0:
            time.sleep(wait)



def rainbow_colors(pixels, wait=0.05):
    for j in range(256): # one cycle of all 256 colors in the wheel
        for i in range(pixels.count()):
            pixels.set_pixel(i, wheel((256 // pixels.count() + j) % 256))
        pixels.show()
        if wait > 0:
            time.sleep(wait)

def brightness_decrease(pixels, wait=0.01, step=1):
    for j in range(int(256 // step)):
        for i in range(pixels.count()):
            r, g, b = pixels.get_pixel_rgb(i)
            r = int(max(0, r - step))
            g = int(max(0, g - step))
            b = int(max(0, b - step))
            pixels.set_pixel(i, Adafruit_WS2801.RGB_to_color( r, g, b))
        pixels.show()
        if wait > 0:
            time.sleep(wait)

def blink_color(pixels, blink_times=5, wait=0.5, color=(255, 0, 0)):
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

def appear_from_back(pixels, color=(255, 0, 0)):
    for i in range(pixels.count()):
        for j in reversed(range(i, pixels.count())):
            pixels.clear()
            # first set all pixels at the begin
            for k in range(i):
                pixels.set_pixel(k, Adafruit_WS2801.RGB_to_color( color[0], color[1], color[2]))
            # set then the pixel at position j
            pixels.set_pixel(j, Adafruit_WS2801.RGB_to_color( color[0], color[1], color[2]))
            pixels.show()
            time.sleep(0.02)

 
if __name__ == "__main__":
    pixels = Adafruit_WS2801.WS2801Pixels(96, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE), gpio=GPIO)
    pixels.clear()
    pixels.show()

    blue  = Adafruit_WS2801.RGB_to_color(0, 0, 255)
    white = Adafruit_WS2801.RGB_to_color(100, 100, 100)
    red   = Adafruit_WS2801.RGB_to_color(255, 0, 0)
    green = Adafruit_WS2801.RGB_to_color(0, 255, 0)
    # for color in [red, green, white, blue]:
    #     for i in range(96):
    #         pixels.set_pixel(i, color)
    #         pixels.show()
    #         time.sleep(0.1)


    # while True:
    #     list_led = list(range(96 - 7)) + list(range(96 - 7, 0, -1))
    #     for i2 in list_led:
    #         pixels.clear()
    #
    #         for i in range(96 - 7):
    #             if i == i2:
    #                 pixels.set_pixel(i + 0, blue)
    #                 pixels.set_pixel(i + 1, blue)
    #                 pixels.set_pixel(i + 2, white)
    #                 pixels.set_pixel(i + 3, white)
    #                 pixels.set_pixel(i + 4, red)
    #                 pixels.set_pixel(i + 5, red)
    #                 pixels.set_pixel(i + 6, green)
    #                 pixels.set_pixel(i + 7, green)
    #         pixels.show()
    #         time.sleep(0.05)

    #rainbow_cycle_successive(pixels, wait=0.1)
    blink_color(pixels)
    
    #for t in range(1000):
    #    for i in range(96):
    #        pixels.clear()
    #        pixels.set_pixel(i, Adafruit_WS2801.RGB_to_color(i, 50, 127))
    #        pixels.show()
    #        time.sleep(0.001)

    # pixels = Adafruit_WS2801.WS2801Pixels(PIXEL_COUNT, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE), gpio=GPIO)
    #
    # for i in range(10):
    #     # Clear all the pixels to turn them off.
    #     pixels.clear()
    #     pixels.show()  # Make sure to call show() after changing any pixels!
    #
    #     rainbow_cycle_successive(pixels, wait=0.1)

    # while True:
    #    rainbow_cycle(pixels, wait=0.01)
    
    #brightness_decrease(pixels)
    
    #appear_from_back(pixels)
    #
    # for i in range(3):
    #     blink_color(pixels, blink_times = 1, color=(255, 0, 0))
    #     blink_color(pixels, blink_times = 1, color=(0, 255, 0))
    #     blink_color(pixels, blink_times = 1, color=(0, 0, 255))
    #
    #rainbow_colors(pixels)
    
    #brightness_decrease(pixels)
