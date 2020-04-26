import hug
from . import warehouses
from . import locations
from . import users
from model import SESSION



@hug.extend_api('/warehouses')
def warehouse_api():
    return [warehouses]

@hug.extend_api('/locations')
def locations_api():
    return [locations]

@hug.extend_api('/users')
def users_api():
    return [users]