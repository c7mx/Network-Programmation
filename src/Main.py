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


def create_view(args, battlefield, generals):
    """Create and return the appropriate view (Console or GUI)."""
    if args.terminal:
        return Console(battlefield)
    return GUI(battlefield, generals, VIEW_ELEVATION)


def create_battlefield(all_units):
    """Create and return a Battlefield with a generated heightmap."""
    return Battlefield(COLS, ROWS, all_units, generate_heightmap(COLS, ROWS))


if __name__ == '__main__':

    parser = create_parser()
    args = parser.parse_args()

    if args.command == 'run':
        print(f"Running battle between {args.AI1} and {args.AI2}")

        scenario_maker = ScenarioMaker(get_scenario(), args.AI1, args.AI2, id_joueur="0")
        data = scenario_maker.get_data()

        general1 = data.get("general1")
        general2 = data.get("general2")
        all_units = data.get("all_units")

        battlefield = create_battlefield(all_units)

        sock = NetPy.connect_sock_send()
        for unit in all_units.values():
            NetPy.send_data(sock, unit.id, unit.hp, unit.position[0], unit.position[1], unit.symbol)

        view = create_view(args, battlefield, [general1, general2])
        battle = Battle(general1, general2, battlefield, view)
        battle.start()

    elif args.command == 'run4':
        print(f"Running battle between {args.AI1} and {args.AI2}")

        scenario_maker = ScenarioMaker4(get_scenario(), args.AI1, args.AI2, args.AI3, args.AI4, id_joueur="0")
        data = scenario_maker.get_data()

        general1 = data.get("general1")
        general2 = data.get("general2")
        general3 = data.get("general3")
        general4 = data.get("general4")
        all_units = data.get("all_units")

        battlefield = create_battlefield(all_units)
        view = create_view(args, battlefield, [general1, general2, general3, general4])
        battle = Battle4(general1, general2, general3, general4, battlefield, view)
        battle.start()

    elif args.command == 'multi':
        print(f"Bataille avec l'IA {args.AI1}, Joueur ID: {args.id_joueur}")

        scenario_maker = ScenarioMaker(get_scenario(), args.AI1, id_joueur=args.id_joueur)
        data = scenario_maker.get_data()

        general1 = data.get("general1")
        all_units = data.get("all_units")

        battlefield = create_battlefield(all_units)
        view = create_view(args, battlefield, [general1])
        battle = BattleMulti(general1, battlefield, view, args.id_joueur)
        battle.start()
