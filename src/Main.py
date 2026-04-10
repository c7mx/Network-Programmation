from Constant import ROWS, COLS, VIEW_ELEVATION
from util.ScenarioMaker import ScenarioMaker
from model.Battlefield import Battlefield
from model.Battle import Battle
from model.BattleMulti import BattleMulti
from view.GUI import GUI
from view.Console import Console
from util.Functions import parse_units_list, parse_range, get_scenario, create_parser, generate_heightmap
#import subprocess

if __name__ == '__main__':
    subprocess.Popen(["./network/comm_c_c"])
    parser = create_parser()
    args = parser.parse_args()

    if args.command == 'run':
        print(f"Running battle between {args.AI1} and {args.AI2}")

        scenario_maker = ScenarioMaker(get_scenario(), args.AI1, args.AI2)
        data = scenario_maker.get_data()

        general1 = data.get("general1")
        general2 = data.get("general2")
        all_units = data.get("all_units")


        battlefield = Battlefield(COLS, ROWS, all_units, generate_heightmap(COLS, ROWS))

        if args.terminal:
            view = Console(battlefield)
        else:
            view = GUI(battlefield, [general1, general2], VIEW_ELEVATION)

        if args.datafile:
            battle = Battle(general1, general2, battlefield, view, args.datafile)
        else:
            battle = Battle(general1, general2, battlefield, view)

        if args.plot:
            battle.collectStats = True

        battle.start()

    if args.command == 'multi':
        print(f"Bataille avec l'IA {args.AI1}")

        scenario_maker = ScenarioMaker(get_scenario(), args.AI1)
        data = scenario_maker.get_data()

        general1 = data.get("general1")
        all_units = data.get("all_units")


        battlefield = Battlefield(COLS, ROWS, all_units, generate_heightmap(COLS, ROWS))

        if args.terminal:
            view = Console(battlefield)
        else:
            view = GUI(battlefield, [general1], VIEW_ELEVATION)

        if args.datafile:
            battle = BattleMulti(general1, battlefield, view, args.datafile)
        else:
            battle = BattleMulti(general1, battlefield, view)

        if args.plot:
            battle.collectStats = True

        battle.start()
