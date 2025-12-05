import pygame
import sys

# --- AYARLAR ---
pygame.init()
WIDTH, HEIGHT = 800, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Satranç Kalıp Bulucu - Pattern Explorer")
clock = pygame.time.Clock()

# Renkler (Modern Tema)
COLOR_BG = (45, 30, 60)        # Koyu Mor
COLOR_BOARD_LIGHT = (240, 230, 200) # Bej Kareler
COLOR_BOARD_DARK = (118, 150, 86)   # Yeşilimsi (Klasik Satranç)
COLOR_BTN = (160, 100, 220) 
COLOR_BTN_HOVER = (180, 130, 240)
COLOR_TEXT = (255, 255, 255)
COLOR_BLACK_PAWN = (20, 20, 20)
COLOR_WHITE_PAWN = (255, 255, 255)

# Fontlar
font_title = pygame.font.SysFont("Verdana", 32, bold=True)
font_ui = pygame.font.SysFont("Arial", 20)
font_big = pygame.font.SysFont("Arial", 40, bold=True)

# --- ALGORİTMA (MANTIK) ---
def find_patterns(n):
    valid_patterns = []
    
    def generate(current_pattern):
        if len(current_pattern) == n:
            valid_patterns.append(current_pattern)
            return

        last_color = current_pattern[-1]
        
        # Her zaman Beyaz eklenebilir
        generate(current_pattern + "B")
        
        # Siyah eklenebilir mi? (Önceki Siyah değilse)
        if last_color != "S":
            generate(current_pattern + "S")

    # Kural: İlk piyon Siyah olamaz -> B ile başla
    generate("B")
    return valid_patterns

# --- DEĞİŞKENLER ---
n_val = 3 # Başlangıç piyon sayısı
patterns = []
current_idx = 0
state = "MENU" # MENU, RESULT

# --- ÇİZİM FONKSİYONLARI ---
def draw_pawn(surface, color, x, y, size):
    # Piyon Çizimi (Geometrik Şekillerle)
    center_x = x + size // 2
    base_y = y + size - 10
    
    # Gövde (Üçgenimsi)
    pygame.draw.polygon(surface, color, [
        (center_x - size//4, base_y),
        (center_x + size//4, base_y),
        (center_x, y + size//3)
    ])
    # Kafa (Daire)
    pygame.draw.circle(surface, color, (center_x, y + size//3), size//5)
    # Taban
    pygame.draw.rect(surface, color, (center_x - size//3, base_y - 5, size//1.5, 5))
    
    # Kenar Çizgisi (Beyaz piyonlar belli olsun diye)
    if color == COLOR_WHITE_PAWN:
        pygame.draw.circle(surface, (0,0,0), (center_x, y + size//3), size//5, 2)

def draw_board(pattern):
    # Tahtayı Ortala
    square_size = 60
    total_w = len(pattern) * square_size
    start_x = (WIDTH - total_w) // 2
    start_y = 200
    
    for i, char in enumerate(pattern):
        x = start_x + i * square_size
        
        # Kare Çizimi
        color = COLOR_BOARD_LIGHT if i % 2 == 0 else COLOR_BOARD_DARK
        pygame.draw.rect(screen, color, (x, start_y, square_size, square_size))
        pygame.draw.rect(screen, (0,0,0), (x, start_y, square_size, square_size), 2) # Çerçeve
        
        # Piyon Çizimi
        pawn_color = COLOR_BLACK_PAWN if char == 'S' else COLOR_WHITE_PAWN
        draw_pawn(screen, pawn_color, x, start_y, square_size)
        
        # Altına Yazı (B/S)
        txt = font_ui.render(char, True, COLOR_TEXT)
        screen.blit(txt, (x + square_size//2 - 5, start_y + square_size + 5))

def draw_button(text, rect, active=True):
    mouse_pos = pygame.mouse.get_pos()
    color = COLOR_BTN
    if active and rect.collidepoint(mouse_pos):
        color = COLOR_BTN_HOVER
    if not active:
        color = (100, 100, 100) # Gri (Pasif)
        
    pygame.draw.rect(screen, color, rect, border_radius=10)
    txt_surf = font_ui.render(text, True, COLOR_TEXT)
    screen.blit(txt_surf, (rect.x + (rect.width - txt_surf.get_width())//2, rect.y + 10))
    return rect

# --- EKRANLAR ---
def screen_menu():
    global n_val, state, patterns, current_idx
    
    screen.fill(COLOR_BG)
    
    # Başlık
    title = font_title.render("SATRANÇ KALIP BULUCU", True, COLOR_TEXT)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
    
    sub = font_ui.render("Kural: İlk piyon Siyah olamaz, Çift Siyah yan yana gelemez.", True, (200, 200, 200))
    screen.blit(sub, (WIDTH//2 - sub.get_width()//2, 140))

    # Sayaç (N Değeri)
    txt_n = font_big.render(f"Piyon Sayısı: {n_val}", True, COLOR_TEXT)
    screen.blit(txt_n, (WIDTH//2 - txt_n.get_width()//2, 250))

    # Butonlar (- / +)
    btn_minus = pygame.Rect(WIDTH//2 - 120, 320, 50, 50)
    btn_plus = pygame.Rect(WIDTH//2 + 70, 320, 50, 50)
    
    draw_button("-", btn_minus)
    draw_button("+", btn_plus)
    
    # Hesapla Butonu
    btn_calc = pygame.Rect(WIDTH//2 - 100, 400, 200, 50)
    draw_button("HESAPLA", btn_calc)
    
    # Event Yönetimi
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if btn_minus.collidepoint(event.pos) and n_val > 1:
                n_val -= 1
            if btn_plus.collidepoint(event.pos) and n_val < 10: # Ekran sığsın diye sınır 10
                n_val += 1
            if btn_calc.collidepoint(event.pos):
                patterns = find_patterns(n_val)
                current_idx = 0
                state = "RESULT"

def screen_result():
    global state, current_idx
    
    screen.fill(COLOR_BG)
    
    # Üst Bilgi
    title = font_title.render(f"Sonuçlar (N={n_val})", True, COLOR_TEXT)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
    
    info = font_ui.render(f"Toplam {len(patterns)} farklı dizilim bulundu.", True, (200, 255, 200))
    screen.blit(info, (WIDTH//2 - info.get_width()//2, 100))
    
    # Kalıbı Çiz
    if patterns:
        pattern_str = patterns[current_idx]
        draw_board(pattern_str)
        
        # Sayaç (1 / 5)
        counter = font_ui.render(f"{current_idx + 1} / {len(patterns)}", True, COLOR_TEXT)
        screen.blit(counter, (WIDTH//2 - counter.get_width()//2, 300))

    # Navigasyon Butonları
    btn_prev = pygame.Rect(WIDTH//2 - 150, 350, 100, 40)
    btn_next = pygame.Rect(WIDTH//2 + 50, 350, 100, 40)
    btn_back = pygame.Rect(WIDTH//2 - 100, 420, 200, 50)
    
    draw_button("< Önceki", btn_prev, active=(current_idx > 0))
    draw_button("Sonraki >", btn_next, active=(current_idx < len(patterns)-1))
    draw_button("YENİ HESAPLA", btn_back)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if btn_prev.collidepoint(event.pos) and current_idx > 0:
                current_idx -= 1
            if btn_next.collidepoint(event.pos) and current_idx < len(patterns)-1:
                current_idx += 1
            if btn_back.collidepoint(event.pos):
                state = "MENU"

# --- ANA DÖNGÜ ---
while True:
    if state == "MENU":
        screen_menu()
    elif state == "RESULT":
        screen_result()
        
    pygame.display.flip()
    clock.tick(30)