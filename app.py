import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import os
import sys
import json
from datetime import datetime, timedelta

# Ajout du chemin vers le dossier src
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from scraper import AgroDataScraper
from data_processor import AgroDataProcessor
from visualizations import AgroDataVisualizer
from interactive_features import InteractiveFeatures
from advanced_features import AdvancedFeatures

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Agroalimentaire",
    page_icon="🥬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour un look moderne
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
    .stButton > button {
        background: linear-gradient(90deg, #2E8B57, #3CB371);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(46, 139, 87, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Titre principal
st.title("🥬 Dashboard d'Analyse des Prix Agroalimentaires")
st.markdown("*Analyse des données du Réseau des Nouvelles des Marchés (RNM)*")

# Sidebar pour la navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox(
    "Choisissez une page",
    ["🏠 Accueil", "📊 Dashboard", "🔄 Scraping", "📈 Analyses", "🤖 IA & Prédictions", "⚙️ Outils Interactifs", "🚀 Features Avancées", "ℹ️ À propos"]
)

def load_data():
    """Charge les données depuis le fichier CSV"""
    try:
        if os.path.exists('data/processed_agro_prices.csv'):
            df = pd.read_csv('data/processed_agro_prices.csv', encoding='utf-8')
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
            return df
        else:
            return None
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {e}")
        return None

def advanced_features_page():
    """Page avec fonctionnalités avancées de niveau expert"""
    st.header("🚀 Features Avancées - Niveau Expert")
    
    df = load_data()
    if df is None:
        st.error("Impossible de charger les données")
        return
    
    advanced = AdvancedFeatures(df)
    
    # Navigation par onglets
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🧠 Sentiment Market", "🔍 Anomalies", "🎯 Clustering", 
        "📊 Elasticite", "📡 Monitoring Live", 
    ])
    
    with tab1:
        st.subheader("🧠 Analyseur de Sentiment du Marche")
        
        sentiment_data = advanced.create_market_sentiment_analyzer()
        
        # Metriques globales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            positive_sentiment = len(sentiment_data[sentiment_data['sentiment_score'] >= 70])
            st.metric("🟢 Sentiment Positif", positive_sentiment)
        
        with col2:
            neutral_sentiment = len(sentiment_data[(sentiment_data['sentiment_score'] >= 40) & (sentiment_data['sentiment_score'] < 70)])
            st.metric("🟡 Sentiment Neutre", neutral_sentiment)
        
        with col3:
            negative_sentiment = len(sentiment_data[sentiment_data['sentiment_score'] < 40])
            st.metric("🔴 Sentiment Negatif", negative_sentiment)
        
        with col4:
            avg_sentiment = sentiment_data['sentiment_score'].mean()
            st.metric("📊 Sentiment Moyen", f"{avg_sentiment:.1f}/100")
        
        # Visualisation du sentiment
        # Corriger les valeurs pour éviter les erreurs de taille
        sentiment_data['size_abs'] = sentiment_data['stability'].clip(lower=0.1)
        
        fig = px.scatter(
            sentiment_data,
            x='volatility',
            y='trend',
            color='sentiment_score',
            size='size_abs',
            hover_name='product',
            title='Carte de Sentiment du Marche',
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Tableau detaille
        st.subheader("📋 Analyse de Sentiment par Produit")
        sentiment_display = sentiment_data.sort_values('sentiment_score', ascending=False)
        st.dataframe(sentiment_display.round(2), use_container_width=True)
    
    with tab2:
        st.subheader("🔍 Detecteur d'Anomalies de Prix")
        
        anomalies = advanced.create_price_anomaly_detector()
        
        if not anomalies.empty:
            st.warning(f"🚨 {len(anomalies)} anomalie(s) detectee(s)")
            
            # Visualisation des anomalies
            fig = go.Figure()
            
            for product in anomalies['product'].unique()[:10]:  # Top 10
                product_data = df[df['product_clean'] == product].sort_values('date')
                product_anomalies = anomalies[anomalies['product'] == product]
                
                # Prix normaux
                fig.add_trace(go.Scatter(
                    x=product_data['date'],
                    y=product_data['price'],
                    mode='lines',
                    name=f'{product} (normal)',
                    line=dict(width=1)
                ))
                
                # Anomalies
                if not product_anomalies.empty:
                    fig.add_trace(go.Scatter(
                        x=product_anomalies['date'],
                        y=product_anomalies['price'],
                        mode='markers',
                        name=f'{product} (anomalie)',
                        marker=dict(size=10, symbol='x', color='red')
                    ))
            
            fig.update_layout(
                title='Detection d\'Anomalies de Prix',
                xaxis_title='Date',
                yaxis_title='Prix (€)',
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Tableau des anomalies
            st.subheader("📋 Detail des Anomalies")
            st.dataframe(anomalies.round(2), use_container_width=True)
        else:
            st.success("✅ Aucune anomalie detectee")
    
    with tab3:
        st.subheader("🎯 Clustering Intelligent des Marches")
        
        market_clusters, kmeans, X_scaled = advanced.create_market_clustering()
        
        # Visualisation 3D des clusters
        # Corriger les valeurs pour éviter les erreurs de taille
        market_clusters['size_abs'] = market_clusters['observation_frequency'].clip(lower=1)
        
        fig = px.scatter_3d(
            market_clusters,
            x='avg_price',
            y='price_volatility',
            z='product_diversity',
            color='cluster_name',
            hover_name='market',
            size='size_abs',
            title='Clustering 3D des Marches'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Analyse des clusters
        st.subheader("📊 Analyse des Clusters")
        
        for cluster_name in market_clusters['cluster_name'].unique():
            cluster_data = market_clusters[market_clusters['cluster_name'] == cluster_name]
            
            with st.expander(f"📁 {cluster_name} ({len(cluster_data)} marches)"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Prix moyen", f"{cluster_data['avg_price'].mean():.2f}€")
                
                with col2:
                    st.metric("Volatilite", f"{cluster_data['price_volatility'].mean():.3f}")
                
                with col3:
                    st.metric("Diversite", f"{cluster_data['product_diversity'].mean():.1f}")
                
                st.dataframe(cluster_data[['market', 'avg_price', 'price_volatility', 'product_diversity']].round(2))
    
    with tab4:
        st.subheader("📊 Analyse d'Elasticite des Prix")
        
        elasticity_data = advanced.create_price_elasticity_analyzer()
        
        # Distribution de l'elasticite
        fig = px.histogram(
            elasticity_data,
            x='elasticity',
            color='elasticity_category',
            title='Distribution de l\'Elasticite des Prix',
            nbins=20
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Matrice de sensibilite
        st.subheader("🎯 Matrice de Sensibilite")
        
        elasticity_pivot = elasticity_data.pivot_table(
            index='product',
            columns='elasticity_category',
            values='elasticity',
            fill_value=0
        )
        
        fig = px.imshow(
            elasticity_pivot,
            title='Matrice d\'Elasticite par Produit',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Tableau detaille
        st.dataframe(elasticity_data.round(3), use_container_width=True)
    
    with tab5:
        st.subheader("📡 Monitoring en Temps Reel")
        
        monitoring_data = advanced.create_real_time_monitoring()
        
        # Tableau de monitoring
        st.dataframe(monitoring_data.round(2), use_container_width=True)
        
        # Graphique des changements de prix
        fig = px.bar(
            monitoring_data,
            x='product',
            y='price_change',
            color='status',
            title='Changements de Prix en Temps Reel',
            text='trend'
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        
        # Alertes automatiques
        high_changes = monitoring_data[abs(monitoring_data['price_change']) > 5]
        if not high_changes.empty:
            st.error("🚨 Alertes de Changement Significatif:")
            for _, alert in high_changes.iterrows():
                st.error(f"{alert['product']}: {alert['price_change']:.2f}% {alert['status']}")
    
    with tab6:
        st.subheader("💼 Optimiseur de Portefeuille")
        
        portfolio_data = advanced.create_portfolio_optimizer()
        
        # Metriques du portefeuille
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_return = portfolio_data['expected_return'].mean()
            st.metric("📈 Rendement Moyen", f"{avg_return:.2%}")
        
        with col2:
            avg_volatility = portfolio_data['volatility'].mean()
            st.metric("📊 Volatilite Moyenne", f"{avg_volatility:.2%}")
        
        with col3:
            avg_sharpe = portfolio_data['sharpe_ratio'].mean()
            st.metric("🎯 Sharpe Moyen", f"{avg_sharpe:.3f}")
        
        with col4:
            high_sharpe = len(portfolio_data[portfolio_data['sharpe_ratio'] > 1.0])
            st.metric("🔥 Produits Premium", high_sharpe)
        
        # Graphique risque-rendement
        # Corriger les valeurs négatives pour la taille
        portfolio_data['size_abs'] = portfolio_data['sharpe_ratio'].abs()
        portfolio_data['size_abs'] = portfolio_data['size_abs'].clip(lower=0.1)  # Éviter les tailles nulles
        
        fig = px.scatter(
            portfolio_data,
            x='volatility',
            y='expected_return',
            size='size_abs',
            color='risk_category',
            hover_name='product',
            title='Optimisation de Portefeuille - Risque vs Rendement',
            color_discrete_map={
                '🟢 Faible risque': 'green',
                '🟵 Modere': 'blue',
                '🟡 Risque': 'orange',
                '🔴 Tres risque': 'red'
            }
        )
        
        # Ajout de la ligne efficiente (simplifiee)
        fig.add_shape(
            type="line",
            x0=0, y0=0,
            x1=portfolio_data['volatility'].max(),
            y1=portfolio_data['expected_return'].max(),
            line=dict(color="red", dash="dash"),
            name="Frontiere Efficient"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Recommandations de portefeuille
        st.subheader("💡 Recommandations de Portefeuille")
        
        # Top produits par Sharpe ratio
        top_products = portfolio_data.nlargest(5, 'sharpe_ratio')
        
        st.write("🏆 **Top 5 des Produits Recommandes:**")
        for _, product in top_products.iterrows():
            st.markdown(f"""
            **{product['product']}**
            - Rendement attendu: {product['expected_return']:.2%}
            - Volatilite: {product['volatility']:.2%}
            - Sharpe Ratio: {product['sharpe_ratio']:.3f}
            - Poids recommande: {product['weight_recommendation']}
            - Risque: {product['risk_category']}
            """)
        
        # Tableau complet
        st.dataframe(portfolio_data.round(3), use_container_width=True)
        
        # Export du rapport
        if st.button("📊 Generer Rapport Complet", type="primary"):
            with st.spinner("Generation du rapport avance..."):
                report = advanced.export_advanced_report()
                
                # Conversion en JSON pour le telechargement
                json_report = json.dumps(report, indent=2, default=str)
                
                st.download_button(
                    label="📥 Telecharger Rapport JSON",
                    data=json_report,
                    file_name=f"advanced_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
                
                st.success("✅ Rapport genere avec succes!")

def home_page():
    """Page d'accueil"""
    st.header("🏠 Bienvenue sur le Dashboard Agroalimentaire")
    
    # Message de bienvenue visible
    st.success("🎉 Projet de Data Science - Scraping et Analyse des Prix Agroalimentaires")
    
    # Statistiques si les données sont disponibles
    df = load_data()
    if df is not None and not df.empty:
        st.subheader("📊 Dernières statistiques")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total enregistrements", f"{len(df):,}")
        
        with col2:
            st.metric("Produits uniques", df['product_clean'].nunique() if 'product_clean' in df.columns else 0)
        
        with col3:
            st.metric("Marchés couverts", df['market_clean'].nunique() if 'market_clean' in df.columns else 0)
        
        with col4:
            st.metric("Prix moyen", f"{df['price'].mean():.2f}€" if 'price' in df.columns else "N/A")
        
        # Graphique rapide
        st.subheader("📈 Vue d'ensemble rapide")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'product_category' in df.columns:
                category_counts = df['product_category'].value_counts()
                fig = px.pie(values=category_counts.values, names=category_counts.index, title='Répartition par catégorie')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'date' in df.columns and 'price' in df.columns:
                daily_avg = df.groupby(df['date'].dt.date)['price'].mean().reset_index()
                fig = px.line(daily_avg, x='date', y='price', title='Évolution moyenne des prix')
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("📋 Aucune donnée chargée. Veuillez vérifier que le fichier data/processed_agro_prices.csv existe.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 📋 Description du projet
        
        Ce projet de scraping et d'analyse de données agroalimentaires collecte des informations 
        sur les prix des produits frais depuis le **Réseau des Nouvelles des Marchés (RNM)** de FranceAgriMer.
        
        ### 🎯 Objectifs
        
        - **Collecte automatique** des données de prix agroalimentaires
        - **Nettoyage et structuration** des données brutes
        - **Analyse statistique** des tendances de prix
        - **Visualisations interactives** pour l'exploration des données
        - **Dashboard web** pour la consultation des résultats
        
        ### 📊 Sources de données
        
        Les données proviennent du site officiel du RNM qui fournit :
        - Prix des fruits et légumes
        - Prix des produits de la mer
        - Prix de la viande
        - Prix des produits laitiers
        """)
    
    with col2:
        st.markdown("""
        ### 🛠️ Technologies utilisées
        
        - **Python** pour le scraping et l'analyse
        - **BeautifulSoup** pour l'extraction web
        - **Pandas** pour la manipulation de données
        - **Plotly** pour les visualisations
        - **Streamlit** pour l'interface web
        - **scikit-learn** pour le Machine Learning
        
        ### 📈 Métriques clés
        
        - Mise à jour quotidienne
        - Plus de 10 catégories de produits
        - Analyse multi-marchés
        - Prédictions IA
        - Détection d'anomalies
        """)
    
    # Actions rapides
    st.subheader("🚀 Actions rapides")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Voir Dashboard", type="primary"):
            st.session_state.page = "📊 Dashboard"
            st.rerun()
    
    with col2:
        if st.button("🤖 IA & Prédictions"):
            st.session_state.page = "🤖 IA & Prédictions"
            st.rerun()
    
    with col3:
        if st.button("🔄 Lancer Scraping"):
            st.session_state.page = "🔄 Scraping"
            st.rerun()
    
    with col4:
        if st.button("🚀 Features Avancées"):
            st.session_state.page = "🚀 Features Avancées"
            st.rerun()

def dashboard_page():
    """Page principale du dashboard"""
    st.header("📊 Dashboard Principal")
    
    df = load_data()
    if df is None or df.empty:
        st.warning("Aucune donnée disponible. Veuillez d'abord exécuter le scraping.")
        return
    
    # Filtres dans la sidebar
    st.sidebar.subheader("🔍 Filtres")
    
    # Filtre par catégorie de produit
    if 'product_category' in df.columns:
        categories = ['Toutes'] + list(df['product_category'].unique())
        selected_category = st.sidebar.selectbox("Catégorie de produit", categories)
        if selected_category != 'Toutes':
            df = df[df['product_category'] == selected_category]
    
    # Filtre par marché
    if 'market_clean' in df.columns:
        markets = ['Tous'] + list(df['market_clean'].unique())
        selected_market = st.sidebar.selectbox("Marché", markets)
        if selected_market != 'Tous':
            df = df[df['market_clean'] == selected_market]
    
    # Filtre par plage de dates
    if 'date' in df.columns:
        min_date = df['date'].min().date()
        max_date = df['date'].max().date()
        start_date, end_date = st.sidebar.date_input("Plage de dates", [min_date, max_date])
        
        df = df[(df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)]
    
    # Onglets pour différentes visualisations
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Évolution", "📊 Distribution", "🗺️ Comparaisons", "📋 Données"])
    
    with tab1:
        st.subheader("Évolution des prix dans le temps")
        
        if 'price' in df.columns and 'date' in df.columns:
            # Prix moyens par jour
            daily_prices = df.groupby('date')['price'].mean().reset_index()
            
            fig = px.line(daily_prices, x='date', y='price', 
                         title='Évolution des prix moyens quotidiens',
                         labels={'price': 'Prix moyen (€)', 'date': 'Date'})
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Prix par catégorie
            if 'product_category' in df.columns:
                category_prices = df.groupby(['date', 'product_category'])['price'].mean().reset_index()
                
                fig2 = px.line(category_prices, x='date', y='price', color='product_category',
                             title='Évolution des prix par catégorie',
                             labels={'price': 'Prix moyen (€)', 'date': 'Date', 'product_category': 'Catégorie'})
                
                st.plotly_chart(fig2, use_container_width=True)
    
    with tab2:
        st.subheader("Distribution des prix")
        
        if 'price' in df.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                # Histogramme
                fig_hist = px.histogram(df, x='price', nbins=30, 
                                      title='Distribution des prix',
                                      labels={'price': 'Prix (€)', 'count': 'Fréquence'})
                st.plotly_chart(fig_hist, use_container_width=True)
            
            with col2:
                # Boîte à moustaches
                fig_box = px.box(df, y='price', 
                               title='Boîte à moustaches des prix',
                               labels={'price': 'Prix (€)'})
                st.plotly_chart(fig_box, use_container_width=True)
            
            # Distribution par catégorie
            if 'product_category' in df.columns:
                fig_violin = px.violin(df, x='product_category', y='price',
                                      title='Distribution des prix par catégorie',
                                      labels={'price': 'Prix (€)', 'product_category': 'Catégorie'})
                st.plotly_chart(fig_violin, use_container_width=True)
    
    with tab3:
        st.subheader("Comparaisons entre marchés et origines")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Comparaison des marchés
            if 'market_clean' in df.columns and 'price' in df.columns:
                market_prices = df.groupby('market_clean')['price'].mean().sort_values(ascending=False).head(10)
                
                # Conversion en DataFrame pour Plotly
                market_df = market_prices.reset_index()
                market_df.columns = ['market', 'mean_price']
                
                fig_market = px.bar(market_df, x='mean_price', y='market',
                                   orientation='h', title='Top 10 marchés par prix moyen',
                                   labels={'mean_price': 'Prix moyen (€)', 'market': 'Marché'})
                st.plotly_chart(fig_market, use_container_width=True)
        
        with col2:
            # Comparaison des origines
            if 'origin' in df.columns and 'price' in df.columns:
                origin_prices = df.groupby('origin')['price'].mean().sort_values(ascending=False).head(10)
                
                # Conversion en DataFrame pour Plotly
                origin_df = origin_prices.reset_index()
                origin_df.columns = ['origin', 'mean_price']
                
                fig_origin = px.bar(origin_df, x='mean_price', y='origin',
                                   orientation='h', title='Top 10 origines par prix moyen',
                                   labels={'mean_price': 'Prix moyen (€)', 'origin': 'Origine'})
                st.plotly_chart(fig_origin, use_container_width=True)
        
        # Heatmap des prix
        if 'product_clean' in df.columns and 'market_clean' in df.columns:
            st.subheader("Heatmap des prix par produit et marché")
            
            # Sélection des produits et marchés les plus fréquents
            top_products = df['product_clean'].value_counts().head(8).index
            top_markets = df['market_clean'].value_counts().head(6).index
            
            filtered_df = df[
                (df['product_clean'].isin(top_products)) & 
                (df['market_clean'].isin(top_markets))
            ]
            
            pivot_data = filtered_df.pivot_table(values='price', index='product_clean', 
                                              columns='market_clean', aggfunc='mean')
            
            fig_heatmap = px.imshow(pivot_data, title='Heatmap des prix moyens',
                                  labels=dict(x="Marché", y="Produit", color="Prix moyen (€)"))
            st.plotly_chart(fig_heatmap, use_container_width=True)
    
    with tab4:
        st.subheader("Tableau des données")
        
        # Options d'affichage
        col1, col2 = st.columns([1, 3])
        
        with col1:
            show_rows = st.number_input("Nombre de lignes à afficher", min_value=10, max_value=1000, value=50)
        
        with col2:
            search_term = st.text_input("Rechercher dans les données")
        
        # Filtrage des données
        display_df = df.copy()
        
        if search_term:
            mask = display_df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)
            display_df = display_df[mask]
        
        # Affichage du tableau
        st.dataframe(display_df.head(show_rows), use_container_width=True)
        
        # Bouton de téléchargement
        csv = display_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Télécharger les données filtrées (CSV)",
            data=csv,
            file_name='agro_prices_filtered.csv',
            mime='text/csv'
        )

def scraping_page():
    """Page de scraping"""
    st.header("🔄 Scraping des données")
    
    st.markdown("""
    Cette page permet de lancer le scraping des données depuis le site du RNM.
    Le processus collecte les informations sur les prix des produits agroalimentaires.
    """)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("⚙️ Configuration")
        
        # Options de scraping
        categories = {
            'Légumes': 'https://rnm.franceagrimer.fr/prix?LEGUMES',
            'Fruits': 'https://rnm.franceagrimer.fr/prix?FRUITS',
            'Viande': 'https://rnm.franceagrimer.fr/prix?VIANDE',
            'Beurre/Oeuf/Fromage': 'https://rnm.franceagrimer.fr/prix?BEURRE-OEUF-FROMAGE'
        }
        
        selected_categories = st.multiselect(
            "Sélectionnez les catégories à scraper",
            list(categories.keys()),
            default=['Légumes', 'Fruits']
        )
        
        max_products = st.number_input(
            "Nombre maximum de produits par catégorie",
            min_value=1,
            max_value=100,
            value=10
        )
        
        delay = st.number_input(
            "Délai entre les requêtes (secondes)",
            min_value=0,
            max_value=10,
            value=1
        )
        
        if st.button("🚀 Lancer le scraping", type="primary"):
            with st.spinner("Scraping en cours..."):
                try:
                    scraper = AgroDataScraper()
                    all_data = []
                    
                    for category in selected_categories:
                        st.write(f"Scraping de la catégorie: {category}")
                        category_url = categories[category]
                        
                        # Simulation du scraping (à remplacer par le vrai code)
                        category_data = scraper.scrape_category(category, category_url)
                        all_data.extend(category_data)
                    
                    if all_data:
                        # Sauvegarde des données
                        df = pd.DataFrame(all_data)
                        df.to_csv('data/all_agro_prices.csv', index=False, encoding='utf-8')
                        
                        st.success(f"Scraping terminé! {len(all_data)} enregistrements collectés.")
                        
                        # Traitement des données
                        with st.spinner("Traitement des données..."):
                            processor = AgroDataProcessor()
                            processed_df = processor.clean_data(df)
                            enriched_df = processor.add_derived_features(processed_df)
                            enriched_df.to_csv('data/processed_agro_prices.csv', index=False, encoding='utf-8')
                        
                        st.success("Données traitées et sauvegardées!")
                    else:
                        st.warning("Aucune donnée collectée.")
                        
                except Exception as e:
                    st.error(f"Erreur lors du scraping: {e}")
    
    with col2:
        st.subheader("📊 Statistiques du scraping")
        
        # Affichage des statistiques si les données existent
        if os.path.exists('data/all_agro_prices.csv'):
            try:
                df = pd.read_csv('data/all_agro_prices.csv', encoding='utf-8')
                
                st.metric("Total enregistrements", len(df))
                
                if 'product' in df.columns:
                    st.metric("Produits uniques", df['product'].nunique())
                
                if 'market' in df.columns:
                    st.metric("Marchés uniques", df['market'].nunique())
                
                if 'date' in df.columns:
                    st.metric("Plage de dates", f"{df['date'].min()} - {df['date'].max()}")
                
                # Aperçu des données
                st.subheader("Aperçu des données")
                st.dataframe(df.head(10))
                
            except Exception as e:
                st.error(f"Erreur lors de la lecture des données: {e}")
        else:
            st.info("Aucune donnée disponible. Lancez le scraping pour collecter des données.")

def analyses_page():
    """Page d'analyses détaillées"""
    st.header("📈 Analyses Détaillées")
    
    df = load_data()
    if df is None or df.empty:
        st.warning("Aucune donnée disponible pour l'analyse.")
        return
    
    # Analyse par saison
    if 'season' in df.columns and 'price' in df.columns:
        st.subheader("🌍 Analyse saisonnière")
        
        seasonal_stats = df.groupby('season')['price'].agg(['mean', 'count', 'std']).reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_season_bar = px.bar(seasonal_stats, x='season', y='mean',
                                   title='Prix moyen par saison',
                                   labels={'mean': 'Prix moyen (€)', 'season': 'Saison'})
            st.plotly_chart(fig_season_bar, use_container_width=True)
        
        with col2:
            fig_season_count = px.bar(seasonal_stats, x='season', y='count',
                                     title='Nombre d\'observations par saison',
                                     labels={'count': 'Nombre', 'season': 'Saison'})
            st.plotly_chart(fig_season_count, use_container_width=True)
    
    # Analyse des produits les plus chers/bon marché
    if 'product_clean' in df.columns and 'price' in df.columns:
        st.subheader("💰 Analyse des prix par produit")
        
        product_stats = df.groupby('product_clean')['price'].agg(['mean', 'count']).reset_index()
        product_stats = product_stats[product_stats['count'] >= 5]  # Filtre les produits avec peu de données
        
        col1, col2 = st.columns(2)
        
        with col1:
            most_expensive = product_stats.nlargest(10, 'mean')
            fig_expensive = px.bar(most_expensive, x='mean', y='product_clean',
                                  orientation='h', title='Top 10 produits les plus chers',
                                  labels={'mean': 'Prix moyen (€)', 'product_clean': 'Produit'})
            st.plotly_chart(fig_expensive, use_container_width=True)
        
        with col2:
            cheapest = product_stats.nsmallest(10, 'mean')
            fig_cheap = px.bar(cheapest, x='mean', y='product_clean',
                             orientation='h', title='Top 10 produits les moins chers',
                             labels={'mean': 'Prix moyen (€)', 'product_clean': 'Produit'})
            st.plotly_chart(fig_cheap, use_container_width=True)
    
    # Analyse des corrélations
    if 'price' in df.columns:
        st.subheader("🔗 Analyse des corrélations")
        
        # Création de variables numériques pour la corrélation
        numeric_df = df.copy()
        
        # Conversion des variables catégorielles en numériques
        if 'product_category' in numeric_df.columns:
            numeric_df['product_category_code'] = pd.Categorical(numeric_df['product_category']).codes
        
        if 'season' in numeric_df.columns:
            numeric_df['season_code'] = pd.Categorical(numeric_df['season']).codes
        
        # Sélection des colonnes numériques
        numeric_cols = numeric_df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) > 1:
            correlation_matrix = numeric_df[numeric_cols].corr()
            
            fig_corr = px.imshow(correlation_matrix, 
                                title='Matrice de corrélation',
                                color_continuous_scale='RdBu_r')
            st.plotly_chart(fig_corr, use_container_width=True)

def ai_predictions_page():
    """Page avec fonctionnalités d'IA et de prédiction"""
    st.header("🤖 Intelligence Artificielle & Prédictions")
    
    df = load_data()
    if df is None:
        st.error("Impossible de charger les données")
        return
    
    interactive = InteractiveFeatures(df)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Prédictions", "🎯 Modèle ML", "📊 Importance Features", "⚠️ Alertes"])
    
    with tab1:
        st.subheader("Prédiction des Prix Futurs")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            product = st.selectbox("Sélectionnez un produit", sorted(df['product_clean'].unique()))
            days_ahead = st.slider("Jours à prédire", 1, 30, 7)
            
        with col2:
            st.markdown("### 📋 Paramètres")
            st.info(f"Modèle entraîné sur les données historiques du produit sélectionné")
        
        if st.button("🔮 Prédire les prix", type="primary"):
            with st.spinner("Entraînement du modèle et prédiction en cours..."):
                predictions, error = interactive.predict_future_prices(days_ahead, product)
                
                if error:
                    st.error(error)
                else:
                    st.success(f"Prédictions générées pour les {days_ahead} prochains jours")
                    
                    # Graphique des prédictions
                    pred_df = pd.DataFrame(predictions)
                    pred_df['date'] = pd.to_datetime(pred_df['date'])
                    
                    # Données historiques pour comparaison
                    historical = df[df['product_clean'] == product].tail(30)
                    
                    fig = go.Figure()
                    
                    # Prix historiques
                    fig.add_trace(go.Scatter(
                        x=historical['date'],
                        y=historical['price'],
                        mode='lines+markers',
                        name='Prix historiques',
                        line=dict(color='blue')
                    ))
                    
                    # Prédictions
                    fig.add_trace(go.Scatter(
                        x=pred_df['date'],
                        y=pred_df['predicted_price'],
                        mode='lines+markers',
                        name='Prédictions',
                        line=dict(color='red', dash='dash')
                    ))
                    
                    fig.update_layout(
                        title=f'Prédictions des prix pour {product}',
                        xaxis_title='Date',
                        yaxis_title='Prix (€)',
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Tableau des prédictions
                    st.subheader("📋 Détail des prédictions")
                    st.dataframe(pred_df, use_container_width=True)
    
    with tab2:
        st.subheader("🎯 Modèle de Machine Learning")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_product = st.selectbox("Produit pour l'analyse", sorted(df['product_clean'].unique()), key="ml_product")
            selected_market = st.selectbox("Marché (optionnel)", ["Tous"] + sorted(df['market_clean'].unique()), key="ml_market")
            selected_origin = st.selectbox("Origine (optionnelle)", ["Toutes"] + sorted(df['origin'].unique()), key="ml_origin")
        
        with col2:
            st.markdown("### 📊 Performance")
        
        if st.button("🚀 Entraîner le modèle", type="primary"):
            with st.spinner("Entraînement du modèle en cours..."):
                market = None if selected_market == "Tous" else selected_market
                origin = None if selected_origin == "Toutes" else selected_origin
                
                model_result, error = interactive.price_prediction_model(
                    product=selected_product, market=market, origin=origin
                )
                
                if error:
                    st.error(error)
                else:
                    st.success("✅ Modèle entraîné avec succès!")
                    
                    # Métriques de performance
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("MAE", f"{model_result['mae']:.2f}€")
                    
                    with col2:
                        st.metric("R²", f"{model_result['r2']:.3f}")
                    
                    with col3:
                        st.metric("Taille échantillon", model_result['sample_size'])
                    
                    # Importance des features
                    st.subheader("🎯 Importance des caractéristiques")
                    
                    fig = px.bar(
                        model_result['feature_importance'],
                        x='importance',
                        y='feature',
                        orientation='h',
                        title='Importance des caractéristiques'
                    )
                    st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("📊 Analyse Comparative des Features")
        
        # Analyse globale de l'importance des features
        all_products = sorted(df['product_clean'].unique())
        selected_products = st.multiselect("Sélectionnez des produits à comparer", all_products, default=all_products[:5])
        
        if selected_products:
            feature_comparison = []
            
            for product in selected_products:
                model_result, error = interactive.price_prediction_model(product=product)
                if not error:
                    for _, row in model_result['feature_importance'].iterrows():
                        feature_comparison.append({
                            'product': product,
                            'feature': row['feature'],
                            'importance': row['importance']
                        })
            
            if feature_comparison:
                comparison_df = pd.DataFrame(feature_comparison)
                
                # Heatmap de comparaison
                pivot_df = comparison_df.pivot(index='feature', columns='product', values='importance')
                
                fig = px.imshow(
                    pivot_df,
                    title='Importance des features par produit',
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader("⚠️ Système d'Alertes Intelligent")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            alert_product = st.selectbox("Produit à surveiller", sorted(df['product_clean'].unique()))
            threshold = st.slider("Seuil d'alerte (%)", 5, 50, 20)
        
        with col2:
            st.markdown("### 🔔 Configuration")
            st.info(f"Alerte si variation > {threshold}%")
        
        if st.button("🔍 Analyser les alertes", type="primary"):
            alerts_data = interactive.create_alert_system(alert_product, threshold)
            
            if alerts_data['alerts']:
                st.warning(f"🚨 {alerts_data['message']}")
                
                for alert in alerts_data['alerts']:
                    if alert['type'] == 'variation_significative':
                        st.error(f"📈 {alert['message']} - {alert['date']} - {alert['marche']}")
                    elif alert['type'] == 'prix_eleve':
                        st.warning(f"💰 {alert['message']} - {alert['date']} - {alert['marche']}")
                    else:
                        st.info(f"📉 {alert['message']} - {alert['date']} - {alert['marche']}")
                
                # Statistiques
                st.subheader("📊 Statistiques du produit")
                stats = alerts_data['stats']
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Prix moyen", f"{stats['prix_moyen']:.2f}€")
                with col2:
                    st.metric("Prix min", f"{stats['prix_min']:.2f}€")
                with col3:
                    st.metric("Prix max", f"{stats['prix_max']:.2f}€")
                with col4:
                    st.metric("Volatilité", f"{stats['volatilite']:.2f}")
            else:
                st.success(f"✅ {alerts_data['message']}")

def interactive_tools_page():
    """Page avec outils interactifs avancés"""
    st.header("⚙️ Outils Interactifs Avancés")
    
    df = load_data()
    if df is None:
        st.error("Impossible de charger les données")
        return
    
    interactive = InteractiveFeatures(df)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Comparateur", "📊 Analyse Marchés", "🌡️ Analyse Saisonnière", "📤 Export"])
    
    with tab1:
        st.subheader("🔍 Comparateur Interactif de Prix")
        
        comparison_data = interactive.create_price_comparison_tool()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_products = st.multiselect("Produits à comparer", comparison_data['products'], default=comparison_data['products'][:3])
        
        with col2:
            selected_markets = st.multiselect("Marchés", comparison_data['markets'], default=comparison_data['markets'][:3])
        
        with col3:
            selected_origins = st.multiselect("Origines", comparison_data['origins'], default=comparison_data['origins'][:3])
        
        if selected_products:
            st.subheader("📈 Évolution des prix comparés")
            
            fig = go.Figure()
            
            colors = px.colors.qualitative.Set1
            
            for i, product in enumerate(selected_products):
                evolution_data = interactive.get_price_evolution_data(product)
                
                if not evolution_data.empty:
                    fig.add_trace(go.Scatter(
                        x=evolution_data['date'],
                        y=evolution_data['prix_moyen'],
                        mode='lines+markers',
                        name=product,
                        line=dict(color=colors[i % len(colors)])
                    ))
            
            fig.update_layout(
                title='Comparaison des prix',
                xaxis_title='Date',
                yaxis_title='Prix (€)',
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Tableau comparatif
            comparison_table = []
            
            for product in selected_products:
                product_data = df[df['product_clean'] == product]
                
                comparison_table.append({
                    'Produit': product,
                    'Prix moyen': product_data['price'].mean(),
                    'Prix min': product_data['price'].min(),
                    'Prix max': product_data['price'].max(),
                    'Écart type': product_data['price'].std(),
                    'Nombre observations': len(product_data)
                })
            
            comparison_df = pd.DataFrame(comparison_table)
            st.dataframe(comparison_df.round(2), use_container_width=True)
    
    with tab2:
        st.subheader("📊 Analyse Comparative des Marchés")
        
        market_analysis = interactive.create_market_analysis()
        
        # Métriques globales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Nombre de marchés", len(market_analysis))
        with col2:
            st.metric("Prix moyen global", f"{df['price'].mean():.2f}€")
        with col3:
            st.metric("Marché le plus cher", market_analysis.index[0])
        with col4:
            st.metric("Marché le moins cher", market_analysis.index[-1])
        
        # Graphique des marchés
        fig = px.bar(
            x=market_analysis['prix_moyen'].head(10),
            y=market_analysis.head(10).index,
            orientation='h',
            title='Top 10 marchés par prix moyen'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Tableau détaillé
        st.subheader("📋 Détail des marchés")
        st.dataframe(market_analysis.round(2), use_container_width=True)
    
    with tab3:
        st.subheader("🌡️ Analyse Saisonnière")
        
        seasonal_analysis = interactive.create_seasonal_analysis()
        
        # Sélection de produits
        selected_seasonal_products = st.multiselect(
            "Produits pour l'analyse saisonnière",
            sorted(df['product_clean'].unique()),
            default=sorted(df['product_clean'].unique())[:5]
        )
        
        if selected_seasonal_products:
            seasonal_filtered = seasonal_analysis[seasonal_analysis['product_clean'].isin(selected_seasonal_products)]
            
            # Graphique saisonnier
            fig = px.box(
                seasonal_filtered,
                x='season',
                y='prix_moyen',
                color='product_clean',
                title='Distribution des prix par saison'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Tableau saisonnier
            st.dataframe(seasonal_filtered.round(2), use_container_width=True)
    
    with tab4:
        st.subheader("📤 Export de Données Personnalisé")
        
        st.markdown("### 🔍 Filtres d'export")
        
        col1, col2 = st.columns(2)
        
        with col1:
            export_products = st.multiselect("Produits", sorted(df['product_clean'].unique()))
            export_markets = st.multiselect("Marchés", sorted(df['market_clean'].unique()))
            export_origins = st.multiselect("Origines", sorted(df['origin'].unique()))
        
        with col2:
            date_start = st.date_input("Date de début", df['date'].min().date())
            date_end = st.date_input("Date de fin", df['date'].max().date())
            price_min = st.number_input("Prix minimum", min_value=0.0, value=float(df['price'].min()))
            price_max = st.number_input("Prix maximum", min_value=0.0, value=float(df['price'].max()))
        
        if st.button("📤 Exporter les données filtrées", type="primary"):
            filters = {
                'product': export_products,
                'market': export_markets,
                'origin': export_origins,
                'date_start': date_start,
                'date_end': date_end,
                'price_min': price_min,
                'price_max': price_max
            }
            
            filtered_data = interactive.export_filtered_data(filters)
            
            st.success(f"✅ {len(filtered_data)} enregistrements trouvés")
            st.dataframe(filtered_data, use_container_width=True)
            
            # Bouton de téléchargement
            csv = filtered_data.to_csv(index=False)
            st.download_button(
                label="📥 Télécharger en CSV",
                data=csv,
                file_name=f"agro_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

def about_page():
    """Page à propos"""
    st.header("ℹ️ À propos du projet")
    
    st.markdown("""
    ## 🎯 Objectif du projet
    
    Ce projet a été développé dans le cadre d'un portfolio pour démontrer des compétences en :
    - **Web scraping** avec Python
    - **Analyse de données** avec Pandas
    - **Visualisation** avec Plotly
    - **Développement web** avec Streamlit
    
    ## 📊 Source des données
    
    Les données proviennent du **Réseau des Nouvelles des Marchés (RNM)**, un service public français 
    qui collecte et diffuse les informations sur les prix des produits agroalimentaires.
    
    ### Site source : [rnm.franceagrimer.fr](https://rnm.franceagrimer.fr)
    
    ## 🛠️ Stack technique
    
    ### Backend
    - **Python 3.8+**
    - **BeautifulSoup4** : Parsing HTML
    - **Requests** : Requêtes HTTP
    - **Pandas** : Manipulation de données
    - **NumPy** : Calculs numériques
    
    ### Visualisation
    - **Plotly** : Graphiques interactifs
    - **Matplotlib** : Graphiques statiques
    - **Seaborn** : Visualisations statistiques
    
    ### Interface web
    - **Streamlit** : Dashboard web
    - **HTML/CSS** : Mise en page
    
    ## 📁 Structure du projet
    
    ```
    agro_data_scraping/
    ├── app.py                 # Application Streamlit principale
    ├── requirements.txt       # Dépendances Python
    ├── src/                   # Code source
    │   ├── scraper.py        # Script de scraping
    │   ├── data_processor.py # Traitement des données
    │   └── visualizations.py # Création des graphiques
    ├── data/                  # Données collectées
    ├── static/               # Fichiers statiques
    └── notebooks/             # Notebooks d'analyse
    ```
    
    ## 🚀 Comment utiliser
    
    1. **Installation** :
       ```bash
       pip install -r requirements.txt
       ```
    
    2. **Lancement du scraping** :
       ```bash
       python src/scraper.py
       ```
    
    3. **Traitement des données** :
       ```bash
       python src/data_processor.py
       ```
    
    4. **Génération des graphiques** :
       ```bash
       python src/visualizations.py
       ```
    
    5. **Lancement du dashboard** :
       ```bash
       streamlit run app.py
       ```
    
    ## 📈 Métriques et KPIs
    
    - **Fréquence de mise à jour** : Quotidienne
    - **Nombre de catégories** : 4+ (Légumes, Fruits, Viande, Produits laitiers)
    - **Nombre de marchés** : 20+
    - **Période couverte** : Variable selon les données disponibles
    
    ## 🔮 Évolutions possibles
    
    - [ ] Ajout de plus de catégories de produits
    - [ ] Intégration de données historiques
    - [ ] Modélisation prédictive des prix
    - [ ] Alertes sur les variations de prix
    - [ ] API REST pour l'accès aux données
    
    ## 👤 Auteur
    
    Projet développé pour démontrer des compétences en data science et web scraping.
    
    ---
    *Ce projet est à but éducatif et respecte les conditions d'utilisation du site source.*
    """)

# Navigation entre les pages
if page == "🏠 Accueil":
    home_page()
elif page == "📊 Dashboard":
    dashboard_page()
elif page == "🔄 Scraping":
    scraping_page()
elif page == "📈 Analyses":
    analyses_page()
elif page == "🤖 IA & Prédictions":
    ai_predictions_page()
elif page == "⚙️ Outils Interactifs":
    interactive_tools_page()
elif page == "🚀 Features Avancées":
    advanced_features_page()
elif page == "ℹ️ À propos":
    about_page()

# Footer
st.markdown("---")
st.markdown("🥬 Dashboard Agroalimentaire | Données RNM FranceAgriMer ")
