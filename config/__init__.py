import configparser
import pathlib
import json
import os

config_file_name = os.environ.get("MASTOK_CONFIG_FILE")
if config_file_name is None:
	config_file_name = "config.ini"

def dictparser(string):
	return json.loads(string)

PARENT = pathlib.Path(__file__).parent
CONFIG = configparser.ConfigParser(converters={
  "dict": dictparser
})
CONFIG.read_file(open(PARENT / config_file_name))

def get(*args, **xargs):
	return CONFIG.get(*args, **xargs)

def getdict(*args, **xargs):
	return CONFIG.getdict(*args, **xargs)

def getboolean(*args, **xargs):
	return CONFIG.getboolean(*args, **xargs)