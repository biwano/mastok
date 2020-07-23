""" part of the API managing categories """
import hug
from model import Category, queries
from . import helpers


@hug.extend_api()
def shared():
    """ Adds common directives """
    return [helpers.extend]



@hug.post('', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def create_category(session: helpers.extend.session, user: hug.directives.user, response, warehouse_id: int, name):
    """Creates a category"""
    return helpers.do_in_warehouse("category",
    	queries.user_warehouse(session, user, warehouse_id),
    	lambda warehouse: Category(warehouse=warehouse, name=name))

@hug.get('/{id}', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def get_category(session: helpers.extend.session, user: hug.directives.user, response, id: int):
    """Gets a category"""
    return helpers.get("category", session, queries.user_category(session, user, id))

@hug.put('/{id}', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def update_category(session: helpers.extend.session, user: hug.directives.user, response, id: int, name):
    """Updates a category"""
    return helpers.update("category", session, queries.user_category(session, user, id), {"name": name})

@hug.delete('/{id}', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def delete_category(session: helpers.extend.session, user: hug.directives.user, response, id: int):
    """Deletes a category"""
    return helpers.delete("category", session, queries.user_category(session, user, id))

@hug.get('', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def list_categories(session: helpers.extend.session, user: hug.directives.user, response, warehouse_id: int, name=None):
    """ Lists warehouse categories """
    def filter(warehouse):
        query = session.query(Category).filter_by(warehouse=warehouse)
        print(name)
        if name:
            query = query.filter_by(name=name)
        return query.all()
    return helpers.do_in_warehouse("category",
    	queries.user_warehouse(session, user, warehouse_id),filter)
