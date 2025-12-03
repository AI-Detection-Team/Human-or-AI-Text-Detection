import pygame
import sys
import os
import time
import random

# --- KRİTİK DÜZELTME: ÖZYİNELEME SINIRINI ARTIR ---
sys.setrecursionlimit(5000) # Labirent oluştururken çökmemesi için şart

# --- AYARLAR VE BAŞLATMA ---
try:
    pygame.init()
    print(" Pygame başlatıldı.")
except Exception as e:
    print(f" Pygame başlatılamadı: {e}")
    input("Kapatmak için Enter'a bas...")
    sys.exit()

TILE_SIZE = 50
COLS, ROWS = 15, 12
WIDTH, HEIGHT = COLS * TILE_SIZE, ROWS * TILE_SIZE + 80

try:
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Labirent - Human or AI Project")
    clock = pygame.time.Clock()
    
    # Fontları güvenli yükle
    font_title = pygame.font.SysFont("Arial", 36, bold=True)
    font_ui = pygame.font.SysFont("Arial", 18)
    font_input = pygame.font.SysFont("Arial", 24)
except Exception as e:
    print(f" Ekran veya Font hatası: {e}")

# --- RENK PALETİ ---
COLOR_BG = (45, 30, 60)        
COLOR_WALL = (240, 230, 200)   
COLOR_PATH = (60, 45, 80)      
COLOR_BUTTON = (160, 100, 220) 
COLOR_BUTTON_HOVER = (180, 130, 240)
COLOR_TEXT = (255, 250, 220)   
COLOR_P1_BACKUP = (100, 200, 255) # Mavi
COLOR_P2_BACKUP = (255, 100, 100) # Kırmızı
COLOR_CHEESE_BACKUP = (255, 200, 50) # Sarı

# --- RESİMLERİ YÜKLEME (DEBUG MODLU) ---
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
# Hem 'images' hem 'resimler' klasörüne bak
IMG_PATH = os.path.join(BASE_PATH, "images") 
if not os.path.exists(IMG_PATH): 
    IMG_PATH = os.path.join(BASE_PATH, "resimler")

print(f"📂 Resim Klasörü: {IMG_PATH}")

def load_and_scale(filename):
    full_path = os.path.join(IMG_PATH, filename)
    if os.path.exists(full_path):
        try:
            img = pygame.image.load(full_path)
            print(f" Yüklendi: {filename}")
            return pygame.transform.scale(img, (TILE_SIZE - 5, TILE_SIZE - 5))
        except Exception as e:
            print(f" Hata ({filename}): {e}")
            return None
    else:
        print(f" Bulunamadı: {filename} (Varsayılan renk kullanılacak)")
        return None

img_mouse1 = load_and_scale("mouse.png")
img_mouse2 = load_and_scale("mouse2.png")
img_cheese = load_and_scale("cheese.png")

# --- OYUN DEĞİŞKENLERİ ---
current_map = []
p1_pos = [1, 1]
p2_pos = [1, 1]
mode = "MENU" 
moves_p1 = 0
moves_p2 = 0
winner_msg = ""
auto_path = []
p1_name = "Oyuncu 1"
p2_name = "Oyuncu 2"
input_active_idx = 1
temp_name = ""

# --- RASTGELE LABİRENT OLUŞTURUCU ---
def generate_maze(rows, cols):
    maze = [[1 for _ in range(cols)] for _ in range(rows)]
    
    def carve_passages_from(cx, cy):
        directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < rows and 0 <= ny < cols and maze[nx][ny] == 1:
                maze[cx + dx//2][cy + dy//2] = 0
                maze[nx][ny] = 0
                carve_passages_from(nx, ny)

    maze[1][1] = 0
    carve_passages_from(1, 1)
    
    # Giriş ve Peynir
    maze[1][1] = 9 
    placed = False
    while not placed:
        r, c = random.randint(1, rows-2), random.randint(1, cols-2)
        if maze[r][c] == 0:
            maze[r][c] = 2
            placed = True
    return maze

# --- OYUNU BAŞLATMA ---
def start_game(selected_mode):
    global current_map, p1_pos, p2_pos, moves_p1, moves_p2, mode, auto_path, p1_name
    
    print(f"🎲 Oyun Başlatılıyor: {selected_mode}")
    current_map = generate_maze(ROWS, COLS)
    p1_pos = [1, 1]
    p2_pos = [1, 1]
    moves_p1 = 0
    moves_p2 = 0
    mode = selected_mode
    
    if mode == "SINGLE" and p1_name == "Oyuncu 1": p1_name = "Oyuncu"
    if mode == "AUTO": 
        auto_path = get_auto_path()
        p1_name = "Bilgisayar"

def get_auto_path():
    path = []
    visited = set()
    
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
                    path.pop()
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
    
    buttons = [
        (btn1, "TEK KİŞİLİK", "SINGLE"),
        (btn2, "İKİ KİŞİLİK (YARIŞ)", "INPUT_NAMES"), 
        (btn3, "BİLGİSAYAR ÇÖZSÜN", "AUTO")
    ]
    
    for btn, text, _ in buttons:
        color = COLOR_BUTTON_HOVER if btn.collidepoint(m_pos) else COLOR_BUTTON
        pygame.draw.rect(screen, color, btn, border_radius=10)
        txt = font_ui.render(text, True, COLOR_TEXT)
        screen.blit(txt, (btn.x + (btn.width - txt.get_width())//2, btn.y + 15))
        
    return btn1, btn2, btn3

def draw_input_names():
    screen.fill(COLOR_BG)
    
    header = "1. Oyuncu İsmi (Mavi)" if input_active_idx == 1 else "2. Oyuncu İsmi (Kırmızı)"
    title = font_title.render(header, True, COLOR_TEXT)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 150))
    
    # Giriş Kutusu
    input_box = pygame.Rect(WIDTH//2 - 150, 250, 300, 50)
    pygame.draw.rect(screen, COLOR_WALL, input_box, border_radius=10)
    
    # Yazılan İsim
    txt_surf = font_input.render(temp_name, True, COLOR_BG)
    screen.blit(txt_surf, (input_box.x + 10, input_box.y + 10))
    
    hint = font_ui.render("Yazmak için klavyeyi kullan, Enter ile onayla.", True, COLOR_BUTTON_HOVER)
    screen.blit(hint, (WIDTH//2 - hint.get_width()//2, 320))

def draw_gameover():
    s = pygame.Surface((WIDTH, HEIGHT))
    s.set_alpha(150)
    s.fill((0,0,0))
    screen.blit(s, (0,0))
    
    msg = font_title.render(winner_msg, True, (255, 215, 0))
    screen.blit(msg, (WIDTH//2 - msg.get_width()//2, 200))
    
    btn_retry = pygame.Rect(WIDTH//2 - 100, 300, 200, 60)
    m_pos = pygame.mouse.get_pos()
    color = COLOR_BUTTON_HOVER if btn_retry.collidepoint(m_pos) else COLOR_BUTTON
    
    pygame.draw.rect(screen, color, btn_retry, border_radius=10)
    txt = font_ui.render("TEKRAR OYNA", True, COLOR_TEXT)
    screen.blit(txt, (btn_retry.x + (btn_retry.width - txt.get_width())//2, btn_retry.y + 20))
    
    return btn_retry

def draw_game():
    screen.fill(COLOR_BG)
    
    for r in range(ROWS):
        for c in range(COLS):
            x, y = c * TILE_SIZE, r * TILE_SIZE
            tile = current_map[r][c]
            
            if tile == 1: 
                pygame.draw.rect(screen, COLOR_WALL, (x, y, TILE_SIZE, TILE_SIZE))
                pygame.draw.rect(screen, (200, 190, 160), (x, y, TILE_SIZE, TILE_SIZE), 2)
            elif tile == 2: 
                if img_cheese: screen.blit(img_cheese, (x + 2, y + 2))
                else: pygame.draw.circle(screen, COLOR_CHEESE_BACKUP, (x + 25, y + 25), 15)
            else: 
                pygame.draw.rect(screen, COLOR_PATH, (x+2, y+2, TILE_SIZE-4, TILE_SIZE-4))

    # P1
    x1, y1 = p1_pos[1] * TILE_SIZE, p1_pos[0] * TILE_SIZE
    if img_mouse1: screen.blit(img_mouse1, (x1 + 2, y1 + 2))
    else: pygame.draw.rect(screen, COLOR_P1_BACKUP, (x1 + 10, y1 + 10, 30, 30), border_radius=5)
    
    # P2
    if mode == "MULTI":
        x2, y2 = p2_pos[1] * TILE_SIZE, p2_pos[0] * TILE_SIZE
        if img_mouse2: screen.blit(img_mouse2, (x2 + 2, y2 + 2))
        else: pygame.draw.rect(screen, COLOR_P2_BACKUP, (x2 + 15, y2 + 15, 20, 20), border_radius=5)

    # Alt Panel
    pygame.draw.rect(screen, (30, 20, 40), (0, ROWS * TILE_SIZE, WIDTH, 80))
    pygame.draw.line(screen, COLOR_WALL, (0, ROWS*TILE_SIZE), (WIDTH, ROWS*TILE_SIZE), 3)
    
    if mode == "MULTI":
        t1 = font_ui.render(f"{p1_name}: {moves_p1} Hamle", True, COLOR_P1_BACKUP)
        t2 = font_ui.render(f"{p2_name}: {moves_p2} Hamle", True, COLOR_P2_BACKUP)
        screen.blit(t1, (20, ROWS * TILE_SIZE + 15))
        screen.blit(t2, (20, ROWS * TILE_SIZE + 45))
    else:
        t = font_ui.render(f"{p1_name} - Hamle: {moves_p1}", True, COLOR_TEXT)
        screen.blit(t, (20, ROWS * TILE_SIZE + 30))

# --- ANA DÖNGÜ (HATA YAKALAMALI) ---
try:
    current_map = generate_maze(ROWS, COLS)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            
            if mode == "MENU":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    b1, b2, b3 = draw_menu()
                    if b1.collidepoint(event.pos): start_game("SINGLE")
                    elif b2.collidepoint(event.pos): 
                        mode = "INPUT_NAMES"
                        input_active_idx = 1
                        temp_name = ""
                    elif b3.collidepoint(event.pos): start_game("AUTO")
            
            elif mode == "INPUT_NAMES":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if input_active_idx == 1:
                            p1_name = temp_name if temp_name else "Oyuncu 1"
                            input_active_idx = 2
                            temp_name = ""
                        else:
                            p2_name = temp_name if temp_name else "Oyuncu 2"
                            start_game("MULTI")
                    elif event.key == pygame.K_BACKSPACE:
                        temp_name = temp_name[:-1]
                    else:
                        if len(temp_name) < 12: 
                            temp_name += event.unicode

            elif mode == "GAMEOVER":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if draw_gameover().collidepoint(event.pos): mode = "MENU"

            elif mode in ["SINGLE", "MULTI"]:
                if event.type == pygame.KEYDOWN:
                    # P1
                    nr, nc = p1_pos[0], p1_pos[1]
                    moved = False
                    if event.key == pygame.K_UP: nr -= 1; moved=True
                    elif event.key == pygame.K_DOWN: nr += 1; moved=True
                    elif event.key == pygame.K_LEFT: nc -= 1; moved=True
                    elif event.key == pygame.K_RIGHT: nc += 1; moved=True
                    
                    if moved and 0<=nr<ROWS and 0<=nc<COLS and current_map[nr][nc] != 1:
                        p1_pos = [nr, nc]
                        moves_p1 += 1
                        if current_map[nr][nc] == 2:
                            winner_msg = f"TEBRİKLER {p1_name}!"
                            mode = "GAMEOVER"

                    # P2
                    if mode == "MULTI":
                        nr2, nc2 = p2_pos[0], p2_pos[1]
                        moved2 = False
                        if event.key == pygame.K_w: nr2 -= 1; moved2=True
                        elif event.key == pygame.K_s: nr2 += 1; moved2=True
                        elif event.key == pygame.K_a: nc2 -= 1; moved2=True
                        elif event.key == pygame.K_d: nc2 += 1; moved2=True
                        
                        if moved2 and 0<=nr2<ROWS and 0<=nc2<COLS and current_map[nr2][nc2] != 1:
                            p2_pos = [nr2, nc2]
                            moves_p2 += 1
                            if current_map[nr2][nc2] == 2:
                                winner_msg = f"TEBRİKLER {p2_name}!"
                                mode = "GAMEOVER"

        if mode == "AUTO":
            if moves_p1 < len(auto_path):
                time.sleep(0.15)
                p1_pos = list(auto_path[moves_p1])
                moves_p1 += 1
            else:
                winner_msg = "BİLGİSAYAR BULDU!"
                mode = "GAMEOVER"

        if mode == "MENU": draw_menu()
        elif mode == "INPUT_NAMES": draw_input_names()
        elif mode == "GAMEOVER": draw_game(); draw_gameover()
        else: draw_game()

        pygame.display.flip()
        clock.tick(30)

except Exception as e:
    print(f" Kritik Hata: {e}")
    pygame.quit()