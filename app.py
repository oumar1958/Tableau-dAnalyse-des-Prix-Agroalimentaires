import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
import numpy as np

# Ajout du chemin vers le dossier src
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from scraper import AgroDataScraper
from data_processor import AgroDataProcessor
from visualizations import AgroDataVisualizer

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Agroalimentaire",
    page_icon="🥬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Titre principal
st.title("🥬 Dashboard d'Analyse des Prix Agroalimentaires")
st.markdown("*Analyse des données du Réseau des Nouvelles des Marchés (RNM)*")

# Sidebar pour la navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox(
    "Choisissez une page",
    ["🏠 Accueil", "📊 Dashboard", "🔄 Scraping", "📈 Analyses", "ℹ️ À propos"]
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

def home_page():
    """Page d'accueil"""
    st.header("🏠 Bienvenue sur le Dashboard Agroalimentaire")
    
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
        
        ### 📈 Métriques clés
        
        - Mise à jour quotidienne
        - Plus de 10 catégories de produits
        - Analyse multi-marchés
        """)
    
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
            if 'price' in df.columns:
                avg_price = df['price'].mean()
                st.metric("Prix moyen", f"{avg_price:.2f}€")

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
elif page == "ℹ️ À propos":
    about_page()

# Footer
st.markdown("---")
st.markdown("🥬 Dashboard Agroalimentaire | Données RNM FranceAgriMer | Projet Portfolio")
