import math
from iastrategy.Strategy import Strategy
from Constant import EPSILON, UNIT_RADIUS


class SmartElevation(Strategy):
    """
    SmartElevation Strategy:
    - Sans ennemi : toutes les unités cherchent la meilleure élévation sur la map.
    - Pikemen tiennent le centre comme bouclier défensif.
    - Knights/Crossbowmen grimpent vers le point le plus haut accessible.
    - Si un élite est attaqué → mode assaut forcé sur tous.
    - Passe en mode agressif après une longue inactivité ou assaut forcé.
    """

    # Nombre de positions candidates à évaluer pour trouver le meilleur sommet
    ELEVATION_CANDIDATES = 20

    def __init__(self):
        super().__init__()
        self.idle_frames = 0
        self.forced_assault = False

        # Position haute trouvée pour les élites (calculée une seule fois)
        self._best_high_pos = None
        # Position centrale pour les Pikemen
        self._center_pos = None

    def __repr__(self):
        return "SmartElevation"

    # ------------------------------------------------------------------
    # RECHERCHE DU MEILLEUR POINT EN HAUTEUR
    # ------------------------------------------------------------------
    def _find_best_elevation_pos(self, battlefield):
        """
        Cherche la position avec la plus haute élévation sur la map.
        Échantillonne une grille de positions et retourne la meilleure.
        """
        if not battlefield.heightmap:
            # Pas de heightmap → on reste au bord le plus proche du spawn
            return None

        best_pos = None
        best_h = -math.inf

        steps = self.ELEVATION_CANDIDATES
        x_step = battlefield.width / steps
        y_step = battlefield.height / steps

        for xi in range(steps):
            for yi in range(steps):
                x = xi * x_step
                y = yi * y_step
                h = battlefield.get_height(x, y)
                if h > best_h:
                    best_h = h
                    best_pos = (x, y)

        return best_pos

    def _find_best_elevation_pos_near(self, unit, battlefield, radius=15):
        """
        Cherche la meilleure élévation dans un rayon autour de l'unité.
        Utilisé pour que chaque unité cherche localement si le sommet global
        est trop loin.
        """
        if not battlefield.heightmap:
            return None

        ux, uy = unit.position
        best_pos = None
        best_h = -math.inf

        for angle in range(0, 360, 20):
            for r in [radius * 0.25, radius * 0.5, radius * 0.75, radius]:
                rad = math.radians(angle)
                x = ux + math.cos(rad) * r
                y = uy + math.sin(rad) * r
                if not battlefield.is_valid_position((x, y)):
                    continue
                h = battlefield.get_height(x, y)
                if h > best_h:
                    best_h = h
                    best_pos = (x, y)

        return best_pos if best_pos else unit.position

    # ------------------------------------------------------------------
    # LOGIQUE PRINCIPALE
    # ------------------------------------------------------------------
    def play(self, general, battlefield):
        my_units = [u for u in general.get_my_units(battlefield) if u.is_alive()]
        if not my_units:
            return

        # 1. INITIALISATION DES POSITIONS CIBLES (une seule fois)
        if self._best_high_pos is None:
            self._best_high_pos = self._find_best_elevation_pos(battlefield)
            # Si pas de heightmap, fallback sur le bord de spawn
            if self._best_high_pos is None:
                avg_x = sum(u.position[0] for u in my_units) / len(my_units)
                edge_x = 0.0 if avg_x < battlefield.width / 2 else battlefield.width - 0.5
                self._best_high_pos = (edge_x, battlefield.height / 2)

            self._center_pos = (battlefield.width / 2, battlefield.height / 2)

        # 2. GESTION DU MODE AGRESSIF
        if not self.forced_assault:
            for u in my_units:
                if u.name in ["Knight", "Crossbowman"]:
                    attacker = getattr(u, "last_attacker", None)
                    if attacker and attacker.is_alive():
                        self.forced_assault = True
                        print("[SmartElevation] Assaut forcé activé !")
                        break

        any_attacking = any(u.current_order == "attack" for u in my_units)
        self.idle_frames = 0 if any_attacking else self.idle_frames + 1
        aggressive_mode = (self.idle_frames > 1500) or self.forced_assault

        # 3. LOGIQUE PAR UNITÉ
        for unit in my_units:
            target = self._find_nearest_enemy(unit, battlefield)

            # ── PAS D'ENNEMI : chercher la meilleure élévation ──────────
            if not target:
                if unit.name == "Pikeman":
                    # Pikemen vont au centre
                    unit.set_order("move", target_pos=self._center_pos)
                else:
                    # Élites vont au sommet global
                    # Si l'unité est déjà proche du sommet, affiner localement
                    dist_to_summit = math.hypot(
                        unit.position[0] - self._best_high_pos[0],
                        unit.position[1] - self._best_high_pos[1]
                    )
                    if dist_to_summit < 5:
                        # Affiner : chercher le meilleur point tout proche
                        local_best = self._find_best_elevation_pos_near(unit, battlefield, radius=10)
                        unit.set_order("move", target_pos=local_best)
                    else:
                        unit.set_order("move", target_pos=self._best_high_pos)
                continue

            # ── ENNEMI PRÉSENT ───────────────────────────────────────────
            dist_to_target = unit.distance_to(target)
            contact_range = unit.range + UNIT_RADIUS * 2 + EPSILON

            # --- PIKEMAN : fonce sur l'ennemi ---
            if unit.name == "Pikeman":
                if dist_to_target <= contact_range:
                    unit.set_order("attack", target=target)
                else:
                    unit.set_order("move", target_pos=target.position)
                continue

            # --- ÉLITES : Knights & Crossbowmen ---
            if aggressive_mode:
                if unit.type_attack == "Melee":
                    # Knight : charge
                    if dist_to_target <= contact_range:
                        unit.set_order("attack", target=target)
                    else:
                        unit.set_order("move", target_pos=target.position)
                else:
                    # Crossbowman : tire si à portée, sinon avance
                    enemies = [e for e in battlefield.get_enemy_units(unit) if e.is_alive()]
                    in_range = [e for e in enemies if unit.distance_to(e) <= contact_range]
                    if in_range:
                        best = min(in_range, key=lambda e: e.hp)
                        unit.set_order("attack", target=best)
                    elif enemies:
                        nearest = min(enemies, key=lambda e: unit.distance_to(e))
                        unit.set_order("move", target_pos=nearest.position)
            else:
                # Pas encore agressif : grimper vers le sommet
                unit.set_order("move", target_pos=self._best_high_pos)
