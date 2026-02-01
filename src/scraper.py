import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from fake_useragent import UserAgent
import logging
from urllib.parse import urljoin, urlparse
import re
from datetime import datetime

class AgroDataScraper:
    def __init__(self):
        self.base_url = "https://rnm.franceagrimer.fr"
        self.session = requests.Session()
        self.ua = UserAgent()
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def get_page(self, url, params=None):
        """Récupère le contenu d'une page avec gestion des erreurs"""
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erreur lors de la récupération de {url}: {e}")
            return None

    def extract_product_links(self, category_url):
        """Extrait les liens des produits depuis une page de catégorie"""
        html = self.get_page(category_url)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        product_links = []
        
        # Cherche les liens vers les produits
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href']
            if '/prix?' in href and len(href.split('?')) > 1:
                full_url = urljoin(self.base_url, href)
                product_links.append(full_url)
        
        return list(set(product_links))  # Élimine les doublons

    def extract_price_data(self, product_url):
        """Extrait les données de prix d'un produit"""
        html = self.get_page(product_url)
        if not html:
            return None
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extraction du nom du produit
        title = soup.find('h1')
        product_name = title.get_text().strip() if title else "Inconnu"
        
        # Extraction de la date
        date_element = soup.find('h2')
        date_text = date_element.get_text().strip() if date_element else ""
        date_match = re.search(r'(\d{2}-\d{2}-\d{4})', date_text)
        date = date_match.group(1) if date_match else datetime.now().strftime('%d-%m-%Y')
        
        # Extraction des données de prix
        price_data = []
        
        # Cherche tous les éléments qui pourraient contenir des prix
        all_text = soup.get_text()
        
        # Patterns de prix plus robustes
        price_patterns = [
            r'(\d+[.,]\d+)\s*€\s*HT',  # 12,50 € HT
            r'€\s*HT\s*(\d+[.,]\d+)',  # € HT 12,50
            r'(\d+)\s*€\s*HT',  # 12 € HT
            r'(\d+[.,]\d+)\s*€',  # 12,50 €
            r'(\d+)\s*€',  # 12 €
            r'(\d+[.,]\d+)\s*EUR',  # 12.50 EUR
        ]
        
        # Extraction des prix du texte complet
        prices_found = []
        for pattern in price_patterns:
            matches = re.findall(pattern, all_text)
            for match in matches:
                try:
                    price = float(match.replace(',', '.'))
                    if 0.1 < price < 1000:  # Filtre les prix réalistes
                        prices_found.append(price)
                except ValueError:
                    continue
        
        # Si on trouve des prix, on crée des enregistrements
        if prices_found:
            # Extraction des marchés
            market_links = soup.find_all('a', href=re.compile(r'MARCHE'))
            markets = [link.get_text().strip() for link in market_links if link.get_text().strip()]
            
            # Si pas assez de marchés, on utilise le nom du produit comme marché
            if len(markets) < len(prices_found):
                markets = [product_name] * len(prices_found)
            
            # Création des enregistrements
            for i, price in enumerate(prices_found[:len(markets)]):
                market = markets[i] if i < len(markets) else product_name
                
                price_data.append({
                    'product': product_name,
                    'date': date,
                    'market': market,
                    'description': f'Prix extrait: {price}€',
                    'source_url': product_url
                })
        
        # Si toujours pas de prix, on essaie une approche différente
        if not price_data:
            # Cherche les tableaux qui pourraient contenir des prix
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    row_text = ' '.join([cell.get_text().strip() for cell in cells])
                    
                    # Cherche des prix dans cette ligne
                    for pattern in price_patterns:
                        match = re.search(pattern, row_text)
                        if match:
                            try:
                                price = float(match.group(1).replace(',', '.'))
                                if 0.1 < price < 1000:
                                    price_data.append({
                                        'product': product_name,
                                        'date': date,
                                        'market': product_name,
                                        'description': row_text[:200],  # Limite la longueur
                                        'source_url': product_url
                                    })
                                    break
                            except ValueError:
                                continue
        
        return {
            'product': product_name,
            'date': date,
            'price_data': price_data,
            'source_url': product_url
        }

    def scrape_category(self, category_name, category_url):
        """Scrape une catégorie complète de produits"""
        self.logger.info(f"Début du scraping de la catégorie: {category_name}")
        
        # Récupère les liens des produits
        product_links = self.extract_product_links(category_url)
        self.logger.info(f"Trouvé {len(product_links)} produits dans {category_name}")
        
        all_data = []
        
        for i, product_url in enumerate(product_links[:10]):  # Limite à 10 produits pour le test
            self.logger.info(f"Scraping du produit {i+1}/{len(product_links)}: {product_url}")
            
            product_data = self.extract_price_data(product_url)
            if product_data and product_data['price_data']:
                all_data.extend(product_data['price_data'])
            
            # Pause pour éviter de surcharger le serveur
            time.sleep(1)
        
        return all_data

    def save_data(self, data, filename):
        """Sauvegarde les données dans un fichier CSV"""
        if not data:
            self.logger.warning("Aucune donnée à sauvegarder")
            return
        
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8')
        self.logger.info(f"Données sauvegardées dans {filename}")

def main():
    scraper = AgroDataScraper()
    
    # Catégories principales à scraper
    categories = {
        'Légumes': 'https://rnm.franceagrimer.fr/prix?LEGUMES',
        'Fruits': 'https://rnm.franceagrimer.fr/prix?FRUITS',
        'Viande': 'https://rnm.franceagrimer.fr/prix?VIANDE',
        'Beurre_Oeuf_Fromage': 'https://rnm.franceagrimer.fr/prix?BEURRE-OEUF-FROMAGE'
    }
    
    all_results = []
    
    for category_name, category_url in categories.items():
        try:
            category_data = scraper.scrape_category(category_name, category_url)
            all_results.extend(category_data)
            
            # Sauvegarde intermédiaire par catégorie
            if category_data:
                scraper.save_data(category_data, f'data/{category_name.lower()}_prices.csv')
                
        except Exception as e:
            scraper.logger.error(f"Erreur lors du scraping de {category_name}: {e}")
    
    # Sauvegarde finale
    if all_results:
        scraper.save_data(all_results, 'data/all_agro_prices.csv')
        print(f"Scraping terminé. {len(all_results)} enregistrements collectés.")
    else:
        print("Aucune donnée collectée.")

if __name__ == "__main__":
    main()
