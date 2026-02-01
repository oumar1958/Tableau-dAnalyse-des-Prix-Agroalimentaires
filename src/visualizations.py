import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import logging
from datetime import datetime
import os

class AgroDataVisualizer:
    def __init__(self, data_path='data/processed_agro_prices.csv'):
        self.data_path = data_path
        self.df = pd.DataFrame()
        self.logger = logging.getLogger(__name__)
        
        # Configuration des styles
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Création du dossier pour les graphiques
        os.makedirs('static/plots', exist_ok=True)
        
        self.load_data()

    def load_data(self):
        """Charge les données pour la visualisation"""
        try:
            self.df = pd.read_csv(self.data_path, encoding='utf-8')
            if 'date' in self.df.columns:
                self.df['date'] = pd.to_datetime(self.df['date'])
            self.logger.info(f"Données chargées pour visualisation: {len(self.df)} enregistrements")
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement des données: {e}")

    def create_price_evolution_plot(self):
        """Crée un graphique de l'évolution des prix dans le temps"""
        if self.df.empty or 'price' not in self.df.columns:
            return None
        
        # Prix moyens par date
        daily_prices = self.df.groupby('date')['price'].mean().reset_index()
        
        fig = px.line(
            daily_prices, 
            x='date', 
            y='price',
            title='Évolution des prix moyens des produits agroalimentaires',
            labels={'price': 'Prix moyen (€)', 'date': 'Date'},
            template='plotly_white'
        )
        
        fig.update_layout(
            hovermode='x unified',
            showlegend=False,
            height=500
        )
        
        # Sauvegarde
        fig.write_html('static/plots/price_evolution.html')
        fig.write_image('static/plots/price_evolution.png')
        
        return fig

    def create_price_distribution_plot(self):
        """Crée un graphique de distribution des prix"""
        if self.df.empty or 'price' not in self.df.columns:
            return None
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Distribution des prix', 'Boîte à moustaches', 
                          'Histogramme par catégorie', 'Top 10 produits'),
            specs=[[{"type": "histogram"}, {"type": "box"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Histogramme
        fig.add_trace(
            go.Histogram(x=self.df['price'], name='Distribution des prix'),
            row=1, col=1
        )
        
        # Boîte à moustaches
        fig.add_trace(
            go.Box(y=self.df['price'], name='Boîte à moustaches'),
            row=1, col=2
        )
        
        # Distribution par catégorie de prix
        if 'price_category' in self.df.columns:
            category_counts = self.df['price_category'].value_counts()
            fig.add_trace(
                go.Bar(x=category_counts.index, y=category_counts.values, name='Par catégorie'),
                row=2, col=1
            )
        
        # Top 10 des produits
        if 'product_clean' in self.df.columns:
            top_products = self.df['product_clean'].value_counts().head(10)
            fig.add_trace(
                go.Bar(x=top_products.values, y=top_products.index, 
                      orientation='h', name='Top 10 produits'),
                row=2, col=2
            )
        
        fig.update_layout(
            height=800,
            title_text="Analyse de la distribution des prix",
            showlegend=False
        )
        
        fig.write_html('static/plots/price_distribution.html')
        fig.write_image('static/plots/price_distribution.png')
        
        return fig

    def create_market_comparison_plot(self):
        """Compare les prix entre différents marchés"""
        if self.df.empty or 'price' not in self.df.columns:
            return None
        
        # Prix moyens par marché
        market_prices = self.df.groupby('market_clean')['price'].agg(['mean', 'count']).reset_index()
        market_prices = market_prices[market_prices['count'] >= 5]  # Filtre les marchés avec peu de données
        market_prices = market_prices.sort_values('mean', ascending=True).tail(15)
        
        fig = px.bar(
            market_prices,
            x='mean',
            y='market_clean',
            orientation='h',
            title='Prix moyens par marché (Top 15)',
            labels={'mean': 'Prix moyen (€)', 'market_clean': 'Marché'},
            template='plotly_white'
        )
        
        fig.update_layout(height=600)
        
        fig.write_html('static/plots/market_comparison.html')
        fig.write_image('static/plots/market_comparison.png')
        
        return fig

    def create_origin_analysis_plot(self):
        """Analyse les prix par origine géographique"""
        if self.df.empty or 'price' not in self.df.columns or 'origin' not in self.df.columns:
            return None
        
        # Filtrer les données avec origine connue
        origin_data = self.df[self.df['origin'].notna()]
        
        if origin_data.empty:
            return None
        
        # Prix moyens par origine
        origin_prices = origin_data.groupby('origin')['price'].agg(['mean', 'count']).reset_index()
        origin_prices = origin_prices[origin_prices['count'] >= 3]  # Filtre les origines avec peu de données
        origin_prices = origin_prices.sort_values('mean', ascending=True)
        
        fig = px.bar(
            origin_prices,
            x='mean',
            y='origin',
            orientation='h',
            title='Prix moyens par pays d\'origine',
            labels={'mean': 'Prix moyen (€)', 'origin': 'Origine'},
            template='plotly_white'
        )
        
        fig.update_layout(height=500)
        
        fig.write_html('static/plots/origin_analysis.html')
        fig.write_image('static/plots/origin_analysis.png')
        
        return fig

    def create_seasonal_analysis_plot(self):
        """Analyse saisonnière des prix"""
        if self.df.empty or 'price' not in self.df.columns or 'season' not in self.df.columns:
            return None
        
        # Prix moyens par saison
        seasonal_prices = self.df.groupby('season')['price'].agg(['mean', 'count', 'std']).reset_index()
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Prix moyens par saison', 'Nombre d\'observations par saison'),
            specs=[[{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Prix moyens
        fig.add_trace(
            go.Bar(x=seasonal_prices['season'], y=seasonal_prices['mean'], 
                  name='Prix moyen', error_y=dict(type='data', array=seasonal_prices['std'])),
            row=1, col=1
        )
        
        # Nombre d'observations
        fig.add_trace(
            go.Bar(x=seasonal_prices['season'], y=seasonal_prices['count'], 
                  name='Nombre d\'observations'),
            row=1, col=2
        )
        
        fig.update_layout(
            height=400,
            title_text="Analyse saisonnière des prix",
            showlegend=False
        )
        
        fig.write_html('static/plots/seasonal_analysis.html')
        fig.write_image('static/plots/seasonal_analysis.png')
        
        return fig

    def create_product_price_heatmap(self):
        """Crée une heatmap des prix par produit et marché"""
        if self.df.empty or 'price' not in self.df.columns:
            return None
        
        # Sélection des produits et marchés les plus fréquents
        top_products = self.df['product_clean'].value_counts().head(10).index
        top_markets = self.df['market_clean'].value_counts().head(8).index
        
        # Filtre les données
        filtered_df = self.df[
            (self.df['product_clean'].isin(top_products)) & 
            (self.df['market_clean'].isin(top_markets))
        ]
        
        # Pivot table pour la heatmap
        pivot_data = filtered_df.pivot_table(
            values='price', 
            index='product_clean', 
            columns='market_clean', 
            aggfunc='mean'
        )
        
        fig = px.imshow(
            pivot_data,
            title='Heatmap des prix moyens par produit et marché',
            labels=dict(x="Marché", y="Produit", color="Prix moyen (€)"),
            template='plotly_white'
        )
        
        fig.update_layout(height=600)
        
        fig.write_html('static/plots/product_heatmap.html')
        fig.write_image('static/plots/product_heatmap.png')
        
        return fig

    def create_dashboard_summary(self):
        """Crée un tableau de bord résumé"""
        if self.df.empty:
            return None
        
        # Statistiques générales
        stats = {
            'Total enregistrements': len(self.df),
            'Produits uniques': self.df['product_clean'].nunique() if 'product_clean' in self.df.columns else 0,
            'Marchés uniques': self.df['market_clean'].nunique() if 'market_clean' in self.df.columns else 0,
            'Prix moyen': f"{self.df['price'].mean():.2f}€" if 'price' in self.df.columns else 'N/A',
            'Prix médian': f"{self.df['price'].median():.2f}€" if 'price' in self.df.columns else 'N/A',
            'Période': f"{self.df['date'].min().strftime('%d/%m/%Y')} - {self.df['date'].max().strftime('%d/%m/%Y')}" if 'date' in self.df.columns else 'N/A'
        }
        
        # Création du tableau de bord
        fig = make_subplots(
            rows=3, cols=3,
            subplot_titles=list(stats.keys()),
            specs=[[{"type": "indicator"}]*3]*3
        )
        
        for i, (key, value) in enumerate(stats.items()):
            row = (i // 3) + 1
            col = (i % 3) + 1
            
            if isinstance(value, str) and '€' in value:
                numeric_value = float(value.replace('€', ''))
                fig.add_trace(
                    go.Indicator(
                        mode="number+gauge+delta",
                        value=numeric_value,
                        title={'text': key},
                        gauge={'axis': {'range': [None, max(10, numeric_value * 1.2)]}}
                    ),
                    row=row, col=col
                )
            else:
                fig.add_trace(
                    go.Indicator(
                        mode="number",
                        value=float(value) if str(value).isdigit() else 0,
                        title={'text': key}
                    ),
                    row=row, col=col
                )
        
        fig.update_layout(
            height=800,
            title_text="Tableau de bord - Statistiques générales"
        )
        
        fig.write_html('static/plots/dashboard.html')
        fig.write_image('static/plots/dashboard.png')
        
        return fig

    def generate_all_plots(self):
        """Génère tous les graphiques"""
        plots = {}
        
        try:
            plots['price_evolution'] = self.create_price_evolution_plot()
            self.logger.info("Graphique d'évolution des prix créé")
        except Exception as e:
            self.logger.error(f"Erreur création graphique évolution: {e}")
        
        try:
            plots['price_distribution'] = self.create_price_distribution_plot()
            self.logger.info("Graphique de distribution des prix créé")
        except Exception as e:
            self.logger.error(f"Erreur création graphique distribution: {e}")
        
        try:
            plots['market_comparison'] = self.create_market_comparison_plot()
            self.logger.info("Graphique de comparaison des marchés créé")
        except Exception as e:
            self.logger.error(f"Erreur création graphique marchés: {e}")
        
        try:
            plots['origin_analysis'] = self.create_origin_analysis_plot()
            self.logger.info("Graphique d'analyse par origine créé")
        except Exception as e:
            self.logger.error(f"Erreur création graphique origine: {e}")
        
        try:
            plots['seasonal_analysis'] = self.create_seasonal_analysis_plot()
            self.logger.info("Graphique d'analyse saisonnière créé")
        except Exception as e:
            self.logger.error(f"Erreur création graphique saisonnier: {e}")
        
        try:
            plots['product_heatmap'] = self.create_product_price_heatmap()
            self.logger.info("Heatmap des produits créée")
        except Exception as e:
            self.logger.error(f"Erreur création heatmap: {e}")
        
        try:
            plots['dashboard'] = self.create_dashboard_summary()
            self.logger.info("Tableau de bord créé")
        except Exception as e:
            self.logger.error(f"Erreur création tableau de bord: {e}")
        
        return plots

def main():
    visualizer = AgroDataVisualizer()
    plots = visualizer.generate_all_plots()
    
    print(f"Génération de {len(plots)} graphiques terminée!")
    print("Graphiques disponibles dans le dossier 'static/plots/'")
    
    for plot_name, plot in plots.items():
        if plot:
            print(f"- {plot_name}: ✅")
        else:
            print(f"- {plot_name}: ❌")

if __name__ == "__main__":
    main()
