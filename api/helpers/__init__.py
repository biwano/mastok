from model import SESSION
import traceback
import hug
import inspect
import uuid
import logging
from config import config
from . import extend
from . import authentication
from . import response

def wraps(func):
    @hug.decorators.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            if "hug_session" in kwargs:
                session = kwargs["hug_session"]
            else:
                session = SESSION()
            if "session" in inspect.getargspec(func):
                kwargs["session"] = session
            res = func(*args, **kwargs)
            print(session.new)
            session.commit()
        except Exception as e:
            traceback.print_exc()
            logging.critical("Unhandled error caught by wrapper")
            session.rollback()
            res = {"error": repr(e)}
        finally:
            session.close()
        return res
        
    return wrapper


def make_key():
    return uuid.uuid1().hex

