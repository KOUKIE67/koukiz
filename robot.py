import ccxt, json, os, time, datetime, requests
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

exchange = ccxt.binance({'enableRateLimit': True})
MEMOIRE_FICHIER = 'memoire_omega.json'
TICKETS_FICHIER = 'tickets_ordre.json'

def envoyer_telegram(msg):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID: return
    try: requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", json={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "HTML"})
    except: pass

def charger_memoire():
    if not os.path.exists(MEMOIRE_FICHIER): return {"capital_usdt": 5000.0, "positions": {}}
    with open(MEMOIRE_FICHIER, 'r') as f: return json.load(f)

def demarrer_sniper():
    print("🔫 SNIPER V14 - PRÊT À FAIRE FEU")
    envoyer_telegram("🔫 <b>SNIPER V14 ACTIVÉ</b>\n<i>En attente des tickets du Quant...</i>")
    
    while True:
        try:
            memoire = charger_memoire()
            
            # 1. GESTION DES SORTIES (La priorité absolue)
            for symb, data in list(memoire["positions"].items()):
                p_actuel = exchange.fetch_ticker(symb)['last']
                if p_actuel > data['plus_haut_atteint']: data['plus_haut_atteint'] = p_actuel
                
                seuil = data['plus_haut_atteint'] * 0.95 # Trailing stop de sécurité
                if p_actuel <= seuil:
                    pnl = ((p_actuel - data['prix_entree']) / data['prix_entree']) * 100
                    memoire["capital_usdt"] += (data['montant_investi'] * (1 + pnl/100))
                    envoyer_telegram(f"🔪 <b>VENTE {symb}</b>\nPnL: {pnl:.2f}%")
                    del memoire["positions"][symb]

            # 2. LECTURE DES TICKETS DU QUANT (Entrées)
            if len(memoire["positions"]) < 4:
                try:
                    with open(TICKETS_FICHIER, 'r') as f: tickets = json.load(f)
                except: tickets = []
                
                for ticket in tickets:
                    symb = ticket['symbol']
                    if symb not in memoire["positions"]:
                        montant = memoire["capital_usdt"] * ticket['pourcentage_capital']
                        memoire["positions"][symb] = {
                            "prix_entree": ticket['prix_cible'],
                            "plus_haut_atteint": ticket['prix_cible'],
                            "montant_investi": montant
                        }
                        memoire["capital_usdt"] -= montant
                        envoyer_telegram(f"🎯 <b>ACHAT VALIDÉ PAR LE QUANT</b>\nActif: {symb}\nMise: {montant:.2f}$")
                        
                # On vide les tickets une fois traités
                with open(TICKETS_FICHIER, 'w') as f: json.dump([], f)

            with open(MEMOIRE_FICHIER, 'w') as f: json.dump(memoire, f, indent=4)
            time.sleep(30) # Le Sniper est très rapide, il vérifie toutes les 30 sec.
            
        except Exception as e:
            time.sleep(30)

if __name__ == "__main__": demarrer_sniper()