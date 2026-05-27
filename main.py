# main.py
import pygame
import sys
import config
from player import Player

def load_level(level_number):
    """ Алгоритм загрузки карты уровня из файла (Средний алгоритм) """
    filename = f"level{level_number}.txt"
    platforms = []
    magnets = []
    crystals = []
    exits = []
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
                    elif char == 'F':
                        player_positions['F'] = (rect.x, rect.y)
                    elif char == 'W':
                        player_positions['W'] = (rect.x, rect.y)
                        
    except FileNotFoundError:
        # Если файл уровня не найден, значит мы прошли игру!
        return None
        
    return platforms, magnets, crystals, exits, player_positions

def main():
    pygame.init()
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption("Elemental Odyssey: 5 Levels Pack")
    clock = pygame.time.Clock()
    
    current_level = 1
    score = 0
    
    # Загружаем первый уровень
    level_data = load_level(current_level)
    if not level_data:
        print("Ошибка: Не найден первый уровень level1.txt")
        sys.exit()
        
    platforms, magnets, crystals, exits, player_positions = level_data
    
    fire_keys = {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'jump': pygame.K_UP}
    water_keys = {'left': pygame.K_a, 'right': pygame.K_d, 'jump': pygame.K_w}
    
    fx, fy = player_positions.get('F', (100, 100))
    wx, wy = player_positions.get('W', (150, 100))
    fire_boy = Player(fx, fy, config.COLOR_FIRE, fire_keys, charge=1)
    water_girl = Player(wx, wy, config.COLOR_WATER, water_keys, charge=-1)
    
    game_over = False
    is_running = True
    
    while is_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
        
        if not game_over:
            # 1. Обновление физики игроков
            fire_boy.update(platforms, magnets)
            water_girl.update(platforms, magnets)
            
            # 2. АЛГОРИТМ СБОРА КРИСТАЛЛОВ (Легкий алгоритм)
            # Перебираем кристаллы с конца списка, чтобы безопасно удалять собранные
            for crystal in crystals[:]:
                if fire_boy.rect.colliderect(crystal) or water_girl.rect.colliderect(crystal):
                    crystals.remove(crystal)
                    score += 10 # За каждый кристалл даем 10 очков
            
            # 3. АЛГОРИТМ ПРОВЕРКИ ФИНИША (Средний алгоритм)
            # Игроки прошли уровень, если ОБА коснулись дверей выхода
            fire_on_exit = any(fire_boy.rect.colliderect(exit_rect) for exit_rect in exits)
            water_on_exit = any(water_girl.rect.colliderect(exit_rect) for exit_rect in exits)
            
            if fire_on_exit and water_on_exit:
                current_level += 1
                level_data = load_level(current_level)
                
                if level_data is None:
                    # Если load_level вернул None, значит уровней больше нет — ПОБЕДА!
                    game_over = True
                else:
                    # Загружаем данные нового уровня
                    platforms, magnets, crystals, exits, player_positions = level_data
                    # Перезапускаем игроков на новые начальные позиции
                    fx, fy = player_positions.get('F', (100, 100))
                    wx, wy = player_positions.get('W', (150, 100))
                    fire_boy.rect.x, fire_boy.rect.y = fx, fy
                    water_girl.rect.x, water_girl.rect.y = wx, wy
        
        # --- ОТРИСОВКА (View разделение) ---
        screen.fill(config.COLOR_BG)
        
        # Рисуем платформы, магниты, кристаллы и выходы
        for platform in platforms:
            pygame.draw.rect(screen, config.COLOR_PLATFORM, platform)
            
        for mag_rect, mag_type in magnets:
            color = config.COLOR_N if mag_type == 1 else config.COLOR_S
            pygame.draw.rect(screen, color, mag_rect, border_radius=4)
            font = pygame.font.SysFont('Arial', 12, bold=True)
            text = font.render('N' if mag_type == 1 else 'S', True, (255, 255, 255))
            screen.blit(text, text.get_rect(center=mag_rect.center))
            
        for crystal in crystals:
            pygame.draw.rect(screen, config.COLOR_CRYSTAL, crystal, border_radius=5)
            
        for exit_rect in exits:
            pygame.draw.rect(screen, config.COLOR_EXIT, exit_rect)
            
        # Рисуем персонажей
        fire_boy.draw(screen)
        water_girl.draw(screen)
        
        # --- ОТРИСОВКА ИНТЕРФЕЙСА (UX критений) в черной нижней зоне ---
        pygame.draw.rect(screen, (40, 40, 45), (0, 300, config.SCREEN_WIDTH, 300)) # Разделитель панели
        
        ui_font = pygame.font.SysFont('Courier New', 20, bold=True)
        
        # Если игра продолжается, выводим счетчик
        if not game_over:
            level_text = ui_font.render(f"LEVEL: {current_level} / 5", True, (255, 255, 255))
            score_text = ui_font.render(f"SCORE: {score}", True, (255, 215, 0))
            controls_f = ui_font.render("FIRE (Red): Arrows to move", True, config.COLOR_FIRE)
            controls_w = ui_font.render("WATER (Blue): WASD to move", True, config.COLOR_WATER)
            
            screen.blit(level_text, (30, 330))
            screen.blit(score_text, (30, 370))
            screen.blit(controls_f, (400, 330))
            screen.blit(controls_w, (400, 370))
        else:
            # Экран финальной победы
            win_text = ui_font.render("CONGRATULATIONS! YOU BEAT THE GAME!", True, (0, 255, 0))
            screen.blit(win_text, (config.SCREEN_WIDTH // 2 - 200, 400))
            
        pygame.display.flip()
        clock.tick(config.FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
