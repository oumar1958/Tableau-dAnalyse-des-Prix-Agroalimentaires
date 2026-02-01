#!/usr/bin/env python3
"""
Script principal pour exécuter le pipeline complet de scraping et d'analyse
"""

import sys
import os
import argparse
from datetime import datetime

# Ajout du chemin vers src
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from scraper import AgroDataScraper
from data_processor import AgroDataProcessor
from visualizations import AgroDataVisualizer

def run_full_pipeline():
    """Exécute le pipeline complet de scraping à visualisation"""
    print("🚀 Démarrage du pipeline complet de scraping agroalimentaire")
    print("=" * 60)
    
    # Étape 1: Scraping
    print("\n📡 Étape 1: Scraping des données")
    print("-" * 30)
    
    try:
        scraper = AgroDataScraper()
        
        categories = {
            'Légumes': 'https://rnm.franceagrimer.fr/prix?LEGUMES',
            'Fruits': 'https://rnm.franceagrimer.fr/prix?FRUITS',
            'Viande': 'https://rnm.franceagrimer.fr/prix?VIANDE',
            'Beurre_Oeuf_Fromage': 'https://rnm.franceagrimer.fr/prix?BEURRE-OEUF-FROMAGE'
        }
        
        all_results = []
        
        for category_name, category_url in categories.items():
            print(f"  📂 Scraping de la catégorie: {category_name}")
            category_data = scraper.scrape_category(category_name, category_url)
            all_results.extend(category_data)
            
            # Sauvegarde intermédiaire
            if category_data:
                scraper.save_data(category_data, f'data/{category_name.lower()}_prices.csv')
        
        # Sauvegarde finale
        if all_results:
            scraper.save_data(all_results, 'data/all_agro_prices.csv')
            print(f"  ✅ Scraping terminé: {len(all_results)} enregistrements collectés")
        else:
            print("  ❌ Aucune donnée collectée")
            return False
            
    except Exception as e:
        print(f"  ❌ Erreur lors du scraping: {e}")
        return False
    
    # Étape 2: Traitement des données
    print("\n🧹 Étape 2: Traitement et nettoyage des données")
    print("-" * 30)
    
    try:
        processor = AgroDataProcessor()
        
        # Chargement et nettoyage
        df = processor.load_data('data/all_agro_prices.csv')
        if df.empty:
            print("  ❌ Aucune donnée à traiter")
            return False
        
        clean_df = processor.clean_data(df)
        enriched_df = processor.add_derived_features(clean_df)
        
        # Sauvegarde
        processor.save_processed_data(enriched_df, 'data/processed_agro_prices.csv')
        
        # Statistiques
        stats = processor.generate_summary_stats(enriched_df)
        print("  📊 Statistiques des données traitées:")
        for key, value in stats.items():
            print(f"    - {key}: {value}")
        
        print("  ✅ Traitement terminé avec succès")
        
    except Exception as e:
        print(f"  ❌ Erreur lors du traitement: {e}")
        return False
    
    # Étape 3: Visualisations
    print("\n📈 Étape 3: Génération des visualisations")
    print("-" * 30)
    
    try:
        visualizer = AgroDataVisualizer()
        plots = visualizer.generate_all_plots()
        
        successful_plots = sum(1 for plot in plots.values() if plot is not None)
        print(f"  ✅ {successful_plots}/{len(plots)} graphiques générés avec succès")
        
        print("  📁 Graphiques disponibles dans 'static/plots/'")
        for plot_name, plot in plots.items():
            status = "✅" if plot else "❌"
            print(f"    {status} {plot_name}")
        
    except Exception as e:
        print(f"  ❌ Erreur lors de la génération des graphiques: {e}")
        return False
    
    # Étape 4: Lancement du dashboard
    print("\n🌐 Étape 4: Lancement du dashboard")
    print("-" * 30)
    
    try:
        import subprocess
        import webbrowser
        import time
        
        print("  🚀 Lancement de Streamlit...")
        
        # Lancement de Streamlit en arrière-plan
        streamlit_process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "app.py", "--server.headless", "true"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Attendre que le serveur démarre
        time.sleep(5)
        
        print("  🌐 Dashboard disponible à: http://localhost:8501")
        print("  📝 Appuyez sur Ctrl+C pour arrêter le serveur")
        
        # Ouvrir le navigateur (optionnel)
        try:
            webbrowser.open('http://localhost:8501')
        except:
            print("    (Impossible d'ouvrir automatiquement le navigateur)")
        
        # Attendre que l'utilisateur arrête
        try:
            streamlit_process.wait()
        except KeyboardInterrupt:
            print("\n  🛑 Arrêt du serveur Streamlit...")
            streamlit_process.terminate()
        
    except Exception as e:
        print(f"  ❌ Erreur lors du lancement du dashboard: {e}")
        return False
    
    print("\n🎉 Pipeline terminé avec succès!")
    return True

def run_scraping_only():
    """Exécute uniquement le scraping"""
    print("📡 Lancement du scraping uniquement")
    
    try:
        scraper = AgroDataScraper()
        
        categories = {
            'Légumes': 'https://rnm.franceagrimer.fr/prix?LEGUMES',
            'Fruits': 'https://rnm.franceagrimer.fr/prix?FRUITS',
            'Viande': 'https://rnm.franceagrimer.fr/prix?VIANDE',
            'Beurre_Oeuf_Fromage': 'https://rnm.franceagrimer.fr/prix?BEURRE-OEUF-FROMAGE'
        }
        
        all_results = []
        
        for category_name, category_url in categories.items():
            print(f"Scraping de: {category_name}")
            category_data = scraper.scrape_category(category_name, category_url)
            all_results.extend(category_data)
        
        if all_results:
            scraper.save_data(all_results, 'data/all_agro_prices.csv')
            print(f"✅ {len(all_results)} enregistrements collectés")
        else:
            print("❌ Aucune donnée collectée")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

def run_processing_only():
    """Exécute uniquement le traitement des données"""
    print("🧹 Lancement du traitement des données")
    
    try:
        processor = AgroDataProcessor()
        
        df = processor.load_data('data/all_agro_prices.csv')
        if df.empty:
            print("❌ Aucune donnée à traiter")
            return
        
        clean_df = processor.clean_data(df)
        enriched_df = processor.add_derived_features(clean_df)
        
        processor.save_processed_data(enriched_df, 'data/processed_agro_prices.csv')
        
        stats = processor.generate_summary_stats(enriched_df)
        print("📊 Statistiques:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        print("✅ Traitement terminé")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

def run_visualizations_only():
    """Exécute uniquement la génération des visualisations"""
    print("📈 Génération des visualisations")
    
    try:
        visualizer = AgroDataVisualizer()
        plots = visualizer.generate_all_plots()
        
        successful_plots = sum(1 for plot in plots.values() if plot is not None)
        print(f"✅ {successful_plots}/{len(plots)} graphiques générés")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

def main():
    """Fonction principale avec gestion des arguments"""
    parser = argparse.ArgumentParser(description='Pipeline de scraping et analyse agroalimentaire')
    
    parser.add_argument(
        '--mode', 
        choices=['full', 'scraping', 'processing', 'visualizations', 'dashboard'],
        default='full',
        help='Mode d\'exécution (default: full)'
    )
    
    args = parser.parse_args()
    
    print("🥬 Dashboard Agroalimentaire - Pipeline de Scraping")
    print(f"🕐 Démarré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Vérification des dossiers nécessaires
    os.makedirs('data', exist_ok=True)
    os.makedirs('static/plots', exist_ok=True)
    
    # Exécution selon le mode
    if args.mode == 'full':
        success = run_full_pipeline()
    elif args.mode == 'scraping':
        run_scraping_only()
        success = True
    elif args.mode == 'processing':
        run_processing_only()
        success = True
    elif args.mode == 'visualizations':
        run_visualizations_only()
        success = True
    elif args.mode == 'dashboard':
        # Lancement du dashboard uniquement
        os.system("streamlit run app.py")
        success = True
    else:
        print("❌ Mode non reconnu")
        success = False
    
    if success:
        print("\n🎉 Opération terminée avec succès!")
    else:
        print("\n❌ Opération échouée")
        sys.exit(1)

if __name__ == "__main__":
    main()
