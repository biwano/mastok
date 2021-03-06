#!python
import os
os.environ["MASTOK_CONFIG_FILE"] = "test.ini"

import pathlib
import hug
import mastok
import falcon
import config
import sys
import json
import datetime
from urllib.parse import urlencode

# Delete DB if it exists
PARENT = pathlib.Path(__file__).parent
try:
    os.remove(PARENT / "mastok.test.db")
except:
    print("Cannot remove test db")
    pass

debug_ = len(sys.argv) > 1

# Create db with alembic
os.environ["MASTOK_SQL_ALCHEMY_URL"] = config.get("sqlalchemy", "url")
stream = os.popen('alembic upgrade head')
output = stream.read()
print("Migrating database: ")
print(output)

def headers(user=None):
    return {
        "X-API-KEY": user["api_key"] if user is not None else "bad api key"
    }

def debug(txt):
    if debug_:
        print(txt)

def debug_response(response):
    debug(json.dumps(response.data, indent=4, sort_keys=True))


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
                u = url_and_param(model, id, kwargs.get("extra_url"))
                kwargs["url"] = u["url"]
                kwargs["params"] = u["params"]

            debug("")
            print(" - %s %s %s" % (function.__name__, args, kwargs))
            response = function(*args, **kwargs)
            debug_response(response)
            debug("status: %s" % response.status)
            debug("expected status: %s" % args[0])
            assert response.status == args[0]
            return response.data
        return wrapper
    return decorator

def url_and_param(model, id, extra_url=None):
    if type(id)==int:
        url = '/%s/%s' % (model, id)
        params=None
    else:
        url = '/%s' % model
        params = id
    if extra_url:
        url = '%s%s'% (url, extra_url)
    return { "url": url, "params": params}

def get(account, model, id, extra_url=None):
    u = url_and_param(model, id, extra_url)
    response = hug.test.get(mastok, u["url"], params=u["params"], headers=headers(account))
    debug("Response:")
    debug_response(response)
    return response.data       

@test()
def create_user(expect, mail):
    return hug.test.post(mastok, '/users', {'mail': mail })

@test()
def delete_user(expect, account, id):
    return hug.test.delete(mastok, '/users/%s' %id, headers=headers(account))

@test()
def auth_action(expect, account, action, mail,params={}):
    return hug.test.post(mastok, '/auth/%s/%s'%(mail, action), params=params, headers=headers(account))

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
def update(expect, account, model, id, payload, url=None, params=None, extra_url=None):
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
        print("Testing %s[%s] = %s (actual value is:%s)" % (model, key, payload[key], thing[key]))
        assert(thing[key] == payload[key])


    # delete things
    delete(falcon.HTTP_401, faker, model, id)
    delete(falcon.HTTP_200, owner, model, id)
    assert len(list(falcon.HTTP_200, owner, model, params)) == nb - 1


def tests_mastok():
    admin_user = config.getdict("authentication", "admin_user")
    admin_api_key = admin_user["api_key"]

    ############################## USERS
    user1_mail = "user1@mastok.com"
    user2_mail = "user2@mastok.com"
    user3_mail = "user3@mastok.com"
    # create user
    create_user(falcon.HTTP_400, "wrongemail@address")
    create_user(falcon.HTTP_200, user1_mail)
    create_user(falcon.HTTP_200, user2_mail)
    create_user(falcon.HTTP_200, user3_mail)
    user1 = auth_action(falcon.HTTP_200, None, "login", user1_mail, {})
    user2 = auth_action(falcon.HTTP_200, None, "login", user2_mail, {})
    user3 = auth_action(falcon.HTTP_200, None, "login", user3_mail, {})
    create_user(falcon.HTTP_400, "user2@mastok.com") # Create an existing user
    delete_user(falcon.HTTP_401, user1, user3["id"])
    delete_user(falcon.HTTP_200, admin_user, user3["id"])
    passcode = auth_action(falcon.HTTP_200, admin_user, "send_passcode", user1["mail"])["passcode"] # getpasscode
    auth_action(falcon.HTTP_401, None, "login", user1["mail"], {"passcode": "wrongpasscode"}) # authenticate with wrongpasscode
    user1 = auth_action(falcon.HTTP_200, None, "login", user1["mail"], {"passcode": passcode}) # authenticate with passcode and get verified user api_key
    assert(user1["is_mail_verified"])
    auth_action(falcon.HTTP_401, None, "login", user1["mail"], {"passcode": passcode}) # try to consume passcode twice
    auth_action(falcon.HTTP_401, None, "login", user1["mail"], {"api_key": "wrongapikey"}) # try to     uthenticate with wrong api_key
    
    # TODO: test get user

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

    # warehouse settings
    update(falcon.HTTP_200, user1, "warehouses", warehouse11["id"], {"my_setting": True}, extra_url="/settings")
    settings = get(user1, "warehouses", warehouse11["id"], extra_url="/settings")
    assert(settings=={"my_setting": True})

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

    ############################## CATEGORIES
    # create category
    category111 = create(falcon.HTTP_200, user1, "categories", {"warehouse_id": warehouse11["id"], "name": "My first category"})
    category112 = create(falcon.HTTP_200, user1, "categories", {"warehouse_id": warehouse11["id"], "name": "My second category"})
    category121 = create(falcon.HTTP_200, user1, "categories", {"warehouse_id": warehouse12["id"], "name": "My third category"})
    create(falcon.HTTP_401, user2, "categories", {"warehouse_id": warehouse12["id"], "name": "My fourth category"})
    category211 = create(falcon.HTTP_200, user2, "categories", {"warehouse_id": warehouse21["id"], "name": "My fifth category"})
    category212 = create(falcon.HTTP_200, user2, "categories", {"warehouse_id": warehouse21["id"], "name": "My sixth category"})
    category213 = create(falcon.HTTP_200, user2, "categories", {"warehouse_id": warehouse21["id"], "name": "My seventh category"})

    test_list_update_delete(user2, user1, "categories", 3, category213["id"], {"name":'This was My seventh category'}, params={"warehouse_id": warehouse21["id"]})

    ############################## REFERENCES
    # create reference

    reference111 = create(falcon.HTTP_200, user1, "references", {"warehouse_id": warehouse11["id"], "name": "My first reference", "categories": [category111["id"]]})
    reference112 = create(falcon.HTTP_200, user1, "references", {"warehouse_id": warehouse11["id"], "name": "My second reference"})
    reference121 = create(falcon.HTTP_200, user1, "references", {"warehouse_id": warehouse12["id"], "name": "My third reference"})
    create(falcon.HTTP_401, user2, "references", {"warehouse_id": warehouse12["id"], "name": "My fourth reference"})
    reference211 = create(falcon.HTTP_200, user2, "references", {"warehouse_id": warehouse21["id"], "name": "My fifth reference"})
    reference212 = create(falcon.HTTP_200, user2, "references", {"warehouse_id": warehouse21["id"], "name": "My sixth reference"})
    reference213 = create(falcon.HTTP_200, user2, "references", {"warehouse_id": warehouse21["id"], "name": "My seventh reference", "target_quantity": 12})

    test_list_update_delete(user2, user1, "references", 3, reference213["id"], {"name":'This was My seventh reference', "target_quantity": 15}, params={"warehouse_id": warehouse21["id"]})

    ############################## REFERENCES
    # create tags
    tag111 = create(falcon.HTTP_200, user1, "tags", {"warehouse_id": warehouse11["id"], "name": "My first tag"})
    tag112 = create(falcon.HTTP_200, user1, "tags", {"warehouse_id": warehouse11["id"], "name": "My second tag"})
    tag113 = create(falcon.HTTP_200, user1, "tags", {"warehouse_id": warehouse11["id"], "name": "My second tag bis"})
    tag121 = create(falcon.HTTP_200, user1, "tags", {"warehouse_id": warehouse12["id"], "name": "My third tag"})
    create(falcon.HTTP_401, user2, "tags", {"warehouse_id": warehouse12["id"], "name": "My fourth tag"})
    tag211 = create(falcon.HTTP_200, user2, "tags", {"warehouse_id": warehouse21["id"], "name": "My fifth tag"})
    tag212 = create(falcon.HTTP_200, user2, "tags", {"warehouse_id": warehouse21["id"], "name": "My sixth tag"})
    tag213 = create(falcon.HTTP_200, user2, "tags", {"warehouse_id": warehouse21["id"], "name": "My seventh tag"})


    ##############################  ARTICLES
    expiry = datetime.date.today().strftime("%Y-%m-%d")
    # create article
    article11 = create(falcon.HTTP_200, user1, "articles", { "warehouse_id": warehouse11["id"], "location_id": location111["id"], "reference_id": reference111["id"], "quantity": 5, "expiry": expiry, "tags": [tag111["id"], tag112["id"]]})
    article12 = create(falcon.HTTP_200, user1, "articles", { "warehouse_id": warehouse11["id"], "location_id": location111["id"], "reference_id": reference112["id"], "quantity":10, "expiry": expiry})
    article13 = create(falcon.HTTP_200, user1, "articles", { "warehouse_id": warehouse12["id"], "location_id": location121["id"], "reference_id": reference121["id"], "quantity":15, "expiry": expiry})
    create(falcon.HTTP_400, user1, "articles", { "warehouse_id": warehouse11["id"], "location_id": location111["id"], "reference_id": reference121["id"], "quantity":20}) # reference and location not in same warehouse
    create(falcon.HTTP_401, user2, "articles", { "warehouse_id": warehouse11["id"], "location_id": location111["id"], "reference_id": reference111["id"], "quantity":25}) # not authorized
    article21 = create(falcon.HTTP_200, user2, "articles", { "warehouse_id": warehouse21["id"], "location_id": location211["id"], "reference_id": reference211["id"], "quantity":30, "expiry": expiry})
    article22 = create(falcon.HTTP_200, user2, "articles", { "warehouse_id": warehouse21["id"], "location_id": location211["id"], "reference_id": reference212["id"], "quantity":40, "expiry": expiry})
    article23 = create(falcon.HTTP_200, user2, "articles", { "warehouse_id": warehouse21["id"], "location_id": location212["id"], "reference_id": reference212["id"], "quantity":50, "expiry": expiry})
    article24 = create(falcon.HTTP_200, user2, "articles", { "warehouse_id": warehouse21["id"], "location_id": location211["id"], "reference_id": reference211["id"], "quantity":35, "expiry": expiry}) # duplicate location and reference

    test_list_update_delete(user2, user1, "articles", 4, article23["id"],
        {"location_id": location212["id"], "quantity":7, "expiry": "2022-12-15", "tags": [tag213]},
        {"warehouse_id": warehouse21["id"]})
    

tests_mastok()