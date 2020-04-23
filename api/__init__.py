import hug
from . import warehouse

@hug.extend_api('/warehouses')
def warehouse_api():
    return [warehouse]