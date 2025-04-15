import os
import shutil 
import pyautogui
import cv2
import csv
from exif import Image

def prepare_directory():
    dir_made = False
    while dir_made == False:
        test_num = str(input('select test number: '))
        location = f'/home/nvidia/Documents/Waimanalo/data{test_num}/'
        file_rgb = location +'RGB/'
        file_ir = location + 'IR/'
        file_extra = location + 'extra/'
        file_temperature = location +'Temperatures/'
        csv_file = location + '/lat_lon.csv'
        if os.path.exists(location):
            choice = input('test number already taken, type y to overwrite : ')
            if choice == 'y':
                shutil.rmtree(location)
                os.mkdir(location)
                os.mkdir(file_ir)
                os.mkdir(file_rgb)
                os.mkdir(file_temperature)
                os.mkdir(file_extra)
                dir_made = True
            else:
                continue
        else:
            os.mkdir(location)
            os.mkdir(file_ir)
            os.mkdir(file_rgb)
            os.mkdir(file_temperature)
            os.mkdir(file_extra)
            dir_made = True
    return test_num,file_ir,file_rgb,file_temperature,file_extra,csv_file

def show_screens(image1,image2):

	screen_width, _ = pyautogui.size()
	img_width, img_height = 640, 540 
	x_pos = screen_width - img_width  
	y_pos1 = 0 
	y_pos2 = img_height
	cv2.imshow("RGB feed",image1) 
	#cv2.moveWindow("RGB feed",x_pos,y_pos1)
	cv2.imshow('IR feed',image2)
	#cv2.moveWindow('IR feed',x_pos,y_pos2)
    
  

def input_exif_data(file_ir,file_rgb,csv_to_use):
	with open(csv_to_use,'r') as csv_file:
		reader = csv.reader(csv_file)    
		for i,line in enumerate(reader):
			IR_to_add_exif = file_ir + f'Image #:{i}.jpg'
			RGB_to_add_exif =  file_rgb+f'Image #:{i}.jpg'
			with open(IR_to_add_exif, 'rb') as img1, open(RGB_to_add_exif,'rb') as img2:
				ir_image = Image(img1)
				rgb_image = Image(img2)
				ir_image.gps_latitude = line[0]
				ir_image.gps_longitude = line[1]
				ir_image.datetime = line[2]
				rgb_image.gps_latitude = line[0]
				rgb_image.gps_longitude = line[1]
				rgb_image.datetime = line[2]
				
			with open(IR_to_add_exif, 'wb') as final_ir_exif,open(RGB_to_add_exif,'wb') as final_rgb_exif:
				final_ir_exif.write(ir_image.get_file())
				final_rgb_exif.write(rgb_image.get_file())
				
