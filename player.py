import pygame
import config
import math

class Player:
    def __init__(self, x, y, color, controls, charge):
        self.rect = pygame.Rect(x, y, config.PLAYER_WIDTH, config.PLAYER_HEIGHT)
        self.color = color
        self.controls = controls
        # Заряд персонажа: +1 (Огонь), -1 (Вода)
        self.charge = charge 
        
        self.velocity_x = 0
        self.velocity_y = 0
        self.is_grounded = False
        self.current_speed = config.MOVE_SPEED
        # Дополнительная скорость от магнитов
        self.magnetic_boost_x = 0
        self.magnetic_boost_y = 0

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.velocity_x = 0
        
        if keys[self.controls['left']]:
            self.velocity_x = -self.current_speed
        if keys[self.controls['right']]:
            self.velocity_x = self.current_speed
            
        if keys[self.controls['jump']] and self.is_grounded:
            self.velocity_y = config.JUMP_FORCE
            self.is_grounded = False

    def apply_magnet_force(self, magnets):
        # Векторная физика магнитных полей
        self.magnetic_boost_x = 0
        self.magnetic_boost_y = 0
        
        player_center = self.rect.center
        
        for mag_rect, mag_type in magnets:
            mag_center = mag_rect.center
            
            # 1. Считаю расстояние между центрами (по теореме Пифагора)
            dx = player_center[0] - mag_center[0]
            dy = player_center[1] - mag_center[1]
            dist = math.sqrt(dx**2 + dy**2)
            
            # 2. Если я внутри радиуса действия магнита
            if 0 < dist < config.MAGNET_RADIUS:
                # Нормализация вектора
                dir_x = dx / dist
                dir_y = dy / dist
                
                # 3. Определяем притяжение или отталкивание (+ или - сила)
                force_magnitude = config.MAGNET_FORCE * (1 - dist / config.MAGNET_RADIUS)
                final_force = force_magnitude * (mag_type * self.charge)
                
                # Применяю силу к бусту скорости
                self.magnetic_boost_x += dir_x * final_force
                self.magnetic_boost_y += dir_y * final_force

    def update(self, platforms, magnets):
        self.handle_input()
        
        # Сначала считаю силы от магнитов
        self.apply_magnet_force(magnets)
        
        # Гравитация
        self.velocity_y += config.GRAVITY
        
        # Итоговая скорость = физика + буст от магнита
        total_vx = self.velocity_x + self.magnetic_boost_x
        total_vy = self.velocity_y + self.magnetic_boost_y
        
        # Движение по X
        self.rect.x += total_vx
        self.handle_collision(platforms, axis='x')
        
        # Движение по Y
        self.rect.y += total_vy
        self.is_grounded = False
        self.handle_collision(platforms, axis='y')
        
        # Ограничения экрана
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > config.SCREEN_WIDTH: self.rect.right = config.SCREEN_WIDTH

    def handle_collision(self, platforms, axis):
        """ Обработка коллизий (Model/Легкий алгоритм) """
        # Вектор скорости для коллизии я беру только основной
        vx = self.velocity_x + self.magnetic_boost_x
        vy = self.velocity_y + self.magnetic_boost_y
        
        for platform in platforms:
            if self.rect.colliderect(platform):
                if axis == 'x':
                    if vx > 0: # Двигаюсь вправо
                        self.rect.right = platform.left
                    if vx < 0: # Двигаюсь влево
                        self.rect.left = platform.right
                if axis == 'y':
                    if vy > 0: # Падаю вниз
                        self.rect.bottom = platform.top
                        self.velocity_y = 0
                        self.is_grounded = True
                    if vy < 0: # Лечу вверх
                        self.rect.top = platform.bottom
                        self.velocity_y = 0

    def draw(self, target_surface):
        pygame.draw.rect(target_surface, self.color, self.rect, border_radius=4)
