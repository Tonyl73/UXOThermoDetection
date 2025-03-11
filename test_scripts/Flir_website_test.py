#c#capture.py
import cv2
import numpy as np
import time


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


folder = '/media/86EA-C0D6/raw_frames/test1/IR' #ensure these are correct
folder_rgb = '/media/86EA-C0D6/raw_frames/test1/RGB'
num = 0
frame_buf=[]
frame_buf2=[]
times = []

while True:#record indefinitely (until user presses q), replace with "while True"
    ir_stream_ret, frame1 = IR.read()
    rgb_stream_ret, frame2 = RGB.read()
    if ir_stream_ret and rgb_stream_ret:
        cv2.imshow("RGB feed",frame2)
        cv2.imshow('IR feed',frame1)	
        frame_buf.append(frame1)
        frame_buf2.append(frame2)
        time_now = time.time()
        curr = time.ctime(time_now)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
IR.release()
RGB.release()
cv2.destroyAllWindows()

for i in range(len(frame_buf)):
        cv2.imwrite(f'{folder}/cap_{num}_{times[i]}.tiff', frame_buf.pop(0))
        cv2.imwrite(f'{folder_rgb}/cap_{num}_{times[i]}.tiff', frame_buf2.pop(0))
        num += 1




