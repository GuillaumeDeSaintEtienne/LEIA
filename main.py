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
fenetre = ttk.Window(themename="darkly")
fenetre.title("Chat LEIA")

# Définition des couleurs
couleur_fond = "#150d25"
fenetre.configure(bg=couleur_fond)

style = ttk.Style()
style.configure("Custom.TFrame", background=couleur_fond)

# Frame principal
frame = ttk.Frame(fenetre, style="Custom.TFrame")
frame.pack(side="right", padx=10, pady=10)

# Historique des conversations
frame_historique = ttk.Frame(fenetre, style="Custom.TFrame")
frame_historique.pack(side="left", fill="y", padx=10, pady=10)

label_historique = ttk.Label(frame_historique, text="📜 Conversations", font=("Arial", 14, "bold"), bootstyle="primary", background=couleur_fond)
label_historique.pack(pady=5)

liste_conversations = tk.Listbox(frame_historique, height=15, bg="#34495E", fg="white", font=("Arial", 12))
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

    label_pos.configure(text=f"{stats['pos']}/{total}")
    label_neu.configure(text=f"{stats['neu']}/{total}")
    label_neg.configure(text=f"{stats['neg']}/{total}")

def envoyer_message(event=None):
    texte_saisi = entree.get().strip()
    if texte_saisi:
        conversation_box.configure(state="normal")
        conversation_box.insert("end", f"👤 Vous : {texte_saisi}\n", "user")
        reponse = analyseConv(texte_saisi)
        conversation_box.insert("end", f"🤖 IA : Je pense que c’est {reponse}\n", "bot")

        conversations[current_conversation].append(f"👤 Vous : {texte_saisi}")
        conversations[current_conversation].append(f"🤖 IA : Je pense que c’est {reponse}")

        update_bars()

        conversation_box.configure(state="disabled")
        entree.delete(0, "end")
        conversation_box.see("end")

def nouvelle_conversation():
    global current_conversation
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_conversation = timestamp
    conversations[current_conversation] = ["🤖 IA : Bonjour ! Comment puis-je vous aider ?"]
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
        tag = "user" if ligne.startswith("👤") else "bot"
        conversation_box.insert("end", ligne + "\n", tag)
    conversation_box.configure(state="disabled")
    update_bars()

# Chargement et affichage du logo
image = Image.open("LEIA/logoLEIA.png")
image = image.resize((200, 200))
photo = ImageTk.PhotoImage(image)
label_logo = ttk.Label(frame, image=photo, background=couleur_fond)
label_logo.image = photo
label_logo.pack(pady=5)

titre = ttk.Label(frame, text="💬 Chat avec LEIA :", font=("Arial", 16, "bold"), bootstyle="primary", background=couleur_fond)
titre.pack(pady=5)

conversation_box = ttk.Text(frame, width=60, height=12, font=("Arial", 12))
conversation_box.pack(pady=5)
conversation_box.tag_config("user", foreground="cyan")
conversation_box.tag_config("bot", foreground="red")
conversation_box.configure(state="disabled")

entree = ttk.Entry(frame, width=50, font=("Arial", 14))
entree.pack(pady=3)
entree.bind("<Return>", envoyer_message)

bouton_envoyer = ttk.Button(frame, text="📩 Analyser", bootstyle="success", command=envoyer_message)
bouton_envoyer.pack(pady=3)

bouton_nouvelle_conversation = ttk.Button(frame, text="➕ Nouvelle Conversation", bootstyle="info", command=nouvelle_conversation)
bouton_nouvelle_conversation.pack(pady=6)

# Barres de progression
progress_frame = ttk.Frame(frame, style="Custom.TFrame")
progress_frame.pack(pady=(10, 5))

progress_pos = ttk.Progressbar(progress_frame, length=200, bootstyle="success-striped")
label_pos = ttk.Label(progress_frame, text="0/0", background=couleur_fond)
progress_pos.pack(pady=2)
label_pos.pack(pady=(0, 5))

progress_neu = ttk.Progressbar(progress_frame, length=200, bootstyle="warning-striped")
label_neu = ttk.Label(progress_frame, text="0/0", background=couleur_fond)
progress_neu.pack(pady=2)
label_neu.pack(pady=(0, 5))

progress_neg = ttk.Progressbar(progress_frame, length=200, bootstyle="danger-striped")
label_neg = ttk.Label(progress_frame, text="0/0", background=couleur_fond)
progress_neg.pack(pady=2)
label_neg.pack(pady=(0, 5))

# Initialisation
current_conversation = None
nouvelle_conversation()
fenetre.mainloop()

