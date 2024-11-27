import pygame
import sys
import os
os.environ["IMAGEIO_FFMPEG_EXE"] = "/opt/homebrew/bin/ffmpeg"
import random
import datetime
import moviepy
from moviepy import VideoFileClip  # Importer moviepy pour lire la vidéo


# Hardcoded metadata values
app_name = "Joyeux Anniversaire!"


# Constantes
WHITE = (255, 255, 255)
SCREEN_WIDTH, SCREEN_HEIGHT = 400, 600
BIRD_X = 50
BIRD_Y = 300
GRAVITY = 0.25
FLAP_STRENGTH = -5
PIPE_SPEED_INIT = -4
PIPE_GAP = 150
PIPE_GAP_MIN = 180  # Valeur minimale de l'écart
PIPE_GAP_MAX = 200  # Valeur maximale de l'écart
SPEED_INCREASE_INTERVAL = 3000
SCORE_INTERVAL_FOR_SPEED_INCREASE = 3

FONT_NAME = '/Users/souchaud/Documents/Autre/2024_11_26_anniv_anatole/resources/SuperMario256.ttf' #pygame.font.match_font('avenir')

def draw_text(surf, text, size, x, y, color=(255, 255, 255), font_name=FONT_NAME):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

def create_snowflakes(num_flakes):
    return [[random.randint(0, SCREEN_WIDTH),
             random.randint(0, SCREEN_HEIGHT),
             random.randint(2, 5)] for _ in range(num_flakes)]

def update_and_draw_snowflakes(screen, snowflakes):
    for flake in snowflakes:
        flake[1] += flake[2]
        pygame.draw.circle(screen, WHITE, (flake[0], flake[1]), flake[2])
        if flake[1] > SCREEN_HEIGHT:
            flake[0] = random.randint(0, SCREEN_WIDTH)
            flake[1] = -5
            flake[2] = random.randint(2, 5)

def draw_button(surf, text, x, y, width, height, color =  (126, 223, 71)):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    button_clicked = False

    if x + width > mouse[0] > x and y + height > mouse[1] > y:
        pygame.draw.rect(surf, color, (x, y, width, height))
        if click[0] == 1:
            button_clicked = True
    else:
        pygame.draw.rect(surf, (170, 170, 170), (x, y, width, height))

    draw_text(surf, text, 20, x + width / 2, y + 10)
    return button_clicked

def start_screen(screen):
    # Charger l'image de titre
    image_path = "/Users/souchaud/Documents/Autre/2024_11_26_anniv_anatole/resources/mission_joyeux_anniversaire.png"
    try:
        title_image = pygame.image.load(image_path).convert_alpha()
    except FileNotFoundError:
        print(f"Erreur: Le fichier image '{image_path}' est introuvable.")
        pygame.quit()
        sys.exit()

    # Redimensionner l'image si nécessaire (par exemple pour une largeur de 300 pixels)
    image_width = 300
    image_height = int(title_image.get_height() * (image_width / title_image.get_width()))
    title_image = pygame.transform.scale(title_image, (image_width, image_height))

    # Créer les étoiles et flocons de neige
    stars = create_stars(25)  # Étoiles
    snowflakes = create_snowflakes(100)  # Flocons de neige

    # Texte d'introduction
    intro_text = [
        "Bienvenue au jeu d'anniversaire!",
        "Aidez Mario a atteindre",
        "le score de 10 pour une surprise speciale!",
        "",
        "Utilisez la fleche du haut pour monter,",
        "et celle du bas pour descendre.",
        "Bonne chance!"
    ]

    while True:
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Fond bleu clair
        screen.fill((102, 190, 209))

        # Dessiner les étoiles et les flocons de neige
        draw_stars(screen, stars)
        update_and_draw_snowflakes(screen, snowflakes)

        # Afficher l'image de titre
        screen.blit(title_image, (SCREEN_WIDTH / 2 - title_image.get_width() / 2, SCREEN_HEIGHT / 10))

        # Afficher le texte explicatif sous l'image
        y_offset = SCREEN_HEIGHT / 3
        for line in intro_text:
            draw_text(screen, line, 15, SCREEN_WIDTH / 2, y_offset)
            y_offset += 30

        # Afficher le bouton "Commencer"
        if draw_button(screen, "Commencer", 125, 450, 150, 50):
            break

        # Rafraîchir l'écran
        pygame.display.flip()
        pygame.time.Clock().tick(15)

def game_over_screen(screen, final_score):

    # Charger l'image de titre
    image_path = "/Users/souchaud/Documents/Autre/2024_11_26_anniv_anatole/resources/Game_over.png"
    try:
        title_image = pygame.image.load(image_path).convert_alpha()
    except FileNotFoundError:
        print(f"Erreur: Le fichier image '{image_path}' est introuvable.")
        pygame.quit()
        sys.exit()

    # Redimensionner l'image si nécessaire (par exemple pour une largeur de 300 pixels)
    image_width = 300
    image_height = int(title_image.get_height() * (image_width / title_image.get_width()))
    title_image = pygame.transform.scale(title_image, (image_width, image_height))

    stars = create_stars(25)  # Création des étoiles
    snowflakes = create_snowflakes(100)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Dessiner le fond
        screen.fill((102, 190, 209))

        # Dessiner les étoiles et les flocons
        draw_stars(screen, stars)
        update_and_draw_snowflakes(screen, snowflakes)

        # Dessiner l'image de Game Over
        screen.blit(title_image, (SCREEN_WIDTH / 2 - title_image.get_width() / 2, SCREEN_HEIGHT / 4))

        # Afficher le score final
        score_text = f"Score Final: {final_score}"
        draw_text(screen, score_text, 36, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

        # Dessiner les boutons
        if draw_button(screen, "Rejouer", 100, 450, 100, 50):
            return True  # Indique de recommencer le jeu
        if draw_button(screen, "Quitter", 200, 450, 100, 50, color=(249, 24, 39)):
            return False  # Indique de quitter le jeu

        # Rafraîchir l'écran
        pygame.display.flip()
        pygame.time.Clock().tick(15)

def create_stars(num_stars):
    return [[random.randint(0, SCREEN_WIDTH),
             random.randint(0, SCREEN_HEIGHT)] for _ in range(num_stars)]

def draw_stars(screen, stars):
    for star in stars:
        pygame.draw.circle(screen, (255, 255, 0), star, random.randint(1, 3))

def wait_for_key():
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False

def play_video(screen, video_path):
    clip = VideoFileClip(video_path)
    clip = clip.resized(height=SCREEN_HEIGHT, width=SCREEN_WIDTH)
    clock = pygame.time.Clock()

    for frame in clip.iter_frames(fps=30, dtype="uint8"):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        screen.blit(frame_surface, (0, 0))
        pygame.display.update()
        clock.tick(30)
    clip.close()

def draw_pipe(screen, pipe_x, pipe_y, pipe_gap, brique_img, plante_img, has_plant):
    """
    Dessine un tuyau (pipe) constitué de briques et, éventuellement, d'une plante.

    Paramètres:
        - screen: Surface Pygame sur laquelle dessiner les tuyaux.
        - pipe_x: Position x du tuyau (en pixels).
        - pipe_y: Position y du bord supérieur du tuyau inférieur (en pixels).
        - pipe_gap: Espace vertical entre les deux tuyaux (en pixels).
        - brique_img: Image de la brique utilisée pour construire les tuyaux.
        - plante_img: Image de la plante (optionnelle) placée dans le tuyau supérieur.
        - has_plant: Booléen indiquant si une plante est présente dans le tuyau supérieur.

    Retourne:
        Aucun. La fonction dessine directement sur l'écran.
    """

    # Obtenir les dimensions des images (briques et plante)
    brique_height = brique_img.get_height()  # Hauteur d'une brique
    brique_width = brique_img.get_width()    # Largeur d'une brique
    plante_height = plante_img.get_height()  # Hauteur de la plante
    plante_width = plante_img.get_width()    # Largeur de la plante

    # Dessiner le tuyau supérieur (les briques à l'envers)
    # Initialiser la position verticale pour les briques du tuyau supérieur
    y_top = pipe_y - pipe_gap - brique_height  # Position initiale juste au-dessus de l'écart
    min_y_top = -brique_height                # Limite supérieure (hors écran)

    # Si une plante est présente, réduire le nombre de briques dans le tuyau supérieur
    if has_plant:
        min_y_top += 2 * brique_height  # Réduire de deux briques pour faire de la place à la plante

    # Boucle pour dessiner les briques du tuyau supérieur
    while y_top > min_y_top:  # Tant que la position est au-dessus de la limite
        # Dessiner une brique retournée (tuyau supérieur est inversé)
        screen.blit(pygame.transform.flip(brique_img, False, True), (pipe_x, y_top))
        y_top -= brique_height  # Remonter pour la prochaine brique

    # Dessiner le tuyau inférieur (les briques normales)
    # Initialiser la position verticale pour les briques du tuyau inférieur
    y_bottom = pipe_y

    # Boucle pour dessiner les briques du tuyau inférieur
    while y_bottom < SCREEN_HEIGHT:  # Tant que la position est en dessous de l'écran
        # Dessiner une brique normalement orientée
        screen.blit(brique_img, (pipe_x, y_bottom))
        y_bottom += brique_height  # Descendre pour la prochaine brique

    # Dessiner la plante si le tuyau supérieur contient une plante
    if has_plant:
        # Calculer la position de la plante dans le tuyau supérieur
        plant_x = pipe_x + (brique_width - plante_width) // 2  # Centrer horizontalement
        plant_y = pipe_y - plante_height                      # Juste au-dessus du bord supérieur
        # Dessiner la plante
        screen.blit(plante_img, (plant_x, plant_y))

def main():
    pygame.init()
    pygame.display.set_caption(app_name)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    start_screen(screen)

    # Initialisation des images
    bird_img = pygame.image.load('/Users/souchaud/Documents/Autre/2024_11_26_anniv_anatole/resources/mario_volant.png').convert_alpha()
    bird_img = pygame.transform.scale(bird_img, (50, 50))
    brique_img = pygame.image.load('/Users/souchaud/Documents/Autre/2024_11_26_anniv_anatole/resources/brique.png').convert_alpha()
    brique_img = pygame.transform.scale(brique_img, (50, 50))
    plante_img = pygame.image.load('/Users/souchaud/Documents/Autre/2024_11_26_anniv_anatole/resources/plante.png').convert_alpha()
    plante_img = pygame.transform.scale(plante_img, (50, 75))

    stars = create_stars(10)

    video_played = False
    last_speed_increase_score = 0

    running = True
    while running:
        bird_y = BIRD_Y
        bird_velocity = 0
        pipe_speed = PIPE_SPEED_INIT  # Assurez-vous que pipe_speed est défini ici

        # Calculer la position initiale du premier tuyau pour un délai de 3 secondes
        delay_seconds = 3
        frames_per_second = 30
        pipe_speed_per_second = -pipe_speed * frames_per_second  # pipe_speed est négatif
        distance = pipe_speed_per_second * delay_seconds
        initial_pipe_x = SCREEN_WIDTH + distance

        # Initialiser les tuyaux avec la nouvelle position
        pipes = [[initial_pipe_x, random.randint(100, 400), False,
                  random.randint(PIPE_GAP_MIN, PIPE_GAP_MAX), random.choice([True, False])]]

        score = 0
        snowflakes = create_snowflakes(25)

        GAP_MARGIN = 50  # Marge minimale pour le gap (en pixels)

        while running:
            # Gestion des événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        bird_velocity = FLAP_STRENGTH
                    elif event.key == pygame.K_DOWN:
                        bird_velocity = -FLAP_STRENGTH

            bird_velocity += GRAVITY
            bird_y += bird_velocity

            screen.fill((102, 190, 209))
            draw_stars(screen, stars)
            update_and_draw_snowflakes(screen, snowflakes)
            screen.blit(bird_img, (BIRD_X, bird_y))
            bird_rect = bird_img.get_rect(topleft=(BIRD_X, bird_y))

            # Gestion des tuyaux
            for pipe in pipes:
                pipe[0] += pipe_speed
                pipe_x, pipe_y, pipe_passed, pipe_gap, has_plant = pipe

                # Dessiner le tuyau
                draw_pipe(screen, pipe_x, pipe_y, pipe_gap, brique_img, plante_img, has_plant)

                # Générer de nouveaux tuyaux avec des contraintes sur pipe_y
                if pipe[0] < -50:
                    new_gap = random.randint(PIPE_GAP_MIN, PIPE_GAP_MAX)

                    # Assurez-vous que le gap respecte les marges
                    new_pipe_y = random.randint(
                        GAP_MARGIN + new_gap,  # Au moins GAP_MARGIN en dessous du haut
                        SCREEN_HEIGHT - GAP_MARGIN  # Au moins GAP_MARGIN au-dessus du bas
                    )
                    has_plant = random.choice([True, False])

                    pipes.append([400, new_pipe_y, False, new_gap, has_plant])
                    pipes.pop(0)

                # Vérifier si le tuyau a été passé pour augmenter le score
                if pipe[0] + brique_img.get_width() < BIRD_X and not pipe_passed:
                    score += 1
                    pipe[2] = True  # Marquer le tuyau comme passé

            # Détection des collisions
            for pipe in pipes:
                pipe_x, pipe_y, pipe_passed, pipe_gap, has_plant = pipe
                pipe_width = brique_img.get_width()
                brique_height = brique_img.get_height()

                # Calculer la hauteur du tuyau supérieur
                upper_pipe_height = pipe_y - pipe_gap
                if has_plant:
                    upper_pipe_height -= 2 * brique_height

                upper_pipe_rect = pygame.Rect(pipe_x, 0, pipe_width, upper_pipe_height)
                lower_pipe_rect = pygame.Rect(pipe_x, pipe_y, pipe_width, SCREEN_HEIGHT - pipe_y)

                if bird_rect.colliderect(upper_pipe_rect) or bird_rect.colliderect(lower_pipe_rect):
                    running = False
                    break

                if has_plant:
                    plante_rect = plante_img.get_rect()
                    plante_rect.x = pipe_x + (pipe_width - plante_img.get_width()) // 2
                    plante_rect.y = pipe_y - plante_img.get_height()
                    if bird_rect.colliderect(plante_rect):
                        running = False
                        break

            draw_text(screen, f"Score: {score}", 24, SCREEN_WIDTH - 100, 50)

            # Augmenter la vitesse des tuyaux
            if score // SCORE_INTERVAL_FOR_SPEED_INCREASE > last_speed_increase_score:
                pipe_speed -= 1
                last_speed_increase_score = score // SCORE_INTERVAL_FOR_SPEED_INCREASE

            # Jouer la vidéo lorsque le score atteint 10
            if score >= 1 and not video_played:
                play_video(screen, '/Users/souchaud/Documents/Autre/2024_11_26_anniv_anatole/resources/test_video.avi')
                video_played = True

            # Vérifier si l'oiseau est sorti de l'écran
            if bird_y >= SCREEN_HEIGHT - bird_img.get_height() or bird_y <= 0:
                running = False

            pygame.display.update()
            pygame.time.Clock().tick(frames_per_second)

        if not game_over_screen(screen, score):
            break  # Quitter si l'utilisateur choisit de ne pas rejouer

        running = True
        video_played = False

    pygame.quit()

if __name__ == "__main__":
    main()
