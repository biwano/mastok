def error(message, status, details=None):
    res =  {"error": message,
            "status": status
    }
    if details:
        res.update({ 'details': details})
    return res

def ok(message):
    return {"result": message}

def data(message):
    return data

def list(items):
    return [item.to_dict() for item in items]


def item(item):
    return item.to_dict()
