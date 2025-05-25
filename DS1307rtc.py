from machine import I2C, Pin
import utime

# DS1307 Address
DS1307_I2C_ADDRESS = 0x68

class DS1307:
    def __init__(self, i2c):
        self.i2c = i2c

    def bcd_to_dec(self, bcd):
        return (bcd // 16) * 10 + (bcd % 16)

    def dec_to_bcd(self, dec):
        return (dec // 10) * 16 + (dec % 10)

    def set_time(self, year, month, day, weekday, hour, minute, second):
        data = bytearray(7)
        data[0] = self.dec_to_bcd(second)
        data[1] = self.dec_to_bcd(minute)
        data[2] = self.dec_to_bcd(hour)
        data[3] = self.dec_to_bcd(weekday)
        data[4] = self.dec_to_bcd(day)
        data[5] = self.dec_to_bcd(month)
        data[6] = self.dec_to_bcd(year - 2000)  # Year offset
        self.i2c.writeto_mem(DS1307_I2C_ADDRESS, 0x00, data)

    def get_time(self):
        data = self.i2c.readfrom_mem(DS1307_I2C_ADDRESS, 0x00, 7)
        second = self.bcd_to_dec(data[0] & 0x7F)
        minute = self.bcd_to_dec(data[1])
        hour = self.bcd_to_dec(data[2] & 0x3F)
        weekday = self.bcd_to_dec(data[3])
        day = self.bcd_to_dec(data[4])
        month = self.bcd_to_dec(data[5])
        year = self.bcd_to_dec(data[6]) + 2000
        return year, month, day, weekday, hour, minute, second

# Initialize I2C
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=32768)

# Initialize DS1307
rtc = DS1307(i2c)

devices = i2c.scan()
if devices:
    print("I2C devices found:", [hex(d) for d in devices])
else:
    print("No I2C devices found!")


# Uncomment this to set the time (do this once):
# rtc.set_time(2024, 12, 29, 7, 14, 55, 0)

# Continuously display the time
while True:
    year, month, day, weekday, hour, minute, second = rtc.get_time()
    print(f"Date: {year:04d}-{month:02d}-{day:02d} Time: {hour:02d}:{minute:02d}:{second:02d}")
    utime.sleep(1)
