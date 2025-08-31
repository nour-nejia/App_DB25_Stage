# import des bibliothèques nécessaires
from logging import root
from lxml import etree as ET
import re
import pandas as pd
from tkinter import filedialog, messagebox
from customtkinter import CTkInputDialog
import customtkinter as ctk

#extraire les infos contenus dans la section config du fichier xml 
def get_config_info(configs, data_name):
    #verfier si la section configs existe et retourner les valeurs par défaut si elle n'existe pas
    if configs is None:
        return '-', '-'
    # boucle de chaque élement config dans la section configs
    for config in configs.findall('Config'):
        #chercher l'elemnet courant en parametre de get config info 
        if config.attrib.get('DiagItem') == data_name:
            option = config.find('Option')
            # extraire le champs MTC
            mtc = option.attrib.get('MTC', '-') if option is not None else '-'
            return  mtc
    # valeur par défaut 
    return '-'

# fonction pour extraire les infos de la section requests( DID et Ref ) du fichier xml 
def get_request_info(requests, data_name):
    # vérifier si la section requests existe sinon retourner les valeurs par defaut
    if requests is None:
        return '-', '-'
    # boucle de chaque element request de la section requests 
    for req in requests.findall('Request'):
        # chercher la balise received courante
        received = req.find('Received')
        # verifie l'existence de received
        if received is not None:
            # boucle à travers chaque élément DataItem dans la section received
            for dataitem in received.findall('DataItem'):
                #verifie si l'element en cours est le même que celui en paramètres
                if dataitem.attrib.get('Name') == data_name:
                    # extraire l'attribut Ref
                    ref = dataitem.attrib.get('Ref', '-')
                    # chercher la balise sent 
                    sent = req.find('Sent')
                    # did initialisé à -
                    did = '-'
                    # verifier l'existence de la balise sent
                    if sent is not None:
                        # Extraire le contenu textuel de l'élément SentBytes, utiliser une chaîne vide par défaut
                        sentbytes = sent.findtext('SentBytes', '')
                        # expression général de texte dans balise sent est 22 puis 4 caracteres hexadécimales
                        m = re.match(r'22([0-9A-Fa-f]{4,})', sentbytes)
                        # verifier l'existence de correspondance du format 
                        if m:
                            # extraire les 4 derniers caractères car ils sont le DID 
                            did = m.group(1)[-4:]
                    # retourner Ref et le DID 
                    return ref, did
    # Valeurs par défaut 
    return '-', '-'

# extraire les infos dans la section datas du fichier xml 
def get_data_info(data):
    # Vérifier si l'élément de données est None (n'existe pas)
    if data is None:
        # si la section datas n'existe pas : Retourner un dictionnaire avec des valeurs par défaut pour tous les champs
        return {
            'dataname': '-',
            'comment': '-',
            'length': '-',
            'scaled_unit': '-',
            'step': '-',
            'offset': '-',
            'values': '-'
        }
    # Etraire l'attribut Name
    name = data.attrib.get('Name', '-')
    # Extraire le commentaire
    comment = data.findtext('Comment', '-')
    # extraire la balise Bits
    bits = data.find('Bits')
    #extraire le champs count de bits
    length = bits.attrib.get('count', '-') if bits is not None and 'count' in bits.attrib else '-'
    # initialiser 
    scaled_unit = step = offset = '-'
    # initialiser le liste de values à vide ( cest le champs values dans le tableau final )
    values = []
    # verifie que bits existe 
    if bits is not None:
        # recuperer l'element scaled 
        scaled = bits.find('Scaled')
        if scaled is not None:
            # Extraire l'attribut Unit de l'élément scaled, utiliser '-' par défaut s'il n'est pas trouvé
            scaled_unit = scaled.attrib.get('Unit', '-')
            # Extraire l'attribut Step de l'élément scaled, utiliser '-' par défaut s'il n'est pas trouvé
            step = scaled.attrib.get('Step', '-')
            # Extraire l'attribut Offset de l'élément scaled, utiliser '-' par défaut s'il n'est pas trouvé
            offset = scaled.attrib.get('Offset', '-')
#chercher l'element list s'il existe 
        lst = bits.find('List')
        if lst is not None:
            # boucle pour la liste des items dans la section list
            for item in lst.findall('Item'):
                # Extraire l'attribut Value de l'élément item, utiliser '-' par défaut si non trouvé
                val = item.attrib.get('Value', '-')
                # Extraire l'attribut Text de l'élément item, utiliser '-' par défaut si non trouvé
                txt = item.attrib.get('Text', '-')
                # Ajouter la valeur et le texte formaté dans la liste values
                values.append(f"{val} ({txt})")
    # Retourner un dictionnaire avec toutes les informations extraites
    return {
        'dataname': name,
        'comment': comment,
        'length': length,
        'scaled_unit': scaled_unit,
        'step': step,
        'offset': offset,
        # choisir le séparateur pour les valeurs, ici on utilise un point-virgule
        'values': "; ".join(values) if values else '-'
    }

#la fonction qui controle le parsing dans la GUI 
def Parsing_Main (datas, configs, requests):
    columns = ["N°", "DataName", "DID", "Ref", "Comment", "MTC", "Length", "Scaled Unit", "Step", "Offset", "Values"]
    rows = []
    #message d'erreur si la section datas n'existe pas et sortie de la fonction export to excel
    if datas is None:
        messagebox.showerror("Error", "Choose a DDT2000 BLOB file") # en fait tout fichier BLOB ddt2000 contient sections datas pour ceci ce message d'erreur est convenable
        return
    # initialiser la numérotation
    idx = 1
    # boucle pour parcourir tous les paramètres existants ( tous les datas)
    for data in datas.findall('Data'):
        #info contient la liste des infos dans la section data
        info = get_data_info(data)
        # mtc est la valeur dans Config
        mtc = get_config_info(configs, info['dataname'])
        # ref et did se trouvent dans la section requests
        ref, did = get_request_info(requests, info['dataname'])
        # remplissage d'une ligne avec les infos extraites
        row = [
            idx,                    # numéro de ligne
            info['dataname'],       # nom du paramètre
            did,                    # DID du paramètre
            ref,                    # référence de la requête
            info['comment'],        # Commentaire 
            mtc,                    # MTC de la configuration
            info['length'],         # Longueur des bits de données
            info['scaled_unit'],    # Unité de mesure du paramètre
            info['step'],           # Pas de mise à l'échelle 
            info['offset'],         # Décalage 
            info['values']          # Valeurs énumérées et le texte correpondant
        ]
        # ajouter la ligne à la liste des lignes
        rows.append(row)
        # Incrémenter le compteur de lignes
        idx += 1    
    # Vérifier si des lignes de données ont été créées(rows n'est pas vide)
    if not rows:
        # Afficher un message d'erreur si aucune entrée Data n'a été trouvée et sortir de la fonction ( bonne pratique pour ne pas creer un fichier excel vide ) 
        messagebox.showerror("Aucune donnée trouvée", "Le fichier XML ne contient aucun paramètre à extraire.\n\nVérifiez que votre fichier contient des éléments <Data> dans la section <Datas>.")
        return
    df = pd.DataFrame(rows, columns=columns)
    return df

# fonction pour l'export en excel du résultat de parsing
def export_to_excel(datas, configs, requests, excel_path):
    # definir l'entete du fichier excel les différents champs de colonnes 
    header = [
        "N°", "DataName", "DID", "Ref", "Comment",
        "MTC", "Length", "Scaled Unit", "Step", "Offset", "Values"
    ]
    # liste pour stocker les lignes de données extraites , initilaisée vide 
    rows = []
    #message d'erreur si la section datas n'existe pas et sortie de la fonction export to excel
    # initialiser la numérotation
    idx = 1
    # boucle pour parcourir tous les paramètres existants ( tous les datas)
    for data in datas.findall('Data'):
        #info contient la liste des infos dans la section data
        info = get_data_info(data)
        # mtc est la valeur dans Config
        mtc = get_config_info(configs, info['dataname'])
        # ref et did se trouvent dans la section requests
        ref, did = get_request_info(requests, info['dataname'])
        # remplissage d'une ligne avec les infos extraites
        row = [
            idx,                  
            info['dataname'],       
            did,                    
            ref,                    
            info['comment'],       
            mtc,                    
            info['length'],         
            info['scaled_unit'],    
            info['step'],           
            info['offset'],         
            info['values']          
        ]
        # ajouter la ligne à la liste des lignes
        rows.append(row)
        # Incrémenter le compteur de lignes
        idx += 1    
    # Vérifier si des lignes de données ont été créées(rows n'est pas vide)
    if not rows:
        # Afficher un message d'erreur si aucune entrée Data n'a été trouvée et sortir de la fonction ( bonne pratique pour ne pas creer un fichier excel vide ) 
        messagebox.showerror("Aucune donnée trouvée", "Le fichier XML ne contient aucun paramètre à extraire.\n\nVérifiez que votre fichier contient des éléments <Data> dans la section <Datas>.")
        return

    # creation d'un tableau avec les nom du colonnes deja definies et le contenu de rows deja créé
    df = pd.DataFrame(rows, columns=header)
    # Export du tableau vers excel et en inhibtant la numérotation de lignes de ce fait on aura une numerotation valide car on lui a créé une colonne special ( N°)
    df.to_excel(excel_path, index=False)
    # afficher un message de succès avec le chemin du fichier Excel créé
    messagebox.showinfo("Success", f"Félicitations ;) table exportée vers :\n{excel_path}")

# fonction pour traiter le fichier XML et extraire les données et l'enregistrement dans un emplacement 
def process_xml(xml_file):
    # try-except pour gérer les erreurs lors du traitement du fichier XML
    try:
        global datas, configs, requests
        #recupere la structure xml entière dans la variable tree  
        tree = ET.parse(xml_file)
        # recuperer l'element racine de l'arbre XML qui contient tooutes les autres sections comme configs , datas et requests
        root = tree.getroot()
        # recuperer la section Configs du fichier xml 
        configs = root.find('Configs')
        # recuperer la section Datas du fichier xml
        datas = root.find('Datas')
        # recuperer la section Requests du fichier xml
        requests = root.find('Requests')
        # Ouvrir une boîte de dialogue pour permettre à l'utilisateur de choisir où enregistrer le fichier Excel qui sera créé ,asksaveasfilename est la fonction qui permet d'ouvrir la boite d'enregister sous 
    except Exception as e:
        # message d'erreur
        messagebox.showerror("Error", f"Erreur lors du traitement du fichier\n{e}")

# fonction pour sélectionner un fichier XML
def select_file():
    # Ouvrir une boîte de dialogue pour permettre à l'utilisateur de choisir un fichier XML
    xml_file = filedialog.askopenfilename(
        filetypes=[("XML files", "*.xml")],  # Filtre de type de fichier pour n'afficher que les fichiers XML
        title="Choisir le fichier BLOB"      # Titre de la boîte de dialogue
    )
    # Vérifier si l'utilisateur a sélectionné un fichier (n'a pas annulé la boîte de dialogue)
    if xml_file:
        # Appeler la fonction process_xml avec le fichier sélectionné
        process_xml(xml_file)

#la fonction qui permet le control du parsing 
def Control_Parsing(show_result, show_dataframe):
    select_file()
    while True:
        dialog = CTkInputDialog(text="Voulez-vous exporter les données vers un fichier Excel ? répondez par OUI ou NON", title="Mode d'exportation")
        response = dialog.get_input()
        if response is None:  # User cancelled
            show_result("choisir l'option du résultat")
            return
        if response.upper() == "OUI" or response.upper() == "NON":
            break
        else:
            messagebox.showerror("Format incorrect", message="Veuillez répondre par OUI ou NON")
    if response.upper() == "OUI":
         excel_path = filedialog.asksaveasfilename( #la fonction asksavefilename retourne soit un champs vide soit un emplacement
            defaultextension=".xlsx",           # extension par defaut du fichier excel 
            filetypes=[("Fichiers Excel", "*.xlsx")],  # filtrer les fichiers qui appariteront ici on gardera seulement les fichiers excel 
            title="Enregistrer le fichier excel sous " # titre de la fenetre d'enregistrement
        )
         if excel_path: #verifie si le user a choisi un emplacement valide 
            #appel de la fonction d'export vers excel 
            export_to_excel(datas, configs, requests, excel_path)
    df = Parsing_Main(datas, configs, requests)
    show_dataframe(df)