import cv2
import numpy as np

scale_factor = 0.67

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
		


def crop_and_scale_rgb(RGB_IMAGE):
    
    IMAGE = RGB_IMAGE


    HEIGTH, WIDTH = IMAGE.shape[:2]

   
    NEW_WIDTH = int(WIDTH * scale_factor)
    NEW_HEIGTH = int(HEIGTH * scale_factor)
    resized_img = cv2.resize(IMAGE, (NEW_WIDTH, NEW_HEIGTH), interpolation=cv2.INTER_AREA)

    x_start = (NEW_WIDTH - 640) // 2
    y_start = (NEW_HEIGTH - 512) // 2
    CROPPED_IMAGE = resized_img[y_start:y_start+512, x_start:x_start+640]
    return CROPPED_IMAGE,IMAGE
    
  

def detect_object_IR(INPUT_IMAGE,CANVAS_IMAGE):
   
   
    SMOOTHED_IMAGE = cv2.medianBlur(INPUT_IMAGE, 3)
    #GREYSCALE_IMAGE = cv2.equalizeHist(SMOOTHED_IMAGE)
    #cv2.imshow('Smoothed Image',SMOOTHED_IMAGE)
    
    #IMAGE_WITH_EDGES_SHOWN = cv2.Canny(SMOOTHED_IMAGE, 120, 200)
    #kernel = np.ones((5, 5), np.uint8) 
    #IMAGE_WITH_THICK_EDGES = cv2.dilate(IMAGE_WITH_EDGES_SHOWN, kernel, iterations=1)

    _, BLACK_AND_WHITE_IMAGE = cv2.threshold(SMOOTHED_IMAGE, 200, 255, cv2.THRESH_BINARY)
  
    _,INITIAL_CONTOURS, _ = cv2.findContours(BLACK_AND_WHITE_IMAGE, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    print (len(INITIAL_CONTOURS))
    
    #cv2.imshow('hot',BLACK_AND_WHITE_IMAGE)
    
    LARGE_AREA_CONTOURS = [contour for contour in INITIAL_CONTOURS if 300 < cv2.contourArea(contour) < 7000]

    print (len(LARGE_AREA_CONTOURS))

    FINAL_CONTOURS = []
    centers = []
    '''for contour in LARGE_AREA_CONTOURS:
        mask = np.zeros_like(GREYSCALE_IMAGE, dtype=np.uint8)
        cv2.drawContours(mask, [contour], -1, 255, thickness=cv2.FILLED)
        overlap = cv2.bitwise_and(IMAGE_WITH_THICK_EDGES, mask)
        if np.count_nonzero(overlap) > 200:  
            FINAL_CONTOURS.append(contour)'''
    
    BEST_RECTANGLE = .35

    for contour in LARGE_AREA_CONTOURS:
        x, y, w, h = cv2.boundingRect(contour)
        center_x, center_y = x + w//2, y + h//2
        centers.append((center_x,center_y))
        ASPECT_RATIO = max(w, h) / min(w, h)
        AREA = cv2.contourArea(contour)
        BOUNDING_BOX_AREA = w * h
        RECTANGLE_SCORE = (AREA / BOUNDING_BOX_AREA) * (1 / ASPECT_RATIO)

        if RECTANGLE_SCORE > BEST_RECTANGLE:
 
            print('heated score',RECTANGLE_SCORE)
            FINAL_CONTOURS.append(contour) 

    print(len(FINAL_CONTOURS))
    
    box_locations = []
    
    i = 0
    for contour in FINAL_CONTOURS:
        i = i + 1
        rect = cv2.minAreaRect(contour)
        box = np.int0(cv2.boxPoints(rect))
        box_locations.append(box)
        cv2.putText(CANVAS_IMAGE, f"Box {i}" , tuple(box[0]), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,255,0), 1)
        cv2.drawContours(CANVAS_IMAGE, [box], 0, (0, 0, 255), 2)

    return CANVAS_IMAGE, box_locations, centers



def detect_object_IR_cool(IMAGE):
    
    SMOOTHED_IMAGE = cv2.medianBlur(IMAGE, 3)

    GREYSCALE_IMAGE = cv2.equalizeHist(SMOOTHED_IMAGE)

    _, BLACK_AND_WHITE_IMAGE_COOL = cv2.threshold(GREYSCALE_IMAGE, 20, 250, cv2.THRESH_BINARY_INV)

    _,INITIAL_CONTOURS_COOL, _ = cv2.findContours(BLACK_AND_WHITE_IMAGE_COOL, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    cv2.imshow('cool',BLACK_AND_WHITE_IMAGE_COOL)

    LARGE_AREA_CONTOURS_COOL = [contour for contour in INITIAL_CONTOURS_COOL if 800 < cv2.contourArea(contour) < 7000]

    FINAL_CONTOURS = []

    BEST_RECTANGLE = .4

    for contour in LARGE_AREA_CONTOURS_COOL:
        x, y, w, h = cv2.boundingRect(contour)
        ASPECT_RATIO = max(w, h) / min(w, h)
        AREA = cv2.contourArea(contour)
        BOUNDING_BOX_AREA = w * h
        RECTANGLE_SCORE = (AREA / BOUNDING_BOX_AREA) * (1 / ASPECT_RATIO)

        if RECTANGLE_SCORE > BEST_RECTANGLE:
         
            print('shaded score' ,RECTANGLE_SCORE)
            FINAL_CONTOURS = [contour] 

    print(len(FINAL_CONTOURS))

    for contour in FINAL_CONTOURS:
        rect = cv2.minAreaRect(contour)
        box = np.int0(cv2.boxPoints(rect))
        cv2.drawContours(IMAGE, [box], 0, (0, 0, 255), 2)
    return IMAGE

def enhance_greyscale(greyscale_img, temp_img, gradient_scale=50,delta=6):

   
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

    return enhanced_img


def mask_green(rgb_img, greyscale_img):
 
   
    hsv_img = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2HSV)
    
   
    lower_green = np.array([30, 40, 40])   
    upper_green = np.array([90, 255, 255]) 
    
   
    mask = cv2.inRange(hsv_img, lower_green, upper_green)
    
   
    greyscale_masked = greyscale_img.copy()
    greyscale_masked[mask > 0] = 0
    
    return greyscale_masked
