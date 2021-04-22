'''
Point of this file: turn some images into a collage.

Helped by this URL: https://www.includehelp.com/python/create-a-collage-of-images-with-the-help-of-numpy-and-python-opencv-cv2.aspx
'''

#Import everything.
import cv2
import numpy as np
import glob
import random
import os
from .image_search import *
from .rotate_image import *
from .grid_borders import *
d = 7 #This'll be the standard number of columns.
default_square_size = 100 #This'll be the standard square size.
	
	
#All-in-one swoop function to rotate, crop, and then square an image.
def rotate_crop_square_image(image):
	return make_image_square(rotate_image(image))
	

#A helper function to make sure there's only an even number of items.
def find_nearest_divisible_number(n, divisor=d):
	if n % divisor == 0:
		return n
	elif n >= 0:
		return find_nearest_divisible_number(n-1, divisor)
	else:
		return None

		
#A helper function to evenly partition a list, and properly stack.
#taken from URL: https://itqna.net/questions/10814/divide-list-n-sublists
def chunks(items, num_partitions):
	desired_length_of_each_chunk = len(items) // num_partitions
	for i in range(0, len(items), desired_length_of_each_chunk):
		yield(np.vstack(items[i:i + desired_length_of_each_chunk]))
def partition(items, num_partitions=d):
	return(list(chunks(items, num_partitions)))
	

#A helper function to retrieve images, from a folder or from online.
def retrieve_images(topic_name, num_images=50):

	#First, make sure it's searchable as a directory name.
	searchable_topic_name = topic_name.replace(" ", "_")
	path_name = 'simple_images/'+searchable_topic_name+'/*'
	
	#If the directory doesn't exist locally, go retrieve them from online.
	if not glob.glob(path_name):
		try:
			image_search(topic_name, limit=num_images)
		except:
			print("Error in collage.py:")
			print(" Directory for "+searchable_topic_name+" not found,")
			print(" and, for some reason, this program was ")
			print(" unable to do an online image search. ")

	#Read each image.
	#helped by URL: https://stackoverflow.com/questions/37747021/create-numpy-array-of-images
	images = []
	files = glob.glob(path_name)
	
	#If the calling has specified a number of images to work with, use only that number.
	if num_images==None:
		files = files
	elif num_images > len(files): #Don't want to request more images than there actually are.
		files = files
		num_images = len(files)
	else:
		files = files[:num_images]
	
	return files
	
#Make a collage of images.
def make_collage(topic_name, num_columns, rotate=True, num_images=None, borders=True, blur=True, s=default_square_size, thin=True):
	#The thin value got abandoned and it isn't worth the effort to delete it, but the idea of it was to ensure that the number of columns would be less than the number of rows, so that the collage would end up thin, so that it's able to get tilted later on.
	#(It would work in the following way: Check if num_columns < sqrt(num_images): if so, do nothing; else, reduce num_columns by 1 and try again.)
	
	#borders=False: no borders
	#borders=True, blur=True: borders that are blur
	#borders=True, blur=False: borders that are lines
		
	#Get the images.
	files = retrieve_images(topic_name, num_images)
	
	#Go through each image, process it, and put it in the list of images.
	images = []
	for file in files:
	
		image = cv2.imread(file)

		if not image is None:
		
			#Rotate the image, especially if the calling of the function requests it.
			if rotate:
				image = rotate_image(image)
			else:
				image = make_image_square(image)
		
			#Make all of the images the same size.
			image = cv2.resize(image,(s,s))
			
			#Append it to the list of images.
			#(I merged what could have been multiple for-loops, for efficiency's sake.)
			images.append(image)
			
	#It'd be nice to have the collage be randomly-ordered images.
	random.shuffle(images)
	
	#Make sure we're only dealing with a properly divisible number of images.
	images = images[:find_nearest_divisible_number(len(images), divisor=num_columns)]
		
	#Now we will stack some images.	
	longways = partition(images, num_columns)
	shortway_attachment = np.hstack(longways)
	
	#Finally, add grid borders if and as requested.
	if borders:
		print("Borders requested.")
		return grid_borders(shortway_attachment, s, s//5, blur)
	print("Borders NOT requested.")
	
	#Return the final attachment.
	return shortway_attachment
	

#One-swoop function to do the thing.
#(I sequester the work to a separate function, largely so it can appear sleek here.)
def collage(topic_name, num_columns, rotate=True, num_images=None, borders=True, blur=True, square_size=default_square_size, thin=True):
	collage = make_collage(topic_name, num_columns, rotate, num_images, borders, blur, square_size, thin)
	cv2.imwrite("collages/"+topic_name.replace(" ","_")+"_collage.jpg", collage)
	return collage
	
#An experiment of the method.
if __name__=='__main__':

	#Do the functions.
	phrase = 'bee movie but'
	collage = collage(phrase, square_size=100)
	
	#Show the final collage.
	cv2.imshow("Final Collage", collage)
	cv2.waitKey(0)
	cv2.destroyAllWindows()
	cv2.imwrite(phrase.replace(" ","_")+"_collage.jpg", collage)