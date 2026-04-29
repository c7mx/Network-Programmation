import json

def create_json(uid, type, hp=None, x=None, y=None):
    
    if hp and x and y:
        data = {
            "uid": uid,
            "hp": hp,
            "x": x,
            "y": y,
            "type" : type
        }
    
    elif hp:
        data = {
            "uid": uid,
            "hp": hp,
            "type" : type
        }

    elif x and y:
        data = {
            "uid": uid,
            "x": x,
            "y": y,
            "type" : type
        }

    else:
        return ""

    msg = json.dumps(data)  # dict → string JSON

    return msg

def create_jsonbis(Req, uid, etat, Post_local):
    data = {
        "Req": Req,
        "uid": uid,
        "etat": etat,
        "Post_local": Post_local
    }

    msg = json.dumps(data)  # dict → string JSON

    return msg



def create_jsonbisbis(Ask, uid, etat, Post_local):
    data = {
        "Ask": Ask,
        "uid": uid,
        "etat": etat,
        "Post_local": Post_local
    }

    msg = json.dumps(data)  # dict → string JSON

    return msg
    
def load_json(msg):

    data = json.loads(msg)  # string → dict
    
    return data
