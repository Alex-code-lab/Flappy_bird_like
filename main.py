import pygame
import sys
import os
import random
from moviepy import VideoFileClip  # Importer VideoFileClip depuis moviepy
import time  # Importer time pour gérer le cooldown
import logging
from pathlib import Path
import threading

# Définir un chemin absolu pour le fichier de logs (par exemple, sur le bureau)
desktop_path = Path.home() / "Desktop" / "game.log"

logging.basicConfig(level=logging.DEBUG, filename=str(desktop_path), filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')

# Configuration de l'environnement pour MoviePy (si nécessaire)
# os.environ["IMAGEIO_FFMPEG_EXE"] = "/opt/homebrew/bin/ffmpeg" # Ajustez le chemin si nécessaire
os.environ["IMAGEIO_FFMPEG_EXE"] = "/Users/souchaud/Documents/Autre/2024_11_26_anniv_anatole/resources/ffmpeg" # Ajustez le chemin si nécessaire

# Constantes globales du jeu
WHITE = (255, 255, 255)  # Couleur blanche en RGB
SCREEN_WIDTH, SCREEN_HEIGHT = 400, 600  # Dimensions de la fenêtre du jeu
FPS = 30  # Images par seconde
GRAVITY = 0.25  # Gravité appliquée au joueur
FLAP_STRENGTH = -5  # Force du saut du joueur
PIPE_SPEED_INIT = -4  # Vitesse initiale des tuyaux
PIPE_GAP_MIN = 150  # Écart minimal entre les tuyaux (augmenté pour faciliter le jeu)
PIPE_GAP_MAX = 250  # Écart maximal entre les tuyaux (augmenté pour faciliter le jeu)
SCORE_INTERVAL_FOR_SPEED_INCREASE = 3  # Score nécessaire pour augmenter la vitesse
DAY_NIGHT_CYCLE = 5  # Intervalle de score pour changer le cycle jour/nuit
TRANSITION_DURATION = FPS * 2  # Durée de la transition jour/nuit en frames
PAUSE_COOLDOWN = 2  # Délai en secondes pour le cooldown de la pause
AGE_ENFANT = 10 # Age de l'enfant pour avoir la suprise

def resource_path(relative_path):
    """Obtenir le chemin absolu vers une ressource, fonctionne pour le développement et pour py2app."""
    try:
        # py2app utilise sys.frozen
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class Game:
    """
    Classe principale du jeu qui gère la boucle du jeu, les événements, les mises à jour et les rendus.
    """

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Joyeux Anniversaire!")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.load_resources()
        self.running = True
        self.video_played = False
        self.score = 0
        self.last_speed_increase_score = 0
        self.font_name = self.font_path
        self.is_night = False  # Indicateur du cycle jour/nuit
        self.game_paused = False  # Indicateur si le jeu est en pause

        # Variables pour la transition jour/nuit
        self.transitioning = False
        self.transition_progress = 0
        self.transition_direction = 1  # 1 pour jour vers nuit, -1 pour nuit vers jour
        self.day_color = pygame.Color(102, 190, 209)
        self.night_color = pygame.Color(25, 25, 112)
        self.background_color = self.day_color

        # Créer les objets du jeu
        self.player = Player(self)
        self.pipes = []
        self.clouds = [Cloud(self) for _ in range(5)]
        self.stars = [Star() for _ in range(25)]
        self.shells = [Shell(self) for _ in range(3)]

        # Attribut pour gérer les transitions multiples
        self.cycle_changed = False

        # Initialiser les boutons de pause (vide au début)
        self.pause_buttons = []

        # Initialiser le timer pour le cooldown de la pause
        self.last_pause_toggle_time = 0

    def load_resources(self):
        """Charger toutes les ressources nécessaires (images, polices, musique)."""
        try:
            logging.debug("Loading resources")
            # Chemin vers la police utilisée
            self.font_path = resource_path('resources/SuperMario256.ttf')

            # Charger et redimensionner les images nécessaires
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

            # Redimensionner les images de titre et de fin
            image_width = 300
            title_image_height = int(self.title_image.get_height() * (image_width / self.title_image.get_width()))
            self.title_image = pygame.transform.scale(self.title_image, (image_width, title_image_height))
            game_over_image_height = int(self.game_over_image.get_height() * (image_width / self.game_over_image.get_width()))
            self.game_over_image = pygame.transform.scale(self.game_over_image, (image_width, game_over_image_height))

            # Charger FFMPEG pour MoviePy
            ffmpeg_path = resource_path('resources/ffmpeg')  # Assurez-vous que le binaire FFMPEG est présent
            os.environ["IMAGEIO_FFMPEG_EXE"] = ffmpeg_path
            logging.debug(f"FFMPEG path set to: {ffmpeg_path}")

            # Charger et jouer la musique de fond
            pygame.mixer.music.load(resource_path('resources/mario_theme_song.mp3'))
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
            logging.debug("Background music started")
        except Exception as e:
            logging.error(f"Error loading resources: {e}")
            raise

    def draw_text(self, surf, text, size, x, y, color=(255, 255, 255)):
        """
        Dessiner du texte sur une surface donnée.
        """
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        surf.blit(text_surface, text_rect)

    def run(self):
        """
        Lancer le jeu, gérer la boucle principale et les écrans de démarrage et de fin.
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
        Initialiser une nouvelle partie en réinitialisant les variables et en créant les objets du jeu.
        """
        self.player.reset()
        self.score = 0
        self.video_played = False
        self.pipes = []
        self.clouds = [Cloud(self) for _ in range(5)]
        self.stars = [Star() for _ in range(25)]
        self.shells = [Shell(self) for _ in range(3)]
        self.is_night = False  # Commencer le jeu en mode jour
        self.background_color = self.day_color
        self.transitioning = False
        self.game_paused = False
        self.cycle_changed = False
        self.pause_buttons = []  # Réinitialiser les boutons de pause
        self.last_pause_toggle_time = 0  # Réinitialiser le timer de cooldown
        self.create_initial_pipes()

    def create_initial_pipes(self):
        """
        Créer le premier tuyau avec un délai pour que le joueur ait le temps de se préparer.
        """
        delay_seconds = 3
        pipe_speed_per_second = -PIPE_SPEED_INIT * FPS
        distance = pipe_speed_per_second * delay_seconds
        initial_pipe_x = SCREEN_WIDTH + distance
        self.pipes.append(Pipe(self, initial_pipe_x))

    def game_loop(self):
        """
        Boucle principale du jeu où les événements, les mises à jour et les rendus sont gérés.
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
        Gérer les événements tels que les entrées du clavier ou la fermeture de la fenêtre.
        """
        current_time = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                # Vérifier si le cooldown est passé
                if event.key == pygame.K_RETURN and (current_time - self.last_pause_toggle_time) > PAUSE_COOLDOWN:
                    # Bascule l'état de pause lorsqu'on appuie sur Entrée
                    self.game_paused = not self.game_paused
                    self.last_pause_toggle_time = current_time  # Réinitialiser le timer de cooldown
                # Gérer les actions du joueur uniquement si le jeu n'est pas en pause
                if not self.game_paused:
                    if event.key == pygame.K_UP:
                        self.player.flap()
                    elif event.key == pygame.K_DOWN:
                        self.player.dive()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_paused and self.pause_buttons:
                    for button in self.pause_buttons:
                        if button.is_clicked():
                            if button.text == "Reprendre la partie":
                                self.game_paused = False

    def update(self):
        """
        Mettre à jour l'état du jeu, y compris le joueur, les tuyaux, les nuages et la détection des collisions.
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

        # Gérer la transition jour/nuit
        if self.transitioning:
            self.transition_progress += 1
            progress_ratio = self.transition_progress / TRANSITION_DURATION
            if self.transition_direction == 1:
                # Jour vers nuit
                self.background_color = self.day_color.lerp(self.night_color, progress_ratio)
            else:
                # Nuit vers jour
                self.background_color = self.night_color.lerp(self.day_color, progress_ratio)
            if self.transition_progress >= TRANSITION_DURATION:
                self.transitioning = False
                self.is_night = not self.is_night
                self.transition_progress = 0
        else:
            # Commencer la transition si le score atteint le multiple
            if (self.score % DAY_NIGHT_CYCLE == 0 and self.score != 0 and 
                not self.transitioning and not self.cycle_changed):
                self.transitioning = True
                self.transition_direction = 1 if not self.is_night else -1
                self.transition_progress = 0
                self.cycle_changed = True  # Empêcher de déclencher plusieurs fois
            elif self.score % DAY_NIGHT_CYCLE != 0:
                self.cycle_changed = False  # Réinitialiser pour permettre le prochain changement

        # Augmenter la vitesse des tuyaux en fonction du score
        if self.score // SCORE_INTERVAL_FOR_SPEED_INCREASE > self.last_speed_increase_score:
            for pipe in self.pipes:
                pipe.speed -= 1
                global PIPE_SPEED_INIT
                PIPE_SPEED_INIT -= 1
            self.last_speed_increase_score = self.score // SCORE_INTERVAL_FOR_SPEED_INCREASE

        # Vérifier les collisions entre le joueur et les tuyaux
        for pipe in self.pipes:
            if self.player.collide_with(pipe):
                self.player.dead = True

        # Vérifier si le joueur est sorti de l'écran
        if self.player.y >= SCREEN_HEIGHT - self.player.height or self.player.y <= 0:
            self.player.dead = True

        # Jouer la vidéo si le score atteint 10 et que la vidéo n'a pas encore été jouée
        if self.score >= AGE_ENFANT and not self.video_played:
            self.play_video(resource_path('resources/video_anniv.mp4'))
            self.video_played = True
            self.game_paused = True
            self.pause_buttons = [
                Button("Reprendre la partie", 100, 450, 200, 50, (81, 219, 63))
            ]

    def draw(self):
        """
        Dessiner tous les éléments du jeu à l'écran.
        """
        # Remplir l'écran avec la couleur de fond actuelle
        self.screen.fill(self.background_color)

        # Dessiner les étoiles uniquement pendant la nuit ou la transition vers la nuit
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
            # Afficher l'écran de pause spécifique après la vidéo
            self.draw_text(self.screen, "Jeu en Pause", 36, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50)
            for button in self.pause_buttons:
                button.draw(self.screen, font_name=self.font_name)
        
        if self.game_paused and not self.video_played:
            # Afficher l'écran de pause standard
            self.draw_pause_screen()

        pygame.display.update()

    def draw_pause_screen(self):
        """
        Dessiner l'écran de pause.
        """
        # Créer un rectangle semi-transparent pour l'arrière-plan de la pause
        pause_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pause_overlay.fill((0, 0, 0, 180))  # Noir avec alpha pour transparence
        self.screen.blit(pause_overlay, (0, 0))

        # Afficher le texte de pause
        pause_text = "PAUSE, appuyez sur ENTRE pour reprendre"
        self.draw_text(self.screen, pause_text, 15, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 15, color=(255, 255, 255))

    def start_screen(self):
        """
        Afficher l'écran de démarrage du jeu avec les instructions et un bouton pour commencer.
        """
        intro_text = [
            ("Bienvenue au jeu d'anniversaire!", 20, (255, 255, 255)),
            ("Aide Mario a atteindre", 15, (255, 255, 255)),
            ("le score egal à ton age pour ", 15, (255, 255, 255)),
            ("une surprise speciale!", 15, (255, 255, 255)),
            ("", 20),
            ("Utilise :", 15, (255, 255, 255)),
            ("- la fleche du haut pour monter,", 15, (255, 255, 255)),
            ("- celle du bas pour descendre.", 15, (255, 255, 255)),
            ("", 20),
            ("Bonne chance!", 20, (255, 255, 255))
        ]
        buttons = [
            Button("Commencer", 125, 450, 150, 50, (126, 223, 71))
        ]
        self.show_screen(self.title_image, intro_text, buttons)

    def game_over_screen(self):
        """
        Afficher l'écran de fin de jeu avec le score final et des options pour rejouer ou quitter.
        """
        score_text = f"Score Final: {self.score}"
        text_lines_with_styles = [
            (score_text, 36, (255, 255, 255)),
        ]
        buttons = [
            Button("Rejouer", 100, 450, 100, 50, (81, 219, 63)),
            Button("Quitter", 200, 450, 100, 50, (247, 46, 46))
        ]
        result = self.show_screen(self.game_over_image, text_lines_with_styles, buttons)
        return result == "Rejouer"

    def show_screen(self, image, text_lines_with_styles, buttons, default_size=15, default_color=(255, 255, 255)):
        """
        Afficher un écran générique avec une image, du texte (avec tailles et couleurs) et des boutons.
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
                            if button.text == "Commencer":
                                return
                            elif button.text == "Rejouer":
                                return "Rejouer"
                            elif button.text == "Quitter":
                                pygame.quit()
                                sys.exit()
            # Remplir l'écran avec la couleur de fond actuelle
            self.screen.fill(self.background_color)

            # Dessiner les étoiles si c'est la nuit
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

    # def play_video(self, video_path):
    #     """
    #     Jouer une vidéo en plein écran.
    #     """
    #     clip = VideoFileClip(video_path)
    #     clip = clip.resized(height=SCREEN_HEIGHT, width=SCREEN_WIDTH)
    #     clock = pygame.time.Clock()
    #     for frame in clip.iter_frames(fps=30, dtype="uint8"):
    #         for event in pygame.event.get():
    #             if event.type == pygame.QUIT:
    #                 pygame.quit()
    #                 sys.exit()
    #         frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
    #         self.screen.blit(frame_surface, (0, 0))
    #         pygame.display.update()
    #         clock.tick(30)
    #     clip.close()

    def play_video(self, video_path):
        clip = VideoFileClip(video_path)
        clip = clip.resized(new_size=(300, 500))

        pygame.mixer.music.pause()
        # Charger et jouer la musique de fond
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
            # frame_surface = pygame.transform.rotate(frame_surface, -90)  # Si besoin de rotation
            # frame_surface = pygame.transform.flip(frame_surface, True, False)  # Si besoin de flip
            frame_width = frame_surface.get_width()
            frame_height = frame_surface.get_height()
            x = (SCREEN_WIDTH - frame_width) // 2
            y = (SCREEN_HEIGHT - frame_height) // 2
            self.screen.blit(frame_surface, (x, y))




            pygame.display.update()

            clock.tick(30)
            # pygame.mixer.music.stop()
        pygame.mixer.music.pause()
        # Charger et jouer la musique de fond
        pygame.mixer.music.load(resource_path('resources/mario_theme_song.mp3'))
        pygame.mixer.music.set_volume(0.8)
        pygame.mixer.music.play(-1)
        clip.close()

    # def play_video(self, video_path):
    #     """
    #     Jouer une vidéo sans son tout en lisant l'audio depuis un fichier MP3.
    #     """
    #     try:
    #         # Mettre en pause la musique de fond du jeu si elle est en cours de lecture
    #         pygame.mixer.music.pause()
            
    #         # Charger le clip vidéo sans audio
    #         clip = VideoFileClip(video_path).without_audio()
    #         # Redimensionner le clip pour correspondre à la taille souhaitée
    #         clip = clip.resized(newsize=(300, 500))
            
    #         # Charger et jouer l'audio avec pygame.mixer.music
    #         audio_path = resource_path('resources/test_video.mp3')  # Assurez-vous que le chemin est correct
    #         pygame.mixer.music.load(audio_path)
    #         pygame.mixer.music.play()
            
    #         clock = pygame.time.Clock()
    #         for frame in clip.iter_frames(fps=30, dtype="uint8"):
    #             for event in pygame.event.get():
    #                 if event.type == pygame.QUIT:
    #                     pygame.mixer.music.stop()
    #                     pygame.quit()
    #                     sys.exit()
    #             # Convertir la frame en surface
    #             frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
    #             frame_width = frame_surface.get_width()
    #             frame_height = frame_surface.get_height()
    #             x = (SCREEN_WIDTH - frame_width) // 2
    #             y = (SCREEN_HEIGHT - frame_height) // 2
    #             self.screen.blit(frame_surface, (x, y))
    #             pygame.display.update()
    #             clock.tick(30)
            
    #         # Attendre la fin de la lecture audio
    #         while pygame.mixer.music.get_busy():
    #             pygame.time.Clock().tick(10)
            
    #         # Arrêter la musique de la vidéo
    #         pygame.mixer.music.stop()
    #         # Reprendre la musique de fond du jeu
    #         pygame.mixer.music.unpause()
    #         clip.close()
    #     except Exception as e:
    #         logging.error(f"Error playing video: {e}")
    #         print(f"Error playing video: {e}")
    #         # Assurez-vous que le jeu continue même en cas d'erreur
    #         self.video_played = True
   

class Star:
    """
    Classe représentant une étoile scintillante en arrière-plan.
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
        Mettre à jour l'effet de scintillement de l'étoile.
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
        Dessiner l'étoile avec une luminosité variable.
        """
        brightness_color = (int(self.brightness), int(self.brightness), 0)
        pygame.draw.circle(screen, brightness_color, (int(self.x), int(self.y)), int(self.current_radius))

class Player:
    """
    Classe représentant le joueur (Mario volant).
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
        Réinitialiser la position et l'état du joueur.
        """
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.dead = False

    def flap(self):
        """
        Faire sauter le joueur en lui appliquant une force vers le haut.
        """
        self.velocity = FLAP_STRENGTH

    def dive(self):
        """
        Faire plonger le joueur en lui appliquant une force vers le bas.
        """
        self.velocity = -FLAP_STRENGTH

    def update(self):
        """
        Mettre à jour la position du joueur en fonction de la gravité et de sa vitesse.
        """
        self.velocity += GRAVITY
        self.y += self.velocity

    def draw(self, screen):
        """
        Dessiner le joueur à l'écran.
        """
        screen.blit(self.image, (self.x, self.y))

    def get_rect(self):
        """
        Obtenir le rectangle englobant du joueur pour la détection des collisions.
        """
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def collide_with(self, pipe):
        """
        Vérifier la collision avec un tuyau.
        """
        player_rect = self.get_rect()
        collision = player_rect.colliderect(pipe.upper_pipe_rect) or \
                    player_rect.colliderect(pipe.lower_pipe_rect)
        if pipe.has_plant and pipe.plant_rect:
            collision = collision or player_rect.colliderect(pipe.plant_rect)
        return collision

class Pipe:
    """
    Classe représentant un tuyau dans le jeu.
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
        Calculer les rectangles de collision pour le tuyau supérieur, le tuyau inférieur et la plante.
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
        Mettre à jour la position du tuyau et recalculer les rectangles de collision.
        """
        self.x += self.speed
        self.calculate_collision_rects()

    def off_screen(self):
        """
        Vérifier si le tuyau est sorti de l'écran.
        """
        return self.x < -self.width

    def draw(self, screen):
        """
        Dessiner le tuyau et la plante (si présente) à l'écran.
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
    Classe représentant un nuage en arrière-plan.
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
        Mettre à jour la position du nuage.
        """
        self.x -= self.speed
        if self.x < -self.width:
            self.x = SCREEN_WIDTH
            self.y = random.randint(0, SCREEN_HEIGHT // 2)
            self.speed = random.uniform(0.1, 2)

    def draw(self, screen):
        """
        Dessiner le nuage à l'écran.
        """
        screen.blit(self.image, (self.x, self.y))

class Shell:
    """
    Classe représentant une carapace volante en arrière-plan.
    """
    def __init__(self, game):
        self.game = game
        self.original_images = [game.shell_red_img_original, game.shell_green_img_original]
        self.image_original = random.choice(self.original_images)
        
        # Taille aléatoire entre 0.01 et 0.03 de la taille originale
        self.scale_factor = random.uniform(0.01, 0.03)
        self.width = int(self.image_original.get_width() * self.scale_factor)
        self.height = int(self.image_original.get_height() * self.scale_factor)
        self.image = pygame.transform.scale(self.image_original, (self.width, self.height))

        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT // 2)
        self.speed_x = random.uniform(-3, 3)
        while abs(self.speed_x) < 1:  # Éviter une vitesse horizontale trop faible
            self.speed_x = random.uniform(-3, 3)
        self.speed_y = random.uniform(-1.5, 1.5)

        # Déterminer si on doit appliquer l'effet miroir
        self.update_image_direction()

    def update_image_direction(self):
        """
        Appliquer ou non l'effet miroir en fonction de la direction de mouvement.
        """
        if self.speed_x < 0:
            # Appliquer un miroir horizontal si la carapace se déplace vers la gauche
            self.image = pygame.transform.flip(self.image_original, True, False)
            # Re-redimensionner l'image après flip
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
        else:
            # Sinon, utiliser l'image originale redimensionnée
            self.image = pygame.transform.scale(self.image_original, (self.width, self.height))

    def update(self):
        """
        Mettre à jour la position de la carapace.
        """
        self.x += self.speed_x
        self.y += self.speed_y

        # Repositionner la carapace si elle sort de l'écran
        if self.x < -self.width or self.x > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH if self.speed_x < 0 else -self.width
            self.y = random.randint(0, SCREEN_HEIGHT // 2)
            self.speed_x = random.uniform(-3, 3)
            while abs(self.speed_x) < 1:
                self.speed_x = random.uniform(-3, 3)
            self.speed_y = random.uniform(-1.5, 1.5)
            
            # Taille aléatoire entre 0.01 et 0.03
            self.scale_factor = random.uniform(0.01, 0.03)
            self.width = int(self.image_original.get_width() * self.scale_factor)
            self.height = int(self.image_original.get_height() * self.scale_factor)
            self.image = pygame.transform.scale(self.image_original, (self.width, self.height))
            self.update_image_direction()
        
        # Inverser la direction verticale si la carapace atteint le bord de l'écran
        if self.y < 0 or self.y > SCREEN_HEIGHT - self.height:
            self.speed_y *= -1

    def draw(self, screen):
        """
        Dessiner la carapace à l'écran.
        """
        screen.blit(self.image, (self.x, self.y))

class Button:
    """
    Représente un bouton interactif dans l'interface utilisateur.
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
        Dessine le bouton sur l'écran.
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
        Vérifie si la souris survole le bouton.
        """
        return self.x < mouse[0] < self.x + self.width and self.y < mouse[1] < self.y + self.height

    def is_clicked(self):
        """
        Vérifie si le bouton est cliqué.
        """
        return self.is_hovered(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]

# def main():
#     """
#     Fonction principale pour lancer le jeu.
#     """
#     game = Game()
#     game.run()
def main():
    try:
        logging.debug("Starting game")
        game = Game()
        game.run()
    except Exception as e:
        logging.error(f"Exception in main: {e}")

if __name__ == "__main__":
    main()