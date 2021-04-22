import cv2
import os
import sys
import argparse
from .make_panels import blur_image, collage, finish_strip, grid_borders, image_search, make_panels, rotate_image
from .make_panels import *
import numpy as np


minvert = 800
htvr = 1 #horizontal-to-vertical ratio
minhorz = minvert * htvr


#Function to make an individual panel.
def make_panel(topic, square_size=100, num_columns=7, borders=False, blur=False):
	if not directory_exists(topic):
		print("Directory for '"+topic+"' does not exist.")
		image_search(topic)
	pinboard = collage(topic, square_size=square_size, num_columns=num_columns, borders=True, blur=True)
	background = finish_strip(pinboard)
	return background
	
# Concatenate, but also add a blur over the line:
def smush_together(img, to_append):
	h, w, c = img.shape #The original image ~~ mostly interested in that w value.
	appended = cv2.hconcat([img, to_append])
	height, width, channels = appended.shape #That width is how we know where to put the line (for blurring)

	# Now to try to make some blurs on the lines: 
	mask = np.full((height, width, channels), fill_value=1)
	
	# Make the one horizontal line (Derivative of blur_image.py.)
	blur_thickness=60
	mask[0:height, int(w-blur_thickness):int(w+blur_thickness),:] = 0
	
	# Make the blur.
	blurred_appended = blur_image.blur_image_locally(appended, mask, use_gaussian_blur=True, gaussian_sigma=10, uniform_filter_size=201)
	return blurred_appended
	
def panel_onto_img(panel, img):
	print(type(panel))
	height, width = panel.shape[:2]
	#height, width = get_as_image(panel).shape[:2]
	drratio = minvert / height #desired-to-real ratio
	to_append = cv2.resize(panel, (round(width * drratio), round(height * drratio)))

	if not isinstance(img, np.ndarray):
		appended = to_append
	else:
		appended = smush_together(img, to_append)

	return appended
	
	
def big_enough(img):
	height, width = img.shape[:2]
	if width > height * htvr:
		return True
	else:
		return False
	
	
def magic_background(topic_name):
	img = None
	done = False
	while not done:
	
		panel = make_panel(topic_name)
		
		img = panel_onto_img(panel, img)
		print(type(img))
		
		if big_enough(img):
			done = True
			
	imgurl = topic_name.replace(" ","_")+"_mb.jpg"
	fullimgurl = "static/"+imgurl
	cv2.imwrite(fullimgurl, img)
	return img, fullimgurl
	
	
if __name__=='__main__':
	img, imgurl = magic_background('chess')
	cv2.imshow('img', img)
	cv2.waitKey(0)
	cv2.destroyAllWindows()