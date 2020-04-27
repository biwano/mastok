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
def create_location(session: helpers.extend.session, user: hug.directives.user, response, warehouse_id: int, name):
    """Creates a location"""
    try:
        warehouse = queries.user_warehouse(session, user, warehouse_id)
        location = Location(warehouse=warehouse, name=name)
        return location
    except NoResultFound:
        return helpers.response.error("warehouse_not_found", falcon.HTTP_401)


@hug.get('/{id}', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def get_location(session: helpers.extend.session, user: hug.directives.user, response, id: int, name):
    """Deletes a location"""
    try:
        location = queries.user_location(session, user, id)
        return location
    except NoResultFound:
        return helpers.response.error("location_not_found", falcon.HTTP_401)  

@hug.put('/{id}', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def update_location(session: helpers.extend.session, user: hug.directives.user, response, id: int, name):
    """Deletes a location"""
    try:
        location = queries.user_location(session, user, id)
        location.name = name
        return helpers.response.ok("location_updated")
    except NoResultFound:
        return helpers.response.error("location_not_found", falcon.HTTP_401)  

@hug.delete('/{id}', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def delete_location(session: helpers.extend.session, user: hug.directives.user, response, id: int):
    """Deletes a location"""
    try:
        location = queries.user_location(session, user, id)
        session.delete(location)
        return helpers.response.ok("location_deleted")
    except NoResultFound:
        return helpers.response.error("location_not_found", falcon.HTTP_401)    

@hug.get('', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def list_locations(session: helpers.extend.session, user: hug.directives.user, response, warehouse_id: int):
    """ Lists warehouse locations """
    try:
        warehouse = queries.user_warehouse(session, user, warehouse_id)
        locations = session.query(Location).filter(warehouse=warehouse)
        return locations
    except NoResultFound:
        return helpers.response.error("warehouse_not_found", falcon.HTTP_401)
