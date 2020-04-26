from .model import BASE, User, Warehouse, Warehouse_ACE, Location


def user_warehouses(session, user):
	return session.query(Warehouse).filter(Warehouse_ACE.user == user)
