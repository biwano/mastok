from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
import traceback
import logging
import hug
from model import SESSION, User
from config import config


def authenticate_user_key(api_key):
    try:
        session = SESSION()
        user = session.get(User.api_key == api_key).one()
        logging.debug("Authenticated user with key: %s" % api_key)
        return user
    except MultipleResultsFound as e:
        traceback.print_exc()
        logging.critical("Impossible") 
    except NoResultFound as e:
        logging.debug("Cannot authenticate user with key: %s" % api_key)
    return False


def authenticate_admin_key(api_key):
    """Authenticate an administrator using the key in config.ini"""
    admin_user = config.getdict("authentication", "admin_user")
    if api_key == admin_user["api_key"]:
        logging.debug("Authenticated admin with key: %s" % api_key)
        return admin_user
    logging.debug("Cannot authenticate admin with key: %s" % api_key)
    return False

is_authenticated = hug.authentication.authenticator(authenticate_user_key)
is_admin = hug.authentication.api_key(authenticate_admin_key)