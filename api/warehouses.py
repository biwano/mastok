""" part of the API managing warehouses """
import falcon
import hug
from sqlalchemy.orm.exc import NoResultFound
from model import Warehouse, WarehouseACE, Location, queries
from . import helpers


@hug.extend_api()
def shared():
    """ Adds common directives """
    return [helpers.extend]

@hug.post('/', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def create_warehouse(session: helpers.extend.session, user: hug.directives.user, name):
    """Creates a warehouse"""
    helpers.sleep(5)
    warehouse = Warehouse(name=name)
    ace = WarehouseACE(warehouse=warehouse, user=user, role=helpers.roles.owner)
    session.add(ace)
    return warehouse


@hug.get('/{id}', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def get_warehouse(session: helpers.extend.session, user: hug.directives.user, response, id: int):
    """Gets a warehouse"""
    return helpers.get("warehouse", session, queries.user_warehouse(session, user, id))

@hug.put('/{id}', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def update_warehouse(session: helpers.extend.session, user: hug.directives.user, response, id: int, name):
    """Updates a warehouse"""
    return helpers.update("warehouse", session, queries.user_warehouse(session, user, id), {"name": name})


@hug.delete('/{id}', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def delete_warehouse(session: helpers.extend.session, user: hug.directives.user, response, id: int):
    """Deletes a warehouse"""
    return helpers.delete("warehouse", session, queries.user_warehouse(session, user, id))

@hug.get('/', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def list_warehouses(session: helpers.extend.session, user: hug.directives.user, response):
    """ Lists user warehouses """
    return queries.user_warehouses(session, user).all()
