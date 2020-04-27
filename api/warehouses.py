""" part of the API managing warehouses """
import falcon
import hug
from sqlalchemy.orm.exc import NoResultFound
from model import Warehouse, Warehouse_ACE, Location, queries
from . import helpers


@hug.extend_api()
def shared():
    """ Adds common directives """
    return [helpers.extend]

@hug.post('/', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def create_warehouse(session: helpers.extend.session, user: hug.directives.user, name):
    """Creates a warehouse"""
    warehouse = Warehouse(name=name)
    ace = Warehouse_ACE(warehouse=warehouse, user=user, role=helpers.roles.owner)
    session.add(ace)
    return warehouse


@hug.get('/{id}', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def get_warehouse(session: helpers.extend.session, user: hug.directives.user, response, id: int):
    """Deletes a location"""
    try:
        warehouse = queries.user_warehouse(session, user, id)
        return warehouse
    except NoResultFound:
        return helpers.response.error("warehouse_not_found", falcon.HTTP_401)  

@hug.put('/{id}', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def update_warehouse(session: helpers.extend.session, user: hug.directives.user, response, id: int, name):
    """Deletes a location"""
    try:
        warehouse = queries.user_warehouse(session, user, id)
        warehouse.name = name
        return warehouse
    except NoResultFound:
        return helpers.response.error("warehouse_not_found", falcon.HTTP_401)  

@hug.delete('/{id}', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def delete_warehouse(session: helpers.extend.session, user: hug.directives.user, response, id: int):
    """Deletes a warehouse"""
    try:
        warehouse = queries.user_warehouse(session, user, id)
        session.delete(warehouse)
        return helpers.response.ok("warehouse_deleted")
    except NoResultFound:
        return helpers.response.error("warehouse_not_found", falcon.HTTP_401)

@hug.get('/', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def list_warehouses(session: helpers.extend.session, user: hug.directives.user, response):
    """ Lists user warehouses """
    warehouses = queries.user_warehouses(session, user).all()
    return warehouses
