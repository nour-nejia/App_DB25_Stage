import tkinter as tk
from tkinter import ttk
import customtkinter as ctk 
import pandas as pd
from Parsing import Control_Parsing 
from SearchByDID import Control
from ExtractBlob import ControlExtract


ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")  

# Fenêtre principale
root = ctk.CTk()
root.title("DB25 - Analyseur de fichiers BLOB")
root.update_idletasks()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{screen_width}x{screen_height}+0+0")

# Cadre principal
main_frame = ctk.CTkFrame(root, corner_radius=25, fg_color="#E6F0FA")  
main_frame.pack(fill="both", expand=True)

# Barre latérale
sidebar = ctk.CTkFrame(main_frame, width=220, corner_radius=15, fg_color="#C3DDFE")  
sidebar.pack(side="left", fill="y", padx=(25, 0), pady=25)

# Contenu principal
center_frame = ctk.CTkFrame(main_frame, corner_radius=20, fg_color="#F4F9FF")  
center_frame.pack(side="left", fill="both", expand=True, padx=25, pady=25)

# Titre
welcome_label = ctk.CTkLabel(
    center_frame,
    text="Bienvenue dans notre application DB25 :) ",
    font=ctk.CTkFont(size=20, weight="bold"),
    text_color="#12486B"
)
welcome_label.pack(pady=(60, 30))

# Zone d'affichage des résultats
result_text = ctk.CTkTextbox(center_frame, height=250, font=("Consolas", 14), wrap="word")
result_text.pack(fill="both", expand=True, padx=40, pady=(0, 30))
result_text.insert("end", "\nRésultats et messages s'afficheront ici...")
result_text.configure(state="disabled")

# fonction pour afficher les résultats
def show_result(msg):
    # supprimer le tableau si j'ai fait le parsing deja
    for widget in center_frame.winfo_children():
        if isinstance(widget, tk.Canvas) or isinstance(widget, tk.Scrollbar):
            widget.destroy()
    # Recréer le champ de texte si nécessaire
    if not any(isinstance(widget, ctk.CTkTextbox) for widget in center_frame.winfo_children()):
        global result_text
        result_text = ctk.CTkTextbox(center_frame, height=250, font=("Consolas", 14), wrap="word")
        result_text.pack(fill="both", expand=True, padx=40, pady=(0, 30))
    result_text.configure(state="normal")
    result_text.delete("1.0", "end")
    result_text.insert("end", msg)
    result_text.configure(state="disabled")

# Boutons
btn_style = {
    "font": ctk.CTkFont(size=16),
    "fg_color": "#005C99",
    "hover_color": "#007ACC",
    "text_color": "white",
    "corner_radius": 12,
    "height": 45
}

#fonction pour afficher le tableau
def show_dataframe(df):
    # supprimer le champs de texte
    for widget in center_frame.winfo_children():
        if isinstance(widget, ctk.CTkTextbox):
            widget.pack_forget()
            widget.destroy()

    # Supprimer le tableau/canvas si présent
    for widget in center_frame.winfo_children():
        if isinstance(widget, tk.Canvas) or isinstance(widget, ctk.CTkScrollableFrame):
            widget.pack_forget()
            widget.destroy()

    # Créer canvas et les glisseurs
    canvas_width = 900
    column_width = 120
    num_columns = len(df.columns)
    table_width = column_width * num_columns
    canvas = tk.Canvas(center_frame, bg="#F4F9FF")
    h_scroll = tk.Scrollbar(center_frame, orient="horizontal", command=canvas.xview)
    v_scroll = tk.Scrollbar(center_frame, orient="vertical", command=canvas.yview)
    h_scroll.pack(side="top", fill="x")
    v_scroll.pack(side="right", fill="y")
    canvas.pack(fill="both", expand=True)
    canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)

    # Définir la largeur du cadre du tableau pour s'adapter à toutes les colonnes
    table_frame = tk.Frame(canvas, bg="#F4F9FF", width=table_width)
    table_frame.pack_propagate(False)
    window_id = canvas.create_window((0, 0), window=table_frame, anchor="nw")

    # Mettre à jour la région de défilement chaque fois que la taille du tableau change
    def resize_canvas(event):
        canvas.config(scrollregion=canvas.bbox("all"))
    table_frame.bind("<Configure>", resize_canvas)

    # Ajouter les noms des colonnes
    for col_idx, col_name in enumerate(df.columns):
        header = tk.Label(table_frame, text=col_name, font=("Arial", 12, "bold"), bg="#D9EAF7")
        header.grid(row=0, column=col_idx, padx=2, pady=2, sticky="nsew")

    # Ajouter les lignes de données
    for row_idx, row in enumerate(df.values, start=1):
        for col_idx, value in enumerate(row):
            cell = tk.Label(table_frame, text=str(value), font=("Arial", 11), bg="#F4F9FF")
            cell.grid(row=row_idx, column=col_idx, padx=2, pady=2, sticky="nsew")

    # mise à jour de tableau 
    table_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

btn1 = ctk.CTkButton(sidebar, text="Parsing du fichier BLOB", command=lambda: Control_Parsing(show_result, show_dataframe), **btn_style)
btn1.pack(pady=(30, 20), padx=20, fill="x")

btn2= ctk.CTkButton(sidebar, text="Recherche par DID", command=lambda: Control(show_result), **btn_style)
btn2.pack(pady=20, padx=20, fill="x")

btn3 = ctk.CTkButton(sidebar, text="Extraction BLOB depuis BDD", command=lambda: ControlExtract(show_result), **btn_style)
btn3.pack(pady=20, padx=20, fill="x")

# Bouton d'aide
help_btn = ctk.CTkButton(
    sidebar,
    text="Besoin d'aide ?",
    font=ctk.CTkFont(size=15, weight="bold"),
    fg_color="#B8D8F2",       
    text_color="#003B73",      
    hover_color="#A2CBE8",
    corner_radius=12,
    height=40,
    command=lambda: tk.messagebox.showinfo(
        "Contact",
        "Veuillez nous contacter via mail : DB25.contact@gmail.com\nou via notre numéro : 71230230"
    )
)
help_btn.pack(pady=(50, 10), padx=20, fill="x")
