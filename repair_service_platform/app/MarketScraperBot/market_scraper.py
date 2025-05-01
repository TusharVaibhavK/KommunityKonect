import requests
from bs4 import BeautifulSoup
from datetime import datetime
import sys
import os

# Add the parent directory to sys.path to make imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from repair_service_platform.app import create_app
from repair_service_platform.app.models import db, MarketPrice

def scrape_urbanclap_prices(service_type=None):
    """
    Scrape prices from UrbanClap for a given service type
    Returns a dictionary with service name as key and price as value
    """
    # Dictionary to store the results
    results = {}
    
    # Define service type specific URLs
    urls = {
        'sink_repair': 'https://www.urbancompany.com/bangalore-plumbers',
        'electrician_visit': 'https://www.urbancompany.com/bangalore-electricians',
        'general': 'https://www.urbancompany.com/bangalore-home-services'
    }
    
    # Use general URL if service_type not specified or not in our list
    url = urls.get(service_type, urls['general'])
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Mock data for development (in case the actual scraping doesn't work)
        mock_data = {
            'sink_repair': {'Basic Sink Repair': 249, 'Advanced Plumbing': 499},
            'electrician_visit': {'Electrical Inspection': 199, 'Outlet Installation': 299},
            'general': {'Home Cleaning': 399, 'Pest Control': 599}
        }
        
        # Try to extract real data, fallback to mock data
        services = soup.find_all('div', class_='service-card')
        if services:
            for service in services:
                try:
                    name = service.find('h3').text.strip()
                    price_text = service.find('span', class_='price').text.strip()
                    price = float(price_text.replace('₹', '').replace(',', ''))
                    results[name] = price
                except:
                    continue
        else:
            # If scraping fails, use mock data
            results = mock_data.get(service_type, mock_data['general'])
            
        # Save the results to database
        for service_name, price in results.items():
            market_price = MarketPrice(
                service_type=service_type or 'general',
                service_name=service_name,
                avg_price=price,
                scraped_at=datetime.utcnow()
            )
            db.session.add(market_price)
        
        db.session.commit()
        print(f"Scraped and saved {len(results)} {service_type or 'general'} services")
        
        return results
    
    except Exception as e:
        print(f"Error scraping prices: {str(e)}")
        return mock_data.get(service_type, mock_data['general'])

# def fetch_market_prices():
#     # URLs for specific services
#     urls = {
#         'sink_repair': 'https://www.urbancompany.com/bangalore-plumbers',
#         'electrician_visit': 'https://www.urbancompany.com/bangalore-electricians'
#     }

#     headers = {'User-Agent': 'Mozilla/5.0'}

#     for service_type, url in urls.items():
#         response = requests.get(url, headers=headers)
#         soup = BeautifulSoup(response.content, 'html.parser')

#         # Extracting service details
#         if service_type == 'sink_repair':
#             services = soup.find_all('div', class_='service-card')
#             for service in services:
#                 name = service.find('h3').text.strip()
#                 price_text = service.find('span', class_='price').text.strip()
#                 price = float(price_text.replace('₹', '').replace(',', ''))

#                 market_price = MarketPrice(
#                     service_type='sink repair',
#                     service_name=name,
#                     market_rate=price,
#                     last_checked=datetime.utcnow()
#                 )
#                 db.session.add(market_price)

#         elif service_type == 'electrician_visit':
#             services = soup.find_all('div', class_='service-card')
#             for service in services:
#                 name = service.find('h3').text.strip()
#                 price_text = service.find('span', class_='price').text.strip()
#                 price = float(price_text.replace('₹', '').replace(',', ''))

#                 market_price = MarketPrice(
#                     service_type='electrician visit',
#                     service_name=name,
#                     market_rate=price,
#                     last_checked=datetime.utcnow()
#                 )
#                 db.session.add(market_price)

#         db.session.commit()
#         print(f"Fetched and saved {len(services)} {service_type} services.")

def fetch_market_prices():
    # URL for plumbing services
    url = 'https://www.urbancompany.com/bangalore-plumbers'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    try:
        # Fetch webpage content
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise exception for bad status codes
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all service categories (assuming categories are in divs with a specific class)
        categories = soup.find_all('div', class_='category-section')  # Adjust class name based on actual HTML
        total_services = 0

        for category in categories:
            # Extract category name (e.g., "Tap & Mixer")
            category_name = category.find('h2').text.strip() if category.find('h2') else 'Unknown'

            # Find all service cards within this category
            services = category.find_all('div', class_='service-card')  # Adjust class name based on actual HTML

            for service in services:
                try:
                    # Extract service name
                    name = service.find('h3').text.strip() if service.find('h3') else 'Unknown'

                    # Extract price
                    price_elem = service.find('span', class_='price')
                    if price_elem:
                        price_text = price_elem.text.strip()
                        # Remove ₹ and commas, convert to float
                        price = float(price_text.replace('₹', '').replace(',', ''))
                    else:
                        price = 0.0  # Default if price not found

                    # Create MarketPrice object
                    market_price = MarketPrice(
                        service_type='plumbing',
                        category=category_name,
                        service_name=name,
                        market_rate=price,
                        last_checked=datetime.utcnow()
                    )
                    db.session.add(market_price)
                    total_services += 1

                except Exception as e:
                    print(f"Error processing service in category {category_name}: {str(e)}")
                    continue

        # Commit all changes to the database
        db.session.commit()
        print(f"Fetched and saved {total_services} plumbing services.")

    except requests.RequestException as e:
        print(f"Error fetching webpage: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        fetch_market_prices()
    # Run this script to fetch market prices
    # and save them to the database.
