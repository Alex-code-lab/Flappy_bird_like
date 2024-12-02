import pygame
import sys
import os
import random
from moviepy import VideoFileClip  # Corrected import
import time
import logging
from pathlib import Path

# Set up logging
desktop_path = Path.home() / "Desktop" / "game.log"

logging.basicConfig(level=logging.DEBUG, filename=str(desktop_path), filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')

# Global game constants
WHITE = (255, 255, 255)  # RGB color for white
SCREEN_WIDTH, SCREEN_HEIGHT = 400, 600  # Game window dimensions
FPS = 30  # Frames per second
GRAVITY = 0.25  # Gravity applied to the player
FLAP_STRENGTH = -5  # Player's jump strength
PIPE_SPEED_INIT = -4  # Initial pipe speed
PIPE_GAP_MIN = 150  # Minimum gap between pipes (increased to make the game easier)
PIPE_GAP_MAX = 250  # Maximum gap between pipes (increased to make the game easier)
SCORE_INTERVAL_FOR_SPEED_INCREASE = 3  # Score needed to increase the speed
DAY_NIGHT_CYCLE = 5  # Score interval to change day/night cycle
TRANSITION_DURATION = FPS * 2  # Day/night transition duration in frames
PAUSE_COOLDOWN = 2  # Pause cooldown in seconds

def resource_path(relative_path):
    """Get absolute path to resource, works for development and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Game:
    """
    Main game class that handles the game loop, events, updates, and rendering.
    """

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Happy Birthday!")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.load_resources()
        self.running = True
        self.video_played = False
        self.score = 0
        self.last_speed_increase_score = 0
        self.font_name = self.font_path
        self.is_night = False  # Indicator for day/night cycle
        self.game_paused = False  # Indicator if the game is paused

        # Variables for day/night transition
        self.transitioning = False
        self.transition_progress = 0
        self.transition_direction = 1  # 1 for day to night, -1 for night to day
        self.day_color = pygame.Color(102, 190, 209)
        self.night_color = pygame.Color(25, 25, 112)
        self.background_color = self.day_color

        # Create game objects
        self.player = Player(self)
        self.pipes = []
        self.clouds = [Cloud(self) for _ in range(5)]
        self.stars = [Star() for _ in range(25)]
        self.shells = [Shell(self) for _ in range(3)]

        # Attribute to manage multiple transitions
        self.cycle_changed = False

        # Initialize pause buttons (empty at the start)
        self.pause_buttons = []

        # Initialize timer for pause cooldown
        self.last_pause_toggle_time = 0

    def load_resources(self):
        """Load all necessary resources (images, fonts, music)."""
        try:
            logging.debug("Loading resources")
            # Path to the font used
            self.font_path = resource_path('resources/SuperMario256.ttf')

            # Load and resize necessary images
            self.bird_img = pygame.image.load(resource_path('resources/mario_volant.png')).convert_alpha()
            self.bird_img = pygame.transform.scale(self.bird_img, (50, 50))

            self.brique_img = pygame.image.load(resource_path('resources/brique.png')).convert_alpha()
            self.brique_img = pygame.transform.scale(self.brique_img, (50, 50))

            self.plante_img = pygame.image.load(resource_path('resources/plante.png')).convert_alpha()
            self.plante_img = pygame.transform.scale(self.plante_img, (50, 75))

            self.nuage_img = pygame.image.load(resource_path('resources/nuage.png')).convert_alpha()
            self.nuage_img = pygame.transform.scale(self.nuage_img, (100, 60))

            self.shell_red_img_original = pygame.image.load(resource_path('resources/carapace_rouge.png')).convert_alpha()
            self.shell_green_img_original = pygame.image.load(resource_path('resources/carapace_verte.png')).convert_alpha()

            self.title_image = pygame.image.load(resource_path('resources/mission_joyeux_anniversaire.png')).convert_alpha()
            self.game_over_image = pygame.image.load(resource_path('resources/Game_over.png')).convert_alpha()

            # Resize title and game over images
            image_width = 300
            title_image_height = int(self.title_image.get_height() * (image_width / self.title_image.get_width()))
            self.title_image = pygame.transform.scale(self.title_image, (image_width, title_image_height))
            game_over_image_height = int(self.game_over_image.get_height() * (image_width / self.game_over_image.get_width()))
            self.game_over_image = pygame.transform.scale(self.game_over_image, (image_width, game_over_image_height))

            logging.debug("Resources loaded successfully")

            # Load and play background music
            pygame.mixer.music.load(resource_path('resources/mario_theme_song.mp3'))
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
            logging.debug("Background music started")
        except Exception as e:
            logging.error(f"Error loading resources: {e}")
            raise

    def draw_text(self, surf, text, size, x, y, color=(255, 255, 255)):
        """
        Draw text on a given surface.
        """
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        surf.blit(text_surface, text_rect)

    def run(self):
        """
        Run the game, manage the main loop, and handle start and end screens.
        """
        self.start_screen()
        while self.running:
            self.new_game()
            self.game_loop()
            if not self.game_over_screen():
                self.running = False
        pygame.quit()
        sys.exit()

    def new_game(self):
        """
        Initialize a new game by resetting variables and creating game objects.
        """
        self.player.reset()
        self.score = 0
        self.video_played = False
        self.pipes = []
        self.clouds = [Cloud(self) for _ in range(5)]
        self.stars = [Star() for _ in range(25)]
        self.shells = [Shell(self) for _ in range(3)]
        self.is_night = False  # Start the game in day mode
        self.background_color = self.day_color
        self.transitioning = False
        self.game_paused = False
        self.cycle_changed = False
        self.pause_buttons = []  # Reset pause buttons
        self.last_pause_toggle_time = 0  # Reset cooldown timer
        self.create_initial_pipes()

    def create_initial_pipes(self):
        """
        Create the first pipe with a delay so the player has time to prepare.
        """
        delay_seconds = 3
        pipe_speed_per_second = -PIPE_SPEED_INIT * FPS
        distance = pipe_speed_per_second * delay_seconds
        initial_pipe_x = SCREEN_WIDTH + distance
        self.pipes.append(Pipe(self, initial_pipe_x))

    def game_loop(self):
        """
        Main game loop where events, updates, and rendering are managed.
        """
        self.last_speed_increase_score = 0
        running = True
        while running:
            self.clock.tick(FPS)
            self.handle_events()
            if not self.game_paused:
                self.update()
            self.draw()
            if self.player.dead:
                running = False

    def handle_events(self):
        """
        Handle events such as keyboard inputs or window closing.
        """
        current_time = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                # Check if the cooldown has passed
                if event.key == pygame.K_RETURN and (current_time - self.last_pause_toggle_time) > PAUSE_COOLDOWN:
                    # Toggle pause state when Enter is pressed
                    self.game_paused = not self.game_paused
                    self.last_pause_toggle_time = current_time  # Reset cooldown timer
                # Handle player actions only if the game is not paused
                if not self.game_paused:
                    if event.key == pygame.K_UP:
                        self.player.flap()
                    elif event.key == pygame.K_DOWN:
                        self.player.dive()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_paused and self.pause_buttons:
                    for button in self.pause_buttons:
                        if button.is_clicked():
                            if button.text == "Resume Game":
                                self.game_paused = False

    def update(self):
        """
        Update the game state, including the player, pipes, clouds, and collision detection.
        """
        self.player.update()
        for cloud in self.clouds:
            cloud.update()
        for shell in self.shells:
            shell.update()
        for pipe in self.pipes:
            pipe.update()
            if pipe.off_screen():
                self.pipes.remove(pipe)
                self.pipes.append(Pipe(self))
            if not pipe.passed and pipe.x + pipe.width < self.player.x:
                self.score += 1
                pipe.passed = True

        # Handle day/night transition
        if self.transitioning:
            self.transition_progress += 1
            progress_ratio = self.transition_progress / TRANSITION_DURATION
            if self.transition_direction == 1:
                # Day to night
                self.background_color = self.day_color.lerp(self.night_color, progress_ratio)
            else:
                # Night to day
                self.background_color = self.night_color.lerp(self.day_color, progress_ratio)
            if self.transition_progress >= TRANSITION_DURATION:
                self.transitioning = False
                self.is_night = not self.is_night
                self.transition_progress = 0
        else:
            # Start transition if the score reaches the multiple
            if (self.score % DAY_NIGHT_CYCLE == 0 and self.score != 0 and
                not self.transitioning and not self.cycle_changed):
                self.transitioning = True
                self.transition_direction = 1 if not self.is_night else -1
                self.transition_progress = 0
                self.cycle_changed = True  # Prevent triggering multiple times
            elif self.score % DAY_NIGHT_CYCLE != 0:
                self.cycle_changed = False  # Reset to allow the next change

        # Increase pipe speed based on the score
        if self.score // SCORE_INTERVAL_FOR_SPEED_INCREASE > self.last_speed_increase_score:
            for pipe in self.pipes:
                pipe.speed -= 1
                global PIPE_SPEED_INIT
                PIPE_SPEED_INIT -= 1
            self.last_speed_increase_score = self.score // SCORE_INTERVAL_FOR_SPEED_INCREASE

        # Check collisions between the player and pipes
        for pipe in self.pipes:
            if self.player.collide_with(pipe):
                self.player.dead = True

        # Check if the player is out of screen bounds
        if self.player.y >= SCREEN_HEIGHT - self.player.height or self.player.y <= 0:
            self.player.dead = True

        # Play the video if the score reaches 10 and the video hasn't been played yet
        if self.score >= 10 and not self.video_played:
            self.play_video(resource_path('resources/video_anniv.mp4'))
            self.video_played = True
            self.game_paused = True
            self.pause_buttons = [
                Button("Resume Game", 100, 450, 200, 50, (81, 219, 63))
            ]

    def draw(self):
        """
        Draw all game elements on the screen.
        """
        # Fill the screen with the current background color
        self.screen.fill(self.background_color)

        # Draw stars only during night or transition to night
        if self.is_night or (self.transitioning and self.transition_direction == 1):
            for star in self.stars:
                star.update()
                star.draw(self.screen)

        for cloud in self.clouds:
            cloud.draw(self.screen)
        for shell in self.shells:
            shell.draw(self.screen)
        self.player.draw(self.screen)
        for pipe in self.pipes:
            pipe.draw(self.screen)
        self.draw_text(self.screen, f"Score: {self.score}", 24, SCREEN_WIDTH - 100, 50)

        if self.game_paused and self.video_played:
            # Display the pause screen after the video
            self.draw_text(self.screen, "Game Paused", 36, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50)
            for button in self.pause_buttons:
                button.draw(self.screen, font_name=self.font_name)

        if self.game_paused and not self.video_played:
            # Display the standard pause screen
            self.draw_pause_screen()

        pygame.display.update()

    def draw_pause_screen(self):
        """
        Draw the pause screen.
        """
        # Create a semi-transparent rectangle for the pause background
        pause_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pause_overlay.fill((0, 0, 0, 180))  # Black with alpha for transparency
        self.screen.blit(pause_overlay, (0, 0))

        # Display pause text
        pause_text = "PAUSE, press ENTER to resume"
        self.draw_text(self.screen, pause_text, 15, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 15, color=(255, 255, 255))

    def start_screen(self):
        """
        Display the game's start screen with instructions and a button to begin.
        """
        intro_text = [
            ("Welcome to the Birthday Game!", 20, (255, 255, 255)),
            ("Help Mario reach", 15, (255, 255, 255)),
            ("a score equal to your age for", 15, (255, 255, 255)),
            ("a special surprise!", 15, (255, 255, 255)),
            ("", 20),
            ("Use:", 15, (255, 255, 255)),
            ("- Up arrow to go up,", 15, (255, 255, 255)),
            ("- Down arrow to go down.", 15, (255, 255, 255)),
            ("", 20),
            ("Good luck!", 20, (255, 255, 255))
        ]
        buttons = [
            Button("Start", 125, 450, 150, 50, (126, 223, 71))
        ]
        self.show_screen(self.title_image, intro_text, buttons)

    def game_over_screen(self):
        """
        Display the game over screen with the final score and options to replay or quit.
        """
        score_text = f"Final Score: {self.score}"
        text_lines_with_styles = [
            (score_text, 36, (255, 255, 255)),
        ]
        buttons = [
            Button("Play Again", 100, 450, 100, 50, (81, 219, 63)),
            Button("Quit", 200, 450, 100, 50, (247, 46, 46))
        ]
        result = self.show_screen(self.game_over_image, text_lines_with_styles, buttons)
        return result == "Play Again"

    def show_screen(self, image, text_lines_with_styles, buttons, default_size=15, default_color=(255, 255, 255)):
        """
        Display a generic screen with an image, text (with sizes and colors), and buttons.
        """
        waiting = True
        while waiting:
            self.clock.tick(15)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for button in buttons:
                        if button.is_clicked():
                            if button.text == "Start":
                                return
                            elif button.text == "Play Again":
                                return "Play Again"
                            elif button.text == "Quit":
                                pygame.quit()
                                sys.exit()
            # Fill the screen with the current background color
            self.screen.fill(self.background_color)

            # Draw stars if it's night
            if self.is_night:
                for star in self.stars:
                    star.update()
                    star.draw(self.screen)

            for cloud in self.clouds:
                cloud.update()
                cloud.draw(self.screen)
            for shell in self.shells:
                shell.update()
                shell.draw(self.screen)
            self.screen.blit(image, (SCREEN_WIDTH / 2 - image.get_width() / 2, SCREEN_HEIGHT / 10))
            y_offset = SCREEN_HEIGHT / 3
            for item in text_lines_with_styles:
                if isinstance(item, tuple):
                    line = item[0]
                    size = item[1] if len(item) > 1 else default_size
                    color = item[2] if len(item) > 2 else default_color
                else:
                    line = item
                    size = default_size
                    color = default_color
                self.draw_text(self.screen, line, size, SCREEN_WIDTH / 2, y_offset, color)
                y_offset += size + 5
            for button in buttons:
                button.draw(self.screen, font_name=self.font_name)
            pygame.display.flip()

    def play_video(self, video_path):
        clip = VideoFileClip(video_path)
        clip = clip.d(newsize=(300, 500))

        pygame.mixer.music.pause()
        # Load and play the background music for the video
        pygame.mixer.music.load(resource_path('resources/video_anniv.mp3'))
        pygame.mixer.music.set_volume(0.8)
        pygame.mixer.music.play(-1)

        clock = pygame.time.Clock()
        for frame in clip.iter_frames(fps=30, dtype="uint8"):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
            frame_width = frame_surface.get_width()
            frame_height = frame_surface.get_height()
            x = (SCREEN_WIDTH - frame_width) // 2
            y = (SCREEN_HEIGHT - frame_height) // 2
            self.screen.blit(frame_surface, (x, y))

            pygame.display.update()

            clock.tick(30)
        pygame.mixer.music.pause()
        # Resume the game's background music
        pygame.mixer.music.load(resource_path('resources/mario_theme_song.mp3'))
        pygame.mixer.music.set_volume(0.8)
        pygame.mixer.music.play(-1)
        clip.close()

class Star:
    """
    Class representing a twinkling star in the background.
    """

    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.base_radius = random.randint(1, 3)
        self.radius_variation = random.uniform(0.1, 0.5)
        self.current_radius = self.base_radius
        self.pulse_speed = random.uniform(0.02, 0.05)
        self.brightness = 255
        self.direction = 1

    def update(self):
        """
        Update the star's twinkling effect.
        """
        self.brightness += self.direction * self.pulse_speed * 255
        if self.brightness > 255:
            self.brightness = 255
            self.direction = -1
        elif self.brightness < 150:
            self.brightness = 150
            self.direction = 1
        self.current_radius = self.base_radius + self.radius_variation * (self.brightness / 255)

    def draw(self, screen):
        """
        Draw the star with variable brightness.
        """
        brightness_color = (int(self.brightness), int(self.brightness), 0)
        pygame.draw.circle(screen, brightness_color, (int(self.x), int(self.y)), int(self.current_radius))

class Player:
    """
    Class representing the player (flying Mario).
    """
    def __init__(self, game):
        self.game = game
        self.image = game.bird_img
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.x = 50
        self.reset()

    def reset(self):
        """
        Reset the player's position and state.
        """
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.dead = False

    def flap(self):
        """
        Make the player jump by applying an upward force.
        """
        self.velocity = FLAP_STRENGTH

    def dive(self):
        """
        Make the player dive by applying a downward force.
        """
        self.velocity = -FLAP_STRENGTH

    def update(self):
        """
        Update the player's position based on gravity and velocity.
        """
        self.velocity += GRAVITY
        self.y += self.velocity

    def draw(self, screen):
        """
        Draw the player on the screen.
        """
        screen.blit(self.image, (self.x, self.y))

    def get_rect(self):
        """
        Get the player's bounding rectangle for collision detection.
        """
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def collide_with(self, pipe):
        """
        Check for collision with a pipe.
        """
        player_rect = self.get_rect()
        collision = player_rect.colliderect(pipe.upper_pipe_rect) or \
                    player_rect.colliderect(pipe.lower_pipe_rect)
        if pipe.has_plant and pipe.plant_rect:
            collision = collision or player_rect.colliderect(pipe.plant_rect)
        return collision

class Pipe:
    """
    Class representing a pipe in the game.
    """
    def __init__(self, game, x=None):
        self.game = game
        self.image = game.brique_img
        self.plant_image = game.plante_img
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.x = x if x is not None else SCREEN_WIDTH
        self.speed = PIPE_SPEED_INIT
        self.pipe_gap = random.randint(PIPE_GAP_MIN, PIPE_GAP_MAX)
        self.pipe_y = random.randint(100 + self.pipe_gap, SCREEN_HEIGHT - 50)
        self.has_plant = random.choice([True, False])
        self.passed = False

        self.upper_pipe_rect = None
        self.lower_pipe_rect = None
        self.plant_rect = None
        self.calculate_collision_rects()

    def calculate_collision_rects(self):
        """
        Calculate collision rectangles for the upper pipe, lower pipe, and plant.
        """
        y_top = self.pipe_y - self.pipe_gap - self.height
        min_y_top = -self.height
        if self.has_plant:
            min_y_top += 2 * self.height
        upper_pipe_height = y_top - min_y_top
        self.upper_pipe_rect = pygame.Rect(
            self.x, min_y_top, self.width, upper_pipe_height
        )

        y_bottom = self.pipe_y
        lower_pipe_height = SCREEN_HEIGHT - y_bottom
        self.lower_pipe_rect = pygame.Rect(
            self.x, y_bottom, self.width, lower_pipe_height
        )

        if self.has_plant:
            plant_x = self.x + (self.width - self.plant_image.get_width()) // 2
            plant_y = self.pipe_y - self.plant_image.get_height()
            plant_width = self.plant_image.get_width()
            plant_height = self.plant_image.get_height()
            self.plant_rect = pygame.Rect(
                plant_x, plant_y, plant_width, plant_height
            )
        else:
            self.plant_rect = None

    def update(self):
        """
        Update the pipe's position and recalculate collision rectangles.
        """
        self.x += self.speed
        self.calculate_collision_rects()

    def off_screen(self):
        """
        Check if the pipe has moved off-screen.
        """
        return self.x < -self.width

    def draw(self, screen):
        """
        Draw the pipe and plant (if present) on the screen.
        """
        y = self.upper_pipe_rect.bottom - self.height
        while y >= self.upper_pipe_rect.top:
            screen.blit(pygame.transform.flip(self.image, False, True), (self.x, y))
            y -= self.height

        y = self.lower_pipe_rect.top
        while y < SCREEN_HEIGHT:
            screen.blit(self.image, (self.x, y))
            y += self.height

        if self.has_plant and self.plant_rect:
            screen.blit(self.plant_image, (self.plant_rect.x, self.plant_rect.y))

class Cloud:
    """
    Class representing a cloud in the background.
    """
    def __init__(self, game):
        self.game = game
        self.image = game.nuage_img
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT // 2)
        self.speed = random.uniform(0.1, 2)

    def update(self):
        """
        Update the cloud's position.
        """
        self.x -= self.speed
        if self.x < -self.width:
            self.x = SCREEN_WIDTH
            self.y = random.randint(0, SCREEN_HEIGHT // 2)
            self.speed = random.uniform(0.1, 2)

    def draw(self, screen):
        """
        Draw the cloud on the screen.
        """
        screen.blit(self.image, (self.x, self.y))

class Shell:
    """
    Class representing a flying shell in the background.
    """
    def __init__(self, game):
        self.game = game
        self.original_images = [game.shell_red_img_original, game.shell_green_img_original]
        self.image_original = random.choice(self.original_images)
        
        # Random size between 0.01 and 0.03 of the original size
        self.scale_factor = random.uniform(0.01, 0.03)
        self.width = int(self.image_original.get_width() * self.scale_factor)
        self.height = int(self.image_original.get_height() * self.scale_factor)
        self.image = pygame.transform.scale(self.image_original, (self.width, self.height))

        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT // 2)
        self.speed_x = random.uniform(-3, 3)
        while abs(self.speed_x) < 1:  # Avoid too slow horizontal speed
            self.speed_x = random.uniform(-3, 3)
        self.speed_y = random.uniform(-1.5, 1.5)

        # Determine if the image should be mirrored
        self.update_image_direction()

    def update_image_direction(self):
        """
        Apply or not the mirror effect based on the movement direction.
        """
        if self.speed_x < 0:
            # Apply a horizontal flip if the shell moves left
            self.image = pygame.transform.flip(self.image_original, True, False)
            # Resize the image after flip
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
        else:
            # Use the original resized image
            self.image = pygame.transform.scale(self.image_original, (self.width, self.height))

    def update(self):
        """
        Update the shell's position.
        """
        self.x += self.speed_x
        self.y += self.speed_y

        # Reposition the shell if it moves off-screen
        if self.x < -self.width or self.x > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH if self.speed_x < 0 else -self.width
            self.y = random.randint(0, SCREEN_HEIGHT // 2)
            self.speed_x = random.uniform(-3, 3)
            while abs(self.speed_x) < 1:
                self.speed_x = random.uniform(-3, 3)
            self.speed_y = random.uniform(-1.5, 1.5)
            
            # Random size between 0.01 and 0.03
            self.scale_factor = random.uniform(0.01, 0.03)
            self.width = int(self.image_original.get_width() * self.scale_factor)
            self.height = int(self.image_original.get_height() * self.scale_factor)
            self.image = pygame.transform.scale(self.image_original, (self.width, self.height))
            self.update_image_direction()
        
        # Reverse vertical direction if the shell reaches screen edges
        if self.y < 0 or self.y > SCREEN_HEIGHT - self.height:
            self.speed_y *= -1

    def draw(self, screen):
        """
        Draw the shell on the screen.
        """
        screen.blit(self.image, (self.x, self.y))

class Button:
    """
    Represents an interactive button in the user interface.
    """
    def __init__(self, text, x, y, width, height, color=(170, 170, 170), text_color=(255, 255, 255)):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.text_color = text_color

    def draw(self, screen, font_name, font_size=20):
        """
        Draws the button on the screen.
        """
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if self.is_hovered(mouse):
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        else:
            pygame.draw.rect(screen, (200, 200, 200), (self.x, self.y, self.width, self.height))
        font = pygame.font.Font(font_name, font_size)
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=(self.x + self.width / 2, self.y + self.height / 2))
        screen.blit(text_surface, text_rect)

    def is_hovered(self, mouse):
        """
        Checks if the mouse is hovering over the button.
        """
        return self.x < mouse[0] < self.x + self.width and self.y < mouse[1] < self.y + self.height

    def is_clicked(self):
        """
        Checks if the button is clicked.
        """
        return self.is_hovered(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]

def main():
    """
    Main function to start the game.
    """
    try:
        logging.debug("Starting game")
        game = Game()
        game.run()
    except Exception as e:
        logging.error(f"Exception in main: {e}")

if __name__ == "__main__":
    main()