import yfinance as yf
from google import genai
import json, time, datetime, os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('GEMINI_API_KEY')
client = genai.Client(api_key=API_KEY)

MATRICE_FICHIER = 'matrice_decision.json'

# ==========================================
# 📚 LES ALGORITHMES DES MAÎTRES
# ==========================================

def theorie_ray_dalio_macro():
    """Inspiré de Ray Dalio : Analyse de la liquidité (Dollar) et de la macro."""
    try:
        dxy = yf.Ticker("DX-Y.NYB").history(period="5d")
        tendance_dollar = (dxy['Close'].iloc[-1] - dxy['Close'].iloc[0]) / dxy['Close'].iloc[0]
        # Si le dollar monte de plus de 0.5% en 5 jours, l'argent fuit les cryptos.
        if tendance_dollar > 0.005: return "CONTRACTION_LIQUIDITE", 0.3 # Score d'autorisation faible
        return "EXPANSION_LIQUIDITE", 1.0
    except: return "INCONNU", 0.5

def theorie_nassim_taleb_risque():
    """Inspiré de Nassim Taleb : Le VIX (Indice de la Peur) pour détecter le chaos."""
    try:
        vix = yf.Ticker("^VIX").history(period="1d")
        niveau_peur = vix['Close'].iloc[-1]
        # Au-dessus de 25, les marchés traditionnels paniquent. Risque de contagion.
        if niveau_peur > 25: return "CYGNE_NOIR_EMINENT", 0.1
        if niveau_peur < 15: return "COMPLAISANCE", 0.8
        return "NORMAL", 1.0
    except: return "INCONNU", 0.5

def theorie_kahneman_psychologie():
    """Inspiré de Daniel Kahneman : Analyse des biais cognitifs via Gemini."""
    prompt = """
    En tant qu'économiste comportemental, analyse l'humeur générale des marchés crypto aujourd'hui.
    Les foules sont-elles dans une "exubérance irrationnelle" (bull) ou une "capitulation" (bear) ?
    Réponds UNIQUEMENT par l'un de ces mots : EUPHORIE, PANIQUE, NEUTRE.
    """
    try:
        reponse = client.models.generate_content(model='gemini-1.5-flash', contents=prompt).text.strip().upper()
        if "PANIQUE" in reponse: return "PANIQUE", 0.9 # Acheter au son du canon (Soros)
        if "EUPHORIE" in reponse: return "EUPHORIE", 0.2 # Vendre au son du violon
        return "NEUTRE", 0.8
    except: return "NEUTRE", 0.5

# ==========================================
# ⚖️ LE TRIBUNAL DE L'ORACLE (Synthèse)
# ==========================================
def rediger_decret():
    print(f"\n[{datetime.datetime.now().strftime('%H:%M:%S')}] L'Oracle consulte les Maîtres...")
    
    macro_etat, macro_score = theorie_ray_dalio_macro()
    risque_etat, risque_score = theorie_nassim_taleb_risque()
    psycho_etat, psycho_score = theorie_kahneman_psychologie()
    
    # Le score final est une multiplication (Système de points de défaillance unique)
    score_final = macro_score * risque_score * psycho_score
    
    # Décision binaire pour le Sniper
    autorisation_tir = True if score_final >= 0.5 else False
    regime = "RISK_ON (Feu Vert)" if autorisation_tir else "RISK_OFF (Bunker)"
    
    decret = {
        "date_maj": str(datetime.datetime.now()),
        "autorisation_achat": autorisation_tir,
        "score_synthese": round(score_final, 2),
        "analyse_dalio": macro_etat,
        "analyse_taleb": risque_etat,
        "analyse_kahneman": psycho_etat,
        "regime_actuel": regime
    }
    
    with open(MATRICE_FICHIER, 'w') as f: json.dump(decret, f, indent=4)
    
    print(f"📜 Décret rédigé : {regime} (Score: {score_final:.2f})")
    print(f"   - Liquidité (Dalio) : {macro_etat}")
    print(f"   - Risque (Taleb) : {risque_etat}")
    print(f"   - Psychologie (Kahneman) : {psycho_etat}")

def lancer_oracle():
    while True:
        try:
            rediger_decret()
            time.sleep(3600) # L'Oracle réfléchit 1 heure avant de revoir sa copie
        except Exception as e:
            print(f"Erreur Oracle: {e}")
            time.sleep(60)

if __name__ == "__main__":
    lancer_oracle()