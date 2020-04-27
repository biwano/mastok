import hug
from . import users
from . import warehouses
from . import locations
from . import references
from . import items
from model import SESSION



@hug.extend_api('/users')
def users_api():
    return [users]

@hug.extend_api('/warehouses')
def warehouse_api():
    return [warehouses]

@hug.extend_api('/locations')
def locations_api():
    return [locations]


@hug.extend_api('/references')
def references_api():
    return [references]

@hug.extend_api('/items')
def items_api():
    return [items]
