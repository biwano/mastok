import hug
from . import users
from . import auth
from . import warehouses
from . import locations
from . import references
from . import categories
from . import articles
from . import tags
from model import SESSION



@hug.extend_api('/users')
def users_api():
    return [users]

@hug.extend_api('/auth')
def authentication_api():
    return [auth]

@hug.extend_api('/warehouses')
def warehouse_api():
    return [warehouses]

@hug.extend_api('/locations')
def locations_api():
    return [locations]


@hug.extend_api('/references')
def references_api():
    return [references]

@hug.extend_api('/categories')
def categories_api():
    return [categories]

@hug.extend_api('/articles')
def articles_api():
    return [articles]

@hug.extend_api('/tags')
def tags_api():
    return [tags]
