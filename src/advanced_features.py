import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import streamlit as st
from datetime import datetime, timedelta
import json
import io
import base64

class AdvancedFeatures:
    """Fonctionnalités avancées pour un projet de niveau expert"""
    
    def __init__(self, df):
        self.df = df.copy()
        self.prepare_advanced_data()
    
    def prepare_advanced_data(self):
        """Prépare les données pour les analyses avancées"""
        if 'date' in self.df.columns:
            self.df['date'] = pd.to_datetime(self.df['date'])
            self.df['day_of_week'] = self.df['date'].dt.dayofweek
            self.df['week_of_year'] = self.df['date'].dt.isocalendar().week
            self.df['quarter'] = self.df['date'].dt.quarter
    
    def create_market_sentiment_analyzer(self):
        """Analyseur de sentiment du marché"""
        # Simulation d'indicateurs de sentiment
        sentiment_data = []
        
        for product in self.df['product_clean'].unique():
            product_data = self.df[self.df['product_clean'] == product]
            
            # Calcul de métriques de sentiment
            price_volatility = product_data['price'].std() / product_data['price'].mean()
            price_trend = self.calculate_price_trend(product_data)
            volume_stability = len(product_data) / 30  # Stabilité des observations
            
            # Score de sentiment (0-100)
            sentiment_score = 50 + (price_trend * 10) - (price_volatility * 20) + (volume_stability * 5)
            sentiment_score = max(0, min(100, sentiment_score))
            
            sentiment_data.append({
                'product': product,
                'sentiment_score': sentiment_score,
                'volatility': price_volatility,
                'trend': price_trend,
                'stability': volume_stability,
                'recommendation': self.get_sentiment_recommendation(sentiment_score)
            })
        
        return pd.DataFrame(sentiment_data)
    
    def calculate_price_trend(self, product_data):
        """Calcule la tendance des prix"""
        if len(product_data) < 2:
            return 0
        
        product_data = product_data.sort_values('date')
        prices = product_data['price'].values
        
        # Régression linéaire simple
        x = np.arange(len(prices))
        slope = np.polyfit(x, prices, 1)[0]
        
        # Normalisation
        mean_price = np.mean(prices)
        normalized_slope = slope / mean_price * 100
        
        return normalized_slope
    
    def get_sentiment_recommendation(self, score):
        """Génère une recommandation basée sur le sentiment"""
        if score >= 70:
            return "🟢 Fort - Achat recommandé"
        elif score >= 50:
            return "🟡 Modéré - Surveillance"
        elif score >= 30:
            return "🟠 Faible - Prudence"
        else:
            return "🔴 Très faible - Éviter"
    
    def create_price_anomaly_detector(self):
        """Détecteur d'anomalies de prix avec Isolation Forest"""
        anomalies = []
        
        for product in self.df['product_clean'].unique():
            product_data = self.df[self.df['product_clean'] == product].copy()
            
            if len(product_data) < 10:
                continue
            
            # Préparation des features pour la détection d'anomalies
            features = ['price', 'month', 'day_of_week']
            X = product_data[features].values
            
            # Standardisation
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Isolation Forest
            iso_forest = IsolationForest(contamination=0.1, random_state=42)
            anomaly_labels = iso_forest.fit_predict(X_scaled)
            
            # Identification des anomalies
            product_data['is_anomaly'] = anomaly_labels == -1
            anomaly_records = product_data[product_data['is_anomaly']]
            
            for _, record in anomaly_records.iterrows():
                anomalies.append({
                    'product': product,
                    'date': record['date'],
                    'price': record['price'],
                    'market': record['market_clean'],
                    'anomaly_score': iso_forest.decision_function(scaler.transform([record[features].values]))[0],
                    'reason': self.get_anomaly_reason(record, product_data)
                })
        
        return pd.DataFrame(anomalies)
    
    def get_anomaly_reason(self, record, product_data):
        """Détermine la raison de l'anomalie"""
        price_mean = product_data['price'].mean()
        price_std = product_data['price'].std()
        
        if record['price'] > price_mean + 2 * price_std:
            return "Prix anormalement élevé"
        elif record['price'] < price_mean - 2 * price_std:
            return "Prix anormalement bas"
        else:
            return "Pattern inhabituel détecté"
    
    def create_market_clustering(self):
        """Clustering des marchés par comportement de prix"""
        # Préparation des données pour le clustering
        market_features = []
        
        for market in self.df['market_clean'].unique():
            market_data = self.df[self.df['market_clean'] == market]
            
            features = {
                'market': market,
                'avg_price': market_data['price'].mean(),
                'price_volatility': market_data['price'].std() / market_data['price'].mean(),
                'product_diversity': market_data['product_clean'].nunique(),
                'observation_frequency': len(market_data),
                'avg_price_range': market_data['price'].max() - market_data['price'].min()
            }
            market_features.append(features)
        
        features_df = pd.DataFrame(market_features)
        
        # Standardisation pour le clustering
        feature_columns = ['avg_price', 'price_volatility', 'product_diversity', 'observation_frequency', 'avg_price_range']
        X = features_df[feature_columns].values
        X_scaled = StandardScaler().fit_transform(X)
        
        # K-Means clustering
        kmeans = KMeans(n_clusters=4, random_state=42)
        cluster_labels = kmeans.fit_predict(X_scaled)
        
        features_df['cluster'] = cluster_labels
        features_df['cluster_name'] = features_df['cluster'].map({
            0: "Premium - Prix élevés, faible volatilité",
            1: "Volume - Beaucoup d'observations, prix moyens",
            2: "Diversifié - Grande variété de produits",
            3: "Volatil - Prix instables"
        })
        
        return features_df, kmeans, X_scaled
    
    def create_price_elasticity_analyzer(self):
        """Analyseur d'élasticité des prix"""
        elasticity_data = []
        
        for product in self.df['product_clean'].unique():
            product_data = self.df[self.df['product_clean'] == product].sort_values('date')
            
            if len(product_data) < 5:
                continue
            
            # Simulation d'élasticité basée sur les variations de prix
            prices = product_data['price'].values
            price_changes = np.diff(prices) / prices[:-1]
            
            # Élasticité (simplifiée)
            elasticity = np.corrcoef(price_changes[1:], price_changes[:-1])[0, 1]
            if np.isnan(elasticity):
                elasticity = 0
            
            elasticity_data.append({
                'product': product,
                'elasticity': abs(elasticity),
                'elasticity_category': self.get_elasticity_category(abs(elasticity)),
                'price_sensitivity': self.get_price_sensitivity(abs(elasticity))
            })
        
        return pd.DataFrame(elasticity_data)
    
    def get_elasticity_category(self, elasticity):
        """Catégorise l'élasticité"""
        if elasticity > 0.8:
            return "Très élastique"
        elif elasticity > 0.5:
            return "Élastique"
        elif elasticity > 0.2:
            return "Peu élastique"
        else:
            return "Inélastique"
    
    def get_price_sensitivity(self, elasticity):
        """Détermine la sensibilité au prix"""
        if elasticity > 0.7:
            return "🔴 Très sensible"
        elif elasticity > 0.4:
            return "🟡 Sensible"
        else:
            return "🟢 Peu sensible"
    
    def create_real_time_monitoring(self):
        """Simulation de monitoring en temps réel"""
        # Données simulées pour le monitoring
        current_data = []
        
        for product in self.df['product_clean'].unique()[:10]:  # Top 10 produits
            product_data = self.df[self.df['product_clean'] == product].tail(7)  # 7 derniers jours
            
            if len(product_data) > 0:
                current_price = product_data.iloc[-1]['price']
                prev_price = product_data.iloc[-2]['price'] if len(product_data) > 1 else current_price
                
                price_change = ((current_price - prev_price) / prev_price) * 100 if prev_price != 0 else 0
                
                current_data.append({
                    'product': product,
                    'current_price': current_price,
                    'price_change': price_change,
                    'trend': '📈' if price_change > 0 else '📉' if price_change < 0 else '➡️',
                    'status': self.get_price_status(price_change),
                    'last_update': product_data.iloc[-1]['date']
                })
        
        return pd.DataFrame(current_data)
    
    def get_price_status(self, change):
        """Détermine le statut du prix"""
        if change > 5:
            return "🔴 Hausse forte"
        elif change > 2:
            return "🟡 Hausse modérée"
        elif change < -5:
            return "🟢 Baisse forte"
        elif change < -2:
            return "🔵 Baisse modérée"
        else:
            return "⚪ Stable"
    
    def create_predictive_dashboard(self):
        """Tableau de bord prédictif avancé"""
        predictions = []
        
        for product in self.df['product_clean'].unique()[:15]:  # Top 15 produits
            product_data = self.df[self.df['product_clean'] == product].sort_values('date')
            
            if len(product_data) < 10:
                continue
            
            # Prédictions simplifiées basées sur les tendances
            recent_prices = product_data.tail(10)['price'].values
            trend = np.polyfit(range(len(recent_prices)), recent_prices, 1)[0]
            
            # Prédiction pour les 7 prochains jours
            last_price = recent_prices[-1]
            for day in range(1, 8):
                predicted_price = last_price + (trend * day)
                confidence = max(0.5, 1.0 - (day * 0.1))  # Confiance décroissante
                
                predictions.append({
                    'product': product,
                    'date_ahead': day,
                    'predicted_price': max(0.1, predicted_price),
                    'confidence': confidence,
                    'risk_level': self.get_risk_level(confidence)
                })
        
        return pd.DataFrame(predictions)
    
    def get_risk_level(self, confidence):
        """Détermine le niveau de risque"""
        if confidence >= 0.8:
            return "🟢 Faible"
        elif confidence >= 0.6:
            return "🟡 Moyen"
        else:
            return "🔴 Élevé"
    
    def create_portfolio_optimizer(self):
        """Optimiseur de portefeuille de produits"""
        # Simulation d'optimisation de portefeuille
        products = self.df['product_clean'].unique()[:20]  # Top 20 produits
        
        portfolio_data = []
        
        for product in products:
            product_data = self.df[self.df['product_clean'] == product]
            
            # Métriques pour l'optimisation
            avg_return = (product_data['price'].pct_change().mean() * 252)  # Annualisé
            volatility = product_data['price'].pct_change().std() * np.sqrt(252)  # Annualisé
            sharpe_ratio = avg_return / volatility if volatility != 0 else 0
            
            portfolio_data.append({
                'product': product,
                'expected_return': avg_return,
                'volatility': volatility,
                'sharpe_ratio': sharpe_ratio,
                'weight_recommendation': self.get_weight_recommendation(sharpe_ratio),
                'risk_category': self.get_risk_category(volatility)
            })
        
        return pd.DataFrame(portfolio_data)
    
    def get_weight_recommendation(self, sharpe_ratio):
        """Recommandation de poids dans le portefeuille"""
        if sharpe_ratio > 1.5:
            return "🔥 Fort (15-20%)"
        elif sharpe_ratio > 1.0:
            return "📈 Modéré (10-15%)"
        elif sharpe_ratio > 0.5:
            return "⚖️ Équilibré (5-10%)"
        else:
            return "📉 Faible (0-5%)"
    
    def get_risk_category(self, volatility):
        """Catégorie de risque"""
        if volatility > 0.3:
            return "🔴 Très risqué"
        elif volatility > 0.2:
            return "🟡 Risqué"
        elif volatility > 0.1:
            return "🟵 Modéré"
        else:
            return "🟢 Faible risque"
    
    def export_advanced_report(self, selected_products=None):
        """Génère un rapport avancé complet"""
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'market_sentiment': self.create_market_sentiment_analyzer().to_dict('records'),
            'anomalies': self.create_price_anomaly_detector().to_dict('records'),
            'elasticity': self.create_price_elasticity_analyzer().to_dict('records'),
            'monitoring': self.create_real_time_monitoring().to_dict('records'),
            'predictions': self.create_predictive_dashboard().to_dict('records'),
            'portfolio': self.create_portfolio_optimizer().to_dict('records')
        }
        
        return report_data
