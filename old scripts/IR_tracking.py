import cv2
import numpy as np



scale_factor = 0.7 



def crop_and_scale_rgb(RGB_IMAGE):
    
    IMAGE = RGB_IMAGE


    HEIGTH, WIDTH = IMAGE.shape[:2]

   
    NEW_WIDTH = int(WIDTH * scale_factor)
    NEW_HEIGTH = int(HEIGTH * scale_factor)
    resized_img = cv2.resize(IMAGE, (NEW_WIDTH, NEW_HEIGTH), interpolation=cv2.INTER_AREA)

    x_start = (NEW_WIDTH - 640) // 2
    y_start = (NEW_HEIGTH - 512) // 2
    CROPPED_IMAGE = resized_img[y_start:y_start+512, x_start:x_start+640]
    return CROPPED_IMAGE
    
def detect_object_IR(INPUT_IMAGE):

    IMAGE = INPUT_IMAGE
    GREYSCALE_IMAGE = IMAGE

    #cv2.imshow('pic before',IMAGE)

    SMOOTHED_IMAGE = cv2.medianBlur(GREYSCALE_IMAGE,5)
    
    #SMOOTHED_IMAGE = cv2.GaussianBlur(GREYSCALE_IMAGE,(3,3),0)

    IMAGE_WITH_EDGES_SHOWN = cv2.Canny(SMOOTHED_IMAGE,70,200)
    
    kernel = np.ones((5, 5), np.uint8) 

    IMAGE_WITH_THICK_EDGES= cv2.dilate(IMAGE_WITH_EDGES_SHOWN, kernel, iterations=1)

    _, BLACK_AND_WHITE_IMAGE = cv2.threshold(SMOOTHED_IMAGE,160,210,cv2.THRESH_BINARY)

    

    _,INITIAL_CONTOURS, _, = cv2.findContours(BLACK_AND_WHITE_IMAGE,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)

    LARGE_AREA_CONTOURS = []

    FINAL_CONTOURS = []

    for contour in INITIAL_CONTOURS:
        threshold_area_min = 600
        threshold_area_max = 5000
        area = cv2.contourArea(contour)
        if area > threshold_area_min and area < threshold_area_max :
            LARGE_AREA_CONTOURS.append(contour)

    for contour in LARGE_AREA_CONTOURS:
        mask = np.zeros_like(IMAGE,dtype=np.uint8)
        
        cv2.drawContours(mask, [contour], -1, 255, 100)
        overlap = cv2.bitwise_and(IMAGE_WITH_THICK_EDGES,mask)
        if np.count_nonzero(overlap) > 300:  
            FINAL_CONTOURS.append(contour)

    print(len(FINAL_CONTOURS))

    for contour in FINAL_CONTOURS:
        rect = cv2.minAreaRect(contour)
        box = cv2.boxPoints(rect)
        box = np.array(box).reshape((-1,1,2)).astype(np.int32)
        cv2.drawContours(IMAGE,[box],0,(0,0,255),2)

    return IMAGE


def detect_object_RGB2(INPUT_IMAGE):
    
    IMAGE = INPUT_IMAGE


    IMAGE_IN_HSV = cv2.cvtColor(IMAGE,cv2.COLOR_BGR2HSV)
    cv2.imshow('hsv',IMAGE_IN_HSV)
    UPPER_BOUND_COLOR = np.array([150,250,250])
    LOWER_BOUND_COLOR = np.array([100,0,0])

    MASK = cv2.inRange(IMAGE_IN_HSV,LOWER_BOUND_COLOR,UPPER_BOUND_COLOR)
#    


    result = cv2.bitwise_and(IMAGE, IMAGE, mask=MASK)

    result = cv2.medianBlur(result,7)

    GREYSCALE_IMAGE = cv2.cvtColor(result,cv2.COLOR_BGR2GRAY)

    _, BLACK_AND_WHITE_IMAGE = cv2.threshold(GREYSCALE_IMAGE,140,210,cv2.THRESH_BINARY)

   

    _,INITIAL_CONTOURS, _ = cv2.findContours(BLACK_AND_WHITE_IMAGE,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
    
    cv2.imshow('mask',result)
    LARGE_AREA_CONTOURS = []

    FINAL_CONTOURS = []



    for contour in INITIAL_CONTOURS:
        threshold_area_min = 100
        threshold_area_max = 7000
        area = cv2.contourArea(contour)
        if area > threshold_area_min and area < threshold_area_max :
            LARGE_AREA_CONTOURS.append(contour)

    BEST_RECTANGLE = 0  

    for contour in LARGE_AREA_CONTOURS:
        x,y,w,h = cv2.boundingRect(contour)
        ASPECT_RATIO = max(w,h)/min(w,h)
        AREA = cv2.contourArea(contour)
        BOUNDING_BOX_AREA = w*h
        RECTANGLE_SCORE = (AREA/BOUNDING_BOX_AREA)*(1/ASPECT_RATIO)
        if RECTANGLE_SCORE > BEST_RECTANGLE:
            FINAL_CONTOURS.append(contour)


    for contour in FINAL_CONTOURS:
        rect = cv2.minAreaRect(contour)
        box = cv2.boxPoints(rect)
        box = np.array(box).reshape((-1,1,2)).astype(np.int32)
        cv2.drawContours(IMAGE,[box],0,(0,0,255),2)

    return IMAGE


