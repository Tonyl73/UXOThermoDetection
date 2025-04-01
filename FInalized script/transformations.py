import cv2 as cv
import cameratransform as ct
import numpy as np
import math

# EO camera settings (FLIR Hadron 640)

# Change these according to your camera setup
FOCAL_LENGTH = 13.6 # Focal length in mm
SENSOR_SIZE = (4.3,5.9) # Sensor size in mm
IMAGE_SIZE = (640,512) # Image size in pixels
SENSOR_SIZE = (6.14, 4.15)
POS_X = 0 # x location of camera in meters (relative frame of reference for image info)
POS_Y = 0
ELEVATION = 1 # Camera elevation in meters
TILT = 90 # Tilt angle in degrees, 0 is facing ground, 90 is parallel to ground, 180 is facing upward
HEADING = 0
ROLL = 0
objheight = 0.5 # How high up are your objects expected to be; 0.5 works for dirt box

# Displays coordinate of points clicked on image 
def click_event(event, x, y, flags, params): 
    # checking for left mouse clicks 
    if event == cv.EVENT_LBUTTONDOWN: 
  
        # Print coordinates to terminal
        print(x, ' ', y) 

# Declare camera object
cam = ct.Camera(ct.RectilinearProjection(focallength_mm=FOCAL_LENGTH, image=IMAGE_SIZE, sensor = SENSOR_SIZE),
                ct.SpatialOrientation(pos_x_m = POS_X, pos_y_m = POS_Y, elevation_m=ELEVATION, tilt_deg = TILT, roll_deg = ROLL, heading_deg = HEADING))

def set_camera_orientation(roll, tilt, heading):
    """Update the camera’s tilt, roll, and heading before processing."""
    global cam, TILT, ROLL, HEADING
    ROLL = tilt
    TILT = roll + 90.0 #90 degree offset to agree with note in TILT above (i.e., 90 degree is parallel to ground)
    HEADING = heading

    # Reinitialize camera with updated orientation
    cam = ct.Camera(ct.RectilinearProjection(focallength_mm=FOCAL_LENGTH, image=IMAGE_SIZE, sensor=SENSOR_SIZE),
                    ct.SpatialOrientation(pos_x_m=POS_X, pos_y_m=POS_Y, elevation_m=ELEVATION,
                                          tilt_deg=TILT, roll_deg=ROLL, heading_deg=HEADING))

def returnSpatialLocation(boxes, image):
	# Get the image dimensions
	height, width = image.shape 
	# Print the dimensions
	print(f"Height: {height} pixels")
	print(f"Width: {width} pixels")
	# print(f"Channels: {channels}") # only for color images

	# Assume we have array of boxes of the form [xmin, ymin, xmax, ymax]
	num_boxes = len(boxes)

	locationsOnImage = []
	for i in range(0, num_boxes):
		xavg = (boxes[i][0] + boxes[i][2])/2
		yavg = (boxes[i][1] + boxes[i][3])/2
		print(f'averages: {xavg,yavg}')
		locationsOnImage.append([xavg,yavg])
		
	positions = []
	for i in range(0, num_boxes):
		positions.append(cam.spaceFromImage(locationsOnImage[i], Y = 2))
	
	return positions

def returnGPSlocation(lat, long, positions, heading):
    #cam = ct.Camera(ct.RectilinearProjection(focallength_mm=FOCAL_LENGTH, image=IMAGE_SIZE, sensor = SENSOR_SIZE),
                    #ct.SpatialOrientation(pos_x_m = POS_X, pos_y_m = POS_Y, elevation_m=ELEVATION, tilt_deg = TILT, roll_deg = ROLL, heading_deg = HEADING))
    cam.setGPSpos(lat, long)
    GPSpositions = []
    num_objects = np.size(positions,0)
    print(num_objects)
    for i in range (0,num_objects):
        #print(f"i={i}")
        HEADING_RAD = HEADING*math.pi/180
        #print(HEADING_RAD)
        latunit = 1/(111139)
        longunit = 1/(111139)*math.cos(long)
        #print(latunit,longunit)
        x = positions[i][0]
        y = positions[i][1]
        z = positions[i][2]
        longGPS = long + x*longunit
        #print(x*longunit*math.sin(HEADING_RAD))
        latGPS = lat + y*latunit
        #print(f"x,y,z={x},{y},{z}")
        GPSpositions.append([latGPS, longGPS])
    return GPSpositions
