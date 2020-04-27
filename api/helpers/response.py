def error(message, status):
    return {"error": message,
            "status": status
    }

def ok(message):
    return {"result": message}

def list(items):
    return [item.to_dict() for item in items]


def item(item):
    return item.to_dict()
