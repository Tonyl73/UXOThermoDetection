from ublox_gps import UbloxGps
import serial
# Can also use SPI here - import spidev
# I2C is not supported

port = serial.Serial('/dev/ttyACM1', baudrate=38400, timeout=1)
gps = UbloxGps(port)

def run():
  
  try: 
    print("Listening for UBX Messages.")
    lon1 = 0
    lat1 = 0
    while True:
      try: 
        coords = gps.geo_coords()
        #print("balls")
        attitude = gps.veh_attitude()
        #print("balls2")
        #imu = gps.imu_alignment()
        #print("balls3")
        #print(imu.roll)
        #print( '\npitch',imu.pitch,'\nroll', imu.roll)
        print('longitude:',coords.lon , '\nlatitude:',coords.lat,)
        print('diff lon = ', (lon1-float(coords.lon)), ' diff lat =' , lat1-float(coords.lat))
        
        lon1 = float(coords.lon)
        lat1 = float(coords.lat)
        
        #'\nheight:', coords.height, '\npitch',imu.pitch,'\nroll', imu.roll,'\nheading',attitude.heading)
      except (ValueError, IOError) as err:
        print(err)
  
  finally:
    port.close()

if __name__ == '__main__':
  run()
