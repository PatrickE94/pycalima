#!/usr/bin/env python3.6

# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from struct import pack, unpack
import time
import datetime
import bluepy.btle as ble
import binascii
from collections import namedtuple

Fanspeeds = namedtuple('Fanspeeds', 'Humidity Light Trickle')
Fanspeeds.__new__.__defaults__ = (2250, 1625, 1000)
Time = namedtuple('Time', 'DayOfWeek Hour Minute Second')
Sensitivity = namedtuple('Sensitivity', 'HumidityOn Humidity LightOn Light')
LightSensorSettings = namedtuple('LightSensorSettings', 'DelayedStart RunningTime')
SilentHours = namedtuple('SilentHours', 'On StartingHour StartingMinute EndingHour EndingMinute')
TrickleDays = namedtuple('TrickleDays', 'Weekdays Weekends')
BoostMode = namedtuple('BoostMode', 'OnOff Speed Seconds')

FanState = namedtuple('FanState', 'Humidity Temp Light RPM BoostActive Mode Unknown Unknown2')
FanStateShort = namedtuple('FanState', 'Humidity Temp Light RPM BoostActive Mode')


def FindCalimas():
    scanner = ble.Scanner()
    devices = scanner.scan()
    calimas = filter(lambda dev: dev.addr[0:8] == "58:2b:db", devices)
    return tuple(map(lambda dev: dev.addr, calimas))

class Calima:

    def __init__(self, addr, pin):
        # Set debug to true if you want more verbose output
        self._debug = False
        self.conn = ble.Peripheral(deviceAddr=addr)
        self.setAuth(pin)

    def __del__(self):
        self.conn.disconnect()

    def disconnect(self):
        self.conn.disconnect()

    def _bToStr(self, val):
        return binascii.b2a_hex(val).decode('utf-8')

    def _readHandleShort(self, handle):
        val = self.conn.readCharacteristic(handle)
        if (self._debug):
            print("%s" % (self._bToStr(val)))

        return val

    def _readHandle(self, handle):
        val = self.conn.readCharacteristic(handle)
        if (self._debug):
            print("[Calima] [R] %s = %s" % (hex(handle), self._bToStr(val)))

        return val

    def _writeHandleShort(self, handle, val):
        if (self._debug):
            print("%s" % (self._bToStr(val)))

        self.conn.writeCharacteristic(handle, val, withResponse=True)

    def _writeHandle(self, handle, val):
        if (self._debug):
            print("[Calima] [W] %s = %s" % (hex(handle), self._bToStr(val)))

        self.conn.writeCharacteristic(handle, val, withResponse=True)

    def scanCharacteristics(self):
        val = self.conn.getCharacteristics()
        for ch in val:
            if (ch.supportsRead()):
                rd = ch.read()
                print("[%s] %s (%s) = (%d) %s" % (hex(ch.getHandle()), ch.uuid.getCommonName(), ch.propertiesToString(), len(rd), self._bToStr(rd)))
            else:
                print("[%s] %s (%s)" % (hex(ch.getHandle()), ch.uuid.getCommonName(), ch.propertiesToString()))

    # --- Generic GATT Characteristics

    def getDeviceName(self):
        return self._readHandle(0x3).decode('ascii')

    def getModelNumber(self):
        return self._readHandle(0xd).decode('ascii')

    def getSerialNumber(self):
        return self._readHandle(0xb).decode('ascii')

    def getHardwareRevision(self):
        return self._readHandle(0xf).decode('ascii')

    def getFirmwareRevision(self):
        return self._readHandle(0x11).decode('ascii')

    def getSoftwareRevision(self):
        return self._readHandle(0x13).decode('ascii')

    def getManufacturer(self):
        return self._readHandle(0x15).decode('ascii')

    # --- Onwards to PAX "unknown" characteristics

    def setAuth(self, pin):
        self._writeHandleShort(0x18, pack("<I", int(pin)))

    def setAlias(self, name):
        self._writeHandle(0x1c, pack('20s', bytearray(name, 'utf-8')))

    def getAlias(self):
        return self._readHandle(0x1c).decode('utf-8')

    def getIsClockSet(self):
        return self._bToStr(self._readHandleShort(0x1f))

    def getStateShort(self):
        v = unpack('<4HBHB', self._readHandle(0x21))
        boostMode = bool(v[4] & 0x10)
        mode = v[4] >> 1
        #return self._bToStr(self._readHandleShort(0x21))
        return FanStateShort(v[0], v[1]/4, v[2], v[3], boostMode, mode)
        #return (v[0], v[1]/4, v[2], v[3], boostMode, mode)

    def getState(self):
        v = unpack('<4HBHB', self._readHandle(0x21))
        boostMode = bool(v[4] & 0x10)
        #mode = ('Unknown', 'Trickle', 'Light', 'Humidity')[v[4] & ~(0x10)]
        mode = v[4] >> 1
        return FanState(v[0], v[1]/4, v[2], v[3], boostMode, mode, v[5], v[6])

    def getUnknown24(self):
        return self._bToStr(self._readHandle(0x24))

    def getUnknown26(self):
        return self._bToStr(self._readHandle(0x26))

    def setFanSpeedSettings(self, humidity=2250, light=1625, trickle=1000):
        for val in (humidity, light, trickle):
            if (val % 25 != 0):
                raise ValueError("Speeds should be multiples of 25")
            if (val > 2500 or val < 0):
                raise ValueError("Speeds must be between 0 and 2500 rpm")

        self._writeHandle(0x28, pack('<HHH', humidity, light, trickle))

    def getFanSpeedSettings(self):
        return Fanspeeds._make(unpack('<HHH', self._readHandle(0x28)))

    def setSensorsSensitivity(self, humidity, light):
        if humidity > 3 or humidity < 0:
            raise ValueError("Humidity sensitivity must be between 0-3")
        if light > 3 or light < 0:
            raise ValueError("Light sensitivity must be between 0-3")

        value = pack('<4B', bool(humidity), humidity, bool(light), light)
        self._writeHandle(0x2a, value)

    def getSensorsSensitivity(self):
        return Sensitivity._make(unpack('<4B', self._readHandle(0x2a)))

    def setLightSensorSettings(self, delayed, running):
        if delayed not in (0, 5, 10):
            raise ValueError("Delayed must be 0, 5 or 10 minutes")
        if running not in (5, 10, 15, 30, 60):
            raise ValueError("Running time must be 5, 10, 15, 30 or 60 minutes")

        self._writeHandle(0x2c, pack('<2B', delayed, running))

    def getLightSensorSettings(self):
        return LightSensorSettings._make(unpack('<2B', self._readHandle(0x2c)))

    def getUnknown2e(self):
        return self._bToStr(self._readHandle(0x2e))

    def setBoostMode(self, on, speed, seconds):
        if speed % 25:
            raise ValueError("Speed must be a multiple of 25")
        if not on:
            speed = 0
            seconds = 0

        self._writeHandle(0x30, pack('<BHH', on, speed, seconds))

    def getBoostMode(self):
        return BoostMode._make(unpack('<BHH', self._readHandle(0x30)))

    def getUnknown32(self):
        return self._bToStr(self._readHandle(0x32))

    def setAutomaticCycles(self, setting):
        if setting < 0 or setting > 3:
            raise ValueError("Setting must be between 0-3")

        self._writeHandle(0x34, pack('<B', setting))

    def getAutomaticCycles(self):
        return unpack('<B', self._readHandle(0x34))[0]

    def setTime(self, dayofweek, hour, minute, second):
        self._writeHandle(0x36, pack('<4B', dayofweek, hour, minute, second))

    def getTime(self):
        return Time._make(unpack('<BBBB', self._readHandle(0x36)))

    def setTimeToNow(self):
        now = datetime.datetime.now()
        self.setTime(now.isoweekday(), now.hour, now.minute, now.second)

    def setSilentHours(self, on, startingHours, startingMinutes, endingHours, endingMinutes):
        if startingHours < 0 or startingHours > 23:
            raise ValueError("Starting hour is an invalid number")
        if endingHours < 0 or endingHours > 23:
            raise ValueError("Ending hour is an invalid number")
        if startingMinutes < 0 or startingMinutes > 59:
            raise ValueError("Starting minute is an invalid number")
        if endingMinutes < 0 or endingMinutes > 59:
            raise ValueError("Ending minute is an invalid number")

        value = pack('<5B', int(on),
                     startingHours, startingMinutes,
                     endingHours, endingMinutes)
        self._writeHandle(0x38, value)

    def getSilentHours(self):
        return SilentHours._make(unpack('<5B', self._readHandle(0x38)))

    def setTrickleDays(self, weekdays, weekends):
        self._writeHandle(0x3a, pack('<2B', weekdays, weekends))

    def getTrickleDays(self):
        return TrickleDays._make(unpack('<2B', self._readHandle(0x3a)))
