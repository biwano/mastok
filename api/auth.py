""" part of the API managing users """
import falcon
import hug
import smtplib
import re
import random
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from model import User, ApiKey
from . import helpers
import config

def user_with_key(user, api_key):
    res = user.to_dict()
    res["api_key"] = api_key.api_key
    return res

def set_user_passcode(session, mail):
    digits = map(lambda number: str(round(random.random()*9)), range(8))
    passcode = "".join(digits)
    helpers.update("user", session, session.query(User).filter(User.mail == mail), {"passcode": passcode})
    return passcode


@hug.post('/{mail}/login')
@helpers.wraps
def auth_by_mail(session: helpers.extend.session, response, mail, passcode=None, api_key=None):
    """Authenticates a user by email and passcode"""
    try:
        query = session.query(User).filter(User.mail == mail)
        requested_user = query.one()
        new_key = ApiKey(user=requested_user, api_key=helpers.make_key())
        # Standard api_key authorization
        if api_key:
            if api_key in requested_user.api_keys:
                return user_with_key(requested_user, api_key)
            return helpers.response.error("API key authentication_failed", falcon.HTTP_401)
        # Passcode verification
        elif passcode: 
            if requested_user.passcode == passcode:
                # Consume passcode
                requested_user.passcode = None
                # Mail already verified append key
                if requested_user.is_mail_verified:
                    requested_user.api_keys.append(new_key)
                # Else mark mail as verified and reset keys
                else:
                    requested_user.is_mail_verified = True
                    requested_user.api_keys = [new_key]
                session.add(requested_user)
                return user_with_key(requested_user, new_key)
            return helpers.response.error("Passcode authentication_failed", falcon.HTTP_401)
        # Exploration account
        elif not requested_user.is_mail_verified:
            # Ensure there is a key
            if not requested_user.api_keys:
                requested_user.api_keys.append(new_key)
                session.add(requested_user)
            return user_with_key(requested_user, new_key)
        # Everything failed
        return helpers.response.error("Auhentication required", falcon.HTTP_401)
        
    except NoResultFound:
        return helpers.response.error("user_not_found", falcon.HTTP_400)

@hug.post('/{mail}/send_passcode')
@helpers.wraps
def send_passcode(session: helpers.extend.session, response, mail, test=False):
    """Send a verification mail """
    passcode = set_user_passcode(session, mail)
    helpers.mail.from_template(mail, "verify_mail", body_params={"passcode": passcode}, test=test)
    return helpers.response.ok("mail_sent")
    
@hug.post('/{mail}/set_passcode', requires=helpers.authentication.is_admin)
@helpers.wraps
def set_passcode(session: helpers.extend.session, response, mail, test=False):
    """Sets the passcode of a user - same as send_passcode but returns the passcode in the response instead of sending a mail for testing purpose  - """
    passcode = set_user_passcode(session, mail)
    return {"passcode": passcode}
    
