<<<<<<< HEAD
# ESP32-S3 Vehicle Collision Detection System

A comprehensive collision detection system using ESP32-S3 microcontroller with MPU6050 accelerometer, buzzer alerts, and Telegram notifications.

## 🚗 System Overview

This system continuously monitors vehicle acceleration and detects potential collisions. When a collision is detected (acceleration > 1.5g), it:
- 🔊 Sounds an emergency buzzer pattern
- 📱 Sends detailed Telegram notification with location
- 📊 Logs collision data with acceleration values

## 🔧 Hardware Components

| Component | Model | Purpose |
|-----------|-------|---------|
| Microcontroller | ESP32-S3 PLUS | Main processing unit with WiFi |
| Accelerometer | MPU6050 | 3-axis acceleration sensing |
| Buzzer | Active Buzzer | Audio collision alerts |
| Breadboard | Half-size | Component mounting |
| Jumper Wires | M-M, M-F | Connections |

## 📐 Wiring Diagram

### ESP32-S3 Pin Connections

```
ESP32-S3 PLUS          MPU6050
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GPIO8 (SCL)      ←→    SCL
GPIO9 (SDA)      ←→    SDA
3.3V             ←→    VCC
GND              ←→    GND

ESP32-S3 PLUS          BUZZER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GPIO10           ←→    Positive (+)
GND              ←→    Negative (-)
```

### Physical Wiring Layout

```
          ESP32-S3 PLUS
     ┌─────────────────────┐
     │ 3.3V  GND  GPIO8-9  │
     │  │     │     │   │  │
     └──┼─────┼─────┼───┼──┘
        │     │     │   │
        │     │   ┌─┴───┴─┐
        │     │   │ MPU6050│
        │     │   │ SCL SDA│
        │     │   │ VCC GND│
        │     │   └───┬───┬┘
        │     │       │   │
        └─────┼───────┘   │
              └───────────┘

     GPIO10    GND
        │       │
        │   ┌───┴───┐
        └───┤ BUZZER │
            │   +   - │
            └───────┘
```

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    VEHICLE MONITORING SYSTEM                 │
├─────────────────────────────────────────────────────────────┤
│                     APPLICATION LAYER                        │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │            VehicleMonitoringSystem                      │ │
│  │  • Orchestrates all components                          │ │
│  │  • Main execution loop                                  │ │
│  │  • Error handling & recovery                            │ │
│  └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    BUSINESS LOGIC LAYER                      │
│  ┌─────────────────┐  ┌─────────────────────────────────────┐ │
│  │ CollisionDetector│  │           DataLogger                │ │
│  │ • Threshold calc │  │ • Console logging                   │ │
│  │ • Magnitude calc │  │ • Collision events                  │ │
│  │ • Decision logic │  │ • Live sensor data                  │ │
│  └─────────────────┘  └─────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                      ACTUATOR LAYER                          │
│  ┌─────────────────┐  ┌─────────────┐  ┌─────────────────┐   │
│  │ BuzzerController│  │ WiFiManager │  │TelegramNotifier │   │
│  │ • PWM control   │  │ • Connect   │  │ • API calls     │   │
│  │ • Alert patterns│  │ • Monitor   │  │ • Error handle  │   │
│  │ • Emergency tone│  │ • Reconnect │  │ • URL encoding  │   │
│  └─────────────────┘  └─────────────┘  └─────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                       SENSOR LAYER                           │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                 MPU6050Sensor                           │ │
│  │  • I2C communication                                   │ │
│  │  • Raw data conversion                                 │ │
│  │  • 3-axis acceleration reading                         │ │
│  │  • Gravity unit conversion                             │ │
│  └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                     HARDWARE LAYER                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐   │
│  │   ESP32-S3  │  │   MPU6050   │  │       BUZZER        │   │
│  │ • WiFi      │  │ • Accel X   │  │ • PWM Audio         │   │
│  │ • I2C       │  │ • Accel Y   │  │ • Emergency Pattern │   │
│  │ • PWM       │  │ • Accel Z   │  │ • Collision Alert   │   │
│  │ • Processing│  │ • I2C Bus   │  │                     │   │
│  └─────────────┘  └─────────────┘  └─────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Data Flow Diagram

```
┌─────────────┐    ┌──────────────┐    ┌─────────────────┐
│   MPU6050   │───▶│ Read Accel   │───▶│ Calculate       │
│ Accelerometer│    │ X, Y, Z      │    │ Magnitude       │
└─────────────┘    └──────────────┘    └─────────────────┘
                                                │
                   ┌─────────────────┐         ▼
                   │ Live Data       │◀────┌─────────────────┐
                   │ Console Log     │     │ Threshold       │
                   └─────────────────┘     │ Comparison      │
                                          └─────────────────┘
                                                │
                                          ┌─────▼─────┐
                                          │ Collision │
                                          │ Detected? │
                                          └─────┬─────┘
                                               │ YES
                          ┌────────────────────┼────────────────────┐
                          ▼                    ▼                    ▼
                   ┌─────────────┐    ┌─────────────────┐  ┌─────────────────┐
                   │   Buzzer    │    │ Console Alert   │  │ Telegram Alert  │
                   │ Emergency   │    │ with Location   │  │ with GPS Link   │
                   │   Pattern   │    │ & Acceleration  │  │ & Details       │
                   └─────────────┘    └─────────────────┘  └─────────────────┘
```

## ⚙️ Configuration

Edit the `Config` class in `main.py`:

```python
class Config:
    # WiFi Settings - CHANGE THESE
    WIFI_SSID = "YourWiFiName"
    WIFI_PASSWORD = "YourWiFiPassword"
    
    # Telegram Settings - CHANGE THESE
    BOT_TOKEN = "your_bot_token_here"
    CHAT_ID = "your_chat_id_here"
    
    # Collision Threshold (g-force)
    COLLISION_THRESHOLD = 1.5  # Adjust sensitivity
    
    # Pin Assignments
    SCL_PIN = 8   # I2C Clock
    SDA_PIN = 9   # I2C Data
    BUZZER_PIN = 10  # PWM Buzzer
```

## 🚀 Installation & Setup

### 1. Hardware Assembly
1. Connect MPU6050 to ESP32-S3 using I2C (pins 8 & 9)
2. Connect buzzer to GPIO10 and GND
3. Power ESP32-S3 via USB-C

### 2. Software Setup
1. Flash MicroPython firmware to ESP32-S3
2. Configure WiFi credentials in `main.py`
3. Set up Telegram bot and get bot token
4. Upload code to ESP32-S3

### 3. Telegram Bot Setup
1. Message @BotFather on Telegram
2. Create new bot: `/newbot`
3. Get bot token from BotFather
4. Get your chat ID by messaging @userinfobot

### 4. Upload and Run
```bash
# Upload main.py to ESP32-S3
mpremote connect /dev/cu.usbserial-10 fs cp main.py :/main.py

# Run the system
mpremote connect /dev/cu.usbserial-10 run main.py
```

## 📊 System Operation

### Normal Operation
```
=== Vehicle Collision Detection System ===
Connecting to WiFi: YourWiFiName
WiFi connected successfully! IP: 192.168.1.100
System initialized successfully!
Monitoring threshold: 1.5g
WiFi Status: Connected (IP: 192.168.1.100)
========================================
Live Accel: X=0.43, Y=0.53, Z=-0.80, Total=1.05
Live Accel: X=0.44, Y=0.52, Z=-0.79, Total=1.04
...
```

### Collision Detected
```
Live Accel: X=2.50, Y=1.80, Z=0.95, Total=3.20

🚨 COLLISION DETECTED!

🚗 Vehicle: V123
📍 Location: https://www.google.com/maps?q=23.798258,90.449808
🕒 Time: Current time

Sending Telegram notification...
Telegram notification sent successfully!
```

## 🔧 Troubleshooting

### Common Issues

**WiFi Connection Failed**
- Check SSID and password in Config
- Ensure WiFi is 2.4GHz (ESP32 limitation)
- Verify WiFi range and signal strength

**MPU6050 Not Responding**
- Check I2C wiring (SCL=8, SDA=9)
- Verify 3.3V power connection
- Test with I2C scanner code

**Telegram Not Working**
- Verify bot token and chat ID
- Check internet connectivity
- Test bot with @BotFather first

**False Collision Detection**
- Adjust `COLLISION_THRESHOLD` in Config
- Check sensor mounting (should be stable)
- Calibrate for your vehicle's normal vibration

### Debug Mode
Add debug prints to troubleshoot:
```python
print(f"Raw acceleration: {ax}, {ay}, {az}")
print(f"WiFi status: {self.wifi_manager.is_connected()}")
```

## 📱 Telegram Notification Format

When collision detected, you'll receive:
```
🚨 🚨 COLLISION DETECTED! 🚨 🚨

Vehicle accident detected at Current time
Location: https://www.google.com/maps?q=23.798257,90.449808
Acceleration: X=2.50g, Y=1.80g, Z=-0.95g
```

## 🔋 Power Consumption

| Component | Current Draw | Notes |
|-----------|--------------|-------|
| ESP32-S3 | ~80mA | Active WiFi |
| MPU6050 | ~3.9mA | Normal operation |
| Buzzer | ~30mA | When active |
| **Total** | **~114mA** | During collision alert |

## 📈 Performance Metrics

- **Sensor Reading Rate**: 10Hz (100ms interval)
- **Collision Detection Latency**: <200ms
- **Telegram Notification Time**: 2-5 seconds
- **Buzzer Response Time**: <100ms
- **WiFi Reconnection Time**: 5-10 seconds

## 🛡️ Safety Features

- **Graceful Degradation**: Works without WiFi
- **Error Recovery**: Automatic WiFi reconnection
- **Fail-Safe Operation**: Buzzer works independently
- **Threshold Protection**: Prevents false positives
- **Status Monitoring**: Real-time system health

## 📄 License

This project is open source. Feel free to modify and distribute.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit your changes
4. Push to the branch
5. Create Pull Request

## 📞 Support

For issues and questions:
- Check troubleshooting section
- Review wiring connections
- Verify configuration settings
- Test individual components

---
**Made with ❤️ for vehicle safety**
=======
# Vehicle-Accident-Theft-Detection-System
>>>>>>> 251e6f15d576ef07d19e0ad23316e4c91b1b51ae
