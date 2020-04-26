""" part of the API managing warehouses """
import hug
from sqlalchemy.orm.exc import NoResultFound
from model import Warehouse, Warehouse_ACE, queries
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
    ace = Warehouse_ACE(warehouse=warehouse, user=user)
    session.add(ace)
    return warehouse


@hug.delete('/{id}', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def delete_warehouse(session: helpers.extend.session, user: hug.directives.user, id: int):
    """Deletes an account"""
    try:
        warehouse = queries.user_warehouses(session, user).filter(Warehouse.id == id).one()
        session.delete(warehouse)
        return helpers.response.ok("warehouse_deleted")
    except NoResultFound:
        return helpers.response.error("warehouse_not_found")

@hug.get('/', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def list_warehouses(session: helpers.extend.session, user: hug.directives.user):
    """ Lists all accounts """
    warehouses = queries.user_warehouses(session, user).all()
    return warehouses
