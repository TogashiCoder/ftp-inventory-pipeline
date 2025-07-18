import os
import sys
import yaml
import time
import string
import threading
import customtkinter as ctk

from pathlib import Path
from tkinter import scrolledtext
from utils import read_yaml_file
from functions.functions_update import *
from config.logging_config import logger
from config.config_path_variables import *
from tkinter import filedialog, messagebox
from config.temporary_data_list import current_dataFiles
from functions.functions_FTP import upload_updated_files_to_marketplace

class MajManuelleFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        
        self.annotation_platforms = {'PLATFORM_A': 'ALZURA2025-2.csv',
                                 'PLATFORM_B':'departo.csv',
                                 'PLATFORM_C':'Market-DE-...csv',
                                 'PLATFORM_D':'07zr2026.csv',
                                 'PLATFORM_E':'Ajout offre drox...xlsx',
                                 'PLATFORM_F':'pieces aftermarket.xlsx',
                                 'PLATFORM_G':'TIELEHABERDER.csv'
                                 }
    
        self.annotation_fournisseurs = {'FOURNISSEUR_A': 'pricing_stock.xlsx ',
                                 'FOURNISSEUR_B':'stocklist.xls',
                                 'FOURNISSEUR_C':'AJS-OFERTA-...csv',
                                 'FOURNISSEUR_D':'export (66).csv',
                                 'FOURNISSEUR_E':'Airstal.csv',
                                 'FOURNISSEUR_F':'skv.xlsx ',
                                 'FOURNISSEUR_G':'Stock.txt',
                                  'FOURNISSEUR_H':'...Shop-Artikelsta...csv',
                                  'FOURNISSEUR_I':'rad_01.csv',
                                  'FOURNISSEUR_J':'rad_02.csv',
                                 }
        
        
        
        # Common button style with orange theme
        orange_hover =  "#ef8018"#"#FFA500"   # Darker orange on hover
        self.button_kwargs = {            
            "font": ("Arial", 15),
            "height": 35,
            "corner_radius": 8,
            "fg_color": "#253d61", #"#2d4d7e",  #"#c5c7c8", #"#3B8ED0",
            "hover_color": orange_hover,
            "text_color": "white",
        }
        button_MAJ_kwargs = {            
            "font": ("Arial", 16),
            "height": 45,
            "corner_radius": 8,
            "fg_color": "#253d61", #"#2d4d7e",  #"#c5c7c8", #"#3B8ED0",
            "hover_color": orange_hover,
            "text_color": "white",
        }
        # Police utilisée
        title_font = ("Segoe UI", 20, "bold")

        # ------------------------------------ Titre ------------------------------
        label = ctk.CTkLabel(self, text="Synchronisation des Stocks : Fournisseurs → Plateformes", font=title_font)
        label.pack(pady=(10, 20))

        self.platform_file = None
        self.fournisseur_files = []
        # -------------------------------------------------------------------------
        

        # ----------------------- Bloc 2 : Listes Fournisseurs -----------------------
        self.block2 = ctk.CTkFrame(self, corner_radius=15, fg_color="transparent")
        self.block2.pack(fill="x", pady=(37,15))
        
        self.sub_blockA = ctk.CTkFrame(self.block2, fg_color="transparent")
        self.sub_blockA.pack(fill="x", padx=1, pady=5)

        # change here ----------------->>>>>>
        self.sub_blockA_1 = ctk.CTkFrame(self.sub_blockA, corner_radius=10, fg_color="transparent", border_width=1, border_color="#555555")
        self.sub_blockA_1.pack(side="left", fill="both", expand=True, padx=(1, 3), pady=5)

        self.sub_blockA_1_a = ctk.CTkFrame(self.sub_blockA_1, fg_color="transparent")
        self.sub_blockA_1_a.pack(fill="x", padx=8, pady=5)
                
        self.execution_label = ctk.CTkLabel(self.sub_blockA_1_a,fg_color="transparent", text="📁 Fichiers Fournisseurs",  font=("Segoe UI", 13, "bold"))
        self.execution_label.pack(side="left",fill="both", anchor="w")
                
    
        self.scrollable_frame = ctk.CTkScrollableFrame(self.sub_blockA_1, height=225, fg_color="transparent")
        self.scrollable_frame.pack(fill="x", anchor="n", padx=2)
        
            
        # ----------------------- Bloc 4 : Listes Plateforms -----------------------
        self.sub_blockB_1 = ctk.CTkFrame(self.sub_blockA, corner_radius=10, fg_color="transparent", border_width=1, border_color="#555555")
        self.sub_blockB_1.pack(side="right", fill="both", expand=True, padx=(3, 1), pady=5)

        self.sub_blockB_1_a = ctk.CTkFrame(self.sub_blockB_1, fg_color="transparent")
        self.sub_blockB_1_a.pack(fill="x", padx=8,pady=5)

        self.execution_label = ctk.CTkLabel(self.sub_blockB_1_a, fg_color="transparent", text="📁 Fichiers Plateforms", anchor="w", font=("Segoe UI", 13, "bold"))
        self.execution_label.pack(side="left", anchor="w",fill="both")
                


        self.scrollable_frameF = ctk.CTkScrollableFrame(self.sub_blockB_1, height=225, fg_color="transparent")
        self.scrollable_frameF.pack(fill="x", anchor="n", padx=2)


        self.sub_blockB = ctk.CTkFrame(self.block2, fg_color="transparent")
        self.sub_blockB.pack(fill="x", pady=3)

            # Bouton Valider
        self.submit_btn = ctk.CTkButton(self.sub_blockB, text="✅ \tValider la Mise à Jour\t", command=self.run_update, **button_MAJ_kwargs)
        self.submit_btn.pack( pady=5)
        # -------------------------------------------------------------------------

    

        # ----------------------- Bloc 3 : Affichage du log -----------------------
        self.block3 = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent", border_width=1, border_color="#555555")
        self.block3.pack(fill="x", pady=(0,2))

        self.log_label = ctk.CTkLabel(self.block3, text="Journal de Mise à Jour :", anchor="w", font=("Segoe UI", 13, "bold"))
        self.log_label.pack(anchor="w", padx=15)

        self.log_frame = ctk.CTkScrollableFrame(self.block3, height=130, fg_color="#2e2e2e", corner_radius=0)
        self.log_frame.pack(fill="x", padx=15, pady=(5, 10))
        # -------------------------------------------------------------------------
        self.list_platforms = {}
        self.list_fournisseurs = {}
        self.platform_blocks = {}
        self.fournisseur_blocks = {}
        self.load_platforms_from_yaml(HEADER_PLATFORMS_YAML)
        self.load_fournisseurs_from_yaml(HEADER_FOURNISSEURS_YAML)


        
    def tronquer_nom_fichier(self, nom_fichier, max_longueur=40):
        if len(nom_fichier) <= max_longueur:
            return nom_fichier
        else:
            # Séparer nom et extension
            nom_sans_ext, ext = os.path.splitext(nom_fichier)
            # Garder un peu du début et ajouter "..." + extension
            taille_visible = max_longueur - len(ext) - 3  # 3 pour "..."
            return nom_sans_ext[:taille_visible] + "..." + ext
        
    
        
        # -----------------------------------------------------

    def load_platforms_from_yaml(self, yaml_path):
        try:
            platforms_data = read_yaml_file(yaml_path=yaml_path)
            # Boucle sur les plateformes
            """for idx, (platform_key, platform_info) in enumerate(platforms_data.items()):
                letter = string.ascii_uppercase[idx]  # A, B, C...
                self.create_platform_block(letter, platform_key)
            """
            lettres = list(string.ascii_uppercase)
            for i, platform_key in enumerate(platforms_data.keys()):
                letter = lettres[i] if i < len(lettres) else f"Extra_{i}"
                self.add_platform_block(letter, platform_key)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des plateformes : {e}")



    def load_fournisseurs_from_yaml(self, yaml_path):
        try:
            fournisseurs_data = read_yaml_file(yaml_path=yaml_path)
            # Boucle sur les plateformes
            """for idx, (platform_key, platform_info) in enumerate(platforms_data.items()):
                letter = string.ascii_uppercase[idx]  # A, B, C...
                self.create_platform_block(letter, platform_key)
            """
            lettres = list(string.ascii_uppercase)
            for i, fournisseur_key in enumerate(fournisseurs_data.keys()):
                letter = lettres[i] if i < len(lettres) else f"Extra_{i}"
                self.add_fournisseur_block(letter, fournisseur_key)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des fournisseurs : {e}")


    def select_platform_file(self, letter):
        file_path = filedialog.askopenfilename(title="Choisir un fichier Plateforme")
        if file_path:
            self.list_platforms[f'PLATFORM_{letter.upper()}'] = f"./fichiers_platforms/{os.path.basename(file_path)}"
            print('platform list:', self.list_platforms)
            self.platform_blocks[letter]["file_path"] = file_path
            self.platform_blocks[letter]["path_label"].configure(text=self.tronquer_nom_fichier(os.path.basename(file_path)), text_color="#FFFFFF" )

    def select_fournisseur_file(self, letter):
        file_path = filedialog.askopenfilename(title="Choisir un fichier Fournisseur")
        if file_path:
            self.list_fournisseurs[f'FOURNISSEUR_{letter.upper()}'] = f"./fichiers_fournisseurs/{os.path.basename(file_path)}"
            print('fournisseurs list:', self.list_fournisseurs)
            self.fournisseur_blocks[letter]["file_path"] = file_path
            self.fournisseur_blocks[letter]["path_label"].configure(text=self.tronquer_nom_fichier(os.path.basename(file_path)), text_color="#FFFFFF" )


    def clear_platform_file(self, letter):
        if f'PLATFORM_{letter}' in self.list_platforms:
            del self.list_platforms[f'PLATFORM_{letter}']
        self.platform_blocks[letter]["file_path"] = None
        self.platform_blocks[letter]["path_label"].configure(text=f"**Required:** {self.annotation_platforms[f'PLATFORM_{letter}']}...",text_color="#FDC8AF")
        
    
    def clear_fournisseur_file(self, letter):
        if f'FOURNISSEUR_{letter}' in self.list_fournisseurs:
            del self.list_fournisseurs[f'FOURNISSEUR_{letter}']
        self.fournisseur_blocks[letter]["file_path"] = None
        self.fournisseur_blocks[letter]["path_label"].configure(text=f"**Required:** {self.annotation_fournisseurs[f'FOURNISSEUR_{letter}']}...", text_color="#FDC8AF")



    def add_platform_block(self, letter, platform_key):
        block = ctk.CTkFrame(self.scrollable_frameF, fg_color="transparent")
        block.pack(fill="x", padx=20, pady=6)

        label = ctk.CTkLabel(block, text=f"🔹 Plateform {letter}", font=("Segoe UI", 14))
        label.pack(side="left", padx=(0, 5))

        path_label = ctk.CTkLabel(block, text=f"**Required:** {self.annotation_platforms[f'PLATFORM_{letter}']}", text_color="#FDC8AF", font=("Segoe UI", 13))
        path_label.pack(side="left", fill="x", expand=True)

        btn_load = ctk.CTkButton(block, text="📁", command=lambda: self.select_platform_file(letter), **{
            "font": ("Arial", 14), "height": 24, "width": 45, "corner_radius": 8,
            "fg_color": "#253d61", "hover_color": "#ef8018", "text_color": "white"
        })
        btn_load.pack(side="right", padx=(5, 0))

        btn_delete = ctk.CTkButton(block, text="❌", command=lambda: self.clear_platform_file(letter), **{
            "font": ("Arial", 8), "height": 10, "width": 5, "corner_radius": 6,
            "fg_color": "#f8d2b2", "hover_color": "#ef8018", "text_color": "#d6470e"
        })
        btn_delete.pack(side="right")

        # Enregistre dans le dictionnaire
        self.platform_blocks[letter] = {
            "key": platform_key,
            "block": block,
            "path_label": path_label,
            "file_path": None
        }



    def add_fournisseur_block(self, letter, fournisseur_key):
        block = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        block.pack(fill="x", padx=20, pady=6)

        label = ctk.CTkLabel(block, text=f"🔹 Fournisseur {letter}", font=("Segoe UI", 14))
        label.pack(side="left", padx=(0, 5))

        path_label = ctk.CTkLabel(block, text=f"**Required:** {self.annotation_fournisseurs[f'FOURNISSEUR_{letter}']}",text_color="#FDC8AF", font=("Segoe UI", 13))
        path_label.pack(side="left", fill="x", expand=True)

        btn_load = ctk.CTkButton(block, text="📁", command=lambda: self.select_fournisseur_file(letter), **{
            "font": ("Arial", 14), "height": 24, "width": 45, "corner_radius": 8,
            "fg_color": "#253d61", "hover_color": "#ef8018", "text_color": "white"
        })
        btn_load.pack(side="right", padx=(5, 0))

        btn_delete = ctk.CTkButton(block, text="❌", command=lambda: self.clear_fournisseur_file(letter), **{
            "font": ("Arial", 8), "height": 10, "width": 5, "corner_radius": 6,
            "fg_color": "#f8d2b2", "hover_color": "#ef8018", "text_color": "#d6470e"
        })
        btn_delete.pack(side="right")

        # Enregistre dans le dictionnaire
        self.fournisseur_blocks[letter] = {
            "key": fournisseur_key,
            "block": block,
            "path_label": path_label,
            "file_path": None
        }


    def load_file(label):
        path = filedialog.askopenfilename()
        if path:
            label.configure(text=path)


    def show_logs(self,LOG_FILE_PATH):
        # Affichage ligne par ligne
        if os.path.exists(LOG_FILE_PATH):
            with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
                for line in f.readlines():
                    label = ctk.CTkLabel(self.log_frame, text=line.strip(), anchor="w", text_color="white")
                    label.pack(anchor="w", pady=1, padx=5)
        else:
            label = ctk.CTkLabel(self.log_frame, text="Erreur: Fichier de log introuvable.", anchor="w", text_color="white")
            label.pack(anchor="w", pady=1, padx=5)


    def get_latest_file(self, folder_path):
        files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        
        if not files:
            return None  # Aucun fichier

        latest_file = max(files, key=os.path.getctime)  # ou os.path.getmtime
        return latest_file



    def select_fournisseur_files(self):
        files = filedialog.askopenfilenames(
            title="Choisir les fichiers Fournisseurs",
            filetypes=[
                ("Fichiers supportés", "*.csv *.xlsx *.xls *.txt *.json"),
                ("Fichiers CSV", "*.csv"),
                ("Fichiers Excel", "*.xlsx *.xls"),
                ("Fichiers texte", "*.txt"),
                ("Fichiers JSON", "*.json"),
                ("Tous les fichiers", "*.*")
            ]
        )
        if files:
            self.fournisseur_files = files
            for f in files:
                label = ctk.CTkLabel(self.fournisseur_list, text=f"🔹 {os.path.basename(f)}", anchor="w", height=25)
                label.pack(anchor="w", padx=10, pady=2)


    def validate_update(self):
        dossier_A = "logs"
        dernier_fichier = self.get_latest_file(dossier_A)
        self.show_logs(dernier_fichier)
        messagebox.showinfo("Traitement", "Fonction de validation appelée.")


    def populate_list(self, container, items):
        for item in items:

            label = ctk.CTkLabel(container, text=f"🔹 Plateforme {item}", anchor="w", height=25)
            label.pack(anchor="w", padx=10, pady=2)

            #label = ctk.CTkLabel(container, text=f"🔹 Plateforme {item}", anchor="w", height=25)
            #label.pack(anchor="w", padx=10, pady=2)



    def get_latest_file(self, folder_path=LOG_FOLDER):
        files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        
        if not files:
            return None  # Aucun fichier

        latest_file = max(files, key=os.path.getctime)  # ou os.path.getmtime
        return latest_file


    def run_update(self):
        # ---------------- Nettoyage du log précédent ----------------
        for widget in self.log_frame.winfo_children():
            widget.destroy()
        
        self.log_running = True  # Pour arrêter plus tard

        # ---------------- Afficher le début du log ----------------
        txt_line = '----------------------------------- Start -----------------------------------'
        label = ctk.CTkLabel(self.log_frame, text=txt_line, anchor="w", text_color="white")
        label.pack(anchor="w", pady=1, padx=5)

        self.log_file_path = self.get_latest_file()
      
        # Lancement de la lecture dynamique
        threading.Thread(target=self.tail_log_file, daemon=True).start()

        # Lancement du traitement principal
        threading.Thread(target=self._run_update_process, daemon=True).start()

        





    def _run_update_process(self):
        try:
            # ---------------------- Loding Data via FTP ---------------------
            # fichiers_fournisseurs, fichiers_platforms = config_and_load_data_from_FTP()

            # ----------------------- Loding Local Data ----------------------
            #fichiers_fournisseurs, fichiers_platforms = current_dataFiles()
            fichiers_fournisseurs = self.list_fournisseurs
            fichiers_platforms = self.list_platforms

            # ---------------------- Loding Data via FTP ---------------------
           
            fournisseurs_files_valides = check_ready_files(title_files='Fournisseurs', downloaded_files=fichiers_fournisseurs, yaml_with_header_items=HEADER_FOURNISSEURS_YAML)
            platforms_files_valides = check_ready_files(title_files='Plateformes', downloaded_files=fichiers_platforms, yaml_with_header_items=HEADER_PLATFORMS_YAML)
                
            # ------------------- Mettre A Jour le stock ---------------------
            is_store_updated = mettre_a_jour_Stock(platforms_files_valides, fournisseurs_files_valides)

            if is_store_updated:

                logger.info('-- -- ✅ -- --  Mise à jour effectuée -- -- ✅ -- -- ')
                upload_updated_files_to_marketplace(dry_run=False)
                messagebox.showinfo("Succès", "✅ La mise à jour a été effectuée avec succès.\nFiles have been uploaded to marketplaces FTP.")
                 
                # Supprimer ancien bouton s'il existe
                if hasattr(self, 'open_update_btn') and self.open_update_btn.winfo_exists():
                    self.open_update_btn.destroy()
                    
                # Bouton pour accéder au dossier mis à jour
                self.open_update_btn = ctk.CTkButton(
                    self.log_frame,
                    text="📂 Accéder aux fichiers mis à jour",
                    command=self.open_update_folder,
                    **self.button_kwargs
                )
                self.open_update_btn.pack(padx=15, pady=(0, 5))
        
            else:
                messagebox.showerror("Error", "-- -- ❌ -- --  Error de mise à jour  -- -- ❌ -- --")
                logger.info('-- -- ❌ -- --  Error de mise à jour  -- -- ❌ -- -- ')
            
            # Fin du suivi
            self.log_running = False

        except Exception as e:
            logger.error(f"❌ Erreur : {e}")
            messagebox.showerror("Erreur", str(e))
            # Fin du suivi
            self.log_running = False
        
   






    def tail_log_file(self):
        """Lit le fichier log ligne par ligne pendant qu'il est en cours d'écriture."""
        # Attend que le fichier existe
        while not os.path.exists(self.log_file_path):
            time.sleep(0.1)

        with open(self.log_file_path, "r", encoding="utf-8") as f:
            # Aller à la fin du fichier existant
            f.seek(0, os.SEEK_END)

            while self.log_running:
                line = f.readline()
                if line:
                    self.after(0, lambda l=line: self.add_log_line(l.strip()))
                else:
                    time.sleep(0.2)  # Pause courte avant de re-tester


    def add_log_line(self, line):
        color = "white"
        if "❌" in line or "Erreur" in line:
            color = "#FA936A"
        elif "✅" in line or "Succès" in line:
            color = "#5BB2EC"
        elif "⚠️" in line :
            color = "#F1D639"

        label = ctk.CTkLabel(self.log_frame, text=line, anchor="w",  text_color=color, font=("Segoe UI Emoji", 13))
        label.pack(anchor="w", pady=0, padx=2)

    
    def open_update_folder(self):
        dossier_mis_a_jour = UPDATED_FILES_PATH_RACINE  # à adapter si ton dossier de sortie est différent

        try:
            if os.path.exists(dossier_mis_a_jour):
                if os.name == 'nt':  # Windows
                    os.startfile(dossier_mis_a_jour)
                elif os.name == 'posix':  # MacOS, Linux
                    subprocess.Popen(['xdg-open', dossier_mis_a_jour])
            else:
                messagebox.showwarning("Dossier introuvable", f"Le dossier {dossier_mis_a_jour} n'existe pas.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir le dossier : {str(e)}")

    

    def show_logs(self, LOG_FILE_PATH):
        if not os.path.exists(LOG_FILE_PATH):
            label = ctk.CTkLabel(self.log_frame, text="Erreur: Fichier de log introuvable.", anchor="w", text_color="white")
            label.pack(anchor="w", pady=1, padx=5)
            return

        # Lire les lignes à l'avance
        with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
            self.log_lines = f.readlines()

        self.current_line_index = 0
        self.display_next_log_line()


    def display_next_log_line(self):
        if self.current_line_index < len(self.log_lines):
            line = self.log_lines[self.current_line_index].strip()
            label = ctk.CTkLabel(self.log_frame, text=line, anchor="w", text_color="white")
            label.pack(anchor="w", pady=0, padx=2)

            self.current_line_index += 1

            # Affiche la prochaine ligne après 10 ms
            self.after(10, self.display_next_log_line)
    
