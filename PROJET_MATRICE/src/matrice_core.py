import time, csv, requests, os
from google import genai
import pandas as pd

# ==========================================
# ⚙️ CONFIGURATION ON-CHAIN
# ==========================================
CLE_API_GEMINI = "TA_CLE_API_GEMINI_ICI"  # <-- METS TA CLÉ ICI
# Utilisation du nouveau client officiel Google GenAI
client = genai.Client(api_key=CLE_API_GEMINI)
DATA_FILE = "../data/matrice_onchain_v18.csv"

# ==========================================
# 🛰️ LES SONDES DE DONNÉES BLINDÉES
# ==========================================
def scanner_liquidite_onchain():
    try:
        req_llama = requests.get("https://api.llama.fi/protocols").json()
        dict_tvl = {}
        for p in req_llama:
            if p.get('symbol'):
                val_tvl = p.get('tvl')
                dict_tvl[p['symbol'].upper()] = float(val_tvl) if val_tvl is not None else 0.0

        req_cg = requests.get("https://api.coingecko.com/api/v3/coins/markets", 
                              params={'vs_currency':'usd', 'per_page': 50}).json()
        
        donnees_fusionnees = []
        for c in req_cg:
            sym = c.get('symbol', '').upper()
            if not sym: continue
            
            tvl = dict_tvl.get(sym, 0.0)
            mcap = float(c.get('market_cap') or 0.0)
            vol = float(c.get('total_volume') or 0.0)
            change = float(c.get('price_change_percentage_24h') or 0.0)
            price = float(c.get('current_price') or 0.0)
            
            # CALCUL DES ARMÉES
            kings = int(tvl / 10_000_000) 
            knights = int((vol / (mcap + 1)) * 1000) 
            pawns = int(abs(change) * (vol / 100_000_000))
            
            donnees_fusionnees.append({
                'symbol': sym, 'price': price, 'change': change,
                'kings': kings, 'knights': knights, 'pawns': pawns, 'tvl': tvl
            })
        return donnees_fusionnees
    except Exception as e:
        print(f"⚠️ Brouillard radar On-Chain : {e}")
        return []

# ==========================================
# 🧠 LE CONSEIL DES SOUVERAINS (IA)
# ==========================================
def analyser_rotation(crypto, btc_change):
    prompt = f"""
    Analyse de rotation des capitaux.
    BTC Variation: {btc_change}%.
    Cible: {crypto['symbol']} | Rois (TVL Institutionnelle): {crypto['kings']} | Cavaliers (Algos): {crypto['knights']} | Pions (Retail): {crypto['pawns']}
    Si les Rois dominent, c'est solide. Si les Pions explosent sans Rois, c'est une bulle.
    Donne ton ordre stratégique.
    FORMAT STRICT -> ORDRE: [ACHAT/VENTE/ATTENTE] | RAISON: [10 mots max]
    """
    try:
        # Nouvelle syntaxe Google GenAI
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
        )
        res = response.text
        ordre = res.split("ORDRE:")[1].split("|")[0].strip()
        raison = res.split("RAISON:")[1].strip()
        return ordre, raison
    except: return "ATTENTE", "Analyse impossible"

# ==========================================
# 🚀 LE LANCEUR
# ==========================================
def executer_matrice_onchain():
    print("🌍 Connexion aux noeuds blockchain... Sondes On-Chain activées.")
    capital = 10000.0
    
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', newline='') as f:
            csv.writer(f).writerow(["Time", "Symbol", "Price", "Kings_TVL", "Knights_Vol", "Pawns_Retail", "IA_Order", "IA_Reason", "Portfolio"])

    while True:
        ts = time.strftime("%H:%M:%S")
        marche_reel = scanner_liquidite_onchain()
        
        if not marche_reel:
            time.sleep(60); continue

        btc_data = next((item for item in marche_reel if item["symbol"] == "BTC"), None)
        btc_change = btc_data['change'] if btc_data else 0.0

        print(f"\n[{ts}] ⚡ Scan On-Chain terminé. Analyse de l'État-Major :")

        for crypto in marche_reel[:10]: # Analyse du Top 10
            ordre, raison = analyser_rotation(crypto, btc_change)
            
            # AFFICHAGE VISUEL DANS LE TERMINAL
            couleur = "🟢" if ordre == "ACHAT" else "🔴" if ordre == "VENTE" else "⚪"
            print(f"   {couleur} {crypto['symbol'].ljust(5)} : {ordre.ljust(8)} | {raison}")
            
            # Simulation d'impact
            if ordre == "ACHAT":
                capital *= (1 + (crypto['change'] / 100) * 0.1)
            
            with open(DATA_FILE, 'a', newline='') as f:
                csv.writer(f).writerow([ts, crypto['symbol'], crypto['price'], crypto['kings'], crypto['knights'], crypto['pawns'], ordre, raison, round(capital, 2)])
                
        print(f"💰 Capital mis à jour : ${capital:.2f}")
        print("-" * 50)
        time.sleep(120) 

if __name__ == "__main__":
    executer_matrice_onchain()