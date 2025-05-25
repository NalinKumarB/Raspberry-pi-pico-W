from machine import Pin, time_pulse_us
import time

# Define pins
TRIG = Pin(3, Pin.OUT)
ECHO = Pin(2, Pin.IN)

def get_distance():
    TRIG.low()
    time.sleep_us(2)
    TRIG.high()
    time.sleep_us(10)
    TRIG.low()

    duration = time_pulse_us(ECHO, 1, 30000)  # timeout of 30ms
    distance = (duration * 0.0343) / 2  # cm

    return distance

while True:
    dist = get_distance()
    print("Distance: {:.2f} cm".format(dist))
    time.sleep(1)
