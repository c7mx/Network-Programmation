
import json
import sys
import os

# Absolute path of src directory
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from model.Unit import Unit
from model.Battlefield import Battlefield

def update(data_list, battlefield: Battlefield):
    while data_list:
        data = data_list.pop(0)

        # BUG 1 FIXED : if → elif pour éviter de tester les 3 types à chaque fois
        if data["type"] == 'K':
            data["name"] = "Knight"
            data["type_attack"] = "Melee"
            data["attack"] = 8
            data["armor"] = 2
            data["pierce_armor"] = 2
            data["range"] = 0.01
            data["line_of_sight"] = 0
            data["speed"] = 1.35
            data["attack_delay"] = 0
            data["reload_time"] = 1.8
            data["accuracy"] = 1

        elif data["type"] == 'C':
            data["name"] = "Crossbowman"
            data["type_attack"] = "Pierce"
            data["attack"] = 5
            data["armor"] = 0
            data["pierce_armor"] = 0
            data["range"] = 5
            data["line_of_sight"] = 0
            data["speed"] = 0.96
            data["attack_delay"] = 0
            data["reload_time"] = 5
            data["accuracy"] = 0.85

        elif data["type"] == 'P':
            data["name"] = "Pikeman"
            data["type_attack"] = "Melee"
            data["attack"] = 4
            data["armor"] = 0
            data["pierce_armor"] = 0
            data["range"] = 0.01
            data["line_of_sight"] = 0
            data["speed"] = 1
            data["attack_delay"] = 0
            data["reload_time"] = 3
            data["accuracy"] = 1

        else:
            # Type inconnu : on ignore ce message
            continue

        uid = data["uid"]

        if uid not in battlefield.troupes:
            if data["hp"] > 0:
                battlefield.troupes[uid] = Unit(
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
        else:
            if data["hp"] < battlefield.troupes[uid].hp:
                battlefield.troupes[uid].hp = data["hp"]

            if battlefield.troupes[uid].line_of_sight == 0:
                if (battlefield.troupes[uid].position[0] != data["x"]
                        or battlefield.troupes[uid].position[1] != data["y"]):
                    battlefield.troupes[uid].position = (data["x"], data["y"])

            # BUG 2 FIXED : un seul remove_unit, protégé par un 'in' pour éviter KeyError
            if uid in battlefield.troupes and battlefield.troupes[uid].hp <= 0:
                battlefield.remove_unit(uid)
