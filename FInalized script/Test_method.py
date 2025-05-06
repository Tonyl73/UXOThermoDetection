import cv2
import numpy as np



def find_corners(box_array):
    num_boxes = len(box_array)
    corners = []
    for i in range(0, num_boxes):
        maxX = np.max(box_array[i][:,0])
        maxY = np.max(box_array[i][:,1])
        minX = np.min(box_array[i][:,0])
        minY = np.min(box_array[i][:,1])
        corners.append([minX, minY, maxX, maxY])
    return corners
		


def crop_and_scale_rgb(RGB_IMAGE,SCALE_FACTOR = 0.67):
    
    IMAGE = RGB_IMAGE
    HEIGTH, WIDTH = IMAGE.shape[:2]
    NEW_WIDTH = int(WIDTH * SCALE_FACTOR)
    NEW_HEIGTH = int(HEIGTH * SCALE_FACTOR)
    resized_img = cv2.resize(IMAGE, (NEW_WIDTH, NEW_HEIGTH), interpolation=cv2.INTER_AREA)
    x_start = (NEW_WIDTH - 640) // 2
    y_start = (NEW_HEIGTH - 512) // 2
    CROPPED_IMAGE = resized_img[y_start:y_start+512, x_start:x_start+640]
    return CROPPED_IMAGE,IMAGE

def homographic_transform(IMAGE_IR,IMAGE_RGB):
	source_points = np.array([[420,114],[1425,114],[420,918],[1425,918]])
	dest_points = np.array([[0,0],[640,0],[0,512],[640,512]])
	homo, _ = cv2.findHomography(source_points,dest_points)
	output = cv2.warpPerspective(IMAGE_RGB,homo,(IMAGE_IR.shape[1],IMAGE_IR.shape[0]))
	return output
    
  

def detect_object_IR(INPUT_IMAGE_IR,INPUT_TEMPERATURES,CANVAS_IMAGE):
	
    
   
	#SMOOTH OUT THE IMAGE AND FIND AVERAGE VALUE
    SMOOTHED_IMAGE = cv2.medianBlur(INPUT_IMAGE_IR, 3)
    AVERAGE_VALUE = np.mean(INPUT_TEMPERATURES)
    STANDARD_DEVIATION = np.std(INPUT_TEMPERATURES)
    TEMPS_IMAGE = INPUT_IMAGE_IR.copy()
    TEMPS_IMAGE[TEMPS_IMAGE < (AVERAGE_VALUE + STANDARD_DEVIATION)] = 0
    
    print(AVERAGE_VALUE)
   
   #DETERMINE THRESHOLD VALUE BASED ON THE TOP 75 PERCENTILE
    THRESHOLD_VALUE =  np.percentile(SMOOTHED_IMAGE,85)
    print(THRESHOLD_VALUE)
    
    #APPLY REGULAR,UTSO,AND ADAPTIVE THRESHOLDING 
    _,REGULAR_THRESHOLD_IMAGE = cv2.threshold(SMOOTHED_IMAGE, THRESHOLD_VALUE, 255, cv2.THRESH_BINARY_INV)
    ADAPTIVE_THRESHOLD_IMAGE = cv2.adaptiveThreshold(SMOOTHED_IMAGE,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,1201,-(np.mean(SMOOTHED_IMAGE)*.3))
    _, OTSU_THRESHOLD_IMAGE = cv2.threshold(SMOOTHED_IMAGE, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    
    #SUTRACT ALL THRESHOLDING FOR FINAL IMAGE
    FINAL_THRESHOLD = ADAPTIVE_THRESHOLD_IMAGE - REGULAR_THRESHOLD_IMAGE - OTSU_THRESHOLD_IMAGE
    _,FINAL_THRESHOLD = cv2.threshold(FINAL_THRESHOLD, 250, 255, cv2.THRESH_BINARY)
    #ERODE THEN USE OPENING ON FINAL IMAGE
    KERNEL = cv2.getStructuringElement(cv2.MORPH_RECT,(5,5))
    FINAL_IMAGE = cv2.morphologyEx(FINAL_THRESHOLD,cv2.MORPH_OPEN,KERNEL)
    
    #FIND CONTOURS
    _,INITIAL_CONTOURS, _ = cv2.findContours(FINAL_IMAGE, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    
    
    cv2.imshow('thresh',REGULAR_THRESHOLD_IMAGE)
    cv2.imshow('thresh adapt',ADAPTIVE_THRESHOLD_IMAGE)
    cv2.imshow('thresh otsu',OTSU_THRESHOLD_IMAGE)
    cv2.imshow('final',FINAL_IMAGE)
    cv2.imshow('temps',TEMPS_IMAGE)
    
    LARGE_AREA_CONTOURS = [cont for cont in INITIAL_CONTOURS if 300 < cv2.contourArea(cont) < 7000]

    

   
    box_locations = []
    centers = []
    print(f'final cont {len(LARGE_AREA_CONTOURS)}')
    
    for contour in LARGE_AREA_CONTOURS:
        x, y, w, h = cv2.boundingRect(contour)
        center_x, center_y = x + w//2, y + h//2
        centers.append((center_x,center_y))
        AREA = cv2.contourArea(contour)
        BOUNDING_BOX_AREA = w * h
       


    for i,contour in enumerate(LARGE_AREA_CONTOURS):

        rect = cv2.minAreaRect(contour)
        box = np.int0(cv2.boxPoints(rect))
        box_locations.append(box)
        cv2.putText(CANVAS_IMAGE, f"Box {i}" , tuple(box[0]), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,255,0), 1)
        cv2.drawContours(CANVAS_IMAGE, [box], 0, (0, 0, 255), 2)
    
    CANVAS_IMAGE_COLOR = cv2.applyColorMap(CANVAS_IMAGE, cv2.COLORMAP_HOT)

    return CANVAS_IMAGE, box_locations, centers, CANVAS_IMAGE_COLOR




def enhance_greyscale(greyscale_img, temp_img, gradient_scale=150,delta=20):

   
    temp_img = temp_img.astype(np.float32) 
    grad_x = np.abs(temp_img[:,delta:] - temp_img[:,:-delta])
    grad_y = np.abs(temp_img[delta:,:] - temp_img[:-delta,:])
    
    grad_x = np.pad(grad_x, ((0,0), (delta,0)), mode ='edge')
    grad_y = np.pad(grad_y, ((delta,0),(0,0)), mode ='edge')
    
    temp_gradient = np.sqrt(grad_x**2 + grad_y**2)


    temp_gradient = (temp_gradient - np.min(temp_gradient)) / (np.max(temp_gradient) - np.min(temp_gradient) + 1e-6)
    
    temp_gradient *= gradient_scale

 
    enhanced_img = greyscale_img - temp_gradient
    enhanced_img = np.clip(enhanced_img, 0, 255).astype(np.uint8)
    
    cv2.waitKey(0)
    return enhanced_img


def mask_green(rgb_img, greyscale_img):
 
   
    hsv_img = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2HSV)
    
   
    lower_green = np.array([30, 40, 40])   
    upper_green = np.array([90, 255, 255]) 
    
   
    mask = cv2.inRange(hsv_img, lower_green, upper_green)
    
   
    greyscale_masked = greyscale_img.copy()
    greyscale_masked[mask > 0] = 0
    
    return greyscale_masked




