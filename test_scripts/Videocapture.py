# Python program to illustrate 
# saving an operated video


import numpy as np
import cv2

# This will return video from the first webcam on your computer.
cap = cv2.VideoCapture(0)  

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'avc1')
#out = cv2.VideoWriter('/media/86EA-C0D6/raw_frames/test1/output.mp4', fourcc, 30.0, (1920, 1080))
out = cv2.VideoWriter('/home/nvidia/Desktop/vid_test/output.mkv', fourcc, 30.0, (1920, 1080))

# loop runs if capturing has been initialized. 
while(True):
    # reads frames from a camera 
    # ret checks return at each frame
    ret, frame = cap.read() 

    # Converts to HSV color space, OCV reads colors as BGR
    # frame is converted to hsv

    
    # output the frame
    
    
    # The original input frame is shown in the window 
    #cv2.imshow('Original', frame)

    # The window showing the operated video stream 
    
    out.write(frame)
    
    # Wait for 'a' key to stop the program 
    #if cv2.waitKey(1) & 0xFF == ord('a'):
    #    break

# Close the window / Release webcam
cap.release()

# After we release our webcam, we also release the output
out.release() 

# De-allocate any associated memory usage 
cv2.destroyAllWindows()
