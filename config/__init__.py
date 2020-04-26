import configparser
import pathlib
import json


def dictparser(string):
	return json.loads(string)

PARENT = pathlib.Path(__file__).parent
CONFIG = configparser.ConfigParser(converters={
  "dict": dictparser
})
CONFIG.read_file(open(PARENT / "config.ini"))

def get(*args, **xargs):
	return CONFIG.get(*args, **xargs)

def getdict(*args, **xargs):
	return CONFIG.getdict(*args, **xargs)