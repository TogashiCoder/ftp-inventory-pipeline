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
# Remove get_info_ftp_env and separer_fournisseurs_et_plateformes


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


def check_ready_files(title_files, downloaded_files, yaml_with_header_items, report_gen=None):
    logger.info(f'------------ Vérifiez si tous les fichiers {title_files} sont prêts--------------')
    files_with_header = keep_data_with_header_specified(downloaded_files, yaml_with_header_items)
    files_valides = verifier_fichiers_existent(files_with_header)
    if len(files_valides) > 0:
        logger.info(f'{len(files_valides)} fichiers sont prêts')
    else:
        logger.info(f'Aucun fichier trouvé')
        if report_gen:
            report_gen.add_warning(f"Aucun fichier trouvé pour {title_files}")
    # Log missing columns or files
    for key, data in files_with_header.items():
        if key not in files_valides:
            if report_gen:
                report_gen.add_warning(f"Fichier manquant ou colonnes non conformes: {key}")
    logger.info('---------------------------------------------------------------')
    return files_valides
