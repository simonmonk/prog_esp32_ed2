from machine import Pin
from neopixel import NeoPixel

pixel = NeoPixel(Pin(48), 1)

pixel.fill((255, 255, 255))
pixel.write()