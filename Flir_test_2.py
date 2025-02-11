#capture.py
import cv2
import numpy as np
import time
import datetime

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


folder = '/media/86EA-C0D6/raw_frames/test1/IR'
folder_rgb = '/media/86EA-C0D6/raw_frames/test1/RGB'
num = 0
framenum = 0
try:
    while True:#record indefinitely (until user presses q), replace with "while True"
        ir_stream_ret, frame1 = IR.read()
        rgb_stream_ret, frame2 = RGB.read()
        if ir_stream_ret and rgb_stream_ret:
            cv2.imshow("RGB feed",frame2) #turn off feed when controlling via ssh
            cv2.imshow('IR feed',frame1)
            print('Working')
            ts = time.time()	
            st = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y_%H-%M-%S')
            if num%10 == 0: #set interval between saved frames here
                cv2.imwrite(folder + "/frame#" + str(framenum) + ' '+ st + ".jpg",frame1)
                cv2.imwrite(folder_rgb + "/frame#" + str(framenum) + ' '+ st + ".jpg",frame2)
                time.sleep(.01)
                framenum+=1
            num += 1
            
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
except KeyboardInterrupt:
    pass

IR.release()
RGB.release()
cv2.destroyAllWindows()



