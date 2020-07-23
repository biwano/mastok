import hug
from model import SESSION

@hug.directive()
def session(context_name='session', request=None, **kwargs):
    """Returns the session associated with the current request"""
    return SESSION()