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

from . import Calima, FindCalimas

import sys, getopt

def printHelp():
    print("Calima\n")
    print("This tool prints all the information we can get from a Calima fan.\n")
    print("-h\tshow this help list")
    print("-l\tScan and list all found Calimas")
    print("-m\tSpecify Calima MAC address")
    print("-p\tSpecify Calima Pincode")
    print("-s\tScan all characteristics")

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hlm:p:",["mac=","pin="])
    except getopt.GetoptError:
        printHelp()
        sys.exit(2)

    mac_address = ""
    pincode = ""

    for opt, arg in opts:
        if opt == '-h':
            printHelp()
            sys.exit()
        elif opt == '-l':
            print(FindCalimas())
            sys.exit()
        elif opt in ("-m", "--mac"):
            mac_address = arg
        elif opt in ("-p", "--pin"):
            pincode = arg
        elif opt in ("-s", "--scan"):
            action = "scan"

    if pincode == "" or mac_address == "":
        print("You need to set both mac address and pincode to connect\n")
        sys.exit(2)

    fan = Calima(mac_address, pincode)
    if action == "scan":
        fan.scanCharacteristics()
        fan.disconnect()
    else:
        print("Device Name: ", fan.getDeviceName())
        print("Model Number: ", fan.getModelNumber())
        print("Serial Number: ", fan.getSerialNumber())
        print("Hardware Revision: ", fan.getHardwareRevision())
        print("Firmware Revision: ", fan.getFirmwareRevision())
        print("Software Revision: ", fan.getSoftwareRevision())
        print("Manufacturer: ", fan.getManufacturer())
        print("Alias: ", fan.getAlias())
        print("Unknown 1f: ", fan.getUnknown1f())
        print("Unknown 24: ", fan.getUnknown24())
        print("Unknown 26: ", fan.getUnknown26())
        print("Fan Speed Settings: ", fan.getFanSpeedSettings())
        print("Sensors Sensitivity: ", fan.getSensorsSensitivity())
        print("Light Sensor Settings: ", fan.getLightSensorSettings())
        print("Unknown 2e: ", fan.getUnknown2e())
        print("Boost Mode: ", fan.getBoostMode())
        print("Unknown 32: ", fan.getUnknown32())
        print("Automatic Cycles: ", fan.getAutomaticCycles())
        print("Time: ", fan.getTime())
        print("Silent Hours: ", fan.getSilentHours())
        print("Trickle Days: ", fan.getTrickleDays())

        while True:
            try:
                print(fan.getState())
                time.sleep(2)
            except Exception as e:
                print(e)
                fan.disconnect()
                break
