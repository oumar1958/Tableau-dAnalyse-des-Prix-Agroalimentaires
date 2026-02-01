# 🥬 Dashboard Agroalimentaire - Projet de Scraping et Analyse

Un projet complet de web scraping et d'analyse de données agroalimentaires pour votre portfolio, avec dashboard interactif.


## 📊 Source des données

**Réseau des Nouvelles des Marchés (RNM)** - FranceAgriMer
- Site officiel : [rnm.franceagrimer.fr](https://rnm.franceagrimer.fr)
- Données publiques sur les prix des produits agroalimentaires
- Mise à jour quotidienne des cotations

### Catégories de données collectées
- 🥬 **Légumes** : Tomates, carottes, salades, etc.
- 🍎 **Fruits** : Pommes, oranges, cerises, etc.
- 🥩 **Viande** : Bœuf, porc, volaille
- 🧀 **Produits laitiers** : Beurre, œufs, fromages

## 🛠️ Stack Technique

### Backend & Scraping
- **Python 3.8+** : Langage principal
- **BeautifulSoup4** : Parsing HTML
- **Requests** : Requêtes HTTP avec gestion d'erreurs
- **Fake UserAgent** : Rotation d'en-têtes HTTP
- **Pandas** : Manipulation et analyse de données
- **NumPy** : Calculs numériques

### Visualisation & Analyse
- **Plotly** : Graphiques interactifs
- **Matplotlib** : Graphiques statiques
- **Seaborn** : Visualisations statistiques avancées

### Interface Web
- **Streamlit** : Dashboard web interactif
- **HTML/CSS** : Mise en page responsive

## 📁 Structure du Projet

```
agro_data_scraping/
├── app.py                    # Application Streamlit principale
├── requirements.txt          # Dépendances Python
├── README.md                # Documentation du projet
├── src/                     # Code source modularisé
│   ├── scraper.py          # Script de scraping web
│   ├── data_processor.py   # Nettoyage et traitement des données
│   └── visualizations.py   # Génération des graphiques
├── data/                    # Données collectées et traitées
│   ├── all_agro_prices.csv     # Données brutes
│   └── processed_agro_prices.csv # Données nettoyées
├── static/                  # Fichiers statiques
│   └── plots/             # Graphiques générés
├── notebooks/              # Notebooks d'analyse (optionnel)
└── venv/                   # Environnement virtuel
```

## 🚀 Installation et Démarrage

### 1. Clonage et environnement
```bash
# Cloner le projet
git clone <https://github.com/oumar1958/Tableau-dAnalyse-des-Prix-Agroalimentaires>
cd agro_data_scraping

# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2. Installation des dépendances
```bash
pip install -r requirements.txt
```

### 3. Exécution du projet

#### Option A : Scraping complet (recommandé)
```bash
# 1. Lancer le scraping des données
python src/scraper.py

# 2. Traiter les données collectées
python src/data_processor.py

# 3. Générer les visualisations
python src/visualizations.py

# 4. Lancer le dashboard
streamlit run app.py
```

#### Option B : Lancement rapide du dashboard
```bash
# Le dashboard inclut des fonctions de scraping intégrées
streamlit run app.py
```



## 📋 Fonctionnalités du Dashboard

### 🏠 Page d'accueil
- Vue d'ensemble du projet
- Statistiques en temps réel
- Technologies utilisées

### 📊 Dashboard Principal
- **Évolution temporelle** des prix
- **Distribution** des prix par catégorie
- **Comparaisons** entre marchés et origines
- **Heatmap** interactif des prix
- **Tableau de données** filtrable et exportable

### 🔄 Page de Scraping
- Configuration du scraping
- Sélection des catégories
- Monitoring en temps réel
- Statistiques de collecte

### 📈 Analyses Détaillées
- Analyse saisonnière
- Produits les plus chers/bon marché
- Matrice de corrélation
- Tendances par marché

### ℹ️ Page À propos
- Documentation complète
- Stack technique
- Structure du projet
- Évolutions possibles


## 👤 Contributeur

Oumar Abdramane ALLAWAN

---

