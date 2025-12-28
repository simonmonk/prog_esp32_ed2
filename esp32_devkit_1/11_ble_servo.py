import asyncio
import aioble
import bluetooth
import struct
from machine import PWM, Pin

SERVICE_NAME = "ESP32 Servo"
SERVICE_UUID = bluetooth.UUID('d6cf5b08-10d8-4ac5-a1e5-14f04c436bf7') 
SERVO_UUID = bluetooth.UUID('66d97a32-c887-4b93-87f9-98013aa2e964')
ADVERTISING_INTERVAL_MICROS = 100000

ble_service = aioble.Service(SERVICE_UUID)
servo_characteristic = aioble.Characteristic(ble_service, SERVO_UUID, write=True, notify=True, capture=True)
aioble.register_services(ble_service)

servo = PWM(Pin(32))
servo.freq(50) # pulse every 20ms

def set_angle(angle, min_pulse_us=500, max_pulse_us=2500):
    us_per_degree = (max_pulse_us - min_pulse_us) / 180
    pulse_us = us_per_degree * angle + min_pulse_us
    # duty 0 to 1023. At 50Hz, each duty_point is 20000/65535 = 0.305 µs/duty_point
    duty = int(pulse_us / 0.305)
    servo.duty_u16(duty)

def decode_data(data):
    try:
        if data is not None:
            number = int.from_bytes(data, 'big')
            return number
    except Exception as e:
        print("Error decoding angle:", e)
        return None

async def wait_for_servo_angle():
    while True:
        try:
            connection, data = await servo_characteristic.written()
            angle = decode_data(data)
            print('Angle: ', angle)
            set_angle(angle)
        except Exception as e:
            print("Error in peripheral_task:", e)
        finally:
            await asyncio.sleep_ms(100)
            
        
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
    t1 = asyncio.create_task(wait_for_servo_angle())
    t2 = asyncio.create_task(peripheral_task())
    await asyncio.gather(t2)
    
asyncio.run(main())

