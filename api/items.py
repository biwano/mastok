""" part of the API managing locations """
import falcon
import uuid
import hug
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import exc
from model import Session, Location, Item, queries
from . import helpers


@hug.extend_api()
def shared():
    """ Adds common directives """
    return [helpers.extend]

@hug.post('', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def create_item(session: helpers.extend.session, user: hug.directives.user, response, location_id: int, reference_id: int, quantity: int):
    """Creates a location"""
    try:
        queries.user_item(session, user, location_id, reference_id).one()
        return helpers.response.error("item_exists", falcon.HTTP_400)
    except:
        try:
            location = queries.user_location(session, user, location_id).one()
            reference = queries.user_reference(session, user, reference_id).one()
            if location.warehouse.id != reference.warehouse.id:
                return helpers.response.error("bad_location_and_or_reference", falcon.HTTP_400)
            item = Item(location=location, reference=reference, quantity=quantity)
            return item
        except NoResultFound:
            return helpers.response.error("location_and_or_reference_not_found", falcon.HTTP_401)
    
@hug.get('', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def get_reference(session: helpers.extend.session, user: hug.directives.user, response, location_id: int, reference_id: int=None):
    """Gets a item"""
    if reference_id is not None:
         return helpers.get("reference", session, queries.user_item(session, user, location_id, reference_id))
    else:
        """ Lists warehouse items """
        return helpers.do_in_location("item",
            queries.user_location(session, user, location_id),
            lambda location: session.query(Item).filter_by(location=location).all())


@hug.put('', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def update_item(session: helpers.extend.session, user: hug.directives.user, response, location_id: int, reference_id: int, quantity: int):
    """Updates a item"""
    return helpers.update("item", session, queries.user_item(session, user, location_id, reference_id), {"quantity": quantity})

@hug.delete('', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def delete_item(session: helpers.extend.session, user: hug.directives.user, response, location_id: int, reference_id: int):
    """Deletes a item"""
    return helpers.delete("item", session, queries.user_item(session, user, location_id, reference_id))

