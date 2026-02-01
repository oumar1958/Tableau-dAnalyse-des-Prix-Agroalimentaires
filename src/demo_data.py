import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_demo_data():
    """Génère des données de démonstration réalistes pour le dashboard"""
    
    # Produits et catégories
    products_data = {
        'Légumes': [
            'Tomate', 'Carotte', 'Salade', 'Chou', 'Poivron', 'Oignon', 'Ail',
            'Courgette', 'Aubergine', 'Pomme de terre', 'Haricot vert', 'Poireau'
        ],
        'Fruits': [
            'Pomme', 'Poire', 'Orange', 'Citron', 'Fraise', 'Cerise', 'Pêche',
            'Banane', 'Kiwi', 'Raisin', 'Melon', 'Pastèque'
        ],
        'Viande': [
            'Bœuf', 'Porc', 'Veau', 'Agneau', 'Poulet', 'Dinde', 'Canard',
            'Lapin', 'Cheval', 'Veau', 'Agneau', 'Volaille'
        ],
        'Produits laitiers': [
            'Beurre', 'Fromage', 'Lait', 'Yaourt', 'Crème', 'Œuf', 'Fromage de chèvre'
        ]
    }
    
    # Marchés
    markets = [
        'MIN de Rungis', 'MIN de Paris', 'MIN de Lyon', 'MIN de Marseille',
        'MIN de Bordeaux', 'MIN de Lille', 'MIN de Toulouse', 'MIN de Nantes',
        'MIN de Strasbourg', 'MIN de Nice', 'MIN de Perpignan', 'MIN d\'Avignon'
    ]
    
    # Origines
    origins = ['France', 'Espagne', 'Italie', 'Maroc', 'Belgique', 'Pays-Bas', 'Allemagne', 'Portugal']
    
    # Génération des données
    data = []
    base_date = datetime.now() - timedelta(days=90)
    
    for category, products in products_data.items():
        for product in products:
            # Prix de base par catégorie
            if category == 'Légumes':
                base_price = random.uniform(1.5, 8.0)
            elif category == 'Fruits':
                base_price = random.uniform(2.0, 12.0)
            elif category == 'Viande':
                base_price = random.uniform(8.0, 35.0)
            else:  # Produits laitiers
                base_price = random.uniform(2.5, 15.0)
            
            # Génération de plusieurs enregistrements par produit
            for _ in range(random.randint(8, 25)):
                # Date aléatoire dans les 90 derniers jours
                days_offset = random.randint(0, 90)
                date = base_date + timedelta(days=days_offset)
                
                # Variation de prix saisonnière et aléatoire
                seasonal_factor = 1.0
                if category == 'Fruits':
                    if date.month in [6, 7, 8]:  # Été
                        seasonal_factor = random.uniform(0.8, 1.2)
                    elif date.month in [12, 1, 2]:  # Hiver
                        seasonal_factor = random.uniform(1.1, 1.5)
                
                price_variation = random.uniform(0.85, 1.15)
                final_price = base_price * seasonal_factor * price_variation
                
                # Arrondi à 2 décimales
                final_price = round(final_price, 2)
                
                # Sélection aléatoire du marché et origine
                market = random.choice(markets)
                origin = random.choice(origins)
                
                # Qualité
                qualities = ['Cat. I', 'Cat. II', 'Extra', 'Bio']
                quality = random.choice(qualities)
                
                data.append({
                    'product': product,
                    'date': date.strftime('%Y-%m-%d'),
                    'market': market,
                    'description': f'{product} {quality} - {origin}',
                    'source_url': f'https://rnm.franceagrimer.fr/prix?{product.replace(" ", "-").upper()}',
                    'price': final_price,
                    'quantity': random.randint(1, 10),
                    'unit': random.choice(['kg', 'pièce', 'litre']),
                    'origin': origin,
                    'quality': quality,
                    'product_clean': product.title(),
                    'market_clean': market,
                    'unit_price': final_price,
                    'month': date.month,
                    'year': date.year,
                    'season': get_season(date.month),
                    'product_category': category,
                    'price_category': get_price_category(final_price)
                })
    
    # Création du DataFrame
    df = pd.DataFrame(data)
    
    # Mélange des données
    df = df.sample(frac=1).reset_index(drop=True)
    
    return df

def get_season(month):
    """Détermine la saison à partir du mois"""
    if month in [12, 1, 2]:
        return 'Hiver'
    elif month in [3, 4, 5]:
        return 'Printemps'
    elif month in [6, 7, 8]:
        return 'Été'
    else:
        return 'Automne'

def get_price_category(price):
    """Catégorise le prix"""
    if price < 2:
        return '<2€'
    elif price < 5:
        return '2-5€'
    elif price < 10:
        return '5-10€'
    elif price < 20:
        return '10-20€'
    else:
        return '>20€'

def save_demo_data():
    """Génère et sauvegarde les données de démonstration"""
    print("🎲 Génération des données de démonstration...")
    
    df = generate_demo_data()
    
    # Sauvegarde
    df.to_csv('data/all_agro_prices.csv', index=False, encoding='utf-8')
    df.to_csv('data/processed_agro_prices.csv', index=False, encoding='utf-8')
    
    print(f"✅ {len(df)} enregistrements générés et sauvegardés")
    print(f"📊 Période: {df['date'].min()} - {df['date'].max()}")
    print(f"🥬 Produits: {df['product_clean'].nunique()}")
    print(f"🏪 Marchés: {df['market_clean'].nunique()}")
    print(f"🌍 Origines: {df['origin'].nunique()}")
    print(f"💰 Prix moyens: {df['price'].mean():.2f}€")
    
    # Statistiques par catégorie
    print("\n📈 Statistiques par catégorie:")
    for category in df['product_category'].unique():
        cat_data = df[df['product_category'] == category]
        print(f"  • {category}: {len(cat_data)} enregistrements, prix moyen: {cat_data['price'].mean():.2f}€")
    
    return df

if __name__ == "__main__":
    save_demo_data()
