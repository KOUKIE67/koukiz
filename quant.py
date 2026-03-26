import ccxt, numpy as np
import time, datetime, json, os

# ==========================================
# 🧮 LE QUANT (LIMIER + ACTUAIRE FUSIONNÉS)
# ==========================================
exchange = ccxt.binance({'enableRateLimit': True})
MATRICE_FICHIER = 'matrice_decision.json'
TICKETS_FICHIER = 'tickets_ordre.json'

def traquer_baleines(symbol):
    """Analyse le carnet d'ordres (Dark Pool Level 2) pour voir où l'argent intelligent se place."""
    try:
        ob = exchange.fetch_order_book(symbol, limit=50)
        volume_bids = sum([bid[1] for bid in ob['bids']]) # Murs d'achat
        volume_asks = sum([ask[1] for ask in ob['asks']]) # Murs de vente
        ratio = volume_bids / volume_asks if volume_asks > 0 else 1
        return ratio > 1.5 # Vrai si la pression acheteuse des baleines est 50% supérieure
    except: return False

def simulateur_monte_carlo(prix, volatilite, iterations=500):
    """Simule 500 futurs pour vérifier le risque de crash."""
    echecs = 0
    stop_loss = prix * 0.95 # Stop à -5%
    for _ in range(iterations):
        p_sim = prix
        for _ in range(12): # 12 périodes
            p_sim *= (1 + np.random.normal(0, volatilite))
            if p_sim <= stop_loss:
                echecs += 1
                break
    return (echecs / iterations) * 100

def calculer_mise_kelly(risque_simule):
    proba_win = (100 - risque_simule) / 100
    if proba_win < 0.65: return 0 # Rejet mathématique
    f_star = (proba_win * 1.5 - (1 - proba_win)) / 1.5
    return max(0.01, min(f_star * 0.20, 0.10)) # Max 10% du capital

def generer_tickets():
    print(f"\n[{datetime.datetime.now().strftime('%H:%M:%S')}] Le Quant analyse le marché...")
    
    # 1. Lire les ordres de l'Oracle
    try:
        with open(MATRICE_FICHIER, 'r') as f: decret = json.load(f)
    except: decret = {"autorisation_achat": False}

    tickets = []
    
    if decret.get("autorisation_achat") == True:
        # 2. Le Limier : Chercher des cibles (Top Volume)
        print("🔍 Radar activé : Recherche de traces institutionnelles...")
        cibles_potentielles = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "AVAX/USDT"]
        
        for cible in cibles_potentielles:
            if traquer_baleines(cible):
                # 3. L'Actuaire : Mathématiques de Survie
                ticker = exchange.fetch_ticker(cible)
                prix = ticker['last']
                volatilite = 0.02 # Simplifié pour la performance
                
                risque = simulateur_monte_carlo(prix, volatilite)
                mise_pct = calculer_mise_kelly(risque)
                
                if mise_pct > 0:
                    print(f"✅ {cible} validée. Probabilité de gain: {100-risque:.1f}%")
                    tickets.append({
                        "symbol": cible,
                        "prix_cible": prix,
                        "pourcentage_capital": mise_pct,
                        "date_analyse": str(datetime.datetime.now())
                    })
    else:
        print("🛑 L'Oracle interdit le trading. Le Quant se met en veille.")

    # 4. Rédiger les tickets pour le Sniper
    with open(TICKETS_FICHIER, 'w') as f: json.dump(tickets, f, indent=4)

def lancer_quant():
    while True:
        try:
            generer_tickets()
            time.sleep(120) # Le Quant travaille toutes les 2 minutes
        except Exception as e:
            print(f"Erreur Quant: {e}")
            time.sleep(60)

if __name__ == "__main__": lancer_quant()