from Constant import ROWS, COLS, VIEW_ELEVATION
from util.ScenarioMaker import ScenarioMaker
from util.ScenarioMaker4 import ScenarioMaker4
from model.Battlefield import Battlefield
from model.Battle4 import Battle4
from model.BattleMulti import BattleMulti
from view.GUI import GUI
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

    if args.command == 'run4':
        print(f"Running battle between {args.AI1}, {args.AI2}, {args.AI3}, {args.AI4}")

        scenario_maker = ScenarioMaker4(
            get_scenario(),
            args.AI1,
            args.AI2,
            args.AI3,
            args.AI4,
            player_id="0"
        )
        data = scenario_maker.get_data()

        generals, all_units = extract_generals(data, 4)
        battlefield, view = setup_environment(args, generals, all_units)

        battle = Battle4(*generals, battlefield, view)
    
    elif args.command == 'multi':
        print(f"Battle with {args.AI}, Player ID: {args.player_id}")

        scenario_maker = ScenarioMaker(
            get_scenario(),
            args.AI,
            player_id=args.player_id
        )
        data = scenario_maker.get_data()

        generals, all_units = extract_generals(data, 1)
        battlefield, view = setup_environment(args, generals, all_units)

        battle = BattleMulti(*generals, battlefield, view, args.player_id)

    battle.start()
