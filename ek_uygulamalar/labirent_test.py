import unittest

# Test için sanal bir harita ve hareket fonksiyonu tanımlıyoruz
# (Pygame grafiklerini test edemeyiz, mantığı test ederiz)

# 1: Duvar, 0: Yol, 2: Peynir, 9: Fare
test_map = [
    [1, 1, 1, 1],
    [1, 9, 0, 2], # Fare (1,1), Peynir (1,3)
    [1, 1, 1, 1]
]

def check_move(current_pos, direction):
    r, c = current_pos
    if direction == "UP": r -= 1
    elif direction == "DOWN": r += 1
    elif direction == "LEFT": c -= 1
    elif direction == "RIGHT": c += 1
    
    # Duvar kontrolü
    if test_map[r][c] == 1:
        return current_pos, "DUVAR"
    # Peynir kontrolü
    elif test_map[r][c] == 2:
        return [r, c], "WIN"
    else:
        return [r, c], "OK"

class TestMazeGame(unittest.TestCase):

    # Test 1: Duvara Çarpma
    def test_wall_collision(self):
        start_pos = [1, 1]
        # Yukarıda duvar var (0,1) -> 1
        new_pos, status = check_move(start_pos, "UP")
        self.assertEqual(status, "DUVAR")
        self.assertEqual(new_pos, start_pos) # Hareket etmemeli
        print("Duvar Testi Başarılı")

    # Test 2: Normal Hareket
    def test_normal_move(self):
        start_pos = [1, 1]
        # Sağda yol var (1,2) -> 0
        new_pos, status = check_move(start_pos, "RIGHT")
        self.assertEqual(status, "OK")
        self.assertEqual(new_pos, [1, 2])
        print("Hareket Testi Başarılı")

    # Test 3: Peyniri Bulma
    def test_find_cheese(self):
        current_pos = [1, 2]
        # Sağda peynir var (1,3) -> 2
        new_pos, status = check_move(current_pos, "RIGHT")
        self.assertEqual(status, "WIN")
        print("Peynir Testi Başarılı")

if __name__ == '__main__':
    unittest.main()