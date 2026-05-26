import pygame
import sys
import config
from player import Player

def load_level(filename):
    """ Алгоритм парсинга карты"""
    platforms = []
    magnets = [] # Кортежи (pygame.Rect, type)
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
                        # Магнит Север (+) = заряд +1
                        magnets.append((rect, 1))
                    elif char == 'S':
                        # Магнит Юг (-) = заряд -1
                        magnets.append((rect, -1))
                    elif char == 'F':
                        player_positions['F'] = (rect.x, rect.y)
                    elif char == 'W':
                        player_positions['W'] = (rect.x, rect.y)
                        
    except FileNotFoundError:
        print(f"Критическая ошибка: Файл {filename} не найден!")
        pygame.quit()
        sys.exit()
        
    return platforms, magnets, player_positions

def main():
    pygame.init()
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption("Elemental Odyssey: Magnetic Fields")
    clock = pygame.time.Clock()
    
    # Загрузка уровня
    platforms, magnets, player_positions = load_level("level.txt")
    
    fire_keys = {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'jump': pygame.K_UP}
    water_keys = {'left': pygame.K_a, 'right': pygame.K_d, 'jump': pygame.K_w}
    
    # Спавним игроков, добавляем заряд (+1 и -1)
    fx, fy = player_positions.get('F', (100, 100))
    wx, wy = player_positions.get('W', (150, 100))
    
    fire_boy = Player(fx, fy, config.COLOR_FIRE, fire_keys, charge=1)
    water_girl = Player(wx, wy, config.COLOR_WATER, water_keys, charge=-1)
    
    is_running = True
    while is_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
                
        # 1. Модели
        fire_boy.update(platforms, magnets)
        water_girl.update(platforms, magnets)
        
        # 2. Отрендерить сцену (View)
        screen.fill(config.COLOR_BG)
        
        # Рисую карту
        for platform in platforms:
            pygame.draw.rect(screen, config.COLOR_PLATFORM, platform)
            
        # Рисую магниты
        for mag_rect, mag_type in magnets:
            color = config.COLOR_N if mag_type == 1 else config.COLOR_S
            pygame.draw.rect(screen, color, mag_rect, border_radius=4)
            # Рисую букву N или S внутри
            font = pygame.font.SysFont('Arial', 14, bold=True)
            text = font.render('N' if mag_type == 1 else 'S', True, (255, 255, 255))
            screen.blit(text, text.get_rect(center=mag_rect.center))
        
        # Рисую персонажей
        fire_boy.draw(screen)
        water_girl.draw(screen)
        
        pygame.display.flip()
        clock.tick(config.FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
