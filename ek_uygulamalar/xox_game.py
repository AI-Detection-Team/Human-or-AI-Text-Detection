import tkinter as tk
from tkinter import messagebox
import socket
import threading
import random

# --- AYARLAR ---
COLOR_BG = "#2D1E3C"       # Arka plan (Koyu Mor)
COLOR_BTN = "#5D4C75"      # Buton Rengi (Daha belirgin mor)
COLOR_BTN_HOVER = "#7D6C95" # Üzerine gelinceki renk
COLOR_TEXT = "#FFFADE"     # Genel Yazı (Krem)
COLOR_X = "#5096FF"        # X Rengi (Mavi)
COLOR_O = "#FF5050"        # O Rengi (Kırmızı)
COLOR_WIN = "#2ECC71"      # Kazanma Rengi (Yeşil)
COLOR_TIMER = "#FFD700"    # Sayaç Rengi (Altın Sarısı)

# --- DEĞİŞKENLER ---
mode = "MENU" 
turn = 'X'
board = [""] * 9
buttons = [] # Artık Label listesi olacak
game_over = False
sock = None
my_net_role = None 
btn_retry = None

# Sayaç Değişkenleri
timer_id = None
time_left = 10

# Pencere
window = tk.Tk()
window.title("XOX - Pro Network (Mac Uyumlu)")
window.geometry("500x700")
window.configure(bg=COLOR_BG)

# --- MAC İÇİN ÖZEL BUTON YAPISI ---
# Mac'te standart butonlar renklenmediği için, Label kullanarak kendi butonumuzu yapıyoruz.
class CustomButton(tk.Label):
    def __init__(self, parent, text, command, width=20, height=2, font=("Arial", 14), bg=COLOR_BTN, fg=COLOR_TEXT):
        super().__init__(parent, text=text, font=font, bg=bg, fg=fg, width=width, height=height, cursor="hand2")
        self.command = command
        self.default_bg = bg
        self.hover_bg = COLOR_BTN_HOVER
        
        # Tıklama ve Hover olaylarını bağla
        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        
    def on_click(self, event):
        if self['state'] != 'disabled':
            self.command()
            
    def on_enter(self, event):
        if self['state'] != 'disabled':
            self.config(bg=self.hover_bg)
            
    def on_leave(self, event):
        if self['state'] != 'disabled':
            self.config(bg=self.default_bg)

# --- SAYAÇ MANTIĞI ---

def start_timer():
    global timer_id, time_left
    if timer_id: window.after_cancel(timer_id)
    if game_over: return
    
    if mode in ["NET_SERVER", "NET_CLIENT"] and turn != my_net_role:
        lbl_timer.config(text="Rakibin Süresi...", fg="gray")
        return
    if mode == "AI" and turn == 'O':
        lbl_timer.config(text="Yapay Zeka Düşünüyor...", fg="gray")
        return

    time_left = 10
    update_timer_display()
    countdown()

def countdown():
    global time_left, timer_id
    if time_left > 0:
        time_left -= 1
        update_timer_display()
        timer_id = window.after(1000, countdown)
    else:
        handle_timeout()

def update_timer_display():
    color = COLOR_TIMER if time_left > 3 else "#FF0000"
    lbl_timer.config(text=f"⏳ Kalan Süre: {time_left} sn", fg=color)

def handle_timeout():
    if mode in ["NET_SERVER", "NET_CLIENT"]:
        try: sock.send("TIMEOUT".encode()); switch_turn_no_move()
        except: pass
    else:
        switch_turn_no_move()

def switch_turn_no_move():
    global turn
    if game_over: return
    turn = 'O' if turn == 'X' else 'X'
    if mode in ["NET_SERVER", "NET_CLIENT"]: update_network_status()
    else:
        lbl_status.config(text=f"Süre Doldu! Sıra: {turn}", fg="orange")
        if mode == "AI" and turn == 'O': window.after(500, ai_move)
    start_timer()

# --- ORTAK MANTIK ---

def check_winner(silent=False):
    global game_over
    wins = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    
    for a,b,c in wins:
        if board[a] == board[b] == board[c] != "":
            if not silent:
                if timer_id: window.after_cancel(timer_id)
                # Label olduğu için config(bg=...) çalışır
                buttons[a].config(bg=COLOR_WIN); buttons[b].config(bg=COLOR_WIN); buttons[c].config(bg=COLOR_WIN)
                game_over = True
                winner = board[a]
                lbl_timer.config(text="OYUN BİTTİ", fg=COLOR_WIN)
                
                msg = "🎉 KAZANDINIZ!" if (mode in ["NET_SERVER", "NET_CLIENT"] and winner == my_net_role) else f"KAZANAN: {winner}"
                if mode in ["NET_SERVER", "NET_CLIENT"] and winner != my_net_role: msg = "💀 KAYBETTİNİZ!"
                
                messagebox.showinfo("Sonuç", msg)
                show_retry_button()
            return board[a]
            
    if "" not in board:
        if not silent:
            if timer_id: window.after_cancel(timer_id)
            game_over = True
            lbl_timer.config(text="OYUN BİTTİ", fg=COLOR_WIN)
            messagebox.showinfo("Sonuç", "BERABERE!")
            show_retry_button()
        return "DRAW"
    return None

def show_retry_button():
    if btn_retry: btn_retry.pack(pady=10)

def hide_retry_button():
    if btn_retry: btn_retry.pack_forget()

def reset_board_logic():
    global board, game_over, turn
    board = [""] * 9
    game_over = False
    turn = 'X'
    
    for btn in buttons:
        btn.config(text="", bg=COLOR_BTN, state="normal")
    
    hide_retry_button()
    
    if mode in ["NET_SERVER", "NET_CLIENT"]: update_network_status()
    else:
        lbl_status.config(text=f"Sıra: {turn}", fg=COLOR_X)
        start_timer()
        if mode == "AI" and turn == 'O': window.after(500, ai_move)

# --- NETWORK İŞLEMLERİ ---

def click_network(idx):
    if board[idx] != "" or game_over: return
    if turn != my_net_role: return 
    try: sock.send(str(idx).encode()); apply_move(idx, my_net_role)
    except: messagebox.showerror("Hata", "Bağlantı Koptu!"); show_main_menu()

def apply_move(idx, player):
    global turn
    board[idx] = player
    buttons[idx].config(text=player, fg=COLOR_X if player=='X' else COLOR_O)
    if check_winner(): return
    turn = 'O' if player == 'X' else 'X'
    update_network_status()
    start_timer()

def update_network_status():
    if turn == my_net_role:
        lbl_status.config(text="SIRA SENDE!", fg=COLOR_WIN); start_timer()
    else:
        lbl_status.config(text="Rakip Düşünüyor...", fg="gray"); start_timer()

def send_reset_signal():
    try: sock.send("RESET".encode()); reset_board_logic()
    except: pass

def network_listener():
    while True:
        try:
            data = sock.recv(1024).decode()
            if not data: break
            if data == "RESET": window.after(0, reset_board_logic)
            elif data == "TIMEOUT": window.after(0, switch_turn_no_move)
            else:
                idx = int(data); opponent = 'O' if my_net_role=='X' else 'X'
                window.after(0, lambda: apply_move(idx, opponent))
        except: break

def start_server():
    global sock, my_net_role, turn, mode
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('0.0.0.0', 65432)); s.listen(1)
        lbl_net_status.config(text="Sunucu Açıldı! Rakip Bekleniyor...", fg="orange")
        window.update()
        sock, addr = s.accept(); s.close()
        my_net_role = 'X'; turn = 'X'; mode = "NET_SERVER"
        setup_game_ui()
        threading.Thread(target=network_listener, daemon=True).start()
    except Exception as e: messagebox.showerror("Hata", str(e)); show_main_menu()

def connect_server():
    global sock, my_net_role, turn, mode
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 65432))
        my_net_role = 'O'; turn = 'X'; mode = "NET_CLIENT"
        setup_game_ui()
        threading.Thread(target=network_listener, daemon=True).start()
    except: messagebox.showerror("Hata", "Sunucu Bulunamadı!"); show_main_menu()

# --- YEREL / AI İŞLEMLERİ ---

def click_local(idx):
    global turn
    if board[idx] != "" or game_over: return
    board[idx] = turn
    buttons[idx].config(text=turn, fg=COLOR_X if turn=='X' else COLOR_O)
    if check_winner(): return
    turn = 'O' if turn == 'X' else 'X'
    lbl_status.config(text=f"Sıra: {turn}", fg=COLOR_X if turn=='X' else COLOR_O)
    start_timer()
    if mode == "AI" and turn == 'O' and not game_over: window.after(500, ai_move)

def ai_move():
    if game_over: return
    empty = [i for i, x in enumerate(board) if x == ""]
    if empty: click_local(random.choice(empty))

# --- ARAYÜZ YÖNETİMİ ---

def clear_ui():
    if timer_id: window.after_cancel(timer_id)
    for widget in window.winfo_children(): widget.destroy()

def show_main_menu():
    global mode
    mode = "MENU"
    try: sock.close()
    except: pass
    clear_ui()
    
    tk.Label(window, text="XOX PFY TEAM", font=("Verdana", 32, "bold"), bg=COLOR_BG, fg=COLOR_TEXT).pack(pady=50)
    
    # CustomButton Sınıfımızı kullanıyoruz (tk.Button yerine)
    CustomButton(window, text="🏠 Aynı Bilgisayarda", command=lambda: start_local("LOCAL")).pack(pady=10)
    CustomButton(window, text="🤖 Bilgisayara Karşı", command=lambda: start_local("AI")).pack(pady=10)
    
    tk.Label(window, text="--- veya ---", bg=COLOR_BG, fg="gray").pack(pady=5)
    CustomButton(window, text="🌐 Network Oyunu", command=show_network_menu).pack(pady=5)

def show_network_menu():
    clear_ui()
    tk.Label(window, text="NETWORK LOBİSİ", font=("Verdana", 24, "bold"), bg=COLOR_BG, fg=COLOR_TEXT).pack(pady=30)
    global lbl_net_status
    lbl_net_status = tk.Label(window, text="Lütfen bir rol seçin:", font=("Arial", 12), bg=COLOR_BG, fg="gray")
    lbl_net_status.pack(pady=10)
    
    CustomButton(window, text="📡 Sunucu Kur (Host)", command=lambda: threading.Thread(target=start_server, daemon=True).start()).pack(pady=10)
    CustomButton(window, text="🔗 Bağlan (Client)", command=lambda: threading.Thread(target=connect_server, daemon=True).start()).pack(pady=10)
    
    # Geri butonu biraz farklı renk
    CustomButton(window, text="🔙 Geri", bg="#E74C3C", command=show_main_menu, width=10).pack(pady=30)

def start_local(selected_mode):
    global mode
    mode = selected_mode
    setup_game_ui()

def setup_game_ui():
    global buttons, lbl_status, board, btn_retry, lbl_timer
    board = [""] * 9
    clear_ui()
    
    title = "XOX ONLINE" if "NET" in mode else "XOX OYUNU"
    tk.Label(window, text=title, font=("Arial", 20, "bold"), bg=COLOR_BG, fg=COLOR_TEXT).pack(pady=10)
    
    lbl_timer = tk.Label(window, text="⏳ Kalan Süre: 10 sn", font=("Arial", 14, "bold"), bg=COLOR_BG, fg=COLOR_TIMER)
    lbl_timer.pack(pady=5)

    lbl_status = tk.Label(window, text="Oyun Başlıyor...", font=("Arial", 16), bg=COLOR_BG, fg=COLOR_TEXT)
    lbl_status.pack(pady=5)
    
    frame = tk.Frame(window, bg=COLOR_BG)
    frame.pack(pady=10)
    
    buttons = []
    for i in range(9):
        cmd = lambda idx=i: click_network(idx) if "NET" in mode else click_local(idx)
        
        # OYUN BUTONLARINI DA CUSTOM YAPIYORUZ
        # width ve height değerleri Label için karakter sayısıdır, piksel değil.
        btn = CustomButton(frame, text="", width=6, height=3, font=("Arial", 24, "bold"), 
                           bg=COLOR_BTN, fg=COLOR_TEXT, command=cmd)
        btn.grid(row=i//3, column=i%3, padx=5, pady=5)
        buttons.append(btn)
        
    retry_cmd = send_reset_signal if "NET" in mode else reset_board_logic
    btn_retry = CustomButton(window, text="TEKRAR OYNA 🔄", bg="#E67E22", fg="white", font=("Arial", 12, "bold"), command=retry_cmd)
    
    CustomButton(window, text="MENÜYE DÖN", bg="#E74C3C", fg="white", command=show_main_menu).pack(side="bottom", pady=20)
    
    reset_board_logic()

# --- BAŞLAT ---
show_main_menu()