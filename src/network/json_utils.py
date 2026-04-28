import json

def create_json(uid, hp, x, y, type=None):
    data = {
        "uid": uid,
        "hp": hp,
        "x": x,
        "y": y,
        "type" : type
    }

    msg = json.dumps(data)  # dict → string JSON

    return msg

def create_jsonbis(Req, uid, ETAT, Post_local):
    data = {
        "Req": Req,
        "uid": uid,
        "etat": etat,
        "Post_local": Post_local
    }

    msg = json.dumps(data)  # dict → string JSON

    return msg

def load_json(msg):

    data = json.loads(msg)  # string → dict
    
    return data
