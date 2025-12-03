import tkinter as tk
from tkinter import messagebox, simpledialog
import socket
import threading
import time
import random
import sys

# --- AYARLAR ---
COLOR_BG = "#2D1E3C"
COLOR_BTN = "#A064DC"
COLOR_BTN_HOVER = "#B482E6"
COLOR_TEXT = "#FFFADE"
COLOR_X = "#5096FF"
COLOR_O = "#FF5050"
COLOR_WIN = "#2ECC71"

# --- OYUN DEĞİŞKENLERİ ---
mode = "MENU" 
turn = 'X'
board = [""] * 9
buttons = []
game_over = False
sock = None
timer_id = None
time_left = 10
my_network_symbol = 'X'
is_server = False

# --- PENCERE ---
window = tk.Tk()
window.title("XOX - Ultimate Pro")
window.geometry("450x680")
window.configure(bg=COLOR_BG)

# --- FONKSİYONLAR ---

def stop_timer():
    global timer_id
    if timer_id:
        window.after_cancel(timer_id)
        timer_id = None

def start_timer():
    global time_left, timer_id
    stop_timer() # Önce varsa durdur
    time_left = 10
    
    # Network modunda sadece sıra bendeyse süre işlesin
    if mode in ["NET_SERVER", "NET_CLIENT"]:
        if turn == my_network_symbol:
            countdown()
        else:
            lbl_timer.config(text="⏳ Rakip Bekleniyor...", fg="gray")
    else:
        # Local ve AI modunda her zaman işlesin
        countdown()

def countdown():
    global time_left, timer_id, game_over, turn
    
    if game_over or mode == "MENU": return
    
    # Ekranı Güncelle
    color = "white"
    if time_left <= 3: color = "red"
    lbl_timer.config(text=f"⏳ Süre: {time_left}", fg=color)
    
    if time_left == 0:
        # SÜRE DOLDU!
        handle_timeout()
        return

    time_left -= 1
    timer_id = window.after(1000, countdown)

def handle_timeout():
    global turn
    stop_timer()
    
    if mode in ["NET_SERVER", "NET_CLIENT"]:
        # Eğer sıra bendeyken süre bittiyse KAYBETTİM
        if turn == my_network_symbol:
            try: sock.send("WIN".encode()) # Rakibe "Kazandın" de
            except: pass
            messagebox.showerror("Süre Doldu", "Süreniz bitti! Kaybettiniz.")
            show_main_menu()
    
    else:
        # Local modda sıra diğerine geçer ve rastgele oynar
        lbl_status.config(text="Süre Doldu! Rastgele Oynandı", fg="orange")
        empty = [i for i, x in enumerate(board) if x == ""]
        if empty:
            make_move(random.choice(empty), turn)

def reset_board():
    global board, game_over, turn
    board = [""] * 9
    game_over = False
    turn = 'X' # Her zaman X başlar
    
    for btn in buttons:
        btn.config(text="", bg=COLOR_BTN, state="normal")
    
    lbl_status.config(text=f"Sıra: {turn}", fg=COLOR_X)
    
    # Network ise butonları kilitle/aç
    if mode in ["NET_SERVER", "NET_CLIENT"]:
        if my_network_symbol == 'X':
            enable_buttons()
            lbl_status.config(text="Sıra Sende (X)", fg=COLOR_X)
            start_timer()
        else:
            disable_buttons()
            lbl_status.config(text="Rakip Başlıyor (X)", fg="gray")
            lbl_timer.config(text="⏳ Rakip...", fg="gray")
    else:
        start_timer()

def check_winner(silent=False):
    global game_over
    wins = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    
    for a,b,c in wins:
        if board[a] == board[b] == board[c] != "":
            if not silent:
                buttons[a].config(bg=COLOR_WIN); buttons[b].config(bg=COLOR_WIN); buttons[c].config(bg=COLOR_WIN)
                game_over = True
                stop_timer()
                winner = board[a]
                
                # Network Mesajları
                if mode in ["NET_SERVER", "NET_CLIENT"]:
                    msg = "KAZANDINIZ! 🎉" if winner == my_network_symbol else "KAYBETTİNİZ 💀"
                    messagebox.showinfo("Oyun Bitti", msg)
                    show_main_menu() # Oyundan çık
                else:
                    messagebox.showinfo("Oyun Bitti", f"KAZANAN: {winner}")
                    show_main_menu()
            return board[a]
            
    if "" not in board:
        if not silent:
            game_over = True
            stop_timer()
            messagebox.showinfo("Oyun Bitti", "BERABERE!")
            show_main_menu()
        return "DRAW"
    return None

def handle_click(idx):
    global turn
    if board[idx] != "" or game_over: return
    
    # NETWORK MODU KONTROLÜ
    if mode in ["NET_SERVER", "NET_CLIENT"]:
        if turn != my_network_symbol: return 
        
        # Hamleyi Gönder
        try:
            sock.send(str(idx).encode())
            make_move(idx, my_network_symbol)
        except:
            messagebox.showerror("Hata", "Bağlantı Koptu!")
            show_main_menu()
        return

    # LOCAL ve AI MODLARI
    make_move(idx, turn)
    
    if mode == "AI" and not game_over and turn == 'O':
        disable_buttons() # AI düşünürken basama
        window.after(500, ai_move)

def make_move(idx, player):
    global turn
    board[idx] = player
    buttons[idx].config(text=player, fg=COLOR_X if player=='X' else COLOR_O)
    
    if check_winner(): return
    
    turn = 'O' if player == 'X' else 'X'
    lbl_status.config(text=f"Sıra: {turn}", fg=COLOR_X if turn=='X' else COLOR_O)
    
    # Network Modunda Buton Yönetimi
    if mode in ["NET_SERVER", "NET_CLIENT"]:
        if turn == my_network_symbol:
            enable_buttons()
            lbl_status.config(text="SIRA SENDE!", fg=COLOR_WIN)
            start_timer()
        else:
            disable_buttons()
            lbl_status.config(text="Rakip Düşünüyor...", fg="gray")
            start_timer() # Timer'ı "Bekleniyor" moduna al
            
    elif mode == "AI" and turn == 'X':
        enable_buttons()
        start_timer()
    elif mode == "LOCAL":
        start_timer()

def ai_move():
    if game_over: return
    empty_spots = [i for i, x in enumerate(board) if x == ""]
    if empty_spots:
        handle_click(random.choice(empty_spots))

def disable_buttons():
    for btn in buttons: btn.config(state="disabled")

def enable_buttons():
    for i, btn in enumerate(buttons):
        if board[i] == "": btn.config(state="normal")

# --- NETWORK (ARKA PLAN) ---
def start_hosting():
    global sock, is_server, my_network_symbol, mode
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('0.0.0.0', 65432))
        sock.listen(1)
        window.after(0, lambda: lbl_info.config(text="Sunucu Açıldı! Rakip Bekleniyor..."))
        
        conn, addr = sock.accept()
        sock.close() # Dinleyiciyi kapat, bağlantıyı tut
        sock = conn  # Aktif bağlantı
        
        is_server = True
        my_network_symbol = 'X'
        mode = "NET_SERVER"
        
        window.after(0, start_game_ui)
        threading.Thread(target=receive_network_move, daemon=True).start()
    except Exception as e:
        window.after(0, lambda: messagebox.showerror("Hata", f"Sunucu Hatası: {e}"))
        window.after(0, show_main_menu)

def connect_to_host():
    global sock, is_server, my_network_symbol, mode
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 65432))
        is_server = False
        my_network_symbol = 'O'
        mode = "NET_CLIENT"
        
        window.after(0, start_game_ui)
        threading.Thread(target=receive_network_move, daemon=True).start()
    except:
        window.after(0, lambda: messagebox.showerror("Hata", "Sunucu Bulunamadı!\nÖnce diğer pencereden 'Sunucu Kur' yapın."))
        window.after(0, show_network_menu)

def receive_network_move():
    while True:
        try:
            data = sock.recv(1024).decode()
            if not data: break
            
            if data == "WIN": # Rakip "Ben kazandım" dedi (Yani sen kaybettin veya süren bitti sanıp yolladı)
                # Buradaki mantık: Rakip süresi bitince bize WIN yollar
                window.after(0, lambda: messagebox.showinfo("Sonuç", "🎉 Rakibin Süresi Doldu! KAZANDIN!"))
                window.after(0, show_main_menu)
                break
            
            elif data == "LOSE": # Rakip "Ben kaybettim" dedi
                window.after(0, lambda: messagebox.showinfo("Sonuç", "🎉 Rakip Pes Etti! KAZANDIN!"))
                window.after(0, show_main_menu)
                break
            
            elif data == "DRAW":
                window.after(0, lambda: messagebox.showinfo("Sonuç", "Berabere!"))
                window.after(0, show_main_menu)
                break
                
            else:
                idx = int(data)
                opponent = 'O' if my_network_symbol=='X' else 'X'
                window.after(0, lambda: make_move(idx, opponent))
        except:
            break

# --- MENÜLER ---
def clear_window():
    for widget in window.winfo_children():
        widget.destroy()

def show_main_menu():
    global mode
    mode = "MENU"
    stop_timer()
    try: sock.close()
    except: pass
    
    clear_window()
    tk.Label(window, text="XOX ULTIMATE", font=("Verdana", 32, "bold"), bg=COLOR_BG, fg=COLOR_TEXT).pack(pady=50)
    
    btn_style = {"font":("Arial", 14, "bold"), "bg":COLOR_BTN, "fg":"white", "width":22, "height":2}
    
    tk.Button(window, text="🏠 Aynı Bilgisayarda", **btn_style, command=lambda: [set_mode("LOCAL"), start_game_ui()]).pack(pady=10)
    tk.Button(window, text="🤖 Bilgisayara Karşı", **btn_style, command=lambda: [set_mode("AI"), start_game_ui()]).pack(pady=10)
    tk.Button(window, text="🌐 Network Oyunu", **btn_style, command=show_network_menu).pack(pady=10)

def show_network_menu():
    clear_window()
    tk.Label(window, text="NETWORK MODU", font=("Verdana", 24, "bold"), bg=COLOR_BG, fg=COLOR_TEXT).pack(pady=40)
    
    global lbl_info
    lbl_info = tk.Label(window, text="Bir rol seçin:", font=("Arial", 12), bg=COLOR_BG, fg="gray")
    lbl_info.pack(pady=10)
    
    btn_style = {"font":("Arial", 14), "bg":COLOR_BTN, "fg":"white", "width":20, "height":2}
    
    tk.Button(window, text="📡 Sunucu Kur (Host)", **btn_style, 
              command=lambda: threading.Thread(target=start_hosting, daemon=True).start()).pack(pady=10)
    
    tk.Button(window, text="🔗 Bağlan (Connect)", **btn_style, 
              command=lambda: threading.Thread(target=connect_to_host, daemon=True).start()).pack(pady=10)
    
    tk.Button(window, text="🔙 Geri", font=("Arial", 12), bg="#E74C3C", fg="white", command=show_main_menu).pack(pady=30)

def set_mode(m):
    global mode
    mode = m

def start_game_ui():
    clear_window()
    global buttons, lbl_status, lbl_timer
    
    info_frame = tk.Frame(window, bg=COLOR_BG)
    info_frame.pack(pady=20)
    
    lbl_status = tk.Label(info_frame, text="Sıra: X", font=("Arial", 18, "bold"), bg=COLOR_BG, fg=COLOR_X)
    lbl_status.pack()
    
    lbl_timer = tk.Label(info_frame, text="⏳ 10", font=("Arial", 16), bg=COLOR_BG, fg="white")
    lbl_timer.pack()

    grid_frame = tk.Frame(window, bg=COLOR_BG)
    grid_frame.pack()
    
    buttons = []
    for i in range(9):
        btn = tk.Button(grid_frame, text="", font=("Arial", 28, "bold"), width=4, height=2,
                        bg="#3E2A52", fg="white",
                        command=lambda idx=i: handle_click(idx))
        btn.grid(row=i//3, column=i%3, padx=5, pady=5)
        buttons.append(btn)
    
    tk.Button(window, text="🛑 Çıkış / Menü", font=("Arial", 12), bg="#E74C3C", fg="white", 
              command=show_main_menu).pack(pady=20)
    
    reset_board()

# --- BAŞLAT ---
show_main_menu()
window.mainloop()