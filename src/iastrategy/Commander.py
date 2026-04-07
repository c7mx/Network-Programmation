import math
from typing import List, Tuple, Optional, Dict
from iastrategy.Strategy import Strategy
from Constant import EPSILON, UNIT_RADIUS


class Commander(Strategy):
    """
    AGGRESSIVE STRATEGY WITH SCORING TARGETING
    
    PHILOSOPHY: "Controlled aggression"
    - Immediate engagement if enemy detected
    - Ultra-fast training (1 frame)
    - Intelligent targeting by scoring
    - Dynamic adaptation (ENGAGED/SCRAMBLE)
    - STRICT ADHERENCE TO ATTACK RANGES
    """

    def __init__(self, name: str = "Commander"):
        self.name = name
        self.frame = 0
        self.formation_set = False
        self.formation_complete_frame = -1
        
        # Tactical status
        self.mode = "FORMATION"  # FORMATION / ENGAGED / SCRAMBLE
        
        # Tactical settings
        self.params = {
            # Training (ultra-fast)
            "formation_spacing": 1.5,
            "formation_wait_frames": 1,  # 1 frame seulement !
            
            # SCRAMBLE thresholds
            "scramble_enemy_distance": 12.0,
            "scramble_loss_rate": 0.25,
            
            # Targeting scoring
            "max_target_range": 40.0,
            "hp_weight": 1.5,
            "distance_weight": 2.0,
            "threat_weight": 4.0,
            "threat_radius": 6.0,
            "finish_kill_bonus": 150.0,
            "finish_kill_hp": 35,
            
            # Bonus by type
            "type_bonus": {
                "Pikeman": {"Knight": 60, "Pikeman": 15, "Crossbowman": 5},
                "Crossbowman": {"Pikeman": 60, "Crossbowman": 15, "Knight": 5},
                "Knight": {"Crossbowman": 60, "Knight": 15, "Pikeman": 5}
            },
            
            # Anti-flight
            "suicide_threshold": 200,
            
            # Melee contact
            "melee_contact_bonus": 80.0,
        }
        
        self.last_combat_frame = 0
        self.initial_unit_count = 0

    def __repr__(self):
        return "Commander"

    # =================================================================
    # UTILITIES
    # =================================================================

    def _get_unit_type(self, unit) -> str:
        """Returns the exact type of the unit"""
        return getattr(unit, "name", "unknown")

    def _get_group_center(self, units: List) -> Tuple[float, float]:
        """Calculates the centre of mass of a group of units."""
        if not units:
            return (0.0, 0.0)
        total_x = sum(u.position[0] for u in units)
        total_y = sum(u.position[1] for u in units)
        return (total_x / len(units), total_y / len(units))

    def _distance_to_point(self, unit, point: Tuple[float, float]) -> float:
        """Calculates the distance between a unit and a point."""
        ux, uy = unit.position
        px, py = point
        return math.hypot(ux - px, uy - py)

    def _is_in_attack_range(self, attacker, target) -> bool:
        """
        Checks whether a target is within attack range.
        CRITICISM: Respects the true ranges of units.
        """
        dist = attacker.distance_to(target)
        
        contact_range = attacker.range + UNIT_RADIUS * 2
        return dist <= contact_range + EPSILON
        
     
    # =================================================================
    # IMPROVED SCORING SYSTEM
    # =================================================================

    def _calculate_target_score(self, attacker, target, unit_type: str) -> float:
        """
        Calculates a priority score for a target.
        THE HIGHER THE SCORE, THE HIGHER THE PRIORITY OF THE TARGET.
        """
        # Distance
        dist = attacker.distance_to(target)
        
        # 1️⃣ HP SCORE: The weaker the enemy, the better the score.
        max_hp = getattr(target, 'max_hp', 100)
        hp_ratio = target.hp / max_hp if max_hp > 0 else 0
        hp_score = (1 - hp_ratio) * 100 * self.params["hp_weight"]
        
        # 2️⃣ SCORE DISTANCE: The closer it is, the MUCH better the score
        max_range = self.params["max_target_range"]
        distance_ratio = min(dist / max_range, 1.0)
        distance_score = (1 - distance_ratio**0.5) * 100 * self.params["distance_weight"]
        
        # 3️⃣ EMERGENCY SCORE: Enemy within threat range = MASSIVE BONUS
        threat_radius = self.params["threat_radius"]
        if dist <= threat_radius:
            threat_score = ((threat_radius - dist) / threat_radius) * 100 * self.params["threat_weight"]
        else:
            threat_score = 0
        
        # 4️⃣ BONUS TYPE: Strategic bonus depending on the matchup
        target_type = self._get_unit_type(target)
        type_bonuses = self.params["type_bonus"].get(unit_type, {})
        type_bonus = type_bonuses.get(target_type, 0)
        
        # 5️⃣ FINISH KILL BONUS: Enemy almost dead = HIGH PRIORITY
        finish_bonus = 0
        if target.hp <= self.params["finish_kill_hp"]:
            finish_bonus = self.params["finish_kill_bonus"]
        
        # 6️⃣ Melee Contact Bonus: For units in close combat
        contact_bonus = 0
        if attacker.type_attack == "Melee":
            contact_range = attacker.range + UNIT_RADIUS * 2
            if dist <= contact_range + EPSILON:
                contact_bonus = self.params["melee_contact_bonus"]
        
        # TOTAL SCORE
        total_score = hp_score + distance_score + threat_score + type_bonus + finish_bonus + contact_bonus
        
        return total_score

    def _get_valid_targets(self, attacker, enemies: List) -> List:
        """
        Filters out enemies to retain only relevant candidates.
        """
        max_range = self.params["max_target_range"]
        valid = []
        
        for enemy in enemies:
            if not enemy.is_alive():
                continue
            
            dist = attacker.distance_to(enemy)
            
            # Garder si dans le rayon max OU déjà ciblé
            if dist <= max_range or getattr(attacker, 'target_unit', None) == enemy:
                valid.append(enemy)
        
        # FALLBACK : Si aucun ennemi dans le rayon, prendre le plus proche
        if not valid and enemies:
            alive_enemies = [e for e in enemies if e.is_alive()]
            if alive_enemies:
                closest = min(alive_enemies, key=lambda e: attacker.distance_to(e))
                valid.append(closest)
        
        return valid

    def _find_best_target(self, attacker, enemies: List, unit_type: str) -> Optional[object]:
        """
        Find the BEST target for the attacker using scoring.
        """
        valid_targets = self._get_valid_targets(attacker, enemies)
        
        if not valid_targets:
            return None
        
        # Calculate the score for each target
        scored_targets = [
            (target, self._calculate_target_score(attacker, target, unit_type))
            for target in valid_targets
        ]
        
        # Sort by descending score and take the best
        scored_targets.sort(key=lambda x: x[1], reverse=True)
        
        return scored_targets[0][0]

    # =================================================================
    # GLOBAL ENGAGEMENT DETECTION
    # =================================================================

    def _any_enemy_in_range(self, my_units: List, enemies: List) -> bool:
        """
        Check if AT LEAST ONE enemy is within attack range of ONE of our units.
        """
        for unit in my_units:
            if not unit.is_alive():
                continue
            for enemy in enemies:
                if not enemy.is_alive():
                    continue
                
                # Use the centralised verification function
                if self._is_in_attack_range(unit, enemy):
                    return True
        return False

    def _any_enemy_close(self, my_units: List, enemies: List, threshold: float = 25.0) -> bool:
        """
        Check if ANY enemy is near OUR units.
        """
        for unit in my_units:
            if not unit.is_alive():
                continue
            for enemy in enemies:
                if not enemy.is_alive():
                    continue
                if unit.distance_to(enemy) <= threshold:
                    return True
        return False

    # =================================================================
    # SCRAMBLE MODE DETECTION
    # =================================================================

    def _should_scramble(self, my_units: List, enemies: List, army_center: Tuple[float, float]) -> bool:
        """
        Check whether we need to switch to SCRAMBLE mode (intelligent panic).
        """
        # Criterion 1: Enemy very close to the centre
        for enemy in enemies:
            if not enemy.is_alive():
                continue
            dist = self._distance_to_point(enemy, army_center)
            if dist < self.params["scramble_enemy_distance"]:
                return True
        
        # Criterion 2: Significant losses
        if self.initial_unit_count > 0:
            current_count = len(my_units)
            loss_rate = 1 - (current_count / self.initial_unit_count)
            if loss_rate > self.params["scramble_loss_rate"]:
                return True
        
        return False

    # =================================================================
    # FORMATION
    # =================================================================

    def setup_simple_formation(self, center: Tuple[float, float], pikemen: List,
                               crossbowmen: List, knights: List):
        """Quick and easy training."""
        cx, cy = center
        spacing = self.params["formation_spacing"]
        assigned_positions = []
        
        sample_unit = pikemen[0] if pikemen else (crossbowmen[0] if crossbowmen else knights[0])
        general_id = sample_unit.id // 1000
        direction = 1 if general_id == 0 else -1

        # PIKEMEN (front)
        for i, pike in enumerate(pikemen):
            x = cx + (i - len(pikemen) / 2) * spacing
            y = cy + direction * 2.0
            pos = self._find_free_position((x, y), assigned_positions, pike.battlefield)
            pike.set_order("move", target_pos=pos)
            assigned_positions.append(pos)

        # CROSSBOWMEN (back)
        for i, crossbow in enumerate(crossbowmen):
            x = cx + (i - len(crossbowmen) / 2) * spacing
            y = cy - direction * 2.0
            pos = self._find_free_position((x, y), assigned_positions, crossbow.battlefield)
            crossbow.set_order("move", target_pos=pos)
            assigned_positions.append(pos)

        # KNIGHTS (flanks)
        mid = len(knights) // 2
        for i, knight in enumerate(knights[:mid]):
            x = cx - 5.0
            y = cy + (i - mid / 2) * spacing
            pos = self._find_free_position((x, y), assigned_positions, knight.battlefield)
            knight.set_order("move", target_pos=pos)
            assigned_positions.append(pos)

        for i, knight in enumerate(knights[mid:]):
            x = cx + 5.0
            y = cy + (i - (len(knights) - mid) / 2) * spacing
            pos = self._find_free_position((x, y), assigned_positions, knight.battlefield)
            knight.set_order("move", target_pos=pos)
            assigned_positions.append(pos)

    def _find_free_position(self, target_pos: Tuple[float, float], 
                           assigned_positions: List, battlefield) -> Tuple[float, float]:
        """Trouve une position libre proche de la position cible."""
        if not assigned_positions:
            return target_pos
        
        # If the position is available, use it.
        min_dist = min(math.hypot(target_pos[0] - p[0], target_pos[1] - p[1]) 
                      for p in assigned_positions)
        if min_dist > 0.5:
            return target_pos
        
        # Otherwise, look around
        for offset in [(0.5, 0), (-0.5, 0), (0, 0.5), (0, -0.5)]:
            new_pos = (target_pos[0] + offset[0], target_pos[1] + offset[1])
            min_dist = min(math.hypot(new_pos[0] - p[0], new_pos[1] - p[1]) 
                          for p in assigned_positions)
            if min_dist > 0.5:
                return new_pos
        
        return target_pos

    # =================================================================
    # BEHAVIOUR BY MODE
    # =================================================================

    def _control_unit(self, unit, enemies: List):
        """
        Universal control of a unit with scoring targeting.
        ✅ STRICTLY RESPECT THE RANGES OF ATTACK.
        """
        unit_type = self._get_unit_type(unit)
        best_target = self._find_best_target(unit, enemies, unit_type)
        
        if not best_target:
            return
        
        # ✅ STRICT SCOPE VERIFICATION
        if self._is_in_attack_range(unit, best_target):
            # ✅ IN RANGE → Attack
            unit.set_order("attack", target=best_target)
        else:
            # ❌ OUT OF RANGE → Move towards the target
            tx, ty = best_target.position
            unit.set_order("move", target_pos=(tx, ty))
            # Memorise the target for continuity
            unit.target_unit = best_target

    # =================================================================
    # ANTI-FLIGHT
    # =================================================================

    def _check_combat_activity(self, my_units: List) -> bool:
        """Check if at least one unit is in combat."""
        for unit in my_units:
            if unit.current_order == "attack" and unit.target_unit:
                return True
        return False

    def _force_suicide_attack(self, my_units: List):
        """Force all units to charge."""
        for unit in my_units:
            if not unit.is_alive():
                continue
            closest = self._find_nearest_enemy(unit, unit.battlefield)
            if closest:
                # In suicide mode, you force yourself to move towards the enemy.
                # The attack will be launched by _control_unit when within range.
                tx, ty = closest.position
                unit.set_order("move", target_pos=(tx, ty))
                unit.target_unit = closest

    def _find_nearest_enemy(self, unit, battlefield):
        """Find the nearest enemy."""
        enemies = battlefield.get_enemy_units(unit)
        if not enemies:
            return None
        
        alive_enemies = [e for e in enemies if e.is_alive()]
        if not alive_enemies:
            return None
        
        return min(alive_enemies, key=lambda e: unit.distance_to(e))

    # =================================================================
    # MAIN LOOP
    # =================================================================

    def play(self, general, battlefield):
        """Main loop with immediate engagement."""
        self.frame += 1

        my_units = general.get_my_units(battlefield)
        if not my_units:
            return

        # Reset counter
        if self.initial_unit_count == 0:
            self.initial_unit_count = len(my_units)

        enemies = battlefield.get_enemy_units(my_units[0]) if my_units else []
        if not enemies:
            return

        # Classify by type
        pikemen = [u for u in my_units if self._get_unit_type(u) == "Pikeman"]
        crossbowmen = [u for u in my_units if self._get_unit_type(u) == "Crossbowman"]
        knights = [u for u in my_units if self._get_unit_type(u) == "Knight"]

        # ========== PHASE 1: TRAINING ==========
        if not self.formation_set:
            center = self._get_group_center(my_units)
            self.setup_simple_formation(center, pikemen, crossbowmen, knights)
            self.formation_set = True
            self.formation_complete_frame = self.frame
            self.mode = "FORMATION"
            return

        # ========== PHASE 2: IMMEDIATE ENGAGEMENT IF ENEMY IS NEAR ==========
        enemy_close = self._any_enemy_close(my_units, enemies, threshold=25.0)
        enemy_in_range = self._any_enemy_in_range(my_units, enemies)
        
        if enemy_close or enemy_in_range:
            self.mode = "ENGAGED"
        elif self.frame - self.formation_complete_frame < self.params["formation_wait_frames"]:
            return

        # ========== PHASE 3: MODE DETECTION ==========
        army_center = self._get_group_center(my_units)
        
        if self._should_scramble(my_units, enemies, army_center):
            self.mode = "SCRAMBLE"
        elif self.mode != "ENGAGED":
            self.mode = "ENGAGED"

        # ========== PHASE 4 : ANTI-FLIGHT ==========
        combat_detected = self._check_combat_activity(my_units)
        if combat_detected:
            self.last_combat_frame = self.frame
        
        frames_without_combat = self.frame - self.last_combat_frame
        if frames_without_combat > self.params["suicide_threshold"]:
            self._force_suicide_attack(my_units)
            return

        # ========== PHASE 5 : EXECUTION WITH SCORING ==========
        for unit in my_units:
            if not unit.is_alive():
                continue
            
            # Check whether the unit already has an assigned target (attack OR movement)
            if unit.target_unit and unit.target_unit.is_alive():
                # Case 1: The unit is already attacking AND the target is still within range
                if unit.current_order == "attack" and self._is_in_attack_range(unit, unit.target_unit):
                    continue  # ✅ Maintenir l'attaque en cours
                
                # Case 2: The unit moves towards a target AND the target is now within range
                elif unit.current_order == "move" and self._is_in_attack_range(unit, unit.target_unit):
                    # ✅ Switch to attack mode!
                    unit.set_order("attack", target=unit.target_unit)
                    continue
                
                # Case 3: The unit moves AND the target is still out of range
                elif unit.current_order == "move" and not self._is_in_attack_range(unit, unit.target_unit):
                    continue  # ✅ Continuer le mouvement
            
            # If none of the above apply: find a new target
            self._control_unit(unit, enemies)

    @staticmethod
    def create():
        """Factory method to create an instance of the policy."""
        return Commander()
#{"Crossbowman":10, "Pikeman":10,"Knight":10,"startLine":55,"startCol":50,"armyDistance":30, "unitPerCol":5}
