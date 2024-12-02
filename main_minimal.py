import pygame
import sys

def main():
    pygame.init()
    screen = pygame.display.set_mode((400, 600))
    pygame.display.set_caption("Test Minimal")
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill((255, 255, 255))
        pygame.display.flip()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()