import sys
import os

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from model.Unit import Unit
from model.Battlefield import Battlefield
import network.comm_py_c as NetPy

VALID_UNIT_TYPES = {'K', 'C', 'P'}

def is_possible_action(data: dict, battlefield: Battlefield) -> bool:
    required_fields = {"uid", "hp", "x", "y", "type"}

    if not required_fields.issubset(data.keys()):
        print(f"[REJECTED] Missing Fields: {required_fields - data.keys()}")
        return False

    if data["type"] not in VALID_UNIT_TYPES:
        print(f"[REJECTED] Invalid Type : '{data['type']}'")
        return False

    if data["hp"] < 0:
        print(f"[REJECTED] Negative HP : {data['hp']}")
        return False

    if not battlefield.is_valid_position((data["x"], data["y"])):
        print(f"[REJECTED] Out of Bounds Location : ({data['x']}, {data['y']})")
        return False

    return True


def update(data_list, battlefield: Battlefield):
    while data_list:
        data = data_list.pop(0)

        if "Req" in data:
            post_local = data["Post_local"]
            if (battlefield.troupes[post_local*1000 + 1].line_of_sight != 0):
                uid = data["uid"]
                if(uid in battlefield.troupes):
                    battlefield.troupes[uid].property = True

        elif "Ask" in data:
            uid = data["uid"]
            if(uid in battlefield.troupes and battlefield.troupes[uid].property):
                battlefield.troupes[uid].property = False
                sockp = NetPy.connect_sock_send()
                NetPy.send_property(sockp, "Req", data["uid"], None, data["Post_local"])

        else: 
            if not is_possible_action(data, battlefield):
                continue
            if data["type"] == 'K':
                data["name"] = "Knight"
                data["type_attack"] = "Melee"
                data["attack"] = 8
                data["armor"] = 2
                data["pierce_armor"] = 2
                data["range"] = 0.01
                data["speed"] = 1.35
                data["reload_time"] = 1.8
                data["accuracy"] = 1

            if data["type"] == 'C':
                data["name"] = "Crossbowman"
                data["type_attack"] = "Pierce"
                data["attack"] = 5
                data["armor"] = 0
                data["pierce_armor"] = 0
                data["range"] = 5
                data["speed"] = 0.96
                data["reload_time"] = 5
                data["accuracy"] = 0.85

            if data["type"] == 'P':
                data["name"] = "Pikeman"
                data["type_attack"] = "Melee"
                data["attack"] = 4
                data["armor"] = 0
                data["pierce_armor"] = 0
                data["range"] = 0.01
                data["speed"] = 1
                data["reload_time"] = 3
                data["accuracy"] = 1

            data["attack_delay"] = 0
            data["line_of_sight"] = 0
            data["property"] = False
            uid = data["uid"]

            if uid not in battlefield.troupes:
                if data ["hp"] != 0:
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
                        (data["x"], data["y"]),
                        data["property"]
                    )

            else:
                if data["hp"] < battlefield.troupes[uid].hp:
                    battlefield.troupes[uid].hp = data["hp"]

                if battlefield.troupes[uid].line_of_sight == 0:
                    if (battlefield.troupes[uid].position[0] != data["x"]
                            or battlefield.troupes[uid].position[1] != data["y"]):
                        battlefield.troupes[uid].position = (data["x"], data["y"])
