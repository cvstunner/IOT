from machine import Pin, I2C, Timer
from ssd1306 import SSD1306_I2C
import math
import utime
import _thread
from machine import ADC
from time import sleep

last_time = 0
bpm_time = False
status = False
bpm = 0
bpm_prev = 0
bpm_curr = 1
upside = 560
downside = 530
adc = ADC(26)
current_time = utime.ticks_ms()
sda = machine.Pin(4)
scl = machine.Pin(5)
i2c = machine.I2C(0, sda=sda, scl=scl, freq=400000)
oled = SSD1306_I2C(128, 64, i2c)
oled.fill(0)
oled.text("bpm:...", 6, 2)
oled.show()


def bpm_thread():
    while True:
        current_time = utime.ticks_ms()
        global status, bpm_time, bpm, last_time, bpm_prev, bpm_curr
        deger = round(adc.read_u16() / 64)
        if deger > upside:
            if status == True:
                bpm = current_time - last_time
                bpm = round(1000 * (60 / bpm))
                bpm_time = False
                status = 0
            if bpm_time == 0:
                last_time = utime.ticks_ms()
                bpm_time = True
        if deger < downside and bpm_time:
            status = True
        bpm_prev = bpm_curr
        bpm_curr = deger
        if bpm_curr == bpm_prev and bpm > 0:
            bpm = 0
        sleep(0.1)


_thread.start_new_thread(bpm_thread, ())

while True:
    for i in range(1, 127):
        adc_readout = round(adc.read_u16() / 512)
        y = math.ceil((adc_readout / 2) - 1)
        oled.pixel(i, y, 1)
        oled.show()
    oled.fill(0)
    oled.text("bpm: ", 6, 2)
    oled.text(str(bpm), 40, 2)
    oled.show()
