
import requests


class OpenFoodFactsService:
    
    BASE_URL = 'https://world.openfoodfacts.net/api/v2/product'
    TIMEOUT = 10
    
    @staticmethod
    def fetch_product(barcode):
        """
        function that attempts to get product infromation using barcode from Open Food Facts API
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
                    
                    name = (
                        product_data.get('product_name') or 
                        product_data.get('product_name_en') or 
                        product_data.get('generic_name') or
                        'Unknown Product'
                    )
                    
                    unit = OpenFoodFactsService._parse_unit(product_data.get('quantity', ''))
                    
                    print(f"Found product: {name}")
                    
                    return {
                        'name': name,
                        'unit': unit,
                    }
                else:
                    print(f"Product not found in Open Food Facts")
                    return None
                    
            elif response.status_code == 404:
                print(f"Product {barcode} not found in Open Food Facts database")
                return None
            else:
                print(f"Open Food Facts API returned status: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print("Open Food Facts API timeout")
            return None
        except Exception as e:
            print(f"Error fetching from Open Food Facts: {e}")
            return None
    
    @staticmethod
    def _parse_unit(quantity_string):
        
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