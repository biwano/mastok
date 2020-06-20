""" part of the API managing locations """
import falcon
import uuid
import hug
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import exc
from model import Session, Location, Item, queries
from . import helpers
from marshmallow import fields

@hug.extend_api()
def shared():
    """ Adds common directives """
    return [helpers.extend]

@hug.post('', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def create_item(session: helpers.extend.session, user: hug.directives.user, response, warehouse_id: int, location_id: int, reference_id: int, quantity: int, expiry: fields.Date(allow_none=True)=None):
    """Creates a location"""
    try:
        warehouse = queries.user_warehouse(session, user, warehouse_id).one()
        location = queries.user_location(session, user, location_id).one()
        reference = queries.user_reference(session, user, reference_id).one()
        if warehouse.id != location.warehouse.id or warehouse.id != reference.warehouse.id:
            return helpers.response.error("bad_location_and_or_reference", falcon.HTTP_400)
        item = Item(warehouse=warehouse, location=location, reference=reference, quantity=quantity, expiry=expiry)
        return item
    except NoResultFound:
        return helpers.response.error("warehouse_location_or_reference_not_found", falcon.HTTP_401)

@hug.get('/{id}', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def get_item(session: helpers.extend.session, user: hug.directives.user, response, id: int=None):
    """Gets a item"""
    return helpers.get("item", session, queries.user_item(session, user, id))


@hug.put('/{id}', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def update_item(session: helpers.extend.session, user: hug.directives.user, response, id: int, location_id: int, quantity: int, expiry: fields.Date(allow_none=True)=None):
    """Updates a item"""
    def update(item):
        if location_id:
            location = queries.user_location(session, user, location_id).one()
            if location.warehouse_id != item.warehouse_id:
                raise Exception("Incoherent request")
        return {"location_id": location_id, "quantity": quantity, "expiry": expiry}
    try:
        return helpers.update("item", session, queries.user_item(session, user, id), update)
    except Exception:
        return helpers.response.error("incoherent request", falcon.HTTP_404)    

@hug.delete('/{id}', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def delete_item(session: helpers.extend.session, user: hug.directives.user, response, id: int):
    """Deletes a item"""
    return helpers.delete("item", session, queries.user_item(session, user, id))

@hug.get('', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def list_items(session: helpers.extend.session, user: hug.directives.user, response, warehouse_id: int=None, location_id: int=None):
    """ Lists warehouse locations """
    if location_id is not None:
        """ Lists location items """
        return helpers.do_in_location("item",
            queries.user_location(session, user, location_id),
            lambda location: session.query(Item).filter_by(location=location).all())
    elif warehouse_id is not None:
        """ Lists location items """
        return helpers.do_in_warehouse("item",
            queries.user_warehouse(session, user, warehouse_id),
            lambda warehouse: session.query(Item).filter_by(warehouse=warehouse).all())
    else:
        return response.error("incoherent_request", falcon.HTTP_400)
