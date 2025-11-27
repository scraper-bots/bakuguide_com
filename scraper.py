import asyncio
import aiohttp
from bs4 import BeautifulSoup
import csv
import re
from typing import List, Dict
from urllib.parse import urljoin
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BakuGuideScraper:
    """Async scraper for BakuGuide restaurant data"""

    BASE_URL = "https://bakuguide.com"
    LISTING_URL = f"{BASE_URL}/az/1-yemek-icmek/13-restoranlar-p"

    def __init__(self, max_concurrent=10):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.session = None

    async def __aenter__(self):
        """Async context manager entry"""
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def fetch_page(self, url: str) -> str:
        """Fetch a page with rate limiting"""
        async with self.semaphore:
            try:
                async with self.session.get(url) as response:
                    response.raise_for_status()
                    return await response.text()
            except Exception as e:
                logger.error(f"Error fetching {url}: {e}")
                return None

    def parse_listing_page(self, html: str) -> Dict[str, Dict]:
        """Extract restaurant URLs and listing data from a listing page"""
        soup = BeautifulSoup(html, 'lxml')
        restaurant_data = {}

        # Find all restaurant cards
        articles = soup.find_all('article', class_='card')

        for article in articles:
            # Find the link to restaurant detail page
            link = article.find('a', href=re.compile(r'/az/1-yemek-icmek/13-restoranlar/\d+'))
            if not link or not link.get('href'):
                continue

            full_url = urljoin(self.BASE_URL, link['href'])
            data = {}

            # Extract data from the listing card
            try:
                # Average cost for 2 people
                rows = article.find_all('div', class_='row')
                for row in rows:
                    col_lg_3 = row.find('div', class_='col-lg-3')
                    if col_lg_3 and '2 nəfərə orta xərc' in col_lg_3.get_text():
                        col_lg_9 = row.find('div', class_='col-lg-9')
                        if col_lg_9:
                            # Get all text content including the manat symbol
                            cost_text = col_lg_9.get_text(strip=True)
                            # Clean up the text
                            cost_text = cost_text.replace('M', '').strip()
                            if cost_text:
                                data['avg_cost_2_people'] = cost_text
                        break

                # Features/Amenities
                for row in rows:
                    col_lg_3 = row.find('div', class_='col-lg-3')
                    if col_lg_3 and 'Xüsusiyyətləri' in col_lg_3.get_text():
                        col_lg_9 = row.find('div', class_='col-lg-9')
                        if col_lg_9:
                            features = [a.get_text(strip=True) for a in col_lg_9.find_all('a')]
                            if features:
                                data['features'] = '; '.join(features)
                        break

                # Cuisine from listing
                for row in rows:
                    col_lg_3 = row.find('div', class_='col-lg-3')
                    if col_lg_3 and 'Mətbəx' in col_lg_3.get_text():
                        col_lg_9 = row.find('div', class_='col-lg-9')
                        if col_lg_9:
                            cuisines = [a.get_text(strip=True) for a in col_lg_9.find_all('a')]
                            if cuisines:
                                data['cuisine'] = '; '.join(cuisines)
                        break

                # Working hours from listing
                for row in rows:
                    col_lg_3 = row.find('div', class_='col-lg-3')
                    if col_lg_3 and 'İş saatları' in col_lg_3.get_text():
                        col_lg_9 = row.find('div', class_='col-lg-9')
                        if col_lg_9:
                            hours = col_lg_9.get_text(strip=True)
                            if hours:
                                data['working_hours'] = hours
                        break

                # Address from listing
                for row in rows:
                    col_lg_3 = row.find('div', class_='col-lg-3')
                    if col_lg_3 and 'Ünvan' in col_lg_3.get_text():
                        col_lg_9 = row.find('div', class_='col-lg-9')
                        if col_lg_9:
                            address = col_lg_9.get_text(strip=True)
                            if address:
                                data['address'] = address
                        break

                # Phone from listing
                for row in rows:
                    col_lg_3 = row.find('div', class_='col-lg-3')
                    if col_lg_3 and 'Telefon' in col_lg_3.get_text():
                        col_lg_9 = row.find('div', class_='col-lg-9')
                        if col_lg_9:
                            phone = col_lg_9.get_text(strip=True)
                            if phone:
                                data['phones'] = phone
                        break

            except Exception as e:
                logger.error(f"Error parsing listing card for {full_url}: {e}")

            restaurant_data[full_url] = data

        return restaurant_data

    def parse_restaurant_detail(self, html: str, url: str) -> Dict:
        """Extract all data from a restaurant detail page"""
        soup = BeautifulSoup(html, 'lxml')
        data = {'url': url}

        try:
            # Name
            name_elem = soup.find('h1', class_='page_title')
            data['name'] = name_elem.get_text(strip=True) if name_elem else ''

            # Address
            address_section = soup.find('h4', string='Ünvan')
            if address_section:
                address_p = address_section.find_next('p')
                data['address'] = address_p.get_text(strip=True) if address_p else ''
            else:
                data['address'] = ''

            # Phone numbers
            phone_div = soup.find('div', class_='phone_numbers')
            if phone_div:
                phones = [a.get_text(strip=True) for a in phone_div.find_all('a')]
                data['phones'] = '; '.join(phones)
            else:
                data['phones'] = ''

            # Cuisine types
            kitchen_section = soup.find('h4', string='Mətbəx növü')
            if kitchen_section:
                kitchen_p = kitchen_section.find_next('p', class_='place-view-kitchen')
                if kitchen_p:
                    cuisines = [a.get_text(strip=True) for a in kitchen_p.find_all('a')]
                    data['cuisine'] = '; '.join(cuisines)
                else:
                    data['cuisine'] = ''
            else:
                data['cuisine'] = ''

            # Category
            category_section = soup.find('h4', string='Kateqoriya')
            if category_section:
                category_p = category_section.find_next('p')
                data['category'] = category_p.get_text(strip=True) if category_p else ''
            else:
                data['category'] = ''

            # Working hours
            hours_section = soup.find('h4', string='İş saatları')
            if hours_section:
                hours_p = hours_section.find_next('p')
                data['working_hours'] = hours_p.get_text(strip=True) if hours_p else ''
            else:
                data['working_hours'] = ''

            # Average cost for 2 people (detail page may have it too)
            # This is usually only on listing page, but check just in case
            data['avg_cost_2_people'] = ''

            # Restaurant features/amenities (detail page may have it)
            # This is usually only on listing page, but check just in case
            data['features'] = ''

            # Description
            desc_section = soup.find('h4', class_='panel-title', string='Məkan təsviri')
            if desc_section:
                text_div = desc_section.find_next('div', class_='text')
                if text_div:
                    data['description'] = text_div.get_text(strip=True)
                else:
                    data['description'] = ''
            else:
                data['description'] = ''

            # Social media links
            social_section = soup.find('h4', string='Digər əlaqə vasitələri')
            social_links = {}
            if social_section:
                # Find the parent div and look for all links after the h4
                parent_div = social_section.find_parent('div', class_='info_icon_text')
                if parent_div:
                    for link in parent_div.find_all('a'):
                        href = link.get('href', '')
                        title = link.get('title', '').lower()

                        # Check both href and title for social media platforms
                        if 'facebook' in href.lower() or 'facebook' in title:
                            social_links['facebook'] = href
                        elif 'instagram' in href.lower() or 'instagram' in title:
                            social_links['instagram'] = href
                        elif 'twitter' in href.lower() or 'twitter' in title:
                            social_links['twitter'] = href
                        elif 'foursquare' in title or '4sq.com' in href:
                            social_links['foursquare'] = href
                        elif '/cdn-cgi/l/email-protection' in href or 'mailto:' in href:
                            # Email (might be obfuscated by CloudFlare)
                            if 'mailto:' in href:
                                social_links['email'] = href.replace('mailto:', '')
                            elif title == 'facebook' and 'email-protection' in href:
                                # This is actually an email, not facebook
                                social_links['email'] = 'protected'

            data['facebook'] = social_links.get('facebook', '')
            data['instagram'] = social_links.get('instagram', '')
            data['twitter'] = social_links.get('twitter', '')
            data['foursquare'] = social_links.get('foursquare', '')
            data['email'] = social_links.get('email', '')

            # Map coordinates (from Google Maps iframe)
            iframe = soup.find('iframe', src=re.compile(r'google\.com/maps'))
            if iframe:
                src = iframe.get('src', '')
                # Extract center coordinates from URL
                center_match = re.search(r'center=([-\d.]+),([-\d.]+)', src)
                if center_match:
                    data['latitude'] = center_match.group(1)
                    data['longitude'] = center_match.group(2)
                else:
                    data['latitude'] = ''
                    data['longitude'] = ''
            else:
                data['latitude'] = ''
                data['longitude'] = ''

            # Images
            carousel = soup.find('div', class_='carousel-inner')
            if carousel:
                images = []
                for img in carousel.find_all('img'):
                    img_src = img.get('src', img.get('data-src', ''))
                    if img_src and 'noimage' not in img_src:
                        full_img_url = urljoin(self.BASE_URL, img_src)
                        images.append(full_img_url)
                data['images'] = '; '.join(images)
            else:
                data['images'] = ''

        except Exception as e:
            logger.error(f"Error parsing restaurant detail from {url}: {e}")

        return data

    async def scrape_restaurant(self, url: str) -> Dict:
        """Scrape a single restaurant detail page"""
        logger.info(f"Scraping restaurant: {url}")
        html = await self.fetch_page(url)

        if html:
            return self.parse_restaurant_detail(html, url)
        return None

    async def get_all_restaurant_data_from_listings(self, total_pages: int = 50) -> Dict[str, Dict]:
        """Get all restaurant URLs and listing data from all listing pages"""
        logger.info(f"Fetching restaurant data from {total_pages} listing pages...")

        # Create tasks for all listing pages
        tasks = []
        for page_num in range(1, total_pages + 1):
            url = f"{self.LISTING_URL}{page_num}"
            tasks.append(self.fetch_page(url))

        # Fetch all pages concurrently
        pages_html = await asyncio.gather(*tasks)

        # Parse all listing pages
        all_restaurant_data = {}
        for html in pages_html:
            if html:
                page_data = self.parse_listing_page(html)
                all_restaurant_data.update(page_data)

        logger.info(f"Found {len(all_restaurant_data)} unique restaurants")

        return all_restaurant_data

    async def scrape_all_restaurants(self, total_pages: int = 50) -> List[Dict]:
        """Scrape all restaurants from all pages"""
        # Get all restaurant data from listing pages
        listing_data = await self.get_all_restaurant_data_from_listings(total_pages)
        restaurant_urls = list(listing_data.keys())

        # Scrape all restaurant detail pages concurrently
        logger.info(f"Scraping {len(restaurant_urls)} restaurant detail pages...")
        tasks = [self.scrape_restaurant(url) for url in restaurant_urls]
        results = await asyncio.gather(*tasks)

        # Merge listing data with detail page data
        restaurants = []
        for detail_data in results:
            if detail_data is not None:
                url = detail_data['url']
                # Start with listing data (which has avg_cost, features, etc.)
                merged_data = listing_data.get(url, {}).copy()
                # Update with detail page data (detail data takes priority)
                # But only if the detail field is not empty
                for key, value in detail_data.items():
                    if value or key not in merged_data:
                        merged_data[key] = value
                restaurants.append(merged_data)

        logger.info(f"Successfully scraped {len(restaurants)} restaurants")

        return restaurants

    def save_to_csv(self, restaurants: List[Dict], filename: str = 'bakuguide_restaurants.csv'):
        """Save restaurant data to CSV file"""
        if not restaurants:
            logger.warning("No restaurants to save")
            return

        # Define CSV fields
        fieldnames = [
            'name', 'address', 'phones', 'cuisine', 'category',
            'working_hours', 'avg_cost_2_people', 'features', 'description',
            'facebook', 'instagram', 'twitter', 'foursquare', 'email',
            'latitude', 'longitude', 'images', 'url'
        ]

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for restaurant in restaurants:
                # Ensure all fields exist
                row = {field: restaurant.get(field, '') for field in fieldnames}
                writer.writerow(row)

        logger.info(f"Saved {len(restaurants)} restaurants to {filename}")


async def main():
    """Main function to run the scraper"""
    async with BakuGuideScraper(max_concurrent=10) as scraper:
        # Scrape all restaurants from all 50 pages
        restaurants = await scraper.scrape_all_restaurants(total_pages=50)

        # Save to CSV
        scraper.save_to_csv(restaurants, 'bakuguide_restaurants.csv')

        logger.info("Scraping completed!")


if __name__ == "__main__":
    asyncio.run(main())
