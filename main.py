import customtkinter as ctk
from valclient.client import Client
import threading
import time
import random
import string
import keyboard

# --- TÜM GÜNCEL AJANLARIN KİMLİK KODLARI (2026) ---
AGENT_DATA = {
    "REYNA": "a3bfb853-43b2-7238-a4f1-ad90e9e46bcc",
    "CLOVE": "1dbf2edd-4729-0984-3115-daa5eed44993",
    "JETT": "add6443a-41bd-e414-f6ad-e58d267f4e95",
    "ISO": "0e38b510-41a8-5780-5e8f-568b2a4f2d6c",
    "RAZE": "f94c3b30-42be-e959-889c-5aa313dba261",
    "VYSE": "efba5359-4016-a1e5-7626-b1ae76895940",
    "GEKKO": "e370fa57-4757-3604-3648-499e1f642d3f",
    "OMEN": "8e253930-4c05-31dd-1b6c-968525494517",
    "VIER": "707eab51-4836-f488-046a-cda6bf494859", # Viper
    "SAGE": "569fdd95-4d10-43ab-ca70-79becc718b46",
    "SOVA": "320b2a48-4d9b-a075-30f1-1f93a9b638fa",
    "PHOENIX": "eb93336a-449b-9c1b-0a54-a891f7921d69",
    "BRIMSTONE": "9f0d8ba9-4140-b941-57d3-a7ad57c6b417",
    "CYPHER": "117ed9e3-49f3-6512-3ccf-0cada7e3823b",
    "KILLJOY": "1e58de9c-4950-5125-93e9-a0aee9f98746",
    "BREACH": "5f8d3a7f-467b-97f3-062c-13acf203c006",
    "SKYE": "6f2a04ca-43e0-be17-7f36-b3908627744d",
    "YORU": "7f94d92c-4234-0a36-9646-3a87eb8b5c89",
    "ASTRA": "41fb69c1-4189-7b37-f117-bcaf1e96f1bf",
    "KAY/O": "601dbbe7-43ce-be57-2a40-4abd24953621",
    "CHAMBER": "22697a3d-45bf-8dd7-4fec-84a9e28c69d7",
    "NEON": "bb2a4828-46eb-8cd1-e765-15848195d751",
    "FADE": "dade69b4-4f5a-8528-247b-219e5a1facd6",
    "HARBOR": "95b78ed7-4637-86d9-7e41-71ba8c293152",
    "DEADLOCK": "cc8b64c8-4b25-4ff9-6e7f-37b4da43d235"
}

class ScorpionLockerV6(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- PENCERE AYARLARI ---
        self.title(''.join(random.choices(string.ascii_letters, k=12))) # Anti-Vanguard Title
        self.geometry("500x850")
        self.configure(fg_color="#0B0E11") # Daha derin siyah
        
        self.client = None
        self.active = False
        self.selected_uuid = None
        self.lock_speed = 0.1 # Varsayılan hız

        # --- LOGO & BAŞLIK ---
        self.header = ctk.CTkLabel(self, text="SCORPION ENGINE", text_color="#FF4655", 
                                  font=("Impact", 32))
        self.header.pack(pady=(30, 5))
        
        self.sub_header = ctk.CTkLabel(self, text="API-BASED INSTALOCKER v6.0", text_color="#555E67", 
                                      font=("Arial", 12, "bold"))
        self.sub_header.pack(pady=(0, 20))

        # --- DURUM PANELİ ---
        self.status_frame = ctk.CTkFrame(self, fg_color="#161B22", corner_radius=10)
        self.status_frame.pack(fill="x", padx=40, pady=10)
        
        self.status_lbl = ctk.CTkLabel(self.status_frame, text="DURUM: BEKLENİYOR", text_color="#36D5B8",
                                     font=("Arial", 13, "bold"))
        self.status_lbl.pack(pady=10)

        # --- AJAN SEÇİM ALANI ---
        ctk.CTkLabel(self, text="HEDEF AJAN SEÇİN", text_color="white", font=("Arial", 11, "bold")).pack(anchor="w", padx=45)
        
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="#0B0E11", border_width=2, 
                                                 border_color="#1F2326", height=320)
        self.scroll_frame.pack(fill="both", padx=40, pady=5)

        # Ajan Butonlarını Oluştur
        self.agent_buttons = {}
        for name in sorted(AGENT_DATA.keys()):
            btn = ctk.CTkButton(self.scroll_frame, text=name, fg_color="#1F2326", 
                               hover_color="#FF4655", text_color="#EEEEEE",
                               font=("Arial", 13, "bold"), height=40,
                               command=lambda n=name: self.select_agent(n))
            btn.pack(pady=3, fill="x")
            self.agent_buttons[name] = btn

        # --- AYARLAR PANELİ ---
        self.settings_frame = ctk.CTkFrame(self, fg_color="#161B22", corner_radius=10)
        self.settings_frame.pack(fill="x", padx=40, pady=15)
        
        ctk.CTkLabel(self.settings_frame, text="KİLİTLEME HIZI (MS)", text_color="white", font=("Arial", 10)).pack(pady=(5,0))
        self.speed_slider = ctk.CTkSlider(self.settings_frame, from_=0.01, to=1.0, 
                                        button_color="#FF4655", command=self.update_speed)
        self.speed_slider.set(0.1)
        self.speed_slider.pack(pady=10, padx=20)

        # --- KONSOL ---
        self.console = ctk.CTkTextbox(self, height=100, fg_color="#080A0C", 
                                     text_color="#36D5B8", font=("Consolas", 11),
                                     border_width=1, border_color="#1F2326")
        self.console.pack(fill="x", padx=40, pady=10)

        # --- ANA BUTON ---
        self.main_btn = ctk.CTkButton(self, text="SİSTEMİ AKTİF ET (F9)", fg_color="#FF4655", 
                                     hover_color="#D13644", height=50, 
                                     font=("Arial", 16, "bold"), command=self.toggle_system)
        self.main_btn.pack(pady=20, padx=40, fill="x")

        # Background threads
        threading.Thread(target=self.key_handler, daemon=True).start()

    def update_speed(self, val):
        self.lock_speed = float(val)

    def log(self, msg):
        self.console.insert("end", f"> {msg}\n")
        self.console.see("end")

    def select_agent(self, name):
        # Önceki seçimi temizle
        for btn in self.agent_buttons.values():
            btn.configure(fg_color="#1F2326")
        
        self.selected_uuid = AGENT_DATA[name]
        self.agent_buttons[name].configure(fg_color="#FF4655")
        self.status_lbl.configure(text=f"HEDEF: {name}", text_color="#FF4655")
        self.log(f"Hedef {name} olarak ayarlandı.")

    def toggle_system(self):
        if not self.selected_uuid:
            self.log("HATA: Önce bir ajan seçin!")
            return

        if not self.active:
            try:
                self.log("API Bağlantısı kuruluyor...")
                self.client = Client(region="eu")
                self.client.activate()
                self.active = True
                self.main_btn.configure(text="SİSTEMİ DURDUR", fg_color="#36393F")
                self.log("BAĞLANTI BAŞARILI. Tarama aktif.")
                threading.Thread(target=self.locking_loop, daemon=True).start()
            except:
                self.log("HATA: Valorant bulunamadı!")
        else:
            self.active = False
            self.main_btn.configure(text="SİSTEMİ AKTİF ET (F9)", fg_color="#FF4655")
            self.log("Sistem durduruldu.")

    def locking_loop(self):
        while self.active:
            try:
                # Pregame kontrolü
                match_data = self.client.pregame_fetch_match()
                if "ID" in match_data:
                    self.log("MAÇ BULUNDU! İşlem yapılıyor...")
                    # ŞAK!
                    self.client.pregame_select_character(self.selected_uuid)
                    time.sleep(self.lock_speed) # Ayarlanabilir gecikme
                    self.client.pregame_lock_character(self.selected_uuid)
                    
                    self.log("AJAN KİLİTLENDİ.")
                    self.active = False
                    self.after(0, lambda: self.main_btn.configure(text="SİSTEMİ AKTİF ET (F9)", fg_color="#FF4655"))
                    break
            except: pass
            time.sleep(0.1)

    def key_handler(self):
        while True:
            if keyboard.is_pressed('f9'):
                self.after(0, self.toggle_system)
                time.sleep(1)
            time.sleep(0.05)

if __name__ == "__main__":
    app = ScorpionLockerV6()
    app.mainloop()