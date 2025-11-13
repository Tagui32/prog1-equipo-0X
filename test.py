# Requiere: pygame

import pygame
import sys
import random
import math
import json
import os
from collections import deque
from datetime import datetime

# ----------------------
# CONFIG
# ----------------------
TILE_SIZE = 32
MAP_SIZE = 25
VISION_RADIUS = 6
CAMERA_RADIUS = 9
WINDOW_TILES = CAMERA_RADIUS * 2 + 1
SCREEN_W = WINDOW_TILES * TILE_SIZE
SCREEN_H = WINDOW_TILES * TILE_SIZE + 120  # Aumenté el HUD de 96 a 120
FPS = 30

# Colors
COLOR_BG = (18, 18, 20)
COLOR_FLOOR = (40, 40, 50)
COLOR_WALL = (100, 70, 40)
COLOR_PLAYER = (0, 200, 90)
COLOR_PLAYER_SHADOW = (0, 80, 30)
COLOR_ENEMY = (200, 40, 40)
COLOR_ENEMY_SHADOW = (90, 30, 30)
COLOR_EXIT = (0, 180, 255)
COLOR_SHOP = (220, 180, 0)
COLOR_TEXT = (230, 230, 230)
FOG_EXPLORED = (0, 0, 0, 150)
FOG_UNEXPLORED = (0, 0, 0, 255)

pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Roguelike Mejorado - test.py")
clock = pygame.time.Clock()

# Fuentes más grandes
font = pygame.font.SysFont(None, 20)        # Era 18
bigfont = pygame.font.SysFont(None, 28)     # Era 24  
tinyfont = pygame.font.SysFont(None, 16)    # Era 14

# Archivos de guardado
SAVE_FILE = "save_game.json"
LEADERBOARD_FILE = "leaderboard.json"

# ----------------------
# CARGAR ENEMIGOS DESDE JSON
# ----------------------
def load_enemy_types():
    try:
        with open('enemies.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("ERROR: No se encontró el archivo enemies.json")
        # Datos por defecto en caso de error
        return {
            "Murciélago de Caverna": {
                "sprite": "Murciélago de Caverna.png",
                "dialogues": ["Tus pasos retumban como un tambor en mi cabeza.", "Los humanos nunca aprenden, siempre suben… o bajan.", "Tu sangre suena deliciosa.", "Podría volar lejos, pero prefiero desgarrarte."]
            },
            "Esqueleto del Abismo": {
                "sprite": "Esqueleto del Abismo.png", 
                "dialogues": ["Te escuché venir desde la otra sala, suenan tus pasos… vivos.", "¿Venís a unirte a nosotros?", "Antes fui un caballero, como vos.", "No hay victoria en este lugar, solo polvo."]
            },
            "Rata Gigante": {
                "sprite": "Rata Gigante.png",
                "dialogues": ["No todos los días la cena viene con armadura.", "Hueles a miedo.", "Deberías dejarme morderte, es tradición.", "¿Sabés lo que me costó encontrar comida acá abajo?"]
            },
            "Slime Sombrío": {
                "sprite": "SlimeSombrío.png",
                "dialogues": ["Glup... otro héroe. Qué sorpresa.", "Cada golpe tuyo me hace más grande.", "He comido mejores guerreros que vos.", "¿De verdad trajiste una espada? Soy gelatina."]
            },
            "Goblin Minero": {
                "sprite": "GoblingMinero.png", 
                "dialogues": ["Otra vez un tipo con espada? Pensé que ya se habían extinguido.", "Eh, no toques mi oro o te muerdo los dedos.", "Llevo toda la noche cavando y venís a molestar.", "No me subestimes, humano brillante."]
            }
        }
    except json.JSONDecodeError as e:
        print(f"ERROR: El archivo enemies.json tiene formato inválido: {e}")
        return {}

# Cargar los tipos de enemigos
ENEMY_TYPES = load_enemy_types()

# ----------------------
# CARGAR SPRITES
# ----------------------
# Cargar sprites de enemigos
enemy_sprites = {}
for enemy_type in ENEMY_TYPES.keys():
    try:
        sprite_path = f"sprites/{ENEMY_TYPES[enemy_type]['sprite']}"
        enemy_sprites[enemy_type] = pygame.image.load(sprite_path)
        # Escalar el sprite si es necesario (ajusta el tamaño según necesites)
        enemy_sprites[enemy_type] = pygame.transform.scale(enemy_sprites[enemy_type], (80, 80))
    except:
        print(f"Error cargando sprite: {sprite_path}")
        # Si no hay sprite, usaremos dibujos por defecto

# Cargar sprite del jugador
try:
    player_sprite = pygame.image.load("sprites/HeroSprite.png")
    player_sprite = pygame.transform.scale(player_sprite, (80, 80))
    print(f"Sprite del jugador cargado correctamente. Tamaño: {player_sprite.get_size()}")
except Exception as e:
    print(f"Error cargando sprite del jugador: {e}")
    player_sprite = None

# ----------------------
# GAME STATE
# ----------------------
game_map = None
visible = None
explored = None
map_rooms = []
player = None
enemies = []
exit_pos = (0,0)
shop_pos = None
game_state = "exploracion"   # or "combate" or "shop" or "gameover"
active_enemy = None
combat_log = ""
combat_turn = "player"
level_number = 1
escape_chance = 0.45
combat_log_timer = 0

# NUEVAS VARIABLES PARA EL SISTEMA DE GUARDADO Y PUNTAJE
enemies_killed = 0
total_score = 0
player_nickname = ""

# visual effects
particles = []   # each: dict {x,y,dx,dy,life,color,size}
floating_texts = []  # each: dict {x,y,text,color,life,vy}

# ----------------------
# SISTEMA DE GUARDADO
# ----------------------
def save_game():
    if not player_nickname or player is None or game_state == "gameover":
        return False
    
    # Guardar el estado completo del mapa y enemigos
    save_data = {
        'player': {
            'hp': player['hp'],
            'hp_max': player['hp_max'],
            'atk': player['atk'],
            'def': player['def'],
            'gold': player['gold'],
            'potions': player['potions'],
            'attack_buff': player.get('attack_buff', 0),
            'level': player.get('level', 1),
            'exp': player.get('exp', 0),
            'exp_to_next_level': player.get('exp_to_next_level', 15),
            'cd_strike': player['cd_strike'],
            'cd_arrow': player['cd_arrow'],
            'x': player['x'],
            'y': player['y']
        },
        'enemies': [
            {
                'x': e['x'], 'y': e['y'], 'hp': e['hp'], 'hp_max': e['hp_max'],
                'atk': e['atk'], 'def': e['def'], 'level': e['level'], 'type': e['type'],
                'active': e['active'], 'gold_drop': e.get('gold_drop', 0)
            }
            for e in enemies
        ],
        'game_map': game_map,  # <-- GUARDAR EL MAPA COMPLETO
        'exit_pos': exit_pos,
        'shop_pos': shop_pos,
        'enemies_killed': enemies_killed,
        'total_score': total_score,
        'level_reached': level_number,
        'player_nickname': player_nickname,
        'timestamp': datetime.now().isoformat()
    }
    try:
        with open(SAVE_FILE, 'w') as f:
            json.dump(save_data, f)
        print("Partida guardada correctamente")
        return True
    except Exception as e:
        print(f"Error guardando partida: {e}")
        return False

def load_game():
    try:
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error cargando partida: {e}")
    return None

def save_leaderboard_entry():
    if not player_nickname:
        return False
    
    try:
        leaderboard = []
        if os.path.exists(LEADERBOARD_FILE):
            with open(LEADERBOARD_FILE, 'r') as f:
                leaderboard = json.load(f)
        
        entry = {
            'nickname': player_nickname,
            'score': total_score,
            'level_reached': level_number,
            'enemies_killed': enemies_killed,
            'timestamp': datetime.now().isoformat()
        }
        
        leaderboard.append(entry)
        # Ordenar por puntaje (descendente)
        leaderboard.sort(key=lambda x: x['score'], reverse=True)
        # Mantener solo los top 10
        leaderboard = leaderboard[:10]
        
        with open(LEADERBOARD_FILE, 'w') as f:
            json.dump(leaderboard, f)
        print("Puntuación guardada en leaderboard")
        return True
    except Exception as e:
        print(f"Error guardando leaderboard: {e}")
        return False

def get_leaderboard():
    try:
        if os.path.exists(LEADERBOARD_FILE):
            with open(LEADERBOARD_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return []

# ----------------------
# UTIL / MAP GENERATOR
# ----------------------

def create_empty_map():
    return [[1 for _ in range(MAP_SIZE)] for _ in range(MAP_SIZE)]

def rooms_dungeon(rooms=6, room_min=3, room_max=7):
    dungeon = create_empty_map()
    room_list = []

    def intersects(r1, r2):
        x1,y1,x2,y2 = r1
        a1,b1,a2,b2 = r2
        return (x1 <= a2 and x2 >= a1 and y1 <= b2 and y2 >= b1)

    for _ in range(rooms*4):
        w = random.randint(room_min, room_max)
        h = random.randint(room_min, room_max)
        x = random.randint(1, MAP_SIZE - w - 2)
        y = random.randint(1, MAP_SIZE - h - 2)
        new_room = (x, y, x + w - 1, y + h - 1)
        if any(intersects(new_room, other) for other in room_list):
            continue
        for yy in range(new_room[1], new_room[3] + 1):
            for xx in range(new_room[0], new_room[2] + 1):
                if 0 <= xx < MAP_SIZE and 0 <= yy < MAP_SIZE:
                    dungeon[yy][xx] = 0
        if room_list:
            px, py = ((room_list[-1][0] + room_list[-1][2]) // 2,
                      (room_list[-1][1] + room_list[-1][3]) // 2)
            nx, ny = ((new_room[0] + new_room[2]) // 2,
                      (new_room[1] + new_room[3]) // 2)
            carve_corridor(dungeon, px, py, nx, ny)
        room_list.append(new_room)
        if len(room_list) >= rooms:
            break

    for _ in range((MAP_SIZE*MAP_SIZE)//50):
        rx = random.randint(1, MAP_SIZE-2)
        ry = random.randint(1, MAP_SIZE-2)
        if 0 <= rx < MAP_SIZE and 0 <= ry < MAP_SIZE:
            dungeon[ry][rx] = 0 if random.random() < 0.75 else 1

    return dungeon, room_list

def carve_corridor(dungeon, x1,y1,x2,y2):
    x1 = max(0, min(x1, len(dungeon[0])-1))
    y1 = max(0, min(y1, len(dungeon)-1))
    x2 = max(0, min(x2, len(dungeon[0])-1))
    y2 = max(0, min(y2, len(dungeon)-1))
    
    if random.random() < 0.5:
        for x in range(min(x1,x2), max(x1,x2)+1):
            if 0 <= x < len(dungeon[0]) and 0 <= y1 < len(dungeon):
                dungeon[y1][x] = 0
        for y in range(min(y1,y2), max(y1,y2)+1):
            if 0 <= x2 < len(dungeon[0]) and 0 <= y < len(dungeon):
                dungeon[y][x2] = 0
    else:
        for y in range(min(y1,y2), max(y1,y2)+1):
            if 0 <= x1 < len(dungeon[0]) and 0 <= y < len(dungeon):
                dungeon[y][x1] = 0
        for x in range(min(x1,x2), max(x1,x2)+1):
            if 0 <= x < len(dungeon[0]) and 0 <= y2 < len(dungeon):
                dungeon[y2][x] = 0

def random_free_cell_from_map(game_map):
    attempts = 0
    free_cells = []
    
    for y in range(1, MAP_SIZE - 1):
        for x in range(1, MAP_SIZE - 1):
            if game_map[y][x] == 0:
                free_cells.append((x, y))
    
    if free_cells:
        return random.choice(free_cells)
    
    for y in range(MAP_SIZE):
        for x in range(MAP_SIZE):
            if game_map[y][x] == 0:
                free_cells.append((x, y))
    
    if free_cells:
        return random.choice(free_cells)
    
    return (MAP_SIZE // 2, MAP_SIZE // 2)

# ----------------------
# PATHFINDING PARA VERIFICAR ACCESIBILIDAD
# ----------------------

def is_reachable(start, end, game_map):
    """Verifica si hay un camino entre start y end usando BFS"""
    if start == end:
        return True
    
    visited = set()
    queue = deque([start])
    visited.add(start)
    
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    
    while queue:
        x, y = queue.popleft()
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            
            if (0 <= nx < MAP_SIZE and 0 <= ny < MAP_SIZE and 
                game_map[ny][nx] != 1 and (nx, ny) not in visited):
                
                if (nx, ny) == end:
                    return True
                
                visited.add((nx, ny))
                queue.append((nx, ny))
    
    return False

def find_reachable_exit_position(player_pos, game_map, max_attempts=50):
    """Encuentra una posición de salida que sea alcanzable desde el jugador"""
    player_x, player_y = player_pos
    
    # Primero intentar con celdas lejanas
    candidate_cells = []
    for y in range(MAP_SIZE):
        for x in range(MAP_SIZE):
            if game_map[y][x] == 0:  # Es suelo
                distance = abs(x - player_x) + abs(y - player_y)
                if distance > 6:
                    candidate_cells.append((x, y, distance))
    
    # Ordenar por distancia (más lejanas primero)
    candidate_cells.sort(key=lambda cell: cell[2], reverse=True)
    
    # Probar las celdas más lejanas primero
    for x, y, dist in candidate_cells:
        if is_reachable(player_pos, (x, y), game_map):
            return (x, y)
    
    # Si no se encuentra una lejana, buscar cualquier celda alcanzable
    for y in range(MAP_SIZE):
        for x in range(MAP_SIZE):
            if game_map[y][x] == 0 and (x, y) != player_pos:
                if is_reachable(player_pos, (x, y), game_map):
                    return (x, y)
    
    # Último recurso: crear un camino forzado
    return create_forced_path(player_pos, game_map)

def create_forced_path(player_pos, game_map):
    """Crea un camino forzado desde el jugador hasta el borde del mapa"""
    player_x, player_y = player_pos
    
    # Encontrar la dirección hacia el borde más cercano
    if player_x < MAP_SIZE // 2:
        direction = (1, 0)  # Derecha
    else:
        direction = (-1, 0)  # Izquierda
    
    if player_y < MAP_SIZE // 2:
        direction = (0, 1)  # Abajo
    else:
        direction = (0, -1)  # Arriba
    
    # Crear camino
    x, y = player_x, player_y
    path = []
    
    for _ in range(min(10, max(MAP_SIZE - player_x, player_x, MAP_SIZE - player_y, player_y))):
        x += direction[0]
        y += direction[1]
        
        if not (0 <= x < MAP_SIZE and 0 <= y < MAP_SIZE):
            break
            
        # Convertir pared en suelo si es necesario
        if game_map[y][x] == 1:
            game_map[y][x] = 0
        
        path.append((x, y))
        
        # Si llegamos al borde, usar esta posición
        if x == 0 or x == MAP_SIZE-1 or y == 0 or y == MAP_SIZE-1:
            return (x, y)
    
    # Si no llegamos al borde, usar la última posición del camino
    if path:
        return path[-1]
    
    # Último recurso absoluto
    return (MAP_SIZE-2, MAP_SIZE-2)

def create_direct_path(start, end, game_map):
    """Crea un camino directo entre start y end"""
    start_x, start_y = start
    end_x, end_y = end
    
    # Primero mover en X, luego en Y
    x, y = start_x, start_y
    
    # Mover en dirección X
    while x != end_x:
        if x < end_x:
            x += 1
        else:
            x -= 1
        
        if 0 <= x < MAP_SIZE and 0 <= y < MAP_SIZE:
            if game_map[y][x] == 1:
                game_map[y][x] = 0
    
    # Mover en dirección Y
    while y != end_y:
        if y < end_y:
            y += 1
        else:
            y -= 1
        
        if 0 <= x < MAP_SIZE and 0 <= y < MAP_SIZE:
            if game_map[y][x] == 1:
                game_map[y][x] = 0
    
    return True

# ----------------------
# ENTITIES (dicts)
# ----------------------

def make_player(x,y):
    return {
        "x": x, "y": y,
        "hp": 40, "hp_max":40,
        "atk": 10, "def": 8,
        "gold": 0,
        "potions": 1,
        "attack_buff": 0,
        "speed": 6,
        "stun": 0,
        "cd_strike": 0,
        "cd_arrow": 0,
        "last_dir": (0, -1),
        "vx": 0.0, "vy": 0.0,
        "level": 1,
        "exp": 0,
        "exp_to_next_level": 15
    }

def make_enemy(x,y,level=1):
    # Elegir tipo de enemigo aleatorio
    enemy_type = random.choice(list(ENEMY_TYPES.keys()))
    enemy_data = ENEMY_TYPES[enemy_type]
    
    base_hp = random.randint(10, 16) + (level * 6)
    return {
        "x": x, "y": y,
        "hp": base_hp, "hp_max": base_hp,
        "atk": random.randint(6, 10) + (level * 2),
        "def": random.randint(4, 8) + (level * 1),
        "active": False,
        "level": level,
        "type": enemy_type,
        "sprite": enemy_data["sprite"],
        "dialogues": enemy_data["dialogues"],
        "current_dialogue": "",
        "gold_drop": random.randint(3, 10) + level,
        "patrol_dir": random.choice([(1,0),(-1,0),(0,1),(0,-1)]),
        "aggro_range": 6 + level//2,
        "stun": 0,
        "vx": 0.0, "vy": 0.0
    }

# ----------------------
# VISIBILITY (raycast-style)
# ----------------------

def generar_direcciones():
    valores = [1,0,-1]
    comb = []
    for a in valores:
        for b in valores:
            if (a,b) != (0,0):
                comb.append((a,b))
    return comb

def illuminate(x, y, depth, dx, dy):
    if depth > VISION_RADIUS:
        return
    if not (0 <= x < MAP_SIZE and 0 <= y < MAP_SIZE):
        return
    visible[y][x] = True
    explored[y][x] = True
    if game_map[y][x] == 1:
        return
    illuminate(x + dx, y + dy, depth+1, dx, dy)
    if dx != 0 and dy != 0:
        illuminate(x + dx, y, depth+1, dx, 0)
        illuminate(x, y + dy, depth+1, 0, dy)
    else:
        illuminate(x + dx, y, depth+2, dx, 0)
        illuminate(x, y + dy, depth+2, 0, dy)

def compute_visibility(px, py):
    global visible, explored
    visible = [[False for _ in range(MAP_SIZE)] for _ in range(MAP_SIZE)]
    if 0 <= px < MAP_SIZE and 0 <= py < MAP_SIZE:
        visible[py][px] = True
        explored[py][px] = True
    for dx,dy in generar_direcciones():
        illuminate(px + dx, py + dy, 1, dx, dy)

# ----------------------
# LEVEL LOADING / RESET
# ----------------------

def new_level(level=1, preserve_stats=True, generate_new_level=True):  # <-- AGREGAR PARÁMETRO
    global game_map, explored, visible, player, enemies, exit_pos, shop_pos, map_rooms
    global level_number, combat_log, game_state, active_enemy, particles
    global enemies_killed, total_score, player_nickname
    
    # PRESERVAR ESTADO DEL JUGADOR SOLO SI preserve_stats ES True
    old_player_stats = None
    if player is not None and preserve_stats:
        old_player_stats = {
            'hp': player['hp'],
            'hp_max': player['hp_max'],
            'atk': player['atk'],
            'def': player['def'],
            'gold': player['gold'],
            'potions': player['potions'],
            'attack_buff': player['attack_buff'],
            'level': player.get('level', 1),
            'exp': player.get('exp', 0),
            'exp_to_next_level': player.get('exp_to_next_level', 15),
            'cd_strike': player['cd_strike'],
            'cd_arrow': player['cd_arrow']
        }
    
    level_number = level
    combat_log = ""
    game_state = "exploracion"
    active_enemy = None
    particles.clear()
    floating_texts.clear()
    
    # RESETEAR CONTADORES SOLO EN NUEVA PARTIDA
    if not preserve_stats:
        enemies_killed = 0
        total_score = 0

    # SOLO GENERAR NUEVO NIVEL SI generate_new_level ES True
    if generate_new_level:
        dungeon, rooms = rooms_dungeon(rooms=max(4, min(10, 3 + level//2)), room_min=3, room_max=6)
        game_map = [[dungeon[y][x] for x in range(MAP_SIZE)] for y in range(MAP_SIZE)]
        map_rooms = rooms

        if rooms:
            r = random.choice(rooms)
            sx = (r[0] + r[2])//2
            sy = (r[1] + r[3])//2
        else:
            sx, sy = random_free_cell_from_map(dungeon)
        
        # CREAR NUEVO JUGADOR - RESTAURAR ESTADÍSTICAS SOLO SI SE DEBEN PRESERVAR
        if old_player_stats and preserve_stats:
            player = make_player(sx, sy)
            # RESTAURAR ESTADÍSTICAS
            player['hp'] = old_player_stats['hp']
            player['hp_max'] = old_player_stats['hp_max']
            player['atk'] = old_player_stats['atk']
            player['def'] = old_player_stats['def']
            player['gold'] = old_player_stats['gold']
            player['potions'] = old_player_stats['potions']
            player['attack_buff'] = old_player_stats['attack_buff']
            player['level'] = old_player_stats['level']
            player['exp'] = old_player_stats['exp']
            player['exp_to_next_level'] = old_player_stats['exp_to_next_level']
            player['cd_strike'] = old_player_stats['cd_strike']
            player['cd_arrow'] = old_player_stats['cd_arrow']
        else:
            player = make_player(sx, sy)

        enemies.clear()
        # ENEMIGOS MÁS DIFÍCILES EN NIVELES ALTOS
        num_en = random.randint(2 + level//2, 4 + int(level//1.5))
        
        # MEZCLA DE NIVELES DE ENEMIGOS
        for i in range(num_en):
            ex, ey = random_free_cell_from_map(dungeon)
            if (ex,ey) == (player["x"], player["y"]): continue
            
            # Algunos enemigos del nivel actual, otros de nivel superior
            enemy_level = level
            if random.random() < 0.3:  # 30% de chance de enemigo más fuerte
                enemy_level = min(level + 1, level + 2)  # Máximo 2 niveles arriba
            
            enemies.append(make_enemy(ex, ey, level=enemy_level))

        # GENERACIÓN ROBUSTA DE SALIDA - MEJORADA CON PATHFINDING
        exit_found = False
        
        # Usar pathfinding para encontrar una posición alcanzable
        exit_candidate = find_reachable_exit_position((player["x"], player["y"]), game_map)
        
        if exit_candidate:
            exit_x, exit_y = exit_candidate
            exit_pos = (exit_x, exit_y)
            game_map[exit_y][exit_x] = 3
            exit_found = True
            print(f"Salida colocada en posición alcanzable: ({exit_x}, {exit_y})")
        
        # Verificación de que la salida es realmente alcanzable
        if exit_found and not is_reachable((player["x"], player["y"]), exit_pos, game_map):
            print("ADVERTENCIA: La salida no es alcanzable, forzando conexión...")
            # Crear un camino directo
            create_direct_path((player["x"], player["y"]), exit_pos, game_map)
        
        # Estrategia de respaldo si todo falla
        if not exit_found:
            print("ERROR: No se pudo colocar salida. Usando posición por defecto.")
            # Buscar cualquier celda libre cerca del jugador
            for distance in range(1, 10):
                for dx in range(-distance, distance + 1):
                    for dy in range(-distance, distance + 1):
                        if abs(dx) + abs(dy) == distance:
                            x, y = player["x"] + dx, player["y"] + dy
                            if (0 <= x < MAP_SIZE and 0 <= y < MAP_SIZE and 
                                game_map[y][x] == 0):
                                exit_pos = (x, y)
                                game_map[y][x] = 3
                                exit_found = True
                                print(f"Salida de emergencia en: ({x}, {y})")
                                break
                    if exit_found:
                        break
                if exit_found:
                    break
        
        # Último recurso absoluto
        if not exit_found:
            print("CRÍTICO: Creando salida forzada en (1,1)")
            exit_pos = (1, 1)
            game_map[1][1] = 3
            exit_found = True

        # Tienda (igual que antes)
        shop_found = False
        if random.random() < 0.6 or level % 3 == 0:
            attempts = 0
            while attempts < 100:
                sx2, sy2 = random_free_cell_from_map(dungeon)
                if (0 <= sx2 < MAP_SIZE and 0 <= sy2 < MAP_SIZE and 
                    (sx2, sy2) not in [(player["x"], player["y"]), exit_pos]):
                    shop_pos = (sx2, sy2)
                    game_map[sy2][sx2] = 2
                    shop_found = True
                    break
                attempts += 1
        else:
            shop_pos = None

        explored = [[False for _ in range(MAP_SIZE)] for _ in range(MAP_SIZE)]
        visible = [[False for _ in range(MAP_SIZE)] for _ in range(MAP_SIZE)]
        compute_visibility(player["x"], player["y"])
        
        print(f"Nivel {level} generado. Salida en: {exit_pos}")
    
    # Guardar progreso automáticamente (solo si se generó nuevo nivel o es continuación)
    if player_nickname:
        save_game()


# ----------------------
# RENDERING
# ----------------------

def draw_map(surface, interp=1.0):
    surface.fill(COLOR_BG)
    px = player["x"]
    py = player["y"]
    for row in range(-CAMERA_RADIUS, CAMERA_RADIUS + 1):
        for col in range(-CAMERA_RADIUS, CAMERA_RADIUS + 1):
            mx = px + col
            my = py + row
            sx = (col + CAMERA_RADIUS) * TILE_SIZE
            sy = (row + CAMERA_RADIUS) * TILE_SIZE
            if 0 <= mx < MAP_SIZE and 0 <= my < MAP_SIZE:
                tile = game_map[my][mx]
                if tile == 1:
                    pygame.draw.rect(surface, COLOR_WALL, (sx, sy, TILE_SIZE, TILE_SIZE))
                    pygame.draw.line(surface, (70,50,30), (sx+2,sy+2),(sx+TILE_SIZE-4, sy+TILE_SIZE-6),1)
                elif tile == 0:
                    pygame.draw.rect(surface, COLOR_FLOOR, (sx, sy, TILE_SIZE, TILE_SIZE))
                elif tile == 2:
                    pygame.draw.rect(surface, COLOR_FLOOR, (sx, sy, TILE_SIZE, TILE_SIZE))
                    pygame.draw.rect(surface, COLOR_SHOP, (sx+4, sy+4, TILE_SIZE-8, TILE_SIZE-8), border_radius=4)
                elif tile == 3:
                    pygame.draw.rect(surface, COLOR_FLOOR, (sx, sy, TILE_SIZE, TILE_SIZE))
                    pygame.draw.rect(surface, COLOR_EXIT, (sx+6, sy+6, TILE_SIZE-12, TILE_SIZE-12), border_radius=6)

                for e in enemies:
                    if e["x"] == mx and e["y"] == my:
                        if not explored[my][mx] and not e["active"]:
                            pass
                        else:
                            ex = sx + TILE_SIZE//2 + int(e["vx"] * TILE_SIZE * interp)
                            ey = sy + TILE_SIZE//2 + int(e["vy"] * TILE_SIZE * interp)
                            pygame.draw.circle(surface, COLOR_ENEMY_SHADOW, (ex, ey+8), 12)
                            pygame.draw.circle(surface, COLOR_ENEMY, (ex, ey), 10)
                            lvl = tinyfont.render(f"{e['level']}", True, (20,20,20))
                            surface.blit(lvl, (ex - lvl.get_width()//2, ey - 6))

                if not explored[my][mx]:
                    overlay = pygame.Surface((TILE_SIZE, TILE_SIZE))
                    overlay.fill((0,0,0))
                    surface.blit(overlay, (sx, sy))
                else:
                    if not visible[my][mx]:
                        overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                        overlay.fill(FOG_EXPLORED)
                        surface.blit(overlay, (sx, sy))
                    else:
                        dist = math.hypot(mx - px, my - py)
                        if dist > 0:
                            alpha = int(90 * (dist / VISION_RADIUS))
                            alpha = max(0, min(alpha, 200))
                            if alpha > 0:
                                overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                                overlay.fill((0,0,0, alpha))
                                surface.blit(overlay, (sx, sy))
            else:
                pygame.draw.rect(surface, (0,0,0), (sx, sy, TILE_SIZE, TILE_SIZE))

    # Dibujar jugador en el mapa - CUADRADO VERDE ORIGINAL
    center_x = CAMERA_RADIUS * TILE_SIZE + TILE_SIZE//2 + int(player["vx"] * TILE_SIZE * interp)
    center_y = CAMERA_RADIUS * TILE_SIZE + TILE_SIZE//2 + int(player["vy"] * TILE_SIZE * interp)
    
    # REPRESENTACIÓN ORIGINAL (cuadrado verde sin sprite)
    pygame.draw.ellipse(surface, COLOR_PLAYER_SHADOW, (center_x-12, center_y+8, 24, 10))
    pygame.draw.rect(surface, COLOR_PLAYER, (center_x-10, center_y-10, 20, 20), border_radius=4)
    

    for ft in floating_texts:
        txt = tinyfont.render(ft["text"], True, ft["color"])
        surface.blit(txt, ( (ft["x"] - px) * TILE_SIZE + CAMERA_RADIUS * TILE_SIZE - txt.get_width()//2,
                   (ft["y"] - py) * TILE_SIZE + CAMERA_RADIUS * TILE_SIZE - 10 ))



def draw_hud(surface):
    global combat_log, combat_log_timer
    
    hud_y = WINDOW_TILES * TILE_SIZE
    # Fondo del HUD más oscuro para mejor contraste
    pygame.draw.rect(surface, (15, 15, 20), (0, hud_y, SCREEN_W, SCREEN_H - hud_y))
    
    # Línea divisoria
    pygame.draw.line(surface, (60, 60, 80), (0, hud_y), (SCREEN_W, hud_y), 2)
    
    # ===== SECCIÓN DE ESTADÍSTICAS PRINCIPALES =====
    stats_section_y = hud_y + 8
    
    # Línea 1: Información básica del jugador
    line1 = f"Jugador: {player_nickname} | Nivel: {player.get('level', 1)} | Vida: {player['hp']}/{player['hp_max']}"
    txt1 = font.render(line1, True, COLOR_TEXT)
    surface.blit(txt1, (10, stats_section_y))
    
    # Barra de vida visual
    hp_pct = player['hp'] / player['hp_max']
    hp_bar_width = 200
    pygame.draw.rect(surface, (40, 40, 40), (10, stats_section_y + 20, hp_bar_width, 12))
    pygame.draw.rect(surface, (220, 60, 60) if hp_pct < 0.3 else (60, 200, 80), 
                    (10, stats_section_y + 20, int(hp_bar_width * hp_pct), 12))
    hp_text = tinyfont.render(f"{player['hp']}/{player['hp_max']} HP", True, (240, 240, 240))
    surface.blit(hp_text, (15, stats_section_y + 22))
    
    # Línea 2: Experiencia y recursos
    exp_percentage = (player['exp'] / player['exp_to_next_level']) * 100 if player['exp_to_next_level'] > 0 else 0
    line2 = f"EXP: {player.get('exp', 0)}/{player.get('exp_to_next_level', 15)} ({exp_percentage:.0f}%) | Oro: {player['gold']} | Pociones: {player['potions']}"
    txt2 = font.render(line2, True, COLOR_TEXT)
    surface.blit(txt2, (10, stats_section_y + 40))
    
    # Barra de experiencia
    exp_pct = player['exp'] / player['exp_to_next_level'] if player['exp_to_next_level'] > 0 else 0
    exp_bar_width = 200
    pygame.draw.rect(surface, (40, 40, 40), (10, stats_section_y + 58, exp_bar_width, 8))
    pygame.draw.rect(surface, (100, 200, 255), (10, stats_section_y + 58, int(exp_bar_width * exp_pct), 8))
    
    # Línea 3: Progreso del juego
    line3 = f"Piso: {level_number} | Enemigos: {enemies_killed} | Puntos: {total_score}"
    txt3 = font.render(line3, True, COLOR_TEXT)
    surface.blit(txt3, (10, stats_section_y + 72))
    
    # ===== SECCIÓN DE HABILIDADES Y COOLDOWNS =====
    skills_section_x = SCREEN_W - 320
    skills_section_y = hud_y + 8
    
    # Título de habilidades
    skills_title = font.render("HABILIDADES", True, (200, 200, 255))
    surface.blit(skills_title, (skills_section_x, skills_section_y))
    
    # CD_LINES CORREGIDO - SIN CARACTERES ESPECIALES PROBLEMÁTICOS
    arrow_status = "LISTA" if player['cd_arrow'] == 0 else f"CD {player['cd_arrow']}"
    strike_status = "LISTO" if player['cd_strike'] == 0 else f"CD {player['cd_strike']}"
    
    cd_lines = [
        f"[A] Flecha: {arrow_status}",
        f"[Z] Golpe Fuerte: {strike_status}",
        f"[P] Poción: {player['potions']} disp.",
    ]
    
    for i, line in enumerate(cd_lines):
        # Colores diferentes según el estado
        if "LIST" in line:
            color = (100, 255, 100)  # Verde para habilidades listas
        elif "CD" in line:
            color = (255, 200, 100)  # Amarillo/naranja para en cooldown
        elif "Poción" in line:
            color = (100, 200, 255)  # Azul para pociones
        elif "Buff" in line:
            color = (255, 100, 255) if player.get('attack_buff', 0) > 0 else (180, 180, 200)  # Rosa si está activo
        else:
            color = (200, 200, 200)  # Gris por defecto
            
        cd_text = font.render(line, True, color)
        surface.blit(cd_text, (skills_section_x, skills_section_y + 25 + i * 20))
    
    # ===== LOG DE COMBATE =====
    if combat_log and combat_log_timer > 0:
        log_bg = pygame.Surface((SCREEN_W - 20, 30), pygame.SRCALPHA)
        log_bg.fill((0, 0, 0, 180))
        surface.blit(log_bg, (10, hud_y - 35))
        
        logtxt = bigfont.render(combat_log, True, (255, 220, 100))
        surface.blit(logtxt, (SCREEN_W // 2 - logtxt.get_width() // 2, hud_y - 30))

# ----------------------
# MENU DE PAUSA
# ----------------------

def show_pause_menu():
    global game_state
    
    # Crear overlay semi-transparente
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    # Panel del menú de pausa
    panel_width = 400
    panel_height = 250
    panel_x = (SCREEN_W - panel_width) // 2
    panel_y = (SCREEN_H - panel_height) // 2
    
    pygame.draw.rect(screen, (30, 35, 50), 
                   (panel_x, panel_y, panel_width, panel_height), 
                   border_radius=15)
    pygame.draw.rect(screen, (100, 200, 255), 
                   (panel_x, panel_y, panel_width, panel_height), 
                   3, border_radius=15)
    
    # Título
    title = bigfont.render("MENU DE PAUSA", True, (255, 215, 0))
    screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, panel_y + 30))
    
    # Botones
    button_width = 300
    button_height = 40
    button_x = (SCREEN_W - button_width) // 2
    
    continuar_btn = pygame.Rect(button_x, panel_y + 80, button_width, button_height)
    menu_principal_btn = pygame.Rect(button_x, panel_y + 140, button_width, button_height)
    salir_btn = pygame.Rect(button_x, panel_y + 200, button_width, button_height)
    
    # Dibujar botones
    for btn, text, y_offset in [(continuar_btn, "CONTINUAR", 80), 
                               (menu_principal_btn, "MENU PRINCIPAL", 140),
                               (salir_btn, "SALIR DEL JUEGO", 200)]:
        color = (70, 90, 110) if btn.collidepoint(pygame.mouse.get_pos()) else (50, 70, 90)
        pygame.draw.rect(screen, color, btn, border_radius=8)
        pygame.draw.rect(screen, (100, 200, 255), btn, 2, border_radius=8)
        
        text_surf = font.render(text, True, (200, 200, 220))
        screen.blit(text_surf, (btn.centerx - text_surf.get_width() // 2, 
                              btn.centery - text_surf.get_height() // 2))
    
    pygame.display.flip()
    
    # Esperar input del usuario
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "continue"
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                
                if continuar_btn.collidepoint(mouse_pos):
                    return "continue"
                elif menu_principal_btn.collidepoint(mouse_pos):
                    return "menu"
                elif salir_btn.collidepoint(mouse_pos):
                    return "quit"
        
        clock.tick(60)
    
    return "continue"

# ----------------------
# DAMAGE / COMBAT LOGIC
# ----------------------

def calc_damage(attacker, defender, power=1.0, is_crit=False):
    base = attacker['atk'] * power
    variance = random.uniform(0.85, 1.15)
    raw = base * variance
    mit = defender['def'] / (defender['def'] + 20)
    dmg = max(1, int(raw * (1 - mit)))
    if is_crit:
        dmg = int(dmg * 1.8)
    return dmg

def roll_hit_and_crit(attacker, defender):
    hit_chance = 0.75 + (attacker['atk'] - defender['def']) * 0.015
    hit_chance = max(0.2, min(0.98, hit_chance))
    if random.random() > hit_chance:
        return False, False
    dodge = max(0.02, min(0.35, (defender.get('speed',4) - attacker.get('speed',4)) * 0.03 + 0.05))
    if random.random() < dodge:
        return False, False
    crit_chance = 0.06 + (attacker['atk'] * 0.008)
    crit = (random.random() < crit_chance)
    return True, crit

def apply_status_ticks(entity):
    if entity.get('bleed',0) > 0:
        dmg = max(1, int(entity['hp_max'] * 0.03))
        entity['hp'] -= dmg
        entity['bleed'] -= 1

# ----------------------
# MOVEMENT & AI
# ----------------------

def try_move_player(dx, dy):
    global game_state
    if game_state != "exploracion":
        return
    if player.get("stun",0) > 0:
        return
    nx = player['x'] + dx
    ny = player['y'] + dy
    if not (0 <= nx < MAP_SIZE and 0 <= ny < MAP_SIZE): return
    tile = game_map[ny][nx]
    if tile == 1: return
    player['x'], player['y'] = nx, ny
    player['last_dir'] = (dx, dy) if (dx,dy) != (0,0) else player['last_dir']
    player['vx'] = dx * 0.25
    player['vy'] = dy * 0.25
    compute_visibility(player['x'], player['y'])
    for e in enemies:
        if visible[e['y']][e['x']]:
            e['active'] = True
    for e in enemies:
        if e['x'] == player['x'] and e['y'] == player['y'] and e['active']:
            start_combat(e)
            return
    if shop_pos and (player['x'], player['y']) == shop_pos:
        pass
    if (player['x'], player['y']) == exit_pos:
        new_level(level_number + 1, preserve_stats=True)

def move_enemies_ai():
    for e in enemies:
        if e.get('stun',0) > 0:
            e['stun'] -= 1
            continue
        d = abs(e['x'] - player['x']) + abs(e['y'] - player['y'])
        if d <= e['aggro_range'] and (visible[e['y']][e['x']] or e['active']):
            e['active'] = True
            dx = player['x'] - e['x']
            dy = player['y'] - e['y']
            mvx = (dx > 0) - (dx < 0)
            mvy = (dy > 0) - (dy < 0)
            attempts = [(mvx, mvy), (mvx,0),(0,mvy)]
            random.shuffle(attempts)
            moved = False
            for ax,ay in attempts:
                nx = e['x'] + ax
                ny = e['y'] + ay
                if 0 <= nx < MAP_SIZE and 0 <= ny < MAP_SIZE and game_map[ny][nx] != 1:
                    if not any((other['x']==nx and other['y']==ny) for other in enemies if other is not e):
                        e['x'], e['y'] = nx, ny
                        e['vx'] = ax * 0.2
                        e['vy'] = ay * 0.2
                        moved = True
                        break
            if not moved:
                ax,ay = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
                nx = e['x'] + ax; ny = e['y'] + ay
                if 0 <= nx < MAP_SIZE and 0 <= ny < MAP_SIZE and game_map[ny][nx] != 1:
                    if not any((other['x']==nx and other['y']==ny) for other in enemies if other is not e):
                        e['x'], e['y'] = nx, ny
            if e['x'] == player['x'] and e['y'] == player['y']:
                start_combat(e)

# ----------------------
# COMBAT
# ----------------------

def combat_attack(attacker, defender, power=1.0, status_apply=None):
    hit, crit = roll_hit_and_crit(attacker, defender)
    if not hit:
        if random.random() < 0.1:
            return ("¡Fallo crítico! No conectas.", 0, False)
        return ("Falla el ataque.", 0, False)
    dmg = calc_damage(attacker, defender, power=power, is_crit=crit)
    defender['hp'] -= dmg
    log = f"Infliges {dmg} daño."
    if crit:
        log = "¡Crítico! " + log
    if status_apply:
        for k,v in status_apply.items():
            defender[k] = defender.get(k,0) + v
    return (log, dmg, True)

def start_combat(enemy):
    global game_state, active_enemy, combat_turn, combat_log, escape_chance
    game_state = "combate"
    active_enemy = enemy
    combat_turn = "player"
    
    # Elegir diálogo aleatorio para este enemigo
    enemy["current_dialogue"] = random.choice(enemy["dialogues"])
    
    combat_log = f"Combate contra {enemy['type'].capitalize()} nivel {enemy['level']}"
    escape_chance = 0.45

def end_combat(victor):
    global game_state, active_enemy, combat_log
    global enemies_killed, total_score
    
    if victor == 'player':
        # Contar enemigo eliminado
        enemies_killed += 1
        
        # Calcular puntos (nivel del enemigo * 1 punto base)
        enemy_points = active_enemy['level']
        total_score += enemy_points
        
        # Dar experiencia balanceada
        exp_gained = max(5, active_enemy['level'] * 6)
        gain_experience(exp_gained)
        
        combat_log = f"Has derrotado al enemigo. +{exp_gained} EXP"
        g = active_enemy.get('gold_drop', 0)
        player['gold'] += g
        combat_log += f" (+{g} oro)"
        
        # Mostrar puntos ganados
        try:
            enemies.remove(active_enemy)
        except ValueError:
            pass
        active_enemy = None
        game_state = "exploracion"
        
        # Guardar progreso después de cada combate
        if player_nickname:
            save_game()
            
    elif victor == 'enemy':
        # Guardar puntaje final cuando el jugador muere
        if player_nickname:
            save_leaderboard_entry()
        
        # ELIMINAR ARCHIVO DE GUARDADO AL MORIR
        try:
            if os.path.exists(SAVE_FILE):
                os.remove(SAVE_FILE)
                print("Partida eliminada por Game Over")
        except Exception as e:
            print(f"Error eliminando partida: {e}")
            
        combat_log = "Has sido derrotado..."
        game_state = "gameover"

def handle_player_combat_input(key):
    global combat_turn, combat_log, active_enemy, game_state
    global escape_chance
    
    if combat_turn != "player" or not active_enemy:
        return
    if player.get('stun',0) > 0:
        player['stun'] -= 1
        combat_turn = "enemy"
        return
        
    if key == pygame.K_1:
        # light attack
        log, dmg, hit = combat_attack(player, active_enemy, power=1.0)
        combat_log = log
        # Verificar si el enemigo murió
        if active_enemy['hp'] <= 0:
            end_combat('player')
        else:
            combat_turn = "enemy"
            
    elif key == pygame.K_2:
        # defend
        combat_log = "Te defiendes: +6 defensa por 1 turno."
        player['def_backup'] = player['def']
        player['def'] += 6
        player['def_turns'] = 1
        combat_turn = "enemy"
        
    elif key == pygame.K_3:
        # attempt flee with progressive chance
        if random.random() < escape_chance:
            combat_log = "¡Huyes exitosamente!"
            for dx,dy in [(0,-1),(0,1),(-1,0),(1,0)]:
                nx = player['x'] + dx
                ny = player['y'] + dy
                if 0 <= nx < MAP_SIZE and 0 <= ny < MAP_SIZE and game_map[ny][nx] != 1 and not any(e['x']==nx and e['y']==ny for e in enemies):
                    player['x'], player['y'] = nx, ny
                    break
            active_enemy = None
            game_state = "exploracion"
            combat_turn = "player"
            escape_chance = 0.45
        else:
            combat_log = f"No puedes huir! ({int(escape_chance*100)}% chance)"
            escape_chance = min(escape_chance + 0.15, 0.9)
            combat_turn = "enemy"
            
    elif key == pygame.K_p:
        # use potion
        if player['potions'] > 0:
            player['potions'] -= 1
            heal = min(player['hp_max'] - player['hp'], player['hp_max'] * 0.2)
            player['hp'] += heal
            combat_log = f"Usas una poción y recuperas {heal} HP."
            combat_turn = "enemy"
        else:
            combat_log = "No tienes pociones."
            
    elif key == pygame.K_a:
        # ranged arrow
        if player['cd_arrow'] > 0:
            combat_log = f"Flecha en cooldown ({player['cd_arrow']})"
        else:
            dx,dy = player['last_dir']
            if dx == 0 and dy == 0:
                dx,dy = (0,-1)
            for dist in range(1,7):
                tx = player['x'] + dx*dist
                ty = player['y'] + dy*dist
                if not (0 <= tx < MAP_SIZE and 0 <= ty < MAP_SIZE): break
                if game_map[ty][tx] == 1: break
                target = next((ee for ee in enemies if ee['x']==tx and ee['y']==ty), None)
                if target:
                    log, dmg, hit = combat_attack(player, target, power=0.9)
                    combat_log = f"Flecha: {log}"
                    player['cd_arrow'] = 4
                    # Verificar si el enemigo murió
                    if target['hp'] <= 0:
                        try:
                            enemies.remove(target)
                            if target == active_enemy:
                                end_combat('player')
                                return
                        except ValueError:
                            pass
                    break
            else:
                combat_log = "Flecha no impacta a nadie."
            combat_turn = "enemy"
            

def enemy_turn():
    global combat_turn, combat_log
    if not active_enemy:
        combat_turn = "player"
        return
    if active_enemy.get('stun',0) > 0:
        combat_log = "El enemigo está aturdido y pierde el turno."
        active_enemy['stun'] -= 1
        combat_turn = "player"
        return
    choice = random.random()
    if choice < 0.75:
        log, dmg, hit = combat_attack(active_enemy, player, power=1.0)
        combat_log = "Enemigo: " + log
    elif choice < 0.9:
        log, dmg, hit = combat_attack(active_enemy, player, power=0.9, status_apply={"bleed":2})
        combat_log = "Enemigo aplica sangrado! " + log
    else:
        if random.random() < 0.4:
            player['stun'] = 1
            combat_log = "Enemigo aturde!"
        else:
            log, dmg, hit = combat_attack(active_enemy, player, power=0.6)
            combat_log = "Enemigo intenta aturdir y falla en parte. " + log

    if player.get('def_turns',0) > 0:
        player['def_turns'] -= 1
        if player['def_turns'] <= 0 and 'def_backup' in player:
            player['def'] = player['def_backup']
            del player['def_backup']

    apply_status_ticks(player)
    apply_status_ticks(active_enemy)

    if player['cd_arrow'] > 0: player['cd_arrow'] -= 1
    if player['cd_strike'] > 0: player['cd_strike'] -= 1
    if player.get('buff_turns',0) > 0:
        player['buff_turns'] -= 1
        if player['buff_turns'] <= 0:
            player['attack_buff'] = 0

    if player['hp'] <= 0:
        end_combat('enemy')
    elif active_enemy['hp'] <= 0:
        end_combat('player')
    else:
        combat_turn = "player"

# ----------------------
# PLAYER LEVEL SYSTEM
# ----------------------

def gain_experience(amount):
    """El jugador gana experiencia"""
    player['exp'] += amount
    player['exp_to_next_level'] = max(10, player['level'] * 15)
    
    # Verificar si subió de nivel
    if player['exp'] >= player['exp_to_next_level']:
        level_up()

def level_up():
    """El jugador sube de nivel"""
    player['level'] += 1
    player['exp'] = 0
    player['exp_to_next_level'] = player['level'] * 25  # Más experiencia requerida
    
    # MEJORAS BALANCEADAS
    hp_increase = random.randint(5, 8)    # Menos HP
    atk_increase = random.randint(1, 2)   # Menos ataque
    def_increase = random.randint(1, 2)   # Menos defensa
    
    old_hp_max = player['hp_max']
    player['hp_max'] += hp_increase
    
    # NO curar completamente - mantener el mismo porcentaje de vida
    hp_percentage = player['hp'] / old_hp_max if old_hp_max > 0 else 1
    player['hp'] = int(player['hp_max'] * hp_percentage)
    
    player['atk'] += atk_increase
    player['def'] += def_increase
    
    # Mostrar mensaje


# ----------------------
# SHOP
# ----------------------
SHOP_ITEMS = [
    {"name":"Poción de Vida"},
    {"name":"Poción Grande"},
    {"name":"Elixir de Fuerza"}
]

shop_open = False
shop_message = ""
shop_message_timer = 0


def shop_buy(idx):
    global shop_message, shop_message_timer
    if idx < 0 or idx >= len(SHOP_ITEMS):
        return
    item = SHOP_ITEMS[idx]
    if player['gold'] < item['price']:
        shop_message = "No tienes suficiente oro."
        shop_message_timer = 120  # 2 segundos
        return
    player['gold'] -= item['price']
    if item['type'] == 'potion':
        if item["heal"] > 39:
            player['potions'] += 2
        else:
            player['potions'] += 1
        shop_message = f"Compraste {item['name']}."
    elif item['type'] == 'buff':
        player['attack_buff'] += item['atk_bonus']
        player['buff_turns'] = item['turns']
        shop_message = f"Compraste {item['name']} (+{item['atk_bonus']} atk por {item['turns']} turnos)."
    shop_message_timer = 120  # 2 segundos


# ----------------------
# COMBAT SCREEN - CORREGIDA
# ----------------------

def draw_combat_screen(surface):
    surface.fill((25, 20, 30))
    
    # ===== ENEMIGO =====
    enemy_x = SCREEN_W // 3
    enemy_y = SCREEN_H // 2 - 100
    
    # Dibujar sprite del enemigo MÁS GRANDE
    enemy_type = active_enemy['type']
    if enemy_type in enemy_sprites:
        large_enemy_sprite = pygame.transform.scale(enemy_sprites[enemy_type], (120, 120))
        sprite_rect = large_enemy_sprite.get_rect(center=(enemy_x, enemy_y))
        surface.blit(large_enemy_sprite, sprite_rect)
    else:
        pygame.draw.circle(surface, COLOR_ENEMY_SHADOW, (enemy_x, enemy_y + 60), 35)
        pygame.draw.circle(surface, COLOR_ENEMY, (enemy_x, enemy_y), 30)
    
    # Diálogo del enemigo MEJORADO - MÁS ANCHO Y CON MANEJO DE TEXTO LARGO
    if active_enemy['current_dialogue']:
        dialogue_text = active_enemy['current_dialogue']
        
        # Dividir texto largo en múltiples líneas si es necesario
        max_chars_per_line = 50  # Caracteres máximos por línea
        if len(dialogue_text) > max_chars_per_line:
            # Encontrar el último espacio antes del límite
            words = dialogue_text.split(' ')
            lines = []
            current_line = ""
            
            for word in words:
                if len(current_line + word) <= max_chars_per_line:
                    current_line += word + " "
                else:
                    lines.append(current_line.strip())
                    current_line = word + " "
            lines.append(current_line.strip())
            
            # Dibujar múltiples líneas
            dialogue_height = 30 + (len(lines) * 25)
            dialogue_bg = pygame.Surface((450, dialogue_height), pygame.SRCALPHA)
            dialogue_bg.fill((0, 0, 0, 200))
            surface.blit(dialogue_bg, (enemy_x - 225, enemy_y - 130))
            
            for i, line in enumerate(lines):
                line_text = font.render(f'"{line}"', True, (255, 255, 200))
                surface.blit(line_text, (enemy_x - line_text.get_width()//2, enemy_y - 120 + i * 25))
        else:
            # Texto corto, una sola línea
            dialogue_bg = pygame.Surface((450, 50), pygame.SRCALPHA)
            dialogue_bg.fill((0, 0, 0, 200))
            surface.blit(dialogue_bg, (enemy_x - 225, enemy_y - 130))
            
            dialogue_render = font.render(f'"{dialogue_text}"', True, (255, 255, 200))
            surface.blit(dialogue_render, (enemy_x - dialogue_render.get_width()//2, enemy_y - 120))
    
    # Información del enemigo más prominente
    enemy_name = bigfont.render(f"{active_enemy['type'].capitalize()} Nvl {active_enemy['level']}", True, (255, 180, 180))
    surface.blit(enemy_name, (enemy_x - enemy_name.get_width()//2, enemy_y - 80))
    
    # Barra de vida del enemigo más grande
    enemy_hp_pct = active_enemy['hp'] / active_enemy['hp_max']
    pygame.draw.rect(surface, (50, 50, 50), (enemy_x - 70, enemy_y + 80, 140, 16))
    pygame.draw.rect(surface, (220, 60, 60), (enemy_x - 70, enemy_y + 80, int(140 * enemy_hp_pct), 16))
    enemy_hp_text = font.render(f"{active_enemy['hp']}/{active_enemy['hp_max']} HP", True, (240, 240, 240))
    surface.blit(enemy_hp_text, (enemy_x - enemy_hp_text.get_width()//2, enemy_y + 82))
    
    # ===== JUGADOR =====
    player_x = SCREEN_W * 2 // 3
    player_y = SCREEN_H // 2 - 80
    
    # Dibujar sprite del jugador MÁS GRANDE Y FLIPEADO
    if player_sprite is not None:
        large_player_sprite = pygame.transform.scale(player_sprite, (120, 120))
        flipped_player_sprite = pygame.transform.flip(large_player_sprite, True, False)
        sprite_rect = flipped_player_sprite.get_rect(center=(player_x, player_y))
        surface.blit(flipped_player_sprite, sprite_rect)
        
        # Sombra más grande
        pygame.draw.ellipse(surface, COLOR_PLAYER_SHADOW, (player_x - 35, player_y + 45, 70, 20))
    else:
        pygame.draw.ellipse(surface, COLOR_PLAYER_SHADOW, (player_x - 35, player_y + 45, 70, 20))
        pygame.draw.rect(surface, COLOR_PLAYER, (player_x - 18, player_y - 18, 36, 36), border_radius=8)
    
    # Información del jugador
    player_name = bigfont.render(f"Héroe Nvl {player['level']}", True, (180, 255, 180))
    surface.blit(player_name, (player_x - player_name.get_width()//2, player_y - 70))
    
    # Barra de vida del jugador más grande
    player_hp_pct = player['hp'] / player['hp_max']
    pygame.draw.rect(surface, (50, 50, 50), (player_x - 70, player_y + 80, 140, 16))
    pygame.draw.rect(surface, (60, 200, 80), (player_x - 70, player_y + 80, int(140 * player_hp_pct), 16))
    player_hp_text = font.render(f"{player['hp']}/{player['hp_max']} HP", True, (240, 240, 240))
    surface.blit(player_hp_text, (player_x - player_hp_text.get_width()//2, player_y + 82))
    
    # ===== PANEL DE ACCIONES MEJORADO =====
    action_panel_height = 160
    pygame.draw.rect(surface, (35, 30, 40), (0, SCREEN_H - action_panel_height, SCREEN_W, action_panel_height))
    pygame.draw.rect(surface, (70, 60, 90), (0, SCREEN_H - action_panel_height, SCREEN_W, 4))
    
    # Log de combate más prominente
    if combat_log:
        log_bg = pygame.Surface((SCREEN_W - 40, 35), pygame.SRCALPHA)
        log_bg.fill((0, 0, 0, 180))
        surface.blit(log_bg, (20, SCREEN_H - action_panel_height + 10))
        
        log_text = bigfont.render(combat_log, True, (255, 220, 100))
        surface.blit(log_text, (SCREEN_W//2 - log_text.get_width()//2, SCREEN_H - action_panel_height + 15))
    
    # Opciones de combate reorganizadas y más grandes
    options = [
        ("1 - Ataque Básico", "Ataque rápido y confiable"),
        ("2 - Defender", "+6 DEF por 1 turno"), 
        ("3 - Huir", f"{int(escape_chance*100)}% de éxito"),
        ("P - Usar Poción", f"{player['potions']} disponible(s)"),
        ("A - Flecha", "Ataque a distancia" if player['cd_arrow'] == 0 else f"CD: {player['cd_arrow']}"),
        ("Z - Golpe Fuerte", "Ataque poderoso" if player['cd_strike'] == 0 else f"CD: {player['cd_strike']}")
    ]
    
    for i, (option, desc) in enumerate(options):
        col = i % 3
        row = i // 3
        
        x_pos = 50 + col * (SCREEN_W // 3)
        y_pos = SCREEN_H - action_panel_height + 60 + row * 40
        
        # Texto principal
        opt_text = font.render(option, True, (220, 220, 240))
        surface.blit(opt_text, (x_pos, y_pos))
        
        # Descripción
        desc_text = tinyfont.render(desc, True, (180, 180, 200))
        surface.blit(desc_text, (x_pos, y_pos + 20))
    
    # Indicador de turno más destacado
    turn_bg = pygame.Surface((200, 40), pygame.SRCALPHA)
    turn_bg.fill((0, 0, 0, 150))
    surface.blit(turn_bg, (SCREEN_W//2 - 100, 20))
    
    turn_text = bigfont.render(f"Turno: {'JUGADOR' if combat_turn == 'player' else 'ENEMIGO'}", True, 
                           (100, 255, 100) if combat_turn == 'player' else (255, 100, 100))
    surface.blit(turn_text, (SCREEN_W//2 - turn_text.get_width()//2, 30))

# ----------------------
# INPUT / MAIN LOOP
# ----------------------

def draw_everything():
    if game_state == "combate":
        draw_combat_screen(screen)
    elif game_state == "shop":
        # Fondo principal primero
        draw_map(screen)
        draw_hud(screen)
        
        # Overlay de tienda semi-transparente
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Negro semi-transparente
        screen.blit(overlay, (0, 0))
        
        # Panel principal de tienda MÁS GRANDE
        shop_panel_width = 500  # Era 400
        shop_panel_height = 400  # Era 300
        shop_panel_x = (SCREEN_W - shop_panel_width) // 2
        shop_panel_y = (SCREEN_H - shop_panel_height) // 2
        
        # Fondo del panel
        pygame.draw.rect(screen, (30, 25, 40), (shop_panel_x, shop_panel_y, shop_panel_width, shop_panel_height), border_radius=12)
        pygame.draw.rect(screen, (60, 50, 80), (shop_panel_x, shop_panel_y, shop_panel_width, shop_panel_height), 3, border_radius=12)
        
        # Título
        title = bigfont.render("TIENDA DEL AVENTURERO", True, (255, 240, 160))
        screen.blit(title, (SCREEN_W//2 - title.get_width()//2, shop_panel_y + 20))
        
        # Oro del jugador
        gold_text = font.render(f"Tu oro: {player['gold']}", True, (255, 215, 0))
        screen.blit(gold_text, (SCREEN_W//2 - gold_text.get_width()//2, shop_panel_y + 55))
        
        # Items de la tienda con texto más grande
        for i, item in enumerate(SHOP_ITEMS):
            y_pos = shop_panel_y + 100 + i * 80  # Más espacio entre items
            
            # Fondo del item más grande
            pygame.draw.rect(screen, (45, 40, 65), (shop_panel_x + 20, y_pos, shop_panel_width - 40, 70), border_radius=10)
            pygame.draw.rect(screen, (80, 70, 110), (shop_panel_x + 20, y_pos, shop_panel_width - 40, 70), 2, border_radius=10)
            
            # Nombre y precio con fuentes más grandes
            name_text = bigfont.render(f"{i+1}. {item['name']}", True, (240, 240, 240))
            price_text = bigfont.render(f"{item['price']} oro", True, (255, 215, 0))
            
            screen.blit(name_text, (shop_panel_x + 40, y_pos + 15))
            screen.blit(price_text, (shop_panel_x + 40, y_pos + 40))
            
            # Descripción más detallada
            if item['type'] == 'potion':
                desc_text = font.render(f"Recupera {item['heal']} puntos de vida", True, (150, 255, 150))
            else:
                desc_text = font.render(f"+{item['atk_bonus']} ATK por {item['turns']} turnos de combate", True, (255, 150, 150))
            
            screen.blit(desc_text, (shop_panel_x + shop_panel_width - 250, y_pos + 28))
        
        # Mensaje de la tienda
        if shop_message and (shop_message_timer > 0 or shop_message == "Bienvenido. 1/2/3 comprar, Q salir."):
            message_text = font.render(shop_message, True, (200, 200, 255))
            screen.blit(message_text, (SCREEN_W//2 - message_text.get_width()//2, shop_panel_y + shop_panel_height - 40))
        
    else:
        # Pantalla normal de exploración
        draw_map(screen)
        draw_hud(screen)
        for ft in floating_texts:
            sx = int((ft["x"] - player["x"]) * TILE_SIZE + CAMERA_RADIUS * TILE_SIZE)
            sy = int((ft["y"] - player["y"]) * TILE_SIZE + CAMERA_RADIUS * TILE_SIZE)
            txt = tinyfont.render(ft["text"], True, ft["color"])
            screen.blit(txt, (sx - txt.get_width()//2, sy - 10))
    
    pygame.display.flip()

def main():
    global player_nickname, enemies_killed, total_score, game_map, exit_pos, shop_pos, enemies, game_state, level_number, player
    
    # Mostrar menú principal
    try:
        from menu import main_menu
        
        while True:
            action, data = main_menu()
            
            if action == "quit":
                pygame.quit()
                sys.exit()
                
            elif action == "new":
                player_nickname = data
                enemies_killed = 0
                total_score = 0
                new_level(1, preserve_stats=False, generate_new_level=True)
                game_state = "exploracion"
                level_number = 1
                break
                
            elif action == "continue":
                # Cargar partida guardada COMPLETA
                saved_data = data
                player_nickname = saved_data.get('player_nickname', 'Jugador')
                enemies_killed = saved_data['enemies_killed']
                total_score = saved_data['total_score']
                
                # CARGAR EL MAPA Y ESTADO COMPLETO
                game_map = saved_data['game_map']
                exit_pos = tuple(saved_data['exit_pos'])
                shop_pos = tuple(saved_data['shop_pos']) if saved_data['shop_pos'] else None
                
                # Crear jugador en la posición guardada
                player_data = saved_data['player']
                player = make_player(player_data['x'], player_data['y'])
                player.update(player_data)
                
                # Cargar enemigos
                enemies.clear()
                for enemy_data in saved_data['enemies']:
                    enemy = make_enemy(enemy_data['x'], enemy_data['y'], enemy_data['level'])
                    # Actualizar con todos los datos del enemigo guardado
                    enemy.update({
                        'hp': enemy_data['hp'],
                        'hp_max': enemy_data['hp_max'],
                        'atk': enemy_data['atk'],
                        'def': enemy_data['def'],
                        'type': enemy_data['type'],
                        'active': enemy_data['active'],
                        'gold_drop': enemy_data.get('gold_drop', 0)
                    })
                    enemies.append(enemy)
                
                # Inicializar sistemas de visibilidad
                global explored, visible
                explored = [[False for _ in range(MAP_SIZE)] for _ in range(MAP_SIZE)]
                visible = [[False for _ in range(MAP_SIZE)] for _ in range(MAP_SIZE)]
                compute_visibility(player["x"], player["y"])
                
                level_number = saved_data['level_reached']
                game_state = "exploracion"
                print(f"Partida cargada - Nivel {level_number}")
                break
    except ImportError:
        # Si no hay menú, empezar directamente
        player_nickname = "Jugador"
        new_level(1, preserve_stats=False, generate_new_level=True)
        game_state = "exploracion"
        level_number = 1
    
    # Loop principal del juego
    last_time = pygame.time.get_ticks()

    while True:
        dt = clock.tick(FPS)
        now = pygame.time.get_ticks()
        
        # Actualizar timers de mensajes
        global combat_log_timer, shop_message_timer
        if combat_log_timer > 0:
            combat_log_timer -= 1
        if shop_message_timer > 0:
            shop_message_timer -= 1
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Guardar al salir
                if player_nickname and game_state != "gameover":
                    save_game()
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                # MENU DE PAUSA CON ESC
                if event.key == pygame.K_ESCAPE and game_state in ["exploracion", "combate", "shop"]:
                    action = show_pause_menu()
                    if action == "quit":
                        if player_nickname and game_state != "gameover":
                            save_game()
                        pygame.quit()
                        sys.exit()
                    elif action == "menu":
                        # Volver al menú principal
                        return main()  # Reiniciar el juego volviendo al menú
                    # Si es "continue", simplemente continuar el juego
                
                if game_state == "exploracion":
                    if event.key == pygame.K_UP:
                        try_move_player(0, -1); move_enemies_ai()
                    elif event.key == pygame.K_DOWN:
                        try_move_player(0, 1); move_enemies_ai()
                    elif event.key == pygame.K_LEFT:
                        try_move_player(-1, 0); move_enemies_ai()
                    elif event.key == pygame.K_RIGHT:
                        try_move_player(1, 0); move_enemies_ai()
                    elif event.key == pygame.K_p:
                        if player['potions'] > 0 and player['hp'] < player['hp_max']:
                            heal = min(player['hp_max'] - player['hp'], player['hp_max'] * 0.2)
                            player['hp'] += heal
                            player['potions'] -= 1
                    elif event.key == pygame.K_a:
                        dx,dy = player['last_dir']
                        if dx == 0 and dy == 0: dx,dy = (0,-1)
                        if player['cd_arrow'] > 0:
                            pass
                        else:
                            hit_any = False
                            for step in range(1,7):
                                tx = player['x'] + dx*step
                                ty = player['y'] + dy*step
                                if not (0 <= tx < MAP_SIZE and 0 <= ty < MAP_SIZE): break
                                if game_map[ty][tx] == 1: break
                                target = next((ee for ee in enemies if ee['x']==tx and ee['y']==ty), None)
                                if target:
                                    log, dmg, hit = combat_attack(player, target, power=0.9)
                                    player['cd_arrow'] = 4
                                    hit_any = True
                                    break
                            if not hit_any:
                                for e in enemies:
                                    if e['x'] == player['x'] and e['y'] == player['y']:
                                        start_combat(e)
                                        handle_player_combat_input(pygame.K_z)
                                        break
                    elif event.key == pygame.K_n:
                        new_level(level_number + 1, preserve_stats=True, generate_new_level=True)
                elif game_state == "combate":
                    handle_player_combat_input(event.key)
                    if combat_turn == "enemy":
                        pygame.time.delay(120)
                        enemy_turn()
                elif game_state == "shop":
                    if event.key == pygame.K_q:
                        shop_buy(0)
                    elif event.key == pygame.K_2:
                        shop_buy(1)
                    elif event.key == pygame.K_3:
                        shop_buy(2)

        # Solo actualizar y dibujar si no estamos en pausa o game over
        if game_state != "gameover":
            draw_everything()
    
        if game_state == "gameover":
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0,0,0,200))
            screen.blit(overlay, (0,0))
            
            # Usar level_number si está definida, sino usar 1 por defecto
            current_level = level_number if 'level_number' in globals() else 1
            current_kills = enemies_killed if 'enemies_killed' in globals() else 0
            current_score = total_score if 'total_score' in globals() else 0
            
            txt = bigfont.render("GAME OVER - Presiona cualquier tecla para continuar", True, (255,80,80))
            screen.blit(txt, (SCREEN_W//2 - txt.get_width()//2, SCREEN_H//2 - 20))
            
            # Mostrar estadísticas finales
            stats_text = font.render(f"Piso alcanzado: {current_level} | Enemigos derrotados: {current_kills} | Puntuación: {current_score}", True, (255,255,255))
            screen.blit(stats_text, (SCREEN_W//2 - stats_text.get_width()//2, SCREEN_H//2 + 20))
            
            pygame.display.flip()
            
            # Esperar input para volver al menú
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                        waiting = False
                        # NO guardar la partida al morir, ya se eliminó el archivo
                        return main()  # Volver al menú principal

if __name__ == "__main__":
    main()