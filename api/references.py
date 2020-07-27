""" part of the API managing references """
import hug
import falcon
from model import Reference, queries
from . import helpers
from marshmallow import fields


@hug.extend_api()
def shared():
    """ Adds common directives """
    return [helpers.extend]


@hug.post('', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def create_reference(session: helpers.extend.session, user: hug.directives.user, response, warehouse_id: int, name, categories=None, target_quantity: fields.Int(allow_none=True)=None):
    """Creates a reference"""
    if len(name) == 0:
        return helpers.response.error("reference_name_mandatory", falcon.HTTP_400)
    db_categories = queries.get_categories_from_ids(session, user, warehouse_id, categories)
    if db_categories == None:
        return response.error("invalid_category_ids", falcon.HTTP_400)
    return helpers.do_in_warehouse("reference",
    	queries.user_warehouse(session, user, warehouse_id),
    	lambda warehouse: Reference(warehouse=warehouse, name=name, categories=db_categories, target_quantity=target_quantity))

@hug.get('/{id}', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def get_reference(session: helpers.extend.session, user: hug.directives.user, response, id: int):
    """Gets a reference"""
    return helpers.get("reference", session, queries.user_reference(session, user, id))

@hug.put('/{id}', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def update_reference(session: helpers.extend.session, user: hug.directives.user, response, id: int, name, categories=None, target_quantity: fields.Int(allow_none=True)=None):
    """Updates a reference"""
    if len(name) == 0:
        return helpers.response.error("reference_name_mandatory", falcon.HTTP_400)
    db_categories = queries.get_categories_from_ids(session, user, session.query(Reference).get(id).warehouse_id, categories)
    if db_categories == None:
        return response.error("invalid_category_ids", falcon.HTTP_400)
    return helpers.update("reference", session, queries.user_reference(session, user, id), {"name": name, "categories":db_categories, "target_quantity": target_quantity })

@hug.delete('/{id}', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def delete_reference(session: helpers.extend.session, user: hug.directives.user, response, id: int):
    """Deletes a reference"""
    return helpers.delete("reference", session, queries.user_reference(session, user, id))

@hug.get('', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def list_references(session: helpers.extend.session, user: hug.directives.user, response, warehouse_id: int, name=None):
    """ Lists warehouse references """
    def filter(warehouse):
        query = session.query(Reference).filter_by(warehouse=warehouse)
        if name:
            query = query.filter_by(name=name)
        return query.all()
    return helpers.do_in_warehouse("reference",
    	queries.user_warehouse(session, user, warehouse_id),filter)
