import hug
from . import warehouses
from . import locations
from . import accounts
from model import SESSION



@hug.extend_api('/warehouses')
def warehouse_api():
    return [warehouses]

@hug.extend_api('/locations')
def locations_api():
    return [locations]

@hug.extend_api('/accounts')
def accounts_api():
    return [accounts]