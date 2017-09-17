import os
import sys
import json
import math
from PIL import Image, ImageDraw, ImageFont


# Relative path to a folder containing any non-python files.
DATA_FOLDER = "data"

# Files with extensions from this list will be processed
VALID_EXTENSIONS = [".jpg"]


def path():
	"""Returns full path to this package"""
	
	try:
		root = __file__
		if os.path.islink(root):
			root = os.path.realpath(root)
		return os.path.dirname(os.path.abspath(root))
	except:
		print("I'm sorry, but something is wrong.")
		print("There is no __file__ variable. Please contact the author.")
		sys.exit ()


def pathto(filename):
	"""Returns full path to the file (<path-to-this-package>/data/filename)"""

	datafolder = os.path.join(path(), DATA_FOLDER)
	return os.path.join(datafolder, filename)


# Absolute paths to some needed files
FONT_FILE = pathto("DellaRespira.ttf")
SETTINGS_FILE = pathto("settings.json")
SETTINGS_PREVIEW_FILE = pathto("preview.jpg")


class Settings:
	"""Class holding settings for watermark functions"""
	
	def __init__(self, data):
		"""Creates settings class from a dictionary"""
		
		self._data = data
		self.__dict__.update(**data)
	
	def load(path):
		"""Returns a new Settings object, loaded from the settings file"""
		
		with open(path) as json_data_file:
			data = json.load(json_data_file)
			return Settings(data)
	
	def save(self, path):
		"""Saves settings to the settings file"""
		
		with open(path, 'w') as json_data_file:
			json.dump(self.__dict__, json_data_file)
		
		
def is_file_ext_right(path):
	"""Checks if given file has the right extension"""

	fn, ext = os.path.splitext(path)
	return os.path.isfile(path) and ext in VALID_EXTENSIONS


def listfiles(path):
	"""Iterates through all files in a directory, returns full paths."""
	
	try:
		result = []
		for fn in os.listdir(path):
			fp = os.path.join(path, fn)
			if os.path.isfile(fp):
				yield fp
	except:
		return None


def _has_action(settings):
	"""Checks if there is any watermark to add with given settings."""
	
	return 	len(settings.text) and settings.sizefactor \
			and (settings.center or settings.topleft or settings.topright \
			or settings.bottomleft or settings.bottomright)


def add_watermark(image, settings):
	"""Returns a watermarked PIL.Image."""
	
	if not _has_action(settings):
		return image
	
	image = image.convert("RGBA")
	width, height = image.size
	
	wm_image = Image.new("RGBA", image.size, (255, 255, 255, 0))
	draw = ImageDraw.Draw(wm_image)
	
	color = (255, 255, 255, settings.alpha)
	
	fontsize = int(math.sqrt(width * height) * settings.sizefactor / 100.0)
	try:
		font = ImageFont.truetype(FONT_FILE, fontsize)
	except:
		print("Error loading font {}".format(FONT_FILE))
		return False
	textwidth, textheight = draw.textsize(settings.text, font)
	
	xmargin = int(width * settings.xmargin / 100.0)
	ymargin = int(height * settings.ymargin / 100.0)
	
	left = xmargin
	right = width - textwidth - xmargin
	top = ymargin
	bottom = height - textheight - ymargin
	centerx = width // 2 - textwidth // 2
	centery = height // 2 - textheight // 2
	
	if settings.topleft:
		draw.text((left, top), settings.text, color, font)
	if settings.topright:
		draw.text((right, top), settings.text, color, font)
	if settings.bottomleft:
		draw.text((left, bottom), settings.text, color, font)
	if settings.bottomright:
		draw.text((right, bottom), settings.text, color, font)
	if settings.center:
		draw.text((centerx, centery), settings.text, color, font)
	
	image = Image.alpha_composite(image, wm_image)
	
	return image.convert("RGB")


def add_watermark_to_file(path, settings):
	"""Adds a watermark to image file and overwrites it."""
	
	if not _has_action(settings):
		return False
	print("PROCESSING", os.path.basename(path), end="")
	try:
		image = Image.open(path).convert("RGBA")
	except Exception as e:
		print("Error while loading image file '{}'\n{}".format(filename, e))
		return False
	
	image = add_watermark(image, settings)
	
	try:
		image.save(path)
	except Exception as e:
		print("Error while saving image file '{}'\n{}".format(path, e))
		return False
	
	print("...OK")
	return True

