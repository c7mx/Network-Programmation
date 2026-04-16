import importlib
import os
import argparse
import json
import ast
import random
from Constant import DEFAULT_SCENARIOS, STATS_FILEPATH, REPORTS_FOLDER, ELEVATON_MAX_VALUE
import datetime


def generate_heightmap(width, height, center_size=40, max_elev=ELEVATON_MAX_VALUE):
    """
    Generate a heightmap with a flat central area and increasing elevation
    towards the edges.

    Parameters
    ----------
    width : int
        Width of the map (number of columns)
    height : int
        Height of the map (number of rows)
    center_size : int
        Size of the flat central square (center_size x center_size)
    max_elev : int
        Maximum elevation at the edges

    Returns
    -------
    list[list[int]]
        2D heightmap
    """
    map_data = [[0 for _ in range(width)] for _ in range(height)]

    cx = width // 2
    cy = height // 2
    half_center = center_size // 2

    for y in range(height):
        for x in range(width):
            # Distance from center in "tiles"
            dx = max(0, abs(x - cx) - half_center)
            dy = max(0, abs(y - cy) - half_center)
            dist = max(dx, dy)  # Chebyshev distance for square gradient

            # Compute elevation: normalized distance -> max_elev
            max_dist = max(cx, cy) - half_center
            elev = round((dist / max_dist) * max_elev)

            # Optional: add small random variation
            elev += random.choice([0, 0, 1])  # mostly smooth, rare bumps
            if elev > max_elev:
                elev = max_elev

            map_data[y][x] = elev

    return map_data


def load_heightmap(filepath):
    """
    Load a battlefield heightmap from a JSON file.

    Returns:
        width, height, grid (2D list of ints)
    """
    path = os.path.dirname(__file__)
    with open(os.path.join(path, filepath), 'r') as f:
        data = json.load(f)
    return data["grid"]


def create_parser():
    """
    Create and configure the command-line argument parser.

    This function defines all available commands (`run`, `run4` and `multi`) along with their required and optional arguments.

    Returns
    -------
    argparse.ArgumentParser
        The fully configured parser instance.
    """
    parser = argparse.ArgumentParser(description='AI Battle Simulator')
    subparsers = parser.add_subparsers(dest='command', required=True)

    run_p = subparsers.add_parser('run', help='Run a battle between two AIs')

    run_p.add_argument('AI1', help='First AI name')
    run_p.add_argument('AI2', help='Second AI name')
    run_p.add_argument('-t', '--terminal', action='store_true', help='Display output in terminal')

    run4_p = subparsers.add_parser('run4', help='Run a battle between two AIs')

    run4_p.add_argument('AI1', help='First AI name')
    run4_p.add_argument('AI2', help='Second AI name')
    run4_p.add_argument('AI3', help='Third AI name')
    run4_p.add_argument('AI4', help='Fourth AI name')
    run4_p.add_argument('-t', '--terminal', action='store_true', help='Display output in terminal')

    multi_p = subparsers.add_parser('multi', help='Initialisation of one AI for multi mode')

    multi_p.add_argument('AI1', help='First AI name')
    multi_p.add_argument('-t', '--terminal', action='store_true', help='Display output in terminal')
    multi_p.add_argument('--id_joueur', type=str, required=True, help="ID du joueur")

    return parser


def get_scenario():
    """
    Prompt the user to enter a scenario definition in dictionary form.

    The user must enter a Python dictionary describing the scenario configuration
    (e.g., unit counts, starting distances, line length, etc.).

    Returns
    -------
    dict
        The scenario parameters entered by the user.

    Notes
    -----
    This function uses `eval()` to interpret the user input. Only use in trusted
    environments.
    """
    print("Please enter a scenario")
    print("Format : {\"Crossbowman\":10, \"Pikeman\":10, \"Knight\":10, \"startLine\":55, \"startCol\":50, \"armyDistance\":10, \"unitPerCol\":10}")
    while True:
        raw = input("->").strip()
        if raw.startswith("Format:"):
            raw = raw[len("Format:"):].strip()
        if not raw:
            print("Empty input. Please enter a scenario dict.")
            continue
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            try:
                return ast.literal_eval(raw)
            except (ValueError, SyntaxError):
                print("Invalid format. Please paste a dict or JSON example as shown.")


def parse_units_list(s: str):
    """
    Parse a unit list string into a Python list of unit names.

    Examples
    --------
    "[Knight, Pikeman]" → ["Knight", "Pikeman"]

    Parameters
    ----------
    s : str
        The raw unit list string.

    Returns
    -------
    list[str]
        Cleaned list of unit names.
    """
    s = s.strip()
    if s.startswith("[") and s.endswith("]"):
        s = s[1:-1]

    return [u.strip() for u in s.split(",") if u.strip()]


def parse_range(expr):
    """
    Safely evaluate a range expression from the command line.

    Parameters
    ----------
    expr : str
        A textual Python range expression (e.g. "range(1, 10)").

    Returns
    -------
    range
        The evaluated Python range object.

    Notes
    -----
    Only `range()` is allowed; builtins are disabled for safety.
    """
    return eval(expr, {"__builtins__": None}, {"range": range})


def save_report(html_content: str) -> str:
    """
    Save an HTML snapshot of a battle report.

    The report is stored in the configured reports directory with a timestamped
    filename.

    Parameters
    ----------
    html_content : str
        The HTML content to save.

    Returns
    -------
    str
        The full path to the saved file.
    """
    out_dir = os.path.join(os.getcwd(), REPORTS_FOLDER)
    os.makedirs(out_dir, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = os.path.join(out_dir, f"snapshot_{ts}.html")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    return out_file


def readStatsFromFile(filepath: str):
    """
    Load and parse unit statistics from a CSV file.

    The CSV must contain the following columns:
    Unit, HP, Type_Attack, Attack, Armor, Pierce_Armor, Range,
    Line_of_Sight, Speed, Attack_Delay, Reload_Time, Accuracy

    Parameters
    ----------
    filepath : str
        Path to the CSV file.

    Returns
    -------
    dict[str, dict[str, int|float|str]]
        A dictionary mapping each unit type to its corresponding stats.

    Raises
    ------
    ValueError
        If a CSV row does not contain the expected number of fields.
    """
    stats = {}
    with open(filepath, 'r') as file:
        file.readline()  # Skip the CSV header
        for line in file:
            parts = line.strip().split(',')
            if len(parts) < 12:
                raise ValueError(f"Invalid stats line (expected 12 fields): {line!r}")

            unit_type = parts[0]
            stats[unit_type] = {
                "hp": int(parts[1]),
                "type_Attack": parts[2],
                "attack": int(parts[3]),
                "armor": int(parts[4]),
                "pierce_armor": int(parts[5]),
                "range": float(parts[6]),
                "line_of_sight": int(parts[7]),
                "speed": float(parts[8]),
                "attack_Delay": float(parts[10]),
                "reload_time": float(parts[10]),
                "accuracy": float(parts[11])
            }
    return stats

def get_max_hp(unit_type):
    """
    Retrieve the maximum HP value for a given unit type.

    Parameters
    ----------
    unit_type : str
        Name of the unit type.

    Returns
    -------
    int
        The maximum HP defined in the stats file.
    """
    path = os.path.dirname(__file__)
    stats = readStatsFromFile(os.path.join(path, STATS_FILEPATH))
    return int(stats[unit_type]["hp"])


def create_strategy(name):
    """
    Dynamically load and instantiate a strategy class from the iastrategy module.

    The module `iastrategy.<name>` must exist and contain a class with
    the same name.

    Parameters
    ----------
    name : str
        Strategy class name.

    Returns
    -------
    Strategy
        An instance of the requested strategy.

    Raises
    ------
    ValueError
        If the strategy cannot be found or the import fails.
    """
    try:
        mod = importlib.import_module(f"iastrategy.{name}")
        cls = getattr(mod, name)
        return cls()
    except Exception as e:
        raise ValueError(f"Unknown IA name '{name}' and dynamic import failed: {e}")


def load_scenarios(scenarios_input):
    """
    Convert an input list of scenario identifiers or expressions into scenario definitions.

    Parameters
    ----------
    scenarios_input : list[int | str] or None
        - Integer values refer to indices in DEFAULT_SCENARIOS.
        - String expressions are evaluated if possible.
        - None returns DEFAULT_SCENARIOS.

    Returns
    -------
    list
        A list of scenario definitions, either loaded from defaults or evaluated.

    Notes
    -----
    String evaluation is sandboxed using restricted builtins.
    """

    if not scenarios_input:
        return DEFAULT_SCENARIOS

    scenarios = []
    for s in scenarios_input:
        if(isinstance(s, int)):
            if 1 <= s <= len(DEFAULT_SCENARIOS):
                scenarios.append(DEFAULT_SCENARIOS[s-1])
        elif isinstance(s, str):
            try :
                val = eval(s, {"__builtins__": None}, {})
                scenarios.append(val)
            except Exception:
                scenarios.append(s)
    return scenarios


def elevation_color(elevation: int) -> tuple[int, int, int]:
    """
    Maps an elevation value (0–16) to a realistic terrain color
    using linear interpolation between topographic color bands.
    """

    # Clamp elevation
    e = max(0, min(16, elevation))

    # Elevation → Color stops (topographic style)
    stops = [
        (0,  (30,  90,  30)),    # low ground (dark green)
        (4,  (70, 140,  60)),    # plains
        (8,  (150, 160,  80)),   # hills
        (12, (170, 130, 100)),   # plateau
        (16, (190, 180, 150))    # rocky high ground (beige stone)
    ]

    # Find surrounding stops
    for i in range(len(stops) - 1):
        h0, c0 = stops[i]
        h1, c1 = stops[i + 1]

        if h0 <= e <= h1:
            t = (e - h0) / (h1 - h0)

            return (
                int(c0[0] + (c1[0] - c0[0]) * t),
                int(c0[1] + (c1[1] - c0[1]) * t),
                int(c0[2] + (c1[2] - c0[2]) * t),
            )
    return stops[-1][1]
