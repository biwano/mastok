from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
import traceback
import logger
import hug
from model import SESSION, ApiKey
import config
import requests

def check_user_key(api_key, context):
    try:
        session = SESSION()
        api_key = session.query(ApiKey).filter_by(api_key=api_key).one()
        logger.debug("Authenticated user with key: %s" % api_key)
        user = api_key.user
        session.close()
        return user
    except MultipleResultsFound:
        traceback.print_exc()
        logger.critical("Impossible")
    except NoResultFound:
        logger.debug("Cannot authenticate user with key: %s" % api_key)
    return False


def check_admin_key(api_key):
    """Authenticate an administrator using the key in config.ini"""
    admin_user = config.getdict("authentication", "admin_user")
    if api_key == admin_user["api_key"]:
        logger.debug("Authenticated admin with key: %s" % api_key)
        return admin_user
    logger.debug("Cannot authenticate admin with key: %s" % api_key)
    return False

def check_captcha(captcha):
    """Authenticate a googlae captcha v23 token"""
    if config.get("auth", "captcha") == "bypass":
        return True
    data = {
        "secret": config.get("recaptchav3", "secret"),
        "response": captcha
        }
    response = requests.post(config.get("recaptchav3", "endpoint"), data=data)
    response = response.json()
    return response["success"]

is_authenticated = hug.authentication.api_key(check_user_key)
is_admin = hug.authentication.api_key(check_admin_key)
