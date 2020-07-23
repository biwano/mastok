""" Logger facility """
import logging
import config

LOGGER = logging.getLogger('mastok')
LEVEL = getattr(logging, config.get("logging", "level"))
LOGGER.setLevel(LEVEL)

def debug(*args, **kwargs):
	LOGGER.debug(*args, **kwargs)

def info(*args, **kwargs):
	LOGGER.info(*args, **kwargs)

def warning(*args, **kwargs):
	LOGGER.warning(*args, **kwargs)

def error(*args, **kwargs):
	LOGGER.error(*args, **kwargs)

def critical(*args, **kwargs):
	LOGGER.critical(*args, **kwargs)
