import os
os.environ["MASTOK_CONFIG_FILE"] = "test.ini"

import pathlib
import hug
import mastok
import falcon
import config
import sys

# Delete DB if it exists
PARENT = pathlib.Path(__file__).parent
try:
    os.remove(PARENT / "mastok.test.db")
except:
	pass

debug_ = len(sys.argv) > 1
print(debug_)

# Create db with alembic
os.environ["MASTOK_SQL_ALCHEMY_URL"] = config.get("sqlalchemy", "url")
stream = os.popen('alembic upgrade head')
output = stream.read()
print(output)

def headers(user=None):
	return {
		"X-API-KEY": user["api_key"] if user is not None else "bad api key"
	}

def test():
    def decorator(function):
        def wrapper(*args, **kwargs):
            print(" - %s %s %s" % (function.__name__, args, kwargs))
            response = function(*args, **kwargs)
            if debug_:
                print(response.data)
            assert response.status == args[0]
            return response.data
        return wrapper
    return decorator
  
        

@test()
def create_user(expect, mail):
    return hug.test.post(mastok, '/users', {'mail': mail })

@test()
def list_users(expect, account):
    return hug.test.get(mastok, '/users',headers=headers(account))

@test()
def create_warehouse(expect, account, name):
    return hug.test.post(mastok, '/warehouses', {'name': name }, headers=headers(account))

@test()
def list_warehouses(expect, account):
    return hug.test.get(mastok, '/warehouses', headers=headers(account))

@test()
def delete_warehouse(expect, account, warehouse_id):
    print("(%s) Delete warehouse %s " % (account["mail"], warehouse_id))
    return hug.test.delete(mastok, '/warehouses/%s' % warehouse_id, headers=headers(account))

@test()
def create_location(expect, account, warehouse_id, name):
    return hug.test.post(mastok, '/locations/', 
    	{"name": name, "warehouse_id": warehouse_id}, headers=headers(account))

@test()
def create_reference(expect, account, warehouse_id, name):
    return hug.test.post(mastok, '/references/', 
    	{"name": name, "warehouse_id": warehouse_id}, headers=headers(account))

@test()
def create_item(expect, account, location_id, reference_id, quantity):
    return hug.test.post(mastok, '/items/', 
    	{"location_id": location_id, "reference_id": reference_id, "quantity": quantity}, headers=headers(account))


def tests_mastok():
    admin_user = config.getdict("authentication", "admin_user")
    admin_api_key = admin_user["api_key"]

	# create user
    user1 = create_user(falcon.HTTP_200, "user1@mastok.com")
    user2 = create_user(falcon.HTTP_200, "user2@mastok.com")
    create_user(falcon.HTTP_401, "user2@mastok.com")

	# list users
    users = list_users(falcon.HTTP_200, admin_user)
    assert len(users) == 2
    list_users(falcon.HTTP_401, user1)

	# create warehouse
    warehouse11 = create_warehouse(falcon.HTTP_200, user1, 'My first warehouse')
    warehouse12 = create_warehouse(falcon.HTTP_200, user1, 'My second warehouse')
    warehouse21 = create_warehouse(falcon.HTTP_200, user2, 'My first warehouse (2)')

	# list warehouses
    warehouses = list_warehouses(falcon.HTTP_200, user1)
    assert len(warehouses) == 2

    # delete warehouse
    delete_warehouse(falcon.HTTP_401, user2, warehouse11["id"])
    delete_warehouse(falcon.HTTP_200, user1, warehouse11["id"])

	# create location
    location111 = create_location(falcon.HTTP_200, user1, warehouse11["id"], "My first location")
    location112 = create_location(falcon.HTTP_200, user1, warehouse11["id"], "My second location")
    location121 = create_location(falcon.HTTP_200, user1, warehouse12["id"], "My third location")
    create_location(falcon.HTTP_401, user2, warehouse11["id"], "My fourth location")
    location211 = create_location(falcon.HTTP_200, user2, warehouse21["id"], "My fifth location")

	# create reference
    reference111 = create_reference(falcon.HTTP_200, user1, warehouse11["id"], "My first reference")
    reference112 = create_reference(falcon.HTTP_200, user1, warehouse11["id"], "My second reference")
    reference121 = create_reference(falcon.HTTP_200, user1, warehouse12["id"], "My third reference")
    create_reference(falcon.HTTP_401, user2, warehouse12["id"], "My fourth reference")
    reference211 = create_reference(falcon.HTTP_200, user2, warehouse21["id"], "My fifth reference")

	# create item
    create_item(falcon.HTTP_200, user1, location111["id"], reference111["id"], 5)
    create_item(falcon.HTTP_200, user1, location111["id"], reference112["id"], 10)
    create_item(falcon.HTTP_200, user1, location121["id"], reference121["id"], 15)
    create_item(falcon.HTTP_400, user1, location111["id"], reference121["id"], 20)
    create_item(falcon.HTTP_401, user2, location111["id"], reference111["id"], 25)



tests_mastok()