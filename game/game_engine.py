import pygame

from game.maze import generate_maze, CELL
from game.entities import Player, Enemy


COLS, ROWS = 13, 11

WIDTH = COLS * CELL
HEIGHT = ROWS * CELL + 50

FPS = 60


class GameEngine:

    def __init__(self):

        pygame.init()

        self.screen = pygame.display.set_mode(
            (WIDTH, HEIGHT)
        )

        pygame.display.set_caption(
            "Maze Chase"
        )

        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont(
            "monospace",
            18
        )

        self.big_font = pygame.font.SysFont(
            "monospace",
            38,
            bold=True
        )

        self.reset()

    def reset(self):

        self.walls = generate_maze(
            COLS,
            ROWS
        )

        # -----------------------------------------
        # Player
        # -----------------------------------------

        self.player = Player(0, 0)

        # -----------------------------------------
        # Three enemies
        # -----------------------------------------

        self.enemies = [
            Enemy(ROWS - 1, COLS - 1),
            Enemy(ROWS - 1, 0),
            Enemy(0, COLS - 1)
        ]

        # -----------------------------------------
        # Exit
        # -----------------------------------------

        self.exit_rect = pygame.Rect(
            (COLS // 2) * CELL + 5,
            (ROWS // 2) * CELL + 5,
            CELL - 10,
            CELL - 10
        )

        # -----------------------------------------
        # POWER PELLET
        # -----------------------------------------
        #
        # IMPORTANT:
        # Put it somewhere different from EXIT.
        #
        # This is row 5, column 2.
        #

        pellet_row = 5
        pellet_col = 2

        self.pellet_rect = pygame.Rect(
            pellet_col * CELL + CELL // 2 - 8,
            pellet_row * CELL + CELL // 2 - 8,
            16,
            16
        )

        self.pellet_active = True

        # 300-frame freeze timer
        self.freeze_timer = 0

        # -----------------------------------------
        # Game state
        # -----------------------------------------

        self.caught = False
        self.won = False

        # -----------------------------------------
        # Difficulty ramp
        # -----------------------------------------

        self.start_time = pygame.time.get_ticks()

        self.speed_tier = 1

        self.enemy_move_interval = 20

    def handle_events(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_r:
                    self.reset()

        return True

    # =================================================
    # DIFFICULTY RAMP
    # =================================================

    def update_difficulty(self):

        elapsed_time = (
            pygame.time.get_ticks()
            - self.start_time
        )

        # Every 15 seconds
        elapsed_periods = elapsed_time // 15000

        # Reduce by 2 every 15 seconds.
        # Minimum = 5.
        new_interval = max(
            5,
            20 - elapsed_periods * 2
        )

        new_speed_tier = (
            (20 - new_interval) // 2
        ) + 1

        if new_interval != self.enemy_move_interval:

            self.enemy_move_interval = new_interval

            self.speed_tier = new_speed_tier

            for enemy in self.enemies:

                enemy.move_interval = (
                    self.enemy_move_interval
                )

    # =================================================
    # POWER PELLET
    # =================================================

    def update_power_pellet(self):

        # -----------------------------------------
        # Player collects pellet
        # -----------------------------------------

        if (
            self.pellet_active
            and self.player.rect.colliderect(
                self.pellet_rect
            )
        ):

            print("POWER PELLET COLLECTED!")

            # Remove pellet
            self.pellet_active = False

            # Start 300-frame countdown
            self.freeze_timer = 300

            # Freeze ALL enemies
            for enemy in self.enemies:

                enemy.frozen = True

        # -----------------------------------------
        # Freeze countdown
        # -----------------------------------------

        if self.freeze_timer > 0:

            self.freeze_timer -= 1

            # Countdown finished
            if self.freeze_timer <= 0:

                self.freeze_timer = 0

                for enemy in self.enemies:

                    enemy.frozen = False

                print("ENEMIES UNFROZEN!")

    # =================================================
    # UPDATE
    # =================================================

    def update(self):

        if self.caught or self.won:
            return

        # Difficulty
        self.update_difficulty()

        # -----------------------------------------
        # Player
        # -----------------------------------------

        keys = pygame.key.get_pressed()

        self.player.move(
            keys,
            self.walls,
            ROWS,
            COLS
        )

        # -----------------------------------------
        # Power pellet
        # -----------------------------------------

        self.update_power_pellet()

        # -----------------------------------------
        # Enemies
        # -----------------------------------------

        for enemy in self.enemies:

            enemy.update(
                self.walls,
                self.player,
                ROWS,
                COLS
            )

            # Frozen enemies cannot catch player
            if (
                not enemy.frozen
                and self.player.rect.colliderect(
                    enemy.rect
                )
            ):

                self.caught = True

        # -----------------------------------------
        # Exit
        # -----------------------------------------

        if self.player.rect.colliderect(
            self.exit_rect
        ):

            self.won = True

    # =================================================
    # DRAW
    # =================================================

    def draw(self):

        self.screen.fill(
            (230, 220, 210)
        )

        wall_color = (50, 40, 60)

        # -----------------------------------------
        # Maze
        # -----------------------------------------

        for r in range(ROWS):

            for c in range(COLS):

                x = c * CELL
                y = r * CELL

                w = self.walls[r][c]

                if w[0]:

                    pygame.draw.line(
                        self.screen,
                        wall_color,
                        (x, y),
                        (x + CELL, y),
                        3
                    )

                if w[1]:

                    pygame.draw.line(
                        self.screen,
                        wall_color,
                        (x, y + CELL),
                        (x + CELL, y + CELL),
                        3
                    )

                if w[2]:

                    pygame.draw.line(
                        self.screen,
                        wall_color,
                        (x + CELL, y),
                        (x + CELL, y + CELL),
                        3
                    )

                if w[3]:

                    pygame.draw.line(
                        self.screen,
                        wall_color,
                        (x, y),
                        (x, y + CELL),
                        3
                    )

        # -----------------------------------------
        # EXIT
        # -----------------------------------------

        pygame.draw.rect(
            self.screen,
            (80, 200, 80),
            self.exit_rect,
            border_radius=4
        )

        exit_label = self.font.render(
            "EXIT",
            True,
            (20, 80, 20)
        )

        self.screen.blit(
            exit_label,
            (
                self.exit_rect.x + 2,
                self.exit_rect.y + 6
            )
        )

        # -----------------------------------------
        # POWER PELLET
        # -----------------------------------------

        if self.pellet_active:

            pygame.draw.circle(
                self.screen,
                (255, 220, 0),
                self.pellet_rect.center,
                8
            )

        # -----------------------------------------
        # PLAYER
        # -----------------------------------------

        self.player.draw(
            self.screen
        )

        # -----------------------------------------
        # ENEMIES
        # -----------------------------------------

        for enemy in self.enemies:

            enemy.draw(
                self.screen
            )

        # -----------------------------------------
        # HUD
        # -----------------------------------------

        hud = pygame.Rect(
            0,
            ROWS * CELL,
            WIDTH,
            50
        )

        pygame.draw.rect(
            self.screen,
            (30, 30, 50),
            hud
        )

        # Speed tier
        speed_text = (
            f"Enemy Speed: Tier "
            f"{self.speed_tier} "
            f"(Interval: "
            f"{self.enemy_move_interval})"
        )

        speed_label = self.font.render(
            speed_text,
            True,
            (255, 220, 100)
        )

        self.screen.blit(
            speed_label,
            (
                8,
                ROWS * CELL + 4
            )
        )

        # Freeze status
        if self.freeze_timer > 0:

            freeze_text = (
                f"FROZEN: "
                f"{self.freeze_timer} frames"
            )

            freeze_label = self.font.render(
                freeze_text,
                True,
                (100, 200, 255)
            )

            self.screen.blit(
                freeze_label,
                (
                    8,
                    ROWS * CELL + 27
                )
            )

        else:

            freeze_label = self.font.render(
                "Power Pellet: Available"
                if self.pellet_active
                else "Power Pellet: Used",
                True,
                (200, 200, 200)
            )

            self.screen.blit(
                freeze_label,
                (
                    8,
                    ROWS * CELL + 27
                )
            )

        # Restart
        restart_label = self.font.render(
            "R = Restart",
            True,
            (200, 200, 200)
        )

        self.screen.blit(
            restart_label,
            (
                WIDTH
                - restart_label.get_width()
                - 8,
                ROWS * CELL + 27
            )
        )

        # -----------------------------------------
        # GAME OVER
        # -----------------------------------------

        if self.caught:

            self._overlay(
                "CAUGHT!",
                (220, 60, 60)
            )

        if self.won:

            self._overlay(
                "ESCAPED!",
                (80, 220, 80)
            )

        pygame.display.flip()

    # =================================================
    # OVERLAY
    # =================================================

    def _overlay(self, text, color):

        surf = pygame.Surface(
            (
                WIDTH,
                ROWS * CELL
            ),
            pygame.SRCALPHA
        )

        surf.fill(
            (0, 0, 0, 140)
        )

        self.screen.blit(
            surf,
            (0, 0)
        )

        msg = self.big_font.render(
            text,
            True,
            color
        )

        sub = self.font.render(
            "Press R to Restart",
            True,
            (200, 200, 200)
        )

        self.screen.blit(
            msg,
            (
                WIDTH // 2
                - msg.get_width() // 2,
                ROWS * CELL // 2 - 30
            )
        )

        self.screen.blit(
            sub,
            (
                WIDTH // 2
                - sub.get_width() // 2,
                ROWS * CELL // 2 + 20
            )
        )

    # =================================================
    # RUN
    # =================================================

    def run(self):

        running = True

        while running:

            running = self.handle_events()

            self.update()

            self.draw()

            self.clock.tick(FPS)

        pygame.quit()
