from Constant import ROWS, COLS, VIEW_ELEVATION
from util.ScenarioMaker import ScenarioMaker
from util.ScenarioMaker4 import ScenarioMaker4
from model.Battlefield import Battlefield
from model.Battle import Battle
from model.Battle4 import Battle4
from model.BattleMulti import BattleMulti
from view.GUI import GUI
import network.comm_py_c as NetPy
from view.Console import Console
from util.Functions import get_scenario, create_parser, generate_heightmap

if __name__ == '__main__':

    parser = create_parser()
    args = parser.parse_args()

    if args.command == 'run':
        print(f"Running battle between {args.AI1} and {args.AI2}")

        scenario_maker = ScenarioMaker(get_scenario(), args.AI1, args.AI2,id_joueur="0")
        data = scenario_maker.get_data()

        general1 = data.get("general1")
        general2 = data.get("general2")
        all_units = data.get("all_units")


        battlefield = Battlefield(COLS, ROWS, all_units, generate_heightmap(COLS, ROWS))
        sock = NetPy.connect_sock_send()
        for unit in all_units.values():
            NetPy.send_data(sock, unit.id, unit.hp, unit.position[0], unit.position[1], unit.symbol)

        if args.terminal:
            view = Console(battlefield)
        else:
            view = GUI(battlefield, [general1, general2], VIEW_ELEVATION)

        battle = Battle(general1, general2, battlefield, view)

        battle.start()

    if args.command == 'run4':
        print(f"Running battle between {args.AI1} and {args.AI2}")

        scenario_maker = ScenarioMaker4(get_scenario(), args.AI1, args.AI2, args.AI3, args.AI4,id_joueur="0")
        data = scenario_maker.get_data()

        general1 = data.get("general1")
        general2 = data.get("general2")
        general3 = data.get("general3")
        general4 = data.get("general4")
        all_units = data.get("all_units")


        battlefield = Battlefield(COLS, ROWS, all_units, generate_heightmap(COLS, ROWS))

        if args.terminal:
            view = Console(battlefield)
        else:
            view = GUI(battlefield, [general1, general2, general3,general4], VIEW_ELEVATION)

        battle = Battle4(general1, general2, general3 , general4,battlefield, view)

        battle.start()

    if args.command == 'multi':
        print(f"Bataille avec l'IA {args.AI1},Joueur ID: {args.id_joueur}")

        scenario_maker = ScenarioMaker(get_scenario(), args.AI1,id_joueur=args.id_joueur)
        data = scenario_maker.get_data()

        general1 = data.get("general1")
        all_units = data.get("all_units")


        battlefield = Battlefield(COLS, ROWS, all_units, generate_heightmap(COLS, ROWS))

        if args.terminal:
            view = Console(battlefield)
        else:
            view = GUI(battlefield, [general1], VIEW_ELEVATION)

        battle = BattleMulti(general1, battlefield, view,args.id_joueur)


        battle.start()
