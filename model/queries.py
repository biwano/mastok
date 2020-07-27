from .model import BASE, User, Warehouse, WarehouseACE, Location, Reference, Category, Article, Tag

def has_warehouse(user, query):
	return query.\
	    filter(Warehouse.id == WarehouseACE.warehouse_id).\
	    filter(WarehouseACE.user == user)

def user_warehouses(session, user):
	return has_warehouse(user, session.query(Warehouse))

def user_warehouse(session, user, id):
	return user_warehouses(session, user).filter(Warehouse.id == id)

def user_warehouse_thing(session, user, Thing, id):
	return has_warehouse(user,
		session.query(Thing).\
		filter(Thing.id==id).\
	    filter(Thing.warehouse_id == Warehouse.id))

def user_location(session, user, id):
	return user_warehouse_thing(session, user, Location, id)

def user_reference(session, user, id):
	return user_warehouse_thing(session, user, Reference, id)

def user_category(session, user, id):
	return user_warehouse_thing(session, user, Category, id)

def user_article(session, user, id):
	return user_warehouse_thing(session, user, Article, id)

def warehouse_things(session, user, warehouse_id, Thing, ids):
	# Convert categories to ids 
	ids = list(map(lambda id: id if type(id) == int else id["id"], ids))
	return has_warehouse(user,
		session.query(Thing).\
		filter(Thing.id.in_(ids)).\
	    filter(Thing.warehouse_id == warehouse_id))

def warehouse_categories(session, user, warehouse_id, ids):
	return warehouse_things(session, user, warehouse_id, Category, ids)

def warehouse_tags(session, user, warehouse_id, ids):
	return warehouse_things(session, user, warehouse_id, Tag, ids)

def get_things_from_ids(session, user, warehouse_id, Thing, things):
    if things:
        db_things = warehouse_things(session, user, warehouse_id, Thing, things).all()
        if (len(db_things) != len(things)):
            return None
    else:
        db_things = []
    return db_things

def get_categories_from_ids(session, user, warehouse_id, categories):
	return get_things_from_ids(session, user, warehouse_id, Category, categories)

def get_tags_from_ids(session, user, warehouse_id, tags):
	return get_things_from_ids(session, user, warehouse_id, Tag, tags)
