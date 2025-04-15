#capture.py
import cv2
import numpy as np
import time
import datetime
import os


IR = cv2.VideoCapture(1)
RGB = cv2.VideoCapture(0)
#RGB.set(cv2.CAP_PROP_FRAME_HEIGHT, 512) 
#RGB.set(cv2.CAP_PROP_FRAME_WIDTH, 640) 
RGB.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'UYVY'))
RGB.set(cv2.CAP_PROP_CONVERT_RGB, 1)

IR.set(cv2.CAP_PROP_FRAME_HEIGHT, 512) #use 256 for Boson 320
IR.set(cv2.CAP_PROP_FRAME_WIDTH, 640) #use 320 for Boson 320
IR.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('Y','U','1','2'))
IR.set(cv2.CAP_PROP_CONVERT_RGB, 0)


test_num = input('Select test number  ')


folder = f'/home/nvidia/Documents/IR_test{test_num}/'
folder_rgb = f'/home/nvidia/Documents/RGB_test{test_num}/'
folder1 = f'/home/nvidia/Documents/Temperature{test_num}/'

os.mkdir(folder)
os.mkdir(folder1)
os.mkdir(folder_rgb)

num = 0

try:
    while True:#record indefinitely (until user presses q), replace with "while True"
        ir_stream_ret, frame1 = IR.read()
        print((frame1/100)-273.15)
        rgb_stream_ret, frame2 = RGB.read()
        gray_scale_image = cv2.normalize(frame1, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        if ir_stream_ret and rgb_stream_ret:
            cv2.imshow("RGB feed",frame2) #turn off feed when controlling via ssh
            cv2.imshow('IR feed',gray_scale_image)
            print('Working')
            ts = time.time()	
            st = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y_%H-%M-%S')
	   
            #if num% 10 == 0: #set interval between saved frames here
            if cv2.waitKey(1) & 0xFF == ord('t'):
                ir_frame = folder + st
                temp_frame = folder1 + st
                rgb_frame = folder_rgb + st 

                cv2.imwrite(ir_frame + ".jpg",gray_scale_image)
                cv2.imwrite(temp_frame + ".png", frame1)
                cv2.imwrite(rgb_frame + ".jpg",frame2)
                time.sleep(.01)
                
                print('saved')
            num += 1
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
except KeyboardInterrupt:
    pass

IR.release()
RGB.release()
cv2.destroyAllWindows()
print('done')


