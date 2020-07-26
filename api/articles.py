""" part of the API managing locations """
import falcon
import uuid
import hug
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import exc
from model import Session, Location, Article, queries
from . import helpers
from marshmallow import fields

@hug.extend_api()
def shared():
    """ Adds common directives """
    return [helpers.extend]

@hug.post('', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def create_article(session: helpers.extend.session, user: hug.directives.user, response, warehouse_id: int, reference_id: int, quantity: int, expiry: fields.Date(allow_none=True)=None, location_id: fields.Int(allow_none=True)=None):
    """Creates a location"""
    try:
        warehouse = queries.user_warehouse(session, user, warehouse_id).one()
        location = queries.user_location(session, user, location_id).one() if location_id else None
        reference = queries.user_reference(session, user, reference_id).one()
        if warehouse.id != reference.warehouse.id or (location is not None and warehouse.id != location.warehouse.id):
            return helpers.response.error("bad_referenece_and_or_location", falcon.HTTP_400)
        article = Article(warehouse=warehouse, location=location, reference=reference, quantity=quantity, expiry=expiry)
        return article
    except NoResultFound:
        return helpers.response.error("warehouse_location_or_reference_not_found", falcon.HTTP_401)

@hug.get('/{id}', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def get_article(session: helpers.extend.session, user: hug.directives.user, response, id: int=None):
    """Gets a article"""
    return helpers.get("article", session, queries.user_article(session, user, id))


@hug.put('/{id}', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def update_article(session: helpers.extend.session, user: hug.directives.user, response, id: int, quantity: int, expiry: fields.Date(allow_none=True)=None, location_id: fields.Int(allow_none=True)=None):
    """Updates a article"""
    def update(article):
        if location_id:
            location = queries.user_location(session, user, location_id).one()
            if location.warehouse_id != article.warehouse_id:
                raise Exception("Incoherent request")
        return {"location_id": location_id, "quantity": quantity, "expiry": expiry}
    try:
        print(id)
        return helpers.update("article", session, queries.user_article(session, user, id), update)
    except Exception:
        return helpers.response.error("incoherent request", falcon.HTTP_404)    

@hug.delete('/{id}', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def delete_article(session: helpers.extend.session, user: hug.directives.user, response, id: int):
    """Deletes a article"""
    return helpers.delete("article", session, queries.user_article(session, user, id))

@hug.get('', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def list_articles(session: helpers.extend.session, user: hug.directives.user, response, warehouse_id: int=None, location_id: int=None):
    """ Lists warehouse locations """
    if location_id is not None:
        """ Lists location articles """
        return helpers.do_in_location("article",
            queries.user_location(session, user, location_id),
            lambda location: session.query(Article).filter_by(location=location).all())
    elif warehouse_id is not None:
        """ Lists location articles """
        return helpers.do_in_warehouse("article",
            queries.user_warehouse(session, user, warehouse_id),
            lambda warehouse: session.query(Article).filter_by(warehouse=warehouse).all())
    else:
        return response.error("incoherent_request", falcon.HTTP_400)
