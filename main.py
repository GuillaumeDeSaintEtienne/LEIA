import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
from datetime import datetime
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch


# Liste pour stocker les conversations
conversations = {}

tokenizer_fr = AutoTokenizer.from_pretrained("ulrichING/bert-base-sentiment-analysis-french")
model_fr = AutoModelForSequenceClassification.from_pretrained("ulrichING/bert-base-sentiment-analysis-french")

tokenizer_multi_lang = AutoTokenizer.from_pretrained("tabularisai/multilingual-sentiment-analysis")
model_multi_lang = AutoModelForSequenceClassification.from_pretrained("tabularisai/multilingual-sentiment-analysis")

def analyseConv(text):
    
    inputs = tokenizer_multi_lang(text, return_tensors="pt")

    with torch.no_grad():
        outputs = model_multi_lang(**inputs)

        logits = outputs.logits
        predicted_class = torch.argmax(logits).item()

        print(text)
        print(f"Raw logits: {logits}")
        print(f"Predicted sentiment class: {predicted_class + 1} (1 = worst, 5 = best)")

    if (predicted_class+1 == 1) : return "negatif" 
    else : return "positif"

def envoyer_message(event=None):
    """Affiche le message de l'utilisateur dans la conversation et l'enregistre."""
    texte_saisi = entree.get().strip()

    if texte_saisi:
        conversation_box.configure(state="normal")
        conversation_box.insert("end", f"👤 Vous : {texte_saisi}\n", "user")
        reponse = analyseConv(texte_saisi)
        conversation_box.insert("end", f"🤖 IA : Je reçois votre message : '{texte_saisi}'\nJe pense qu'il est plutot {reponse}", "bot")

        # Ajouter le message à la conversation actuelle
        conversations[current_conversation].append(f"👤 Vous : {texte_saisi}")
        conversations[current_conversation].append(f"🤖 IA : Je reçois votre message : '{texte_saisi}'")

        conversation_box.configure(state="disabled")
        entree.delete(0, "end")
        conversation_box.see("end")


def nouvelle_conversation():
    """Crée une nouvelle conversation avec la date et l'affiche."""
    global current_conversation

    # Générer un titre basé sur la date et l'heure
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_conversation = timestamp
    conversations[current_conversation] = ["🤖 IA : Bonjour ! Comment puis-je vous aider ?"]

    # Ajouter à la liste des conversations
    liste_conversations.insert(0, current_conversation)
    afficher_conversation(current_conversation)


def afficher_conversation(titre):
    """Affiche une conversation existante sans permettre de la modifier."""
    conversation_box.configure(state="normal")
    conversation_box.delete("1.0", "end")

    for ligne in conversations[titre]:
        if ligne.startswith("👤"):
            conversation_box.insert("end", ligne + "\n", "user")
        else:
            conversation_box.insert("end", ligne + "\n", "bot")

    conversation_box.configure(state="disabled")


# Création de la fenêtre principale
fenetre = ttk.Window(themename="darkly")
fenetre.title("Chat LEIA")

# Définition des couleurs
couleur_fond = "#150d25"
fenetre.configure(bg=couleur_fond)



# Style personnalisé
style = ttk.Style()
style.configure("Custom.TFrame", background=couleur_fond)

# Conteneur principal
frame = ttk.Frame(fenetre, style="Custom.TFrame")
frame.pack(side="right", padx=20, pady=20)

# Panneau latéral pour l'historique des conversations
frame_historique = ttk.Frame(fenetre, style="Custom.TFrame")
frame_historique.pack(side="left", fill="y", padx=10, pady=10)

label_historique = ttk.Label(frame_historique, text="📜 Conversations", font=("Arial", 14, "bold"), bootstyle="primary",
                             background=couleur_fond)
label_historique.pack(pady=5)

# ✅ Correction : Utilisation de tk.Listbox au lieu de ttk.Listbox
liste_conversations = tk.Listbox(frame_historique, height=15, bg="#34495E", fg="white", font=("Arial", 12))
liste_conversations.pack(fill="y", expand=True, padx=5, pady=5)
liste_conversations.bind("<<ListboxSelect>>", lambda e: afficher_conversation(
    liste_conversations.get(liste_conversations.curselection())) if liste_conversations.curselection() else None)

# Chargement et affichage du logo
image = Image.open("LEIA/logoLEIA.png")  # Remplace par ton image
image = image.resize((400, 400))
photo = ImageTk.PhotoImage(image)

label_logo = ttk.Label(frame, image=photo, background=couleur_fond)
label_logo.image = photo
label_logo.pack(pady=10)

# Titre
titre = ttk.Label(frame, text="💬 Chat avec LEIA :", font=("Arial", 16, "bold"), bootstyle="primary",
                  background=couleur_fond)
titre.pack(pady=10)

# Zone d'affichage de la conversation
conversation_box = ttk.Text(frame, width=60, height=15, font=("Arial", 12))
conversation_box.pack(pady=5)
conversation_box.tag_config("user", foreground="cyan")
conversation_box.tag_config("bot", foreground="red")
conversation_box.configure(state="disabled")

# Champ de saisie
entree = ttk.Entry(frame, width=50, font=("Arial", 14))
entree.pack(pady=5)
entree.bind("<Return>", envoyer_message)

# Bouton d'envoi
bouton_envoyer = ttk.Button(frame, text="📩 Analyser", bootstyle="success", command=envoyer_message)
bouton_envoyer.pack(pady=5)

# Bouton Nouvelle Conversation
bouton_nouvelle_conversation = ttk.Button(frame, text="➕ Nouvelle Conversation", bootstyle="info",
                                          command=nouvelle_conversation)
bouton_nouvelle_conversation.pack(pady=5)

# Démarrer une première conversation
current_conversation = None
nouvelle_conversation()

# Lancement de l'interface
fenetre.mainloop()
