#import des bib 
from lxml import etree as ET
import re
from tkinter import filedialog, messagebox
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

# fonction pour extraire les infos de la section requests( DID et Ref ) 
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
                            did = m.group(1)[-4:]
                    return ref, did
    # Valeurs par défaut 
    return '-', '-'

# extraire les infos dans la section datas du fichier blob 
def get_data_info(data):
    # Vérifier si l'élément de données est None (n'existe pas)
    if data is None:
        # si la section datas n'existe pas : Retourner un dictionnaire avec des valeurs par défaut pour tous les champs
        return {
            'DataName': '-',
            'Comment': '-',
            'Length': '-',
            'Scaled Unit': '-',
            'Step': '-',
            'Offset': '-',
            'Values': '-'
        }
    # Etraire l'attribut Name
    name = data.attrib.get('Name', '-')
    # Extraire le commentaire
    comment = data.findtext('Comment', '-')
    comment=comment.replace('\xa0', ' ')
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
        'DataName': name,
        'Comment': comment.replace('\xa0', ' '),
        'Length': length,
        'Scaled Unit': scaled_unit,
        'Step': step,
        'Offset': offset,
        # choisir le séparateur pour les valeurs, ici on utilise un point-virgule
        'Values': "; ".join(values) if values else '-'
    }

#fonction qui retourne la section data correspondant à un DID donné
def get_databyDID(DID,datas,requests):
    while True:
        if datas is not None:
            for data in datas.findall('Data'):
                ref,did=get_request_info(requests, data.attrib.get('Name', '-'))
                if did==DID:
                    return data
        return None

#fonction qui retourne le résultat final sous forme de json 
def getAll(data,requests,configs):
    result = []
    info = get_data_info(data)
        # mtc est la valeur dans Config
    mtc = get_config_info(configs, info['DataName'])
        # ref et did se trouvent dans la section requests
    ref, did = get_request_info(requests, info['DataName'])
        # Ajouter les informations dans le résultat
    result.append({
            'DID': did,
            'DataName': info['DataName'],
            'Comment': info['Comment'],
            'Length': info['Length'],
            'Scaled Unit': info['Scaled Unit'],
            'Step': info['Step'],
            'Offset': info['Offset'],
            'Values': info['Values'],
            'MTC': mtc,
            'Ref': ref,
           })
    return result

#fonction permettant de choisir un DID selon un format précis et retourne la liste des DID
def choose_DID():
    while True:
        dialog = ctk.CTkInputDialog(text="DID = 4 chiffres hexadécimaux et si vous allez choisir plusieurs DID respecter ce format : DID_DID.._DID" , title="Recherche par DID")
        did = dialog.get_input()
        if did is None:  
            return None
        did_list=did.split('_')
        if all(re.fullmatch(r"[0-9A-Fa-f]{4}", d) for d in did_list):
            return did_list
        else:
            messagebox.showerror("Format incorrect", message="Veuillez respecter le format indiqué : un DID= 4 chiffres hexadécimaux (ex: 1A2B) et si vous allez choisir plusieurs DID respecter ce format : DID_DID.._DID ")

#analyse du fichier xml 
def process_xml(xml_file):
    # try-except pour gérer les erreurs lors du traitement du fichier XML
    try:
        global datas, requests, configs
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
    # traitement si une exception ( quelque soit son type ) est levée
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
        global DID_LIST
        DID_LIST = choose_DID()

# fonction de contrôle de tout 
def Control (show_result):
    select_file()
    if DID_LIST is None:
        show_result("Vous n'avez saisi aucun DID")
        return
    else:
        ch = ""
        for DID in DID_LIST:
            data = get_databyDID(DID, datas, requests)
            if data is None:
                ch += f"Le DID {DID} n'a pas été trouvé dans le fichier."+"\n"+"\n"
            else:
                result=getAll(data, requests, configs)
                for d in result:
                    ch +="{"
                    for clef, valeur in d.items():
                        ch += f"{clef}: {valeur}\n"
                    ch += "}" + "\n" + "\n" 
        show_result(ch)

