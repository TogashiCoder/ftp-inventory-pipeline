import customtkinter as ctk

class PlateformFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
    
        # === Police utilisée === 
        title_font = ("Segoe UI", 20, "bold")

        # === Titre principal ===
        label = ctk.CTkLabel(self, text="Administration des Connexions Plateforme (FTP)", font=title_font)
        label.pack(pady=(10, 20))