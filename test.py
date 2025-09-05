import pygame
import sys
import random
import math
from map import example_map
# Configuración inicial
pygame.init()
TILE_SIZE = 32
MAP_SIZE = 25
VISION_RADIUS = 6   # radio de luz
CAMERA_RADIUS = 9
WINDOW_SIZE = CAMERA_RADIUS * 2 + 1

screen = pygame.display.set_mode((WINDOW_SIZE * TILE_SIZE, WINDOW_SIZE * TILE_SIZE))
pygame.display.set_caption("Juego con luz dinámica y paredes que bloquean visión")

clock = pygame.time.Clock()

# Colores
GREEN = (0, 200, 0)   # jugador
BROWN = (100, 60, 30) # pared
DARK_EXPLORED = (0, 0, 0, 150)  # sombra ligera
DARK_UNEXPLORED = (0, 0, 0, 255)  # completamente negro

# Cargar imagen de fondo (suelo)
map_image = pygame.image.load("mapa.png").convert()
map_image = pygame.transform.scale(map_image, (MAP_SIZE*TILE_SIZE, MAP_SIZE*TILE_SIZE))

# Generar mapa: (pared, explorada)
# game_map = [[(0 if random.random() > 0.2 else 1, False) for _ in range(MAP_SIZE)] for _ in range(MAP_SIZE)]
game_map = example_map
# Posición inicial del jugador
player_x, player_y = MAP_SIZE // 2, MAP_SIZE // 2
game_map[player_y][player_x] = (0, True)

# Guardamos visibilidad actual (True si la celda está iluminada este frame)
visible_tiles = [[False for _ in range(MAP_SIZE)] for _ in range(MAP_SIZE)]

def generar_direcciones():
    valores = [1, 0, -1]
    combinaciones = []
    for a in valores:
        for b in valores:
            combinaciones.append((a, b))
    combinaciones.remove((0,0))
    return combinaciones
    
def illuminate(x, y, depth, dx,dy):
    """Recursivamente propaga luz en dirección (dx, dy)."""
    if depth > VISION_RADIUS:
        return
    if not (0 <= x < MAP_SIZE and 0 <= y < MAP_SIZE):
        return

    pared, explorada = game_map[y][x]
    visible_tiles[y][x] = True
    game_map[y][x] = (pared, True)  # marcar como explorada

    if pared == 1:
        return  # la luz no pasa paredes

    # continuar propagando en la misma dirección
    # direcciones_restantes = directions.copy()
    
    illuminate(x + dx, y + dy, depth + 1, dx, dy)
    if dx != 0 and dy != 0:
        illuminate(x + dx, y, depth + 1, dx, 0)
        illuminate(x, y + dy, depth + 1, 0, dy)
    elif dx != 0 and dy == 0 or dx == 0 and dy != 0:
        illuminate(x + dx, y, depth + 2, dx, 0)
        illuminate(x, y + dy, depth + 2, 0, dy)

        

def compute_visibility():
    """Recalcula qué casillas son visibles con propagación recursiva."""
    global visible_tiles
    visible_tiles = [[False for _ in range(MAP_SIZE)] for _ in range(MAP_SIZE)]

    # iluminar la posición del jugador
    visible_tiles[player_y][player_x] = True
    game_map[player_y][player_x] = (game_map[player_y][player_x][0], True)

    # lanzar rayos en 360° alrededor del jugador
    

    
    directions = generar_direcciones()

    # for angle in range(0, 360, 5):  # cada 5 grados para mayor densidad
    #     rad = math.radians(angle)
    #     dx = round(math.cos(rad))
    #     dy = round(math.sin(rad))
    #     print(f"dx: {dx} dy: {dy}")
    #     if (dx, dy) != (0, 0) and (dx, dy) not in directions:
    #         directions.append((dx, dy))

    for dx, dy in directions:
        illuminate(player_x + dx, player_y + dy, 1, dx,dy)

def draw_map():
    """Dibuja el área visible con fog of war persistente + luz dinámica."""
    screen.fill((0, 0, 0))

    for row in range(-CAMERA_RADIUS, CAMERA_RADIUS + 1):
        for col in range(-CAMERA_RADIUS, CAMERA_RADIUS + 1):
            map_x = player_x + col
            map_y = player_y + row
            screen_x = (col + CAMERA_RADIUS) * TILE_SIZE
            screen_y = (row + CAMERA_RADIUS) * TILE_SIZE

            if 0 <= map_x < MAP_SIZE and 0 <= map_y < MAP_SIZE:
                pared, explorada = game_map[map_y][map_x]
                visible = visible_tiles[map_y][map_x]

                if not explorada:
                    # nunca explorada → negro total
                    pygame.draw.rect(screen, (0,0,0), (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                else:
                    # dibujar piso
                    rect = pygame.Rect(map_x*TILE_SIZE, map_y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    screen.blit(map_image, (screen_x, screen_y), rect)

                    # dibujar pared encima
                    if pared == 1:
                        pygame.draw.rect(screen, BROWN, (screen_x, screen_y, TILE_SIZE, TILE_SIZE))

                    if not visible:
                        # explorada pero no visible → sombra ligera
                        overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                        overlay.fill(DARK_EXPLORED)
                        screen.blit(overlay, (screen_x, screen_y))

    # dibujar jugador
    center_x = CAMERA_RADIUS * TILE_SIZE
    center_y = CAMERA_RADIUS * TILE_SIZE
    pygame.draw.rect(screen, GREEN, (center_x, center_y, TILE_SIZE, TILE_SIZE))

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

    pared, _ = game_map[new_y][new_x]
    if pared == 0:
        player_x, player_y = new_x, new_y

# Bucle principal
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    handle_input()
    compute_visibility()
    draw_map()
    pygame.display.flip()
    clock.tick(10)
