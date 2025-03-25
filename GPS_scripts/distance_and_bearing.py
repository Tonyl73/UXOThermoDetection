from ublox_gps import UbloxGps
import serial
import math
from geopy.distance import geodesic
import transformations as trans
import new_method as track
import cv2
# Can also use SPI here - import spidev
# I2C is not supported
try:
    ard_port = serial.Serial('/dev/ttyACM2', baudrate=115200, timeout=1)
    gps_port = serial.Serial('/dev/ttyACM1', baudrate=38400, timeout=1)
    gps = UbloxGps(gps_port)

except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
    exit()

IR = cv2.VideoCapture(1)
IR.set(cv2.CAP_PROP_FRAME_HEIGHT, 512) #use 256 for Boson 320
IR.set(cv2.CAP_PROP_FRAME_WIDTH, 640) #use 320 for Boson 320
IR.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'YU12'))
IR.set(cv2.CAP_PROP_CONVERT_RGB, 0)



def send_target_location():
    #Default state entering this function: GPS port is open, Arduino port is closed, box is detected and verified
    #Sleep timers are arbitrary to prevent race conditions with python. 
	coords = gps.geo_coords()
	print(f"Finding target with camera at lat={coords.lat} lon={coords.lon}")
	ard_port.write(b"GET_IMU\n") # Send trigger command to Arduino
	#time.sleep(0.25)  
	print("sent")
	line = ard_port.readline().decode().strip() # Read response from Arduino
	if line:
		print('line = ', line)
		try:
			# Expecting: Roll, Pitch, Yaw, Heading
			parts = line.split(',')
			if len(parts) == 4:
				roll, pitch, yaw, heading = map(float, parts)
				print(f"Received: Roll={roll}, Pitch={pitch}, Yaw={yaw}, Heading={heading}") #Optional print for debugging

				# Set camera orientation using received data, then use for processing
				trans.set_camera_orientation(roll, pitch, heading)
				target = trans.returnGPSlocation(coords.lat, coords.lon, convert.returnSpatialLocation(corners,frame1),heading)
				#time.sleep(1)
				# Send coordinates back to the Arduino for ROS2 transfer 
				response = (target[0][0],target[0][1])
				
				
		except ValueError:
			print(f"Invalid data received: {line}")
	else:
		
		print("Didn't receive response from Arduino")
	return response

def calculate_bearing(point1,point2):
	if (type(point1) != tuple) or (type(point2) != tuple):
		raise TypeError ('tuples are only supported type')
	lat1 = math.radians(point1[0])
	lat2 = math.radians(point2[0])
	diffLong = math.radians(point1[1] - point2[1])
	x = math.sin(diffLong) * math.cos(lat2)
	y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) *math.cos(diffLong))
	
	initial_bearing = math.atan2(x,y)
	initial_bearing = math.degrees(initial_bearing)
	compass_bearing = (initial_bearing +360)%360
	return compass_bearing

def run():
	frameCooldown = 0
	totalDetections = 0
	try: 
		pointA =()
		pointB =()
		
		if input("input any key for point distance"):
			if input('type 1 to set first point'):
				coords = gps.geo_coords()
				pointA = (coords.lat, coords.lon)
			if input('type 1 to set second point'):
				coords = gps.geo_coords()
				pointB = (coords.lat, coords.lon)
			
			print(f"bearing:{calculate_bearing(pointA,pointB)}")
			print(f"distance: {geodesic(pointA,pointB).meters} meters")
		
		
		
		else:		
		
			coords = gps.geo_coords()
			pointA = (coords.lat, coords.lon)
			point_2_found = False
			while point_2_found == False:#record indefinitely (until user presses q), replace with "while True"
				ir_stream_ret, frame1 = IR.read()
		
				if ir_stream_ret:
					FRAME_IR,BOXES = track.detect_object_IR(frame1)
					cv2.imshow('IR feed',FRAME_IR)
        
					print(f'Frame #{frameCooldown}')
					print('Working')
					print(f'Boxes:{BOXES}')
					corners = track.find_corners(BOXES)
					print(f'Corners: {corners}')
					objectLocations = trans.returnSpatialLocation(corners, frame1)
					print(f'Locations: {objectLocations}')
					
					
					DETECTION = ((len(BOXES) != 0) and (frameCooldown > 60))
					print(f'Detection: {DETECTION}')
					
					
					if DETECTION:
						totalDetections = totalDetections + 1
						frameCooldown = 30
						print(f"Detection #{totalDetections}")
						goodDetection = input("Is this a valid detection?")
						goodDetection = bool(goodDetection)
						pointB = send_target_location()
						point_2_found = True
					
					frameCooldown = frameCooldown + 1
					
				if cv2.waitKey(1) & 0xFF == ord('q'):
					break
			
			print(f"bearing:{calculate_bearing(pointA,pointB)}")
			print(f"distance: {geodesic(pointA,pointB).meters}")
	
	except KeyboardInterrupt:
		pass
  
	finally:
		print('done')
		ard_port.close()
		gps_port.close()
		IR.release()
		cv2.destroyAllWindows()

if __name__ == '__main__':
	run()
