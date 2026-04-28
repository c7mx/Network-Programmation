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
    if args.terminal:
        return Console(battlefield)
    return GUI(battlefield, generals, VIEW_ELEVATION)


def create_battlefield(all_units):
    return Battlefield(COLS, ROWS, all_units, generate_heightmap(COLS, ROWS))


def extract_generals(data, count):
    """Extract generals and units from scenario data."""
    generals = [data.get(f"general{i}") for i in range(1, count + 1)]
    all_units = data.get("all_units")
    return generals, all_units


def setup_environment(args, generals, all_units):
    """Create battlefield and view."""
    battlefield = create_battlefield(all_units)
    view = create_view(args, battlefield, generals)
    return battlefield, view




if __name__ == '__main__':

    parser = create_parser()
    args = parser.parse_args()


    if args.command == 'run':
        print(f"Running battle between {args.AI1} and {args.AI2}")

        scenario_maker = ScenarioMaker(
            get_scenario(),
            args.AI1,
            args.AI2,
            id_joueur="0"
        )
        data = scenario_maker.get_data()

        generals, all_units = extract_generals(data, 2)
        battlefield, view = setup_environment(args, generals, all_units)

    
        sock = NetPy.connect_sock_send()
        for unit in all_units.values():
            NetPy.send_data(
                sock,
                unit.id,
                unit.hp,
                unit.position[0],
                unit.position[1],
                unit.symbol
            )

        battle = Battle(*generals, battlefield, view)
        battle.start()

   
    elif args.command == 'run4':
        print(f"Running battle between {args.AI1}, {args.AI2}, {args.AI3}, {args.AI4}")

        scenario_maker = ScenarioMaker4(
            get_scenario(),
            args.AI1,
            args.AI2,
            args.AI3,
            args.AI4,
            id_joueur="0"
        )
        data = scenario_maker.get_data()

        generals, all_units = extract_generals(data, 4)
        battlefield, view = setup_environment(args, generals, all_units)

        battle = Battle4(*generals, battlefield, view)
        battle.start()

    
    elif args.command == 'multi':
        print(f"Bataille avec l'IA {args.AI1}, Joueur ID: {args.id_joueur}")

        scenario_maker = ScenarioMaker(
            get_scenario(),
            args.AI1,
            id_joueur=args.id_joueur
        )
        data = scenario_maker.get_data()

        generals, all_units = extract_generals(data, 1)
        battlefield, view = setup_environment(args, generals, all_units)

        battle = BattleMulti(*generals, battlefield, view, args.id_joueur)
        battle.start()
