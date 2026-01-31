from amazon_paapi import AmazonApi

# --- YOUR AMAZON CREDENTIALS ---
ACCESS_KEY = "AKPAXDR8A81769815313"
SECRET_KEY = "wGAZnD4T+gjd3kyjdzSdKXE6ustFVAP/Lz1ginIG"
PARTNER_TAG = "lablocker-20"
COUNTRY = "US"

# Initialize the Amazon API client (Note the capitalization change to AmazonApi)
try:
    amazon = AmazonApi(ACCESS_KEY, SECRET_KEY, PARTNER_TAG, COUNTRY)
    print(f"--- Successfully connected as {PARTNER_TAG} ---")
except Exception as e:
    print(f"Connection Error: {e}")

# The hardware categories we are tracking
SEARCH_QUERIES = [
    "NVIDIA RTX 5090 Graphics Card",
    "NVIDIA RTX 4090 24GB",
    "Apple Mac Studio M4 Max",
    "Seagate IronWolf Pro 20TB",
    "Western Digital Red Pro 22TB"
]

def fetch_hardware_prices():
    for query in SEARCH_QUERIES:
        print(f"\nSearching for: {query}...")
        try:
            # Search for the top 3 items in this category
            search_results = amazon.search_items(keywords=query, item_count=3)
            
            if not search_results or not search_results.items:
                print("No results found for this query.")
                continue

            for item in search_results.items:
                title = item.item_info.title.display_value
                price = "Price not found"
                
                # Check for offers and extract price safely
                if item.offers and item.offers.listings:
                    price = item.offers.listings[0].price.display_amount
                
                link = item.detail_page_url
                
                print(f"Product: {title}")
                print(f"Current Price: {price}")
                print(f"Your Affiliate Link: {link}")
                print("-" * 30)
                
        except Exception as e:
            print(f"Error searching for {query}: {e}")

if __name__ == "__main__":
    fetch_hardware_prices()
