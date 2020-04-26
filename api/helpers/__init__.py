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
        try:
            if "session" in kwargs:
                session = kwargs["session"]
            else:
                session = SESSION()
            res = func(*args, **kwargs)
            if issubclass(type(res), BASE):
                session.add(res)
                session.commit()
                res = response.item(res)
            elif type(res) == list:
                res = response.list(res)
            session.commit()
            return res
        except Exception as exc:
            traceback.print_exc()
            logger.critical("Unhandled error caught by wrapper")
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
