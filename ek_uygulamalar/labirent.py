import pygame
import sys
import os
import time
import random

# --- AYARLAR ---
sys.setrecursionlimit(5000) 

try:
    pygame.init()
except Exception as e:
    print(f"Hata: {e}")
    sys.exit()

TILE_SIZE = 50 
COLS, ROWS = 15, 12
WIDTH, HEIGHT = COLS * TILE_SIZE, ROWS * TILE_SIZE + 80 # Alt panel için +80 px

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Labirent - Retry Özellikli")
clock = pygame.time.Clock()# FPS (kare hızı) kontrolü için saat objesi

# Fontlar
font_title = pygame.font.SysFont("Arial", 36, bold=True)
font_ui = pygame.font.SysFont("Arial", 18)
font_input = pygame.font.SysFont("Arial", 24)
font_btn_small = pygame.font.SysFont("Arial", 16, bold=True)

# Renkler
COLOR_BG = (45, 30, 60)        
COLOR_WALL = (240, 230, 200)   
COLOR_PATH = (60, 45, 80)      
COLOR_BUTTON = (160, 100, 220) 
COLOR_BUTTON_HOVER = (180, 130, 240)
COLOR_EXIT_BTN = (200, 60, 60)
COLOR_RETRY_BTN = (60, 180, 100) # Tekrar butonu için yeşilimsi
COLOR_TEXT = (255, 250, 220)   
COLOR_P1_BACKUP = (100, 200, 255) 
COLOR_P2_BACKUP = (255, 100, 100) 
COLOR_CHEESE_BACKUP = (255, 200, 50) 

# --- RESİM YÜKLEME fare --- 
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
IMG_PATH = os.path.join(BASE_PATH, "images") 
if not os.path.exists(IMG_PATH): IMG_PATH = os.path.join(BASE_PATH, "resimler")

def load_and_scale(filename):
    full_path = os.path.join(IMG_PATH, filename)
    if os.path.exists(full_path):
        try:
            img = pygame.image.load(full_path)
            return pygame.transform.scale(img, (TILE_SIZE - 5, TILE_SIZE - 5))
        except: return None
    return None

img_mouse1 = load_and_scale("mouse.png")
img_mouse2 = load_and_scale("mouse2.png")
img_cheese = load_and_scale("cheese.png")

# --- DEĞİŞKENLER ---
current_map = [] #labirent haritası
p1_pos = [1, 1]
p2_pos = [1, 1]
mode = "MENU" 
moves_p1 = 0 #hamle sayacı
moves_p2 = 0
winner_msg = ""
auto_path = [] # Bilgisayarın bulduğu çözüm yolu
p1_name = "Oyuncu 1"
p2_name = "Oyuncu 2"
input_active_idx = 1
temp_name = ""

# --- FONKSİYONLAR --- """Recursive Backtracking algoritması ile rastgele labirent oluşturur."""
def generate_maze(rows, cols):
    maze = [[1 for _ in range(cols)] for _ in range(rows)]
    def carve(cx, cy):
        dirs = [(0, 2), (0, -2), (2, 0), (-2, 0)]
        random.shuffle(dirs) # Rastgelelik katmak için yönleri karıştırıyoruz
        for dx, dy in dirs:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < rows and 0 <= ny < cols and maze[nx][ny] == 1:
                maze[cx + dx//2][cy + dy//2] = 0
                maze[nx][ny] = 0
                carve(nx, ny)
    maze[1][1] = 0 # Başlangıç noktası
    carve(1, 1)
    maze[1][1] = 9 
    placed = False
    while not placed:
        r, c = random.randint(1, rows-2), random.randint(1, cols-2)
        if maze[r][c] == 0:
            maze[r][c] = 2
            placed = True
    return maze

#"""Oyunu sıfırlar ve başlatır."""
def start_game(selected_mode):
    global current_map, p1_pos, p2_pos, moves_p1, moves_p2, mode, auto_path, p1_name
    current_map = generate_maze(ROWS, COLS)
    p1_pos = [1, 1] # Konumları sıfırla
    p2_pos = [1, 1]
    moves_p1 = 0
    moves_p2 = 0
    mode = selected_mode # Modu koru veya güncelle
    
    if mode == "SINGLE" and p1_name == "Oyuncu 1": p1_name = "Oyuncu"
    if mode == "AUTO": 
        auto_path = get_auto_path()
        p1_name = "Bilgisayar"

#"""Bilgisayar için labirenti çözen fonksiyon."""
def get_auto_path():
    path = []
    visited = set() # Ziyaret edilen kareleri tutar (sonsuz döngüyü engeller)
    def solve(r, c):
        if current_map[r][c] == 2: return True
        visited.add((r,c))
        dirs = [(1,0), (0,1), (-1,0), (0,-1)]
        random.shuffle(dirs)
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS:
                if current_map[nr][nc] != 1 and (nr,nc) not in visited:
                    path.append((nr, nc))
                    if solve(nr, nc): return True
                    path.pop()# Ziyaret edilen kareleri tutar (sonsuz döngüyü engeller)
        return False
    solve(p1_pos[0], p1_pos[1])
    return path

# --- ÇİZİM ---
def draw_menu():
    screen.fill(COLOR_BG)
    title = font_title.render("LABİRENT OYUNU", True, COLOR_TEXT)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))

    btn1 = pygame.Rect(WIDTH//2 - 120, 200, 240, 50)
    btn2 = pygame.Rect(WIDTH//2 - 120, 270, 240, 50)
    btn3 = pygame.Rect(WIDTH//2 - 120, 340, 240, 50)
    
    m_pos = pygame.mouse.get_pos()
    buttons = [(btn1, "TEK KİŞİLİK"), (btn2, "İKİ KİŞİLİK"), (btn3, "AUTO ÇÖZÜM")]
    
    for btn, text in buttons:
        color = COLOR_BUTTON_HOVER if btn.collidepoint(m_pos) else COLOR_BUTTON
        pygame.draw.rect(screen, color, btn, border_radius=10)
        txt = font_ui.render(text, True, COLOR_TEXT)
        screen.blit(txt, (btn.centerx - txt.get_width()//2, btn.centery - txt.get_height()//2))
        
    return btn1, btn2, btn3

def draw_input_names():
    screen.fill(COLOR_BG)
    header = "1. Oyuncu İsmi" if input_active_idx == 1 else "2. Oyuncu İsmi"
    t = font_title.render(header, True, COLOR_TEXT)
    screen.blit(t, (WIDTH//2 - t.get_width()//2, 150))
    
    box = pygame.Rect(WIDTH//2 - 150, 250, 300, 50)
    pygame.draw.rect(screen, COLOR_WALL, box, border_radius=10)
    txt = font_input.render(temp_name, True, COLOR_BG)
    screen.blit(txt, (box.x + 10, box.y + 10))

def draw_gameover():
    s = pygame.Surface((WIDTH, HEIGHT))
    s.set_alpha(150); s.fill((0,0,0))
    screen.blit(s, (0,0))
    
    msg = font_title.render(winner_msg, True, (255, 215, 0))
    screen.blit(msg, (WIDTH//2 - msg.get_width()//2, 200))
    
    # Sadece menüye dön butonu burada kalsın
    btn = pygame.Rect(WIDTH//2 - 100, 300, 200, 60)
    pygame.draw.rect(screen, COLOR_BUTTON, btn, border_radius=10)
    t = font_ui.render("MENÜYE DÖN", True, COLOR_TEXT)
    screen.blit(t, (btn.centerx - t.get_width()//2, btn.centery - t.get_height()//2))
    return btn

def draw_game():
    screen.fill(COLOR_BG)
    # Harita
    for r in range(ROWS):
        for c in range(COLS):
            x, y = c * TILE_SIZE, r * TILE_SIZE
            tile = current_map[r][c]
            if tile == 1: 
                pygame.draw.rect(screen, COLOR_WALL, (x, y, TILE_SIZE, TILE_SIZE))
                pygame.draw.rect(screen, (200, 190, 160), (x, y, TILE_SIZE, TILE_SIZE), 2)
            elif tile == 2: 
                if img_cheese: screen.blit(img_cheese, (x+2, y+2))
                else: pygame.draw.circle(screen, COLOR_CHEESE_BACKUP, (x+25, y+25), 15)
            else: pygame.draw.rect(screen, COLOR_PATH, (x+2, y+2, TILE_SIZE-4, TILE_SIZE-4))

    # Oyuncular
    x1, y1 = p1_pos[1]*TILE_SIZE, p1_pos[0]*TILE_SIZE
    if img_mouse1: screen.blit(img_mouse1, (x1+2, y1+2))
    else: pygame.draw.rect(screen, COLOR_P1_BACKUP, (x1+10,y1+10,30,30), border_radius=5)
    
    if mode == "MULTI":
        x2, y2 = p2_pos[1]*TILE_SIZE, p2_pos[0]*TILE_SIZE
        if img_mouse2: screen.blit(img_mouse2, (x2+2, y2+2))
        else: pygame.draw.rect(screen, COLOR_P2_BACKUP, (x2+15,y2+15,20,20), border_radius=5)

    # --- ALT PANEL ---
    py = ROWS * TILE_SIZE
    pygame.draw.rect(screen, (30, 20, 40), (0, py, WIDTH, 80))
    pygame.draw.line(screen, COLOR_WALL, (0, py), (WIDTH, py), 3)
    
    # İsimler ve Skor
    info_text = f"{p1_name}: {moves_p1}" if mode != "MULTI" else f"{p1_name}: {moves_p1}  |  {p2_name}: {moves_p2}"
    t = font_ui.render(info_text, True, COLOR_TEXT)
    screen.blit(t, (20, py + 30))

    # --- BUTONLAR (TEKRAR | MENÜ | ÇIKIŞ) ---
    m_pos = pygame.mouse.get_pos()
    
    # 1. Tekrar (Retry)
    btn_retry = pygame.Rect(WIDTH - 290, py + 20, 80, 40)
    c_retry = (80, 200, 120) if btn_retry.collidepoint(m_pos) else COLOR_RETRY_BTN
    pygame.draw.rect(screen, c_retry, btn_retry, border_radius=8)
    t_retry = font_btn_small.render("TEKRAR", True, COLOR_TEXT)
    screen.blit(t_retry, (btn_retry.centerx - t_retry.get_width()//2, btn_retry.centery - t_retry.get_height()//2))

    # 2. Menü
    btn_menu = pygame.Rect(WIDTH - 200, py + 20, 80, 40)
    c_menu = COLOR_BUTTON_HOVER if btn_menu.collidepoint(m_pos) else COLOR_BUTTON
    pygame.draw.rect(screen, c_menu, btn_menu, border_radius=8)
    t_menu = font_btn_small.render("MENÜ", True, COLOR_TEXT)
    screen.blit(t_menu, (btn_menu.centerx - t_menu.get_width()//2, btn_menu.centery - t_menu.get_height()//2))

    # 3. Çıkış
    btn_exit = pygame.Rect(WIDTH - 110, py + 20, 80, 40)
    c_exit = (220, 80, 80) if btn_exit.collidepoint(m_pos) else COLOR_EXIT_BTN
    pygame.draw.rect(screen, c_exit, btn_exit, border_radius=8)
    t_exit = font_btn_small.render("ÇIKIŞ", True, COLOR_TEXT)
    screen.blit(t_exit, (btn_exit.centerx - t_exit.get_width()//2, btn_exit.centery - t_exit.get_height()//2))

    return btn_retry, btn_menu, btn_exit

# --- OYUN DÖNGÜSÜ ---
try:
    current_map = generate_maze(ROWS, COLS)

    while True:
        # Buton rect'lerini çizimden önce veya içinde almamız lazım, 
        # ama olay döngüsü çizimden bağımsız çalışmalı. 
        # Basitlik için panel koordinatlarını burada manuel biliyoruz:
        py = ROWS * TILE_SIZE
        # Olaylar için rect tanımları (Draw fonksiyonundakilerle aynı olmalı)
        rect_retry = pygame.Rect(WIDTH - 290, py + 20, 80, 40)
        rect_menu = pygame.Rect(WIDTH - 200, py + 20, 80, 40)
        rect_exit = pygame.Rect(WIDTH - 110, py + 20, 80, 40)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            # --- OYUN İÇİ TIKLAMALAR ---
            if mode in ["SINGLE", "MULTI", "AUTO"]:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if rect_retry.collidepoint(event.pos):
                        print("Yeniden başlatılıyor...")
                        start_game(mode) # Mevcut modda oyunu sıfırla
                    elif rect_menu.collidepoint(event.pos):
                        mode = "MENU"
                    elif rect_exit.collidepoint(event.pos):
                        pygame.quit(); sys.exit()

            # --- MENÜ MODU ---
            if mode == "MENU":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    b1, b2, b3 = draw_menu()
                    if b1.collidepoint(event.pos): start_game("SINGLE")
                    elif b2.collidepoint(event.pos): 
                        mode = "INPUT_NAMES"; input_active_idx = 1; temp_name = ""
                    elif b3.collidepoint(event.pos): start_game("AUTO")
            
            # --- İSİM GİRİŞ MODU ---
            elif mode == "INPUT_NAMES":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if input_active_idx == 1:
                            p1_name = temp_name if temp_name else "Oyuncu 1"
                            input_active_idx = 2; temp_name = ""
                        else:
                            p2_name = temp_name if temp_name else "Oyuncu 2"
                            start_game("MULTI")
                    elif event.key == pygame.K_BACKSPACE: temp_name = temp_name[:-1]
                    else: 
                        if len(temp_name) < 12: temp_name += event.unicode
            
            # --- GAMEOVER MODU ---
            elif mode == "GAMEOVER":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if draw_gameover().collidepoint(event.pos): mode = "MENU"

            # --- OYUN HAREKETLERİ ---
            elif mode in ["SINGLE", "MULTI"]:
                if event.type == pygame.KEYDOWN:
                    # P1
                    nr, nc = p1_pos[0], p1_pos[1]; moved = False
                    if event.key == pygame.K_UP: nr-=1; moved=True
                    elif event.key == pygame.K_DOWN: nr+=1; moved=True
                    elif event.key == pygame.K_LEFT: nc-=1; moved=True
                    elif event.key == pygame.K_RIGHT: nc+=1; moved=True
                    
                    if moved and 0<=nr<ROWS and 0<=nc<COLS and current_map[nr][nc]!=1:
                        p1_pos=[nr,nc]; moves_p1+=1
                        if current_map[nr][nc]==2: winner_msg=f"{p1_name} KAZANDI!"; mode="GAMEOVER"

                    # P2
                    if mode == "MULTI":
                        nr2, nc2 = p2_pos[0], p2_pos[1]; moved2 = False
                        if event.key == pygame.K_w: nr2-=1; moved2=True
                        elif event.key == pygame.K_s: nr2+=1; moved2=True
                        elif event.key == pygame.K_a: nc2-=1; moved2=True
                        elif event.key == pygame.K_d: nc2+=1; moved2=True
                        if moved2 and 0<=nr2<ROWS and 0<=nc2<COLS and current_map[nr2][nc2]!=1:
                            p2_pos=[nr2,nc2]; moves_p2+=1
                            if current_map[nr2][nc2]==2: winner_msg=f"{p2_name} KAZANDI!"; mode="GAMEOVER"

        # Auto Oynatma
        if mode == "AUTO":
            if moves_p1 < len(auto_path):
                time.sleep(0.15)
                p1_pos = list(auto_path[moves_p1])
                moves_p1 += 1
            else: winner_msg="BİLGİSAYAR TAMAMLADI"; mode="GAMEOVER"

        # Çizim Çağrıları
        if mode == "MENU": draw_menu()
        elif mode == "INPUT_NAMES": draw_input_names()
        elif mode == "GAMEOVER": draw_game(); draw_gameover()
        else: draw_game()

        pygame.display.flip()
        clock.tick(30)

except Exception as e:
    print(f"Hata: {e}")
    pygame.quit()