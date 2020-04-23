import configparser
import pathlib

parent = pathlib.Path(__file__).parent
config = configparser.ConfigParser()
config.read_file(open(parent / "config.ini"))
