import unittest

# --- TEST EDİLECEK MANTIK ---
# Oyunun içindeki kazanma algoritmasının aynısını buraya alıyoruz.
def check_win_logic(board, player):
    """
    Verilen tahtada (board) belirtilen oyuncunun (player) 
    kazanıp kazanmadığını kontrol eder.
    """
    # Kazanma Kombinasyonları (İndeksler)
    wins = [
        (0,1,2), (3,4,5), (6,7,8), # Yatay
        (0,3,6), (1,4,7), (2,5,8), # Dikey
        (0,4,8), (2,4,6)           # Çapraz
    ]
    
    for a, b, c in wins:
        # Eğer üç kutuda da aynı oyuncunun sembolü varsa kazanmıştır
        if board[a] == board[b] == board[c] == player:
            return True
    return False

def check_draw_logic(board):
    """
    Beraberlik durumunu kontrol eder (Tahta dolu ve kazanan yok).
    """
    # Tahtada boş yer ("") yoksa VE X kazanmadıysa VE O kazanmadıysa -> Berabere
    if "" not in board and not check_win_logic(board, 'X') and not check_win_logic(board, 'O'):
        return True
    return False

class TestXOXGame(unittest.TestCase):
    
    def setUp(self):
        # Her testten önce boş bir tahta oluştur (9 adet boş string)
        self.board = [""] * 9

    # --- TEST CASE 1: YATAY KAZANMA ---
    def test_horizontal_win(self):
        print("\n--- Test 1: Yatay Kazanma Kontrolü ---")
        # Senaryo: X oyuncusu ilk satırı (0, 1, 2) dolduruyor
        self.board[0] = 'X'
        self.board[1] = 'X'
        self.board[2] = 'X'
        
        is_winner = check_win_logic(self.board, 'X')
        
        self.assertTrue(is_winner, "Hata: Yatay 3'lü seri kazanmadı!")
        print(" X oyuncusu yatayda (0-1-2) kazandı.")

    # --- TEST CASE 2: DİKEY KAZANMA ---
    def test_vertical_win(self):
        print("\n--- Test 2: Dikey Kazanma Kontrolü ---")
        # Senaryo: O oyuncusu sol sütunu (0, 3, 6) dolduruyor
        self.board[0] = 'O'
        self.board[3] = 'O'
        self.board[6] = 'O'
        
        is_winner = check_win_logic(self.board, 'O')
        
        self.assertTrue(is_winner, "Hata: Dikey 3'lü seri kazanmadı!")
        print("O oyuncusu dikeyde (0-3-6) kazandı.")

    # --- TEST CASE 3: ÇAPRAZ KAZANMA ---
    def test_diagonal_win(self):
        print("\n--- Test 3: Çapraz Kazanma Kontrolü ---")
        # Senaryo: X oyuncusu çapraz (0, 4, 8) yapıyor
        self.board[0] = 'X'
        self.board[4] = 'X'
        self.board[8] = 'X'
        
        is_winner = check_win_logic(self.board, 'X')
        
        self.assertTrue(is_winner, "Hata: Çapraz 3'lü seri kazanmadı!")
        print("X oyuncusu çaprazda (0-4-8) kazandı.")

    # --- TEST CASE 4: BERABERLİK ---
    def test_draw_condition(self):
        print("\n--- Test 4: Beraberlik Kontrolü ---")
        # Senaryo: Tahta dolu ama kazanan yok
        self.board = ['X', 'O', 'X', 
                      'X', 'O', 'O', 
                      'O', 'X', 'X']
        
        is_draw = check_draw_logic(self.board)
        self.assertTrue(is_draw, "Hata: Tahta doluyken oyun bitmedi!")
        print("Oyun berabere bitti.")

# --- İŞTE BU KISIM EKSİKTİ ---
if __name__ == '__main__':
    unittest.main()