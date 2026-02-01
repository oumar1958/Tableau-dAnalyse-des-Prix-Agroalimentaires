import pandas as pd
import numpy as np
import re
from datetime import datetime
import logging

class AgroDataProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def load_data(self, filepath):
        """Charge les données depuis un fichier CSV"""
        try:
            df = pd.read_csv(filepath, encoding='utf-8')
            self.logger.info(f"Données chargées: {len(df)} enregistrements depuis {filepath}")
            return df
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement des données: {e}")
            return pd.DataFrame()

    def clean_price_text(self, text):
        """Extrait le prix d'un texte"""
        if pd.isna(text):
            return None
        
        # Cherche les patterns de prix
        price_patterns = [
            r'(\d+[.,]\d+)\s*€',  # 12,50 €
            r'€\s*(\d+[.,]\d+)',  # € 12,50
            r'(\d+[.,]\d+)\s*EUR',  # 12.50 EUR
            r'(\d+)\s*€',  # 12 €
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, str(text).upper())
            if match:
                price_str = match.group(1).replace(',', '.')
                try:
                    return float(price_str)
                except ValueError:
                    continue
        return None

    def extract_quantity(self, text):
        """Extrait la quantité et l'unité d'un texte"""
        if pd.isna(text):
            return None, None
        
        text = str(text).upper()
        
        # Patterns pour la quantité
        quantity_patterns = [
            r'(\d+)\s*KG',
            r'(\d+)\s*G',
            r'(\d+)\s*L',
            r'(\d+)\s*ML',
            r'(\d+)\s*PIECE',
            r'(\d+)\s*BARQ',
            r'(\d+)\s*COLIS',
            r'(\d+)\s*PLATEAU',
        ]
        
        for pattern in quantity_patterns:
            match = re.search(pattern, text)
            if match:
                quantity = int(match.group(1))
                unit = pattern.split('\\s*')[1] if '\\s*' in pattern else 'unit'
                return quantity, unit
        
        return None, None

    def extract_origin(self, text):
        """Extrait le pays d'origine"""
        if pd.isna(text):
            return None
        
        text = str(text).upper()
        
        # Liste des pays courants dans les données agro
        countries = [
            'FRANCE', 'ESPAGNE', 'MAROC', 'ITALIE', 'BELGIQUE', 'PAYS-BAS',
            'TUNISIE', 'UE', 'U.E.', 'ALLEMAGNE', 'PORTUGAL', 'GRÈCE'
        ]
        
        for country in countries:
            if country in text:
                return country
        
        return None

    def extract_quality(self, text):
        """Extrait la qualité/calibre du produit"""
        if pd.isna(text):
            return None
        
        text = str(text).upper()
        
        quality_patterns = [
            r'CAT\.\s*(I|II|III|1|2|3)',
            r'EXTRA',
            r'BIO',
            r'(\d{2})-(\d{2})MM',  # Calibre en mm
            r'(\d{2})-(\d{2})\s*MM'
        ]
        
        for pattern in quality_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        
        return None

    def clean_data(self, df):
        """Nettoie et structure les données brutes"""
        self.logger.info("Début du nettoyage des données")
        
        # Copie du DataFrame pour éviter les modifications inplace
        clean_df = df.copy()
        
        # Extraction des prix
        clean_df['price'] = clean_df['description'].apply(self.clean_price_text)
        
        # Extraction des quantités
        clean_df[['quantity', 'unit']] = clean_df['description'].apply(
            lambda x: pd.Series(self.extract_quantity(x))
        )
        
        # Extraction des origines
        clean_df['origin'] = clean_df['description'].apply(self.extract_origin)
        
        # Extraction des qualités
        clean_df['quality'] = clean_df['description'].apply(self.extract_quality)
        
        # Conversion de la date
        clean_df['date'] = pd.to_datetime(clean_df['date'], format='%d-%m-%Y', errors='coerce')
        
        # Nettoyage du nom du produit
        clean_df['product_clean'] = clean_df['product'].str.strip().str.title()
        
        # Nettoyage du nom du marché
        clean_df['market_clean'] = clean_df['market'].str.strip().str.title()
        
        # Calcul du prix unitaire si possible
        clean_df['unit_price'] = clean_df.apply(
            lambda row: row['price'] / row['quantity'] 
            if pd.notna(row['price']) and pd.notna(row['quantity']) and row['quantity'] > 0 
            else row['price'],
            axis=1
        )
        
        # Suppression des doublons
        clean_df = clean_df.drop_duplicates()
        
        # Statistiques de nettoyage
        original_count = len(df)
        cleaned_count = len(clean_df)
        prices_extracted = clean_df['price'].notna().sum()
        
        self.logger.info(f"Nettoyage terminé:")
        self.logger.info(f"- Enregistrements originaux: {original_count}")
        self.logger.info(f"- Enregistrements nettoyés: {cleaned_count}")
        self.logger.info(f"- Prix extraits: {prices_extracted}")
        
        return clean_df

    def add_derived_features(self, df):
        """Ajoute des caractéristiques dérivées pour l'analyse"""
        df = df.copy()
        
        # Mois et année
        df['month'] = df['date'].dt.month
        df['year'] = df['date'].dt.year
        df['season'] = df['month'].apply(self.get_season)
        
        # Catégories de produits
        df['product_category'] = df['product_clean'].apply(self.categorize_product)
        
        # Plages de prix (uniquement si des prix valides existent)
        if 'price' in df.columns and df['price'].notna().any():
            # Filtre les prix valides pour éviter les erreurs
            valid_prices = df['price'].dropna()
            if not valid_prices.empty:
                df['price_category'] = pd.cut(
                    df['price'],
                    bins=[0, 2, 5, 10, 20, float('inf')],
                    labels=['<2€', '2-5€', '5-10€', '10-20€', '>20€']
                )
            else:
                df['price_category'] = 'Non disponible'
        else:
            df['price_category'] = 'Non disponible'
        
        return df

    def get_season(self, month):
        """Détermine la saison à partir du mois"""
        if month in [12, 1, 2]:
            return 'Hiver'
        elif month in [3, 4, 5]:
            return 'Printemps'
        elif month in [6, 7, 8]:
            return 'Été'
        else:
            return 'Automne'

    def categorize_product(self, product_name):
        """Catégorise les produits par type"""
        product_name = str(product_name).lower()
        
        categories = {
            'Légumes': ['tomate', 'carotte', 'salade', 'chou', 'poivre', 'oignon', 'ail'],
            'Fruits': ['pomme', 'poire', 'orange', 'citron', 'fraise', 'cerise'],
            'Viande': ['bœuf', 'porc', 'veau', 'agneau', 'poulet', 'dinde'],
            'Produits laitiers': ['beurre', 'fromage', 'œuf', 'lait']
        }
        
        for category, keywords in categories.items():
            if any(keyword in product_name for keyword in keywords):
                return category
        
        return 'Autre'

    def generate_summary_stats(self, df):
        """Génère des statistiques descriptives"""
        if df.empty:
            return {}
        
        stats = {
            'total_records': len(df),
            'date_range': {
                'start': df['date'].min().strftime('%Y-%m-%d') if 'date' in df.columns else None,
                'end': df['date'].max().strftime('%Y-%m-%d') if 'date' in df.columns else None
            },
            'products': {
                'unique_count': df['product_clean'].nunique(),
                'top_products': df['product_clean'].value_counts().head(10).to_dict()
            },
            'markets': {
                'unique_count': df['market_clean'].nunique(),
                'top_markets': df['market_clean'].value_counts().head(10).to_dict()
            }
        }
        
        if 'price' in df.columns and df['price'].notna().any():
            stats['prices'] = {
                'mean': df['price'].mean(),
                'median': df['price'].median(),
                'min': df['price'].min(),
                'max': df['price'].max(),
                'std': df['price'].std()
            }
        
        return stats

    def save_processed_data(self, df, filepath):
        """Sauvegarde les données traitées"""
        try:
            df.to_csv(filepath, index=False, encoding='utf-8')
            self.logger.info(f"Données traitées sauvegardées dans {filepath}")
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde: {e}")

def main():
    processor = AgroDataProcessor()
    
    # Charge et nettoie les données
    df = processor.load_data('data/all_agro_prices.csv')
    if not df.empty:
        clean_df = processor.clean_data(df)
        enriched_df = processor.add_derived_features(clean_df)
        
        # Sauvegarde
        processor.save_processed_data(enriched_df, 'data/processed_agro_prices.csv')
        
        # Statistiques
        stats = processor.generate_summary_stats(enriched_df)
        print("Statistiques des données:")
        for key, value in stats.items():
            print(f"{key}: {value}")

if __name__ == "__main__":
    main()
