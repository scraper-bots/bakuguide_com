#!/usr/bin/env python3
"""
Run the full BakuGuide restaurant scraper for all 50 pages.
This may take several minutes to complete.
"""
import asyncio
import time
from scraper import BakuGuideScraper


async def main():
    """Run full scraper with progress tracking"""
    print("=" * 80)
    print("BakuGuide Restaurant Scraper - Full Scrape")
    print("=" * 80)
    print("\nThis will scrape all 50 pages of restaurant listings.")
    print("Estimated time: 3-10 minutes depending on your connection.\n")

    response = input("Do you want to continue? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Scraping cancelled.")
        return

    start_time = time.time()

    async with BakuGuideScraper(max_concurrent=10) as scraper:
        # Scrape all 50 pages
        restaurants = await scraper.scrape_all_restaurants(total_pages=50)

        # Save to CSV
        output_file = 'bakuguide_restaurants.csv'
        scraper.save_to_csv(restaurants, output_file)

        elapsed_time = time.time() - start_time

        print("\n" + "=" * 80)
        print("SCRAPING COMPLETED!")
        print("=" * 80)
        print(f"Total restaurants scraped: {len(restaurants)}")
        print(f"Time elapsed: {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes)")
        print(f"Output file: {output_file}")
        print("\nYou can now open the CSV file in Excel, Google Sheets, or any spreadsheet program.")
        print("=" * 80)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nScraping interrupted by user.")
    except Exception as e:
        print(f"\n\nError occurred: {e}")
        import traceback
        traceback.print_exc()
