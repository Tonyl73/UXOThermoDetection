import spidev

spi = spidev.SpiDev()
spi.open(0, 0) 
spi.max_speed_hz = 1000000

response = spi.xfer2([0x00])
print(f"IMU Response: {response}")
