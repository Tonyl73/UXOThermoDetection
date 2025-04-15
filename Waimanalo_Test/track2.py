#capture.py
import os
import cv2
import numpy as np
import time
import datetime
import new_method as track
import transformations as convert
import house_keeping as clean
from ublox_gps import UbloxGps
import csv
import serial


# Initialize GPS and Arduino ports, make sure to close the Arduino port prior to opening GPS

try:
    ard_port = serial.Serial('/dev/device_ECDA3B60BB24', baudrate=115200, timeout=1)
    gps_port = serial.Serial('/dev/device_01a9', baudrate=38400, timeout=1)
    gps = UbloxGps(gps_port)


except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
    exit()



test_num,folder_ir,folder_rgb, folder_temperatures,folder_extra, csv_filename = clean.prepare_directory()



IR = cv2.VideoCapture(1)
RGB = cv2.VideoCapture(0)
RGB.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'UYVY'))
RGB.set(cv2.CAP_PROP_CONVERT_RGB, 1)

IR.set(cv2.CAP_PROP_FRAME_HEIGHT, 512) #use 256 for Boson 320
IR.set(cv2.CAP_PROP_FRAME_WIDTH, 640) #use 320 for Boson 320
IR.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('Y','1','6',' '))
IR.set(cv2.CAP_PROP_CONVERT_RGB, 0)



coords = gps.geo_coords()



num = 0
image_num = 0
frameCooldown = 0
totalDetections = 0


def send_target_location():
    #Default state entering this function: GPS port is open, Arduino port is closed, box is detected and verified
    #Sleep timers are arbitrary to prevent race conditions with python. 
	coords = gps.geo_coords()
	print(f"Finding target with camera at lat={coords.lat} lon={coords.lon}")
	ard_port.write(b"GET_IMU\n") # Send trigger command to Arduino
	#time.sleep(0.25)  
	line = ard_port.readline().decode().strip() # Read response from Arduino
	if line:
		try:
			# Expecting: Roll, Pitch, Yaw, Heading
			parts = line.split(',')
			if len(parts) == 4:
				roll, pitch, yaw, heading = map(float, parts)
				print(f"Received: Roll={roll}, Pitch={pitch}, Yaw={yaw}, Heading={heading}") #Optional print for debugging

				# Set camera orientation using received data, then use for processing
				convert.set_camera_orientation(roll, pitch, heading)
				target = convert.returnGPSlocation(coords.lat, coords.lon, convert.returnSpatialLocation(corners,frame1),heading)
				#time.sleep(1)
				# Send coordinates back to the Arduino for ROS2 transfer 
				response = f"{target[0][0]:.7f},{target[0][1]:.7f}\n"
				ard_port.write(response.encode())
				print(f"Sent: {response.strip()}") #Optional print for debugging
				
		except ValueError:
			print(f"Invalid data received: {line}")
	else:
		print("Didn't receive response from Arduino")
	#time.sleep(1)


try:
	with open(csv_filename,'w',newline='') as csv_file:
		writer = csv.writer(csv_file)
		while True:#record indefinitely (until user presses q), replace with "while True"
			
			ir_stream_ret, frame1 = IR.read()
			rgb_stream_ret, frame2 = RGB.read()
			
			frame2,UNCROPPED =track.crop_and_scale_rgb(frame2)
			grey_scale_image = cv2.normalize(frame1, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
			
			
			if ir_stream_ret and rgb_stream_ret:
				
				#grey_scale_image1 =track.enhance_greyscale(grey_scale_image,frame1)
				
				#cv2.imshow('enhanced', grey_scale_image1)
				
				grey_scale_image2 = track.mask_green(frame2,grey_scale_image)
				
				cv2.imshow('no green', grey_scale_image2)
				
				grey_scale_image ,BOXES, centers  = track.detect_object_IR(grey_scale_image2 ,grey_scale_image)
				
				#FRAME_IR_COOL = track.detect_object_IR_cool(frame1)
				
				
				clean.show_screens(frame2,grey_scale_image)
				
				corners = track.find_corners(BOXES)
				objectLocations = convert.returnSpatialLocation(corners, grey_scale_image)
				ts = time.time()	
				st = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y_%H-%M-%S')
				
				#print(f'Frame #{frameCooldown}')
				#print('Working')
				print(f'Boxes:{BOXES}')
				print(f'Centers: {centers}')
				print(f'frame1 {np.shape(frame1)}')
				
				#print(f'Corners: {corners}')
				#print(f'Locations: {objectLocations}')
				center_temps = []
				
				for i in range(0, len(centers)):
					temperature = frame1[centers[i][1]][centers[i][0]]/100 - 273.15
					print(f'Temperature of box {i}: {temperature}')
					center_temps.append(temperature)
				
				DETECTION = ((len(BOXES) != 0) and (frameCooldown > 60))
				print(f'Detection: {DETECTION}')
				
				if cv2.waitKey(1) & 0xFF == ord('q'):
					break
				
				'''if DETECTION:
					goodDetection = input("Is this a valid detection?")
					goodDetection = bool(goodDetection)
					frameCooldown = 0

					if goodDetection:
						print("Sending to Arduino")
						send_target_location()'''

				if num%10 == 0: #set interval between saved frames here
					final_image_ir = folder_ir +f'Image #:{image_num}' + ".jpg"
					final_image_rgb = folder_rgb + f'Image #:{image_num}' +  ".jpg"
					final_temperature_frame = folder_temperatures + f'Image #:{image_num}' + '.png'
					final_extra = folder_extra + f'Image #:{image_num}' +  ".jpg"
					cv2.imwrite(final_image_ir,grey_scale_image)
					cv2.imwrite(final_image_rgb,UNCROPPED)
					cv2.imwrite(final_temperature_frame,frame1)
					cv2.imwrite(final_extra, grey_scale_image2)
					if coords.lat < 0:
						ref_lat = 'S'
					else:
						ref_lat = 'N'
					if coords.lon < 0:
						ref_lon = 'W'
					else:
						ref_lon = 'E'
					writer.writerow([np.abs(coords.lat),np.abs(coords.lon),st,ref_lat,ref_lon,tuple(center_temps)])
					image_num += 1
					time.sleep(.01)   
				num += 1
				
			frameCooldown = frameCooldown + 1
				
        
    
except KeyboardInterrupt:
    pass
    
#clean.input_exif_data(folder_ir,folder_rgb,csv_filename)

	 
ard_port.close()
gps_port.close()
IR.release()
RGB.release()
cv2.destroyAllWindows()
