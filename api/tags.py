""" part of the API managing tags """
import hug  
from model import Tag, queries
from . import helpers


@hug.extend_api()
def shared():
    """ Adds common directives """
    return [helpers.extend]



@hug.post('', requires=helpers.authentication.is_authenticated)
@helpers.wraps  
def create_tag(session: helpers.extend.session, user: hug.directives.user, response, warehouse_id: int, name):
    """Creates a tag"""
    return helpers.do_in_warehouse("tag",
    	queries.user_warehouse(session, user, warehouse_id),
    	lambda warehouse: Tag(warehouse=warehouse, name=name))

@hug.get('/{id}', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def get_tag(session: helpers.extend.session, user: hug.directives.user, response, id: int):
    """Gets a tag"""
    return helpers.get("tag", session, queries.user_tag(session, user, id))

@hug.put('/{id}', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def update_tag(session: helpers.extend.session, user: hug.directives.user, response, id: int, name):
    """Updates a tag"""
    return helpers.update("tag", session, queries.user_tag(session, user, id), {"name": name})

@hug.delete('/{id}', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def delete_tag(session: helpers.extend.session, user: hug.directives.user, response, id: int):
    """Deletes a tag"""
    return helpers.delete("tag", session, queries.user_tag(session, user, id))

@hug.get('', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def list_tags(session: helpers.extend.session, user: hug.directives.user, response, warehouse_id: int, name=None):
    """ Lists warehouse tags """
    def filter(warehouse):
        query = session.query(Tag).filter_by(warehouse=warehouse)
        print(name)
        if name:
            query = query.filter_by(name=name)
        return query.all()
    return helpers.do_in_warehouse("tag",
    	queries.user_warehouse(session, user, warehouse_id),filter)
