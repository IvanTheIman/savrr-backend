# api/services/open_food_facts.py

import requests


class OpenFoodFactsService:
    """Service for interacting with Open Food Facts API"""
    
    BASE_URL = 'https://world.openfoodfacts.net/api/v2/product'
    TIMEOUT = 10
    
    @staticmethod
    def fetch_product(barcode):
        """
        Fetch product information from Open Food Facts API
        
        Args:
            barcode (str): Product barcode
            
        Returns:
            dict: Product info with 'name' and 'unit' or None if not found
        """
        try:
            url = f'{OpenFoodFactsService.BASE_URL}/{barcode}'
            print(f"Fetching from Open Food Facts: {url}")
            
            headers = {
                'User-Agent': 'GroceryPriceApp/1.0',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=OpenFoodFactsService.TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 1 and data.get('product'):
                    product_data = data['product']
                    
                    # Extract product name
                    name = (
                        product_data.get('product_name') or 
                        product_data.get('product_name_en') or 
                        product_data.get('generic_name') or
                        'Unknown Product'
                    )
                    
                    # Try to determine unit
                    unit = OpenFoodFactsService._parse_unit(product_data.get('quantity', ''))
                    
                    print(f"✅ Found product: {name}")
                    
                    return {
                        'name': name,
                        'unit': unit,
                    }
                else:
                    print(f"❌ Product not found in Open Food Facts")
                    return None
                    
            elif response.status_code == 404:
                print(f"❌ Product {barcode} not found in Open Food Facts database")
                return None
            else:
                print(f"⚠️ Open Food Facts API returned status: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print("⏱️ Open Food Facts API timeout")
            return None
        except Exception as e:
            print(f"❌ Error fetching from Open Food Facts: {e}")
            return None
    
    @staticmethod
    def _parse_unit(quantity_string):
        """
        Parse unit from quantity string
        
        Args:
            quantity_string (str): Quantity from Open Food Facts
            
        Returns:
            str: Parsed unit (kg, g, L, ml, or 'each')
        """
        if not quantity_string:
            return 'each'
        
        quantity_lower = quantity_string.lower()
        
        if 'kg' in quantity_lower:
            return 'kg'
        elif 'g' in quantity_lower and 'kg' not in quantity_lower:
            return 'g'
        elif 'l' in quantity_lower or 'liter' in quantity_lower:
            return 'L'
        elif 'ml' in quantity_lower:
            return 'ml'
        else:
            return 'each'