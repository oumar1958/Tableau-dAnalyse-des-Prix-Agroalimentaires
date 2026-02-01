import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import streamlit as st
from datetime import datetime, timedelta

class InteractiveFeatures:
    """Classe pour les fonctionnalités interactives avancées"""
    
    def __init__(self, df):
        self.df = df.copy()
        self.prepare_data()
    
    def prepare_data(self):
        """Prépare les données pour les analyses avancées"""
        # Conversion des dates
        if 'date' in self.df.columns:
            self.df['date'] = pd.to_datetime(self.df['date'])
        
        # Encodage des variables catégorielles pour ML
        self.label_encoders = {}
        categorical_columns = ['product_clean', 'market_clean', 'origin', 'quality', 'season']
        
        for col in categorical_columns:
            if col in self.df.columns:
                le = LabelEncoder()
                self.df[f'{col}_encoded'] = le.fit_transform(self.df[col].astype(str))
                self.label_encoders[col] = le
    
    def price_prediction_model(self, product=None, market=None, origin=None):
        """Modèle de prédiction des prix"""
        try:
            # Préparation des données
            features = ['month', 'year', 'product_clean_encoded', 'market_clean_encoded', 
                       'origin_encoded', 'quality_encoded', 'season_encoded']
            
            # Filtrage si spécifié
            df_filtered = self.df.copy()
            if product:
                df_filtered = df_filtered[df_filtered['product_clean'] == product]
            if market:
                df_filtered = df_filtered[df_filtered['market_clean'] == market]
            if origin:
                df_filtered = df_filtered[df_filtered['origin'] == origin]
            
            if len(df_filtered) < 10:
                return None, "Pas assez de données pour l'entraînement"
            
            X = df_filtered[features]
            y = df_filtered['price']
            
            # Split et entraînement
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            
            # Évaluation
            y_pred = model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # Importance des features
            feature_importance = pd.DataFrame({
                'feature': features,
                'importance': model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            return {
                'model': model,
                'mae': mae,
                'r2': r2,
                'feature_importance': feature_importance,
                'sample_size': len(df_filtered)
            }, None
            
        except Exception as e:
            return None, f"Erreur lors de l'entraînement: {str(e)}"
    
    def predict_future_prices(self, days_ahead=7, product=None):
        """Prédit les prix futurs"""
        try:
            model_result, error = self.price_prediction_model(product=product)
            if error:
                return None, error
            
            model = model_result['model']
            
            # Génération de dates futures
            last_date = self.df['date'].max()
            future_dates = [last_date + timedelta(days=i) for i in range(1, days_ahead + 1)]
            
            predictions = []
            for date in future_dates:
                # Caractéristiques moyennes pour la prédiction
                avg_features = self.df[self.df['date'].dt.month == date.month].mean(numeric_only=True)
                
                # Création des features pour la prédiction
                pred_features = pd.DataFrame([{
                    'month': date.month,
                    'year': date.year,
                    'product_clean_encoded': avg_features.get('product_clean_encoded', 0),
                    'market_clean_encoded': avg_features.get('market_clean_encoded', 0),
                    'origin_encoded': avg_features.get('origin_encoded', 0),
                    'quality_encoded': avg_features.get('quality_encoded', 0),
                    'season_encoded': avg_features.get('season_encoded', 0)
                }])
                
                pred_price = model.predict(pred_features)[0]
                predictions.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'predicted_price': round(pred_price, 2)
                })
            
            return predictions, None
            
        except Exception as e:
            return None, f"Erreur lors de la prédiction: {str(e)}"
    
    def create_price_comparison_tool(self):
        """Outil de comparaison de prix interactif"""
        return {
            'products': sorted(self.df['product_clean'].unique()),
            'markets': sorted(self.df['market_clean'].unique()),
            'origins': sorted(self.df['origin'].unique()),
            'date_range': [self.df['date'].min().strftime('%Y-%m-%d'), 
                          self.df['date'].max().strftime('%Y-%m-%d')]
        }
    
    def get_price_evolution_data(self, product, market=None, origin=None):
        """Données d'évolution des prix pour un produit"""
        df_filtered = self.df[self.df['product_clean'] == product].copy()
        
        if market:
            df_filtered = df_filtered[df_filtered['market_clean'] == market]
        if origin:
            df_filtered = df_filtered[df_filtered['origin'] == origin]
        
        # Agrégation par date
        evolution = df_filtered.groupby('date').agg({
            'price': ['mean', 'min', 'max', 'count']
        }).round(2)
        
        evolution.columns = ['prix_moyen', 'prix_min', 'prix_max', 'nombre_observations']
        evolution = evolution.reset_index()
        
        return evolution.sort_values('date')
    
    def create_market_analysis(self):
        """Analyse comparative des marchés"""
        market_stats = self.df.groupby('market_clean').agg({
            'price': ['mean', 'std', 'min', 'max', 'count'],
            'product_clean': 'nunique'
        }).round(2)
        
        market_stats.columns = ['prix_moyen', 'prix_ecart_type', 'prix_min', 'prix_max', 'nombre_observations', 'nombre_produits']
        market_stats = market_stats.sort_values('prix_moyen', ascending=False)
        
        return market_stats
    
    def create_seasonal_analysis(self):
        """Analyse saisonnière des prix"""
        seasonal_stats = self.df.groupby(['product_clean', 'season']).agg({
            'price': ['mean', 'std', 'count']
        }).round(2)
        
        seasonal_stats.columns = ['prix_moyen', 'prix_ecart_type', 'nombre_observations']
        seasonal_stats = seasonal_stats.reset_index()
        
        return seasonal_stats
    
    def create_alert_system(self, product, threshold_percent=20):
        """Système d'alertes sur les variations de prix"""
        try:
            product_data = self.df[self.df['product_clean'] == product].copy()
            product_data = product_data.sort_values('date')
            
            if len(product_data) < 2:
                return {"alerts": [], "message": "Pas assez de données pour l'analyse"}
            
            # Calcul des variations de prix
            product_data['price_change_pct'] = product_data['price'].pct_change() * 100
            
            # Détection d'alertes
            alerts = []
            
            # Variation significative
            significant_changes = product_data[abs(product_data['price_change_pct']) > threshold_percent]
            for _, row in significant_changes.iterrows():
                alerts.append({
                    'type': 'variation_significative',
                    'date': row['date'].strftime('%Y-%m-%d'),
                    'prix': row['price'],
                    'variation': round(row['price_change_pct'], 2),
                    'marche': row['market_clean'],
                    'message': f"Variation de {abs(row['price_change_pct']):.1f}% détectée"
                })
            
            # Prix anormalement élevés/bas
            q75 = product_data['price'].quantile(0.75)
            q25 = product_data['price'].quantile(0.25)
            iqr = q75 - q25
            
            outliers = product_data[
                (product_data['price'] > q75 + 1.5 * iqr) | 
                (product_data['price'] < q25 - 1.5 * iqr)
            ]
            
            for _, row in outliers.iterrows():
                alert_type = 'prix_eleve' if row['price'] > q75 + 1.5 * iqr else 'prix_bas'
                alerts.append({
                    'type': alert_type,
                    'date': row['date'].strftime('%Y-%m-%d'),
                    'prix': row['price'],
                    'marche': row['market_clean'],
                    'message': f"Prix {'élevé' if alert_type == 'prix_eleve' else 'bas'} détecté: {row['price']:.2f}€"
                })
            
            return {
                "alerts": alerts,
                "message": f"{len(alerts)} alerte(s) trouvée(s)",
                "stats": {
                    "prix_moyen": product_data['price'].mean(),
                    "prix_min": product_data['price'].min(),
                    "prix_max": product_data['price'].max(),
                    "volatilite": product_data['price'].std()
                }
            }
            
        except Exception as e:
            return {"alerts": [], "message": f"Erreur: {str(e)}"}
    
    def export_filtered_data(self, filters):
        """Exporte les données filtrées"""
        df_filtered = self.df.copy()
        
        # Application des filtres
        if 'product' in filters and filters['product']:
            df_filtered = df_filtered[df_filtered['product_clean'].isin(filters['product'])]
        
        if 'market' in filters and filters['market']:
            df_filtered = df_filtered[df_filtered['market_clean'].isin(filters['market'])]
        
        if 'origin' in filters and filters['origin']:
            df_filtered = df_filtered[df_filtered['origin'].isin(filters['origin'])]
        
        if 'date_start' in filters and filters['date_start']:
            # Conversion de date en datetime pour la comparaison
            date_start = pd.to_datetime(filters['date_start'])
            df_filtered = df_filtered[df_filtered['date'] >= date_start]
        
        if 'date_end' in filters and filters['date_end']:
            # Conversion de date en datetime pour la comparaison
            date_end = pd.to_datetime(filters['date_end'])
            df_filtered = df_filtered[df_filtered['date'] <= date_end]
        
        if 'price_min' in filters and filters['price_min']:
            df_filtered = df_filtered[df_filtered['price'] >= filters['price_min']]
        
        if 'price_max' in filters and filters['price_max']:
            df_filtered = df_filtered[df_filtered['price'] <= filters['price_max']]
        
        return df_filtered
