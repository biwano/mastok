# filename: happy_birthday.py
"""A basic (single function) API written using hug"""
import api
import hug


@hug.extend_api('')
def something_api():
    return [api]