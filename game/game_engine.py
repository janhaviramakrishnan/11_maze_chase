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
        # Power pellet
        # -----------------------------------------

        pellet_row = 5
        pellet_col = 2

        self.pellet_rect = pygame.Rect(
            pellet_col * CELL + CELL // 2 - 8,
            pellet_row * CELL + CELL // 2 - 8,
            16,
            16
        )

        self.pellet_active = True

        # 300-frame freeze countdown
        self.freeze_timer = 0

        # -----------------------------------------
        # Game state
        # -----------------------------------------

        self.caught = False
        self.won = False

        # -----------------------------------------
        # TASK 4: SURVIVAL SCORE
        # -----------------------------------------

        # Score starts at zero.
        # It increases by 1 every frame
        # while the player is alive.
        self.score = 0

        # -----------------------------------------
        # Difficulty ramp
        # -----------------------------------------

        self.start_time = pygame.time.get_ticks()

        self.speed_tier = 1

        self.enemy_move_interval = 20

    # =================================================
    # EVENTS
    # =================================================

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

        # Reduce enemy interval by 2
        # every 15 seconds.
        # Minimum interval is 5.
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

            # Apply new interval to every enemy
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

            # Remove pellet
            self.pellet_active = False

            # Start 300-frame countdown
            self.freeze_timer = 300

            # Freeze all enemies
            for enemy in self.enemies:

                enemy.frozen = True

        # -----------------------------------------
        # Freeze countdown
        # -----------------------------------------

        if self.freeze_timer > 0:

            self.freeze_timer -= 1

            if self.freeze_timer <= 0:

                self.freeze_timer = 0

                # Unfreeze all enemies
                for enemy in self.enemies:

                    enemy.frozen = False

    # =================================================
    # UPDATE
    # =================================================

    def update(self):

        # If game is over, don't update the score.
        if self.caught or self.won:
            return

        # -----------------------------------------
        # TASK 4: SURVIVAL SCORE
        # -----------------------------------------
        #
        # Player is alive at this point,
        # so add one point for this frame.
        #

        self.score += 1

        # -----------------------------------------
        # Difficulty
        # -----------------------------------------

        self.update_difficulty()

        # -----------------------------------------
        # Player movement
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
        # Draw maze
        # -----------------------------------------

        for r in range(ROWS):

            for c in range(COLS):

                x = c * CELL
                y = r * CELL

                w = self.walls[r][c]

                # Top
                if w[0]:

                    pygame.draw.line(
                        self.screen,
                        wall_color,
                        (x, y),
                        (x + CELL, y),
                        3
                    )

                # Bottom
                if w[1]:

                    pygame.draw.line(
                        self.screen,
                        wall_color,
                        (x, y + CELL),
                        (x + CELL, y + CELL),
                        3
                    )

                # Right
                if w[2]:

                    pygame.draw.line(
                        self.screen,
                        wall_color,
                        (x + CELL, y),
                        (x + CELL, y + CELL),
                        3
                    )

                # Left
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

        # -----------------------------------------
        # TASK 4: SURVIVAL TIME
        # -----------------------------------------

        survived_seconds = self.score // 60

        survived_text = (
            f"Survived: "
            f"{survived_seconds}s"
        )

        survived_label = self.font.render(
            survived_text,
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            survived_label,
            (8, ROWS * CELL + 4)
        )

        # -----------------------------------------
        # Enemy speed tier
        # -----------------------------------------

        speed_text = (
            f"Speed: Tier "
            f"{self.speed_tier}"
        )

        speed_label = self.font.render(
            speed_text,
            True,
            (255, 220, 100)
        )

        self.screen.blit(
            speed_label,
            (
                150,
                ROWS * CELL + 4
            )
        )

        # -----------------------------------------
        # Freeze status
        # -----------------------------------------

        if self.freeze_timer > 0:

            freeze_text = (
                f"FROZEN: "
                f"{self.freeze_timer}"
            )

            freeze_label = self.font.render(
                freeze_text,
                True,
                (100, 200, 255)
            )

            self.screen.blit(
                freeze_label,
                (
                    300,
                    ROWS * CELL + 4
                )
            )

        # -----------------------------------------
        # Restart
        # -----------------------------------------

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
        # Pellet status
        # -----------------------------------------

        if self.freeze_timer <= 0:

            if self.pellet_active:

                pellet_text = (
                    "Power Pellet: Available"
                )

            else:

                pellet_text = (
                    "Power Pellet: Used"
                )

            pellet_label = self.font.render(
                pellet_text,
                True,
                (200, 200, 200)
            )

            self.screen.blit(
                pellet_label,
                (
                    8,
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
    # GAME OVER OVERLAY
    # =================================================

    def _overlay(self, text, color):

        # Dark overlay
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

        # -----------------------------------------
        # Game over text
        # -----------------------------------------

        msg = self.big_font.render(
            text,
            True,
            color
        )

        self.screen.blit(
            msg,
            (
                WIDTH // 2
                - msg.get_width() // 2,
                ROWS * CELL // 2 - 55
            )
        )

        # -----------------------------------------
        # TASK 4: FINAL SCORE
        # -----------------------------------------

        final_score = self.score // 60

        score_text = (
            f"Survived: "
            f"{final_score}s"
        )

        score_label = self.font.render(
            score_text,
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            score_label,
            (
                WIDTH // 2
                - score_label.get_width() // 2,
                ROWS * CELL // 2
            )
        )

        # -----------------------------------------
        # Restart instruction
        # -----------------------------------------

        sub = self.font.render(
            "Press R to Restart",
            True,
            (200, 200, 200)
        )

        self.screen.blit(
            sub,
            (
                WIDTH // 2
                - sub.get_width() // 2,
                ROWS * CELL // 2 + 35
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
