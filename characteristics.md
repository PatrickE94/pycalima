Pax Calima Bluetooth Characteristics
====================================

This tiny document intends to describe what is discovered about the
Characteristics of this fan.

## Miscellaneus
Protocol is little-endian.

## Characteristics

Formats are specified using keywords or
[struct format characters](https://docs.python.org/2/library/struct.html#format-characters).

| Name               | Example Value                       | Format          | R/W |
|--------------------|-------------------------------------|-----------------|-----|
| Device Name        | "Calima"                            | String          | R   |
| Appearance         | 0 (Generic)                         | Numeric         | R   |
| Model number       | "10"                                | String          | R   |
| Serial number      | "000000"                            | String          | R   |
| Hardware revision  | "01.00"                             | String          | R   |
| Firmware revision  | "01.01"                             | String          | R   |
| Software revision  | "01.04"                             | String          | R   |
| Manufacturer       | "PAX"                               | String          | R   |
| Auth               | 01:02:03:04                         | BBBB            | W   |
| Alias              | "My Vent"                           | 20 bytes String | R/W |
| Is Clock Set       | 00(true) or 02(false)               | B               | R   |
| Status             | 00:00:5f:00:0b:00:81:06:02:00:00:00 | HHHHBHB         | R   |
| Settings changed   | 01                                  | ?               | R   |
| Mode               | 00                                  | B               | R/W |
| Fan speed          | 01:00:02:00:03:00                   | HHH             | R/W |
| Sensors            | 01:03:01:03                         | BBBB            | R/W |
| Light sensor       | 01:02                               | BB              | R/W |
| Heat Distributor   | 19:00:00:34:08                      | BHH             | R/W |
| Manual fan control | 01:02:03:02:03                      | BHH             | R/W |
| Led                | 00                                  | B               | R/W |
| Automatic Cycles   | 00                                  | B               | R/W |
| Time               | 01:02:03:04                         | BBBB            | R/W |
| Silent hours       | 01:02:03:04:05                      | BBBBB           | R/W |
| Trickle settings   | 01:00                               | BB              | R/W |
| Reset              | 00:00                               | I               | W   |

Note: Handles are now omitted since we are using UUID's. These are too long to write out in
the table. Check the code!

### Auth
The pincode is encoded as a single large number represented in Hex.
```
01234567 => 12D687 => 87:D6:12:00
```

### Alias
The App always transmits 20 bytes. If the string is less than 20 bytes,
the rest is null padded.

### IsCLockSet
If Calima was power cycled the LED will become red on fron side which mean the internal clock is not set. This is reflected by this parameter.

```
    Clock is set: 00
Clock is not set: 02
```

### Fan speed settings
Fan speed is ranging from 0 to 2500 and measured in RPM.
Thus the fan speed is represented by 2 bytes. The speed
can only be configured in steps of 25.

```
   00:00:00:00:00:00
Humidity|Light|Trickle

Example: 1650 rpm => 72:06
Note little endian (0672 => 7206) and 2 byte width.
```

### Sensors
```
 Humidity|Light
    01:03:01:03
On/Off |  |  Sensitivity
       |  On/Off
Sensitivity  

Sensitivity ranges from 1 -> 3 (Low, Medium, High)
On/Off is a boolean 0 or 1 (Off, On)
```

### Light sensor settings
```
Delay|Runtime
   05:0f
```
The example above is 5 minutes delayed start and 15 minutes runtime.

### Manual fan control
This is mainly used by boost function and to preview settings while in-app.
```
On/Off|Speed|Runtime
    01:00:02:01:01
```

The fan speed is the same as with Fan speed settings.
The runtime is measured in seconds, two byte numeric
(e.g. `300 seconds => 012c => 2c:01`).

### Automatic cycles
Single byte setting ranging from 0 to 3. Values are below.
```
  off: 00
30min: 01
60min: 02
90min: 03
```

### Time
```
         01:10:35:3b
Day of week |  |  Second
         Hour  Minute
```
The example above is Monday, 16:53:59.

__TODO__: Is the day zero or one indexed?

### Silent hours
```
          01:16:00:07:00
      On/Off |  |  |  Ending minutes
Starting hours  |  Ending hours
 Starting minutes
```

Example above is On from 22:00 to 07:00.

### Trickle weekdays/weekend setting
```
Weekdays|Weekend
      01:00
```
The example above is on during weekdays, off during weekends.

### Status
Current values and state.

```
  00:00:5f:00:0b:00:81:06:02:00:00:00
Humidity |    Light |     |  Unknown
    Temp |          |     |
             Fanspeed     Mode
```
Unsure about the temperature field, but it seems about right.  
Fan speed is measured as always in RPM.

## Normal App connection flow
1.  0x0018 (Auth) and 0x0036 (Set time) are sent.
2.  Read of characteristics starts to gather data for the app view.
3.  0x0021 is continuously polled every other second to update state.
