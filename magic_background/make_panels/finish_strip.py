'''
Finish making the background images for a page.

Goal: two sidepanels.
'''

import math
import cv2
import numpy as np
import random
import math
from scipy import ndimage
from .rotate_image import *

phi = (1 + math.sqrt(5)) / 2
'''
^
The golden ratio ;)
There's no real need to use this number,
it's just to maybe sprinkle a bit of
magical Euclid-esque aesthetic onto this project. :)
'''

#Don't want to rotate past the angle of the hypotenuse --
# the program doesn't work beyond that angle,
# and it's not really worth fixing that bug, for the purposes
# of this project.
def max_angle_to_rotate(original_image):
	height = original_image.shape[0] #in this case, adjacent
	width = original_image.shape[1] #in this case, opposite
	hyp_angle = math.degrees(math.atan(width / height))
	return hyp_angle / phi #rest in abstraction, Euclid, #-b.c. to #-b.c..
def random_angle(original_image):
	max_angle = max_angle_to_rotate(original_image)
	return random.uniform(-max_angle, max_angle)

#Get bounds to crop
def get_horizontal_crop_thickness(angle, original_image, rotated_image):
	original_height = original_image.shape[0]
	new_height = rotated_image.shape[0]
	new_width = rotated_image.shape[1]
	thickness = int(math.sin(math.radians(angle)) * original_height) #Some simple trig
	return abs(thickness)
	
#def get_vertical_crop_thickness(angle, desired_width):
#	return int(math.tan(math.radians(angle)) * desired_width) #More simple trig
	
def horizontally_crop_image(angle, original_image, rotated_image):
	to_crop = get_horizontal_crop_thickness(angle, original_image, rotated_image)
	height = rotated_image.shape[0]
	width = rotated_image.shape[1]
	return rotated_image[0:height, to_crop:width-to_crop]
	
#=============================================================

#Returns the horizontal placement of a random start point for a new sliver.
def random_sliver_start(cropped_image, desired_width):
	width = cropped_image.shape[1]
	return math.randint(0, width-desired_width)

#Once I know how far right to start, I want to know how far down to crop.
def vertical_crop_distance(cropped_image, theta, x=None):
	if x==None:
		x = width = cropped_image.shape[1] #Readability quirk
	return int(x * math.tan(math.radians(abs(theta)))) #---previous bug: Didn't realize abs(theta) was needed instead of just theta, because, for example, -10deg should be treated the same as +10deg.
	
#The original goal was to allow cropping at a desired width, but cutting corners here (in a literal sense; cool) to just crop it down in a more slap-dash way than originally planned.
#	(Original plan may have been the result of overthinking, anyway... The point of this kind of collage is to feel exactly slapdash.)
def simple_crop_vertically(angle, horizontally_cropped_image):
	height = horizontally_cropped_image.shape[0]
	width = horizontally_cropped_image.shape[1]
	to_crop = vertical_crop_distance(horizontally_cropped_image, angle)
	return horizontally_cropped_image[to_crop:height-to_crop, 0:width]
	
#============================================================

def tilt_image(image):
	print("Doing tilt_image.")
	angle = random_angle(image)
	print(angle)
	rotated_image = ndimage.rotate(image, angle)
	#cv2.imshow("rotated_image in tilt_image",rotated_image)
	horizontally_cropped_image = horizontally_crop_image(angle, image, rotated_image)
	#cv2.imshow("horizontally_cropped_image in tilt_image",horizontally_cropped_image)
	vertically_cropped_image = simple_crop_vertically(angle, horizontally_cropped_image)
	#cv2.imshow("vertically_cropped_image in tilt_image",vertically_cropped_image)
	
	#if vertically_cropped_image.shape[0] < vertically_cropped_image.shape[1]: #fat image
	#	return tilt_image(image) #try again.
	return vertically_cropped_image
	
def slice_image(image):
	#Not going to worry about implementing this method just yet.
	return image
	
def finish_strip(image, desired_width=None):
	print("Doing finish_strip.")
	tilted_image = tilt_image(image)
	sliced_image = slice_image(tilted_image) #---previous bug: accidentally did slice_image(image) before, was wondering why this kept on returning the original collage... Lesson learned: make sure code isn't dumb
	return sliced_image
	
#----------------------------------------------------------------
	
def main():
	image = cv2.imread("bee_movie_but_collage.jpg")
	angle = random_angle(image)
	rotated_image = ndimage.rotate(image, angle)
	cropped_image = horizontally_crop_image(angle, image, rotated_image)
	cropped_image = simple_crop_vertically(angle, cropped_image)
	cv2.imshow("image!", cropped_image)
	cv2.waitKey(0)
	cv2.destroyAllWindows()
	cv2.imwrite("cropped_image.jpg", cropped_image)
	
if __name__=="__main__":
	main()