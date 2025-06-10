#!/usr/bin/env python3

import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

class ADCManager:
    def __init__(self):
        # Setup I2C for ADS1115
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS.ADS1115(self.i2c)
        self.adc_channel = AnalogIn(self.ads, ADS.P0)

    def get_voltage(self):
        """Get current voltage reading from ADC"""
        return self.adc_channel.voltage

    def voltage_to_angle(self, voltage):
        """Convert feedback voltage to angle based on datasheet calibration:
        2.60V ≈ 0° (900µs position)
        1.66V ≈ 150° (1500µs neutral position) 
        0.72V ≈ 300° (2100µs position)
        """
        # Handle voltage limits
        if voltage >= 2.60:
            return 0.0
        elif voltage <= 0.72:
            return 300.0
        
        # Linear interpolation between known points
        if voltage >= 1.66:
            # Between 2.60V (0°) and 1.66V (150°)
            ratio = (2.60 - voltage) / (2.60 - 1.66)
            return 0.0 + ratio * (150.0 - 0.0)
        else:
            # Between 1.66V (150°) and 0.72V (300°)
            ratio = (1.66 - voltage) / (1.66 - 0.72)
            return 150.0 + ratio * (300.0 - 150.0)