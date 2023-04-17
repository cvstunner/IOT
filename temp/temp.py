from machine import Pin, Timer, I2C
from ssd1306 import SSD1306_I2C
from oled import Write
from oled.fonts import ubuntu_mono_15, ubuntu_mono_20
import framebuf
import time
import ntptime
import utime

import network
from machine import RTC
import rp2
import sys
import usocket as socket
import ustruct as struct
import uasyncio as asyncio
from aswitch import Pushbutton

timer = Timer()
led = Pin("LED", Pin.OUT)


def toggleLED(timer):
    led.toggle()


def blinkLED():
    timer.init(freq=1, mode=Timer.PERIODIC, callback=toggleLED)


blinkLED()


# WiFi Crediantials
ssid = "CVSTUNNER"
password = "12345678912"
wlan = network.WLAN(network.STA_IF)

# ssid = 'Poco F1'
# password = 'chetan7897'


def connectWiFi():
    wlan.active(True)
    wlan.connect(ssid, password)
    max_wait = 0
    print("Waiting for connection ", end="")
    while max_wait < 10:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait += 1
        print(" ", max_wait, "s", end=" ")
        utime.sleep(1)
    status = None
    if wlan.status() != 3:
        # raise RuntimeError('\nConnections failed')
        print("\nConnections failed")
        return -1
    else:
        status = wlan.ifconfig()
        print("\nconnection to", ssid, "succesfully established!", sep=" ")
        print("IP-adress: " + status[0])
    ipAddress = status[0]
    return 1


GMT_OFFSET = 3600 * 5.5
NTP_HOST = ("pool.ntp.org", "in.pool.ntp.org")


def getTimeNTP():
    NTP_DELTA = 2208988800
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1B
    addr = socket.getaddrinfo(NTP_HOST[0], 123)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.settimeout(1)
        res = s.sendto(NTP_QUERY, addr)
        msg = s.recv(48)
    except:
        print("Server Down!")
        return -1
    finally:
        s.close()
        wlan.active(False)
    ntp_time = struct.unpack("!I", msg[40:44])[0]
    print(ntp_time)
    return time.gmtime(int(ntp_time - NTP_DELTA + GMT_OFFSET))


rtc = RTC()


def setTimeRTC():
    tm = getTimeNTP()
    if tm != -1:
        rtc.datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))


def sync():
    status = connectWiFi()
    if status == 1:
        setTimeRTC()
        print()
        print(rtc.datetime())
        displayTime()
    else:
        return


# Oled Display Module
width = 128
height = 64

i2c = I2C(0, scl=Pin(17), sda=Pin(12), freq=400000)
display = SSD1306_I2C(width, height, i2c)
write15 = Write(display, ubuntu_mono_15)
write20 = Write(display, ubuntu_mono_20)

# display.text('Kya Dekhra', 10, 0)
# display.setFont('ArialMT_Plain_16')
# display.text('CHETAN', 25, 7)

disp_tim = Timer()


def displayTime():
    write15.text(formatDate(rtc.datetime()), 29, 2)
    write20.text(formatTime(rtc.datetime()), 38, 25)
    display.show()
    asyncio.sleep(600)
    # while True:
    # display.fill(0)
    # utime.sleep(60)
    # disp_tim.init(freq=1, mode=Timer.PERIODIC, callback=writeTime)


def writeTime():
    write20.text(formatTime(rtc.datetime()), 38, 25)


def formatDate(datetime):
    day = ""
    date_day = ""
    date_month = ""

    if datetime[3] == 0:
        day = "Mon"
    elif datetime[3] == 1:
        day = "Tue"
    elif datetime[3] == 2:
        day = "Wed"
    elif datetime[3] == 3:
        day = "Thu"
    elif datetime[3] == 4:
        day = "Fri"
    elif datetime[3] == 5:
        day = "Sat"
    elif datetime[3] == 6:
        day = "Sun"

    if datetime[1] == 1:
        date_month = "Jan"
    elif datetime[1] == "2":
        date_month = "Feb"
    elif datetime[1] == "3":
        date_month = "Mar"
    elif datetime[1] == 4:
        date_month = "Apr"
    elif datetime[1] == "5":
        date_month = "May"
    elif datetime[1] == "6":
        date_month = "jun"
    elif datetime[1] == "7":
        date_month = "Jul"
    elif datetime[1] == "8":
        date_month = "Aug"
    elif datetime[1] == "9":
        date_month = "Sep"
    elif datetime[1] == "10":
        date_month = "Oct"
    elif datetime[1] == "11":
        date_month = "Nov"
    elif datetime[1] == "12":
        date_month = "Dec"

    return day + ", " + str(datetime[2]) + " " + date_month


def formatTime(datetime):
    hour = ""
    minute = ""

    if datetime[4] < 10:
        hour = "0" + str(datetime[4])
    else:
        hour = str(datetime[4])

    if datetime[5] < 10:
        minute = "0" + str(datetime[5])
    else:
        minute = str(datetime[5])

    if datetime[4] > 12:
        hour = str(datetime[4] - 12)
        if int(hour) < 10:
            hour = "0" + hour

    return hour + ":" + minute


# print(time.strftime('%b %d %Y  %H:%M:%S', time.localtime()))
sync()


async def my_app():
    await asyncio.sleep(600)


button_G = Pin(16, Pin.IN, Pin.PULL_UP)
# button_W = Pin(18, Pin.IN, Pin.PULL_UP)


# buttons
# pushbutton click Event Handler
def toggle():
    print("Btn Clicked!")


# pushbutton double-click Event Handler
def toggle_two():
    # tim.deinit()
    print("Btn Double Clicked!")


# pushbutton long press Event Handler
def toggle_long():
    print("Long Press Btn!")


pb_G = Pushbutton(button_G, suppress=True)
pb_G.release_func(toggle)
pb_G.double_func(toggle_two)
pb_G.long_func(toggle_long)


# Running the main loop
loop = asyncio.get_event_loop()
loop.run_until_complete(my_app())
