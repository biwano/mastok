from .model import BASE, User, Warehouse, WarehouseACE, Location, Reference, Category, Article

def has_warehouse(user, query):
	return query.\
	    filter(Warehouse.id == WarehouseACE.warehouse_id).\
	    filter(WarehouseACE.user == user)

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
	# Convert categories to ids 
	ids = list(map(lambda id: id if type(id)==int else id["id"], ids))
	print(ids)
	return has_warehouse(user,
		session.query(Category).\
		filter(Category.id.in_(ids)).\
	    filter(Category.warehouse_id == warehouse_id))

def user_article(session, user, id):
    return has_warehouse(user,
        session.query(Article).\
        filter(Article.id == id).\
        filter(Article.warehouse_id == Warehouse.id))
