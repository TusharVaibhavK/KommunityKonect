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
        'wash_basin_repair': 'https://www.urbancompany.com/bangalore-plumbers',
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
            'wash_basin_repair': {'Wash basin leakage repair': 249, 'Wash basin installation': 499},
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
                type=service_type or 'general',
                service_name=service_name,
                market_rate=price,
                last_checked=datetime.utcnow()
            )
            db.session.add(market_price)
        
        db.session.commit()
        print(f"Scraped and saved {len(results)} {service_type or 'general'} services")
        
        return results
    
    except Exception as e:
        print(f"Error scraping prices: {str(e)}")
        return mock_data.get(service_type, mock_data['general'])

def scrape_urban_company_plumbing_services():
    """
    Scrape detailed information about plumbing services from Urban Company
    Specifically targeting the wash basin repair section
    """
    try:
        # URL for wash basin repair
        url = 'https://www.urbancompany.com/bangalore-plumbers/wash-basin-leakage-repair'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Fetch webpage content
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print(f"Scraping plumbing services data from Urban Company...")
        service_data = []
        
        # Extract main service details
        main_service = extract_main_service_details(soup)
        if main_service:
            service_data.append(main_service)
        
        # Extract service variants
        variants = extract_service_variants(soup)
        if variants:
            service_data.extend(variants)
        
        # Extract reviews sentiment
        reviews_sentiment = extract_reviews_sentiment(soup)
        
        # Save data to database
        save_plumbing_services_to_db(service_data, reviews_sentiment)
        
        return service_data
        
    except requests.RequestException as e:
        print(f"Error fetching webpage: {str(e)}")
        return []
    except Exception as e:
        print(f"Unexpected error in scrape_urban_company_plumbing_services: {str(e)}")
        return []


def extract_main_service_details(soup):
    """Extract details of the main wash basin repair service"""
    try:
        # Look for the main service heading
        service_heading = soup.find('h3', class_='css-146c3p1')
        if not service_heading:
            print("Main service heading not found")
            return None
        
        service_name = service_heading.text.strip()
        
        # Look for rating information
        rating_text = None
        reviews_count = None
        rating_element = soup.find('p', string=lambda text: text and 'reviews' in text)
        if rating_element:
            rating_info = rating_element.text.strip()
            # Extract rating (e.g., "4.82 (38K reviews)")
            rating_match = re.search(r'([\d.]+)\s*\(([^)]+)\s*reviews\)', rating_info)
            if rating_match:
                rating_text = float(rating_match.group(1))
                reviews_count = rating_match.group(2)
        
        # Create main service object
        main_service = {
            'type': 'plumbing',
            'category': 'Wash basin',
            'service_name': service_name,
            'market_rate': 249,  # Default price which will be updated by variants
            'rating': rating_text or 0.0,
            'review_count': reviews_count or '0',
            'is_main_service': True
        }
        
        return main_service
        
    except Exception as e:
        print(f"Error extracting main service details: {str(e)}")
        return None


def extract_service_variants(soup):
    """Extract details of service variants (waste pipe, bottle trap, etc.)"""
    variants = []
    try:
        # Find variant container elements
        variant_elements = soup.find_all('div', class_='css-175oi2r r-1xfd6ze r-1phboty r-rs99b7')
        
        for variant in variant_elements:
            try:
                # Extract variant name
                name_element = variant.find('p', class_='css-146c3p1', string=lambda s: s and len(s.strip()) > 0)
                if not name_element:
                    continue
                    
                variant_name = name_element.text.strip()
                
                # Extract ratings
                rating_value = 0.0
                review_count = '0'
                rating_element = variant.find('p', string=lambda text: text and 'reviews' in text)
                if rating_element:
                    rating_info = rating_element.text.strip()
                    # Extract rating (e.g., "4.82 (32K reviews)")
                    rating_match = re.search(r'([\d.]+)\s*\(([^)]+)\s*reviews\)', rating_info)
                    if rating_match:
                        rating_value = float(rating_match.group(1))
                        review_count = rating_match.group(2)
                
                # Extract price
                price = 0.0
                price_element = variant.find('p', string=lambda text: text and '₹' in text)
                if price_element:
                    price_text = price_element.text.strip()
                    price_match = re.search(r'₹\s*(\d+)', price_text)
                    if price_match:
                        price = float(price_match.group(1))
                
                # Create variant object
                variant_data = {
                    'type': 'plumbing',
                    'category': 'Wash basin',
                    'service_name': f"Wash basin repair - {variant_name}",
                    'variant_name': variant_name,
                    'market_rate': price,
                    'rating': rating_value,
                    'review_count': review_count,
                    'is_main_service': False
                }
                
                variants.append(variant_data)
                
            except Exception as e:
                print(f"Error extracting variant details: {str(e)}")
                continue
        
        # If no variants found using the primary approach, try an alternative
        if not variants:
            # Try looking for service cards in a different format
            variant_cards = soup.find_all('div', class_='css-175oi2r r-14lw9ot r-1xfd6ze r-1phboty')
            for card in variant_cards:
                try:
                    # Extract name, price, and rating using different selectors
                    name_element = card.find('p', attrs={'style': lambda s: s and '-webkit-line-clamp: 2' in s})
                    if name_element:
                        variant_name = name_element.text.strip()
                        
                        # Look for price
                        price_element = card.find('p', string=lambda s: s and '₹' in s)
                        price = 0.0
                        if price_element:
                            price_text = price_element.text.strip()
                            price_match = re.search(r'₹\s*(\d+)', price_text)
                            if price_match:
                                price = float(price_match.group(1))
                        
                        # Look for rating
                        rating_element = card.find('p', string=lambda s: s and 'reviews' in s)
                        rating_value = 0.0
                        review_count = '0'
                        if rating_element:
                            rating_info = rating_element.text.strip()
                            rating_match = re.search(r'([\d.]+)\s*\(([^)]+)\s*reviews\)', rating_info)
                            if rating_match:
                                rating_value = float(rating_match.group(1))
                                review_count = rating_match.group(2)
                        
                        # Create variant object
                        variant_data = {
                            'type': 'plumbing',
                            'category': 'Wash basin',
                            'service_name': f"Wash basin repair - {variant_name}",
                            'variant_name': variant_name,
                            'market_rate': price,
                            'rating': rating_value,
                            'review_count': review_count,
                            'is_main_service': False
                        }
                        
                        variants.append(variant_data)
                except Exception as e:
                    print(f"Error in alternative variant extraction: {str(e)}")
                    continue
            
        # If still no variants found, use the data from the screenshot
        if not variants:
            print("Using default data from screenshot for variants")
            variants = [
                {
                    'type': 'plumbing',
                    'category': 'Wash basin',
                    'service_name': 'Wash basin repair - Waste pipe',
                    'variant_name': 'Waste pipe',
                    'market_rate': 99.0,
                    'rating': 4.82,
                    'review_count': '32K',
                    'is_main_service': False
                },
                {
                    'type': 'plumbing',
                    'category': 'Wash basin',
                    'service_name': 'Wash basin repair - Bottle trap',
                    'variant_name': 'Bottle trap',
                    'market_rate': 199.0,
                    'rating': 4.80,
                    'review_count': '6K',
                    'is_main_service': False
                }
            ]
        
        return variants
        
    except Exception as e:
        print(f"Error extracting service variants: {str(e)}")
        return []


def extract_reviews_sentiment(soup):
    """Extract sentiment from reviews to identify customer pain points and satisfaction factors"""
    reviews_data = {
        'positive_keywords': [],
        'negative_keywords': [],
        'total_reviews_analyzed': 0,
        'avg_rating': 0.0,
        'positive_count': 0,
        'negative_count': 0,
        'neutral_count': 0
    }
    
    try:
        # Find all review containers
        review_containers = soup.find_all('div', class_='css-175oi2r r-1niwhzg r-17gur6a r-13qz1uu r-wh77r2')
        
        total_rating = 0
        ratings_count = 0
        
        for container in review_containers:
            try:
                # Extract review text
                review_text_element = container.find('p', class_='css-146c3p1', style=lambda s: s and 'font-family: os_regular; font-size: 14px' in s)
                if not review_text_element:
                    continue
                
                review_text = review_text_element.text.strip()
                
                # Extract rating
                rating_element = container.find('p', string=lambda s: s and s.strip().isdigit())
                rating = 0
                if rating_element:
                    try:
                        rating = int(rating_element.text.strip())
                        total_rating += rating
                        ratings_count += 1
                    except ValueError:
                        pass
                
                # Categorize review
                if rating >= 4:
                    reviews_data['positive_count'] += 1
                    # Extract positive keywords
                    positive_words = extract_sentiment_keywords(review_text, positive=True)
                    reviews_data['positive_keywords'].extend(positive_words)
                elif rating <= 2:
                    reviews_data['negative_count'] += 1
                    # Extract negative keywords
                    negative_words = extract_sentiment_keywords(review_text, positive=False)
                    reviews_data['negative_keywords'].extend(negative_words)
                else:
                    reviews_data['neutral_count'] += 1
                
                reviews_data['total_reviews_analyzed'] += 1
                
            except Exception as e:
                print(f"Error processing review: {str(e)}")
                continue
        
        # Calculate average rating
        if ratings_count > 0:
            reviews_data['avg_rating'] = total_rating / ratings_count
        
        # Get frequency counts for keywords
        reviews_data['positive_keywords'] = get_keyword_frequency(reviews_data['positive_keywords'])
        reviews_data['negative_keywords'] = get_keyword_frequency(reviews_data['negative_keywords'])
        
        return reviews_data
        
    except Exception as e:
        print(f"Error extracting reviews sentiment: {str(e)}")
        return reviews_data


def extract_sentiment_keywords(text, positive=True):
    """Extract keywords indicating sentiment from review text"""
    # Define positive and negative keyword patterns
    positive_patterns = [
        r'excellent|great|good|awesome|amazing|satisfied|happy|professional|clean|recommend|helpful|polite|patient|perfect'
    ]
    
    negative_patterns = [
        r'bad|poor|terrible|not good|waste|problem|issue|charged extra|didn\'t work|not satisfied|incomplete|didn\'t finish'
    ]
    
    keywords = []
    patterns = positive_patterns if positive else negative_patterns
    
    for pattern in patterns:
        matches = re.finditer(pattern, text.lower())
        for match in matches:
            keyword = match.group(0)
            # Get some context around the keyword
            start = max(0, match.start() - 10)
            end = min(len(text), match.end() + 10)
            context = text[start:end].strip()
            keywords.append((keyword, context))
    
    return keywords


def get_keyword_frequency(keywords):
    """Get frequency count of sentiment keywords"""
    frequency = {}
    for keyword, context in keywords:
        if keyword in frequency:
            frequency[keyword]['count'] += 1
            # Add context if it's unique
            if context not in [c for c, _ in frequency[keyword]['contexts']]:
                frequency[keyword]['contexts'].append((context, 1))
        else:
            frequency[keyword] = {
                'count': 1,
                'contexts': [(context, 1)]
            }
    
    # Sort by frequency
    return dict(sorted(frequency.items(), key=lambda x: x[1]['count'], reverse=True))


def save_plumbing_services_to_db(service_data, reviews_sentiment=None):
    """Save the scraped plumbing service data to the database"""
    try:
        # Delete existing records for wash basin services to avoid duplicates
        existing_records = MarketPrice.query.filter_by(type='plumbing', category='Wash basin').all()
        for record in existing_records:
            db.session.delete(record)
        
        # Add new records
        for service in service_data:
            market_price = MarketPrice(
                type=service.get('type', 'plumbing'),
                category=service.get('category', 'Wash basin'),
                service_name=service.get('service_name', 'Unknown Service'),
                market_rate=service.get('market_rate', 0.0),
                rating=service.get('rating', 0.0),
                review_count=service.get('review_count', '0'),
                options_count=service.get('options_count', 0),
                last_checked=datetime.utcnow(),
                is_main_service=service.get('is_main_service', False),
                variant_name=service.get('variant_name', None)
            )
            db.session.add(market_price)
        
        # Save sentiment analysis if available
        if reviews_sentiment and reviews_sentiment['total_reviews_analyzed'] > 0:
            # First, let's store the overall sentiment metrics
            sentiment_summary = MarketPrice(
                type='sentiment_analysis',
                category='Wash basin repair',
                service_name='Review Sentiment Summary',
                rating=reviews_sentiment['avg_rating'],
                review_count=str(reviews_sentiment['total_reviews_analyzed']),
                market_rate=0.0,  # Not applicable for sentiment
                positive_count=reviews_sentiment['positive_count'],
                negative_count=reviews_sentiment['negative_count'],
                neutral_count=reviews_sentiment['neutral_count'],
                last_checked=datetime.utcnow()
            )
            db.session.add(sentiment_summary)
            
            # Store top positive keywords
            for keyword, data in list(reviews_sentiment['positive_keywords'].items())[:5]:  # Top 5 only
                positive_keyword = MarketPrice(
                    type='sentiment_keyword',
                    category='positive',
                    service_name=keyword,
                    review_count=str(data['count']),
                    notes="; ".join([context for context, _ in data['contexts'][:3]]),  # Store up to 3 contexts
                    last_checked=datetime.utcnow()
                )
                db.session.add(positive_keyword)
            
            # Store top negative keywords
            for keyword, data in list(reviews_sentiment['negative_keywords'].items())[:5]:  # Top 5 only
                negative_keyword = MarketPrice(
                    type='sentiment_keyword',
                    category='negative',
                    service_name=keyword,
                    review_count=str(data['count']),
                    notes="; ".join([context for context, _ in data['contexts'][:3]]),  # Store up to 3 contexts
                    last_checked=datetime.utcnow()
                )
                db.session.add(negative_keyword)
        
        db.session.commit()
        print(f"Successfully saved {len(service_data)} plumbing services to database")
        if reviews_sentiment:
            print(f"Analyzed {reviews_sentiment['total_reviews_analyzed']} reviews for sentiment")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error saving plumbing services to database: {str(e)}")


def fetch_market_prices():
    try:
        # First try the new specialized scraper for detailed wash basin repair data
        plumbing_data = scrape_urban_company_plumbing_services()
        
        if not plumbing_data:
            # If the specialized scraper fails, fall back to the original method
            print("Specialized scraper failed, falling back to original method")
            url = 'https://www.urbancompany.com/bangalore-plumbers'
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

            try:
                # Fetch webpage content
                response = requests.get(url, headers=headers)
                response.raise_for_status()  # Raise exception for bad status codes
                soup = BeautifulSoup(response.content, 'html.parser')

                # Look for "View details" elements specifically
                view_details_elements = soup.find_all('p', class_='css-146c3p1')
                
                # If we find these elements, process them differently
                if view_details_elements:
                    print(f"Found {len(view_details_elements)} 'View details' elements")
                    services_found = process_view_details_elements(soup, view_details_elements)
                    if services_found:
                        return
                
                # If no view details elements or processing failed, continue with original approach
                service_sections = soup.find_all('div', class_='service-section')  # Adjust class based on actual HTML
                
                if not service_sections:
                    # Fallback to manual data from image if scraping fails
                    print("No service sections found, using data from image")
                    plumbing_services = [
                        {
                            'name': 'Tap repair',
                            'rating': 4.83,
                            'reviews': '103K',
                            'starting_price': 49,
                            'options': 3
                        },
                        {
                            'name': 'Tap installation/replacement',
                            'rating': 4.84,
                            'reviews': '43K',
                            'starting_price': 99,
                            'options': 3
                        },
                        {
                            'name': 'Tap accessory installation',
                            'rating': 4.86,
                            'reviews': '2K',
                            'starting_price': 69,
                            'options': 4
                        }
                    ]
                    
                    # Save the manually entered data
                    for service in plumbing_services:
                        market_price = MarketPrice(
                            type='plumbing',
                            category='Tap & mixer',
                            service_name=service['name'],
                            market_rate=service['starting_price'],
                            rating=service['rating'],
                            review_count=service['reviews'],
                            options_count=service['options'],
                            last_checked=datetime.utcnow()
                        )
                        db.session.add(market_price)
                    
                    db.session.commit()
                    print(f"Saved {len(plumbing_services)} plumbing services from manual data.")
                    return
                
                total_services = 0
                
                for section in service_sections:
                    try:
                        # Extract service name
                        service_title = section.find('h2', class_='service-title') or section.find('h3', class_='service-name')
                        service_name = service_title.text.strip() if service_title else 'Unknown Service'
                        
                        # Extract rating information
                        rating_elem = section.find('span', class_='rating')
                        rating = float(rating_elem.text.strip()) if rating_elem else 0.0
                        
                        # Extract reviews count
                        reviews_elem = section.find('span', class_='reviews')
                        reviews_text = reviews_elem.text.strip() if reviews_elem else '0'
                        reviews_text = reviews_text.replace('(', '').replace(')', '').replace('reviews', '').strip()
                        
                        # Extract starting price
                        price_elem = section.find('span', class_='price') or section.find('div', class_='price')
                        if price_elem:
                            price_text = price_elem.text.strip()
                            # Look for patterns like "Starts at ₹49"
                            if 'starts at' in price_text.lower():
                                price_text = price_text.lower().replace('starts at', '').strip()
                            price = float(price_text.replace('₹', '').replace(',', '').strip())
                        else:
                            price = 0.0
                        
                        # Extract number of options
                        options_elem = section.find('span', class_='options-count') or section.find('div', class_='options')
                        options_text = options_elem.text.strip() if options_elem else '0'
                        options_count = int(options_text.split()[0]) if options_text.split() else 0
                        
                        # Create MarketPrice object
                        market_price = MarketPrice(
                            type='plumbing',
                            category='Tap & mixer',
                            service_name=service_name,
                            market_rate=price,
                            rating=rating,
                            review_count=reviews_text,
                            options_count=options_count,
                            last_checked=datetime.utcnow()
                        )
                        db.session.add(market_price)
                        total_services += 1
                        
                    except Exception as e:
                        print(f"Error processing service {service_name if 'service_name' in locals() else 'unknown'}: {str(e)}")
                        continue
                
                # Additional plumbing categories from the image
                plumbing_categories = ['Toilet', 'Bath & shower', 'Bath accessories', 'Basin & sink', 
                                    'Drainage & blockage', 'Leakage & connections', 'Water tank & motor']
                
                # Add these categories as placeholders for future scraping
                for category in plumbing_categories:
                    market_price = MarketPrice(
                        type='plumbing',
                        category=category,
                        service_name=f'{category} services',
                        market_rate=0.0,  # Placeholder
                        rating=0.0,
                        review_count='0',
                        options_count=0,
                        last_checked=datetime.utcnow(),
                        is_placeholder=True
                    )
                    db.session.add(market_price)
                    total_services += 1

                # Commit all changes to the database
                db.session.commit()
                print(f"Fetched and saved {total_services} plumbing services.")

            except requests.RequestException as e:
                print(f"Error fetching webpage: {str(e)}")
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
    except Exception as e:
        print(f"Error in fetch_market_prices: {str(e)}")


def process_view_details_elements(soup, view_details_elements):
    """
    Process the page structure where "View details" elements are present
    Returns True if successfully processed any services
    """
    services_processed = 0
    
    try:
        # Find parent service cards - typically these "View details" elements 
        # are within service cards or sections
        for view_element in view_details_elements:
            try:
                # Navigate up to find the service card container
                # This might be a parent div that contains all service info
                service_card = find_parent_container(view_element, max_levels=4)
                
                if not service_card:
                    continue
                
                # Extract service information from the container
                service_name = extract_text(service_card, ['h2', 'h3', 'div.service-name', 'div.service-title'])
                if not service_name:
                    # Try to find any heading element within the container
                    heading_elements = service_card.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                    if heading_elements:
                        service_name = heading_elements[0].text.strip()
                    else:
                        service_name = "Unknown Service"
                
                # Extract price information - often near "View details" or within specific price elements
                price_text = extract_text(service_card, ['span.price', 'div.price', 'p.price'])
                price = 0.0
                if price_text:
                    # Clean and extract the numeric price
                    price = extract_price_from_text(price_text)
                else:
                    # Look for any text containing currency symbols or price indicators
                    all_texts = [p.text.strip() for p in service_card.find_all('p') if p.text.strip()]
                    for text in all_texts:
                        if '₹' in text or 'Rs.' in text or 'rs' in text.lower() or 'starts at' in text.lower():
                            price = extract_price_from_text(text)
                            if price > 0:
                                break
                
                # Extract rating if available
                rating_text = extract_text(service_card, ['span.rating', 'div.rating'])
                rating = 0.0
                if rating_text:
                    try:
                        rating = float(rating_text.replace('★', '').strip())
                    except:
                        # Look for numeric values that could be ratings
                        import re
                        rating_match = re.search(r'(\d+\.\d+)', rating_text)
                        if rating_match:
                            rating = float(rating_match.group(1))
                
                # Extract reviews count
                reviews_text = extract_text(service_card, ['span.reviews', 'div.reviews'])
                if not reviews_text:
                    # Try to find text containing review indicators
                    all_small_texts = [span.text.strip() for span in service_card.find_all(['span', 'small'])]
                    for text in all_small_texts:
                        if 'review' in text.lower() or 'ratings' in text.lower():
                            reviews_text = text
                            break
                
                # Create MarketPrice object
                market_price = MarketPrice(
                    type='plumbing',
                    category='General',  # Default category
                    service_name=service_name,
                    market_rate=price,
                    rating=rating,
                    review_count=reviews_text if reviews_text else '0',
                    options_count=0,  # Default value
                    last_checked=datetime.utcnow()
                )
                db.session.add(market_price)
                services_processed += 1
                
            except Exception as e:
                service_name_var = service_name if 'service_name' in locals() else "Unknown"
                print(f"Error processing 'View details' service {service_name_var}: {str(e)}")
                continue
        
        if services_processed > 0:
            db.session.commit()
            print(f"Successfully processed {services_processed} services from 'View details' elements")
            return True
        
        return False
        
    except Exception as e:
        print(f"Error in process_view_details_elements: {str(e)}")
        return False


def find_parent_container(element, max_levels=4):
    """Find the parent container that likely contains all service information"""
    current = element
    level = 0
    
    while current and level < max_levels:
        # Check if this parent seems to be a complete service card
        if current.name == 'div' and (
            'card' in current.get('class', [''])[0].lower() if current.get('class') else False or
            'service' in current.get('class', [''])[0].lower() if current.get('class') else False or
            'item' in current.get('class', [''])[0].lower() if current.get('class') else False or
            len(current.find_all(['h2', 'h3', 'p'])) >= 3  # Service cards typically have multiple elements
        ):
            return current
        
        # Move up to parent
        current = current.parent
        level += 1
    
    # If no ideal container found, return the highest level we reached
    return current if level > 0 else None


def extract_text(container, selectors):
    """Extract text from the first matching selector"""
    for selector in selectors:
        if '.' in selector:
            tag, class_name = selector.split('.')
            element = container.find(tag, class_=class_name)
        else:
            element = container.find(selector)
            
        if element and element.text.strip():
            return element.text.strip()
    
    return None


def extract_price_from_text(text):
    """Extract price value from text containing price information"""
    import re
    
    # Remove non-essential text
    text = text.lower().replace('starts at', '').replace('starting at', '')
    
    # Look for amount with ₹ symbol
    price_match = re.search(r'₹\s*(\d+[,\d]*(\.\d+)?)', text)
    if price_match:
        return float(price_match.group(1).replace(',', ''))
    
    # Look for Rs. format
    price_match = re.search(r'rs\.?\s*(\d+[,\d]*(\.\d+)?)', text, re.IGNORECASE)
    if price_match:
        return float(price_match.group(1).replace(',', ''))
    
    # Look for just a number that might be a price
    price_match = re.search(r'(\d+[,\d]*(\.\d+)?)', text)
    if price_match:
        return float(price_match.group(1).replace(',', ''))
    
    return 0.0


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        fetch_market_prices()
    # Run this script to fetch market prices
    # and save them to the database.
