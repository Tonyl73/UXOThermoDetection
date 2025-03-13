import cv2 as cv
import cameratransform as ct

# Displays coordinate of points clicked on image 
def click_event(event, x, y, flags, params): 
    # checking for left mouse clicks 
    if event == cv.EVENT_LBUTTONDOWN: 
  
        # Print coordinates to terminal
        print(x, ' ', y) 

# EO camera settings (FLIR Hadron 640)

# Change these according to your camera setup
FOCAL_LENGTH = 13.6 # Focal length in mm
SENSOR_SIZE = (4.3,5.9) # Sensor size in mm
IMAGE_SIZE = (640,512) # Image size in pixels
SENSOR_SIZE = (6.14, 4.15)
POS_X = 0 # x location of camera in meters (relative frame of reference for image info)
POS_Y = 0
ELEVATION = 2.13 # Camera elevation in meters
TILT = 3 # Tilt angle in degrees, 0 is facing ground, 90 is parallel to ground, 180 is facing upward
HEADING = 0
ROLL = 0

def FOOT_TO_METER(foot):
    return foot*0.3408

# Declare camera object
cam = ct.Camera(ct.RectilinearProjection(focallength_mm=FOCAL_LENGTH, image=IMAGE_SIZE, sensor = SENSOR_SIZE),
                ct.SpatialOrientation(pos_x_m = POS_X, pos_y_m = POS_Y, elevation_m=ELEVATION, tilt_deg = TILT, roll_deg = ROLL, heading_deg = HEADING))
'''
print(cam.spaceFromImage([1,1]))
print(cam.spaceFromImage([1,6944]))
print(cam.spaceFromImage([9248,6944]))
print(cam.spaceFromImage([9248,6944]))
'''

image = cv.imread(r"IR_test4\27-02-2025_17-03-20.jpg")
# Get the image dimensions
height, width, channels = image.shape 
# Print the dimensions
print(f"Height: {height} pixels")
print(f"Width: {width} pixels")
print(f"Channels: {channels}") # only for color images
#cv.rectangle(image, (x1, y1), (x2, y2), color, thickness)

# Assume we have array of boxes of the form [xmin, ymin, xmax, ymax]
x11 = 343
y11 = 101
x21 = 382
y21 = 176

x12 = 296
y12 = 114
x22 = 323
y22 = 170

x13 = 237
y13 = 76
x23 = 255
y23 = 206

objheight = 0.4
location1 = [(x11+x21)/2, (y11+y21)/2]
pos = cam.spaceFromImage(location1, Z=FOOT_TO_METER(0.5))
pos[0] = pos[0]*3.28*12
pos[1] = pos[1]*3.28*12
pos[2] = pos[2]*3.28*12
print(pos)

location2 = [(x12+x22)/2, (y12+y22)/2]
pos2 = cam.spaceFromImage(location2, Z=FOOT_TO_METER(0.5))
pos2[0] = pos2[0]*3.28*12
pos2[1] = pos2[1]*3.28*12
pos2[2] = pos2[2]*3.28*12
print(pos2)

location3 = [(x13+x23)/2, (y13+y23)/2]
pos3 = cam.spaceFromImage(location3, Z=FOOT_TO_METER(0.5))
pos3[0] = pos3[0]*3.28*12
pos3[1] = pos3[1]*3.28*12
pos3[2] = pos3[2]*3.28*12
print(pos3)

origin = cam.imageFromSpace([0,0,0])
print(origin)

cv.rectangle(image, (x11, y11), (x21, y21), (0,0,255), thickness = 1)
cv.rectangle(image, (x12, y12), (x22, y22), (0,0,255), thickness = 1)
cv.rectangle(image, (x13, y13), (x23, y23), (0,0,255), thickness = 1)
cv.putText(image, f"Object 1: ({pos[0]:.3},{pos[1]:.3},{pos[2]:.3})\"", org=(x11,y11), fontFace=cv.FONT_HERSHEY_SIMPLEX, fontScale=0.4, color=(0,255,0), thickness=1)
cv.putText(image, f"Object 2: ({pos2[0]:.3},{pos2[1]:.3},{pos2[2]:.3})\"", org=(x12,y12), fontFace=cv.FONT_HERSHEY_SIMPLEX, fontScale=0.4, color=(0,255,0), thickness=1)
cv.putText(image, f"Object 3: ({pos3[0]:.3},{pos3[1]:.3},{pos3[2]:.3}\")", org=(x13,y13), fontFace=cv.FONT_HERSHEY_SIMPLEX, fontScale=0.4, color=(0,255,0), thickness=1)
cv.circle(image, (320, 330), 3, (255,0,255), 5)
cv.putText(image, f"Origin: ({0},{0},{0})\"", org=(320, 330), fontFace=cv.FONT_HERSHEY_SIMPLEX, fontScale=0.4, color=(0,255,0), thickness=1)
cv.imshow('image', image)

cv.setMouseCallback('image', click_event) 
cv.waitKey(0)
