import pygame
import sys
import json
import os
from datetime import datetime

# Inicializar Pygame
pygame.init()

# Configuración de la ventana (igual que tu juego)
TILE_SIZE = 32
MAP_SIZE = 25
CAMERA_RADIUS = 9
WINDOW_TILES = CAMERA_RADIUS * 2 + 1
SCREEN_W = WINDOW_TILES * TILE_SIZE
SCREEN_H = WINDOW_TILES * TILE_SIZE + 96

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Roguelike Mejorado")

# Colores mejorados
DARK_BLUE = (15, 20, 30)
DARK_PURPLE = (40, 30, 60)
STONE_GRAY = (70, 80, 100)
BUTTON_COLOR = (50, 70, 90)
BUTTON_HOVER = (70, 90, 110)
BUTTON_DISABLED = (40, 50, 60)
GOLD = (255, 215, 0)
SILVER = (200, 200, 220)
CRYSTAL_BLUE = (100, 200, 255)
CRYSTAL_PURPLE = (180, 100, 255)
RED = (220, 60, 60)
GREEN = (60, 220, 120)

# Fuentes
title_font = pygame.font.Font(None, 64)
button_font = pygame.font.Font(None, 32)
small_font = pygame.font.Font(None, 24)
input_font = pygame.font.Font(None, 28)

# Archivos de guardado
SAVE_FILE = "save_game.json"
LEADERBOARD_FILE = "leaderboard.json"


# ---- Button helpers (no classes) ----
def make_button(x, y, width, height, text, enabled=True):
    return {
        'rect': pygame.Rect(x, y, width, height),
        'text': text,
        'is_hovered': False,
        'enabled': enabled
    }

def draw_button(btn, surface):
    rect = btn['rect']
    enabled = btn.get('enabled', True)
    is_hovered = btn.get('is_hovered', False)
    if not enabled:
        color = BUTTON_DISABLED
        text_color = (100, 100, 100)
    else:
        color = BUTTON_HOVER if is_hovered else BUTTON_COLOR
        text_color = CRYSTAL_BLUE if is_hovered else SILVER

    pygame.draw.rect(surface, color, rect, border_radius=8)
    pygame.draw.rect(surface, STONE_GRAY, rect, 3, border_radius=8)

    if enabled and is_hovered:
        pygame.draw.line(surface, SILVER,
                         (rect.left + 5, rect.top + 5),
                         (rect.right - 5, rect.top + 5), 2)

    text_surface = button_font.render(btn['text'], True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)

def check_button_hover(btn, mouse_pos):
    btn['is_hovered'] = btn['rect'].collidepoint(mouse_pos) and btn.get('enabled', True)

def is_button_clicked(btn, event):
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        return btn['rect'].collidepoint(event.pos) and btn.get('enabled', True)
    return False


# ---- InputBox helpers (no classes) ----
def make_inputbox(x, y, width, height, text=''):
    return {
        'rect': pygame.Rect(x, y, width, height),
        'text': text,
        'active': False
    }

def handle_inputbox_event(inputbox, event):
    if event.type == pygame.MOUSEBUTTONDOWN:
        inputbox['active'] = inputbox['rect'].collidepoint(event.pos)
    if event.type == pygame.KEYDOWN:
        if inputbox['active']:
            if event.key == pygame.K_RETURN:
                return True
            elif event.key == pygame.K_BACKSPACE:
                inputbox['text'] = inputbox['text'][:-1]
            else:
                if len(inputbox['text']) < 15:
                    inputbox['text'] += event.unicode
    return False

def draw_inputbox(inputbox, surface):
    rect = inputbox['rect']
    color = CRYSTAL_BLUE if inputbox.get('active', False) else SILVER
    pygame.draw.rect(surface, DARK_BLUE, rect, border_radius=5)
    pygame.draw.rect(surface, color, rect, 2, border_radius=5)

    text_surface = input_font.render(inputbox.get('text', ''), True, SILVER)
    surface.blit(text_surface, (rect.x + 10, rect.y + 8))

# Funciones de guardado
def load_game():
    try:
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return None

def save_leaderboard_entry(nickname, score, level_reached, enemies_killed):
    try:
        leaderboard = []
        if os.path.exists(LEADERBOARD_FILE):
            with open(LEADERBOARD_FILE, 'r') as f:
                leaderboard = json.load(f)
        
        entry = {
            'nickname': nickname,
            'score': score,
            'level_reached': level_reached,
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
        return True
    except:
        return False

def get_leaderboard():
    try:
        if os.path.exists(LEADERBOARD_FILE):
            with open(LEADERBOARD_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return []

# Funciones de dibujo mejoradas
def draw_crystal(surface, x, y, size, color1, color2):
    points = [
        (x, y - size),
        (x + size // 2, y - size // 3),
        (x + size // 3, y + size // 2),
        (x - size // 3, y + size // 2),
        (x - size // 2, y - size // 3)
    ]
    pygame.draw.polygon(surface, color1, points)
    pygame.draw.polygon(surface, color2, points, 2)

def draw_torch_flame(surface, x, y, size, frame):
    # Animación simple de llama
    flame_size = size + (frame % 3)
    points = [
        (x, y - flame_size),
        (x + size // 2, y),
        (x, y + size // 3),
        (x - size // 2, y)
    ]
    pygame.draw.polygon(surface, (255, 200, 100), points)
    pygame.draw.polygon(surface, (255, 100, 50), points, 1)

def draw_background(surface, frame_counter):
    # Fondo degradado
    for y in range(SCREEN_H):
        color_factor = y / SCREEN_H
        color = (
            int(DARK_BLUE[0] * (1 - color_factor) + DARK_PURPLE[0] * color_factor),
            int(DARK_BLUE[1] * (1 - color_factor) + DARK_PURPLE[1] * color_factor),
            int(DARK_BLUE[2] * (1 - color_factor) + DARK_PURPLE[2] * color_factor)
        )
        pygame.draw.line(surface, color, (0, y), (SCREEN_W, y))
    
    # Entrada de mazmorra
    pygame.draw.arc(surface, STONE_GRAY, 
                   (SCREEN_W // 4, 50, SCREEN_W // 2, 200), 
                   3.14, 6.28, 5)
    
    # Cristales decorativos
    draw_crystal(surface, 100, 200, 30, CRYSTAL_BLUE, (150, 220, 255))
    draw_crystal(surface, SCREEN_W - 100, 250, 25, CRYSTAL_PURPLE, (200, 150, 255))
    draw_crystal(surface, 150, SCREEN_H - 150, 35, CRYSTAL_BLUE, (150, 220, 255))
    draw_crystal(surface, SCREEN_W - 150, SCREEN_H - 100, 40, CRYSTAL_PURPLE, (200, 150, 255))
    
    # Antorchas animadas
    draw_torch_flame(surface, 80, 300, 15, frame_counter)
    draw_torch_flame(surface, SCREEN_W - 80, 350, 15, frame_counter)
    
    # Suelo de la mazmorra
    pygame.draw.rect(surface, (30, 25, 40), 
                   (0, SCREEN_H - 100, SCREEN_W, 100))
    
    # Patrón de piedras en el suelo
    for i in range(0, SCREEN_W, 40):
        pygame.draw.rect(surface, (40, 35, 50), 
                       (i, SCREEN_H - 100, 30, 20))

def draw_title(surface):
    # Título con efecto neón
    title_text = "ROGUELIKE"
    subtitle_text = "MAZMORRAS OSCURAS"
    
    # Efecto de sombra
    shadow = title_font.render(title_text, True, (20, 20, 40))
    shadow_rect = shadow.get_rect(center=(SCREEN_W // 2 + 3, 103))
    surface.blit(shadow, shadow_rect)
    
    # Texto principal con brillo
    title = title_font.render(title_text, True, CRYSTAL_BLUE)
    title_rect = title.get_rect(center=(SCREEN_W // 2, 100))
    surface.blit(title, title_rect)
    
    # Subtítulo
    subtitle = small_font.render(subtitle_text, True, SILVER)
    subtitle_rect = subtitle.get_rect(center=(SCREEN_W // 2, 140))
    surface.blit(subtitle, subtitle_rect)

def draw_leaderboard(surface, leaderboard_data):
    # Fondo semitransparente
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    surface.blit(overlay, (0, 0))
    
    # Panel del leaderboard
    panel_width = 600
    panel_height = 500
    panel_x = (SCREEN_W - panel_width) // 2
    panel_y = (SCREEN_H - panel_height) // 2
    
    pygame.draw.rect(surface, (30, 35, 50), 
                   (panel_x, panel_y, panel_width, panel_height), 
                   border_radius=15)
    pygame.draw.rect(surface, CRYSTAL_BLUE, 
                   (panel_x, panel_y, panel_width, panel_height), 
                   3, border_radius=15)
    
    # Título
    title = title_font.render("LEADERBOARD", True, GOLD)
    surface.blit(title, (SCREEN_W // 2 - title.get_width() // 2, panel_y + 30))
    
    # Encabezados
    headers = ["POS", "NICKNAME", "PUNTAJE", "PISO", "ENEMIGOS"]
    header_x = panel_x + 50
    for i, header in enumerate(headers):
        text = small_font.render(header, True, CRYSTAL_PURPLE)
        surface.blit(text, (header_x + i * 120, panel_y + 80))
    
    # Datos
    for i, entry in enumerate(leaderboard_data[:10]):  # Top 10
        y_pos = panel_y + 110 + i * 35
        
        # Posición
        pos_text = small_font.render(f"{i+1}.", True, SILVER)
        surface.blit(pos_text, (header_x, y_pos))
        
        # Nickname
        name_text = small_font.render(entry['nickname'][:12], True, SILVER)
        surface.blit(name_text, (header_x + 120, y_pos))
        
        # Puntaje
        score_text = small_font.render(str(entry['score']), True, GOLD)
        surface.blit(score_text, (header_x + 240, y_pos))
        
        # Piso alcanzado
        level_text = small_font.render(str(entry['level_reached']), True, GREEN)
        surface.blit(level_text, (header_x + 360, y_pos))
        
        # Enemigos eliminados
        kills_text = small_font.render(str(entry['enemies_killed']), True, RED)
        surface.blit(kills_text, (header_x + 480, y_pos))
    
    # Instrucción para volver
    back_text = small_font.render("Presiona ESC o click para volver", True, SILVER)
    surface.blit(back_text, (SCREEN_W // 2 - back_text.get_width() // 2, panel_y + panel_height - 30))

def show_nickname_input(surface):
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    surface.blit(overlay, (0, 0))
    
    # Panel de entrada
    panel_width = 500
    panel_height = 200
    panel_x = (SCREEN_W - panel_width) // 2
    panel_y = (SCREEN_H - panel_height) // 2
    
    pygame.draw.rect(surface, (30, 35, 50), 
                   (panel_x, panel_y, panel_width, panel_height), 
                   border_radius=15)
    pygame.draw.rect(surface, CRYSTAL_BLUE, 
                   (panel_x, panel_y, panel_width, panel_height), 
                   3, border_radius=15)
    
    # Título
    title = button_font.render("INGRESA TU NICKNAME", True, GOLD)
    surface.blit(title, (SCREEN_W // 2 - title.get_width() // 2, panel_y + 30))
    
    # Instrucción
    instr = small_font.render("(Máximo 15 caracteres, presiona ENTER para confirmar)", True, SILVER)
    surface.blit(instr, (SCREEN_W // 2 - instr.get_width() // 2, panel_y + 70))
    
    # Caja de entrada
    input_box = make_inputbox(SCREEN_W // 2 - 150, panel_y + 100, 300, 40)
    
    return input_box

# Función principal del menú
def main_menu():
    clock = pygame.time.Clock()
    frame_counter = 0
    
    # Verificar si hay partida guardada
    saved_game = load_game()
    
    # Crear botones
    button_width = 300
    button_height = 50
    button_x = (SCREEN_W - button_width) // 2
    start_y = 250
    
    nueva_partida_btn = make_button(button_x, start_y, button_width, button_height, "NUEVA PARTIDA")
    continuar_btn = make_button(button_x, start_y + 70, button_width, button_height, "CONTINUAR", enabled=(saved_game is not None))
    leaderboard_btn = make_button(button_x, start_y + 140, button_width, button_height, "LEADERBOARD")
    salir_btn = make_button(button_x, start_y + 210, button_width, button_height, "SALIR")
    
    buttons = [nueva_partida_btn, continuar_btn, leaderboard_btn, salir_btn]
    
    # Estados del menú
    current_state = "main"  # "main", "nickname", "leaderboard"
    nickname = ""
    input_box = None
    
    running = True
    while running:
        frame_counter += 1
        mouse_pos = pygame.mouse.get_pos()
        
        # Actualizar hover de botones
        for button in buttons:
            check_button_hover(button, mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit", None
                
            if current_state == "main":
                if is_button_clicked(nueva_partida_btn, event):
                    print("Nueva Partida clickeado")
                    current_state = "nickname"
                    input_box = show_nickname_input(screen)
                    
                elif is_button_clicked(continuar_btn, event):
                    print("Continuar clickeado")
                    return "continue", saved_game
                    
                elif is_button_clicked(leaderboard_btn, event):
                    print("Leaderboard clickeado")
                    current_state = "leaderboard"
                    
                elif is_button_clicked(salir_btn, event):
                    print("Salir clickeado")
                    return "quit", None
            
            elif current_state == "nickname" and input_box:
                if handle_inputbox_event(input_box, event):
                    nickname = input_box.get('text','').strip()
                    if nickname:
                        print(f"Nickname ingresado: {nickname}")
                        return "new", nickname
                    else:
                        # Si no ingresó nickname, volver al menú principal
                        current_state = "main"
                        input_box = None
            
            elif current_state == "leaderboard":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    current_state = "main"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    current_state = "main"
        
        # Dibujar todo según el estado actual
        draw_background(screen, frame_counter)
        draw_title(screen)
        
        if current_state == "main":
            # Dibujar información de partida guardada si existe
            if saved_game:
                save_info = small_font.render(
                    f"Partida guardada: Piso {saved_game['level_reached']} - {saved_game['enemies_killed']} enemigos", 
                    True, GREEN
                )
                screen.blit(save_info, (button_x + 20, start_y + 70 + 60))
            
            # Dibujar botones
            for button in buttons:
                draw_button(button, screen)
                
        elif current_state == "nickname" and input_box:
            draw_inputbox(input_box, screen)
            
        elif current_state == "leaderboard":
            leaderboard_data = get_leaderboard()
            draw_leaderboard(screen, leaderboard_data)
        
        pygame.display.flip()
        clock.tick(60)
    
    return "quit", None