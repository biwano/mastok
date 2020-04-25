""" part of the API managing locations """
import uuid
import hug
from model import Session, Location
from . import helpers


@hug.extend_api()
def shared():
    """ Adds common directives """
    return [helpers.extend]

@hug.post('/', requires=helpers.authentication.is_authenticated)
@helpers.wraps
def create_location():
    """Creates a warehouse"""
    with Session() as session:
        location = Location(uuid=uuid.uuid1().hex)
        session.add(location)

    return location.to_dict()
    