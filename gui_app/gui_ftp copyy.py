import time 
import customtkinter as ctk
from tkinter import filedialog, messagebox
from tkinter import scrolledtext
import os
import sys
import threading

from functions.functions_update import *

class MajFTPFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        # Common button style with orange theme
        orange_hover =  "#ef8018"#"#FFA500"   # Darker orange on hover
        button_kwargs = {            
            "font": ("Arial", 15),
            "height": 35,
            "corner_radius": 8,
            "fg_color": "#253d61", #"#2d4d7e",  #"#c5c7c8", #"#3B8ED0",
            "hover_color": orange_hover,
            "text_color": "white",
        }
        button_MAJ_kwargs = {            
            "font": ("Arial", 17),
            "height": 55,
            "corner_radius": 8,
            "fg_color": "#253d61", #"#2d4d7e",  #"#c5c7c8", #"#3B8ED0",
            "hover_color": orange_hover,
            "text_color": "white",
        }
        frames_dark_kwargs={
            "fg_color": "transparent", 
            "border_width": 1, 
            "border_color": "#555555"
        }
        frames_light_kwargs={
            "fg_color": "transparent", 
            "border_width": 1, 
            "border_color": "#AAAAAA"
        }
        # Police utilisée
        title_font = ("Segoe UI", 20, "bold")

        # ------------------------------------ Titre ------------------------------
        label = ctk.CTkLabel(self, text="Synchronisation des Stocks : Fournisseurs → Plateformes", font=title_font)
        label.pack(pady=(10, 20))

        self.platform_file = None
        self.fournisseur_files = []
        # -------------------------------------------------------------------------

        # ------------------------- Bloc 1 : Exécution FTP ------------------------
        self.block1 = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent", border_width=1, border_color="#555555")
        self.block1.pack(fill="x", pady=(45,5))

        self.execution_label = ctk.CTkLabel(self.block1, text="Synchronisation Automatique :", anchor="w", font=("Segoe UI", 13, "bold"))
        self.execution_label.pack(anchor="w", padx=15)
        
        self.execute_btn = ctk.CTkButton(self.block1, text="🖧      Mettre à Jour via FTP       🖧", command=self.run_update, **button_MAJ_kwargs)
        self.execute_btn.pack(padx=15, pady=(0, 25))
        # -------------------------------------------------------------------------
        


        # ----------------------- Bloc 2 : Listes Fournisseurs et Plateformes -----------------------
        self.block2 = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent", border_width=1, border_color="#555555")
        self.block2.pack(fill="x", pady=12)

        # Fournisseurs
        fournisseurs_label = ctk.CTkLabel(self.block2, text="📦 Plateformes et Fournisseurs disponibles :", anchor="w", font=("Segoe UI", 13, "bold"))
        fournisseurs_label.pack(anchor="w", padx=15)


                # Frame contenant les deux listes côte à côte
        list_container = ctk.CTkFrame(self.block2, fg_color="transparent")
        list_container.pack(fill="x", padx=15, pady=(5, 10))

        # Fournisseurs
        self.fournisseur_list = ctk.CTkScrollableFrame(list_container, height=80, width=200)
        self.fournisseur_list.pack(side="left", fill="both", expand=True, padx=(0, 10))
        #self.populate_list(self.fournisseur_list, ["Fournisseur_A", "Fournisseur_B", "Fournisseur_C"])  # Remplace par ta vraie liste

        # Plateformes
        self.plateform_list = ctk.CTkScrollableFrame(list_container, height=80, width=200)
        self.plateform_list.pack(side="left", fill="both", expand=True)
        #self.populate_list(self.plateform_list, ["Plateforme_1", "Plateforme_2", "Plateforme_3"])  # Remplace aussi ici
        # -------------------------------------------------------------------------

        


        # ----------------------- Bloc 3 : Affichage du log -----------------------
        self.block3 = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent", border_width=1, border_color="#555555")
        self.block3.pack(fill="x", pady=8)

        self.log_label = ctk.CTkLabel(self.block3, text="Journal de Mise à Jour :", anchor="w", font=("Segoe UI", 13, "bold"))
        self.log_label.pack(anchor="w", padx=10)
        self.log_frame = ctk.CTkScrollableFrame(self.block3, height=130, fg_color="#2e2e2e", corner_radius=0)
        self.log_frame.pack(fill="x", padx=15, pady=(3, 5))

        self.load_ftp_infos()

        # -------------------------------------------------------------------------

    """
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
    """

    def get_latest_file(self, folder_path):
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
        txt_line = '-------------- * * * Start * * * --------------'
        label = ctk.CTkLabel(self.log_frame, text=txt_line, anchor="w", text_color="white")
        label.pack(anchor="w", pady=1, padx=5)

        dossier_A = LOG_FOLDER
        self.log_file_path = self.get_latest_file(dossier_A)
      
        # Lancement de la lecture dynamique
        threading.Thread(target=self.tail_log_file, daemon=True).start()

        # Lancement du traitement principal
        threading.Thread(target=self._run_update_process, daemon=True).start()


    def _run_update_process(self):
        try:
            # ---------------------- Loding Data via FTP ---------------------
            # fichiers_fournisseurs, fichiers_platforms = config_and_load_data_from_FTP()

            # ----------------------- Loding Local Data ----------------------
            fichiers_fournisseurs, fichiers_platforms = current_dataFiles()

            # ---------------------- Loding Data via FTP ---------------------
            valide_fichiers_fournisseurs, valide_fichiers_platforms = check_ready_files(fichiers_fournisseurs, fichiers_platforms)
                
            # ------------------- Mettre A Jour le stock ---------------------
            is_updated_store = mettre_a_jour_Stock(valide_fichiers_platforms, valide_fichiers_fournisseurs)

            if is_updated_store:

                messagebox.showinfo("Succès", "✅ La mise à jour a été effectuée avec succès.")
                logger.info('-- -- ✅ -- --  Mise à jour effectuée -- -- ✅ -- -- ')
                 
                # Bouton pour accéder au dossier mis à jour
                self.open_update_btn = ctk.CTkButton(
                    self.log_frame,
                    text="📂 Accéder aux fichiers mis à jour",
                    command=self.open_update_folder,
                    #**button_kwargs
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
        
            
        
        # Affichage progressif depuis le thread principal
    #    self.after(0, lambda: self.show_logs(dernier_fichier))
        
   
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
        label = ctk.CTkLabel(self.log_frame, text=line, anchor="w", text_color="white", font=("Segoe UI Emoji", 13))
        label.pack(anchor="w", pady=0, padx=2)


    
    def open_update_folder(self):
        dossier_mis_a_jour = "UPDATED_FILES"  # à adapter si ton dossier de sortie est différent

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

    
    def select_platform_file(self):
        file = filedialog.askopenfilename(title="Choisir le fichier Plateform", filetypes=[("Fichiers CSV", "*.csv")])
        if file:
            self.platform_file = file
            self.platform_file_label.configure(text=os.path.basename(file))

    def select_fournisseur_files(self):
        files = filedialog.askopenfilenames(title="Choisir les fichiers Fournisseurs", filetypes=[("Fichiers CSV", "*.csv")])
        if files:
            self.fournisseur_files = files
            display_names = ", ".join([os.path.basename(f) for f in files])
            self.fournisseurs_files_label.configure(text=display_names)

    def validate_update(self):
        messagebox.showinfo("Traitement", "Fonction de validation appelée.")

    
    def populate_list(self, container, items):
        #for item in items:
            # label = ctk.CTkLabel(container, text=f"🔹 {item}", anchor="w", height=25)
            # label.pack(anchor="w", padx=10, pady=2)
            # populate_list(self, container, items):
        for item in items:
            label = ctk.CTkLabel(
                container,
                text=f"🔹 {item}",
                anchor="w",
                height=25,
                font=ctk.CTkFont(size=13),
                wraplength=400  # empêche le débordement horizontal
            )
            label.pack(anchor="w", padx=10, pady=4)
    
    
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

    
    from dotenv import dotenv_values  # Assure-toi que c'est bien importé

    def load_ftp_infos(self):
        data = get_info_ftp_env(ENV_PATH)  # Tu peux aussi spécifier un path .env ici
        fournisseurs = []
        plateformes = []

        for nom_entite, infos in data.items():
            # exemple nom_entite: FOURNISSEUR_A
            label = f"{nom_entite} : {infos.get('host', 'inconnu')}"
            if nom_entite.startswith("FOURNISSEUR"):
                fournisseurs.append(label)
            elif nom_entite.startswith("PLATFORM"):
                plateformes.append(label)

        # Nettoie les anciennes entrées si besoin
        for widget in self.fournisseur_list.winfo_children():
            widget.destroy()
        for widget in self.plateform_list.winfo_children():
            widget.destroy()

        self.populate_list(self.fournisseur_list, fournisseurs)
        self.populate_list(self.plateform_list, plateformes)

    