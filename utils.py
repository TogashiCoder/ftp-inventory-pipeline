import os
import re
import sys
import yaml
import pandas as pd
import smtplib
import chardet

from pathlib import Path
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.logging_config import logger

from config.config_path_variables import YAML_ENCODING_SEP_FILE_PATH, YAML_REFERENCE_NAME, YAML_QUANTITY_NAME

# Charger les variables du fichier .env
load_dotenv()


# ------------------------------------------------------------------------------
#           Envoi d'une notification par email (Success / Failure)
# ------------------------------------------------------------------------------
def send_email_notification(subject: str, body: str, to_emails: list[str])-> None:
    from_email = os.getenv("EMAIL_ADDRESS") 
    password = os.getenv("EMAIL_PASSWORD")
    
    if not from_email or not password:
        logger.error("-- ❌ --  Email ou mot de passe non trouvés!")
        return  

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_emails 
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        # with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        # no need server.starttls() delete it
        with smtplib.SMTP("smtp.office365.com", 587) as server:
            server.starttls()
            server.login(from_email, password)
            server.send_message(msg)
        logger.info("📧 Email envoyé avec succès.")
    except Exception as e:
        logger.error(f"-- ❌ --  Erreur lors de l'envoi de l'email: {e}")


# ------------------------------------------------------------------------------
#                         Lecture d'un fichier YAML
# ------------------------------------------------------------------------------
def read_yaml_file(yaml_path: Path) -> dict:
    if not yaml_path.is_file():
        logger.error(f"-- ❌ --  Fichier introuvable : {yaml_path}")
        raise FileNotFoundError(f"Fichier introuvable : {yaml_path}")

    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if not isinstance(data, dict):
                logger.error("-- ❌ --  Le contenu YAML doit être un dictionnaire.")
                raise ValueError("Le fichier YAML ne contient pas un dictionnaire valide.")
            return data
    except yaml.YAMLError as e:
        logger.exception("-- ❌ --  Erreur de parsing YAML.")
        raise ValueError(f"Erreur de parsing YAML : {e}")
    except Exception as e:
        logger.exception("-- ❌ --  Erreur inattendue lors du chargement du fichier YAML.")
        raise ValueError("Erreur inattendue lors du chargement du fichier YAML.")


# ------------------------------------------------------------------------------
#                      Enregistrement d'un fichier DataFrame 
# ------------------------------------------------------------------------------
def save_file(file_name: str, df: pd.DataFrame, encoding: str = 'utf-8', sep: str= ',') -> pd.DataFrame:
    try:
        ext = Path(file_name).suffix.lower()
        if ext in {'.csv', '.txt'}:
            df.to_csv(file_name, encoding=encoding, sep=sep, index=False)
        elif ext in {'.xls', '.xlsx'}:
            df.to_excel(file_name, index=False)
        else:
            raise ValueError(f"Extension de fichier non supportée: {file_name}")
        
        logger.info(f"-- ✅ -- Fichier enregistré en : {file_name} - avec ({len(df)} lignes)")
        return df
    
    except Exception as e:
        logger.exception(f"-- ❌ -- Erreur lors de l'enregistrement de {file_name}: {e}")
        return pd.DataFrame()  # Retourne un DataFrame vide en cas d'erreur


# ------------------------------------------------------------------------
#                        Détection rapide de l'encodage
# ------------------------------------------------------------------------
def detect_encoding_fast(file_path: str, size_bytes: int = 2048) -> str:
    with open(file_path, 'rb') as f:
        raw_data = f.read(size_bytes)
        result = chardet.detect(raw_data)
    return result['encoding'] if result['encoding'] else 'utf-8'


# ------------------------------------------------------------------------
#               Vérification:  si le fichier n'a pas d'entête 
# ------------------------------------------------------------------------
def has_valid_header(df: pd.DataFrame) -> bool:
    col_names = list(df.columns)
    
    # Si les noms sont tous alphanumériques courts (ex: 'RAD', '000057'), suspect
    if all(isinstance(col, str) and (col.isupper() or col.isdigit() or col.strip().isnumeric()) for col in col_names):
        return False
    
    # Si tous les noms sont numériques ou Unnamed
    if all(str(col).startswith("Unnamed") or str(col).isdigit() for col in col_names):
        return False

    return True


# ------------------------------------------------------------------------
#     Lecture robuste de CSV avec test d'encodages/séparateurs & header
# ------------------------------------------------------------------------
def try_read_csv(file_path: str, sep: str, encoding: str, usecols=None) -> pd.DataFrame | None:
    try:
        temp_df = pd.read_csv(file_path, sep=sep, encoding=encoding, nrows=4)
        header_option = 0 if has_valid_header(temp_df) else None
        df = pd.read_csv(file_path, sep=sep, encoding=encoding, header=header_option, usecols=usecols)
        return df
    except Exception:
        return None


def read_csv_file_checking_encodings_sep(
    file_path: str,
    usecols=None,
    yaml_encoding_sep_path: Path = Path(YAML_ENCODING_SEP_FILE_PATH)
    ) -> tuple[pd.DataFrame, str, str]:
    
    yaml_info = read_yaml_file(yaml_encoding_sep_path)
    encodings, separators = yaml_info['encodings'], yaml_info['separators']

    # Test rapide avec chardet
    detected_encoding = detect_encoding_fast(file_path)

    for encoding in [detected_encoding] + encodings:
        for sep in separators:
            df = try_read_csv(file_path, sep, encoding, usecols)
            if df is not None and df.shape[1] >= 2:
                return df, encoding, sep

    logger.error("❌ Échec de lecture : aucun encodage ou séparateur ne fonctionne.")
    raise ValueError("Échec de lecture du fichier CSV.")


# ------------------------------------------------------------------------------
#                   Open Files of differents formats
# ------------------------------------------------------------------------------
def read_dataset_file(file_name: str, usecols=None) -> dict:
    logger.info(f"📥 Tentative de lecture du fichier : {file_name}  ...")

    try:
        ext = Path(file_name).suffix.lower()
        if ext in {'.csv', '.txt'}:
            df,  encoding, sep = read_csv_file_checking_encodings_sep(file_name, usecols=usecols, yaml_encoding_sep_path=YAML_ENCODING_SEP_FILE_PATH)
            logger.info(f"📄 Fichier lu : {file_name} -- avec ({len(df)} lignes)")
            return {'dataset':df, 'encoding':encoding, 'sep':sep}
        
        elif ext in {'.xls', '.xlsx'}:
            #df = pd.read_excel(file_name, usecols=usecols)
            temp_df = pd.read_excel(file_name,  nrows=4,  header=0)
            header_option = 0 if has_valid_header(temp_df) else None
            df = pd.read_excel(file_name, header=header_option, usecols=usecols)
            logger.info(f"📄 Fichier lu : {file_name} -- avec ({len(df)} lignes)")
            return {'dataset':df, 'encoding':'', 'sep':''}
       
        else:
            raise ValueError(f"Extension de fichier non supportée: {file_name}")
    except Exception as e:
        logger.error(f"-- ❌ --  Erreur lors de la lecture de {file_name}: {e}")
        return {'dataset':pd.DataFrame(), 'encoding':'', 'sep':''}  # Retourne un DataFrame vide en cas d'erreur


# ------------------------------------------------------------------------------
#                       Adapter les chemins pour .exe
# ------------------------------------------------------------------------------
def get_resource_path(relative_path: str) -> str:    # used for creating .exe (managing paths)
    try:
        # PyInstaller crée un dossier temporaire _MEIxxx
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# ------------------------------------------------------------------------------
#          Remove >= from Stock & change 'AVAILABLE' by 3 & 'N/A', -1 by 0
# ------------------------------------------------------------------------------
def process_stock_value(value):
    """Nettoie et convertit une valeur de stock en entier."""

    # Convertir en chaîne propre
    value = str(value).strip().upper()

    # Cas spéciaux
    if value == "AVAILABLE":
        return 3
    if value in ["N/A", "", "NONE"]:
        return 0

    # Supprimer les symboles ambigus
    value = re.sub(r"[<>~=±≃≅]", "", value)

    # Remplacer les virgules par des points (12,5 → 12.5)
    value = value.replace(",", ".")     

    # Gérer les valeurs négatives explicites        
    if value.startswith('-'):
        value = 0
    
    # Essayer de convertir proprement float → int
    try:
        int_value = int(float(value))
        return max(int_value, 0)
    except ValueError:
        pass

    # En dernier recours : extraire tous les chiffres
    cleaned_value = re.sub(r"[^0-9]", "", value)
    if not cleaned_value:
        return 0

    try:
        int_value = int(cleaned_value)
        return max(int_value, 0)
    except ValueError:
        return 0


# ------------------------------------------------------------------------------
#         Remove spaces before/after '='  + avoid '' or "" in the env file
# ------------------------------------------------------------------------------
def clean_env_file(path_env):
    '''
    replace .env after cleaning
    '''
    print('path_env', path_env)
    with open(path_env, "r") as f:
        lines = f.readlines()

    cleaned_lines = []
    for line in lines:
        if "=" in line:
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            cleaned_lines.append(f"{key}={value}\n")
        else:
            cleaned_lines.append(line)

    with open(path_env, "w") as f:
        f.writelines(cleaned_lines)
