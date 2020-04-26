from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
import traceback
import logger
import hug
from model import SESSION, User
import config


def authenticate_user_key(api_key, context):
    try:
        session = SESSION()
        user = session.query(User).filter(User.api_key == api_key).one()
        logger.debug("Authenticated user with key: %s" % api_key)
        session.close()
        return user
    except MultipleResultsFound:
        traceback.print_exc()
        logger.critical("Impossible")
    except NoResultFound:
        logger.debug("Cannot authenticate user with key: %s" % api_key)
    return False


def authenticate_admin_key(api_key):
    """Authenticate an administrator using the key in config.ini"""
    admin_user = config.getdict("authentication", "admin_user")
    if api_key == admin_user["api_key"]:
        logger.debug("Authenticated admin with key: %s" % api_key)
        return admin_user
    logger.debug("Cannot authenticate admin with key: %s" % api_key)
    return False

is_authenticated = hug.authentication.api_key(authenticate_user_key)
is_admin = hug.authentication.api_key(authenticate_admin_key)