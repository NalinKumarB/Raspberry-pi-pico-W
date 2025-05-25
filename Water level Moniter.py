import machine
import utime
import network
import socket

# === CONFIG ===
SSID = 'BALU'
PASSWORD = 'balu1234'
TANK_HEIGHT_CM = 12  # Height of tank in centimeters

# === HC-SR04 Pins ===
TRIG = machine.Pin(3, machine.Pin.OUT)
ECHO = machine.Pin(2, machine.Pin.IN)

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    print("Connecting to WiFi...", end='')
    while not wlan.isconnected():
        print('.', end='')
        utime.sleep(0.5)
    print("\nConnected, IP:", wlan.ifconfig()[0])
    return wlan.ifconfig()[0]

def measure_distance():
    TRIG.low()
    utime.sleep_us(2)
    TRIG.high()
    utime.sleep_us(10)
    TRIG.low()

    while ECHO.value() == 0:
        signaloff = utime.ticks_us()
    while ECHO.value() == 1:
        signalon = utime.ticks_us()

    time_passed = utime.ticks_diff(signalon, signaloff)
    distance_cm = (time_passed * 0.0343) / 2
    return round(distance_cm, 2)

def calculate_level(distance):
    # Water level from bottom
    level = TANK_HEIGHT_CM - distance
    if level < 0:
        level = 0
    elif level > TANK_HEIGHT_CM:
        level = TANK_HEIGHT_CM

    percentage = int((level / TANK_HEIGHT_CM) * 100)

    if percentage >= 90:
        status = "Full"
    elif percentage >= 50:
        status = "Half"
    elif percentage >= 20:
        status = "Low"
    else:
        status = "Need to Fill"

    return level, percentage, status

def web_page(level_cm, percentage, status):
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Water Level Monitor</title>
    <meta http-equiv="refresh" content="5">
    <style>
        body {{ font-family: Arial; text-align: center; background: #eef; }}
        .card {{
            background: #fff; padding: 20px; border-radius: 10px;
            display: inline-block; margin-top: 50px; box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #333; }}
        .meter {{
            height: 30px; width: 100%; background: #ddd;
            border-radius: 15px; overflow: hidden; margin-top: 20px;
        }}
        .fill {{
            height: 100%; background: #4caf50; width: {percentage}%;
            text-align: center; line-height: 30px; color: white;
        }}
        .status {{
            font-size: 20px; margin-top: 10px; color: #555;
        }}
    </style>
</head>
<body>
    <div class="card">
        <h1>Water Level Monitor</h1>
        <h2>{level_cm} cm ({percentage}%)</h2>
        <div class="meter">
            <div class="fill">{percentage}%</div>
        </div>
        <div class="status"><strong>Status:</strong> {status}</div>
    </div>
</body>
</html>"""
    return html

# === MAIN ===
ip = connect_wifi()
addr = socket.getaddrinfo(ip, 80)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)
print("Listening on", addr)

while True:
    cl, addr = s.accept()
    print("Client connected from", addr)
    request = cl.recv(1024)
    distance = measure_distance()
    level_cm, percentage, status = calculate_level(distance)
    response = web_page(level_cm, percentage, status)
    cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
    cl.send(response)
    cl.close()
