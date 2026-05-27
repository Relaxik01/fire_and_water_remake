# player.py
import pygame
import config
import math

class Player:
    def __init__(self, x, y, color, controls, charge):
        self.rect = pygame.Rect(x, y, config.PLAYER_WIDTH, config.PLAYER_HEIGHT)
        self.color = color
        self.controls = controls
        self.charge = charge 
        
        self.velocity_x = 0
        self.velocity_y = 0
        self.is_grounded = False
        self.current_speed = config.MOVE_SPEED
        self.magnetic_boost_x = 0
        self.magnetic_boost_y = 0

        # Матрицы для рисования лиц персонажей
        self.face_matrix = [
            [0, 0, 0, 0, 0],
            [0, 1, 0, 1, 0],
            [0, 0, 0, 0, 0],
            [0, 1, 1, 1, 0],
            [0, 0, 0, 0, 0]
        ]

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
        """Физика магнитных полей """
        self.magnetic_boost_x = 0
        self.magnetic_boost_y = 0
        player_center = self.rect.center
        
        for mag_rect, mag_type in magnets:
            mag_center = mag_rect.center
            dx = player_center[0] - mag_center[0]
            dy = player_center[1] - mag_center[1]
            dist = math.sqrt(dx**2 + dy**2)
            
            if 0 < dist < config.MAGNET_RADIUS:
                dir_x = dx / dist
                dir_y = dy / dist
                force_magnitude = config.MAGNET_FORCE * (1 - dist / config.MAGNET_RADIUS)
                final_force = force_magnitude * (mag_type * self.charge)
                
                self.magnetic_boost_x += dir_x * final_force
                self.magnetic_boost_y += dir_y * final_force

    def update(self, platforms, magnets):
        self.handle_input()
        self.apply_magnet_force(magnets)
        
        self.velocity_y += config.GRAVITY
        total_vx = self.velocity_x + self.magnetic_boost_x
        total_vy = self.velocity_y + self.magnetic_boost_y
        
        self.rect.x += total_vx
        self.handle_collision(platforms, axis='x')
        
        self.rect.y += total_vy
        self.is_grounded = False
        self.handle_collision(platforms, axis='y')
        
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > config.SCREEN_WIDTH: self.rect.right = config.SCREEN_WIDTH

    def handle_collision(self, platforms, axis):
        vx = self.velocity_x + self.magnetic_boost_x
        vy = self.velocity_y + self.magnetic_boost_y
        
        for platform in platforms:
            if self.rect.colliderect(platform):
                if axis == 'x':
                    if vx > 0: self.rect.right = platform.left
                    if vx < 0: self.rect.left = platform.right
                if axis == 'y':
                    if vy > 0:
                        self.rect.bottom = platform.top
                        self.velocity_y = 0
                        self.is_grounded = True
                    if vy < 0:
                        self.rect.top = platform.bottom
                        self.velocity_y = 0

    def draw(self, target_surface):
        """Рисую форму Капли/Огня и лицо """
        if self.charge == 1:
            # Рисую ОГОНЬ
            points = [
                (self.rect.centerx, self.rect.top), # Верхушка пламени
                (self.rect.right, self.rect.bottom),
                (self.rect.left, self.rect.bottom)
            ]
            pygame.draw.polygon(target_surface, self.color, points)
        else:
            # Рисую ВОДУ
            pygame.draw.circle(target_surface, self.color, (self.rect.centerx, self.rect.bottom - 16), 16)
            points = [
                (self.rect.centerx, self.rect.top),
                (self.rect.centerx - 16, self.rect.bottom - 16),
                (self.rect.centerx + 16, self.rect.bottom - 16)
            ]
            pygame.draw.polygon(target_surface, self.color, points)

        # Рисую пиксельное лицо поверх формы
        start_x = self.rect.centerx - 10
        start_y = self.rect.centery - 5
        pixel_size = 4
        
        for r_idx, row in enumerate(self.face_matrix):
            for c_idx, val in enumerate(row):
                if val == 1:
                    face_pixel = pygame.Rect(start_x + c_idx * pixel_size, start_y + r_idx * pixel_size, pixel_size, pixel_size)
                    pygame.draw.rect(target_surface, (255, 255, 255), face_pixel)
