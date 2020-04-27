""" Provides helpers from views """
import traceback
import inspect
import uuid
import logger
import hug
import config
from model import SESSION, BASE
from . import extend
from . import authentication
from . import response


def wraps(func):
    """ Wraps a view so errors and session are handled automagically """
    @hug.decorators.wraps(func)
    def wrapper(*args, **kwargs):
        session = None
        resp = None
        try:
            if "session" in kwargs:
                session = kwargs["session"]
            if "response" in kwargs:
                resp = kwargs["response"]
            # Execute view
            res = func(*args, **kwargs)
            # Commits instance in db and serialize it
            if issubclass(type(res), BASE):
                if session is not None:
                    session.add(res)
                    session.commit()
                res = response.item(res)
            # Serialize list of objects
            elif type(res) == list:
                res = response.list(res)
            # If error sets response status
            elif "error" in res and response is not None:
                resp.status = res["status"]
            # Return response
            return res
        except Exception as exc:
            traceback.print_exc()
            logger.critical("Unhandled error caught by wrapper")
            if session is not None:
                session.rollback()
            res = {"error": repr(exc)}
        finally:
            session.close()
        return res

    return wrapper


def make_key():
    """ Creates a 64 hexadecimel key """
    return uuid.uuid1().hex


class roles():
    """ provides static fields for roles definition """
    owner = "owner"
    admin = "admin"
