""" part of the API managing users """
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
import hug
from model import User
from . import helpers


@hug.extend_api()
def shared():
    """ Adds common directives """
    return [helpers.extend]

@hug.post('/')
@helpers.wraps
def create_account(session: helpers.extend.session, mail):
    """Creates an account"""
    try:
        session.query(User).filter(User.mail == mail).one()
        return helpers.response.error("user_exists")
    except MultipleResultsFound:
        return helpers.response.error("impossible")
    except NoResultFound:
        user = User(mail=mail, api_key=helpers.make_key())
        session.add(user)
        return user

@hug.delete('/{id}', requires=helpers.authentication.is_admin)
@helpers.wraps
def delete_account(session: helpers.extend.session, id: int):
    """Deletes an account"""
    user = session.query(User).get(id)
    if user is not None:
        session.delete(user)
        return helpers.response.ok("user_deleted")
    return helpers.response.error("user_not_found")

@hug.get('/', requires=helpers.authentication.is_admin)
@helpers.wraps
def list_accounts(session: helpers.extend.session):
    """ Lists all accounts """
    users = session.query(User).all()
    return users
