import unittest

# --- TEST EDİLECEK MANTIK FONKSİYONLARI ---
# (Oyun arayüzünden bağımsız olarak mantığı buraya kopyalıyoruz ki 
# arayüz açılmadan test edebilelim)

def check_win_logic(board, player):
    """
    Verilen tahtada belirtilen oyuncunun kazanıp kazanmadığını kontrol eder.
    """
    wins = [(0,1,2),(3,4,5),(6,7,8), # Yatay
            (0,3,6),(1,4,7),(2,5,8), # Dikey
            (0,4,8),(2,4,6)]         # Çapraz
    
    for a,b,c in wins:
        if board[a] == board[b] == board[c] == player:
            return True
    return False

def check_draw_logic(board):
    """
    Beraberlik durumunu kontrol eder (Tahta dolu ve kazanan yok).
    """
    if "" not in board and not check_win_logic(board, 'X') and not check_win_logic(board, 'O'):
        return True
    return False

class TestXOXGame(unittest.TestCase):
    
    def setUp(self):
        # Her testten önce boş bir tahta oluştur
        self.board = [""] * 9

    # --- TEST CASE 1: YATAY KAZANMA ---
    def test_horizontal_win(self):
        print("\n--- Test 1: Yatay Kazanma Kontrolü ---")
        # X oyuncusu üst satırı dolduruyor
        self.board[0] = 'X'
        self.board[1] = 'X'
        self.board[2] = 'X'
        
        is_winner = check_win_logic(self.board, 'X')
        self.assertTrue(is_winner, "Hata: Yatay 3'lü seri kazanmadı!")
        print(" X oyuncusu yatayda kazandı.")

    # --- TEST CASE 2: DİKEY KAZANMA ---
    def test_vertical_win(self):
        print("\n--- Test 2: Dikey Kazanma Kontrolü ---")
        # O oyuncusu sol sütunu dolduruyor
        self.board[0] = 'O'
        self.board[3] = 'O'
        self.board[6] = 'O'
        
        is_winner = check_win_logic(self.board, 'O')
        self.assertTrue(is_winner, "Hata: Dikey 3'lü seri kazanmadı!")
        print(" O oyuncusu dikeyde kazandı.")

    # --- TEST CASE 3: ÇAPRAZ KAZANMA ---
    def test_diagonal_win(self):
        print("\n--- Test 3: Çapraz Kazanma Kontrolü ---")
        # X oyuncusu çapraz yapıyor
        self.board[0] = 'X'
        self.board[4] = 'X'
        self.board[8] = 'X'
        
        is_winner = check_win_logic(self.board, 'X')
        self.assertTrue(is_winner, "Hata: Çapraz 3'lü seri kazanmadı!")
        print(" X oyuncusu çaprazda kazandı.")

    # --- TEST CASE 4: BERABERLİK ---
    def test_draw_condition(self):
        print("\n--- Test 4: Beraberlik Kontrolü ---")
        # Berabere biten bir tahta simülasyonu
        # X O X
        # X O O
        # O X X
        self.board = ['X', 'O', 'X', 
                      'X', 'O', 'O', 
                      'O', 'X', 'X']
        
        is_draw = check_draw_logic(self.board)
        self.assertTrue(is_draw, "Hata: Tahta doluyken oyun bitmedi!")
        print(" Oyun berabere bitti.")

if __name__ == '__main__':
    unittest.main()