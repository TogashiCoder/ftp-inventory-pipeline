import os

from utils import *
from ftplib import FTP
from dotenv import dotenv_values
from functions.functions_FTP import *
from config.logging_config import logger
from config.config_path_variables import *

# ----------------------------------------------------------------------
#            Lire les info de l'FTP stockées en fichier .env
# ----------------------------------------------------------------------
def get_info_ftp_env(path_env=ENV_PATH):
    '''
    return: 
        data:  {'FOURNISSEUR_A': {'host': 'ftp.platform-a.com', 'user': 'user_a', 'password': 'pass_a'}, 
                'FOURNISSEUR_B': {...},
                'PLATFORM_A': {'host': 'ftp.platform-a.com', 'user': 'user_a', 'password': 'pass_a'}, 
                'PLATFORM_B': {...},
                ...
                }
    '''
    clean_env_file(path_env)  # Appel du nettoyage

    env_vars = dotenv_values(path_env)
    
    data = {}
    erreurs = []

    for key, value in env_vars.items():
        if key.startswith("FTP_"):
            parts = key.split("_")  # ex: FTP_HOST_FOURNISSEUR_A → ['FTP', 'HOST', 'FOURNISSEUR', 'A']
            if len(parts) < 4:
                continue

            champ = parts[1].lower()      # host, user, password

            type_entite = parts[2]        # FOURNISSEUR ou PLATFORM
            nom_entite = parts[3]         # A, B, etc.

            nom_complet = f"{type_entite.upper()}_{nom_entite.upper()}"


            if nom_complet not in data:
                data[nom_complet] = {}

            data[nom_complet][champ] = value

    # Vérification des champs manquants
    for nom, creds in data.items():
        manquants = [k for k in ["host", "user", "password"] if k not in creds or not creds[k]]
        if manquants:
            erreurs.append(f"-- ❌ --  {nom} → champs manquants ou vides : {manquants}")

    # Affichage des erreurs
    for err in erreurs:
        logger.error(err)

    return data


def separer_fournisseurs_et_plateformes(data_env):
    """
    Sépare le dictionnaire data_env en deux dictionnaires :
    - clés commençant par "FOURNISSEUR"
    - clés commençant par "PLATFORM"
    
    Args:
        data_env: dict contenant fournisseurs et plateformes.
        :
            {'FOURNISSEUR_A': {'host': 'ftp.platform-a.com', 'user': 'user_a', 'password': 'pass_a'}, 
             'FOURNISSEUR_B': {...},
             'PLATFORM_A': {'host': 'ftp.platform-a.com', 'user': 'user_a', 'password': 'pass_a'}, 
             'PLATFORM_B': {...},
             ...
            }
    Returns:
        tuple (fournisseurs, plateformes)
              liste_fournisseurs = ['FOURNISSEUR_A', 'FOURNISSEUR_B', ...]
              liste_plateformes = ['PLATFORM_A', 'PLATFORM_B', ...]
        
    """
    fournisseurs = {k: v for k, v in data_env.items() if k.startswith("FOURNISSEUR")}
    plateformes = {k: v for k, v in data_env.items() if k.startswith("PLATFORM")}
    return fournisseurs, plateformes


# ------------------------------------------------------------------------------
#          Only file that column Ref & Qte are identified in yaml file
# ------------------------------------------------------------------------------
def keep_data_with_header_specified(list_fichiers, yaml_with_header_items):
    '''
    list_fichiers ==> dict('FOURNISSEUR_A': chemin fichierA , 'FOURNISSEUR_B': chemin fichierB,... )

    Args:
        list_fichiers: Dictionnaire {fournisseur: chemin_fichier}.
        yaml_with_header_items: Chemin vers fichier YAML contenant les headers requis.

    Returns:
        Dict avec fournisseurs valides et info associée:
        { fournisseur: {
              'chemin_fichier': str,
              YAML_REFERENCE_NAME: str,
              YAML_QUANTITY_NAME: str
          }, ...
        }
    '''
    header_data = read_yaml_file(yaml_with_header_items)
    
    # Dictionnaire des fournisseurs/platformes valides
    items_valides = {}              # will keep only files that are loaded from ftp (or manually) & that their id & qte cols are specified in yaml file

    for item, chemin in list_fichiers.items():
        if item not in header_data:
            logger.exception(f"-- ⚠️ --  {item} non trouvé dans le YAML ")
            continue

        # Vérifier les champs requis
        info = header_data[item]
        nom_ref = info.get(YAML_REFERENCE_NAME, '')
        qte_stock = info.get(YAML_QUANTITY_NAME, '')

        if nom_ref is None or nom_ref == "" or qte_stock is None or qte_stock == "":
            logger.error(f"-- ⚠️ --  {item} est défini dans le YAML mais contient un champ vide :")
            if nom_ref is None or nom_ref == "":
                logger.error(f"     - le nom de column pour 'nom_reference' est vide ")
            if qte_stock is None or qte_stock == "":
                logger.error(f"     - le nom de column pour 'quantite_stock' est vide")
            continue

        # Ajouter à la liste des valides
        items_valides[item] = {
            'chemin_fichier': chemin,
            YAML_REFERENCE_NAME: nom_ref,
            YAML_QUANTITY_NAME: qte_stock
        }

    return items_valides


# ------------------------------------------------------------------------------
#                       Si les fichiers existent vraiment
# ------------------------------------------------------------------------------
def verifier_fichiers_existent(list_files):
    item_valides = {}
    
    for item_file, infos in list_files.items():
        chemin = infos.get("chemin_fichier")
        if chemin and os.path.isfile(chemin):
            item_valides[item_file] = infos
        else:
            logger.error(f"-- ⚠️ --  Fichier introuvable pour {item_file} → '{chemin}' → supprimé.")
    
    return item_valides
