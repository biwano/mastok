""" part of the API managing locations """
import hug
from model import Location, queries
from . import helpers


@hug.extend_api()
def shared():
    """ Adds common directives """
    return [helpers.extend]

@hug.post('', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def create_location(session: helpers.extend.session, user: hug.directives.user, response, warehouse_id: int, name):
    """Creates a location"""
    return helpers.do_in_warehouse("location",
    	queries.user_warehouse(session, user, warehouse_id),
    	lambda warehouse: Location(warehouse=warehouse, name=name))

@hug.get('/{id}', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def get_location(session: helpers.extend.session, user: hug.directives.user, response, id: int):
    """Gets a location"""
    return helpers.get("location", session, queries.user_location(session, user, id))

@hug.put('/{id}', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def update_location(session: helpers.extend.session, user: hug.directives.user, response, id: int, name):
    """Updates a location"""
    return helpers.update("location", session, queries.user_location(session, user, id), {"name": name})

@hug.delete('/{id}', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def delete_location(session: helpers.extend.session, user: hug.directives.user, response, id: int):
    """Deletes a location"""
    return helpers.delete("location", session, queries.user_location(session, user, id))

@hug.get('', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def list_locations(session: helpers.extend.session, user: hug.directives.user, response, warehouse_id: int):
    """ Lists warehouse locations """
    return helpers.do_in_warehouse("location",
    	queries.user_warehouse(session, user, warehouse_id),
    	lambda warehouse: session.query(Location).filter(warehouse=warehouse))
