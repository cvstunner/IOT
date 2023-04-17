from machine import Pin, Timer, I2C, ADC
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
import _thread
import math
import max30100


class main:
    def __init__(self):
        super(main, self).__init__()
        print("run")
        self.timer = Timer()

        # Blink On-Board LED
        self.led = Pin("LED", Pin.OUT)
        self.timer.init(freq=1, mode=Timer.PERIODIC, callback=self.toggleLED)

        # WiFi Crediantials
        self.ssid = "CVSTUNNER"
        self.password = "12345678912"
        self.creds = {
            0: {"ssid": "CVSTUNNER", "password": "12345678912"},
            1: {"ssid": "Poco F1", "password": "chetan7897"},
            2: {"ssid": "vivo 1814", "password": "Monu7777"},
            3: {"ssid": "Redmi Note 9 Pro", "password": "sonu7777"},
        }
        self.wlan = network.WLAN(network.STA_IF)

        # Time Clock
        self.rtc = RTC()
        self.GMT_OFFSET = 3600 * 5.5
        self.NTP_HOST = ("pool.ntp.org", "in.pool.ntp.org")

        # Time Task
        self.timeTask = None

        # Oled self.display Module
        self.oled_width = 128
        self.oled_height = 64

        self.i2c = I2C(0, scl=Pin(21), sda=Pin(20), freq=400000)
        self.display = SSD1306_I2C(self.oled_width, self.oled_height, self.i2c)
        self.write15 = Write(self.display, ubuntu_mono_15)
        self.write20 = Write(self.display, ubuntu_mono_20)

        self.page_status = 0
        self.activity_status = 0
        button_G = Pin(15, Pin.IN, Pin.PULL_UP)
        button_W = Pin(14, Pin.IN, Pin.PULL_UP)
        self.pb_G = Pushbutton(button_G, suppress=True)
        self.pb_G.release_func(self.toggle)
        self.pb_W = Pushbutton(button_W, suppress=True)
        self.pb_W.release_func(self.runActivity)
        #self.pb_G.double_func(self.toggle_two)
        #self.pb_G.long_func(self.toggle_long)
        # self.sync()
        # sync_loop = asyncio.get_event_loop()
        # sync_loop.run_until_complete(self.sync())
        # evt_loop = asyncio.get_event_loop()
        # .run_until_complete(self.my_app())

        # t2 = _thread.start_new_thread(self.my_app, ())
        # t1 = threading.Thread(target=sync, arg=())
        # t1.start()
        # t1 = _thread.start_new_thread(self.sync, ())
        self.adc = ADC(26)
        self.display_SPO2()
        asyncio.run(self.main())
        print("hi")
        

    def toggleLED(self, timer):
        self.led.toggle()

    def connectWiFi(self):
        print('connectWiFi')
        self.wlan.active(True)
        for index, cred in self.creds.items():
            print('\n' + cred["ssid"], cred["password"])
            self.ssid = cred["ssid"]
            self.password = cred["password"]
            self.wlan.connect(cred["ssid"], cred["password"])
            max_wait = 0
            print("Waiting for connection ", end="")
            while max_wait < 10:
                if self.wlan.status() < 0 or self.wlan.status() >= 3:
                    break
                max_wait += 1
                print(" ", max_wait, "s", end=" ")
                utime.sleep(1)
            print()
            if self.wlan.status() == 3:
                break

            status = None
        if self.wlan.status() != 3:
            # raise RuntimeError("\nConnections failed")
            print("\nConnections failed")
            return -1
        else:
            status = self.wlan.ifconfig()
            print("\nconnection to", self.ssid, "succesfully established!", sep=" ")
            print("IP-adress: " + status[0])
        ipAddress = status[0]
        return 1

    def getTimeNTP(self):
        NTP_DELTA = 2208988800
        NTP_QUERY = bytearray(48)
        NTP_QUERY[0] = 0x1B
        addr = socket.getaddrinfo(self.NTP_HOST[0], 123)[0][-1]
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
            self.wlan.active(False)
        ntp_time = struct.unpack("!I", msg[40:44])[0]
        print(ntp_time)
        return time.gmtime(int(ntp_time - NTP_DELTA + self.GMT_OFFSET))

    def setTimeRTC(self):
        tm = self.getTimeNTP()
        if tm != -1:
            self.rtc.datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))

    # self.display.text('Kya Dekhra', 10, 0)
    # self.display.setFont('ArialMT_Plain_16')
    # self.display.text('CHETAN', 25, 7)

    # disp_tim = Timer()

    def writeTime(self):
        self.write20.text(formatTime(self.rtc.datetime()), 38, 25)

    def formatDate(self, datetime):
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

    def formatTime(self, datetime):
        hour = ""
        minute = ""
        
        if datetime[4] == 0:
            hour = str(datetime[4] + 12)    
        elif datetime[4] < 10:
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

    async def displayTime(self):
        print("displaying time")
        self.write15.text(self.formatDate(self.rtc.datetime()), 29, 2)
        while True:
            self.write20.text(self.formatTime(self.rtc.datetime()), 38, 25)
            self.display.show()
            print('time task')
            await asyncio.sleep(5)

    def display_SPO2(self):
        mx30 = max30100.MAX30100()
        mx30.refresh_temperature()
        temp = mx30.get_temperature()
        print('TEMP=%d'%temp)
        reg = mx30.get_registers()
        mx30.enable_spo2()
        mx30.read_sensor()

    # Scolling Animations
    def scroll_out_screen(self, speed, direction):
        for i in range(-int((self.oled_width + 1) / speed), 0):
            for j in range(-int(self.oled_height), 0):
                self.display.pixel(i, j, 0)
            self.display.scroll(direction * speed, 0)
            self.display.show()

    async def sync(self):
        print('sync task')
        status = self.connectWiFi()
        if status >= 0:
            self.setTimeRTC()
            print()
            print(self.rtc.datetime())
            # self.write15.text('CHETAN', 29, 2)
            # self.display.text('CHETAN', 29, 2)
            # self.displayTime()
            self.timeTask = asyncio.create_task(self.displayTime())
            while True:
                await asyncio.sleep_ms(1)
        else:
            self.timeTask = asyncio.create_task(self.displayTime())
            while True:
                await asyncio.sleep_ms(1)

    async def main(self):
        print('main')
        sync_task = asyncio.create_task(self.sync())
        while True:
            await asyncio.sleep_ms(1)
            break
        sync_task.cancel()
        self.app_task = asyncio.create_task(self.app())
        while True:
            await asyncio.sleep_ms(1)
        #asyncio.run(self.app())
        print('yeep')
        #await asyncio.create_task(self.app())

    # print(time.strftime('%b %d %Y  %H:%M:%S', time.localtime()))
    
    async def displayECG(self):
        while True:
            self.display.fill(0)
            for i in range(1, 127):
                adc_readout = round(self.adc.read_u16() / 512)
                y = math.ceil((adc_readout / 2) - 1)
                self.display.pixel(i, y, 1)
                self.display.show()
                await asyncio.sleep_ms(1)
            print('ecg')
            
    async def ECGActivity(self):
        self.activity_status = 1
        self.ecgTask = asyncio.create_task(self.displayECG())
        while True:
            await asyncio.sleep_ms(1)
            print('ecg_acv')
            break
        self.app_task = asyncio.create_task(self.app())
        while True:
            await asyncio.sleep_ms(10000)
            print('app_task_ecg')
        
    async def app(self):
        await asyncio.sleep_ms(1)
        print("hm")

    # pushbutton click Event Handler
    def toggle(self):
        print("Btn Clicked!")
        self.scroll_out_screen(16, -1)
        if self.page_status == 0:
            #self.activity_status = 0
            self.page_status = 1
            self.timeTask.cancel()
            self.display.fill(0)
            self.write20.text("ECG", 38, 25)
            self.display.show()
        elif self.page_status == 1:
            self.display.fill(0)
            if self.activity_status == 1:
                self.ecgTask.cancel()
                self.activity_status = 0
            self.timeTask = asyncio.create_task(self.displayTime())
            self.page_status = 0
            self.scroll_out_screen(16, 1)
            print('sync task')
            while True:
                await asyncio.sleep_ms(1)
                break
                
            
    def runActivity(self):
        print('runActivity')
        if self.page_status == 1 and self.activity_status != 1:
            self.app_task.cancel()
            asyncio.run(self.ECGActivity())
            while True:
                await asyncio.sleep_ms(1)
                break
            

    # pushbutton double-click Event Handler
    def toggle_two(self):
        # tim.deinit()
        print("Btn Double Clicked!")
        self.scroll_out_screen(16, 1)
        self.display.fill(0)
        self.timeTask = asyncio.create_task(self.displayTime())
        print('sync task')
        while True:
            await asyncio.sleep_ms(1)
            break

    # pushbutton long press Event Handler
    def toggle_long(self):
        print("Long Press Btn!")


if __name__ == "__main__":
    main = main()
    print("Yup!")


