'''
Goal of this file: help with rotating an image and then cropping it to cut out the resulting black edges.

This entire file was pretty much copy-pasted wholesale from various submissions on this StackOverflow thread:
https://stackoverflow.com/questions/16702966/rotate-image-and-crop-out-black-borders
'''


import math
import cv2
import numpy as np
import random



#A helper function to randomly cut a largest square from an image.
#helped by this StackOverflow thread: https://stackoverflow.com/questions/16646183/crop-an-image-in-the-centre-using-pil
def make_image_square(image):

	#First, I get the dimensions:
	width = len(image)
	height = len(image[0])
	
	#From there, I know how big the square should be:
	square_length = min(width, height)
	
	#THIS WILL CHANGE -- just ignore this.
	width_start=0
	height_start=0
	width_end=width
	height_end=height
	
	#Then what I want is to figure out which side is changing, and act accordingly:
	if width==square_length:
	
		#Height is the thing that changes.
		random_height_start = random.randint(0,height - square_length)
		
		#This gives me new starting points.
		height_start = random_height_start
		height_end = random_height_start + square_length
		
	elif height==square_length:
	
		#Width is the thing that changes.
		random_width_start = random.randint(0, width - square_length)
		
		#This then gives me new starting points.
		width_start = random_width_start
		width_end = random_width_start + square_length
		
	else:
	
		#Probably won't ever get to this condition.
		return None
	return image[width_start:width_end, height_start:height_end]



def rotatedRectWithMaxArea(w, h, angle):
	"""
	Given a rectangle of size wxh that has been rotated by 'angle' (in
	radians), computes the width and height of the largest possible
	axis-aligned rectangle (maximal area) within the rotated rectangle.
	"""
	if w <= 0 or h <= 0:
		return 0,0

	width_is_longer = w >= h
	side_long, side_short = (w,h) if width_is_longer else (h,w)
  
	# since the solutions for angle, -angle and 180-angle are all the same,
	# if suffices to look at the first quadrant and the absolute values of sin,cos:
	sin_a, cos_a = abs(math.sin(angle)), abs(math.cos(angle))
	if side_short <= 2.*sin_a*cos_a*side_long or abs(sin_a-cos_a) < 1e-10:
		# half constrained case: two crop corners touch the longer side,
		#   the other two corners are on the mid-line parallel to the longer line
		x = 0.5*side_short
		wr,hr = (x/sin_a,x/cos_a) if width_is_longer else (x/cos_a,x/sin_a)
	else:
		# fully constrained case: crop touches all 4 sides
		cos_2a = cos_a*cos_a - sin_a*sin_a
		wr,hr = (w*cos_a - h*sin_a)/cos_2a, (h*cos_a - w*sin_a)/cos_2a

	return wr,hr


def rotate_bound(image, angle):
	# CREDIT: https://www.pyimagesearch.com/2017/01/02/rotate-images-correctly-with-opencv-and-python/
	(h, w) = image.shape[:2]
	(cX, cY) = (w // 2, h // 2)
	M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
	cos = np.abs(M[0, 0])
	sin = np.abs(M[0, 1])
	nW = int((h * sin) + (w * cos))
	nH = int((h * cos) + (w * sin))
	M[0, 2] += (nW / 2) - cX
	M[1, 2] += (nH / 2) - cY
	return cv2.warpAffine(image, M, (nW, nH))


def rotate_max_area(image, angle):
	""" image: cv2 image matrix object
		angle: in degree
	"""
	
	wr, hr = rotatedRectWithMaxArea(image.shape[1], image.shape[0],math.radians(angle))
	rotated = rotate_bound(image, angle)
	h, w, _ = rotated.shape
	y1 = h//2 - int(hr/2)
	y2 = y1 + int(hr)
	x1 = w//2 - int(wr/2)
	x2 = x1 + int(wr)
	return rotated[y1:y2, x1:x2]
	

def rotate_crop_image(image, angle):
	return rotate_max_area(image, angle)
	

#Function to do the thing, once you import an image.
def rotate_image(image, angle=None):

	#If angle is unspecified, get a new random angle.
	if angle==None:
		angle = random.randrange(-45,45)

	#Do the standard process for rotating the image.
	rotated_image = rotate_crop_image(image, angle)
	squared_image = make_image_square(rotated_image)
	return squared_image
	

if __name__=='__main__':
	from collage import *
	image = cv2.imread('image2.jpeg')
	image = rotate_image(image)
	cv2.imshow("Image!", image)
	cv2.waitKey(0)
	cv2.destroyAllWindows()