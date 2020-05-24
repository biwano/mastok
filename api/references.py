""" part of the API managing references """
import hug
import falcon
from model import Reference, queries
from . import helpers


@hug.extend_api()
def shared():
    """ Adds common directives """
    return [helpers.extend]



@hug.post('', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def create_reference(session: helpers.extend.session, user: hug.directives.user, response, warehouse_id: int, name, categories=None):
    """Creates a reference"""
    if categories:
        db_categories = queries.warehouse_categories(session, user, warehouse_id, categories).all()
        if (len(db_categories) != len(categories)):
            return response.error("incoherent_request", falcon.HTTP_400)
    return helpers.do_in_warehouse("reference",
    	queries.user_warehouse(session, user, warehouse_id),
    	lambda warehouse: Reference(warehouse=warehouse, name=name, categories=db_categories))

@hug.get('/{id}', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def get_reference(session: helpers.extend.session, user: hug.directives.user, response, id: int):
    """Gets a reference"""
    return helpers.get("reference", session, queries.user_reference(session, user, id))

@hug.put('/{id}', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def update_reference(session: helpers.extend.session, user: hug.directives.user, response, id: int, name, categories=None):
    """Updates a reference"""
    return helpers.update("reference", session, queries.user_reference(session, user, id), {"name": name})

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
        print(name)
        if name:
            query = query.filter_by(name=name)
        return query.all()
    return helpers.do_in_warehouse("reference",
    	queries.user_warehouse(session, user, warehouse_id),filter)
