""" part of the API managing users """
import falcon
import hug
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from model import User
from . import helpers
import re



@hug.extend_api()
def shared():
    """ Adds common directives """
    return [helpers.extend]

@hug.post('/')
@helpers.wraps
def create_user(session: helpers.extend.session, response, mail):
    """Creates an account"""
    if len(mail) == 0:
        return helpers.response.error("user_mail_empty", falcon.HTTP_400)
    if not helpers.is_mail(mail):
        return helpers.response.error("user_mail_invalid", falcon.HTTP_400)
    try:
        session.query(User).filter(User.mail == mail).one()
        return helpers.response.error("user_exists", falcon.HTTP_400)
    except NoResultFound:
        user = User(mail=mail, is_mail_verified=False, passcode=None)
        session.add(user)
        return user


@hug.delete('/{id}', requires=helpers.authentication.is_admin)
@helpers.wraps
def delete_user(session: helpers.extend.session, response, id: int):
    """Deletes an account"""
    user = session.query(User).get(id)
    if user is not None:
        session.delete(user)
        return helpers.response.ok("user_deleted")
    return helpers.response.error("user_not_found", falcon.HTTP_400)


@hug.get('/', requires=helpers.authentication.is_admin)
@helpers.wraps
def list_users(session: helpers.extend.session):
    """ Lists all accounts """
    users = session.query(User).all()
    return users

