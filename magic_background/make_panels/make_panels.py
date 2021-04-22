from .image_search import *
from .collage import *
#from .background import *
from .finish_strip import *

def make_strip(topic, desired_width=None):
	if not directory_exists(topic):
		image_search(topic)
	collage = collage(topic)
	strip = finish_strip(collage)
	return strip
	
def make_panels(topic):
	strip = make_strip(topic)
	return strip #Will just do this for now.