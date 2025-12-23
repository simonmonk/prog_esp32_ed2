from machine import Pin
from onewire import OneWire
from ds18x20 import DS18X20
from time import sleep

sensor_pin = Pin(4, Pin.PULL_UP)
sensor_bus = DS18X20(OneWire(sensor_pin))

sensor = sensor_bus.scan()[0]

while True:
    sensor_bus.convert_temp()
    print(sensor_bus.read_temp(sensor))
    sleep(0.5)