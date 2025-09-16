# System Diagram Description

## Visual System Overview

```
                    COLLISION DETECTION SYSTEM
    ┌─────────────────────────────────────────────────────────────┐
    │                                                             │
    │  ┌─────────────┐    I2C Bus     ┌─────────────────────────┐ │
    │  │   MPU6050   │◀──────────────▶│      ESP32-S3 PLUS      │ │
    │  │ Accelerometer│   GPIO8(SCL)   │                         │ │
    │  │             │   GPIO9(SDA)   │  ┌─────────────────────┐ │ │
    │  │ • X-Axis    │                │  │   WiFi Module       │ │ │
    │  │ • Y-Axis    │                │  │   802.11 b/g/n      │ │ │
    │  │ • Z-Axis    │                │  └─────────────────────┘ │ │
    │  └─────────────┘                │                         │ │
    │                                  │  ┌─────────────────────┐ │ │
    │                                  │  │   I2C Controller    │ │ │
    │  ┌─────────────┐   GPIO10       │  │   PWM Controller    │ │ │
    │  │   BUZZER    │◀─────────────────┤   CPU (Dual Core)   │ │ │
    │  │ (Active)    │                │  │   Memory (8MB)      │ │ │
    │  │             │                │  └─────────────────────┘ │ │
    │  │ ♪ Emergency │                │                         │ │
    │  │   Pattern   │                └─────────────────────────┘ │
    │  └─────────────┘                            │               │
    │                                             │               │
    └─────────────────────────────────────────────┼───────────────┘
                                                  │
                                                  │ WiFi
                                                  │ Connection
                                                  ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                    INTERNET SERVICES                        │
    │                                                             │
    │  ┌─────────────────────────────────────────────────────────┐ │
    │  │              TELEGRAM BOT API                           │ │
    │  │                                                         │ │
    │  │  POST https://api.telegram.org/bot<TOKEN>/sendMessage   │ │
    │  │                                                         │ │
    │  │  {                                                      │ │
    │  │    "chat_id": "5217461051",                            │ │
    │  │    "text": "🚨 COLLISION DETECTED! 🚨                  │ │
    │  │             Location: GPS Coordinates                   │ │
    │  │             Acceleration: X=2.5g Y=1.8g Z=0.9g"        │ │
    │  │  }                                                      │ │
    │  └─────────────────────────────────────────────────────────┘ │
    │                                                             │
    │  ┌─────────────────────────────────────────────────────────┐ │
    │  │                GOOGLE MAPS                              │ │
    │  │                                                         │ │
    │  │  Location Link:                                         │ │
    │  │  https://www.google.com/maps?q=23.798,90.449          │ │
    │  └─────────────────────────────────────────────────────────┘ │
    └─────────────────────────────────────────────────────────────┘
                                    │
                                    │ Notification
                                    ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                   USER DEVICE                               │
    │                                                             │
    │  ┌─────────────────────────────────────────────────────────┐ │
    │  │                TELEGRAM APP                             │ │
    │  │                                                         │ │
    │  │  🚨 🚨 COLLISION DETECTED! 🚨 🚨                        │ │
    │  │                                                         │ │
    │  │  Vehicle accident detected at Current time              │ │
    │  │  Location: [GPS Link] (clickable)                       │ │
    │  │  Acceleration: X=2.50g, Y=1.80g, Z=-0.95g             │ │
    │  │                                                         │ │
    │  │  [View Location on Map] 📍                             │ │
    │  └─────────────────────────────────────────────────────────┘ │
    └─────────────────────────────────────────────────────────────┘
```

## Signal Flow Diagram

```
    SENSOR READING CYCLE (100ms intervals)
    ════════════════════════════════════════
    
    MPU6050 ──┐
              │ I2C Read
              │ (6 bytes)
              ▼
    ┌─────────────────────┐
    │   Raw Data          │
    │  ┌─────────────────┐│
    │  │ ACCEL_XOUT_H    ││
    │  │ ACCEL_XOUT_L    ││
    │  │ ACCEL_YOUT_H    ││ ──┐
    │  │ ACCEL_YOUT_L    ││   │ Convert to
    │  │ ACCEL_ZOUT_H    ││   │ signed int
    │  │ ACCEL_ZOUT_L    ││   │
    │  └─────────────────┘│ ◀─┘
    └─────────────────────┘
              │
              │ ÷ 16384 (sensitivity)
              ▼
    ┌─────────────────────┐
    │   G-Force Values    │
    │  ┌─────────────────┐│
    │  │ ax = X / 16384  ││
    │  │ ay = Y / 16384  ││ ──┐
    │  │ az = Z / 16384  ││   │ Calculate
    │  └─────────────────┘│   │ magnitude
    └─────────────────────┘ ◀─┘
              │
              │ √(ax² + ay² + az²)
              ▼
    ┌─────────────────────┐
    │ Total Acceleration  │
    │                     │ ──┐
    │   total_accel       │   │ Compare with
    │                     │   │ threshold
    └─────────────────────┘ ◀─┘
              │
              │ if |total - 1| > 1.5g
              ▼
    ┌─────────────────────┐
    │   COLLISION         │
    │   DETECTED!         │
    │                     │
    └─────────────────────┘
              │
        ┌─────┼─────┐
        │     │     │
        ▼     ▼     ▼
    ┌─────┐ ┌───┐ ┌────────┐
    │BUZZ │ │LOG│ │TELEGRAM│
    │ER   │ │   │ │  API   │
    └─────┘ └───┘ └────────┘
```

## Layered Architecture Detail

```
    APPLICATION LAYER
    ═════════════════════════════════════════════════════════════
    ┌─────────────────────────────────────────────────────────┐
    │            VehicleMonitoringSystem                      │
    │  ┌─────────────────────────────────────────────────────┐│
    │  │ Main Loop:                                          ││
    │  │  while True:                                        ││
    │  │    1. Read sensor data                              ││
    │  │    2. Process acceleration                          ││
    │  │    3. Check collision threshold                     ││
    │  │    4. Handle collision events                       ││
    │  │    5. Sleep 100ms                                   ││
    │  └─────────────────────────────────────────────────────┘│
    └─────────────────────────────────────────────────────────┘
    
    BUSINESS LOGIC LAYER
    ═════════════════════════════════════════════════════════════
    ┌─────────────────────┐ ┌─────────────────────────────────┐
    │  CollisionDetector  │ │          DataLogger             │
    │ ┌─────────────────┐ │ │ ┌─────────────────────────────┐ │
    │ │ calculate_      │ │ │ │ log_sensor_data()           │ │
    │ │ magnitude()     │ │ │ │ • Live acceleration         │ │
    │ │ • √(x²+y²+z²)   │ │ │ │ • Console output            │ │
    │ │                 │ │ │ │                             │ │
    │ │ is_collision()  │ │ │ │ log_collision_event()       │ │
    │ │ • |total-1|>1.5 │ │ │ │ • Emergency alert           │ │
    │ │ • Threshold     │ │ │ │ • GPS coordinates           │ │
    │ └─────────────────┘ │ │ └─────────────────────────────┘ │
    └─────────────────────┘ └─────────────────────────────────┘
    
    ACTUATOR LAYER
    ═════════════════════════════════════════════════════════════
    ┌───────────────┐ ┌─────────────┐ ┌───────────────────────┐
    │BuzzerController│ │WiFiManager │ │  TelegramNotifier     │
    │┌─────────────┐│ │┌───────────┐│ │┌─────────────────────┐│
    ││sound_alert()││ ││connect()  ││ ││send_collision_      ││
    ││• PWM freq   ││ ││• SSID/PWD ││ ││alert()              ││
    ││• Duty cycle ││ ││• Timeout  ││ ││• Format message     ││
    ││• Pattern    ││ ││           ││ ││• URL encode         ││
    ││  - 2000Hz   ││ ││is_        ││ ││• POST request       ││
    ││  - 4000Hz   ││ ││connected()││ ││• Error handling     ││
    ││  - 8 cycles ││ ││• Status   ││ ││                     ││
    │└─────────────┘│ │└───────────┘│ │└─────────────────────┘│
    └───────────────┘ └─────────────┘ └───────────────────────┘
    
    SENSOR LAYER
    ═════════════════════════════════════════════════════════════
    ┌─────────────────────────────────────────────────────────┐
    │                 MPU6050Sensor                           │
    │ ┌─────────────────────────────────────────────────────┐ │
    │ │ read_acceleration():                                │ │
    │ │  1. Read 6 bytes via I2C (0x3B register)          │ │
    │ │  2. Convert high/low bytes to signed integers      │ │
    │ │  3. Apply sensitivity scaling (÷16384)             │ │
    │ │  4. Return (ax, ay, az) in g-force units           │ │
    │ │                                                     │ │
    │ │ _convert_raw_data():                                │ │
    │ │  • Combine high/low bytes                           │ │
    │ │  • Handle two's complement                          │ │
    │ │  • 16-bit signed integer conversion                 │ │
    │ └─────────────────────────────────────────────────────┘ │
    └─────────────────────────────────────────────────────────┘
    
    HARDWARE LAYER
    ═════════════════════════════════════════════════════════════
    ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐
    │  ESP32-S3   │ │   MPU6050   │ │        BUZZER           │
    │┌───────────┐│ │┌───────────┐│ │┌───────────────────────┐│
    ││CPU Cores  ││ ││3-Axis     ││ ││Active Buzzer          ││
    ││• Core 0   ││ ││Accelero   ││ ││• Piezo element        ││
    ││• Core 1   ││ ││meter      ││ ││• Built-in oscillator  ││
    ││           ││ ││           ││ ││• PWM controlled       ││
    ││WiFi Radio ││ ││I2C Bus    ││ ││• 2-5V operation       ││
    ││• 2.4GHz   ││ ││• 400kHz   ││ ││                       ││
    ││• 802.11n  ││ ││• 0x68     ││ ││                       ││
    ││           ││ ││           ││ ││                       ││
    ││GPIO Pins  ││ ││Registers  ││ ││                       ││
    ││• I2C      ││ ││• 0x3B-40  ││ ││                       ││
    ││• PWM      ││ ││• Accel    ││ ││                       ││
    │└───────────┘│ │└───────────┘│ │└───────────────────────┘│
    └─────────────┘ └─────────────┘ └─────────────────────────┘
```
