from .model import BASE, User, Warehouse, Warehouse_ACE, Location, Reference, Category, Item

def has_warehouse(user, query):
	return query.\
	    filter(Warehouse.id == Warehouse_ACE.warehouse_id).\
	    filter(Warehouse_ACE.user == user)

def user_warehouses(session, user):
	return has_warehouse(user, session.query(Warehouse))

def user_warehouse(session, user, id):
	return user_warehouses(session, user).filter(Warehouse.id == id)

def user_location(session, user, id):
	return has_warehouse(user,
		session.query(Location).\
		filter(Location.id==id).\
	    filter(Location.warehouse_id == Warehouse.id))

def user_reference(session, user, id):
	return has_warehouse(user,
		session.query(Reference).\
		filter(Reference.id==id).\
	    filter(Reference.warehouse_id == Warehouse.id))

def user_category(session, user, id):
	return has_warehouse(user,
		session.query(Category).\
		filter(Category.id==id).\
	    filter(Category.warehouse_id == Warehouse.id))

def warehouse_categories(session, user, warehouse_id, ids):
	return has_warehouse(user,
		session.query(Category).\
		filter(Category.id.in_(ids)).\
	    filter(Category.warehouse_id == warehouse_id))

def user_item(session, user, id):
    return has_warehouse(user,
        session.query(Item).\
        filter(Item.id == id).\
        filter(Item.location_id == Location.id).\
        filter(Location.warehouse_id == Warehouse.id))