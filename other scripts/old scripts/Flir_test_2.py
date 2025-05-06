#capture.py
import cv2
import numpy as np
import time
import datetime
import os
import new_method as nm
import matplotlib.pyplot as plt
import numpy as np

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

img_data = np.zeros((1080,1920))
fig,ax = plt.subplots()
img = plt.imshow(img_data)
plt.ion()

try:
	while True:#record indefinitely (until user presses q), replace with "while True"
			ir_stream_ret, frame1 = IR.read()

			rgb_stream_ret, frame2 = RGB.read() 
			gray_scale_image = cv2.normalize(frame1, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
			
			
			
			if ir_stream_ret and rgb_stream_ret:
				
				
				
				'''img_data = frame2
				img.set_data(img_data)
				fig.canvas.draw()
				fig.canvas.flush_events()
				plt.pause(.01)'''
				source_points = np.array([[420,114],[1425,114],[420,918],[1425,918]])
				dest_points = np.array([[0,0],[640,0],[0,512],[640,512]])
				homo, _ = cv2.findHomography(source_points,dest_points)
				output = cv2.warpPerspective(frame2,homo,(frame1.shape[1],frame1.shape[0]))
				cv2.imshow('out',output)
				#cv2.imshow("RGB feed",frame2) #turn off feed when controlling via ssh
				cv2.imshow('IR feed',gray_scale_image)
				no_green = nm.mask_green(output,gray_scale_image)
				crop ,rgb = nm.crop_and_scale_rgb(frame2)
				cv2.imshow('crop',crop)
				cv2.imshow('green mask',no_green)
			if cv2.waitKey(1) & 0xFF == ord('q'):
				break
    
except KeyboardInterrupt:
    pass

IR.release()
RGB.release()
cv2.destroyAllWindows()
print('done')


