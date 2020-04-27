""" part of the API managing locations """
import falcon
import uuid
import hug
from sqlalchemy.orm.exc import NoResultFound
from model import Session, Location, queries
from . import helpers


@hug.extend_api()
def shared():
    """ Adds common directives """
    return [helpers.extend]

@hug.post('', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def create_location(session: helpers.extend.session, user: hug.directives.user, response, warehouse_id, name):
    """Creates a location"""
    try:
        warehouse = queries.user_warehouse(session, user, warehouse_id)
        location = Location(warehouse=warehouse, name=name)
        return location
    except NoResultFound:
        return helpers.response.error("warehouse_not_found", falcon.HTTP_401)
    

