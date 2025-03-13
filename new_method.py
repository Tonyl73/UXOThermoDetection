import cv2
import numpy as np

scale_factor = 0.65

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
    
  

def detect_object_IR(INPUT_IMAGE):
   
   
    SMOOTHED_IMAGE = cv2.medianBlur(INPUT_IMAGE, 3)
    #GREYSCALE_IMAGE = cv2.equalizeHist(SMOOTHED_IMAGE)
    cv2.imshow('Smoothed Image',SMOOTHED_IMAGE)
    
    #IMAGE_WITH_EDGES_SHOWN = cv2.Canny(SMOOTHED_IMAGE, 120, 200)
    #kernel = np.ones((5, 5), np.uint8) 
    #IMAGE_WITH_THICK_EDGES = cv2.dilate(IMAGE_WITH_EDGES_SHOWN, kernel, iterations=1)

    _, BLACK_AND_WHITE_IMAGE = cv2.threshold(SMOOTHED_IMAGE, 120, 255, cv2.THRESH_BINARY)
  
    _,INITIAL_CONTOURS, _ = cv2.findContours(BLACK_AND_WHITE_IMAGE, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    print (len(INITIAL_CONTOURS))
    cv2.imshow('hot',BLACK_AND_WHITE_IMAGE)
    
    LARGE_AREA_CONTOURS = [contour for contour in INITIAL_CONTOURS if 300 < cv2.contourArea(contour) < 7000]

    print (len(LARGE_AREA_CONTOURS))

    FINAL_CONTOURS = []
    '''for contour in LARGE_AREA_CONTOURS:
        mask = np.zeros_like(GREYSCALE_IMAGE, dtype=np.uint8)
        cv2.drawContours(mask, [contour], -1, 255, thickness=cv2.FILLED)
        overlap = cv2.bitwise_and(IMAGE_WITH_THICK_EDGES, mask)
        if np.count_nonzero(overlap) > 200:  
            FINAL_CONTOURS.append(contour)'''
    
    BEST_RECTANGLE = .4

    for contour in LARGE_AREA_CONTOURS:
        x, y, w, h = cv2.boundingRect(contour)
        ASPECT_RATIO = max(w, h) / min(w, h)
        AREA = cv2.contourArea(contour)
        BOUNDING_BOX_AREA = w * h
        RECTANGLE_SCORE = (AREA / BOUNDING_BOX_AREA) * (1 / ASPECT_RATIO)

        if RECTANGLE_SCORE > BEST_RECTANGLE:
 
            print('heated score',RECTANGLE_SCORE)
            FINAL_CONTOURS.append(contour) 

    print(len(FINAL_CONTOURS))
    
    box_locations = []
    
    for contour in FINAL_CONTOURS:
        rect = cv2.minAreaRect(contour)
        box = np.int0(cv2.boxPoints(rect))
        box_locations.append(box)
        cv2.drawContours(INPUT_IMAGE, [box], 0, (0, 0, 255), 2)

    return INPUT_IMAGE, box_locations



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

def detect_object_RGB(INPUT_IMAGE):
   
    IMAGE = INPUT_IMAGE

    if IMAGE is None:
        raise ValueError("err")

    

    IMAGE_IN_HSV = cv2.cvtColor(IMAGE, cv2.COLOR_BGR2HSV)

    cv2.imshow('hsv',IMAGE_IN_HSV)
    LOWER_BOUND_COLOR = np.array([90, 0, 0])
    UPPER_BOUND_COLOR = np.array([150, 250, 250])
    MASK = cv2.inRange(IMAGE_IN_HSV, LOWER_BOUND_COLOR, UPPER_BOUND_COLOR)

    result = cv2.bitwise_and(IMAGE, IMAGE, mask=MASK)
    GREYSCALE_IMAGE = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)

    _, BLACK_AND_WHITE_IMAGE = cv2.threshold(GREYSCALE_IMAGE, 100, 255, cv2.THRESH_BINARY)

    _,INITIAL_CONTOURS, _ = cv2.findContours(BLACK_AND_WHITE_IMAGE, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    
    LARGE_AREA_CONTOURS = [contour for contour in INITIAL_CONTOURS if 800 < cv2.contourArea(contour) < 7000]

    print(len(LARGE_AREA_CONTOURS))

    BEST_RECTANGLE = .4 
    FINAL_CONTOURS = []

    for contour in LARGE_AREA_CONTOURS:
        x, y, w, h = cv2.boundingRect(contour)
        ASPECT_RATIO = max(w, h) / min(w, h)
        AREA = cv2.contourArea(contour)
        BOUNDING_BOX_AREA = w * h
        RECTANGLE_SCORE = (AREA / BOUNDING_BOX_AREA) * (1 / ASPECT_RATIO)

        if RECTANGLE_SCORE > BEST_RECTANGLE:
            
            FINAL_CONTOURS = [contour] 

    print(len(FINAL_CONTOURS))

    for contour in FINAL_CONTOURS:
        rect = cv2.minAreaRect(contour)
        box = np.int0(cv2.boxPoints(rect))
        cv2.drawContours(IMAGE, [box], 0, (0, 0, 255), 2)

    return IMAGE
