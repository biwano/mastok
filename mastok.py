# filename: happy_birthday.py
"""A basic (single function) API written using hug"""
import api
import hug
from hug_middleware_cors import CORSMiddleware

mastok_api = hug.API(__name__)
mastok_api.http.add_middleware(hug.middleware.CORSMiddleware(mastok_api, allow_origins=["*"]))

@hug.extend_api('')
def something_api():
    return [api]