from ublox_gps import UbloxGps
import serial
import math
from geopy.distance import geodesic
import transformations as trans
import new_method as track
import cv2
import threading 
# Can also use SPI here - import spidev
# I2C is not supported
try:
    ard_port = serial.Serial('/dev/device_ECDA3B60BB24', baudrate=115200, timeout=1)
    gps_port = serial.Serial('/dev/device_01a9', baudrate=38400, timeout=1)
    gps = UbloxGps(gps_port)

except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
    exit()

IR = cv2.VideoCapture(1)
IR.set(cv2.CAP_PROP_FRAME_HEIGHT, 512) #use 256 for Boson 320
IR.set(cv2.CAP_PROP_FRAME_WIDTH, 640) #use 320 for Boson 320
IR.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'YU12'))
IR.set(cv2.CAP_PROP_CONVERT_RGB, 0)

current_lat, current_lon = None, None

def collect_lat_lon():
	global gps
	global current_lat
	global current_lon
	while True:
		coords = gps.geo_coords()
		if coords:
			current_lat = coords.lat
			current_lon = coords.lon
			
thread = threading.Thread(target= collect_lat_lon,daemon = True)
thread.start()


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
			print(parts)
			if len(parts) == 4:
				roll, pitch, yaw, heading = map(float, parts)
				print(f"Received: Roll={roll}, Pitch={pitch}, Yaw={yaw}, Heading={heading}") #Optional print for debugging

				# Set camera orientation using received data, then use for processing
				trans.set_camera_orientation(roll, pitch, heading)
				target = trans.returnGPSlocation(coords.lat, coords.lon, trans.returnSpatialLocation(corners,frame1),heading)
				#time.sleep(1)
				# Send coordinates back to the Arduino for ROS2 transfer 
				response = (target[0][0],target[0][1])
				
				
		except ValueError:
			print(f"Invalid data received: {line}")
	else:
		
		print("Didn't receive response from Arduino")
	print(response)
	return response

def calculate_bearing(point1,point2):
	if (type(point1) != tuple) or (type(point2) != tuple):
		raise TypeError("Only tuples are supported as arguments")

	lat1 = math.radians(point1[0])
	lat2 = math.radians(point2[0])

	diffLong = math.radians(point2[1] - point1[1])

	x = math.sin(diffLong) * math.cos(lat2)
	y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(diffLong))

	initial_bearing = math.atan2(x, y)

	# Now we have the initial bearing but math.atan2 return values
	# from -180° to + 180° which is not what we want for a compass bearing
	# The solution is to normalize the initial bearing as shown below
	initial_bearing = math.degrees(initial_bearing)
	compass_bearing = (initial_bearing + 360) % 360

	return compass_bearing

frameCooldown = 0
totalDetections = 0

try: 
	pointA =()
	pointB =()
	mode = input("input '1' to perform a point to point gps test , input '2' to test ryans transform code ")
	if mode == '1':
		while pointA == ():
			if input('input 1 to set first point ') == '1':
				pointA = (current_lat, current_lon)
		while pointB == ():
			if input('input 1 to set second point'):
				coords = gps.geo_coords()
				pointB = (current_lat, current_lon)
		
		print(f"bearing :{calculate_bearing(pointA,pointB)} degrees")
		print(f"distance: {geodesic(pointA,pointB).meters} meters")
	
	
	
	elif mode == '2':		
	
	
		pointA = (current_lat, current_lon)
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
				
				
				DETECTION = ((len(BOXES) != 0) and (frameCooldown > 70))
				print(f'Detection: {DETECTION}')
				
				if cv2.waitKey(1) & 0xFF == ord('q'):
					break
					
				if DETECTION:
					totalDetections = totalDetections + 1
					frameCooldown = 30
					print(f"Detection #{totalDetections}")
					goodDetection = input("Is this a valid detection?, input anything for yes ")
					goodDetection = bool(goodDetection)
					if goodDetection == True:
						pointB = send_target_location()
						point_2_found = True
				
				frameCooldown = frameCooldown + 1
				
			
		
		print(f"bearing:{calculate_bearing(pointA,pointB)} degrees")
		print(f"distance: {geodesic(pointA,pointB).meters} meters")

except KeyboardInterrupt:
	pass

finally:
	
	print('done')
	ard_port.close()
	gps_port.close()
	IR.release()
	cv2.destroyAllWindows()


