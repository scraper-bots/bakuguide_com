# BakuGuide Restaurant Scraper

An asynchronous web scraper for extracting restaurant data from [BakuGuide.com](https://bakuguide.com) using Python, asyncio, and aiohttp.

## Features

- **Async/Concurrent Scraping**: Uses asyncio and aiohttp for fast, concurrent data extraction
- **Comprehensive Data Extraction**: Captures all restaurant details including:
  - Name, address, and phone numbers
  - Cuisine types and category
  - Working hours and average cost
  - Restaurant features/amenities
  - Description
  - Social media links (Facebook, Instagram, Twitter, Foursquare)
  - GPS coordinates
  - Images
- **CSV Export**: Saves all data to a structured CSV file
- **Rate Limiting**: Built-in semaphore to prevent overwhelming the server
- **Error Handling**: Robust error handling and logging

## Installation

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Test Scraper (3 pages)

To test the scraper with just 3 pages (~30 restaurants):

```bash
python test_scraper.py
```

This will create `test_restaurants.csv` with sample data.

### Full Scraper (All 50 pages)

To scrape all restaurants from all 50 pages:

```bash
python scraper.py
```

This will create `bakuguide_restaurants.csv` with all restaurant data. The scraping process may take several minutes depending on your internet connection.

## Output Format

The CSV file contains the following columns:

| Column | Description |
|--------|-------------|
| name | Restaurant name |
| address | Physical address |
| phones | Phone numbers (semicolon-separated) |
| cuisine | Cuisine types (semicolon-separated) |
| category | Restaurant category |
| working_hours | Operating hours |
| avg_cost_2_people | Average cost for 2 people |
| features | Restaurant features/amenities (semicolon-separated) |
| description | Restaurant description |
| facebook | Facebook URL |
| instagram | Instagram URL |
| twitter | Twitter URL |
| foursquare | Foursquare URL |
| email | Contact email |
| latitude | GPS latitude |
| longitude | GPS longitude |
| images | Image URLs (semicolon-separated) |
| url | BakuGuide detail page URL |

## Configuration

You can modify the scraper behavior by adjusting parameters in the code:

- `max_concurrent`: Maximum number of concurrent requests (default: 10)
- `total_pages`: Number of listing pages to scrape (default: 50)
- Timeout settings in `BakuGuideScraper.__aenter__()` (default: 30 seconds)

## Code Structure

```
bakuguide_com/
├── scraper.py           # Main scraper implementation
├── test_scraper.py      # Test script for limited scraping
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── bakuguide_restaurants.csv  # Output from full scraper
└── test_restaurants.csv       # Output from test scraper
```

## How It Works

1. **Fetch Listing Pages**: The scraper first fetches all 50 listing pages concurrently
2. **Extract URLs**: Parses each listing page to extract restaurant detail page URLs
3. **Scrape Details**: Visits each restaurant detail page concurrently to extract data
4. **Parse Data**: Uses BeautifulSoup to parse HTML and extract structured data
5. **Save to CSV**: Exports all data to a CSV file

## Example

```python
import asyncio
from scraper import BakuGuideScraper

async def main():
    async with BakuGuideScraper(max_concurrent=10) as scraper:
        # Scrape 5 pages
        restaurants = await scraper.scrape_all_restaurants(total_pages=5)

        # Save to CSV
        scraper.save_to_csv(restaurants, 'my_restaurants.csv')

asyncio.run(main())
```

## Notes

- The scraper respects rate limiting to avoid overwhelming the server
- Failed requests are logged but don't stop the scraping process
- Empty fields are saved as empty strings in the CSV
- Image URLs and other lists are semicolon-separated

## Dependencies

- aiohttp: Async HTTP client
- beautifulsoup4: HTML parsing
- lxml: XML/HTML parser
- pandas: Data manipulation (optional, for CSV export)
- aiofiles: Async file operations

## License

This scraper is for educational purposes only. Please respect BakuGuide's terms of service and robots.txt when using this tool.
