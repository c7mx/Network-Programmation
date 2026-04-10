from math import ceil
from model.General import General
from util.UnitsFactory import UnitsFactory
from util.Functions import create_strategy

class ScenarioMaker4:
    def __init__(self, scenario, ia1Name, ia2Name=None ,ia3Name=None, ia4Name=None):
        self.scenario = scenario
        self.ia1Name = ia1Name
        self.ia2Name = ia2Name
        self.ia3Name = ia3Name
        self.ia4Name = ia4Name

        self.units_factory = UnitsFactory()
        self.all_units = {}
        self.positions1 = {}
        self.positions2 = {}
        self.positions3 = {}
        self.positions4 = {}

        self.create_positions()
        self.create_units()
        self.general1, self.general2 ,self.general3 , self.general4= self.create_generals()

    def create_positions(self):
        start_line = self.scenario["startLine"]
        start_col = self.scenario["startCol"]
        unit_per_col = self.scenario["unitPerCol"]
        army_distance = self.scenario["armyDistance"]

        # Order of units (from rear to front)
        # Army 1 will have its Knights at the front (to the right of its block).
        # Army 2 will have its Knights at the front (to the left of its block).
        unit_order = ["Crossbowman", "Pikeman", "Knight"]

        self.positions1 = {}
        self.positions2 = {}
        self.positions3 = {}
        self.positions4 = {}

        # =========================================================
        # 1. CALCULATING THE WIDTH OF THE ARMY 1
        # =========================================================
        total_cols_army1 = 0
        for unit_type in unit_order:
            nb = self.scenario.get(unit_type, 0)
            if nb > 0:
                total_cols_army1 += ceil(nb / unit_per_col)

        # =========================================================
        # 2. ARMED POSITION 1 (Towards the right)
        # =========================================================
        current_col_1 = start_col
        for unit_type in unit_order:
            nb_units = self.scenario.get(unit_type, 0)
            if nb_units <= 0: continue
            
            self.positions1[unit_type] = []
            nb_cols = ceil(nb_units / unit_per_col)
            unit_idx = 0
            
            for c in range(nb_cols):
                col = current_col_1 + c
                for r in range(unit_per_col):
                    if unit_idx < nb_units:
                        self.positions1[unit_type].append((start_line + r, col))
                        unit_idx += 1
            current_col_1 += nb_cols

        # =========================================================
        # 3. ARMED POSITION 2 (Mirror, to the right)
        # =========================================================
        # The starting point is: beginning of army 1 + its width + the empty space
        if self.ia2Name:
            start_col_army2 = start_col + total_cols_army1 + army_distance
            
            # For the mirror effect, army 2 must have its front on the LEFT of its block.
            # We therefore reverse the order of placement (Knight first to face Knight 1).
            mirror_order = list(reversed(unit_order)) 
            
            current_col_2 = start_col_army2
            for unit_type in mirror_order:
                nb_units = self.scenario.get(unit_type, 0)
                if nb_units <= 0: continue
                
                self.positions2[unit_type] = []
                nb_cols = ceil(nb_units / unit_per_col)
                unit_idx = 0
                
                for c in range(nb_cols):
                    # We are expanding to the right (+c)
                    col = current_col_2 + c
                    for r in range(unit_per_col):
                        if unit_idx < nb_units:
                            self.positions2[unit_type].append((start_line + r, col))
                            unit_idx += 1
                current_col_2 += nb_cols



        if self.ia3Name:
            start_col_army3 = start_col + total_cols_army1 + 2*army_distance
            
            # For the mirror effect, army 2 must have its front on the LEFT of its block.
            # We therefore reverse the order of placement (Knight first to face Knight 1).
            mirror_order = list(reversed(unit_order)) 
            
            current_col_3 = start_col_army3
            for unit_type in mirror_order:
                nb_units = self.scenario.get(unit_type, 0)
                if nb_units <= 0: continue
                
                self.positions3[unit_type] = []
                nb_cols = ceil(nb_units / unit_per_col)
                unit_idx = 0
                
                for c in range(nb_cols):
                    # We are expanding to the right (+c)
                    col = current_col_3 + c
                    for r in range(unit_per_col):
                        if unit_idx < nb_units:
                            self.positions3[unit_type].append((start_line + r, col))
                            unit_idx += 1
                current_col_3 += nb_cols
            
        if self.ia4Name:
            start_col_army4 = start_col + total_cols_army1 + 3*army_distance
            
            # For the mirror effect, army 2 must have its front on the LEFT of its block.
            # We therefore reverse the order of placement (Knight first to face Knight 1).
            mirror_order = list(reversed(unit_order)) 
            
            current_col_4 = start_col_army4
            for unit_type in mirror_order:
                nb_units = self.scenario.get(unit_type, 0)
                if nb_units <= 0: continue
                
                self.positions4[unit_type] = []
                nb_cols = ceil(nb_units / unit_per_col)
                unit_idx = 0
                
                for c in range(nb_cols):
                    # We are expanding to the right (+c)
                    col = current_col_4 + c
                    for r in range(unit_per_col):
                        if unit_idx < nb_units:
                            self.positions4[unit_type].append((start_line + r, col))
                            unit_idx += 1
                current_col_4 += nb_cols

    def create_units(self):
        # Using a set to avoid duplicate technical keys
        unit_keys = ["Crossbowman", "Pikeman", "Knight"]
        unit_id = 0

        for unit_type in unit_keys:
            # Army 1
            for pos in self.positions1.get(unit_type, []):
                u1 = self.units_factory.create_unit(unit_id, unit_type)
                u1.position = pos
                self.all_units[unit_id] = u1
                unit_id += 1

            # Army 2 (An ID offset is used for clarity.)
            for pos in self.positions2.get(unit_type, []):
                id_2 = unit_id + 1000
                u2 = self.units_factory.create_unit(id_2, unit_type)
                u2.position = pos
                self.all_units[id_2] = u2
                unit_id += 1

            for pos in self.positions3.get(unit_type, []):
                id_3 = unit_id + 2000
                u3 = self.units_factory.create_unit(id_3, unit_type)
                u3.position = pos
                self.all_units[id_3] = u3
                unit_id += 1

            for pos in self.positions4.get(unit_type, []):
                id_4 = unit_id + 3000
                u4 = self.units_factory.create_unit(id_4, unit_type)
                u4.position = pos
                self.all_units[id_4] = u4
                unit_id += 1

    def create_generals(self):
        strat1 = create_strategy(self.ia1Name)
        general1 = General("General1", 1, strat1)

        general2 = None
        if self.ia2Name:
            strat2 = create_strategy(self.ia2Name)
            general2 = General("General2", 2, strat2)
        general3 = None
        if self.ia3Name:
            strat3 = create_strategy(self.ia3Name)
            general3 = General("General3", 3, strat3)

        general4 = None
        if self.ia4Name:
            strat4 = create_strategy(self.ia4Name)
            general4 = General("General4", 4, strat4)

        return general1, general2 , general3 , general4

    def get_data(self):
        return {"general1": self.general1, "general2": self.general2,"general3": self.general3,"general4": self.general4, "all_units": self.all_units}
