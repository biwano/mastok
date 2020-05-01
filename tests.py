import os
os.environ["MASTOK_CONFIG_FILE"] = "test.ini"

import pathlib
import hug
import mastok
import falcon
import config
import sys
import json
from urllib.parse import urlencode

# Delete DB if it exists
PARENT = pathlib.Path(__file__).parent
try:
    os.remove(PARENT / "mastok.test.db")
except:
    pass

debug_ = len(sys.argv) > 1

# Create db with alembic
os.environ["MASTOK_SQL_ALCHEMY_URL"] = config.get("sqlalchemy", "url")
stream = os.popen('alembic upgrade head')
output = stream.read()
print(output)

def headers(user=None):
    return {
        "X-API-KEY": user["api_key"] if user is not None else "bad api key"
    }

def debug(response):
    if debug_:
        print(json.dumps(response.data, indent=4, sort_keys=True))
        print("\n")

def get(account, model, id):
    u = url_and_param(model, id)
    response = hug.test.get(mastok, u["url"], params=u["params"], headers=headers(account))
    debug(response)
    return response.data

def test_value(account, model, id, field, value):
    print("Testing %s[%s].%s = %s" % (model, id, field, value))
    data = get(account, model, id)
    assert data[field] == value

def test(autoroute=False):
    def decorator(function):
        def wrapper(*args, **kwargs):
            if autoroute:
                model = args[2]
                id = args[3]
                u = url_and_param(model, id)
                kwargs["url"] = u["url"]
                kwargs["params"] = u["params"]

            print(" - %s %s %s" % (function.__name__, args, kwargs))
            response = function(*args, **kwargs)
            debug(response)
            assert response.status == args[0]
            return response.data
        return wrapper
    return decorator

def url_and_param(model, id):
    if type(id)==int:
        url = '/%s/%s' % (model, id)
        params=None
    else:
        url = '/%s' % model
        params = id
    return { "url": url, "params": params}
       

@test()
def create_user(expect, mail):
    return hug.test.post(mastok, '/users', {'mail': mail })

@test()
def list_users(expect, account):
    return hug.test.get(mastok, '/users', headers=headers(account))

@test()
def create(expect, account, model, payload):
    return hug.test.post(mastok, '/%s' % model, payload, headers=headers(account))

@test()
def list(expect, account, model, params=None):
    return hug.test.get(mastok, '/%s' % model, params=params, headers=headers(account))

@test(autoroute=True)
def delete(expect, account, model, id, url=None, params=None):
    return hug.test.delete(mastok, url, params=params, headers=headers(account))

@test(autoroute=True)
def update(expect, account, model, id, payload, url=None, params=None):
    return hug.test.put(mastok, url, payload, params=params, headers=headers(account))

def test_list_update_delete(owner, faker, model, nb, id, payload, params=None):
    # list things
    things = list(falcon.HTTP_200, owner, model, params)
    assert len(things) == nb

    # update things
    update(falcon.HTTP_200, owner, model, id, payload)
    update(falcon.HTTP_401, faker, model, id, payload)
    thing = get(owner, model, id)
    for key in payload:
        assert(thing[key] == payload[key])


    # delete things
    delete(falcon.HTTP_401, faker, model, id)
    delete(falcon.HTTP_200, owner, model, id)
    assert len(list(falcon.HTTP_200, owner, model, params)) == nb - 1


def tests_mastok():
    admin_user = config.getdict("authentication", "admin_user")
    admin_api_key = admin_user["api_key"]

    ############################## USERS
    # create user
    user1 = create_user(falcon.HTTP_200, "user1@mastok.com")
    user2 = create_user(falcon.HTTP_200, "user2@mastok.com")
    create_user(falcon.HTTP_401, "user2@mastok.com")

    # list users
    users = list_users(falcon.HTTP_200, admin_user)
    assert len(users) == 2
    # non admin cant list users
    list_users(falcon.HTTP_401, user1)

    ############################## WAREHOUSES
    # create warehouse
    warehouse11 = create(falcon.HTTP_200, user1, "warehouses", { "name": 'My first warehouse'})
    warehouse12 = create(falcon.HTTP_200, user1, "warehouses", { "name": 'My second warehouse'})
    warehouse21 = create(falcon.HTTP_200, user2, "warehouses", { "name": 'My first warehouse (2)'})
    warehouse22 = create(falcon.HTTP_200, user2, "warehouses", { "name": 'My second warehouse (2)'})

    test_list_update_delete(user2, user1, "warehouses", 2, warehouse22["id"], {"name":'This was My second warehouse (2)'})
    

    ############################## LOCATIONS
    # create location
    location111 = create(falcon.HTTP_200, user1, "locations", {"warehouse_id": warehouse11["id"], "name": "My first location"})
    location112 = create(falcon.HTTP_200, user1, "locations", {"warehouse_id": warehouse11["id"], "name": "My second location"})
    location121 = create(falcon.HTTP_200, user1, "locations", {"warehouse_id": warehouse12["id"], "name": "My third location"})
    create(falcon.HTTP_401, user2, "locations", {"warehouse_id": warehouse11["id"], "name": "My fourth location"})
    location211 = create(falcon.HTTP_200, user2, "locations", {"warehouse_id": warehouse21["id"], "name": "My fifth location"})
    location212 = create(falcon.HTTP_200, user2, "locations", {"warehouse_id": warehouse21["id"], "name": "My sixth location"})
    location213 = create(falcon.HTTP_200, user2, "locations", {"warehouse_id": warehouse21["id"], "name": "My seventh location"})

    # list locations
    list(falcon.HTTP_401, user2, "locations/", { "warehouse_id": warehouse11["id"]})
    locations = list(falcon.HTTP_200, user1, "locations/", { "warehouse_id": warehouse11["id"]})
    assert len(locations) == 2

    test_list_update_delete(user2, user1, "locations", 3, location213["id"], {"name":'This was My seventh location'}, params={"warehouse_id": warehouse21["id"]})

    ############################## REFERENCES
    # create reference
    reference111 = create(falcon.HTTP_200, user1, "references", {"warehouse_id": warehouse11["id"], "name": "My first reference"})
    reference112 = create(falcon.HTTP_200, user1, "references", {"warehouse_id": warehouse11["id"], "name": "My second reference"})
    reference121 = create(falcon.HTTP_200, user1, "references", {"warehouse_id": warehouse12["id"], "name": "My third reference"})
    create(falcon.HTTP_401, user2, "references", {"warehouse_id": warehouse12["id"], "name": "My fourth reference"})
    reference211 = create(falcon.HTTP_200, user2, "references", {"warehouse_id": warehouse21["id"], "name": "My fifth reference"})
    reference212 = create(falcon.HTTP_200, user2, "references", {"warehouse_id": warehouse21["id"], "name": "My sixth reference"})
    reference213 = create(falcon.HTTP_200, user2, "references", {"warehouse_id": warehouse21["id"], "name": "My seventh reference"})

    test_list_update_delete(user2, user1, "references", 3, reference213["id"], {"name":'This was My seventh reference'}, params={"warehouse_id": warehouse21["id"]})

    ############################## ITEMS
    # create item
    item11 = create(falcon.HTTP_200, user1, "items", { "location_id": location111["id"], "reference_id": reference111["id"], "quantity": 5})
    item12 = create(falcon.HTTP_200, user1, "items", { "location_id": location111["id"], "reference_id": reference112["id"], "quantity":10})
    item13 = create(falcon.HTTP_200, user1, "items", { "location_id": location121["id"], "reference_id": reference121["id"], "quantity":15})
    create(falcon.HTTP_400, user1, "items", { "location_id": location111["id"], "reference_id": reference121["id"], "quantity":20}) # reference and location not in same warehouse
    create(falcon.HTTP_401, user2, "items", { "location_id": location111["id"], "reference_id": reference111["id"], "quantity":25}) # not authorized
    item21 = create(falcon.HTTP_200, user2, "items", { "location_id": location211["id"], "reference_id": reference211["id"], "quantity":30})
    item22 = create(falcon.HTTP_200, user2, "items", { "location_id": location211["id"], "reference_id": reference212["id"], "quantity":40})
    item23 = create(falcon.HTTP_200, user2, "items", { "location_id": location212["id"], "reference_id": reference212["id"], "quantity":50})
    create(falcon.HTTP_400, user2, "items", { "location_id": location211["id"], "reference_id": reference211["id"], "quantity":35}) # duplicate location and reference

    test_list_update_delete(user2, user1, "items", 1, 
        {"location_id": location212["id"], "reference_id": reference212["id"]},
        {"quantity":7},
        {"location_id": location212["id"]})

tests_mastok()