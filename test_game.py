import unittest
import pygame
import os
import config
from main import load_level
from player import Player

class TestElementalOdyssey(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Инициализация Pygame один раз для тестов, чтобы работал класс Player"""
        pygame.init()
        # Временный тестовый файл карты
        cls.test_filename = "level_test_map.txt"
        cls.test_content = (
            "########################################\n"
            "#..F...W..............................E#\n"
            "#..C.......................X..........E#\n"
            "########################################\n"
        )
        with open(cls.test_filename, "w") as f:
            f.write(cls.test_content)

    @classmethod
    def tearDownClass(cls):
        """Удаление временного файла после прохождения тестов"""
        if os.path.exists(cls.test_filename):
            os.remove(cls.test_filename)
        pygame.quit()

    def test_01_load_level_success(self):
        """Тест алгоритма загрузки существующего уровня"""
        result = load_level(1)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 6)

    def test_02_load_non_existent_level(self):
        """Загрузка несуществующего уровня"""
        result = load_level(999)
        self.assertIsNone(result)

    def test_03_player_initialization(self):
        """Тест корректного создания объекта игрока и его хитбокса"""
        keys = {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'jump': pygame.K_UP}
        player = Player(100, 200, (255, 0, 0), keys, charge=1)
        
        self.assertEqual(player.rect.x, 100)
        self.assertEqual(player.rect.y, 200)
        self.assertEqual(player.charge, 1)

    def test_04_crystal_collection_logic(self):
        """Сбор кристалла"""
        keys = {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'jump': pygame.K_UP}
        player = Player(100, 100, (255, 0, 0), keys, charge=1)
        
        crystal_hit = pygame.Rect(100, 100, config.BLOCK_SIZE, config.BLOCK_SIZE)
        crystal_miss = pygame.Rect(500, 500, config.BLOCK_SIZE, config.BLOCK_SIZE)
        
        self.assertTrue(player.rect.colliderect(crystal_hit))
        self.assertFalse(player.rect.colliderect(crystal_miss))

if __name__ == '__main__':
    unittest.main()
