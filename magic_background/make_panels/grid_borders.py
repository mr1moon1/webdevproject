'''
The Gaussian Blur part of this module is taken entirely from a Stackoverflow solution.

URL:  https://stackoverflow.com/questions/54826757/what-is-the-most-elegant-way-to-blur-parts-of-an-image-using-python

Username of person who wrote this solution: Mr.Epic Fail
(Thank you, Mr.Epic Fail!)
'''


import numpy as np
import matplotlib.pyplot as plt
from scipy import misc
import scipy.ndimage
import cv2


#==================================================================
# BORDERS TO BE BLUR:


def gaussian_blur(sharp_image, sigma):
    # Filter channels individually to avoid gray scale images
    blurred_image_r = scipy.ndimage.filters.gaussian_filter(sharp_image[:, :, 0], sigma=sigma)
    blurred_image_g = scipy.ndimage.filters.gaussian_filter(sharp_image[:, :, 1], sigma=sigma)
    blurred_image_b = scipy.ndimage.filters.gaussian_filter(sharp_image[:, :, 2], sigma=sigma)
    blurred_image = np.dstack((blurred_image_r, blurred_image_g, blurred_image_b))
    return blurred_image


def uniform_blur(sharp_image, uniform_filter_size):
    # The multidimensional filter is required to avoid gray scale images
    multidim_filter_size = (uniform_filter_size, uniform_filter_size, 1)
    blurred_image = scipy.ndimage.filters.uniform_filter(sharp_image, size=multidim_filter_size)
    return blurred_image


def blur_image_locally(sharp_image, mask, use_gaussian_blur, gaussian_sigma, uniform_filter_size):

    one_values_f32 = np.full(sharp_image.shape, fill_value=1.0, dtype=np.float32)
    sharp_image_f32 = sharp_image.astype(dtype=np.float32)
    sharp_mask_f32 = mask.astype(dtype=np.float32)

    if use_gaussian_blur:
        blurred_image_f32 = gaussian_blur(sharp_image_f32, sigma=gaussian_sigma)
        blurred_mask_f32 = gaussian_blur(sharp_mask_f32, sigma=gaussian_sigma)

    else:
        blurred_image_f32 = uniform_blur(sharp_image_f32, uniform_filter_size)
        blurred_mask_f32 = uniform_blur(sharp_mask_f32, uniform_filter_size)

    blurred_mask_inverted_f32 = one_values_f32 - blurred_mask_f32
    weighted_sharp_image = np.multiply(sharp_image_f32, blurred_mask_f32)
    weighted_blurred_image = np.multiply(blurred_image_f32, blurred_mask_inverted_f32)
    locally_blurred_image_f32 = weighted_sharp_image + weighted_blurred_image

    locally_blurred_image = locally_blurred_image_f32.astype(dtype=np.uint8)

    return locally_blurred_image
	
	
#A function to blur the borders within a collage.
def blur_borders(image, square_length=200, blur_thickness=None):
	print("Doing blur_borders.")

	#Before anything, clarify what the blur_thickness is, by default:
	if blur_thickness==None:
		blur_thickness = square_length // 5

	height, width, channels = image.shape
	mask = np.full((height, width, channels), fill_value=1)
	
	#First, get the borders:
	mask[0:blur_thickness, 0:width, :] = 0
	mask[height-blur_thickness:height, 0:width, :] = 0
	mask[0:height, 0:blur_thickness, :] = 0
	mask[0:height, width-blur_thickness:width, :]=0
	
	#Make the horizontal lines.
	h = square_length
	while h < height - blur_thickness:
		mask[int(h-blur_thickness):int(h+blur_thickness), 0:width, :] = 0
		h += square_length
	
	#Make the vertical lines.
	w = square_length
	while w < width - blur_thickness:
		mask[0:height, int(w-blur_thickness):int(w+blur_thickness), :] = 0
		w += square_length
	
	#Make the blurs.
	result = blur_image_locally(
        image,
        mask,
        use_gaussian_blur=True,
        gaussian_sigma=10,
        uniform_filter_size=201)
	return result
	
	
#One-swoop function to blur an image:
def draw_blurs(image, square_length=200, blur_thickness=None):
	return blur_borders(image, square_length, blur_thickness)
	
	
#============================================================
# BORDERS TO BE LINES:


def line_borders(image, square_length=200, color=(0,0,0), line_thickness=None): #(Note: color of the lines will be black by default.)
	height, width, channels = image.shape
	
	#When drawing the lines, this'll make them longer than necessary, just to be on the safe side...
	overshoot_distance = square_length
	longheight = height + overshoot_distance
	longwidth = width + overshoot_distance
	
	#To clarify what the line_thickness is, by default:
	if line_thickness==None:
		line_thickness = square_length // 5
	
	#Draw all the lines along both axes:
	x=0
	while x <= longwidth:
		start_point = (0,x)
		end_point = (longheight,x)
		cv2.line(image, start_point, end_point, color, line_thickness)
		x += square_length
	y=0
	while y <= longheight:
		start_point = (y,0)
		end_point = (y,longwidth)
		cv2.line(image, start_point, end_point, color, line_thickness)
		y += square_length
	
	return image
	

def draw_lines(image, square_length=200, line_thickness=None):
	return line_borders(image, square_length, line_thickness)
	
	
#===============================================
# (main())


def grid_borders(image, square_length=200, thickness=None, blur=True): #blur==True: use blur. blur==False: use line.
	print("Doing grid_borders.")
	if blur:
		print("Blur requested.")
		return draw_blurs(image, square_length, thickness)
	else:
		print("Lines requested.")
		return draw_lines(image, square_length, thickness)
	
if __name__=='__main__':
	image = cv2.imread('collage.jpg')
	blurred_image = blur_borders(image)
	cv2.imshow("SKF", blurred_image)
	cv2.waitKey(0)
	cv2.destroyAllWindows()