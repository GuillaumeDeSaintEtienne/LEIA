import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
from datetime import datetime
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Liste pour stocker les conversations
conversations = {}

# Création de la fenêtre principale
fenetre = ttk.Window(themename="cosmo")  # Thème plus doux et moderne
fenetre.title("Chat LEIA")

# Définition des couleurs
couleur_fond = "#150d25"  # Fond clair et doux
couleur_texte = "#2d3e50"  # Texte foncé mais pas noir
couleur_accent = "#6c7a89"  # Accent doux/neutre

fenetre.configure(bg=couleur_fond)

style = ttk.Style()
style.configure("Custom.TFrame", background=couleur_fond)
style.configure("TLabel", background=couleur_fond, foreground=couleur_texte)
style.configure("TButton", font=("Arial", 11))
style.configure("TEntry", font=("Arial", 12))

# Frame principal
frame = ttk.Frame(fenetre, style="Custom.TFrame")
frame.pack(side="right", padx=20, pady=20)

# Historique des conversations
frame_historique = ttk.Frame(fenetre, style="Custom.TFrame")
frame_historique.pack(side="left", fill="y", padx=20, pady=20)

label_historique = ttk.Label(frame_historique, text="Conversations", font=("Helvetica", 14, "bold"), bootstyle="secondary", background=couleur_fond)
label_historique.pack(pady=10)

liste_conversations = tk.Listbox(frame_historique, height=15, bg="#f8f9fa", fg=couleur_texte, 
                                font=("Helvetica", 11), relief="flat", borderwidth=1, 
                                highlightbackground="#d6dce4", selectbackground="#b3c2d1")
liste_conversations.pack(fill="y", expand=True, padx=5, pady=5)
liste_conversations.bind("<<ListboxSelect>>", lambda e: afficher_conversation(liste_conversations.get(liste_conversations.curselection())) if liste_conversations.curselection() else None)

# Chargement du modèle
model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# Variables de stats
stats_conversations = {}

def analyseConv(text):
    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        predicted_class = torch.argmax(logits).item() + 1

    if predicted_class == 1:
        stats_conversations[current_conversation]['neg'] += 1
        return "Vraiment négatif"
    elif predicted_class == 2:
        stats_conversations[current_conversation]['neg'] += 1
        return "Négatif"
    elif predicted_class == 3:
        stats_conversations[current_conversation]['neu'] += 1
        return "Neutre"
    elif predicted_class == 4:
        stats_conversations[current_conversation]['pos'] += 1
        return "Positif"
    elif predicted_class == 5:
        stats_conversations[current_conversation]['pos'] += 1
        return "Vraiment positif"

def update_bars():
    stats = stats_conversations.get(current_conversation, {'pos': 0, 'neg': 0, 'neu': 0})
    total = sum(stats.values())
    total = total if total != 0 else 1

    progress_pos.configure(value=stats['pos'] / total * 100)
    progress_neu.configure(value=stats['neu'] / total * 100)
    progress_neg.configure(value=stats['neg'] / total * 100)

    label_pos.configure(text=f"Positif: {stats['pos']}/{total}")
    label_neu.configure(text=f"Neutre: {stats['neu']}/{total}")
    label_neg.configure(text=f"Négatif: {stats['neg']}/{total}")

def envoyer_message(event=None):
    texte_saisi = entree.get().strip()
    if texte_saisi:
        conversation_box.configure(state="normal")
        conversation_box.insert("end", f"Vous: {texte_saisi}\n", "user")
        reponse = analyseConv(texte_saisi)
        conversation_box.insert("end", f"LEIA: Je pense que c'est {reponse}\n", "bot")

        conversations[current_conversation].append(f"Vous: {texte_saisi}")
        conversations[current_conversation].append(f"LEIA: Je pense que c'est {reponse}")

        update_bars()

        conversation_box.configure(state="disabled")
        entree.delete(0, "end")
        conversation_box.see("end")

def nouvelle_conversation():
    global current_conversation
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
    current_conversation = timestamp
    conversations[current_conversation] = ["LEIA: Bonjour ! Comment puis-je vous aider ?"]
    stats_conversations[current_conversation] = {'pos': 0, 'neg': 0, 'neu': 0}
    liste_conversations.insert(0, current_conversation)
    afficher_conversation(current_conversation)
    update_bars()

def afficher_conversation(titre):
    global current_conversation
    current_conversation = titre
    conversation_box.configure(state="normal")
    conversation_box.delete("1.0", "end")
    for ligne in conversations[titre]:
        tag = "user" if ligne.startswith("Vous") else "bot"
        conversation_box.insert("end", ligne + "\n", tag)
    conversation_box.configure(state="disabled")
    update_bars()

# Chargement et affichage du logo
image = Image.open("LEIA/logoLEIA.png")
image = image.resize((150, 150))  # Logo légèrement plus petit
photo = ImageTk.PhotoImage(image)
label_logo = ttk.Label(frame, image=photo, background=couleur_fond)
label_logo.image = photo
label_logo.pack(pady=10)

titre = ttk.Label(frame, text="Conversation avec LEIA", font=("Helvetica", 16, "bold"), bootstyle="secondary", background=couleur_fond)
titre.pack(pady=10)

# Cadre pour la zone de conversation avec bordure douce
conversation_frame = ttk.Frame(frame, bootstyle="secondary-light")
conversation_frame.pack(pady=5, padx=5, fill="both")

conversation_box = ttk.Text(conversation_frame, width=60, height=12, font=("Helvetica", 11), background="#fafcff", relief="flat")
conversation_box.pack(pady=5, padx=5, fill="both")
conversation_box.tag_config("user", foreground="#3498db")  # Bleu plus doux pour utilisateur
conversation_box.tag_config("bot", foreground="#8e44ad")   # Violet plus doux pour l'IA
conversation_box.configure(state="disabled")

# Frame pour l'entrée et le bouton envoyer (côte à côte)
input_frame = ttk.Frame(frame, style="Custom.TFrame")
input_frame.pack(pady=10, fill="x")

entree = ttk.Entry(input_frame, width=45, font=("Helvetica", 12))
entree.pack(side="left", pady=5, padx=(0, 5), fill="x", expand=True)
entree.bind("<Return>", envoyer_message)

bouton_envoyer = ttk.Button(input_frame, text="Analyser", bootstyle="secondary-outline", command=envoyer_message)
bouton_envoyer.pack(side="right", pady=5)

bouton_nouvelle_conversation = ttk.Button(frame, text="Nouvelle Conversation", bootstyle="secondary", command=nouvelle_conversation)
bouton_nouvelle_conversation.pack(pady=10)

# Barres de progression avec séparation visuelle
progress_frame = ttk.LabelFrame(frame, text="Statistiques de la conversation", style="Custom.TFrame", padding=10)
progress_frame.pack(pady=10, fill="x")

# Progressbar positive
label_pos = ttk.Label(progress_frame, text="Positif: 0/0", background=couleur_fond)
label_pos.pack(anchor="w", pady=(5, 0))
progress_pos = ttk.Progressbar(progress_frame, length=200, bootstyle="success")
progress_pos.pack(fill="x", pady=(0, 10))

# Progressbar neutre
label_neu = ttk.Label(progress_frame, text="Neutre: 0/0", background=couleur_fond)
label_neu.pack(anchor="w", pady=(5, 0))
progress_neu = ttk.Progressbar(progress_frame, length=200, bootstyle="info")
progress_neu.pack(fill="x", pady=(0, 10))

# Progressbar négative
label_neg = ttk.Label(progress_frame, text="Négatif: 0/0", background=couleur_fond)
label_neg.pack(anchor="w", pady=(5, 0))
progress_neg = ttk.Progressbar(progress_frame, length=200, bootstyle="danger")
progress_neg.pack(fill="x")

# Initialisation
current_conversation = None
nouvelle_conversation()
fenetre.mainloop()