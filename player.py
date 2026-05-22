import pygame
import config

class Player:
    def __init__(self, x, y, color, controls):
        """
        Инициализация игрока.
        Словарь с кнопками управления (влево, вправо, прыжок)
        """
        # Класс Rect, отвечающий за определение хитбокса, будет содержать всю необходимую информацию об игроке.
        self.rect = pygame.Rect(x, y, config.PLAYER_WIDTH, config.PLAYER_HEIGHT)
        self.color = color
        self.controls = controls
        
        # Физические свойства объекта
        self.velocity_x = 0
        self.velocity_y = 0
        self.is_grounded = False  # Стоит ли персонаж на земле

    def handle_input(self):
        """ Считывание нажатий клавиш """
        keys = pygame.key.get_pressed()
        self.velocity_x = 0
        
        # Движение по горизонтали
        if keys[self.controls['left']]:
            self.velocity_x = -config.MOVE_SPEED
        if keys[self.controls['right']]:
            self.velocity_x = config.MOVE_SPEED
            
        # Логика прыжка (прыгнуть можно только с земли)
        if keys[self.controls['jump']] and self.is_grounded:
            self.velocity_y = config.JUMP_FORCE
            self.is_grounded = False

    def update(self):
        """ Математический расчет положения игрока (Model) """
        self.handle_input()
        
        # Применяю силу тяжести
        self.velocity_y += config.GRAVITY
        
        # Изменяю позиции хитбокса
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        
        # Временная коллизия с нижним краем экрана (чтобы не падать в бездну)
        if self.rect.bottom >= config.SCREEN_HEIGHT - 50:
            self.rect.bottom = config.SCREEN_HEIGHT - 50
            self.velocity_y = 0
            self.is_grounded = True
            
        # Ограничение движения, чтобы игроки не убегали за пределы экрана
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > config.SCREEN_WIDTH:
            self.rect.right = config.SCREEN_WIDTH

    def draw(self, target_surface):
        """ Визуализация персонажа на экране (View) """
        pygame.draw.rect(target_surface, self.color, self.rect, border_radius=4)
