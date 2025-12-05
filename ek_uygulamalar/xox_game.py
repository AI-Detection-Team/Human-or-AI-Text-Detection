import tkinter as tk
from tkinter import messagebox
import socket
import threading
import random

# --- AYARLAR ---
COLOR_BG = "#2D1E3C"
COLOR_BTN = "#A064DC"
COLOR_TEXT = "#FFFADE"
COLOR_X = "#5096FF"
COLOR_O = "#FF5050"
COLOR_WIN = "#2ECC71"

# --- DEĞİŞKENLER ---
mode = "MENU" # LOCAL, AI, NET_SERVER, NET_CLIENT
turn = 'X'
board = [""] * 9
buttons = []
game_over = False
sock = None
my_net_role = None # Network'te ben kimim?
btn_retry = None

# Pencere
window = tk.Tk()
window.title("XOX - Pro Network")
window.geometry("500x650")
window.configure(bg=COLOR_BG)

# --- ORTAK MANTIK ---

def check_winner(silent=False):
    global game_over
    wins = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    
    for a,b,c in wins:
        if board[a] == board[b] == board[c] != "":
            if not silent:
                # Kazananı boya
                buttons[a].config(bg=COLOR_WIN); buttons[b].config(bg=COLOR_WIN); buttons[c].config(bg=COLOR_WIN)
                game_over = True
                winner = board[a]
                
                if mode in ["NET_SERVER", "NET_CLIENT"]:
                    if winner == my_net_role: messagebox.showinfo("Sonuç", "🎉 KAZANDINIZ!")
                    else: messagebox.showinfo("Sonuç", "💀 KAYBETTİNİZ!")
                else:
                    messagebox.showinfo("Sonuç", f"KAZANAN: {winner}")
                
                show_retry_button()
            return board[a]
            
    if "" not in board:
        if not silent:
            game_over = True
            messagebox.showinfo("Sonuç", "BERABERE!")
            show_retry_button()
        return "DRAW"
    return None

def show_retry_button():
    if btn_retry:
        btn_retry.pack(pady=10)

def hide_retry_button():
    if btn_retry:
        btn_retry.pack_forget()

def reset_board_logic():
    global board, game_over, turn
    board = [""] * 9
    game_over = False
    turn = 'X'
    
    for btn in buttons:
        btn.config(text="", bg=COLOR_BTN, state="normal")
    
    hide_retry_button()
    
    # Network modunda sıra güncellemesi
    if mode in ["NET_SERVER", "NET_CLIENT"]:
        update_network_status()
    else:
        lbl_status.config(text=f"Sıra: {turn}", fg=COLOR_X)
        if mode == "AI" and turn == 'O': window.after(500, ai_move)

# --- NETWORK İŞLEMLERİ ---

def click_network(idx):
    if board[idx] != "" or game_over: return
    if turn != my_net_role: return # Sıra bende değil
    
    try:
        sock.send(str(idx).encode()) # Hamleyi yolla
        apply_move(idx, my_net_role)
    except:
        messagebox.showerror("Hata", "Bağlantı Koptu!")
        show_main_menu()

def apply_move(idx, player):
    global turn
    board[idx] = player
    buttons[idx].config(text=player, fg=COLOR_X if player=='X' else COLOR_O)
    
    if check_winner(): return
    
    turn = 'O' if player == 'X' else 'X'
    update_network_status()

def update_network_status():
    if turn == my_net_role:
        lbl_status.config(text="SIRA SENDE!", fg=COLOR_WIN)
    else:
        lbl_status.config(text="Rakip Düşünüyor...", fg="gray")

def send_reset_signal():
    try:
        sock.send("RESET".encode())
        reset_board_logic()
    except:
        pass

def network_listener():
    while True:
        try:
            data = sock.recv(1024).decode()
            if not data: break
            
            if data == "RESET":
                # Ana thread'de çalıştır
                window.after(0, reset_board_logic)
            else:
                idx = int(data)
                opponent = 'O' if my_net_role=='X' else 'X'
                window.after(0, lambda: apply_move(idx, opponent))
        except:
            break

def start_server():
    global sock, my_net_role, turn, mode
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('0.0.0.0', 65432))
        s.listen(1)
        lbl_net_status.config(text="Sunucu Açıldı! Rakip Bekleniyor...", fg="orange")
        window.update()
        
        sock, addr = s.accept()
        s.close() # Dinleyiciyi kapat, aktif soketi tut
        
        my_net_role = 'X'
        turn = 'X'
        mode = "NET_SERVER"
        
        setup_game_ui()
        threading.Thread(target=network_listener, daemon=True).start()
    except Exception as e:
        messagebox.showerror("Hata", str(e))
        show_main_menu()

def connect_server():
    global sock, my_net_role, turn, mode
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 65432))
        
        my_net_role = 'O'
        turn = 'X'
        mode = "NET_CLIENT"
        
        setup_game_ui()
        threading.Thread(target=network_listener, daemon=True).start()
    except:
        messagebox.showerror("Hata", "Sunucu Bulunamadı!\nÖnce diğer terminalde 'Sunucu Kur' diyin.")

# --- YEREL / AI İŞLEMLERİ ---

def click_local(idx):
    global turn
    if board[idx] != "" or game_over: return
    
    board[idx] = turn
    buttons[idx].config(text=turn, fg=COLOR_X if turn=='X' else COLOR_O)
    
    if check_winner(): return
    
    turn = 'O' if turn == 'X' else 'X'
    lbl_status.config(text=f"Sıra: {turn}", fg=COLOR_X if turn=='X' else COLOR_O)
    
    if mode == "AI" and turn == 'O' and not game_over:
        window.after(500, ai_move)

def ai_move():
    if game_over: return
    empty = [i for i, x in enumerate(board) if x == ""]
    if empty: click_local(random.choice(empty))

# --- ARAYÜZ YÖNETİMİ ---

def clear_ui():
    for widget in window.winfo_children(): widget.destroy()

def show_main_menu():
    global mode
    mode = "MENU"
    try: sock.close()
    except: pass
    
    clear_ui()
    
    tk.Label(window, text="XOX ULTIMATE", font=("Verdana", 32, "bold"), bg=COLOR_BG, fg=COLOR_TEXT).pack(pady=50)
    
    btn_style = {"font":("Arial", 14), "bg":COLOR_BTN, "fg":"white", "width":22, "height":2}
    
    tk.Button(window, text="🏠 Aynı Bilgisayarda", **btn_style, command=lambda: start_local("LOCAL")).pack(pady=10)
    tk.Button(window, text="🤖 Bilgisayara Karşı", **btn_style, command=lambda: start_local("AI")).pack(pady=10)
    
    tk.Label(window, text="--- veya ---", bg=COLOR_BG, fg="gray").pack(pady=5)
    tk.Button(window, text="🌐 Network Oyunu", **btn_style, command=show_network_menu).pack(pady=5)

def show_network_menu():
    clear_ui()
    tk.Label(window, text="NETWORK LOBİSİ", font=("Verdana", 24, "bold"), bg=COLOR_BG, fg=COLOR_TEXT).pack(pady=30)
    
    global lbl_net_status
    lbl_net_status = tk.Label(window, text="Lütfen bir rol seçin:", font=("Arial", 12), bg=COLOR_BG, fg="gray")
    lbl_net_status.pack(pady=10)
    
    btn_style = {"font":("Arial", 14), "bg":COLOR_BTN, "fg":"white", "width":20, "height":2}
    
    tk.Button(window, text="📡 Sunucu Kur (Host)", **btn_style, 
              command=lambda: threading.Thread(target=start_server, daemon=True).start()).pack(pady=10)
    
    tk.Button(window, text="🔗 Bağlan (Client)", **btn_style, 
              command=lambda: threading.Thread(target=connect_server, daemon=True).start()).pack(pady=10)
    
    tk.Button(window, text="🔙 Geri", bg="#E74C3C", fg="white", width=10, command=show_main_menu).pack(pady=30)

def start_local(selected_mode):
    global mode
    mode = selected_mode
    setup_game_ui()

def setup_game_ui():
    global buttons, lbl_status, board, btn_retry
    board = [""] * 9
    clear_ui()
    
    # Başlık
    title = "XOX ONLINE" if "NET" in mode else "XOX OYUNU"
    tk.Label(window, text=title, font=("Arial", 20, "bold"), bg=COLOR_BG, fg=COLOR_TEXT).pack(pady=15)
    
    lbl_status = tk.Label(window, text="Oyun Başlıyor...", font=("Arial", 16), bg=COLOR_BG, fg=COLOR_TEXT)
    lbl_status.pack(pady=5)
    
    frame = tk.Frame(window, bg=COLOR_BG)
    frame.pack(pady=10)
    
    buttons = []
    for i in range(9):
        # Buton fonksiyonu moda göre değişir
        cmd = lambda idx=i: click_network(idx) if "NET" in mode else click_local(idx)
        
        btn = tk.Button(frame, text="", font=("Arial", 24, "bold"), width=4, height=2,
                        bg="#3E2A52", fg="white", command=cmd)
        btn.grid(row=i//3, column=i%3, padx=5, pady=5)
        buttons.append(btn)
        
    # Retry butonu (Başlangıçta gizli)
    retry_cmd = send_reset_signal if "NET" in mode else reset_board_logic
    btn_retry = tk.Button(window, text="TEKRAR OYNA 🔄", bg="#E67E22", fg="white", 
                          font=("Arial", 12, "bold"), command=retry_cmd)
    
    tk.Button(window, text="MENÜYE DÖN", bg="#E74C3C", fg="white", command=show_main_menu).pack(side="bottom", pady=20)
    
    # Başlat
    reset_board_logic()

# --- BAŞLAT ---
show_main_menu()
window.mainloop()