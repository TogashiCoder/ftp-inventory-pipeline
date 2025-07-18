import os
import yaml
import customtkinter as ctk
from tkinter import messagebox
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parents[1] / 'config' / 'fournisseurs_connexions.yaml'

class FournisseurAdminFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.connexions = self.load_connexions()
        self.selected_fournisseur = None
        self.selected_row_widget = None
        self.build_gui()

    def load_connexions(self):
        if not CONFIG_PATH.exists():
            return {}
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}

    def save_connexions(self):
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            yaml.safe_dump(self.connexions, f, allow_unicode=True)

    def build_gui(self):
        title = ctk.CTkLabel(self, text="Administration Connexion Fournisseur", font=("Segoe UI", 20, "bold"))
        title.pack(pady=(10, 10))
        
        # Table header
        header_frame = ctk.CTkFrame(self, fg_color="#253d61")
        header_frame.pack(fill="x", padx=10)
        headers = ["Nom", "Type", "Hôte", "Port", "Utilisateur", "Mot de passe", "Notes"]
        for i, h in enumerate(headers):
            ctk.CTkLabel(header_frame, text=h, font=("Segoe UI", 13, "bold"), anchor="w", text_color="#fff", fg_color="#253d61").grid(row=0, column=i, padx=4, pady=2, sticky="w")

        # Table body (scrollable)
        self.table_scroll = ctk.CTkScrollableFrame(self, height=260)
        self.table_scroll.pack(fill="x", padx=10, pady=(0, 5))

        # Action buttons
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=8)
        self.add_btn = ctk.CTkButton(btn_frame, text="➕ Ajouter", command=self.add_fournisseur_modal)
        self.edit_btn = ctk.CTkButton(btn_frame, text="✏️ Modifier", command=self.edit_fournisseur_modal, state="disabled")
        self.del_btn = ctk.CTkButton(btn_frame, text="🗑️ Supprimer", command=self.remove_fournisseur, state="disabled")
        self.test_btn = ctk.CTkButton(btn_frame, text="🔌 Tester Connexion", command=self.test_connexion, state="disabled")
        self.add_btn.pack(side="left", padx=5)
        self.edit_btn.pack(side="left", padx=5)
        self.del_btn.pack(side="left", padx=5)
        self.test_btn.pack(side="left", padx=5)

        # Status bar
        self.status_bar = ctk.CTkLabel(self, text="", font=("Segoe UI", 11), text_color="#888", anchor="w")
        self.status_bar.pack(fill="x", padx=10, pady=(2, 0))

        # Now safe to call refresh_table
        self.refresh_table()

    def refresh_table(self):
        for widget in self.table_scroll.winfo_children():
            widget.destroy()
        alt_colors = ["#f7f7f7", "#e9e9e9"]
        for idx, (name, info) in enumerate(self.connexions.items()):
            is_selected = (name == self.selected_fournisseur)
            row_bg = "#ffe5c2" if is_selected else alt_colors[idx%2]
            row_font = ("Segoe UI", 12, "bold") if is_selected else ("Segoe UI", 12)
            row_frame = ctk.CTkFrame(self.table_scroll, fg_color=row_bg)
            row_frame.pack(fill="x", pady=1)
            pw_mask = '******' if info.get('password') else ''
            values = [name, info.get('type',''), info.get('host',''), info.get('port',''), info.get('username',''), pw_mask, info.get('notes','')]
            for i, v in enumerate(values):
                ctk.CTkLabel(row_frame, text=v, anchor="w", font=row_font, text_color="#222", fg_color=row_bg).grid(row=0, column=i, padx=4, pady=2, sticky="w")
            row_frame.bind("<Button-1>", lambda e, n=name, rf=row_frame: self.select_row(n, rf))
            for child in row_frame.winfo_children():
                child.bind("<Button-1>", lambda e, n=name, rf=row_frame: self.select_row(n, rf))
            # highlight if selected
            if is_selected:
                row_frame.configure(border_width=2, border_color="#ef8018")
            else:
                row_frame.configure(border_width=0)
        # --- FIX: After table refresh, reset selection and buttons ---
        self.selected_fournisseur = None
        self.selected_row_widget = None
        self.edit_btn.configure(state="disabled")
        self.del_btn.configure(state="disabled")
        self.test_btn.configure(state="disabled")
        self.status_bar.configure(text="Sélectionnez un fournisseur pour modifier, supprimer ou tester.", text_color="#888")
        # Set focus to Add button to remove hover from last row
        self.add_btn.focus_set()

    def select_row(self, name, row_widget):
        self.selected_fournisseur = name
        if self.selected_row_widget:
            self.selected_row_widget.configure(border_width=0, fg_color="#f7f7f7")
        row_widget.configure(border_width=2, border_color="#ef8018", fg_color="#ffe5c2")
        self.selected_row_widget = row_widget
        self.edit_btn.configure(state="normal")
        self.del_btn.configure(state="normal")
        self.test_btn.configure(state="normal")
        self.status_bar.configure(text=f"Fournisseur sélectionné: {name}", text_color="#253d61")

    def add_fournisseur_modal(self):
        self.open_fournisseur_modal("Ajouter un fournisseur")

    def edit_fournisseur_modal(self):
        if not self.selected_fournisseur:
            return
        self.open_fournisseur_modal("Modifier le fournisseur", self.selected_fournisseur, self.connexions[self.selected_fournisseur])

    def open_fournisseur_modal(self, title, name_init=None, info=None):
        modal = ctk.CTkToplevel(self)
        modal.title(title)
        modal.geometry("500x370")
        modal.grab_set()
        modal.focus()
        modal.resizable(False, False)
        fields = ["Nom", "Type", "Hôte", "Port", "Utilisateur", "Mot de passe", "Notes"]
        entries = {}
        for i, field in enumerate(fields):
            ctk.CTkLabel(modal, text=field+":", anchor="w").grid(row=i, column=0, sticky="w", padx=12, pady=7)
            if field == "Type":
                entry = ctk.CTkComboBox(modal, values=["FTP", "manual"])
                entry.set((info.get('type') if info and info.get('type') else "FTP"))
            elif field == "Mot de passe":
                entry = ctk.CTkEntry(modal, show="*")
                entry.insert(0, info.get('password') if info and info.get('password') else "")
            elif field == "Port":
                entry = ctk.CTkEntry(modal)
                entry.insert(0, str(info.get('port')) if info and info.get('port') else "21")
            elif field == "Nom":
                entry = ctk.CTkEntry(modal)
                entry.insert(0, name_init if name_init else "")
                if name_init:
                    entry.configure(state="disabled")
            else:
                # For all other fields, show empty if missing/null
                entry = ctk.CTkEntry(modal)
                entry.insert(0, info.get(field.lower().replace(' ','')) if info and info.get(field.lower().replace(' ','')) else "")
            entry.grid(row=i, column=1, sticky="ew", padx=8, pady=7)
            entries[field] = entry
        modal.grid_columnconfigure(1, weight=1)
        def on_save():
            name = entries["Nom"].get().strip()
            type_ = entries["Type"].get().strip()
            host = entries["Hôte"].get().strip()
            port = entries["Port"].get().strip()
            username = entries["Utilisateur"].get().strip()
            password = entries["Mot de passe"].get().strip()
            notes = entries["Notes"].get().strip()
            if not name:
                self.status_bar.configure(text="Le nom est requis.", text_color="#d6470e")
                return
            if not type_:
                self.status_bar.configure(text="Le type est requis.", text_color="#d6470e")
                return
            if type_.lower() == "ftp" and (not host or not username or not password):
                self.status_bar.configure(text="Hôte, utilisateur et mot de passe requis pour FTP.", text_color="#d6470e")
                return
            try:
                port = int(port) if port else 21
            except ValueError:
                self.status_bar.configure(text="Le port doit être un nombre.", text_color="#d6470e")
                return
            info_dict = {
                'type': type_,
                'host': host,
                'port': port,
                'username': username,
                'password': password,
                'notes': notes
            }
            if not name_init and name in self.connexions:
                self.status_bar.configure(text="Ce fournisseur existe déjà.", text_color="#d6470e")
                return
            self.connexions[name] = info_dict
            self.save_connexions()
            self.refresh_table()
            self.status_bar.configure(text="Fournisseur enregistré avec succès.", text_color="#1a7f37")
            modal.destroy()
        def on_cancel():
            modal.destroy()
        btn_save = ctk.CTkButton(modal, text="💾 Enregistrer", command=on_save)
        btn_cancel = ctk.CTkButton(modal, text="Annuler", command=on_cancel)
        btn_save.grid(row=len(fields), column=0, pady=15, padx=12)
        btn_cancel.grid(row=len(fields), column=1, pady=15, padx=12, sticky="e")

    def remove_fournisseur(self):
        if not self.selected_fournisseur:
            return
        if messagebox.askyesno("Confirmer", f"Supprimer {self.selected_fournisseur} ?"):
            del self.connexions[self.selected_fournisseur]
            self.save_connexions()
            # --- FIX: Reset selection and buttons after delete ---
            self.selected_fournisseur = None
            self.selected_row_widget = None
            self.refresh_table()
            self.status_bar.configure(text="Fournisseur supprimé.", text_color="#d6470e")

    def test_connexion(self):
        # Always use the current selected_fournisseur and update status bar
        if not self.selected_fournisseur or self.selected_fournisseur not in self.connexions:
            self.status_bar.configure(text="Sélectionnez un fournisseur à tester.", text_color="#d6470e")
            return
        info = self.connexions[self.selected_fournisseur]
        if info.get('type', '').lower() == 'manual':
            self.status_bar.configure(text="Ce fournisseur est manuel (pas de connexion à tester).", text_color="#888")
            return
        try:
            from ftplib import FTP
            ftp = FTP()
            ftp.connect(info['host'], int(info['port']))
            ftp.login(info['username'], info['password'])
            ftp.quit()
            self.status_bar.configure(text="Connexion FTP réussie !", text_color="#1a7f37")
        except Exception as e:
            self.status_bar.configure(text=f"Échec de la connexion FTP : {e}", text_color="#d6470e")
