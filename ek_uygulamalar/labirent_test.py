import unittest
import sys
import os

# Pygame başlatmadan modülü import etmek için
# (Normalde import edince oyun başlar, bunu engellemek için kodun __main__ kısmında olmalı)
# Burada sadece mantığı test edeceğimiz için fonksiyonları mock (taklit) edebiliriz veya
# oyun kodundaki mantık fonksiyonlarını import edebiliriz.

# Basitlik için oyun mantığını buraya simüle ediyoruz (White Box Test)
# Çünkü oyun kodu 'while True' döngüsüne girdiği için doğrudan import edilirse testler çalışmaz.

# --- TEST EDİLECEK FONKSİYONLAR ---
def check_wall_collision(r, c, maze_map):
    # Harita sınırları ve duvar kontrolü
    if r < 0 or r >= len(maze_map) or c < 0 or c >= len(maze_map[0]):
        return True # Dışarı çıktı (Duvar gibi davran)
    if maze_map[r][c] == 1:
        return True # Duvar
    return False

def check_cheese_found(r, c, maze_map):
    if maze_map[r][c] == 2:
        return True
    return False

def move_player(current_pos, direction):
    r, c = current_pos
    if direction == "UP": r -= 1
    elif direction == "DOWN": r += 1
    elif direction == "LEFT": c -= 1
    elif direction == "RIGHT": c += 1
    return [r, c]

# --- TEST SENARYOLARI ---
class TestMazeGame(unittest.TestCase):

    def setUp(self):
        # 1: Duvar, 0: Yol, 2: Peynir, 9: Başlangıç
        self.test_map = [
            [1, 1, 1, 1, 1],
            [1, 9, 0, 2, 1], # Fare(1,1), Peynir(1,3)
            [1, 0, 1, 1, 1],
            [1, 1, 1, 1, 1]
        ]
        self.player_pos = [1, 1]

    # TEST 1: Duvara Çarpma Kontrolü
    def test_wall_collision(self):
        print("\n--- Test 1: Duvar Engeli ---")
        # Yukarı gitmeyi dene (1,1 -> 0,1). 0,1'de Duvar (1) var.
        next_pos = move_player(self.player_pos, "UP")
        is_collision = check_wall_collision(next_pos[0], next_pos[1], self.test_map)
        
        self.assertTrue(is_collision, "Hata: Duvar engellemedi!")
        print("Duvar testi başarılı.")

    # TEST 2: Geçerli Hareket Kontrolü
    def test_valid_move(self):
        print("\n--- Test 2: Geçerli Hareket ---")
        # Sağa gitmeyi dene (1,1 -> 1,2). 1,2'de Yol (0) var.
        next_pos = move_player(self.player_pos, "RIGHT")
        is_collision = check_wall_collision(next_pos[0], next_pos[1], self.test_map)
        
        self.assertFalse(is_collision, "Hata: Yol engellendi!")
        self.assertEqual(next_pos, [1, 2])
        print("Hareket testi başarılı.")

    # TEST 3: Peyniri Bulma Kontrolü
    def test_find_cheese(self):
        print("\n--- Test 3: Peynir Bulma ---")
        # Peynirin olduğu konuma (1,3) gitmiş gibi yapalım
        cheese_pos = [1, 3]
        found = check_cheese_found(cheese_pos[0], cheese_pos[1], self.test_map)
        
        self.assertTrue(found, "Hata: Peynir bulunamadı!")
        print("Peynir tespiti başarılı.")

    # TEST 4: Harita Sınırları
    def test_map_boundaries(self):
        print("\n--- Test 4: Harita Dışı ---")
        # Harita dışına çıkmayı dene (-1, 1)
        out_pos = [-1, 1]
        is_collision = check_wall_collision(out_pos[0], out_pos[1], self.test_map)
        
        self.assertTrue(is_collision, "Hata: Harita dışına çıkıldı!")
        print("Sınır kontrolü başarılı.")

if __name__ == '__main__':
    unittest.main()