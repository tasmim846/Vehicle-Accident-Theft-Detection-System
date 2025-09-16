import machine
import time
from machine import I2C, Pin, PWM

# MPU6050 I2C address
MPU6050_ADDR = 0x68

# MPU6050 Registers
ACCEL_XOUT_H = 0x3B
PWR_MGMT_1 = 0x6B

# Buzzer setup
BUZZER_PIN = 10  # GPIO10 for buzzer

class MPU6050:
    def __init__(self, i2c):
        self.i2c = i2c
        # Wake up the MPU6050
        self.i2c.writeto_mem(MPU6050_ADDR, PWR_MGMT_1, b'\x00')

    def read_accel(self):
        data = self.i2c.readfrom_mem(MPU6050_ADDR, ACCEL_XOUT_H, 6)
        # Convert 16-bit signed integers from big-endian bytes
        ax = (data[0] << 8) | data[1]
        if ax > 32767:
            ax -= 65536
        ay = (data[2] << 8) | data[3]
        if ay > 32767:
            ay -= 65536
        az = (data[4] << 8) | data[5]
        if az > 32767:
            az -= 65536
        # Convert to g (assuming default sensitivity)
        ax = ax / 16384
        ay = ay / 16384
        az = az / 16384
        return (ax, ay, az)

def sound_buzzer(pin, frequency=1000, duration=0.5):
    """Sound buzzer at given frequency for specified duration"""
    buzzer = PWM(Pin(pin))
    buzzer.freq(frequency)
    buzzer.duty(512)  # 50% duty cycle
    time.sleep(duration)
    buzzer.duty(0)  # Turn off
    buzzer.deinit()

def detect_collision(threshold=1.5, interval=0.1):
    i2c = I2C(0, scl=Pin(8), sda=Pin(9))  # Use GPIO8 for SCL, GPIO9 for SDA
    mpu = MPU6050(i2c)
    print("Monitoring for collision...")
    while True:
        ax, ay, az = mpu.read_accel()
        total_accel = (ax**2 + ay**2 + az**2) ** 0.5
        # Print live acceleration values
        print("Live Accel: X={:.2f}, Y={:.2f}, Z={:.2f}, Total={:.2f}".format(ax, ay, az, total_accel))
        
        # Check for collision
        if abs(total_accel - 1) > threshold:
            print("*** COLLISION DETECTED! *** Accel: X={:.2f}, Y={:.2f}, Z={:.2f}".format(ax, ay, az))
            # Sound the buzzer
            sound_buzzer(BUZZER_PIN, frequency=2000, duration=1.0)
        time.sleep(interval)

if __name__ == "__main__":
    detect_collision()
