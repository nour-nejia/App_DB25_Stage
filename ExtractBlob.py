#IMPORT DES BIB 
from lxml import etree as ET
import re
from tkinter import filedialog, messagebox
import customtkinter as ctk

#fonction qui retourne la liste des blobs (DID et Name)
def getBLOBInfo(requests):
    result=[]
    if requests is not None:
        for req in requests:
          ns = req.tag.split('}')[0] + '}' if '}' in req.tag else ''
          if req.tag.endswith('Request'):
            BLOB = req.find(f'{ns}Blob')
            received = req.find(f'{ns}Received')
            if BLOB is not None:
            # boucle à travers chaque élément DataItem dans la section received
              if received is not None:
                for dataitem in received.findall(f'{ns}DataItem'):
                  sent = req.find(f'{ns}Sent')
                  name = dataitem.attrib.get('Name', '-')
                  did = '-'
                    # verifier l'existence de la balise sent
                  if sent is not None:
                      sentbytes = sent.findtext(f'{ns}SentBytes', '')
                      m = re.match(r'22([0-9A-Fa-f]{4,})', sentbytes)
                        # verifier l'existence de correspondance du format 
                      if m:
                         did = m.group(1)[-4:]
              dict = {"Name": name, "DID": did}
              result.append(dict)
            else:
              continue
    return result

# fonction pour analyser le fichier XML
def process_xml(xml_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        # Recherche toutes les balises, peu importe la profondeur, la casse ou le namespace
        global requests
        requests = None
        for elem in root.iter():
            if elem.tag.lower().endswith('requests'):
                requests = elem
                break
        if requests is None:
            messagebox.showerror("Erreur", "section Requests not found in xml")
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors du traitement du fichier\n{e}")

# fonction pour sélectionner un fichier XML
def select_file():
    # Ouvrir une boîte de dialogue pour permettre à l'utilisateur de choisir un fichier XML
    xml_file = filedialog.askopenfilename(
        filetypes=[("XML files", "*.xml")],  # Filtre de type de fichier pour n'afficher que les fichiers XML
        title="Choisir la base de données de l'ECU"      # Titre de la boîte de dialogue
    )
    # Vérifier si l'utilisateur a sélectionné un fichier (n'a pas annulé la boîte de dialogue)
    if xml_file:
        # Appeler la fonction process_xml avec le fichier sélectionné
        process_xml(xml_file)

# fonction de contrôle de tout
def ControlExtract(show_result):
    select_file()
    result = getBLOBInfo(requests)
    if result == []:
      print("result vide")
      show_result("Aucun BLOB trouvé dans le fichier.")
    else:
      ch="Le nombre de paramètres de type BLOB est " + str(len(result)) + "\n" +"\n" + "Les paramètres de type BLOB existants sont:"+ "\n" 
      i=1
      for d in result:
          ch += str(i) + ") "+ "{ " f"Nom: {d['Name']} ;  DID: {d['DID']}" + " }\n"
          i += 1
      show_result(ch)

