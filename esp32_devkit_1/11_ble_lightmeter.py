import asyncio
import aioble
import bluetooth
import struct
from machine import ADC, Pin

SERVICE_NAME = "ESP32 Lightmeter"
SERVICE_UUID = bluetooth.UUID('c3fc429a-9b4a-4f9f-bc3c-8916a35eeb26') 
LIGHTMETER_UUID = bluetooth.UUID('b71e4aab-b0f9-446a-8072-4a1bdd47e0c0')
ADVERTISING_INTERVAL_MICROS = 100000

analog = ADC(Pin(32), atten=ADC.ATTN_11DB)
max_reading = 58000

ble_service = aioble.Service(SERVICE_UUID)
sensor_characteristic = aioble.Characteristic(ble_service, LIGHTMETER_UUID, read=True, notify=True)
aioble.register_services(ble_service)

def read_light():
    reading = analog.read_u16()
    percent = int(reading / max_reading * 100)
    return percent

def to_utf8(data):
    return str(data).encode('utf-8')

async def sensor_task():
    while True:
        sensor_characteristic.write(to_utf8(read_light()), send_update=True)
        await asyncio.sleep_ms(1000)
        
async def peripheral_task():
    while True:
        try:
            async with await aioble.advertise(
                ADVERTISING_INTERVAL_MICROS,
                name=SERVICE_NAME,
                services=[SERVICE_UUID],
                ) as connection:
                    print('Connected to: ', connection.device)
                    await connection.disconnected()             
        except Exception as e:
            print('Error but the show must go on:', e)
        finally:
            await asyncio.sleep_ms(100)

async def main():
    t1 = asyncio.create_task(sensor_task())
    t2 = asyncio.create_task(peripheral_task())
    await asyncio.gather(t1, t2)
    
asyncio.run(main())
