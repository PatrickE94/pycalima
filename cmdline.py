#!/usr/bin/env python3

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


from pycalima.Calima import Calima,FindCalimas

import sys, getopt, time

def printHelp():
    print("\nCommand control and monitoring tool for PAX Calima fan. Let the air flow!\n")
    print("-h\tshow this help list")
    print("-l\tScan and list all found Calimas")
    print("-m MAC\tSpecify Calima MAC address")
    print("-p PIN\tSpecify Calima Pincode")
    print("-s\tScan all characteristics")
    print("-b SEC\tEnable Boost mode for SEC seconds")
    print("-t SPD\tSet trickle speed to SPD in all modes. Use max 2000.")
    print("\tWarning: this will make fan run at at this speed all the time")

def main():

# Define vars
    action = ""
    mac_address = ""
    pincode = ""
    boostsecs = 0
    tricklespeed = 950


    try:
        opts, args = getopt.getopt(sys.argv[1:], "hb:lsm:p:t:")
    except getopt.GetoptError:
        printHelp()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            printHelp()
            sys.exit()
        elif opt == '-l':
            print(FindCalimas())
            sys.exit()
        elif opt in ("-m"):
            mac_address = arg
        elif opt in ("-p"):
            pincode = arg
        elif opt in ("-s"):
            action = "scan"
        elif opt == '-b':
            action = "startboost" 
            boostsecs= int(arg)
        elif opt == '-t':
            action = "settrickle" 
            tricklespeed= int(arg)
        else:
            usage()
            sys.exit(2)

    if pincode == "" or mac_address == "":
        print("You need to set both mac address and pincode to connect\n")
        print("Run me with -h to get some help\n")
        sys.exit(2)

    fan = Calima(mac_address, pincode)

    if action == "startboost":
        print("Setting Boost mode for {} seconds".format(boostsecs))
        fan.setBoostMode(1,2250,boostsecs)
        time.sleep(2)
        print(fan.getBoostMode())
        fan.disconnect()
    elif action == "scan":
        fan.scanCharacteristics()
        #currentState = fan.getStateShort()
        #for item in currentState._fields:
        #  print("{}={} ".format(item,getattr(currentState, item)),end='')
        fan.disconnect()
    elif action == "settrickle":
        print("Setting tricklespeed to {} ".format(tricklespeed))
        fan.setFanSpeedSettings(2250,975,tricklespeed)
        time.sleep(2)
        print(fan.getFanSpeedSettings())

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
        print("Factory Settings Changed: ", fan.getFactorySettingsChanged())
        print("Mode: ", fan.getMode())
        print("Fan Speed Settings: ", fan.getFanSpeedSettings())
        print("Sensors Sensitivity: ", fan.getSensorsSensitivity())
        print("Light Sensor Settings: ", fan.getLightSensorSettings())
        print("Heat Distributor: ", fan.getHeatDistributor())
        print("Boost Mode: ", fan.getBoostMode())
        print("Led: ", fan.getLed())
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


if __name__ == '__main__':
   main()
