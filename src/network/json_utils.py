import json

def create_json(uid, hp, x, y):
    data = {
        "uid": uid,
        "hp": hp,
        "x": x,
        "y": y   
    }

    msg = json.dumps(data)  # dict → string JSON

    return msg

def load_json(msg):

    data = json.loads(msg)  # string → dict
    
    return data
