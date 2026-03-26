import time, json, os, requests
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
MEMOIRE_FICHIER = 'memoire_omega.json'
MATRICE_FICHIER = 'matrice_decision.json'

def lire_fichiers():
    try:
        with open(MEMOIRE_FICHIER, 'r') as f: memoire = json.load(f)
    except: memoire = {"capital_usdt": 0, "positions": {}}
    
    try:
        with open(MATRICE_FICHIER, 'r') as f: decret = json.load(f)
    except: decret = {"regime_actuel": "INCONNU", "analyse_dalio": "INCONNU", "analyse_taleb": "INCONNU", "analyse_kahneman": "INCONNU"}
    
    return memoire, decret

def envoyer_message(chat_id, texte):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": texte, "parse_mode": "HTML"})

def ecouter_telegram():
    print("📻 OFFICIER DE LIAISON - ACTIVÉ (Écoute Telegram en cours...)")
    url_base = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    dernier_update_id = 0
    
    while True:
        try:
            # On va chercher les nouveaux messages
            reponse = requests.get(f"{url_base}?offset={dernier_update_id}&timeout=10").json()
            
            if reponse.get("ok"):
                for message_data in reponse["result"]:
                    dernier_update_id = message_data["update_id"] + 1
                    
                    if "message" in message_data and "text" in message_data["message"]:
                        texte_recu = message_data["message"]["text"].lower()
                        chat_id = message_data["message"]["chat"]["id"]
                        
                        memoire, decret = lire_fichiers()
                        
                        # --- TRAITEMENT DES ORDRES DU PATRON ---
                        if texte_recu == "/statut":
                            nb_pos = len(memoire.get("positions", {}))
                            msg = f"🏦 <b>STATUT DE LA FIRME</b>\nCapital dispo : {memoire.get('capital_usdt', 0):.2f}$\nPositions actives : {nb_pos}"
                            envoyer_message(chat_id, msg)
                            
                        elif texte_recu == "/meteo":
                            msg = f"🌍 <b>CLIMAT MONDIAL</b>\nDécision de l'Oracle : <b>{decret.get('regime_actuel')}</b>"
                            envoyer_message(chat_id, msg)
                            
                        elif texte_recu == "/pourquoi":
                            # L'explication transparente des choix
                            msg = (f"🧠 <b>RAPPORT D'ANALYSE DE L'ORACLE</b>\n\n"
                                   f"Voici pourquoi nous sommes en {decret.get('regime_actuel')} :\n"
                                   f"▪️ <b>Ray Dalio (Liquidité/Dollar) :</b> {decret.get('analyse_dalio')}\n"
                                   f"▪️ <b>Nassim Taleb (Risque/VIX) :</b> {decret.get('analyse_taleb')}\n"
                                   f"▪️ <b>Daniel Kahneman (Psychologie) :</b> {decret.get('analyse_kahneman')}\n\n"
                                   f"<i>Note : Le Quant refusera de rédiger des tickets tant que ces 3 maîtres ne sont pas alignés.</i>")
                            envoyer_message(chat_id, msg)
                            
                        elif texte_recu == "/urgence":
                            envoyer_message(chat_id, "🚨 <b>BOUTON ROUGE ACTIVÉ</b> 🚨\nFermeture immédiate des algorithmes d'achat. Purge de la mémoire demandée.")
                            # On force le stop en vidant les positions (Simulation pour l'instant)
                            memoire["positions"] = {}
                            with open(MEMOIRE_FICHIER, 'w') as f: json.dump(memoire, f)
                            
                        else:
                            envoyer_message(chat_id, "🤖 <b>Commandes reconnues :</b>\n/statut\n/meteo\n/pourquoi\n/urgence")
                            
        except Exception as e:
            time.sleep(5)

if __name__ == "__main__":
    ecouter_telegram()