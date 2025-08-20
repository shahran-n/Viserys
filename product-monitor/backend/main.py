import json
import requests

def get_product_price(product):
    variants = product.get('variants', [])
    if variants:
        return variants[0].get('price', 'N/A')
    return 'N/A'

def is_product_available(product):
    """Check if any variant is available"""
    variants = product.get('variants', [])
    return any(variant.get('available', False) for variant in variants)

def get_all_products(url):
    """Get all products from the store"""
    products_url = f"{url}/products.json"
    all_products = []
    page = 1
    
    while True:
        paginated_url = f"{products_url}?limit=250&page={page}"
        
        try:
            response = requests.get(paginated_url)
            response.raise_for_status()
            data = response.json()
            
            products = data.get('products', [])
            
            if not products:
                break
                
            all_products.extend(products)
            page += 1
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {page}: {e}")
            break
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            break
    
    return all_products

def search_all_products_manual(url, keyword):
    """Manually search through all products for keyword matches"""
    print(f"Manually searching all products for '{keyword}'...")
    all_products = get_all_products(url)
    matching_products = []
    
    keyword_lower = keyword.lower()
    
    for product in all_products:
        # Search in title
        title = product.get('title', '').lower()
        # Search in description
        description = product.get('body_html', '').lower()
        # Search in tags
        tags = ' '.join(product.get('tags', [])).lower()
        # Search in vendor
        vendor = product.get('vendor', '').lower()
        
        if (keyword_lower in title or 
            keyword_lower in description or 
            keyword_lower in tags or 
            keyword_lower in vendor):
            matching_products.append(product)
    
    print(f"Found {len(matching_products)} products matching '{keyword}'")
    return matching_products

def shopify_scraper(url, keyword=None):
    """
    Scrapes Shopify products using Product ID as unique identifier with keyword search
    
    Args:
        url: Store URL (e.g., "https://shop-us.doverstreetmarket.com")
        keyword: Keyword to search for in product titles, descriptions, and tags
    
    Returns:
        Dictionary with Product ID as key and product data as value
    """
    products_dict = {}
    
    # Try Shopify's built-in search first
    if keyword:
        search_url = f"{url}/search.json?q={keyword}&limit=250"
        print(f"Searching for '{keyword}' using Shopify search...")
        
        try:
            response = requests.get(search_url)
            response.raise_for_status()
            data = response.json()
            
            # Check if search endpoint exists and returned results
            if 'results' in data:
                products = data.get('results', [])
                print(f"Found {len(products)} products via search endpoint")
            else:
                # Fallback to manual search
                products = search_all_products_manual(url, keyword)
        except:
            # Fallback to manual search if search endpoint fails
            products = search_all_products_manual(url, keyword)
    else:
        # Get all products if no keyword
        products = get_all_products(url)
    
    # Process found products
    for product in products:
        product_id = product.get('id')
        if not product_id:
            continue
                
        product_title = product.get('title', '')
        
        # Use Product ID as unique key
        products_dict[product_id] = {
            'id': product_id,
            'title': product_title,
            'handle': product.get('handle'),
            'vendor': product.get('vendor'),
            'product_type': product.get('product_type'),
            'price': get_product_price(product),
            'available': is_product_available(product),
            'url': f"{url}/products/{product.get('handle')}",
            'tags': product.get('tags', []),
            'description': product.get('body_html', ''),
            'created_at': product.get('created_at'),
            'updated_at': product.get('updated_at')
        }
        
        print(f"Product ID: {product_id} - {product_title}")
    
    return products_dict

if __name__ == "__main__":
    # Simple function call
    products = shopify_scraper("https://shop-us.doverstreetmarket.com", "shirt")
    
    print(f"\nTotal products found: {len(products)}")
