import serial
import time

# ----------------- CONFIGURATION ----------------- #
PORT = "COM3"        # Change this to your actual port (e.g., COM4 on Windows, /dev/ttyUSB0 on Linux)
BAUD_RATE = 115200   # Must match the Arduino Serial.begin() value
TIMEOUT = 2          # Seconds

# ----------------- MAIN CODE ----------------- #
try:
    # Initialize serial connection
    print(f"🔌 Connecting to {PORT} at {BAUD_RATE} baud...")
    ser = serial.Serial(PORT, BAUD_RATE, timeout=TIMEOUT)
    time.sleep(2)  # Wait for Arduino reset
    print("✅ Connected successfully! Reading sensor data...\n")

    while True:
        # Read a line from serial
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if line:
            print(line)

except serial.SerialException:
    print("❌ ERROR: Could not connect to the serial port. Check your port and connection.")

except KeyboardInterrupt:
    print("\n🛑 Stopped by user.")

finally:
    try:
        ser.close()
        print("🔒 Serial connection closed.")
    except:
        pass
