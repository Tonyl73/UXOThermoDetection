#capture.py
import os
import cv2
import numpy as np
import time
import datetime
import new_method as track

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

os.mkdir(folder)
os.mkdir(folder_rgb)

num = 0

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
        
           
            print('Working')
            print(BOXES)
            ts = time.time()	
            st = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y_%H-%M-%S')

            if num%10 == 0: #set interval between saved frames here
                #cv2.imwrite(folder + st + ".jpg",frame1)
                #cv2.imwrite(folder_rgb + st + ".jpg",UNCROPPED)
                time.sleep(.01)   
            num += 1
            
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
except KeyboardInterrupt:
    pass

IR.release()
RGB.release()
cv2.destroyAllWindows()
