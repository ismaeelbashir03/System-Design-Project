# from iotools import MotorControl
import smbus2 as smbus
import numpy as np
from time import sleep
from datetime import datetime
import os
import time

class Motors(object):
    def __init__(self):
        print("Starting SMBus . . .")
        self.bus = smbus.SMBus(1)
        sleep(2)
        print("SMBus Started.")
        self.mc = MotorControl()
        self.encoder_address = 0x05
        self.encoder_register = 0x0
        self.num_encoder_ports = 6
        self.refresh_rate = 10 #refresh rate reduces errors in i2c reading

    def move_motor(self, id, speed):
        self.mc.setMotor(id, speed)

    def stop_motor(self, id):
        self.mc.stopMotor(id)

    def stop_motors (self):
        self.mc.stopMotors()

    def __i2c_read_encoder(self):
        self.encoder_data = self.bus.read_i2c_block_data(self.encoder_address, self.encoder_register, self.num_encoder_ports)

    def read_encoder(self, id):
        self. i2c_read_encoder()
        encoder_id_value =self.encoder_data[id]
        return encoder_id_value
    
    def print_encoder_data(self):
        self.__i2c_read_encoder()
        ts = str(datetime.now())
        print(self.encoder_data, ts.rjust(50,'.'))

class MotorControl:
    def __init__(self):
        self.bus = smbus.SMBus(1)
        self.address = 0x04

    def setMotor(self, id, speed):
        """
        Mode 2 is Forward.
        Mode 3 is Backwards.
        """
        direction = 2 if speed >= 0 else 3
        speed = np.clip(abs(speed), 0, 100)
        byte1 = id << 5 | 24 | direction << 1
        byte2 = int(speed * 2.55)
        self.__write_block([byte1, byte2])

    def stopMotor(self, id):
        """
        Mode 0 floats the motor.
        """
        direction = 0
        byte1 = id << 5 | 16 | direction << 1
        self.__write(byte1)

    def stopMotors(self):
        """
        The motor board stops all motors if bit 0 is high.
        """
        print('[INFO] [MotorControl] Stopping all motors...')
        self.__write(0x01)

    def __write(self, value):
        try:
            self.bus.write_byte_data(self.address, 0x00, value)
        except IOError as e:
            print('I/O error({0}): {1}'.format(e.errno, e.strerror))

    def __write_block(self, values):
        try:
            msg = smbus.i2c_msg.write(self.address, values)
            self.bus.i2c_rdwr(msg)
        except IOError as e:
            print('I/O error({0}): {1}'.format(e.errno, e.strerror))
