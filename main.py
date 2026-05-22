import pygame
import sys
import config
from player import Player

def main():
    # Инициализация модулей Pygame
    pygame.init()
    
    # Создание окна приложения
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption("Elemental Co-op Game (1st Year Project)")
    
    # Контроллер времени (FPS)
    clock = pygame.time.Clock()
    
    # Настройка раскладки клавиатуры
    fire_keys = {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'jump': pygame.K_UP}
    water_keys = {'left': pygame.K_a, 'right': pygame.K_d, 'jump': pygame.K_w}
    
    # Инициализация объектов игроков
    fire_boy = Player(150, 400, config.COLOR_FIRE, fire_keys)
    water_girl = Player(250, 400, config.COLOR_WATER, water_keys)
    
    # Главный игровой цикл
    is_running = True
    while is_running:
        # Закрытие окна
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
                
        # Обновление состояний моделей (Model)
        fire_boy.update()
        water_girl.update()
        
        # Графическое представление сцены (View)
        screen.fill(config.COLOR_BG)
        
        # Временная тестовая платформа (земля)
        pygame.draw.rect(screen, config.COLOR_PLATFORM, (0, config.SCREEN_HEIGHT - 50, config.SCREEN_WIDTH, 50))
        
        # Отрисовка персонажей
        fire_boy.draw(screen)
        water_girl.draw(screen)
        
        # Обновление кадра на экране
        pygame.display.flip()
        
        # Стабилизация FPS
        clock.tick(FPS_LIMIT := config.FPS)

    # Корректный выход из игры
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
