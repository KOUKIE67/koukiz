import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time

# ==========================================
# ⚙️ CONFIGURATION & THEME ABSOLU
# ==========================================
st.set_page_config(page_title="TERMINAL ARCHITECTE", layout="wide", initial_sidebar_state="collapsed")

# Injection de CSS pour écraser le style basique de Streamlit
st.markdown("""
    <style>
    /* Fond de l'application entier */
    [data-testid="stAppViewContainer"] { background-color: #0b0e14; }
    [data-testid="stHeader"] { background-color: transparent; }
    
    /* Typographie et couleurs de base */
    .main { color: #a1a1aa; font-family: 'Inter', 'Segoe UI', sans-serif; }
    h1, h2, h3 { color: #ffffff !important; font-weight: 600 !important; }
    
    /* Cartes de Métriques (Style Bloomberg/Glassnode) */
    div[data-testid="metric-container"] {
        background-color: #181825;
        border: 1px solid #2a2a35;
        border-radius: 8px;
        padding: 15px 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    div[data-testid="metric-container"] > div { color: #cbd5e1 !important; }
    
    /* Ligne de séparation personnalisée */
    hr { border-color: #2a2a35; margin-top: 2rem; margin-bottom: 2rem; }
    
    /* Conteneurs de texte */
    .stAlert { background-color: #181825; border: 1px solid #3b82f6; color: #e2e8f0; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>👁️ THE MATRIX : INSTITUTIONAL TERMINAL</h1>", unsafe_allow_html=True)

try:
    # Chargement des données (Tolérance aux erreurs si le fichier est en cours d'écriture)
    df = pd.read_csv("../data/matrice_onchain_v18.csv")
    if df.empty:
        st.warning("Base de données initialisée. En attente du premier cycle réseau...")
        st.stop()
        
    last_ts = df['Time'].iloc[-1]
    df_live = df[df['Time'] == last_ts]
    portfolio_val = df['Portfolio'].iloc[-1]

    # ==========================================
    # 📊 LIGNE 1 : MÉTROLOGIE MACRO
    # ==========================================
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 CAPITAL DÉPLOYÉ", f"${portfolio_val:,.2f}", delta=f"{portfolio_val - 10000:,.2f} $")
    c2.metric("📡 UNITÉS SOUS SURVEILLANCE", f"{len(df_live)} Actifs")
    c3.metric("🕒 DERNIER SCAN ON-CHAIN", f"{last_ts}")
    
    # Calcul de la dynamique globale (Combien de Pions sur tout le plateau)
    total_pawns = df_live['Pawns_Retail'].sum()
    c4.metric("♟️ VOLUME RETAIL GLOBAL", f"{total_pawns:,.0f} Pions")

    st.markdown("<hr>", unsafe_allow_html=True)

    # ==========================================
    # 🗺️ LIGNE 2 : LA CARTE DE GUERRE (Treemap)
    # ==========================================
    st.markdown("<h3>🗺️ DÉPLOIEMENT TACTIQUE (Liquidité Mondiale)</h3>", unsafe_allow_html=True)
    st.caption("Taille des blocs = Volume de Pions (Hype) | Couleur = Présence des Rois (TVL Institutionnelle)")
    
    # On utilise un Treemap au lieu du Scatter plot plat pour un look hyper pro
    # On ajoute +1 à Kings_TVL pour éviter les couleurs nulles sur le BTC
    df_live_map = df_live.copy()
    df_live_map['Color_TVL'] = df_live_map['Kings_TVL'] + 1 
    
    fig_tree = px.treemap(df_live_map, path=['Symbol'], values='Pawns_Retail',
                          color='Color_TVL', color_continuous_scale='tealgrn',
                          hover_data=['Price', 'Kings_TVL', 'Knights_Vol'])
    fig_tree.update_layout(margin=dict(t=10, l=10, r=10, b=10), paper_bgcolor="#0b0e14", font_color="#ffffff")
    st.plotly_chart(fig_tree, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ==========================================
    # 🎯 LIGNE 3 : PROFILAGE D'UNITÉ & RADAR
    # ==========================================
    col_sel, col_radar, col_log = st.columns([1, 1.5, 1.5])

    with col_sel:
        st.markdown("<h3>🎯 CIBLAGE</h3>", unsafe_allow_html=True)
        cible = st.selectbox("Sélectionner l'entité :", df_live['Symbol'].unique(), label_visibility="collapsed")
        u = df_live[df_live['Symbol'] == cible].iloc[0]
        
        st.markdown(f"**Prix Actuel:** ${u['Price']:,.4f}")
        
        # Affichage conditionnel de l'ordre de l'IA avec couleurs
        if u['IA_Order'] == "ACHAT":
            st.success(f"🟢 ORDRE IA : {u['IA_Order']}")
        elif u['IA_Order'] == "VENTE":
            st.error(f"🔴 ORDRE IA : {u['IA_Order']}")
        else:
            st.warning(f"⚪ ORDRE IA : {u['IA_Order']}")
            
        st.info(f"**ANALYSE :** {u['IA_Reason']}")

    with col_radar:
        st.markdown(f"<h3>🕸️ STRUCTURE DE L'ARMÉE ({cible})</h3>", unsafe_allow_html=True)
        # Graphique Radar (Spider Chart) pour montrer l'équilibre de l'armée
        categories = ['Rois (TVL)', 'Cavaliers (Algos)', 'Pions (Retail)']
        # On normalise un peu les valeurs pour le radar afin que ce soit lisible
        valeurs = [u['Kings_TVL'], u['Knights_Vol'], u['Pawns_Retail']/10] 
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=valeurs, theta=categories, fill='toself', 
            name=cible, line_color='#00ff41', fillcolor='rgba(0, 255, 65, 0.2)'
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=False, range=[0, max(valeurs)+1])),
            showlegend=False, paper_bgcolor="#0b0e14", font_color="#ffffff",
            margin=dict(t=30, l=30, r=30, b=30)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with col_log:
        st.markdown(f"<h3>📈 DYNAMIQUE DE PRIX ({cible})</h3>", unsafe_allow_html=True)
        df_history = df[df['Symbol'] == cible]
        
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=df_history['Time'], y=df_history['Price'], 
            mode='lines', line=dict(color='#3b82f6', width=3),
            fill='tozeroy', fillcolor='rgba(59, 130, 246, 0.1)'
        ))
        fig_line.update_layout(
            paper_bgcolor="#0b0e14", plot_bgcolor="#0b0e14", font_color="#a1a1aa",
            margin=dict(t=10, l=0, r=0, b=0), xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#181825')
        )
        st.plotly_chart(fig_line, use_container_width=True)

except Exception as e:
    st.error(f"📡 ERREUR TERMINAL : Impossible de charger l'interface tactique. ({e})")
    st.info("Assure-toi que 'matrice_core.py' a bien généré le fichier CSV.")