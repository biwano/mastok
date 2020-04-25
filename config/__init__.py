import configparser
import pathlib
import json


def dictparser(string):
	return json.loads(string)
	
parent = pathlib.Path(__file__).parent
config = configparser.ConfigParser(converters={
  "dict": dictparser
})
config.read_file(open(parent / "config.ini"))
