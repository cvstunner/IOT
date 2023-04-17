from utime import ticks_diff, ticks_us, sleep
from max30102 import MAX30102, MAX30105_PULSE_AMP_MEDIUM
import hrcalc

from machine import Pin, Timer, SoftI2C, I2C, ADC
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
        #self.timer.init(freq=1, mode=Timer.PERIODIC, callback=self.toggleLED)

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

        #self.i2c = I2C(0, scl=Pin(21), sda=Pin(20), freq=400000)
        #self.display = SSD1306_I2C(self.oled_width, self.oled_height, self.i2c)
        #self.write15 = Write(self.display, ubuntu_mono_15)
        #self.write20 = Write(self.display, ubuntu_mono_20)

        self.page_status = 0
        self.activity_status = 0
        button_G = Pin(15, Pin.IN, Pin.PULL_UP)
        button_W = Pin(14, Pin.IN, Pin.PULL_UP)
        self.pb_G = Pushbutton(button_G, suppress=True)
        #self.pb_G.release_func(self.toggle)
        self.pb_W = Pushbutton(button_W, suppress=True)
        #self.pb_W.release_func(self.runActivity)
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
        #t1 = _thread.start_new_thread(self.oximeter, ())
        
        self.adc = ADC(26)
        
        self.oximeter()
        
    def read_sequential(self, amount=100):
        red_buf = []
        ir_buf = []
        print(self.oxi.check(), self.oxi.available())
        while True:
            red = self.oxi.pop_red_from_storage()
            ir = self.oxi.pop_ir_from_storage()
            print(red, ir)
            sleep(1)
                
        if self.oxi.available():
            for i in range(amount):
                red = self.oxi.pop_red_from_storage()
                ir = self.oxi.pop_ir_from_storage()
                print(red, ir)
                red_buf.append(red)
                ir_buf.append(ir)
        else:
            return
        
        return red_buf, ir_buf
    
    def oximeter(self):
        self.oxi = MAX30102()
        i2c = SoftI2C(sda=Pin(22), scl=Pin(21),freq=400000)
        #i2c = machine.I2C(0, scl=machine.Pin(13), sda=machine.Pin(12), freq=400000)
        if self.oxi.i2c_address not in i2c.scan():
            print("Sensor not found.")
        elif not (self.oxi.check_part_id()):
            print("I2C device ID not corresponding to MAX30102 or MAX30105.")
        else:
           print("Sensor connected and recognized.")
        
        self.oxi.setup_sensor()
        self.oxi.set_sample_rate(400)
        self.oxi.set_fifo_average(8)
        self.oxi.set_active_leds_amplitude(MAX30105_PULSE_AMP_MEDIUM)
        while True:
            #print(self.oxi.read_temperature())
            red = self.oxi.get_red()
            ir = self.oxi.get_ir()
            print(red, ir)
        
        #self.read_sequential(100)
    
    def calc(sensor):
        #red, ir = read_sequential(sensor, 100)
        amount=100
        red_buf = []
        ir_buf = []
        while True:
            red = sensor.pop_red_from_storage()
            ir = sensor.pop_ir_from_storage()
            print(red, ir)
            red_buf.append(red)
            ir_buf.append(ir)
            if amount==100:
                break
    
        hr,hrb,sp,spb = hrcalc.calc_hr_and_spo2(ir, red)

        print("hr detected:",hrb)
        print("sp detected:",spb)
    
        if(hrb == True and hr != -999):
            hr2 = int(hr)
            print("Heart Rate : ",hr2)
        if(spb == True and sp != -999):
            sp2 = int(sp)
            print("SPO2       : ",sp2)
    

if __name__ == "__main__":
    main = main()
    print("Yup!")





#class main:
    
#    print(sensor.read_temperature())
#    compute_frequency = True    
#    t_start = ticks_us()  # Starting time of the acquisition
#    samples_n = 0  # Number of samples that have been collected

#    hr2 = 0
#    sp2 = 0

#    red_buf = []
#    ir_buf = []
    
    

