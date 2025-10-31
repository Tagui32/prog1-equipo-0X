import pygame
import sys
import random
import math
from map import example_map

# ----------------------------
# Configuración inicial
# ----------------------------
pygame.init()
TILE_SIZE = 32
MAP_SIZE = 25
VISION_RADIUS = 6   # radio de luz
CAMERA_RADIUS = 9
WINDOW_SIZE = CAMERA_RADIUS * 2 + 1

screen = pygame.display.set_mode((WINDOW_SIZE * TILE_SIZE, WINDOW_SIZE * TILE_SIZE))
pygame.display.set_caption("Juego algoritmos y estructuras de datos (sin clases)")

clock = pygame.time.Clock()

# Colores
GREEN = (0, 200, 0)   # jugador
BROWN = (100, 60, 30) # pared
DARK_EXPLORED = (0, 0, 0, 150)  # sombra ligera (alpha)
DARK_UNEXPLORED = (0, 0, 0, 255)  # totalmente negro (no usado directamente)

# ----------------------------
# Mapa y visibilidad
# ----------------------------
# game_map es una matriz de tuplas: (pared: 0/1, explorada: bool)
# Empezamos usando example_map como base de datos de paredes (0/1)
# Los niveles definirán game_map real más abajo.

visible_tiles = [[False for _ in range(MAP_SIZE)] for _ in range(MAP_SIZE)]

def generar_direcciones():
    valores = [1, 0, -1]
    combinaciones = []
    for a in valores:
        for b in valores:
            combinaciones.append((a, b))
    combinaciones.remove((0,0))
    return combinaciones

def illuminate(x, y, depth, dx, dy):
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

    # Propagar en la misma dirección
    illuminate(x + dx, y + dy, depth + 1, dx, dy)
    if dx != 0 and dy != 0:
        illuminate(x + dx, y, depth + 1, dx, 0)
        illuminate(x, y + dy, depth + 1, 0, dy)
    elif (dx != 0 and dy == 0) or (dx == 0 and dy != 0):
        illuminate(x + dx, y, depth + 2, dx, 0)
        illuminate(x, y + dy, depth + 2, 0, dy)

def compute_visibility():
    """Recalcula qué casillas son visibles con propagación recursiva."""
    global visible_tiles
    visible_tiles = [[False for _ in range(MAP_SIZE)] for _ in range(MAP_SIZE)]

    # iluminar la posición del jugador
    visible_tiles[player_y][player_x] = True
    game_map[player_y][player_x] = (game_map[player_y][player_x][0], True)

    directions = generar_direcciones()
    for dx, dy in directions:
        illuminate(player_x + dx, player_y + dy, 1, dx, dy)

# ----------------------------
# "Clases" convertidas a diccionarios + funciones
# ----------------------------
def crear_combatiente(ataque, defensa, vida):
    return {"ataque": ataque, "defensa": defensa, "vida": vida}

def crear_player(ataque=10, defensa=8, vida=30):
    p = crear_combatiente(ataque, defensa, vida)
    return p

def crear_enemigo(x, y, speed, ataque=8, defensa=6, vida=20):
    return {
        "x": x,
        "y": y,
        "speed": speed,
        "active": False,
        "ataque": ataque,
        "defensa": defensa,
        "vida": vida
    }

def actualizar_enemigo(enemy, target_x, target_y):
    """Comportamiento de movimiento del enemigo (igual a la clase)."""
    if not enemy["active"]:
        return
    dx = target_x - enemy["x"]
    dy = target_y - enemy["y"]

    move_x, move_y = 0, 0
    if dx != 0:
        move_x = int(dx / abs(dx))
    if dy != 0:
        move_y = int(dy / abs(dy))

    # diagonal
    new_x = enemy["x"] + move_x
    new_y = enemy["y"] + move_y
    if 0 <= new_x < MAP_SIZE and 0 <= new_y < MAP_SIZE and game_map[int(new_y)][int(new_x)][0] == 0:
        enemy["x"] = new_x
        enemy["y"] = new_y
        return

    # horizontal
    new_x = enemy["x"] + move_x
    new_y = enemy["y"]
    if move_x != 0 and 0 <= new_x < MAP_SIZE and game_map[int(new_y)][int(new_x)][0] == 0:
        enemy["x"] = new_x
        return

    # vertical
    new_x = enemy["x"]
    new_y = enemy["y"] + move_y
    if move_y != 0 and 0 <= new_y < MAP_SIZE and game_map[int(new_y)][int(new_x)][0] == 0:
        enemy["y"] = new_y
        return

def dibujar_enemigo(enemy, surface, offset_x, offset_y):
    if enemy["active"]:
        screen_x = (enemy["x"] - offset_x + CAMERA_RADIUS) * TILE_SIZE
        screen_y = (enemy["y"] - offset_y + CAMERA_RADIUS) * TILE_SIZE
        pygame.draw.rect(surface, (200, 0, 0), (screen_x, screen_y, TILE_SIZE, TILE_SIZE))

def crear_nivel(map_data, bg_image_path, player_start, enemies_data, exit_pos):
    bg_image = pygame.image.load(bg_image_path).convert()
    bg_image = pygame.transform.scale(bg_image, (MAP_SIZE*TILE_SIZE, MAP_SIZE*TILE_SIZE))
    return {
        "map_data": map_data,
        "bg_image": bg_image,
        "player_start": player_start,
        "enemies_data": enemies_data,
        "exit_pos": exit_pos
    }

# ----------------------------
# Niveles
# ----------------------------
levels = [
    # Nivel 1
    crear_nivel(
        map_data=example_map,
        bg_image_path="mapa1.png",
        player_start=(12, 12),
        enemies_data=[(5, 5, 1), (20, 18, 1), (10, 15, 1)],
        exit_pos=(23, 23)
    ),

    # Nivel 2
    crear_nivel(
        map_data=example_map,
        bg_image_path="mapa2.png",
        player_start=(2, 2),
        enemies_data=[(10, 10, 1), (8, 18, 1)],
        exit_pos=(0, 23)
    ),

    # Nivel 3
    crear_nivel(
        map_data=example_map,
        bg_image_path="mapa1.png",
        player_start=(5, 5),
        enemies_data=[(6, 10, 1), (15, 15, 2), (22, 7, 1)],
        exit_pos=(23, 0)
    ),

    # Nivel 4
    crear_nivel(
        map_data=example_map,
        bg_image_path="mapa2.png",
        player_start=(3, 22),
        enemies_data=[(7, 20, 2), (15, 5, 1), (22, 22, 1)],
        exit_pos=(23, 23)
    ),

    # Nivel 5
    crear_nivel(
        map_data=example_map,
        bg_image_path="mapa1.png",
        player_start=(12, 12),
        enemies_data=[(5, 5, 1), (10, 15, 2), (20, 5, 2)],
        exit_pos=(1, 23)
    ),

    # Nivel 6
    crear_nivel(
        map_data=example_map,
        bg_image_path="mapa2.png",
        player_start=(10, 10),
        enemies_data=[(5, 20, 1), (15, 15, 1), (22, 5, 3)],
        exit_pos=(23, 23)
    ),

    # Nivel 7
    crear_nivel(
        map_data=example_map,
        bg_image_path="mapa1.png",
        player_start=(0, 0),
        enemies_data=[(10, 10, 2), (12, 8, 2), (8, 12, 2)],
        exit_pos=(23, 23)
    )
]


# ----------------------------
# Estado global del juego
# ----------------------------
current_level = 0
game_state = "exploracion"  # "exploracion" o "combate"
active_enemy = None         # referencia al diccionario del enemigo en combate
combat_turn = "player"      # "player" o "enemy"
combat_log = ""

# Crear jugador como diccionario
player = crear_player(ataque=10, defensa=8, vida=30)
player_x, player_y = MAP_SIZE // 2, MAP_SIZE // 2

# Inicializamos variables que load_level rellenará:
game_map = None
map_image = None
enemies = []
exit_pos = None

# ----------------------------
# Funciones de carga de niveles y utilidades
# ----------------------------
def load_level(level_index):
    global game_map, map_image, player_x, player_y, enemies, exit_pos, current_level
    current_level = level_index
    lvl = levels[level_index]
    # clonamos la estructura del mapa para que todas las celdas comiencen como no exploradas
    game_map = [[(cell[0], False) for cell in row] for row in lvl["map_data"]]
    map_image = lvl["bg_image"]
    player_x, player_y = lvl["player_start"]
    game_map[player_y][player_x] = (game_map[player_y][player_x][0], True)
    enemies = [crear_enemigo(x, y, speed) for (x, y, speed) in lvl["enemies_data"]]
    exit_pos = lvl["exit_pos"]
    # Exponer variables globales
    globals().update({
        "game_map": game_map,
        "map_image": map_image,
        "player_x": player_x,
        "player_y": player_y,
        "enemies": enemies,
        "exit_pos": exit_pos
    })

def next_level():
    global current_level
    current_level += 1
    if current_level < len(levels):
        load_level(current_level)
    else:
        print("¡Juego terminado!")
        pygame.quit()
        sys.exit()

# ----------------------------
# Dibujo del mapa y HUD
# ----------------------------
def draw_map():
    global map_image
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
                    # dibujar piso desde la imagen del nivel
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
                            alpha = int(90 * (dist / VISION_RADIUS))
                            alpha = max(0, min(alpha, 220))
                            if alpha > 0:
                                overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                                overlay.fill((0, 0, 0, alpha))
                                screen.blit(overlay, (screen_x, screen_y))

            # Dibujar la salida si está en pantalla
            if (map_x, map_y) == exit_pos:
                pygame.draw.rect(screen, (0, 255, 0), (screen_x, screen_y, TILE_SIZE, TILE_SIZE))

    # dibujar jugador (en el centro)
    center_x = CAMERA_RADIUS * TILE_SIZE
    center_y = CAMERA_RADIUS * TILE_SIZE
    pygame.draw.rect(screen, GREEN, (center_x, center_y, TILE_SIZE, TILE_SIZE))

    # dibujar enemigos
    for enemy in enemies:
        dibujar_enemigo(enemy, screen, player_x, player_y)

# ----------------------------
# Entrada y actualización de estado
# ----------------------------
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
    if (pared == 0 or (new_x, new_y) == exit_pos) and (player_x != new_x or player_y != new_y):

        player_x_old, player_y_old = player_x, player_y
        player_x, player_y = new_x, new_y
        
        # actualizar enemigos (se mueven después del paso del jugador)
        for enemy in enemies:
            actualizar_enemigo(enemy, player_x, player_y)
            # si la celda del enemigo ya fue explorada, se activa
            if 0 <= enemy["y"] < MAP_SIZE and 0 <= enemy["x"] < MAP_SIZE:
                if game_map[enemy["y"]][enemy["x"]][1]:
                    # enemigo descubierto
                    enemy["active"] = True
                    # print("enemigo descubierto")  # debugging

# ----------------------------
# Chequeos (combate / salida)
# ----------------------------
def check_combat():
    global game_state, active_enemy
    for enemy in enemies:
        if enemy["active"] and enemy["x"] == player_x and enemy["y"] == player_y:
            game_state = "combate"
            active_enemy = enemy
            break

def check_exit():
    if (player_x, player_y) == exit_pos:
        next_level()

# ----------------------------
# Menú y lógica de combate
# ----------------------------
def draw_combat_menu():
    screen.fill((30, 30, 30))
    font = pygame.font.SysFont(None, 32)
    title = font.render("¡Combate!", True, (255, 0, 0))
    screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 40))

    options = ["1. Atacar", "2. Defender", "3. Huir"]
    for i, opt in enumerate(options):
        txt = font.render(opt, True, (255, 255, 255))
        screen.blit(txt, (screen.get_width()//2 - txt.get_width()//2, 120 + i*40))

    if active_enemy:
        info = font.render(f"Enemigo: Vida {active_enemy['vida']} | Atk {active_enemy['ataque']} | Def {active_enemy['defensa']}", True, (200, 0, 0))
        screen.blit(info, (screen.get_width()//2 - info.get_width()//2, 220))
    info2 = font.render(f"Jugador: Vida {player['vida']} | Atk {player['ataque']} | Def {player['defensa']}", True, (0, 200, 0))
    screen.blit(info2, (screen.get_width()//2 - info2.get_width()//2, 260))
    if combat_log:
        logtxt = font.render(combat_log, True, (255,255,0))
        screen.blit(logtxt, (screen.get_width()//2 - logtxt.get_width()//2, 320))

def combat_attack(attacker, defender):
    """Atacar entre diccionarios de combatientes."""
    global combat_log
    dice = random.randint(1, 20)
    porcentaje = random.randint(60, 100) / 100.0
    base_damage = math.ceil(attacker["ataque"] * porcentaje)
    log = f"Tira d20: {dice} + Atk {attacker['ataque']} vs Def {defender['defensa']}. "
    if dice == 1:
        self_damage = math.ceil(base_damage * 0.5)
        attacker["vida"] -= self_damage
        log += f"¡Pifia! El atacante se hiere por {self_damage}."
    elif dice == 20:
        if dice + attacker["ataque"] >= defender["defensa"]:
            damage = base_damage * 2
            defender["vida"] -= math.ceil(damage)
            log += f"¡Crítico! Daño doble: {math.ceil(damage)}."
        else:
            log += "¡Crítico pero no supera defensa!"
    elif dice + attacker["ataque"] >= defender["defensa"]:
        defender["vida"] -= base_damage
        log += f"Golpea y causa {base_damage} daño."
    else:
        log += "Falla el ataque."
    combat_log = log
    draw_combat_menu()
    pygame.time.delay(500)

def handle_combat_input():
    global game_state, active_enemy, combat_turn, combat_log
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and combat_turn == "player":
            if event.key == pygame.K_1:
                if active_enemy:
                    combat_attack(player, active_enemy)
                combat_turn = "enemy"
            elif event.key == pygame.K_2:
                combat_log = "El jugador se defiende (sin efecto por ahora)."
                combat_turn = "enemy"
            elif event.key == pygame.K_3:
                combat_log = "¡Huyes del combate!"
                game_state = "exploracion"
                combat_turn = "player"
                active_enemy = None

def handle_enemy_combat():
    global game_state, active_enemy, combat_turn, combat_log
    if active_enemy and combat_turn == "enemy":
        combat_attack(active_enemy, player)
        combat_turn = "player"
        # Chequear si alguien muere
        if player["vida"] <= 0:
            combat_log = "¡Has sido derrotado!"
            print("¡Has sido derrotado!")
            pygame.quit()
            sys.exit()
        elif active_enemy["vida"] <= 0:
            combat_log = "¡Enemigo derrotado!"
            print("¡Enemigo derrotado!")
            # eliminar enemigo de la lista
            try:
                enemies.remove(active_enemy)
            except ValueError:
                pass
            active_enemy = None
            game_state = "exploracion"
            combat_turn = "player"

# ----------------------------
# Inicialización de nivel y loop principal
# ----------------------------
# cargar primer nivel
load_level(0)

# marcar posición inicial explorada
game_map[player_y][player_x] = (game_map[player_y][player_x][0], True)

# enemigos iniciales ya creados en load_level; si querés enemigos globales por defecto:
# enemies = [crear_enemigo(5,5,1), crear_enemigo(20,18,1)]

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
        draw_combat_menu()
        pygame.display.flip()
        pygame.time.delay(500)
        handle_enemy_combat()
        pygame.display.flip()
        clock.tick(10)
