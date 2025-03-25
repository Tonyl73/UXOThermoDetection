#capture.py
import os
import cv2
import numpy as np
import time
import datetime
import new_method as track
import transformations as convert
from ublox_gps import UbloxGps
import serial


port = serial.Serial('/dev/ttyACM1', baudrate=38400, timeout=1)
gps = UbloxGps(port)


IR = cv2.VideoCapture(1)
RGB = cv2.VideoCapture(0)
#RGB.set(cv2.CAP_PROP_FRAME_HEIGHT, 512) 
#RGB.set(cv2.CAP_PROP_FRAME_WIDTH, 640) 
RGB.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'UYVY'))
RGB.set(cv2.CAP_PROP_CONVERT_RGB, 1)

IR.set(cv2.CAP_PROP_FRAME_HEIGHT, 512) #use 256 for Boson 320
IR.set(cv2.CAP_PROP_FRAME_WIDTH, 640) #use 320 for Boson 320
IR.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'YU12'))
IR.set(cv2.CAP_PROP_CONVERT_RGB, 0)


test_num = input('Select test number  ')


folder = f'/home/nvidia/Documents/IR_test{test_num}/'
folder_rgb = f'/home/nvidia/Documents/RGB_test{test_num}/'
coords = gps.geo_coords()
#os.mkdir(folder)
#os.mkdir(folder_rgb)

num = 0

frameCooldown = 0
totalDetections = 0

try:
    while True:#record indefinitely (until user presses q), replace with "while True"
        ir_stream_ret, frame1 = IR.read()
		
        rgb_stream_ret, frame2 = RGB.read()

        frame2,UNCROPPED =track.crop_and_scale_rgb(frame2)
        
        
        if ir_stream_ret and rgb_stream_ret:

            #FRAME_RGB = track.detect_object_RGB(frame2)
            FRAME_IR,BOXES = track.detect_object_IR(frame1)
            #FRAME_IR_COOL = track.detect_object_IR_cool(frame1)
            cv2.imshow("RGB feed",frame2) #turn off feed when controlling via ssh
            #cv2.imshow('IR feed cool',FRAME_IR_COOL)
            cv2.imshow('IR feed',FRAME_IR)
        
            print(f'Frame #{frameCooldown}')
            print('Working')
            print(f'Boxes:{BOXES}')
            corners = track.find_corners(BOXES)
            print(f'Corners: {corners}')
            objectLocations = convert.returnSpatialLocation(corners, frame1)
            print(f'Locations: {objectLocations}')
            ts = time.time()	
            st = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y_%H-%M-%S')
            
            DETECTION = ((len(BOXES) != 0) and (frameCooldown > 60))
            print(f'Detection: {DETECTION}')
            
            
            if DETECTION:
                totalDetections = totalDetections + 1
                frameCooldown = 30
                print(f"Detection #{totalDetections}")
                goodDetection = input("Is this a valid detection?")
                goodDetection = bool(goodDetection)
                lon1 = coords.lon
                lat1 = coords.lat
                print(lat1,lon1)

            if num%10 == 0: #set interval between saved frames here
                #cv2.imwrite(folder + st + ".jpg",frame1)
                #cv2.imwrite(folder_rgb + st + ".jpg",UNCROPPED)
                time.sleep(.01)   
            num += 1
            
        frameCooldown = frameCooldown + 1
            
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
except KeyboardInterrupt:
    pass
port.close()
IR.release()
RGB.release()
cv2.destroyAllWindows()
