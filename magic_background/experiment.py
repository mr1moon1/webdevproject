
import cv2
'''
from blur_image import *
from collage import *
from image_search import *
from make_background import *
from rotate_image import *
'''

import os
import sys #Take the command line argument.
import argparse
from make_panels import *
d = 5

#All-in-one function to do the thing I want.
def make_panel(topic, square_size=100, num_columns=d, borders=False, blur=False):
	if not directory_exists(topic):
		print("Directory for '"+topic+"' does not exist.")
		image_search(topic)
	pinboard = collage(topic, square_size=square_size, num_columns=num_columns, borders=borders, blur=blur)
	background = finish_strip(pinboard)
	return background
	
#Quick function to help process the command line arguments as a phrase.
def take_args():
	args = sys.argv #Take the arguments.
	args = args[1:] #Remove the current filename from the arguments.
	topic = ""
	for arg in args:
		topic += arg+" " #Join the words to be a phrase.
	if len(topic)>0:
		topic = topic[:-1] #Remove that last space.
	return topic

#-------------------------------------------------------------------------
	
#A main function.
if __name__=="__main__":
	#topic = take_args() #Take the command line argument as one whole phrase that can have spaces in it.
	
	parser = argparse.ArgumentParser()
	parser.add_argument('-topic','-t','--topic',metavar='topic',required=True,help='the topic to make a collage for')
	parser.add_argument('-square_size','-s','--square_size',metavar='square_size',required=False,help='the size each square will have in the collage')
	parser.add_argument('-num_columns','-nc','--num_columns',metavar='num_columns',required=False,help='the number of columns the collage should have (before tilting & cropping)')
	parser.add_argument('-borders','-bd','--borders',metavar='borders',required=False,help='whether or not the collage should be marked with borders along the grid')
	parser.add_argument('-blur','-bl','--blur',metavar='blur',required=False,help='whether or not the borders along the collage\'s grid should be blur; thick lines otherwise.')
	args = parser.parse_args()
	
	#Simplify referencing the arguments.
	topic = args.topic
	square_size = args.square_size
	num_columns = args.num_columns
	borders = args.borders
	blur = args.blur
	
	print(borders)
	
	#Set defaults.
	if not square_size: square_size=100
	else: square_size = int(square_size)
	if not num_columns: num_columns=5
	else: num_columns = int(num_columns)
	if blur==None: #Currently there's a bug somewhere here, but it's unclear yet how to fix it
		blur=True
	if borders==None or blur==True:
		borders==True
		
	print(borders)
	
	panel = make_panel(topic=topic, square_size=square_size, num_columns=num_columns, borders=borders, blur=blur)
	
	cv2.imshow(topic, panel)
	cv2.waitKey(0)
	cv2.destroyAllWindows()
	cv2.imwrite("panels/"+topic.replace(" ","_")+"_panel.jpg", panel)