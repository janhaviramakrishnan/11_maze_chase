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

        # Player
        self.player = Player(0, 0)

        # Three independent enemies
        self.enemies = [
            Enemy(ROWS - 1, COLS - 1),  # Bottom-right
            Enemy(ROWS - 1, 0),          # Bottom-left
            Enemy(0, COLS - 1)           # Top-right
        ]

        # Exit
        self.exit_rect = pygame.Rect(
            (COLS // 2) * CELL + 5,
            (ROWS // 2) * CELL + 5,
            CELL - 10,
            CELL - 10
        )

        self.caught = False
        self.won = False

        # -----------------------------------------
        # Difficulty ramp
        # -----------------------------------------

        # Time at which the game started/restarted
        self.start_time = pygame.time.get_ticks()

        # Current difficulty tier
        self.speed_tier = 1

        # Initial enemy movement interval
        self.enemy_move_interval = 20

    def handle_events(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_r:
                    self.reset()

        return True

    def update_difficulty(self):

        # Current elapsed time in milliseconds
        elapsed_time = (
            pygame.time.get_ticks()
            - self.start_time
        )

        # Number of complete 15-second periods
        elapsed_periods = elapsed_time // 15000

        # Starting interval is 20.
        # Reduce by 2 every 15 seconds.
        new_interval = max(
            5,
            20 - (elapsed_periods * 2)
        )

        # Speed tier:
        # Tier 1 = 20
        # Tier 2 = 18
        # Tier 3 = 16
        # ...
        # Tier 8 = 6
        # Tier 9+ = 5
        new_speed_tier = (
            (20 - new_interval) // 2
        ) + 1

        # Only update if the difficulty changed
        if new_interval != self.enemy_move_interval:

            self.enemy_move_interval = new_interval
            self.speed_tier = new_speed_tier

            # Apply the new interval to every enemy
            for enemy in self.enemies:

                enemy.move_interval = (
                    self.enemy_move_interval
                )

    def update(self):

        if self.caught or self.won:
            return

        # Update difficulty based on elapsed time
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
        # Enemy movement
        # -----------------------------------------

        for enemy in self.enemies:

            # Each enemy independently calls BFS
            # on every update.
            enemy.update(
                self.walls,
                self.player,
                ROWS,
                COLS
            )

            # Check collision
            if self.player.rect.colliderect(
                enemy.rect
            ):
                self.caught = True

        # -----------------------------------------
        # Exit condition
        # -----------------------------------------

        if self.player.rect.colliderect(
            self.exit_rect
        ):
            self.won = True

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
        # Draw exit
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
        # Draw player
        # -----------------------------------------

        self.player.draw(
            self.screen
        )

        # -----------------------------------------
        # Draw enemies
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

        # Current enemy interval
        speed_text = (
            f"Enemy Speed: Tier {self.speed_tier} "
            f"(Interval: {self.enemy_move_interval})"
        )

        speed_label = self.font.render(
            speed_text,
            True,
            (255, 220, 100)
        )

        self.screen.blit(
            speed_label,
            (8, ROWS * CELL + 5)
        )

        # Restart instruction
        restart_label = self.font.render(
            "R = Restart",
            True,
            (200, 200, 200)
        )

        self.screen.blit(
            restart_label,
            (
                WIDTH - restart_label.get_width() - 8,
                ROWS * CELL + 5
            )
        )

        # -----------------------------------------
        # Game-over overlay
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

    def run(self):

        running = True

        while running:

            running = self.handle_events()

            self.update()

            self.draw()

            self.clock.tick(FPS)

        pygame.quit()
        