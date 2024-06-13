import time
import adafruit_dht
import board

pin = board.D7
dhtDevice = adafruit_dht.DHT22(pin, use_pulseio=False)

while True:
    try:
        temperature = dhtDevice.temperature
        humidity = dhtDevice.humidity
        print(f"Temperature type: {type(temperature)}")  # 형식 확인
        print(f"Temperature: {temperature}°C, Humidity: {humidity}%")
        time.sleep(1)
    except RuntimeError as error:
        print(error.args[0])
    except KeyboardInterrupt:
        break

# Clean up resources
dhtDevice.exit()

