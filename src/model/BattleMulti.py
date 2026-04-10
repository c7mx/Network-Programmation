from model.General import General
from view.View import View
from model.Battlefield import Battlefield
from Constant import FPS, PLOTS_FOLDER, HEADLESS_SPEEDUP
from util.Functions import plot
import pygame
from util.Logger import Logger
from .GameSnapshotReporter import GameSnapshotReporter
import webbrowser
from view.Console import Console
from view.GUI import GUI
import time


class BattleMulti:

    def __init__(self, general: General, battlefield: Battlefield, view: View = None, datafile: str = None):
        self.battlefield = battlefield
        self.general = general
        self.winner = None
        self.paused = False
        self.collectStats = False
        self.view = view
        self.logger = None
        self.frame_count = 0

        if datafile:
            self.logger = Logger(datafile)

        self.terminal_view = None
        self._queued_battle = None
        self.should_exit = False

        if self.view and hasattr(self.view, 'clock'):
            self.mode_terminal = False
        elif self.view:
            self.mode_terminal = True

        self.speed = HEADLESS_SPEEDUP if not self.view else 1

    # ===================================================================
    def start(self, is_tourney=False):

        axis_x = []
        axis_y = [[]]
        i = 0

        running = True
        clock = pygame.time.Clock()

        while running:

            # ------------------ Timing ------------------
            if self.view and hasattr(self.view, 'clock'):
                dt = self.view.clock.tick(FPS) / 1000
            elif self.view:
                time.sleep(1.0 / FPS)
                dt = 1.0 / FPS
            else:
                dt = clock.tick(FPS * self.speed) / 1000

            self.frame_count += 1

            # ------------------ Events ------------------
            self.handle_event()

            if self._queued_battle:
                self._apply_loaded_battle(self._queued_battle)
                self._queued_battle = None

            # ------------------ Simulation ------------------
            if not self.paused and self.winner is None:

                for _ in range(self.speed):
                    self.general.play(self.battlefield)

                    if self.logger:
                        self.logger.log_info_from_general(self.general, self.battlefield)

                    self.battlefield.update(dt)

                if self.general.is_defeated(self.battlefield):
                    if self.view is None:
                        running = False

                if self.view:
                    self.view.update()

        return self.winner

    # ===================================================================
    def handle_event(self):

        if not self.view or not hasattr(self.view, 'screen'):
            return

        
        reporter = GameSnapshotReporter(self.general, self.general, self.battlefield)

        keys = pygame.key.get_pressed()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                return True

            elif event.type == pygame.KEYDOWN:

                # ================= SNAPSHOT =================
                if event.key == pygame.K_TAB:
                    print("\nTAB → snapshot + pause")

                    self.paused = True
                    if self.view:
                        self.view.pause = True

                    current_time_info = f"Frame {self.frame_count}"

                    file_path = reporter.generate_snapshot(current_time_info)

                    webbrowser.open(f"file://{file_path}")

                # ================= PAUSE =================
                elif event.key == pygame.K_p:
                    self.paused = not self.paused
                    if self.view:
                        self.view.pause = self.paused
                        self.view.update()

                # ================= QUIT =================
                elif event.key == pygame.K_o:
                    pygame.quit()
                    exit()

                # ================= SWITCH VIEW =================
                elif event.key == pygame.K_F9:
                    if isinstance(self.view, GUI):
                        pygame.display.quit()
                        self.view = Console(self.battlefield)
                    else:
                        pygame.display.quit()
                        self.view = GUI(self.battlefield, [self.general], False)

        # UI toggles
        if keys[pygame.K_F1] and self.view:
            self.view.hide_info_pannel()
        elif keys[pygame.K_F4] and self.view:
            self.view.show_info_pannel()

    # ===================================================================
    def _apply_loaded_battle(self, loaded_battle):
        self.general = loaded_battle.general
        self.battlefield = loaded_battle.battlefield
        self.winner = None
        self.paused = loaded_battle.paused
