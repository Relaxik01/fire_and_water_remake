import pygame
import sys
import config
from player import Player

def load_level(level_number):
    """ Алгоритм загрузки карты уровня из файла"""
    filename = f"level{level_number}.txt"
    platforms = []
    magnets = []
    crystals = []
    exits = []
    lavas = [] # Список для зон смерти
    player_positions = {}
    
    try:
        with open(filename, 'r') as file:
            for row_idx, line in enumerate(file):
                for col_idx, char in enumerate(line.strip()):
                    rect = pygame.Rect(
                        col_idx * config.BLOCK_SIZE,
                        row_idx * config.BLOCK_SIZE,
                        config.BLOCK_SIZE,
                        config.BLOCK_SIZE
                    )
                    
                    if char == '#':
                        platforms.append(rect)
                    elif char == 'N':
                        magnets.append((rect, 1))
                    elif char == 'S':
                        magnets.append((rect, -1))
                    elif char == 'C':
                        crystals.append(rect)
                    elif char == 'E':
                        exits.append(rect)
                    elif char == 'X':
                        lavas.append(rect)
                    elif char == 'F':
                        player_positions['F'] = (rect.x, rect.y)
                    elif char == 'W':
                        player_positions['W'] = (rect.x, rect.y)
                        
    except FileNotFoundError:
        return None
        
    return platforms, magnets, crystals, exits, lavas, player_positions

def draw_menu(screen, font, start_btn, exit_btn):
    screen.fill(config.COLOR_BG)
    title_text = font.render("Fire_and_Water_remake)", True, (255, 255, 255))
    screen.blit(title_text, (config.SCREEN_WIDTH // 2 - title_text.get_width() // 2, 120))
    
    sub_text = pygame.font.SysFont('Courier New', 16).render("Project", True, (120, 120, 130))
    screen.blit(sub_text, (config.SCREEN_WIDTH // 2 - sub_text.get_width() // 2, 160))
    
    pygame.draw.rect(screen, (50, 150, 50), start_btn, border_radius=6)
    start_txt = font.render("PLAY", True, (255, 255, 255))
    screen.blit(start_txt, (start_btn.centerx - start_txt.get_width() // 2, start_btn.centery - start_txt.get_height() // 2))
    
    pygame.draw.rect(screen, (150, 50, 50), exit_btn, border_radius=6)
    exit_txt = font.render("EXIT", True, (255, 255, 255))
    screen.blit(exit_txt, (exit_btn.centerx - exit_txt.get_width() // 2, exit_btn.centery - exit_txt.get_height() // 2))

def main():
    pygame.init()
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption("Fire_andWater_remake")
    clock = pygame.time.Clock()
    
    game_state = "MENU"
    start_button = pygame.Rect(config.SCREEN_WIDTH // 2 - 100, 250, 200, 50)
    exit_button = pygame.Rect(config.SCREEN_WIDTH // 2 - 100, 330, 200, 50)
    
    main_font = pygame.font.SysFont('Courier New', 24, bold=True)
    ui_font = pygame.font.SysFont('Courier New', 20, bold=True)
    
    current_level = 1
    score = 0
    game_over = False
    
    level_data = load_level(current_level)
    platforms, magnets, crystals, exits, lavas, player_positions = level_data
    
    fire_keys = {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'jump': pygame.K_UP}
    water_keys = {'left': pygame.K_a, 'right': pygame.K_d, 'jump': pygame.K_w}
    
    fx, fy = player_positions.get('F', (100, 100))
    wx, wy = player_positions.get('W', (150, 100))
    fire_boy = Player(fx, fy, config.COLOR_FIRE, fire_keys, charge=1)
    water_girl = Player(wx, wy, config.COLOR_WATER, water_keys, charge=-1)
    
    is_running = True
    while is_running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
            if event.type == pygame.MOUSEBUTTONDOWN and game_state == "MENU":
                if event.button == 1:
                    if start_button.collidepoint(mouse_pos):
                        game_state = "GAME"
                    elif exit_button.choose_point(mouse_pos) or exit_button.collidepoint(mouse_pos):
                        is_running = False
        
        if game_state == "MENU":
            draw_menu(screen, main_font, start_button, exit_button)
            
        elif game_state == "GAME":
            if not game_over:
                fire_boy.update(platforms, magnets)
                water_girl.update(platforms, magnets)
                
                # Сбор кристаллов
                for crystal in crystals[:]:
                    if fire_boy.rect.colliderect(crystal) or water_girl.rect.colliderect(crystal):
                        crystals.remove(crystal)
                        score += 10
                
                # АЛГОРИТМ ПРОВЕРКИ СМЕРТИ
                hit_lava_f = any(fire_boy.rect.colliderect(lava) for lava in lavas)
                hit_lava_w = any(water_girl.rect.colliderect(lava) for lava in lavas)
                
                if hit_lava_f or hit_lava_w:
                    # Респавн: возвращаю на начальные точки текущего уровня
                    fire_boy.rect.x, fire_boy.rect.y = fx, fy
                    water_girl.rect.x, water_girl.rect.y = wx, wy
                    fire_boy.velocity_x = fire_boy.velocity_y = 0
                    water_girl.velocity_x = water_girl.velocity_y = 0
                    score = max(0, score - 5) 
                
                # Проверка финиша
                fire_on_exit = any(fire_boy.rect.colliderect(exit_rect) for exit_rect in exits)
                water_on_exit = any(water_girl.rect.colliderect(exit_rect) for exit_rect in exits)
                
                if fire_on_exit and water_on_exit:
                    current_level += 1
                    level_data = load_level(current_level)
                    
                    if level_data is None:
                        game_over = True
                    else:
                        platforms, magnets, crystals, exits, lavas, player_positions = level_data
                        fx, fy = player_positions.get('F', (100, 100))
                        wx, wy = player_positions.get('W', (150, 100))
                        fire_boy.rect.x, fire_boy.rect.y = fx, fy
                        water_girl.rect.x, water_girl.rect.y = wx, wy
            
            # Отрисовка
            screen.fill(config.COLOR_BG)
            
            for platform in platforms:
                pygame.draw.rect(screen, config.COLOR_PLATFORM, platform)
                
            for mag_rect, mag_type in magnets:
                color = config.COLOR_N if mag_type == 1 else config.COLOR_S
                pygame.draw.rect(screen, color, mag_rect, border_radius=4)
                font_mag = pygame.font.SysFont('Arial', 12, bold=True)
                text = font_mag.render('N' if mag_type == 1 else 'S', True, (255, 255, 255))
                screen.blit(text, text.get_rect(center=mag_rect.center))
                
            for crystal in crystals:
                pygame.draw.rect(screen, config.COLOR_CRYSTAL, crystal, border_radius=5)
                
            for exit_rect in exits:
                pygame.draw.rect(screen, config.COLOR_EXIT, exit_rect)
                
            # Рисую ловушки
            for lava in lavas:
                pygame.draw.rect(screen, config.COLOR_LAVA, lava, border_radius=2)
                
            fire_boy.draw(screen)
            water_girl.draw(screen)
            
            # Нижний HUD
            pygame.draw.rect(screen, (40, 40, 45), (0, 300, config.SCREEN_WIDTH, 300))
            
            if not game_over:
                level_text = ui_font.render(f"LEVEL: {current_level} / 5", True, (255, 255, 255))
                score_text = ui_font.render(f"SCORE: {score}", True, (255, 215, 0))
                controls_f = ui_font.render("FIRE (Red): Arrows", True, config.COLOR_FIRE)
                controls_w = ui_font.render("WATER (Blue): WASD", True, config.COLOR_WATER)
                
                screen.blit(level_text, (30, 330))
                screen.blit(score_text, (30, 370))
                screen.blit(controls_f, (450, 330))
                screen.blit(controls_w, (450, 370))
            else:
                win_text = ui_font.render("Congratulations! You passed the level", True, (0, 255, 0))
                screen.blit(win_text, (config.SCREEN_WIDTH // 2 - win_text.get_width() // 2, 400))
                
        pygame.display.flip()
        clock.tick(config.FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
