import tkinter as tk
from tkinter import messagebox
import socket
import threading
import random

# --- AYARLAR ---
COLOR_BG = "#2D1E3C"       # Arka plan (Koyu Mor)
COLOR_BTN = "#4B3B60"      # Buton Rengi (Daha yumuşak mor)
COLOR_TEXT = "#FFFADE"     # Genel Yazı (Krem)
COLOR_X = "#5096FF"        # X Rengi (Mavi)
COLOR_O = "#FF5050"        # O Rengi (Kırmızı)
COLOR_WIN = "#2ECC71"      # Kazanma Rengi (Yeşil)
COLOR_TIMER = "#FFD700"    # Sayaç Rengi (Altın Sarısı)

# --- DEĞİŞKENLER ---
mode = "MENU" 
turn = 'X'
board = [""] * 9
buttons = []
game_over = False
sock = None
my_net_role = None 
btn_retry = None

# Sayaç Değişkenleri
timer_id = None
time_left = 10

# Pencere
window = tk.Tk()
window.title("XOX - Pro Network (Zamanlı)")
window.geometry("500x700")
window.configure(bg=COLOR_BG)

# --- SAYAÇ MANTIĞI (YENİ) ---

def start_timer():
    """Sayacı başlatır veya sıfırlar."""
    global timer_id, time_left
    
    # Eski sayacı durdur
    if timer_id:
        window.after_cancel(timer_id)
    
    if game_over: return
    
    # Network modunda sıra bende değilse sayaç çalıştırma
    if mode in ["NET_SERVER", "NET_CLIENT"] and turn != my_net_role:
        lbl_timer.config(text="Rakibin Süresi...", fg="gray")
        return

    # AI modunda sıra bilgisayardaysa sayaç çalıştırma (o hemen oynar)
    if mode == "AI" and turn == 'O':
        lbl_timer.config(text="Yapay Zeka Düşünüyor...", fg="gray")
        return

    time_left = 10
    update_timer_display()
    countdown()

def countdown():
    """Geri sayım fonksiyonu."""
    global time_left, timer_id
    
    if time_left > 0:
        time_left -= 1
        update_timer_display()
        timer_id = window.after(1000, countdown)
    else:
        # SÜRE BİTTİ!
        handle_timeout()

def update_timer_display():
    color = COLOR_TIMER if time_left > 3 else "#FF0000" # Son 3 saniye kırmızı olsun
    lbl_timer.config(text=f"⏳ Kalan Süre: {time_left} sn", fg=color)

def handle_timeout():
    """Süre dolunca ne olacağını yönetir."""
    global turn
    
    # Süre doldu sesi veya uyarısı (Konsola yazalım şimdilik)
    print("Süre doldu! Sıra geçiyor.")
    
    if mode in ["NET_SERVER", "NET_CLIENT"]:
        # Network'te karşıya "PAS GEÇTİM" mesajı yolla
        try:
            sock.send("TIMEOUT".encode())
            switch_turn_no_move()
        except:
            pass
    else:
        # Yerel oyunda direkt sırayı değiştir
        switch_turn_no_move()

def switch_turn_no_move():
    """Hamle yapmadan sırayı rakibe verir."""
    global turn
    if game_over: return
    
    # Sırayı değiştir
    turn = 'O' if turn == 'X' else 'X'
    
    # Durumu güncelle
    if mode in ["NET_SERVER", "NET_CLIENT"]:
        update_network_status()
    else:
        lbl_status.config(text=f"Süre Doldu! Sıra: {turn}", fg="orange")
        if mode == "AI" and turn == 'O': 
            window.after(500, ai_move)
            
    # Yeni kişi için sayacı başlat
    start_timer()

# --- ORTAK MANTIK ---

def check_winner(silent=False):
    global game_over
    wins = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    
    for a,b,c in wins:
        if board[a] == board[b] == board[c] != "":
            if not silent:
                if timer_id: window.after_cancel(timer_id) # Oyun bitti sayacı durdur
                buttons[a].config(bg=COLOR_WIN); buttons[b].config(bg=COLOR_WIN); buttons[c].config(bg=COLOR_WIN)
                game_over = True
                winner = board[a]
                lbl_timer.config(text="OYUN BİTTİ", fg=COLOR_WIN)
                
                if mode in ["NET_SERVER", "NET_CLIENT"]:
                    if winner == my_net_role: messagebox.showinfo("Sonuç", "🎉 KAZANDINIZ!")
                    else: messagebox.showinfo("Sonuç", "💀 KAYBETTİNİZ!")
                else:
                    messagebox.showinfo("Sonuç", f"KAZANAN: {winner}")
                
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
    
    if mode in ["NET_SERVER", "NET_CLIENT"]:
        update_network_status()
    else:
        lbl_status.config(text=f"Sıra: {turn}", fg=COLOR_X)
        start_timer() # Yerel oyun başlarken sayacı başlat
        if mode == "AI" and turn == 'O': window.after(500, ai_move)

# --- NETWORK İŞLEMLERİ ---

def click_network(idx):
    if board[idx] != "" or game_over: return
    if turn != my_net_role: return 
    
    try:
        sock.send(str(idx).encode()) 
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
    start_timer() # Hamle yapıldı, yeni kişi için sayaç başlasın

def update_network_status():
    if turn == my_net_role:
        lbl_status.config(text="SIRA SENDE!", fg=COLOR_WIN)
        start_timer()
    else:
        lbl_status.config(text="Rakip Düşünüyor...", fg="gray")
        start_timer() # Rakibin süresini göstermek (veya gizlemek) için çağır

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
                window.after(0, reset_board_logic)
            elif data == "TIMEOUT":
                # Rakibin süresi doldu, sıra bana geçti (hamle yok)
                window.after(0, switch_turn_no_move)
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
        s.close() 
        
        my_net_role = 'X'; turn = 'X'; mode = "NET_SERVER"
        setup_game_ui()
        threading.Thread(target=network_listener, daemon=True).start()
    except Exception as e:
        messagebox.showerror("Hata", str(e)); show_main_menu()

def connect_server():
    global sock, my_net_role, turn, mode
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 65432))
        
        my_net_role = 'O'; turn = 'X'; mode = "NET_CLIENT"
        setup_game_ui()
        threading.Thread(target=network_listener, daemon=True).start()
    except:
        messagebox.showerror("Hata", "Sunucu Bulunamadı!"); show_main_menu()

# --- YEREL / AI İŞLEMLERİ ---

def click_local(idx):
    global turn
    if board[idx] != "" or game_over: return
    
    board[idx] = turn
    buttons[idx].config(text=turn, fg=COLOR_X if turn=='X' else COLOR_O)
    
    if check_winner(): return
    
    turn = 'O' if turn == 'X' else 'X'
    lbl_status.config(text=f"Sıra: {turn}", fg=COLOR_X if turn=='X' else COLOR_O)
    
    start_timer() # Sıra değişti, sayaç başlasın
    
    if mode == "AI" and turn == 'O' and not game_over:
        window.after(500, ai_move)

def ai_move():
    if game_over: return
    empty = [i for i, x in enumerate(board) if x == ""]
    if empty: click_local(random.choice(empty))

# --- ARAYÜZ YÖNETİMİ ---

def clear_ui():
    if timer_id: window.after_cancel(timer_id) # Menüye dönerken sayacı durdur
    for widget in window.winfo_children(): widget.destroy()

def show_main_menu():
    global mode
    mode = "MENU"
    try: sock.close()
    except: pass
    clear_ui()
    
    tk.Label(window, text="XOX PFY TEAM", font=("Verdana", 32, "bold"), bg=COLOR_BG, fg=COLOR_TEXT).pack(pady=50)
    btn_style = {"font":("Arial", 14), "bg":COLOR_BTN, "fg":COLOR_TEXT, "width":22, "height":2}
    
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
    
    btn_style = {"font":("Arial", 14), "bg":COLOR_BTN, "fg":COLOR_TEXT, "width":20, "height":2}
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
    global buttons, lbl_status, board, btn_retry, lbl_timer
    board = [""] * 9
    clear_ui()
    
    title = "XOX ONLINE" if "NET" in mode else "XOX OYUNU"
    tk.Label(window, text=title, font=("Arial", 20, "bold"), bg=COLOR_BG, fg=COLOR_TEXT).pack(pady=10)
    
    # SAYAÇ GÖSTERGESİ (YENİ)
    lbl_timer = tk.Label(window, text="⏳ Kalan Süre: 10 sn", font=("Arial", 14, "bold"), bg=COLOR_BG, fg=COLOR_TIMER)
    lbl_timer.pack(pady=5)

    lbl_status = tk.Label(window, text="Oyun Başlıyor...", font=("Arial", 16), bg=COLOR_BG, fg=COLOR_TEXT)
    lbl_status.pack(pady=5)
    
    frame = tk.Frame(window, bg=COLOR_BG)
    frame.pack(pady=10)
    
    buttons = []
    for i in range(9):
        cmd = lambda idx=i: click_network(idx) if "NET" in mode else click_local(idx)
        # RENK DÜZELTMESİ: fg=COLOR_TEXT ve bg=COLOR_BTN
        btn = tk.Button(frame, text="", font=("Arial", 24, "bold"), width=4, height=2,
                        bg=COLOR_BTN, fg=COLOR_TEXT, command=cmd)
        btn.grid(row=i//3, column=i%3, padx=5, pady=5)
        buttons.append(btn)
        
    retry_cmd = send_reset_signal if "NET" in mode else reset_board_logic
    btn_retry = tk.Button(window, text="TEKRAR OYNA 🔄", bg="#E67E22", fg="white", 
                          font=("Arial", 12, "bold"), command=retry_cmd)
    
    tk.Button(window, text="MENÜYE DÖN", bg="#E74C3C", fg="white", command=show_main_menu).pack(side="bottom", pady=20)
    
    reset_board_logic()

# --- BAŞLAT ---
show_main_menu()
window.mainloop()