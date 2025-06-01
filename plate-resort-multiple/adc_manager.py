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
        """Convert feedback voltage to angle based on observed readings:
        2.51V ≈ 68.5° (minimum angle)
        1.56V ≈ 159° (middle position)
        0.58V ≈ 240° (maximum angle)
        """
        # Handle limits
        if voltage >= 2.51:
            return 68.5
        elif voltage <= 0.58:
            return 240.0
        
        # Linear interpolation between known points
        if voltage >= 1.56:
            # Between 2.51V (68.5°) and 1.56V (159°)
            ratio = (2.51 - voltage) / (2.51 - 1.56)
            return 68.5 + ratio * (159.0 - 68.5)
        else:
            # Between 1.56V (159°) and 0.58V (240°)
            ratio = (1.56 - voltage) / (1.56 - 0.58)
            return 159.0 + ratio * (240.0 - 159.0) 