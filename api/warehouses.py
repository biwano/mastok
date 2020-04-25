""" part of the API managing warehouses """
import uuid 
import hug
from model import Session, Warehouse
from . import helpers


@hug.extend_api()
def shared():
    """ Adds common directives """
    return [helpers.extend]

@hug.post('/', requires=helpers.authentication.is_authenticated)
def create_warehouse():
    """Creates a warehouse"""
    with Session() as session:
        warehouse = Warehouse(uuid=uuid.uuid1().hex)
        session.add(warehouse)

    return warehouse.to_dict()
    