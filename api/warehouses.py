""" part of the API managing warehouses """
import falcon
import hug
from sqlalchemy.orm.exc import NoResultFound
from model import Warehouse, WarehouseACE, Location, queries, roles
from . import helpers
import json

@hug.extend_api()
def shared():
    """ Adds common directives """
    return [helpers.extend]

@hug.post('/', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def create_warehouse(session: helpers.extend.session, user: hug.directives.user, name):
    """Creates a warehouse"""
    warehouse = Warehouse(name=name)
    ace = WarehouseACE(warehouse=warehouse, user=user, role=roles.owner)
    session.add(ace)
    return warehouse


@hug.get('/{id}', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def get_warehouse(session: helpers.extend.session, user: hug.directives.user, response, id: int):
    """Gets a warehouse"""
    return helpers.get("warehouse", session, queries.with_viewer_role(queries.user_warehouse(session, user, id)))

@hug.put('/{id}', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def update_warehouse(session: helpers.extend.session, user: hug.directives.user, response, id: int, name):
    """Updates a warehouse"""
    return helpers.update("warehouse", session, queries.with_editor_role(queries.user_warehouse(session, user, id)), {"name": name})


@hug.delete('/{id}', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def delete_warehouse(session: helpers.extend.session, user: hug.directives.user, response, id: int):
    """Deletes a warehouse"""
    return helpers.delete("warehouse", session, queries.with_owner_role(queries.user_warehouse(session, user, id)))

@hug.get('/', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def list_warehouses(session: helpers.extend.session, user: hug.directives.user, response):
    """ Lists user warehouses """
    return queries.with_viewer_role(queries.user_warehouses(session, user)).all()

@hug.get('/{id}/settings', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def get_warehouse_settings(session: helpers.extend.session, user: hug.directives.user, response, id: int):
    """Gets a warehouse"""
    warehouse = helpers.get("warehouse", session, queries.with_viewer_role(queries.user_warehouse(session, user, id)))
    return helpers.response.from_json(warehouse.settings)

@hug.put('/{id}/settings', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def update_warehouse_settings(session: helpers.extend.session, user: hug.directives.user, response, id: int, body):
    """Gets a warehouse"""
    helpers.update("warehouse", session, queries.with_editor_role(queries.user_warehouse(session, user, id)), {"settings": json.dumps(body)})
    return body
