import Adafruit_WS2801
from .utils import is_raspberry_pi

faster_team_to_answer = None
blue_score = 0
red_score = 0

if is_raspberry_pi:
    blue  = Adafruit_WS2801.RGB_to_color(0, 0, 255)
    white = Adafruit_WS2801.RGB_to_color(100, 100, 100)
    red   = Adafruit_WS2801.RGB_to_color(255, 0, 0)
else:
    blue = white = red = None
