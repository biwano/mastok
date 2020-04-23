import hug
from model import Session, Warehouse
import uuid 


@hug.post('/')
def create_warehouse():
    """Creates a warehouse"""
    with Session() as session:
        warehouse = Warehouse(uuid=uuid.uuid1().hex)
        session.add(warehouse)

    return warehouse.to_dict()
    