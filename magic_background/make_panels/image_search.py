import glob
from simple_image_download import simple_image_download

#Check to see if a directory exists:
def directory_exists(topic_name):

	#First, make sure it's searchable as a directory name.
	searchable_topic_name = topic_name.replace(" ", "_")
	path_name = 'simple_images/'+searchable_topic_name+'/*'
	
	#Check if the path exists.
	if glob.glob(path_name):
		return True
	else:	
		return False

#One function to do an image search for relevant images:
def image_search(phrase, limit=50):
	print("Doing image_search")
	try:
		response = simple_image_download.simple_image_download
	except:
		print("Unable to do simple_image_download.")
	return response().download(phrase,limit)