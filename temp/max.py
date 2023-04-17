# main.py
# Some ports need to import 'sleep' from 'time' module
from machine import SoftI2C, Pin
from utime import ticks_diff, ticks_us, sleep

from max30102 import MAX30102, MAX30105_PULSE_AMP_MEDIUM


def main():
    i2c = SoftI2C(sda=Pin(22),  # Here, use your I2C SDA pin
                  scl=Pin(21),  # Here, use your I2C SCL pin
                  freq=400000)  # Fast: 400kHz, slow: 100kHz

    # Sensor instance
    sensor = MAX30102()  # An I2C instance is required

    # Scan I2C bus to ensure that the sensor is connected
    if sensor.i2c_address not in i2c.scan():
        print("Sensor not found.")
        return
    elif not (sensor.check_part_id()):
        # Check that the targeted sensor is compatible
        print("I2C device ID not corresponding to MAX30102 or MAX30105.")
        return
    else:
        print("Sensor connected and recognized.")
        
    
    sensor.setup_sensor()

    # It is also possible to tune the configuration parameters one by one.
    # Set the sample rate to 400: 400 samples/s are collected by the sensor
    sensor.set_sample_rate(400)
    # Set the number of samples to be averaged per each reading
    sensor.set_fifo_average(8)
    # Set LED brightness to a medium value
    sensor.set_active_leds_amplitude(MAX30105_PULSE_AMP_MEDIUM)

    sleep(1)
    print(sensor.read_temperature())
    compute_frequency = True    
    t_start = ticks_us()  # Starting time of the acquisition
    samples_n = 0  # Number of samples that have been collected
    
    #while True:
        #print(sensor.read_temperature())
        #print(sensor.get_temperature())
        #sleep(1)
        
    while True:
        sensor.check()

        if sensor.available():
            red_reading = sensor.pop_red_from_storage()
            ir_reading = sensor.pop_ir_from_storage()
            print(red_reading, ",", ir_reading)

            if compute_frequency:
                if ticks_diff(ticks_us(), t_start) >= 999999:
                    f_HZ = samples_n
                    samples_n = 0
                    #print(f_HZ)
                    t_start = ticks_us()
                else:
                    samples_n = samples_n + 1
        #break
                    
if __name__ == '__main__':
    main()        


