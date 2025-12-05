import unittest

# --- TEST EDİLECEK MANTIK ---
# (Algoritmayı buraya dahil ettik ki test bağımsız çalışabilsin)
def find_patterns_logic(n):
    valid_patterns = []
    
    def generate(current_pattern):
        if len(current_pattern) == n:
            valid_patterns.append(current_pattern)
            return

        last_color = current_pattern[-1]
        
        # Her zaman Beyaz (B) eklenebilir
        generate(current_pattern + "B")
        
        # Siyah (S) sadece önceki Siyah değilse eklenebilir
        if last_color != "S":
            generate(current_pattern + "S")

    # Kural 1: İlk piyon Siyah olamaz -> B ile başla
    if n > 0:
        generate("B")
    
    return valid_patterns

class TestChessPattern(unittest.TestCase):

    # --- TEST 1: N=3 İçin Doğruluk Kontrolü ---
    def test_n_3_results(self):
        print("\n--- Test 1: N=3 Senaryosu ---")
        sonuclar = find_patterns_logic(3)
        # Beklenen: BBB, BBS, BSB (Toplam 3)
        # BSS olamaz (çift S), S... olamaz (başlangıç)
        expected = ["BBB", "BBS", "BSB"]
        
        self.assertEqual(len(sonuclar), 3, "Eleman sayısı hatalı!")
        self.assertEqual(sorted(sonuclar), sorted(expected), "Dizilimler hatalı!")
        print(f" N=3 için sonuçlar doğru: {sonuclar}")

    # --- TEST 2: 'S' ile Başlamama Kuralı ---
    def test_start_rule(self):
        print("\n--- Test 2: Başlangıç Kuralı (S Olamaz) ---")
        # N=5 için deneyelim
        sonuclar = find_patterns_logic(5)
        for patern in sonuclar:
            self.assertFalse(patern.startswith("S"), f"HATA: {patern} S ile başlıyor!")
        print("Hiçbir dizilim Siyah ile başlamıyor.")

    # --- TEST 3: 'SS' (Yan Yana Siyah) Kuralı ---
    def test_double_black_rule(self):
        print("\n--- Test 3: Çift Siyah (SS) Kuralı ---")
        sonuclar = find_patterns_logic(6)
        for patern in sonuclar:
            self.assertFalse("SS" in patern, f"HATA: {patern} içinde SS var!")
        print("Hiçbir dizilimde yan yana Siyah yok.")

if __name__ == '__main__':
    unittest.main()