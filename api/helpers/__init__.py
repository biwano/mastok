""" Provides helpers from views """
import traceback
import inspect
import uuid
import logger
import falcon
import hug
from contextlib import contextmanager
from sqlalchemy.orm.exc import NoResultFound
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

def get(model, session, query):
    try:
        obj = query.one()
        return obj
    except NoResultFound:
        return response.error("%s_not_found" % model, falcon.HTTP_401)

def delete(model, session, query):
    try:
        obj = query.one()
        session.delete(obj)
        return response.ok("%s_deleted" % model)
    except NoResultFound:
        return response.error("%s_not_found" % model, falcon.HTTP_401)

def update(model, session, query, data):
    try:
        obj = query.one()
        for key in data:
            setattr(obj, key, data[key])
        return obj
    except NoResultFound:
        return response.error("%s_not_found" % model, falcon.HTTP_401)
    
def do_in_place(model, place, place_query, func):
    try:
        place = place_query.one()
        res = func(place)
        return res
    except NoResultFound:
        return response.error("%s_not_found" % place, falcon.HTTP_401)
    
def do_in_warehouse(model, place_query, func):
    return do_in_place(model, "warehouse", place_query, func)

def do_in_location(model, place_query, func):
    return do_in_place(model, "location", place_query, func)

def make_key():
    """ Creates a 64 hexadecimel key """
    return uuid.uuid1().hex


class roles():
    """ provides static fields for roles definition """
    owner = "owner"
    admin = "admin"
