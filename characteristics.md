Pax Calima Bluetooth Characteristics
====================================

This tiny document intends to describe what is discovered about the
Characteristics of this fan.

## Miscellaneus
Protocol is little-endian.

## Characteristics

Formats are specified using keywords or
[struct format characters](https://docs.python.org/2/library/struct.html#format-characters).

| Handle | Name               | Example Value                       | Format          | R/W |
|--------|--------------------|-------------------------------------|-----------------|-----|
| 0x0003 | Device Name        | "Calima"                            | String          | R   |
| 0x0003 | Appearance         | 0 (Generic)                         | Numeric         | R   |
| 0x000d | Model number       | "10"                                | String          | R   |
| 0x000b | Serial number      | "000000"                            | String          | R   |
| 0x000f | Hardware revision  | "01.00"                             | String          | R   |
| 0x0011 | Firmware revision  | "01.01"                             | String          | R   |
| 0x0013 | Software revision  | "01.04"                             | String          | R   |
| 0x0015 | Manufacturer       | "PAX"                               | String          | R   |
| 0x0018 | Auth               | 01:02:03:04                         | BBBB            | W   |
| 0x001c | Alias              | "My Vent"                           | 20 bytes String | R/W |
| 0x001f | IsClockSet         | 00 or 02                            | -               | R   |
| 0x0021 | Status             | 00:00:5f:00:0b:00:81:06:02:00:00:00 | HHHHBHB         | R   |
| 0x0024 | Unknown            | 01                                  | -               | R/W?|
| 0x0026 | Unknown            | 00                                  | -               | R/W?|
| 0x0028 | Fan speed          | 01:00:02:00:03:00                   | HHH             | R/W |
| 0x002a | Sensors            | 01:03:01:03                         | BBBB            | R/W |
| 0x002c | Light sensor       | 01:02                               | BB              | R/W |
| 0x002e | Unknown            | 19:00:00:34:08                      | -               | R/W?|
| 0x0030 | Manual fan control | 01:02:03:02:03                      | BHH             | R/W |
| 0x0032 | Unknown            | 00:00                               | -               | R/W?|
| 0x0034 | Automatic Cycles   | 00                                  | B               | R/W |
| 0x0036 | Time               | 01:02:03:04                         | BBBB            | R/W |
| 0x0038 | Silent hours       | 01:02:03:04:05                      | BBBBB           | R/W |
| 0x003a | Trickle settings   | 01:00                               | BB              | R/W |

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
  ClockIsSet:  00
ClockIsNotSet: 02
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
Humidity |    Light |     |     |  
    Temp |          |     |     Unknown
             Fanspeed     Unknown mode short
```
Unsure about the temperature field, but it seems about right.  
Fan speed is measured as always in RPM.

#### Unknown mode short
```
01:00 When light(no), given mode (trickle), sensors(on)
01:00 when light(no), given mode (trickle), sensors(off)
11:00 When light(no), given mode (BOOST), sensors(off)
12:00 When light(yes), given mode (Booost), sensors(on)
43:0b When light(yes), given mode (humidity), sensors(on)
63:08 randomly in trickle mode a while after shower has been used
02:00 When light(no), given mode (silent), sensors(on), silent(on)
02:00 When light(no?), given mode (light), sensors(on), silent(off)
```
Representation sticks better with current mode/sensor values than set mode and values.

The last two bytes are complete unknown for now.

### Unknown Characteristics
Below are a few undecoded characteristics with their recorded values.
```
0x001f = 00
0x0024 = 01
0x0026 = 00
0x002e = 19:00:00:34:08
0x0032 = 00:00
```

## Normal App connection flow
1.  0x0018 (Auth) and 0x0036 (Set time) are sent.
2.  Read of characteristics starts to gather data for the app view.
3.  0x0021 is continuously polled every other second to update state.
