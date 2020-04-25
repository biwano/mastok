""" part of the API managing accounts """
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
def create_account(hug_session, mail):
    """Creates an account"""
    try:
        hug_session.query(User).filter(User.mail == mail).one()
        return helpers.response.error("account_exists")
    except MultipleResultsFound:
        return helpers.response.error("impossible")
    except NoResultFound:
        user = User(mail=mail, api_key=helpers.make_key())
        hug_session.add(user)
        return helpers.response.item(user)

@hug.get('/', requires=helpers.authentication.is_admin)
@helpers.wraps
def list_accounts(hug_session):
    """ Lists all accounts """
    users = hug_session.query(User).all()
    return helpers.response.list(users)
