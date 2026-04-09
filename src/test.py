import json
from model.Unit import Unit


data_list = [
    '{"uid": 1999, "hp": 32, "x": 40, "y": 50, "type": "P"}',
    '{"uid": 1324, "hp": 78, "x": -12, "y": 34, "type": "K"}',
    '{"uid": 1789, "hp": 45, "x": 22, "y": -5, "type": "C"}',
    '{"uid": 1543, "hp": 91, "x": -47, "y": 12, "type": "P"}',
    '{"uid": 1198, "hp": 23, "x": 8, "y": -33, "type": "K"}',
    '{"uid": 1650, "hp": 67, "x": 49, "y": 0, "type": "C"}',
    '{"uid": 1432, "hp": 10, "x": -25, "y": -44, "type": "P"}',
    '{"uid": 1876, "hp": 88, "x": 15, "y": 27, "type": "K"}',
    '{"uid": 1211, "hp": 52, "x": -3, "y": -19, "type": "C"}',
    '{"uid": 1999, "hp": 36, "x": 40, "y": 50, "type": "P"}',
    '{"uid": 1107, "hp": 99, "x": -50, "y": -1, "type": "K"}'
]
battlefield = {}

def depilement_liste(data_list):
    while data_list:
        element = data_list.pop(0)

        data = json.loads(element)
        if data["type"] == 'K':
            data["name"] = "Knight"
            data["type_attack"]="Melee"
        if data["type"] == 'C':
            data["name"] = "Crossbowman"
            data["type_attack"]="Pierce"
        if data["type"] == 'P':
            data["name"] = "Pikeman"
            data["type_attack"]="Melee"

        data["attack"] = None
        data["armor"] = None
        data["pierce_armor"] = None
        data["range"] = None
        data["line_of_sight"] = None
        data["speed"] = None
        data["attack_delay"] = None
        data["reload_time"] = None
        data["accuracy"] = None

        uid = data["uid"]

        # Création de l'unité avec les stats du fichier
        battlefield[uid] = Unit(
            data["uid"],
            data["name"],
            data["type"],
            data["hp"],
            data["type_attack"],
            data["attack"],
            data["armor"],
            data["pierce_armor"],
            data["range"],
            data["line_of_sight"],
            data["speed"],
            data["attack_delay"],
            data["reload_time"],
            data["accuracy"],
            (data["x"], data["y"])
        )
    print("\nBattlefield complet :", battlefield)
    return battlefield

depilement_liste(data_list)

