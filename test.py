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
# map_image = pygame.image.load("mapa.png").convert()
# map_image = pygame.transform.scale(map_image, (MAP_SIZE*TILE_SIZE, MAP_SIZE*TILE_SIZE))

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
    
    illuminate(x + dx, y + dy, depth + 1, dx,dy)
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

class Enemy:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed
        self.active = False

    def update(self, target_x, target_y):
        if not self.active:
            return
        print("enemigo moviendose")
        dx = target_x - self.x
        dy = target_y - self.y

        move_x, move_y = 0, 0
        # Movimiento preferente: diagonal, luego horizontal, luego vertical
        if dx != 0:
            move_x = int(dx / abs(dx))
        if dy != 0:
            move_y = int(dy / abs(dy))

        # Probar movimiento diagonal
        new_x = self.x + move_x
        new_y = self.y + move_y
        if 0 <= new_x < MAP_SIZE and 0 <= new_y < MAP_SIZE and game_map[int(new_y)][int(new_x)][0] == 0:
            self.x = new_x
            self.y = new_y
            return

        # Probar movimiento horizontal
        new_x = self.x + move_x
        new_y = self.y
        if move_x != 0 and 0 <= new_x < MAP_SIZE and game_map[int(new_y)][int(new_x)][0] == 0:
            self.x = new_x
            return

        # Probar movimiento vertical
        new_x = self.x
        new_y = self.y + move_y
        if move_y != 0 and 0 <= new_y < MAP_SIZE and game_map[int(new_y)][int(new_x)][0] == 0:
            self.y = new_y
            return

    def draw(self, surface, offset_x, offset_y):
        if self.active:
            screen_x = (self.x - offset_x + CAMERA_RADIUS) * TILE_SIZE
            screen_y = (self.y - offset_y + CAMERA_RADIUS) * TILE_SIZE
            pygame.draw.rect(surface, (200, 0, 0), (screen_x, screen_y, TILE_SIZE, TILE_SIZE))

class Level:
    def __init__(self, map_data, bg_image_path, player_start, enemies_data, exit_pos):
        self.map_data = map_data  # matriz de paredes/exploradas
        self.bg_image = pygame.image.load(bg_image_path).convert()
        self.bg_image = pygame.transform.scale(self.bg_image, (MAP_SIZE*TILE_SIZE, MAP_SIZE*TILE_SIZE))
        self.player_start = player_start  # (x, y)
        self.enemies_data = enemies_data  # lista de tuplas (x, y, speed)
        self.exit_pos = exit_pos          # (x, y) posición de la salida

levels = [
    Level(
        map_data=example_map,
        bg_image_path="mapa1.png",
        player_start=(12, 12),
        enemies_data=[(5, 5, 1), (20, 18, 1)],
        exit_pos=(23, 23)
    ),
    Level(
        map_data=example_map,
        bg_image_path="mapa2.png",
        player_start=(2, 2),
        enemies_data=[(10, 10, 1)],
        exit_pos=(0, 24)
    ),
    # ...agrega más niveles aquí...
]

current_level = 0
exit_pos = levels[current_level].exit_pos

def load_level(level_index):
    global game_map, map_image, player_x, player_y, enemies, exit_pos
    lvl = levels[level_index]
    game_map = [[(cell[0], False) for cell in row] for row in lvl.map_data]
    map_image = lvl.bg_image
    player_x, player_y = lvl.player_start
    game_map[player_y][player_x] = (game_map[player_y][player_x][0], True)
    enemies = [Enemy(x, y, speed) for (x, y, speed) in lvl.enemies_data]
    exit_pos = lvl.exit_pos

def check_exit():
    global current_level
    if (player_x, player_y) == exit_pos:
        next_level()

def draw_map():
    global map_image
    """Dibuja el área visible con fog of war persistente + luz dinámica + degradado."""
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

                    # --- Degradado de niebla ---
                    dist = math.hypot(map_x - player_x, map_y - player_y)
                    if not visible:
                        # explorada pero no visible → sombra ligera
                        overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                        overlay.fill(DARK_EXPLORED)
                        screen.blit(overlay, (screen_x, screen_y))
                    else:
                        # visible: aplicar degradado según distancia
                        if dist > 0:
                            # calcula opacidad: cerca = transparente, lejos = más opaco
                            # opacidad máxima en el borde de la visión
                            alpha = int(90 * (dist / VISION_RADIUS))
                            alpha = max(0, min(alpha, 220))
                            if alpha > 0:
                                overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                                overlay.fill((0, 0, 0, alpha))
                                screen.blit(overlay, (screen_x, screen_y))
            # Dibujar la salida si está en pantalla
            if (map_x, map_y) == exit_pos:
                pygame.draw.rect(screen, (0, 255, 0), (screen_x, screen_y, TILE_SIZE, TILE_SIZE))

    # dibujar jugador
    center_x = CAMERA_RADIUS * TILE_SIZE
    center_y = CAMERA_RADIUS * TILE_SIZE
    pygame.draw.rect(screen, GREEN, (center_x, center_y, TILE_SIZE, TILE_SIZE))

    # dibujar enemigos
    for enemy in enemies:
        enemy.draw(screen, player_x, player_y)

def handle_input():
    global player_x, player_y
    keys = pygame.key.get_pressed()
    new_x, new_y = player_x, player_y
    
    if keys[pygame.K_UP] and player_y > 0:
        new_y -= 1
    elif keys[pygame.K_DOWN] and player_y < MAP_SIZE - 1:
        new_y += 1
    elif keys[pygame.K_LEFT] and player_x > 0:
        new_x -= 1
    elif keys[pygame.K_RIGHT] and player_x < MAP_SIZE - 1:
        new_x += 1

    pared, _ = game_map[new_y][new_x]
    if pared == 0 and (player_x != new_x or player_y != new_y):
        player_x, player_y = new_x, new_y
        
        for enemy in enemies:
            enemy.update(player_x, player_y)
            if game_map[enemy.y][enemy.x][1]:
                print("enemigo descubierto")
                enemy.active = True
        

game_state = "exploracion"  # Puede ser "exploracion" o "combate"
active_enemy = None         # Enemigo actual en combate
enemies = [
    Enemy(5, 5, 1),
    Enemy(20, 18, 1)
]
def check_combat():
    global game_state, active_enemy
    for enemy in enemies:
        if enemy.active and enemy.x == player_x and enemy.y == player_y:
            game_state = "combate"
            active_enemy = enemy
            break

def draw_combat_menu():
    # Fondo de combate
    screen.fill((30, 30, 30))
    font = pygame.font.SysFont(None, 32)
    # Título
    title = font.render("¡Combate!", True, (255, 0, 0))
    screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 40))
    # Opciones de menú
    options = ["1. Atacar", "2. Defender", "3. Huir"]
    for i, opt in enumerate(options):
        txt = font.render(opt, True, (255, 255, 255))
        screen.blit(txt, (screen.get_width()//2 - txt.get_width()//2, 120 + i*40))
    # Info del enemigo
    info = font.render(f"Enemigo en ({active_enemy.x}, {active_enemy.y})", True, (200, 0, 0))
    screen.blit(info, (screen.get_width()//2 - info.get_width()//2, 220))

def handle_combat_input():
    global game_state, active_enemy
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                # Atacar (ejemplo: eliminar enemigo y volver a exploración)
                enemies.remove(active_enemy)
                active_enemy = None
                # next_level()
                game_state = "exploracion"
            elif event.key == pygame.K_2:
                # Defender (puedes expandir lógica)
                game_state = "exploracion"
            elif event.key == pygame.K_3:
                # Huir (volver a exploración)
                game_state = "exploracion"



# Para pasar al siguiente nivel:
def next_level():
    global current_level
    current_level += 1
    if current_level < len(levels):
        load_level(current_level)
    else:
        print("¡Juego terminado!")
        pygame.quit()
        sys.exit()

def load_level(level_index):
    global game_map, map_image, player_x, player_y, enemies, exit_pos
    lvl = levels[level_index]
    game_map = [[(cell[0], False) for cell in row] for row in lvl.map_data]
    map_image = lvl.bg_image
    player_x, player_y = lvl.player_start
    game_map[player_y][player_x] = (game_map[player_y][player_x][0], True)
    enemies = [Enemy(x, y, speed) for (x, y, speed) in lvl.enemies_data]
    exit_pos = lvl.exit_pos

class Level:
    def __init__(self, map_data, bg_image_path, player_start, enemies_data, exit_pos):
        self.map_data = map_data  # matriz de paredes/exploradas
        self.bg_image = pygame.image.load(bg_image_path).convert()
        self.bg_image = pygame.transform.scale(self.bg_image, (MAP_SIZE*TILE_SIZE, MAP_SIZE*TILE_SIZE))
        self.player_start = player_start  # (x, y)
        self.enemies_data = enemies_data  # lista de tuplas (x, y, speed)
        self.exit_pos = exit_pos          # (x, y) posición de la salida

levels = [
    Level(
        map_data=example_map,
        bg_image_path="mapa1.png",
        player_start=(12, 12),
        enemies_data=[(5, 5, 1), (20, 18, 1)],
        exit_pos=(23, 23)
    ),
    Level(
        map_data=example_map,
        bg_image_path="mapa2.png",
        player_start=(2, 2),
        enemies_data=[(10, 10, 1)],
        exit_pos=(0, 23)
    ),
    # ...agrega más niveles aquí...
]

current_level = 0
exit_pos = levels[current_level].exit_pos
map_image = levels[current_level].bg_image
# Bucle principal
while True:
    if game_state == "exploracion":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        compute_visibility()
        draw_map()
        handle_input()
        check_combat()
        check_exit()
        pygame.display.flip()
        clock.tick(10)
    elif game_state == "combate":
        draw_combat_menu()
        handle_combat_input()
        pygame.display.flip()
        clock.tick(10)
