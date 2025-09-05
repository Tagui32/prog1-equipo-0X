import pygame
import sys
import math
import random
from map import generar_cuadrado
# Configuración inicial
pygame.init()
TILE_SIZE = 12
MAP_SIZE = 300
VISION_RADIUS = 10
CAMERA_RADIUS = 25
WINDOW_SIZE = CAMERA_RADIUS * 2 + 1

screen = pygame.display.set_mode((WINDOW_SIZE * TILE_SIZE, WINDOW_SIZE * TILE_SIZE))
pygame.display.set_caption("Juego con imagen de fondo y colisiones")

clock = pygame.time.Clock()

# Colores
GREEN = (0, 200, 0)
DARK = (30, 30, 30)
BLUE = (0, 0, 100)


# Cargar imagen de fondo del mapa (debe tener tamaño MAP_SIZE*TILE_SIZE)
map_image = pygame.image.load("map.png").convert()
map_image = pygame.transform.scale(map_image, (MAP_SIZE*TILE_SIZE, MAP_SIZE*TILE_SIZE))

# Generar mapa de colisiones (0 = suelo, 1 = pared)

# game_map = [[0 if random.random() > 0.2 else 1 for _ in range(MAP_SIZE)] for _ in range(MAP_SIZE)]
game_map = generar_cuadrado(MAP_SIZE)
# game_map = [[0 for _ in range(MAP_SIZE)] for _ in range(MAP_SIZE)]

player_x, player_y = MAP_SIZE // 2, MAP_SIZE // 2
game_map[player_y][player_x] = 0  # asegurar que no esté en una pared

def draw_map():
    """Dibuja el área visible de la imagen de fondo y aplica visión limitada."""
    screen.fill((0,0,0))

    for row in range(-CAMERA_RADIUS, CAMERA_RADIUS + 1):
        for col in range(-CAMERA_RADIUS, CAMERA_RADIUS + 1):
            map_x = player_x + col
            map_y = player_y + row
            screen_x = (col + CAMERA_RADIUS) * TILE_SIZE
            screen_y = (row + CAMERA_RADIUS) * TILE_SIZE

            # Solo dibujar si está dentro de los límites del mapa
            if 0 <= map_x < MAP_SIZE and 0 <= map_y < MAP_SIZE:
                rect = pygame.Rect(map_x*TILE_SIZE, map_y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                screen.blit(map_image, (screen_x, screen_y), rect)

                # Aplicar visión limitada
                dist = math.sqrt(col**2 + row**2)
                if dist > VISION_RADIUS:
                    overlay = pygame.Surface((TILE_SIZE, TILE_SIZE))
                    overlay.set_alpha(180)
                    overlay.fill((0,0,0))
                    screen.blit(overlay, (screen_x, screen_y))
            else:
                # Si estamos fuera del mapa, dibujar negro
                pygame.draw.rect(screen, (0,0,0), (screen_x, screen_y, TILE_SIZE, TILE_SIZE))

    # Dibujar jugador
    center_x = CAMERA_RADIUS * TILE_SIZE
    center_y = CAMERA_RADIUS * TILE_SIZE
    pygame.draw.rect(screen, (0,200,0), (center_x, center_y, TILE_SIZE, TILE_SIZE))


def handle_input():
    global player_x, player_y
    keys = pygame.key.get_pressed()
    new_x, new_y = player_x, player_y

    if keys[pygame.K_UP] and player_y > 0:
        new_y -= 1
    if keys[pygame.K_DOWN] and player_y < MAP_SIZE - 1:
        new_y += 1
    if keys[pygame.K_LEFT] and player_x > 0:
        new_x -= 1
    if keys[pygame.K_RIGHT] and player_x < MAP_SIZE - 1:
        new_x += 1

    # Solo mover si la casilla no es pared según la matriz
    if game_map[new_y][new_x] == 0:
        player_x, player_y = new_x, new_y

# Bucle principal
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    handle_input()
    draw_map()
    pygame.display.flip()
    clock.tick(10)
