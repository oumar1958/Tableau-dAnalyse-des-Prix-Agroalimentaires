

# 🎯 Objectif du Projet

L’objectif de ce projet est de concevoir une plateforme décisionnelle complète permettant d’analyser, modéliser et visualiser les dynamiques du secteur agroalimentaire à partir de données collectées automatiquement sur le web.

## 🚀 Fonctionnalités Principales

### 📊 **Dashboard Principal**
- **Vue d'ensemble** avec métriques en temps réel
- **Graphiques interactifs** (évolution, distribution, heatmap)
- **Filtres dynamiques** par produit, marché, origine, période
- **Export de données** personnalisé

### 🤖 **Intelligence Artificielle & Prédictions**
- **Prédiction des prix** sur 1-30 jours avec RandomForest
- **Modèle ML entraînable** avec métriques (MAE, R²)
- **Importance des features** et analyse comparative
- **Système d'alertes** intelligent sur variations de prix

### 🚀 **Features Avancées - Niveau Expert**
- 🧠 **Analyseur de Sentiment du Marché** (score 0-100)
- 🔍 **Détecteur d'Anomalies** avec Isolation Forest
- 🎯 **Clustering Intelligent** des marchés (K-Means)
- 📊 **Analyse d'Élasticité** des prix
- 📡 **Monitoring en Temps Réel**
- 💼 **Optimiseur de Portefeuille** (Sharpe Ratio)

### ⚙️ **Outils Interactifs**
- **Comparateur de prix** multi-produits
- **Analyse comparative des marchés**
- **Analyse saisonnière** avancée
- **Export personnalisé** avec filtres multiples

## 📊 Source des Données

**Réseau des Nouvelles des Marchés (RNM)** - FranceAgriMer
- 🌐 Site officiel : [rnm.franceagrimer.fr](https://rnm.franceagrimer.fr)
- 📈 Données publiques sur les prix agroalimentaires
- 🔄 Mise à jour quotidienne des cotations
- 🏪 12+ marchés français couverts
- 🥬 4+ catégories de produits



### Architecture
```
📁 agro_data_scraping/
├── 📄 app.py                    # Application Streamlit principale
├── 📄 app_advanced.py           # Features avancées
├── 📄 main.py                   # Pipeline orchestration
├── 📄 requirements.txt          # Dépendances
├── 📁 src/                      # Code source modulaire
│   ├── 📄 scraper.py           # Web scraping
│   ├── 📄 data_processor.py    # Traitement données
│   ├── 📄 visualizations.py    # Graphiques
│   ├── 📄 interactive_features.py # Fonctionnalités IA
│   ├── 📄 advanced_features.py # Features expert
│   └── 📄 demo_data.py         # Générateur données
├── 📁 data/                     # Données brutes et traitées
├── 📁 notebooks/               # Analyses exploratoires
├── 📁 static/                  # Fichiers statiques
```

## 🚀 Installation & Démarrage Rapide

### 1️⃣ **Clôner le projet**
```bash
git clone https://github.com/oumar1958/Tableau-dAnalyse-des-Prix-Agroalimentaires.git
cd agro_data_scraping
```

### 2️⃣ **Environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3️⃣ **Installation des dépendances**
```bash
pip install -r requirements.txt
```

### 4️⃣ **Génération des données de démonstration**
```bash
python src/demo_data.py
```

### 5️⃣ **Lancement du dashboard**
```bash
streamlit run app.py
```

## 📖 Utilisation du Dashboard

### 🏠 **Page d'Accueil**
- Vue d'ensemble avec statistiques en temps réel
- Graphiques rapides (camembert, évolution)
- Navigation rapide vers toutes les fonctionnalités

### 📊 **Dashboard Principal**
- Filtres multi-dimensionnels
- Visualisations interactives
- Export de données personnalisé

### 🤖 **IA & Prédictions**
- Prédiction des prix futurs
- Entraînement de modèles ML
- Système d'alertes intelligent

### 🚀 **Features Avancées**
- Analyse de sentiment du marché
- Détection d'anomalies
- Clustering de marchés
- Optimisation de portefeuille



## 📈 Métriques & Performance

### 📊 **Données Traitées**
- ✅ **681 enregistrements** générés
- ✅ **41 produits** uniques
- ✅ **12 marchés** français
- ✅ **8 origines** différentes
- ✅ **Période** : 3 mois de données

### 🤖 **Modèles ML**
- 🎯 **RandomForest** : Prédiction de prix (R² > 0.85)
- 🔍 **Isolation Forest** : Détection d'anomalies
- 🎯 **K-Means** : Clustering de marchés
- 📊 **Analyse financière** : Sharpe Ratio, élasticité

### 🚀 **Performance**
- ⚡ **Chargement** : < 2 secondes
- 🔄 **Mise à jour** : Temps réel
- 📱 **Responsive** : Mobile & Desktop
- 🎨 **Design** : Moderne & intuitif


## 🌟 Points Forts Techniques

### 🏗️ **Architecture**
- **Code modulaire** et maintenable
- **Gestion d'erreurs** robuste
- **Logging** complet
- **Tests** intégrés

### 🤖 **Machine Learning**
- **Modèles supervisés** et non supervisés
- **Validation croisée**
- **Métriques de performance**
- **Persistance** des modèles

### 📊 **Visualisations**
- **Graphiques 3D** interactifs
- **Dashboard responsive**
- **Export multiple** (PNG, HTML, CSV)
- **Thème personnalisé**


## 👨‍💻 Auteur

Développé par **Oumar Abdramane ALLAWAN** 

- 📧 Contact : [oumarallawan7@gmail.com]
- 🌐 LinkedIn : [[https://www.linkedin.com/in/oumar-abdramane-allawan-628b19250/]
- 💼 GitHub : [oumar1958](https://github.com/oumar1958)

