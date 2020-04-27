""" part of the API managing locations """
import falcon
import uuid
import hug
from sqlalchemy.orm.exc import NoResultFound
from model import Session, Location, Item, queries
from . import helpers


@hug.extend_api()
def shared():
    """ Adds common directives """
    return [helpers.extend]

@hug.post('', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def create_item(session: helpers.extend.session, user: hug.directives.user, response, location_id, reference_id, quantity):
    """Creates a location"""
    try:
        location = queries.user_location(session, user, location_id)
        print(location)
        reference = queries.user_reference(session, user, reference_id)
        print(reference)
        if location.warehouse.id != reference.warehouse.id:
        	return helpers.response.error("bad_location_and_or_reference", falcon.HTTP_400)
        item = Item(location=location, reference=reference, quantity=quantity)
        return item
    except NoResultFound:
        return helpers.response.error("location_and_or_reference_not_found", falcon.HTTP_401)
    

